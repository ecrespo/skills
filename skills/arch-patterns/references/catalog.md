# Catalog: 19 architecture styles and patterns

**Style** (macro) = shape and deployment of the whole system. **Pattern** (meso) = organisation
inside one unit. They combine. Each entry: what it is · pros · contras · when · avoid ·
associated patterns · anti-patterns · signals you need it. Language: Spanish/English mixed on
purpose so the terms match what users say.

## Quick comparison table

| # | Architecture | Type | Pros | Contras | Use when | Avoid when |
|---|---|---|---|---|---|---|
| 1 | Layered / N-Tier Monolith | Pattern/Style | Simple to build, test, deploy; trivial ACID; one repo | Growing coupling; all-or-nothing deploy/scale; tech lock-in | MVPs, internal CRUD, unknown domain, < 10 devs | Multiple autonomous teams, per-component scaling |
| 2 | Modular Monolith | Style | Monolith benefits + explicit module boundaries; migratable later | Needs discipline/tooling (import-linter); single deploy | **Default in 2026**: known domain, 1-3 teams, want optionality | Real, immediate need for independent scaling/deploy |
| 3 | Client-Server / N-Tier | Style | Clear UI/logic/data split; thin clients; central security | Server = SPOF; connectivity dependence; logic duplication | Web/mobile apps, dashboards (Reflex/React + API) | P2P, extreme offline-first |
| 4 | Microservices | Style | Independent deploy/scale; team autonomy; fault isolation | Distributed complexity: network, sagas, observability, cost | Many teams, mature domain, uneven scaling, high release cadence | Startups, small teams, no DevOps maturity |
| 5 | SOA | Style | Reuse across apps; integrates legacy; formal contracts | ESB bottleneck; heavy governance; fat shared services | Large corporations integrating heterogeneous systems (banks, insurers) | New digital products, agile teams |
| 6 | Event-Driven (EDA) | Style | Temporal/spatial decoupling; absorbs peaks; extensible | Hard to reason/debug; eventual consistency; idempotency mandatory | Async integrations, payments/reconciliation, IoT, reactive systems | Flows needing strong sync consistency; teams new to messaging |
| 7 | Serverless / FaaS | Style | No servers; scale to zero; pay per use; fast TTM | Cold starts; limits; lock-in; cost at constant load | Sporadic loads, webhooks, event ETL, glue code | Constant high volume, long processes, ultra-low latency |
| 8 | Hexagonal (Ports & Adapters) | Pattern | Domain isolated from frameworks/DB/UI; test without infra; swap adapters | More abstractions; over-engineering for pure CRUD | Rich, long-lived, regulated logic; multiple channels | Throwaway prototypes, pure CRUD |
| 9 | Clean / Onion | Pattern | Strict dependency rule; explicit use cases + DTOs; testability | Boilerplate; "layers in disguise" risk; ceremony | Complex enterprise apps, 5-10 year lifespan | Scripts, trivial services, MVPs |
| 10 | CQRS + Event Sourcing | Pattern | Read/write optimised separately; full audit; multiple projections | High complexity; eventual write→read; event versioning; hard to undo | Contended writes + strong audit (payments, policies, trading) | CRUD, simple domains; never by default |
| 11 | Microkernel (Plugins) | Pattern | Stable minimal core; extensible; per-plugin isolation | Plugin contract expensive to change; versioning | IDEs, workflow engines (n8n), rules engines, skills/agents platforms | No third-party extensibility need |
| 12 | Pipes & Filters | Pattern | Small composable stages; parallel per stage; clear data flow | Serialization overhead; no global tx; implicit coupling by formats | ETL, OCR/documents, ML/data pipelines, streaming | Request/response with many branches and shared state |
| 13 | Space-Based | Style | Extreme elasticity; DB no longer bottleneck | Very complex; eventual; memory cost | Massive unpredictable peaks: tickets, auctions, trading | Predictable load, strong consistency |
| 14 | Service-Based | Style | 4-12 coarse services, independent deploy, shared DB | Shared DB = schema coupling | Pragmatic step from monolith; medium teams | When shared DB blocks autonomy |
| 15 | Micro-frontends | Style (front) | Vertical teams end-to-end; independent front deploy | Duplicate deps; UX consistency; composition | Large fronts, several teams/domains | Small front or one team |
| 16 | Peer-to-Peer | Style | No SPOF; scales with nodes | Discovery, NAT, consistency hard | Blockchain, mesh, local-first sync | Mandatory central authority (banking, insurance) |
| 17 | Cell-Based | Style | Bounded blast radius; canary per cell | Cell routing/replication complexity; cost | Hyperscale multi-tenant platforms | Everything else (use bulkheads instead) |
| 18 | Agentic (LLM agents) | Emerging style | Automates non-deterministic tasks; extensible via tools/MCP | Non-determinism; token cost; prompt injection; evals | Assistants, support automation, semantic extraction | Strict determinism/latency |
| 19 | DOMA (Uber) | Style (microservices evolution) | Domains + gateways + layer design + extensions: fewer visible dependencies; migrations behind gateways | Only pays at large scale; gateway/extension governance | Large orgs with hundreds of services in "migration hell" | Small/medium orgs (think domain-oriented, skip gateways) |

