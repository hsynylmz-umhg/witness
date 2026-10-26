"""Fresh checkouts may omit all private operator material without weakening hashes."""

import importlib.util
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
spec = importlib.util.spec_from_file_location(
    "workspace_validator", ROOT / "scripts/validate_workspace.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def test_fresh_checkout_without_private_material_passes_once(tmp_path, capsys):
    for name in ("src", "tests", "scripts", "config", "docs"):
        shutil.copytree(ROOT / name, tmp_path / name, ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", "README.md", "pyproject.toml", "uv.lock"):
        shutil.copy2(ROOT / name, tmp_path / name)
    assert not (tmp_path / "context").exists()
    assert validator.validate_root(tmp_path) == 0
    lines = capsys.readouterr().out.splitlines()
    expected = "private context not present in this checkout; skipping 6 recorded hashes"
    assert lines.count(expected) == 1


def test_present_private_hash_mismatch_still_fails(tmp_path):
    for name in ("src", "tests", "scripts", "config", "docs"):
        shutil.copytree(ROOT / name, tmp_path / name, ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", "README.md", "pyproject.toml", "uv.lock"):
        shutil.copy2(ROOT / name, tmp_path / name)
    archive = tmp_path / "context" / "archive" / "initial-scaffold"
    archive.mkdir(parents=True)
    (archive / "AGENTS.md.txt").write_text("SYNTHETIC_CHANGED_REFERENCE", encoding="utf-8")
    with pytest.raises(ValueError, match="bytes changed"):
        validator.validate_root(tmp_path)
