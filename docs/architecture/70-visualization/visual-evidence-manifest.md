# Visual Evidence Manifest

Status: active
Date: 2026-05-26

## Purpose

This manifest connects solver evidence, viewer projections, visual QA, review
artifacts, and product demo packages. It is the lightweight index that keeps
UI/viewer/scientific-figure work from splitting into unrelated visual tracks.

## Evidence Chain

```text
source scene -> report or metadata evidence -> viewer_bridge projection
    -> workbench state or figure panel -> QA/review artifact -> demo package
```

## Entries

| ID | Source evidence | Projection or viewer surface | Review artifact | QA evidence | Demo |
| --- | --- | --- | --- | --- | --- |
| VE-001 Figure 72 integrated showcase | `fixtures/scene/showcase/integrated_feature_showcase.gcs.json`; `fixtures/scene/showcase/integrated_feature_showcase.metadata.json`; `fixtures/scene/showcase/integrated_feature_showcase_missing_fixed.metadata.json` | Figure panels for scene contract, constraint graph, boundary plan, numeric evidence, gluing diagnostics, negative variant, and gate chain | `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.review.png`; `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.review.pdf` | `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-browser-export.json`; `docs/architecture/70-visualization/assets/screenshot-baselines.json` | `docs/product/demos/d5-solver-evidence-workbench/` |
| VE-002 Viewer focus and diagnostics | `python/gcs_viz/viewer_bridge.py`; `tests/tools/test_gcs_viz_history_replay.py`; UI QA fixture | selection focus, constraint states, and replay frame projections consumed by `platform_gui.py` and `visualizer.py` | Future desktop screenshot after Phase 10 manual visual QA | `tools/ui_qa/gcs_ui_qa.py`; focused no-Tk replay tests | `docs/product/demos/d5-solver-evidence-workbench/` |

## Acceptance Rules

- A manifest entry must name a source scene or source report.
- A manifest entry must name the projection or visual surface that consumes the
  evidence.
- A stable review PNG must be listed in `assets/screenshot-baselines.json`.
- Degraded or future-only viewer evidence must be labeled as such instead of
  treated as screenshot-proven.
- Demo packages should link to this manifest when they depend on visual
  evidence.

## Known Gaps

- VE-002 does not yet have a committed desktop GUI screenshot baseline because
  Phase 10 manual visual QA is still pending.
- Solver diagnostics in the current Python viewer still rely on safe text
  parsing when structured reports are unavailable.
- Local-to-global context-cover and gluing overlays should wait for planner
  and diagnostics contracts to expose enough structured evidence.
