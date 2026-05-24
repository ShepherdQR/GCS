---
task_id: 2026-05-24-p6-1-integrated-showcase-brief
status: complete
request: "Define the P6.1 integrated feature constraint graph showcase brief."
scope: architecture
risk: low
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-scientific-figure-producer
affected_contracts:
  - GCS Quiet Technical Atelier
  - GCS Warm Evidence Tokens
  - GCS Evidence-First Interface Grammar
  - GCS Scientific Figure Pipeline
  - GCS Visual Integrity Gate
  - GCS Art Director Review
affected_paths:
  - docs/architecture/88-p6-1-integrated-showcase-brief.md
  - docs/architecture/76-ui-design-system-execution-plan.md
  - docs/architecture/82-ui-design-next-work-plan.md
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - validate-docs
  - showcase-renderer-tests
  - git-diff-check
human_gate_required: false
human_gate_reason: ""
---

# P6.1 Integrated Showcase Brief

## Scope

Define the showcase claim, audience, source evidence, canonical evidence
vocabulary, required panels, and art-direction review questions before P6.2 or
P6.3 changes fixture or figure assets.

## Non-Goals

- Do not edit fixture JSON or metadata.
- Do not regenerate Figure 72.
- Do not add new visual QA tools.
- Do not decide Figma MCP.

## Context To Read

- `fixtures/scene/showcase/README.md`
- `fixtures/scene/showcase/integrated_feature_showcase.metadata.json`
- `docs/architecture/70-visualization/showcase-scene-report.md`
- `docs/architecture/87-p5-visual-integrity-phase-close.md`

## Execution Plan

1. Read existing showcase scene, metadata, renderer, report, and visual-token
   vocabulary.
2. Write the P6.1 showcase brief.
3. Mark P6.1 done and P6.2 next in the roadmap docs.
4. Archive the step and extract process learning.
5. Validate and commit the brief docs.

## Acceptance Gates

- Main claim, audience, source evidence, evidence vocabulary, required panels,
  and art-direction questions are explicit.
- P6.2 fixture evidence requirements are clear.
- P6.3 figure panel requirements are clear.
- P6.4 Figma MCP decision criteria are tied to the showcase artifact.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p6-1-integrated-showcase-brief.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p6-1-integrated-showcase-brief\README.md
python tools\agentic_design\agentic_toolkit.py validate-docs
python -m unittest tests.tools.test_showcase_scene_renderer
git diff --check -- docs/architecture docs/agentic/tasks docs/completed-tasks
```

## Evidence Bundle

- Showcase brief added.
- Existing showcase renderer tests remain green.
- P6.2 declared as next step.

## Residual Risks

- P6.1 defines the brief but does not prove the fixture or final figure.
- Art-direction approval remains pending until P6.3 renders the showcase.
