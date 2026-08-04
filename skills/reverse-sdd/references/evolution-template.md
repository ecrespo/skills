# Template: 03-EVOLUTION.md

Source: `analysis/history.md` (eras and clusters). This is a narrative, not a log
dump: 5-15 lines per era. Every historical claim cites `[COMMITS: hash1, hash2]`.

---

# System evolution — {system name}

> {N} commits analyzed, {start date} → {end date}.
> Eras delimited by {release tags | quarters (untagged repo)}.

## Timeline

Mermaid `timeline` diagram with the eras and their main capability.

## Era 1: {label} ({from} → {to})

- **What the system gained**: capability(ies) built, in business language
- **Active clusters**: `cluster-a`, `cluster-b`
- **Representative commits**: `[COMMITS: ...]` (the highest-churn ones of the era)
- **Technical context**: stack/architecture changes if any

*(repeat per era)*

## Patterns observed in the history

- **Rhythm**: release/activity cadence, peaks and valleys with a hypothesis for the cause
- **Recurring fixes**: files with ≥2 fix commits (table from the script) — each one is
  a design symptom that v2 must attack and a source of acceptance criteria
- **Abandoned directions**: features started and reverted/removed
  `[COMMITS: ...]` — document why (if the message says so) to avoid repeating them

## Lessons for v2

A numbered, actionable list. Each lesson links the historical pattern that originates it
to a concrete rebuild decision (e.g.: "the payments module accumulated 7 race-condition
fixes `[COMMITS: ...]` → v2 must design idempotency from the Data Model, see US-0XX").
