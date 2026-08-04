# Graphify reference (meaning layer)

Multi-modal knowledge graph builder: tree-sitter AST for code (deterministic,
zero LLM) plus one LLM semantic pass for docs, SQL schemas, configs, PDFs,
images, and diagrams (cached per-file by SHA256). Nodes are functions, files,
classes, and *concepts*; edges are calls, imports, references, and inferred
semantic relationships. Leiden community detection clusters the graph into
thematic modules. Not a vector index: no embeddings, a real traversable graph
where every edge is explained.

## Commands

```bash
/graphify .                      # (in Claude Code) build/refresh the graph
/graphify . --update             # incremental — only changed files, AST-only for code
graphify query "<question>"      # NL question → scoped subgraph (a map, not a wall of code)
graphify path "<A>" "<B>"        # shortest explained path between two entities
graphify explain "<concept>"     # one node and its neighborhood
graphify extract <dir> [--backend ollama --token-budget N]   # CLI extraction
graphify install [--project]     # (re)register the assistant skill
```

Query logging: every query/path/explain and MCP `query_graph` call is logged
to `~/.cache/graphify-queries.log` — useful to audit what the agent actually
asked.

## Output artifacts (`graphify-out/`)

- `GRAPH_REPORT.md` — the single highest-value file for orientation: key
  concepts, god nodes (highest-degree symbols — a change there ripples wide),
  detected communities, surprising cross-file/cross-modal connections, and
  suggested questions. Read it FIRST for any onboarding/overview request.
- `graph.json` — the persistent full graph; all queries read this, never the
  raw tree.
- `graph.html` — interactive vis.js view for the human; point the user at it
  rather than describing the graph in prose.
- Optional exports: Obsidian vault, Neo4j, SVG, GraphML, MCP server.

## Edge provenance — calibrate trust

Every edge is tagged:
- **EXTRACTED** — explicit in the source. Treat as fact.
- **INFERRED** — resolved by graphify (name resolution, semantic linking).
  Treat as a strong hint; verify with `codegraph_callers`/`codegraph_node`
  or a targeted file read before building an argument on it.

Ghost duplicates (same symbol from AST + semantic passes) are auto-merged at
build time in current versions; if a pre-v0.8.33 graph shows duplicates, run
a full re-extract.

## Cost model

- Code extraction: free (AST, no LLM), all supported languages.
- Docs/images/PDF semantic pass: uses the assistant's model tokens (or a
  configured API key / local Ollama). One-time, then cached.
- Incremental updates after commits: free for code-only changes, <5s.
- Query time: a scoped subgraph typically costs a few hundred tokens vs tens
  of thousands for grep+read equivalents. (Vendor benchmarks are directional,
  not guarantees — corpus size and query mix matter.)

## Local Ollama backend

```bash
GRAPHIFY_OLLAMA_NUM_CTX=8192 graphify extract ./docs --backend ollama --token-budget 4000
```
- KV-cache window auto-sizes but may exceed GPU VRAM — lower `NUM_CTX`.
- "LLM returned invalid JSON / Unterminated string" → the model hit its
  output-token limit mid-response; lower `--token-budget`.

## Special strengths — reach for Graphify when

- The question spans code AND non-code (docs, SQL schema, infra config):
  it is the only layer with all of them in one graph.
- You need a *path* between two distant things ("how does the upload endpoint
  end up touching the billing table?") — `graphify path`.
- Hidden duplication: semantically similar but structurally disconnected code
  (duplication / missing abstraction / sync-async twins) that neither text
  search nor the structural graph surfaces alone (via graphify-mcp
  `hidden_links` when that server is installed).
- Onboarding: `GRAPH_REPORT.md` + a couple of `graphify query` calls beat any
  amount of file listing.
