# Decision guide

## §1 Decision inputs (collect before recommending)

| Dimension | Questions to answer | Why it matters |
|---|---|---|
| Organisation | How many teams? Do they release independently? DevOps/observability maturity? On-call capacity? | Conway's law: architecture mirrors communication; distributed styles need platform maturity |
| Domain | How complex are the rules? Are bounded contexts clear? Regulatory/audit requirements? Expected lifespan? | Rich/regulated domains justify Hexagonal/Clean; audit justifies ES; unclear contexts forbid microservices |
| Scalability | Predictable or spiky load? Do parts scale asymmetrically? Cost per request sensitivity? | Asymmetric scaling justifies extraction; spikes justify EDA/Serverless/Space-Based |
| Consistency | Where is ACID mandatory? Where is eventual acceptable? Need for history? | Determines EDA/CQRS/ES viability |
| Evolution | Change rate? Third-party extensibility? Multiple products on one platform? | Microkernel/DOMA extensions; Modular Monolith for optionality |
| Operations | Blast-radius tolerance? Multi-tenant isolation? Infra budget? | Cell-Based/bulkheads; cost of microservices vs monolith |

If an input is unknown, state the assumption explicitly in the ADR and name the trigger that
would flip the decision. Prefer one compact multi-part question over several rounds.

## §2 Quality-attribute matrix (★ low … ★★★★★ high; n/a = pattern does not decide it)

| Attribute | Monolith | Modular Monolith | Microservices | DOMA | EDA | Serverless | Hexagonal/Clean | CQRS+ES | Space-Based |
|---|---|---|---|---|---|---|---|---|---|
| Simplicity | ★★★★★ | ★★★★ | ★ | ★★ | ★★ | ★★★ | ★★★ | ★ | ★ |
| Testability | ★★★★ | ★★★★ | ★★ | ★★ | ★★ | ★★ | ★★★★★ | ★★★ | ★ |
| Independent deploy | ★ | ★ | ★★★★★ | ★★★★★ | ★★★★ | ★★★★★ | n/a | n/a | ★★★ |
| Scalability | ★★ | ★★ | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | n/a | ★★★★ | ★★★★★ |
| Strong consistency | ★★★★★ | ★★★★★ | ★★ | ★★ | ★ | ★★ | n/a | ★★ | ★ |
| Evolvability | ★★ | ★★★★ | ★★★★ | ★★★★★ | ★★★★★ | ★★★ | ★★★★★ | ★★★ | ★★ |
| Operational cost (↑ = cheaper) | ★★★★★ | ★★★★★ | ★ | ★ | ★★ | ★★★★ (low use) | n/a | ★★ | ★ |
| Fault tolerance | ★ | ★ | ★★★★ | ★★★★ | ★★★★★ | ★★★★ | n/a | ★★★ | ★★★★★ |

Reading DOMA: same fundamentals as microservices, +1 evolvability (gateways, extensions), +1
perceived simplicity for consumers, highest governance cost in the table.

Show only the rows that discriminate between the finalists for the user's case.

## §3 Decision tree

```
How many teams work on the system?
├─ 1-2 → Complex domain / long lifespan?
│        ├─ No  → Layered monolith
│        └─ Yes → Modular monolith + Hexagonal/Clean   <- default base 2026
└─ 3+  → DevOps and observability maturity?
         ├─ Low  → Service-Based
         └─ High → Microservices
                   └─ Hundreds of services, deep chains, migration hell? -> DOMA

Then, on top of any base:
  Async integrations or traffic peaks?             -> + Event-Driven (idempotency, outbox, DLQ)
  Strong audit / high write contention?            -> + CQRS (+- Event Sourcing) in that sub-domain only
  Sporadic or irregular workloads?                 -> + Serverless for those workloads
  Third-party extensibility / product variants?    -> Microkernel (plugins) in that component
  Staged data/document flow?                       -> Pipes & Filters in that component
  Several frontend teams?                          -> Micro-frontends
  Multi-tenant hyperscale, blast radius?           -> Cell-Based (otherwise: bulkheads)
  Non-deterministic semantic tasks?                -> Agentic (with Hexagonal around the LLM)
If the answer is No: do not add it yet.
```

Interior pattern per unit (module or service):
- Rich rules, regulated, multiple channels → **Hexagonal**; add Clean's explicit use cases/DTOs
  when the team is large or the horizon is long.
- CRUD without rules → plain Layered inside the module.
- Audit + contention → **CQRS**, ES only if history/replay is a stated requirement.
- Extensibility → **Microkernel**. Data/document flow → **Pipes & Filters**.

## §4 How styles combine (reference system)

Frontend (Micro-frontends / Reflex apps) → API Gateway/BFF → Services (Service-Based →
Microservices → DOMA domains): Underwriting (Hexagonal + Clean), Billing (Hexagonal + CQRS/ES),
Documents (Pipes & Filters + Microkernel) <-> Event Bus (EDA) → Serverless functions
(notifications, ETL), LLM agents (support, extraction), OCR pipeline workers.

Reading: the macro style fixes boundaries, data ownership and communication; meso patterns fix
the inside of each unit; Serverless/agents cover irregular and semantic loads, always triggered
by bus events. None of this requires starting distributed: the same modules live first in a
modular monolith.

## §5 Advice by organisation size (Uber's DOMA post + Richards/Ford)

- **Startup / 1-2 teams**: postpone microservices; modular monolith; the first modules will be
  the longest-lived, so name them after the core business.
- **Mid-size / several teams**: hierarchy between services matters; platform vs product logic;
  domain-oriented thinking even if one service per domain; consider extension points to keep
  platforms product-agnostic; Service-Based as the pragmatic step.
- **Large / hundreds of engineers and services**: DOMA (domains, gateways, layers, extensions);
  migrations behind gateways ("trim the hedge", never rewrite everything).

## §6 Anti-pattern checklist to run on every recommendation

For the chosen base and complements, list the anti-patterns from `catalog.md` §Anti-patterns
that apply and write the mitigation next to each. Minimum set:
- Microservices/Service-Based → distributed monolith, nano-services, shared DB without ownership.
- EDA → event spaghetti, missing idempotency/outbox/DLQ, events used as RPC.
- CQRS/ES → adopted by fashion, no versioning strategy, UI not designed for eventual reads.
- Hexagonal/Clean → anemic domain, ports mirroring ORM, ceremony without rules.
- DOMA → networked monolith, gateway team bottleneck, extension contract churn.
- Any migration → big-bang rewrite instead of strangler fig.
