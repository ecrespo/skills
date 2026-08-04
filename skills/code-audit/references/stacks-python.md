# Python stacks — FastAPI and Django

Tool matrix, run commands and interpretation. All raw output goes to
`docs/code-audit/analysis/`. Run in read-only mode (no `--fix`) during the audit.

## Quick install (audit environment, does not touch the repo)

```bash
# with uv (preferred) — or pip install --break-system-packages in a sandbox
uv tool install ruff
uv pip install bandit[toml] pip-audit lizard radon flake8 flake8-cognitive-complexity pytest pytest-cov
# semgrep if the environment allows it (heavy): uv pip install semgrep
```

## Common to FastAPI + Django

| Dimension | Tool | Command | Threshold / interpretation |
|---|---|---|---|
| Secrets | Gitleaks | `gitleaks detect --source . -v --report-path analysis/gitleaks.json` and `gitleaks detect --log-opts="--all"` for history | 1 real secret = P1. Distinguish from examples/fixtures (`.gitleaksignore`) |
| SAST | Bandit | `bandit -r app/ -c pyproject.toml --severity-level=medium -f json -o analysis/bandit.json` | Confirmed HIGH = P1-P2. `assert` in prod, `shell=True`, pickle, `eval` |
| SAST | Semgrep | `semgrep --config=p/python --config=p/secrets --config=p/owasp-top-ten --json -o analysis/semgrep.json .` | Add `p/fastapi` or `p/django` depending on the stack. If it does not run locally (pkg_resources dep on 3.13), mark "pending CI" |
| SCA | pip-audit | `pip-audit -f json -o analysis/pip-audit.json` (inside the repo's venv) or `pip-audit -r requirements.txt` | Critical/high CVE in a reachable dep = P1. Document each `--ignore-vuln` with reason and review date (PYSEC-2025-183/pyjwt pattern) |
| Complexity | Lizard | `lizard app/ --CCN 10 --arguments 5 --length 200 -w > analysis/lizard.txt` | CCN>10 = amber; >20 = red (proxy for violated SRP) |
| Cognitive complexity | flake8+CCR001 | `flake8 --select=CCR001 --max-cognitive-complexity=12 app/` | Complements CCN; functions >12 → refactor candidates |
| Types | ty / mypy | `uv run ty check app/` or `mypy app/ --strict` | No typing at boundaries (schemas, repos) = amber in SOLID/DIP |
| DRY | pylint dup | `pylint app/ --disable=all --enable=duplicate-code --min-similarity-lines=6 > analysis/pylint-dup.txt` | See thresholds in dry-solid-tests.md. Cross-language alternative: `npx jscpd app/ --min-tokens 70 --reporters json --output analysis/` |
| Format/lint | Ruff | `ruff check app/ --statistics` + `ruff format --check app/` | Informational only during the audit; the gate blocks on it |

## FastAPI-specific

- **Semgrep ruleset**: `p/fastapi` (injection in `Depends`, response without a model, CORS `*`).
- **Review by hand** (with `[VERIFY: file:line]`):
  - `CORSMiddleware(allow_origins=["*"], allow_credentials=True)` → P1 if there is cookie-based auth.
  - Endpoints without `response_model` returning raw ORM objects → field leakage (P2).
  - Sync `Depends(get_db)` in async endpoints → event loop blocking (P2 perf).
  - Validation: every input through Pydantic v2 (`model_config = ConfigDict(strict=True)` on money/IDs).
  - JWT: pinned algorithm (`algorithms=["RS256"]`), expiration, key outside the code.
- **Integration tests**: `httpx.AsyncClient` + `ASGITransport` pattern, or TestClient against
  the real app with an ephemeral DB (testcontainers). Count in Phase 0; if 0 → red in dimension 4.

## Django-specific

- **Native check**: `python manage.py check --deploy --fail-level WARNING > analysis/django-check.txt`
  — covers `DEBUG=True`, weak `SECRET_KEY`, cookies without `Secure`, HSTS, `ALLOWED_HOSTS`.
  It is the first command to run on Django; every WARNING is a finding with an ID (`security.W004`…).
- **Semgrep ruleset**: `p/django` (raw SQL with formatting, `mark_safe`, `csrf_exempt`).
- **Templates**: djLint — `djlint templates/ --lint --profile=django`.
- **Migrations**: `python manage.py makemigrations --check --dry-run` (drift = amber in CI).
- **Review by hand**:
  - `.raw(` / `cursor.execute(` with f-strings → P1 (SQLi).
  - `csrf_exempt` on views with side effects → P1-P2 depending on exposure.
  - `mark_safe` / `|safe` with user data → P1 (XSS).
  - `pickle`/`django-redis` with a pickle serializer over external data → P1.
- **Tests**: unit with `SimpleTestCase`/plain pytest; integration = `TestCase` with DB,
  `pytest-django` with `@pytest.mark.django_db`. The marker/folder separation counts for
  dimension 4.

## What goes in the gate (pre-commit) vs CI

- **pre-commit**: gitleaks, standard hooks, ruff+format, ty, flake8-CCR001, lizard,
  bandit medium+, pip-audit (only if the lockfile changes), hadolint. Templates:
  `assets/precommit/fastapi.pre-commit-config.yaml`, `assets/precommit/django.pre-commit-config.yaml`.
- **CI**: pytest+cov (coverage gate), full semgrep rulesets, trivy fs+image,
  `manage.py check --deploy` (Django), optional mutation testing (`mutmut`).
