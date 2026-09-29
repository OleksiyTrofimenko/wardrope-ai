# Spec: <feature name>

- Epic: <epic>  ·  Status: draft | approved | built  ·  Owner: Oleksii  ·  Spec version: 1
- Related ADRs: ADR-000x  ·  Phase: N

## 1. Goal & user story

As a <role>, I want <capability> so that <outcome>. One paragraph on why now.

## 2. Contract

```yaml
# OpenAPI fragment (paths, schemas, error responses as RFC 7807)
```

```ts
// Shared TypeScript types if the UI consumes this
```

## 3. Data

Tables / columns / indexes added or changed. Migration + rollback notes. Backfill if any.

## 4. Acceptance criteria

- AC-1: Given … When … Then …
- AC-2: …
(Every AC must map to at least one test named after it.)

## 5. Non-functional requirements

- Latency: p95 ≤ … ms
- Cost: ≤ … (LLM tokens / AWS)
- Logs (events): `…`, `…`
- Metrics: `capsule_<service>_…`
- Security / authz: who may call this; rate limits
- Privacy: PII handling

## 6. Out of scope

Explicit list. Anything here found in the PR is a scope violation.

## 7. Task split

| # | PR title | Role | Depends on | Est. lines |
|---|---|---|---|---|

## 8. Open questions
