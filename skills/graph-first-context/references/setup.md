# Setup: installing and wiring the three layers

Read this when the user asks to set up, install, or automate CodeGraph,
Graphify, or lat.md — or when Step 0 detection finds a layer missing that
would clearly help.

Always confirm with the user before installing anything or modifying agent
configuration files.

## CodeGraph (structure layer)

Two implementations exist; prefer whichever the user already uses.

**TypeScript/npm original (colbymchenry/codegraph):**
```bash
npm install -g @codegraph/cli     # verify exact package name on the repo
codegraph setup                    # auto-configures detected agents (Claude Code, Cursor, Codex, opencode...)
codegraph index                    # one-time full index → .codegraph/db.sqlite
```

**Rust rewrite (Cleboost/codegraph-rs)** — single binary, no Node runtime:
```bash
# install per repo instructions (cargo install / release binary)
codegraph index                    # creates .codegraph/ (db.sqlite, config.toml, .gitignore)
```

Key facts:
- Indexing uses tree-sitter only — zero LLM tokens, fault-tolerant to syntax
  errors, ~20 languages, framework-aware routing (FastAPI, NestJS, Django,
  Express, Rails, Spring, ...).
- A native file watcher (inotify/FSEvents) keeps the index fresh with a ~2s
  debounce; no hook needed.
- `.codegraphignore` (gitignore syntax) excludes extra paths.
- The MCP server is what agents talk to. `codegraph setup` writes the MCP
  entry for Claude Code (`.mcp.json` project-scoped or user config). For
  Claude Desktop / Cowork, add the same server to Settings → Connectors
  (local MCP server via stdio) so Cowork sessions get the tools too.

Verify wiring: the agent's tool list should contain `codegraph_search`,
`codegraph_callers`, `codegraph_impact`, etc. If not, run `codegraph_status`
equivalent from CLI (`codegraph status`) and re-run setup.

## Graphify (meaning layer)

```bash
uv tool install graphifyy          # or: pipx install graphifyy
graphify install                   # registers the /graphify skill user-wide
graphify install --project         # OR project-scoped: writes .claude/skills/graphify/SKILL.md
```

First build (from the agent, so doc/image extraction can use the assistant's
model):
```
/graphify .
```
Outputs `graphify-out/`:
- `graph.html` — interactive vis.js graph (clickable, filterable)
- `GRAPH_REPORT.md` — one-page audit: key concepts, god nodes, communities,
  surprising connections, suggested questions
- `graph.json` — the full graph, queried by CLI/MCP without re-reading files

Cost model — explain this to the user before the first build:
- Code files: tree-sitter AST, deterministic, **zero LLM tokens**.
- Docs / PDFs / images / diagrams: one semantic LLM pass, then cached by
  SHA256 per file. One-time cost.
- To make even that pass free, use a local Ollama backend:
  ```bash
  GRAPHIFY_OLLAMA_NUM_CTX=8192 graphify extract ./docs --backend ollama --token-budget 4000
  ```
  Reduce NUM_CTX if the GPU runs out of VRAM; truncated-JSON warnings mean
  the model hit its output limit — lower the token budget.

Incremental updates (AST-only for code, <5s, zero tokens):
```
/graphify . --update
```

Git post-commit hook for hands-free freshness (`.git/hooks/post-commit`):
```bash
#!/usr/bin/env bash
graphify extract . --update --quiet &   # re-extracts only changed files
```
Make it executable (`chmod +x`). Combined with CodeGraph's watcher, both
machine-maintained layers stay current without agent effort.

Optional MCP mode (exposes `query_graph` etc. as tools instead of CLI):
Graphify ships an embedded server (`graphify <dir> --mcp`); the community
`graphify-mcp` package adds token-budgeted subgraphs, NL queries, and git
freshness checks on top (`pip install "graphify-mcp[treesitter]"`). For
Claude Desktop / Cowork, register either as a local connector so the graph is
queryable outside a terminal session.

## lat.md (intent layer)

```bash
npm install -g lat.md              # verify package name via repo: github.com/1st1/lat.md
lat init                           # scaffolds lat.md/ + installs agent hooks/instructions
```

`lat init` configures popular coding agents (writes instructions so agents
run `lat search` before coding and `lat check` before finishing). For Claude
Code it wires the project automatically; for Claude Desktop / Cowork, ensure
the `lat` CLI is on PATH in the Cowork environment, and mention lat.md in the
project's context so sessions know to use it.

Bootstrapping content for an existing codebase — do this WITH the user, not
silently:
1. Identify sources of truth: existing design docs, ADRs, PRDs, technical
   designs (e.g. an Obsidian vault, docs/ folder, wiki).
2. Create topical files (`lat.md/architecture.md`, `lat.md/payments.md`,
   `lat.md/auth.md`, `lat.md/tests.md`...) — never one monolith.
3. For each non-obvious decision, write a section: leading paragraph stating
   what and why, then detail. Link code with `[[src/path.ts#Symbol]]`.
4. Add `// @lat: [[section-id]]` comments at the linked code sites.
5. `lat check` until clean; commit `lat.md/` to the repo.

CI idea: run `lat check` in the pipeline so drift between docs and code fails
the build, same as a linter.

## Recommended combined rollout order

1. **CodeGraph first** — instant win, zero token cost, no authoring effort.
2. **Graphify second** — one build, then incremental; biggest payoff in repos
   with substantial docs/schemas or for onboarding-heavy teams.
3. **lat.md last** — highest effort, highest leverage; requires human-curated
   authoring. Seed it from existing design documents rather than writing from
   scratch.

After rollout, the division of labor: CodeGraph and Graphify maintain
themselves (watcher + hook); lat.md is maintained by the agent+human loop
(`lat check` as the finishing gate).
