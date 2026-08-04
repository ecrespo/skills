# Template: tasks/feature-tasks.md

The bridge between the plan and execution (human or by agent): atomic tasks,
ordered by dependency, each traceable to a requirement and with a verifiable "Done".
Generated AFTER the Implementation Plan and BEFORE the Analyze.

Rules:
- **Atomic** = a change reviewable and revertible on its own (≈ one small commit/PR).
- **Traceable** = each task cites the `REQ-NNN`(s) it implements. Task without a REQ →
  either the requirement is missing (write it) or the task is superfluous (delete it).
  The Analyze verifies this.
- **[P]** marks parallelizable tasks (no dependency between them and no shared files).
- **Verifiable Done** = a concrete command or observation, not "finished".
- Agent execution: first batch of 3-5 tasks, review, adjust, then scale.
  Progress is marked in this file (checkbox + date) so any session can resume.

---

# Tasks — {feature}

> Source specs: {links to PRD, API Spec, Tech Design, Data Model, Plan}
> Plan phase covered: {Phase N} · Generated: {date}

## Conventions for this file

- Order = execution order except for [P].
- States: `[ ]` pending · `[~]` in progress · `[x] {date}` done · `[!]` blocked (note).

## Tasks

### T-001 · Preparation {[P] if applicable}
- **What**: {e.g.: create the migration for the `payments` collection per Data Model §3}
- **REQ**: REQ-PAY-001, REQ-PAY-004
- **Files**: {expected paths}
- **Depends on**: —
- **Done**: {e.g.: `pytest tests/migrations/test_payments_schema.py` green}

### T-002 · {title}
- **What**: ...
- **REQ**: ...
- **Depends on**: T-001
- **Done**: ...

*(continue; 8-25 tasks per feature is the healthy range — 40+ means the feature
should have been split into phases)*

## Traceability matrix

| REQ | Tasks | Tests citing it |
|---|---|---|
| REQ-PAY-001 | T-001, T-003 | test_confirm_payment_creates_tx |
| REQ-PAY-002 | T-004 | test_idempotent_confirmation |

Every MUST from the PRD must appear here with ≥1 task and ≥1 test. SHOULDs without a
task are explicitly listed as deferred.

## Execution log

| Date | Tasks | Result | Notes |
|---|---|---|---|
| {date} | T-001..T-004 | ✅/❌ | {deviations from the spec → open a Delta} |

If during implementation you discover the spec was wrong: **stop, update the spec (or
open a Delta), and only then continue** — never let the code and the spec silently
diverge.
