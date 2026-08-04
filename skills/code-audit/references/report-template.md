# Report templates

## 01-AUDIT-REPORT.md

```markdown
# Code and security audit — {repo}

**Date:** {YYYY-MM-DD} · **Stack:** {stacks} · **Audited commit:** {short sha}
**Tools executed:** {list with versions} · **Not executed:** {list + reason}

## Executive summary
{3-5 lines: overall posture, the most serious finding, the main strength, and the
first step of the plan. No tool jargon.}

## Scorecard

| # | Dimension | Verdict | Evidence (1-3 lines) |
|---|-----------|---------|----------------------|
| 1 | DRY | 🟢/🟡/🔴 | [TOOL: jscpd → 4.2% duplicated, 12 clones] |
| 2 | SOLID | 🟢/🟡/🔴 | per principle: S🟡 O🟢 L🟢 I🟡 D🔴 + key evidence |
| 3 | Unit tests | 🟢/🟡/🔴 | [TOOL: pytest-cov → 68% global, payments 41%] |
| 4 | Integration tests | 🟢/🟡/🔴 | [VERIFY: tests/integration/ → 0 bank-timeout tests] |
| 5 | SAST | 🟢/🟡/🔴 | [TOOL: bandit → 2 confirmed HIGH] |
| 6 | SCA | 🟢/🟡/🔴 | [TOOL: pip-audit → 1 reachable critical CVE] |
| 7 | Secrets | 🟢/🟡/🔴 | [TOOL: gitleaks → 0 in tree, 1 in history] |
| 8 | Containers | 🟢/🟡/🔴 | [TOOL: hadolint → no USER; trivy: pending CI] |

{Dimension without executed tooling → "⚪ not evaluated (tooling)" + what is missing to evaluate it.}

## Strengths
{3-6 points with the same evidence as the findings. Mandatory.}

## Findings

### P1 — {imperative title, e.g. "Mercantil secret in git history"}
- **Dimension:** {n} · **Evidence:** [TOOL/VERIFY/GAP: …]
- **Impact:** {what can happen, in business/data terms}
- **Fix:** → REMEDIATION-PLAN #{n}

### P2 — …
### P3 — {group into one table if they are style/volume items}

## Discarded findings
| Tool report | Reason discarded |
|---|---|
| bandit B101 assert in tests/ | assert is idiomatic in pytest |
```

## 02-REMEDIATION-PLAN.md

```markdown
# Remediation plan — {repo}

## Phase 0 — Guardrails (before touching code)
Install the proposed `.pre-commit-config.yaml` + equivalent CI job. Freezes the state:
nothing new gets in worse than it already is.

## Phase 1 — P1 ({n} items)
### R-01 · {title} (finding P1-{n})
- **Fix:** {concrete: command, file, pattern}
- **Effort:** S/M/L · **Fix risk:** {what could break}
- **Verification:** {re-runnable command: "gitleaks detect → 0", "pip-audit → 0 high"}

## Phase 2 — P2 · Phase 3 — P3 (batch)
{same format; P3 in a compact table}

## Follow-up
| Item | Owner | Verification | Status |
```

Vault file convention (if a copy is requested for Obsidian):
`YYYY-MM-DD-Audit-{repo}.md`, same format as the forensic reports.
