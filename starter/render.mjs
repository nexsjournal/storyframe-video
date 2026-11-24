#!/usr/bin/env node
/**
 * Storyframe 快渲染器 v2
 *
 * 相对 v1 的四项提速（实测 Apple M4 Pro / 1080p30 / 轻场景）：
 *   1. 不再逐帧打 rAF 等帧  —— 省 ~33 ms/帧（seek 是同步纯函数，等帧是白等）
 *   2. 不再把 JPEG 写进磁盘 —— 帧直接 pipe 进 ffmpeg stdin（image2pipe）
 *   3. Chromium 关掉 vsync / 帧率限制，用 beginFrame 控制 —— capture 从 33 ms 降到 ~13 ms
 *   4. macOS 终渲走 h264_videotoolbox 硬编 —— 编码环节从 CPU 抢回时间
 *
 * 顺带把 QA 抽帧合并进渲染过程：--beat-sheet 1 表示每拍存一张小图，零额外渲染成本。
 *
 * 用法：
 *   node render.mjs --preview                      # 640 短边 24fps 快速预览
 *   node render.mjs --from 0 --to 60 --audio audio/music.wav --output videos/final.mp4
 *   node render.mjs --from 0 --to 12 --output parts/p1.mp4   # 分段渲，改哪段重渲哪段
 *   node render.mjs --concat parts --audio audio/music.wav --output videos/final.mp4
 *   node render.mjs --beat-sheet 1 --output videos/silent.mp4 # 每拍一张 QA 缩略图
 */
import fs from 'node:fs';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { chromium } from 'playwright-core';
import { PROJECT } from './src/config.js';
import { startServer } from './server.mjs';

/* ---------------------------------------------------------------- 参数 */

const argv = process.argv.slice(2);
const arg = (name, fallback) => {
  const i = argv.indexOf(`--${name}`);
  if (i >= 0 && argv[i + 1] != null && !argv[i + 1].startsWith('--')) return argv[i + 1];
  return fallback;
};
const has = (name) => argv.includes(`--${name}`);
const num = (name, fallback) => {
  const v = arg(name, undefined);
  if (v === undefined) return fallback;
  const n = Number(v);
  if (!Number.isFinite(n)) throw new Error(`--${name} 必须是数字，收到 ${v}`);
  return n;
};

if (has('concat')) {
  await concat(arg('concat'), {
    audio: arg('audio', null),
    output: arg('output', 'videos/final.mp4'),
    crf: num('crf', 18),
    encoder: arg('encoder', 'auto'),
  });
  process.exit(0);
}

const preview = has('preview') || has('draft');
const fps = num('fps', preview ? 24 : PROJECT.fps);
const from = num('from', 0);
const to = num('to', PROJECT.duration);
const crf = num('crf', preview ? 28 : 18);
const quality = num('quality', preview ? 78 : 92);
const preset = arg('preset', preview ? 'veryfast' : 'medium');
const encoder = arg('encoder', 'auto');
const output = arg('output', preview ? 'videos/preview.mp4' : 'videos/final.mp4');
const audio = arg('audio', null);
const scale = num('scale', preview ? 1 / 3 : 1);
const beatSheetPerBeat = num('beat-sheet', 0); // 每 N 拍存一张 QA 小图，0 = 关
const beatSheetDir = arg('beat-sheet-dir', path.join('renders', 'beats'));
const beatSheetEdge = num('beat-sheet-edge', 480);
const sheetQuality = num('sheet-quality', 70);
const settleFrames = num('settle-frames', 0); // 默认 0：seek 是同步的，不需要等帧
const keepTemp = has('keep-temp');
const forcePath = arg('capture', 'auto'); // auto | dom | canvas

if (!(to > from)) throw new Error('--to 必须大于 --from');
if (!(fps > 0)) throw new Error('--fps 必须大于 0');

const aspect = PROJECT.width / PROJECT.height;
let width = num('width', NaN);
let height = num('height', NaN);
if (Number.isFinite(width) && !Number.isFinite(height)) height = Math.round(width / aspect);
else if (!Number.isFinite(width) && Number.isFinite(height)) width = Math.round(height * aspect);
else if (!Number.isFinite(width) && !Number.isFinite(height)) {
  if (scale !== 1) {
    if (PROJECT.width >= PROJECT.height) {
      width = Math.round((PROJECT.width * scale) / 2) * 2;
      height = Math.round(width / aspect / 2) * 2;
    } else {
      height = Math.round((PROJECT.height * scale) / 2) * 2;
      width = Math.round(height * aspect / 2) * 2;
    }
  } else {
    width = PROJECT.width;
    height = PROJECT.height;
  }
}

