"""Fresh checkouts may omit all private operator material without weakening hashes."""

import importlib
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


def test_all_project_modules_and_scripts_import_without_errors():
    source_root = ROOT / "src"
    module_paths = sorted((source_root / "witness").rglob("*.py"))
    script_paths = sorted((ROOT / "scripts").glob("*.py"))
    for path in module_paths + script_paths:
        relative = path.relative_to(source_root if path.is_relative_to(source_root) else ROOT)
        parts = list(relative.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        module_name = ".".join(parts)
        importlib.import_module(module_name)


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
