# Template: 02-TECH-STACK.md

Primary source: `analysis/inventory.json` + manifests + lockfiles.
Exact versions from lockfiles when they exist; if only ranges are available, say so.

---

# Tech stack — {system name}

> Reference commit: `{HEAD hash}` · Date: {date}

## 1. Executive summary

One-view table: main language(s), backend framework, frontend framework,
database(s), messaging, infrastructure, CI/CD. One row per category.

## 2. Languages

| Language | Approx. LOC | Role | Required version | Evidence |
|---|---|---|---|---|

## 3. Main dependencies

Only the ones that define the system (framework, ORM/ODM, infrastructure clients,
domain libraries). Utility libraries go in the appendix.

| Dependency | Version (lockfile) | Role in the system | Usage evidence |
|---|---|---|---|

## 4. Persistence and data

Engines, drivers, schemas/migrations, and where the connections are configured `[VERIFY:]`.

## 5. Infrastructure and deployment

- Containers: Dockerfiles and compose files found, base images and their versions
- IaC: Terraform/K8s/serverless if present
- CI/CD: detected pipeline, stages it runs (lint, test, scan, build, deploy)

## 6. Testing and quality

Test frameworks, linters, formatters, security scanners present, and which
CI stage runs them.

## 7. Rebuild risks

| Risk | Detail | Recommendation for v2 |
|---|---|---|
| EOL/deprecated | e.g.: unsupported framework version | upgrade to X |
| Unpinned | dependencies without a locked version | pin with a lockfile |
| Orphan | dependency declared but no usage detected | remove |

## Appendix: full dependency list

Reference `analysis/inventory.json` instead of duplicating the N dependencies here.
