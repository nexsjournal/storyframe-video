---
name: storyframe-video-skill
slug: storyframe-video
displayName: Storyframe 视频生产系统
display_name: Storyframe 视频生产系统
display_name_en: Storyframe Video
category: Design Tools
description_zh: >-
  从 brief、文案、音乐到 15–180 秒成片：六种模式、24 种风格预设、代码合成配乐 + 节拍卡点、确定性渲染与自动质检。适配任意 Agent、任意 harness、任意模型：强模型从零写场景，快模型填模板，只有工具调用时走剪辑降级路径。
description_en: >-
  A production system for agent-made videos: 24 style presets, code-synthesized music with a beat grid, beat-locked canvas rendering (9 s for a 12 s 1080p clip), and automated QA.
author: nexsjournal
version: 1.4.2
summary: >-
  模型与 harness 无关的视频生产系统：音乐先出、画面按拍布点、一次出片，Playwright + ffmpeg 确定性渲染与自动质检；强模型写场景、快模型填模板、纯工具调用走剪辑路径；60 秒 1080p 片约 25 秒渲完。
compatibility: >-
  任意 Agent / 任意 harness（Claude Code、Codex、DSH、Cursor、Cline、Zed、自建 loop）/ 任意模型。不依赖任何厂商 SDK 或 MCP；只用文件 + 命令行。
license: MIT
homepage: https://github.com/nexsjournal/storyframe-video
tags: [video, product-video, motion-graphics, storyboard, ffmpeg, playwright, beat-sync, procedural-audio, mv, model-agnostic, harness-agnostic]
description: >-
  从 brief 到成片的标准视频生产系统，覆盖产品推广、知识讲解、口播优化、活动宣传、课程演示和音乐 MV。先接收并核验用户提供的文案、音乐、录屏、截图、Logo 与参考片，再用真实素材、故事方向、分镜、节拍表、声音设计和验收清单，产出 15–180 秒的 16:9 / 9:16 / 1:1 成片；包含代码合成配乐与节拍网格、Playwright + ffmpeg 确定性渲染和自动质检；默认不加配音，画面卡点全部吸附到 beats.json。当用户要求做宣传片、讲解片、活动片、课程演示、口播剪辑、产品片、MV，或要把一段文案/歌曲/录屏变成视频时使用。支持 UI 电影、动态字体、纸感手作、丝网印、像素世界、流体着色器、音频反应等 24 种风格关键词。方法重于工具：渲染器、音乐生成、检查脚本都是参考实现，可以换成环境里已有的能力。
---

# Storyframe 视频生产系统

把视频当成一个 **故事 + 证据 + 时间 + 声音** 的工程，而不是会动的 PPT。每一支片子先回答“观众看完记住什么”，再决定画面、文案、镜头和声音。

本 skill 的默认交付：**能直接投放的 MP4 + 封面 + 字幕 + 可复现工程 + 验收报告**。不是“给几个创意”，也不是“先堆素材再说”。

## 适用面：任意 Agent、任意 harness、任意模型

这不是某个模型的补丁，也不是某个 harness 的插件。它是**方法 + 可替换的参考实现**：判断写成文件，时间写成拍点，渲染交给环境里有的能力。

| 你的环境 | 怎么用 | 期望结果 |
|---|---|---|
| 强模型 + 能跑命令的 harness | 从零写 `src/scene.js`，自由设计画面与动效 | 30 秒片端到端 ≤3 分钟 |
| 快模型 / 小模型（flash 类、本地小模型） | **不要从零写场景**：改模板里的文字、数据、配色三处（见 [快车道 §5](references/fast-lane.md)） | 同样能出片，少走一轮返工 |
| 只有工具调用、不能跑 shell/node | 用现成素材 + 现成音乐走剪辑/合成路径，`plan.json` 当时间线，人工核对 | 交付仍完整，只是没有代码动画 |
| 已有自己的渲染栈（Remotion / manim / Canvas 自建 / 录屏） | 把本 skill 当流程与验收规范，渲染层换掉 | 保留卡点、首帧、QA 的硬底线 |

**兼容性**：不调用任何厂商 SDK、不需要 MCP、不需要特定 IDE；只要能读写文件、能执行命令（或能驱动一个执行环境），就能跑。已按 Claude Code / Codex / DSH / Cursor / Cline / Zed / 自建 loop 的通用约定组织：`SKILL.md` 是唯一入口，其余全是相对路径。

