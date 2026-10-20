# Changelog

## 1.1.0 — 2026-10-20

- 首轮改为“素材交接”：只问三组（要什么片 / 文案 / 音乐与素材），不再一次抛 7 个问题
- 明确用户文案与音乐的处理规则：原文为准、音乐为时间基准、不覆盖、不静默改写
- 新增 `references/usage-playbook.md`：用户怎么开场、四个 Gate 怎么反馈、三种常见起点
- `init_project.py` 支持 `--script` / `--music`，复制素材、登记 `plan.json`、生成 `SOURCES.json`
- MV 模式未指定时长时，自动跟随用户音乐时长
- `BRIEF.md` / `SCRIPT.md` 增加文案来源、音乐授权、素材核验表
- 新增内部参考库（仅方向阶段使用，不对外暴露来源）
- 重写公开 README：徽章、Mermaid 工作流、示例静帧、素材库、FAQ、Contributing、MIT License
- CI 增加 `--script/--music` 素材交接测试

## 1.0.0 — 2026-10-20

首个公开版本。

- 六种模式：product / explainer / oral / event / course / mv
- 10 步流程 + 4 个 Gate（A–D）
- `init_project.py` 一键建工程
- Suno 歌词预算、联系表、响度、交付检查 4 个脚本
- Playwright + ffmpeg 的确定性 starter
- 两份真实案例：绘声绘色 48.8s MV、一帧亿影 48.0s 产品 MV
