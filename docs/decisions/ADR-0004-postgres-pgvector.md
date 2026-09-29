# ADR-0004: PostgreSQL with pgvector as the single datastore (plus Redis for ephemeral state)

- Status: accepted
- Date: 2026-09-24
- Deciders: Oleksii (lead)

## Context

We need relational data (users, items, listings, offers), vector search (image and text embeddings for
similarity, look retrieval, RAG) and ephemeral counters (quotas, rate limits, pub/sub).

## Options considered

1. **Postgres + pgvector** — one transactional store; filters + vectors in one query; RDS managed. Cons: HNSW at
   > ~5 M vectors needs care; fewer ANN knobs than dedicated engines.
2. **Postgres + Pinecone/Qdrant** — best ANN performance. Cons: two sources of truth, sync jobs, extra cost and ops.
3. **DynamoDB + OpenSearch** — AWS-native scale. Cons: far more complexity than a v1 needs.

## Decision

RDS Postgres 16 with pgvector (HNSW, cosine). Redis (ElastiCache) only for quotas, rate limits, cache and pub/sub —
never as a source of truth. Embedding width fixed at 1024 (Bedrock Titan) in ADR-scope; changing it is a migration.

## Consequences

- One backup, one migration tool (Alembic in core-api), joins between listings and vectors.
− Must watch index build times and `work_mem`; vector columns make rows wide — keep them in `items` but exclude from hot list queries.

## How we would know this was wrong

p95 vector query > 200 ms at our scale; > 5 M items; need for hybrid BM25 + vector beyond what `pg_trgm`/`tsvector` gives.
