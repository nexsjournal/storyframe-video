#!/usr/bin/env python3
"""Measure integrated loudness / true peak / LRA with ffmpeg ebur128."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys


def measure(video: str) -> dict:
    proc = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            video,
            "-filter_complex",
            "ebur128=peak=true",
            "-f",
            "null",
            "-",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    text = proc.stderr
    out = {
        "integrated_lufs": None,
        "lra_lu": None,
        "true_peak_dbtp": None,
    }
    # summary block is the most reliable; fall back to the last progress line
    ms = re.findall(r"I:\s*(-?\d+(?:\.\d+)?)\s*LUFS", text)
    if ms:
        out["integrated_lufs"] = float(ms[-1])
    ms = re.findall(r"LRA:\s*(-?\d+(?:\.\d+)?)\s*LU", text)
    if ms:
        out["lra_lu"] = float(ms[-1])
    ms = re.findall(r"Peak:\s*(-?\d+(?:\.\d+)?)\s*dBFS", text)
    if ms:
        out["true_peak_dbtp"] = float(ms[-1])
    out["ok"] = out["integrated_lufs"] is not None
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Measure loudness")
    p.add_argument("video")
    p.add_argument("--json", action="store_true")
    p.add_argument("--target", type=float, default=None, help="target integrated LUFS")
    args = p.parse_args()
    try:
        res = measure(args.video)
    except FileNotFoundError:
        print("error: ffmpeg not found", file=sys.stderr)
        return 2
    if args.target is not None and res["integrated_lufs"] is not None:
        res["target_lufs"] = args.target
        res["delta_lu"] = round(res["integrated_lufs"] - args.target, 2)
        res["within_2lu"] = abs(res["delta_lu"]) <= 2.0
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"Integrated: {res['integrated_lufs']} LUFS")
        print(f"True Peak:  {res['true_peak_dbtp']} dBTP")
        print(f"LRA:        {res['lra_lu']} LU")
        if "delta_lu" in res:
            print(f"Target:     {args.target} LUFS (delta {res['delta_lu']:+.2f})")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
