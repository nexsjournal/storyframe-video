# [TITLE] — 视频工程

## 成片

- `videos/final.mp4`
- `videos/final.srt`
- `videos/cover.png`

## 规格

- 画幅：
- 时长：
- fps：
- 编码：H.264 + AAC
- 响度：

## 复现

> 本工程默认只有文档 / plan / 空目录。需要代码驱动渲染时，把 skill 的 `starter/` 复制进来，再执行下面命令。

```sh
# 0. 仅当使用 starter/
npm install

# 1. 预览/静帧
node still.mjs 1.0 3.0

# 2. 渲染
node render.mjs --from 0 --to <duration> --fps <fps> --audio audio/master.wav --output videos/final.mp4

# 3. 检查（需要 ffmpeg + python3 + pillow/numpy）
python3 <skill-dir>/scripts/check_delivery.py plan.json --video videos/final.mp4 \
  --mix-report audio/mix_report.json --captions videos/final.srt
```

## 素材来源 / 授权

用户提供的文案、音乐、截图等已复制进 `assets/copy/`、`audio/`；原始文件未被修改。
机器可读的交接记录见 `SOURCES.json`（如果初始化时带了 `--script/--music`）。

| 素材 | 来源 | 许可 | 备注 |
|---|---|---|---|
| 文案 | | | |
| 音乐 | | | |
| 截图/录屏 | | | |
| Logo/字体 | | | |

## 结构

- `BRIEF.md`：目标/受众/约束/证据
- `DIRECTION.md`：方向/视觉规范/镜头表
- `SCRIPT.md`：逐句脚本
- `STORYBOARD.md`：分镜
- `plan.json`：机器可读时间线
- `src/`：代码驱动工程
- `audio/`：音乐/音效/混音
- `renders/`：联系表/关键帧
- `QA.md`：验收

## 已知限制

- 
