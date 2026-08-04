# Node stacks — Node.js, NestJS, Next.js, React, Vite

The JS ecosystem has no 1:1 equivalents of Bandit/pip-audit; this table maps each
hook of the FastAPI gate to its Node counterpart. Raw output → `docs/code-audit/analysis/`.

## FastAPI gate → Node mapping

| Role in FastAPI gate | Node equivalent | Notes |
|---|---|---|
| Ruff (lint) | ESLint 9 flat config + `typescript-eslint` | |
| Ruff format | Prettier (or Biome, which replaces both) | Biome = 1 tool for lint+format, faster |
| ty / mypy | `tsc --noEmit` | Non-negotiable in TS; in plain JS, `// @ts-check` + jsconfig |
| C901 / CCR001 / Lizard | `eslint-plugin-sonarjs` → `sonarjs/cognitive-complexity: [error, 12]` + core rule `complexity: [error, 10]` | Same thresholds as the Python gate |
| Bandit | `eslint-plugin-security` + `njsscan` (backend) | njsscan = Node-specific SAST (Semgrep's p/nodejs works too) |
| Semgrep | `semgrep --config=p/javascript --config=p/typescript --config=p/react --config=p/nextjs --config=p/expressjs` | Pick configs per stack |
| pip-audit | `npm audit --omit=dev --audit-level=high` or **osv-scanner** (`osv-scanner scan --lockfile package-lock.json`) | osv-scanner has fewer false positives and covers pnpm/yarn lockfiles |
| pylint duplicate-code | **jscpd** — `npx jscpd src/ --min-tokens 70 --threshold 3 --reporters json,console --output analysis/` | `--threshold 3` fails if >3% duplicated |
| Gitleaks / Hadolint | Identical (language-agnostic) | |

## Audit commands (all Node stacks)

```bash
npx tsc --noEmit 2>&1 | tee analysis/tsc.txt
npx eslint . -f json -o analysis/eslint.json
npx jscpd src/ --min-tokens 70 --reporters json --output analysis/
npm audit --omit=dev --json > analysis/npm-audit.json || true   # exit!=0 with vulns
npx better-npm-audit audit 2>/dev/null || true                   # optional, filters noise
```

Also review `package.json`: scripts with `curl | sh`, dependencies with `git+http`,
suspicious `postinstall` hooks (supply-chain vector = P1), and missing `"packageManager"`
/ committed lockfile (P2).

## Framework-specific

### NestJS
- ESLint plugins: `@darraghor/eslint-plugin-nestjs-typed` (unvalidated DTOs,
  misdeclared injection). Review: all DTOs with `class-validator` +
  a global `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true })` — without
  this, mass assignment = P1. Guards on mutating endpoints; `@Exclude()` on exposed
  entities.
- Tests: unit = `Test.createTestingModule` with mocked providers; integration =
  `supertest` against `app.getHttpServer()`; e2e in `test/*.e2e-spec.ts` (the Phase 0
  count already separates them).

### Next.js
- ESLint: `eslint-config-next` (core-web-vitals). Semgrep `p/nextjs`.
- Review by hand: secrets in client components (`NEXT_PUBLIC_` with sensitive material
  = P1); Server Actions without input validation (zod) or auth checks = P1;
  `dangerouslySetInnerHTML` with external data = P1 (XSS); route handlers without rate
  limiting on auth. Auth middleware: verify it runs on the right routes
  (matcher), do not rely on layout alone.
- Tests: unit = vitest/jest + Testing Library; integration = Playwright/route handlers
  with `next-test-api-route-handler`.

### React / Vite (SPA)
- ESLint: `eslint-plugin-react-hooks` (hooks rules = error), `eslint-plugin-jsx-a11y`,
  sonarjs. Review: `dangerouslySetInnerHTML`, tokens in `localStorage` when an
  httpOnly alternative exists (amber-P2 depending on threat model), `VITE_*` variables
  with secrets (P1 — everything `VITE_*` ends up in the bundle).
- Optional `npx vite-bundle-visualizer` for dead dependencies.
- Tests: vitest + Testing Library (unit); Playwright/Cypress (integration/e2e).
  `vitest run --coverage` → gate in CI.

### Node.js backend (Express/Fastify)
- Review: helmet enabled, explicit CORS, rate limiting on auth, `child_process` with
  external input (P1), `express-validator`/zod at boundaries, EOL Node versions in
  `engines`/Dockerfile (P2).

## What goes in the gate vs CI

- **pre-commit**: gitleaks, standard hooks, prettier/biome, eslint (with sonarjs +
  security), tsc --noEmit, jscpd, npm audit only if the lockfile changed, hadolint.
  Templates: `nodejs`, `nestjs`, `nextjs`, `react-vite` in `assets/precommit/`.
- **CI**: jest/vitest --coverage with a threshold, full semgrep, osv-scanner, trivy
  fs+image, optional Stryker (mutation).
