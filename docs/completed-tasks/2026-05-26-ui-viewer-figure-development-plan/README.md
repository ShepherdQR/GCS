---
task_id: 2026-05-26-ui-viewer-figure-development-plan
status: complete
session_goal: "Saved the next-stage development plan for the UI/viewer/scientific-figure line, linked it from architecture and D5 demo docs, preserved the narrative map unchanged, and prepared a pushed handoff."
archive_target: docs/completed-tasks/2026-05-26-ui-viewer-figure-development-plan/
experience_links:
  - docs/agentic/experience/001-task-scoped-session-closure/
---

# 2026-05-26-ui-viewer-figure-development-plan

## Task Objective

Create and save the next development plan for the UI/viewer/scientific figures
line, push the result, and close out the task with a durable report.

## Scope And Non-Goals

In scope:

- A saved architecture development plan for the line after VE-001 and VE-002.
- Links from the active integration plan, design execution plan, architecture
  README, and D5 demo package.
- Task card, closeout report, validators, commit, and push.

Out of scope:

- `docs/architecture/95-gcs-narrative-map.md`.
- GUI, solver, report, or figure-generation implementation changes.
- Claiming future UVF milestones are already complete.

## Interaction Summary

The user asked to turn the next development path for the
UI/viewer/scientific-figure line into a saved plan, push it, and then run the
`codex-task-closeout` workflow. The work stayed on the existing isolated
integration branch and preserved the user's earlier boundary: do not rush
another narrative-map update.

## Work Completed

- Added `docs/architecture/98-ui-viewer-figure-development-plan.md`.
- Defined the milestone sequence:
  - UVF-01 viewer visual evidence hardening;
  - UVF-02 structured report projection;
  - UVF-03 constraint-manager projection;
  - UVF-04 workbench surface;
  - UVF-05 local-to-global evidence projection;
  - UVF-06 next scientific figure;
  - UVF-07 D5-to-D6 external reviewer story;
  - UVF-08 narrative reassessment.
- Linked the plan from:
  - `docs/architecture/97-ui-viewer-figure-integration-plan.md`;
  - `docs/architecture/76-ui-design-system-execution-plan.md`;
  - `docs/architecture/README.md`;
  - `docs/product/demos/d5-solver-evidence-workbench/README.md`.
- Added task card:
  `docs/agentic/tasks/2026-05-26-ui-viewer-figure-development-plan.md`.

## Files And Artifacts

- `docs/architecture/98-ui-viewer-figure-development-plan.md`: active
  next-stage roadmap for UVF-01 through UVF-08.
- `docs/architecture/97-ui-viewer-figure-integration-plan.md`: now points to
  the forward development plan.
- `docs/architecture/76-ui-design-system-execution-plan.md`: records the
  post-P7 handoff and narrative-map deferral rule.
- `docs/architecture/README.md`: indexes the new plan.
- `docs/product/demos/d5-solver-evidence-workbench/README.md`: links the D5
  next task to the new plan.
- `docs/agentic/tasks/2026-05-26-ui-viewer-figure-development-plan.md`: task
  card.
- `docs/completed-tasks/2026-05-26-ui-viewer-figure-development-plan/README.md`:
  closeout report.
- `docs/completed-tasks/README.md`: archive index entry.

## Evidence

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-ui-viewer-figure-development-plan.md
PASS.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-ui-viewer-figure-development-plan\README.md
Initial run failed because the report was missing project-required sections.
This report was updated and revalidated before commit.

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-ui-viewer-figure-development-plan\README.md --min-score 30
Initial run scored 23/40 because the report lacked artifact, risk, follow-up,
and archive-handoff sections. This report was updated and rescored before
commit.

python tools\agentic_design\agentic_toolkit.py validate-docs
PASS.

git diff --check
PASS with LF-to-CRLF working-copy warnings only.
```

## Decisions

- Keep `97-ui-viewer-figure-integration-plan.md` as the integration contract.
- Create `98-ui-viewer-figure-development-plan.md` as the staged development
  roadmap.
- Defer narrative-map updates until a new proof point lands, because a plan
  alone should not upgrade the maturity label.
- Keep the next work centered on report-to-viewer-to-figure evidence rather
  than on cosmetic UI expansion.

## Skipped Checks And Risks

- The plan is not implementation evidence. Future UVF milestones still need
  code, tests, visual artifacts, and task archives.
- The next true maturity reassessment depends on structured report projection
  or another end-to-end evidence chain, not on this document alone.
- No GUI, solver, or figure-generation tests were run because this task changed
  roadmap documentation only.

## Follow-Up

- Start with UVF-01 if the next priority is visual QA hardening and review.
- Start with UVF-02 if the next priority is structured solver-report evidence.
- Reassess the narrative map only after UVF-03 or UVF-06 produces a new
  validated proof point.

## Session Learning

- Experience: no new promotion. This reused the existing durable-planning and
  task-closeout pattern.
- Skill: no new promotion. Existing architecture, UI, figure, and closeout
  skills covered the task.
- Agent: no new promotion. Existing steward roles are sufficient.

## Final State

- Branch: `codex/2026-05-26-ui-viewer-figure-integration`
- Commit: pending at report creation; final commit hash is recorded in the
  chat handoff after commit.
- Push: pending at report creation; final push state is recorded in the chat
  handoff after push.

## Archive Handoff

- Task card:
  `docs/agentic/tasks/2026-05-26-ui-viewer-figure-development-plan.md`
- Archive path:
  `docs/completed-tasks/2026-05-26-ui-viewer-figure-development-plan/`
- Development plan:
  `docs/architecture/98-ui-viewer-figure-development-plan.md`
