---
task_id: 2026-05-24-agentic-se-experience-library
status: complete
session_goal: "Create a folder-based agentic-SE experience library and promote the first task-closure experience."
archive_target: docs/completed-tasks/2026-05-24-agentic-se-experience-library/
experience_links:
  - docs/agentic/experience/001-task-scoped-session-closure/
---

# Agentic SE Experience Library

## Task Objective

Create a durable folder for practical agentic-SE lessons discovered during GCS
work, define the folder-per-experience convention, and summarize the first
experience: task-scoped sessions must end with an execution report before
archive.

## Scope And Non-Goals

In scope:

- define the `docs/agentic/experience/` folder contract;
- create the first experience as a subfolder;
- include related candidate skill, agent role card, and templates;
- update the agentic README and experience record template to point at the new
  convention;
- archive this task with an execution report.

Out of scope:

- installing the candidate skill as an active `.codex/skills` skill;
- adding validators or CI gates for completed-task reports;
- changing solver runtime, architecture contracts, or C++ source.

## Interaction Summary

The session began from a request to formalize a project-local experience
library for agentic-SE practice. Existing documentation already contained
`docs/agentic/experience/`, so the work reused that path instead of creating a
parallel knowledge store. The first experience was generalized from a process
observation into a reusable operating model: every non-trivial session should
have a task goal, multi-turn execution discipline, a task execution report, and
an archive handoff.

## Work Completed

- Converted `docs/agentic/experience/` into a folder-per-experience library.
- Added E001, "Task-scoped session closure", with problem statement, theory
  lift, invariants, completion criteria, and promotion path.
- Added a candidate skill for session closure discipline.
- Added a session closure agent role card.
- Added a task execution report template and archive checklist.
- Updated agentic docs so closure reporting appears in the minimum workflow.
- Created this completed-task archive to practice the new rule immediately.

## Files And Artifacts

- `docs/agentic/experience/README.md`: folder contract and index.
- `docs/agentic/experience/001-task-scoped-session-closure/README.md`: first
  promoted experience and theory summary.
- `docs/agentic/experience/001-task-scoped-session-closure/skills/task-scoped-session-closer/SKILL.md`:
  candidate skill material.
- `docs/agentic/experience/001-task-scoped-session-closure/agents/session-closure-agent.md`:
  agent role card.
- `docs/agentic/experience/001-task-scoped-session-closure/templates/task-execution-report.md`:
  reusable report template.
- `docs/agentic/experience/001-task-scoped-session-closure/templates/archive-checklist.md`:
  archive checklist.
- `docs/agentic/README.md`: minimum workflow update.
- `docs/agentic/experience-record-template.md`: note that promoted lessons live
  as folder README records with supporting materials.
- `docs/completed-tasks/2026-05-24-agentic-se-experience-library/README.md`:
  this task execution report.

## Evidence

```text
python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed
```

## Decisions

- Reused `docs/agentic/experience/` because the project already treats
  `docs/agentic` as the executable operating layer for agentic workflow.
- Used one folder per experience so a lesson can carry theory, skill material,
  agent material, templates, and future evidence together.
- Kept the candidate closure skill inside the experience folder rather than
  installing it as an active project skill before it has repeated use.
- Archived this task under `docs/completed-tasks/` to apply the experience
  immediately.

## Skipped Checks And Risks

- Full C++ build and CTest were skipped because this was a documentation-only
  workflow change.
- No validator currently enforces completed-task report shape; this remains a
  future tool opportunity.
- The candidate skill is not active until promoted or copied into `.codex/skills`.

## Follow-Up

- Add a validator for completed-task reports if the archive grows enough to
  need enforcement.
- Consider promoting `task-scoped-session-closer` into `.codex/skills` after it
  proves useful across more than one task.
- Add a closure-evidence eval where an agent must refuse to mark a task done
  when report evidence is missing.

## Archive Handoff

- Archive path: `docs/completed-tasks/2026-05-24-agentic-se-experience-library/`
- Related experience: `docs/agentic/experience/001-task-scoped-session-closure/`
- Skill update needed: not yet; candidate skill is staged as experience
  material.
