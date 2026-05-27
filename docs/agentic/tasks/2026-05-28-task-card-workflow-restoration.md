---
task_id: 2026-05-28-task-card-workflow-restoration
status: complete
request: "Analyze why the task card workflow stopped running, then implement a three-layer defense to restore it."
scope: tool
risk: low
owning_agent: gcs-contract-tools-steward
specialist_agents:
  - gcs-quality-steward
affected_contracts:
  - none
affected_paths:
  - docs/agentic/default-agentic-gate-decision.md
  - docs/agentic/tasks/
  - tools/agentic_design/agentic_toolkit.py
  - CLAUDE.md
  - .claude/skills/session-close-orchestrator/SKILL.md
  - .gitignore
required_evidence:
  - validate-docs
  - validate-task-card
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-28-task-card-workflow-restoration

## Scope

Diagnose why the task card (计划卡) workflow stopped producing new cards after
2026-05-26, then implement a three-layer defense to restore it:

1. **Code gate** — `.claude/current-task` declaration mechanism, auto-detected by
   `run-quality-gates`, with `--require-task-card` for strict CI enforcement
2. **Behavior instruction** — CLAUDE.md "Task Card Requirement" section
3. **Process gate** — session-close-orchestrator Step 0: auto-create task card
   when missing during closeout

## Root Cause Analysis

Three decisions combined to cause the drift:

- S2-05 (2026-05-25) explicitly made task-card validation opt-in rather than
  a default quality gate ("keep opt-in today; allow a future current-task
  default only after the command has an explicit current-task artifact input")
- Lifecycle runbook Step 1.5 created a broad low-risk chat-only escape hatch
- Governance execution queue shifted focus from documentation to tooling,
  creating an "implement → archive directly" pattern

## Evidence Bundle

- `new-task-card --write` correctly writes `.claude/current-task` — verified
- `run-quality-gates` auto-detects and validates task card from `.claude/current-task` — verified
- `run-quality-gates --require-task-card` fails when no task card is declared — verified
- Python syntax validated via `ast.parse` — passed
- Commit `cbaf7ef`: 4 files, +126/-5 lines

## Residual Risks

- `--require-task-card` needs calibration on at least two non-documentation CI
  branches before it becomes the default for all CI presets
- The real test is whether future sessions naturally follow the "task card first"
  pattern rather than bypassing it
- `2026-05-24-agentic-operating-layer.md` remains the only draft card — should
  be updated to complete or archived
