---
task_id: 2026-05-25-s2-01-opt-in-gate-policy
status: complete
session_goal: "Design opt-in task-card and completed-report quality-gate policy without default enforcement."
archive_target: docs/completed-tasks/2026-05-25-s2-01-opt-in-gate-policy
experience_links:
  - docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-25-s2-01-opt-in-gate-policy-forging-note.md
---

# S2-01 Opt-In Gate Policy

## Task Objective

Complete S2-01 by designing how Agentic SE task-card and completed-task report
validators should be included in quality gates on demand, without turning them
on by default for all historical artifacts.

## Scope And Non-Goals

In scope:

- design `--include-task-cards` and `--include-completed-reports` policy;
- name gate IDs, pathspec behavior, default behavior, and legacy exemptions;
- document implementation order for S2-02 through S2-05;
- update quality-gate docs, Agentic roadmap, near-term plan, and completed-task
  index;
- add a Bladesmith note.

Out of scope:

- no CLI flag implementation;
- no default quality-gate enforcement;
- no legacy archive migration;
- no E001 scorer threshold changes;
- no solver, runtime, IO, viewer, fixture, or CTest changes.

## Interaction Summary

After Step 50 closed the replay evidence workflow review, S2-01 became the
next Agentic SE tooling design task. The task was kept documentation-level
because S3-02 and S1-04 showed both sides of the policy: bad closure should be
catchable, but low-risk work must not be over-archived.

## Work Completed

- Added `docs/agentic/quality-gate-opt-in-policy.md`.
- Proposed `--include-task-cards <pathspec>` and
  `--include-completed-reports <pathspec>`.
- Named future gate IDs: `agentic.task-cards` and
  `agentic.completed-task-reports`.
- Defined repository-relative pathspec expansion and unmatched-path failure.
- Kept default `run-quality-gates` free of bulk archive validation.
- Deferred implementation to S2-02 and S2-03.
- Deferred legacy migration/exemption policy to S2-04.
- Updated the quality-gate architecture doc and roadmaps.

## Files And Artifacts

- `docs/agentic/quality-gate-opt-in-policy.md`
- `docs/agentic/README.md`
- `docs/agentic/tasks/2026-05-25-s2-01-opt-in-gate-policy.md`
- `docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-25-s2-01-opt-in-gate-policy-forging-note.md`
- `docs/architecture/69-ci-ready-quality-gates.md`
- `docs/agentic/agile-pdca-roadmap.md`
- `docs/agentic/near-term-agent-plan.md`
- `docs/completed-tasks/2026-05-25-s2-01-opt-in-gate-policy/README.md`
- `docs/completed-tasks/README.md`

## Evidence

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-s2-01-opt-in-gate-policy.md
[OK] task-card passed.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-s2-01-opt-in-gate-policy\README.md
[OK] completed-task-report passed.

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-s2-01-opt-in-gate-policy\README.md --min-score 30
Closure score: 36/40.

python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed.
```

## Decisions

- Use explicit pathspec flags instead of default tree-wide validation.
- Fail unmatched include pathspecs so an intended gate cannot silently pass.
- Keep closure scoring out of the initial completed-report gate until S2-03 or
  S2-05 calibrates whether it belongs in the gate.
- Treat legacy archives as exempt until S2-04 defines a migration or exemption
  policy.

## Skipped Checks And Risks

- No Python unit tests were added because S2-01 is design-only.
- The policy is not executable yet; S2-02 and S2-03 must add implementation
  and tests before workflow reliance.
- Full CTest was skipped because no executable behavior changed.

## Follow-Up

- S2-02: implement and test task-card include behavior.
- S2-03: implement and test completed-report include behavior for new reports.
- S2-04: document legacy archive migration or exemption policy.
- S3-04: decide whether E001 should remain an experience, become a skill, or
  stay provisional using this policy boundary.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-25-s2-01-opt-in-gate-policy`
- Related policy:
  `docs/agentic/quality-gate-opt-in-policy.md`
- Skill, eval, fixture, or tool update needed:
  S2-02 should add executable tests before implementing task-card include
  behavior.
