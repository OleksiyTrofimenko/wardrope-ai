# ADR-0003: Two Python services (core-api, ai-service) and Go at the throughput edges

- Status: accepted
- Date: 2026-09-24
- Deciders: Oleksii (lead)

## Context
Marketplace CRUD and AI workloads have different dependencies, scaling profiles and change cadence.
The lead wants Go in the stack where it earns its place, without splitting domain logic across languages.

## Options considered
1. **Single FastAPI monolith** — simplest; but LangChain/vision deps bloat the core image and AI incidents take down CRUD.
2. **core-api + ai-service (Python), Go for media-worker and edge (WS + rate limiting)** — domain logic stays in Python;
   Go where it is small, CPU/IO bound and stateless.
3. **Core API in Go** — fastest runtime; but slows a Python-learning lead and duplicates the domain model.

## Decision
Option 2. `core-api` owns the schema and all business rules. `ai-service` owns prompts, agents, embeddings and
writes only AI-owned columns/tables. `media-worker` (Go) resizes and strips EXIF. `edge` (Go) does WebSocket
fan-out and rate limiting. Services talk via SQS (async) and HTTP through generated clients (sync).

## Consequences
+ Independent scaling and deploys; AI failures isolated. + Go usage is real but bounded.
− Four deployables to observe; contracts must be versioned; local dev needs docker-compose for all.

## How we would know this was wrong
More than 20 % of PRs touch two services at once; Go services grow business rules; ai-service needs synchronous
writes to core tables.
