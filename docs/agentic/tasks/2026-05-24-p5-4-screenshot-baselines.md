---
task_id: 2026-05-24-p5-4-screenshot-baselines
status: complete
request: "Add the P5.4 screenshot baseline policy and first stable visual baseline."
scope: tool
risk: medium
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-scientific-figure-producer
affected_contracts:
  - GCS Visual Integrity Gate
  - GCS Scientific Figure Pipeline
  - GCS Warm Evidence Tokens
affected_paths:
  - tools/ui_qa/
  - docs/architecture/70-visualization/assets/
  - tools/agentic_design/agentic_toolkit.py
  - tests/tools/
required_evidence:
  - screenshot-baseline-current-manifest
  - missing-png-fixture-fails
  - dimension-mismatch-fixture-fails
  - hash-mismatch-fixture-fails
  - default-quality-gate-registration
human_gate_required: false
human_gate_reason: ""
---

# P5.4 Screenshot Baselines

## Scope

Add a durable screenshot-baseline policy and a first stable screenshot artifact
for the Figure 71 review PNG.

## Non-Goals

- Do not install a new browser automation service.
- Do not add Figma or MCP integration.
- Do not add perceptual image diffing.
- Do not redesign Figure 71.

## Context To Read

- `docs/architecture/70-visualization/overlap-contrast-gate.md`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-browser-export.json`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.review.png`

## Execution Plan

1. Add a screenshot-baseline manifest for stable PNG review artifacts.
2. Add a standard-library PNG baseline checker.
3. Add forced missing-file, dimension-mismatch, and hash-mismatch fixtures.
4. Promote the checker and tests into default quality gates.
5. Document the change policy for future baseline updates.
6. Update roadmap, archive, and process learning.

## Acceptance Gates

- Current screenshot baseline manifest passes.
- Missing PNG fixture fails.
- Dimension mismatch fixture fails.
- SHA256 mismatch fixture fails.
- Default quality gates include screenshot baseline checks.

## Verification Plan

```bat
python -B tools\ui_qa\gcs_screenshot_baseline.py
python -m unittest tests.tools.test_gcs_screenshot_baseline
python -m unittest tests.tools.test_agentic_toolkit
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p5-4-screenshot-baselines.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p5-4-screenshot-baselines\README.md
git diff --check
```

## Evidence Bundle

- Pending final validation after implementation.

## Residual Risks

- Exact SHA256 baselines are intentionally strict and will require deliberate
  updates when browser-rendered pixels change.
- Perceptual diffing remains a future enhancement, not a P5.4 dependency.
