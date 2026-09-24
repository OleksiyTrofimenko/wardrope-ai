---
description: Write failing tests from a spec only (test-engineer role)
argument-hint: <spec path>
---
Act as the test engineer (`.claude/agents/test-engineer.md`). Spec: $ARGUMENTS.
Do not read any feature branch. Write tests named after acceptance criteria, negative tests for every
contract rule, and an E2E outline if UI is involved. Deliver on branch `test/<epic>-<feature>`.
