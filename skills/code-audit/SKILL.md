---
name: code-audit
description: >
  Full quality + security audit of a repo with deterministic evidence and markdown
  reports across 8 dimensions: DRY, SOLID, unit tests, integration tests, SAST, SCA
  (dependency CVEs), secrets, and container security. Auto-detects the stack and applies
  the right tool matrix per framework — FastAPI, Django, Node.js, NestJS, Next.js, React,
  Vite, Golang — with ready-to-use .pre-commit-config.yaml templates per stack replicating
  the CuidaSalud gate (Gitleaks, Ruff/ESLint/golangci-lint, Bandit/gosec, pip-audit/npm
  audit/govulncheck, Hadolint, complexity). Use whenever the user wants to audit, evaluate
  or harden a repo's quality or security, asks for a "code audit", "assess the repo's
  security", "review DRY/SOLID", "test coverage", "validate dependencies or containers",
  "set up the pre-commit for X stack", or wants a security/quality report in markdown —
  even for a single dimension (e.g. just SAST or just the pre-commit).
---

# Code-Audit: quality + security audit with evidence

Audit a repository across 8 dimensions and produce reports a tech lead can act on.
Deliverables land in the target repo:

```
docs/code-audit/
├── analysis/                    # Script + tool outputs (stack.json, gaps.md, raw logs)
├── 01-AUDIT-REPORT.md           # 8-dimension scorecard + ranked findings
├── 02-REMEDIATION-PLAN.md       # Fixes by severity with effort and verification
└── .pre-commit-config.yaml      # Proposed for the detected stack (if none exists)
```

## The 8 dimensions

| # | Dimension | What it measures | Deterministic evidence |
|---|-----------|------------------|------------------------|
| 1 | DRY | Code duplication | jscpd / pylint R0801 / dupl (golangci) |
| 2 | SOLID | Class/module design | signals: size, fan-in/out, checklist |
| 3 | Unit tests | Existence, coverage, isolation | pytest-cov / jest·vitest --coverage / go test -cover |
| 4 | Integration tests | API/DB/external layer covered | test inventory + markers/patterns |
| 5 | SAST (code) | Vulnerabilities in the code | Bandit / Semgrep / ESLint-security / gosec |
| 6 | SCA (packages) | CVEs in dependencies | pip-audit / npm audit·osv-scanner / govulncheck |
| 7 | Secrets | Hardcoded credentials | Gitleaks (working tree + history) |
| 8 | Containers | Dockerfile and image | Hadolint / Trivy / Dockle |

## Ground rules

1. **No finding without evidence.** Every finding carries a tag: `[TOOL: cmd → output]`
   (strongest), `[VERIFY: file:line]` (code reading), `[GAP: missing config]`. SOLID is
   the only dimension where reading-based findings are the norm — even there, anchor
   each one to a file:line. If you write "could" or "possibly" without a tag,
   find the evidence or drop the finding.
2. **Run tools, don't simulate them.** If a tool is installable in the environment,
   install and run it; paste real output into `analysis/`. If it cannot run (no
   network, no Docker daemon), say so explicitly and mark the dimension **"not
   evaluated (tooling)"** — never invent counts of vulnerabilities or coverage.
3. **Severity is risk, not lint noise.** P1 = exploitable or loss of data/money
   (real secret, reachable critical CVE, SQL injection). P2 = weakens defenses
   (no SCA in CI, coverage <40% in the payments module). P3 = quality (duplication,
   complexity). A repo with 400 style warnings and 1 secret has **1** P1 finding.
4. **Strengths are mandatory.** Name what the repo already does well, with the same
   rigor. An audit that only lists problems loses the reader.

## Workflow

### Phase 0 — Stack detection + gap matrix (script, ~30s)

```bash
python3 scripts/detect_stack.py /path/to/repo -o /path/to/repo/docs/code-audit/analysis
```

Outputs `stack.json` + `gaps.md`: detected stacks (FastAPI/Django/Node/Nest/Next/React/
Vite/Go, may be several in a monorepo), Dockerfiles, lockfiles, test inventory
(unit vs integration heuristic), and the **gap matrix**: which of the 8 dimensions
already have tooling configured (pre-commit, CI, configs) vs missing. Read `gaps.md`
before anything else — it decides which reference file to open next.

