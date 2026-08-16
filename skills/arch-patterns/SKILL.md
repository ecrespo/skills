---
name: arch-patterns
description: >
  Catalog, decision guide and implementation kit for 19 software architectures (Layered,
  Modular Monolith, Client-Server, Microservices, DOMA, SOA, Event-Driven, Serverless,
  Hexagonal, Clean, CQRS+Event Sourcing, Microkernel, Pipes & Filters, Space-Based,
  Service-Based, Micro-frontends, P2P, Cell-Based, Agentic). Recommends base style +
  interior pattern + complements via decision tree and quality matrix, explains pros/contras
  and anti-patterns, draws Mermaid diagrams, writes ADRs, scaffolds Python/FastAPI/Reflex
  skeletons and checks layer/module boundaries. Use whenever the user asks which architecture
  to use or which one suits their system, "monolith or microservices", "design the architecture
  of X", "hexagonal vs clean", "explain CQRS/DOMA/EDA", wants a comparison table or
  diagram, needs an ADR, wants a FastAPI project laid out as hexagonal/clean/modular/CQRS, or
  asks to verify a repo respects its layers — even for just one part.
---

# Arch-Patterns: choose, explain, diagram and scaffold software architectures

Turn an architecture question into a decision a tech lead can defend: **which style for the
system, which pattern inside each unit, which complements at the boundaries**, plus the diagram,
the ADR and (optionally) a runnable skeleton. The reasoning stays evidence-first: every
recommendation names the quality attributes and organisational facts that drove it, and the
"cheapest architecture that meets today's attributes and keeps tomorrow open" wins by default.

## When this skill triggers, decide the mode first

| Mode | Typical asks | Output |
|---|---|---|
| **Explain** | "what is DOMA", "explain CQRS", "difference between hexagonal and clean" | Prose + Mermaid diagram + when-to-use + anti-patterns (from `references/catalog.md`, `references/diagrams.md`) |
| **Compare** | "monolith or microservices", "comparison table", "pros and cons of serverless vs EDA" | Comparison table + quality-attribute matrix rows + verdict for their context |
| **Recommend** | "which architecture for X", "design the architecture of platform Y" | Decision walk-through → recommendation (base + interior + complements) → diagram → ADR (`assets/adr-template.md`) |
| **Scaffold** | "set up a hexagonal FastAPI project", "CQRS structure", "modular monolith with import-linter" | `scripts/scaffold.py` output + explanation of each folder + boundary rules |
| **Check** | "does this repo respect its layers?", "verify the modules do not import each other" | `scripts/check_boundaries.py` report (violations with file:line) |

Several modes can chain (Recommend → Scaffold is common). If the ask is ambiguous, default to
Recommend and state the assumptions inline rather than asking many questions.

## Workflow for Recommend (the core path)

1. **Collect the six decision inputs** — from the conversation, repo, or by asking one compact
   question if truly missing (`references/decision-guide.md` §1 lists them):
   organisation (teams, DevOps maturity), domain (complexity, bounded contexts, regulation),
   scalability (peaks, asymmetric scaling), consistency (ACID vs eventual, audit), evolution
   (lifespan, change rate, third-party extensibility), operations (observability, blast radius,
   infra budget). Missing inputs become explicit assumptions in the ADR.
2. **Walk the decision tree** (`decision-guide.md` §3): pick the **base** (Layered → Modular
   Monolith → Service-Based → Microservices → DOMA when services reach the hundreds), then the
   **interior pattern** per unit (Hexagonal / Clean for rich domains, CQRS±ES only for audited
   or contended sub-domains, Microkernel for extensibility, Pipes & Filters for data/document
   flows), then the **complements** (EDA at boundaries, Serverless for sporadic loads,
   Micro-frontends only with multiple front teams, Cell-Based only at hyperscale, Agentic for
   semantic tasks).
3. **Score the finalists** against the quality-attribute matrix (`decision-guide.md` §2).
   Show only the rows that matter for this case; do not paste the whole matrix.
