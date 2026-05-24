---
task_id: 2026-05-24-p5-3-overlap-contrast-gates
status: complete
request: "Add the P5.3 overlap and contrast gates for generated figure HTML."
scope: tool
risk: medium
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-scientific-figure-producer
affected_contracts:
  - GCS Scientific Figure Pipeline
  - GCS Visual Integrity Gate
  - GCS Warm Evidence Tokens
affected_paths:
  - tools/ui_qa/
  - tools/architecture_visualization/figure71_html_compositor.py
  - docs/architecture/70-visualization/assets/
  - tools/agentic_design/agentic_toolkit.py
  - tests/tools/
required_evidence:
  - overlap-contrast-current-html
  - forced-overlap-fixture-fails
  - weak-contrast-fixture-fails
  - missing-marker-fixture-fails
  - figure-qa
human_gate_required: false
human_gate_reason: ""
---

# P5.3 Overlap And Contrast Gates

## Scope

Add executable source-level overlap and contrast checks for generated HTML
figures. The first landing instruments Figure 71 with layout boxes and
contrast targets.

## Non-Goals

- Do not add screenshot baselines; P5.4 owns them.
- Do not install browser automation, Figma, MCP, or graph/chart dependencies.
- Do not redesign Figure 71.
- Do not change solver/runtime/viewer behavior.

## Context To Read

- `docs/architecture/70-visualization/text-overflow-gate.md`
- `tools/ui_qa/gcs_text_overflow.py`
- `tools/architecture_visualization/figure71_html_compositor.py`

## Execution Plan

1. Add layout-box and contrast metadata to Figure 71 HTML output.
2. Add a standard-library overlap/contrast checker.
3. Add forced overlap, weak contrast, and missing-marker fixtures.
4. Promote the checker and tests into default quality gates.
5. Regenerate Figure 71 HTML and QA evidence.
6. Update roadmap, archive, and process learning.

## Acceptance Gates

- Current Figure 71 HTML passes.
- Forced overlap fixture fails.
- Forced low-contrast fixture fails.
- Missing-marker fixture fails.
- Default quality gates include the overlap/contrast checker and tests.

## Verification Plan

```bat
python -B tools\ui_qa\gcs_overlap_contrast.py
python -m unittest tests.tools.test_gcs_overlap_contrast
python -m unittest tests.tools.test_agentic_toolkit
python -B tools\architecture_visualization\figure_qa.py --figure figure71
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p5-3-overlap-contrast-gates.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p5-3-overlap-contrast-gates\README.md
git diff --check
```

## Evidence Bundle

- `gcs_overlap_contrast.py`: passed with six boxes and 21 contrast targets.
- `tests.tools.test_gcs_overlap_contrast`: passed.
- `tests.tools.test_agentic_toolkit`: passed after adding the new gate ids.
- Figure 71 QA passed after regenerating HTML.

## Residual Risks

- P5.3 checks declared design-grid boxes and contrast markers, not screenshot
  pixels.
- P5.4 remains responsible for stable screenshot baselines.
