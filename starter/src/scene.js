/**
 * scene.js —— 默认演示片：一拍，一帧（12s / 120 BPM / 24 拍）
 *
 * 这个文件是模板：把 S1..S6 换掉就是你的片子。
 * 规则只有三条：
 *   1) 所有画面 = f(t)，t 是唯一输入；没有 timer、没有帧间状态
 *   2) 每个切点、每次入场都落在 beats.json 的拍点上
 *   3) 只画 Canvas2D 图形与文字，不叠滤镜（滤镜让光栅成本翻几倍）
 */
import { PROJECT } from './config.js';
import {
  Stage, Grid, PALETTE, TAU, clamp, lerp, inv, ease, spring, hit,
  roundRect, line, drawGridLines, count, setFont, charLayout,
} from './stage.js';

const { paper, ink, accent, accent2 } = PALETTE;

/* --- 节拍：优先读 audio/beats.json（音乐生成器产出），否则按 120 BPM 兜底 --- */
const FALLBACK = new Grid({ bpm: 120, duration: PROJECT.duration });
let grid = FALLBACK;

async function loadGrid() {
  try {
    const res = await fetch('audio/beats.json', { cache: 'no-store' });
    if (!res.ok) return FALLBACK;
    const json = await res.json();
    if (!json || !json.bpm || !json.beatDur) return FALLBACK;
    return Grid.from(json);
  } catch {
    return FALLBACK;
  }
}

const stage = new Stage(document.getElementById('stage'), { width: PROJECT.width, height: PROJECT.height });
const ctx = stage.ctx;
const W = PROJECT.width;
const H = PROJECT.height;
const M = 120;

/* ------------------------------------------------------------------ 组件 */

function topline(left, right, dark = false) {
  setFont(ctx, { size: 20, weight: 600, spacing: 3 });
  ctx.fillStyle = dark ? 'rgba(242,237,225,0.62)' : 'rgba(20,18,25,0.55)';
  ctx.textAlign = 'left';
  ctx.fillText(left, M, 92);
  ctx.textAlign = 'right';
  ctx.fillText(right, W - M, 92);
  ctx.textAlign = 'left';
  line(ctx, M, 112, W - M, 112, 1, dark ? 'rgba(242,237,225,0.18)' : 'rgba(20,18,25,0.14)');
}

/** 大字逐字入场：每字一条闭式弹簧；负的 start 让首帧就是完成态 */
function bigType(text, { x, y, size, color, weight = 800, start = 0, stagger = 0.04, dur = 0.5, rise = 120, tracking = -4 }) {
  const layout = charLayout(ctx, text, { x, y, size, weight, spacing: tracking });
  for (const item of layout) {
    const p = spring(tLocal - start - item.i * stagger, { dur, freq: 8.5, damp: 7.5 });
    if (p <= 0.001) continue;
    ctx.save();
    ctx.globalAlpha = clamp(p * 1.8);
    ctx.translate(item.x + item.w / 2, item.y + (1 - p) * rise);
    ctx.fillStyle = color;
    ctx.fillText(item.ch, -item.w / 2, 0);
    ctx.restore();
  }
  return layout;
}

let tGlobal = 0; // 全片时间
let tLocal = 0; // 当前镜头内时间

/* ------------------------------------------------------------------ S1 开场（0–2s） */

