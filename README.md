<div align="center">
  <img src="docs/assets/hero.svg" alt="Storyframe — a production system for videos made by agents" width="100%" />
  <h1>Storyframe Video Skill</h1>
  <p><strong>把视频当成一个工程，而不是会动的 PPT。</strong><br />
  故事 · 证据 · 时间 · 声音 · 验收</p>
  <p>
    <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/version-1.4.2-F2416B?style=flat-square" alt="Version 1.4.1" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-17141A?style=flat-square" alt="MIT License" /></a>
    <img src="https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+" />
    <img src="https://img.shields.io/badge/node-20%2B-339933?style=flat-square&logo=node.js&logoColor=white" alt="Node 20+" />
    <img src="https://img.shields.io/badge/ffmpeg-required-007808?style=flat-square&logo=ffmpeg&logoColor=white" alt="ffmpeg" />
    <img src="https://img.shields.io/badge/any%20agent-any%20model-17141A?style=flat-square" alt="Any agent, any model" />
    <a href="https://github.com/nexsjournal/storyframe-video/actions/workflows/check.yml"><img src="https://github.com/nexsjournal/storyframe-video/actions/workflows/check.yml/badge.svg" alt="CI" /></a>
  </p>
  <p>
    <a href="#参考片墙">参考片墙</a> ·
    <a href="#怎么用两种开始方式">怎么用</a> ·
    <a href="#风格库">风格库</a> ·
    <a href="#快速开始">快速开始</a> ·
    <a href="#六种模式">六种模式</a> ·
    <a href="#工作流">工作流</a> ·
    <a href="#faq">FAQ</a>
  </p>
</div>

---

**Storyframe** 是一个面向 AI Agent 的视频生产 Skill —— **不绑定模型，不绑定 harness，不绑定渲染器**。它不负责“生成一段会动的画面”，而是把一支片子拆成可以被执行、被检查、被复现的工程：

- **故事**：观众看完记住哪一句话？
- **证据**：每个产品功能、数据、日期、场地，来源在哪？
- **时间**：镜头、动作、字幕、音乐卡点是否对齐？
- **声音**：音乐、口播、音效是否在同一条叙事线上？
- **验收**：首帧、黑帧、响度、字幕、CTA 是否真的过了一遍？

默认交付不是“几个创意”，而是 **MP4 + 封面 + SRT + 可复现工程 + 验收报告**。

<p align="center">
  <a href="https://nexsjournal.github.io/storyframe-video/assets/storyframe-promo.mp4"><img src="docs/assets/storyframe-promo-loop.gif" width="86%" alt="Storyframe 30 秒宣传片片段：视频不是剪出来的，是写出来的" /></a>
</p>

<p align="center"><sub>上面是它自己做的 30 秒宣传片的循环片段（124 BPM，硬切全部落在拍上，配乐由代码合成）· <a href="https://nexsjournal.github.io/storyframe-video/assets/storyframe-promo.mp4">看完整版 ▶</a></sub></p>

