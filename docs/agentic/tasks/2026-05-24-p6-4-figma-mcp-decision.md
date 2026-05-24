---
task_id: 2026-05-24-p6-4-figma-mcp-decision
status: complete
request: "Decide whether to install or configure Figma MCP after P5/P6 repo-native visual QA work."
scope: architecture
risk: medium
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-scientific-figure-producer
  - gcs-third-party-governance-steward
affected_contracts:
  - GCS Scientific Figure Pipeline
  - GCS Visual Integrity Gate
  - GCS Art Director Review
affected_paths:
  - docs/architecture/91-p6-4-figma-mcp-decision.md
  - docs/architecture/76-ui-design-system-execution-plan.md
  - docs/architecture/82-ui-design-next-work-plan.md
required_evidence:
  - figma-official-docs-checked
  - third-party-decision-recorded
  - validate-task-card
  - validate-completed-task-report
  - validate-docs
  - git-diff-check
human_gate_required: false
human_gate_reason: ""
---

# P6.4 Figma MCP Decision

## Scope

Decide whether Figma MCP should be installed or configured now that P5 visual
integrity gates and the P6 showcase HTML artifact exist.

## Non-Goals

- Do not install Figma MCP.
- Do not configure MCP client settings.
- Do not create a Figma file.
- Do not add unofficial Figma MCP packages.

## Context To Read

- `docs/architecture/90-p6-3-showcase-figure-pipeline.md`
- `docs/architecture/87-p5-visual-integrity-phase-close.md`
- `docs/architecture/50-implementation/third-party-policy.md`
- Figma official MCP documentation.

## Execution Plan

1. Check official Figma MCP documentation for current remote/desktop guidance.
2. Compare Figma MCP value against the repo-native Figure 72 HTML pipeline.
3. Record a `ThirdPartyDecision` with provider order, license/version boundary,
   CMake/runtime impact, offline behavior, and future audit gates.
4. Update roadmap, archive, and process learning.
5. Validate and commit the decision docs.

## Acceptance Gates

- Decision explicitly says install now, pilot later, or defer.
- Provider order and offline behavior are recorded.
- No dependency or MCP configuration is added accidentally.
- Future pilot conditions are explicit.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p6-4-figma-mcp-decision.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p6-4-figma-mcp-decision\README.md
python tools\agentic_design\agentic_toolkit.py validate-docs
git diff --check -- docs/architecture docs/agentic/tasks docs/completed-tasks
```

## Evidence Bundle

- Figma official docs checked.
- Decision: defer install/configuration now; allow only a future explicit pilot.

## Residual Risks

- Figma MCP capabilities and access terms may change; revisit from official
  docs before any future pilot.
- This decision does not create a browser PNG/PDF baseline for Figure 72.
