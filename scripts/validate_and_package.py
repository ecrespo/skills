#!/usr/bin/env python3
"""validate_and_package.py — Validate Agent Skills and package them for distribution.

Validation (per skill folder under skills/):
  - SKILL.md exists and starts with YAML frontmatter
  - frontmatter contains only `name` and `description`
  - `name` matches the folder name, is lowercase letters/digits/hyphens, <= 64 chars
  - `description` is non-empty and <= 1024 chars
  - no Spanish/accented characters remain in any text file
  - every relative path mentioned in SKILL.md (references/, scripts/, assets/) exists

Packaging:
  - zips each valid skill into dist/<name>.skill (a zip with the skill folder at
    the root, as expected by Claude Desktop / claude.ai skill upload)

Pure stdlib, read-only except for dist/.

Usage:
  python3 scripts/validate_and_package.py [--repo PATH] [--no-package]
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SPANISH_RE = re.compile(r"[áéíóúñÁÉÍÓÚÑ¿¡]")
REL_PATH_RE = re.compile(r"(?:references|scripts|assets)/[A-Za-z0-9._/\-]+")
TEXT_EXT = {".md", ".py", ".yaml", ".yml", ".txt", ".json"}


def parse_frontmatter(text: str) -> tuple[dict, list[str]]:
    errors: list[str] = []
    if not text.startswith("---"):
        return {}, ["SKILL.md does not start with YAML frontmatter"]
    end = text.find("\n---", 3)
    if end == -1:
        return {}, ["frontmatter is not closed with ---"]
    block = text[3:end]
    fields: dict[str, str] = {}
    current = None
    for line in block.splitlines():
        if not line.strip():
            continue
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m and not line.startswith((" ", "\t")):
            current = m.group(1)
            fields[current] = m.group(2).strip().lstrip(">|").strip()
        elif current:
            fields[current] += (" " if fields[current] else "") + line.strip()
    return fields, errors


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return ["missing SKILL.md"]
    text = skill_md.read_text(encoding="utf-8")
    fields, fm_errors = parse_frontmatter(text)
    errors += fm_errors

    extra = set(fields) - {"name", "description"}
    if extra:
        errors.append(f"frontmatter has extra keys: {sorted(extra)}")
    name = fields.get("name", "")
    if name != skill_dir.name:
        errors.append(f"frontmatter name {name!r} != folder name {skill_dir.name!r}")
    if not NAME_RE.match(name or ""):
        errors.append(f"name {name!r} is not lowercase-hyphen format")
    if len(name) > 64:
        errors.append("name exceeds 64 characters")
    desc = fields.get("description", "")
    if not desc:
        errors.append("description is empty")
    if len(desc) > 1024:
        errors.append(f"description is {len(desc)} chars (max 1024)")

    # Leftover Spanish in any text file
    for f in sorted(skill_dir.rglob("*")):
        if f.is_file() and f.suffix in TEXT_EXT:
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if SPANISH_RE.search(line):
                    errors.append(f"Spanish characters in {f.relative_to(skill_dir)}:{i}")

    # Bundled paths referenced from SKILL.md must exist
    for ref in sorted(set(REL_PATH_RE.findall(text))):
        ref = ref.rstrip("/.")
        if not (skill_dir / ref).exists():
            errors.append(f"SKILL.md references missing file: {ref}")
    return errors


def package_skill(skill_dir: Path, dist: Path) -> Path:
    dist.mkdir(parents=True, exist_ok=True)
    out = dist / f"{skill_dir.name}.skill"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(skill_dir.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts:
                zf.write(f, f"{skill_dir.name}/{f.relative_to(skill_dir)}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--no-package", action="store_true", help="validate only")
    args = ap.parse_args()

    repo = Path(args.repo)
    skills_root = repo / "skills"
    if not skills_root.is_dir():
        print(f"ERROR: {skills_root} not found", file=sys.stderr)
        return 2

    failed = False
    for skill_dir in sorted(p for p in skills_root.iterdir() if p.is_dir()):
        errors = validate_skill(skill_dir)
        if errors:
            failed = True
            print(f"FAIL {skill_dir.name}")
            for e in errors:
                print(f"     - {e}")
            continue
        line = f"OK   {skill_dir.name}"
        if not args.no_package:
            out = package_skill(skill_dir, repo / "dist")
            line += f"  -> {out.relative_to(repo)}"
        print(line)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
