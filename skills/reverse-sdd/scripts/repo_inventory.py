#!/usr/bin/env python3
"""repo_inventory.py — Detect languages, frameworks, infra and CI of a repository.

Outputs:
  <outdir>/inventory.json
  <outdir>/inventory.md

Pure stdlib, read-only.

Usage:
  python3 repo_inventory.py /path/to/repo -o /path/to/outdir
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
             ".next", ".nuxt", "target", "vendor", ".idea", ".vscode", "coverage",
             ".pytest_cache", ".mypy_cache", ".ruff_cache", "eggs", ".tox"}

LANG_BY_EXT = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript (React)",
    ".js": "JavaScript", ".jsx": "JavaScript (React)", ".go": "Go", ".rs": "Rust",
    ".java": "Java", ".kt": "Kotlin", ".rb": "Ruby", ".php": "PHP", ".cs": "C#",
    ".c": "C", ".cpp": "C++", ".h": "C/C++ header", ".sh": "Shell", ".sql": "SQL",
    ".tf": "Terraform", ".yml": "YAML", ".yaml": "YAML", ".vue": "Vue",
    ".svelte": "Svelte", ".dart": "Dart", ".ex": "Elixir", ".exs": "Elixir",
}

MANIFESTS = {
    "package.json": "Node.js", "pyproject.toml": "Python", "requirements.txt": "Python",
    "Pipfile": "Python", "setup.py": "Python", "go.mod": "Go", "Cargo.toml": "Rust",
    "pom.xml": "Java (Maven)", "build.gradle": "Java/Kotlin (Gradle)",
    "composer.json": "PHP", "Gemfile": "Ruby", "mix.exs": "Elixir",
    "pubspec.yaml": "Dart/Flutter", "*.csproj": ".NET",
}

CI_FILES = {
    "bitbucket-pipelines.yml": "Bitbucket Pipelines",
    ".gitlab-ci.yml": "GitLab CI",
    ".github/workflows": "GitHub Actions",
    "Jenkinsfile": "Jenkins",
    ".circleci/config.yml": "CircleCI",
    "azure-pipelines.yml": "Azure Pipelines",
}

# framework hints: dependency-name → framework label
DEP_HINTS = {
    "@nestjs/core": "NestJS", "express": "Express", "fastify": "Fastify",
    "next": "Next.js", "react": "React", "vue": "Vue", "@angular/core": "Angular",
    "svelte": "Svelte", "vite": "Vite",
    "fastapi": "FastAPI", "django": "Django", "flask": "Flask", "litestar": "Litestar",
    "sqlalchemy": "SQLAlchemy", "pydantic": "Pydantic", "celery": "Celery",
    "prefect": "Prefect", "airflow": "Airflow", "langchain": "LangChain",
    "langgraph": "LangGraph", "litellm": "LiteLLM", "httpx": "httpx",
    "pymongo": "MongoDB (PyMongo)", "mongoose": "MongoDB (Mongoose)",
    "pg": "PostgreSQL", "psycopg2": "PostgreSQL", "psycopg": "PostgreSQL",
    "mysql2": "MySQL", "redis": "Redis", "ioredis": "Redis", "prisma": "Prisma",
    "typeorm": "TypeORM", "sequelize": "Sequelize", "kafkajs": "Kafka",
    "amqplib": "RabbitMQ", "pika": "RabbitMQ", "boto3": "AWS SDK",
    "aws-sdk": "AWS SDK", "@aws-sdk/client-s3": "AWS SDK",
    "pytest": "pytest", "jest": "Jest", "vitest": "Vitest", "mocha": "Mocha",
    "cypress": "Cypress", "playwright": "Playwright", "@playwright/test": "Playwright",
}


def iter_files(root: Path):
    for p in root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file():
            yield p


def read_deps(root: Path) -> dict[str, str]:
    """Return {dep_name: version} from common manifests (best effort)."""
    deps: dict[str, str] = {}
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            for section in ("dependencies", "devDependencies"):
                deps.update(data.get(section) or {})
        except Exception:
            pass
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'^\s*"?([A-Za-z0-9_.\-\[\]]+?)"?\s*(?:[=><~!^]=?|@)\s*"?([^",\s\]]+)',
                             text, re.M):
            name = m.group(1).lower().split("[")[0]
            if name not in {"python", "requires-python", "version", "name", "line-length",
                            "target-version", "python_requires"}:
                deps.setdefault(name, m.group(2))
        for m in re.finditer(r'"([A-Za-z0-9_.\-]+)\[?[A-Za-z0-9_,\-]*\]?\s*[=><~!^]=?\s*([^"]+)"', text):
            deps.setdefault(m.group(1).lower(), m.group(2))
    req = root / "requirements.txt"
    if req.exists():
        for line in req.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith(("#", "-")):
                m = re.match(r"([A-Za-z0-9_.\-]+)\[?.*?\]?\s*(?:[=><~!]=?\s*(.+))?$", line)
                if m:
                    deps.setdefault(m.group(1).lower(), m.group(2) or "(unpinned)")
    return deps


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", type=Path)
    ap.add_argument("-o", "--outdir", type=Path, required=True)
    args = ap.parse_args()
    root = args.repo.resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        return 2

    lang_loc: Counter[str] = Counter()
    manifests_found: list[str] = []
    docker: list[str] = []
    ci: list[str] = []
    infra: list[str] = []
    test_dirs: set[str] = set()

    for p in iter_files(root):
        rel = p.relative_to(root).as_posix()
        lang = LANG_BY_EXT.get(p.suffix.lower())
        if lang:
            try:
                lang_loc[lang] += sum(1 for _ in p.open("rb"))
            except Exception:
                pass
        if p.name in MANIFESTS:
            manifests_found.append(rel)
        if p.name.lower().startswith("dockerfile") or p.name in (
                "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
            docker.append(rel)
        for ci_key, ci_name in CI_FILES.items():
            if rel == ci_key or rel.startswith(ci_key + "/"):
                if ci_name not in ci:
                    ci.append(ci_name)
        if p.suffix == ".tf" or "k8s" in rel.lower() or "kubernetes" in rel.lower() \
                or p.name in ("serverless.yml", "template.yaml", "cdk.json"):
            infra.append(rel)
        parts = rel.split("/")
        if any(seg in ("tests", "test", "__tests__", "e2e", "spec") for seg in parts[:-1]):
            test_dirs.add("/".join(parts[:parts.index(next(
                s for s in parts if s in ("tests", "test", "__tests__", "e2e", "spec"))) + 1]))

    deps = read_deps(root)
    frameworks = sorted({label for dep, label in DEP_HINTS.items() if dep in deps})

    lockfiles = [n for n in ("package-lock.json", "yarn.lock", "pnpm-lock.yaml",
                             "poetry.lock", "uv.lock", "Pipfile.lock", "go.sum",
                             "Cargo.lock", "composer.lock", "Gemfile.lock")
                 if (root / n).exists()]

    inv = {
        "repo": str(root),
        "languages_loc": dict(lang_loc.most_common()),
        "manifests": sorted(manifests_found),
        "lockfiles": lockfiles,
        "frameworks_detected": frameworks,
        "dependencies_count": len(deps),
        "dependencies": dict(sorted(deps.items())),
        "docker": sorted(docker),
        "ci": ci,
        "infra": sorted(infra)[:30],
        "test_dirs": sorted(test_dirs),
    }

    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "inventory.json").write_text(
        json.dumps(inv, indent=2, ensure_ascii=False), encoding="utf-8")
    (args.outdir / "inventory.md").write_text(render_md(inv), encoding="utf-8")
    print(f"OK: {len(lang_loc)} languages, {len(frameworks)} frameworks detected, "
          f"{len(deps)} dependencies. Written to {args.outdir}/inventory.{{json,md}}")
    return 0


def render_md(inv: dict) -> str:
    lines = ["# Repository inventory", "",
             f"**Repo:** `{inv['repo']}`", "",
             "## Languages (by approx. LOC)", "", "| Language | LOC |", "|---|---|"]
    for lang, loc in inv["languages_loc"].items():
        lines.append(f"| {lang} | {loc} |")
    lines += ["", "## Key frameworks and libraries detected", ""]
    lines += [f"- {f}" for f in inv["frameworks_detected"]] or ["- (none detected via hints)"]
    lines += ["", f"## Manifests ({len(inv['manifests'])})", ""]
    lines += [f"- `{m}`" for m in inv["manifests"]]
    if inv["lockfiles"]:
        lines += ["", "## Lockfiles (use these to pin exact versions)", ""]
        lines += [f"- `{l}`" for l in inv["lockfiles"]]
    if inv["docker"]:
        lines += ["", "## Docker", ""] + [f"- `{d}`" for d in inv["docker"]]
    if inv["ci"]:
        lines += ["", "## CI/CD", ""] + [f"- {c}" for c in inv["ci"]]
    if inv["infra"]:
        lines += ["", "## Infrastructure as code", ""] + [f"- `{i}`" for i in inv["infra"]]
    if inv["test_dirs"]:
        lines += ["", "## Test directories (source of acceptance criteria)", ""]
        lines += [f"- `{t}`" for t in inv["test_dirs"]]
    lines += ["", f"*{inv['dependencies_count']} dependencies in total — "
                  "see `inventory.json` for the full list with versions.*"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
