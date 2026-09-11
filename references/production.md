# 日常生产

## 模板路由

| 条件 | 模板 |
|---|---|
| 成交、签约、回款、复购、客户交付或订单推进 | `deal-report` |
| 课程复盘、学习体验、感谢、推荐或文字密集好评 | `review-tide` |
| 欢迎加入、班级动态、开营/结营、阶段喜讯或轻量庆祝 | `daily-good-news` |
| 用户明确指定模板 | 指定模板 |

用户提示优先于关键词；关键词只用于辅助判断截图语义。不要因为“感谢老师”就将普通课程好评误判为成交，也不要把有收入承诺的模糊表述改写为成交事实。

长截图不要缩小整张来换取“全量展示”。`review-tide` 顶部裁切以保持文字可读；若需要展示多段内容，拆成多张海报并逐张处理隐私。

## 渲染

先校验项目包，再执行渲染。下面命令中的遮挡坐标只是格式示例，必须按本次截图重新核对：

```bash
UV_CACHE_DIR="${TMPDIR:-/tmp}/student-feedback-poster-uv" uv run --with pillow --with pyyaml \
  python scripts/render_poster.py \
  --project assets/projects/ai-authorized-instructor-class \
  --template review-tide \
  --feedback /absolute/path/to/feedback.png \
  --redactions '[[35,210,95,95],[145,225,180,54]]' \
  --out work/ai-authorized-instructor-class/poster.png
```

脚本不接受空遮挡列表。若截图本身已脱敏，仍应提供最小的、真实存在的遮挡区域，或在本次任务中由用户明确批准“截图已完整脱敏，可不做遮挡”后再修改流程记录；不要绕过默认保护。

## 输出说明

交付时写明：项目名、模板名、遮挡的项目，以及是否为长图顶部裁切。不得把“脚本成功写出 PNG”说成已完成外部平台发布。
