# Viewer History Frame Projection

Status: complete
Date: 2026-05-26

Governing conventions:

- **GCS Evidence-First Interface Grammar**
- **GCS Visual Integrity Gate**

## Result

Replay rail state now consumes a pure `project_history_frame(history, index)`
projection from `python/gcs_viz/viewer_bridge.py`.

The projection contains:

- frame index and one-based step;
- total history length;
- action and action label;
- progress;
- title;
- focus projection;
- deletion hints for removed rigid sets, geometries, and constraints.

The GUI still reconstructs the frame graph through `build_history_graph`, but
the rail wording, progress, focus, and deletion hints come from the same
UI-neutral projection contract.

## Workbench Effect

The replay rail is now a provenance surface rather than a local string builder.
It can say what changed during removal actions even when the removed object is
no longer present in the reconstructed graph.

The replay speed control is mirrored into the viewport rail and shares the
same `replay_speed_var` as the command-panel slider, so speed changes affect
subsequent replay steps without introducing another replay owner.

## Boundary

Replay remains a viewer projection over existing history. It does not rerun
the solver, mutate scene history, or persist UI-only frame state.
