# ADR-0001: Single monorepo for all apps, services and infrastructure

- Status: accepted
- Date: 2026-09-24
- Deciders: Oleksii (lead)

## Context

One lead directing AI agents across a Next.js app, two Python services, two Go services and Terraform.
Agents have no memory between sessions; the repository is their only shared context. Cross-service
contracts (OpenAPI → generated clients) change often in the first month.

## Options considered

1. **Monorepo** — one clone gives an agent the whole picture; one CI; atomic contract changes; simple CODEOWNERS.
   Cons: CI must be path-filtered; tooling for three languages in one tree.
2. **Repo per service** — clean ownership, independent CI. Cons: contract drift, 5× the CLAUDE.md upkeep,
   agents cannot see the consumer of what they change.

## Decision

Monorepo `wardrobe-ai` with `apps/`, `services/`, `packages/`, `infra/`, `docs/`. Path-filtered workflows per area.

## Consequences

- Positive: Agents read specs, contracts and consumers in one place.
- Positive: One PR can change a contract and both sides.
- Negative: CI config is more complex.
- Negative: Repo size grows; enforce ≤ 400-line PRs and no binaries (golden images go to S3/LFS).

## How we would know this was wrong

CI > 15 min despite path filters; frequent unrelated-area conflicts; a second team needing separate release cadence.
