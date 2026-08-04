# Checklist: Analyze phase (cross-artifact validation, read-only)

Run it with all artifacts ready and BEFORE implementing. It is read-only: the output
is a list of findings with severity; the human decides what to fix. Never skip it on
complex features — it catches the gaps that turn into runtime failures.

## How to run it

Read ALL of the feature's artifacts (and the constitution) and walk through the 7
categories. Report in the format at the end. Fix nothing during the analysis.

## 1. Coverage (the queen category)

- [ ] Every MUST in the PRD has ≥1 task in tasks.md and ≥1 planned test citing its REQ
- [ ] Every endpoint in the API Spec appears in the Tech Design and has tasks
- [ ] Every field in the API Spec exists in the Data Model (consistent names and types)
- [ ] Every phase of the Implementation Plan is covered by tasks
- [ ] No orphan tasks (without a REQ) and no ghost REQs (cited but never defined)

## 2. Constitution

- [ ] No artifact contradicts an article (stack, data, security, process)
- [ ] Requested exceptions have written justification in the constitution check

## 3. Ambiguity

- [ ] Every EARS criterion names an observable outcome (a test could verify it)
- [ ] No unmeasurable adverbs ("fast", "robust") outside a context with a number
- [ ] Limits have a value and a unit (timeouts, sizes, ranges, p50/p95)

## 4. Terminology consistency

- [ ] The same concept uses the same noun across all 5+ documents ("order" in the
      PRD, "request" in the API, and "purchase" in the Data Model? → unify)
- [ ] States and their transitions are identical between API Spec and Tech Design

## 5. Unhappy paths

- [ ] Every external integration has its IF...THEN cases (timeout, outage, duplicate)
- [ ] Every mutation involving money/external effects defines idempotency and compensation
- [ ] API Spec errors have a code, a response shape, and an associated criterion

## 6. Data

- [ ] Money in Decimal, dates with explicit timezone, IDs with a defined format
- [ ] Every Data Model index tied to a query in the API/Tech Design (and vice versa:
      hot queries without an index → finding)
- [ ] Migrations considered if pre-existing data exists

## 7. Task executability

- [ ] Dependency order has no cycles; [P] only where no files are shared
- [ ] Every Done is a concrete command or observation
- [ ] First batch identified (3-5 tasks) for supervised execution

## Report format

```
# Analyze — {feature} · {date}

| # | Severity | Category | Finding | Artifacts | Suggestion |
|---|---|---|---|---|---|
| A-01 | CRITICAL | Coverage | REQ-PAY-002 has no task or test | PRD, tasks | add T-0XX |
| A-02 | HIGH | Unhappy paths | POST /reconcile lacks duplicate case | API, PRD | new IF...THEN REQ |
| A-03 | MEDIUM | Terminology | "order"/"request" mixed | PRD, API | unify on "order" |

Verdict: READY TO IMPLEMENT | FIX CRITICALS FIRST | MAJOR REVISION
```

Severities: **CRITICAL** = implementing as-is produces a system that does not meet the
spec or violates the constitution · **HIGH** = a gap an agent will fill by inventing ·
**MEDIUM** = friction/drift · **LOW** = style.

Final rule: the Analyze approves nothing — it presents findings. Approval is human.
