"""Validate authored workspace files without reading secrets or local environments."""

import ast
import hashlib
import json
import re
import tomllib
from pathlib import Path


def validate_root(root: Path) -> int:
    required = (
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        "README.md",
        "pyproject.toml",
        "uv.lock",
        "docs/STATUS.md",
        "docs/RULES.md",
        "docs/TOOLING.md",
        "docs/ENVIRONMENT.md",
        "docs/DATA_CONTRACTS.md",
        "docs/API_VERIFICATION.md",
        "docs/inventory/baseline.json",
    )
    for name in required:
        if not (root / name).is_file():
            raise ValueError(f"Missing required workspace file: {name}")
    for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
        text = (root / name).read_text(encoding="utf-8")
        if "docs/RULES.md" not in text or len(text) > 1024:
            raise ValueError(f"Tool entry must remain a thin shared-rule reference: {name}")
    python_paths = [
        path for folder in ("src", "tests", "scripts") for path in (root / folder).rglob("*.py")
    ]
    for path in python_paths:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for path in (root / "pyproject.toml", root / "uv.lock", root / "config/defaults.toml"):
        with path.open("rb") as stream:
            tomllib.load(stream)
    markdown = list(root.glob("*.md")) + list((root / "docs").rglob("*.md"))
    for path in markdown:
        text = path.read_text(encoding="utf-8")
        if re.search(r"\bcontext[\\/]", text, flags=re.IGNORECASE):
            raise ValueError(f"Private path reference in published documentation: {path.name}")
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"`[^`\n]*`", "", text)
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if ":" in target or target.startswith("#"):
                continue
            relative = target.split("#", maxsplit=1)[0]
            if not (path.parent / relative).exists():
                raise ValueError(f"Broken authored Markdown link in {path.name}: {target}")
    baseline = json.loads((root / "docs/inventory/baseline.json").read_text(encoding="utf-8"))
    hashes = {entry["path"]: entry["sha256"] for entry in baseline["files"]}
    private_root = root / "context"
    originals = [
        entry
        for entry in baseline["files"]
        if Path(entry["path"]).parts[0] == private_root.name
        and Path(entry["path"]).name.startswith("WITNESS-")
    ]
    preserved = [(root / entry["path"], entry["sha256"]) for entry in originals]
    archive = private_root / "archive" / "initial-scaffold"
    for archived, original in (
        ("AGENTS.md.txt", "AGENTS.md"),
        ("START_PROMPT.md.txt", "START_PROMPT.md"),
        ("validate_scaffold.py.txt", "scripts/validate_scaffold.py"),
        ("defaults.toml.txt", "config/defaults.toml"),
        ("STATUS.md.txt", "docs/STATUS.md"),
    ):
        preserved.append((archive / archived, hashes[original]))
    missing = 0
    for path, expected in preserved:
        if not path.is_file():
            missing += 1
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("Preserved private reference/archive bytes changed.")
    if missing:
        print(f"private context not present in this checkout; skipping {missing} recorded hashes")
    print(f"PASS: {len(python_paths)} Python files, TOML, authored links and thin tool entries")
    print(f"PASS: {len(preserved) - missing} available private reference/archive hashes verified")
    print("NOT RUN: instruction loading in other apps, model API, real hardware media, performance")
    return 0


def main() -> int:
    return validate_root(Path(__file__).resolve().parents[1])


if __name__ == "__main__":
    raise SystemExit(main())
