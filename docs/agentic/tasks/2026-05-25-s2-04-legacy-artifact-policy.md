---
task_id: 2026-05-25-s2-04-legacy-artifact-policy
status: complete
request: "Define S2-04 legacy archive migration and exemption policy before any default Agentic artifact gate enforcement."
scope: docs
risk: medium
owning_agent: gcs-quality-steward
specialist_agents:
  - task-scoped-session-closer
affected_contracts:
  - Agentic artifact opt-in quality gates
  - Completed-task archive discoverability
  - Lifecycle low-risk boundary
affected_paths:
  - docs/agentic/legacy-artifact-policy.md
  - docs/agentic/quality-gate-opt-in-policy.md
  - docs/completed-tasks/README.md
  - docs/agentic/agile-pdca-roadmap.md
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - score-closure-report
  - run-quality-gates opt-in artifact selection
  - validate-docs
human_gate_required: false
human_gate_reason: ""
---

# S2-04 Legacy Artifact Policy

## Scope

Define how legacy task cards and completed-task archives are classified,
exempted, or migrated now that S2-02 and S2-03 have made Agentic artifact gates
executable.

## Non-Goals

- Do not migrate the whole historical archive tree.
- Do not treat old narrative records as failed current tasks.
- Do not change default `run-quality-gates` behavior in this step.
- Do not touch solver/runtime/IO/viewer behavior.
- Do not include unrelated UI/item4 work from the foreground checkout.

## Context To Read

- `docs/agentic/lifecycle-runbook.md`
- `docs/agentic/quality-gate-opt-in-policy.md`
- `docs/completed-tasks/README.md`
- `.codex/skills/task-scoped-session-closer/SKILL.md`
- `.codex/skills/gcs-quality-steward/SKILL.md`

## Acceptance Gates

- A legacy artifact policy names current, migratable legacy, narrative legacy,
  low-risk no-archive, and parallel-session states.
- The completed-task index documents the policy labels and how future agents
  should use them.
- The opt-in gate policy records that S2-04 is complete.
- This task closes through its own include-gate cycle.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-s2-04-legacy-artifact-policy.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-s2-04-legacy-artifact-policy\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-s2-04-legacy-artifact-policy\README.md --min-score 30
python tools\agentic_design\agentic_toolkit.py run-quality-gates --skip-build --skip-ctest --skip-cli --include-task-cards docs\agentic\tasks\2026-05-25-s2-04-legacy-artifact-policy.md --include-completed-reports docs\completed-tasks\2026-05-25-s2-04-legacy-artifact-policy
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

- This task's focused verification is recorded in its completed-task archive.

## Residual Risks

- S2-05 must still decide whether any checks become default.
- The policy intentionally avoids historical bulk migration, so some old
  records remain useful but validator-exempt.
