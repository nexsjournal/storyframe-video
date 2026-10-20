# 声音与音乐

声音不是“配个 BGM”，而是第二条叙事线：音乐给情绪，音效给动作，人声给信息。

## 1. 音乐来源

优先级：

1. **用户提供**：确认授权/来源；问清是否可商用、是否要署名。
2. **已授权库/生成**：Artlist/Epidemic/Suno 等；保留 license/生成记录。
3. **代码合成**：没有合适素材时，用 Python/Web Audio 合成；可完全控 BPM/结构，但音色要设计。
4. **不要**：来路不明的商业曲、短视频热门音频（除非平台授权明确）。

音乐必须能支撑结构：intro/hook/build/chorus/bridge/outro；不要一首 loop 从头铺到尾。

### 1.1 用户给了音乐文件

先接手，再设计：

```sh
ffprobe -v error -select_streams a:0 \
  -show_entries stream=sample_rate,channels,codec_name:format=duration \
  -of json music.mp3
```

- 复制为 `audio/music.<ext>`，不要改原文件；在 `plan.json > audio.music` 登记 `file/source/license/duration`。
- 以它的时长/BPM/段落为时间基准；不要用新生成的音乐覆盖。
- 目标时长和音乐时长不一致时：先问“裁音乐/循环/改片长”，不要默默截断。
- 没有 BPM 就测/听/用节拍器对；卡点前先确认第一拍位置。
- 授权不明时只做内部版，不交付商用版。

## 2. 结构

- **0–2s**：给钩子；可以只有一声 impact/环境，不要慢前奏。
- **2–8s**：建立节奏；loop 进入。
- **中段**：每 8–15s 一个变化（加/减层、filter、break）。
- **高潮**：副歌/结果；加鼓/贝斯/亮度。
- **结尾**：硬收/铃/混响尾；不要突然静音（除非设计过）。

音乐驱动片先建 beat map：

```json
{"bpm":128,"beats":[0.0,0.469,...],"bars":[0.0,1.875,...],"duration":48.8}
```

所有切点/动作从 beat/bar 取；不要在代码里手写“大概 2 秒”。

## 3. 音效

### 常用家族
- **动作**：笔刷、铅笔、盖章、点击、滑动、翻页、开合。
- **转场**：whoosh、riser、reverse、glitch、scan、tape stop。
- **反馈**：chime、bell、click、success、error。
- **环境**：房间底噪、街道、人群、风、雨（低音量）。
- **冲击**：impact、sub drop、flash hit。

### 放置
- 关键动作 **同帧**；转场提前 1–3 帧（whoosh 起音）。
- 不要每个 cut 都加 whoosh；优先动作/信息变化。
- 一个动作一个主音效；不要叠 5 层。
- 音效音量：低于人声 6–12 dB，低于音乐峰值 3–6 dB；冲击可短暂高于音乐。

### cue 表

```json
{
  "cues": [
    {"at": 1.52, "kind": "impact", "gain_db": -8, "pan": 0, "actionId": "a03", "syncOffset": -0.02, "file": "audio/sfx/impact.wav"}
  ]
}
```

`at + syncOffset` 是实际出声时间；impact 常负偏移，whoosh 常正偏移。

## 4. 人声

- 录音：48kHz/24bit；房间尽量干；麦克风离嘴 15–20cm。
- 降噪：轻度；不要把呼吸/齿音全杀掉。
- EQ：高通 80–100Hz；2–5kHz +1–2dB 清晰度；低频浑浊 −2dB。
- 压缩：3:1–4:1，attack 5–10ms，release 80–150ms；目标 3–6dB 衰减。
- 去齿音：5–8kHz，动态处理。
- 响度：口播单独 −16 到 −14 LUFS；混入音乐后整体 −14（web）。

## 5. 混音

- 音乐在口播下 **−3 到 −6 dB**；可用 sidechain 或自动化。
- 音乐/音效/人声分 bus；总线上轻压缩/limiter。
- 低频：音乐 60–120Hz 与男声/爆炸冲突时，侧链或 EQ 让位。
- 立体声：人声居中；音效可左右 20–40%；音乐宽但不要相位问题。
- 手机外放检查：低频是否消失？人声是否还清楚？

## 6. 响度目标

| 场景 | Integrated | True Peak | LRA |
|---|---:|---:|---:|
| 网页/社交 | −14 LUFS | ≤ −1.0 dBTP | 5–12 |
| 展会/大屏 | −10.5 到 −12 LUFS | ≤ −1.0 dBTP | 3–8 |
| 广播 | −23 LUFS | ≤ −1.0 dBTP | 按平台 |
| 课程 | −16 到 −14 LUFS | ≤ −1.0 dBTP | 5–10 |

用 ffmpeg 测：

```sh
ffmpeg -hide_banner -nostats -i final.mp4 -filter_complex ebur128=peak=true -f null -
```

不要只看峰值；Integrated 才是观众感受到的响度。

## 7. 静音/例外

- 用户要求静音：`plan.audioExceptionReason` 记录原因；仍然要设计字幕节奏。
- 平台自动静音：首帧/字幕必须能独立成立。
- 无音乐但有人声：确保环境底噪/呼吸自然；不要“真空”。

## 8. 声音验收

- [ ] 0–2s 有声音钩子，不是慢前奏？
- [ ] 口播每个字清楚？音乐不盖人声？
- [ ] 关键动作有音效，且同帧？
- [ ] 转场有 whoosh/riser，但不滥？
- [ ] 结尾是设计过的收，不是突然断？
- [ ] Integrated/True Peak 达标？
- [ ] 手机外放听一遍？
- [ ] 静音看一遍，信息仍成立？
