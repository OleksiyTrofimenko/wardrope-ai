# Spec: core-api skeleton

- Epic: foundation · Status: approved · Phase: 1 · Related: ADR-0003, ADR-0005

## 1. Goal

A FastAPI service with the cross-cutting concerns every later feature relies on: typed settings, structured
JSON logging with trace ids, RFC 7807 error responses, health/readiness, OpenTelemetry instrumentation,
and the layered package layout that `import-linter` enforces. No domain code.

## 2. Contract

Package `services/core-api/src/capsule_core/` with `main.py` (app factory `create_app()`), `settings.py`
(pydantic-settings, reads env, fails fast on missing required vars), `logging.py` (structlog JSON, binds
`trace_id`, `span_id`, `request_id`, `service`, `env`, `version`), `errors.py` (exception handlers →
`application/problem+json` with `type,title,status,detail,instance,trace_id`; validation errors include
`errors[]`), `telemetry.py` (OTel tracer + meter providers; OTLP exporter if `OTEL_EXPORTER_OTLP_ENDPOINT`
set, else console in local, none in tests; FastAPI + SQLAlchemy instrumentation), `api/health.py`
(`GET /healthz` → 200 `{status:"ok",version}` always; `GET /readyz` → 200 if `SELECT 1` on Postgres succeeds,
503 problem details otherwise), `api/deps.py` (async session dependency), `db/engine.py`.
Packages `api/`, `services/`, `repositories/`, `models/` exist (empty `__init__.py`) with `.importlinter`
contracts: `api` may import `services`, `services` may import `repositories`, `repositories` may import `models`;
no reverse edges; `models` imports no FastAPI.
`pyproject.toml`: fastapi, uvicorn, pydantic-settings, sqlalchemy[asyncio], asyncpg, structlog, hatchling, 
opentelemetry-{api,sdk,instrumentation-fastapi,instrumentation-sqlalchemy,exporter-otlp}; dev: pytest,
pytest-asyncio, httpx, ruff, mypy (strict), import-linter, pytest-cov, testcontainers[postgres].


## 2.1 Behavioural contract (agreed with the test engineer)
a. `ENV=test` is a valid non-local value; `ENV` is required (no default) and startup fails fast without it.
b. Logging goes through stdlib `logging`; the app must not replace existing root handlers (no `basicConfig(force=True)`), so `caplog` sees records.
c. `create_app()` reads the environment on every call, keeps no process-wide settings cache, and is safe to call repeatedly.
d. The app starts even when the database is down; `/readyz` returns 503 in that case.
e. `trace_id` is a real OpenTelemetry trace id (32 hex chars, not all zeros); an incoming `traceparent` header is honoured.
f. Validation errors are listed in `errors[]` with `field` and `message` keys.
g. The `route` field in the request log is the route template (`/items/{id}`), not the raw path.
h. The request log line for a 500 is below ERROR level, so AC-5's "exactly one ERROR line" holds.
i. `.importlinter` lives in `services/core-api/`; layered contracts allow indirect imports (`api → services → repositories`), skip-level direct imports are forbidden, and `models` must not import any web framework (`include_external_packages = True`).



## 4. Acceptance criteria

- AC-1: `GET /healthz` returns 200 with `status` and `version` and does not touch the database.
- AC-2: `GET /readyz` returns 200 when Postgres is reachable and 503 `application/problem+json` when it is not.
- AC-3: An unknown route returns 404 as problem details with a `trace_id` field.
- AC-4: A request failing validation returns 422 problem details with an `errors[]` list of field/message.
- AC-5: An unhandled exception returns 500 problem details with no stack trace in the body, and one `ERROR` log line with the traceback.
- AC-6: Every request produces exactly one `http.request` log line containing `method, route, status, duration_ms, trace_id`.
- AC-7: Logs are single-line JSON in non-local envs; `LOG_LEVEL` is respected.
- AC-8: `lint-imports` passes and a test proves that adding `from capsule_core.api import x` inside `repositories/` would fail it.
- AC-9: Missing required setting (e.g. `DATABASE_URL`) makes startup fail with a clear message.
- AC-10: `uv run pytest` green, `ruff`, `mypy --strict` clean, coverage ≥ 80 %.

## 5. NFR

- `/healthz` p95 < 5 ms locally. Logs: `http.request`, `app.startup`, `app.shutdown`. Metrics: FastAPI instrumentation provides
  `http.server.request.duration`; the mapping to `capsule_core_api_*` names happens in the exporter config (E7-1).
- Security: no debug mode outside `ENV=local`; docs UI only in local.

## 6. Out of scope — Alembic, any table, auth, Dockerfile (E1-4 adds it), business endpoints

## 7. Task split
Tests are written first by the test engineer on branch `test/E3-1` (no PR of their own; they merge with the implementation).
PR-B1 — skeleton: settings, logging, errors, middleware, app factory, health, DB engine/session, import-linter, packaging. Carries the `size-exception` label because every test needs the whole app.
PR-B2 — OTLP/console exporters, SQLAlchemy instrumentation, `services/core-api/CLAUDE.md` (~70 lines).
