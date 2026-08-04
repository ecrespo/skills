# [PROJECT/FEATURE NAME] — Implementation Plan

## Metadata

| Field | Value |
|---|---|
| **Author** | [Name] |
| **Status** | `DRAFT` / `IN_REVIEW` / `APPROVED` / `IN_PROGRESS` / `COMPLETED` |
| **Version** | 1.0 |
| **Date** | YYYY-MM-DD |
| **PRD** | [Link to the PRD] |
| **Tech Design** | [Link to the Tech Design] |
| **Data Model** | [Link to the Data Model] |
| **API Spec** | [Link to the API Spec] |

---

## 1. Implementation Summary

[Paragraph describing the strategy: how many phases, general approach, total estimated duration.]

**Total estimated duration:** [X weeks/sprints]
**Required team:** [X backend, X frontend, X QA]
**Target production date:** [YYYY-MM-DD]

## 2. Prerequisites

| Prerequisite | Owner | Status | Due Date |
|---|---|---|---|
| [E.g.: Approved specs] | Tech Lead | ☐ Pending | YYYY-MM-DD |
| [E.g.: Access to external API] | DevOps | ☐ Pending | YYYY-MM-DD |
| [E.g.: Staging environment] | DevOps | ☐ Pending | YYYY-MM-DD |

## 3. Implementation Phases

---

### Phase 1: Foundation & Infrastructure

**Duration:** [X days/sprints]
**Goal:** Establish the technical foundation.

#### Tasks

| ID | Task | Assignee | Estimate | Dependency | Status |
|---|---|---|---|---|---|
| F1-01 | Create project structure and scaffolding | [Name] | 2d | — | ☐ |
| F1-02 | Configure CI/CD pipeline | [Name] | 1d | F1-01 | ☐ |
| F1-03 | Database setup + migrations | [Name] | 2d | F1-01 | ☐ |
| F1-04 | Health checks and configuration | [Name] | 1d | F1-01 | ☐ |
| F1-05 | Base logging and metrics | [Name] | 1d | F1-04 | ☐ |
| F1-06 | Testing framework setup | [Name] | 1d | F1-01 | ☐ |

#### "Done" Criteria
- CI pipeline green with tests passing
- Successful deploy to staging
- Metrics and logs visible in dashboard

---

### Phase 2: Core Domain Logic

**Duration:** [X days/sprints]
**Goal:** Implement business logic without external integrations.

#### Tasks

| ID | Task | Assignee | Estimate | Dependency | Status |
|---|---|---|---|---|---|
| F2-01 | Domain models + validations | [Name] | 2d | F1-03 | ☐ |
| F2-02 | Repositories (base CRUD) | [Name] | 2d | F2-01 | ☐ |
| F2-03 | Service layer + business rules | [Name] | 3d | F2-02 | ☐ |
| F2-04 | State machine | [Name] | 2d | F2-03 | ☐ |
| F2-05 | Unit tests for domain and services | [Name] | 2d | F2-04 | ☐ |
| F2-06 | Integration tests against real DB | [Name] | 2d | F2-05 | ☐ |

#### "Done" Criteria
- All MUST requirements covered
- Unit and integration tests passing
- Code review approved

---

### Phase 3: API Layer

**Duration:** [X days/sprints]
**Goal:** Expose functionality as a REST API per the API Spec.

#### Tasks

| ID | Task | Assignee | Estimate | Dependency | Status |
|---|---|---|---|---|---|
| F3-01 | CRUD endpoints | [Name] | 2d | F2-03 | ☐ |
| F3-02 | Authentication and authorization | [Name] | 2d | F3-01 | ☐ |
| F3-03 | Pagination, filters, and search | [Name] | 1d | F3-01 | ☐ |
| F3-04 | Actions endpoint (state changes) | [Name] | 2d | F2-04, F3-01 | ☐ |
| F3-05 | Rate limiting | [Name] | 1d | F3-02 | ☐ |
| F3-06 | Global error handling | [Name] | 1d | F3-01 | ☐ |
| F3-07 | API E2E tests | [Name] | 2d | F3-06 | ☐ |
| F3-08 | OpenAPI documentation | [Name] | 1d | F3-07 | ☐ |

#### "Done" Criteria
- API Spec 100% fulfilled
- Swagger/OpenAPI docs accessible

---

### Phase 4: External Integrations

**Duration:** [X days/sprints]
**Goal:** Connect to external services.

#### Tasks

| ID | Task | Assignee | Estimate | Dependency | Status |
|---|---|---|---|---|---|
| F4-01 | External service client | [Name] | 3d | F3-04 | ☐ |
| F4-02 | Circuit breaker + retry logic | [Name] | 2d | F4-01 | ☐ |
| F4-03 | Event publisher to queue | [Name] | 1d | F3-04 | ☐ |
| F4-04 | Queue worker/consumer | [Name] | 2d | F4-03 | ☐ |
| F4-05 | Notification webhooks | [Name] | 2d | F4-04 | ☐ |
| F4-06 | Integration tests with mocks | [Name] | 2d | F4-05 | ☐ |

#### "Done" Criteria
- End-to-end integration working in staging
- Retry logic tested with simulated failures

---

### Phase 5: Hardening & Production Readiness

**Duration:** [X days/sprints]
**Goal:** Prepare for production.

#### Tasks

| ID | Task | Assignee | Estimate | Dependency | Status |
|---|---|---|---|---|---|
| F5-01 | Security audit | [Name] | 2d | F4-05 | ☐ |
| F5-02 | Load testing | [Name] | 2d | F4-05 | ☐ |
| F5-03 | Production alerts | [Name] | 1d | F4-05 | ☐ |
| F5-04 | Operational runbooks | [Name] | 1d | F5-03 | ☐ |
| F5-05 | UAT with stakeholders | [Name] | 3d | F5-02 | ☐ |
| F5-06 | Final documentation | [Name] | 1d | F5-05 | ☐ |

#### "Done" Criteria
- Load test meets performance targets
- No critical/high vulnerabilities
- Stakeholders sign off on UAT

---

## 4. Dependency Map

```
Phase 1: Foundation
  │
  ├──▶ Phase 2: Core Domain ──▶ Phase 3: API Layer ──▶ Phase 4: Integrations
  │                                                         │
  │                                                         ▼
  │                                                   Phase 5: Hardening
  │
  └──▶ [Frontend can start with a mock API from Phase 1]
```

## 5. Implementation Risks

| Risk | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Delayed access to external API | Medium | High | Start with mocks | DevOps |
| Requirement changes mid-sprint | Medium | Medium | Approved spec as gate | PM |
| Edge-case complexity | High | High | Technical spike, pair programming | Backend Lead |

## 6. Communication and Tracking

### Ceremonies

| Ceremony | Frequency | Participants | Purpose |
|---|---|---|---|
| Daily standup | Daily | Dev team | Progress and blockers |
| Sprint review | End of each phase | Team + PM | Deliverables demo |
| Retrospective | End of each phase | Team | Continuous improvement |

### Progress Reports

Weekly report every Friday with: completed tasks, planned tasks, active blockers, estimate changes.

## 7. Definition of Done (Global)

- [ ] Code implemented and merged to main
- [ ] Tests passing (unit + integration + e2e)
- [ ] Code review approved by at least 1 peer
- [ ] Documentation updated (API docs, README)
- [ ] Deployed to staging and verified
- [ ] Metrics and alerts configured
- [ ] Spec updated if anything changed during implementation
- [ ] No known technical debt without a corresponding ticket

---

## Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | YYYY-MM-DD | [Name] | Initial version |
