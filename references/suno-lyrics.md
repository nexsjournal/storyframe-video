# Suno 歌词制作

Suno 不是“时长旋钮”。BPM、歌词长度、段落数、编曲密度共同决定成品长度；**先排小节，再排字**。

## 1. 先定 5 个输入

1. 用途：产品曲 / 活动曲 / 知识/课程主题曲 / MV。
2. 目标时长：15s / 30s / 50–58s / 90s。
3. BPM / 拍号：例如 124 BPM, 4/4；轻快电子流行常用 118–128。
4. 语言/人声：普通话/粤语/英文；自然、年轻、女声/男声/不锁。
5. 必须出现：产品名、卖点、日期、城市、展位、URL。

## 2. 时间预算

```text
1 小节秒数 = 60 / BPM * 每小节拍数
总时长 = 总小节数 * 1 小节秒数
```

124 BPM, 4/4：1 小节 = **1.935s**；27 小节 ≈ **52.3s**（落在 50–58s）。

| 段落 | 小节 | 时间（124 BPM） | 行数 | 每行汉字 |
|---|---:|---:|---:|---:|
| Intro | 1 | 0:00.0–0:01.9 | 1 | 4 |
| Verse | 8 | 0:01.9–0:17.4 | 8 | 6–10 |
| Chorus | 8 | 0:17.4–0:32.9 | 4 | 8–9 |
| Bridge | 4 | 0:32.9–0:40.6 | 4 | 6–8 |
| Final Chorus | 4 | 0:40.6–0:48.4 | 2 | 8 |
| Outro | 2 | 0:48.4–0:52.3 | 2 | ≤12 + 数字 |

**总汉字**：唱词 120–160；加口播 ≤180。超过就删，不加速。

> Suno 不保证精确小节数；27 小节是预算，成品以 50–58s 为准。27 小节 @124 BPM = 52.26s。
> 想更接近 55s：给 Chorus 或 Outro 加 1 小节（28 bars ≈54.2s），不要加速。

## 3. 歌词结构

### Hook 公式
`产品名（4 字） + 好处（4 字）`，8 字，可唱、可记。

例：`绘声绘色，画就会唱`。  
不要：`绘声绘色，画着回响`——氛围有了，但“产品能做什么”不清楚。

### Verse
- 一行一个动作/机制：`动作 + 结果`。
- 6–10 字/行；不要堆形容词/成语。
- 前 4 行给输入/操作，后 4 行给结果/惊喜。

例：
```text
拿起笔，选颜色
让灵感慢慢苏醒了
横着走，时间流动
画高一点，音符跃动
```

### Chorus
- 4 行，每行 8–9 字；两句一组对仗。
- 第 1 句必须出现产品名 + 好处；第 2 句给画面/结果。
- 不要在副歌堆功能；只重复一个钩子。

### Bridge
- 4 行，6–8 字；短句、口语、拟声词；配器变薄。
- 写“怎么玩”，不要上价值。

### Final Chorus
- 2 行，8 字；只重复一次，换一个结果/愿景，不要整段复制。

### Outro
- 2 行，口播：日期 + 城市 + 展位 + 一句邀请。
- 最后短铃/硬收；不要长淡出。

## 4. 段标签（表演指令）

```text
[Intro - Quick, Spoken]
[Verse - Light, Bouncy]
[Chorus - Catchy, Melodic]
[Bridge - Playful, Rhythmic]
[Final Chorus - Bright, Short]
[Outro - Spoken, Quick]
[End - Short Bell, Clean Stop]
```

标签里的形容词是给 Suno 的“怎么唱”，不是装饰。唱得太喊，把 `Bouncy` 改成 `Soft, Conversational`。

## 5. Style of Music

必须覆盖：genre / BPM / meter / duration / instruments / vocal / mood / arrangement / negatives / mix。

模板：

```text
[Genre], [BPM] BPM, [meter], [bars], target [duration]. [Instrumentation]. [Mood / image]. [Vocal type/language], [phrasing], [hook]. [Arrangement: intro/verse/chorus/bridge/outro/ending]. [Sound-design accents]. [Production polish]. No [negatives]. Tight arrangement, clean hard stop under [limit].
```

轻快创意电子流行示例：

```text
Playful, light and sophisticated indie electro-pop, 124 BPM, 4/4, 27 bars, target 50-58 seconds. Bright plucked piano, delicate music-box bells, warm marimba, soft synths, subtle funky bass and crisp, bouncy electronic drums. Colorful, whimsical, creative and uplifting, like a hand-drawn melody coming to life. Natural youthful Mandarin vocals, warm and expressive, smooth melodic phrasing, catchy singable chorus, gentle rhythmic bounce. Quick spoken intro, immediate vocal entry, compact verses, memorable melodic hook, short playful bridge, concise spoken outro, clean bell stop. Tasteful sound-design accents like tiny chimes, marker strokes and scanning sparkles. Modern, polished, charming and energetic but never aggressive. Mandarin-only lead vocal. No rap, no shout-chant, no heavy EDM drop, no long instrumental intro or outro, no vocal chops, no aggressive distortion. Tight arrangement, brisk transitions, clean hard stop under one minute.
```

## 6. Exclude Styles

如果界面有该栏：

```text
rap, shout-chant, gang vocals, heavy EDM, big-room drop, aggressive bass, distorted vocals, vocal chops, chipmunk vocals, long instrumental intro, long fade-out, stadium anthem
```

## 7. Suno 设置

| 项目 | 设置 |
|---|---|
| 模式 | Custom |
| 目标时长 | 50–58s（27 小节 @124 BPM ≈52.3s） |
| BPM | 124 |
| 拍号 | 4/4 |
| 人声 | 自然、年轻、有笑意的普通话；不锁性别 |
| 开头 | 口播“三、二、一，画！”，1 小节内进入 |
| 结尾 | 口播日期/展位 + 短铃，最后一拍硬收 |
| 风格倾向 | 自然旋律优先，不追求高 weirdness |

## 8. 生成后验收

- [ ] 0–2s 出现口播，没有长前奏。
- [ ] 第一次副歌在目标时间出现，Hook 吐字清楚。
- [ ] 人声是唱，不是喊；没有口号式重复。
- [ ] 时长 50–58s；>60s 不加速，先删 Bridge 后两句/重复副歌。
- [ ] 结尾有日期/展位口播，最后一拍短铃/硬收。
- [ ] 听完能记住 Hook，而不是只记住产品名被喊了很多次。

## 9. 超时/太赶的修改顺序

1. **>60s**：删 Bridge 的“画下来，听一听 / 让你的创意被听见”，再删 Final Chorus 重复；不要提速。
2. **<50s**：重复一次 Final Chorus（2 句），或加 2 小节木琴/铃声尾奏；不要加长前奏。
3. **像喊麦**：段标签改 `[Verse - Soft, Conversational]`；Style 降“energetic”，加“breathy, intimate, restrained”。
4. **字太密**：删 10 字行里的修饰词；保持一行一个动作。
5. **产品名不清楚**：Hook 放副歌第一句；减少同段信息；不要靠重复喊补救。

## 10. 字符预算工具

用 `scripts/lyric_budget.py`：

```sh
python3 <skill-dir>/scripts/lyric_budget.py lyrics.md --bpm 124 --bars 27 --hook "绘声绘色，画就会唱"
```

它会输出每段/每行汉字数、总时长、字/秒、超长行和 Hook 检查。先跑工具，再生成。

## 11. 一条硬规则

**删词，不加速。** Suno 把词唱快了，灵动就变成赶场；宁可少两句，也不要让副歌变成绕口令。
