# Template: 01-EVALUATION-REPORT.md

Rules: every weakness carries evidence tags (`[METRIC:]` / `[VERIFY:]` / `[COMMITS:]`);
P1 requires deterministic evidence; strengths are mandatory; dismissed findings go at
the end.

---

# Architecture evaluation — {system name}

> Reference commit: `{HEAD hash}` · Date: {date}
> Evidence: `analysis/dep_graph.json`, `analysis/arch_signals.json`
> Scope: {what was analyzed and what was not}

## Executive summary

5-10 lines: overall verdict, the 3 weaknesses that matter most, and the underlying
recommendation (evolve in place / rebuild / hybrid). No script jargon: this is read
by someone who decides budget.

## Attribute scorecard

| Attribute | Verdict | Key evidence |
|---|---|---|
| Coupling and boundaries | 🟢/🟡/🔴/— | |
| Cohesion and responsibility | | |
| Testability | | |
| Resilience and integrations | | |
| Data and consistency | | |
| Observability | | |
| Security | | |
| Evolvability and deployment | | |

## Strengths

3-6 points with the same evidence as the weaknesses. What any refactor or v2 must
**preserve**.

## Weaknesses (ranked)

| ID | Severity | Weakness | Attribute | Affected modules (fan-in) | Evidence | Proposal |
|---|---|---|---|---|---|---|
| WEAK-01 | P1 | | | | `[METRIC:]` | ADR-001 |

### WEAK-{NN}: {title}

- **What happens**: concrete description, with the numbers from the analysis
- **Evidence**: full tags (metric + verification in code + commits if applicable)
- **Why it matters**: degraded attribute + blast radius (fan-in of the modules)
- **What happens if nothing is done**: honest projection, no catastrophizing
- **Proposal**: link to the ADR, or "accepted risk: {reason}"

*(repeat per weakness; 5-12 is the useful range)*

## Dismissed findings

False positives from the scripts with their reason (barrel files, type-only imports,
generated code...). This keeps the next audit from re-litigating the same items.

## Areas not evaluated

What was left out and why (no runtime access, language not covered by the graph,
module excluded from scope).
