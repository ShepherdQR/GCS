---
task_id: 2026-05-25-s4-05-institutional-agent-reassessment
status: complete
request: "Execute S4-05 by reassessing institutional agents after multiple real closures and updating the candidate table."
scope: docs
risk: medium
owning_agent: gcs-architecture-steward
specialist_agents:
  - task-scoped-session-closer
affected_contracts:
  - Institutional-agent operating standard
  - Agentic SE roadmap
affected_paths:
  - docs/agentic/institutional-agents/
  - docs/agentic/agile-pdca-roadmap.md
  - docs/agentic/near-term-agent-plan.md
  - docs/completed-tasks/
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - score-closure-report
  - validate-docs
human_gate_required: false
human_gate_reason: ""
---

# S4-05 Institutional-Agent Reassessment

## Scope

Reassess the standing institutional agents after multiple real closure samples
and the E001 active-skill promotion.

## Non-Goals

- Do not create a new institutional-agent directory.
- Do not install another skill.
- Do not modify solver, runtime, IO, viewer, fixture, or CTest behavior.
- Do not promote visual seed agents without real review artifacts.

## Context To Read

- `docs/agentic/institutional-agents/README.md`
- `docs/agentic/institutional-agents/OPERATING-STANDARD.md`
- `docs/agentic/institutional-agents/001-bladesmith-quench-forge/`
- `docs/agentic/institutional-agents/002-tailor-stitch-timeline/`
- `docs/agentic/institutional-agents/003-atelier-steward-calibrate-review/README.md`
- `docs/agentic/institutional-agents/004-art-director-frame-judge/README.md`
- `docs/agentic/agile-pdca-roadmap.md`

## Acceptance Gates

- Reassessment record exists.
- Institutional-agent index reflects current evidence status.
- Bladesmith and Tailor are upgraded only according to real artifacts.
- Atelier Steward and Art Director remain seed roles with clear next actions.
- No new candidate role directory is created.
- Completed-task archive validates and scores at or above 30.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-s4-05-institutional-agent-reassessment.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-s4-05-institutional-agent-reassessment\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-s4-05-institutional-agent-reassessment\README.md --min-score 30
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

- `validate-task-card`: passed.
- `validate-completed-task-report`: passed.
- `score-closure-report`: passed at 35/40.
- `validate-docs`: passed.

## Residual Risks

- Bladesmith has many examples, but some older example role labels are not
  perfectly normalized.
- Atelier Steward and Art Director still need real prompt/template/eval
  packages before promotion.
