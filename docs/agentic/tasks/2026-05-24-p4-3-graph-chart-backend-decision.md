---
task_id: 2026-05-24-p4-3-graph-chart-backend-decision
status: complete
request: "Record the P4.3 graph/chart backend dependency decision before rebuilding Figure 71."
scope: architecture
risk: low
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-scientific-figure-producer
  - gcs-third-party-governance-steward
affected_contracts:
  - GCS Scientific Figure Pipeline
  - GCS Visual Integrity Gate
  - third-party dependency policy
affected_paths:
  - docs/architecture/84-p4-3-graph-chart-backend-decision.md
  - docs/architecture/76-ui-design-system-execution-plan.md
  - docs/architecture/82-ui-design-next-work-plan.md
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - dependency-decision-doc
  - token-lint-smoke
  - git-diff-check
human_gate_required: false
human_gate_reason: ""
---

# P4.3 Graph/Chart Backend Decision

## Scope

Decide whether P4.4 needs a new graph or chart backend before the execution-map
asset rebuild. Record the decision using the third-party governance contract:
dependency decision, provider order, license/version metadata state, CMake
impact, offline behavior, and future tests.

## Non-Goals

- Do not install graph, chart, browser, Figma, MCP, JavaScript, or Python
  packages.
- Do not rebuild Figure 71 assets; P4.4 owns that.
- Do not change build files or CMake target wiring.
- Do not change solver/runtime/viewer behavior.

## Context To Read

- `docs/architecture/74-scientific-figure-production-paradigm.md`
- `docs/architecture/76-ui-design-system-execution-plan.md`
- `docs/architecture/82-ui-design-next-work-plan.md`
- `docs/architecture/50-implementation/third-party-policy.md`
- `docs/architecture/62-module-agents.md` Third-Party Governance Agent section

## Execution Plan

1. Evaluate whether Figure 71 currently needs graph/chart backends.
2. Record a structured `ThirdPartyDecision` and provider order.
3. Update P4/P5 roadmap docs so P4.4 can proceed under the decision.
4. Archive the task and extract one reusable process lesson.
5. Validate docs and commit the P4.3 boundary.

## Acceptance Gates

- A structured decision doc exists.
- The decision explicitly approves or defers dependencies.
- CMake/runtime/offline behavior is stated.
- P4.4 next step is clear.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p4-3-graph-chart-backend-decision.md
python -B tools\ui_qa\gcs_token_lint.py
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p4-3-graph-chart-backend-decision\README.md
git diff --check -- docs/architecture docs/agentic/tasks docs/completed-tasks
```

## Evidence Bundle

- Decision doc added: `docs/architecture/84-p4-3-graph-chart-backend-decision.md`.
- P4.3 decision: defer external graph/chart dependencies for P4.4.
- P4.4 next step: rebuild Figure 71 with repo-native pipeline and existing
  token/QA gates.

## Residual Risks

- A future showcase figure may still need a real graph or chart backend; that
  future request must include dependency metadata and offline behavior.
- P4.3 does not improve visual output by itself; it prevents ungoverned
  dependency expansion before P4.4.
