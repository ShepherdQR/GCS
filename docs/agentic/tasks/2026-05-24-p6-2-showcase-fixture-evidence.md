---
task_id: 2026-05-24-p6-2-showcase-fixture-evidence
status: complete
request: "Promote the P6.2 showcase fixture evidence for rank, gluing, replay, and diagnostics."
scope: tool
risk: medium
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-scientific-figure-producer
affected_contracts:
  - GCS Evidence-First Interface Grammar
  - GCS Scientific Figure Pipeline
  - GCS Visual Integrity Gate
  - GCS Warm Evidence Tokens
affected_paths:
  - fixtures/scene/showcase/
  - tools/architecture_visualization/showcase_fixture_evidence.py
  - tools/agentic_design/agentic_toolkit.py
  - tests/tools/
required_evidence:
  - showcase-fixture-evidence-current
  - missing-panel-fixture-fails
  - rank-mismatch-fixture-fails
  - negative-report-code-fixture-fails
  - public-quality-gate-registration
human_gate_required: false
human_gate_reason: ""
---

# P6.2 Showcase Fixture Evidence

## Scope

Promote the existing showcase fixture metadata into an explicit evidence bundle
that names the P6.1 brief, required panels, canonical tokens, rank/residual
expectations, gluing, diagnostics, replay-boundary gates, and negative rejection
evidence.

## Non-Goals

- Do not alter the scene geometry or constraints.
- Do not regenerate Figure 72.
- Do not add external renderer dependencies.
- Do not decide Figma MCP.

## Context To Read

- `docs/architecture/88-p6-1-integrated-showcase-brief.md`
- `fixtures/scene/showcase/integrated_feature_showcase.metadata.json`
- `fixtures/scene/showcase/integrated_feature_showcase_missing_fixed.metadata.json`
- `tools/agentic_design/agentic_toolkit.py`

## Execution Plan

1. Enrich positive and negative showcase metadata with P6.1 evidence fields.
2. Add a standard-library fixture evidence checker.
3. Add forced missing-panel, rank-mismatch, and report-code mismatch tests.
4. Promote the checker and tests into default quality gates.
5. Update fixture docs, quality-gate docs, roadmap, archive, and process
   learning.
6. Validate with public evidence gates and commit.

## Acceptance Gates

- Current fixture evidence metadata passes.
- Missing required panel fixture fails.
- Rank mismatch fixture fails.
- Negative report-code mismatch fixture fails.
- Default quality gates include the showcase fixture evidence checker and
  tests.
- Public evidence chain and CLI showcase smoke pass.

## Verification Plan

```bat
python -B tools\architecture_visualization\showcase_fixture_evidence.py
python -m unittest tests.tools.test_showcase_fixture_evidence
python -m unittest tests.tools.test_agentic_toolkit
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p6-2-showcase-fixture-evidence.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p6-2-showcase-fixture-evidence\README.md
python tools\agentic_design\agentic_toolkit.py run-quality-gates
git diff --check
```

## Evidence Bundle

- Pending final validation after implementation.

## Residual Risks

- Metadata checks do not replace runtime CTest/CLI evidence.
- P6.3 still needs to consume the metadata in a production figure.
