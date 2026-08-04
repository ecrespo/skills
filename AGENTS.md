# Agent instructions

This repository is a collection of Agent Skills. Each skill is a self-contained folder under `skills/<name>/` with a `SKILL.md` entry point plus optional `references/`, `scripts/`, and `assets/`.

## Using the skills

When a task matches one of the descriptions below, read the corresponding `skills/<name>/SKILL.md` and follow it. Load files from `references/` only when the skill directs you to; run `scripts/` with Python 3 (stdlib only, no installs needed).

- `skills/arch-evaluator` — evaluate a repository's architecture with deterministic evidence (dependency graph, git-history mining), rank weaknesses, propose ADRs and a migration plan.
- `skills/code-audit` — 8-dimension quality + security audit (DRY, SOLID, unit/integration tests, SAST, SCA, secrets, containers) with per-stack tool matrices and pre-commit templates.
- `skills/graph-first-context` — token-efficient codebase understanding via CodeGraph, Graphify, and lat.md; query graphs before grep/glob/file reads.
- `skills/reverse-sdd` — reverse-engineer docs, user stories, acceptance criteria, and a rebuild plan from an existing repo's code and git history.
- `skills/spec-driven-design` — Spec-Driven Design v2: Constitution, PRD with EARS criteria, API spec, technical design, data model, plan, tasks, delta specs, analyze gate.

## Execution order

When chaining multiple skills over the same repository, follow this order — each stage feeds the next: `graph-first-context` (index the codebase) → `reverse-sdd` (documentation baseline) → `code-audit` (quality/security findings) → `arch-evaluator` (architecture verdict, ADRs, migration plan) → `spec-driven-design` (specs and tasks for the accepted changes). Each skill also works standalone.

## Working on this repository

- Skills must comply with the Agent Skills format: frontmatter limited to `name` and `description`, lowercase-hyphen names matching the folder, description ≤ 1024 chars in third person, English-only content.
- After any change, run `python3 scripts/validate_and_package.py --no-package` and make sure all skills pass.
- Bundled scripts must stay pure-stdlib Python 3 and read-only over analyzed repos.
- Long-form content belongs in `references/`, not in `SKILL.md` bodies.
