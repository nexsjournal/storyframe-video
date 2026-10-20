# 画幅与交付

## 1. 画幅

| 比例 | 分辨率 | 用途 | 安全区 |
|---|---|---|---|
| 16:9 | 1920×1080 / 3840×2160 | 官网、YouTube、B 站、课程 | 四周 5%；字幕底 10% |
| 9:16 | 1080×1920 | 抖音、Reels、Shorts、视频号 | 上 12%、下 18% |
| 1:1 | 1080×1080 | 信息流、Instagram | 四周 8% |
| 4:5 | 1080×1350 | 小红书、Instagram feed | 四周 8% |
| 3:4 | 1200×1600 | 海报/封面 | 四周 8% |

默认先做 **16:9 母版**，再重排 9:16；不要直接裁。

## 2. 平台时长

- **TikTok/Reels/Shorts**：15–34s 最稳；超过 60s 完播率下降。
- **视频号**：15–60s；前 3s 决定跳出。
- **B 站/YouTube**：60–180s 可承载讲解；前 5s 仍要钩子。
- **官网 hero**：15–30s 循环；首帧要完整。
- **展会大屏**：15–30s 循环；字号大、对比强、少字。
- **课程**：3–10 分钟为主；单条 demo 60–180s。

## 3. 编码

### 母版
```sh
ffmpeg -y -i master.mov \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -profile:v high \
  -c:a aac -b:a 320k -ar 48000 -ac 2 \
  -movflags +faststart final.mp4
```

### 社交压缩
- H.264 High，CRF 18–20；1080p 码率 8–12 Mbps。
- AAC 192–256 kbps；48kHz。
- `+faststart`；`-pix_fmt yuv420p` 兼容性最好。
- 竖屏确保 `-vf scale=1080:1920` 不拉伸；用 `force_original_aspect_ratio=decrease,pad`。

### 帧率
- 30fps 基线；60fps 用于高速运动/游戏/UI 滚动。
- 不要混帧率；源 25/50 先转 25/50 或 30，不要 29.97 混 30。

## 4. 封面

- 单独导出 16:9 / 9:16 / 1:1；不要把视频第一帧直接裁。
- 要素：主体/产品 + 一句 6–12 字标题 + 品牌/日期（如需）。
- 首帧本身要能当缩略图；封面是加强版，不是补救。
- 文字在手机大小可读；不要超过 2 个层级。
- 导出 PNG/JPG，<2MB；平台要求另存。

## 5. 字幕

- 烧录版 + `.srt` 双份。
- SRT 编码 UTF-8；时间 `00:00:01,000 --> 00:00:03,000`。
- 中文 12–16 字/行，最多 2 行；英文 38–42 字符/行。
- 每条 1.5–4s；不要跨语义。
- 专有名词统一；数字用阿拉伯数字还是汉字要统一。
- 烧录字幕位置避开平台 UI；9:16 放底部 18% 以上。

## 6. 文件命名

```
<project>_<mode>_<duration>_<aspect>_<lang>_v<version>.mp4
例：drawmusic_product_48s_16x9_zh_v3.mp4
```

封面：`cover_16x9.png` / `cover_9x16.png`。  
字幕：`final_zh.srt` / `final_en.srt`。

## 7. 交付包

```
videos/
  final.mp4
  final.srt
  cover_16x9.png
  cover_9x16.png（如需）
README.md
QA.md
BRIEF.md
DIRECTION.md
SCRIPT.md
STORYBOARD.md
plan.json
audio/
  mix_report.json
  sfx_cues.json
src/（代码驱动）
renders/（联系表/关键帧）
```

README 写：

- 复现命令（依赖、渲染、混音）。
- 素材来源/授权。
- 导出参数。
- 已知限制。

## 8. 平台上传检查

- [ ] 画幅/时长/大小符合平台。
- [ ] 首帧/封面可读。
- [ ] 字幕没有被 UI 挡。
- [ ] 声音响度正常（平台会再压，但不要差太多）。
- [ ] 二维码可扫（如果平台压缩后）。
- [ ] 结尾 CTA 停留 ≥3s。
- [ ] 没有黑边/拉伸/错帧。
- [ ] 文件名/元数据不含敏感信息。

## 9. 版本管理

- 每次大改升版本号；保留 `v1/v2/v3` 成片与 `plan.json`。
- 不在最终文件上直接覆盖；先导出 `vN`，验收后改名 `final`。
- 交付时给 SHA-256（可选但推荐）。
