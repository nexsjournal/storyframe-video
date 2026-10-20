# 风格预设：关键词 → 视觉语法

这不是 12 套模板，而是 12 种 **视觉语法**。用户说一个关键词，先锁定“画面怎么组织、怎么动、什么不该出现”，再回到产品/主题推导方向。

## 怎么用

1. 用户说了风格关键词（如“纸感”“UI 电影”“像素”“Riso”），先在本文件找到对应预设。
2. 把预设的 **视觉规则 + 运动规则 + 不要** 写进 `DIRECTION.md`，再给 3 个不同叙事轴的方向。
3. 用户给了参考片，先按“三层拆解”拆结构/视觉/声音，再映射到最近的预设；不要照搬镜头和配色。
4. 用户没给风格，也没有参考片：从产品/主题推导，不要默认“科技蓝 + 粒子 + 六边形”。
5. 风格只决定视觉层，**不替代** 一句话承诺、证据、时间、声音和 Gate。

**关键词冲突时：** 用户明确说出的风格 > 参考片推断 > 模式默认。用户说“我要 Apple 风但要有纸张颗粒”，就取“极简产品”的留白/字号，加“纸感手作”的纸纹/层影，不要二选一。

---

## 索引

| # | 触发词 | 预设 | 一句话 | 适合 |
|---|---|---|---|---|
| 01 | `UI电影` `界面变形` `一镜到底` | UI Cinema | 真实界面在状态之间连续变形 | product / explainer |
| 02 | `动态字体` `大字` `字随声音` | Kinetic Type | 字就是画面，按节拍变形 | event / product / mv |
| 03 | `3D产品` `产品世界` `材质` | Product 3D | 一个 hero 物体，真实材质与相机 | product / event / mv |
| 04 | `编辑排版` `杂志感` `瑞士网格` | Editorial | 网格、字号对比、版面即镜头 | product / explainer / event |
| 05 | `数据仪器` `HUD` `仪表盘` | Data Instrument | 数据像仪器一样被读取 | product / explainer / course |
| 06 | `丝网印` `Riso` `双色印刷` | Risograph | 2–4 个专色、错版、纸纹 | event / explainer / mv |
| 07 | `纸感` `纸艺` `剪纸` | Paper Craft | 纸片、层影、定格 | explainer / event / product |
| 08 | `手绘` `绘本` `卡通` | Hand-drawn | 线条会呼吸，角色有表演 | explainer / course / event |
| 09 | `像素` `8-bit` `体素` | Pixel World | 16/32 网格、阶梯运动 | explainer / course / event / mv |
| 10 | `拼贴` `collage` `混合媒介` | Collage | 剪贴、胶带、错位 | mv / event / explainer |
| 11 | `复古未来` `CRT` `Y2K` | Retro Future | 扫描线、铬字、终端 | event / mv / product |
| 12 | `流程` `步骤` `recipe` | Process Explainer | 一个流程从空到满 | explainer / course / product |

---

## 01. UI 电影 / UI Cinema

**触发词：** `UI电影` `UI cinema` `界面变形` `一镜到底` `产品界面` `UI morph`

**视觉规则**
- 真实产品界面占画面 60–90%，不是“仿 UI 的装饰卡片”。
- 背景用品牌底色：暖白、近黑或低饱和品牌色；只留 1 个强调色。
- 界面外的字要少：一句标题、一个数字、一个 CTA，不要四周贴满标签。
- 允许浏览器/设备外壳，但不要用 mockup 遮住关键信息。

**运动规则**
- 一个形状/窗口 morph 成下一个状态：按钮 → loader → 播放器 → 面板。
- 相机推近 1.00→1.08，或从 UI 局部拉回全屏；运动要能解释“状态变了”。
- 光标、滚动、输入、拖拽要真实；不要随机漂浮的 UI 卡片。
- 转场优先 match cut（同一元素跨状态），少用闪白。

**适合：** product / explainer / event  
**不要：** 假数据、假界面、8 个状态挤进 15 秒、每个元素都 3D 倾斜。

