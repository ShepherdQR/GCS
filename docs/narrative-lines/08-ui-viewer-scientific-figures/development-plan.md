# 08 — UI/Viewer/Scientific Figures

Status: active
Date: 2026-05-30
Parent map: `docs/architecture/95-gcs-narrative-map.md`

## Current Level

**Strong, integration in progress (4.0)**

## Current State

Viewer, visual QA, figure pipeline, Solver Evidence Workbench direction, and
an explicit UI/viewer/figure integration plan exist. The D5 static workbench
package ties Figure 72, VE-002 viewer canvas evidence, visual QA, and
projection contracts together.

## Main Gap

The next proof point must show one evidence chain from report to viewer to
figure/demo artifact. The integration plan exists but the live walkthrough
is not yet possible (blocked on structured report projection).

## Evidence Artifact

Figure 95 baseline/trend, UI architecture docs, and D5 static screenshot
package with visual QA.

## Promotion Gate

Build a live workbench walkthrough only when viewer evidence projection is
ready.

## Next Move

Promote one end-to-end evidence walkthrough using
`docs/architecture/97-ui-viewer-figure-integration-plan.md`.

## Development Plan

### Short-term (next 2-4 weeks)

1. Complete structured report projection in the viewer bridge (the blocking
   precondition for live walkthrough).
2. Keep the D5 static workbench package current: refresh screenshots and
   visual QA when viewer or figure behavior changes.
3. Run atelier-steward review on any new figure or UI surface before it
   enters the workbench package.

### Medium-term (4-8 weeks)

4. Build the live workbench walkthrough: load scene → solve → inspect
   diagnostics → replay history → export evidence.
5. Record or document the walkthrough and link it from README and demo ladder.
6. Add a "figure freshness" check: when solver output changes, flag any
   figure that may need regeneration.

### Long-term (8+ weeks)

7. Extend viewer to show diagnostic overlays (obstruction highlights,
   redundancy markers) directly on the geometry canvas.
8. Build a figure gallery page that collects all publication-quality figures
   with their source specs and regeneration commands.

## Dependencies

- Viewer bridge: structured report projection must be ready for live
  walkthrough.
- Solver evidence (01): viewer shows solver diagnostics.
- Runtime/replay (05): replay evidence feeds viewer history layer.

## Related

- Arc 2: Evidence Workbench
- `docs/architecture/97-ui-viewer-figure-integration-plan.md`
- `docs/architecture/70-visualization/`
- `python/gcs_viz/`
