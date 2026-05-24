---
task_id: 2026-05-24-p5-3-overlap-contrast-gates
status: complete
session_goal: "Close P5.3 by adding repeatable overlap and contrast gates for generated figure HTML."
archive_target: docs/completed-tasks/2026-05-24-p5-3-overlap-contrast-gates/
experience_links:
  - docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p5-3-overlap-contrast-gates-forging-note.md
---

# P5.3 Overlap And Contrast Gates

## Task Objective

Make generated figure layout-box overlap and text contrast failures detectable
before screenshot baselines and showcase work.

## Scope And Non-Goals

In scope:

- instrument Figure 71 HTML with layout boxes and contrast targets;
- add a standard-library overlap/contrast checker;
- add forced bad fixtures;
- promote the gate to default quality gates;
- update roadmap and archive the step.

Out of scope:

- screenshot/pixel baseline comparison;
- browser automation or external visual testing packages;
- Figure 71 redesign;
- Figma MCP decision.

## Interaction Summary

After P5.2 text budgets landed, P5.3 extended the same generated-HTML
instrumentation approach to panel overlap and contrast. This gives the project
a stronger source-level visual integrity gate before P5.4 chooses screenshot
baselines.

## Work Completed

- Added `tools/ui_qa/gcs_overlap_contrast.py`.
- Added `tests/tools/test_gcs_overlap_contrast.py`.
- Added Figure 71 panel box and contrast markers through the HTML compositor.
- Regenerated Figure 71 HTML and QA evidence.
- Added `python.gcs_overlap_contrast` and
  `python.gcs_overlap_contrast_tests` to default quality gates.
- Added `docs/architecture/70-visualization/overlap-contrast-gate.md`.

## Files And Artifacts

- `tools/ui_qa/gcs_overlap_contrast.py`
- `tests/tools/test_gcs_overlap_contrast.py`
- `tools/architecture_visualization/figure71_html_compositor.py`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.html`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.qa.json`
- `tools/agentic_design/agentic_toolkit.py`
- `tests/tools/test_agentic_toolkit.py`
- `docs/architecture/70-visualization/overlap-contrast-gate.md`
- `docs/architecture/76-ui-design-system-execution-plan.md`
- `docs/architecture/82-ui-design-next-work-plan.md`

## Evidence

```text
python -B tools\ui_qa\gcs_overlap_contrast.py
GCS overlap/contrast checks passed (6 boxes, 21 contrast targets)

python -m unittest tests.tools.test_gcs_overlap_contrast
Ran 4 tests.
OK

python -m unittest tests.tools.test_agentic_toolkit
Ran 6 tests.
OK

python -B tools\architecture_visualization\figure_qa.py --figure figure71
Passed.

python tools\agentic_design\agentic_toolkit.py run-quality-gates
All requested quality gates passed, including python.gcs_overlap_contrast and
python.gcs_overlap_contrast_tests.
```

## Decisions

- Decision: use declared layout boxes before screenshot baselines. Rationale:
  P5.3 can catch deterministic panel overlap without choosing the final pixel
  backend.
- Decision: require missing markers to fail. Rationale: uninstrumented HTML
  should not pass visual integrity review by accident.
- Decision: keep token-chip contrast threshold configurable. Rationale: some
  chips are status/evidence markers rather than body text, but contrast must
  still be reported explicitly.

## Skipped Checks And Risks

- Full quality gates passed before commit; no P5.3-specific source checks were
  skipped.
- Layout boxes are design-grid contracts, not rendered pixel rectangles.
- P5.4 remains responsible for stable screenshot/pixel baselines.

## Follow-Up

- Execute P5.4 screenshot baselines.
- Reuse Figure 71 markers as selectors or labels for future pixel reports.

## Archive Handoff

- Archive path: `docs/completed-tasks/2026-05-24-p5-3-overlap-contrast-gates/`
- Related experience:
  - `docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p5-3-overlap-contrast-gates-forging-note.md`
- Skill, eval, fixture, or tool update needed: P5.4 should choose and document
  the screenshot baseline backend.