### Phase 1 — Run the tool matrix for the detected stack

Open exactly the reference file(s) for the detected stack; each lists install commands,
run commands with the right flags, and how to interpret output:

- `references/stacks-python.md` — FastAPI and Django (Ruff, ty/mypy, Bandit, Semgrep,
  pip-audit, Lizard, flake8-cognitive-complexity, djLint)
- `references/stacks-node.md` — Node.js, NestJS, Next.js, React, Vite (ESLint +
  sonarjs + security, tsc, npm audit/osv-scanner, jscpd, jest/vitest)
- `references/stacks-golang.md` — Golang (golangci-lint: gocyclo+gocognit+gosec+dupl,
  govulncheck, gofumpt)
- `references/containers.md` — Hadolint, Trivy (fs + image + config), Dockle,
  what runs in pre-commit vs CI

Save every raw output under `analysis/` (e.g. `analysis/bandit.txt`,
`analysis/jscpd.json`). Run read-only: never `--fix` during an audit.

### Phase 2 — DRY, SOLID and tests (semi-manual)

Read `references/dry-solid-tests.md`. It defines:
- **DRY**: thresholds (jscpd >3% duplicated lines = amber, >8% = red), which duplication
  is legitimate (DTOs, migrations, fixtures) and which is not.
- **SOLID**: 15 grep-able signals per principle (God classes, `isinstance` ladders,
  fat interfaces, concrete-class imports in domain layer…). Green/amber/red score per
  principle with file:line. If `docs/arch-eval/` exists (arch-evaluator skill), reuse
  its fan-in/fan-out and cycles instead of re-deriving them.
- **Tests**: how to separate unit from integration by stack convention, minimum
  coverage by module criticality, and 6 smells (tests without asserts, sleeps, order-
  dependent tests, mocks of the system under test…).

### Phase 3 — Report

Read `references/report-template.md` and write `01-AUDIT-REPORT.md`:
scorecard of the 8 dimensions (green/amber/red + 1-3 lines of evidence each),
strengths, findings ranked P1→P3 with an evidence tag, and discarded findings
(false positives, with reason). 5-15 findings is the useful range; 40 means you did
not prioritize. Then `02-REMEDIATION-PLAN.md`: each P1/P2 with a concrete fix, effort
(S/M/L), and **verification** ("re-run `pip-audit` → 0 high CVEs"). First phase of the
plan = guardrails (install the proposed pre-commit) before touching code.

### Phase 4 — Pre-commit gate for the stack

Copy the matching template from `assets/precommit/` into the repo as
`.pre-commit-config.yaml` (or diff against the existing one and propose only the
missing hooks). Templates available: `fastapi`, `django`, `nodejs`, `nestjs`,
`nextjs`, `react-vite`, `golang`. All replicate the same gate philosophy:

- **pre-commit (fast, <30s)**: secrets, format, lint, types, complexity, lightweight
  SAST, SCA only if the lockfile changed.
- **CI (slow)**: tests + coverage, Semgrep with full rulesets, Trivy fs+image,
  optional mutation testing.

Adjust pins/versions to what the repo already uses; never downgrade a tool the repo
pins higher. If the repo does not use pre-commit, the remediation plan includes the
same commands as a `make audit` script or an equivalent CI job.

## Validation pass (before delivering)

1. Every `[TOOL:]` claim matches a file in `analysis/` — numbers drift when written
   from memory.
2. Sample 5 `[VERIFY: file:line]` citations; one wrong → re-check all in that report.
3. Every P1 has a fix in `02-REMEDIATION-PLAN.md` or an explicit "risk accepted".
4. The proposed pre-commit actually parses: `pre-commit validate-config` (or YAML
   lint if pre-commit isn't installed).
5. Scorecard honesty: any dimension without executed tooling says "not evaluated
   (tooling)", not a guessed color.

## Scaling & monorepos

Monorepo multi-stack: run Phase 0 once at root (it reports per-directory stacks),
then Phases 1-2 per package, one report with a scorecard per package plus a global
one. Repos >200k LOC: jscpd with `--pattern` per package; Semgrep/Trivy on CI only.
If a dimension is owned elsewhere (e.g. containers built by another team), mark it
"out of scope" with the link, not red.
