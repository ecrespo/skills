# EARS notation for acceptance criteria

EARS (Easy Approach to Requirements Syntax) is a constrained natural language for
requirements: born at Rolls-Royce (2009) for aircraft engine control, it became the
de facto standard for AI-oriented specs (Kiro, Spec Kit) because every well-formed
criterion translates almost 1:1 into a test case. Use EARS in the functional
requirements and acceptance criteria sections of the PRD (template 01).

## The 5 patterns

| Pattern | Form | When to use it |
|---|---|---|
| **Ubiquitous** | THE SYSTEM SHALL {behavior} | Always true; global properties (security, format, limits) |
| **Event-driven** | WHEN {event}, THE SYSTEM SHALL {response} | Reaction to a trigger (the most common) |
| **State-driven** | WHILE {state}, THE SYSTEM SHALL {behavior} | Sustained behavior during a condition |
| **Optional** | WHERE {feature/config enabled}, THE SYSTEM SHALL {behavior} | Variants by configuration, plans, feature flags |
| **Unwanted behavior** | IF {error/abuse condition}, THEN THE SYSTEM SHALL {mitigation} | Errors, third-party outages, invalid input, duplicates |

Patterns combine: "WHILE an invoice is in `pending` state, WHEN the payment webhook
arrives, THE SYSTEM SHALL...".

## Quality rules

1. **One observable behavior per criterion.** If it has an "and" joining two distinct
   outcomes, it is two criteria.
2. **Verifiable or it doesn't exist.** Every criterion must name an outcome a test
   can observe (response, record, state). "SHALL be fast" is not EARS;
   "SHALL respond in < 500 ms p95" is.
3. **Stable ID**: `REQ-{NNN}` (or `REQ-{feature}-{NNN}`). Tasks and tests cite this
   ID — it is the backbone of traceability.
4. **Cover all three paths**: for each capability, at least one happy-path criterion
   (WHEN), plus the IF...THEN cases for errors and duplicates. The "unwanted
   behavior" patterns are where the expensive bugs live (duplicate webhook?
   third party down for 30 min? negative balance?) — forcing yourself to write them
   is 80% of the value of EARS.
5. **Domain vocabulary, consistent.** The same noun for the same concept across all
   artifacts (Analyze detects the drift).

## Example (payment with idempotency)

```
REQ-PAY-001 (event-driven): WHEN the customer confirms a payment with a new
idempotency key, THE SYSTEM SHALL record the transaction and respond 201 with the ID.

REQ-PAY-002 (unwanted behavior): IF a confirmation arrives with an already-processed
idempotency key, THEN THE SYSTEM SHALL respond 200 with the original transaction
without creating a new one.

REQ-PAY-003 (unwanted behavior): IF the payment provider does not respond within 8 s,
THEN THE SYSTEM SHALL mark the transaction `pending_confirmation` and enqueue a retry
with backoff.

REQ-PAY-004 (ubiquitous): THE SYSTEM SHALL represent amounts with Decimal128.

REQ-PAY-005 (state-driven): WHILE a transaction is `pending_confirmation`,
THE SYSTEM SHALL reject a second charge attempt on the same order.
```

## EARS ↔ Gherkin

They do not compete: **EARS is the language of requirements** (PRD); **Gherkin is the
language of tests** (executable criteria). The translation is mechanical:

```
EARS:    WHEN {event}, THE SYSTEM SHALL {response}
Gherkin: Given {implicit state precondition}
         When {event}
         Then {observable response}
```

Each REQ yields 1-N Gherkin scenarios (happy path + edges of the same event). The
reverse-sdd skill produces Gherkin when deriving criteria from existing code; when
promoting those findings to requirements for a new version, rewrite them as EARS with
a REQ-ID and keep the Gherkin as their tests.

## Anti-patterns

- Paragraph-criterion with 4 behaviors → split it.
- EARS theater: perfect syntax, unobservable outcome.
- Happy paths only: if there is no IF...THEN at all, the spec is incomplete.
- Recycled IDs: a removed REQ retires its ID (never reused) — deltas depend on that.
