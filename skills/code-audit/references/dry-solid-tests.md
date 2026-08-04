# DRY, SOLID and Tests — evaluation criteria

## 1. DRY (duplication)

Primary cross-language tool: **jscpd** (`npx jscpd <src> --min-tokens 70
--reporters json,console --output analysis/`). Native alternatives: pylint
`duplicate-code` (Python), `dupl` in golangci (Go), sonarjs `no-identical-functions` (TS).

**Thresholds (on the % of duplicated lines jscpd reports):**

| % duplicated | Verdict |
|---|---|
| < 3% | green |
| 3–8% | amber |
| > 8% | red |

**Legitimate duplication (do not penalize):** migrations, test fixtures/factories,
mirrored DTOs/schemas between layers (sometimes that is correct *de*coupling),
generated code. Exclude with `--ignore` and say so in the report.

**Duplication that is a finding:** repeated business logic (same amount validation in
3 endpoints), HTTP clients copied between integrations (retry/timeout silently
diverge — a well-known pattern in banking integrations), duplicated parsing/mapping.
Report each clone with the 2+ file:line locations and a proposed seam
(helper, base class, or leave it? Rule of three: extract on the third repetition).

## 2. SOLID — grep-able signals + verdict per principle

There is no deterministic tool; evaluate with objective signals anchored to
`[VERIFY: file:line]`. If `docs/arch-eval/analysis/` exists (arch-evaluator skill),
use its fan-in/fan-out and cycles as DIP/SRP evidence instead of re-deriving them.

| Principle | Violation signals (search for) | Measurable proxy |
|---|---|---|
| **S**RP | Classes >300 lines or >10 public methods; ever-growing "utils/helpers/manager" files; services that talk to DB + HTTP + queues at once | Lizard length/CCN; file churn (if it is also a git hotspot, the cost is real) |
| **O**CP | `if/elif isinstance(` chains or `switch(type)` that grow with every feature; enums that force touching N places when adding a case | grep `isinstance(`, `case .*Type` |
| **L**SP | Subclasses raising `NotImplementedError` in inherited methods; overrides that tighten preconditions; concrete-type checks after receiving the abstraction | grep `NotImplementedError`, `raise .*not supported` |
| **I**SP | Interfaces/protocols >5-7 methods implemented partially; test mocks that stub 15 methods to use 2 (the test gives it away) | Size of Protocol/interface/ABC |
| **D**IP | Domain importing concrete infrastructure (`from app.infra…` inside `domain/`); `requests`/`boto3`/DB driver instantiated inside business logic; impossible to test without network/DB | Import direction (arch-evaluator's dep_graph gives it exactly) |

Green/amber/red verdict **per principle**, each with 1-3 pieces of evidence.
Proportionality rule: SOLID serves change, not purity — an OCP violation in a module
that has not changed in 12 months is P3; the same one in the repo's #1 hotspot is P2.
Do not propose new hierarchies/abstractions unless ≥2 real variants already exist
(same anti-overengineering guardrail as arch-evaluator).

## 3. Unit tests (dimension 3)

**Separation by stack convention** (the Phase 0 count uses these heuristics):
pytest without DB/network (or `unit` markers), jest/vitest `*.test.ts`, Go `_test.go`
without build tag.

**Coverage — threshold by module criticality, not a flat global:**

| Module type | Minimum lines | Note |
|---|---|---|
| Money/payments/auth | 85% + branch coverage | Here branch > line |
| Business logic | 70% | |
| Adapters/IO | 40% | Better covered by integration |
| Repo global | 60% indicative | Never report only the global: it hides the 0% in payments |

Commands: `pytest --cov=app --cov-report=json:analysis/cov.json --cov-branch` ·
`vitest run --coverage` / `jest --coverage --json` · `go test -coverprofile`.

**Smells (each with file:line):** tests without asserts; `time.sleep`/timeouts as
synchronization; order-dependent tests (fail with `-p random` / `--shuffle`); mocks of
the very system under test (they test the mock); giant snapshot tests never read;
a single "happy path" test per function with no error/edge cases.

**Optional (if there is time/CI):** mutation testing as the truth about assert
quality — `mutmut` (Python), Stryker (JS/TS), `go-mutesting`. Score <60% with high
coverage = decorative coverage.

## 4. Integration tests (dimension 4)

What must exist for green:
1. **API layer**: at least one test per critical endpoint against the real app
   (TestClient/httpx-ASGI, supertest, httptest) verifying status + contract.
2. **DB layer**: repositories against a real ephemeral DB (testcontainers / test
   compose), not just mocks — queries are the most common bug.
3. **External systems**: integrations (banks, OCR, queues) against contract doubles
   (respx/nock/VCR, wiremock) with error cases: timeout, 5xx, malformed payload.
   A banking integration without a timeout/retry-path test = amber at minimum.
4. **Separated from the fast gate**: their own marker/folder/build-tag; they run in CI,
   not in pre-commit.

Straight red: 0 integration tests with external integrations in production, or an
integration tested only with mocks of your own HTTP client.
