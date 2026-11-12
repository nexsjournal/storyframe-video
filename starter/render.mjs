import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { chromium } from 'playwright-core';
import { PROJECT } from './src/config.js';
import { startServer } from './server.mjs';

const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
].filter(Boolean);

function findChrome() {
  for (const p of CHROME_CANDIDATES) if (fs.existsSync(p)) return p;
  throw new Error('Chrome not found. Set CHROME_PATH to Chrome/Chromium.');
}

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  if (i >= 0 && process.argv[i + 1] != null) return process.argv[i + 1];
  return fallback;
}
const has = (name) => process.argv.includes(`--${name}`);
const preview = has('preview') || has('draft');

const from = Number(arg('from', 0));
const to = Number(arg('to', PROJECT.duration));
const fps = Number(arg('fps', preview ? 12 : PROJECT.fps));
let width = Number(arg('width', NaN));
let height = Number(arg('height', NaN));
if (preview) {
  const longEdge = Number(arg('long-edge', 640));
  const aspect = PROJECT.width / PROJECT.height;
  if (Number.isFinite(width) && !Number.isFinite(height)) height = Math.round(width / aspect);
  else if (!Number.isFinite(width) && Number.isFinite(height)) width = Math.round(height * aspect);
  else if (!Number.isFinite(width) && !Number.isFinite(height)) {
    if (PROJECT.width >= PROJECT.height) {
      width = longEdge;
      height = Math.round(longEdge / aspect);
    } else {
      height = longEdge;
      width = Math.round(longEdge * aspect);
    }
  }
} else {
  width = Number.isFinite(width) ? width : PROJECT.width;
  height = Number.isFinite(height) ? height : PROJECT.height;
}
const crf = Number(arg('crf', preview ? 30 : 18));
const preset = arg('preset', preview ? 'veryfast' : 'medium');
const quality = Number(arg('quality', preview ? 72 : 90));
const settleFrames = Number(arg('settle-frames', preview ? 1 : 2));
const output = arg('output', preview ? 'videos/preview.mp4' : 'videos/test.mp4');
const audio = arg('audio', null);
const keepFrames = has('keep-frames');

if (!(to > from)) throw new Error('--to must be greater than --from');
if (!(fps > 0)) throw new Error('--fps must be > 0');
if (!(width > 0 && height > 0)) throw new Error('--width/--height must be > 0');
if (!(quality >= 1 && quality <= 100)) throw new Error('--quality must be 1..100');
if (!Number.isInteger(settleFrames) || settleFrames < 0) throw new Error('--settle-frames must be >= 0');

const framesDir = path.resolve('frames');
fs.rmSync(framesDir, { recursive: true, force: true });
fs.mkdirSync(framesDir, { recursive: true });
fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true });

const { server, url } = await startServer(process.cwd());
const browser = await chromium.launch({
  executablePath: findChrome(),
  headless: true,
  args: ['--hide-scrollbars', '--force-device-scale-factor=1'],
});
const page = await browser.newPage({ viewport: { width, height } });
await page.goto(url, { waitUntil: 'load' });
await page.waitForFunction(() => window.__READY__ === true);

const total = Math.ceil((to - from) * fps);
const started = Date.now();
for (let i = 0; i < total; i++) {
  const t = from + i / fps;
  await page.evaluate((time) => window.seek(time), t);
  for (let s = 0; s < settleFrames; s++) {
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(r)));
  }
  await page.screenshot({
    path: path.join(framesDir, `f_${String(i).padStart(5, '0')}.jpg`),
    type: 'jpeg',
    quality,
  });
  if (i % 30 === 0 || i === total - 1) {
    console.log(`frame ${i + 1}/${total} t=${t.toFixed(2)} ${(Date.now() - started) / 1000}s`);
  }
}
await browser.close();
await new Promise((r) => server.close(r));

const args = [
  '-y',
  '-framerate', String(fps),
  '-i', path.join(framesDir, 'f_%05d.jpg'),
];
if (audio) args.push('-i', path.resolve(audio));
args.push(
  '-c:v', 'libx264',
  '-preset', preset,
  '-crf', String(crf),
  '-pix_fmt', 'yuv420p',
  '-profile:v', 'high',
  '-tune', 'film',
);
if (audio) args.push('-c:a', 'aac', '-b:a', preview ? '192k' : '320k', '-ar', '48000', '-ac', '2');
args.push('-map', '0:v:0');
if (audio) args.push('-map', '1:a:0');
args.push('-shortest', '-movflags', '+faststart', '-t', String(to - from), output);

console.log(
  `${preview ? 'preview' : 'final'} ${width}x${height} @ ${fps}fps crf=${crf} preset=${preset}`
);
console.log('ffmpeg', args.join(' '));
const ff = spawnSync('ffmpeg', args, { stdio: 'inherit' });
if (ff.status !== 0) throw new Error('ffmpeg failed');
if (!keepFrames) fs.rmSync(framesDir, { recursive: true, force: true });
console.log('wrote', output);
