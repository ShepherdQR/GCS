---
task_id: 2026-05-24-p5-4-screenshot-baselines
status: complete
session_goal: "Close P5.4 by adding a repeatable screenshot-baseline manifest and checker."
archive_target: docs/completed-tasks/2026-05-24-p5-4-screenshot-baselines/
experience_links:
  - docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p5-4-screenshot-baselines-forging-note.md
---

# P5.4 Screenshot Baselines

## Task Objective

Make stable screenshot review artifacts part of the executable visual-integrity
gate before P6 showcase work begins.

## Scope And Non-Goals

In scope:

- add a screenshot-baseline manifest;
- register the Figure 71 review PNG as the first stable baseline;
- add a standard-library PNG baseline checker;
- add forced missing-file, dimension, and digest failure fixtures;
- promote the gate into default quality gates;
- document the baseline update policy.

Out of scope:

- perceptual or pixel-diff image comparison;
- browser automation changes;
- new dependencies or services;
- Figma MCP decision.

## Interaction Summary

P5.1 through P5.3 made visual QA source-level and deterministic: tokens, text
budgets, layout boxes, and contrast targets. P5.4 adds the first artifact-level
pixel contract by pinning the browser-rendered Figure 71 review PNG with
dimensions, byte count, and SHA256.

## Work Completed

- Added `docs/architecture/70-visualization/assets/screenshot-baselines.json`.
- Added `tools/ui_qa/gcs_screenshot_baseline.py`.
- Added `tests/tools/test_gcs_screenshot_baseline.py`.
- Added `python.gcs_screenshot_baseline` and
  `python.gcs_screenshot_baseline_tests` to default quality gates.
- Added `docs/architecture/70-visualization/screenshot-baseline-gate.md`.

## Files And Artifacts

- `docs/architecture/70-visualization/assets/screenshot-baselines.json`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.review.png`
- `tools/ui_qa/gcs_screenshot_baseline.py`
- `tests/tools/test_gcs_screenshot_baseline.py`
- `tools/agentic_design/agentic_toolkit.py`
- `tests/tools/test_agentic_toolkit.py`
- `docs/architecture/70-visualization/screenshot-baseline-gate.md`
- `docs/architecture/76-ui-design-system-execution-plan.md`
- `docs/architecture/82-ui-design-next-work-plan.md`

## Evidence

```text
python -B tools\ui_qa\gcs_screenshot_baseline.py
GCS screenshot baseline checks passed (1 baselines)

python -m unittest tests.tools.test_gcs_screenshot_baseline
Ran 4 tests.
OK

python -m unittest tests.tools.test_agentic_toolkit
Ran 6 tests.
OK

python tools\agentic_design\agentic_toolkit.py run-quality-gates
All requested quality gates passed, including python.gcs_screenshot_baseline
and python.gcs_screenshot_baseline_tests.
```

## Decisions

- Decision: use exact PNG hash baselines for P5.4. Rationale: the repo already
  has a stable browser-rendered review PNG, and exact hashes are simple,
  dependency-free, and fail loudly.
- Decision: keep perceptual diffing out of P5.4. Rationale: a later backend can
  read the same manifest after the repo-native policy exists.
- Decision: include byte count and minimum byte count. Rationale: this catches
  accidental placeholder or truncated exports before a digest review.

## Skipped Checks And Risks

- Full quality gates passed before commit; no P5.4-specific source checks were
  skipped.
- Exact hashes are sensitive to any legitimate rendering change.
- The first baseline covers Figure 71 only; viewer-state screenshots remain
  future baselines.

## Follow-Up

- Close P5 by deciding which visual-integrity gates stay in default quality
  gates versus reviewer-only review.
- Start P6.1 showcase brief from the now-stable repo-native visual QA path.

## Archive Handoff

- Archive path: `docs/completed-tasks/2026-05-24-p5-4-screenshot-baselines/`
- Related experience:
  - `docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p5-4-screenshot-baselines-forging-note.md`
- Skill, eval, fixture, or tool update needed: future screenshot expansion
  should add new manifest entries before adding a heavier diff backend.