Rule of thumb 2026: **start Modular Monolith + Hexagonal**; extract Service-Based/Microservices
only when a module proves it needs independent scaling/deploy; EDA at boundaries; CQRS/ES and
Space-Based only for sub-domains with data to justify them; DOMA when services reach hundreds.

---

## 1. Layered / N-Tier Monolith
- **What**: single deployable, horizontal technical layers Presentation → Service → Domain →
  Persistence. Closed layers talk only to the one below; open layers may skip.
- **Pros**: simplest to understand/test/deploy; ACID trivial; low internal latency; small teams.
- **Contras**: coupling grows ("big ball of mud"); all-or-nothing deploy; vertical scaling; slow
  builds over time; framework lock-in.
- **When**: MVPs, internal CRUD apps, domain not yet understood, < ~10 devs.
- **Avoid**: multiple autonomous teams; per-component scaling; independent release cadence.
- **Anti-patterns**: *architecture sinkhole* (requests pass through layers adding nothing);
  technical layers that hide the domain → cross-cutting coupling.
- **Signals you outgrew it**: build > 10 min, deploy freezes, teams stepping on each other.
- **Python shape**: FastAPI routers → services → repositories; Reflex `rx.State` calls the same
  service in-process.

## 2. Modular Monolith
- **What**: one deployment, code organised in vertical modules by domain (bounded contexts),
  each with public API, own model, own logical persistence. Modules talk only via public API or
  in-process events; boundaries enforced by tooling (import-linter, dependency-cruiser).
- **Pros**: monolith benefits + explicit limits; cheap refactor; ready for strangler-fig
  extraction; majority recommendation of architects 2024-2026.
- **Contras**: needs discipline; one leaky module contaminates all; still one deploy.
- **When**: the default; known domain, 1-3 teams, want future optionality.
- **Avoid**: real, immediate need to scale/deploy a module separately.
- **Anti-patterns**: modules importing each other's internals; shared "utils" that become a
  hidden module; one DB schema without per-module ownership.
- **Signals to extract a module**: it needs different scaling, release cadence, or a separate
  team owns it end-to-end.
- **Python shape**: `proyecto/<modulo>/{api.py, domain.py, repo.py}`, `shared/events.py`
  in-process bus, `.importlinter` contract `type = independence`.

## 3. Client-Server / N-Tier (distributed)
- **What**: physical tiers: client (browser/mobile/desktop), application server, data server.
- **Pros**: clear split; thin clients; central security/backups.
- **Contras**: server SPOF/bottleneck; connectivity dependence; logic duplicated client/server.
- **When**: web/mobile apps, corporate systems, dashboards.
- **Reflex note**: state lives on the server and syncs by WebSocket → thin client with remote
  state; pair with FastAPI as the API tier.

## 4. Microservices
- **What**: small autonomous services, independently deployable, each owning its data, aligned to
  a bounded context; REST/gRPC + events; needs platform (gateway, discovery, observability,
  CI/CD per service).
- **Associated patterns**: API Gateway, Database-per-service, Saga (choreography/orchestration),
  Circuit Breaker, Outbox, Strangler Fig, BFF, Sidecar.
- **Pros**: independent deploy/scale; team autonomy; tech heterogeneity; fault isolation; DDD fit.
- **Contras**: distributed complexity (network, mesh, tracing); eventual consistency; sagas; infra
  cost; latency; hard E2E tests.
- **When**: many teams, mature domain, uneven scaling, high release cadence.
- **Avoid**: startups, small teams, unknown domain, no DevOps maturity.
- **Anti-patterns**: *distributed monolith* (shared DB, coordinated deploys); *nano-services*;
  sharing a database; synchronous call chains > 3 deep.
