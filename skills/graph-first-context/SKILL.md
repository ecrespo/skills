---
name: graph-first-context
description: >-
  Token-efficient codebase understanding by orchestrating three complementary
  knowledge layers: CodeGraph (structure — symbols, callers, impact), Graphify
  (meaning — semantic queries over code + docs), and lat.md (intent — design
  decisions and business rules in markdown). Use this skill whenever working in
  a repository that has a .codegraph/, graphify-out/, or lat.md/ directory, and
  whenever the user asks to explore, refactor, debug, onboard onto, or plan
  changes in a codebase — BEFORE reaching for grep, glob, or reading files.
  Also use it when the user asks to set up, index, sync, or maintain any of
  these tools, mentions "knowledge graph", "code graph", "token efficiency",
  "impact analysis", "blast radius", or complains that the agent is burning
  tokens re-discovering the codebase.
---

# Graph-First Context

Answer codebase questions by querying pre-built knowledge layers instead of
scanning files. Raw exploration (grep → glob → read 10 files) costs tens of
thousands of tokens per question and repeats on every task. The three layers
below front-load that discovery once, so each question costs a handful of
targeted calls.

The three layers and what each one is authoritative for:

| Layer | Tool | Authoritative for | Never use it for |
|---|---|---|---|
| **Intent** | lat.md | Why the code is this way: design decisions, business rules, domain concepts, constraints, test specs | How code works mechanically |
| **Structure** | CodeGraph | What the code is: symbols, call graphs, imports, references, change impact | Why decisions were made |
| **Meaning** | Graphify | How things relate conceptually across code AND docs/schemas/PDFs; high-level orientation | Precise caller/callee facts |

Rule of thumb: **lat.md answers "why", CodeGraph answers "what/where",
Graphify answers "how does it all fit together".**

## Step 0 — Detect what is available

At the start of a session (or when this skill triggers), check once:

```bash
ls -d .codegraph graphify-out lat.md 2>/dev/null
```

- `.codegraph/` → CodeGraph index exists; its MCP tools (`codegraph_search`,
  `codegraph_callers`, `codegraph_callees`, `codegraph_impact`,
  `codegraph_context`, `codegraph_explore`, `codegraph_node`,
  `codegraph_files`, `codegraph_status`) should be in your tool list.
- `graphify-out/` → Graphify graph exists (`graph.json`, `GRAPH_REPORT.md`,
  `graph.html`). Query via `graphify query` / `graphify path` /
  `graphify explain` CLI, or the `query_graph` MCP tool if connected.
- `lat.md/` → intent graph exists. Query via the `lat` CLI (`lat search`,
  `lat section`, `lat locate`, `lat refs`, `lat expand`, `lat check`).

Degrade gracefully: every layer is optional. Use whichever layers exist; fall
back to normal file exploration only for questions no layer can answer. If a
layer that would clearly help is missing, offer to set it up (see
`references/setup.md`) — offer once, don't nag.

If a query fails because an index is stale or missing, re-index (cheap for
CodeGraph and lat, incremental for Graphify) rather than silently falling back
to grep.

## The consultation ladder

For any task touching the codebase, consult layers in this order. Each rung is
cheap; stop descending as soon as you have what you need.

### 1. Intent first (lat.md) — before writing or changing ANY code

```bash
lat expand "<the user's prompt>"   # resolves any [[refs]] the user wrote
lat search "<task topic>"          # semantic search over design decisions
lat section "<file#Section>"       # read the relevant sections
```

Read the matched sections before planning. This is the layer that prevents the
two most expensive failure modes: contradicting a deliberate design decision
(e.g. "why is this client synchronous?" — because the upstream provider
requires it), and re-explaining domain context the project already wrote down.
If `lat search` returns nothing relevant, note it — that may mean the decision
you're about to make deserves a new section (see Maintenance).

### 2. Structure second (CodeGraph) — before touching a symbol

Never grep for definitions, callers, or usages when CodeGraph is present.
Instead:

- Locating something: `codegraph_search` (FTS over symbols/files).
- "What calls X?" / "What does X call?": `codegraph_callers` / `codegraph_callees`.
- "What breaks if I change X?": `codegraph_impact` — run this before every
  non-trivial edit; it replaces reading 5–15 files to eyeball blast radius.
- Orienting inside an unfamiliar module: `codegraph_context` or
  `codegraph_explore` — returns entry points, related symbols, and snippets in
  one call.

Only open a file with Read when you are about to edit it or need exact
surrounding lines. The graph tells you *which* file and *which* lines; the
Read confirms and edits.

### 3. Meaning third (Graphify) — for fuzzy, cross-cutting, or doc-spanning questions

Use when the question is conceptual rather than symbol-precise:

