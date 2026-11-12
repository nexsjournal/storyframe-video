import fs from 'node:fs';
import path from 'node:path';
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
  for (const p of CHROME_CANDIDATES) {
    if (fs.existsSync(p)) return p;
  }
  throw new Error('Chrome not found. Set CHROME_PATH to Chrome/Chromium.');
}

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  if (i >= 0 && process.argv[i + 1] != null) return process.argv[i + 1];
  return fallback;
}
const has = (name) => process.argv.includes(`--${name}`);
const preview = has('preview') || has('draft');

const raw = process.argv.slice(2);
const times = [];
for (let i = 0; i < raw.length; i++) {
  if (raw[i].startsWith('--')) {
    if (!['--preview', '--draft', '--keep-frames'].includes(raw[i])) i += 1;
    continue;
  }
  const n = Number(raw[i]);
  if (Number.isFinite(n)) times.push(n);
}
const shots = times.length ? times : [1, 3, 6];

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

const format = String(arg('format', preview ? 'jpeg' : 'png')).toLowerCase();
if (!['jpeg', 'jpg', 'png'].includes(format)) throw new Error('--format must be jpeg or png');
const ext = format === 'png' ? 'png' : 'jpg';
const quality = Number(arg('quality', preview ? 72 : 92));
if (!(quality >= 1 && quality <= 100)) throw new Error('--quality must be 1..100');
const outDir = arg('out-dir', preview ? 'renders/preview' : 'renders');
const prefix = arg('prefix', preview ? 'preview' : 'still');

const { server, url } = await startServer(process.cwd());
const browser = await chromium.launch({
  executablePath: findChrome(),
  headless: true,
  args: ['--hide-scrollbars', '--force-device-scale-factor=1'],
});
const page = await browser.newPage({ viewport: { width, height } });
await page.goto(url, { waitUntil: 'load' });
await page.waitForFunction(() => window.__READY__ === true);
fs.mkdirSync(outDir, { recursive: true });

for (const t of shots) {
  await page.evaluate((time) => window.seek(time), t);
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(r)));
  const out = path.join(outDir, `${prefix}_${t.toFixed(2)}.${ext}`);
  await page.screenshot({
    path: out,
    type: ext === 'png' ? 'png' : 'jpeg',
    ...(ext === 'png' ? {} : { quality }),
  });
  console.log('still', out, `${width}x${height}`);
}

await browser.close();
await new Promise((r) => server.close(r));
