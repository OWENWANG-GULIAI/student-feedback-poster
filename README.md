<p align="center">
  <img src="assets/brand/guliai-logo.png" alt="GULIAI" width="360">
</p>

# 学员反馈晒圈海报

> 将真实学员反馈截图合成为可发朋友圈或社群的品牌海报；按截图语义匹配模板，并默认保护学员身份信息。

![Version](https://img.shields.io/badge/version-1.1.0-blue) ![Language](https://img.shields.io/badge/language-Python-3776AB) ![License](https://img.shields.io/badge/license-MIT-green)

> **定位**：面向课程主理人，用真实、可追溯的学员反馈做信任背书。
>
> **不做什么**：不伪造聊天记录，不自动发朋友圈，不把普通好评夸大为成交，也不公开学员原始截图。

## 为什么需要它

真实反馈的可信度来自原始证据，而不是把聊天内容重新写成营销文案。这个 Skill 将截图放入固定品牌版式，同时把“课程好评”“成交推进”和“班级喜讯”区分开来，避免用错叙事。

## 快速开始

安装为本地 Codex Skill：

```bash
git clone https://github.com/OWENWANG-GULIAI/student-feedback-poster.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/student-feedback-poster"
```

在新会话中使用 `$student-feedback-poster`，上传反馈截图并说明项目或想强调的内容。Skill 会先检查隐私，再依据内容选择模板；也可以明确指定“成交喜报”“好评如潮”或“今日份开心”。

本地校验项目资料包：

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills/student-feedback-poster"
UV_CACHE_DIR="${TMPDIR:-/tmp}/student-feedback-poster-uv" uv run --with pillow --with pyyaml \
  python scripts/validate_project_pack.py assets/projects/ai-authorized-instructor-class
```

## 使用方法

用自然语言说明目标即可，例如“这是学员课程复盘，做一张海报”或“这张突出签约回款，使用成交喜报”。用户指定的模板名称优先于自动匹配。

## 核心能力

- 固定品牌模板与确定性截图合成
- 基于提示和截图语义的模板建议
- 来源截图坐标级隐私遮挡
- 1080×1920 朋友圈/社群竖版输出

## 适用场景

| 模板 | 适用证据 | 典型提示 |
|---|---|---|
| `deal-report`｜成交喜报 | 成交、签约、回款、复购、客户交付、订单推进 | “这张突出学员成交” |
| `review-tide`｜好评如潮 | 课程复盘、学习体验、感谢、推荐、文字密集好评 | “做一张学员学习反馈海报” |
| `daily-good-news`｜今日份开心 | 欢迎加入、开营结营、获奖、班级动态、阶段喜讯 | “新伙伴加入，做张喜讯海报” |

用户明确指定模板时优先；没有指定时，以截图正文和用户提示中的证据语义匹配。遇到“感谢”与“成交”等混合信息时，不臆测，先询问或交付候选建议。

## 工作流程

1. 读取截图与用户提示，确认项目、证据语义和隐私项。
2. 遮挡昵称、头像、联系方式、地址及其他可识别身份信息；用户单次明确授权后才可保留。
3. 将真实截图确定性嵌入已选模板的证据窗口，不重绘 Logo、讲师形象、模板文字或聊天内容。
4. 输出 1080×1920 PNG，并检查裁切、文字可读性和遮挡范围。

## 示例

```text
使用 AI授权讲师班。这张截图是学员三天课程复盘，请默认遮挡头像和昵称。
```

预期：选择“好评如潮”模板，保留复盘正文的可读部分，并交付一张 1080×1920 PNG。

## 输入与输出

输入为项目名（或已配置的项目）、一张真实反馈截图、可选的模板偏好与需要遮挡的区域。输出为一张脱敏后的 PNG 海报，以及所用模板和裁切/遮挡说明。

## 当前项目资料包

首个公开资料包是“AI授权讲师班”。三张模板已内嵌 GULIAI 品牌元素与固定文案，因此公开包中不含个人微信二维码、可复用的联系方式、学员聊天截图或已生成的反馈海报。

## 仓库结构

```text
├── SKILL.md                         # Skill 入口与路由规则
├── assets/projects/.../templates/   # 三张品牌模板及配置
├── scripts/                         # 渲染、模板选择与项目包校验
├── references/                      # 隐私、生产与质量规则
├── tests/                           # 可重复运行的行为测试
└── evals/                           # 人工验收场景
```

## 隐私与授权

- 学员反馈只能作为当次输入，不得复制进公开仓库、示例或演示资源。
- 默认遮挡昵称、头像、手机号、微信号、地址和其他身份线索。
- 模板中的品牌资产仅用于已授权的品牌海报场景；不要将其与其他课程或品牌混用。

详见 [隐私与证据](references/privacy-and-evidence.md)。

## 当前边界

- 不自动识别所有头像、昵称或联系方式的位置；遮挡位置必须经人工检查。
- 不验证二维码、不自动发布到朋友圈或社群。
- 不从模糊好评推断成交、收入或课程成果。

## 参与贡献

欢迎通过 Issue 或 Pull Request 提交可公开复用的模板配置、测试或文档改进。请勿提交学员截图、客户聊天、二维码、联系方式或其他可识别个人信息。

## 许可证

本仓库以 [MIT License](LICENSE) 发布。
