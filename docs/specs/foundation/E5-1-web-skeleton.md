# Spec: web skeleton
- Epic: foundation · Status: approved · Phase: 1 · Related: ADR-0002

## 1. Goal
Next.js 15 App Router app with Clerk auth, design tokens from the client's design, feature-folder structure,
and the test/lint/typecheck toolchain, so every later UI task starts from a green, conventional base.

## 2. Contract
`apps/web`: TypeScript strict, Tailwind, shadcn/ui initialised (button, card, input), `src/app/` routes:
`/` (public landing placeholder), `/sign-in`, `/sign-up` (Clerk components), `/store` (protected placeholder
"My Store"), `/looks` and `/stylist` (protected placeholders). `middleware.ts` protects everything except `/`,
sign-in/up and `/api/health`. `src/features/` exists with a README describing the folder convention.
Design tokens in `tailwind.config.ts` + CSS variables (`--color-primary`, `--color-surface`, radius, font)
taken from the design file — the lead supplies the values in the brief. Env validated with `@t3-oss/env-nextjs` or zod
in `src/env.ts` (fails build if `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` missing). Scripts: `dev, build, lint, typecheck, test`.
Vitest + Testing Library + jsdom configured with one component test; ESLint (next/core-web-vitals + typescript).
`GET /api/health` route returning `{status:"ok"}` for later synthetic checks.

## 4. Acceptance criteria
- AC-1: Unauthenticated visit to `/store` redirects to `/sign-in`; `/` renders without auth.
- AC-2: After sign-in, `/store` renders a page with the user's name from Clerk.
- AC-3: `pnpm typecheck`, `pnpm lint`, `pnpm test` are green; `pnpm build` succeeds with the example env.
- AC-4: Missing `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` fails `pnpm build` with a readable message.
- AC-5: Tokens are used via CSS variables, not hard-coded hex, in every component added today (grep-able).
- AC-6: `/api/health` returns 200 JSON.

## 5. NFR — Lighthouse performance ≥ 90 on `/` locally; no client component where a server component works.
## 6. Out of scope — any API call to core-api, item wizard, generated client, i18n, PostHog.
## 7. Task split — one PR, ≤ 400 lines excluding lockfile and shadcn-generated files (list them in the PR). Role: implementer.