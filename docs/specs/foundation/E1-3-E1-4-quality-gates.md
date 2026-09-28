# Spec: pre-commit and per-area CI
- Epic: foundation · Status: approved · Phase: 1

## 1. Goal
Fast local feedback (pre-commit) and identical checks in CI per area, path-filtered, each a required check.

## 2. Contract
`.pre-commit-config.yaml`: ruff (lint+format), eslint via `pnpm lint` (staged only), gofmt/goimports (when Go exists),
gitleaks, end-of-file/trailing-whitespace, markdownlint. `.github/workflows/`: `web.yml` (paths `apps/web/**`,
`packages/**`: install with pnpm cache → lint → typecheck → test → build), `core-api.yml` (paths `services/core-api/**`:
uv sync → ruff → mypy → lint-imports → pytest with a Postgres service container → coverage report as PR comment),
`local-stack.yml` (paths `docker-compose.yml`, `infra/local/**`: `make up` → `scripts/smoke-local.sh`).
`ci.yml` gains a `required` summary job that needs all area jobs so branch protection points at one check.
Dockerfiles: `services/core-api/Dockerfile` (multi-stage, uv, non-root, `HEALTHCHECK /healthz`) and
`apps/web/Dockerfile` (standalone output, non-root), built in CI but not pushed (E6 pushes).

## 4. Acceptance criteria
- AC-1: A PR touching only `apps/web` triggers `web.yml` and not `core-api.yml`.
- AC-2: Each area job fails on a deliberately introduced lint error (prove with a throwaway commit in the PR, then revert it).
- AC-3: `required` job is green only when all triggered area jobs are green; skipped jobs count as success.
- AC-4: `pre-commit run --all-files` is clean on `main`.
- AC-5: Both Docker images build in CI in < 4 min each with layer caching.

## 5. NFR — total CI wall-clock for a one-area PR < 6 min.
## 6. Out of scope — deployment, ECR push, Terraform CI, Go workflow (arrives with E4-1).
## 7. Task split — PR-A pre-commit (≤ 100 lines), PR-B CI + Dockerfiles. Role: sre.