**模型无关靠三件事**：① 决策落成文件（`BRIEF.md` / `DIRECTION.md` / `plan.json` / `QA.md`），换模型、换 harness 都能接着做；② 时间落成拍点（`beats.json`），不依赖"感觉"；③ 检查落成脚本（`check_delivery.py` / `snap_plan.py`），不依赖模型自觉。

**渲染器是可换的**：`starter/` 里的 Playwright + ffmpeg 是参考实现，只要求两条——同一个 `t` 渲染出同一帧、切点落在拍上。换成任何满足这两条的实现都算合格。

---

## 默认流水线：音乐先走，一次出片

这是默认路径，不是唯一路径。缺 python / node / ffmpeg / Chrome 时按文末[依赖与降级](#依赖与降级)表换做法，硬底线不变。

除非"方向完全没定、需要比稿"，默认按这条流水线走。**音乐是时间源，画面跟着拍点布** —— 不是先写画面再找音乐硬凑。

```
① 定参数    时长 / 画幅 / 用途 / 风格词           → BRIEF.md
② 出音乐    scripts/make_music.py                 → audio/music.wav + audio/beats.json
③ 锁首帧    1 张 640 静帧（可跳过）               → DIRECTION.md
④ 写场景    canvas draw(t)，切点读 beats.json     → src/scene.js
⑤ 一次出片  starter/make.mjs                      → preview + final + 每拍联系表
⑥ 一轮精修  只重渲改动段 + concat                  → videos/final.mp4
```

```sh
# ② 配乐 + 节拍网格（六种预设：uplift / pulse / cinematic / edm / warm / ambient）
python3 scripts/make_music.py --preset uplift --duration 30 --out audio/music.wav --grid audio/beats.json

# ⑤ 预览 + 终版 + QA 缩略图，一条命令
cd <project> && node make.mjs --duration 30 --preset uplift --final
```

**速度预算（60 秒 1080p30，本机实测）**：配乐 3 s、预览 4 s、终版 20 s、全流程 < 3 min。单帧成本 > 40 ms 就说明场景有问题（见 [渲染速度](references/render-speed.md)）。

**默认不做**：跑 Suno 歌词单（只有 `mv` 且用户给人声/歌词时才做）、加配音或方言念白、逐帧等 rAF、1080p PNG 静帧、渲完再抽帧扫成片、每改一版全片重渲。

**声音默认只有音乐**：宣传片靠配乐 + 动作音效推进；没有人声需求就不出现人声。要口播/配音时由用户明确提出，并按 `oral` 模式单独处理。

---

## 启动：先接素材，再问问题

用户第一次调用时，不要马上写方案，也不要一次抛出 7 个问题。先做一次 **素材交接**：接住已经给的东西，再只问缺的。

**第一轮只问 3 组（用户已经给了就跳过）：**

1. **要什么片**：用途/类型、发布平台、画幅、目标时长；看完希望观众做什么。用户说不清时，按模式给默认值并说明理由。
2. **文案**：有没有现成文案、口播稿、歌词或大纲？直接粘贴，或给文件路径/链接。有就按原文做；没有就明说“没有”，由我起草。
3. **音乐与素材**：有没有音乐/歌曲/配音文件？给路径或链接。产品链接、截图、录屏、Logo、字体、参考片也一起给路径；也可以直接说风格关键词（UI 电影 / 纸感 / 动态字体 / 像素 / 丝网印…）。

用户已经说过的不要重复问。**附件/路径优先于口头描述**：先读文件、用 `ffprobe` 看时长/采样率/声道、看截图；BPM 另外测/听，再决定还缺什么。

**素材规则：**

- 用户给的文案是事实源：只做删减、口语化、调顺序；改动记在 `SCRIPT.md`。
- 用户给的音乐是时间源：复制到 `audio/`，按它的 BPM/段落卡点；不要重新生成或替换。
- 用户给的路径必须验证存在；读不到就直说，不要假装看过。给的是 URL 就先下载到 `assets/` 或 `audio/`，记录来源。
- 首轮回复格式：`已收到` / `还缺什么` / `我接下来做什么`，不要只发一张问卷。收到文件时先复述“收到什么、放在哪、下一步用它做什么”。
- 没有文案也没音乐时，明确给出两个默认方案（例如“我起草文案 + 代码合成配乐”），让用户确认后再往下走。
- 用户说“别问，直接做”时：按模式默认值做，把假设逐条写进 `BRIEF.md`；只有日期/价格/claim/版权这类高风险信息仍要确认。

**续做已有工程：** 当前目录已有 `BRIEF.md`、`plan.json` 或 `videos/` 时，先读现状并从断点继续；不要重新 intake，不要覆盖已有文件。

## 快车道：输入已齐，直接出片

当用户已经给齐 **prompt/文案 + 素材路径 + 音乐**，或说“别问，直接做”，不要跑完整 0–10。按 [快车道](references/fast-lane.md) 执行：

- **跳过** 3 个方向、完整 research、animatic 视频、1080p rough cut。
- **只做 1 个方向**；最多 3 张 480×270 对比缩略图；首帧只渲 1 张 **640 长边 JPEG**（16:9 = 640×360）。
- 先出 **640 长边 / 12fps** 预览，P2 通过后再出 1080p 终版。
- 只有 **2 个人工点**：首帧确认（可跳过）+ 预览确认；标准流程的 Gate A/B/C 不再逐个停。
- 60 秒片目标：预览 ≤ 5 秒、终版 ≤ 30 秒（canvas `draw(t)` + 硬件编码；实测全流程 ~35 秒，见 [渲染速度](references/render-speed.md)）。

**默认不要**为每个方向生成视频、不要用 1080p PNG 做方向对比、不要先渲完整片再改结构。

**Token 预算（快车道）：** 只读用户点名的文件；只做 1 个方向、1 套分镜、1 条预览；一次最多看 3 张低分辨率对比图或 1 张 6–8 格 contact sheet；确定性检查交给脚本；结构修改 1 轮、细节修改 1 轮，不无限试。

## 最短用法

- 只有一句话：`用 storyframe-video-skill 做一条 30 秒产品宣传片，产品是……`。我会先问“文案、音乐、素材”三组问题。
- 已有文案和音乐：`文案在 ./copy.md，音乐在 ./music.mp3，做 30 秒 16:9，发官网`。核验文件后直接走**快车道**：只做 1 个方向，先给 640 长边预览。
- 已有完整 prompt + 素材 + 音乐：`按 ./prompt.md 做，不要改文案；素材在 ./assets/，音乐在 ./music.mp3`。跳过 intake 和 3 方向，直接铺时间线。
- 只有参考片：`照这个片子的节奏做，但不要抄画面：<链接>`。我会拆结构/视觉/声音，再给三个不同方向。
- 只想说风格：`做一条 30 秒产品片，UI 电影 + 暗色 + 快节奏`。我会加载风格预设，但仍然给三个叙事轴不同的方向。

完整的使用步骤、每个 Gate 该给什么反馈，见 [使用手册](references/usage-playbook.md)。

## 先判断模式

| 模式 | 适合 | 默认时长 | 核心结构 | 主视觉 | 声音 |
|---|---|---|---:|---|---|
| `product` | 产品推广、功能发布、SaaS/App | 30–45s | Hook → 痛点 → 真实演示 → 证据 → CTA | 真实 UI、3D 界面、动态字 | 音乐 + 动作音效 |
| `explainer` | 知识点讲解、科普、方法论 | 60–120s | 问题 → 3 个要点 → 例子 →  recap → CTA | 图解、类比、动态字 | 口播 + 轻音乐 |
| `oral` | 口播优化、访谈、课程口播 | 30–90s | 钩子 → 收紧 → 字幕/B-roll → CTA | 原片、跳剪、放大、关键词 | 人声修复 + 音乐 |
| `event` | 活动宣传、展会、发布会 | 15–30s | 钩子 → 什么/谁/何时/何地 → CTA | 海报动效、大字、场地 | 高能量音乐 + 冲击 |
| `course` | 课程演示、软件教学、操作步骤 | 60–180s | 目标 → 步骤 → 结果 → 复习 | 录屏、放大、标注 | 口播 + 点击音 |
| `mv` | 音乐 MV、品牌主题曲 | 歌曲长度 | Intro → Verse → Chorus → Bridge → Final → Outro | 视觉世界、动态字、3D | 歌曲 + 声音设计 |

混合需求先定 **主模式**，再叠加次模式。例如“活动宣传 + 产品演示”用 `event` 的节奏，借 `product` 的真实 UI；不要同时套两套结构。

## 硬底线（这 5 条偏离 = 交付不合格）

1. **真实与证据。** 产品功能、数据、日期、场地、课程步骤必须可追溯；不编造界面、指标、引语。每条主张记录来源和范围。
2. **首帧就是完整画面。** 平台会把第一帧当缩略图；前 5–10 帧不能是空白、纯背景或等待入场。先把开场段落的完成态放上去，再播动画。
3. **可复现。** 同一输入产出同一结果：代码驱动用 `window.seek(t)` 或等价的时间纯函数；剪辑类保留 EDL/决策记录、源素材清单和导出参数。
4. **版权与授权。** 音乐、字体、素材、产品截图都要有来源/许可；用户没授权的内容不进入成片。
5. **声音不空。** 有音乐、有人声，或"设计过的静音"（并在 `QA.md` 记录原因）。不能出现无理由的无声段。

## 默认口味（可以偏离，偏离要写进 `DIRECTION.md` 或 `QA.md`）

这些是**默认值，不是禁令**。有更好的做法就用更好的，只要说明为什么、以及放弃了哪条默认。

| 默认 | 什么情况下换成别的 |
|---|---|
| 不是幻灯片：每个镜头至少一个运动/转场/主体动作 | 静态海报式收尾、特写停帧也可以，只要片内有节奏对比 |
| 声音只有音乐，不加配音 | 用户要口播、或模式是 `explainer` / `oral` / `course` 时加人声 |
| 画面用 Canvas `draw(t)` | 要真实 UI 就用 DOM；要纵深就用 Three.js；要实拍就剪辑 |
| 预览 640、终版一次出片（`make.mjs`） | 没有 node/Chrome 时换别的渲染器或录屏 |
| 24 种风格预设 + 六种模式 | 用户有明确视觉方向时，预设只作对照，不硬套 |
| 响度 −14 LUFS / ≤ −1 dBTP | 展会大屏 −10.5 到 −12；广播 −23（EBU R128） |
| 中文口播 12–22 字/句、字幕 ≤16 字/行 | 平台/画幅/语言不同时按可读性调整 |
| 切点落在拍上（误差 ≤30 ms） | 无音乐或纯旁白片，用语义断点，但要标在 `plan.json` |

**唯一的判断标准**：交付能不能被验证。能被验证的偏离，比机械遵守默认值更好。

## 标准流程（探索型项目，0–10 共 11 步，4 个 Gate）

> 输入已经锁死（prompt/文案/素材/音乐齐全）时，不要跑这一整套；用上面的[快车道](references/fast-lane.md)。标准流程用于“方向还没定、需要研究/比稿”的项目。

### 0. Intake：定模式与约束

先按“启动：先接素材，再问问题”完成素材交接。下面是完整清单，**不是一次全问**；第一轮只问 3 组，其余随流程补。

1. **类型与目标**：product / explainer / oral / event / course / mv？看完要让观众做什么？
2. **受众与平台**：给谁看？发在哪里？16:9 / 9:16 / 1:1 / 4:5？目标时长？
3. **必须出现**：产品名、卖点、日期、城市、展位、URL、二维码、价格、免责声明。
4. **文案与素材**：有没有现成文案/口播稿/歌词/大纲（路径或粘贴）？产品链接/仓库/截图、录屏、人物素材、Logo、字体、参考视频在哪里？
5. **音乐与声音**：有没有音乐/歌曲/配音文件（路径或链接）？是否可商用、是否要署名？没有的话，用生成/代码合成。
6. **语言与人声**：中文/英文/双语；是否需要口播、配音、字幕；谁的声音。
7. **参考与反参考**：喜欢哪支片子的什么（结构/视觉/声音），讨厌什么（模板感/喊麦/科技蓝）。
8. **限制**：claims 证据、版权、deadline、不能出现的人/品牌/信息。

产出 `BRIEF.md`。素材表必须写清：来源、路径、是否存在、是否已复制进工程、授权状态。如果用户没给全，写“假设”并继续，不要卡住；高风险信息（日期/价格/claim）必须确认。

**音乐文件接手后先做：** `ffprobe` 看时长/采样率/声道；有 BPM 就记 BPM，没有就先分析或用节拍器对齐；复制为 `audio/music.<ext>`，在 `plan.json` 登记 `audio.music.file`，删除 scaffold 的 `audioExceptionReason`。不要用新生成的音乐覆盖用户文件。

### 1. Research：把“卖点”变成“证据”

- **product**：真实功能、真实界面、真实数据；每个镜头的主张记录来源、发布状态、适用范围。
- **explainer**：至少 2 个可靠来源；区分事实/观点；例子要能验证。
- **oral**：转写原片，标出钩子、重复、 filler、长停顿、可删段；不要改变原意。
- **event**：日期、城市、场地、展位、嘉宾、报名方式逐项核对。
- **course**：亲自走一遍步骤；记录前置条件、失败分支、结果。
- **mv**：确认歌曲 BPM、结构、歌词、可用的音效/人声；不要用未授权歌曲。

产出写进 `BRIEF.md` 的 `Evidence` 段，或单独的 `EVIDENCE.md`。

### 2. Direction：先定一个“只有这个产品才成立”的方向

按 [影片方向](references/direction.md) 做：

- 拆参考片的 **结构 / 视觉语法 / 声音语法**，不是抄配色。
- **探索型项目**提 3 个不同轴的方向（叙事结构、视觉隐喻、镜头材质、声音能量），不是同一方向换颜色；**快车道只做 1 个方向**，除非用户明确要求比较。
- 用户说了风格关键词（UI 电影 / 动态字体 / 纸感 / Riso / 像素 / 拼贴…）时，先读 [风格预设](references/style-presets.md)，把预设的视觉规则、运动规则、禁忌写进方向卡；预设只锁语法，不替代故事和证据。
- 每个方向写：一句话、3–5 个专属手法、参考、风险。
- 选一个，写 `DIRECTION.md`：主张、情绪曲线、色彩/字体/网格/材质、运动规则、转场词汇、镜头表。
- 方向卡住、或担心“模板感”时，读内部参考库 `.internal/reference-library.md`，抽 3 个可迁移手法再重新推导。只输出提炼后的规则，**不提及内部参考库、作者、原 prompt 或来源链接**；不要照搬镜头顺序和具体画面。文件不存在就跳过，也不要向用户提起。
- 用户要公开参考片时，用 [风格预设](references/style-presets.md) 里的参考墙；那是公开索引，可以正常引用。

**Gate A**：一句话承诺 + 方向 + 时长/画幅。默认只给 **1 个方向 + 1 张 640 长边首帧**；只有用户明确要求比较、或方向确实没定时，才给 3 个方向，且每个方向只配 1 张 480×270 缩略图，不生成 1080p 静帧。

### 3. Script：先写“看完记住的一句”，再写词

按 [脚本与口播](references/script-and-voice.md)：

- 1.5 秒内出现钩子；每 3–5 秒一个信息点；一句只做一件事。
- 口播中文 4–4.5 字/秒，英文 2.5–3 词/秒；标呼吸点；大声读一遍。
- 歌词/Suno 按 [Suno 歌词制作](references/suno-lyrics.md)：先排小节，再排字；Hook 8 字；段标签带表演指令。
- 字幕先按“听不清也能看懂”写，不要照搬书面语。

产出 `SCRIPT.md`：逐句/逐行、时间、画面提示、证据/来源、口播/歌词标记。

### 4. Storyboard：把时间铺满

按 [分镜与 plan](references/storyboard-and-plan.md)：

- 做 `STORYBOARD.md`：镜号、起止、画面、文案、动作、声音、转场、claim/source。
- 同步写 `plan.json`：shots 覆盖 0–duration，无 gap/overlap；每个 action 有 id；每个必需 action 有音效 cue。
- 首帧单独设计：完整画面 + 品牌/主题 + 可读标题；不要“先黑屏再出字”。
- 先做 **animatic**：静帧 + 临时音轨，按时间播放一遍，检查节奏和信息密度。

**Gate B**：分镜/animatic 通过——时间对、信息清、claims 有证据、首帧成立。快车道可跳过独立 animatic，用 6–8 张 480×270 缩略图拼 contact sheet 代替。

### 5. Build：先接通真实素材，再做动效

- **product**：接真实 UI/组件/数据；截图或录屏要清晰；视频尺度下重排，不要直接把桌面截图缩小。
- **explainer/course**：先做图解/录屏，再做标注；箭头、圈选、放大要指向“正在说的那个东西”。
- **oral**：先做 transcript-based 粗剪，再做字幕、B-roll、放大、音效；不要先加花字。
- **event/mv**：先定视觉世界（纸/墨/光/金属/像素），再做字体和镜头；每个场景至少一个“世界规则”。

按 [视觉与运动](references/visual-and-motion.md) 选手法；每个手法都要能说出“因为产品/主题有 X，所以用 Y”。不要所有元素同一种入场、同一种转场。

### 6. Sound：音乐、口播、音效一起设计

按 [声音与音乐](references/audio-and-music.md)：

- 音乐来源优先级：用户提供 → 已授权/生成 → 代码合成；不要用来路不明的商业曲。
- 口播先修：降噪、EQ、压缩、去齿音、响度；音乐在口播下让 3–6 dB。
- 动作音效落在动作帧：笔刷、点击、盖章、whoosh、riser、impact、扫描、铃声；不是每个 cut 都加。
- 以 `plan.json` 的 `audio.cues` 为准：`at / kind / gain_db / pan / actionId / syncOffset / file`。`audio/sfx_cues.json` 只作可选素材清单，不要两套各写一份。
- 混音后测 loudness；写 `audio/mix_report.json`。

### 7. Rough cut：先看节奏，不看细节

- 快车道先看 **640 长边预览** 和 1–2 fps contact sheet；不要为 rough cut 渲 1080p。
- 每个转场前后 10 fps 条带看匹配；文字密集镜头再抽全尺寸帧。
- 静音看一遍：信息是否还成立？字幕是否够？
- 听一遍：口播是否清楚？音效是否抢？音乐是否盖人声？
- 记录问题到 `QA.md`，一次改一类，不要边看边随机改。

**Gate C**：rough cut 通过——节奏、信息、声音、字幕都成立。

### 8. Final render：确定性导出

- 代码驱动：`window.seek(t)` → 逐帧截图 → ffmpeg 编码；不要用实时录屏。
- 剪辑类：锁定 EDL，统一帧率/色彩空间/音频采样率；导出母版后再压社交版。
- 默认：H.264 High、`yuv420p`、CRF 16–18、`-preset medium`、AAC 320 kbps、`+faststart`；1080p 30fps 为基线。不要默认 `-preset slow`。
- 预览：640 长边、12fps、CRF 30、`-preset veryfast`，先看结构；结构冻结后再终渲。
- 字幕：烧录 + 单独 SRT；封面单独导出。

### 9. QA：自动检查 + 人眼/人耳

运行：

```sh
python3 <skill-dir>/scripts/check_delivery.py plan.json --video videos/final.mp4 \
  --mix-report audio/mix_report.json --captions videos/final.srt
python3 <skill-dir>/scripts/contact_sheet.py videos/final.mp4 --out renders/contact.png --fps 1
python3 <skill-dir>/scripts/loudness.py videos/final.mp4
```

自动检查只证明结构/文件/时长/首帧/响度；**画面语义、听感、字幕可读性必须人看人听**。按 [审片与 QA](references/review-and-qa.md) 做最终检查。

**Gate D**：`check_delivery.py` 无 error；人工检查通过；claims/版权/CTA 确认。

### 10. Deliver：交付可复现的包

```
project/
  BRIEF.md
  DIRECTION.md
  SCRIPT.md
  STORYBOARD.md
  plan.json
  SOURCES.json            # 用户文案/音乐的交接记录（可选）
  DESIGN.md（可选，视觉规范）
  assets/                 # 原素材、截图、logo、字体（有授权）；用户文案在 assets/copy/
  audio/                  # 音乐、SFX、mix_report.json
  src/                    # 代码驱动工程
  renders/                # 联系表、关键帧、对比图
  videos/
    final.mp4
    final.srt
    cover.png
  QA.md
  README.md               # 如何复现
```

交付时说明：哪些是自动检查、哪些实际看过/听过、哪些仍未验证；不要用“完美”“电影级”这类无法证明的词。

## 项目文件最小集

| 文件 | 作用 | 必须 |
|---|---|---|
| `BRIEF.md` | 目标、受众、平台、时长、必须出现、证据、限制 | 是 |
| `DIRECTION.md` | 选定的方向、3–5 个专属手法、视觉规范、镜头表 | 是 |
| `SCRIPT.md` | 逐句/逐行脚本、时间、口播/歌词、来源 | 是 |
| `STORYBOARD.md` | 镜号、时间、画面、动作、声音、转场 | 是 |
| `plan.json` | 机器可读的 shots/actions/audio cues | 是（代码驱动/自动检查） |
| `QA.md` | 检查项、问题、修复、残留风险 | 是 |
| `README.md` | 复现命令、素材来源、导出参数 | 是 |

## 方向规则（避免“模板感”）

- **一个主张**：整片只推一个核心承诺；所有镜头都在证明它。
- **三个轴**：叙事（问题→解决 / 一天 / 对比）、视觉（纸/墨、UI 电影、数据仪器、手作）、声音（轻电子、环境、无音乐）。探索型项目的三个方向必须在这三个轴上不同；快车道只做一个方向。
- **风格预设不是模板**：关键词决定语法（材质、运动、排版、禁忌），叙事轴仍然要重新推导；24 个预设见 [风格预设](references/style-presets.md)。
- **专属手法**：3–5 个“因为产品有 X，所以用 Y”。例如“因为画线会生成旋律，所以让线条在副歌变成声波/五线谱/3D 纸带”。
- **反重复**：同一工作区连续做片，不复用上一支的开场、章节、背景；片内不要所有元素同一种入场。
- **反 PPT**：每场至少一个运动/转场/主体动作；连续静态卡片 ≤2；不要“标题+三行 bullet”重复。

## 脚本规则

- **钩子**：1.5 秒内给问题/反差/结果；不要“大家好，今天我来介绍……”。
- **一句一事**：长句拆短；中文口播每句 12–22 字；英文每句 8–16 词。
- **具体**：动词 + 对象 + 结果；“让创意被看见”不如“画一条线，它就会唱”。
- **CTA**：结尾 3–5 秒；说清“去哪、做什么、什么时候”；二维码/URL 至少停留 3 秒。
- **口播**：标停顿/重音；先读顺，再配画面；不要用书面语硬念。
- **歌词**：Hook 先成立；Verse 写机制；Chorus 写标题+好处；Bridge 写玩法；Outro 写 CTA；按小节/字数预算删词，不加速。

## 分镜与 plan 规则

- `shots` 必须覆盖 `0–duration`，容差 ≤0.05s；不允许 gap/overlap。
- 每个 shot 有 `id`、`start`、`end`、`description`、`descriptionAt`、`transition`。
- 每个 action 有 `id`、`at`、`description`；关键 action 在 `audio.cues` 有对应 `actionId`。
- `syncOffset` 是音效相对 action 的偏移；最终 `cue.at + syncOffset ≈ action.at`。
- 首帧 `0.0s` 必须是完整画面；不要把“入场动画的开始”当首帧。

## 声音规则

| 场景 | 集成响度 | True Peak |
|---|---:|---:|
| 网页/社交 | −14 LUFS | ≤ −1.0 dBTP |
| 展会/大屏 | −10.5 到 −12 LUFS | ≤ −1.0 dBTP |
| 广播 | −23 LUFS（EBU R128） | ≤ −1.0 dBTP |

- 口播下音乐让 3–6 dB；侧链或自动化均可。
- 音效不要盖住辅音；关键动作前后留 50–100ms 空间。
- 低频不要堆；手机外放检查一次。
- 音乐结尾要设计：硬收/铃/混响尾，不要突然断。
- 默认没有配音；宣传片的人声只有在用户要求或 `oral`/`explainer`/`course` 模式才加入，且不加方言/口音演绎。
- 切点即拍点：`beats.json` 的 `beats` / `accents` 是硬切、冲击音效、大字入场的唯一时间源。

## 交付定义（Done）

- [ ] 成片 MP4 可播放，时长/画幅/fps 与 brief 一致。
- [ ] 首帧完整，不是空白/纯背景。
- [ ] 全片无意外黑帧/静帧；最长静止镜头有叙事理由。
- [ ] 每个镜头有运动/转场/主体动作；不是幻灯片。
- [ ] 字幕同步、可读、无溢出；静音也能看懂。
- [ ] 声音有音乐/口播/音效；响度达标；无 clipping。
- [ ] claims/日期/场地/CTA 已核对。
- [ ] `check_delivery.py` 无 error；`QA.md` 记录人工检查与残留风险。
- [ ] 交付 MP4 + 封面 + SRT + 工程 + README。

## 工具入口

```sh
# 一条命令出片（音乐 → 预览 → 终版 → 每拍 QA 缩略图）
node make.mjs --duration 30 --preset uplift --final
node make.mjs --duration 15 --audio ../music.mp3 --skip-music    # 用用户给的歌

# 配乐 + 节拍网格（先跑这个，再写画面）
python3 scripts/make_music.py --preset pulse --duration 30 --out audio/music.wav --grid audio/beats.json
python3 scripts/make_music.py --list                              # 看六个预设

# 低分辨率首帧 / 每拍一帧的联系表
node still.mjs 0 --preview
node still.mjs --beat-sheet --every 2 --out-dir renders/beats

# 只重渲改动段，再拼回整片
node render.mjs --from 12 --to 20 --output parts/p3.mp4 --audio audio/music.wav
node render.mjs --concat parts --audio audio/music.wav --output videos/final.mp4

# 时间点吸附到拍上（卡点检查）
python3 scripts/snap_plan.py plan.json --beats audio/beats.json --check --tolerance 0.03

# 初始化项目（复制模板 + plan 骨架；有文案/音乐就直接带进来）
python3 <skill-dir>/scripts/init_project.py --output <video-dir> --mode product --title "..." \
  --script <copy.md> --music <music.mp3>

# Suno/歌词：按 BPM 和小节算时间、字数、行长
python3 <skill-dir>/scripts/lyric_budget.py lyrics.md --bpm 124 --bars 27 --hook "绘声绘色，画就会唱"

# 响度 / 交付检查（联系表已由 render.mjs --beat-sheet 顺手产出，不必再扫成片）
python3 <skill-dir>/scripts/contact_sheet.py videos/final.mp4 --out renders/contact.png --fps 1
python3 <skill-dir>/scripts/loudness.py videos/final.mp4
python3 <skill-dir>/scripts/check_delivery.py plan.json --video videos/final.mp4 \
  --mix-report audio/mix_report.json --captions videos/final.srt
```

## 依赖与降级

工具是手段，不是门槛。缺什么就用环境里已有的能力替代，硬底线（真实、首帧、可复现、授权、有声）不变。

| 缺什么 | 受影响 | 降级做法（照这个顺序试） |
|---|---|---|
| `python3` | 配乐合成、拍点吸附、交付检查 | 用用户给的音乐；按 BPM 手算拍点写 `beats.json`（`beatDur = 60/BPM`）；用 `ffprobe`/播放器人工核对 |
| `node` / 浏览器 | 代码驱动渲染 | 用 harness 自带渲染、Remotion、manim；或用 DOM 页面 + 系统录屏；`plan.json` 当时间线 |
| `ffmpeg` | 编码、响度、抽帧 | 用系统/云端转码；响度用播放器 + 耳朵；抽帧用播放器截图 |
| 无 shell（只有工具调用） | 一切脚本 | 走剪辑路径：素材 + 音乐 + 字幕；交付时间线/EDL + 工程文件，`QA.md` 写清哪些没自动验证 |
| 无 Chrome headless | `render.mjs` 取帧 | 用有头浏览器 + `--headless=false`；或改用录屏；或换 puppeteer |
| 模型不会写复杂代码 | 画面质量 | 只改模板三处（`config.js` / 数据数组 / `PALETTE`），画面用现成组件组合，不新写渲染逻辑 |

判断标准只有一条：**交付物能不能被验证**。验证不了的，就明确写进 `QA.md`，不要假装跑过。

## 参考索引

- [快车道](references/fast-lane.md)：默认六步流水线、音乐优先、一次出片、只重渲改动段的操作细则。
- [渲染速度](references/render-speed.md)：五个时间旋钮、实测对照表、旧流程为什么慢、时间预算与自检。
- [使用手册](references/usage-playbook.md)：用户要准备什么、怎么开场、四个 Gate 怎么给反馈、五种常见起点。
- [Intake 与六种模式](references/intake-and-modes.md)：问题清单、六种模式、交付物。
- [影片方向](references/direction.md)：参考拆解、三个方向、专属手法、视觉规范。
- [风格预设](references/style-presets.md)：24 种风格关键词、视觉/运动规则、公开参考片，附按渲染成本分档。
- [脚本与口播](references/script-and-voice.md)：钩子、结构、口播节奏、口播优化。
- [口播与课程](references/oral-and-course.md)：原片 paper edit、J/L cut、字幕、录屏步骤、课程节奏。
- [分镜与 plan](references/storyboard-and-plan.md)：镜头表、plan schema、时间覆盖、音效 cue。
- [视觉与运动](references/visual-and-motion.md)：色彩/字体/网格、镜头运动、转场、反 PPT。
- [声音与音乐](references/audio-and-music.md)：音乐来源、SFX、混音、响度。
- [Suno 歌词制作](references/suno-lyrics.md)：小节/字数预算、Hook、段标签、Style、fallback。
- [审片与 QA](references/review-and-qa.md)：快车道 P1/P2、标准 Gate A–D、联系表、常见问题、移动端检查。
- [画幅与交付](references/formats-and-delivery.md)：16:9 / 9:16 / 1:1、安全区、编码、封面、SRT。
- [案例：绘声绘色 MV](references/case-study-drawmusic.md)：48.8s 成片的实际参数、指标与复盘。
- [案例：一帧亿影 MV](references/case-study-framyriad.md)：48.0s 产品 MV 的硬切、真实数据、地图与学习卡复盘。

## Starter

`starter/` 是一个**参考实现**，不是运行前提：canvas 舞台 + `window.seek(t)` + 逐字入场 + 卡片/图表/时间轴组件 + Playwright 取帧 + ffmpeg 编码。复制后：

- 换文案/数据/配色：改 `src/config.js`、`src/scene.js` 里的数据数组、`src/stage.js` 的 `PALETTE`（快模型只动这三处就够）。
- 换渲染器：只要满足"同一 `t` 同一帧 + 切点落在拍上"，用 Remotion / manim / Three.js / DOM + 录屏都行，`make.mjs` 换成对应的构建命令即可。

```sh
cd <project>
npm install                 # 只有用 starter 的渲染器时才需要
node make.mjs --duration 30 --final
```