- **Python shape**: services as FastAPI apps; Redis Streams/RabbitMQ for choreographed sagas;
  idempotent consumers; circuit breaker on outbound calls.

## 5. SOA (Service-Oriented Architecture)
- **What**: coarse reusable business services with formal contracts (WSDL/OpenAPI) integrated by
  an ESB (routing, transformation, orchestration).
- **Pros**: reuse across applications; integrates legacy; central governance.
- **Contras**: ESB bottleneck/coupling point; fat shared services; canonical model rigidity.
- **vs Microservices**: reuse vs autonomy; smart pipes vs smart endpoints; shared DB vs own DB.
- **When**: large corporations with heterogeneous legacy (banks, insurers, government).
- **Anti-pattern**: *ESB as monolith* — business logic migrates into the bus.
- **Python shape**: FastAPI "integration service" translating sources into a canonical Pydantic
  model.

## 6. Event-Driven Architecture (EDA)
- **What**: components produce/consume immutable events via a broker. Topologies: **Broker**
  (choreography) and **Mediator** (orchestration). Event kinds: notification, event-carried
  state transfer, event sourcing.
- **Golden rules**: idempotent consumers, outbox pattern, dead-letter queues, versioned schemas
  (CloudEvents/JSON Schema/Avro), explicit ownership per event.
- **Pros**: temporal/spatial decoupling; elasticity; extensibility; resilience to peaks; audit.
- **Contras**: non-linear flow hard to debug; eventual consistency; ordering/duplicates; complex
  tests.
- **When**: async integrations, notifications, payments/reconciliation, IoT, reactive systems.
- **Avoid**: flows needing strong synchronous consistency; teams without messaging experience.
- **Anti-pattern**: *event spaghetti* (chains without contracts/ownership); events as RPC.
- **Python shape**: aio-pika topic exchange + durable queue + DLQ; `if ya_procesado(ev.id)`.

## 7. Serverless / FaaS
- **What**: ephemeral functions triggered by events (HTTP, queues, cron, storage), plus managed
  BaaS. Design stateless, idempotent, fast start, with timeouts.
- **Pros**: no server management; scale to zero/millions; pay per use; fast time-to-market.
- **Contras**: cold starts; time/memory limits; vendor lock-in; local testing; unpredictable
  cost at constant load; external state mandatory.
- **When**: sporadic/irregular loads, webhooks, event ETL, glue code, prototypes.
- **Avoid**: constant high volume, long processes, ultra-low latency, in-memory state.
- **Python shape**: FastAPI + Mangum on Lambda; pure `handler(event, context)` for storage
  events; `serverless.yml`.

## 8. Hexagonal (Ports & Adapters)
- **What** (Cockburn 2005): domain at the centre defines **ports** — primary/driving (how the
  world calls the app) and secondary/driven (what the app needs: persistence, messaging, external
  APIs). **Adapters** implement ports (FastAPI, CLI, Reflex, Mongo, RabbitMQ). Dependencies point
  inward.
- **Pros**: domain free of frameworks/DB/UI; millisecond tests with in-memory adapters; swap
  Mongo→Postgres or REST→gRPC by writing an adapter; longevity.
- **Contras**: more files/abstractions; learning curve; over-engineering for pure CRUD.
- **When**: rich long-lived business logic; regulated systems (health, insurance, finance);
  multiple channels.
- **Avoid**: throwaway prototypes, CRUD without rules.
- **Anti-pattern**: *anemic hexagon* — ports mirroring the ORM 1:1, domain without rules.
- **Python shape**: `core/{domain.py, ports.py (Protocol), use_cases.py}`; `adapters/{api,
  ui, persistence, messaging}`; composition root in `main.py`; in-memory repo for tests.

## 9. Clean / Onion Architecture
- **What** (Martin / Palermo): concentric circles Entities → Use Cases → Interface Adapters →
  Frameworks & Drivers; **dependency rule**: only inward. Generalises Hexagonal with explicit use
  cases, input/output DTOs and presenters.
- **Pros**: strict verifiable dependency rule; explicit use cases; independence from UI/DB/
  frameworks.
- **Contras**: boilerplate (DTOs, mappers, interfaces); risk of "layers in disguise"; ceremony.
- **When**: complex enterprise apps, rich domains, 5-10 year maintenance horizon.
- **Python note**: dataclasses in domain, Pydantic only in adapters; relax where the domain is
  small.
