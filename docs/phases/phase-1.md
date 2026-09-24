# Phase 1 — Walking skeleton (Days 0–7)

**Goal:** one real user journey end-to-end on AWS dev, observable, built through the full process
(spec → tests → implement → review → CI → deploy → metrics). Prove the factory, not the features.

**Entry:** repo with governance (this Day 0 scaffold) · accounts ready (AWS + budget, SES prod-access requested, Clerk, PostHog).

**Exit criteria (all must be true, written down in §4):**
- Sign up → create item with 3 photos → publish listing → visible in browse, on the dev URL, deployed from CI.
- Playwright E2E for that journey green in CI; synthetic check running every 10 min.
- p95 API latency < 300 ms on browse/items under k6 50 rps in dev.
- Dashboards exist for System, Product (incl. time-to-listing baseline) and Engineering families; Phase 1 alarms configured and tested by killing a service.
- ≥ 15 merged PRs, every one meeting the DoD; agent-log filled; ≥ 3 CLAUDE.md rules added from real mistakes.

## 1. Epics & tasks
| ID | Task (one PR each) | Role | Depends on | Status |
|---|---|---|---|---|
| E1-1 | Monorepo tooling: pnpm workspace, uv, Go module layout, Makefile (`up/test/lint/e2e/seed`) | implementer | — | todo |
| E1-2 | docker-compose: postgres+pgvector, redis, LocalStack (S3, SQS) with init script | sre | E1-1 | todo |
| E1-3 | pre-commit + linters (ruff, eslint, gofmt, gitleaks) | implementer | E1-1 | todo |
| E1-4 | CI: path-filtered workflows per area, cache, required checks | sre | E1-1 | todo |
| E2-1 | OpenAPI v0.1: users, items, item_images, listings, uploads | planner | — | todo |
| E2-2 | `packages/contracts`: generated TS client + Pydantic models, drift check | implementer | E2-1 | todo |
| E3-1 | core-api skeleton: settings, structlog, problem details, health/ready, OTel | implementer | E1-1 | todo |
| E3-2 | Alembic + schema v1 (users, items, item_images, listings, product_events) | implementer | E3-1 | todo |
| E3-3 | Clerk JWT dependency + webhook → users upsert | implementer | E3-2 | todo |
| E3-4 | Items CRUD + pagination + product events | implementer | E3-3 | todo |
| E3-5 | Draft item → presigned upload → finalize-upload (enqueue once, idempotent) | implementer | E3-4, E1-2 | todo |
| E3-6 | Listings create/list/browse with filters | implementer | E3-4 | todo |
| E4-1 | media-worker skeleton: config, slog, health, metrics | implementer (Go) | E1-1 | todo |
| E4-2 | SQS consume → S3 download → resize 3 sizes → upload | implementer (Go) | E4-1, E1-2 | todo |
| E4-3 | Write `item_images` + idempotency on redelivery | implementer (Go) | E4-2 | todo |
| E4-4 | EXIF/GPS strip + tests | implementer (Go) | E4-2 | todo |
| E5-1 | Next.js + Clerk + layout + design tokens | implementer (web) | E1-1 | todo |
| E5-2 | Item wizard: upload → form → publish (generated client) | implementer (web) | E5-1, E2-2, E3-5 | todo |
| E5-3 | My Store tab | implementer (web) | E5-2 | todo |
| E5-4 | Browse grid + item page | implementer (web) | E3-6 | todo |
| E5-5 | Vitest/RTL setup + Playwright E2E "create listing" | test-engineer | E5-2 | todo |
| E6-1 | Terraform backend, network, ecr, secrets, github-oidc | sre | — | todo |
| E6-2 | rds, s3-media, sqs (+DLQ) | sre | E6-1 | todo |
| E6-3 | alb + ecs-service module; deploy web, core-api, media-worker | sre | E6-2, E1-4 | todo |
| E6-4 | CloudFront in front of ALB + S3 (OAC) | sre | E6-3 | todo |
| E6-5 | Deploy jobs in CI (dev environment) | sre | E6-3 | todo |
| E7-1 | OTel export wired in all three services | sre | E6-3 | todo |
| E7-2 | Dashboards: System, Product, Engineering | sre | E7-1 | todo |
| E7-3 | Alarms + chaos test (kill a service → alarm ≤ 5 min) | sre | E7-2 | todo |
| E7-4 | Synthetic E2E check every 10 min | sre | E5-5, E6-5 | todo |
| E8-1 | agent-log filled; Day 7 retro; CLAUDE.md v2 | lead + scribe | all | todo |

## 2. Day plan
| Day | Focus | Parallel agents |
|---|---|---|
| 0 | Governance scaffold, accounts | planner, sre |
| 1 | E1-*, E3-1, E5-1 | tooling ‖ web |
| 2 | E2-*, E3-2, E3-3; tests for E3 from spec | planner → core-api ‖ test-engineer |
| 3 | E3-4, E3-5, E4-1, E4-2 | core-api ‖ Go |
| 4 | E3-6, E4-3, E5-2, E5-3 | core-api ‖ web |
| 5 | E6-1..3, E4-4; lead reviews core-api end to end | sre ‖ Go |
| 6 | E6-4, E6-5, E5-4, E5-5, E7-1, E7-2; first CI deploy | sre ‖ web |
| 7 | E7-3, E7-4, E8-1; retro; Phase 2 planning | scribe, planner |

## 3. Metrics snapshot (fill on Day 7)
| Metric | Value |
|---|---|
| PRs merged | |
| First-pass CI green rate | |
| Mean blocking findings / PR | |
| Mean rework cycles | |
| Escaped defects | |
| Mean human review minutes / PR | |
| CI duration (p50) | |
| Deploys to dev | |
| p95 latency browse / items | |
| Time-to-listing median (manual runs) | |
| AWS cost to date | |

## 4. Exit review (Day 7)
Decision: go / one more day. Reason:
Rules added to CLAUDE.md:
Gates added to CI:
What the planner should do differently in Phase 2:
