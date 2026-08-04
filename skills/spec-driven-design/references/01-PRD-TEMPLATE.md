# [FEATURE/PRODUCT NAME]

## Product Requirements Document (PRD)

| Field | Value |
|---|---|
| **Author** | [Name] |
| **Status** | `DRAFT` / `IN_REVIEW` / `APPROVED` / `DEPRECATED` |
| **Version** | 1.0 |
| **Date** | YYYY-MM-DD |
| **Reviewers** | [Reviewer names] |
| **Last updated** | YYYY-MM-DD |

---

## 1. Executive Summary

<!-- 
  2-3 paragraphs maximum. It must answer:
  - What are we going to build?
  - For whom?
  - What problem does it solve?
  A stakeholder who reads only this section must understand the scope.
-->

[Concise description of the proposed feature or product]

## 2. Context and Problem

### 2.1 Current Situation
[Description of the current state]

### 2.2 Problem
[Description of the problem with evidence]

### 2.3 Opportunity
[Description of the opportunity]

## 3. Target Users

### Persona 1: [Role Name]
- **Description:** [Who they are, what they do]
- **Primary need:** [What they need to accomplish]
- **Usage frequency:** [Daily / Weekly / Monthly / Occasional]
- **Technical level:** [Low / Medium / High]

## 4. Goals and Success Metrics

### 4.1 Business Goals

| Goal | Metric | Target | Timeframe |
|---|---|---|---|
| [Goal] | [Metric] | [Target] | [Timeframe] |

### 4.2 User Goals

| User Goal | Indicator |
|---|---|
| [Goal] | [Indicator] |

## 5. Scope

### 5.1 In Scope (Included)
- [ ] [Capability 1]
- [ ] [Capability 2]

### 5.2 Out of Scope (Excluded)
- [Excluded capability 1 — brief reason]

### 5.3 Future Considerations
- [Future consideration 1]

## 6. Functional Requirements

### FR-001: [Requirement Name]
- **Description:** The system must [specific action]
- **Actor:** [Who initiates the action]
- **Preconditions:** [What must be true beforehand]
- **Main flow:**
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]
- **Alternative flow:** [What happens if something goes differently]
- **Postconditions:** [What is true afterwards]
- **Priority:** `MUST` / `SHOULD` / `COULD` / `WONT`

## 7. Non-Functional Requirements

### Performance
- [E.g.: API response time < 200ms at p95]

### Security
- [E.g.: Authentication via JWT with refresh tokens]

### Availability
- [E.g.: SLA 99.9% uptime]

### Scalability
- [E.g.: Horizontally scalable design for 10x growth]

### Observability
- [E.g.: Structured logs, metrics in Prometheus, distributed tracing]

## 8. Constraints and Dependencies

### Technical Constraints
- [E.g.: Must integrate with existing MongoDB v6.0]

### Business Constraints
- [E.g.: Banking regulation requires X]

### External Dependencies

| Dependency | Type | Owner | Status | Risk |
|---|---|---|---|---|
| [Dependency] | [Type] | [Owner] | [Status] | [Risk] |

## 9. User Stories

### Epic: [Epic Name]

**US-001:** As a [persona], I want [action], so that [benefit].
- Acceptance criteria:
  - [ ] [Verifiable criterion 1]
  - [ ] [Verifiable criterion 2]

## 10. Wireframes / Mockups
- [Link to Figma / image / textual description of the flow]

## 11. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| [Risk] | [P] | [I] | [Mitigation] |

## 12. Estimated Timeline

| Phase | Estimated Duration | Deliverable |
|---|---|---|
| Spec & Design | [X weeks] | Approved specs |
| MVP Implementation | [X weeks] | Working feature |
| Testing & QA | [X weeks] | Release candidate |
| Rollout | [X weeks] | Production |

---

## Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | YYYY-MM-DD | [Name] | Initial version |

## Approvals

| Role | Name | Date | Status |
|---|---|---|---|
| Product Manager | [Name] | | ☐ Pending |
| Tech Lead | [Name] | | ☐ Pending |
| Stakeholder | [Name] | | ☐ Pending |
