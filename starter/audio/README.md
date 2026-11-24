# audio/

`beats.json` 是画面时间的唯一来源（BPM、拍点、小节、段落能量）。

配乐本身不提交到仓库，用一条命令生成（六种预设，3 秒出 60 秒曲子）：

```sh
python3 <skill-dir>/scripts/make_music.py --preset uplift --duration <片长> \
  --out audio/music.wav --grid audio/beats.json
```

用用户自己的歌时不要覆盖 `beats.json`：`node make.mjs --duration 45 --audio ./music.mp3 --skip-music`，
脚本会按给定 BPM（或 120 兜底）建网格，画面照样有拍点可用。
