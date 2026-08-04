# Template: US/US-NNN-{slug}.md

One user story per curated cluster. Chronological numbering (US-001 = oldest cluster).
Evidence rules:
- The full user story cites its commits: `[COMMITS: ...]`
- Every criterion derived from an existing test cites the test file
- Every criterion derived from a fixed bug cites the fix hash
- Persona/benefit not evident in the code → `[INFERRED]`

---

# US-{NNN}: {title in business language}

> **Source cluster:** `{cluster}` · **Commits:** {n} `[COMMITS: {hash1}…{hashN}]`
> **Period:** {from} → {to} · **Era:** {label from 03-EVOLUTION.md}

## Story

**As a** {persona/role} `[INFERRED if applicable]`
**I want** {capability}
**So that** {benefit}

## Context of the original implementation

2-5 lines: which files/components materialize this story today `[VERIFY:]`,
and any relevant decision the commits reveal.

## Acceptance criteria

Gherkin format. Sources in priority order: (1) existing tests,
(2) fix commits in the cluster, (3) validations/error handling in the code.

### AC-{NNN}.1: {short name}
```gherkin
Given {precondition}
When {action}
Then {verifiable outcome}
```
*Source: {test `[VERIFY: tests/...]` | fix `[COMMITS: hash]` — describe the bug this
criterion prevents | code `[VERIFY: src/...]`}*

*(minimum: the happy paths + one criterion per bug fixed in the cluster)*

## Test cases

| ID | Criterion | Type | Scenario | Input data | Expected result | Existing test? |
|---|---|---|---|---|---|---|
| TC-{NNN}.1 | AC-{NNN}.1 | happy | | | | `[VERIFY:]` or "write in v2" |
| TC-{NNN}.2 | AC-{NNN}.1 | edge | | | | |
| TC-{NNN}.3 | AC-{NNN}.1 | negative | | | | |

Minimum per criterion: 1 happy + 1 edge + 1 negative. Reuse real test names
when they exist.

## Dependencies

- **Requires**: US-{XXX} (e.g.: authentication before profiles)
- **Enables**: US-{YYY}

## Notes for v2

Optional: what would change about this capability in the rebuild (observed debt,
recurring fixes, better design available today).

---

# Template: US/US-INDEX.md

# User Story Index

> {N} user stories generated from {M} curated clusters. Clusters discarded as noise: {list}.

| US | Title | Cluster | Commits | Hash range | Criteria | Test cases |
|---|---|---|---|---|---|---|
| US-001 | | | | `abc1234`…`def5678` | {n} | {n} |

## Traceability matrix

Coverage verification (must match the skill's validation pass):
- Every non-noise cluster → exactly one user story
- Every user story → rows in 04-TEST-MATRIX.md
- Every user story → a phase in 05-REBUILD-PLAN.md
