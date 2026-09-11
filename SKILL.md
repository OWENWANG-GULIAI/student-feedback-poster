---
name: student-feedback-poster
description: Use when a course owner wants to turn real student-feedback screenshots into branded, privacy-protected posters for WeChat Moments or groups, or wants to add a course/project template pack for that workflow.
metadata:
  author: 王跃平 OWENWANG
  version: "1.1.0"
---

# 学员反馈晒圈海报

将真实反馈作为证据，而不是用 AI 伪造聊天内容。日常出图使用项目资料包中的固定品牌模板；截图内容决定模板，用户指定模板时优先遵从。

## 先判断任务

| 用户意图 | 操作 |
|---|---|
| 上传反馈截图，要求出海报 | 进入“日常出图” |
| 要为课程、讲师班或项目建立模板 | 进入“项目建档” |
| 想改固定文案、版式或模板内容 | 更新对应项目资料包后重新验证 |

**REQUIRED REFERENCE:** 日常出图前读取 [隐私与证据](references/privacy-and-evidence.md)、[日常生产](references/production.md) 和 [质量门](references/quality-gates.md)。新增或更新项目资料包时，读取 [项目资料包](references/project-packs.md)。

## 日常出图

1. 确认项目。用户明确说项目名时优先使用；未说明时列出现有项目并请用户选择，不擅自套用其他项目的品牌元素。
2. 检查截图是否可读、是否包含学生昵称、头像、手机号、微信号、地址或其他身份线索。默认遮挡；用户明确批准公开某项时才保留。
3. 先看用户提示与截图正文，再路由模板：成交/签约/回款/交付用 `deal-report`；课程复盘、学习体验、感谢与推荐用 `review-tide`；欢迎加入、班级动态和阶段喜讯用 `daily-good-news`。用户明确指定模板时照做；无法判断时说明候选并让用户选。
4. 使用模板原图做确定性合成。当前三套模板已经内嵌 Logo、讲师形象和固定文案；不得重新绘制或额外叠加这些元素，也不得重绘聊天截图。
5. 运行项目包校验和渲染命令；交付前按质量门核对尺寸、遮挡、证据可读性与截图窗口对齐。
6. 交付 PNG，并说明项目、模板、已遮挡项目和需要用户人工确认的事项。不得自动发送到朋友圈或社群。

## AI 图像生成边界

图像生成只可用于**项目建档阶段**的抽象背景、纹理或装饰尝试，且新背景必须无文字、无 Logo、无二维码、无人像、无聊天截图。选定后保存为项目包固定资源；日常海报不得随机生图。

## 首个项目与公开边界

`assets/projects/ai-authorized-instructor-class/` 是“AI授权讲师班”项目资料包。它允许将截图中的“AIGC企业应用实战讲师授权班”作为同一项目的原始证据保留。

该资料包的三张已授权品牌模板为：`daily-good-news`（今日份开心）、`deal-report`（成交喜报）、`review-tide`（好评如潮）。公开版本不包含学员聊天截图、已生成海报、个人微信二维码或其他联系信息。

## 非目标

- 不凭空补课程价格、开课时间、成果承诺或学生身份。
- 不将原始学生截图放入项目包、示例或公开压缩包。
- 不宣称已经自动识别、自动打码或完成外部平台发布，除非本次确有对应证据。
