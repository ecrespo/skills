# ADR-NNNN: <Short title of the decision>

- **Status**: Proposed | Accepted | Superseded by ADR-XXXX
- **Date**: YYYY-MM-DD
- **Deciders**: <names / roles>
- **System / scope**: <system, module or sub-domain affected>

## Context
<Which problem is being solved. Decision inputs with evidence:>
- Organisation: <number of teams, release cadence, DevOps/observability maturity>
- Domain: <complexity, bounded contexts, regulation/audit, expected lifespan>
- Scalability: <peaks, asymmetric scaling, cost per request>
- Consistency: <ACID vs eventual per flow; history requirements>
- Evolution: <change rate, extensibility, multiple products>
- Operations: <blast radius, multi-tenancy, infra budget>
- Explicit assumptions: <what could not be verified>

## Decision
**Base**: <macro style> - **Interior per unit**: <pattern> - **Complements**: <EDA / Serverless / CQRS...>

Diagram:
```mermaid
<paste from references/diagrams.md, adapted>
```

Boundary rules that will be enforced (linters / CI): <import-linter contract, ownership, layer rules>

## Alternatives considered
| Alternative | Attributes in favour | Attributes against | Why not |
|---|---|---|---|
| <A> | | | |
| <B> | | | |

## Consequences
- Positive: <...>
- Negative / accepted costs: <...>
- Anti-patterns to watch and their mitigation: <list>

## Adoption / migration plan
1. <incremental step (strangler fig, gateway first, extraction of module X...)>
2. <...>
- Success metrics: <lead time, MTTR, p95 latency, touchpoints per feature...>

## Revisit when
<trigger that would invalidate the decision: 3+ teams, > N services, X peaks, audit requirement...>
