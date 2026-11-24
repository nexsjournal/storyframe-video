#!/usr/bin/env python3
"""代码合成背景音乐 + 节拍网格。

不用 Suno、不用素材库：一条命令同时产出
  audio/music.wav    48kHz 立体声，−14 LUFS 附近，带侧链/混响/限幅
  audio/beats.json   BPM、拍点、小节、段落、重音时间表（画面卡点用这张表）

六种预设：
  uplift     企业发布 / 产品宣传：四拍底鼓 + 明亮 pluck + 暖 pad，中高能量
  pulse      科技极简：半拍贝斯、短促 kick、高频 hat，冷、克制
  cinematic  预告 / 品牌片：低频 drone + 慢 pad + 战鼓，留白大
  edm        活动 / 快闪：128 BPM、全鼓组、offbeat bass、大 drop
  warm       轻 lo-fi：swing、黑胶噪声、柔和七和弦
  ambient    铺底：几乎无鼓，长和弦，适合口播

用法：
  python3 scripts/make_music.py --preset uplift --bpm 124 --duration 30 \
      --out audio/music.wav --grid audio/beats.json
  python3 scripts/make_music.py --preset pulse --duration 15 --bars-file plan.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import wave

import numpy as np

try:  # scipy 只是加速，没装也能跑
    from scipy.signal import lfilter, butter
    _HAS_SCIPY = True
except Exception:  # pragma: no cover
    _HAS_SCIPY = False

SR = 48000
rng = np.random.default_rng(7)

# --------------------------------------------------------------------------- 音阶 / 和弦

SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
}

# 每套预设：调性、和弦进行（相对主音的半音根音 + 和弦性质）、鼓型、乐器开关
PRESETS = {
    "uplift": dict(
        bpm=124, root=60, scale="major",
        prog=[(0, "maj"), (7, "maj"), (9, "min"), (5, "maj")],  # I V vi IV
        drums="four", bass="eighth", pad="sustain", arp="sixteenth",
        hat="eighth", energy=0.78, sparkle=True, swing=0.0,
    ),
    "pulse": dict(
        bpm=122, root=57, scale="minor",
        prog=[(0, "min"), (10, "maj"), (5, "min"), (7, "min")],
        drums="tech", bass="offbeat", pad="swell", arp="sixteenth",
        hat="sixteenth", energy=0.62, sparkle=False, swing=0.0,
    ),
    "cinematic": dict(
        bpm=96, root=52, scale="minor",
        prog=[(0, "min"), (8, "maj"), (3, "maj"), (10, "maj")],
        drums="taiko", bass="whole", pad="sustain", arp="none",
        hat="none", energy=0.55, sparkle=True, swing=0.0,
    ),
    "edm": dict(
        bpm=128, root=53, scale="minor",
        prog=[(0, "min"), (10, "maj"), (8, "maj"), (7, "maj")],
        drums="edm", bass="offbeat", pad="stab", arp="sixteenth",
        hat="sixteenth", energy=0.95, sparkle=True, swing=0.0,
    ),
    "warm": dict(
        bpm=98, root=58, scale="dorian",
        prog=[(0, "min7"), (5, "maj7"), (10, "maj7"), (3, "maj7")],
        drums="lofi", bass="eighth", pad="sustain", arp="eighth",
        hat="eighth", energy=0.45, sparkle=False, swing=0.14,
    ),
    "ambient": dict(
        bpm=84, root=55, scale="minor",
        prog=[(0, "min"), (5, "maj"), (8, "maj"), (7, "maj")],
        drums="none", bass="whole", pad="sustain", arp="none",
        hat="none", energy=0.3, sparkle=False, swing=0.0,
    ),
}

CHORD_INTERVALS = {
    "maj": [0, 4, 7], "min": [0, 3, 7], "maj7": [0, 4, 7, 11], "min7": [0, 3, 7, 10],
    "sus2": [0, 2, 7], "sus4": [0, 5, 7], "add9": [0, 4, 7, 14],
}


def midi_freq(m: float) -> float:
    return 440.0 * 2 ** ((m - 69) / 12.0)


# --------------------------------------------------------------------------- 结构

def plan_sections(bars: int) -> list[tuple[str, int]]:
    """把总小节数分给段落。返回 [(name, bars), ...]。"""
    if bars <= 2:
        return [("main", bars)]
    if bars <= 4:
        return [("intro", 1), ("main", bars - 2), ("outro", 1)]
    if bars <= 8:
        return [("intro", 1), ("build", 1), ("main", bars - 3), ("outro", 1)]
    if bars <= 16:
        build = 2
        brk = 1
        outro = 1
        intro = 2
        main = bars - intro - build - brk - outro
        return [("intro", intro), ("build", build), ("main", max(2, main - 4)), ("break", brk),
                ("main", max(2, 4)), ("outro", outro)]
    # 长曲：两段副歌
    intro, build, brk, outro = 2, 2, 2, 2
    rest = bars - intro - build - brk - outro
    first = max(4, int(rest * 0.45))
    second = rest - first
    return [("intro", intro), ("build", build), ("main", first), ("break", brk),
            ("main", second), ("outro", outro)]


SECTION_ENERGY = {
    "intro": 0.35, "build": 0.7, "main": 1.0, "break": 0.42, "outro": 0.4, "drop": 1.0,
}

# --------------------------------------------------------------------------- 鼓型

# 16 步（一小节 = 16 分音符 × 16）
DRUM_PATTERNS = {
    "four":  dict(kick="1000 1000 1000 1000", snare="0000 1000 0000 1000",
                  hat="1010 1010 1010 1010", clap="0000 1000 0000 1000", ghost="0000 0010 0000 0010"),
    "tech":  dict(kick="1000 0010 1000 0010", snare="0000 0000 0000 1000",
                  hat="1111 1111 1111 1111", clap="0000 0000 0000 0000", ghost="0000 0000 0100 0000"),
    "taiko": dict(kick="1000 0000 0100 0000", snare="0000 0000 0000 0000",
                  hat="0000 0000 0000 0000", clap="0000 0000 0000 0000", ghost="0000 1000 0000 1000"),
    "edm":   dict(kick="1000 1000 1000 1000", snare="0000 1000 0000 1000",
                  hat="0011 0011 0011 0011", clap="0000 1000 0000 1000", ghost="0000 0000 0000 0100"),
    "lofi":  dict(kick="1000 0000 0010 0000", snare="0000 1000 0000 1000",
                  hat="1010 0010 1010 0010", clap="0000 0000 0000 0000", ghost="0000 0000 0100 0000"),
    "none":  dict(kick="0000 0000 0000 0000", snare="0000 0000 0000 0000",
                  hat="0000 0000 0000 0000", clap="0000 0000 0000 0000", ghost="0000 0000 0000 0000"),
}


def parse_steps(pattern: str) -> list[int]:
    return [int(c) for c in pattern.replace(" ", "")]


def drum_hits(preset: dict, sections, bpm: float) -> tuple[list[dict], list[float]]:
    beat = 60.0 / bpm
    step = beat / 4
    pat = DRUM_PATTERNS[preset["drums"]]
    hits: list[dict] = []
    accents: list[float] = []
    b = 0
    for name, n in sections:
        e = SECTION_ENERGY[name] * preset["energy"] + 0.08
        for _ in range(n):
            bar_t = b * beat * 4
            for kind in ("kick", "snare", "clap", "hat", "ghost"):
                steps = parse_steps(pat[kind])
                for i, on in enumerate(steps):
                    if not on:
                        continue
                    # 低能量段落抽掉一部分弱拍
                    if e < 0.6 and kind in ("hat", "ghost") and i % 4 != 0:
                        continue
                    if name == "intro" and kind in ("snare", "clap") and b < 1:
                        continue
                    if name == "break" and kind == "kick" and i % 4 != 0:
                        continue
                    t = bar_t + i * step * (1 + (preset["swing"] if i % 2 else 0))
                    if t >= 0:
                        hits.append(dict(t=round(t, 5), kind=kind, gain=float(min(1.0, e))))
                    if kind in ("kick", "clap") and i % 4 == 0:
                        accents.append(round(t, 5))
            b += 1
    return hits, sorted(set(accents))


# --------------------------------------------------------------------------- 合成基元

def env_exp(n: int, decay: float, attack: float = 0.002) -> np.ndarray:
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-6), 0, 1)
    return a * np.exp(-t / max(decay, 1e-6))


def noise(n: int) -> np.ndarray:
    return rng.standard_normal(n)


def bandpass(x: np.ndarray, lo: float, hi: float, order: int = 2) -> np.ndarray:
    hi = min(hi, SR * 0.45)
    if lo >= hi:
        return x
    if _HAS_SCIPY:
        b, a = butter(order, [lo / (SR / 2), hi / (SR / 2)], btype="band")
        return lfilter(b, a, x)
    return fft_filter(x, lo, hi)


def lowpass(x: np.ndarray, f: float, order: int = 2) -> np.ndarray:
    if _HAS_SCIPY:
        b, a = butter(order, min(f, SR * 0.45) / (SR / 2), btype="low")
        return lfilter(b, a, x)
    return fft_filter(x, 20, f)


def highpass(x: np.ndarray, f: float, order: int = 2) -> np.ndarray:
    if _HAS_SCIPY:
        b, a = butter(order, max(f, 20) / (SR / 2), btype="high")
        return lfilter(b, a, x)
    return fft_filter(x, f, SR * 0.45)


def fft_filter(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """无 scipy 时的兜底：频域斜坡滤波"""
    n = len(x)
    if n < 8:
        return x
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    hi = min(hi, SR * 0.45)
    g = np.ones_like(f)
    if lo > 0:
        g *= 1 / (1 + (lo / np.maximum(f, 1e-6)) ** 4)
    g *= 1 / (1 + (f / max(hi, 1e-6)) ** 4)
    return np.fft.irfft(X * g, n)


def kick(decay=0.30, punch=1.0, f0=118, f1=44) -> np.ndarray:
    n = int(SR * (decay * 2.4))
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
    click = bandpass(noise(n), 1200, 6000) * np.exp(-t / 0.006) * 0.35 * punch
    return np.tanh((body + click) * 1.4) * 0.9


def snare() -> np.ndarray:
    n = int(SR * 0.22)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 186 * t) * np.exp(-t / 0.055) * 0.5
    nz = bandpass(noise(n), 1400, 7200) * np.exp(-t / 0.085)
    return (body + nz * 0.9) * 0.8


def clap() -> np.ndarray:
    n = int(SR * 0.26)
    out = np.zeros(n)
    for k, off in enumerate((0.0, 0.009, 0.019, 0.030)):
        i0 = int(off * SR)
        m = n - i0
        t = np.arange(m) / SR
        burst = bandpass(noise(m), 900, 5200) * np.exp(-t / (0.06 if k == 3 else 0.012))
        out[i0:] += burst * (0.55 if k == 3 else 1.0)
    return out * 0.5


def hat(open_: bool = False) -> np.ndarray:
    n = int(SR * (0.22 if open_ else 0.06))
    t = np.arange(n) / SR
    return highpass(noise(n), 7200) * np.exp(-t / (0.09 if open_ else 0.014)) * 0.35


def bass_note(freq: float, dur: float, kind="eighth") -> np.ndarray:
    n = int(SR * dur)
    t = np.arange(n) / SR
    saw = 2 * ((t * freq) % 1) - 1
    sub = np.sin(2 * np.pi * freq * t)
    x = saw * 0.45 + sub * 0.75
    x = lowpass(x, 420 + 900 * math.exp(-dur * 2))
    e = np.clip(t / 0.006, 0, 1) * np.exp(-t / (dur * 1.6 + 0.05))
    return x * e * 0.55


def pad_chord(freqs: list[float], dur: float, bright=0.5) -> np.ndarray:
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for det in (-1.004, -1.0, 1.0, 1.004):
            ph = rng.random()
            out += 2 * (((t * f * det + ph) % 1)) - 1
    out /= max(1, len(freqs) * 4)
    out = lowpass(out, 700 + 2600 * bright)
    a = np.clip(t / (dur * 0.35), 0, 1) ** 1.5
    r = np.clip((dur - t) / (dur * 0.4), 0, 1) ** 1.2
    return out * a * r * 0.42


def pluck(freq: float, dur=0.34, bright=0.6) -> np.ndarray:
    n = int(SR * dur)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for h in range(1, 7):
        if freq * h > 12000:
            break
        x += np.sin(2 * np.pi * freq * h * t) / (h ** (2.1 - bright))
    x *= np.exp(-t / (dur * 0.35))
    return lowpass(x, 5000) * 0.3


def riser(dur: float, f_lo=300, f_hi=9000) -> np.ndarray:
    n = int(SR * dur)
    t = np.arange(n) / SR
    nz = noise(n)
    seg = 8
    out = np.zeros(n)
    idx = np.linspace(0, n, seg + 1).astype(int)
    for i in range(seg):
        a, b = idx[i], idx[i + 1]
        p = i / seg
        out[a:b] = bandpass(nz[a:b], f_lo * (2 ** (p * 3)), f_hi)
    return out * (t / dur) ** 2.2 * 0.5


def impact() -> np.ndarray:
    n = int(SR * 1.2)
    t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * (52 * np.exp(-t / 0.25) + 28) * t) * np.exp(-t / 0.5)
    tail = lowpass(noise(n), 2000) * np.exp(-t / 0.22) * 0.4
    return np.tanh((sub + tail) * 1.5) * 0.7


def vinyl_noise(n: int) -> np.ndarray:
    h = highpass(noise(n), 1800) * 0.012
    cracks = np.zeros(n)
    pos = rng.integers(0, max(1, n - 400), size=max(1, n // 30000))
    for p in pos:
        cracks[p:p + 60] = noise(60) * np.exp(-np.arange(60) / 12) * 0.10
    return h + cracks


# --------------------------------------------------------------------------- 编曲

def build_events(preset: dict, bpm: float, bars: int):
    beat = 60.0 / bpm
    bar_dur = beat * 4
    sections = plan_sections(bars)
    prog = preset["prog"]

    notes: list[dict] = []
    fx: list[dict] = []
    b0 = 0
    for name, nbars in sections:
        e = SECTION_ENERGY[name]
        for k in range(nbars):
            bar_index = b0 + k
            bar_t = bar_index * bar_dur
            root_off, qual = prog[bar_index % len(prog)]
            chord_root = preset["root"] + root_off
            chord = [chord_root + i for i in CHORD_INTERVALS[qual]]
            last_bar_of_section = k == nbars - 1

            # --- pad
            if preset["pad"] == "sustain" and name not in ("break",) or name == "break" and k == 0:
                notes.append(dict(t=bar_t, dur=bar_dur * 1.02, kind="pad",
                                  midis=[m - 12 for m in chord], gain=0.5 * (0.5 + e * 0.6)))
            elif preset["pad"] == "swell":
                notes.append(dict(t=bar_t, dur=bar_dur * 1.05, kind="pad",
                                  midis=[m - 12 for m in chord], gain=0.4 * (0.5 + e * 0.6)))
            elif preset["pad"] == "stab":
                for i in range(2):
                    notes.append(dict(t=bar_t + i * beat * 2, dur=beat * 0.5, kind="stab",
                                      midis=chord, gain=0.5 * e))

            # --- bass
            if name != "break":
                if preset["bass"] == "offbeat":
                    for i in range(4):
                        notes.append(dict(t=bar_t + i * beat + beat * 0.5, dur=beat * 0.45,
                                          kind="bass", midis=[chord_root - 24], gain=0.85 * e))
                elif preset["bass"] == "eighth":
                    for i in range(8):
                        if i % 2 == 0 or e > 0.7:
                            notes.append(dict(t=bar_t + i * beat * 0.5, dur=beat * 0.42,
                                              kind="bass", midis=[chord_root - 24], gain=0.8 * e))
                elif preset["bass"] == "whole":
                    notes.append(dict(t=bar_t, dur=bar_dur * 0.95, kind="bass",
                                      midis=[chord_root - 24], gain=0.7 * e))

            # --- arp / pluck
            if preset["arp"] == "sixteenth" and name in ("build", "main", "drop"):
                seq = chord + [chord[0] + 12]
                for i in range(16):
                    m = seq[i % len(seq)] + (12 if (i // 4) % 2 else 0)
                    notes.append(dict(t=bar_t + i * beat * 0.25, dur=beat * 0.24, kind="pluck",
                                      midis=[m], gain=(0.16 + 0.2 * e) * (1 if i % 4 == 0 else 0.75)))
            elif preset["arp"] == "eighth":
                seq = chord + [chord[1] + 12]
                for i in range(8):
                    notes.append(dict(t=bar_t + i * beat * 0.5, dur=beat * 0.45, kind="pluck",
                                      midis=[seq[i % len(seq)] + 12], gain=0.18 * e))

            # --- 段落过渡特效
            if last_bar_of_section and name in ("intro", "build", "break"):
                fx.append(dict(t=bar_t + bar_dur * 0.5, kind="riser", dur=bar_dur * 0.5, gain=0.55))
            if name == "main" and k == 0:
                fx.append(dict(t=bar_t, kind="impact", gain=0.7))
            if name == "break" and k == 0:
                fx.append(dict(t=bar_t, kind="impact", gain=0.4))

        b0 += nbars

    return sections, notes, fx


# --------------------------------------------------------------------------- 混音

def render(preset_name: str, bpm: float, duration: float, target_lufs: float, seed: int):
    global rng
    rng = np.random.default_rng(seed)
    preset = dict(PRESETS[preset_name])
    if bpm:
        preset["bpm"] = bpm
    bpm = preset["bpm"]
    beat = 60.0 / bpm
    bar_dur = beat * 4
    bars = max(1, int(round(duration / bar_dur)))
    total = int((bars * bar_dur + 0.6) * SR)

    sections, notes, fx = build_events(preset, bpm, bars)
    hits, accents = drum_hits(preset, sections, bpm)

    drums = np.zeros(total)
    bass = np.zeros(total)
    chords = np.zeros(total)
    lead = np.zeros(total)
    fxbus = np.zeros(total)

    def add(bus, t, sig, gain=1.0):
        i = int(t * SR)
        if i < 0:
            sig = sig[-i:]
            i = 0
        if i >= total:
            return
        n = min(len(sig), total - i)
        bus[i:i + n] += sig[:n] * gain

    # 鼓
    for h in hits:
        g = h["gain"]
        if h["kind"] == "kick":
            add(drums, h["t"], kick(decay=0.30 if preset["drums"] != "edm" else 0.34), 0.85 * g)
        elif h["kind"] == "snare":
            add(drums, h["t"], snare(), 0.42 * g)
        elif h["kind"] == "clap":
            add(drums, h["t"], clap(), 0.5 * g)
        elif h["kind"] == "hat":
            add(drums, h["t"], hat(open_=(h["t"] % (beat * 2) < 1e-3)), 0.34 * g)
        elif h["kind"] == "ghost":
            add(drums, h["t"], snare(), 0.12 * g)

    # 旋律
    for nt in notes:
        if nt["kind"] == "pad":
            sig = pad_chord([midi_freq(m) for m in nt["midis"]], nt["dur"], bright=0.4 + preset["energy"] * 0.3)
            add(chords, nt["t"], sig, nt["gain"])
        elif nt["kind"] == "stab":
            sig = pad_chord([midi_freq(m) for m in nt["midis"]], nt["dur"], bright=0.85)
            add(chords, nt["t"], sig, nt["gain"])
        elif nt["kind"] == "bass":
            sig = bass_note(midi_freq(nt["midis"][0]), nt["dur"])
            add(bass, nt["t"], sig, nt["gain"])
        elif nt["kind"] == "pluck":
            sig = pluck(midi_freq(nt["midis"][0]), bright=0.5 + preset["energy"] * 0.3)
            add(lead, nt["t"], sig, nt["gain"])

    for f in fx:
        if f["kind"] == "riser":
            add(fxbus, f["t"], riser(f["dur"]), f["gain"])
        elif f["kind"] == "impact":
            add(fxbus, f["t"], impact(), f["gain"])

    # 侧链：底鼓压 pad / bass
    sc = np.ones(total)
    duck = 0.42 if preset["drums"] in ("four", "edm") else 0.65
    for h in hits:
        if h["kind"] != "kick":
            continue
        i = int(h["t"] * SR)
        n = min(int(SR * 0.34), total - i)
        if n <= 0:
            continue
        t = np.arange(n) / SR
        env = 1 - (1 - duck) * np.exp(-t / 0.11)
        sc[i:i + n] = np.minimum(sc[i:i + n], env)
    chords *= sc
    bass *= sc * 0.9 + 0.1

    # 混响（合成 IR + FFT 卷积）
    def reverb(x, decay=1.7, mix=0.22):
        n_ir = int(SR * decay)
        ir = rng.standard_normal(n_ir) * np.exp(-np.arange(n_ir) / (SR * decay * 0.32))
        ir = lowpass(ir, 5200)
        ir[: int(SR * 0.012)] = 0
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
        N = len(x) + n_ir
        nfft = 1 << (N - 1).bit_length()
        wet = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
        return x * (1 - mix) + wet * mix * 1.6

    chords = reverb(chords, 1.9, 0.3)
    lead = reverb(lead, 1.4, 0.24)
    fxbus = reverb(fxbus, 2.0, 0.3)

    # 黑胶底噪
    if preset_name in ("warm", "lofi"):
        vinyl = vinyl_noise(total) * 0.6
        chords += vinyl
        lead += vinyl * 0.5

    mix = drums * 1.0 + bass * 0.92 + chords * 0.9 + lead * 0.85 + fxbus * 0.8
    mix = highpass(mix, 28)

    # 立体声：把和弦轻微延时并反相铺宽
    d = int(SR * 0.008)
    left = mix.copy()
    right = mix.copy()
    right[d:] += chords[: total - d] * 0.12
    left[d:] += lead[: total - d] * -0.06
    stereo = np.stack([left, right], axis=1)

    # 母线：软压缩 + 限幅
    stereo = np.tanh(stereo * 1.15) * 0.92
    peak = np.max(np.abs(stereo)) + 1e-9
    stereo /= peak
    rms = np.sqrt(np.mean(stereo ** 2)) + 1e-9
    rms_db = 20 * math.log10(rms)
    gain_db = target_lufs - rms_db - 3.2  # 经验偏移：LUFS ≈ RMS + crest
    stereo *= 10 ** (gain_db / 20)
    stereo = np.tanh(stereo * 1.05) / np.tanh(1.05)
    stereo /= max(1.0, np.max(np.abs(stereo)))

    # 头尾淡入淡出
    fi = int(SR * 0.02)
    fo = int(SR * 0.35)
    stereo[:fi] *= np.linspace(0, 1, fi)[:, None]
    stereo[-fo:] *= np.linspace(1, 0, fo)[:, None]

    # 裁到目标时长
    n_out = int(duration * SR)
    stereo = stereo[:n_out]
    if len(stereo) < n_out:
        stereo = np.pad(stereo, ((0, n_out - len(stereo)), (0, 0)))

    grid = dict(
        bpm=bpm,
        beatsPerBar=4,
        offset=0.0,
        beatDur=round(beat, 5),
        barDur=round(bar_dur, 5),
        duration=round(duration, 3),
        beats=[round(i * beat, 5) for i in range(int(duration / beat) + 1)],
        bars=[round(i * bar_dur, 5) for i in range(bars + 1)],
        sections=[
            dict(name=n, start=round(sum(x[1] for x in sections[:i]) * bar_dur, 4),
                 end=round(sum(x[1] for x in sections[: i + 1]) * bar_dur, 4),
                 bars=m, energy=SECTION_ENERGY[n])
            for i, (n, m) in enumerate(sections)
        ],
        accents=accents,
        hits=[h["t"] for h in hits if h["kind"] in ("kick", "clap")],
        preset=preset_name,
        seed=seed,
        lufs_target=target_lufs,
        rms_db=round(rms_db, 2),
    )
    return stereo, grid


def write_wav(path: str, stereo: np.ndarray):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    pcm = np.clip(stereo, -1, 1)
    pcm = (pcm * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser(description="代码合成背景音乐 + 节拍网格")
    ap.add_argument("--preset", default="uplift", choices=sorted(PRESETS))
    ap.add_argument("--bpm", type=float, default=0, help="0 = 用预设的 BPM")
    ap.add_argument("--duration", type=float, default=0, help="秒；0 = 用 --bars 或 30")
    ap.add_argument("--bars", type=int, default=0)
    ap.add_argument("--out", default="audio/music.wav")
    ap.add_argument("--grid", default="audio/beats.json")
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        for k, v in PRESETS.items():
            print(f"{k:10s} {v['bpm']:>3} BPM  {v['scale']:<7} drums={v['drums']:<6} energy={v['energy']}")
        return

    duration = args.duration
    if duration <= 0 and args.bars > 0:
        bpm = args.bpm or PRESETS[args.preset]["bpm"]
        duration = args.bars * 4 * 60.0 / bpm
    if duration <= 0:
        duration = 30.0

    stereo, grid = render(args.preset, args.bpm, duration, args.lufs, args.seed)
    write_wav(args.out, stereo)
    os.makedirs(os.path.dirname(os.path.abspath(args.grid)) or ".", exist_ok=True)
    with open(args.grid, "w") as f:
        json.dump(grid, f, ensure_ascii=False, indent=2)

    print(f"music  {args.out}  {duration:.1f}s  {grid['bpm']} BPM  preset={args.preset}")
    names = [s["name"] for s in grid["sections"]]
    print(f"grid   {args.grid}  beats={len(grid['beats'])}  sections={names}")


if __name__ == "__main__":
    main()
