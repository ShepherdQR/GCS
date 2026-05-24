---
task_id: 2026-05-24-p6-3-showcase-figure-pipeline
status: complete
request: "Produce the P6.3 showcase figure through the scientific figure pipeline and tokenized HTML compositor."
scope: tool
risk: medium
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
  - tools/architecture_visualization/
  - docs/architecture/70-visualization/assets/
  - tools/ui_qa/
  - tests/tools/
required_evidence:
  - showcase-html-compositor-check
  - showcase-html-compositor-tests
  - text-overflow-current-html
  - overlap-contrast-current-html
  - token-lint
  - default-quality-gate-registration
human_gate_required: false
human_gate_reason: ""
---

# P6.3 Showcase Figure Pipeline

## Scope

Add a tokenized HTML compositor and generated Figure 72 HTML artifact that
consume the P6.1 brief and P6.2 fixture evidence.

## Non-Goals

- Do not install Figma or MCP tooling.
- Do not add graph/chart dependencies.
- Do not remove the legacy Figure 72 SVG.
- Do not add a Figure 72 screenshot baseline.

## Context To Read

- `docs/architecture/88-p6-1-integrated-showcase-brief.md`
- `docs/architecture/89-p6-2-showcase-fixture-evidence.md`
- `fixtures/scene/showcase/integrated_feature_showcase.metadata.json`
- `docs/architecture/87-p5-visual-integrity-phase-close.md`

## Execution Plan

1. Add a Figure 72 semantic spec.
2. Add a tokenized HTML compositor that consumes scene and metadata evidence.
3. Generate the Figure 72 HTML artifact.
4. Extend text-overflow and overlap/contrast gates to scan Figure 72 HTML.
5. Promote compositor freshness and tests into default quality gates.
6. Update atlas, roadmap, archive, and process learning.
7. Validate with visual-integrity and full quality gates.

## Acceptance Gates

- Figure 72 HTML is generated and up to date.
- Compositor tests pass.
- Text overflow passes across Figure 71 and Figure 72 HTML.
- Overlap/contrast passes across Figure 71 and Figure 72 HTML.
- Token lint passes.
- Default quality gates include the compositor check and tests.

## Verification Plan

```bat
python -B tools\architecture_visualization\showcase_scene_html_compositor.py --check
python -m unittest tests.tools.test_showcase_scene_html_compositor
python -B tools\ui_qa\gcs_text_overflow.py
python -B tools\ui_qa\gcs_overlap_contrast.py
python -B tools\ui_qa\gcs_token_lint.py
python -m unittest tests.tools.test_agentic_toolkit
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p6-3-showcase-figure-pipeline.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p6-3-showcase-figure-pipeline\README.md
python tools\agentic_design\agentic_toolkit.py run-quality-gates
git diff --check
```

## Evidence Bundle

- Pending final validation after implementation.

## Residual Risks

- Figure 72 does not yet have a browser-rendered PNG/PDF baseline.
- P6.4 still needs to decide whether Figma MCP adds value beyond the HTML
  production path.
