"""Contracts for the personal ``pessoal`` preset bundled with this fork."""

from pathlib import Path

import yaml

from specify_cli.presets import PresetManager, PresetManifest

PRESET_DIR = Path(__file__).parent.parent / "presets" / "pessoal"

COMMAND_NAMES = {
    "speckit.setup-pessoal",
    "speckit.commit",
    "speckit.openpr",
    "speckit.open-release",
    "speckit.send-release",
    "speckit.refine",
    "speckit.open-jira-issue",
}


def test_manifest_lists_personal_commands():
    manifest = PresetManifest(PRESET_DIR / "preset.yml")

    assert manifest.id == "pessoal"
    assert {entry["name"] for entry in manifest.templates} == COMMAND_NAMES
    assert {entry["type"] for entry in manifest.templates} == {"command"}


def test_command_files_exist_and_have_descriptions():
    manifest = PresetManifest(PRESET_DIR / "preset.yml")

    for entry in manifest.templates:
        path = PRESET_DIR / entry["file"]
        assert path.is_file(), f"missing command file: {entry['file']}"
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        _, frontmatter, _ = text.split("---", 2)
        assert yaml.safe_load(frontmatter)["description"]


def test_jira_and_release_commands_document_config():
    for name in (
        "speckit.setup-pessoal",
        "speckit.refine",
        "speckit.open-jira-issue",
        "speckit.open-release",
        "speckit.send-release",
    ):
        text = (PRESET_DIR / "commands" / f"{name}.md").read_text(encoding="utf-8")
        assert ".specify/pessoal.yml" in text


def test_preset_ships_pull_request_template():
    template = PRESET_DIR / "templates" / "pull_request_template.md"

    assert template.is_file()
    text = template.read_text(encoding="utf-8")
    assert "## What & why" in text
    assert "## Type of change" in text
    assert "## Checklist" in text


def test_setup_command_copies_bundled_template():
    text = (PRESET_DIR / "commands" / "speckit.setup-pessoal.md").read_text(
        encoding="utf-8"
    )

    normalized = " ".join(text.split())
    assert ".specify/presets/pessoal/templates/pull_request_template.md" in text
    assert ".github/pull_request_template.md" in text
    assert "Never overwrite without an explicit confirmation" in normalized


def test_bundled_locator_finds_preset():
    from specify_cli import _locate_bundled_preset

    assert _locate_bundled_preset("pessoal") == PRESET_DIR


def test_install_into_project(tmp_path):
    (tmp_path / ".specify" / "templates").mkdir(parents=True)

    manager = PresetManager(tmp_path)
    manager.install_from_directory(PRESET_DIR, "1.2.5")

    assert manager.registry.is_installed("pessoal")
