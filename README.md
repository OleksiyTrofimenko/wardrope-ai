# wardrobe-ai (Capsule)

Peer-to-peer clothing exchange — sell, trade, borrow, gift — with an AI stylist that tags items from
photos and composes looks from your wardrobe and other members' items.

## How this repo is run
- Humans lead, AI agents implement. Rules for agents: `CLAUDE.md` (root + per area). Roles: `.claude/agents/`.
- Every feature starts as a spec in `docs/specs/`, every decision is an ADR in `docs/decisions/`,
  every phase has a board in `docs/phases/`.
- Nothing merges without tests, review, green CI and the lead's approval (`CODEOWNERS`).
- Numbers over vibes: `docs/observability.md` defines what every feature must emit.

## Local development (target state after E1)
```bash
cp .env.example .env
make up          # postgres+pgvector, redis, localstack
make test
make lint
```

## Layout
```
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
