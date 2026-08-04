# Agent Skills Collection

Five production-ready [Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) for software-engineering workflows: architecture evaluation, code auditing, spec-driven design, reverse-engineering documentation, and token-efficient codebase context. They work with any agent that implements the Agent Skills format (`SKILL.md`), including Claude Desktop / Cowork, Claude Code, the Claude API, Codex, and OpenCode.

## What is a skill?

A skill is a self-contained folder with a `SKILL.md` file. The YAML frontmatter (`name` + `description`) is the only part always loaded into context — the agent reads the body, and any bundled `references/`, `scripts/`, or `assets/`, only when the task matches. This progressive disclosure keeps skills cheap when idle and deep when triggered.

```
skills/
├── arch-evaluator/        # Evidence-based architecture audit
├── code-audit/            # 8-dimension quality + security audit
├── graph-first-context/   # Token-efficient codebase understanding
├── reverse-sdd/           # Reverse-engineer docs & specs from a repo
└── spec-driven-design/    # SDD v2 methodology and templates
scripts/
├── validate_and_package.py  # Validate skills and build dist/*.skill bundles
└── install.sh               # Copy skills into any agent's skills directory
.claude-plugin/              # Claude Code plugin + marketplace manifests
.github/workflows/           # CI: validate, package, release
AGENTS.md                    # Instructions for agents working with/on this repo
```

## Execution order

When applying the full collection to a repository, run the skills in this order — each stage feeds the next:

1. **graph-first-context** — index the codebase first (CodeGraph, Graphify, lat.md) so every later skill queries structure and intent instead of re-discovering the repo file by file.
2. **reverse-sdd** — with context in place, reverse-engineer the documentation baseline: inventory, architecture docs, evolution timeline, user stories, and test matrix.
3. **code-audit** — audit quality and security over the documented baseline (DRY, SOLID, tests, SAST, SCA, secrets, containers) and produce the remediation plan.
4. **arch-evaluator** — evaluate the architecture using the dependency graph, git-history signals, and the audit findings; produce ADRs and a phased migration plan.
5. **spec-driven-design** — turn the accepted proposals into specs: Constitution, PRD with EARS criteria, technical design, data model, implementation plan, and tasks.

Each skill still works standalone; the order matters only when chaining them over the same repo.

## The skills

### arch-evaluator

Audits a repository's architecture with deterministic evidence and produces a scorecard, ranked weaknesses, ADRs for proposed changes, and a phased migration plan. Two pure-stdlib scripts do the heavy lifting before any judgment is made: `scripts/dep_graph.py` builds a module-level dependency graph (Python + TS/JS) to find cycles, god modules, and unstable coupling; `scripts/arch_signals.py` mines git history for hotspots, fix-prone files, and temporal (co-change) coupling. Every finding must carry a `[METRIC]`, `[VERIFY]`, or `[COMMITS]` evidence tag.

Triggers: "evaluate the architecture", "architecture audit", "what's wrong with this repo", "propose architecture improvements".

### code-audit

Full quality and security audit across 8 dimensions: DRY, SOLID, unit tests, integration tests, SAST, SCA (dependency CVEs), secrets, and container security. `scripts/detect_stack.py` auto-detects the stack (FastAPI, Django, Node.js, NestJS, Next.js, React/Vite, Golang) and reports tooling gaps; `references/stacks-*.md` map the right tool matrix per framework; `assets/precommit/` ships seven ready-to-use `.pre-commit-config.yaml` templates (Gitleaks, Ruff/ESLint/golangci-lint, Bandit/gosec, pip-audit/npm audit/govulncheck, Hadolint, complexity). Produces `01-AUDIT-REPORT.md` and `02-REMEDIATION-PLAN.md`.

Triggers: "code audit", "assess the repo's security", "review DRY/SOLID", "set up the pre-commit for X stack".

### graph-first-context

Orchestrates three knowledge layers for token-efficient codebase understanding: CodeGraph (structure — symbols, callers, impact), Graphify (semantic queries over code + docs), and lat.md (design decisions and business rules). Directs the agent to query these graphs before falling back to grep/glob/file reads, cutting token burn on large repos. Includes setup and per-tool reference guides.

Triggers: working in a repo containing `.codegraph/`, `graphify-out/`, or `lat.md/`; "impact analysis", "blast radius", "knowledge graph".

### reverse-sdd

Reverse-engineers a complete documentation and spec kit from an existing repository so a new version can be rebuilt from scratch. `scripts/repo_inventory.py` inventories the codebase and `scripts/git_history.py` clusters commit history into an evolution timeline; from these the skill produces architecture docs, a tech-stack inventory, user stories with Gherkin acceptance criteria, a test matrix, and a rebuild plan mapped to SDD artifacts (`00-INVENTORY.md` … `05-REBUILD-PLAN.md`, `US/US-NNN-*.md`).

