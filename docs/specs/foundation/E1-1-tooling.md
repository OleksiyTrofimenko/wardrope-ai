# Spec: Monorepo tooling and Makefile

- Epic: foundation · Status: approved · Phase: 1 · Related: ADR-0001

## 1. Goal

One set of verbs (`make up|down|lint|typecheck|test|fmt|e2e|seed`) that every human, agent and CI job uses,
delegating to pnpm (JS), uv (Python) and go per area. Toolchain versions pinned.

## 2. Contract

Root files: `pnpm-workspace.yaml` (apps/*, packages/*), `package.json` with `"packageManager": "pnpm@9"`,
`.nvmrc` (22), `.python-version` (3.12), `Makefile` targets above, each running per-area sub-targets
and failing fast on the first non-zero exit. Areas that do not exist yet are skipped with a printed notice, not an error.

## 3. Data — none

## 4. Acceptance criteria

- AC-1: Given a clean clone with Node 22, pnpm 9, uv and Go 1.23 installed, When `make lint typecheck test` runs, Then it exits 0 (no areas yet → notices only).
- AC-2: Given an area directory exists (e.g. `services/core-api`), When `make test` runs, Then that area's test command is invoked and its exit code propagates.
- AC-3: `make help` lists every target with a one-line description.
- AC-4: Every target works from any CWD inside the repo (uses `$(MAKEFILE_DIR)`).

## 5. NFR — `make lint` for an empty repo completes in < 5 s. No network calls except package installs

## 6. Out of scope — installing toolchains, docker-compose, pre-commit, CI workflows, any application code

## 7. Task split — one PR, ≤ 200 lines. Role: implementer
