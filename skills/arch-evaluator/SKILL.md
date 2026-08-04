---
name: arch-evaluator
description: >
  Evaluate the architecture of an existing repository with deterministic evidence, find
  weaknesses, and propose improvements or architecture changes as ADRs plus a phased
  migration plan. Builds a dependency graph (Python and TypeScript/JavaScript) to detect
  circular dependencies, god modules and unstable coupling; mines git history for hotspots,
  fix-prone files and temporal (co-change) coupling; scores the system against a quality-
  attribute checklist (coupling, cohesion, testability, resilience, data consistency,
  observability, security, evolvability); and ranks weaknesses by severity with evidence.
  Use whenever the user wants to evaluate, audit, review or critique a repo's architecture,
  find architectural weaknesses or structural technical debt, asks "evaluate the
  architecture", "architecture audit", "what's wrong with this repo", "propose architecture
  improvements", or wants refactoring / migration proposals — even if they only ask for
  one part (e.g. just the dependency analysis).
---

# Arch-Evaluator: evidence-based architecture audit

Evaluate a repository's architecture and produce a verdict a tech lead can act on:
strengths, ranked weaknesses, change proposals as ADRs, and a phased migration plan.

```
docs/arch-eval/
├── analysis/                   # Script outputs (dep_graph.*, arch_signals.*)
├── 01-EVALUATION-REPORT.md     # Scorecard + strengths + ranked weaknesses
├── adr/ADR-NNN-{slug}.md       # One ADR per proposed change
└── 02-MIGRATION-PLAN.md        # Phased, reversible migration plan
```

## Ground rules

1. **No finding without evidence.** Every weakness carries at least one tag:
   `[METRIC: ...]` (script output — strongest), `[VERIFY: file:line]` (code reading),
   `[COMMITS: hash]` (history). Findings supported only by reading get at most severity
   P2; P1 requires deterministic evidence (a cycle in the graph, a co-change pair, a
   fix-prone hotspot). If you catch yourself writing hedging words like "might" or
   "possibly" without a tag, either find the evidence or drop the finding.

2. **An audit that breaks the codebase is worse than no audit.** A working monolith beats
   a broken set of small modules. Never recommend splitting a large file or extracting a
   service without first identifying the seam (a real boundary the dependency graph and
   co-change data support). Every proposal must state its cost and what NOT to touch.

3. **Strengths are mandatory.** An audit that only lists problems is not credible and
   loses the reader. Name what the architecture does well, with the same evidence rigor.

## Workflow

### Phase 0 — Deterministic evidence (scripts, ~1-2 min)

```bash
python3 scripts/dep_graph.py    /path/to/repo -o /path/to/repo/docs/arch-eval/analysis
python3 scripts/arch_signals.py /path/to/repo -o /path/to/repo/docs/arch-eval/analysis
```

`dep_graph.py` parses Python + TS/JS imports into a module-level graph and reports:
cycles (SCCs), fan-in/fan-out/instability per module, god-module candidates, orphans.
`arch_signals.py` mines git history for: hotspots weighted by churn×fixes, fix-prone
files, **temporal coupling** (file pairs that change together across module boundaries —
the strongest hidden-coupling signal), and knowledge concentration (bus factor) per
module. Read both `.md` summaries before touching any code.

Reuse, don't duplicate: if `docs/reverse-sdd/analysis/` exists (from the reverse-sdd
skill), its `history.json` already has hotspots and fix-prone files — cross-reference
instead of re-deriving conclusions that may drift apart. If a `.codegraph/` index and
the graph-first-context skill are available, use them for the code-reading phases.

If the repo has no `.git`, run `dep_graph.py` only and state in the report that all
history-based signals (temporal coupling, hotspots) are unavailable.

### Phase 1 — Verify the machine findings in the code

