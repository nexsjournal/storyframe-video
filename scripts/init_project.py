#!/usr/bin/env python3
"""Create a storyframe video project from the skill templates."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "templates"

DEFAULT_DURATION = {
    "product": 30.0,
    "explainer": 90.0,
    "oral": 60.0,
    "event": 20.0,
    "course": 120.0,
    "mv": 48.0,
}

ASPECTS = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350),
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Initialize a storyframe video project")
    p.add_argument("--output", required=True, help="project directory")
    p.add_argument("--mode", choices=sorted(DEFAULT_DURATION), default="product")
    p.add_argument("--title", default="Untitled Video")
    p.add_argument("--duration", type=float, default=None)
    p.add_argument("--aspect", choices=sorted(ASPECTS), default="16:9")
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--script", default=None, help="existing copy/script file; copied into assets/copy/")
    p.add_argument("--music", default=None, help="user-provided music file; copied into audio/music.<ext>")
    p.add_argument("--force", action="store_true", help="allow writing into a non-empty directory")
    return p.parse_args()


def probe_audio(path: Path) -> dict:
    """Return duration/sample-rate/channels/codec when ffprobe is available."""
    if not shutil.which("ffprobe"):
        return {}
    p = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=sample_rate,channels,codec_name,duration:format=duration",
            "-of", "json", str(path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if p.returncode != 0:
        return {"probe_error": p.stderr.decode("utf-8", "replace")[:300]}
    try:
        data = json.loads(p.stdout)
        stream = (data.get("streams") or [{}])[0]
        fmt = data.get("format") or {}
        return {
            "duration": float(fmt.get("duration") or stream.get("duration") or 0) or None,
            "sample_rate": int(stream.get("sample_rate") or 0) or None,
            "channels": stream.get("channels"),
            "codec": stream.get("codec_name"),
        }
    except Exception as exc:
        return {"probe_error": str(exc)}


def render_template(name: str, values: dict[str, str]) -> str:
    text = (TEMPLATES / name).read_text(encoding="utf-8")
    for key, val in values.items():
        text = text.replace(f"[{key}]", val)
    return text


def make_plan(title: str, mode: str, duration: float, fps: int, width: int, height: int) -> dict:
    a = round(duration * 0.32, 3)
    b = round(duration * 0.66, 3)
    shots = [
        {
            "id": "s01",
            "start": 0.0,
            "end": a,
            "description": "完整首帧：主题 + 品牌 + 可识别的视觉主体",
            "descriptionAt": 0.0,
            "transition": "cut",
            "claim": "TODO: 可验证的主张",
            "source": "assets/cover.png",
            "actions": [{"id": "a01", "at": round(min(0.4, a / 2), 3), "description": "首个动作"}],
        },
        {
            "id": "s02",
            "start": a,
            "end": b,
            "description": "核心演示/讲解：一个动作或结果",
            "descriptionAt": a,
            "transition": "scan",
            "claim": "TODO: 证据",
            "source": "assets/demo.png",
            "actions": [{"id": "a02", "at": round(a + min(0.6, (b - a) / 2), 3), "description": "关键动作"}],
        },
        {
            "id": "s03",
            "start": b,
            "end": duration,
            "description": "结尾：一句 CTA + 日期/二维码，停留至少 3 秒",
            "descriptionAt": b,
            "transition": "cut",
            "claim": "TODO: CTA",
            "source": "assets/endcard.png",
            "actions": [{"id": "a03", "at": round(b + 0.1, 3), "description": "结束卡落版"}],
        },
    ]
    return {
        "title": title,
        "mode": mode,
        "duration": duration,
        "fps": fps,
        "width": width,
        "height": height,
        "language": "zh",
        "audience": "",
        "platform": "web",
        "cta": "",
        "style": {
            "palette": ["#F6F1E6", "#17141A", "#F2416B"],
            "type": "display/body",
            "motion": "push/stagger/scan",
        },
        "shots": shots,
        "audio": {
            "music": None,
            "cues": [],
            "targetLufs": -14,
            "truePeakDbtp": -1.0,
            "audioExceptionReason": "scaffold: add music/SFX and remove this field",
        },
    }


def main() -> int:
    args = parse_args()

    script_src = Path(args.script).expanduser().resolve() if args.script else None
    if script_src and not script_src.is_file():
        print(f"error: script not found: {script_src}", file=sys.stderr)
        return 2
    music_src = Path(args.music).expanduser().resolve() if args.music else None
    if music_src and not music_src.is_file():
        print(f"error: music not found: {music_src}", file=sys.stderr)
        return 2
    music_info = probe_audio(music_src) if music_src else {}
    if music_info.get("probe_error"):
        print(f"warning: ffprobe could not read music: {music_info['probe_error']}", file=sys.stderr)
    music_duration = music_info.get("duration")

    if args.duration is not None:
        duration = args.duration
    elif args.mode == "mv" and music_duration:
        # A music video follows the track; do not cut the song to a guessed default.
        duration = round(float(music_duration), 3)
    else:
        duration = DEFAULT_DURATION[args.mode]
    if duration <= 0:
        print("error: duration must be > 0", file=sys.stderr)
        return 2

    out = Path(args.output).expanduser().resolve()
    if out.exists() and any(out.iterdir()) and not args.force:
        print(f"error: {out} is not empty (use --force)", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)
    for d in ["assets", "assets/copy", "audio", "audio/sfx", "renders", "src", "videos"]:
        (out / d).mkdir(parents=True, exist_ok=True)

    sources: dict = {}
    script_dest = None
    if script_src:
        script_dest = out / "assets" / "copy" / script_src.name
        if script_src != script_dest.resolve():
            shutil.copy2(script_src, script_dest)
        sources["script"] = {
            "source": str(script_src),
            "copied_to": str(script_dest.relative_to(out)),
        }

    music_dest = None
    if music_src:
        suffix = music_src.suffix.lower() or ".audio"
        music_dest = out / "audio" / f"music{suffix}"
        if music_src != music_dest.resolve():
            shutil.copy2(music_src, music_dest)
        sources["music"] = {
            "source": str(music_src),
            "copied_to": str(music_dest.relative_to(out)),
            "license": "TBD",
            **{k: v for k, v in music_info.items() if k != "probe_error"},
        }

    width, height = ASPECTS[args.aspect]
    values = {"TITLE": args.title, "AUDIENCE": "", "CTA": ""}
    for name in ["BRIEF.md", "DIRECTION.md", "SCRIPT.md", "STORYBOARD.md", "SUNO_LYRIC_SHEET.md", "QA.md", "README.md"]:
        text = render_template(name, values)
        (out / name).write_text(text, encoding="utf-8")

    if script_dest:
        rel = script_dest.relative_to(out).as_posix()
        for name, needle in [("BRIEF.md", "- 文件/链接："), ("SCRIPT.md", "- 原文件/链接：")]:
            p = out / name
            text = p.read_text(encoding="utf-8")
            p.write_text(text.replace(needle + "\n", needle + f"`{rel}`\n", 1), encoding="utf-8")

    plan = make_plan(args.title, args.mode, duration, args.fps, width, height)
    if music_dest:
        rel = music_dest.relative_to(out).as_posix()
        plan["audio"]["music"] = {
            "file": rel,
            "source": "user-provided",
            "license": "TBD",
            **{k: v for k, v in music_info.items() if k != "probe_error"},
        }
        plan["audio"].pop("audioExceptionReason", None)
    (out / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if sources:
        (out / "SOURCES.json").write_text(
            json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    (out / "audio" / "README.md").write_text(
        "# Audio\n\n"
        "- `music.<ext>`：音乐（用户提供/已授权/生成）\n"
        "- `master.wav`：混音母版\n"
        "- `mix_report.json`：响度/混音报告\n"
        "- `sfx/`：动作音效\n\n"
        "用户提供音乐时，以它为时间基准卡点；`plan.json > audio.music` 登记文件与来源。\n"
        "用 `scripts/check_delivery.py` 检查最终混音。\n",
        encoding="utf-8",
    )

    print(f"created: {out}")
    print(f"mode={args.mode} duration={duration:g}s aspect={args.aspect} ({width}x{height}) fps={args.fps}")
    if music_duration and abs(float(music_duration) - duration) > 0.5:
        print(
            f"warning: music is {float(music_duration):.2f}s but video is {duration:.2f}s; "
            "trim/loop the music or adjust --duration",
            file=sys.stderr,
        )
    if music_dest:
        print(f"music: {music_dest.relative_to(out)} (user-provided)")
    if script_dest:
        print(f"script: {script_dest.relative_to(out)} (user-provided)")
    print("\nnext:")
    print("  1. verify BRIEF.md / SCRIPT.md: user copy and music are recorded, no placeholders left")
    print("  2. fill DIRECTION.md and edit STORYBOARD.md / plan.json")
    print("  3. add remaining assets/; keep user music as-is (do not replace it)")
    print("  4. copy <skill-dir>/starter/ into this project for a 7.5s demo, or build src/ yourself")
    print("  5. python3 <skill-dir>/scripts/check_delivery.py plan.json --video videos/final.mp4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
