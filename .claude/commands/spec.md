---
description: Draft a feature spec from a one-paragraph description (planner role)
argument-hint: <epic>/<feature> — one paragraph describing the feature
---
Act as the planner (`.claude/agents/planner.md`). Produce `docs/specs/$ARGUMENTS.md` from
`docs/specs/TEMPLATE.md`. Read the roadmap in `docs/architecture.md` and the current phase board first.
Do not write application code. End with the open questions for the lead.
