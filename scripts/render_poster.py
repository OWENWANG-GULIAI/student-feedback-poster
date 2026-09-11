"""Render local, redacted student-feedback posters from a fixed project pack."""

from __future__ import annotations

import argparse
from collections import deque
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
import yaml


CANVAS_SIZE = (1080, 1920)
GOLD = "#D4A126"
CHARCOAL = "#161616"
IVORY = "#F7F2E8"


def _load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def _find_template(project_dir: Path, template_id: str) -> tuple[dict, Path]:
    for path in (project_dir / "templates").glob("*.yaml"):
        template = _load_yaml(path)
        if template.get("id") == template_id:
            return template, path
    raise ValueError(f"unknown template: {template_id}")


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size, index=0)
        except OSError:
            continue
    return ImageFont.load_default()


def _paste_fit(
    canvas: Image.Image,
    source: Image.Image,
    slot: list[int],
    background: str = "white",
    fit_mode: str = "contain",
) -> None:
    x, y, width, height = slot
    panel = Image.new("RGBA", (width, height), background)
    if fit_mode == "top-crop":
        contained = ImageOps.fit(
            source.convert("RGBA"),
            (width, height),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.0),
        )
    elif fit_mode == "contain":
        contained = ImageOps.contain(source.convert("RGBA"), (width, height), Image.Resampling.LANCZOS)
    else:
        raise ValueError(f"unsupported feedback fit mode: {fit_mode}")
    offset = ((width - contained.width) // 2, (height - contained.height) // 2)
    panel.alpha_composite(contained, offset)
    canvas.alpha_composite(panel, (x, y))


def _blur_rectangles(image: Image.Image, redactions: list[list[int]]) -> Image.Image:
    redacted = image.convert("RGBA").copy()
    draw = ImageDraw.Draw(redacted)
    for rectangle in redactions:
        if len(rectangle) != 4:
            raise ValueError("each redaction must contain [x, y, width, height]")
        if not all(isinstance(value, int) and not isinstance(value, bool) for value in rectangle):
            raise ValueError("redaction coordinates must be integers")
        x, y, width, height = rectangle
        if width <= 0 or height <= 0:
            raise ValueError("redaction width and height must be positive")
        if x < 0 or y < 0 or x + width > redacted.width or y + height > redacted.height:
            raise ValueError("each redaction must be fully within feedback image bounds")
        draw.rectangle((x, y, x + width - 1, y + height - 1), fill="#4B4B4B")
        for offset in range(8, width, 16):
            draw.line((x + offset, y, x + offset, y + height - 1), fill="#6A6A6A", width=5)
    return redacted


def prepare_portrait(image: Image.Image, background_mode: str = "preserve") -> Image.Image:
    """Apply an explicitly chosen, conservative portrait background treatment."""
    portrait = image.convert("RGBA")
    if background_mode == "preserve":
        return portrait
    if background_mode != "edge-neutral-key":
        raise ValueError(f"unsupported portrait background mode: {background_mode}")

    width, height = portrait.size
    pixels = portrait.load()
    visited = bytearray(width * height)
    transparent = bytearray(width * height)

    def is_light_neutral(x: int, y: int) -> bool:
        red, green, blue, alpha = pixels[x, y]
        return alpha > 0 and min(red, green, blue) >= 225 and max(red, green, blue) - min(red, green, blue) <= 18

    queue: deque[tuple[int, int]] = deque()
    for x in range(width):
        queue.extend(((x, 0), (x, height - 1)))
    for y in range(1, height - 1):
        queue.extend(((0, y), (width - 1, y)))

    while queue:
        x, y = queue.popleft()
        index = y * width + x
        if visited[index]:
            continue
        visited[index] = 1
        if not is_light_neutral(x, y):
            continue
        transparent[index] = 1
        for delta_y in (-1, 0, 1):
            for delta_x in (-1, 0, 1):
                next_x, next_y = x + delta_x, y + delta_y
                if 0 <= next_x < width and 0 <= next_y < height:
                    queue.append((next_x, next_y))

    for y in range(height):
        for x in range(width):
            if transparent[y * width + x]:
                red, green, blue, _ = pixels[x, y]
                pixels[x, y] = (red, green, blue, 0)
    return portrait


def _draw_fixed_copy(canvas: Image.Image, project: dict, template_id: str) -> None:
    draw = ImageDraw.Draw(canvas)
    display_name = str(project["display_name"])
    eyebrow = "学员真实反馈" if template_id == "long-review" else "一条真实学员反馈"
    draw.text((90, 210), eyebrow, font=_font(32), fill="#F7F2E8")
    draw.text((90, 258), display_name, font=_font(60, bold=True), fill="white")
    cta = str(project["cta_text"])
    cta_bbox = draw.textbbox((0, 0), cta, font=_font(28))
    draw.text((750 + (230 - (cta_bbox[2] - cta_bbox[0])) // 2, 1885), cta, font=_font(28), fill="#5A4A28")


def render(
    project_dir: Path,
    template_id: str,
    feedback_path: Path,
    redactions: list[list[int]],
    output_path: Path,
) -> Path:
    """Compose an auditable public poster; caller must declare privacy redactions."""
    if not redactions:
        raise ValueError("public output requires at least one redaction")
    project_dir = Path(project_dir)
    feedback_path = Path(feedback_path)
    output_path = Path(output_path)
    project = _load_yaml(project_dir / "project.yaml")
    template, template_file = _find_template(project_dir, template_id)
    if template.get("canvas") != [*CANVAS_SIZE]:
        raise ValueError("template canvas must be [1080, 1920]")

    templates_dir = template_file.parent
    background = Image.open(templates_dir / template["background"]).convert("RGBA")
    if background.size != CANVAS_SIZE:
        raise ValueError("template background must be 1080x1920")
    feedback = _blur_rectangles(Image.open(feedback_path), redactions)
    _paste_fit(
        background,
        feedback,
        list(template["feedback_slot"]),
        fit_mode=str(template.get("feedback_fit", "contain")),
    )

    if template.get("brand_mode", "overlay") == "overlay":
        assets = project["assets"]
        logo = Image.open(project_dir / assets["logo"]).convert("RGBA")
        portrait = prepare_portrait(
            Image.open(project_dir / assets["portrait"]),
            str(project.get("portrait_background_mode", "preserve")),
        )
        qr = Image.open(project_dir / assets["qr"]).convert("RGBA")
        _paste_fit(background, logo, list(template["logo_slot"]), background=(0, 0, 0, 0))
        _paste_fit(background, portrait, list(template["portrait_slot"]), background=(0, 0, 0, 0))
        _paste_fit(background, qr, list(template["qr_slot"]), background="white")
        _draw_fixed_copy(background, project, template_id)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    background.convert("RGB").save(output_path, format="PNG", optimize=True)
    return output_path


def _background_base(template_id: str) -> Image.Image:
    image = Image.new("RGBA", CANVAS_SIZE, IVORY)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1080, 360), fill=CHARCOAL)
    draw.rectangle((0, 340, 1080, 360), fill=GOLD)
    draw.rounded_rectangle((65, 65, 430, 200), radius=24, fill=IVORY)
    if template_id == "long-review":
        draw.rounded_rectangle((65, 375, 1015, 1415), radius=38, fill="white", outline="#E7DAC0", width=4)
        draw.rounded_rectangle((735, 1630, 1015, 1910), radius=28, fill="white")
    else:
        draw.rounded_rectangle((65, 375, 1015, 1355), radius=38, fill="white", outline="#E7DAC0", width=4)
        draw.rectangle((0, 1480, 1080, 1920), fill=CHARCOAL)
        draw.rounded_rectangle((735, 1630, 1015, 1910), radius=28, fill="white")
    return image


def generate_backgrounds(project_dir: Path) -> list[Path]:
    """Write the two first-project text-free background templates."""
    templates = Path(project_dir) / "templates"
    templates.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for template_id in ("long-review", "highlight"):
        output = templates / f"{template_id}-background.png"
        _background_base(template_id).convert("RGB").save(output, format="PNG", optimize=True)
        outputs.append(output)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--generate-backgrounds", action="store_true")
    parser.add_argument("--template")
    parser.add_argument("--feedback", type=Path)
    parser.add_argument("--redactions", help="JSON list of [x, y, width, height] rectangles")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.generate_backgrounds:
        for path in generate_backgrounds(args.project):
            print(path)
        return 0
    if not all((args.template, args.feedback, args.redactions, args.out)):
        parser.error("rendering needs --template, --feedback, --redactions and --out")
    redactions = json.loads(args.redactions)
    if not isinstance(redactions, list):
        parser.error("--redactions must be a JSON list")
    print(render(args.project, args.template, args.feedback, redactions, args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
