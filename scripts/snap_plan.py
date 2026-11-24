#!/usr/bin/env python3
"""把 plan.json 的时间点吸附到节拍网格上（卡点检查 + 自动对齐）。

画面卡点的执行层工具：分镜和 action 的时间点不落在拍上，节奏就会"飘"。
这个脚本读 audio/beats.json，把所有 start / end / action.at 吸附到最近的
1/sub 拍，输出 plan.snapped.json 和一份漂移报告。

用法：
  python3 scripts/snap_plan.py plan.json --beats audio/beats.json
  python3 scripts/snap_plan.py plan.json --beats audio/beats.json --sub 2 --out plan.snapped.json
  python3 scripts/snap_plan.py plan.json --beats audio/beats.json --check --tolerance 0.03
"""
from __future__ import annotations

import argparse
import json
import sys


def load(path):
    with open(path) as f:
        return json.load(f)


def snap(t: float, beat: float, offset: float, sub: int) -> float:
    step = beat / sub
    return round(round((t - offset) / step) * step + offset, 4)


def main():
    ap = argparse.ArgumentParser(description="把 plan 时间点吸附到节拍网格")
    ap.add_argument("plan")
    ap.add_argument("--beats", default="audio/beats.json")
    ap.add_argument("--sub", type=int, default=2, help="每拍细分（2=八分音符, 4=十六分）")
    ap.add_argument("--out", default="plan.snapped.json")
    ap.add_argument("--tolerance", type=float, default=0.03, help="允许漂移秒数")
    ap.add_argument("--check", action="store_true", help="只检查，超标返回非 0")
    args = ap.parse_args()

    try:
        plan = load(args.plan)
        grid = load(args.beats)
    except FileNotFoundError as e:
        print(f"读不到文件：{e.filename}")
        return 2

    beat = float(grid.get("beatDur") or 60.0 / float(grid["bpm"]))
    offset = float(grid.get("offset", 0.0))
    dur = float(grid.get("duration") or plan.get("duration") or 0)
    sections = grid.get("sections") or []

    def section_of(t):
        cur = None
        for s in sections:
            if t >= s["start"] - 1e-6:
                cur = s
        return cur["name"] if cur else "-"

    rows = []
    worst = 0.0
    changed = 0

    shots = plan.get("shots") or []
    for i, sh in enumerate(shots):
        for key in ("start", "end"):
            if key not in sh:
                continue
            old = float(sh[key])
            new = snap(old, beat, offset, args.sub)
            drift = abs(new - old)
            worst = max(worst, drift)
            if drift > 1e-6:
                changed += 1
            rows.append((f"shots[{i}].{key}", old, new, drift, section_of(old)))
            if not args.check:
                sh[key] = new
        # 保持顺序与覆盖
        if not args.check and sh.get("end", 0) <= sh.get("start", 0):
            sh["end"] = round(sh["start"] + beat / args.sub, 4)

    for sh_i, sh in enumerate(shots):
        for a_i, a in enumerate(sh.get("actions") or []):
            if "at" not in a:
                continue
            old = float(a["at"])
            new = snap(old, beat, offset, args.sub)
            drift = abs(new - old)
            worst = max(worst, drift)
            if drift > 1e-6:
                changed += 1
            rows.append((f"shots[{sh_i}].actions[{a_i}].at", old, new, drift, section_of(old)))
            if not args.check:
                a["at"] = new
                a["beat"] = round((new - offset) / beat, 3)

    cues = ((plan.get("audio") or {}).get("cues")) or []
    for c_i, c in enumerate(cues):
        if "at" not in c:
            continue
        old = float(c["at"])
        new = snap(old, beat, offset, args.sub)
        drift = abs(new - old)
        worst = max(worst, drift)
        rows.append((f"audio.cues[{c_i}].at", old, new, drift, section_of(old)))
        if not args.check:
            c["at"] = new

    if dur and shots:
        last = max(float(s.get("end", 0)) for s in shots)
        if abs(last - dur) > 0.05:
            print(f"注意：shots 覆盖到 {last:.2f}s，音频时长 {dur:.2f}s（差 {last - dur:+.2f}s）")

    rows.sort(key=lambda r: -r[3])
    print(f"网格 {grid.get('bpm')} BPM  beat={beat:.4f}s  1/{args.sub} 拍 = {beat / args.sub:.4f}s")
    print(f"对齐点 {len(rows)}  改动 {changed}  最大漂移 {worst * 1000:.1f} ms")
    for name, old, new, drift, sec in rows[:8]:
        if drift > 1e-6:
            print(f"  {name:34s} {old:7.3f} → {new:7.3f}  ({drift * 1000:+6.1f} ms)  [{sec}]")

    bad = [r for r in rows if r[3] > args.tolerance]
    if args.check:
        if bad:
            print(f"失败：{len(bad)} 个时间点漂移超过 {args.tolerance * 1000:.0f} ms")
            return 1
        print("通过：所有时间点都在网格容差内")
        return 0

    with open(args.out, "w") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print(f"写出 {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
