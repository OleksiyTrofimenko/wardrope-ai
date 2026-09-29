## What
<!-- one paragraph; link the spec -->
Spec: `docs/specs/<epic>/<feature>.md` · Task: E?-? · Role: implementer | test-engineer | sre

## Acceptance criteria → tests

| AC | Test |
|---|---|
| AC-1 | `test_AC1_…` |

## What I deliberately did NOT do

-

## How to verify manually

1.

## Risks

-

## Definition of Done

- [ ] All ACs above have passing tests; no existing test assertion weakened or removed
- [ ] Lint, typecheck, tests, CI green
- [ ] Structured logs with `trace_id`; no secrets/PII in logs
- [ ] Metrics named per `docs/observability.md`
- [ ] Migration reversible (if any); seed updated (if needed)
- [ ] Error paths return problem details / typed errors; no bare `except`
- [ ] Docs updated (spec status, CLAUDE.md, ADR) if behaviour or conventions changed
- [ ] ≤ 400 changed lines, or split explained above
- [ ] Reviewer-agent findings addressed (link the review)
- [ ] Row appended to `docs/agent-log.csv`
