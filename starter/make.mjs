#!/usr/bin/env node
/**
 * make.mjs —— 一条命令出片：音乐 → 预览 →（可选）终版 → 报告
 *
 * 目的：把"先跑 Suno 文本 / 再截图 / 再抽帧 / 再合音频"的多步流程压成一次调用，
 * 减少往返等待和重复渲染，也不给模型留"再多渲一遍看看"的余地。
 *
 * 用法：
 *   node make.mjs --duration 12 --title "一拍，一帧"
 *   node make.mjs --preset pulse --duration 30 --final
 *   node make.mjs --duration 15 --audio ../audio/song.mp3 --skip-music
 *   node make.mjs --preview-only
 */
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { PROJECT } from './src/config.js';

const argv = process.argv.slice(2);
const arg = (n, d) => {
  const i = argv.indexOf(`--${n}`);
  if (i >= 0 && argv[i + 1] != null && !argv[i + 1].startsWith('--')) return argv[i + 1];
  return d;
};
const has = (n) => argv.includes(`--${n}`);
const num = (n, d) => (arg(n, undefined) === undefined ? d : Number(arg(n)));

const duration = num('duration', PROJECT.duration);
const preset = arg('preset', 'uplift');
const bpm = num('bpm', 0);
const fps = num('fps', PROJECT.fps);
const finalAlso = has('final');
const previewOnly = has('preview-only');
const skipMusic = has('skip-music');
const userAudio = arg('audio', null);
const musicPath = arg('music', 'audio/music.wav');
const gridPath = arg('grid', 'audio/beats.json');

const t0 = Date.now();
const step = (label) => console.log(`\n▸ ${label}`);
const run = (cmd, args, opts = {}) => {
  const r = spawnSync(cmd, args, { stdio: 'inherit', ...opts });
  if (r.status !== 0) {
    console.error(`失败：${cmd} ${args.join(' ')}`);
    process.exit(r.status || 1);
  }
};

fs.mkdirSync('videos', { recursive: true });
fs.mkdirSync('renders', { recursive: true });
fs.mkdirSync('audio', { recursive: true });

/* ---------------- 1. 时长对齐 ---------------- */
const cfgPath = 'src/config.js';
if (fs.existsSync(cfgPath)) {
  const cfg = fs.readFileSync(cfgPath, 'utf8');
  const m = cfg.match(/duration:\s*([\d.]+)/);
  if (m && Math.abs(Number(m[1]) - duration) > 0.01) {
    fs.writeFileSync(cfgPath, cfg.replace(/duration:\s*[\d.]+/, `duration: ${duration}`));
    console.log(`config.js duration: ${m[1]} → ${duration}`);
  }
}

/* ---------------- 2. 音乐 + 节拍网格 ---------------- */
if (skipMusic) {
  if (!userAudio) throw new Error('--skip-music 需要同时给 --audio <文件>');
  if (path.resolve(userAudio) !== path.resolve(musicPath)) {
    fs.copyFileSync(userAudio, musicPath);
  }
  console.log(`music 用现有文件 ${musicPath}`);
  if (!fs.existsSync(gridPath)) {
    console.log('缺少 beats.json：画面将按 120 BPM 兜底；建议用 --bpm 或重跑音乐生成器');
  }
} else {
  step(`合成配乐（${preset}${bpm ? ` / ${bpm} BPM` : ''}）`);
  const py = process.env.PYTHON || 'python3';
  // 找到 make_music.py：项目自带 → skill 的 starter/ 旁边 → 常见 skill 安装位置
  const here = path.dirname(new URL(import.meta.url).pathname);
  const home = process.env.HOME || '';
  const candidates = [
    process.env.STORYFRAME_SKILL_DIR && path.join(process.env.STORYFRAME_SKILL_DIR, 'scripts/make_music.py'),
    path.resolve('scripts/make_music.py'),
    path.resolve('../scripts/make_music.py'),
    path.join(here, '..', 'scripts', 'make_music.py'),
    home && path.join(home, '.agents/skills/storyframe-video-skill/scripts/make_music.py'),
    home && path.join(home, '.mirasim/skills/storyframe-video-skill/scripts/make_music.py'),
    home && path.join(home, '.claude/skills/storyframe-video-skill/scripts/make_music.py'),
  ].filter(Boolean);
  const script = candidates.find((p) => fs.existsSync(p));
  if (!fs.existsSync(script)) {
    console.log('找不到 make_music.py；跳过配乐，按无音乐渲染');
  } else {
    run(py, [script, '--preset', preset, '--duration', String(duration), '--out', musicPath,
      '--grid', gridPath, ...(bpm ? ['--bpm', String(bpm)] : [])]);
  }
}

/* ---------------- 3. 预览 ---------------- */
step('渲染预览（640 短边 / 24fps）');
const previewOut = 'videos/preview.mp4';
run('node', ['render.mjs', '--preview', '--from', '0', '--to', String(duration),
  ...(fs.existsSync(musicPath) ? ['--audio', musicPath] : []), '--output', previewOut]);

/* ---------------- 4. 终版 ---------------- */
let finalOut = null;
if (!previewOnly) {
  step(`渲染终版（${PROJECT.width}x${PROJECT.height} / ${fps}fps / 硬件编码优先）`);
  finalOut = 'videos/final.mp4';
  run('node', ['render.mjs', '--from', '0', '--to', String(duration), '--fps', String(fps),
    ...(fs.existsSync(musicPath) ? ['--audio', musicPath] : []),
    '--beat-sheet', '1', '--output', finalOut]);
}

/* ---------------- 5. 首帧静帧（给人工确认用，只有一张） ---------------- */
step('首帧静帧（640 短边）');
run('node', ['still.mjs', '0', '--preview', '--out-dir', 'renders/preview']);

/* ---------------- 6. 报告 ---------------- */
const dt = ((Date.now() - t0) / 1000).toFixed(1);
const size = (p) => (fs.existsSync(p) ? `${(fs.statSync(p).size / 1048576).toFixed(1)} MB` : '-');
let gridInfo = '-';
if (fs.existsSync(gridPath)) {
  try {
    const g = JSON.parse(fs.readFileSync(gridPath, 'utf8'));
    gridInfo = `${g.bpm} BPM · ${g.beats.length} 拍 · ${g.sections.map((s) => s.name).join('/')}`;
  } catch {}
}
console.log(`
──────── 出片报告 ────────
时长      ${duration}s @ ${fps}fps  ${PROJECT.width}x${PROJECT.height}
节拍      ${gridInfo}
音乐      ${fs.existsSync(musicPath) ? musicPath : '无'}
预览      ${previewOut}  ${size(previewOut)}
终版      ${finalOut ? `${finalOut}  ${size(finalOut)}` : '未渲染（--final / 去掉 --preview-only）'}
QA 缩略图 renders/beats/
总耗时    ${dt}s
下一步    看 preview.mp4 的节奏和卡点；结构没问题再去渲染/精修细节
──────────────────────────`);
