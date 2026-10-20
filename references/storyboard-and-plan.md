# 分镜与 plan

分镜不是“画面描述”，而是 **时间、信息、动作、声音** 的对齐表。代码驱动的片子，分镜要同时写成机器可读的 `plan.json`。

## 1. 时间数学

### 帧
```text
frame = round(t * fps)
t = frame / fps
```
30fps 下 1 帧 = 33.3ms；不要在 30fps 里写“0.01s”这种不可渲染的时间。

### BPM / beat / bar
```text
beat = 60 / BPM
bar = beat * 4        # 4/4
barIndex = floor(t / bar)
beatInBar = floor((t % bar) / beat)
```
音乐驱动片先建 `beats.json`：`bpm / beats / bars / duration`，所有切点/动作从 beat/bar 取。

### 覆盖
`shots` 必须覆盖 `0–duration`：

```text
shot[0].start == 0
shot[i].end == shot[i+1].start   (±0.05s)
shot[n-1].end == duration        (±0.05s)
```

不允许 gap（中间黑屏）或 overlap（两个镜头同时占时间）。

## 2. 镜头表

```md
| ID | 起止 | 画面/构图 | 文案 | 动作 | 声音 | 转场 | 证据 |
|---|---|---|---|---|---|---|---|
| s01 | 0.0–1.5 | 首帧完整：产品 UI + 大字 | 画一条线，它就会唱 | 线条生长 | 笔刷 + 低频 | 硬切 | 产品录屏 |
```

- **画面**：写“观众看到什么”，不是“放一个标题”。
- **文案**：屏幕上出现的字；口播另列。
- **动作**：谁/什么在动，从哪到哪。
- **声音**：音乐变化/音效；关键动作必须写。
- **转场**：硬切/闪白/扫描/wipe/匹配剪辑；写原因。
- **证据**：claim 来源/素材路径。

## 3. plan.json

最小结构：

```json
{
  "title": "Project title",
  "mode": "product",
  "duration": 30,
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "language": "zh",
  "audience": "...",
  "platform": "web",
  "cta": "...",
  "style": {
    "palette": ["#F6F1E6", "#17141A", "#F2416B"],
    "type": "display/body",
    "motion": "push/stagger/scan"
  },
  "shots": [
    {
      "id": "s01",
      "start": 0,
      "end": 2.0,
      "description": "完整首帧：产品界面 + 标题 + 品牌",
      "descriptionAt": 0,
      "transition": "cut",
      "claim": "真实产品界面",
      "source": "assets/ui.png",
      "actions": [
        {"id": "a01", "at": 0.4, "description": "笔刷从左侧落下"}
      ]
    }
  ],
  "audio": {
    "music": {"file": "audio/music.wav", "bpm": 128, "gain_db": -18},
    "cues": [
      {"at": 0.4, "kind": "brush", "gain_db": -14, "pan": 0, "actionId": "a01", "syncOffset": 0, "file": "audio/sfx/brush.wav"}
    ],
    "targetLufs": -14,
    "truePeakDbtp": -1.0
  }
}
```

### 必填
- 顶层：`title/mode/duration/fps/width/height/shots`。
- shot：`id/start/end/description/descriptionAt`。
- audio：`cues`（可为空，但静音要记录原因）。

### 推荐
- `audience/platform/cta/style/claim/source/actions/transition`。
- `audio.targetLufs`（默认 −14）、`truePeakDbtp`（默认 −1.0）。
- `audioExceptionReason`：如果用户要求无音乐/无音效。

## 4. 动作与音效

- 每个关键动作有 `action.id`；对应 cue 写 `actionId`。
- `cue.at + syncOffset ≈ action.at`；`syncOffset` 用来补偿音效起音延迟（impact 常为负，whoosh 常为正）。
- 不是每个动作都要音效；优先级：**动作反馈 > 转场 > 环境**。
- 音效文件缺失时，先生成/找替代，不要留空 cue。

## 5. 首帧

首帧是缩略图，不是“动画第 0 帧”。

- 放开场段落的 **完成态**：产品/主题 + 标题 + 品牌/日期。
- 文字可读；不要依赖 0.5s 后才出现的元素。
- 之后再淡出/进入动画；不要首帧空白。
- 9:16 首帧同样要完整；不要把 16:9 直接裁成竖屏。

## 6. Animatic

在正式动效前，用静帧 + 临时音轨按时间播放：

- 每镜静帧 1–3 张；按 `plan.json` 的时间切。
- 听节奏：信息是否来得及？镜头是否太长/太碎？
- 看首帧/结尾：是否成立？
- 改 `plan.json`，不要直接改代码。

## 7. 转场选择

| 转场 | 什么时候用 | 什么时候不用 |
|---|---|---|
| 硬切 | 同场景/同主体/节奏点 | 两个完全不同的世界 |
| 闪白 | 副歌/冲击/时间跳 | 连续使用（刺眼） |
| 扫描/wipe | 扫描、读取、段落切换 | 与主题无关的装饰 |
| whip | 快速移动/空间转换 | 信息密集处 |
| match cut | 形状/动作/颜色匹配 | 没有匹配关系时 |
| 材质转场 | 纸/墨/液体/像素世界 | 写实产品演示 |

转场要服务“空间/时间/信息”的变化；不要为了炫技每 2 秒换一种。

## 8. 分镜检查

- [ ] 时间覆盖无 gap/overlap？
- [ ] 首帧完整？
- [ ] 每镜有动作/运动/转场？
- [ ] 连续静态卡片 ≤2？
- [ ] 关键动作有音效？
- [ ] 每个 claim 有来源？
- [ ] 结尾 CTA 至少 3 秒？
- [ ] 9:16 安全区重排过？
