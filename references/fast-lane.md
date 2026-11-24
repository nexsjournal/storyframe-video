# 快车道：音乐先走，一次出片

这份文件是**默认执行流程**，不是备选方案。除了"方向完全没定、需要比稿"的探索型项目，其余都走这里。

核心变化（相对 v1）：**先做音乐和节拍网格，再写画面**。音乐是时间源，画面跟着拍点布；不是先写完画面再找音乐硬凑。

---

## 1. 流水线：六步，一条命令收口

```
① 定参数      时长 / 画幅 / 模式 / 风格关键词          →  BRIEF.md
② 出音乐      make_music.py → music.wav + beats.json     ←  时间源
③ 锁首帧      1 张 640 静帧（可跳过）                    →  DIRECTION.md
④ 写场景      canvas draw(t)，所有切点读 beats.json      →  src/scene.js
⑤ 一次出片    make.mjs → preview + final + 每拍联系表    ←  只渲一次
⑥ 一轮精修    只重渲改动段，concat 回整片
```

**时间预算（60 秒片，本机实测）**

| 步骤 | 目标 | 实测 |
|---|---:|---:|
| ② 音乐 + 网格 | 20 s | 3 s（uplift 60s） |
| ③ 首帧 | 20 s | 2 s |
| ④ 写场景 | 由内容决定 | — |
| ⑤ 预览 + 终版 + 联系表 | 60 s | 25 s |
| ⑥ 一轮精修 | 30 s | 5–10 s |
| **合计（不含写代码）** | **< 3 min** | **~35 s** |

---

## 2. ① 定参数：只问缺的

不重复问用户已经说过的东西。只确认三项，缺的按默认值写进 `BRIEF.md` 的"假设"：

1. 时长 / 画幅 / 用途（product / explainer / event / mv / course / oral）
2. 文案：有没有现成文字、必须出现的信息（产品名、日期、URL、价格）
3. 音乐：给文件，还是用代码合成（给风格词：`uplift` / `pulse` / `cinematic` / `edm` / `warm` / `ambient`）

**默认值**：30 秒 / 16:9 / 音乐 = 代码合成 `uplift` / **无配音**。

---

## 3. ② 音乐与节拍：先有拍，才有画面

```sh
# 合成配乐 + 节拍网格（一条命令，两个产物）
python3 scripts/make_music.py --preset uplift --duration 30 \
  --out audio/music.wav --grid audio/beats.json
```

`beats.json` 是后面所有时间的唯一依据：

```json
{ "bpm": 124, "beatDur": 0.4839, "barDur": 1.9355, "duration": 30,
  "beats": [0, 0.4839, ...], "bars": [0, 1.9355, ...],
  "sections": [{"name":"intro","start":0,"end":3.87,"energy":0.35}, ...],
  "accents": [0, 0.4839, ...] }
```

**用户给了音乐文件时**：不要重新生成，不要替换。`ffprobe` 量时长，用它当时间源；BPM 未知时用 `--bpm` 手工给一个，或按 120 兜底并在 `BRIEF.md` 记"BPM 为估计值"。

---

## 4. ③ 首帧：一张 640，不看三张

```sh
node still.mjs 0 --preview      # renders/preview/still_0.00.jpg（640 短边）
```

只发这一张，问一句"首帧方向对吗"。用户说"直接做"就跳过，把选择写进 `DIRECTION.md`。

**首帧必须是完整画面**：主体、标题、品牌至少各就位一个。入场动画从第 0 帧之后再开始。做法：把入场弹簧的起点设成负时间（`spring(local + 0.55, ...)`），切点那一帧已经是完成态。

---

## 5. ④ 写场景：一个时间纯函数，渲染器随便换

默认用 canvas `draw(t)`（`starter/src/scene.js` + `stage.js`）；**换成 DOM / Three.js / 录屏也行**，只要满足下面三条——这三条是硬约束，canvas 只是默认实现：

1. 一切画面 = `f(t)`。没有 `setTimeout`、没有 CSS transition、没有帧间状态。
2. 每个切点、每次入场都读 `grid.beat(n)` / `grid.bar(n)`，不写死秒数。
3. 单帧成本可控：Canvas2D 图形与文字最便宜；`backdrop-filter`、大半径 `blur`、多层 `box-shadow`、`ctx.filter` 会让单帧涨到 5–7 倍，用之前先量。

### 快模型 / 小模型：只改三处，不写渲染逻辑

