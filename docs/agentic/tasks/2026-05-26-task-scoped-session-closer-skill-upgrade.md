---
task_id: 2026-05-26-task-scoped-session-closer-skill-upgrade
status: complete
request: "Upgrade the task-scoped-session-closer skill so it explicitly supports session summary, experience/skill/agent evaluation, completed-task collection, and push."
scope: docs
risk: low
owning_agent: task-scoped-session-closer
specialist_agents:
  - task-scoped-session-closer
affected_contracts:
  - project skill trigger metadata
  - completed-task archive
  - agentic experience library
affected_paths:
  - .codex/skills/task-scoped-session-closer/SKILL.md
  - .codex/skills/task-scoped-session-closer/agents/openai.yaml
  - docs/agentic/experience/001-task-scoped-session-closure/README.md
  - docs/agentic/experience/001-task-scoped-session-closure/agents/session-closure-agent.md
  - docs/agentic/tasks/2026-05-26-task-scoped-session-closer-skill-upgrade.md
  - docs/completed-tasks/2026-05-26-task-scoped-session-closer-skill-upgrade/
  - docs/completed-tasks/README.md
required_evidence:
  - skill.quick-validate
  - agentic.validate-task-card
  - agentic.validate-completed-task-report
  - agentic.score-closure-report
  - agentic.validate-docs
  - agentic.validate-skills
human_gate_required: false
human_gate_reason: ""
---

## Scope

Upgrade the active project closeout skill so future sessions can satisfy the
request pattern:

1. Summarize the current session.
2. Evaluate whether it produced experience, skill, or institutional-agent
   material.
3. Collect that evaluation into completed tasks.
4. Preserve promotion or deferral thresholds for later reuse.

## Non-Goals

- Do not create a new skill; update the active E001-derived skill.
- Do not create a new institutional agent.
- Do not edit solver, runtime, IO, viewer, fixture, or scene behavior.
- Do not stage unrelated OpusTime, narrative visualization, demo, or report
  worktree changes.

## Context To Read

- `.codex/skills/task-scoped-session-closer/SKILL.md`
- `docs/agentic/experience/001-task-scoped-session-closure/README.md`
- `docs/agentic/experience/001-task-scoped-session-closure/agents/session-closure-agent.md`
- `docs/completed-tasks/2026-05-26-repository-audit-session-closeout/README.md`
- System skill reference: `skill-creator`

## Acceptance Gates

- Skill metadata triggers on session summary and experience/skill/agent
  evaluation requests.
- Skill workflow and guardrails require an explicit promotion or deferral
  decision when that evaluation is requested.
- E001 documents the upgraded capability in a durable project location.
- The completed-task archive records this upgrade and validation evidence.
- Changes are committed and pushed without staging unrelated dirty files.

## Verification Plan

```bat
python C:\Users\QR\.codex\skills\.system\skill-creator\scripts\quick_validate.py .codex\skills\task-scoped-session-closer
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-task-scoped-session-closer-skill-upgrade.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-task-scoped-session-closer-skill-upgrade\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-task-scoped-session-closer-skill-upgrade\README.md --min-score 30
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-skills
```

## Evidence Bundle

Evidence is recorded in the completed-task archive after commands run.

## Residual Risks

- This upgrade relies on procedural skill guidance rather than a new automated
  validator for the experience/skill/agent section.
- Future hardening may add a completed-report schema check for session-learning
  evaluations after the pattern is reused.
