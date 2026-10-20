import { PROJECT } from "./config.js";

const stage = document.getElementById("stage");
const bg = document.getElementById("bg");
const grid = document.getElementById("grid");
const content = document.getElementById("content");
const progress = document.querySelector("#progress > i");

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const easeOut = (x) => 1 - Math.pow(1 - clamp(x), 3);
const easeInOut = (x) => {
  x = clamp(x);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
};

function fit() {
  const s = Math.min(window.innerWidth / PROJECT.width, window.innerHeight / PROJECT.height);
  stage.style.transform = `scale(${s})`;
  stage.style.left = `${(window.innerWidth - PROJECT.width * s) / 2}px`;
  stage.style.top = `${(window.innerHeight - PROJECT.height * s) / 2}px`;
}
window.addEventListener("resize", fit);
fit();

function charsHTML(text, accent = "") {
  const wanted = accent.toLowerCase();
  return text
    .split(/(\s+)/)
    .map((word) => {
      const clean = word.replace(/[^\w]/g, "").toLowerCase();
      const isAccent = Boolean(wanted) && clean === wanted;
      return [...word]
        .map((ch) => {
          const safe = ch === " " ? "&nbsp;" : ch;
          const hot = isAccent && /[A-Za-z]/.test(ch);
          return `<span class="ch${hot ? " accent" : ""}">${safe}</span>`;
        })
        .join("");
    })
    .join("");
}

function renderChars(el, p, { stagger = 0.035, rise = 80, blur = 10, rot = 0 } = {}) {
  const spans = el.querySelectorAll(".ch");
  const n = Math.max(1, spans.length);
  spans.forEach((s, i) => {
    const start = (i / n) * 0.35 + i * stagger;
    const q = p >= 1 ? 1 : easeOut((p - start) / 0.55);
    s.style.opacity = String(q);
    s.style.transform = `translateY(${(1 - q) * rise}px) rotate(${(1 - q) * rot}deg)`;
    s.style.filter = `blur(${(1 - q) * blur}px)`;
  });
}

const s1 = document.createElement("section");
s1.className = "scene s1";
s1.innerHTML = `
  <div class="topline"><span>STORYFRAME / 001</span><span class="muted">A deterministic starter</span></div>
  <div class="kicker">Make a video, not a slide</div>
  <h1 class="title">${charsHTML("Make it move.", "move")}<span class="swatch"></span></h1>
  <p class="sub">A 7.5 second motion test. Every frame is a pure function of <b>t</b>.</p>
  <div class="foot"><span>1920 × 1080</span><span>30 FPS</span><span>SEEK / SCREENSHOT / ENCODE</span></div>
`;

const s2 = document.createElement("section");
s2.className = "scene s2";
s2.innerHTML = `
  <div class="topline"><span>ONE IDEA PER SHOT</span><span class="muted">02 / 03</span></div>
  <div class="kicker">Build the frame</div>
  <h1 class="title medium">${charsHTML("Show the change.", "change")}</h1>
  <div class="cards">
    <article class="card"><div class="num">01 / HOOK</div><div class="big">First frame.</div><div class="desc">Complete before the animation starts.</div><div class="bar"></div></article>
    <article class="card"><div class="num">02 / MOTION</div><div class="big">One move.</div><div class="desc">Camera, type, or subject. Never all three.</div><div class="bar"></div></article>
    <article class="card"><div class="num">03 / SOUND</div><div class="big">One hit.</div><div class="desc">The action lands on the same frame.</div><div class="bar"></div></article>
  </div>
  <div class="foot"><span>STORY / EVIDENCE / TIME / SOUND</span><span>NO STATIC CARDS</span></div>
`;

