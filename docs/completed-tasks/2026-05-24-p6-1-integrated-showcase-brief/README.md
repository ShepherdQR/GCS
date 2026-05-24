---
task_id: 2026-05-24-p6-1-integrated-showcase-brief
status: complete
session_goal: "Define the P6.1 integrated showcase brief before fixture or figure changes."
archive_target: docs/completed-tasks/2026-05-24-p6-1-integrated-showcase-brief/
experience_links:
  - docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p6-1-integrated-showcase-brief-forging-note.md
---

# P6.1 Integrated Showcase Brief

## Task Objective

Define the integrated feature constraint graph showcase so P6.2 fixture work
and P6.3 figure production share one claim, evidence vocabulary, and review
standard.

## Scope And Non-Goals

In scope:

- write the showcase brief;
- name the five-second claim, audience, source evidence, vocabulary, panels,
  and art-direction review questions;
- update the roadmap so P6.2 is next;
- archive the step.

Out of scope:

- editing showcase fixtures;
- regenerating Figure 72;
- adding visual QA tools;
- deciding Figma MCP.

## Interaction Summary

P5 closed with executable visual-integrity gates. P6.1 starts the showcase
phase by defining what the integrated artifact must prove before changing the
fixture or renderer.

## Work Completed

- Added `docs/architecture/88-p6-1-integrated-showcase-brief.md`.
- Marked P6.1 as done in `76-ui-design-system-execution-plan.md`.
- Updated `82-ui-design-next-work-plan.md` so P6.2 is next.
- Added this completed-task archive and a Bladesmith process note.

## Files And Artifacts

- `docs/architecture/88-p6-1-integrated-showcase-brief.md`
- `docs/architecture/76-ui-design-system-execution-plan.md`
- `docs/architecture/82-ui-design-next-work-plan.md`
- `docs/agentic/tasks/2026-05-24-p6-1-integrated-showcase-brief.md`
- `docs/completed-tasks/2026-05-24-p6-1-integrated-showcase-brief/README.md`

## Evidence

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p6-1-integrated-showcase-brief.md
Passed.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p6-1-integrated-showcase-brief\README.md
Passed.

python tools\agentic_design\agentic_toolkit.py validate-docs
Passed.

python -m unittest tests.tools.test_showcase_scene_renderer
Ran 3 tests.
OK

git diff --check -- docs/architecture docs/agentic/tasks docs/completed-tasks
Passed with only existing CRLF conversion warnings.
```

## Decisions

- Decision: P6.1 is a brief-only step. Rationale: changing fixture or figure
  assets before naming the claim would make the showcase drift toward manual
  polish.
- Decision: make the negative missing-fixed variant a required panel. Rationale:
  solver credibility needs rejection evidence, not only happy-path acceptance.
- Decision: use P5 gates as P6 production constraints. Rationale: showcase
  assets should prove the visual-integrity system, not bypass it.

## Skipped Checks And Risks

- Full build and CTest were skipped because this was documentation-only brief
  work and P5.4 already ran the full quality gates.
- P6.1 does not prove fixture completeness; P6.2 owns that.
- P6.1 does not prove final figure quality; P6.3 owns that.

## Follow-Up

- Execute P6.2 showcase fixture evidence.
- Then produce the P6.3 showcase figure before the P6.4 Figma MCP decision.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-24-p6-1-integrated-showcase-brief/`
- Related experience:
  - `docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p6-1-integrated-showcase-brief-forging-note.md`
- Skill, eval, fixture, or tool update needed: P6.2 should promote fixture
  evidence in a way the renderer can consume directly.
