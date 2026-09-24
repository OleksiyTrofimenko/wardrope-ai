# Observability — naming, required signals, dashboards

Everything we ship must be visible in numbers. This file is the contract every spec and PR is checked against.

## 1. Logs
- JSON, one object per line, to stdout. Fields always present:
  `ts, level, service, env, version, trace_id, span_id, event, msg` and `user_id_hash` when a user is in context.
- `event` is `snake.case` and stable: `item.created`, `item.finalized`, `listing.published`, `upload.presigned`,
  `image.processed`, `tagging.completed`, `look.generated`, `quota.exceeded`, `feedback.submitted`, `http.request`.
- Never log secrets, tokens, raw e-mails, image bytes, or full prompts with user content (log prompt version + token counts).
- Python: `structlog` bound to OTel context. Go: `slog` JSON handler with trace fields. Node: `pino`.

## 2. Metrics (OpenTelemetry → CloudWatch EMF)
Naming: `capsule_<service>_<subject>_<unit>`; labels kept low-cardinality (`route`, `method`, `status_class`, `mode`, `category`) — never user ids.

| Metric | Type | Owner |
|---|---|---|
| `capsule_<svc>_http_requests_total{route,method,status_class}` | counter | every HTTP service |
| `capsule_<svc>_http_request_duration_seconds{route}` | histogram | every HTTP service |
| `capsule_media_worker_images_processed_total{result}` | counter | media-worker |
| `capsule_media_worker_process_duration_seconds` | histogram | media-worker |
| `capsule_sqs_message_age_seconds{queue}` | gauge | consumers |
| `capsule_core_api_db_pool_in_use` | gauge | core-api |
| `capsule_ai_llm_tokens_total{feature,model,kind=prompt|completion|cached}` | counter | ai-service (Phase 2) |
| `capsule_ai_llm_cost_usd_total{feature,model}` | counter | ai-service (Phase 2) |
| `capsule_ai_quota_rejections_total{feature}` | counter | ai-service (Phase 3) |

## 3. Traces
W3C `traceparent` propagated over HTTP headers and as an SQS message attribute. Span per HTTP request, DB query
(SQLAlchemy instrumentation), outbound HTTP, SQS publish/consume, LLM call (with `prompt_version`, token counts as attributes).

## 4. Product events (`product_events` table, written by core-api)
`id, user_id, event, props jsonb, ts`. Phase 1 events: `user.signed_up`, `item.created`, `item.photo_uploaded`,
`item.finalized`, `listing.published`, `listing.viewed`. Phase 2+: `tagging.completed{fields_filled, size_detected}`,
`look.generated{questions_asked, sources}`, `look.saved`, `offer.made`, `offer.accepted`, `quota.hit`, `feedback.submitted`.
Derived KPI: **time-to-listing** = `listing.published.ts − item.created.ts` per item (median, p90).

## 5. Dashboards (one per family)
- **System**: RED per route per service; SQS age & DLQ depth; DB pool, slow queries; container CPU/mem; daily AWS cost.
- **Product**: signups/day; items created; time-to-listing median & p90; % listings with size filled; (Phase 2+) looks/day, save rate, offers, quota hits.
- **Engineering**: deploys/day, lead time PR→dev, CI duration, change-failure rate, agent-log metrics (first-pass CI, rework, findings).

## 6. Alarms (Phase 1)
5xx rate > 2 % over 5 min · p95 latency > 500 ms over 10 min · any DLQ depth > 0 · SQS oldest message > 5 min ·
RDS CPU > 80 % / storage < 20 % · daily AWS cost > budget/30 × 1.5 · synthetic E2E check failing twice in a row.

## 7. Definition of done, observability part
The PR names its log events, metrics and (if async) trace propagation, and links the dashboard panel that moved after deploy.
