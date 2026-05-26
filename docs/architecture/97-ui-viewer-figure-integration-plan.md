# UI, Viewer, And Figure Integration Plan

Status: active
Date: 2026-05-26

## Purpose

This plan closes the split between the Python viewer, visual QA, and
scientific figures by making them one evidence program.

The governing chain is:

```text
solver or replay report -> viewer_bridge projection -> workbench overlay
    -> screenshot or QA artifact -> scientific figure or demo package
```

The UI is the interactive evidence surface. The scientific figure is the
review/export surface. Visual QA is the repeatable acceptance surface. None of
these surfaces owns solver truth.

## Governing Conventions

- **GCS Evidence-First Interface Grammar** for report-to-projection-to-overlay
  semantics.
- **GCS Scientific Figure Pipeline** for figure specs, browser-rendered review
  artifacts, and rebuildability.
- **GCS Visual Integrity Gate** for screenshot, contrast, overflow, and
  overlap evidence.
- **GCS Quiet Technical Atelier** for restraint, density, and repeated-use
  legibility.

## Integration Contract

Every promoted visual evidence artifact should name these fields:

| Field | Meaning | Owner |
| --- | --- | --- |
| Source scene | Fixture or model under review. | `io_adapters` / fixture owner |
| Evidence source | Structured report, replay artifact, metadata bundle, or safe fallback. | solver/runtime/diagnostics owner |
| Projection family | `viewer_bridge` projection that makes evidence consumable. | `viewer_bridge` |
| Workbench state | Viewer mode, focus, diagnostic state, replay frame, or selected row. | Python GUI |
| Review artifact | PNG/PDF/HTML/SVG or screenshot baseline. | figure pipeline / UI QA |
| Demo package | User-facing evidence walkthrough. | product docs |
| Known limitation | Unsupported, degraded, or future structured-report dependency. | task owner |

## Surface Mapping

| Surface | Role in the chain | Required evidence |
| --- | --- | --- |
| `python/gcs_viz/viewer_bridge.py` | Converts graph, history, selection, and diagnostic evidence into pure projections. | deterministic no-Tk tests |
| `python/gcs_viz/platform_gui.py` | Orchestrates workbench state and user actions. | projection-fed UI behavior, no solver-truth ownership |
| `python/gcs_viz/visualizer.py` | Draws supplied focus, diagnostic, and replay states only. | headless render or syntax coverage |
| `tools/ui_qa/` | Turns visual conventions into repeatable checks. | pass/fail reports with advisory limits explicit |
| `tools/architecture_visualization/specs/` | Keeps dense figures source-driven. | semantic spec plus source evidence |
| `docs/architecture/70-visualization/assets/` | Stores review/export artifacts. | browser export manifest or screenshot baseline |
| `docs/product/demos/` | Makes the evidence chain legible to a reviewer. | command/viewer path, expected output, evidence artifacts |

## Phase Alignment

| Existing line | Integration interpretation | Next action |
| --- | --- | --- |
| P7 Review Artifact Hardening | Figure 72 becomes a stable review/export surface for the showcase evidence chain. | Produce PNG/PDF review artifacts, baseline the PNG, and record art-direction review. |
| Viewer Phase 8 | Accessibility work makes evidence state readable as text/state, not color alone. | Add contrast-safe status text colors and dynamic graph-node label text. |
| Viewer Phase 9 | Replay rail becomes the visible provenance projection. | Add a pure history-frame projection and surface deletion hints in the rail. |
| Viewer Phase 10 | The workbench line gains a concrete viewer visual artifact. | Maintain VE-002 canvas capture and screenshot baseline until full-window capture is reliable. |
| D5 Solver Evidence Workbench | Product demo proves the chain for one user-facing scenario. | Keep Figure 72 and VE-002 evidence linked from `docs/product/demos/d5-solver-evidence-workbench/`. |

## Acceptance

This line is integrated when a reviewer can start from one evidence item and
trace it through:

1. source scene or report;
2. `viewer_bridge` projection;
3. viewer state or overlay;
4. visual QA or screenshot artifact;
5. scientific figure or demo package;
6. explicit known limitation or follow-up.

The UI/viewer/scientific-figure narrative should remain separate from solver
ownership. The viewer may make evidence inspectable; it must not compute rank,
residual, gluing, conflict, redundancy, or obstruction truth.
