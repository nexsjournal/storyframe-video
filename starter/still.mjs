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

const times = process.argv.slice(2).map(Number).filter((n) => Number.isFinite(n));
const shots = times.length ? times : [1, 3, 6];

const { server, url } = await startServer(process.cwd());
const browser = await chromium.launch({
  executablePath: findChrome(),
  headless: true,
  args: ['--hide-scrollbars', '--force-device-scale-factor=1'],
});
const page = await browser.newPage({ viewport: { width: PROJECT.width, height: PROJECT.height } });
await page.goto(url, { waitUntil: 'load' });
await page.waitForFunction(() => window.__READY__ === true);
fs.mkdirSync('renders', { recursive: true });

for (const t of shots) {
  await page.evaluate((time) => window.seek(time), t);
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  const out = path.join('renders', `still_${t.toFixed(2)}.png`);
  await page.screenshot({ path: out, type: 'png' });
  console.log('still', out);
}

await browser.close();
await new Promise((r) => server.close(r));
