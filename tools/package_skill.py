#!/usr/bin/env python3
"""把本仓库打包成可上传的技能发布包（SkillHub / WorkBuddy）。

产物：
  dist/storyframe-video-skill/                 目录版（SkillHub CLI 直接发布用）
  dist/storyframe-video-skill.zip              固定名 zip（WorkBuddy「上传技能」用）
  dist/storyframe-video-skill-<version>.zip    带版本号的存档副本

用法：
  python3 tools/package_skill.py            # 校验 + 打包
  python3 tools/package_skill.py --check    # 只校验，不写文件

发布包只包含白名单内容；.git / .github / .internal / tools / dist /
__pycache__ / node_modules / .DS_Store / *.pyc 一律不进入压缩包。
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PKG_NAME = "storyframe-video-skill"

# 进入发布包的顶层条目（白名单，避免把内部笔记或开发文件带出去）
INCLUDE = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "VERSION",
    "requirements.txt",
    "references",
    "scripts",
    "templates",
    "starter",
    "docs",
]

EXCLUDE_DIRS = {
    ".git",
    ".github",
    ".internal",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "tools",
}
EXCLUDE_FILES = {".DS_Store", ".gitignore"}
EXCLUDE_SUFFIXES = (".pyc",)

SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

# SkillHub 发布接口限制 10MB（未压缩）；留一点余量
MAX_UNCOMPRESSED = 10 * 1024 * 1024
LEAK_PATTERNS = (
    re.compile(r"/Users/[^/\s]+/"),
    re.compile(r"/home/[^/\s]+/"),
    re.compile(r"skh_[A-Za-z0-9]{20,}"),
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
)


def read_frontmatter(path: Path) -> dict[str, str]:
    """解析 SKILL.md 的简单 YAML front matter（只支持 key: value 与 [a, b]）。"""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise SystemExit("SKILL.md 缺少 front matter（首行必须是 ---）")
    parts = text.split("\n")
    end = next((i for i in range(1, len(parts)) if parts[i].strip() == "---"), -1)
    if end < 0:
        raise SystemExit("SKILL.md front matter 缺少结束标记 ---")
    meta: dict[str, str] = {}
    for raw in parts[1:end]:
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        meta[key.strip()] = val
    return meta


def collect_files() -> list[Path]:
    files: list[Path] = []
    for entry in INCLUDE:
        src = ROOT / entry
        if not src.exists():
            raise SystemExit(f"白名单条目不存在：{entry}")
        if src.is_file():
            files.append(src)
            continue
        for path in sorted(src.rglob("*")):
            if not path.is_file():
                continue
            rel_parts = path.relative_to(ROOT).parts
            if any(part in EXCLUDE_DIRS for part in rel_parts):
                continue
            if path.name in EXCLUDE_FILES or path.name.endswith(EXCLUDE_SUFFIXES):
                continue
            files.append(path)
    return files


def check_metadata(meta: dict[str, str]) -> None:
    for key in ("slug", "version", "displayName", "summary"):
        if not meta.get(key):
            raise SystemExit(f"SKILL.md front matter 缺少 {key}")
    if not SLUG_RE.match(meta["slug"]):
        raise SystemExit(f"slug 不是合法 kebab-case：{meta['slug']}")
    if not SEMVER_RE.match(meta["version"]):
        raise SystemExit(f"version 不是合法 SemVer：{meta['version']}")
    version_file = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version_file != meta["version"]:
        raise SystemExit(
            f"版本不一致：VERSION={version_file}，SKILL.md={meta['version']}"
        )
    if len(meta["summary"]) > 200:
        raise SystemExit("summary 过长（建议 <= 200 字符）")


def check_links(files: list[Path]) -> None:
    """检查发布包内 Markdown 的相对链接是否指向包内真实文件。"""
    rel_set = {p.relative_to(ROOT).as_posix() for p in files}
    problems: list[str] = []
    for path in files:
        if path.suffix.lower() != ".md":
            continue
        rel_dir = path.relative_to(ROOT).parent
        for target in LINK_RE.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            resolved = (rel_dir / clean).resolve()
            try:
                rel = resolved.relative_to(ROOT).as_posix()
            except ValueError:
                problems.append(f"{path.relative_to(ROOT)} -> {target}（指向仓库外）")
                continue
            if rel not in rel_set:
                problems.append(f"{path.relative_to(ROOT)} -> {target}")
    if problems:
        raise SystemExit("存在失效链接：\n  " + "\n  ".join(problems))


def check_leaks(files: list[Path]) -> None:
    problems: list[str] = []
    for path in files:
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".zip"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in LEAK_PATTERNS:
            if pattern.search(text):
                problems.append(f"{path.relative_to(ROOT)} 含敏感片段：{pattern.pattern}")
    if problems:
        raise SystemExit("发布包可能泄露本机路径或密钥：\n  " + "\n  ".join(problems))


def build(files: list[Path], meta: dict[str, str]) -> Path:
    pkg_dir = DIST / PKG_NAME
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
    pkg_dir.mkdir(parents=True)

    for path in files:
        rel = path.relative_to(ROOT)
        dest = pkg_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)

    total = sum(p.stat().st_size for p in files)
    if total > MAX_UNCOMPRESSED:
        raise SystemExit(
            f"发布包未压缩大小 {total / 1024 / 1024:.1f}MB 超过 SkillHub 10MB 限制"
        )

    zip_path = DIST / f"{PKG_NAME}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(rel, date_time=(2020, 1, 1, 0, 0, 0))
            executable = path.suffix in {".py", ".sh", ".mjs", ".js"} or path.name in {
                "render.mjs",
                "still.mjs",
                "server.mjs",
            }
            info.external_attr = (0o100755 if executable else 0o100644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, path.read_bytes())

    versioned = DIST / f"{PKG_NAME}-{meta['version']}.zip"
    shutil.copyfile(zip_path, versioned)
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只校验，不生成文件")
    args = parser.parse_args()

    meta = read_frontmatter(ROOT / "SKILL.md")
    check_metadata(meta)
    files = collect_files()
    check_links(files)
    check_leaks(files)

    total = sum(p.stat().st_size for p in files)
    print(f"✓ 元数据: {meta['slug']}@{meta['version']} / {meta['displayName']}")
    print(f"✓ 文件: {len(files)} 个，未压缩 {total / 1024:.0f}KB")

    if args.check:
        return 0

    zip_path = build(files, meta)
    print(f"✓ 目录: {DIST / PKG_NAME}")
    print(f"✓ 压缩包: {zip_path}（{zip_path.stat().st_size / 1024:.0f}KB）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
