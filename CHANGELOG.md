# Changelog

## 1.3.0 — 2026-11-12

- 新增 `references/fast-lane.md`：输入已齐（prompt/文案 + 素材 + 音乐）时的 5 阶段快车道，跳过 3 方向、完整 research、animatic 视频和 1080p rough cut
- 快车道只做 1 个方向、1 张 640 长边首帧；对比图最多 3 张 480 宽/格，contact sheet 每格 320px，不再用 1080p PNG 做方向比较
- 快车道先出 640×360 / 12fps 预览，P2 通过后再终渲；只有 P1 首帧（可跳过）+ P2 预览两个人工点
- `starter/render.mjs` 增加 `--preview` / `--draft`：640 长边、12fps、CRF 30、`veryfast`、JPEG q72，默认输出 `videos/preview.mp4`
- `starter/still.mjs` 增加 `--preview`：640 长边 JPEG q72，输出 `renders/preview/`；新增 `--width/--height/--quality/--format/--out-dir/--prefix`
- 新增 `scripts/still_sheet.py`：把多张静帧拼成一张带标签的对比表，方向对比不逐张发图
- 终渲默认 `-preset medium`（不再默认 `slow`），并减少每帧 settle 次数；新增 `--preset` / `--quality` / `--settle-frames`
- `SKILL.md` / `direction.md` / `usage-playbook.md` / `review-and-qa.md` / `intake-and-modes.md` / README / 模板同步快车道；新增 token 预算与“两轮修改上限”
- `SKILL.md` front matter 增加发布元数据：SkillHub 的 `slug` / `displayName` / `summary` / `license` / `homepage` / `tags`，以及 WorkBuddy 开放平台要求的 `display_name` / `display_name_en` / `category` / `description_zh` / `description_en` / `author`；Agent 侧的 `name` / `description` 保持不变
- 新增 `tools/package_skill.py`：按白名单生成 `dist/` 目录与 zip，校验元数据、相对链接、本机路径泄露，并对齐 SkillHub 10MB 限制
- README 新增“从技能市场安装”“发布（维护者）”两节
- 新增 `docs/assets/icon-512.png`：SkillHub 技能图标（可自定义上传）
- 版本号升至 1.3.0

## 1.2.0 — 2026-10-20

- 新增 `references/style-presets.md`：12 种风格预设（UI 电影、动态字体、3D 产品、编辑排版、数据仪器、丝网印、纸感手作、手绘叙事、像素世界、拼贴、复古未来、流程讲解），含视觉/运动规则、禁忌、参考片与实现提示
- README 新增“风格库”：关键词选风格、12 张参考片卡、6 个风格修饰词、完整参考索引与授权说明
- `SKILL.md` / `direction.md` / `intake-and-modes.md` / `usage-playbook.md` 支持“直接说风格关键词”，不再只依赖参考片
- 明确风格预设只锁视觉语法，仍要输出 3 个叙事轴不同的方向；可读性与证据优先
- README 重排：参考片墙独立前置，新增“两种开始方式”（已有素材 / 一句话或风格关键词），并加顶部跳转
- 版本号升至 1.2.0

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