function S1(t) {
  const local = t;
  ctx.fillStyle = paper;
  ctx.fillRect(0, 0, W, H);

  drawGridLines(ctx, { x: 0, y: 0, w: W, h: H, step: 120, p: ease.inOut(inv(-0.35, 0.5, local)), color: 'rgba(20,18,25,0.075)' });

  // 右侧：拍弧（开场就完整，兼顾构图平衡）
  ctx.save();
  ctx.translate(W - 470, 430);
  for (let i = 0; i < 5; i++) {
    const ph = hit(local, grid.beat(i), 5);
    ctx.strokeStyle = `rgba(20,18,25,${0.10 + 0.06 * i + ph * 0.12})`;
    ctx.lineWidth = 2 + ph * 2;
    ctx.beginPath();
    ctx.arc(0, 0, 90 + i * 74 + ph * 10, -0.55, 0.55);
    ctx.stroke();
  }
  // 拍针
  const bi = grid.beatIndex(local);
  const ang = -0.55 + (bi % 1) * 0.06;
  ctx.strokeStyle = accent;
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(Math.cos(ang - Math.PI / 2 + 0.55) * 400, Math.sin(ang - Math.PI / 2 + 0.55) * 400);
  ctx.stroke();
  ctx.restore();

  topline('STORYFRAME / 001', 'A PURE FUNCTION OF t');

  setFont(ctx, { size: 26, weight: 600, spacing: 4 });
  ctx.fillStyle = accent;
  ctx.fillText('MOTION / 一拍一帧', M, 210);

  bigType('一拍', { x: M - 8, y: 470, size: 210, color: ink, weight: 800, start: -0.6, rise: 0 });
  bigType('一帧', { x: M - 8, y: 690, size: 210, color: accent, weight: 800, start: -0.1, rise: 0 });

  // 第 3 拍：强调块横扫
  const sw = ease.outQuint(inv(grid.beat(3) - 0.02, grid.beat(3) + 0.45, local));
  if (sw > 0.001) {
    ctx.save();
    ctx.globalAlpha = 0.12;
    ctx.fillStyle = accent2;
    ctx.fillRect(M - 20, 250, (W - M * 2 + 40) * sw, 500);
    ctx.restore();
  }

  setFont(ctx, { size: 30, weight: 400 });
  ctx.fillStyle = 'rgba(20,18,25,0.72)';
  ctx.fillText(`${PROJECT.duration} 秒 · ${grid.bpm} BPM · ${Math.round(PROJECT.duration / grid.beatDur)} 拍 · 每个切点落在拍上`, M, 810);

  setFont(ctx, { size: 22, weight: 600, spacing: 2 });
  ctx.fillStyle = 'rgba(20,18,25,0.45)';
  ctx.fillText(`BPM ${grid.bpm}  /  BEAT ${grid.beatDur.toFixed(3)}s`, M, 870);

  // 底部节拍条
  const cur = Math.floor(grid.beatIndex(local));
  for (let i = 0; i < 24; i++) {
    const on = i <= cur;
    const h = on ? 10 + hit(local, grid.beat(i), 8) * 40 : 10;
    ctx.fillStyle = on ? accent : 'rgba(20,18,25,0.16)';
    ctx.fillRect(W - M - (24 - i) * 22 + 12, 880 - h, 9, h);
  }

  // 切点闪光
  const flash = hit(local, 0, 6);
  if (flash > 0.02) {
    ctx.fillStyle = `rgba(255,59,92,${flash * 0.35})`;
    ctx.fillRect(0, 0, W, 5);
  }
}

/* ------------------------------------------------------------------ S2 三张卡（2–5s） */

const CARDS = [
  { label: 'RENDER', value: 100, unit: '帧 / 秒', note: '单进程 · 不写磁盘', color: accent, decimals: 0 },
  { label: 'BUILD', value: 3.6, unit: '秒', note: '360 帧 1080p30', color: accent2, decimals: 1 },
  { label: 'COMMAND', value: 1, unit: '条命令', note: '音乐 → 渲染 → 成片', color: paper, decimals: 0 },
];

