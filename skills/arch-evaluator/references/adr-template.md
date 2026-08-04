# Template: adr/ADR-NNN-{slug}.md

One ADR per change proposal. The alternatives section is the heart: if "do nothing"
is not argued seriously, the ADR is propaganda. If the engineering:architecture skill
is available, follow its format conventions.

---

# ADR-{NNN}: {decision title}

> **Status**: proposed | accepted | rejected | superseded by ADR-XXX
> **Date**: {date} · **Weakness addressed**: WEAK-{NN}

## Context

What problem exists, with the weakness's evidence (don't repeat it in full: link and
summarize in 3-5 lines). What constraints apply: team, deadlines, systems that cannot
be touched, business requirements.

## Decision

What is proposed, in 2-5 declarative lines. If the proposal is to split a module or
extract a service, **show the seam**: which files go where and what graph/co-change
data supports that exact cut.

## Alternatives considered

### Alternative A: {the proposal}
- Advantages / Disadvantages / Estimated cost (order of magnitude: days/weeks)

### Alternative B: {a real alternative, not a straw man}
- Advantages / Disadvantages / Estimated cost

### Alternative C: Do nothing
- What it costs to live with the problem, with numbers from the analysis if they exist
  (e.g.: "totals.js accumulated 4 fixes in 6 months `[COMMITS:]`; at that rate...")
- When it would be reasonable to choose it

## Consequences

- **Positive**: what improves and how it will be measured (ideally a metric from the
  scripts: "cycles 3→0", "cross-module pairs auth↔billing: 0")
- **Negative**: what gets worse or what new complexity is paid — there is always
  something
- **Neutral**: what changes without being better or worse (conventions, locations)

## Reversibility

Can it be undone? How and at what cost? Irreversible decisions demand a higher
standard of evidence.

## Anti-overengineering guardrails (check before accepting)

- [ ] Doesn't introduce a layer/abstraction "for flexibility" without two real implementations
- [ ] If it extracts a service: justifies the distributed complexity with team and operations
- [ ] A more boring version exists (lint rule, test, convention) and it was explained
      why it isn't enough
- [ ] States what will NOT be touched