- **Python shape**: `src/{domain, application(ports, dto, use_cases), interface_adapters
  (controllers, presenters, repositories), infrastructure(web, db, di)}`.

## 10. CQRS + Event Sourcing
- **What**: CQRS separates write model (commands, invariants) from read model (projections);
  Event Sourcing stores the event sequence instead of state, rebuilding by replay (+ snapshots).
  CQRS **without** ES is cheap and common.
- **Pros**: read/write optimised and scaled separately; full audit/history; time-travel; new
  projections from the past.
- **Contras**: high complexity; eventual consistency write→read; event versioning; snapshots;
  hard to un-adopt.
- **When**: collaborative domains with write contention and strong audit (payments, policies,
  accounts, trading), analytics on history.
- **Avoid**: CRUD, simple domains, inexperienced teams; never by default.
- **Anti-pattern**: *CQRS/ES by fashion*.
- **Python shape**: aggregate with `decide/apply`, append-only store with unique (stream,
  version) index, projectors → read models, `/commands/*` and `/queries/*` endpoints.

## 11. Microkernel (Plugin Architecture)
- **What**: minimal core + extension contract; plugins discovered at start/runtime (entry_points,
  pluggy, decorators). In-process or isolated (subprocess, container, WASM) by trust level.
- **Pros**: stable minimal core; third-party extensibility; per-plugin isolation.
- **Contras**: contract hard/expensive to change; plugin versioning; kernel bottleneck.
- **When**: IDEs, browsers, workflow engines (n8n), rules engines, skills/MCP/agent platforms,
  per-customer variants.
- **Python shape**: `Protocol` contract + `importlib.metadata.entry_points(group=...)` registry +
  FastAPI exposing `kernel.run()`.

## 12. Pipes & Filters (Pipeline)
- **What**: independent transformation stages (filters) connected by channels (pipes); each stage
  knows only its I/O contract. Python: chained generators, asyncio, Beam, Prefect/Dagster, n8n.
- **Pros**: small composable reusable stages; parallel per stage; clear flow; isolated tests.
- **Contras**: serialisation overhead; no global transactions; implicit coupling by intermediate
  formats → define data contracts (dataclasses/Pydantic).
- **When**: ETL, OCR/document processing, ML/data pipelines, compilers, streaming.
- **Avoid**: request/response with many conditional branches and shared state.
- **Python shape**: `Iterable[In] -> Iterable[Out]` filters composed functionally; async
  generators + `StreamingResponse` in FastAPI.

## 13. Space-Based (Tuple Space / In-Memory Data Grid)
- **What**: state in replicated memory across elastic Processing Units; DB written asynchronously
  (write-behind); virtualised middleware (messaging grid, data grid, processing grid, deployment
  manager), data pumps/readers/writers.
- **Pros**: extreme elasticity; DB no longer bottleneck; minimal latency.
- **Contras**: very complex; eventual consistency; memory cost; hard to test.
- **When**: massive unpredictable peaks (tickets, auctions, trading, betting).
- **Avoid**: predictable load, strong consistency; almost never outside hyperscale.
- **Python shape**: FastAPI PU + Redis/KeyDB grid (`hsetnx` atomic) + stream to data writer.

## 14. Service-Based
- **What** (Richards): 4-12 coarse domain services, independently deployable, usually shared or
  partitioned DB and one UI. Middle ground before microservices; ideal strangler-fig stage.
- **Pros**: independent deploy without database-per-service; less complexity.
- **Contras**: shared DB = schema coupling; less granularity.
- **Mitigations**: table/collection ownership per service; additive schema changes; versioned
  shared access library.
- **When**: medium teams wanting independent deploy without paying full microservices price.
- **Python shape**: `OWNERSHIP` map + `assert_owner(service, collection, write=True)`.

## 15. Micro-frontends
- **What**: UI composed of independently built/deployed fragments per domain/team; composition
  at build, server or client (Module Federation, iframes, web components, by route).
- **Pros**: vertical teams end-to-end; independent front deploy; per-module tech.
- **Contras**: duplicated dependencies; UX consistency (design system); routing/state
  composition; performance.
- **When**: large fronts with several teams/domains. **Avoid**: one team / small app.
- **Reflex shape**: one Reflex app per prefix behind nginx `location /polizas → mf-polizas`;
  shell app for navigation.

