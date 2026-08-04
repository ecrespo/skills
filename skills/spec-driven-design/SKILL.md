---
name: spec-driven-design
description: >
  Methodology and templates for Spec-Driven Design/Development (SDD) v2 — specifications
  as the primary artifact before code, aligned with the 2026 state of the art (GitHub Spec
  Kit, Kiro, OpenSpec). Nine artifacts: Constitution (project principles), PRD with EARS
  acceptance criteria, API Spec, Technical Design, Data Model, Implementation Plan, Tasks
  (agent-executable with traceability), Delta Specs (brownfield changes), and the Analyze
  cross-artifact validation. Use whenever the user wants to plan a feature, design an API,
  write a PRD, tech design, data model, implementation plan, constitution, task breakdown,
  or delta/change spec; mentions "spec", "EARS", "constitution", "tasks", "spec kit",
  "kiro", "analyze specs", "spec-driven", "design doc", "break down into tasks", "change
  proposal"; or asks to plan before coding — greenfield or changes to existing systems.
  Even "I need to plan a new feature" or "help me document this before building" triggers it.
---

# Spec-Driven Design (SDD) v2

Specifications are the primary artifact: the spec is the cheapest place to be wrong,
because a wrong spec costs keystrokes while wrong code costs refactors. This skill keeps
the original 5-document core (PRD, API Spec, Technical Design, Data Model, Implementation
Plan) and adds the artifacts the 2025-2026 ecosystem converged on: Constitution, EARS
acceptance criteria, Tasks, Delta Specs, and the Analyze gate.

## Rigor spectrum — decide this first

Ask (or infer) which level the project operates at; it changes which artifacts live on:

- **spec-first**: spec written before the task, discarded after. Minimum viable rigor.
- **spec-anchored** (default for this skill): specs live in the repo, versioned, updated
  as the feature evolves. Changes to shipped features go through Delta Specs.
- **spec-as-source**: humans edit only specs; code is regenerated from them. Aspirational;
  flag the extra discipline it demands (every behavior in the spec, no manual patches).

## The v2 flow

```
Constitution (once per project)
      ↓
PRD with EARS criteria (the what) → API Spec (contract) → Tech Design (the how)
      → Data Model → Implementation Plan (phases) → Tasks (executable)
      ↓
Analyze (cross-artifact validation, read-only) → Implement → Validate
      ↓
Later changes: Delta Spec in changes/ → once approved, folded into specs/
```

Human checkpoints between every phase: each artifact is reviewed and approved before the
next one is generated. Never generate the whole chain in one shot for non-trivial work.

## Depth proportional to risk (updated)

| Type of work | Artifacts |
|---|---|
| Bug fix | None (the ticket is enough) |
| Internal refactor | Tech Design lite (decisions + plan) |
| Simple CRUD + API | API Spec + Data Model + Tasks |
| Change to an already spec-ed feature | Delta Spec + Tasks |
| Medium feature (1-2 sprints) | PRD + API Spec + Data Model + Tasks |
| Complex feature (3+ sprints) | All 5 documents + Tasks + Analyze |
| New service/microservice | Constitution check + all 5 + Tasks + Analyze |
| New project | Constitution first, then the above |

The Constitution is written **once per project** (revisable, not per feature). Tasks are
generated whenever an agent (or a dev with limited context) will do the implementation.

## How to use this skill

