---
task_id: 2026-05-24-p5-2-text-overflow-gate
status: complete
request: "Add the P5.2 text overflow gate for generated UI and figure HTML."
scope: tool
risk: medium
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-scientific-figure-producer
affected_contracts:
  - GCS Scientific Figure Pipeline
  - GCS Visual Integrity Gate
affected_paths:
  - tools/ui_qa/
  - tools/architecture_visualization/figure71_html_compositor.py
  - docs/architecture/70-visualization/assets/
  - tools/agentic_design/agentic_toolkit.py
  - tests/tools/
required_evidence:
  - text-overflow-current-html
  - forced-overflow-fixture-fails
  - missing-budget-fixture-fails
  - figure-qa
  - quality-gate-sequence-test
human_gate_required: false
human_gate_reason: ""
---

# P5.2 Text Overflow Gate

## Scope

Add an executable text overflow budget gate for generated HTML figures. The
first landing instruments Figure 71 HTML with explicit text budgets and checks
them through a standard-library parser.

## Non-Goals

- Do not introduce Playwright, Figma, browser automation, or layout-engine
  dependencies.
- Do not add overlap or contrast gates; P5.3 owns them.
- Do not add screenshot baselines; P5.4 owns them.
- Do not redesign Figure 71.

## Context To Read

- `docs/architecture/86-p4-scientific-figure-pipeline-phase-close.md`
- `docs/architecture/70-visualization/token-lint-gate.md`
- `tools/architecture_visualization/figure71_html_compositor.py`
- `tools/ui_qa/gcs_token_lint.py`

## Execution Plan

1. Add text-budget attributes to key Figure 71 text containers.
2. Add a standard-library text overflow checker.
3. Add tests for current Figure 71, forced overflow, and missing budgets.
4. Promote the checker and tests into the default quality gates.
5. Regenerate Figure 71 HTML and QA evidence.
6. Update roadmap, archive, and process learning.

## Acceptance Gates

- Current Figure 71 HTML passes with checked budgets.
- Forced over-budget fixture fails.
- Missing-budget fixture fails.
- The default quality-gate sequence includes the overflow checker and tests.

## Verification Plan

```bat
python -B tools\ui_qa\gcs_text_overflow.py
python -m unittest tests.tools.test_gcs_text_overflow
python -m unittest tests.tools.test_agentic_toolkit
python -B tools\architecture_visualization\figure_qa.py --figure figure71
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p5-2-text-overflow-gate.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p5-2-text-overflow-gate\README.md
git diff --check
```

## Evidence Bundle

- `gcs_text_overflow.py`: passed with 101 budgets.
- `tests.tools.test_gcs_text_overflow`: passed.
- `tests.tools.test_agentic_toolkit`: passed after adding the new gate ids.
- Figure 71 QA passed after regenerating HTML.

## Residual Risks

- P5.2 is budget-based, not pixel-perfect. P5.4 must still decide screenshot
  baselines.
- P5.3 still needs overlap and contrast gates.
