---
task_id: 2026-05-26-ai-organization-narrative-execution
status: complete
request: "Execute the planned AI organization narrative tasks: operating map, institutional-agent registry scorecard, governance eval roadmap, and task-closure demo; push scoped docs."
scope: docs
risk: medium
owning_agent: gcs-architecture-steward
specialist_agents:
  - gcs-quality-steward
  - task-scoped-session-closer
affected_contracts:
  - none
affected_paths:
  - docs/agentic/
  - docs/product/demos/
  - docs/completed-tasks/
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - validate-docs
  - validate-inventory
  - validate-skills
  - check-dependencies
  - score-closure-report
human_gate_required: false
human_gate_reason: ""
---

# AI Organization Narrative Execution

## Scope

Create the next AI-organization narrative artifacts that were identified after
the narrative maturity audit:

- an operating map for the GCS agentic organization;
- an institutional-agent registry and maturity scorecard;
- a governance eval roadmap;
- an agentic task-closure demo package under product demos;
- safe index, metrics, narrative-map, and archive updates.

## Non-Goals

- Do not change solver runtime, IO, viewer, fixture, or C++ behavior.
- Do not promote any institutional agent without new reuse evidence.
- Do not add default quality-gate enforcement.
- Do not stage unrelated repository-audit, session-efficiency, or OpusTime
  worktree changes.

## Context To Read

- `docs/architecture/95-gcs-narrative-map.md`
- `docs/agentic/README.md`
- `docs/agentic/metrics-dashboard.md`
- `docs/agentic/permission-threat-matrix.md`
- `docs/agentic/institutional-agents/`
- `docs/agentic/evals/review-rubrics.md`
- `docs/agentic/evals/module-agent-evals.md`
- `docs/product/README.md`

## Acceptance Gates

- The AI-organization story is tied back to solver evidence instead of becoming
  a separate process narrative.
- The institutional-agent scorecard uses existing role artifacts and evidence.
- The governance eval roadmap turns the prior threat matrix into concrete eval
  candidates.
- The demo page explains task-card to archive closure as a user-visible
  capability.
- Changed docs are indexed and the completed-task archive is discoverable.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-ai-organization-narrative-execution.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-ai-organization-narrative-execution\README.md
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-ai-organization-narrative-execution\README.md --min-score 30
```

## Evidence Bundle

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-ai-organization-narrative-execution.md
[OK] task-card passed.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-ai-organization-narrative-execution\README.md
[OK] completed-task-report passed.

python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed.

python tools\agentic_design\agentic_toolkit.py validate-inventory
[OK] inventory: structured module inventory passed.

python tools\agentic_design\agentic_toolkit.py validate-skills
[OK] skills: all module skills passed.

python tools\agentic_design\agentic_toolkit.py check-dependencies
[OK] dependencies: import boundaries passed.

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-ai-organization-narrative-execution\README.md --min-score 30
Closure score: 39/40 after final evidence rewrite.
```

Final git staging review is required before commit. Known unrelated dirty or
untracked work includes repository-audit/session-efficiency paths and
`docs/research/OpusTime/OpusTime.md`; those paths must stay unstaged.

Skipped implementation checks:

- Build, CTest, CLI, and UI checks are outside the changed surface because this
  task edits documentation and process artifacts only.

## Residual Risks

- The scorecard is a current evidence snapshot; institutional-agent maturity can
  drift as new examples are added.
- The governance eval roadmap defines eval candidates but does not implement
  new automated validators in this batch.
- The closure demo is a product narrative artifact; future demo packages still
  need command transcripts, screenshots, or replay outputs when they become
  behavior demos.
