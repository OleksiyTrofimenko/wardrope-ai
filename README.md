# wardrobe-ai (Capsule)

Peer-to-peer clothing exchange — sell, trade, borrow, gift — with an AI stylist that tags items from
photos and composes looks from your wardrobe and other members' items.

## How this repo is run

- Humans lead, AI agents implement. Rules for agents: `CLAUDE.md` (root + per area). Roles: `.claude/agents/`.
- Every feature starts as a spec in `docs/specs/`, every decision is an ADR in `docs/decisions/`,
  every phase has a board in `docs/phases/`.
- Nothing merges without tests, review, green CI and the lead's approval (`CODEOWNERS`).
- Numbers over vibes: `docs/observability.md` defines what every feature must emit.

## Local development

Prerequisites (pinned in the repo): Node 22 (`.nvmrc`), pnpm 9 via `corepack enable` (`package.json`
`packageManager`), Python 3.12 (`.python-version`) with `uv`, Go 1.23, Docker.

```bash
cp .env.example .env
make help                  # every target with a one-line description
make up                    # postgres+pgvector, redis, localstack
make lint typecheck test   # per area: apps/web, services/core-api, services/media-worker
```

Areas that do not exist yet are skipped with a notice; the first failing command stops the run.
From a subdirectory, run `make -C <repo-root> <target>` (or `make -f <repo-root>/Makefile <target>`).
Self-test for the Makefile: `scripts/test-make.sh`.

## Layout

```text
apps/web                Next.js 15 (TypeScript)
services/core-api       FastAPI — schema owner, marketplace domain
services/ai-service     FastAPI + LangGraph — tagging, looks, stylist (Phase 2)
services/media-worker   Go — image pipeline
services/edge           Go — WebSocket + rate limiting (Phase 2)
packages/contracts      OpenAPI → generated clients
infra/terraform         AWS, dev + prod
docs/                   specs, decisions, phases, runbooks, observability
```

## Status

Phase 1 — walking skeleton. Board: `docs/phases/phase-1.md`.
