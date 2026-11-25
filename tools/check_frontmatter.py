#!/usr/bin/env python3
"""校验 SKILL.md 的 YAML frontmatter 能被真实 YAML 解析器读通。

为什么需要它：frontmatter 是 harness 发现技能的唯一入口。一个英文冒号 + 空格
（`videos: 24 style presets`）就会让 YAML 把它当成嵌套映射，整块解析失败；
DSH 的 parseSkillFile 捕获异常后直接丢弃该技能，用户看到的是
`skill "xxx" is unknown or no longer available`——文件明明在硬盘上。

用法：
    python3 tools/check_frontmatter.py [SKILL.md ...]     # 默认 ./SKILL.md
退出码 0 = 全部通过；1 = 有文件解析失败或缺少必需字段。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - 依赖缺失时给出可操作提示
    sys.exit("需要 PyYAML：pip install pyyaml")

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")  # harness 的 kebab-case 规则
REQUIRED = ("name", "description")


def check(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---", raw, re.S)
    if not m:
        return ["缺少 frontmatter（文件必须以 --- 开头，并以 --- 收尾）"]
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        line = getattr(exc, "problem_mark", None)
        where = f"第 {line.line + 1} 行" if line else "未知行"
        return [
            f"YAML 解析失败（{where}）：{str(exc).splitlines()[0]}",
            "常见原因：值里有英文冒号+空格、以 @ ` [ { 开头、或用 # 开头——加引号或改 >- 折叠块",
        ]
    if not isinstance(data, dict):
        return ["frontmatter 不是映射"]
    problems = [f"缺少必需字段 {k}" for k in REQUIRED if not isinstance(data.get(k), str) or not data.get(k).strip()]
    name = data.get("name")
    if isinstance(name, str) and not NAME_RE.match(name):
        problems.append(f"name 不符合 kebab-case 规则：{name!r}")
    return problems


def main(argv: list[str]) -> int:
    targets = [Path(p) for p in argv[1:]] or [Path("SKILL.md")]
    failed = 0
    for path in targets:
        if not path.exists():
            print(f"✗ {path}: 文件不存在")
            failed += 1
            continue
        problems = check(path)
        if problems:
            failed += 1
            print(f"✗ {path}")
            for p in problems:
                print(f"   - {p}")
        else:
            data = yaml.safe_load(re.match(r"^---\r?\n(.*?)\r?\n---", path.read_text(encoding="utf-8"), re.S).group(1))
            print(f"✓ {path}: {data['name']} {data.get('version', '')}".rstrip())
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
