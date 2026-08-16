#!/usr/bin/env python3
"""Check architectural import boundaries in a Python package using only the stdlib (ast).

Usage:
    python check_boundaries.py <package_dir> --rules boundaries.json
    python check_boundaries.py --init hexagonal|layered|modular|clean|doma > boundaries.json

Rules file (JSON). Three kinds, mirroring import-linter contracts:

  {"kind": "layers", "root": "pkg", "layers": ["infrastructure", "interface_adapters", "application", "domain"]}
      Higher layers (earlier in the list) may import lower ones; never the reverse.

  {"kind": "independence", "root": "pkg", "modules": ["policies", "payments"], "shared": ["pkg.shared"]}
      Listed modules must not import each other (shared packages are always allowed).

  {"kind": "forbidden", "root": "pkg", "rules": [{"source": "pkg.core", "forbidden": ["pkg.adapters", "fastapi"]}]}
      Source subtree must not import any of the forbidden module prefixes.

A rules file may also be {"rules_sets": [ ...several of the above... ]}.
Exit code 1 if violations exist. Output: one line per violation `file:line  source -> target  (rule)`.
"""
from __future__ import annotations
import argparse, ast, json, sys
from pathlib import Path

INIT = {
    "hexagonal": {"kind": "forbidden", "root": "PKG", "rules": [{"source": "PKG.core", "forbidden": ["PKG.adapters", "PKG.main", "fastapi", "pymongo", "sqlalchemy", "reflex", "httpx"]}]},
    "layered": {"kind": "layers", "root": "PKG", "layers": ["main", "services", "repositories", "domain"]},
    "modular": {"kind": "independence", "root": "PKG", "modules": ["policies", "payments", "beneficiaries"], "shared": ["PKG.shared"]},
    "clean": {"kind": "layers", "root": "PKG", "layers": ["infrastructure", "interface_adapters", "application", "domain"]},
    "doma": {"kind": "layers", "root": "PKG.domains", "layers": ["edge", "presentation", "product", "business", "infrastructure"]},
}


def module_name(path: Path, base: Path, root_pkg: str) -> str:
    rel = path.relative_to(base).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join([root_pkg] + parts) if parts else root_pkg


def imports_of(path: Path, this_mod: str) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out.append((node.lineno, a.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import → resolve against this module
                base = this_mod.split(".")
                base = base[: len(base) - node.level + (0 if path.name != "__init__.py" else 1)]
                mod = ".".join(base + ([node.module] if node.module else []))
            else:
                mod = node.module or ""
            for a in node.names:
                out.append((node.lineno, f"{mod}.{a.name}" if mod else a.name))
                out.append((node.lineno, mod))
    return [(ln, m) for ln, m in out if m]


def starts(mod: str, prefix: str) -> bool:
    return mod == prefix or mod.startswith(prefix + ".")


def layer_index(mod: str, root: str, layers: list[str]) -> int | None:
    for i, l in enumerate(layers):
        if starts(mod, f"{root}.{l}"):
            return i
    return None


def check(rule: dict, files: list[tuple[Path, str, list[tuple[int, str]]]]) -> list[str]:
    v = []
    kind, root = rule["kind"], rule["root"]
    if kind == "layers":
        layers = rule["layers"]
        for path, mod, imps in files:
            li = layer_index(mod, root, layers)
            if li is None:
                continue
            for ln, target in imps:
                ti = layer_index(target, root, layers)
                if ti is not None and ti < li:
                    v.append(f"{path}:{ln}  {mod} -> {target}  (layers: {layers[li]} must not import {layers[ti]})")
    elif kind == "independence":
        mods, shared = rule["modules"], rule.get("shared", [])
        for path, mod, imps in files:
            mine = next((m for m in mods if starts(mod, f"{root}.{m}")), None)
            if mine is None:
                continue
            for ln, target in imps:
                if any(starts(target, s) for s in shared):
                    continue
                other = next((m for m in mods if m != mine and starts(target, f"{root}.{m}")), None)
                if other:
                    v.append(f"{path}:{ln}  {mod} -> {target}  (independence: {mine} imports internals of {other})")
    elif kind == "forbidden":
        for r in rule["rules"]:
            for path, mod, imps in files:
                if not starts(mod, r["source"]):
                    continue
                for ln, target in imps:
                    if any(starts(target, f) for f in r["forbidden"]):
                        v.append(f"{path}:{ln}  {mod} -> {target}  (forbidden from {r['source']})")
    else:
        sys.exit(f"unknown kind: {kind}")
    return v


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("package_dir", nargs="?", help="root package directory (contains __init__.py)")
    ap.add_argument("--rules", help="JSON rules file")
    ap.add_argument("--init", choices=list(INIT), help="print a starter boundaries.json")
    ap.add_argument("--pkg", help="root package name (default: directory name)")
    a = ap.parse_args()
    if a.init:
        print(json.dumps(INIT[a.init], indent=2))
        return
    if not a.package_dir or not a.rules:
        ap.error("package_dir and --rules are required (or use --init)")
    base = Path(a.package_dir).resolve()
    root_pkg = a.pkg or base.name
    rules = json.loads(Path(a.rules).read_text(encoding="utf-8"))
    rule_sets = rules.get("rules_sets", [rules])
    files = []
    for p in sorted(base.rglob("*.py")):
        if any(part in {".venv", "venv", "__pycache__", "node_modules", ".web"} for part in p.parts):
            continue
        mod = module_name(p, base, root_pkg)
        try:
            files.append((p, mod, imports_of(p, mod)))
        except SyntaxError as e:
            print(f"WARN {p}: {e}", file=sys.stderr)
    violations, seen = [], set()
    for r in rule_sets:
        for line in check(r, files):
            key = line.split("  ")[0]  # file:line
            if key not in seen:
                seen.add(key); violations.append(line)
    if violations:
        print(f"FAIL {len(violations)} boundary violation(s):")
        for line in violations:
            print("  " + line)
        sys.exit(1)
    print(f"OK no violations ({len(files)} files, {len(rule_sets)} rule set(s))")


if __name__ == "__main__":
    main()
