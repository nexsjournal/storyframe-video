/**
 * stage.js —— 画布舞台工具层
 *
 * 设计约束（这些约束就是渲染速度的来源，别破坏）：
 *   - 一切都由 seek(t) 算出来，没有 timer、没有 CSS transition、没有帧间状态
 *   - 只画 Canvas2D 图形与文字；不用 ctx.filter / shadowBlur 堆叠（它们让光栅成本翻几倍）
 *   - 画布尺寸 = 视口尺寸，不乘 devicePixelRatio，保证 640 预览和 1080 终版结构一致
 */

export const TAU = Math.PI * 2;
export const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
export const lerp = (a, b, p) => a + (b - a) * p;
export const inv = (a, b, x) => clamp((x - a) / (b - a));

export const ease = {
  out: (x) => 1 - Math.pow(1 - clamp(x), 3),
  outQuint: (x) => 1 - Math.pow(1 - clamp(x), 5),
  in: (x) => Math.pow(clamp(x), 3),
  inOut: (x) => (clamp(x) < 0.5 ? 4 * clamp(x) ** 3 : 1 - Math.pow(-2 * clamp(x) + 2, 3) / 2),
  expo: (x) => (clamp(x) === 1 ? 1 : 1 - Math.pow(2, -10 * clamp(x))),
  back: (x, s = 1.7) => {
    const c = clamp(x);
    return 1 + (s + 1) * Math.pow(c - 1, 3) + s * Math.pow(c - 1, 2);
  },
};

/**
 * 闭式弹簧（不是积分器）：给定起点/终点与时长，任意 t 直接算出值。
 * 帧间无状态 —— 这是"任意帧可单独渲染"的前提。
 */
export function spring(t, { from = 0, to = 1, dur = 0.55, freq = 9, damp = 7 } = {}) {
  const x = clamp(t / dur);
  const w = Math.PI * 2 * freq;
  const e = Math.exp(-damp * x);
  const v = 1 - e * (Math.cos(w * x) + (damp / w) * Math.sin(w * x));
  return from + (to - from) * v;
}

/** 打点包络：在 beat 时刻冲到 1，随后指数衰减。用来做"卡点"缩放/闪光。 */
export function hit(t, at, decay = 6) {
  const d = t - at;
  if (d < 0) return 0;
  return Math.exp(-d * decay);
}

/** 距离最近的重音时刻的脉冲（0..1），用于全局呼吸感 */
export function pulse(t, grid, { every = 1, decay = 7 } = {}) {
  const b = grid.beatIndex(t);
  const at = grid.beat(Math.floor(b / every) * every);
  return hit(t, at, decay);
}

/* ------------------------------------------------------------------ 节拍网格 */

export class Grid {
  constructor({ bpm = 120, beatsPerBar = 4, offset = 0, duration = 12, sections = [] } = {}) {
    this.bpm = bpm;
    this.beatDur = 60 / bpm;
    this.beatsPerBar = beatsPerBar;
    this.offset = offset;
    this.duration = duration;
    this.sections = sections;
  }
  static from(json) {
    return new Grid(json);
  }
  beat(n) {
    return this.offset + n * this.beatDur;
  }
  bar(n, beat = 0) {
    return this.beat(n * this.beatsPerBar + beat);
  }
  beatIndex(t) {
    return (t - this.offset) / this.beatDur;
  }
  /** 把任意时间吸附到最近的 1/sub 拍 */
  snap(t, sub = 1) {
    const step = this.beatDur / sub;
    return Math.round((t - this.offset) / step) * step + this.offset;
  }
  sectionAt(t) {
    let cur = null;
    for (const s of this.sections) if (t >= s.start) cur = s;
    return cur;
  }
  /** 第 n 拍起的能量（0..1），用于给段落切换配不同的运动强度 */
  energy(t) {
    const s = this.sectionAt(t);
    return s?.energy ?? 0.6;
  }
  toJSON() {
    const beats = [];
    for (let i = 0; this.beat(i) <= this.duration + 1e-6; i++) beats.push(+this.beat(i).toFixed(4));
    return {
      bpm: this.bpm,
      beatsPerBar: this.beatsPerBar,
      offset: this.offset,
      duration: this.duration,
      beatDur: +this.beatDur.toFixed(4),
      beats,
      bars: beats.filter((_, i) => i % this.beatsPerBar === 0),
      sections: this.sections,
    };
  }
}

/* ------------------------------------------------------------------ 画布舞台 */

export class Stage {
  constructor(canvas, { width = 1920, height = 1080 } = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d', { alpha: false, desynchronized: true });
    this.W = width;
    this.H = height;
    this.scale = 1;
    this.ox = 0;
    this.oy = 0;
    this.fit();
    window.addEventListener('resize', () => this.fit());
  }

