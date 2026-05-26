---
task_id: 2026-05-26-task-scoped-session-closer-skill-upgrade
status: complete
session_goal: "Upgrade the task-scoped-session-closer skill to handle session summary plus experience/skill/agent evaluation and archive the change."
archive_target: docs/completed-tasks/2026-05-26-task-scoped-session-closer-skill-upgrade
experience_links:
  - docs/agentic/experience/001-task-scoped-session-closure/README.md
---

# Task-Scoped Session Closer Skill Upgrade

## Task Objective

Upgrade the active `task-scoped-session-closer` skill so it explicitly supports
requests to summarize a session, evaluate whether the session produced
experience, skill, or institutional-agent material, and collect that decision
into completed tasks.

## Scope And Non-Goals

In scope:

- Update the project skill trigger metadata and workflow.
- Update the skill UI metadata.
- Document the upgraded capability under E001, the source experience for the
  active skill.
- Update the session-closure role card with the same evaluation obligation.
- Add this task card and completed-task archive.

Out of scope:

- No new skill creation beyond hardening the existing active skill.
- No new institutional-agent promotion.
- No solver, runtime, IO, viewer, fixture, or scene behavior changes.
- No staging of unrelated local worktree changes.

## Interaction Summary

The user first asked whether the existing task closeout skill already covered
the prompt pattern "summarize this session, evaluate whether it produced
experience/skill/agent material, and collect it into completed tasks." The
analysis found partial coverage: E001 and the active skill already supported
completed-task archives and reusable experience notes, but the skill did not
make the experience/skill/agent decision an explicit required output.

This task upgrades the existing active skill instead of creating a parallel
skill. The durable capability statement is placed under E001 because E001 owns
the provenance and promotion path for `task-scoped-session-closer`.

## Work Completed

- Expanded `.codex/skills/task-scoped-session-closer/SKILL.md` so the
  description triggers on session summary, experience/skill/agent evaluation,
  and completed-task collection requests.
- Added archive requirements for a session-learning evaluation with
  experience, skill, and agent decisions.
- Added guardrails against over-promoting a skill or institutional agent from a
  single isolated example.
- Updated `.codex/skills/task-scoped-session-closer/agents/openai.yaml` with
  the new capability statement.
- Added an E001 capability section:
  `docs/agentic/experience/001-task-scoped-session-closure/README.md`.
- Updated the session closure agent role card to ask for explicit
  experience/skill/agent outcomes when requested.

## Files And Artifacts

- `.codex/skills/task-scoped-session-closer/SKILL.md`: active skill workflow
  and trigger metadata.
- `.codex/skills/task-scoped-session-closer/agents/openai.yaml`: UI-facing
  skill summary and default prompt.
- `docs/agentic/experience/001-task-scoped-session-closure/README.md`: durable
  capability explanation for the upgraded skill.
- `docs/agentic/experience/001-task-scoped-session-closure/agents/session-closure-agent.md`:
  role-card alignment.
- `docs/agentic/tasks/2026-05-26-task-scoped-session-closer-skill-upgrade.md`:
  task card.
- `docs/completed-tasks/2026-05-26-task-scoped-session-closer-skill-upgrade/README.md`:
  this archive.
- `docs/completed-tasks/README.md`: completed-task index entry.

## Experience, Skill, And Agent Evaluation

### Experience

Decision: active experience updated.

Target:
`docs/agentic/experience/001-task-scoped-session-closure/README.md`.

Reason: this is a refinement of E001's existing closure practice. The new
capability closes the gap found in the repository-audit session closeout: the
skill could create archives, but did not require an explicit
experience/skill/agent outcome when the user asked for that analysis.

### Skill

Decision: active skill updated.

Target:
`.codex/skills/task-scoped-session-closer/SKILL.md`.

Reason: the requested behavior belongs inside the already-promoted E001 closeout
skill. A separate skill would fragment closeout behavior; this update keeps the
session summary, archive, score, and learning evaluation in one closure loop.

### Agent

Decision: no new institutional agent.

Reason: the existing session-closure role card is sufficient after update.
Creating a separate agent would need repeated independent review demand and an
eval threshold.

Candidate future hardening: add a completed-report validation rule that checks
for an `Experience, Skill, And Agent Evaluation` section when a task card or
archive declares session-learning closeout as in scope.

## Evidence

```text
python C:\Users\QR\.codex\skills\.system\skill-creator\scripts\quick_validate.py .codex\skills\task-scoped-session-closer
ModuleNotFoundError: No module named 'yaml'

Fallback: ran the same quick_validate.py script with an in-memory yaml.safe_load
shim because PyYAML is not installed in either local Python runtime.
Skill is valid!

python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-task-scoped-session-closer-skill-upgrade.md
[OK] task-card: docs/agentic/tasks/2026-05-26-task-scoped-session-closer-skill-upgrade.md passed

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-task-scoped-session-closer-skill-upgrade\README.md
[OK] completed-task-report: docs/completed-tasks/2026-05-26-task-scoped-session-closer-skill-upgrade/README.md passed

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-task-scoped-session-closer-skill-upgrade\README.md --min-score 30
Closure score: 36/40
Passed the configured minimum.

python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed

python tools\agentic_design\agentic_toolkit.py validate-skills
[OK] skills: all module skills passed
```

## Decisions

- Upgrade the existing closeout skill rather than creating a second session
  learning skill.
- Treat the user's prompt as a first-class closeout trigger.
- Keep active skill and institutional-agent promotion evidence-gated.
- Store the capability explanation under E001 because E001 owns the active
  skill's provenance.

## Skipped Checks And Risks

- Full build and CTest are skipped because this task only updates skill and
  agentic documentation.
- There is not yet an automated validator for the new session-learning section.
  The skill now requires it procedurally; schema hardening is a follow-up.

## Follow-Up

- After two more session-learning closeouts, decide whether to add a validator
  rule for experience/skill/agent evaluation sections.
- If the section becomes common, add a template snippet to the E001 archive
  checklist.
- Keep monitoring whether separate roles are needed for skill promotion review;
  no new institutional agent is warranted from this single upgrade.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-26-task-scoped-session-closer-skill-upgrade`
- Experience updated:
  `docs/agentic/experience/001-task-scoped-session-closure/README.md`
- Active skill updated:
  `.codex/skills/task-scoped-session-closer/SKILL.md`