const s3 = document.createElement("section");
s3.className = "scene s3";
s3.innerHTML = `
  <div class="topline"><span>YOUR TURN</span><span class="muted">03 / 03</span></div>
  <div class="kicker">Replace this scene</div>
  <h1 class="title">${charsHTML("Tell it in motion.", "motion")}</h1>
  <div class="pill"><span class="dot"></span>1920×1080 · 30fps · H.264</div>
  <p class="sub">Edit <b>src/main.js</b>, then render. The timeline is yours.</p>
  <div class="foot"><span>STORYFRAME</span><span>STILL / RENDER / CHECK</span></div>
`;

content.append(s1, s2, s3);

const cards = [...s2.querySelectorAll(".card")];
const bars = [...s2.querySelectorAll(".bar")];
const pill = s3.querySelector(".pill");
const s1Title = s1.querySelector(".title");
const s2Title = s2.querySelector(".title");
const s3Title = s3.querySelector(".title");
const s1Sub = s1.querySelector(".sub");

function sceneOpacity(t, a, b, fade = 0.22) {
  return clamp(Math.min((t - a) / fade, (b - t) / fade));
}

function seek(t) {
  const time = clamp(t, 0, PROJECT.duration);
  progress.style.width = `${(time / PROJECT.duration) * 100}%`;

  // background: slow drift, no wall-clock animation
  const p = time / PROJECT.duration;
  bg.style.transform = `translate3d(${-40 + p * 80}px, ${20 - p * 40}px, 0) scale(1.04)`;
  grid.style.transform = `rotate(${-2 + p * 1.5}deg) translate3d(${-p * 60}px, ${-p * 40}px, 0)`;

  // scene 1: complete first frame, subtle settle
  const o1 = clamp((2.7 - time) / 0.22);
  s1.style.display = o1 < 0.01 ? "none" : "flex";
  s1.style.opacity = String(o1);
  const settle = easeOut(clamp(time / 0.7));
  s1Title.style.transform = `translateY(${(1 - settle) * 10}px) scale(${1.02 - settle * 0.02})`;
  renderChars(s1Title, 1, { rise: 0, blur: 0 });
  s1Sub.style.opacity = String(easeOut(clamp((time - 0.9) / 0.7)) * 0.78);
  s1Sub.style.transform = `translateY(${(1 - easeOut(clamp((time - 0.9) / 0.7))) * 18}px)`;

  // scene 2
  const o2 = sceneOpacity(time, 2.6, 5.25);
  s2.style.display = o2 < 0.01 ? "none" : "flex";
  s2.style.opacity = String(o2);
  const p2 = clamp((time - 2.6) / 0.9);
  s2Title.style.transform = `translateY(${(1 - easeOut(p2)) * 40}px)`;
  renderChars(s2Title, clamp((time - 2.65) / 0.8), { stagger: 0.028, rise: 60, blur: 8 });
  cards.forEach((c, i) => {
    const q = easeOut(clamp((time - 2.85 - i * 0.12) / 0.55));
    c.style.opacity = String(q);
    c.style.transform = `translateY(${(1 - q) * 70}px) rotate(${(1 - q) * (i - 1) * 2}deg)`;
    bars[i].style.transform = `scaleX(${easeInOut(clamp((time - 3.0 - i * 0.12) / 0.5))})`;
  });

  // scene 3
  const o3 = clamp((time - 5.15) / 0.2);
  s3.style.display = o3 < 0.01 ? "none" : "flex";
  s3.style.opacity = String(o3);
  const p3 = clamp((time - 5.2) / 0.8);
  s3Title.style.transform = `translateY(${(1 - easeOut(p3)) * 46}px)`;
  renderChars(s3Title, clamp((time - 5.22) / 0.75), { stagger: 0.03, rise: 70, blur: 9 });
  const pq = easeOut(clamp((time - 5.6) / 0.5));
  pill.style.opacity = String(pq);
  pill.style.transform = `translateY(${(1 - pq) * 20}px)`;
}

window.seek = seek;
window.__READY__ = true;
seek(0);

document.fonts?.ready?.then(() => {
  seek(0);
  window.__READY__ = true;
});