  fit() {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    this.canvas.width = Math.max(2, vw);
    this.canvas.height = Math.max(2, vh);
    this.scale = Math.min(vw / this.W, vh / this.H);
    this.ox = (vw - this.W * this.scale) / 2;
    this.oy = (vh - this.H * this.scale) / 2;
  }

  /** 开始一帧：清屏 + 建立"1920×1080 设计坐标系" */
  begin(bg) {
    const { ctx } = this;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = bg || '#0E0D12';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.setTransform(this.scale, 0, 0, this.scale, this.ox, this.oy);
    ctx.save();
    return ctx;
  }

  end() {
    this.ctx.restore();
  }

  /** 页面级截图接口：渲染器检测到 __CAPTURE__==='canvas' 时走这条路（不经过合成器） */
  jpegBase64(quality = 92) {
    const url = this.canvas.toDataURL('image/jpeg', clamp(quality, 1, 100) / 100);
    return url.slice(url.indexOf(',') + 1);
  }
}

/* ------------------------------------------------------------------ 文字 */

export function setFont(ctx, { size = 48, weight = 700, family = 'Helvetica Neue, Arial, PingFang SC, sans-serif', spacing = 0 } = {}) {
  ctx.font = `${weight} ${size}px ${family}`;
  if ('letterSpacing' in ctx) ctx.letterSpacing = `${spacing}px`;
}

/** 逐字入场：返回每字的位置/透明度，绘制由调用方决定，便于做自定义动画 */
export function charLayout(ctx, text, { x, y, size, weight, spacing = 0, family } = {}) {
  setFont(ctx, { size, weight, spacing, family });
  const chars = [...text];
  const widths = chars.map((c) => ctx.measureText(c).width);
  const total = widths.reduce((a, b) => a + b, 0);
  let cx = x;
  return chars.map((c, i) => {
    const item = { ch: c, x: cx, y, w: widths[i], total, i };
    cx += widths[i] + spacing;
    return item;
  });
}

/** 简单换行：返回行数组（中文按字断，英文按词断） */
export function wrap(ctx, text, maxWidth) {
  const isCJK = /[\u4e00-\u9fa5]/.test(text);
  const units = isCJK ? [...text] : text.split(' ');
  const lines = [];
  let line = '';
  for (const u of units) {
    const next = isCJK ? line + u : line ? `${line} ${u}` : u;
    if (ctx.measureText(next).width > maxWidth && line) {
      lines.push(line);
      line = isCJK ? u : u;
    } else line = next;
  }
  if (line) lines.push(line);
  return lines;
}

/* ------------------------------------------------------------------ 图形 */

export function roundRect(ctx, x, y, w, h, r) {
  const rr = Math.min(r, Math.abs(w) / 2, Math.abs(h) / 2);
  ctx.beginPath();
  ctx.moveTo(x + rr, y);
  ctx.arcTo(x + w, y, x + w, y + h, rr);
  ctx.arcTo(x + w, y + h, x, y + h, rr);
  ctx.arcTo(x, y + h, x, y, rr);
  ctx.arcTo(x, y, x + w, y, rr);
  ctx.closePath();
}

export function line(ctx, x1, y1, x2, y2, width = 2, color = '#fff') {
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();
}

/** 网格线，带绘制进度，可做"背景在建"的运动 */
export function drawGridLines(ctx, { x = 0, y = 0, w = 1920, h = 1080, step = 96, color = 'rgba(20,18,26,0.10)', p = 1 } = {}) {
  if (p <= 0) return;
  ctx.save();
  ctx.strokeStyle = color;
  ctx.lineWidth = 1;
  ctx.beginPath();
  for (let gx = x; gx <= x + w + 0.5; gx += step) {
    const q = clamp((p - (gx - x) / w) * 3);
    if (q <= 0) continue;
    ctx.moveTo(gx, y);
    ctx.lineTo(gx, y + h * q);
  }
  for (let gy = y; gy <= y + h + 0.5; gy += step) {
    const q = clamp((p - (gy - y) / h) * 3);
    if (q <= 0) continue;
    ctx.moveTo(x, gy);
    ctx.lineTo(x + w * q, gy);
  }
  ctx.stroke();
  ctx.restore();
}

/** 数字滚动：按进度从 0 走到目标值 */
export function count(p, to, { from = 0, decimals = 0, group = true } = {}) {
  const v = from + (to - from) * clamp(p);
  const s = v.toFixed(decimals);
  if (!group) return s;
  const [i, d] = s.split('.');
  return i.replace(/\B(?=(\d{3})+(?!\d))/g, ',') + (d ? `.${d}` : '');
}

export const PALETTE = {
  paper: '#F2EDE1',
  ink: '#141219',
  accent: '#FF3B5C',
  accent2: '#1E6F5C',
  muted: '#8A8595',
};
