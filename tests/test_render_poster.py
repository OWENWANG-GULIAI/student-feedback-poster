from pathlib import Path

import yaml
import pytest
from PIL import Image

from scripts.render_poster import _blur_rectangles, prepare_portrait, render
from scripts.select_template import select_template


def make_project_pack(root: Path) -> Path:
    project = root / "project"
    assets = project / "assets"
    templates = project / "templates"
    assets.mkdir(parents=True)
    templates.mkdir()

    Image.new("RGBA", (300, 120), "#d6a21e").save(assets / "logo.png")
    Image.new("RGB", (300, 400), "#c9a07a").save(assets / "portrait.png")
    Image.new("RGB", (300, 300), "white").save(assets / "qr.jpg")
    Image.new("RGB", (1080, 1920), "#f7f2e8").save(templates / "background.png")
    (project / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "test-project",
                "display_name": "测试项目",
                "palette": {"gold": "#D4A126", "charcoal": "#161616", "ivory": "#F7F2E8"},
                "privacy": {"default": "redact-student-identifiers"},
                "cta_text": "扫码了解课程详情",
                "assets": {"logo": "assets/logo.png", "portrait": "assets/portrait.png", "qr": "assets/qr.jpg"},
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    (templates / "long-review.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "long-review",
                "canvas": [1080, 1920],
                "background": "background.png",
                "feedback_fit": "top-crop",
                "feedback_slot": [90, 360, 900, 960],
                "logo_slot": [90, 90, 280, 112],
                "portrait_slot": [770, 70, 220, 265],
                "qr_slot": [765, 1660, 210, 210],
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return project


def test_render_requires_declared_redactions_for_public_output(tmp_path: Path) -> None:
    project = make_project_pack(tmp_path)
    feedback = tmp_path / "feedback.png"
    Image.new("RGB", (600, 1200), "#eeeeee").save(feedback)

    with pytest.raises(ValueError, match="redaction"):
        render(project, "long-review", feedback, [], tmp_path / "poster.png")


@pytest.mark.parametrize(
    "redaction",
    [
        [-1, 0, 20, 20],
        [0, -1, 20, 20],
        [590, 0, 20, 20],
        [0, 1190, 20, 20],
        [700, 1400, 20, 20],
    ],
)
def test_render_rejects_redactions_outside_feedback_bounds(tmp_path: Path, redaction: list[int]) -> None:
    project = make_project_pack(tmp_path)
    feedback = tmp_path / "feedback.png"
    Image.new("RGB", (600, 1200), "#eeeeee").save(feedback)

    with pytest.raises(ValueError, match="within feedback image bounds"):
        render(project, "long-review", feedback, [redaction], tmp_path / "poster.png")


def test_render_rejects_non_integer_redaction_coordinates(tmp_path: Path) -> None:
    project = make_project_pack(tmp_path)
    feedback = tmp_path / "feedback.png"
    Image.new("RGB", (600, 1200), "#eeeeee").save(feedback)

    with pytest.raises(ValueError, match="redaction coordinates must be integers"):
        render(project, "long-review", feedback, [[-0.5, 0, 20, 20]], tmp_path / "poster.png")


def test_blur_rectangles_fully_covers_every_declared_pixel() -> None:
    source = Image.new("RGBA", (80, 60), (255, 0, 0, 0))
    redactions = [[5, 7, 20, 18], [40, 12, 24, 30]]

    redacted = _blur_rectangles(source, redactions)

    for x, y, width, height in redactions:
        for pixel_y in range(y, y + height):
            for pixel_x in range(x, x + width):
                assert redacted.getpixel((pixel_x, pixel_y))[3] == 255


def test_render_outputs_fixed_portrait_png_and_obscures_declared_area(tmp_path: Path) -> None:
    project = make_project_pack(tmp_path)
    feedback = tmp_path / "feedback.png"
    source = Image.new("RGB", (600, 1200), "#eeeeee")
    source.paste("#f00000", (0, 0, 120, 120))
    source.save(feedback)
    output = tmp_path / "poster.png"

    result = render(project, "long-review", feedback, [[0, 0, 120, 120]], output)

    assert result == output
    assert Image.open(output).size == (1080, 1920)
    assert Image.open(output).getpixel((100, 370)) != (240, 0, 0)


def test_long_review_uses_top_crop_so_long_text_stays_readable(tmp_path: Path) -> None:
    project = make_project_pack(tmp_path)
    feedback = tmp_path / "long-feedback.png"
    source = Image.new("RGB", (600, 2400), "#2040C0")
    source.paste("#F00000", (0, 0, 600, 400))
    source.save(feedback)
    output = tmp_path / "poster.png"

    render(project, "long-review", feedback, [[500, 2200, 50, 50]], output)

    red, green, blue = Image.open(output).getpixel((150, 460))
    assert red > 200 and green < 30 and blue < 30


def test_edge_neutral_key_removes_only_edge_connected_checkerboard() -> None:
    portrait = Image.new("RGB", (5, 5), "#F2F2F2")
    for coordinate in ((1, 1), (2, 1), (3, 1), (1, 2), (3, 2), (1, 3), (2, 3), (3, 3)):
        portrait.putpixel(coordinate, (80, 50, 35))
    portrait.putpixel((2, 2), (242, 242, 242))

    cleaned = prepare_portrait(portrait, "edge-neutral-key")

    assert cleaned.getpixel((0, 0))[3] == 0
    assert cleaned.getpixel((2, 2))[3] == 255
    assert cleaned.getpixel((1, 1))[3] == 255


def test_default_portrait_mode_preserves_source_pixels() -> None:
    portrait = Image.new("RGB", (1, 1), "#F2F2F2")

    assert prepare_portrait(portrait, "preserve").getpixel((0, 0))[3] == 255


def test_render_embedded_brand_template_without_local_contact_assets(tmp_path: Path) -> None:
    project = tmp_path / "project"
    templates = project / "templates"
    templates.mkdir(parents=True)
    Image.new("RGB", (1080, 1920), "#801010").save(templates / "background.png")
    (project / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "test-project",
                "display_name": "测试项目",
                "palette": {"gold": "#D4A126"},
                "privacy": {"default": "redact-student-identifiers"},
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    (templates / "embedded.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "embedded",
                "label": "内嵌品牌模板",
                "canvas": [1080, 1920],
                "background": "background.png",
                "feedback_fit": "contain",
                "feedback_slot": [200, 400, 680, 1100],
                "brand_mode": "embedded",
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    feedback = tmp_path / "feedback.png"
    Image.new("RGB", (600, 900), "#efefef").save(feedback)

    output = tmp_path / "poster.png"
    render(project, "embedded", feedback, [[0, 0, 30, 30]], output)

    assert Image.open(output).size == (1080, 1920)
    assert Image.open(output).getpixel((50, 50)) == (128, 16, 16)


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("这是学员成交后晒单，刚签约并完成回款", "deal-report"),
        ("三天课程复盘，感谢老师，收获很多", "review-tide"),
        ("欢迎新伙伴加入讲师团，好消息", "daily-good-news"),
    ],
)
def test_template_selection_routes_by_feedback_content(content: str, expected: str) -> None:
    templates = [
        {"id": "deal-report", "route_keywords": ["成交", "签约", "回款"]},
        {"id": "review-tide", "route_keywords": ["复盘", "感谢", "收获"]},
        {"id": "daily-good-news", "route_keywords": ["欢迎", "加入", "好消息"]},
    ]

    assert select_template(templates, content=content) == expected


def test_template_selection_honors_explicit_template_choice() -> None:
    templates = [
        {"id": "deal-report", "route_keywords": ["成交"]},
        {"id": "review-tide", "route_keywords": ["好评"]},
    ]

    assert select_template(templates, content="成交喜报", requested_template="review-tide") == "review-tide"
