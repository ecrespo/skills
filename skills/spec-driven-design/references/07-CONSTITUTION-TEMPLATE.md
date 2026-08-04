# Template: constitution.md

The constitution holds the project's **non-negotiable** principles: written once,
rarely revised (with a changelog), and every subsequent artifact is validated against it
(the "constitution check"). It is the antidote to relitigating standards in every PR and
the mechanism by which any AI agent inherits the project's rules.

Writing rules:
- Each article in ubiquitous EARS form: "THE SYSTEM / THE TEAM SHALL..." — verifiable,
  not aspirational. Bad: "Code must be clean". Good: "Every new module SHALL pass
  Ruff + ty with no warnings before merge".
- 5-9 articles. More than 12 = nobody respects it; fewer than 4 = it says nothing.
- Each article with a one-line rationale (why it exists, what pain it prevents).
- Point CLAUDE.md / AGENTS.md at this file so every agent session loads it.

---

# Constitution — {project name}

> Version {X.Y} · Ratified: {date} · Last amended: {date}
> Scope: {repo(s) it governs}

## Articles

### Art. 1 — {Code quality}
THE TEAM SHALL {verifiable rule, e.g.: keep the pre-commit gate (Gitleaks, Ruff,
ty, Bandit) green; no merge with hooks disabled}.
*Rationale: {one line}.*

### Art. 2 — {Testing}
THE SYSTEM SHALL {e.g.: cover every EARS criterion of a MUST with at least one
automated test that cites it (REQ-NNN) before closing the task}.
*Rationale: ...*

### Art. 3 — {Data}
THE SYSTEM SHALL {e.g.: represent money with Decimal128 and store dates in UTC;
SHALL record every balance mutation with an idempotency key}.
*Rationale: ...*

### Art. 4 — {Architecture}
{e.g.: THE SYSTEM SHALL keep the module boundaries declared in import-linter /
dependency-cruiser; a new dependency cycle breaks CI}.
*Rationale: ...*

### Art. 5 — {Security}
{e.g.: THE SYSTEM SHALL validate all external input with schemas (Pydantic /
class-validator) at the edge; no secrets in code or in history}.
*Rationale: ...*

### Art. 6 — {Observability}
{e.g.: THE SYSTEM SHALL propagate a correlation ID through all main flows and
log errors with enough context to reproduce them}.
*Rationale: ...*

### Art. 7 — {Process}
{e.g.: THE TEAM SHALL obtain an approved spec before implementing any work ≥ medium
feature, and update the spec as part of the Definition of Done}.
*Rationale: ...*

## Stack constraints

What is decided and not re-discussed per feature (with minimum version if applicable):
languages, frameworks, database, messaging, infrastructure, CI.

## Amendments

| Date | Article | Change | Reason | Approved by |
|---|---|---|---|---|

## Constitution check (use in every artifact)

At the end of every PRD / Tech Design / Plan, a 3-5 line section: which articles
apply and how they are satisfied — or which exception is requested and why. An exception
without written justification is a violation.