> **速度**：12 秒 1080p30 全片（含配乐合成、预览、终版、每拍 QA 缩略图）实测 **8 秒**；60 秒片 **约 25 秒**。渲染层用 Canvas `draw(t)` + 硬切卡点 + ffmpeg 管道，单帧 9 ms。
>
> **适用面**：任意 Agent（Claude Code / Codex / DSH / Cursor / Cline / Zed / 自建 loop）、任意模型（强模型从零写场景，快模型填模板）、任意渲染栈（内置 canvas 参考实现，也可以换成 Remotion / manim / 录屏）。详见 [适用于任何 Agent 和模型](#适用于任何-agent-和模型)。
>
> 适用于：产品推广、功能发布、知识讲解、口播优化、活动宣传、课程演示、音乐 MV。
> 默认画幅：16:9 / 9:16 / 1:1 / 4:5；常见时长 15–180 秒（MV 跟随歌曲长度）。

> 想直接开始？看 [两种开始方式](#怎么用两种开始方式)；想先找感觉，往下就是 [参考片墙](#参考片墙)。

---

## 目录

- [参考片墙](#参考片墙)
- [适用于任何 Agent 和模型](#适用于任何-agent-和模型)
- [怎么用：两种开始方式](#怎么用两种开始方式)
- [风格库](#风格库)
- [为什么是 Storyframe](#为什么是-storyframe)
- [你能得到什么](#你能得到什么)
- [六种模式](#六种模式)
- [工作流](#工作流)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [工具链](#工具链)
- [质量门禁](#质量门禁)
- [示例](#示例)
- [素材与工具](#素材与工具)
- [设计原则](#设计原则)
- [FAQ](#faq)
- [发布（维护者）](#发布维护者)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

---

## 参考片墙

先看片找感觉；每张卡都标了关键词，记住关键词就能直接调用。

> 点图看片，点作者名看原帖。缩略图、视频版权归各创作者；这里只做索引与链接，不复制视频文件。

<table>
<tr>
<td width="33%" valign="top">
  <a href="https://skillry.dev/ai-videos/opus-5-5/moritzkremb-466494"><img src="https://media.skillry.dev/opus-5-5/moritzkremb-466494/original.dc5bd867e2.webp" width="100%" alt="UI Cinema reference"></a><br>
  <strong>01 · UI 电影</strong><br>
  <sub><code>UI电影</code> <code>界面变形</code></sub><br>
  <sub>product · explainer</sub><br>
  <sub><a href="https://skillry.dev/ai-videos/opus-5-5/moritzkremb-466494">看片</a> · <a href="https://x.com/moritzkremb">@moritzkremb</a></sub>
</td>
<td width="33%" valign="top">
  <a href="https://skillry.dev/ai-videos/opus-5-5/brainextends-606193"><img src="https://media.skillry.dev/opus-5-5/brainextends-606193/original.f7353b2aa2.webp" width="100%" alt="Kinetic Type reference"></a><br>
  <strong>02 · 动态字体</strong><br>
  <sub><code>动态字体</code> <code>字随声音</code></sub><br>
  <sub>event · product · mv</sub><br>
  <sub><a href="https://skillry.dev/ai-videos/opus-5-5/brainextends-606193">看片</a> · <a href="https://x.com/brainextends">@brainextends</a></sub>
</td>
<td width="33%" valign="top">
  <a href="https://skillry.dev/ai-videos/opus-5-5/lukasersil-726495"><img src="https://media.skillry.dev/opus-5-5/lukasersil-726495/original.2886d94586.webp" width="100%" alt="3D showreel reference"></a><br>
  <strong>03 · 3D 产品</strong><br>
  <sub><code>3D产品</code> <code>材质</code></sub><br>
  <sub>product · event · mv</sub><br>
  <sub><a href="https://skillry.dev/ai-videos/opus-5-5/lukasersil-726495">看片</a> · <a href="https://x.com/lukasersil">@lukasersil</a></sub>
</td>
</tr>
<tr>
<td width="33%" valign="top">
  <a href="https://x.com/notdwd/status/2103995183255998633"><img src="https://media.skillry.dev/opus-5-5/_prompts/notdwd-998633/poster.3ade3adf5d.webp" width="100%" alt="Editorial reference"></a><br>
  <strong>04 · 编辑排版</strong><br>
  <sub><code>编辑排版</code> <code>杂志感</code></sub><br>
  <sub>product · explainer · event</sub><br>
  <sub><a href="https://x.com/notdwd/status/2103995183255998633">看片</a> · <a href="https://x.com/notdwd">@notdwd</a></sub>
</td>
<td width="33%" valign="top">
  <a href="https://skillry.dev/ai-videos/opus-5-5/heyiammallik-293397"><img src="https://media.skillry.dev/opus-5-5/heyiammallik-293397/original.7068f7995f.webp" width="100%" alt="Data Instrument reference"></a><br>
  <strong>05 · 数据仪器</strong><br>
  <sub><code>数据仪器</code> <code>HUD</code></sub><br>
  <sub>product · explainer · course</sub><br>
  <sub><a href="https://skillry.dev/ai-videos/opus-5-5/heyiammallik-293397">看片</a> · <a href="https://x.com/heyiammallik">@heyiammallik</a></sub>
</td>
<td width="33%" valign="top">
  <a href="https://skillry.dev/ai-videos/opus-5-5/rneayan-441493"><img src="https://media.skillry.dev/opus-5-5/rneayan-441493/original.334013836e.webp" width="100%" alt="Risograph reference"></a><br>
  <strong>06 · 丝网印</strong><br>
  <sub><code>丝网印</code> <code>Riso</code></sub><br>
  <sub>event · explainer · mv</sub><br>
  <sub><a href="https://skillry.dev/ai-videos/opus-5-5/rneayan-441493">看片</a> · <a href="https://x.com/rneayan">@rneayan</a></sub>
</td>
</tr>
<tr>
<td width="33%" valign="top">
  <a href="https://x.com/byaiden_vu/status/2104846080722755862"><img src="https://media.skillry.dev/opus-5-5/_prompts/byaiden-vu-755862/poster.de09358b34.webp" width="100%" alt="Paper Craft reference"></a><br>
  <strong>07 · 纸感手作</strong><br>
  <sub><code>纸感</code> <code>剪纸</code></sub><br>
  <sub>explainer · event · product</sub><br>
  <sub><a href="https://x.com/byaiden_vu/status/2104846080722755862">看片</a> · <a href="https://x.com/byaiden_vu">@byaiden_vu</a></sub>
</td>
<td width="33%" valign="top">
  <a href="https://skillry.dev/ai-videos/opus-5-5/eric-khun-667455"><img src="https://media.skillry.dev/opus-5-5/eric-khun-667455/original.071b07fb62.webp" width="100%" alt="Hand-drawn reference"></a><br>
  <strong>08 · 手绘叙事</strong><br>
  <sub><code>手绘</code> <code>绘本</code></sub><br>
  <sub>explainer · course · event</sub><br>
  <sub><a href="https://skillry.dev/ai-videos/opus-5-5/eric-khun-667455">看片</a> · <a href="https://x.com/eric_khun">@eric_khun</a></sub>
</td>
<td width="33%" valign="top">
  <a href="https://skillry.dev/ai-videos/opus-5-5/mozetech-471882"><img src="https://media.skillry.dev/opus-5-5/mozetech-471882/original.9e4feb7be1.webp" width="100%" alt="Pixel World reference"></a><br>
  <strong>09 · 像素世界</strong><br>
  <sub><code>像素</code> <code>8-bit</code></sub><br>
  <sub>explainer · course · event · mv</sub><br>
  <sub><a href="https://skillry.dev/ai-videos/opus-5-5/mozetech-471882">看片</a> · <a href="https://x.com/MozeTech">@MozeTech</a></sub>
</td>
</tr>
<tr>
<td width="33%" valign="top">
  <a href="https://skillry.dev/ai-videos/opus-5-5/tomandrieu96707-875264"><img src="https://media.skillry.dev/opus-5-5/tomandrieu96707-875264/original.810c91d85c.webp" width="100%" alt="Collage reference"></a><br>
  <strong>10 · 拼贴</strong><br>
  <sub><code>拼贴</code> <code>collage</code></sub><br>
  <sub>mv · event · explainer</sub><br>
  <sub><a href="https://skillry.dev/ai-videos/opus-5-5/tomandrieu96707-875264">看片</a> · <a href="https://x.com/TomAndrieu96707">@TomAndrieu96707</a></sub>
</td>
<td width="33%" valign="top">
  <a href="https://skillry.dev/ai-videos/opus-5-5/johnsavage-ai-427263"><img src="https://media.skillry.dev/opus-5-5/johnsavage-ai-427263/original.d2b14d5754.webp" width="100%" alt="Retro Future reference"></a><br>
  <strong>11 · 复古未来</strong><br>
  <sub><code>复古未来</code> <code>CRT</code></sub><br>
  <sub>event · mv · product</sub><br>
  <sub><a href="https://skillry.dev/ai-videos/opus-5-5/johnsavage-ai-427263">看片</a> · <a href="https://x.com/johnsavage_ai">@johnsavage_ai</a></sub>
</td>
<td width="33%" valign="top">
  <a href="https://skillry.dev/ai-videos/opus-5-5/sudo-kiran-335993"><img src="https://media.skillry.dev/opus-5-5/sudo-kiran-335993/original.c03cff47d2.webp" width="100%" alt="Process Explainer reference"></a><br>
  <strong>12 · 流程讲解</strong><br>
  <sub><code>流程</code> <code>recipe</code></sub><br>
  <sub>explainer · course · product</sub><br>
  <sub><a href="https://skillry.dev/ai-videos/opus-5-5/sudo-kiran-335993">看片</a> · <a href="https://x.com/sudo_kiran">@sudo_kiran</a></sub>
</td>
</tr>
</table>

## 适用于任何 Agent 和模型

这个 skill 最初是为了让**跑得快、上下文紧的小模型**也能做出「代码动画」级别的片子，所以它把"判断"从模型脑子里搬到了文件里：

| 它依赖什么 | 怎么保证换模型还能用 |
|---|---|
| 决策 | 落成 `BRIEF.md` / `DIRECTION.md` / `plan.json` / `QA.md`，下一个模型直接读，不用重新猜 |
| 时间 | 落成 `audio/beats.json` 的拍点，不靠"感觉"对齐 |
| 检查 | 落成脚本（`check_delivery.py` / `snap_plan.py` / `loudness.py`），不靠模型自觉 |
| 画面 | 落成 `src/scene.js` 的一个 `draw(t)` 函数，改内容不改架构 |

### 三档用法：环境不同，路径不同

| 你的环境 | 怎么用 | 结果 |
|---|---|---|
| **强模型 + 能跑命令的 harness** | 从零写 `src/scene.js`，自由设计画面 | 30 秒片端到端 ≤3 分钟（实测 2 分 48 秒） |
| **快模型 / 小模型**（flash 类、本地 7B–30B） | 不从零写场景：改模板三处（`src/config.js` 文案、`src/scene.js` 数据数组、`src/stage.js` 的 `PALETTE`），用现成组件拼 | 同一条流水线，少一轮返工 |
| **只有工具调用、不能跑 shell** | 用现成素材 + 音乐走剪辑/合成路径，`plan.json` 当时间线，人工核对 | 交付仍完整，只是没有代码动画 |

### 兼容性

- **Agent / harness**：任何读取 `SKILL.md` 的 agent 都能用（Claude Code、Codex、DSH、Cursor、Cline、Zed、自建 agent loop）。不调用厂商 SDK，不需要 MCP，不需要特定 IDE。
- **模型**：任意。强弱模型的差别只体现在"写多少代码"，不体现在"能不能出片"。
- **渲染器**：`starter/` 里的 Playwright + ffmpeg 是**参考实现**，只要求两条——同一 `t` 渲染同一帧、切点落在拍上。Remotion、manim、Three.js、DOM + 录屏、剪映/PR 时间线都能接。
- **降级**：缺 python / node / ffmpeg / Chrome 时的替代路径写在 [SKILL.md 的「依赖与降级」](SKILL.md) 里。

### 它自己就是证据

<p align="center">
  <a href="https://nexsjournal.github.io/storyframe-video/assets/storyframe-promo.mp4"><img src="docs/assets/storyframe-promo-cover.jpg" width="100%" alt="Storyframe 30 秒宣传片：点开播放" /></a>
</p>

<p align="center"><sub><strong>▶ 点开播放</strong> · 30 秒 · 1920×1080 / 30fps · 124 BPM 全程卡点 · 配乐也是代码合成的<br />
这条片子是用这个 skill 自己做的：端到端 <strong>2 分 48 秒</strong>，其中渲染（900 帧 1080p）<strong>46 秒</strong>、单帧 9.6 ms。</sub></p>

---

## 怎么用：两种开始方式

你不需要先学会写分镜。选一种开始就行。

### A. 已经有文案、音乐或素材（最顺）

一次给齐四样：**目标、文案、音乐、素材路径**。

```text
用 storyframe-video-skill 做一条 30 秒 16:9 官网宣传片。
文案在 ./copy.md，音乐在 ./music.mp3（已授权商用）。
产品截图和 Logo 在 ./assets/。
必须出现：产品名、官网 URL、10 月 24 日发布会。
不要出现：竞品名、未上线功能。
```

如果你连 prompt / 分镜都写好了，再加一句：

> 按这个 prompt 做，不要改文案；只做一个方向，先给 640 长边预览。

这就是**快车道**：不生成 3 个方向，不做 1080p 对比图，先出低分辨率预览，再终渲。60 秒片通常 12–20 分钟；细节见 [快车道](references/fast-lane.md)。

### B. 只有一句话，或只有一个风格关键词

只有一句话也能开始：

```text
用 storyframe-video-skill 做一条宣传片，产品是「绘声绘色」。
```

不想找参考片，就直接说风格：

```text
用 storyframe-video-skill 做一条 30 秒产品片，UI 电影 + 暗色 + 快节奏。
```

Agent 会先问三组问题，而不是一次抛 7 个：

1. **要什么片**：类型、平台、画幅、时长；看完希望观众做什么。
2. **文案**：有没有现成文案/口播稿/歌词/大纲？粘贴或给路径。
3. **音乐与素材**：有没有音乐/歌曲/配音文件？给路径或链接；产品截图、录屏、Logo、字体、参考片也一起给。也可以直接说风格关键词（`UI电影` / `纸感` / `像素` / `Riso`…）。

你回答“没有/你定”也可以。Agent 会给出默认方案，并写进 `BRIEF.md` 的“假设”。

### 四个 Gate：你只需要在这些点出现

> 输入已齐、走快车道时，不需要逐个过四个 Gate：只需要 **P1 首帧**（可跳过）和 **P2 预览**。下面是探索型项目的标准 Gate。

- **Gate A**：选方向。别说“高级一点”，说“选 B，但强调色换成品牌绿”。
- **Gate B**：看分镜/animatic。按时间码提：“0–3 秒信息太满，删第二行”。
- **Gate C**：粗剪。先静音看一遍，再听一遍；画面/声音/字幕分开说。
- **Gate D**：终版。确认日期、价格、CTA、二维码停留时间。

完整的使用步骤、五种常见起点、每个 Gate 怎么反馈，见 [`references/usage-playbook.md`](references/usage-playbook.md)。

## 风格库

**看完参考片，直接说关键词。** 比如：

> 用 storyframe-video-skill 做一条 30 秒产品片，**UI 电影 + 暗色 + 快节奏**。

我会先加载对应预设；探索型项目给 3 个叙事轴不同的方向，输入已齐的快车道只锁 1 个方向。风格只决定视觉层：材质、运动、排版、禁忌；故事、证据、时间、声音仍然从产品/主题推导。

### 一句话选风格

| 关键词 | 风格 | 适合 | 参考片 |
|---|---|---|---|
| `UI电影` `界面变形` `一镜到底` | **UI Cinema** · 真实界面在状态之间连续变形 | product · explainer | [Ramp HQ](https://skillry.dev/ai-videos/opus-5-5/moritzkremb-466494) · [UI morph](https://skillry.dev/ai-videos/opus-5-5/twoclipping-402193) |
| `动态字体` `大字` `字随声音` | **Kinetic Type** · 字就是画面，按节拍变形 | event · product · mv | [VOICE WAITING](https://skillry.dev/ai-videos/opus-5-5/gdgtify-929495) · [Spotify](https://skillry.dev/ai-videos/opus-5-5/brainextends-606193) |
| `3D产品` `产品世界` `材质` | **Product 3D** · 一个 hero 物体，真实材质与相机 | product · event · mv | [phone / frame](https://skillry.dev/ai-videos/opus-5-5/twoclipping-496100) · [3D showreel](https://skillry.dev/ai-videos/opus-5-5/lukasersil-726495) |
| `编辑排版` `杂志感` `瑞士网格` | **Editorial** · 网格、字号对比、版面即镜头 | product · explainer · event | [“200”](https://skillry.dev/ai-videos/opus-5-5/signalz-jp-918002) · [OBLT](https://skillry.dev/ai-videos/opus-5-5/iamtanzil-120030) |
| `数据仪器` `HUD` `仪表盘` | **Data Instrument** · 数据像仪器一样被读取 | product · explainer · course | [data list](https://skillry.dev/ai-videos/opus-5-5/heyiammallik-293397) · [chart](https://skillry.dev/ai-videos/opus-5-5/nikolajankovic-616097) |
| `丝网印` `Riso` `双色印刷` | **Risograph** · 2–4 个专色、错版、纸纹 | event · explainer · mv | [Riso studio](https://skillry.dev/ai-videos/opus-5-5/rneayan-441493) |
| `纸感` `纸艺` `剪纸` | **Paper Craft** · 纸片、层影、定格 | explainer · event · product | [paper battery](https://x.com/byaiden_vu/status/2104846080722755862) · [shadow theatre](https://skillry.dev/ai-videos/opus-5-5/x4b47x-034026) |
| `手绘` `绘本` `卡通` | **Hand-drawn** · 线条会呼吸，角色有表演 | explainer · course · event | [ULTRACODE](https://skillry.dev/ai-videos/opus-5-5/daniel-mac8-306214) · [Mid-Autumn](https://skillry.dev/ai-videos/opus-5-5/eric-khun-667455) |
| `像素` `8-bit` `体素` | **Pixel World** · 16/32 网格、阶梯运动 | explainer · course · event · mv | [pixel wizard](https://skillry.dev/ai-videos/opus-5-5/majidmanzarpour-927543) · [pixel game](https://skillry.dev/ai-videos/opus-5-5/mozetech-471882) |
| `拼贴` `collage` `混合媒介` | **Collage** · 剪贴、胶带、错位 | mv · event · explainer | [collage](https://skillry.dev/ai-videos/opus-5-5/tomandrieu96707-875264) · [poster collage](https://x.com/hakimieiqbal/status/2103456327636762926) |
| `复古未来` `CRT` `Y2K` | **Retro Future** · 扫描线、铬字、终端 | event · mv · product | [OPUS 5.5](https://skillry.dev/ai-videos/opus-5-5/johnsavage-ai-427263) · [brand](https://x.com/notdwd/status/2103995183255998633) |
| `流程` `步骤` `recipe` | **Process Explainer** · 一个流程从空到满 | explainer · course · product | [cocktail](https://skillry.dev/ai-videos/opus-5-5/ror-fly-880547) · [green energy](https://skillry.dev/ai-videos/opus-5-5/sudo-kiran-335993) |

### 风格修饰词

预设决定“语法”，修饰词只调“语气”。最多叠加 2 个，超过 3 个会互相打架。

| 修饰词 / 触发 | 具体做什么 | 不要做什么 |
|---|---|---|
| **极简** · `极简` `白底` `Apple风` | 去掉 50–70% 元素；暖白/墨黑 + 1 强调色；字号加大；运动变慢 | 变成空镜头；信息不足 |
| **暗色** · `暗色` `发布会` `科技感` | 近黑底、单光束、铬/玻璃、产品局部高光 | 蓝紫渐变 + 粒子雨 |
| **高饱和** · `高饱和` `多巴胺` `Y2K` | 3–4 个高饱和专色；大面积色块；硬边 | 颜色超过 5 个；刺眼 |
| **单色** · `单色` `monochrome` `黑白` | 一个色相 + 纸/墨；靠明度/字号/构图 | 全灰、没有焦点 |
| **胶片** · `胶片` `颗粒` `16mm` | 颗粒、halation、轻微 gate weave、暖高光 | 颗粒盖住字幕 |
| **快节奏** · `快节奏` `卡点` `高能` | 0.5–1.5s 切；beat map 驱动；impact 同帧 | 全程 0.2s 闪切；没有呼吸 |

### 参考片怎么拆

拿到一支参考片，不要只说“我喜欢这个感觉”。拆三层：

| 层 | 看什么 | 不要抄什么 |
|---|---|---|
| 结构 | 时长、镜头数、平均镜头长度、信息释放顺序、转场频率 | 具体镜头顺序 |
| 视觉 | 主色/辅色/强调色、字体、构图、材质、运动 | 配色和画面 |
| 声音 | 音乐类型/BPM/能量曲线、音效位置、人声处理 | 原曲和音效 |

拆完写一句：“我借它的 **结构/语法**，不借它的 **画面**。”说不清借的是哪一层，就是抄。然后映射到最近的预设，再加一个只属于这个产品的 motif。

### 更多参考

参考片墙只选了每种语法各 1 支主片。想看同风格的其他片子，按作者名或作品名在公开平台继续找；只借结构/语法，不复制画面。

> 参考片链接指向公开作品页或作者页。缩略图、视频版权归各创作者；本仓库只做索引，不复制视频文件。商用前按原作品/素材许可逐项确认。

## 为什么是 Storyframe

普通“AI 视频”最容易出的五个问题，以及 Storyframe 的对应做法：

| 问题 | 常见结果 | Storyframe 的做法 |
|---|---|---|
| 首帧是空白/半成品 | 平台缩略图废掉，点击率低 | 首帧先做成完整画面，再播动画；自动检查首帧 ink 比例 |
| 每个镜头长得一样 | 像会动的 PPT | 每个镜头至少一个运动/转场/主体动作；连续静态卡片 ≤ 2 |
| 画面很满，但没有 claim | 看完记不住，也无法验证 | 一句话承诺 + 每条 claim 记录来源；高风险信息必须确认 |
| 音乐是后贴的 | 动作和声音不同帧 | 先建 beat map，再让切点/音效落在动作帧 |
| 只有 MP4，没有工程 | 改一版就重做 | 保留 `plan.json`、素材清单、导出参数、QA 记录 |

一句话：**先把“看完记住什么”定下来，再决定画面。**

## 你能得到什么

| 交付物 | 说明 |
|---|---|
| `videos/final.mp4` | H.264 High、`yuv420p`、CRF 16–18、AAC 320 kbps、`+faststart` |
| `videos/final.srt` | 可关闭字幕；与烧录字幕同源 |
| `videos/cover.png` | 平台封面/缩略图，单独导出 |
| `plan.json` | 机器可读的 shots / actions / audio cues；自动检查的输入 |
| `BRIEF.md` | 目标、受众、平台、必须出现、证据、限制、假设 |
| `DIRECTION.md` | 选定的方向、视觉规范、镜头表 |
| `SCRIPT.md` | 逐句/逐行脚本、口播/歌词、来源 |
| `STORYBOARD.md` | 镜号、时间、画面、动作、声音、转场 |
| `QA.md` | 自动检查 + 人眼/人耳检查 + 残留风险 |
| `README.md` | 复现命令、素材来源、导出参数 |

> 不知道自己要什么风格？直接说关键词：`UI电影` `纸感` `动态字体` `像素` `Riso` `流体着色器` `音频反应`… 24 种预设见 [风格库](#风格库)。

### 它不会做什么

- 不会把未发布功能伪装成已上线；概念稿必须标注“概念/原型”。
- 不会用未授权的音乐、字体、素材进入成片。
- 不会用“电影级”“完美”这类无法验证的词代替验收。
- 不会把参考片的配色和镜头顺序直接搬过来；只借结构/语法。

## 六种模式

| 模式 | 适合 | 默认时长 | 核心结构 | 主视觉 | 声音 |
|---|---|---:|---|---|---|
| `product` | 产品推广、功能发布、SaaS / App | 30–45s | Hook → 痛点 → 真实演示 → 证据 → CTA | 真实 UI、3D 界面、动态字 | 音乐 + 动作音效 |
| `explainer` | 知识点讲解、科普、方法论 | 60–120s | 问题 → 3 个要点 → 例子 → recap → CTA | 图解、类比、动态字 | 口播 + 轻音乐 |
| `oral` | 口播优化、访谈、课程口播 | 30–90s | 钩子 → 收紧 → 字幕/B-roll → CTA | 原片、跳剪、放大、关键词 | 人声修复 + 音乐 |
| `event` | 活动宣传、展会、发布会 | 15–30s | 钩子 → 什么/谁/何时/何地 → CTA | 海报动效、大字、场地 | 高能量音乐 + 冲击 |
| `course` | 课程演示、软件教学、操作步骤 | 60–180s | 目标 → 步骤 → 结果 → 复习 | 录屏、放大、标注 | 口播 + 点击音 |
| `mv` | 音乐 MV、品牌主题曲 | 歌曲长度 | Intro → Verse → Chorus → Bridge → Final → Outro | 视觉世界、动态字、3D | 歌曲 + 声音设计 |

混合需求先定 **主模式**，再叠加次模式。例如“活动宣传 + 产品演示”用 `event` 的节奏，借 `product` 的真实 UI；不要同时套两套结构。

## 工作流

> 如果 prompt / 文案 / 素材 / 音乐都已给齐，走 [快车道](references/fast-lane.md)：跳过 Research、3 个方向、animatic 和 1080p rough cut；先出 640 长边预览，再终渲。下面是探索型项目的完整流程。

```mermaid
flowchart LR
  I["0 · Intake"] --> R["1 · Research"]
  R --> D["2 · Direction"]
  D --> GA{"Gate A"}
  GA --> S["3 · Script"]
  S --> ST["4 · Storyboard"]
  ST --> GB{"Gate B"}
  GB --> B["5 · Build"]
  B --> SO["6 · Sound"]
  SO --> RC["7 · Rough cut"]
  RC --> GC{"Gate C"}
  GC --> FR["8 · Final render"]
  FR --> QA["9 · QA"]
  QA --> GD{"Gate D"}
  GD --> DE["10 · Deliver"]
```

| 步骤 | 做什么 | 产出 |
|---|---|---|
| 0 Intake | 判断模式；收文案、音乐、素材；只问缺的 | `BRIEF.md` |
| 1 Research | 把“卖点”变成可核对的证据 | 证据表 |
| 2 Direction | 拆参考片，给 3 个不同轴的方向 | `DIRECTION.md` |
| 3 Script | 写“看完记住的一句”，再写逐句词 | `SCRIPT.md` |
| 4 Storyboard | 分镜 + `plan.json` + animatic | `STORYBOARD.md`、`plan.json` |
| 5 Build | 先接真实素材，再做动效/剪辑 | 可渲染工程 |
| 6 Sound | 音乐卡点、口播修复、音效、混音 | `audio/`、混音报告 |
| 7 Rough cut | 看节奏、静音看信息、听声音 | `QA.md` |
| 8 Final render | 确定性导出 | `final.mp4`、`final.srt`、`cover.png` |
| 9 QA | 自动检查 + 人看/人听 | 验收报告 |
| 10 Deliver | 交付 MP4 + 封面 + SRT + 工程 + README | 可复现包 |

### 四个 Gate

> 快车道只有两个人工点：P1 首帧（可跳过）+ P2 640 长边预览。下表是标准流程的 Gate。

| Gate | 位置 | 通过标准 |
|---|---|---|
| **A** | 方向之后 | 一句话承诺 + 选定的方向 + 时长/画幅 |
| **B** | 分镜/animatic 之后 | 时间对、信息清、claims 有证据、首帧成立 |
| **C** | 粗剪之后 | 静音也能看懂；音乐不盖人声；字幕可读 |
| **D** | 交付之前 | `check_delivery.py` 无 error；人看/人听/手机看通过 |

Gate 不是形式。跳过 A/B 直接渲染，通常会在最后返工。

## 快速开始

**环境要求**

- Python 3.10+
- `ffmpeg` / `ffprobe`（检查媒体、响度、编码）
- Node.js 20+（只有用 `starter/` 做代码驱动渲染时需要）
- Chrome / Chromium（Playwright 逐帧截图时需要）

```sh
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt-get update && sudo apt-get install -y ffmpeg
```

### 1. 安装成 Agent Skill

**Claude Code：**

```sh
git clone git@github.com:nexsjournal/storyframe-video.git \
  ~/.claude/skills/storyframe-video-skill
```

**Codex / DSH / 其他读取 `SKILL.md` 的 Agent：**

```sh
git clone git@github.com:nexsjournal/storyframe-video.git \
  ~/.agents/skills/storyframe-video-skill
```

如果仓库已经克隆在别处，软链过去即可：

```sh
ln -s /path/to/storyframe-video ~/.agents/skills/storyframe-video-skill
```

**Cursor / Cline / Zed / 其他 IDE 内 agent：**

```sh
git clone git@github.com:nexsjournal/storyframe-video.git \
  ~/.agents/skills/storyframe-video-skill

# 在项目里给 agent 加一条规则，指明技能位置
echo '视频任务先读 ~/.agents/skills/storyframe-video-skill/SKILL.md' >> .cursor/rules/storyframe.mdc
```

**不能装技能目录的 harness（网页版、API 直连、自建 loop）：**

把 `SKILL.md` 作为系统提示或首条消息注入，`references/` 与 `scripts/` 放在它可读的目录里即可。它只要求"能读文件、能跑命令"，不要求任何插件机制。

> 目录名建议用 `storyframe-video-skill`，与 `SKILL.md` 的 `name` 一致。不同 Agent 的技能目录不同，只要是“包含 `SKILL.md` 的文件夹”即可。想确认装没装对：让 agent 说一句"读你的 SKILL.md，告诉我默认流水线六步"，能答出来就是通了。

### 2. 从技能市场安装

本 skill 发布在 [SkillHub](https://www.skillhub.cn/skills/storyframe-video)（slug：`storyframe-video`）：

```sh
skillhub install storyframe-video
```

**WorkBuddy：** 左侧「专家·技能·连接器」→「技能」→ 市场里的 SkillHub 分类搜 “Storyframe”；或用本仓库的 `dist/storyframe-video-skill.zip`，走「添加技能」→「上传技能」。

### 3. 60 秒建一个工程

```sh
git clone git@github.com:nexsjournal/storyframe-video.git
cd storyframe-video
python3 -m pip install -r requirements.txt

# 有文案/音乐就直接带进来；会复制到工程并登记到 plan.json
python3 scripts/init_project.py \
  --output ~/Videos/my-film \
  --mode product \
  --title "My Product" \
  --duration 30 \
  --aspect 16:9 \
  --script ./copy.md \
  --music ./music.mp3
```

没有文案或音乐时，删掉对应的 `--script` / `--music` 即可。`init_project.py` 会生成模板、目录、`plan.json` 骨架，以及 `SOURCES.json`（记录用户素材的来源与复制位置）。

### 4. 一条命令出片

```sh
cd ~/Videos/my-film
cp -R <skill-dir>/starter/* .
npm install

# ① 合成配乐 + 节拍网格（六种预设，3 秒出 60 秒曲子）
python3 <skill-dir>/scripts/make_music.py --preset uplift --duration 30 \
  --out audio/music.wav --grid audio/beats.json

# ② 预览 + 终版 + 每拍 QA 缩略图，一条命令跑完
node make.mjs --duration 30 --final

# 用用户自己的歌：跳过合成，直接用它的时长当时间源
node make.mjs --duration 45 --audio ./music.mp3 --skip-music --final
```

`make.mjs` 依次做：对齐 `duration` → 配乐/接手音乐 → 640×360/24fps 预览 → 1920×1080/30fps 终版（硬件编码优先）→ 每拍一张 QA 缩略图 → 首帧静帧 → 出片报告。

**改一段只重渲一段**：

```sh
node render.mjs --from 12 --to 20 --output parts/p3.mp4 --audio audio/music.wav
node render.mjs --concat parts --audio audio/music.wav --output videos/final.mp4
```

**卡点校验**（时间点是否都落在拍上）：

```sh
python3 <skill-dir>/scripts/snap_plan.py plan.json --beats audio/beats.json --check --tolerance 0.03
```

不要把预览渲成 1080p，不要用 1080p 静帧做方向对比，不要在改一版之后整片重渲：单帧成本、分辨率、帧数三个旋钮决定一切，见 [`references/render-speed.md`](references/render-speed.md)。

### 5. 检查交付

```sh
python3 scripts/contact_sheet.py videos/final.mp4 --out renders/contact.png --fps 1
python3 scripts/loudness.py videos/final.mp4 --json > audio/loudness.json
python3 scripts/check_delivery.py plan.json --video videos/final.mp4 \
  --mix-report audio/loudness.json --captions videos/final.srt
```

自动检查通过 ≠ 好看。画面语义、听感、字幕可读性必须人看、人听、手机看。

## 项目结构

### 这个仓库

```text
.
├── SKILL.md                  Agent Skill 入口；模式、流程、Gate、硬规则
├── README.md                 本文件
├── CHANGELOG.md              版本记录
├── LICENSE                   MIT
├── references/               16 份方法文档
│   ├── fast-lane.md          默认六步流水线：音乐优先、一次出片、只重渲改动段
│   ├── render-speed.md       渲染速度：五个旋钮、实测对照、时间预算
│   ├── usage-playbook.md     用户怎么用、怎么给反馈
│   ├── intake-and-modes.md   Intake、六种模式、素材清单
│   ├── direction.md          参考拆解、三个方向、专属手法
│   ├── style-presets.md      24 种风格关键词、视觉/运动规则、参考片
│   ├── script-and-voice.md   钩子、结构、口播节奏
│   ├── oral-and-course.md    口播/课程剪辑
│   ├── storyboard-and-plan.md 分镜、plan schema、音效 cue
│   ├── visual-and-motion.md  色彩、字体、镜头、转场
│   ├── audio-and-music.md    音乐、SFX、混音、响度
│   ├── suno-lyrics.md        Suno 歌词制作单
│   ├── review-and-qa.md      审片、联系表、移动端检查
│   ├── formats-and-delivery.md 画幅、安全区、编码、SRT
│   ├── case-study-drawmusic.md 绘声绘色 MV 复盘
│   └── case-study-framyriad.md 一帧亿影 MV 复盘
├── scripts/                  Python 工具
│   ├── init_project.py       建工程、接收文案/音乐
│   ├── make_music.py         代码合成配乐 + 节拍网格（六种预设）
│   ├── snap_plan.py          plan 时间点吸附到拍点、卡点校验
│   ├── lyric_budget.py       BPM / 小节 / 字数 / 行长
│   ├── contact_sheet.py      视频联系表
│   ├── still_sheet.py        静帧对比表（方向/风格）
│   ├── loudness.py           Integrated / True Peak / LRA
│   └── check_delivery.py     plan / 媒体 / 首帧 / 黑帧 / 响度 / 字幕
├── templates/                项目模板（BRIEF / DIRECTION / SCRIPT / STORYBOARD / QA / Suno / plan）
├── starter/                  Playwright + ffmpeg 确定性渲染工程（canvas draw(t)）
├── docs/assets/              README 配图
├── tools/package_skill.py    发布打包与校验（SkillHub / WorkBuddy）
└── .github/workflows/check.yml
```

### 生成后的视频工程

```text
my-film/
├── BRIEF.md
├── DIRECTION.md
├── SCRIPT.md
├── STORYBOARD.md
├── plan.json
├── SOURCES.json              # 用户文案/音乐的交接记录
├── DESIGN.md                 # 可选，视觉规范
├── assets/                   # 原素材、截图、logo、字体（有授权）
│   └── copy/                 # 用户提供的文案
├── audio/                    # 音乐、SFX、mix_report.json
├── src/                      # 代码驱动工程
├── renders/                  # 联系表、关键帧、对比图
├── videos/
│   ├── final.mp4
│   ├── final.srt
│   └── cover.png
├── QA.md
└── README.md                 # 复现命令、素材来源、导出参数
```

## 工具链

| 工具 | 作用 | 常用命令 |
|---|---|---|
| [`init_project.py`](scripts/init_project.py) | 建工程、复制模板、接收文案/音乐 | `python3 scripts/init_project.py --output ./my-film --mode product --title "..." --script ./copy.md --music ./music.mp3` |
| [`make_music.py`](scripts/make_music.py) | 代码合成配乐 + 节拍网格（uplift / pulse / cinematic / edm / warm / ambient） | `python3 scripts/make_music.py --preset uplift --duration 30 --out audio/music.wav --grid audio/beats.json` |
| [`snap_plan.py`](scripts/snap_plan.py) | 把 plan 的切点/动作时间吸附到拍点并报告漂移 | `python3 scripts/snap_plan.py plan.json --beats audio/beats.json --check --tolerance 0.03` |
| [`make.mjs`](starter/make.mjs) | 一条命令：配乐 → 预览 → 终版 → 每拍缩略图 → 报告 | `node make.mjs --duration 30 --final` |
| [`lyric_budget.py`](scripts/lyric_budget.py) | Suno 歌词：BPM / 小节 / 时长 / 字数 / 行长 / Hook | `python3 scripts/lyric_budget.py lyrics.md --bpm 124 --bars 27 --hook "绘声绘色，画就会唱"` |
| [`contact_sheet.py`](scripts/contact_sheet.py) | 1–2 fps 视频联系表，检查整体节奏 | `python3 scripts/contact_sheet.py videos/final.mp4 --out renders/contact.png --fps 1` |
| [`still_sheet.py`](scripts/still_sheet.py) | 多张静帧拼一张带标签的对比表；方向对比不逐张发 | `python3 scripts/still_sheet.py renders/preview/*.jpg --out renders/compare.png --label` |
| [`loudness.py`](scripts/loudness.py) | Integrated / True Peak / LRA | `python3 scripts/loudness.py videos/final.mp4 --json` |
| [`check_delivery.py`](scripts/check_delivery.py) | plan / 媒体 / 首帧 / 黑帧 / 响度 / 字幕检查 | `python3 scripts/check_delivery.py plan.json --video videos/final.mp4 --captions videos/final.srt` |

### 歌词预算示例

```sh
python3 scripts/lyric_budget.py lyrics.md --bpm 124 --bars 27 \
  --hook "绘声绘色，画就会唱"
```

输出会给出：每小节时长、总时长、逐行汉字数/字符数、行长预算、Hook 是否成立。超预算时先删词，不要加速。

## 质量门禁

`check_delivery.py` 目前检查：

- `plan.json` 必填字段、shot 覆盖 0–duration、无 gap/overlap、action 在 shot 内
- 音效 cue 的 `actionId` 是否存在、`syncOffset` 是否和动作帧对齐
- 视频宽高、fps、时长是否与 plan 一致
- 首帧是否空白（ink 比例）、0.5s 是否仍空白
- 黑帧区间是否超过 0.3s
- 音频流是否存在；Integrated LUFS / True Peak 是否接近目标
- SRT 行数、每行字数、最后一条字幕是否超出片长

它**不能**证明：

- 画面是否好看、信息是否清楚
- 音乐是否好听、音效是否抢戏
- 字幕是否在手机上可读
- claims 是否真实

这些必须按 [`references/review-and-qa.md`](references/review-and-qa.md) 人看、人听、手机看。

## 示例

这支 30 秒宣传片是 skill 用自己做的：七段结构、硬切全部落在拍上、配乐由 `make_music.py` 现场合成。

<p align="center">
  <a href="https://nexsjournal.github.io/storyframe-video/assets/storyframe-promo.mp4"><img src="docs/assets/storyframe-promo-cover.jpg" width="68%" alt="30 秒宣传片封面，点开播放" /></a>
</p>

<p align="center">
  <img src="docs/assets/promo-01-hook.jpg" width="24%" alt="开场：视频不是剪出来的，是写出来的" />
  <img src="docs/assets/promo-03-styles.jpg" width="24%" alt="24 种风格墙，逐拍点亮" />
  <img src="docs/assets/promo-04-beat.jpg" width="24%" alt="beats.json 波形与拍点" />
  <img src="docs/assets/promo-05-cta.jpg" width="24%" alt="结尾安装命令" />
</p>

<p align="center"><sub>1920×1080 · 30fps · H.264 · 30.0s · −15.1 LUFS · 900 帧渲染 9.9 秒 · Canvas `draw(t)` + ffmpeg</sub></p>

<p align="center"><strong><a href="https://nexsjournal.github.io/storyframe-video/assets/storyframe-promo.mp4">▶ 播放这条 30 秒成片（1080p，1.3 MB，浏览器内直接播）</a></strong></p>

### 两个真实案例复盘

| 案例 | 成片参数 | 可以学什么 |
|---|---|---|
| [绘声绘色 48.8s 产品推广 MV](references/case-study-drawmusic.md) | 48.8s · 24 镜 · 52 个音效 cue · −10.6 LUFS | 首帧、3D 副歌、结尾叠化；真实歌曲如何驱动画面 |
| [一帧亿影 48.0s 产品 MV](references/case-study-framyriad.md) | 48.0s · 80 BPM · 8 个 6 秒场景 · −14.2 LUFS | 硬切、地图图钉、学习卡、截图裁切 |

案例只复盘**推导方式**，不要照搬视觉。每个产品都应该有自己的方向。

## 素材与工具

这一节是给你准备素材用的，不是模板库。所有第三方素材上线前都要逐项核对许可。

### 常用素材库

| 类型 | 推荐 | 说明 |
|---|---|---|
| 音乐 | [Mixkit](https://mixkit.co/free-stock-music/)、[Pixabay Music](https://pixabay.com/music/)、[Free Music Archive](https://freemusicarchive.org/) | 逐首核对商用许可；保留下载页/授权截图 |
| 音效 | [Freesound](https://freesound.org/)、[Pixabay SFX](https://pixabay.com/sound-effects/) | CC0/CC BY 要分清；CC BY 需署名 |
| 视频/图片 | [Pexels](https://www.pexels.com/)、[Unsplash](https://unsplash.com/)、[Openverse](https://openverse.org/) | 注意人物肖像/品牌露出 |
| 字体 | [Google Fonts](https://fonts.google.com/)、[Fontshare](https://www.fontshare.com/) | 确认 OFL/商用条款；保留授权 |
| 图标 | [Lucide](https://lucide.dev/)、[Tabler Icons](https://tabler.io/icons) | MIT/ISC；不要混用太多套 |
| 配色 | [Realtime Colors](https://realtimecolors.com/)、[Coolors](https://coolors.co/) | 先定一个强调色，再加中性色 |
| 动效参考 | [Motionographer](https://motionographer.com/)、[Art of the Title](https://www.artofthetitle.com/)、[Behance](https://www.behance.net/) | 只借结构/节奏，不下载素材 |
| 生成音乐/配音 | Suno、ElevenLabs 等 | 核对商用条款；保存生成记录 |

### 素材原则

1. **用户提供 > 已授权/生成 > 代码合成**；来路不明的商业曲不进入成片。
2. 音乐、字体、截图、Logo 都要有来源/许可记录，写进 `README.md` 或 `SOURCES.json`。
3. 产品界面用真实截图/录屏；未发布功能标注“概念/原型”。
4. 二维码/URL 至少停留 3 秒；日期、城市、展位至少出现两次。
5. 参考片只用于拆结构/语法，不直接复刻镜头、配色和文案。

## 设计原则

1. **首帧就是完整画面。** 平台会把第一帧当缩略图；前 5–10 帧不能是空白、纯背景或等待入场。
2. **不是幻灯片。** 每个镜头至少有一个：镜头运动、字体变形、材质转场、主体动作、声音驱动切点。
3. **一个主张。** 整片只推一个核心承诺；所有镜头都在证明它。
4. **声音是叙事。** 默认有音乐、口播/人声、动作音效；关键动作听得见，音画同帧。
5. **可复现。** 代码驱动用 `window.seek(t)`；剪辑类保留 EDL/决策记录、源素材清单和导出参数。
6. **自动检查通过 ≠ 好看。** 必须人看、人听、手机看。

## FAQ

<details>
<summary><strong>支持哪些 Agent 和模型？</strong></summary>

任意。它不调用厂商 SDK、不需要 MCP、不需要特定 IDE；只要 agent 能读文件、能跑命令（或能驱动一个执行环境）就能用。已验证的接法见 [适用于任何 Agent 和模型](#适用于任何-agent-和模型)：技能目录（Claude Code / Codex / DSH / Cursor / Cline / Zed）、网页版/API 直连（把 `SKILL.md` 当系统提示注入）、纯命令行（自己按流程走）。

强弱模型的差别只在"写多少代码"：强模型从零写 `scene.js`，快模型/小模型只改模板三处。不会写动效也能出结构完整的片子。

</details>

<details>
<summary><strong>我的模型不会写复杂的动画代码，还能用吗？</strong></summary>

能，而且这是它的设计前提。`starter/` 已经备好版式、入场、卡点、切镜：你只需要改 `src/config.js` 的文案与时长、`src/scene.js` 里的文字/数字数组、`src/stage.js` 的配色三处。画面组件的加法是"再加一个 `draw` 函数"，不是重写场景。

</details>

<details>
<summary><strong>它和普通 AI 视频生成工具有什么区别？</strong></summary>

普通工具主要解决“生成画面”；Storyframe 解决“这支片子是否成立”：故事、证据、时间、声音、验收。它可以用真实 UI/截图/录屏，也可以用代码做动效；最终交付带工程和 QA，不只是 MP4。

</details>

<details>
<summary><strong>没有文案、没有音乐怎么办？</strong></summary>

直接说“没有”。Agent 会给你两个默认方案（例如“我起草文案 + 代码合成配乐”），确认后继续。没有文案/音乐不会卡住流程，但会写进 `BRIEF.md` 的“假设”。

</details>

<details>
<summary><strong>必须安装 Playwright / Chrome 吗？</strong></summary>

只有用 `starter/` 这套参考实现做代码驱动渲染时需要。只做规划、文案、剪辑类项目时，Python + ffmpeg 就够；连 ffmpeg 都没有时也可以走"素材 + 音乐 + 时间线"的交付路径。降级表见 [SKILL.md 的「依赖与降级」](SKILL.md)。

</details>

<details>
<summary><strong>支持竖版/方形吗？</strong></summary>

支持 16:9、9:16、1:1、4:5。建议先做 16:9 母版，再重排安全区/字号，不要直接裁。

</details>

<details>
<summary><strong>能商用吗？</strong></summary>

代码/文档是 MIT；你产出的片子取决于你使用的音乐、字体、截图、人物肖像等第三方素材的许可。仓库不包含案例中的第三方素材，也不随仓库授权。

</details>

<details>
<summary><strong>会不会套模板？</strong></summary>

不会。流程要求先给 3 个不同轴的方向，再做“因为产品/主题有 X，所以用 Y”的专属手法；反 PPT 规则会拦住“标题 + 三行 bullet”的默认审美。

</details>

## 发布（维护者）

`SKILL.md` 的 front matter 同时承载 Agent 元数据（`name` / `description`）和 SkillHub 发布元数据（`slug` / `displayName` / `version` / `summary` / `license` / `homepage` / `tags`）。改版本时同时更新 `VERSION` 与 `CHANGELOG.md`，然后：

```sh
python3 tools/package_skill.py          # 校验元数据/链接/敏感路径，生成 dist/ 目录与 zip
skillhub publish dist/storyframe-video-skill --dry-run
skillhub publish dist/storyframe-video-skill --changelog "本次变更"
```

- **SkillHub 网页端**也可以直接上传 `dist/storyframe-video-skill-<version>.zip`（开发者中心 → 发布技能）。
- **WorkBuddy** 用 `dist/storyframe-video-skill.zip`：文件名会作为技能名，所以不要带版本号。
- 公开上架 WorkBuddy 技能市场要走开放平台（`open.workbuddy.cn`，需个人或企业认证）；桌面端「上传技能」只是自用/团队导入，不会出现在公开市场。
- 压缩包只含白名单内容：`.internal/`、`.github/`、`tools/`、`.git/`、`__pycache__/` 不会被打包。
- 首次发布需要 API Token：`tools/publish_skillhub.sh` 会交互读取 Token（不回显、不进 shell 历史），也可以手动 `skillhub login --key skh_xxx --host https://api.skillhub.cn`；平台要求账号已实名。

## Contributing

欢迎 issue / PR，尤其是：

- 新的模式案例（附推导过程，不只放成片）
- 更可靠的音画同步/字幕/响度检查
- 新的确定性渲染 starter
- 文档纠错、英文翻译

提交前请跑：

```sh
python3 -m compileall -q scripts

python3 scripts/init_project.py \
  --output /tmp/storyframe-demo \
  --mode product \
  --title "CI Demo" \
  --duration 12

python3 scripts/check_delivery.py --help
python3 scripts/lyric_budget.py --help
python3 scripts/contact_sheet.py --help
python3 scripts/still_sheet.py --help
python3 scripts/loudness.py --help

node --check starter/render.mjs
node --check starter/still.mjs
node --check starter/server.mjs
node --check starter/src/main.js
node --check starter/src/config.js
```

约定：

- 不提交未授权的音乐、字体、截图、Logo。
- 修改 `SKILL.md` 的流程/硬规则时，同步更新 `references/` 和 `templates/`。
- 新增脚本要有 `--help`，并在 CI 里跑通。
- 不要用“完美”“电影级”这类无法验证的词代替验收。

## License

[MIT](LICENSE) © 2026 nexsjournal

案例中的产品名、界面、数据、海报、字体与第三方素材归各自权利方所有，不在本仓库内，也不随本仓库授权。

## Credits

由真实项目复盘整理：

- **绘声绘色 Draw Your Music** — 48.8s 产品推广 MV
- **一帧亿影 FRAMYRIAD** — 48.0s 产品 MV

以及所有让“视频成为工程”成为可能的方法、工具和公开参考资料。

---

<div align="center">
  <sub>If this saves you a re-render, give it a star.</sub><br />
  <a href="https://github.com/nexsjournal/storyframe-video">github.com/nexsjournal/storyframe-video</a>
</div>
