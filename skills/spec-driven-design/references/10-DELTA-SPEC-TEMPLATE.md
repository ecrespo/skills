# Template: changes/{YYYY-MM}-{slug}/ (Delta Spec)

Pattern for evolving features that already have a spec (spec-anchored level): `specs/`
is the current truth; each change lives as a proposal in `changes/` with its delta and
its tasks; once approved and implemented, the delta is **folded** into the base specs
and the change folder is archived. This way the spec is never abandoned: it evolves
with commits just like the code.

When to use it: any modification to already-specified behavior (new rule, new field,
flow change). When NOT to: new features with no prior spec (normal PRD→... flow) or
bug fixes that restore already-specified behavior.

Change structure:

```
changes/2026-08-c2p-idempotency/
├── proposal.md      # why, scope, impact
├── delta-spec.md    # ADDED / MODIFIED / REMOVED against the base specs
└── tasks.md         # template 09, tracing to the new/modified REQs
```

---

## proposal.md

# Proposal — {change title}

> Status: draft | in review | approved | implemented | archived
> Affected base specs: {paths in specs/} · Date: {date} · Author: {who}

**Problem/motivation** (3-6 lines, with data): what hurts today and what evidence
exists (incidents, arch-evaluator/code-audit findings, metrics).

**Scope**: what changes and what explicitly does NOT change.

**Impact**: affected contract consumers, data migrations, compatibility
(breaks the API? → version it), risks.

**Constitution check**: applicable articles and how they are satisfied.

---

## delta-spec.md

# Delta — {title}

Each entry references the base document and section. New REQs take new IDs;
removed ones retire their ID forever.

## ADDED

### specs/prd/{feature}.md → Requirements
- **REQ-PAY-006** (unwanted behavior): IF a C2P debit is received without a prior
  reference, THEN THE SYSTEM SHALL hold it as `unreconciled` and alert operations.

### specs/api/{feature}-api-v1.md → Endpoints
- `POST /payments/{id}/reconcile` — {summary; full contract right here}

## MODIFIED

### specs/prd/{feature}.md → REQ-PAY-003
- **Before**: retry with simple backoff.
- **After**: WHEN the provider does not respond within 8 s, THE SYSTEM SHALL ... with
  exponential backoff and a cap of 5 attempts.
- **Reason**: {incident/finding that motivates it}.

## REMOVED

### specs/prd/{feature}.md → REQ-PAY-00X
- **Reason**: {why it ceases to exist}. Associated tests: {remove/adapt}.

---

## Lifecycle

1. Draft → review (Analyze the delta against the base specs: does it contradict
   anything? does it break traceability?) → approved.
2. Implement with its `tasks.md` (same rules as template 09).
3. **Fold**: apply ADDED/MODIFIED/REMOVED onto the files in `specs/` in the same PR
   that closes the implementation (part of the Definition of Done).
4. Move the folder to `changes/_archive/` (or tag it) — git history keeps everything.

Golden rule: if the code changed and `specs/` did not, the change is not finished.
