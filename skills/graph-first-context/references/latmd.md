# lat.md reference (intent layer)

Agent Lattice: a knowledge graph for the codebase written in markdown, living
in a `lat.md/` directory at the repo root. It replaces the flat AGENTS.md that
stops scaling: sections cross-link with `[[wiki links]]`, markdown links into
code (`[[src/auth.ts#validateToken]]`), code links back with
`// @lat: [[section-id]]` comments, and `lat check` enforces that nothing
drifts. It records what the project does and WHY — domain concepts, design
decisions, business rules, test specifications. It is the only one of the
three layers a machine cannot rebuild from source, because intent is not in
the source.

## CLI

```bash
lat search "<natural language>"   # semantic search (LLM embeddings) across all sections
lat section "<file#Section>"      # read a section
lat locate "Section Name"         # find a section by name (exact or fuzzy)
lat refs "file#Section"           # what references this section (backlinks)
lat expand "<user prompt text>"   # resolve [[refs]] in a prompt to file locations + context
lat check                         # validate referential consistency — the finishing gate
lat init                          # scaffold lat.md/ + install agent hooks/instructions
```

## Agent contract (what lat init installs, honor it even without the hooks)

1. Before writing code: `lat search` the task topic; read matched sections to
   ground the plan in actual architecture instead of guessing.
2. On every user prompt containing `[[refs]]`: `lat expand` it first.
3. Before finishing: update the graph if warranted, then run `lat check` and
   fix all reported errors. The task is not done until both are complete.

## Authoring rules

**Section format** — every section needs a leading paragraph:

```markdown
# Payment idempotency
Brief overview of what this section documents and why it matters. Detail can
follow in paragraphs, lists, or code-linked refs like [[src/payments/store.py#IdempotencyStore]].

## Retry semantics
Details about this child topic.
```

A section that opens directly with a child heading (no leading paragraph) is
invalid; `lat check` reports it. Overly long leading paragraphs are also
flagged.

**What belongs in lat.md:**
- Non-obvious design decisions ("client X is synchronous because the provider
  rejects concurrent sessions")
- Business rules and domain concepts not deducible from code
- Constraints, invariants, rejected alternatives and why
- Test specifications (see coverage workflow below)
- Anything you found yourself explaining twice

**What does NOT belong:**
- Code walkthroughs — the code is the walkthrough; lat.md explains why, not how
- Duplicated code snippets
- Temporary notes, TODOs, status — lat.md is permanent, stable knowledge
- One monolithic file — split by meaningful topic (architecture.md, auth.md,
  payments.md, tests.md, ...)
- Broken links — always finish with `lat check`

## Linking model

- Section → section: `[[Other Section]]`
- Section → code: `[[src/module/file.ts#SymbolName]]`
- Code → section: comment `// @lat: [[section-id]]` (or the language's
  comment syntax) at the relevant code site

Backlinks make review bidirectional: reviewers read the lat.md/ diff first
(the why), then the code diff (the how); `lat refs` shows every code site
governed by a decision.

## Test-spec coverage workflow

Describe test cases as sections and mark them:

```markdown
---
require-code-mention: true
---
# Spec: duplicate payment is rejected
A second payment with the same idempotency key within the window must return
the original result and produce no new charge.
```

Each such spec must be referenced by a `// @lat: [[spec-id]]` comment in test
code; `lat check` flags any spec without a backlink. This turns the knowledge
graph into a reviewable coverage map: specs without tests fail the check.

## Interplay with the other layers

- lat.md tells you the decision; `codegraph_impact` tells you what enforcing
  or changing that decision touches. Use both before architectural edits.
- Graphify's semantic pass can ingest `lat.md/` files too — the intent layer
  then appears in the meaning graph, linking concepts to code communities.
- When `lat search` misses on a topic where a real decision was just made,
  that is the trigger to write the section — capture intent at the moment it
  exists, in the same task.
