---
name: gcs-ui-qa-steward
description: UI quality assurance automation for GCS. Invoke when running or designing UI QA checks — theme token validation, contrast ratio enforcement, GUI static analysis, fixture coverage verification, headless render smoke tests, screenshot baselines, text overflow detection, overlap/contrast gates, or visual integrity gate execution.
---

# GCS UI QA Steward

## Start Here

Use this skill for automated UI quality assurance. The UI QA tools enforce
visual integrity gates that the design steward specifies — this skill runs
the checks.

Read:
- `docs/architecture/75-ui-design-system-conventions.md`
- `docs/architecture/73-gcs-visual-taste-guide.md`

If the work involves defining new design conventions (not just checking them),
also use `gcs-ui-design-steward`.

## Command Reference

```bat
# Run full UI QA suite
python tools\ui_qa\gcs_ui_qa.py

# Token-level design-system lint
python tools\ui_qa\gcs_token_lint.py

# Contrast and overlap checks
python tools\ui_qa\gcs_overlap_contrast.py

# Text overflow detection
python tools\ui_qa\gcs_text_overflow.py

# Screenshot baseline comparison
python tools\ui_qa\gcs_screenshot_baseline.py

# Capture viewer evidence for QA
python tools\ui_qa\capture_viewer_evidence.py
```

## Checks Performed

| Check | What it verifies |
|-------|-----------------|
| **docs** | Required UI aesthetic design docs exist |
| **theme** | All GCS_THEME tokens present with valid #RRGGBB colors |
| **contrast** | WCAG contrast ratios >= 4.5 for text, >= 3.0 for large text |
| **state colors** | STATE_TEXT_COLORS tokens exist and meet contrast |
| **rigid set palette** | Dynamic node label colors are readable on all fills |
| **GUI static** | platform_gui.py has required contract tokens, ASCII labels |
| **fixture** | Mixed geometry/constraint QA fixture covers all types |
| **headless render** | 3D, graph, and 3view renders produce non-empty output |

## Own

- Automated UI QA execution and reporting.
- Theme token validation and contrast enforcement.
- GUI static analysis for contract tokens.
- UI fixture coverage verification.
- Headless render smoke tests.

## Refuse

- Defining new design conventions (belongs to `gcs-ui-design-steward`).
- Approving visual taste (belongs to `art-director-frame-judge`).
- Treating QA warnings as design failures.

## Guardrails

- UI QA is a gate, not a design authority.
- Warnings are advisory; errors are blocking.
- Headless render checks may be skipped when matplotlib is unavailable;
  record as risk, not as pass.

## Required Output

Return a structured QA report with:
- checks run and their status;
- errors (blocking) and warnings (advisory);
- skipped checks with reason and risk;
- specific failing tokens, contrast pairs, or fixture gaps;
- recommended next action.

## Codex Integration

When invoked:
- Use `Bash` to run `python tools/ui_qa/gcs_ui_qa.py` and individual QA tools.
- Use `Read` to inspect `color_scheme.py` and `platform_gui.py` when checks
  fail.
- Use `Edit` to fix identified issues (with `gcs-ui-design-steward` for
  convention changes).
- Use `mcp__Claude_Preview__preview_inspect` to verify visual properties
  against QA findings.
- Record QA results before claiming UI work complete.
