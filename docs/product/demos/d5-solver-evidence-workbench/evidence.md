# D5 Evidence

Date: 2026-05-26

## Evidence Chain

| Stage | Artifact | Role |
| --- | --- | --- |
| Source scene | `fixtures/scene/showcase/integrated_feature_showcase.gcs.json` | Public integrated showcase scene. |
| Metadata evidence | `fixtures/scene/showcase/integrated_feature_showcase.metadata.json` | Rank/residual, boundary, gluing, panel, and gate evidence. |
| Negative evidence | `fixtures/scene/showcase/integrated_feature_showcase_missing_fixed.metadata.json` | Stable missing-fixed-ID rejection code. |
| Figure spec | `tools/architecture_visualization/specs/figure72.yaml` | Semantic source of truth for the review figure. |
| Editable figure | `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.html` | Tokenized browser-composed evidence surface. |
| Review PNG | `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.review.png` | Stable visual review artifact and screenshot baseline. |
| Review PDF | `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.review.pdf` | Portable review/export artifact. |
| Browser manifest | `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-browser-export.json` | Browser export and token-smoke evidence. |
| Screenshot baseline | `docs/architecture/70-visualization/assets/screenshot-baselines.json` | Exact PNG hash gate. |
| Art Director review | `docs/agentic/institutional-agents/004-art-director-frame-judge/examples/2026-05-26-figure72-p7-review-artifact-hardening.md` | Independent visual judgment. |
| Shared manifest | `docs/architecture/70-visualization/visual-evidence-manifest.md` | Cross-surface visual evidence index. |

## Viewer Projection Evidence

The D5 viewer side is represented by projection contracts and no-Tk tests:

- `selection_focus(...)` links table selection to canvas focus.
- `constraint_state_projection(...)` and
  `combine_focus_with_constraint_states(...)` carry diagnostic overlay state.
- `project_history_frame(...)` carries replay rail action, progress, focus, and
  deletion hints.
- `tests/tools/test_gcs_viz_history_replay.py` covers these projections without
  importing Tk.

## Current Validation Targets

```bat
python -m unittest tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa tests.tools.test_browser_export tests.tools.test_gcs_screenshot_baseline
python tools\architecture_visualization\showcase_fixture_evidence.py
python tools\architecture_visualization\showcase_scene_html_compositor.py --check
python tools\ui_qa\gcs_ui_qa.py
python tools\ui_qa\gcs_screenshot_baseline.py
```

## Residual Risk

The live GUI screenshot remains future Phase 10 evidence. Until then, this D5
package proves the repo-native evidence chain and review artifacts, not a
manual desktop inspection result.