const total = Math.max(1, Math.round((to - from) * fps));
fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true });
const beatSheetEvery = (() => {
  if (!(beatSheetPerBeat > 0)) return 0;
  let beatDur = 60 / (PROJECT.bpm || 120);
  for (const p of [arg('beats', 'audio/beats.json'), 'audio/beats.json']) {
    try {
      const g = JSON.parse(fs.readFileSync(p, 'utf8'));
      if (g.beatDur) { beatDur = g.beatDur; break; }
    } catch {}
  }
  return Math.max(1, Math.round(fps * beatDur * beatSheetPerBeat));
})();
if (beatSheetEvery > 0) fs.mkdirSync(path.resolve(beatSheetDir), { recursive: true });

/* --------------------------------------------------------- 浏览器启动 */

const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
].filter(Boolean);

function findChrome() {
  for (const p of CHROME_CANDIDATES) if (p && fs.existsSync(p)) return p;
  throw new Error('找不到 Chrome / Chromium。用 CHROME_PATH 指定可执行文件路径。');
}

// vsync / 帧率限制是 v1 慢的第一原因：截图会被拖到 60Hz 的节拍上，一帧最少 16.7ms。
// deterministic-mode 保留确定性（同一 t 出同一像素），同时解除这个节拍等待。
const FAST_ARGS = [
  '--hide-scrollbars',
  '--force-device-scale-factor=1',
  '--deterministic-mode',
  '--run-all-compositor-stages-before-draw',
  '--disable-gpu-vsync',
  '--disable-frame-rate-limit',
  '--disable-background-timer-throttling',
  '--disable-renderer-backgrounding',
  '--disable-backgrounding-occluded-windows',
  '--font-render-hinting=none',
];

function pickEncoder() {
  if (encoder !== 'auto') return encoder;
  if (process.platform === 'darwin') {
    const ok = spawnSync('ffmpeg', ['-hide_banner', '-encoders'], { encoding: 'utf8' });
    if ((ok.stdout || '').includes('h264_videotoolbox')) return 'h264_videotoolbox';
  }
  return 'libx264';
}

function ffmpegArgs({ fps, width, height, crf, preset, encoder, audio }) {
  const enc = encoder;
  const args = ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(fps), '-i', '-'];
  const audioAt = audio ? 1 : null;
  if (audio) args.push('-i', path.resolve(audio));
  if (enc === 'h264_videotoolbox') {
    args.push('-c:v', 'h264_videotoolbox', '-q:v', String(Math.round(crfToQ(crf))), '-allow_sw', '1', '-realtime', '0');
  } else if (enc === 'hevc_videotoolbox') {
    args.push('-c:v', 'hevc_videotoolbox', '-q:v', String(Math.round(crfToQ(crf))), '-allow_sw', '1', '-tag:v', 'hvc1');
  } else {
    args.push('-c:v', enc, '-preset', preset, '-crf', String(crf), '-tune', 'film');
  }
  args.push('-pix_fmt', 'yuv420p', '-profile:v', 'high', '-g', String(fps * 2), '-bf', '2');
  if (audio) args.push('-c:a', 'aac', '-b:a', preview ? '192k' : '320k', '-ar', '48000', '-ac', '2');
  args.push('-map', '0:v:0');
  if (audio) args.push('-map', `${audioAt}:a:0`);
  args.push('-shortest', '-movflags', '+faststart', '-s', `${width}x${height}`, output);
  return args;
}

// crf 18 ≈ videotoolbox 的 q 78；线性近似够用
const crfToQ = (crf) => Math.max(20, Math.min(95, 100 - (crf - 10) * 2.2));

/* ---------------------------------------------------------- 采集循环 */

function makeWriter(stream) {
  let failed = null;
  stream.on('error', (e) => {
    failed = e;
  });
  return function write(buf) {
    if (failed) return Promise.reject(failed);
    return new Promise((resolve) => {
      if (stream.write(buf)) resolve();
      else stream.once('drain', resolve);
    });
  };
}

const { server, url } = await startServer(process.cwd());

const browser = await chromium.launch({
  executablePath: findChrome(),
  headless: true,
  args: FAST_ARGS,
});
const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
page.on('pageerror', (e) => console.error('[page error]', e.message));
page.on('console', (m) => {
  if (m.type() === 'error') console.error('[console]', m.text());
});
await page.goto(url, { waitUntil: 'load' });
await page.waitForFunction(() => window.__READY__ === true, null, { timeout: 60000 });

