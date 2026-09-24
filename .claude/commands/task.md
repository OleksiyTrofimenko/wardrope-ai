---
description: Brief an implementer for one task from an approved spec
argument-hint: <service> <spec path> <AC ids> <allowed paths> <branch>
---
Act as the implementer (`.claude/agents/implementer.md`).
Service: $1. Spec: $2. Acceptance criteria to deliver: $3. You may touch only: $4. Branch: $5.
Existing tests to make pass live on branch `test/<same-epic-feature>` — do not modify them.
Post your 5–10 line plan and list ambiguities, then WAIT for my OK before writing code.