Scripts detect structure, not intent. For each cycle, god-module candidate and top
temporal-coupling pair, open the code and answer: is this a real problem or a false
positive? Typical false positives: barrel/index files (high fan-in by design), generated
code, type-only imports, a "cycle" through a constants module. Record verdicts —
confirmed findings move forward with `[METRIC + VERIFY]`, dismissed ones go in a
"Dismissed findings" appendix so the next audit doesn't re-litigate them.

### Phase 2 — Quality-attribute scorecard

Read `references/quality-attributes-checklist.md` and evaluate the 8 attributes. Each
gets a green/amber/red verdict with 1-3 evidence lines. The checklist tells you what
evidence to look for per attribute; don't score an attribute you didn't actually
inspect — mark it "not evaluated" instead. Weight the attributes by what the system
*is*: a payments integration lives or dies by resilience and data consistency; an
internal CLI doesn't.

### Phase 3 — Rank weaknesses

Read `references/report-template.md` and write `01-EVALUATION-REPORT.md`. Severity:

- **P1**: deterministic evidence + touches a high fan-in module or a critical attribute
  (data loss, security, money). These block or shape the v2.
- **P2**: confirmed by code reading; contained blast radius.
- **P3**: style/consistency; batch them, don't ADR them.

Blast radius comes from the graph: a weakness in a module with fan-in 12 outranks the
same weakness in a leaf. Tie each weakness to the attribute it degrades and the evidence
tags. 5-12 weaknesses is the useful range; 30 findings means you didn't prioritize.

### Phase 4 — Propose changes as ADRs

For each P1 (and P2s worth fixing), read `references/adr-template.md` and write one ADR:
context (links the weakness), decision, **at least two alternatives with honest
trade-offs** (including "do nothing"), consequences, estimated cost, reversibility.
Anti-overengineering guardrails, non-negotiable:

- No microservices extraction without team-size and operational justification stated in
  the ADR. Distributed complexity is a cost you pay every day.
- No new abstraction layers "for flexibility" — only abstract what demonstrably varies
  (two real implementations, or an integration the history shows churns).
- Prefer boring fixes: enforce a boundary with a lint rule (import-linter,
  dependency-cruiser rules) before proposing a structural rewrite.
- If the fix is "split module X", the ADR must show the seam: which files go where and
  why the graph/co-change data supports that cut.

If the engineering:architecture skill is available, follow its ADR conventions.

### Phase 5 — Migration plan

Read `references/migration-plan-template.md` and write `02-MIGRATION-PLAN.md`: phases
ordered by (risk reduction ÷ effort), each with its ADRs, prerequisites, a verifiable
"Done" (ideally a metric: "cycle count 3→0", "temporal-coupling pairs across auth/
billing: 0"), and a rollback path. First phase should be pure guardrails (lint rules,
tests around the seams) — make the current state enforceable before changing it. If a
reverse-sdd `05-REBUILD-PLAN.md` exists, reconcile: architecture changes either
land as v2 design decisions there, or as incremental phases here — say which.

## Validation pass (before delivering)

1. Re-run both scripts; confirm every `[METRIC:]` claim matches the JSON (numbers drift
   when you write from memory).
2. Sample 5 `[VERIFY:]` citations; wrong line → re-check all citations in that document.
3. Every P1 weakness has either an ADR or an explicit "accepted risk" with reason.
4. Read the ADRs adversarially: for each, can you argue the "do nothing" alternative
   with a straight face? If not, the trade-offs section is propaganda — rewrite it.
5. Count proposals that add complexity (new layers, new services, new tech) vs remove
   it. If adders dominate, re-read ground rule 2 and cut.

## Scaling

Large repos (>200k LOC): run `dep_graph.py` per top-level package (`--root src/moduleX`)
and audit module-by-module; `arch_signals.py --max-commits 1000` for the recent window
plus one historical pass if eras differ. Multi-language monorepos: the graph covers
Python/TS/JS; for other languages state the gap and rely on history signals, which are
language-agnostic.
