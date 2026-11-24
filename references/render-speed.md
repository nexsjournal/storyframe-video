# 渲染速度：时间花在哪、怎么把时间拿回来

这份文件回答两个问题：**为什么以前慢**、**现在每一步花多久**。所有数字都是本机实测（Apple M4 Pro / 14 核 / Chrome headless / ffmpeg 7.1 / 1920×1080），不是估算。

> **这些数字是参考值，不是门槛。** 换机器、换 harness、换渲染器都会变；看趋势比看绝对值重要：单帧成本 × 帧数 ÷ 并行度。判断标准是"比上一版快没快"，以及"是不是卡在下面五条里的一条"。

---

## 1. 一句话结论

一条 60 秒 1080p30 的代码驱动片子，**采集 + 编码 ≈ 20 秒**，加配乐合成与首帧确认，**全流程 2–3 分钟**。如果慢到 10 分钟以上，原因只可能是下面五条之一，不会是"机器不行"。

---

## 2. 时间花在哪：五个旋钮

总时间 ≈ **帧数 × 单帧成本 + 编码 + 启动开销**

| 旋钮 | 影响 | 默认值 | 怎么调 |
|---|---|---|---|
| 帧数 | 线性 | 时长 × fps | 预览 24fps；终版 30fps；不要 60fps 除非有高速运动 |
| 分辨率 | 像素成本，**平方级** | 预览 640 短边；终版 1920×1080 | 预览一定 640；1080p 只在终版出现一次 |
| 场景光栅成本 | 单帧成本主项 | 见第 3 节 | 去掉 `backdrop-filter`、大半径 `blur`、多层 `box-shadow` |
| 采集路径 | 每帧 9–95 ms | canvas `draw(t)` | DOM 场景用 CDP 直采 + 关 vsync |
| 编码器 | 终渲 1–3 s/12s | `h264_videotoolbox`（macOS） | Linux 用 `libx264 -preset veryfast` |

---

## 3. 实测对照表（12 秒 / 360 帧 / 1080p30）

| 场景类型 | 采集方式 | 每帧 | 360 帧总耗时 | 备注 |
|---|---|---:|---:|---|
| 轻 DOM（字卡、三屏） | v1：`screenshot`→磁盘，每帧等 2 次 rAF | **63 ms** | 22.7 s | 旧默认 |
| 轻 DOM | v2：CDP 直采 + `--deterministic-mode` + 0 次 rAF | **14 ms** | 5.0 s | 4.5× |
| DOM + 毛玻璃（140 张 `backdrop-filter` 卡） | v1 | **94 ms** | 33.8 s | 光栅是瓶颈 |
| DOM + 毛玻璃 | v2 | **81 ms** | 29.2 s | 只快 1.16×：优化救不了重光栅 |
| Canvas `draw(t)`（本 skill 默认） | v2：页内 `toDataURL` 出 JPEG，pipe 进 ffmpeg | **9.2 ms** | **3.4 s** | 6.9×，且不随 DOM 数量变慢 |
| 预览 640×360 / 24fps（Canvas） | v2 | **2.5–4.2 ms** | 0.8–1.3 s | 12 秒片预览 1 秒内出 |

旧流程还有一个隐藏成本：渲完再跑 `contact_sheet.py` 扫成片抽帧（解码 + 拼图，几秒到几十秒），以及每改一次就整片重渲。v2 把 QA 抽帧合并进渲染循环（`--beat-sheet 1` = 每拍一张），**零额外成本**。

---

## 4. 旧流程为什么慢：四个具体原因

1. **每帧等两次 rAF。** `seek(t)` 是同步纯函数，`requestAnimationFrame` 等的是下一帧合成，等于每帧白送 16.7 ms（两次 33 ms）。实测 settle=0 与 settle=2 输出像素完全一致（hash 相同）。
2. **截图被 vsync 节拍卡住。** 默认 headless 的 `Page.captureScreenshot` 会被拖到 60 Hz 节拍，单帧下限 16.7 ms。加 `--deterministic-mode --disable-gpu-vsync --disable-frame-rate-limit --run-all-compositor-stages-before-draw` 后降到 ~13 ms，且保持确定性。
3. **每帧写一次磁盘。** 1800 个 JPEG 写盘再让 ffmpeg 读回来，多一轮 I/O。v2 直接把帧 buffer 写进 ffmpeg stdin（`-f image2pipe -c:v mjpeg`）。
4. **用 DOM + 重滤镜做画面。** `backdrop-filter: blur(18px)` 叠 140 层，单帧光栅 80 ms 以上，任何采集技巧都救不回来。

---

## 5. 现在的时间预算（照着执行）

| 片长 | 配乐合成 | 预览 640/24 | 终版 1080p/30 | 全流程目标 |
|---:|---:|---:|---:|---:|
| 15 s | 1.5 s | 1 s | 5 s | **< 45 s** |
| 30 s | 2 s | 2 s | 10 s | **< 90 s** |
| 60 s | 3 s | 4 s | 20 s | **< 3 min** |
| 180 s | 6 s | 10 s | 55 s | **< 6 min** |

超预算时按这个顺序查：① 是不是在 1080p 上迭代 → 改 640；② 场景有没有 `backdrop-filter`/大 blur → 删；③ 是不是 DOM 场景 → 换 canvas `draw(t)`；④ 是不是每改一版都全片重渲 → 改分段。

---

## 6. 三条硬规则

**规则 1：一版只渲一次。**
预览和终版在同一条命令里跑完（`node make.mjs --final`），不要"先渲预览看看、再渲终版看看、再渲一次对比"。

**规则 2：改哪段渲哪段。**

```sh
# 只重渲 12–20 秒这一段
node render.mjs --from 12 --to 20 --output parts/p3.mp4 --audio audio/music.wav

# 拼回整片（不重编视频，只重挂音轨）
node render.mjs --concat parts --audio audio/music.wav --output videos/final.mp4
```

**规则 3：抽帧只抽一次，抽在拍上。**
`--beat-sheet 1` 在渲染时顺手存下每拍一帧（480 宽），一张 6×4 联系表就能看完整片节奏；不要渲完再对成片跑一遍抽帧脚本，也不要抽 1080p 原尺寸帧。

---

## 7. 采集路径怎么选

| 你的画面 | 用什么 | 为什么 |
|---|---|---|
| 图形、字、图表、界面示意、数据动画 | **Canvas `draw(t)`**（默认） | 每帧 9 ms，页内 JPEG 编码，不经过合成器 |
| 真实网页/真实产品 UI（必须是 DOM） | DOM + CDP 直采 | 每帧 14 ms；别加毛玻璃和大 blur |
| 真实录屏、实拍素材 | ffmpeg 剪辑，不逐帧渲染 | 直接 `-c:v copy` 拼接 |

判断方法：页面暴露 `window.__CAPTURE__ = 'canvas'` 就走 canvas 快路，否则走 DOM。`render.mjs` 自动检测，也可以用 `--capture dom|canvas` 强制。

---

## 8. 自检：这条片子该花多久

```sh
# 渲 3 秒样本，看每帧成本，再乘回去
node render.mjs --from 0 --to 3 --output /tmp/probe.mp4
```

日志里 `xx.x ms/帧` 就是单帧成本：

- **< 15 ms** → 健康，60 秒片 20 秒内完成
- **15–40 ms** → 可接受，检查场景有没有多余滤镜
- **> 40 ms** → 先修场景，不要靠调编码器
