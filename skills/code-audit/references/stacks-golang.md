# Golang stack

Go concentrates nearly the entire gate in **golangci-lint** (meta-linter). Raw output →
`docs/code-audit/analysis/`.

## FastAPI gate → Go mapping

| Role in FastAPI gate | Go equivalent | Notes |
|---|---|---|
| Ruff lint | golangci-lint (revive, staticcheck, errcheck) | |
| Ruff format | `gofumpt` (strict superset of gofmt) + `goimports` | |
| ty / mypy | The compiler + `staticcheck` | Typing is built into the language |
| C901 (cyclomatic) | `gocyclo` (golangci linter) `min-complexity: 10` | |
| CCR001 (cognitive) | `gocognit` `min-complexity: 12` | Same thresholds as the gate |
| Bandit | **gosec** (golangci linter or standalone) | G101 secrets, G201/202 SQLi, G304 path traversal, G404 weak rand |
| pip-audit | **govulncheck** — `govulncheck ./... > analysis/govulncheck.txt` | Only reports vulns *reachable* via call-graph → very few false positives; reachable CVE = P1 |
| pylint duplicate-code | `dupl` (golangci linter, threshold 100 tokens) | |
| Gitleaks / Hadolint | Identical | |

## Audit commands

```bash
golangci-lint run ./... --out-format json > analysis/golangci.json || true
govulncheck -format json ./... > analysis/govulncheck.json || true
go vet ./... 2>&1 | tee analysis/govet.txt
go test ./... -cover -coverprofile=analysis/cover.out
go tool cover -func=analysis/cover.out | tail -5   # total at the end
```

Minimal audit `.golangci.yml` (propose it if the repo has none):

```yaml
linters:
  enable:
    - errcheck
    - staticcheck
    - govet
    - revive
    - gosec
    - gocyclo
    - gocognit
    - dupl
    - gofumpt
    - goimports
    - ineffassign
    - unused
linters-settings:
  gocyclo: { min-complexity: 10 }
  gocognit: { min-complexity: 12 }
  dupl: { threshold: 100 }
  gosec: { severity: medium }
```

## Manual Go review (with [VERIFY: file:line])

- Ignored errors `_ = err` or unchecked in money/IO paths → P2 (errcheck lists them).
- SQL built with `fmt.Sprintf` instead of placeholders → P1 (gosec G201).
- `exec.Command` with external input and no allowlist → P1.
- Goroutines without lifecycle control (leaks) in servers → P2; `context.Context`
  propagated through every network/DB call.
- `net/http` without timeouts (`Server{ReadTimeout…}`, `http.Client{Timeout}`) → P2 (DoS).
- Interfaces: defined on the consumer side (idiomatic = ISP/DIP); interfaces with
  >5 methods exported from the producer package = amber SOLID signal.

## Tests in Go

- Unit: `_test.go` next to the code, table-driven. Integration: build tag
  `//go:build integration` or a separate folder + testcontainers-go; run with
  `go test -tags=integration ./...`. Without a build tag/folder separating them,
  dimension 4 cannot be green (you cannot tell what runs in the fast gate).
- Coverage: `-coverprofile` per package; see thresholds in dry-solid-tests.md.
- Race detector in CI: `go test -race ./...` — mandatory in concurrent code;
  its absence with goroutines in the repo = amber.

## Gate vs CI

- **pre-commit**: gitleaks, standard hooks, gofumpt/goimports, golangci-lint (fast,
  `--fast` optional), go vet, hadolint. Template: `assets/precommit/golang.pre-commit-config.yaml`.
- **CI**: go test -race -cover with a threshold, govulncheck, trivy fs+image, full
  golangci-lint without `--fast`.
