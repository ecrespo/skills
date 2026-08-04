# CodeGraph reference (structure layer)

Local-first code intelligence: tree-sitter parses the repo into ASTs; every
symbol, edge (calls, imports, inheritance, implementations), and file lands in
a local SQLite database (`.codegraph/db.sqlite`, WAL mode, FTS5). Exposed over
MCP, CLI, and library. 100% local: no embeddings, no vector DB, no API keys,
nothing leaves the machine. Indexing consumes zero LLM tokens.

## MCP tools (the nine)

| Tool | Ask it | Replaces |
|---|---|---|
| `codegraph_search` | "find symbol/file matching X" (FTS5) | grep across repo |
| `codegraph_node` | full detail on one symbol | opening the file to look |
| `codegraph_callers` | who calls X | grep for usages + reading each hit |
| `codegraph_callees` | what X calls | reading the function body + chasing imports |
| `codegraph_impact` | transitive blast radius of changing X | reading 5–15 files |
| `codegraph_context` | entry points + related symbols + snippets for a task | multi-file orientation reads |
| `codegraph_explore` | walk the graph neighborhood interactively | directory spelunking |
| `codegraph_files` | file-level structure/metadata | glob + head |
| `codegraph_status` | index health, freshness, counts | — (run when results look stale) |

Read the server instructions shipped with the binary — they specify when to
reach for which tool and exact parameter shapes for the installed version.

## Query patterns that save the most tokens

- **Pre-edit ritual**: `codegraph_impact` on every symbol you're about to
  change. Cheap insurance; catches callers in files you'd never have opened.
- **Orientation**: one `codegraph_context` call on the task's focal symbol
  returns entry points + related symbols + code snippets — often enough to
  plan an edit with zero file reads.
- **Verification after edit**: `codegraph_callers` on the changed symbol to
  confirm every call site was updated (watcher re-indexes within ~2s of
  save; if a just-made edit isn't reflected, wait a beat or check
  `codegraph_status`).
- **Cross-agent reuse**: the index is shared — switching between Claude Code,
  Cowork, Cursor, etc. does not re-trigger exploration.

## CLI essentials

```bash
codegraph index            # full (re)index; run after big pulls/rebases
codegraph status           # freshness, node/edge counts
codegraph search "<term>"  # same FTS as the MCP tool
codegraph --path <dir> ... # operate on another workspace root
```

## Configuration

- `.codegraph/config.toml` — language overrides (e.g. header handling for
  C/C++; re-run `codegraph index` after changing).
- `.codegraphignore` — extra exclusions beyond `.gitignore`, same syntax.
- `.codegraph/` ships with a pre-filled `.gitignore` so the index is never
  committed.

## Limits — when NOT to trust it alone

- It is a **structural** graph: it knows that A calls B, not why, and not
  whether the call is semantically correct. Pair with lat.md for intent.
- Dynamic dispatch, reflection, string-based routing, and DI containers can
  produce missing or INFERRED-quality edges — verify surprising absences with
  a targeted read.
- Freshness depends on the watcher; after branch switches or large generated
  changes, `codegraph index` manually.
