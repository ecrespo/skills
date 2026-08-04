# SDD Template Authoring Guide

## Table of Contents

1. How to fill in the PRD
2. How to fill in the API Spec
3. How to fill in the Technical Design
4. How to fill in the Data Model
5. How to fill in the Implementation Plan
6. Full workflow
7. Using AI to speed up the process

---

## 1. How to fill in the PRD

### When to write a PRD?

Write a PRD when you are going to build something new or make a significant change. You do not need a PRD for bug fixes, refactors, or small internal improvements.

### Tips per section

**Executive Summary:** Write it last. Use: "We will build [what], for [whom], solving [problem], measured by [metric]."

**Context and Problem:** Use concrete data, not opinions. Bad: "The system is bad". Good: "65% of payments are processed manually via call center, with 2,300 monthly calls."

**Target Users:** Three personas at most. If you have more, your scope is too broad.

**Goals and Metrics:** Every goal must be SMART. Bad: "Improve the experience". Good: "Reduce payment time from 8 min to under 2 min at p50, within 3 months post-launch."

**Scope:** The most important section for avoiding scope creep. Be explicit about what is NOT included and why.

**Functional Requirements:** Use "The system MUST..." (mandatory) and "The system SHOULD..." (desirable). Every requirement must be verifiable with a concrete test.

**MoSCoW priority:**
- MUST: Without this, it makes no sense. This is the MVP.
- SHOULD: Important but not blocking.
- COULD: Nice to have if there is time.
- WONT: Excluded from this iteration.

### Common mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Ambiguous requirements | Diverging interpretations | Verifiable criteria |
| No success metrics | Cannot be evaluated | Define numbers upfront |
| Overly broad scope | Never finishes | Aggressive MoSCoW |
| No "Out of Scope" | Scope creep | List exclusions |

---

## 2. How to fill in the API Spec

### When to write an API Spec?

Whenever you build endpoints consumed by another team, service, or frontend.

### Tips per section

**Authentication:** Include how to obtain tokens, their lifetime, and refresh. A dev must be able to authenticate by reading this section alone.

**Conventions:** Define once for the whole API: response format, error format (with domain codes like `PAYMENT_INSUFFICIENT_FUNDS`), and pagination.

**Endpoints:** Each endpoint documents: Method+Path, Description, Required roles, Request (body/params with types and validations), Responses (happy path AND all errors), copy-pasteable cURL example.

**State Diagram:** Mandatory if your resource has a lifecycle. Document each transition, what triggers it, and which role executes it.

### Common mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Not documenting errors | Frontend doesn't know what to handle | Error table per endpoint |
| Fields without clear types | Bugs from type mismatch | Explicit types with validations |
| No rate limiting docs | Aggressive client polling | Document limits and headers |
| No versioning | Breaking changes | Version from day 1 |

---

## 3. How to fill in the Technical Design

### When to write a Technical Design?

When there are non-trivial architectural decisions: new infrastructure, complex integration, pattern changes.

### Tips per section

**Design Decisions (the most valuable section):** For each decision document: Context, Options evaluated (at least 2), Evaluation criteria, Final decision, Consequences and trade-offs.

**Data Flow:** Number the steps. Include the happy path and error flows. This lets someone say in code review "step 4 is not covered by tests".

**Security:** Do not leave it empty. For payments: injection, token hijacking, replay attacks, etc.

### Common mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Documenting only the final decision | Discussions get repeated | Document discarded alternatives |
| Over-designing | Wasted time | Design for current requirements + 1 iteration |
| Ignoring error flows | Production bugs | Document the compensation flow |

---

## 4. How to fill in the Data Model

### When to write a Data Model Spec?

Whenever you create new collections/tables or modify existing schemas.

### Key tips

- **Decimal128 for financial amounts**, never float/double
- **Include `created_at` and `updated_at`** in every collection
- **Soft delete (`deleted_at`)** for data that needs auditing
- **Document enum values** explicitly

### Indexes

Every index must have a justification tied to a real query. How to decide:
1. Identify the most frequent queries
2. Verify there is an index covering each one
3. Verify with `explain()` that it is used
4. Do not create indexes "just in case"

**Order in a compound index:** Equality first, then range, then sort.

