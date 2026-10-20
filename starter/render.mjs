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

const from = Number(arg('from', 0));
const to = Number(arg('to', PROJECT.duration));
const fps = Number(arg('fps', PROJECT.fps));
const width = Number(arg('width', PROJECT.width));
const height = Number(arg('height', PROJECT.height));
const crf = Number(arg('crf', 18));
const output = arg('output', 'videos/test.mp4');
const audio = arg('audio', null);
const keepFrames = has('keep-frames');

if (!(to > from)) throw new Error('--to must be greater than --from');
if (!(fps > 0)) throw new Error('--fps must be > 0');

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
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  await page.screenshot({
    path: path.join(framesDir, `f_${String(i).padStart(5, '0')}.jpg`),
    type: 'jpeg',
    quality: 92,
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
  '-preset', 'slow',
  '-crf', String(crf),
  '-pix_fmt', 'yuv420p',
  '-profile:v', 'high',
  '-tune', 'film',
);
if (audio) args.push('-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-ac', '2');
args.push('-map', '0:v:0');
if (audio) args.push('-map', '1:a:0');
args.push('-shortest', '-movflags', '+faststart', '-t', String(to - from), output);

console.log('ffmpeg', args.join(' '));
const ff = spawnSync('ffmpeg', args, { stdio: 'inherit' });
if (ff.status !== 0) throw new Error('ffmpeg failed');
if (!keepFrames) fs.rmSync(framesDir, { recursive: true, force: true });
console.log('wrote', output);
