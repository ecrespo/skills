# Template: 02-MIGRATION-PLAN.md

Principles: Phase 1 is pure guardrails (make the current state verifiable before
changing it); phases ordered by (risk reduction ÷ effort); each phase reversible and
with a measurable "Done"; never big-bang.

---

# Architecture migration plan — {system name}

> Inputs: 01-EVALUATION-REPORT.md + adr/*
> Overall strategy: {evolve in place | strangler | v2 rebuild | hybrid}
> — and why (2-4 lines)

## Phase 1: Guardrails (always first)

Freeze the current state with automated verification, without changing behavior:

- Boundary rules (import-linter / dependency-cruiser / eslint-boundaries) that encode
  the *current* boundaries — even the imperfect ones: first stop things from getting
  worse
- Characterization tests around the seams the ADRs are going to touch
- Baseline metrics recorded: cycles, cross-module pairs, hotspots (the JSON files in
  `analysis/` are the baseline — version them)

**Done**: CI fails if a new cycle appears or an import crosses a declared boundary.

## Phase {n}: {name}

- **ADRs it implements**: ADR-XXX, ADR-YYY
- **Prerequisites**: previous phases, infrastructure, pending decisions
- **Steps**: 3-8 concrete steps, each deployable separately
- **Verifiable Done**: target metric (e.g.: "`invoices↔api` SCC eliminated:
  re-run dep_graph.py and check `cycles_scc: []`") + tests green
- **Rollback**: how this phase is reverted if something goes wrong
- **Risks**: what can break and how it would be detected (observability first if the
  report marked it amber/red)

*(repeat per phase)*

## What will NOT be done

Explicit list of tempting refactors that were rejected and why (with a link to the
rejected alternative in the corresponding ADR). This section protects the plan from
scope creep as much as the phases structure it.

## Reconciliation with a rebuild (if applicable)

If `docs/reverse-sdd/05-REBUILD-PLAN.md` exists: which changes are made
incrementally here vs which are deferred as v2 design decisions, and the criterion
used to split them (rule of thumb: what reduces risk in the current system goes here;
what only makes sense with the full redesign goes to the v2).

## Follow-up

Cadence for re-running the scripts (e.g. monthly or per release) and what threshold
triggers a review: cycles > 0, a new cross-module pair with confidence ≥0.5, a new
hotspot in the top 5.