**参考**
- [moritzkremb — Ramp HQ SaaS 发布](https://skillry.dev/ai-videos/opus-5-5/moritzkremb-466494) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/moritzkremb-466494.md)：真实 UI + 排版切换。
- [twoclipping — 一个形状 morph 成 8–12 个 UI 状态](https://skillry.dev/ai-videos/opus-5-5/twoclipping-402193) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/twoclipping-402193.md)：媒体播放器作为 morph 目标。
- [verbove — 暗色 UI 状态叙事](https://skillry.dev/ai-videos/opus-5-5/verbove-268381) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/verbove-268381.md)：用 8–12 个真实 UI 状态讲故事。

**实现：** 每个 UI 状态一个 DOM 层；用同一个 `border-radius`/容器做跨状态补间；截图前 `window.seek(t)` 固定状态。

---

## 02. 动态字体 / Kinetic Type

**触发词：** `动态字体` `大字` `字随声音` `kinetic type` `typographic` `字效`

**视觉规则**
- 字占画面 40–100%，允许一个字撑满全屏；字体 1 套，最多 2 套字重。
- 高对比：黑底白字、白底黑字、或品牌色底 + 反白；不要给字加投影/描边/渐变。
- 字是物体：可以被拉伸、切分、卷曲、遮挡、变成建筑/轨道/容器。
- 版面有基线/网格；即使“乱”，也要能看出对齐逻辑。

**运动规则**
- 按词/字母入场，不要整段一起淡入；每个重音一个变形。
- 运动跟人声/鼓点：重音放大、停顿留白、长音拉长。
- 允许 3D 旋转/环绕，但保证任一帧至少 3 个字可读。
- 结尾回到一个静态字标/CTA，给眼睛落地。

**适合：** event / product / mv  
**不要：** 3 种以上字体、花体字、字后面加无意义粒子、每帧都在抖。

**参考**
- [Gdgtify — VOICE WAITING 口语诗](https://skillry.dev/ai-videos/opus-5-5/gdgtify-929495) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/gdgtify-929495.md)：大字环绕、spoken-word 节奏。
- [brainextends — Spotify 主题动态图形](https://skillry.dev/ai-videos/opus-5-5/brainextends-606193) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/brainextends-606193.md)：品牌色 + 专辑视觉 + 字体。
- [techhalla — 黑白绿 typographic bumper](https://skillry.dev/ai-videos/opus-5-5/techhalla-498547) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/techhalla-498547.md)：粗字重、硬切、单色强调。

**实现：** 每个词一个绝对定位层；用 `transform` 做位移/缩放/旋转；字与节拍共用一个 `beatMap`，不要各写一套时间。

---

## 03. 3D 产品 / Product 3D

**触发词：** `3D产品` `产品世界` `材质` `3D launch` `产品渲染` `hero object`

**视觉规则**
- 一个 hero 物体占主导：产品、包装、设备、logo 实体；不要同时出现 5 个主角。
- 材质要真实：金属有环境反射、玻璃有折射、纸有纤维；粗糙度/法线别全是默认值。
- 光：一主一辅一轮廓；背景保持干净，允许渐变但不要“科技蓝紫大礼包”。
- 产品上的 UI/Logo/文字必须清晰，不能为了炫技把关键信息转没。

**运动规则**
- 相机 orbit / dolly / push-in；一个镜头只做一个主动作。
- 爆炸图、剖面、材质切换、零件归位；每个动作对应一个卖点。
- 转场用遮挡/穿过物体/景深切；不要随机 glitch。
- 结尾回到可读的产品全貌 + CTA。

**适合：** product / event / mv  
**不要：** 漂浮随机几何、假反射、过曝 bloom、镜头一直转。

**参考**
- [twoclipping — 手机与画框的 3D 产品空间](https://skillry.dev/ai-videos/opus-5-5/twoclipping-496100) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/twoclipping-496100.md)：产品作为空间锚点。
- [lukasersil — 高饱和 3D showreel](https://skillry.dev/ai-videos/opus-5-5/lukasersil-726495) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/lukasersil-726495.md)：材质/色彩/镜头密度。
- [twoclipping — 3D 网格里的产品界面](https://skillry.dev/ai-videos/opus-5-5/twoclipping-000267) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/twoclipping-000267.md)：UI 作为 3D 物件。

**实现：** Three.js 或 Blender 预渲染；固定相机路径；产品贴图用真实截图；输出前检查 logo/文字有没有被材质吃掉。

---

## 04. 编辑排版 / Editorial

**触发词：** `编辑排版` `杂志感` `瑞士网格` `editorial` `年报` `排版` `大字报`

**视觉规则**
- 12 栏网格、明显边距、严格基线；字号对比大（标题 80–160px，正文 22–32px）。
- 衬线标题 + 无衬线正文，或反过来；一套就够，不要混 4 种。
- 大量留白；用细线、页码、图注、边栏制造“编辑感”。
- 颜色克制：纸白/墨黑 + 1 个强调色；图片去背/裁切要统一。

**运动规则**
- 像翻页/排版：整块版面上移、图片裁切变化、数字滚动、下划线画出。
- 一次只动一个层级（标题/图/注），不要所有元素同时飞入。
- 转场可用硬切、遮罩擦除、纸张翻页；不要弹跳。
- 结尾让 CTA 落在网格里，而不是飘在中间。

**适合：** product / explainer / event  
**不要：** 小字过多、假报纸、每屏都是不同版式、装饰性英文。

**参考**
- [signalz_jp — “200” 极简编辑排版](https://skillry.dev/ai-videos/opus-5-5/signalz-jp-918002) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/signalz-jp-918002.md)：数字、细线、留白。
- [iamtanzil — OBLT E-bike 暗色产品头图](https://skillry.dev/ai-videos/opus-5-5/iamtanzil-120030) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/iamtanzil-120030.md)：产品 + 杂志式标题。
- [notdwd — 品牌态度海报](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/notdwd-998633.md)：剪贴字、强态度、版面冲突。

**实现：** 先画 12 栏网格；所有元素吸附到栏/基线；字号和边距写进 `DESIGN.md`，不要每屏临时调。

---

## 05. 数据仪器 / Data Instrument

**触发词：** `数据仪器` `HUD` `仪表盘` `数据可视化` `telemetry` `图表` `监控`

**视觉规则**
- 等宽字体 + 细线 + 刻度 + 网格；像仪器/终端/医疗监视器，不像 PPT 图表。
- 只展示 1 个核心指标 + 1 个辅助指标；其他数字降级为背景刻度。
- 数据必须真实、有单位、有时间范围；不要用随机数装专业。
- 颜色：深底 + 青/绿/橙单色发光，或纸白 + 墨黑 + 红。

**运动规则**
- 线从左到右画出、数字滚动、游标扫描、状态灯切换。
- 镜头推近某个异常点；用圈选/标注解释“为什么重要”。
- 不要所有图表一起长出来；按叙事顺序逐个点亮。
- 结尾把数据翻译成一句人话，不要让观众自己读图。

**适合：** product / explainer / course  
**不要：** 假精度（93.7% 却没来源）、6 个图表同屏、字号小于 18px。

**参考**
- [heyiammallik — 数据/功能清单式动效](https://skillry.dev/ai-videos/opus-5-5/heyiammallik-293397) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/heyiammallik-293397.md)：列表、数字、高亮。
- [_nikolajankovic — 手绘图表讲解](https://skillry.dev/ai-videos/opus-5-5/nikolajankovic-616097) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/nikolajankovic-616097.md)：一张图 + 注释 + 结论。
- [HenriToivar — 像素风流程/图表](https://skillry.dev/ai-videos/opus-5-5/henritoivar-445215) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/henritoivar-445215.md)：把抽象流程变成可读图示。

**实现：** 用真实 CSV/JSON 驱动数字；所有标签有单位；先写“观众要记住的 1 个结论”，再选图表。

---

## 06. 丝网印 / Risograph

**触发词：** `丝网印` `Riso` `孔版` `双色印刷` `印刷感` `halftone` `错版`

**视觉规则**
- 2–4 个专色（荧光粉、蓝、黄、黑），纸白/米色底；不要 CMYK 渐变。
- 明显的错版（套色偏移 1–4px）、半调网点、纸纹、油墨不匀。
- 形状尽量概括：大色块、剪影、粗字；细节会被网点吃掉。
- 允许“印刷事故”：边缘溢出、重影、脏点，但要控制在一个方向。

**运动规则**
- 分层套色：先黑版，再粉版，再蓝版；每层有 1–2 帧错位。
- 定格/翻页/纸张滑动；运动不要丝滑，保留机械感。
- 转场用“换纸/换版/滚墨”，不要 3D 翻转。
- 节拍可以偏慢，让纹理被看见。

**适合：** event / explainer / mv  
**不要：** 4 色以上、干净矢量、渐变、每帧都在抖。

**参考**
- [rneayan — Risograph 工作室片](https://skillry.dev/ai-videos/opus-5-5/rneayan-441493) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/rneayan-441493.md)：粉/蓝/黑套色、错版、纸感。

**实现：** 每个专色一层 Canvas/SVG；用 `mix-blend-mode: multiply`；叠加纸纹和 1–3px 随机偏移；输出前检查文字仍然可读。

---

## 07. 纸感手作 / Paper Craft

**触发词：** `纸感` `纸艺` `剪纸` `paper craft` `stop motion` `纸片`

**视觉规则**
- 纸有纤维/毛边/厚度；层与层之间有真实投影，不是平面贴图。
- 颜色来自纸张：米白、牛皮纸、低饱和专色；避免塑料高光。
- 造型概括，边缘略不齐；允许手工误差。
- 用真实纸张扫描/拍摄最好；纯代码做也要加噪点、纤维、边缘毛刺。

**运动规则**
- 12/15fps 定格感；纸片滑动、翻起、落下，阴影跟着变。
- 相机做轻微俯拍/侧移，像在拍桌面；不要无重力漂浮。
- 转场用纸张遮挡/撕开/翻页；撕纸边缘要有不规则形。
- 声音用纸张摩擦、剪刀、胶带，比电子 whoosh 更可信。

**适合：** explainer / event / product  
**不要：** 完美矢量边缘、塑料光泽、所有元素同一速度。

**参考**
- [byaiden_vu — 纸片电池/充电循环](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/byaiden-vu-755862.md)：纸片分层、手绘标注、定格感。
- [x4b47x — 纸影剧院](https://skillry.dev/ai-videos/opus-5-5/x4b47x-034026) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/x4b47x-034026.md)：剪纸剪影 + 灯光 + 舞台。

**实现：** 纸张纹理叠加 + `drop-shadow` 分层；每层独立位移；抽帧到 12/15fps；边缘用 SVG turbulence 或手绘遮罩。

---

## 08. 手绘叙事 / Hand-drawn

**触发词：** `手绘` `绘本` `卡通` `涂鸦` `hand-drawn` `水彩` `线稿`

**视觉规则**
- 线条有粗细变化和“呼吸”（line boil），不是完美矢量。
- 色彩限制在 4–6 个：水彩/水粉/蜡笔；允许溢出线外。
- 角色有表情/姿态，不是只换嘴；背景比角色低对比。
- 保留纸张/画布纹理；不要加 3D 高光。

**运动规则**
- 2s/3s（每秒 8–12 张）手绘节奏；线条轻微抖动。
- 角色先动，背景后动；用 smear/挤压/拉伸做动画原理。
- 转场用画入/擦除/翻页；不要数字 glitch。
- 旁白/对白与角色动作对齐；关键帧停在表演上。

**适合：** explainer / course / event  
**不要：** AI 塑料感、角色比例每镜变、背景比角色花。

**参考**
- [daniel_mac8 — ULTRACODE 卡通开场](https://skillry.dev/ai-videos/opus-5-5/daniel-mac8-306214) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/daniel-mac8-306214.md)：场记板、角色、手绘标题。
- [eric_khun — 中秋手绘动画](https://skillry.dev/ai-videos/opus-5-5/eric-khun-667455) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/eric-khun-667455.md)：节日、角色、暖色。
- [superalesha — 雾中刺猬式手绘短片](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/superalesha-970412.md)：氛围、颗粒、手绘质感。

**实现：** 用 SVG 手绘线条 + 每 2–3 帧轻微扰动；角色分层（身体/头/手）；背景水彩纹理；输出 12fps 再补到 30fps。

---

## 09. 像素世界 / Pixel World

**触发词：** `像素` `8-bit` `16-bit` `体素` `pixel art` `复古游戏`

**视觉规则**
- 16×16 / 32×32 网格；所有边缘对齐像素，不开抗锯齿。
- 限制调色板（8–16 色）；用 dithering 过渡，不用平滑渐变。
- 等距/俯视/横版选一个视角，不要混。
- 字体用像素字；中文要选 12/16px 点阵，避免糊。

**运动规则**
- 8/12fps 阶梯运动；移动按整像素，不要亚像素漂移。
- 角色 2–4 帧循环（走/跳/攻击）；场景视差按层移动。
- 转场用瓦片刷新/地图滚动/屏幕切换。
- 音效 8-bit 方波/噪声，和动作同帧。

**适合：** explainer / course / event / mv  
**不要：** 高清贴图、平滑光影、极小像素字、3D 景深。

**参考**
- [majidmanzarpour — 像素巫师施法](https://skillry.dev/ai-videos/opus-5-5/majidmanzarpour-927543) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/majidmanzarpour-927543.md)：像素角色、特效、夜景。
- [MozeTech — 像素游戏场景](https://skillry.dev/ai-videos/opus-5-5/mozetech-471882) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/mozetech-471882.md)：地图、UI、任务提示。

**实现：** Canvas 关闭 `imageSmoothingEnabled`；所有坐标取整；调色板写死；用 `image-rendering: pixelated`。

---

## 10. 拼贴 / Collage

**触发词：** `拼贴` `collage` `混合媒介` `剪贴` `zine` `杂志剪贴`

**视觉规则**
- 真实照片剪贴 + 纸张 + 胶带 + 手写 + 印刷字；材质要混。
- 故意错位/大小跳/边缘毛；但保留一个清晰的视觉层级。
- 颜色可以杂，但用一个主色把画面绑住。
- 所有照片/字体必须有授权；不要用未授权杂志页。

**运动规则**
- 剪贴元素逐块出现，像在桌面上贴；每块有独立节奏。
- 定格/跳切/缩放跳；不要平滑 3D 相机。
- 转场用撕纸/胶带/翻页/盖章。
- 声音用剪刀、胶带、纸张、盖章，强化手工感。

**适合：** mv / event / explainer  
**不要：** 素材堆满、没有焦点、用未授权图片、每块都在动。

**参考**
- [TomAndrieu96707 — 异想天开手绘拼贴](https://skillry.dev/ai-videos/opus-5-5/tomandrieu96707-875264) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/tomandrieu96707-875264.md)：手绘 + 剪贴 + 叙事。
- [hakimieiqbal — 海报拼贴](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/hakimieiqbal-762926.md)：人物、贴纸、手写标注。
- [anabology — 剪贴字 + 人像态度海报](https://skillry.dev/ai-videos/opus-5-5/anabology-491441) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/anabology-491441.md)：字形剪贴、强对比。

**实现：** 每个元素一张透明 PNG；随机 1–3° 旋转；用纸张纹理/胶带贴图；限制同时运动元素 ≤ 3。

---

## 11. 复古未来 / Retro Future

**触发词：** `复古未来` `CRT` `Y2K` `终端` `retro-future` `VHS` `赛博`

**视觉规则**
- 深底 + 单色霓虹（绿/青/橙/粉）；CRT 扫描线、轻微色差、 bloom。
- 铬字/玻璃/金属 + 像素/终端字；未来感来自材质，不是蓝紫渐变。
- 画面允许“旧”：VHS 噪点、时间码、追踪线、4:3 安全框。
- 信息层级要清楚；故障效果只做强调，不做背景。

**运动规则**
- 扫描线从上到下、画面 tracking 抖动、信号切换。
- 字/物体可以 glitch 1–3 帧，但下一帧必须可读。
- 相机快速 push-in / 急停；配合低频 impact。
- 转场用频道切换/信号丢失/磁带暂停。

**适合：** event / mv / product  
**不要：** 全程 glitch、字看不清、蓝紫渐变、假 UI 堆满。

**参考**
- [johnsavage_ai — OPUS 5.5 铬字发布](https://skillry.dev/ai-videos/opus-5-5/johnsavage-ai-427263) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/johnsavage-ai-427263.md)：暗底、铬字、CRT 光晕。
- [notdwd — 品牌态度/剪贴字](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/notdwd-998633.md)：强字重、版面冲突、复古印刷。
- [techhalla — 黑白绿字效 bumper](https://skillry.dev/ai-videos/opus-5-5/techhalla-498547) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/techhalla-498547.md)：单色、硬切、终端感。

**实现：** 后处理加 scanlines/色差/噪点；glitch 用位移切片，控制在 1–3 帧；字幕层不参与 glitch。

---

## 12. 流程讲解 / Process Explainer

**触发词：** `流程` `步骤` `recipe` `how it works` `讲解` `从零到一`

**视觉规则**
- 一个连续流程：空杯 → 加料 → 完成；或 0 → 1 → 2 → 3。
- 输入/工具/结果都可见；标签跟随对象，不要另开一屏 bullet。
- 用同一空间/同一视角，让观众看到“累积”。
- 颜色编码步骤，但不超过 4 种；数字/箭头只做必要提示。

**运动规则**
- 物体沿路径移动，镜头跟随；每一步只加一个元素。
- 用“倒入/放入/点击/连接”等真实动作，不用抽象粒子。
- 关键步骤停 0.5–1 秒，让观众看清状态。
- 结尾展示完成态 + 一句总结，不要突然切 CTA。

**适合：** explainer / course / product  
**不要：** 7 条 bullet、假流程图、没有完成态、步骤跳太快。

**参考**
- [Ror_Fly — 鸡尾酒配方流程](https://skillry.dev/ai-videos/opus-5-5/ror-fly-880547) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/ror-fly-880547.md)：空杯到完成，原料/计量可见。
- [sudo_kiran — 绿色能源流程讲解](https://skillry.dev/ai-videos/opus-5-5/sudo-kiran-335993) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/sudo-kiran-335993.md)：图解 + 口播 + 能量流。
- [HenriToivar — 像素风流程/图表](https://skillry.dev/ai-videos/opus-5-5/henritoivar-445215) · [Prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/henritoivar-445215.md)：步骤、图标、递进状态。

**实现：** 先画“开始态/结束态”两张图；中间状态用同一坐标系补间；标签锚定物体；每个步骤一个时间窗。

---

## 风格修饰词

风格预设决定“语法”，修饰词只调“语气”。可以叠加 1–2 个，不要超过 3 个。

| 修饰词 | 触发 | 具体做什么 | 不要做什么 |
|---|---|---|---|
| `极简` | `极简` `白底` `Apple风` | 去掉 50–70% 元素；暖白/墨黑 + 1 强调色；字号加大；运动变慢 | 变成空镜头；信息不足 |
| `暗色` | `暗色` `发布会` `科技感` | 近黑底、单光束、铬/玻璃、产品局部高光 | 蓝紫渐变 + 粒子雨 |
| `高饱和` | `高饱和` `多巴胺` `Y2K` | 3–4 个高饱和专色；大面积色块；硬边 | 颜色超过 5 个；刺眼 |
| `单色` | `单色` `monochrome` `黑白` | 一个色相 + 纸/墨；靠明度/字号/构图 | 全灰、没有焦点 |
| `胶片` | `胶片` `颗粒` `16mm` | 颗粒、halation、轻微 gate weave、暖高光 | 颗粒盖住字幕 |
| `快节奏` | `快节奏` `卡点` `高能` | 0.5–1.5s 切；beat map 驱动；impact 同帧 | 全程 0.2s 闪切；没有呼吸 |

---

## 参考片怎么拆（拿到链接时）

1. **结构层**：时长、镜头数、平均镜头长度、信息释放顺序、转场频率。
2. **视觉层**：主/辅/强调色、字体、构图、材质、运动、纹理。
3. **声音层**：音乐类型/BPM/能量曲线、音效位置、人声处理。

拆完写一句：“我借它的 **结构/语法**，不借它的 **画面**。”然后映射到最近的预设，再加一个只属于这个产品的 motif。

---

## 参考与授权

本文件的参考片索引、Prompt 链接来自 [awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos)（MIT）。缩略图、视频、Prompt 版权归各创作者；本仓库只做索引和链接，不复制视频文件。商用前请按原作品/素材的许可逐项确认。
