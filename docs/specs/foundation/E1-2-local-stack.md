# Spec: Local stack (docker-compose)

- Epic: foundation · Status: approved · Phase: 1 · Related: ADR-0004, ADR-0005

## 1. Goal

`make up` starts Postgres 16 with pgvector, Redis 7, and LocalStack (S3 + SQS) with the buckets/queues
from `.env.example` pre-created, so services and tests run identically on every machine.

## 2. Contract

`docker-compose.yml` services: `postgres` (image `pgvector/pgvector:pg16`, db/user/password `capsule`, port 5432,
healthcheck `pg_isready`), `redis` (7-alpine, 6379), `localstack` (services s3,sqs, port 4566, init script
`infra/local/localstack-init.sh` creating bucket `capsule-media-dev`, queues `image-ingest`, `image-ingest-dlq`,
`ai-tagging`, `ai-tagging-dlq` with redrive policies). Named volumes for postgres data.

## 4. Acceptance criteria

- AC-1: `make up` returns only after all three services report healthy (`docker compose up -d --wait`).
- AC-2: `psql "$DATABASE_URL" -c 'create extension if not exists vector'` succeeds.
- AC-3: `aws --endpoint-url http://localhost:4566 sqs list-queues` lists the four queues; `s3 ls` lists the bucket.
- AC-4: `make down` removes containers and volumes; a following `make up` is clean.
- AC-5: A script `scripts/smoke-local.sh` checks AC-2 and AC-3 and is what CI will call later.

## 5. NFR — cold `make up` < 90 s on a laptop; total image pull < 1.5 GB

## 6. Out of scope — Langfuse, any application containers, Terraform

## 7. Task split — one PR. Role: sre
