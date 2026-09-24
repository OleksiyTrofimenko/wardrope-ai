# ADR-0005: OpenTelemetry everywhere; CloudWatch/X-Ray for system metrics, Postgres `product_events` for product metrics, Langfuse for LLM traces

- Status: accepted
- Date: 2026-09-24
- Deciders: Oleksii (lead)

## Context
The product must be judged in numbers from Phase 1: engineering (DORA), system (RED/USE) and product (funnel)
metrics, plus LLM cost and quality from Phase 2. One person operates it; tooling must be cheap and boring.

## Options considered
1. **OTel → CloudWatch + X-Ray** — no extra vendor; Terraform-native; adequate dashboards. Cons: UI is clunky, cross-signal correlation weaker.
2. **OTel → Grafana Cloud (free tier)** — better dashboards, Loki/Tempo/Prometheus. Cons: another vendor, free-tier limits.
3. **Datadog** — best UX. Cons: cost.

## Decision
Instrument once with OpenTelemetry (SDK in Python/Go/Node, W3C trace context propagated through HTTP and SQS
message attributes). Export to CloudWatch + X-Ray in Phase 1; switching exporter to Grafana Cloud is a config change
if dashboards prove painful. Product metrics are domain events written to `product_events` by core-api and
charted from Postgres; PostHog (free tier) on the web for client-side funnels. LLM traces and costs in Langfuse Cloud.
Naming and required signals per feature are defined in `docs/observability.md`.

## Consequences
+ Vendor-neutral instrumentation. + Product numbers are queryable with SQL from Day 6.
− Three UIs (CloudWatch, PostHog, Langfuse) until consolidated.

## How we would know this was wrong
Lead spends > 30 min/day fighting dashboards; correlation of a trace across services takes > 5 min; CloudWatch cost > $30/month.
