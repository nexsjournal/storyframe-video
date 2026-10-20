#!/usr/bin/env python3
"""Automated delivery checks for a storyframe video project.

Checks plan structure, shot coverage, action/cue sync, media metadata,
first-frame ink, black intervals, loudness and basic caption limits.
Visual semantics and listening still require a human review.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import numpy as np
except Exception as exc:  # pragma: no cover
    print(f"error: needs numpy + pillow ({exc})", file=sys.stderr)
    raise SystemExit(2)


def run(cmd: list[str]) -> tuple[int, bytes, bytes]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout, p.stderr


def probe(video: Path) -> dict:
    code, out, err = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(video),
        ]
    )
    if code != 0:
        raise RuntimeError(err.decode("utf-8", "replace")[:800])
    return json.loads(out)


def fps_of(stream: dict) -> float:
    raw = stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/1"
    try:
        num, den = raw.split("/")
        return float(num) / float(den) if float(den) else 0.0
    except Exception:
        return 0.0


def frame_gray(video: Path, t: float, w: int = 480, h: int = 270) -> np.ndarray:
    code, out, err = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{t:.3f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-vf",
            f"scale={w}:{h}",
            "-pix_fmt",
            "gray",
            "-f",
            "rawvideo",
            "-",
        ]
    )
    if code != 0 or len(out) != w * h:
        raise RuntimeError(f"cannot extract frame at {t}s: {err.decode('utf-8', 'replace')[:300]}")
    return np.frombuffer(out, dtype=np.uint8).reshape(h, w)


def ink_ratio(gray: np.ndarray) -> float:
    med = float(np.median(gray))
    return float(np.mean(np.abs(gray.astype(np.int16) - med) > 32))


def black_intervals(video: Path) -> list[dict]:
    code, out, err = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(video),
            "-vf",
            "blackdetect=d=0.1:pix_th=0.10",
            "-an",
            "-f",
            "null",
            "-",
        ]
    )
    text = (out + err).decode("utf-8", "replace")
    # ffmpeg prints black_start:1.2 black_end:1.8
    pairs = re.findall(r"black_start:\s*([0-9.]+)\s+black_end:\s*([0-9.]+)", text)
    return [{"start": float(a), "end": float(b)} for a, b in pairs]


def parse_srt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n")
    blocks = re.split(r"\n{2,}", text.strip())
    cues = []
    for b in blocks:
        lines = [x for x in b.split("\n") if x.strip()]
        if not lines:
            continue
        if re.fullmatch(r"\d+", lines[0].strip()):
            lines = lines[1:]
        if not lines or "-->" not in lines[0]:
            continue
        a, b = [x.strip() for x in lines[0].split("-->", 1)]
        def sec(s: str) -> float:
            m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)", s)
            if not m:
                return 0.0
            h, mi, se, ms = m.groups()
            return int(h) * 3600 + int(mi) * 60 + int(se) + int(ms.ljust(3, "0")[:3]) / 1000
        cues.append({"start": sec(a), "end": sec(b), "lines": lines[1:]})
    return cues


def load_mix(path: Path | None) -> dict:
    if not path:
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def pick(d: dict, keys: list[str]):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Check a storyframe video delivery")
    ap.add_argument("plan")
    ap.add_argument("--video", required=True)
    ap.add_argument("--mix-report", default=None)
    ap.add_argument("--captions", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    plan_path = Path(args.plan).resolve()
    video = Path(args.video).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict = {}

    if not plan_path.exists():
        print(f"error: plan not found: {plan_path}", file=sys.stderr)
        return 2
    if not video.exists():
        print(f"error: video not found: {video}", file=sys.stderr)
        return 2
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("error: ffmpeg/ffprobe not found", file=sys.stderr)
        return 2

    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"error: bad plan JSON: {exc}", file=sys.stderr)
        return 2

    # ---------- plan structure ----------
    for k in ["title", "duration", "fps", "width", "height", "shots"]:
        if k not in plan:
            errors.append(f"plan missing {k}")
    if errors:
        print("\n".join(errors))
        return 1

    duration = float(plan["duration"])
    shots = plan.get("shots") or []
    if not shots:
        errors.append("plan.shots is empty")
    ids: set[str] = set()
    actions: dict[str, dict] = {}
    cleaned: list[dict] = []
    for i, s in enumerate(shots):
        sid = str(s.get("id", f"#{i}"))
        if sid in ids:
            errors.append(f"duplicate shot id: {sid}")
        ids.add(sid)
        try:
            st, en = float(s["start"]), float(s["end"])
        except Exception:
            errors.append(f"{sid}: bad start/end")
            continue
        if st < -0.001:
            errors.append(f"{sid}: start < 0")
        if en <= st:
            errors.append(f"{sid}: end <= start")
        if en > duration + 0.051:
            errors.append(f"{sid}: end {en:.3f} > duration {duration:.3f}")
        if not s.get("description"):
            errors.append(f"{sid}: missing description")
        dat = s.get("descriptionAt")
        if dat is None:
            warnings.append(f"{sid}: missing descriptionAt")
        else:
            try:
                if float(dat) < st - 0.051 or float(dat) > en + 0.051:
                    warnings.append(f"{sid}: descriptionAt outside shot")
            except Exception:
                warnings.append(f"{sid}: non-numeric descriptionAt")
        for a in s.get("actions", []) or []:
            aid = str(a.get("id", ""))
            if not aid:
                warnings.append(f"{sid}: action without id")
                continue
            if aid in actions:
                errors.append(f"duplicate action id: {aid}")
            try:
                at = float(a["at"])
            except Exception:
                errors.append(f"{aid}: bad action.at")
                continue
            if at < st - 0.051 or at > en + 0.051:
                errors.append(f"{aid}: action.at {at:.3f} outside {sid} ({st:.3f}-{en:.3f})")
            a["_shot"] = sid
            actions[aid] = a
        cleaned.append({**s, "id": sid, "start": st, "end": en})

    cleaned.sort(key=lambda x: x["start"])
    if cleaned:
        if abs(cleaned[0]["start"]) > 0.051:
            errors.append(f"timeline does not start at 0 (starts {cleaned[0]['start']:.3f})")
        for a, b in zip(cleaned, cleaned[1:]):
            gap = b["start"] - a["end"]
            if abs(gap) > 0.051:
                errors.append(f"gap/overlap {a['id']} -> {b['id']}: {gap:+.3f}s")
        if abs(cleaned[-1]["end"] - duration) > 0.051:
            errors.append(f"timeline ends at {cleaned[-1]['end']:.3f}, duration is {duration:.3f}")
    metrics["shots"] = len(cleaned)
    metrics["plan_duration"] = duration

    # ---------- audio cues ----------
    audio = plan.get("audio") or {}
    cues = audio.get("cues") or []
    cue_ids: set[str] = set()
    for c in cues:
        try:
            at = float(c["at"])
        except Exception:
            errors.append("cue missing/invalid at")
            continue
        if at < -0.051 or at > duration + 0.051:
            errors.append(f"cue at {at:.3f} outside 0-{duration:.3f}")
        if not c.get("kind"):
            warnings.append(f"cue at {at:.3f} missing kind")
        aid = c.get("actionId")
        if aid:
            cue_ids.add(str(aid))
            if aid not in actions:
                errors.append(f"cue actionId {aid} not found")
            else:
                try:
                    sync = float(c.get("syncOffset", 0))
                    actual = at + sync
                    target = float(actions[aid]["at"])
                    if abs(actual - target) > 0.08:
                        warnings.append(
                            f"cue {aid} sync drift {actual - target:+.3f}s (cue {at:.3f} + {sync:+.3f} vs action {target:.3f})"
                        )
                except Exception:
                    pass
        f = c.get("file")
        if f:
            p = (plan_path.parent / f).resolve()
            if not p.exists():
                warnings.append(f"cue file missing: {f}")
    for aid in actions:
        if aid not in cue_ids:
            warnings.append(f"action {aid} has no audio cue")
    music = audio.get("music")
    if isinstance(music, dict) and music.get("file"):
        p = (plan_path.parent / music["file"]).resolve()
        if not p.exists():
            warnings.append(f"music file missing: {music['file']}")
    if not cues and not music and not audio.get("audioExceptionReason"):
        warnings.append("no audio cues/music and no audioExceptionReason")
    metrics["cues"] = len(cues)

    # ---------- video metadata ----------
    try:
        info = probe(video)
    except Exception as exc:
        errors.append(f"ffprobe failed: {exc}")
        info = {}
    vstream = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    astream = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not vstream:
        errors.append("no video stream")
    else:
        vw, vh = int(vstream.get("width", 0)), int(vstream.get("height", 0))
        vfps = fps_of(vstream)
        vdur = float(info.get("format", {}).get("duration") or vstream.get("duration") or 0)
        codec = vstream.get("codec_name", "")
        metrics.update(
            {
                "width": vw,
                "height": vh,
                "fps": round(vfps, 3),
                "video_duration": round(vdur, 3),
                "video_codec": codec,
                "video_size_bytes": int(info.get("format", {}).get("size", 0) or 0),
            }
        )
        if vw != int(plan["width"]) or vh != int(plan["height"]):
            errors.append(f"dimension {vw}x{vh} != plan {plan['width']}x{plan['height']}")
        if abs(vfps - float(plan["fps"])) > 0.1:
            errors.append(f"fps {vfps:.2f} != plan {plan['fps']}")
        if abs(vdur - duration) > 0.15:
            errors.append(f"duration {vdur:.2f}s != plan {duration:.2f}s")
        if codec not in {"h264", "hevc", "vp9", "av1"}:
            warnings.append(f"video codec is {codec}; h264 is the safest default")
        if not astream and not audio.get("audioExceptionReason"):
            errors.append("no audio stream and no audioExceptionReason")

    # ---------- first frame ----------
    try:
        g0 = frame_gray(video, 0.0)
        ink0 = ink_ratio(g0)
        metrics["first_frame_ink"] = round(ink0, 4)
        if ink0 < 0.004:
            errors.append(f"first frame looks blank (ink {ink0:.4f} < 0.004)")
        if duration > 0.6:
            ink5 = ink_ratio(frame_gray(video, 0.5))
            metrics["frame_0_5s_ink"] = round(ink5, 4)
            if ink5 < 0.002:
                warnings.append(f"frame at 0.5s looks blank (ink {ink5:.4f})")
    except Exception as exc:
        errors.append(f"first frame check failed: {exc}")

    # ---------- black intervals ----------
    try:
        blacks = black_intervals(video)
        metrics["black_intervals"] = blacks
        total_black = sum(b["end"] - b["start"] for b in blacks)
        metrics["black_seconds"] = round(total_black, 3)
        if total_black > 0.3:
            warnings.append(f"{total_black:.2f}s black detected; check if intentional")
    except Exception as exc:
        warnings.append(f"blackdetect failed: {exc}")

    # ---------- loudness ----------
    target = float(audio.get("targetLufs", -14.0))
    mix = load_mix(Path(args.mix_report).resolve() if args.mix_report else None)
    integrated = pick(mix, ["integrated_lufs", "integratedLufs", "measuredLufs", "measured_lufs", "lufs", "I"])
    peak = pick(mix, ["true_peak_dbtp", "truePeakDbtp", "truePeakDbfs", "true_peak", "Peak"])
    if integrated is None or peak is None:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from loudness import measure  # type: ignore

            m = measure(str(video))
            integrated = integrated if integrated is not None else m.get("integrated_lufs")
            peak = peak if peak is not None else m.get("true_peak_dbtp")
        except Exception as exc:
            warnings.append(f"loudness check failed: {exc}")
    if integrated is not None:
        metrics["integrated_lufs"] = float(integrated)
        if abs(float(integrated) - target) > 2.0:
            warnings.append(f"integrated {float(integrated):.1f} LUFS is >2 LU from target {target:.1f}")
    if peak is not None:
        metrics["true_peak_dbtp"] = float(peak)
        if float(peak) > -0.8:
            warnings.append(f"true peak {float(peak):.1f} dBTP is too close to 0")
    if mix:
        mc = pick(mix, ["cue_count", "cueCount", "cues", "sfx_count"])
        if isinstance(mc, int) and mc != len(cues):
            warnings.append(f"mix report cue count {mc} != plan cues {len(cues)}")

    # ---------- captions ----------
    if args.captions:
        cp = Path(args.captions)
        if not cp.exists():
            warnings.append(f"captions not found: {cp}")
        else:
            try:
                sc = parse_srt(cp)
                metrics["caption_cues"] = len(sc)
                if not sc:
                    warnings.append("captions file has no cues")
                if sc and sc[-1]["end"] > duration + 0.5:
                    warnings.append(f"last caption ends {sc[-1]['end']:.1f}s > video {duration:.1f}s")
                for i, c in enumerate(sc, 1):
                    if len(c["lines"]) > 2:
                        warnings.append(f"caption {i}: more than 2 lines")
                    for line in c["lines"]:
                        cjk = len(re.findall(r"[\u4e00-\u9fff]", line))
                        if cjk > 18 or len(line) > 42:
                            warnings.append(f"caption {i}: line too long ({cjk} CJK / {len(line)} chars)")
                            break
            except Exception as exc:
                warnings.append(f"caption parse failed: {exc}")

    # ---------- report ----------
    result = {"ok": not errors, "errors": errors, "warnings": warnings, "metrics": metrics}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if not errors else "FAIL")
        for e in errors:
            print("ERROR:", e)
        for w in warnings:
            print("WARN: ", w)
        print("\nmetrics:")
        for k, v in metrics.items():
            print(f"  {k}: {v}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
