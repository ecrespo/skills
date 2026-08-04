#!/usr/bin/env python3
"""detect_stack.py — Phase 0 of the code-audit skill.

Detects stacks (FastAPI, Django, Node, NestJS, Next.js, React, Vite, Golang),
inventories Dockerfiles, lockfiles and tests, and builds a gap matrix of the
8 audit dimensions vs tooling already configured in the repo.

Usage:
    python3 detect_stack.py /path/to/repo -o /path/to/repo/docs/code-audit/analysis
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "dist", "build", ".next", ".nuxt",
    "__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache", "coverage",
    "vendor", ".tox", ".idea", ".vscode", "migrations", ".terraform",
}

DIMENSIONS = [
    "DRY", "SOLID", "unit_tests", "integration_tests",
    "SAST", "SCA", "secrets", "containers",
]


def walk(root: Path):
    for p in root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def read_text(p: Path, limit: int = 200_000) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def detect_python_stacks(root: Path, files: list[Path]) -> list[dict]:
    stacks = []
    for py_meta in [p for p in files if p.name in ("pyproject.toml", "requirements.txt", "requirements-dev.txt", "Pipfile")]:
        text = read_text(py_meta).lower()
        base = str(py_meta.parent.relative_to(root)) or "."
        if "fastapi" in text:
            stacks.append({"stack": "fastapi", "dir": base, "evidence": py_meta.name})
        if "django" in text:
            stacks.append({"stack": "django", "dir": base, "evidence": py_meta.name})
        if "fastapi" not in text and "django" not in text and py_meta.name == "pyproject.toml":
            stacks.append({"stack": "python", "dir": base, "evidence": py_meta.name})
    if any(p.name == "manage.py" for p in files):
        if not any(s["stack"] == "django" for s in stacks):
            stacks.append({"stack": "django", "dir": ".", "evidence": "manage.py"})
    return stacks


def detect_node_stacks(root: Path, files: list[Path]) -> list[dict]:
    stacks = []
    for pkg in [p for p in files if p.name == "package.json"]:
        try:
            data = json.loads(read_text(pkg))
        except json.JSONDecodeError:
            continue
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        base = str(pkg.parent.relative_to(root)) or "."
        found = False
        for key, name in [
            ("@nestjs/core", "nestjs"), ("next", "nextjs"), ("vite", "vitejs"), ("react", "reactjs"),
        ]:
            if key in deps:
                stacks.append({"stack": name, "dir": base, "evidence": f"package.json:{key}"})
                found = True
        if not found:
            stacks.append({"stack": "nodejs", "dir": base, "evidence": "package.json"})
    # collapse: react+vite in same dir -> react-vite; next implies react
    return stacks


def detect_go(root: Path, files: list[Path]) -> list[dict]:
    return [
        {"stack": "golang", "dir": str(p.parent.relative_to(root)) or ".", "evidence": "go.mod"}
        for p in files if p.name == "go.mod"
    ]


TEST_INTEGRATION_HINTS = re.compile(
    r"(integration|e2e|functional|testcontainers|integracion|\.integration\.|\.e2e[-.])", re.I
)
TEST_FILE_PATTERNS = re.compile(
    r"(^test_.*\.py$|_test\.py$|_test\.go$|\.(test|spec)\.[jt]sx?$)"
)


def inventory_tests(root: Path, files: list[Path]) -> dict:
    unit, integration = [], []
    for p in files:
        if not p.is_file():
            continue
        rel = str(p.relative_to(root))
        if TEST_FILE_PATTERNS.search(p.name):
            (integration if TEST_INTEGRATION_HINTS.search(rel) else unit).append(rel)
    return {
        "unit_count": len(unit),
        "integration_count": len(integration),
        "unit_sample": unit[:15],
        "integration_sample": integration[:15],
    }


TOOL_SIGNALS = {
    # dimension -> list of (label, predicate over (path_names:set, precommit:str, ci:str, configs:str))
    "DRY": ["jscpd", "dupl", "duplicate-code", "sonarjs"],
    "SOLID": [],  # no deterministic tool; always manual
    "unit_tests": ["pytest", "jest", "vitest", "go test", "unittest", "mocha"],
    "integration_tests": ["testcontainers", "e2e", "integration", "supertest", "httpx.AsyncClient"],
    "SAST": ["bandit", "semgrep", "gosec", "eslint-plugin-security", "codeql", "njsscan"],
    "SCA": ["pip-audit", "npm audit", "osv-scanner", "govulncheck", "safety", "dependabot", "renovate", "snyk", "audit-ci"],
    "secrets": ["gitleaks", "detect-secrets", "trufflehog", "detect-private-key"],
    "containers": ["hadolint", "trivy", "dockle", "grype", "docker scout"],
}


def gap_matrix(root: Path, files: list[Path]) -> dict:
    corpus_parts = []
    interesting = [
        ".pre-commit-config.yaml", "bitbucket-pipelines.yml", ".gitlab-ci.yml",
        "Makefile", "package.json", "pyproject.toml", "go.mod", ".golangci.yml",
        ".golangci.yaml", "renovate.json", "dependabot.yml",
    ]
    sources = []
    for p in files:
        if p.name in interesting or "/.github/workflows/" in str(p).replace("\\", "/"):
            corpus_parts.append(read_text(p))
            sources.append(str(p.relative_to(root)))
    corpus = "\n".join(corpus_parts).lower()
    matrix = {}
    for dim, signals in TOOL_SIGNALS.items():
        hits = sorted({s for s in signals if s.lower() in corpus})
        matrix[dim] = {"covered": bool(hits), "tools_found": hits}
    matrix["SOLID"] = {"covered": False, "tools_found": [], "note": "always manual evaluation (Phase 2)"}
    return {"sources_scanned": sources, "matrix": matrix}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()

    root = Path(args.repo).resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 1
    out = Path(args.output) if args.output else root / "docs" / "code-audit" / "analysis"
    out.mkdir(parents=True, exist_ok=True)

    files = [p for p in walk(root) if p.is_file()]

    stacks = detect_python_stacks(root, files) + detect_node_stacks(root, files) + detect_go(root, files)
    dockerfiles = [str(p.relative_to(root)) for p in files if p.name.lower().startswith("dockerfile")]
    compose = [str(p.relative_to(root)) for p in files if re.match(r"(docker-)?compose.*\.ya?ml$", p.name)]
    lockfiles = [str(p.relative_to(root)) for p in files
                 if p.name in ("uv.lock", "poetry.lock", "package-lock.json", "yarn.lock",
                               "pnpm-lock.yaml", "go.sum", "requirements.txt", "Pipfile.lock")]
    tests = inventory_tests(root, files)
    gaps = gap_matrix(root, files)
    has_precommit = any(p.name == ".pre-commit-config.yaml" for p in files)

    result = {
        "repo": str(root),
        "stacks": stacks,
        "dockerfiles": dockerfiles,
        "compose_files": compose,
        "lockfiles": lockfiles,
        "has_precommit": has_precommit,
        "tests": tests,
        "gaps": gaps,
    }
    (out / "stack.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---- gaps.md ----
    lines = ["# Gap matrix — code-audit Phase 0", ""]
    lines.append(f"**Repo:** `{root}`  ")
    stack_names = ", ".join(sorted({s['stack'] for s in stacks})) or "not detected"
    lines.append(f"**Stacks:** {stack_names}  ")
    lines.append(f"**Dockerfiles:** {len(dockerfiles)} · **Lockfiles:** {len(lockfiles)} · "
                 f"**pre-commit:** {'yes' if has_precommit else 'NO'}")
    lines.append("")
    lines.append(f"**Tests:** {tests['unit_count']} unit (heuristic) · "
                 f"{tests['integration_count']} integration")
    lines.append("")
    lines.append("| Dimension | Tooling present? | Tools found |")
    lines.append("|---|---|---|")
    for dim in DIMENSIONS:
        m = gaps["matrix"][dim]
        mark = "✅" if m["covered"] else "❌"
        lines.append(f"| {dim} | {mark} | {', '.join(m['tools_found']) or '—'} |")
    lines.append("")
    lines.append("## Stack details")
    for s in stacks:
        lines.append(f"- **{s['stack']}** in `{s['dir']}` — evidence: {s['evidence']}")
    if dockerfiles:
        lines.append("\n## Dockerfiles")
        lines.extend(f"- `{d}`" for d in dockerfiles)
    lines.append("\n> Note: the matrix detects *configuration*, not execution. A ✅ means "
                 "the tool appears in the scanned pre-commit/CI/configs; verify in "
                 "Phase 1 that it actually runs and blocks.")
    (out / "gaps.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"stacks: {stack_names}")
    print(f"wrote {out/'stack.json'} and {out/'gaps.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
