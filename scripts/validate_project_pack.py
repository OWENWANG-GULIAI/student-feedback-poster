"""Validate the file contract for a local student-feedback poster project pack."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image
import yaml


REQUIRED_PROJECT_KEYS = ("id", "display_name", "palette", "privacy")
REQUIRED_ASSET_KEYS = ("logo", "portrait", "qr")
REQUIRED_TEMPLATE_KEYS = (
    "id",
    "canvas",
    "background",
    "feedback_fit",
    "feedback_slot",
    "logo_slot",
    "portrait_slot",
    "qr_slot",
)
SLOT_KEYS = ("feedback_slot", "logo_slot", "portrait_slot", "qr_slot")
CANVAS_SIZE = (1080, 1920)
SUPPORTED_FEEDBACK_FITS = ("contain", "top-crop")
SUPPORTED_PORTRAIT_BACKGROUND_MODES = ("preserve", "edge-neutral-key")


def _load_yaml(path: Path, errors: list[str]) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"cannot read {path.name}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{path.name} must contain a YAML mapping")
        return {}
    return data


def _validate_slot(template_id: str, slot_name: str, slot: object, errors: list[str]) -> None:
    if not (
        isinstance(slot, list)
        and len(slot) == 4
        and all(isinstance(value, int) and not isinstance(value, bool) for value in slot)
    ):
        errors.append(f"template {template_id} {slot_name} must be [x, y, width, height] integers")
        return

    x, y, width, height = slot
    if width <= 0 or height <= 0:
        errors.append(f"template {template_id} {slot_name} width and height must be positive")
        return
    if x < 0 or y < 0 or x + width > CANVAS_SIZE[0] or y + height > CANVAS_SIZE[1]:
        errors.append(f"template {template_id} {slot_name} must be within the 1080x1920 canvas")


def validate_pack(project_dir: Path) -> list[str]:
    """Return all observable project-pack contract errors, or an empty list."""
    project_dir = Path(project_dir)
    errors: list[str] = []
    project_file = project_dir / "project.yaml"
    if not project_file.exists():
        return ["missing project.yaml"]

    project = _load_yaml(project_file, errors)
    for key in REQUIRED_PROJECT_KEYS:
        if key not in project:
            errors.append(f"project missing key: {key}")

    portrait_background_mode = project.get("portrait_background_mode", "preserve")
    if portrait_background_mode not in SUPPORTED_PORTRAIT_BACKGROUND_MODES:
        errors.append(f"project unsupported portrait_background_mode: {portrait_background_mode}")

    assets = project.get("assets")
    if assets is not None:
        if not isinstance(assets, dict):
            errors.append("project assets must be a mapping")
            assets = {}
        for key in REQUIRED_ASSET_KEYS:
            if key not in assets:
                errors.append(f"project assets missing key: {key}")
                continue
            relative_path = str(assets[key])
            if not (project_dir / relative_path).is_file():
                errors.append(f"missing asset: {relative_path}")

    templates_dir = project_dir / "templates"
    template_files = sorted(templates_dir.glob("*.yaml")) if templates_dir.is_dir() else []
    if not template_files:
        errors.append("missing template definitions")
        return errors

    for template_file in template_files:
        template = _load_yaml(template_file, errors)
        template_id = str(template.get("id", template_file.stem))
        required_template_keys = REQUIRED_TEMPLATE_KEYS
        if template.get("brand_mode", "overlay") == "embedded":
            required_template_keys = tuple(
                key for key in REQUIRED_TEMPLATE_KEYS if key not in {"logo_slot", "portrait_slot", "qr_slot"}
            )
        for key in required_template_keys:
            if key not in template:
                errors.append(f"template {template_id} missing key: {key}")

        slot_keys = ("feedback_slot",) if template.get("brand_mode", "overlay") == "embedded" else SLOT_KEYS
        for slot_name in slot_keys:
            if slot_name in template:
                _validate_slot(template_id, slot_name, template[slot_name], errors)

        if template.get("brand_mode", "overlay") not in {"overlay", "embedded"}:
            errors.append(f"template {template_id} unsupported brand_mode: {template.get('brand_mode')}")

        if "feedback_fit" in template:
            feedback_fit = template["feedback_fit"]
            if feedback_fit is None:
                errors.append(f"template {template_id} feedback_fit must be contain or top-crop")
            elif feedback_fit not in SUPPORTED_FEEDBACK_FITS:
                errors.append(f"template {template_id} unsupported feedback_fit: {feedback_fit}")

        if "background" in template:
            background = template["background"]
            if isinstance(background, str):
                background_path = templates_dir / background
                if not background_path.is_file():
                    errors.append(f"template {template_id} missing background: templates/{background}")
                else:
                    try:
                        with Image.open(background_path) as image:
                            if image.size != CANVAS_SIZE:
                                errors.append(f"template {template_id} background must be 1080x1920")
                            image.verify()
                    except (OSError, SyntaxError):
                        errors.append(f"template {template_id} cannot decode background: templates/{background}")
            else:
                errors.append(f"template {template_id} background must be a relative path string")

        if "canvas" in template and template["canvas"] != [*CANVAS_SIZE]:
            errors.append(f"template {template_id} canvas must be [1080, 1920]")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    args = parser.parse_args()
    errors = validate_pack(args.project_dir)
    if errors:
        print("INVALID PROJECT PACK")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("VALID PROJECT PACK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
