# Viewer Phase 10 Visual QA

Status: complete with TkAgg canvas evidence
Date: 2026-05-26

Governing conventions:

- GCS Quiet Technical Atelier
- GCS Warm Evidence Tokens
- GCS Evidence-First Interface Grammar
- GCS Visual Integrity Gate

## Purpose

Phase 10 checks the local Python viewer against real workbench states instead
of only static token, contrast, or no-Tk projection tests. This pass keeps the
narrative map unchanged and promotes VE-002 from future viewer evidence to a
committed review artifact.

## Capture

Primary artifact:

- `docs/architecture/70-visualization/assets/ve002-d5-viewer-evidence-workbench.review.png`

Capture manifest:

- `docs/architecture/70-visualization/assets/ve002-d5-viewer-evidence-workbench.capture.json`

Rebuild command, using a Python environment with `python/requirements.txt`
available:

```bat
python tools\ui_qa\capture_viewer_evidence.py
```

The capture tool instantiates `GCSPlatformGUI`, exercises the same TkAgg canvas
path used by the desktop viewer, and records rail-state text in JSON. A full
operating-system window screenshot was not captured in this shell; the review
PNG is therefore a stable viewer-canvas contact sheet, not a full app-window
baseline.

## Checklist

| Target | Result | Evidence |
| --- | --- | --- |
| Empty model | Captured | `empty_model` scenario in the capture manifest. |
| `triangle_003.json` | Captured | `triangle_003_graph_focus` scenario, graph view, selected constraint focus. |
| `mixed_geometry_constraints.json` | Captured | `mixed_constraints_replay` scenario with replay frame projection and diagnostic states. |
| Active replay | Captured | `project_history_frame(...)` drives the replay rail and focus overlay. |
| Solve success | Skipped | C++ engine was not available in this worktree; the pass does not claim a live solve success. |
| Solve warning/error | Represented, not rerun | D5 and mixed scenarios use diagnostic state projections and metadata-backed warning text. |
| Narrow desktop width | Captured | D5 scenario runs at `960x700+40+40` root geometry. |

## Findings

- The empty, triangle, mixed replay, and D5 diagnostic states all rendered
  without Tk or Matplotlib exceptions in the dependency-complete environment.
- The capture exposed a Summary-panel collision between DOF text and the state
  legend in `build_three_view_on_figure(...)`.
- `python/gcs_viz/visualizer.py` now moves the diagnostic Summary text above
  the legend and reduces the legend text size for constrained panels.
- The viewer rail state remains projection evidence. It is recorded in JSON
  rather than embedded into the canvas export.

## Remaining Risk

- `scripts/start_gui.cmd` was not used directly because the active base Python
  in this shell lacks `matplotlib`; the pass used an equivalent direct
  `GCSPlatformGUI` run in an environment with the viewer dependencies present.
- Full-window screenshot capture remains a future enhancement. The stable
  baseline covers the embedded viewer canvas and projection states, not the
  surrounding Tk controls as pixels.
- Structured C++ report to Python viewer projection remains future work; this
  pass uses current diagnostic projection contracts and metadata evidence.

## Next Recommendation

Phase 11 should start only after structured report projections are ready enough
to make constraint-manager rows evidence-backed instead of UI-inferred. Until
then, keep D5 anchored to VE-001 Figure 72 plus VE-002 viewer canvas evidence.
