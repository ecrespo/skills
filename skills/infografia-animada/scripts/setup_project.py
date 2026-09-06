#!/usr/bin/env python3
"""setup_project.py - Scaffold a Remotion project ready for animated infographics.

Creates a blank Remotion project, removes the Tailwind wiring the blank template still
ships (the --no-tailwind flag does not strip it), installs the packages this skill needs
(@remotion/google-fonts, @remotion/paths, simple-icons) and copies the bundled templates
into src/<module>/.

Requires Node.js 18+ with npx on PATH. Pure stdlib; it only writes inside the new project
folder.

Usage:
  python3 scripts/setup_project.py --parent ~/videos --name my-infographic
  python3 scripts/setup_project.py --parent . --name promo --module infografia --dry-run
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATES = ("useAppear.ts", "FlowLine.tsx", "Icon.tsx", "palette.ts")
EXTRA_PACKAGES = ("@remotion/google-fonts", "@remotion/paths")


def run(cmd: list[str], cwd: Path, dry_run: bool) -> None:
    print(f"$ {' '.join(cmd)}  (cwd={cwd})")
    if dry_run:
        return
    subprocess.run(cmd, cwd=str(cwd), check=True)


def strip_tailwind(project: Path, dry_run: bool) -> None:
    """Drop Tailwind lines from remotion.config.ts and index.css.

    The blank template wires Tailwind in even with --no-tailwind, which adds a build step
    and a stylesheet no infographic uses.
    """
    for rel in ("remotion.config.ts", "src/index.css"):
        f = project / rel
        if not f.is_file():
            continue
        lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
        kept = [ln for ln in lines if "tailwind" not in ln.lower()]
        if len(kept) == len(lines):
            continue
        print(f"  stripping Tailwind from {rel} ({len(lines) - len(kept)} lines)")
        if not dry_run:
            f.write_text("".join(kept), encoding="utf-8")


def copy_templates(skill_dir: Path, project: Path, module: str, dry_run: bool) -> None:
    src = skill_dir / "assets" / "templates"
    dest = project / "src" / module
    print(f"  copying templates -> {dest}")
    if dry_run:
        return
    dest.mkdir(parents=True, exist_ok=True)
    for name in TEMPLATES:
        target = dest / name
        if target.exists():
            print(f"    skip {name} (already present)")
            continue
        shutil.copy2(src / name, target)
        print(f"    + {name}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--parent", required=True, help="folder that will contain the project")
    ap.add_argument("--name", required=True, help="project folder name")
    ap.add_argument("--module", default="infografia", help="src subfolder for the templates")
    ap.add_argument(
        "--skill-dir",
        default=str(Path(__file__).resolve().parent.parent),
        help="path to this skill (defaults to the parent of scripts/)",
    )
    ap.add_argument("--dry-run", action="store_true", help="print the steps without running them")
    args = ap.parse_args()

    parent = Path(args.parent).expanduser().resolve()
    project = parent / args.name
    skill_dir = Path(args.skill_dir).expanduser().resolve()

    if not (skill_dir / "assets" / "templates").is_dir():
        print(f"ERROR: templates not found under {skill_dir}", file=sys.stderr)
        return 2
    if not args.dry_run and not shutil.which("npx"):
        print("ERROR: npx not found on PATH (Node.js 18+ required)", file=sys.stderr)
        return 2
    if not args.dry_run:
        parent.mkdir(parents=True, exist_ok=True)

    if project.is_dir():
        print(f"Project {project} already exists; installing dependencies only.")
    else:
        run(["npx", "-y", "create-video@latest", "--yes", "--blank", "--no-tailwind", args.name],
            parent, args.dry_run)

    run(["npm", "install", "--no-fund", "--no-audit"], project, args.dry_run)
    run(["npx", "remotion", "add", *EXTRA_PACKAGES], project, args.dry_run)
    run(["npm", "install", "--save-exact", "--no-fund", "--no-audit", "simple-icons"],
        project, args.dry_run)

    strip_tailwind(project, args.dry_run)
    copy_templates(skill_dir, project, args.module, args.dry_run)
    if not args.dry_run:
        (project / "out").mkdir(exist_ok=True)

    print(f"\nReady: {project}")
    print(f"  templates in src/{args.module}/, renders go to out/")
    print("  next: write the pattern components, then render a still to verify")
    return 0


if __name__ == "__main__":
    sys.exit(main())
