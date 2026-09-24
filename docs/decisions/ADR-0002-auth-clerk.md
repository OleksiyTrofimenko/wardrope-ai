# ADR-0002: Clerk for authentication, JWT verified in every backend

- Status: accepted
- Date: 2026-09-24
- Deciders: Oleksii (lead)

## Context
Four-week window; auth is not a differentiator; every backend (FastAPI ×2, Go ×2) must verify identity;
users must be mirrored into Postgres for relations (items, listings, looks).

## Options considered
1. **Clerk** — hosted UI, Next.js SDK, JWKS, webhooks. ~½ day. Cons: vendor dependency, cost at scale, EU data residency to check.
2. **AWS Cognito** — fits Terraform/AWS learning goal; free tier generous. Cons: clunky hosted UI, ~2 extra days, weaker Next.js DX.
3. **Auth.js self-managed** — full control. Cons: we own password/security surface; slowest.

## Decision
Clerk. Backends verify the session JWT against Clerk JWKS (`pyjwt` / `lestrrat-go/jwx`); a Clerk webhook
upserts `users`. All authz decisions use our own `users.id`, never Clerk ids, so the provider is swappable.

## Consequences
+ Auth done on Day 1. + Provider isolated behind one dependency per service.
− Vendor lock at the edge; migration would need a user export + re-login.

## How we would know this was wrong
Clerk cost > 5 % of infra bill; EU compliance requirement Clerk cannot meet; outage impact > 1 h/month.