function S2(t, local) {
  ctx.fillStyle = ink;
  ctx.fillRect(0, 0, W, H);
  topline('03 NUMBERS', 'EVERY BEAT, ONE CARD', true);

  const flash = hit(local, 0, 6);
  if (flash > 0.03) {
    ctx.fillStyle = `rgba(255,255,255,${flash * 0.05})`;
    ctx.fillRect(0, 0, W, H);
  }

  // 右侧幽灵数字：保证任何时刻画面都不空
  setFont(ctx, { size: 300, weight: 800 });
  ctx.fillStyle = 'rgba(242,237,225,0.045)';
  ctx.textAlign = 'right';
  ctx.fillText('03', W - M + 14, 470);
  ctx.textAlign = 'left';
  ctx.save();
  ctx.translate(W - M + 6, 560);
  ctx.rotate(Math.PI / 2);
  setFont(ctx, { size: 18, weight: 600, spacing: 5 });
  ctx.fillStyle = 'rgba(242,237,225,0.28)';
  ctx.fillText('THREE NUMBERS / THREE BEATS', 0, 0);
  ctx.restore();

  CARDS.forEach((card, i) => {
    const at = (i - 1) * grid.beatDur; // 首卡提前半拍就位，切点那一帧已有主体
    const p = spring(local - at, { dur: 0.52, freq: 8, damp: 7.2 });
    if (p <= 0.001) return;
    const x = M + i * 540;
    const y = 300 + (1 - p) * 150;
    const bw = 500;
    const bh = 470;

    ctx.save();
    ctx.globalAlpha = clamp(p * 1.4);
    ctx.translate(x, y);
    ctx.rotate((1 - p) * 0.02 * (i - 1));

    ctx.fillStyle = 'rgba(242,237,225,0.045)';
    roundRect(ctx, 0, 0, bw, bh, 26);
    ctx.fill();
    ctx.strokeStyle = 'rgba(242,237,225,0.13)';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    setFont(ctx, { size: 20, weight: 700, spacing: 4 });
    ctx.fillStyle = 'rgba(242,237,225,0.55)';
    ctx.fillText(card.label, 40, 62);

    setFont(ctx, { size: 118, weight: 800 });
    ctx.fillStyle = card.color;
    const cp = clamp((local - at - 0.05) / 0.55);
    ctx.fillText(count(ease.out(cp), card.value, { decimals: card.decimals }), 36, 230);

    setFont(ctx, { size: 30, weight: 500 });
    ctx.fillStyle = 'rgba(242,237,225,0.75)';
    ctx.fillText(card.unit, 40, 282);

    const barP = clamp((local - at - 0.1) / (grid.beatDur * 1.2));
    ctx.fillStyle = 'rgba(242,237,225,0.12)';
    roundRect(ctx, 40, 350, bw - 80, 6, 3);
    ctx.fill();
    ctx.fillStyle = card.color;
    roundRect(ctx, 40, 350, (bw - 80) * ease.out(barP), 6, 3);
    ctx.fill();

    setFont(ctx, { size: 24, weight: 400 });
    ctx.fillStyle = 'rgba(242,237,225,0.45)';
    ctx.fillText(card.note, 40, 420);
    ctx.restore();
  });

  const fp = ease.out(inv(grid.beatDur * 3 - 0.4, grid.beatDur * 3 + 0.4, local));
  if (fp > 0.01) {
    setFont(ctx, { size: 26, weight: 500, spacing: 3 });
    ctx.fillStyle = `rgba(242,237,225,${0.6 * fp})`;
    ctx.fillText('没有截帧、没有配音、没有等待', M, 900);
  }
}

/* ------------------------------------------------------------------ S3 卡点大字（5–7s） */

function S3(t, local) {
  ctx.fillStyle = accent;
  ctx.fillRect(0, 0, W, H);

  const b = grid.beatIndex(t);
  const beatStart = Math.floor(b);
  const ph = hit(t, grid.beat(beatStart), 9);
  const sc = 1 + ph * 0.05;

  ctx.save();
  ctx.translate(W / 2, H / 2 - 30);
  ctx.scale(sc, sc);
  setFont(ctx, { size: 340, weight: 800 });
  ctx.textAlign = 'center';
  ctx.fillStyle = ink;
  const p = spring(local + 0.55, { dur: 0.42, freq: 7.5, damp: 6.5 }); // 切进来就是完整大字，靠每拍缩放收节奏
  ctx.globalAlpha = clamp(p * 2);
  ctx.fillText('卡 点', 0, 60 * (1 - p));
  ctx.restore();

  ctx.save();
  ctx.globalAlpha = ease.out(inv(grid.beatDur, grid.beatDur + 0.45, local));
  setFont(ctx, { size: 34, weight: 500 });
  ctx.fillStyle = ink;
  ctx.textAlign = 'center';
  ctx.fillText('每一拍，画面必须动一下；每一刀，都切在拍点上', W / 2, H - 190);
  ctx.textAlign = 'left';
  ctx.restore();

  // 拍点刻度
  for (let i = 0; i < 4; i++) {
    const at = grid.beat(beatStart + i);
    const q = 1 - clamp((t - at) / grid.beatDur);
    ctx.fillStyle = i === 0 ? ink : `rgba(20,18,25,${0.22 + q * 0.65})`;
    ctx.beginPath();
    ctx.arc(W / 2 - 60 + i * 40, H - 110, 6 + q * 12, 0, TAU);
    ctx.fill();
  }
}

