# wardrobe-ai — root CLAUDE.md

## What this is
Capsule: a peer-to-peer clothing exchange (sell / trade / borrow / gift) with an AI stylist that tags items from photos and composes looks. Architecture and rationale live in `docs/decisions/` and `docs/architecture.md`. 

The current phase board is `docs/phases/phase-1.md`.

**Read the linked spec in `docs/specs/` before starting any task.** If no spec exists, stop and ask.

## Non-negotiables
- Work only on the task in your brief. If the spec is unclear or incomplete, STOP and ask — never guess scope.
- Never edit, weaken, skip or delete existing test assertions. If a test is wrong, say so in the PR and wait.
- Never commit secrets, `.env` files, credentials or real user data. Use `.env.example`.
- Never push to `main`, never force-push, never rewrite shared history, never run destructive git or cloud commands
  (`git push --force`, `git reset --hard` on shared branches, `terraform destroy`, `aws s3 rm`, `DROP`).
- Every new endpoint, job or worker emits structured JSON logs with `trace_id` and the metrics named in `docs/observability.md`. A feature without logs and metrics is not done.
- Keep PRs ≤ 400 changed lines. If the task needs more, split it and say how in your plan.
- Prefer three similar lines over one premature abstraction. Add an abstraction only when a second real caller exists.

## Conventions
- Python 3.12, `uv`, `ruff`, `mypy --strict` on new code, `pytest`. Layering `api → services → repositories → models`, enforced by `import-linter`. All wiring through FastAPI `Depends()`; no module builds its own DB session or client.
- TypeScript strict. Next.js App Router, feature folders under `apps/web/src/features/<feature>/`.
  API calls only through the generated client in `packages/contracts`; hand-written `fetch` to our APIs fails lint.
- Go 1.23, `cmd/` + `internal/`, interfaces defined at the consumer, table-driven tests, `golangci-lint`.
- Errors: core-api returns RFC 7807 problem details; web maps them to typed error unions. No bare `except:`.
- Commits: Conventional Commits (`feat(core-api): add finalize-upload endpoint`). Branches: `feat|fix|chore|infra/<epic>-<short>`.
- Docs: a behavior change updates the relevant `docs/specs/*`; a convention change updates a `CLAUDE.md`; an
  architectural choice gets an ADR in `docs/decisions/` (MADR format, next free number).

## How to finish a task
1. `make lint` and `make test` green locally. Type checks clean.
2. Fill `.github/PULL_REQUEST_TEMPLATE.md` completely; map every acceptance criterion to a test name.
3. In the PR description: what changed, what you deliberately did NOT do, risks, and how to verify manually.
4. Append your task row to `docs/agent-log.csv` (the lead fills the review columns).

## Per-area rules
`apps/web/CLAUDE.md` · `services/core-api/CLAUDE.md` · `services/media-worker/CLAUDE.md` · `infra/CLAUDE.md`
(created in Phase 1 as each area is scaffolded).
