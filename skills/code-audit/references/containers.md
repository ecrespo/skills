# Containers — Hadolint, Trivy, Dockle

Three layers: **Dockerfile** (static, fast → pre-commit), **built image**
(slow → CI), **configuration/compose** (static → CI). Output → `analysis/`.

## Layer 1 — Dockerfile (Hadolint, pre-commit)

```bash
hadolint --failure-threshold=warning Dockerfile | tee analysis/hadolint.txt
```

Rules that are almost always a finding:
- **DL3002 / missing `USER`** at the end → container runs as root = **P1** in prod.
- **DL3007 `:latest`** in FROM → non-reproducible builds = P2.
- **DL3008/3013/3016/3018** unpinned deps (apt/pip/npm/apk) → P3, ignorable in CI
  images (document the `--ignore` as in the CuidaSalud gate with DL3008).
- Secrets via `ARG`/`ENV` (visible in `docker history`) → P1; use
  `RUN --mount=type=secret`.
- No multi-stage build when the build toolchain ships in the final image → P2 (attack
  surface).

## Layer 2 — Image and filesystem (Trivy, CI)

```bash
# CVEs in the repo (deps + IaC + secrets) without building an image:
trivy fs --scanners vuln,secret,misconfig --severity HIGH,CRITICAL \
  --format json -o analysis/trivy-fs.json .

# CVEs in the built image (OS packages + app deps):
docker build -t audit-target:local .
trivy image --severity HIGH,CRITICAL --ignore-unfixed \
  --format json -o analysis/trivy-image.json audit-target:local
```

Interpretation: CRITICAL with a fix available in a prod image = **P1**; HIGH = P2;
`--ignore-unfixed` to separate what is actionable. A `.trivyignore` with an ignored CVE
requires a comment with reason + review date (same discipline as pip-audit's
`--ignore-vuln`). If there is no Docker daemon in the audit environment, run only
`trivy fs` and mark the image layer as "pending CI".

## Layer 3 — Image best practices (Dockle, CI)

```bash
dockle --exit-code 1 --exit-level fatal -f json -o analysis/dockle.json audit-target:local
```

CIS checks: non-root user (CIS-DI-0001), no credentials in env, HEALTHCHECK
present, setuid/setgid permissions.

## Manual checklist (compose / runtime)

- `privileged: true`, `network_mode: host`, mounting `/var/run/docker.sock` → **P1**.
- No `read_only: true` or `cap_drop: [ALL]` on services that allow them → P3 hardening.
- Base image: prefer digest pin (`python:3.13-slim@sha256:…`) or at least a minor pin;
  distroless/chainguard for Go/Node runtime → cuts OS CVEs to nearly zero.
- `.dockerignore` present and excluding `.git`, `.env`, tests → without it, secrets
  from the build context can leak into the image (check with `docker history`).
- Resource limits (`mem_limit`/`deploy.resources`) in prod → P3.

## Gate vs CI

- **pre-commit**: hadolint (every template in `assets/precommit/` includes it).
- **CI**: trivy fs + trivy image + dockle; fail the pipeline on CRITICAL with a fix.