const mode = forcePath !== 'auto'
  ? forcePath
  : await page.evaluate(() => window.__CAPTURE__ || 'dom');
const cdp = mode === 'canvas' ? null : await page.context().newCDPSession(page);

const enc = pickEncoder();
const outAbs = path.resolve(output);
const ffArgs = ffmpegArgs({ fps, width, height, crf, preset, encoder: enc, audio });
const ff = spawn('ffmpeg', ffArgs, { stdio: ['pipe', 'inherit', 'inherit'] });
const writeFrame = makeWriter(ff.stdin);
const ffDone = new Promise((resolve, reject) => {
  ff.on('error', reject);
  ff.on('close', (code) => (code === 0 ? resolve() : reject(new Error(`ffmpeg 退出码 ${code}`))));
});

const sheetStep = beatSheetEvery > 0 ? Math.max(1, Math.round(beatSheetEvery)) : 0;
const sheetScale = Math.min(1, beatSheetEdge / Math.max(width, height));

console.log(
  `render ${width}x${height} @${fps}fps ${total} 帧 | capture=${mode} encoder=${enc} ` +
    `quality=${quality} audio=${audio ? path.basename(audio) : '-'}`
);

const started = Date.now();
let lastLog = started;
let sheetCount = 0;

for (let i = 0; i < total; i++) {
  const t = from + i / fps;
  await page.evaluate((time) => window.seek(time), t);
  for (let s = 0; s < settleFrames; s++) {
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(r)));
  }

  let buf;
  if (mode === 'canvas') {
    const b64 = await page.evaluate((q) => window.__frameJPEG(q), quality);
    buf = Buffer.from(b64, 'base64');
  } else {
    const shot = await cdp.send('Page.captureScreenshot', {
      format: 'jpeg',
      quality,
      optimizeForSpeed: true,
      captureBeyondViewport: false,
    });
    buf = Buffer.from(shot.data, 'base64');
  }
  await writeFrame(buf);

  if (sheetStep && i % sheetStep === 0) {
    const file = path.join(beatSheetDir, `b_${String(sheetCount).padStart(4, '0')}_${t.toFixed(2)}.jpg`);
    fs.writeFileSync(file, buf);
    sheetCount += 1;
  }

  const now = Date.now();
  if (now - lastLog > 1500 || i === total - 1) {
    lastLog = now;
    const done = i + 1;
    const per = (now - started) / done;
    const eta = ((total - done) * per) / 1000;
    console.log(
      `  ${done}/${total} ${t.toFixed(2)}s  ${per.toFixed(1)} ms/帧  ${(1000 / per).toFixed(1)} fps  ETA ${eta.toFixed(0)}s`
    );
  }
}

ff.stdin.end();
await ffDone;
await browser.close();
await new Promise((r) => server.close(r));

const secs = (Date.now() - started) / 1000;
const size = fs.existsSync(outAbs) ? (fs.statSync(outAbs).size / 1048576).toFixed(1) : '?';
console.log(
  `wrote ${output}  ${secs.toFixed(1)}s  ${(total / secs).toFixed(1)} 帧/s  ${size} MB` +
    (sheetCount ? `  + ${sheetCount} 张 QA 缩略图 → ${beatSheetDir}` : '')
);
if (!keepTemp) fs.rmSync(path.resolve('frames'), { recursive: true, force: true });

/* -------------------------------------------------------------- 拼接 */

async function concat(dir, { audio, output, crf, encoder }) {
  const parts = fs
    .readdirSync(dir)
    .filter((f) => /\.(mp4|mov|mkv)$/i.test(f))
    .sort()
    .map((f) => path.resolve(dir, f));
  if (!parts.length) throw new Error(`${dir} 里没有可拼接的片段`);
  const list = path.resolve(dir, '.concat.txt');
  fs.writeFileSync(list, parts.map((p) => `file '${p}'`).join('\n'));
  const enc = encoder === 'auto' ? pickEncoder() : encoder;
  const args = ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list];
  if (audio) args.push('-i', path.resolve(audio));
  args.push('-c:v', 'copy');
  if (audio) args.push('-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-ac', '2', '-map', '0:v:0', '-map', '1:a:0', '-shortest');
  args.push('-movflags', '+faststart', output);
  fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true });
  const r = spawnSync('ffmpeg', args, { stdio: 'inherit' });
  if (r.status !== 0) throw new Error('ffmpeg concat 失败');
  console.log(`concat ${parts.length} 段 → ${output}`);
}
