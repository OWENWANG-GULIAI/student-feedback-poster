# 项目资料包

项目资料包是可持续增加的内容层；新增项目不需要改动 `SKILL.md` 的业务规则。

```text
assets/projects/<project-id>/
├── project.yaml
└── templates/
    ├── <template-id>.yaml
    └── <template-id>-background.png
```

## 项目建档

先收集：公开项目名与可识别别名、模板原图、允许公开的品牌色和使用授权。不要把任何学员聊天截图、个人手机号、内部名单或未授权头像写入资料包。

每个内嵌品牌模板必须定义 `canvas`、背景文件、截图槽位、`brand_mode: embedded` 和内容路由关键词。布局槽位使用 `[x, y, width, height]`，以 1080×1920 画布左上角为原点。

创建或更新后运行：

```bash
UV_CACHE_DIR=/private/tmp/student-feedback-poster-uv uv run --with pyyaml --with pillow python scripts/validate_project_pack.py assets/projects/<project-id>
```

只有显示 `VALID PROJECT PACK` 才可用于正式出图。

## 新背景模板

内嵌品牌模板需为 1080×1920，保留用户已授权的 Logo、人物与固定文案，且预留清晰的截图区域。模板原图不可被图像生成工具重绘；更新后保存为静态 PNG。

项目资料包含真实二维码、联系方式或学员证据时，只能保留在本地目录。发布 Skill 或上传公开仓库前必须移除。