4. **Name the anti-patterns the choice is exposed to** (`catalog.md` per entry + §"Anti-patterns")
   and the mitigation for each (e.g. EDA → idempotency + outbox + DLQ; Service-Based → collection
   ownership + additive schema changes).
5. **Draw it**: one Mermaid diagram from `references/diagrams.md`, adapted to the user's domain
   names (services, modules, events). Keep node labels in the user's language.
6. **Write the ADR** with `assets/adr-template.md` (Context → Decision → Alternatives with
   scores → Consequences → Migration path). If the user keeps an Obsidian vault and an Obsidian
   tool is available, offer to save it there; otherwise write it to the working directory.
7. **Offer the scaffold** when the recommendation is a Python/FastAPI/Reflex codebase.

## Ground rules that keep recommendations honest

- **Default is Modular Monolith + Hexagonal.** Recommend anything more distributed only when an
  input in step 1 demands it (3+ autonomous teams, proven asymmetric scaling, independent
  release cadence). Say which input.
- **Styles and patterns combine; never present them as mutually exclusive.** A microservice
  can be Hexagonal inside, use CQRS in one bounded context, talk EDA outside and be grouped
  under a DOMA gateway.
- **CQRS ≠ Event Sourcing.** CQRS alone (two models, one DB) is cheap; ES is a one-way door.
  Recommend ES only for audit/history requirements stated by the user.
- **Never recommend Space-Based, Cell-Based or DOMA "for the future"** — they solve scale that
  must already exist. Mention them as "revisit when X happens".
- **Reflex specifics**: state lives server-side and syncs via WebSocket, so Reflex is a thin
  client over a client-server or a primary adapter in Hexagonal; micro-frontends with Reflex are
  composed by route behind a reverse proxy.
- Match the user's language (Spanish or English) in prose, diagrams and ADR; keep code
  identifiers in the domain language the user already uses.

## Reference files (read only what the mode needs)

- `references/catalog.md` — the 19 entries: definition, pros, contras, when to use / avoid,
  associated patterns, anti-patterns, "signals that you need it". Read the entry(ies) involved.
- `references/decision-guide.md` — §1 decision inputs & questions, §2 quality-attribute matrix,
  §3 decision tree, §4 how styles combine (reference system), §5 org-size advice, §6 anti-pattern
  list with mitigations. Read for Compare/Recommend.
- `references/diagrams.md` — Mermaid templates per architecture + a combined-system diagram.
  Copy, then rename nodes to the user's domain.
- `references/examples-python.md` — minimal FastAPI/Reflex/Python examples per architecture
  (the *shape* of the code, not production code). Use when the user asks what it looks like in
  code, or when scaffolding by hand.

## Scripts

- `scripts/scaffold.py <pattern> <project_name> [--out DIR] [--reflex]` — writes a runnable
  skeleton for `layered | modular-monolith | hexagonal | clean | cqrs-es | microkernel |
  pipes-filters | doma-gateway`, including tests, an `.importlinter` (or layer config) and a
  README explaining the boundaries. Run `python scripts/scaffold.py --list` for details.
- `scripts/check_boundaries.py <src_dir> --rules rules.json` — AST-based import checker for
  layer/module rules (no third-party deps). `--init hexagonal|layered|modular|doma` writes a
  starter rules file. Use it in Check mode or to prove a scaffold's rules hold.

## Output conventions

- Recommend mode ALWAYS ends with this compact block before the ADR:

  ```
  Recommendation: <base> + <interior> (+ <complements>)
  Why: <2-3 decisive inputs>
  Not <alternative> because: <one line each>
  Risks / anti-patterns to watch: <short list with mitigation>
  Revisit when: <trigger that would change the decision>
  ```

  Write the block in the user's language, keeping the same five lines.
- Explain mode: definition → diagram → pros/contras → when → anti-patterns → one code shape,
  in that order, under 400 words unless asked for depth.
- Diagrams are Mermaid fenced blocks (Obsidian and GitHub render them). Offer Excalidraw or
  a slide only if the user asks for a presentation.
