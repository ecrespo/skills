# Template: 04-TEST-MATRIX.md

# Consolidated test matrix — {system name}

> Consolidates the test cases from all user stories. Priority P1 = protects a
> behavior that a fix commit proves was already broken once.

| ID | US | Criterion | Type (unit/integration/e2e) | Priority | Existing test in the current repo? | v2 status |
|---|---|---|---|---|---|---|
| TC-001.1 | US-001 | AC-001.1 | | P1/P2/P3 | `[VERIFY:]` or No | pending |

## Coverage summary

- Total cases: {n} · With an existing automated test: {n} ({%})
- Distribution by type and by priority (short table)
- **Critical gaps**: P1 criteria without an existing test — v2 must write these first

---

# Template: 05-REBUILD-PLAN.md

# Rebuild plan (v2) — {system name}

> Inputs: 01-ARCHITECTURE, 02-TECH-STACK, 03-EVOLUTION, US/*, 04-TEST-MATRIX.
> The original chronology (the era each user story was born in) is the first hint of
> the dependency order; correct it wherever the user-story dependency graph says otherwise.

## 1. Scope of v2

- What is rebuilt as-is (user stories at parity)
- What is redesigned (user stories flagged with "Notes for v2" + lessons from 03-EVOLUTION)
- What is dropped (abandoned/dead features detected in the history)

## 2. Stack decisions for v2

| Area | Current stack | v2 stack | Rationale |
|---|---|---|---|

## 3. Build phases

For each phase:

### Phase {n}: {name}
- **User stories**: US-XXX, US-YYY (with links)
- **Prerequisites**: previous phases / infrastructure
- **Verifiable "Done" criterion**: the test cases of its user stories passing
- **Risks**: inherited from the stack risks section and the observed debt

## 4. Pending SDD artifacts

Mapping to the Spec-Driven Design kit. If the `spec-driven-design` skill is
available, generate these artifacts now using the documents in this kit as
input; otherwise, leave the table as a backlog:

| SDD artifact | Input from this kit | Status |
|---|---|---|
| PRD | User stories + 03-EVOLUTION (context and lessons) | |
| API Spec | 01-ARCHITECTURE §2-3 (endpoints and flows) | |
| Technical Design | 01-ARCHITECTURE §5-7 + v2 stack decisions | |
| Data Model | 01-ARCHITECTURE §4 + cited schemas | |
| Implementation Plan | §3 of this document | |

## 5. What we do NOT know

An honest list of accumulated `[INFERRED]` marks and opaque areas of the repo, with
what would be needed to resolve them (domain expert, runtime access, missing docs).
v2 must not treat these inferences as confirmed requirements.