Triggers: "document this repository", "reverse engineering", "rebuild from scratch", "user stories from commits".

### spec-driven-design

Spec-Driven Design (SDD) v2 methodology: specifications as the primary artifact before code, aligned with GitHub Spec Kit, Kiro, and OpenSpec. Eleven reference templates cover the nine artifacts — Constitution, PRD with EARS acceptance criteria, API Spec, Technical Design, Data Model, Implementation Plan, agent-executable Tasks, Delta Specs for brownfield changes, and the Analyze cross-artifact validation gate — plus an authoring guide and the EARS notation reference.

Triggers: "write a PRD", "design doc", "break down into tasks", "change proposal", "plan before coding".

## Installation

### Claude Code — as a plugin (recommended)

The repo ships a plugin marketplace (`.claude-plugin/`). Inside a Claude Code session:

```
/plugin marketplace add ecrespo/skills
/plugin install ecrespo-skills@ecrespo-skills
```

All five skills install as a managed bundle and update when you refresh the marketplace. Prefer editable copies instead? Use the installer below.

### Claude Code, Codex, Cursor, OpenCode & other agents — skills.sh

```bash
npx skills@latest add ecrespo/skills
```

The [skills.sh](https://skills.sh) installer detects your agents, lets you pick which skills to copy, and writes them into your project as ordinary files you own and can edit.

### Any agent — bundled installer (no Node required)

```bash
# from a clone
./scripts/install.sh                         # all skills -> ~/.claude/skills
./scripts/install.sh --target claude-project # -> ./.claude/skills of the current repo
./scripts/install.sh --target opencode       # -> ~/.config/opencode/skills
./scripts/install.sh --skills code-audit --dest ~/my-agent/skills

# without cloning
curl -fsSL https://raw.githubusercontent.com/ecrespo/skills/main/scripts/install.sh | bash -s -- --list
curl -fsSL https://raw.githubusercontent.com/ecrespo/skills/main/scripts/install.sh | bash -s -- --skills arch-evaluator
```

`--dry-run` previews, `--list` shows available skills, `--dest` targets any skills directory.

### Claude Desktop / claude.ai / Cowork

Download a `.skill` bundle from the [Releases page](https://github.com/ecrespo/skills/releases) — CI attaches one per skill on every `v*` tag — and add it via Settings → Capabilities → Skills (or drop it into a Cowork chat and click "Save skill"). To build bundles locally: `python3 scripts/validate_and_package.py` → `dist/*.skill`.

### Claude API

Upload the skill zip via the Skills endpoint and reference it in a container-enabled request. See the [Agent Skills API docs](https://docs.claude.com/en/docs/agents-and-tools/agent-skills).

## CI / automation

`.github/workflows/skills.yml` runs on every push and PR:

1. **validate** — enforces the Agent Skills rules (frontmatter, naming, English-only, referenced paths), smoke-tests every bundled script, lints the installer, and checks the plugin manifests.
2. **package** — builds `dist/*.skill` and uploads them as a workflow artifact (pushes only).
3. **release** — on `v*` tags, publishes a GitHub Release with the five `.skill` bundles attached and install instructions in the notes.

Cutting a release:

```bash
git tag v1.0.0 && git push origin v1.0.0
```

## Bundled scripts

All scripts are pure Python 3 stdlib — no dependencies to install — and read-only over the analyzed repo (they only write their own reports). Each supports `--help`.

| Script | Skill | Output |
|---|---|---|
| `dep_graph.py` | arch-evaluator | `dep_graph.json` / `.md` — cycles, instability, god modules |
| `arch_signals.py` | arch-evaluator | `arch_signals.json` / `.md` — hotspots, temporal coupling |
| `detect_stack.py` | code-audit | stack detection + `gaps.md` tooling-gap report |
| `repo_inventory.py` | reverse-sdd | `00-INVENTORY.md` — modules, entry points, dependencies |
| `git_history.py` | reverse-sdd | evolution timeline + commit clusters for user stories |

## Validating and packaging

```bash
python3 scripts/validate_and_package.py            # validate + build dist/*.skill
python3 scripts/validate_and_package.py --no-package  # validate only
```

Validation enforces the Agent Skills rules: frontmatter limited to `name` and `description`, name in lowercase-hyphen format (≤ 64 chars) matching the folder, description ≤ 1024 chars, all files English-only, and every `references/`, `scripts/`, or `assets/` path mentioned in `SKILL.md` actually present. Run it before publishing any change.

## Conventions

Skill names are lowercase-with-hyphens. Descriptions are written in third person and state both what the skill does and when to trigger it, since the description is the only signal the agent has when deciding to load the skill. Bodies stay lean; anything long-form lives in `references/` and is loaded on demand. Scripts avoid third-party dependencies so they run in any sandbox.

## License

See [LICENSE](LICENSE).