/* ------------------------------------------------------------------ S4 图表自绘（7–10s） */

function S4(t, local) {
  ctx.fillStyle = paper;
  ctx.fillRect(0, 0, W, H);
  drawGridLines(ctx, { x: M, y: 200, w: W - M * 2, h: 620, step: 124, color: 'rgba(20,18,25,0.06)' });
  topline('04 / DATA', 'DRAWN BY THE BEAT');

  const baseX = M;
  const baseY = 830;
  const chartW = W - M * 2;
  const bars = 12;
  const stepW = chartW / bars;
  const stepDur = grid.beatDur * 0.5;

  const localG = local + stepDur * 4; // 切进来已有 4 格，切点那一帧不空
  const grown = Math.floor(clamp(localG / stepDur, 0, bars));
  for (let i = 0; i <= Math.min(grown, bars - 1); i++) {
    const q = clamp((localG - i * stepDur) / (stepDur * 0.9));
    const hgt = (70 + Math.abs(Math.sin(i * 1.7)) * 380) * ease.outQuint(q);
    ctx.fillStyle = i === grown ? accent : accent2;
    ctx.globalAlpha = 0.35 + 0.65 * q;
    roundRect(ctx, baseX + i * stepW + stepW * 0.22, baseY - hgt, stepW * 0.56, hgt, 8);
    ctx.fill();
  }
  ctx.globalAlpha = 1;

  const p = clamp(localG / (stepDur * 12), 0, 1);
  ctx.beginPath();
  ctx.strokeStyle = ink;
  ctx.lineWidth = 5;
  ctx.lineJoin = 'round';
  for (let i = 0; i <= 200; i++) {
    const u = (i / 200) * p;
    const x = baseX + u * chartW;
    const y = 640 - Math.sin(u * TAU * 1.2) * 90 - u * 130;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  line(ctx, baseX, baseY + 2, baseX + chartW * p, baseY + 2, 2, 'rgba(20,18,25,0.35)');

  setFont(ctx, { size: 18, weight: 600, spacing: 2 });
  for (let i = 0; i <= 12; i += 2) {
    ctx.fillStyle = 'rgba(20,18,25,0.35)';
    ctx.fillText(String(i), baseX + i * stepW + stepW * 0.22, baseY + 44);
  }
  setFont(ctx, { size: 26, weight: 600, spacing: 3 });
  ctx.fillStyle = 'rgba(20,18,25,0.55)';
  ctx.fillText(`BEAT ${Math.min(Math.round(PROJECT.duration / grid.beatDur), Math.floor(grid.beatIndex(t)))} / ${Math.round(PROJECT.duration / grid.beatDur)}`, M, 950);

  const tp = ease.out(inv(0, 0.5, local));
  setFont(ctx, { size: 44, weight: 700 });
  ctx.fillStyle = `rgba(20,18,25,${tp})`;
  ctx.fillText('数据跟着节奏长出来', M, 175);
}

/* ------------------------------------------------------------------ S5 时间轴（10–11s） */

function S5(t, local) {
  ctx.fillStyle = ink;
  ctx.fillRect(0, 0, W, H);
  topline('05 / TIMELINE', 'FRAME = f(t)', true);

  const x0 = M;
  const x1 = W - M;
  const y = 640;

  for (let i = 0; i <= 4; i++) {
    const at = i * grid.beatDur * 0.5;
    const x = x0 + (at / (grid.beatDur * 2)) * (x1 - x0);
    const hot = hit(local, at, 8);
    const isBar = i % 2 === 0;
    ctx.fillStyle = hot > 0.06 ? `rgba(255,59,92,${0.35 + hot * 0.65})` : 'rgba(242,237,225,0.22)';
    const hh = (isBar ? 96 : 52) * (1 + hot * 0.6);
    ctx.fillRect(x, y - hh / 2, 2, hh);
  }

  const p = clamp(local / (grid.beatDur * 2));
  const px = x0 + p * (x1 - x0);
  ctx.fillStyle = accent;
  ctx.fillRect(px - 2, y - 120, 4, 240);
  ctx.beginPath();
  ctx.arc(px, y - 132, 9, 0, TAU);
  ctx.fill();

  setFont(ctx, { size: 128, weight: 800 });
  ctx.fillStyle = paper;
  ctx.fillText('每一帧', M, 360);
  ctx.fillStyle = accent;
  ctx.fillText('只由 t 决定', M, 500);

  setFont(ctx, { size: 26, weight: 500, spacing: 2 });
  ctx.fillStyle = 'rgba(242,237,225,0.55)';
  ctx.fillText(`t = ${t.toFixed(2)}s   frame ${Math.round(t * PROJECT.fps)}`, M, 800);
}

/* ------------------------------------------------------------------ S6 收尾（11–12s） */

function S6(t, local) {
  ctx.fillStyle = paper;
  ctx.fillRect(0, 0, W, H);
  topline('STORYFRAME', 'END CARD');

  const p = spring(local + 0.35, { dur: 0.5, freq: 8, damp: 7 });
  const cx = W / 2;

  ctx.save();
  ctx.translate(cx, 470);
  ctx.rotate((1 - p) * -0.12);
  ctx.globalAlpha = clamp(p * 1.3);
  ctx.fillStyle = ink;
  roundRect(ctx, -70, -70, 140, 140, 34);
  ctx.fill();
  ctx.fillStyle = accent;
  roundRect(ctx, -34, -34, 68, 68, 16);
  ctx.fill();
  ctx.restore();

  const tp = ease.out(inv(-0.3, 0.4, local));
  ctx.save();
  ctx.globalAlpha = tp;
  ctx.textAlign = 'center';
  setFont(ctx, { size: 76, weight: 800, spacing: 2 });
  ctx.fillStyle = ink;
  ctx.fillText('Storyframe', cx, 700);

  setFont(ctx, { size: 30, weight: 400 });
  ctx.fillStyle = 'rgba(20,18,25,0.6)';
  ctx.fillText('写代码，出成片：一拍一帧，帧帧可复现', cx, 762);

  setFont(ctx, { size: 24, weight: 600, spacing: 3 });
  ctx.fillStyle = accent;
  ctx.fillText(`${grid.bpm} BPM · ${Math.round(PROJECT.duration / grid.beatDur)} BEATS · 0 抽帧 · 0 配音`, cx, 830);
  ctx.restore();
}

/* ------------------------------------------------------------------ 时间线：每个切点都在拍上 */

const BEAT = () => grid.beatDur;

/** 段落边界按"总拍数"的比例算，换 BPM / 换片长都不会错位（24 拍时正好是 4/10/14/20/22/24） */
function buildTimeline() {
  const nb = Math.max(8, Math.round(PROJECT.duration / BEAT()));
  const marks = [0, 0.17, 0.42, 0.58, 0.83, 0.92, 1].map((f, i, a) =>
    i === 0 ? 0 : i === a.length - 1 ? nb : Math.round(nb * f));
  // 保证边界严格递增
  for (let i = 1; i < marks.length; i++) marks[i] = Math.max(marks[i], marks[i - 1] + 1);
  marks[marks.length - 1] = nb;
  const at = (b) => Math.min(b * BEAT(), PROJECT.duration);
  const scene = [S1, S2, S3, S4, S5, S6];
  return scene.map((draw, i) => ({
    name: `S${i + 1}`,
    start: at(marks[i]),
    end: i === scene.length - 1 ? PROJECT.duration + 0.001 : at(marks[i + 1]),
    draw,
  }));
}

let timeline = [];

function seek(t) {
  tGlobal = clamp(t, 0, PROJECT.duration);
  stage.begin(PALETTE.ink);
  for (const s of timeline) {
    if (tGlobal < s.start - 0.0001 || tGlobal > s.end) continue;
    tLocal = tGlobal - s.start;
    // 硬切：切点落在拍上就是节拍本身，不需要淡入淡出
    ctx.save();
    s.draw(tGlobal, tLocal);
    ctx.restore();
  }
  stage.end();
}

window.seek = seek;
window.__CAPTURE__ = 'canvas';
window.__frameJPEG = (q) => stage.jpegBase64(q);
window.__READY__ = false;

(async () => {
  grid = await loadGrid();
  timeline = buildTimeline();
  window.__GRID__ = grid.toJSON();
  seek(0);
  window.__READY__ = true;
  document.fonts?.ready?.then(() => seek(tGlobal));
})();
