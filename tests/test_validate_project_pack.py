from pathlib import Path

from PIL import Image
import pytest
import yaml

from tests.test_render_poster import make_project_pack
from scripts.validate_project_pack import validate_pack


def update_template(project: Path, **changes: object) -> None:
    template_path = project / "templates" / "long-review.yaml"
    template = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    template.update(changes)
    template_path.write_text(yaml.safe_dump(template), encoding="utf-8")


def test_valid_project_pack_has_no_errors(tmp_path: Path) -> None:
    assert validate_pack(make_project_pack(tmp_path)) == []


def test_missing_qr_asset_is_reported(tmp_path: Path) -> None:
    project = make_project_pack(tmp_path)
    (project / "assets" / "qr.jpg").unlink()

    assert "missing asset: assets/qr.jpg" in validate_pack(project)


def test_missing_template_field_is_reported(tmp_path: Path) -> None:
    project = make_project_pack(tmp_path)
    (project / "templates" / "long-review.yaml").write_text("id: long-review\n", encoding="utf-8")

    assert "template long-review missing key: canvas" in validate_pack(project)


@pytest.mark.parametrize(
    ("slot_name", "slot", "expected_error"),
    [
        ("feedback_slot", "90,360,900,960", "must be [x, y, width, height] integers"),
        ("logo_slot", [90, 90, 0, 112], "width and height must be positive"),
        ("portrait_slot", [-1, 70, 220, 265], "must be within the 1080x1920 canvas"),
        ("qr_slot", [900, 1800, 210, 210], "must be within the 1080x1920 canvas"),
    ],
)
def test_invalid_template_slot_is_reported(
    tmp_path: Path,
    slot_name: str,
    slot: object,
    expected_error: str,
) -> None:
    project = make_project_pack(tmp_path)
    update_template(project, **{slot_name: slot})

    assert f"template long-review {slot_name} {expected_error}" in validate_pack(project)


def test_missing_feedback_fit_is_reported(tmp_path: Path) -> None:
    project = make_project_pack(tmp_path)
    template_path = project / "templates" / "long-review.yaml"
    template = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    del template["feedback_fit"]
    template_path.write_text(yaml.safe_dump(template), encoding="utf-8")

    assert "template long-review missing key: feedback_fit" in validate_pack(project)


def test_unsupported_feedback_fit_is_reported(tmp_path: Path) -> None:
    project = make_project_pack(tmp_path)
    update_template(project, feedback_fit="stretch")

    assert "template long-review unsupported feedback_fit: stretch" in validate_pack(project)


def test_null_feedback_fit_is_reported(tmp_path: Path) -> None:
    project = make_project_pack(tmp_path)
    update_template(project, feedback_fit=None)

    assert "template long-review feedback_fit must be contain or top-crop" in validate_pack(project)


def test_wrong_sized_background_is_reported(tmp_path: Path) -> None:
    project = make_project_pack(tmp_path)
    Image.new("RGB", (100, 100), "white").save(project / "templates" / "background.png")

    assert "template long-review background must be 1080x1920" in validate_pack(project)


def test_undecodable_background_is_reported(tmp_path: Path) -> None:
    project = make_project_pack(tmp_path)
    (project / "templates" / "background.png").write_bytes(b"not an image")

    assert "template long-review cannot decode background: templates/background.png" in validate_pack(project)


def test_null_background_is_reported(tmp_path: Path) -> None:
    project = make_project_pack(tmp_path)
    update_template(project, background=None)

    assert "template long-review background must be a relative path string" in validate_pack(project)


def test_unsupported_portrait_background_mode_is_reported(tmp_path: Path) -> None:
    project = make_project_pack(tmp_path)
    project_file = project / "project.yaml"
    manifest = yaml.safe_load(project_file.read_text(encoding="utf-8"))
    manifest["portrait_background_mode"] = "erase-all-light-pixels"
    project_file.write_text(yaml.safe_dump(manifest), encoding="utf-8")

    assert "project unsupported portrait_background_mode: erase-all-light-pixels" in validate_pack(project)
