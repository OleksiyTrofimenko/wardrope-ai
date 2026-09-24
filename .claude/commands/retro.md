---
description: End-of-phase retro — turn repeated agent mistakes into rules and gates
argument-hint: <phase number>
---
Read `docs/agent-log.csv`, the merged PRs of phase $ARGUMENTS (`gh pr list --state merged`), and
`docs/phases/phase-$ARGUMENTS.md`. Produce: (1) the phase metrics snapshot filled in; (2) the three most
repeated review findings; (3) for each, a proposed rule for a `CLAUDE.md` or an automated CI gate;
(4) an updated exit-review section. Do not edit CLAUDE.md yourself — propose the diff.
