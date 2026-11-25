## 1.4.2

**修 bug：`SKILL.md` 的 frontmatter 是非法 YAML，导致技能在所有用真实 YAML 解析器的 harness 里"装了但加载不到"**（`skill "storyframe-video-skill" is unknown or no longer available`）。

- 根因：`description_en` 的值里有 `videos: 24 style presets…`——英文冒号 + 空格让 YAML 把它当成嵌套映射，整块 frontmatter 解析失败；DSH 的 `parseSkillFile` 捕获异常后 `return undefined`，技能直接从目录里消失。自 1.3 起就存在，只是没人从加载侧验证过。
- 修法：所有长描述字段改成 `>-` 折叠块标量（值单行，不引入空格），`description_zh` / `description_en` / `summary` / `compatibility` / `description` 五个字段全部 YAML 安全。
- 加验证：发布前用 harness 同款 `yaml` 库解析 frontmatter，失败即阻断。同类检查也扫了本机所有已装技能（37 可解析 / 1 报错，唯一报错的就是本技能）。

## 1.4.1 — 2026-11-25

**主题：把“为某个模型/某个 harness 定制”改成“任意 Agent、任意 harness、任意模型都能用”。**

- `SKILL.md` 新增「适用面：任意 Agent、任意 harness、任意模型」：三档用法（强模型从零写场景 / 快模型改模板三处 / 只有工具调用走剪辑路径）、兼容性说明、渲染器可替换的两条前置条件
- 原「不可妥协」拆成 **硬底线 5 条**（真实、首帧、可复现、授权、声音不空）与 **默认口味 8 条**（可偏离，偏离写进 `DIRECTION.md` / `QA.md`，附"什么情况下换"的对照表）
- 新增「依赖与降级」表：缺 python / node / Chrome / ffmpeg / 无 shell / 模型不会写复杂代码时的替代路径，硬底线不变
- 「默认流水线」明确为默认路径而非唯一路径；`Starter` 改称**参考实现**，写明可换 Remotion / manim / Three.js / 录屏
- front matter 增加 `compatibility` 字段，`description` / `summary` / `tags` 补模型与 harness 无关（`model-agnostic` / `harness-agnostic`）
- `references/fast-lane.md` §5：canvas 由"必须"改为"默认实现"，新增「快模型只改三处」表（`config.js` / 数据数组 / `PALETTE`）与「模型无关的写法」
- `references/render-speed.md`：明确实测数字是参考值不是门槛，换机器看趋势
- `README.md` 新增「适用于任何 Agent 和模型」：决策/时间/检查/画面四层如何做到模型无关、三档用法、兼容性清单；安装段补 Cursor / Cline / Zed / 网页版与 API 直连的接法；徽章加 `any agent · any model`
- 版本号升至 1.4.1


## 1.4.0 — 2026-11-24

**主题：把"慢"和"风格少"两件事一次解决 —— 音乐先出、画面按拍布点、Canvas 一次出片。**

### 速度（实测，Apple M4 Pro / 1080p / 12 秒片 360 帧）

- `starter/render.mjs` 重写 v2：CDP 直采 + `--deterministic-mode --run-all-compositor-stages-before-draw --disable-gpu-vsync --disable-frame-rate-limit`，去掉每帧 rAF 等待（默认 `--settle-frames 0`，与 settle=2 输出逐字节一致）
- 帧走 ffmpeg stdin（`-f image2pipe -c:v mjpeg`），不再逐帧写磁盘
- 新增 Canvas 采集快路：页面暴露 `window.__CAPTURE__='canvas'` 时用 `window.__frameJPEG(q)` 页内编码，绕开合成器
- 编码器自动选：macOS 优先 `h264_videotoolbox`，其余 `libx264 -preset veryfast`；`--encoder` 可强制
- 结果：轻 DOM 63 ms/帧 → 14 ms/帧；Canvas 9.2 ms/帧；12 秒 1080p30 **22.7 s → 3.4 s**；640 预览 359–408 fps
- 新增 `--from/--to` 分段重渲 + `--concat` 拼接（`-c:v copy`，只重挂音轨），改一段只渲一段
- 新增 `--beat-sheet N`：渲染时顺手存"每 N 拍一张"QA 缩略图，不再对成片跑第二遍抽帧
- 新增 `starter/make.mjs`：一条命令完成 配乐 → 预览 → 终版 → 每拍缩略图 → 首帧 → 报告（12 秒片全流程 8 秒）

### 音乐与卡点

- 新增 `scripts/make_music.py`：numpy/scipy 代码合成配乐，六种预设（`uplift` / `pulse` / `cinematic` / `edm` / `warm` / `ambient`），自动分段（intro/build/main/break/main/outro）、侧链压缩、卷积混响、软限幅、−14 LUFS 归一化、固定 seed 可复现
- 同一命令产出 `audio/beats.json`：BPM、拍点、小节、段落能量、重音表，作为画面时间的唯一来源
- 新增 `scripts/snap_plan.py`：把 `plan.json` 的切点/动作/cue 吸附到 1/sub 拍并报告漂移，`--check` 可直接当卡点门禁
- 新增 `starter/src/stage.js`：canvas 工具层（闭式弹簧、`Grid` 节拍类、`Stage` 采集、排版与图形基元）
- `starter/src/scene.js` 改写为默认演示片「一拍，一帧」：12s/24 拍，六段硬切全部落在拍点，首帧即完成态

### 风格

- `references/style-presets.md`：12 → **24 种视觉语法**，新增流体着色器、粒子群、三维世界、终端 HUD、液态铬、蓝图线框、轨道太空、地图叙事、霓虹复古、故障腐蚀、音频反应、白场极简；附"按渲染成本挑风格"分档表（6 ms → 80 ms）

### 流程与文档

- `SKILL.md` 新增「默认流水线：音乐先走，一次出片」六步图与速度预算；声音硬规则改为**默认无配音**（宣传片只上音乐 + 音效），明确禁止脑补口播/方言念白
- `references/fast-lane.md` 重写为默认执行流程：六步、实测时间表、只重渲改动段、"明确不做的事"清单
- 新增 `references/render-speed.md`：五个时间旋钮、实测对照表（含重 DOM 只快 1.16× 的反例）、旧流程四个慢因、按片长的时间预算、自检命令
- `references/audio-and-music.md` 增补代码合成配乐、六预设表、卡点 API 用法与校验
- `starter/still.mjs` 重写 v2：快参数、JPEG 默认、`--beat-sheet`、`--sheet` 直接拼表
- `starter/index.html` 改 canvas 舞台 + `src/scene.js`；旧 DOM 演示保留为 `starter/dom.html`
- README 快速开始改为"一条命令出片"，工具链表补 `make_music.py` / `snap_plan.py` / `make.mjs`
- 版本号升至 1.4.0


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
