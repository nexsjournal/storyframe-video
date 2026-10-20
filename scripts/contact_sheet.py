#!/usr/bin/env python3
"""Build a labeled contact sheet from a video."""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def probe_duration(video: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(video),
        ]
    )
    return float(json.loads(out)["format"]["duration"])


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for p in [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> int:
    p = argparse.ArgumentParser(description="Contact sheet")
    p.add_argument("video")
    p.add_argument("--out", default="renders/contact.png")
    p.add_argument("--fps", type=float, default=1.0)
    p.add_argument("--cols", type=int, default=6)
    p.add_argument("--width", type=int, default=320)
    p.add_argument("--start", type=float, default=0.0)
    p.add_argument("--end", type=float, default=None)
    p.add_argument("--label", action="store_true", default=True)
    args = p.parse_args()

    video = Path(args.video)
    if not video.exists():
        raise SystemExit(f"error: {video} not found")
    duration = probe_duration(video)
    end = args.end if args.end is not None else duration
    if end <= args.start:
        raise SystemExit("error: end must be > start")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="contact-") as td:
        tmp = Path(td)
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                str(args.start),
                "-i",
                str(video),
                "-t",
                str(end - args.start),
                "-vf",
                f"fps={args.fps},scale={args.width}:-1",
                "-q:v",
                "2",
                str(tmp / "f_%04d.jpg"),
            ],
            check=True,
        )
        frames = sorted(tmp.glob("f_*.jpg"))
        if not frames:
            raise SystemExit("error: no frames extracted")
        imgs = [Image.open(f).convert("RGB") for f in frames]
        w, h = imgs[0].size
        label_h = 24
        rows = (len(imgs) + args.cols - 1) // args.cols
        sheet = Image.new("RGB", (args.cols * w, rows * (h + label_h)), (23, 20, 26))
        draw = ImageDraw.Draw(sheet)
        f = font(15)
        for i, im in enumerate(imgs):
            x = (i % args.cols) * w
            y = (i // args.cols) * (h + label_h)
            t = args.start + i / args.fps
            if args.label:
                draw.text((x + 6, y + 3), f"{t:05.1f}s", font=f, fill=(246, 241, 230))
            sheet.paste(im, (x, y + label_h))
        sheet.save(out)
        print(f"wrote {out}  {sheet.width}x{sheet.height}  frames={len(imgs)}  every {1/args.fps:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
