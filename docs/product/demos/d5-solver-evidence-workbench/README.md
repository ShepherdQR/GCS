# D5 Solver Evidence Workbench Demo

Status: active
Date: 2026-05-26

## Audience

Technical reviewer who wants to know whether GCS can make solver evidence
inspectable instead of merely showing geometry.

## Demo Thesis

```text
showcase scene -> structured evidence bundle -> viewer/figure projection
    -> browser review artifact -> viewer canvas review artifact
    -> visual QA and follow-up
```

This package is the first D5 demo. It now includes a Phase 10 viewer-canvas
review artifact produced through `GCSPlatformGUI` and the same TkAgg canvas path
used by the local desktop viewer. It proves that the workbench line has a
concrete evidence chain and review artifacts without updating the narrative map
in this pass.

## Scene

- Positive scene:
  `fixtures/scene/showcase/integrated_feature_showcase.gcs.json`
- Positive metadata:
  `fixtures/scene/showcase/integrated_feature_showcase.metadata.json`
- Negative metadata:
  `fixtures/scene/showcase/integrated_feature_showcase_missing_fixed.metadata.json`

## Command Path

```bat
python tools\architecture_visualization\showcase_fixture_evidence.py
python tools\architecture_visualization\showcase_scene_html_compositor.py --check
python tools\architecture_visualization\browser_export.py --figure figure72 --formats png,pdf --viewport 1600x1400 --require-browser
python tools\ui_qa\capture_viewer_evidence.py
python tools\ui_qa\gcs_screenshot_baseline.py
```

## Viewer Path

- Projection contracts:
  - `selection_focus(...)`
  - `constraint_state_projection(...)`
  - `combine_focus_with_constraint_states(...)`
  - `project_history_frame(...)`
- Python surfaces:
  - `python/gcs_viz/viewer_bridge.py`
  - `python/gcs_viz/platform_gui.py`
  - `python/gcs_viz/visualizer.py`

## Expected Output

- Showcase fixture evidence passes.
- Figure 72 HTML is current.
- Browser export manifest reports `status: exported` and
  `html_tokens_passed: true`.
- Screenshot baseline validates the Figure 72 review PNG.
- Screenshot baseline validates the VE-002 viewer review PNG.
- No-Tk viewer projection tests pass.

## Evidence Artifact

See [evidence.md](evidence.md).

## Known Limitations

- This package uses Figure 72 and VE-002 review artifacts as visual surfaces;
  it does not yet include a full operating-system window screenshot.
- The VE-002 review PNG is a stable TkAgg viewer-canvas contact sheet; rail
  state is recorded in JSON.
- Structured C++ report delivery into Python viewer projections remains a
  future implementation path.
- Local-to-global context-cover overlays are not part of this demo yet.

## Next Task

Follow `docs/architecture/98-ui-viewer-figure-development-plan.md`: harden
VE-002, define structured report projection, and start Phase 11 only after
diagnostic report projections are stable enough to make constraint-manager rows
evidence-backed rather than UI-inferred.
