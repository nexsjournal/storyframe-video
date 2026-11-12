#!/usr/bin/env python3
"""把多张静帧拼成一张带标签的对比表（默认 3 列，480px/格）。

用于方向/风格对比：不要逐张发 1080p 图，拼成一张低分辨率 sheet 一次看完。

用法：
  python3 scripts/still_sheet.py renders/a.jpg renders/b.jpg renders/c.jpg
  python3 scripts/still_sheet.py renders/*.jpg --out renders/compare.png --width 480
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


def font(size: int):
    for name in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("images", nargs="+", help="输入图片路径")
    ap.add_argument("--out", default="renders/compare.png", help="输出 PNG")
    ap.add_argument("--cols", type=int, default=3, help="列数")
    ap.add_argument("--width", type=int, default=480, help="每格宽度 px")
    ap.add_argument("--gap", type=int, default=8, help="格间距 px")
    ap.add_argument("--label", action="store_true", help="显示文件名标签")
    args = ap.parse_args()

    if args.cols < 1 or args.width < 80:
        raise SystemExit("--cols 必须 >=1，--width 必须 >=80")
    paths = [Path(p) for p in args.images]
    for p in paths:
        if not p.is_file():
            raise SystemExit(f"找不到图片：{p}")

    first = Image.open(paths[0]).convert("RGB")
    tile_h = max(1, round(args.width * first.height / first.width))
    label_h = 24 if args.label else 0
    rows = (len(paths) + args.cols - 1) // args.cols
    sheet_w = args.cols * args.width + (args.cols + 1) * args.gap
    sheet_h = rows * (tile_h + label_h) + (rows + 1) * args.gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), (23, 20, 26))
    draw = ImageDraw.Draw(sheet)
    f = font(14)

    for i, p in enumerate(paths):
        row, col = divmod(i, args.cols)
        x = args.gap + col * (args.width + args.gap)
        y = args.gap + row * (tile_h + label_h + args.gap)
        img = Image.open(p).convert("RGB")
        img = ImageOps.pad(img, (args.width, tile_h), method=Image.Resampling.LANCZOS, color=(23, 20, 26))
        sheet.paste(img, (x, y))
        if args.label:
            draw.text((x + 2, y + tile_h + 4), p.stem[:48], fill=(246, 241, 230), font=f)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"wrote {out} {sheet_w}x{sheet_h} tiles={len(paths)} cols={args.cols}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