```bash
graphify query "how does the payment reconciliation flow work end to end?"
graphify path "InvoiceProcessor" "NotificationService"   # how two things connect
graphify explain "IdempotencyStore"                      # one concept, its neighborhood
```

Graphify is the only layer that also covers docs, SQL schemas, configs, PDFs,
and diagrams, and its edges are tagged EXTRACTED (explicit in source) vs
INFERRED (resolved) — trust EXTRACTED, verify INFERRED with CodeGraph or a
targeted Read. For onboarding-style questions ("give me an overview"), read
`graphify-out/GRAPH_REPORT.md` first — it lists key concepts, god nodes, and
communities in one page.

### 4. Raw files last

Grep/glob/read only for: content inside a specific known file, non-indexed
artifacts (logs, lockfiles, generated code), or verifying a graph answer that
looks suspicious. If you catch yourself about to fan out over multiple files
to "understand how X works", stop — that is a rung-1/2/3 question.

## Task playbooks

**Refactoring / renaming / signature change**
1. `lat search` the symbol's domain — any documented constraint? (rung 1)
2. `codegraph_impact` on the symbol — full blast radius. (rung 2)
3. Edit each affected site; use `codegraph_callers` to verify nothing missed.
4. If the refactor changes a documented design, update the lat.md section and
   run `lat check`.

**Bug hunt / debugging**
1. `codegraph_search` the error's symbols → `codegraph_callers` to walk up the
   call chain instead of reading whole files.
2. If the bug spans subsystems, `graphify path <A> <B>` to see the connective
   tissue.
3. Check `lat search` for the business rule — many "bugs" are documented
   intentional behavior.

**New feature**
1. `lat search` + `lat expand` for domain rules and adjacent decisions.
2. `graphify query` for where the feature conceptually belongs.
3. `codegraph_context` on the target module for concrete integration points.
4. Implement. Then: add/extend a lat.md section for any non-obvious decision,
   link test specs, run `lat check`.

**Onboarding / "explain this repo"**
1. `graphify-out/GRAPH_REPORT.md` (one page) — never start by listing files.
2. `lat.md/` index/architecture sections for the why.
3. `codegraph_status` + `codegraph_explore` on the main entry point.
Budget: a competent overview should cost hundreds of tokens of tool output,
not tens of thousands.

**Code review / PR analysis**
1. For each changed symbol: `codegraph_impact` — flag callers outside the diff.
2. `lat refs "<file>#<Section>"` on touched files — does the change violate a
   linked spec? Do `// @lat:` backlinks still point at true statements?
3. Review lat.md/ diffs first (the why), then code (the how).

## Maintenance — keep the layers honest

A stale graph is worse than no graph. Follow these rules whenever you edit
code in a repo that has the layers:

- **CodeGraph**: self-maintains via file watchers. If results look stale
  (`codegraph_status` shows old timestamps), run `codegraph index`.
- **Graphify**: after a substantial change set, run the incremental update
  (`/graphify . --update` or `graphify extract . --update` depending on the
  install). Code-only changes re-parse via AST at zero LLM cost. Recommend a
  git post-commit hook for automation (see `references/setup.md`).
- **lat.md**: this one YOU maintain — it cannot auto-update, by design.
  Before finishing any task in a lat-enabled repo:
  1. If you made a non-obvious design decision, added business logic, or
     changed a documented behavior → write or update the relevant section
     (leading paragraph required; link code with `[[path/file.ts#Symbol]]`
     and add `// @lat: [[section-id]]` backlinks in the code).
  2. Run `lat check` and fix every reported inconsistency.
  Do not consider the task complete until `lat check` passes. Document the
  why, not the how — never paste code walkthroughs into lat.md.

## Anti-patterns

- Grepping for callers/definitions when `.codegraph/` exists.
- Reading 5+ files to "get oriented" when `GRAPH_REPORT.md` exists.
- Making architectural changes without a `lat search` for prior decisions.
- Treating Graphify INFERRED edges as ground truth without verification.
- Editing code in a lat-enabled repo and finishing without `lat check`.
- Re-running full Graphify extraction (LLM cost) when `--update` suffices.
- Answering "why is it built this way?" from code reading when lat.md exists —
  code shows what, only the intent layer records why.

## References

Read these on demand — not upfront:

- `references/setup.md` — installing, indexing, MCP wiring, git hooks, and
  Claude Code vs Claude Desktop/Cowork configuration for all three tools.
- `references/codegraph.md` — full CodeGraph tool/CLI reference and query
  patterns.
- `references/graphify.md` — Graphify commands, extraction backends (incl.
  local Ollama), output artifacts, cost model.
- `references/latmd.md` — lat.md authoring rules, CLI reference, section
  format, test-spec coverage workflow.
