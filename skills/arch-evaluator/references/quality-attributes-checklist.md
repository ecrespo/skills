# Quality-attribute checklist

Evaluate each attribute with a **green / amber / red / not evaluated** verdict and 1-3
lines of evidence with tags. Weight by the nature of the system (a payments integration
lives or dies by resilience+data; an internal CLI doesn't).

Verdict guide: **green** = practice present and consistent; **amber** = present but
inconsistent or with significant exceptions; **red** = absent or contradicted by
deterministic evidence (cycle, hotspot, co-change pair, historical bug).

---

## 1. Coupling and boundaries

- Cycles in `dep_graph.json`? (`cycles_scc`, `cycles_pairs`) → straight red if they
  cross layers or domains.
- Cross-module co-change pairs in `arch_signals.json`? Every cross-module pair with
  confidence ≥0.5 is a fictitious boundary `[METRIC:]`.
- God modules confirmed in Phase 1? (high fan-in AND fan-out AND LOC).
- Do dependencies flow in one coherent direction (api→domain→infra) or are there
  infrastructure imports inside the domain? `[VERIFY:]`
- Is there any rule that *enforces* the boundaries (import-linter, dependency-cruiser,
  eslint boundaries)? Without a rule, the boundary is just a convention.

## 2. Cohesion and responsibility

- Does each module have one reason to change? Inverse signal: modules that show up in
  clusters of unrelated features in the history.
- Files >500 LOC in hotspots: do they mix responsibilities or are they legitimately
  deep? (A deep module with a small interface is good — don't split by size.)
- Pass-through layers? (repositories/services that only delegate — "deletion test": if
  you delete it and wire the two ends together, is anything lost?)

## 3. Testability

- Are dependencies injected or instantiated inside? (new/concrete constructors in
  business logic = sealed seam) `[VERIFY:]`
- Do the test directories cover the high fan-in modules? A central module without
  tests is compounded risk `[METRIC: fan_in]` + `[VERIFY: absence]`.
- Are tests coupled to implementation (mocks of everything) or to behavior?
- Do the hotspots with recurring fixes have a regression test per fix? If not, the
  bugs will come back.

## 4. Resilience and integrations

- For each external integration: explicit timeout, retries with backoff, and what
  happens when the third party goes down? `[VERIFY:]` No timeout = red.
- Idempotency in operations involving money or external effects? (idempotency keys,
  deduplication) — cross-reference with historical duplicate bugs `[COMMITS:]`.
- Circuit breaker / bulkhead where a slow dependency can take down the service?
- Queues/events with poison-message handling and a DLQ?

## 5. Data and consistency

- Transactions wherever there are multi-document/multi-table invariants? Or are race
  conditions possible? — historical "race condition"/"duplicate" fixes are P1
  evidence `[COMMITS:]`.
- Schema migrations versioned and reproducible?
- Money in Decimal (never float)? Explicit time zones?
- Indexes aligned with the critical queries, or full scans on hot paths?

## 6. Observability

- Structured logging with a correlation ID that traverses the main flows?
- Can you answer "what happened to request X?" from logs/traces alone? `[VERIFY:]`
- Business metrics in addition to technical ones? Actionable alerts?
- Inverse signal: historical bugs that took multiple fixes suggest blind
  diagnosis `[COMMITS:]`.

## 7. Security

- AuthN/AuthZ centralized (middleware/guards) or repeated ad-hoc per endpoint?
- Secrets out of the code (env/vault) — and out of the git history?
- Input validation at the edge (Pydantic/class-validator schemas) consistent?
- Dependencies with known CVEs? (if there is a lockfile, point to a tool to check it;
  don't invent CVEs).

## 8. Evolvability and deployment

- CI with real gates (lint, tests, scan) or decorative?
- Per-environment config without touching code? Feature flags where there is gradual
  rollout?
- Bus factor?: central modules with one author ≥90% `[METRIC: bus_factor]` are an
  organizational risk, not just a technical one.
- How much does the typical feature cost to add? (one new module or touching 6? — use
  the co-change clusters as a proxy).