## 16. Peer-to-Peer
- **What**: every node is client and server; discovery (bootstrap/DHT), gossip/consensus, churn.
- **Pros**: no SPOF; scales with nodes; censorship resistance; local-first (CRDTs).
- **Contras**: discovery, NAT traversal, security, consistency; variable latency.
- **When**: blockchain, file sharing, mesh, local-first sync. **Avoid**: mandatory central
  authority (banking, insurance).
- **Python shape**: asyncio node with gossip and seen-set.

## 17. Cell-Based
- **What**: whole system replicated in self-contained cells (services + data + capacity); cell
  router assigns tenants; control plane provisions/migrates; canary by cell.
- **Pros**: bounded blast radius; scale/canary per cell; tenant/region isolation.
- **Contras**: routing/replication complexity; cost; only hyperscale (AWS, Slack).
- **Small-scale equivalent**: bulkheads (isolated pools/queues per client).
- **Python shape**: FastAPI cell router by tenant hash + pinned tenants.

## 18. Agentic (LLM agents + tools/MCP)
- **What**: LLM agents plan/execute tasks by invoking tools under an orchestrator (state graph,
  e.g. LangGraph). Combines Microkernel (tools as plugins), EDA (event-triggered agents), Pipes &
  Filters (processing chains).
- **Principles**: isolate prompts/policies/state from model and tool providers (Hexagonal); tool
  contracts (Microkernel); design for non-determinism (retries, schema-validated outputs); least
  privilege, prompt-injection defence; traces and evals.
- **When**: assistants, support automation, semantic extraction, internal copilots.
- **Avoid**: strict determinism or latency.
- **Python shape**: LangGraph `StateGraph` router → specialised agents with `bind_tools`, FastAPI
  endpoint calling `graph.ainvoke`.

## 19. DOMA — Domain-Oriented Microservice Architecture (Uber, 2020)
- **What**: treat a microservice architecture as one large distributed application and organise
  it: **domains** (collections of related services), **layer design** (Infrastructure → Business
  → Product → Presentation → Edge; depend only downward; blast radius shrinks upward),
  **gateways** (single entry point per domain hiding internal services/tables/ETLs), and
  **extensions** (logic extensions = provider/plugin per endpoint; data extensions = typed
  free payload the platform carries without interpreting). Uber: ~2,200 services → ~70 domains;
  service half-life 1.5 years; onboarding -25/50 %.
- **Pros**: fewer visible dependencies; migrations/rewrites behind gateways; platforms free of
  product logic; dependency management at scale.
- **Contras**: only pays at large scale; gateway can become an organisational bottleneck;
  layers and extension contracts are costly/political; needs dependency tooling; without
  discipline → "networked monolith".
- **When**: large orgs already on microservices suffering deep call chains and migration hell.
  Medium orgs: think domain-oriented (a domain may be one service) and keep hierarchy, without
  gateways yet. Startups: postpone microservices altogether (Uber's own advice).
- **Relations**: microservices + hierarchy + facades; not SOA (no central bus, gateway owned by
  the domain); extensions = Microkernel applied to platforms; compatible with Cell-Based and
  Service-Based.
- **Python shape**: FastAPI domain gateway aggregating internal services; `assert_can_call`
  layer rule; `@logic_extension` registry; `ext: DataExt` field; import-linter `type = layers`.

---

## Anti-patterns (cross-cutting) with mitigations

| Anti-pattern | Symptom | Mitigation |
|---|---|---|
| Distributed monolith | Microservices with shared DB and coordinated deploys | Database-per-service or Service-Based with ownership; contracts; independent pipelines |
| Architecture sinkhole | Layers that only delegate | Collapse layers or move to modules by domain |
| Nano-services | Network chatter dominates | Merge by bounded context; Service-Based granularity |
| Event spaghetti | Event chains without contracts/ownership | Event catalog, schemas, one owner per event, mediator for critical flows |
| ESB as monolith | Business logic in the bus | Smart endpoints, dumb pipes; per-domain gateways (DOMA) |
| CQRS/ES by fashion | Complexity without audit/contention need | CQRS without ES; plain repository |
| Anemic hexagon | Ports mirror ORM, no rules in domain | Move invariants into entities; ports named after use cases |
| Big-bang rewrite | Replace everything at once | Strangler fig behind a gateway/facade |
| Networked monolith (DOMA) | Domains that must deploy together | Gateways + layer rules + extension points instead of cross-domain edits |