```javascript
// Good: equality first
{ user_id: 1, status: 1, created_at: -1 }

// Bad: sort before equality
{ created_at: -1, user_id: 1, status: 1 }
```

### Common mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Float for money | Precision errors | Always Decimal128 |
| Indexes without justification | Slow writes | Tie each to a query |
| No migration plan | Downtime on schema changes | up/down scripts |

---

## 5. How to fill in the Implementation Plan

### When to write an Implementation Plan?

When the implementation takes more than 1 sprint or involves more than 1 person.

### Tips per section

**Phases:** Each phase produces something deployable and verifiable. Recommended structure:
1. Foundation (infra, CI/CD)
2. Core Domain (pure, testable logic)
3. API Layer (expose functionality)
4. Integrations (external services, highest risk)
5. Hardening (security, performance, production)

**Estimates:** Multiply the optimistic estimate by 1.5. If you can't estimate → 2-4 hour technical spike.

| Dev's estimate | Real estimate |
|---|---|
| "1 day" | 1.5-2 days |
| "3 days" | 4-5 days |
| "1 week" | 1.5-2 weeks |
| "I don't know" | Technical spike first |

### Common mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Tasks > 3 days | Hard to track | Break down into 0.5-2 days |
| No dependencies | Blockers | Explicit graph |
| No done criteria | "Are we finished yet?" | Checklist per phase |

---

## 6. Full Workflow

```
Day 1-2:  Write the PRD (PM + Tech Lead)
Day 3:    PRD review with stakeholders
Day 4-5:  Write the API Spec + Data Model (Backend Lead)
Day 6:    API Spec review (Backend + Frontend)
          → Frontend can start with a mock API
Day 7-8:  Write the Technical Design (Tech Lead + Senior Devs)
Day 9:    Technical review of the design
Day 10:   Write the Implementation Plan (Tech Lead)
Day 11:   Plan review + estimate adjustments
Day 12+:  Implementation per the plan
```

### When is it overkill?

| Type of work | Recommended documents |
|---|---|
| Bug fix | None (ticket is enough) |
| Internal refactor | Tech Design lite |
| Simple CRUD + API | API Spec + Data Model |
| Medium feature (1-2 sprints) | PRD + API Spec + Data Model |
| Complex feature (3+ sprints) | All 5 documents |
| New service | All 5 documents |

---

## 7. Using AI to speed up the process

### Generate a PRD draft

```
Act as a Product Manager. Given this context:
- Problem: [describe the problem]
- Users: [describe the users]
- Constraints: [list constraints]

Generate a PRD draft following the Spec-Driven Design template.
```

### Generate an API Spec from the PRD

```
Given this PRD:
[paste the completed PRD]

Generate an API Spec covering all functional requirements FR-001 through FR-00N of the PRD.
```

### Generate tests from the API Spec

```
Given this API Spec:
[paste the API Spec]

Generate integration tests in Python using pytest and httpx that verify:
1. The happy path of each endpoint
2. All documented errors
3. Field validations
4. Valid and invalid state transitions
```

### Generate a Data Model from the Tech Design

```
Given this Technical Design and this API Spec:
[paste both]

Generate a Data Model Spec for MongoDB.
Make sure the indexes cover all queries implied by the API endpoints.
```

### Validate consistency across specs

```
I have these specs for the same feature:
- PRD: [content]
- API Spec: [content]
- Tech Design: [content]
- Data Model: [content]

Identify inconsistencies:
1. Are there PRD requirements not covered by the API Spec?
2. Are there API fields missing from the Data Model?
3. Do the API's state transitions match the Tech Design?
4. Do the Data Model's indexes cover the API's queries?
```

---

## Final Checklist

Before implementing, verify:

- [ ] PRD: MUST requirements with verifiable criteria
- [ ] PRD: Out of Scope defined
- [ ] API Spec: Frontend can integrate without questions
- [ ] API Spec: All errors have codes
- [ ] Tech Design: Decisions with documented alternatives
- [ ] Tech Design: Error flows with compensation
- [ ] Data Model: Indexes tied to queries
- [ ] Data Model: Financial values use Decimal128
- [ ] Plan: Phases with verifiable Done criteria
- [ ] Plan: Dependencies mapped
- [ ] General: Specs in the repository under `/specs`
- [ ] General: Team has reviewed and approved