1. **Scope**: what are they building; pick depth from the table; confirm rigor level.
2. **Constitution first** on new projects (or when standards keep being relitigated in
   PRs — that's the symptom of a missing constitution).
3. **Generate sequentially**, one artifact per exchange, review between each.
4. **Analyze before implement**, always, for anything ≥ medium feature.
5. **Brownfield**: if `docs/reverse-sdd/` exists (reverse-sdd skill), those documents are
   the base specs; new work enters as Delta Specs against them.

### Artifact → reference mapping

| Artifact | Read |
|---|---|
| Constitution | `references/07-CONSTITUTION-TEMPLATE.md` |
| PRD | `references/01-PRD-TEMPLATE.md` + `06-AUTHORING-GUIDE.md` §1 + `08-EARS-NOTATION.md` for the criteria |
| API Spec | `references/02-API-SPEC-TEMPLATE.md` + guide §2 |
| Tech Design | `references/03-TECHNICAL-DESIGN-TEMPLATE.md` + guide §3 |
| Data Model | `references/04-DATA-MODEL-TEMPLATE.md` + guide §4 |
| Implementation Plan | `references/05-IMPLEMENTATION-PLAN-TEMPLATE.md` + guide §5 |
| Tasks | `references/09-TASKS-TEMPLATE.md` |
| Delta Spec | `references/10-DELTA-SPEC-TEMPLATE.md` |
| Analyze | `references/11-ANALYZE-CHECKLIST.md` |

## Core principles

1. **Specs as living code**: in the repo, versioned with Git, updated when requirements
   change. `specs/` is the current truth; `changes/` holds active proposals.
2. **Detail proportional to risk** (table above).
3. **Review before code**, with explicit approval gates between artifacts.
4. **Traceability end-to-end**: every MUST requirement has an ID (REQ-NNN); every task
   cites the REQ it implements; every test cites the criterion it verifies. When someone
   asks "why are we building this?", the chain answers.
5. **Specs as AI input**: a clear PRD generates user stories, an API spec generates
   integration tests, EARS criteria generate test cases nearly 1:1, Tasks are directly
   agent-executable. Point CLAUDE.md / AGENTS.md at the constitution so every agent
   session inherits the project principles.

## EARS in one paragraph

Acceptance criteria in the PRD use EARS (Easy Approach to Requirements Syntax): 5
patterns — ubiquitous ("THE SYSTEM SHALL..."), event-driven ("WHEN X, THE SYSTEM
SHALL..."), state-driven ("WHILE X, ..."), optional ("WHERE feature X is enabled,
..."), and unwanted behavior ("IF X, THEN THE SYSTEM SHALL...").
Details, examples, and the EARS↔Gherkin mapping (EARS for requirements, Gherkin for
tests — reverse-sdd generates Gherkin) in `references/08-EARS-NOTATION.md`.

## The Analyze gate

Read-only cross-artifact review before implementation (`11-ANALYZE-CHECKLIST.md`):
coverage (every MUST → task → test), constitution violations, ambiguity (criteria a
test can't verify), terminology drift between documents, orphan tasks. Output: a findings
list with severity; the human decides what to fix before `implement`. Never skip it to
"save time" on complex features — it catches the gaps that become runtime failures.

## Implementing from Tasks

When executing (or handing to an agent): respect dependency order and [P] parallel
markers; **first run: 3-5 tasks, review, adjust, then scale** — never a 30-task list
unattended; each task's Done is verifiable (test passes, endpoint responds); mark
progress in the file itself so any session can resume.

## Anti-patterns

- **Spec as formality** (written after the code) → block PRs without approved spec
- **Eternal spec** → timebox reviews, accept iteration
- **Abandoned spec** → updating it is part of Definition of Done; deltas exist for this
- **Monolithic spec** → split by feature/component
- **Relitigating standards per PR** → missing constitution; write it
- **Skipping Analyze on complex work** → gaps surface as runtime failures
- **Big-bang implement** → 3-5 tasks first
- **EARS theater** → criteria in perfect syntax that no test can verify; every criterion
  must name its observable outcome

## Output format

```
project-root/
├── specs/                      # current truth (spec-anchored)
│   ├── constitution.md
│   ├── prd/feature.md
│   ├── api/feature-api-v1.md
│   ├── technical/feature-architecture.md
│   ├── data-model/feature-schema.md
│   ├── plans/feature-phase-1.md
│   └── tasks/feature-tasks.md
├── changes/                    # active proposals (brownfield)
│   └── 2026-08-my-change/
│       ├── proposal.md
│       ├── delta-spec.md
│       └── tasks.md
├── src/
└── tests/
```

## Cross-spec validation (quick checks)

1. Every PRD requirement covered by the API Spec; every API field in the Data Model.
2. State transitions consistent between API and Tech Design; indexes cover API queries.
3. Plan references all specs; Tasks cover the whole plan; no task without a REQ.
4. Nothing violates the constitution; approved deltas are folded into `specs/`.
5. Financial data: Decimal, never float. Every index tied to a critical query.

## Interop with the ecosystem

Specs written with this skill map directly onto the major tools, so they're portable:

| This skill | GitHub Spec Kit | Kiro |
|---|---|---|
| constitution.md | /speckit.constitution → constitution.md | steering docs |
| PRD (EARS) | /speckit.specify → spec.md | requirements.md |
| Tech Design + Data Model + API | /speckit.plan → plan.md | design.md |
| Tasks | /speckit.tasks → tasks.md | tasks.md |
| Analyze | /speckit.analyze | requirements analysis |
| Delta Spec | (re-specify) | — (OpenSpec pattern) |
