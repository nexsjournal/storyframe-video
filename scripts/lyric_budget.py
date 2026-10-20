#!/usr/bin/env python3
"""Count Suno lyric characters per section and check timing/length budgets."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

CJK = re.compile(r"[\u4e00-\u9fff]")
SECTION_RE = re.compile(r"^\[([^\]]+)\]\s*$")
BUDGET = {
    "intro": (4, 6),
    "verse": (6, 10),
    "chorus": (8, 9),
    "bridge": (6, 8),
    "final": (8, 8),
    "outro": (0, 12),
    "end": (0, 0),
}


@dataclass
class Section:
    label: str
    kind: str
    lines: list[str] = field(default_factory=list)

    @property
    def hanzi(self) -> int:
        return sum(len(CJK.findall(x)) for x in self.lines)

    @property
    def chars(self) -> int:
        return sum(len(re.sub(r"\s", "", x)) for x in self.lines)


def classify(label: str) -> str:
    s = label.lower()
    if "final" in s:
        return "final"
    if "chorus" in s:
        return "chorus"
    if "verse" in s:
        return "verse"
    if "bridge" in s:
        return "bridge"
    if "intro" in s:
        return "intro"
    if "outro" in s:
        return "outro"
    if s.startswith("end"):
        return "end"
    return "other"


def parse(text: str) -> list[Section]:
    sections: list[Section] = []
    current = Section("(untagged)", "other")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = SECTION_RE.match(line)
        if m:
            if current.lines or current.label != "(untagged)":
                sections.append(current)
            current = Section(m.group(1), classify(m.group(1)))
            continue
        if line.startswith("//") or line.startswith(";"):
            continue
        current.lines.append(line)
    if current.lines or current.label != "(untagged)":
        sections.append(current)
    return sections


def normalize(s: str) -> str:
    return re.sub(r"[\s，。！？、,.!?;；:：\"'“”‘’（）()\[\]【】-]", "", s)


def main() -> int:
    p = argparse.ArgumentParser(description="Suno lyric budget checker")
    p.add_argument("file", nargs="?", help="lyric file; omit to read stdin")
    p.add_argument("--bpm", type=float, default=124.0)
    p.add_argument("--bars", type=int, default=27)
    p.add_argument("--meter", type=int, default=4)
    p.add_argument("--hook", default="", help="expected hook, e.g. 绘声绘色，画就会唱")
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true", help="exit 1 on warnings")
    args = p.parse_args()

    text = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    sections = [s for s in parse(text) if s.kind != "end"]
    tagged = [s for s in sections if s.label != "(untagged)"]
    if tagged:
        sections = tagged
    if not sections:
        print("error: no lyric lines found", file=sys.stderr)
        return 1

    bar_sec = 60.0 / args.bpm * args.meter
    duration = args.bars * bar_sec
    total_hanzi = sum(s.hanzi for s in sections)
    total_lines = sum(len(s.lines) for s in sections)
    warnings: list[str] = []

    for s in sections:
        lo, hi = BUDGET.get(s.kind, (0, 999))
        if s.kind in BUDGET:
            for i, line in enumerate(s.lines, 1):
                n = len(CJK.findall(line))
                if n == 0:
                    continue
                if n > hi:
                    warnings.append(f"{s.label} line {i}: {n} 字 > 上限 {hi}: {line}")
                if n < lo and s.kind not in {"outro", "end"}:
                    warnings.append(f"{s.label} line {i}: {n} 字 < 下限 {lo}: {line}")

    if args.hook:
        if normalize(args.hook) not in normalize(text):
            warnings.append(f"hook not found: {args.hook}")

    if total_hanzi > 180:
        warnings.append(f"total hanzi {total_hanzi} > 180；删词，不加速")
    if total_hanzi < 100:
        warnings.append(f"total hanzi {total_hanzi} < 100；可能太空")

    rows = []
    for s in sections:
        lo, hi = BUDGET.get(s.kind, (0, 999))
        rows.append(
            {
                "label": s.label,
                "kind": s.kind,
                "lines": len(s.lines),
                "hanzi": s.hanzi,
                "chars": s.chars,
                "budget": f"{lo}-{hi}" if s.kind != "outro" else f"0-{hi}",
            }
        )

    result = {
        "bpm": args.bpm,
        "meter": args.meter,
        "bars": args.bars,
        "bar_seconds": round(bar_sec, 4),
        "duration_seconds": round(duration, 3),
        "total_hanzi": total_hanzi,
        "total_lines": total_lines,
        "hanzi_per_second": round(total_hanzi / duration, 3) if duration else None,
        "sections": rows,
        "warnings": warnings,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"BPM {args.bpm:g} · {args.meter}/4 · {args.bars} bars · 1 bar {bar_sec:.3f}s · total {duration:.2f}s")
        print(f"total: {total_hanzi} 汉字 / {total_lines} 行 / {total_hanzi / duration:.2f} 字/秒")
        print()
        print("| 段落 | 行 | 汉字 | 字符 | 预算 |")
        print("|---|---:|---:|---:|---:|")
        for r in rows:
            print(f"| {r['label']} | {r['lines']} | {r['hanzi']} | {r['chars']} | {r['budget']} |")
        if warnings:
            print("\nWARN:")
            for w in warnings:
                print(" -", w)
        else:
            print("\nOK: no budget warnings")

    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
