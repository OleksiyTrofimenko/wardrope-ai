# Architecture (short)

Full design, data model, AI flows and the 28-day roadmap: see the project doc `architecture-and-roadmap.md`
(copy the current version to `docs/architecture-full.md` when the repo becomes the single source of truth).
Process and roles: `engineering-playbook-phase-1.md`. Decisions: `docs/decisions/`.

Topology: CloudFront → ALB → { web (Next.js), core-api (FastAPI), ai-service (FastAPI + LangGraph), edge (Go WS) } on ECS Fargate.
Data: RDS Postgres 16 + pgvector, ElastiCache Redis, S3 media (private, OAC), SQS (`image-ingest`, `ai-tagging`), SES.
Async: S3 event → SQS → media-worker (Go) → `item_images`; `finalize-upload` → SQS → ai-service tagging (Phase 2).
