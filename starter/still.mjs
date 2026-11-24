#!/usr/bin/env node
/**
 * still.mjs v2 —— 低分辨率静帧 / 每拍一帧的 contact sheet
 *
 * 规则：静帧只用来判断构图和首帧，不用来审片。
 * 默认参数就是"够看"：--preview 640 短边、JPEG q72。
 *
 * 用法：
 *   node still.mjs 0 3 6.5 --preview
 *   node still.mjs --beat-sheet --beats audio/beats.json --out-dir renders/beats
 *   node still.mjs 0 6 --preview --sheet renders/sheet.jpg
 */
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { chromium } from 'playwright-core';
import { PROJECT } from './src/config.js';
import { startServer } from './server.mjs';

const argv = process.argv.slice(2);
const arg = (n, d) => {
  const i = argv.indexOf(`--${n}`);
  if (i >= 0 && argv[i + 1] != null && !argv[i + 1].startsWith('--')) return argv[i + 1];
  return d;
};
const has = (n) => argv.includes(`--${n}`);
const preview = has('preview') || has('draft');

const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
].filter(Boolean);
const findChrome = () => {
  for (const p of CHROME_CANDIDATES) if (p && fs.existsSync(p)) return p;
  throw new Error('找不到 Chrome / Chromium；用 CHROME_PATH 指定。');
};

const FAST_ARGS = [
  '--hide-scrollbars',
  '--force-device-scale-factor=1',
  '--deterministic-mode',
  '--run-all-compositor-stages-before-draw',
  '--disable-gpu-vsync',
  '--disable-frame-rate-limit',
];

/* ---- 时间点：命令行数字 / 每拍一帧 / 等分 ---- */
let times = [];
const beatSheet = has('beat-sheet');
const beatsFile = arg('beats', 'audio/beats.json');
if (beatSheet) {
  if (fs.existsSync(beatsFile)) {
    const g = JSON.parse(fs.readFileSync(beatsFile, 'utf8'));
    const every = Number(arg('every', 2)); // 默认每 2 拍一张
    times = (g.beats || []).filter((_, i) => i % every === 0).map((t) => Math.min(t, g.duration - 0.001));
  } else {
    const beat = 60 / (PROJECT.bpm || 120);
    for (let t = 0; t < PROJECT.duration; t += beat) times.push(t);
  }
} else {
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      if (!['--preview', '--draft', '--beat-sheet', '--sheet'].includes(argv[i])) i += 1;
      continue;
    }
    const n = Number(argv[i]);
    if (Number.isFinite(n)) times.push(n);
  }
}
if (!times.length) times = [0, PROJECT.duration / 2, PROJECT.duration - 0.05];

/* ---- 尺寸 ---- */
const aspect = PROJECT.width / PROJECT.height;
let width = Number(arg('width', NaN));
let height = Number(arg('height', NaN));
if (!Number.isFinite(width) && !Number.isFinite(height)) {
  if (preview) {
    if (PROJECT.width >= PROJECT.height) {
      width = 640;
      height = Math.round(640 / aspect);
    } else {
      height = 640;
      width = Math.round(640 * aspect);
    }
  } else {
    width = PROJECT.width;
    height = PROJECT.height;
  }
} else if (Number.isFinite(width) && !Number.isFinite(height)) height = Math.round(width / aspect);
else if (!Number.isFinite(width) && Number.isFinite(height)) width = Math.round(height * aspect);

const format = String(arg('format', preview ? 'jpeg' : 'jpeg')).toLowerCase();
const ext = format === 'png' ? 'png' : 'jpg';
const quality = Number(arg('quality', preview ? 72 : 88));
const outDir = arg('out-dir', preview ? 'renders/preview' : 'renders');
fs.mkdirSync(outDir, { recursive: true });

/* ---- 采集 ---- */
const { server, url } = await startServer(process.cwd());
const browser = await chromium.launch({ executablePath: findChrome(), headless: true, args: FAST_ARGS });
const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
await page.goto(url, { waitUntil: 'load' });
await page.waitForFunction(() => window.__READY__ === true, null, { timeout: 60000 });
const mode = await page.evaluate(() => window.__CAPTURE__ || 'dom');
const cdp = mode === 'canvas' ? null : await page.context().newCDPSession(page);

const files = [];
for (const t of times) {
  await page.evaluate((time) => window.seek(time), t);
  let buf;
  if (mode === 'canvas') {
    buf = Buffer.from(await page.evaluate((q) => window.__frameJPEG(q), quality), 'base64');
  } else {
    const shot = await cdp.send('Page.captureScreenshot', {
      format: ext === 'png' ? 'png' : 'jpeg',
      ...(ext === 'png' ? {} : { quality }),
      optimizeForSpeed: true,
    });
    buf = Buffer.from(shot.data, 'base64');
  }
  const file = path.join(outDir, `still_${t.toFixed(2)}.${ext}`);
  fs.writeFileSync(file, buf);
  files.push(file);
}
await browser.close();
await new Promise((r) => server.close(r));
console.log(`stills ${files.length} 张 @ ${width}x${height} → ${outDir}`);

/* ---- 可选：拼一张对比表 ---- */
const sheet = arg('sheet', null);
if (sheet && files.length > 1) {
  const cols = Number(arg('cols', files.length <= 4 ? 2 : 4));
  const tile = `${cols}x${Math.ceil(files.length / cols)}`;
  const r = spawnSync('ffmpeg', [
    '-y', '-hide_banner', '-loglevel', 'error',
    '-pattern_type', 'glob', '-i', path.join(outDir, `still_*.${ext}`),
    '-vf', `scale=480:-1,tile=${tile}:padding=8:margin=8:color=0x111111`,
    '-frames:v', '1', sheet,
  ], { stdio: 'inherit' });
  if (r.status === 0) console.log(`sheet ${sheet} (${tile})`);
}