| 改这里 | 换什么 | 例子 |
|---|---|---|
| `src/config.js` | 标题、时长、画幅、主题色 | `duration: 30`、`title: '绘声绘色'` |
| `src/scene.js` 里的数据数组 | 每段的文字、数字、卡片内容 | `MODES`、`STYLES`、`SPEED` |
| `src/stage.js` 的 `PALETTE` | 配色（纸/墨/强调色） | `accent: '#FF3B5C'` → 品牌色 |

版式、入场、卡点、切镜全部由模板负责。这样即使模型不会写动效，也能出结构完整的片子；要新的画面组件，再加一个 `draw` 函数，不要重写整个场景。

### 模型无关的写法

- 判断写进文件，不要留在"我记得上一轮说过"里。
- 每个段落一个函数（`S1`…`S7`），入场时间用参数传，便于单独改一段。
- 命名用 `S1/S2/S3` 或语义名，换模型接手时能立刻定位到"第几段"。

写完后用 `snap_plan.py` 检查时间点是否都在拍上（有 `plan.json` 时）：

```sh
python3 scripts/snap_plan.py plan.json --beats audio/beats.json --check --tolerance 0.03
```

---

## 6. ⑤ 一次出片：预览、终版、联系表一起出

```sh
node make.mjs --duration 30 --preset uplift --final
```

它做四件事，中间不停：

1. 合成音乐 → `audio/music.wav` + `audio/beats.json`
2. 640×360 / 24fps 预览 → `videos/preview.mp4`（1–3 秒）
3. 1920×1080 / 30fps 终版 + 每拍一张 QA 缩略图 → `videos/final.mp4` + `renders/beats/`
4. 首帧静帧 + 出片报告（时长、节拍、体积、总耗时）

**联系表**（一次看完整片节奏，6×4）：

```sh
ffmpeg -y -pattern_type glob -i 'renders/beats/*.jpg' \
  -vf "scale=320:-1,tile=6x4:padding=6:margin=6:color=0x141219" -frames:v 1 renders/sheet.jpg
```

这张图是**唯一**需要的画面审片材料。不要再看 1080p 抽帧，不要对成片跑第二遍抽帧脚本。

---

## 7. ⑥ 精修：只重渲改动段

```sh
# 假设 12–20 秒那段要改
node render.mjs --from 12 --to 20 --output parts/p3.mp4 --audio audio/music.wav
node render.mjs --concat parts --audio audio/music.wav --output videos/final.mp4
```

`--concat` 用 `-c:v copy` 拼接，不重编码视频，只重挂音轨，几秒完成。

**修改上限**：结构一轮（在预览前后）、细节一轮（终版后）。超过两轮说明输入没锁死，回 ① 而不是继续试。

---

## 8. 明确不做的事

| 不做 | 为什么 | 替代 |
|---|---|---|
| 每条片子先跑 Suno 歌词单 | 只有 `mv` 且用户提供人声/歌词时才需要；纯配乐用代码合成更快、无版权问题 | `make_music.py` |
| 默认加配音、口播、方言念白 | 用户没要求就没有人声；宣传片用音乐 + 动作音效 | 只出音乐；要人声时明确问 |
| 每帧等 rAF / 1080p PNG 静帧 | 白等 16.7–33 ms/帧、写盘慢 | settle=0 + JPEG + pipe |
| 先渲 1080p 看结构 | 像素成本平方级 | 640 预览 |
| 渲完再抽帧扫成片 | 解码 + 拼图额外几秒到几十秒 | `--beat-sheet 1` 顺手存 |
| 三个方向各渲一条片 | 时间是线性叠加 | 1 个方向 + 最多 3 张 480 缩略图 |
| 每改一版全片重渲 | 90% 的帧没变 | `--from/--to` + `--concat` |

---

## 9. 验收（快车道版）

- [ ] `audio/music.wav` 存在，`beats.json` 的 `bpm / beatDur / duration` 与成片一致
- [ ] 所有切点落在拍上（差 ≤ 30 ms）：`snap_plan.py --check`
- [ ] 首帧是完成画面，不是空白/纯背景
- [ ] 预览 ≤ 5 秒出、终版 ≤ 30 秒出（60 秒片）
- [ ] 每拍联系表能看出完整叙事，没有空帧、黑帧、重复静态卡
- [ ] 成片里没有任何人声（除用户明确要求）
- [ ] 音量：−14 LUFS 附近，峰值 ≤ −1 dBTP
