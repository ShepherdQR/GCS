# UI Aesthetic Phase 2: Viewport Semantics

## Goal

Make the model viewport read as a geometric workspace rather than a debug plot.
The renderer should communicate object kind, rigid-set ownership, constraint
kind, and temporal focus with quiet visual states.

This phase does not change solver semantics, scene IO, or the left inspector
layout. It only strengthens the meaning carried by the existing 3D, graph, and
three-view renderers.

## Semantic Layers

The viewport uses four layers, from calmest to most salient:

- canvas and grid: warm, low-contrast spatial reference;
- rigid-set geometry: muted categorical color by rigid set;
- constraints: darker, thinner connectors with type-specific line styles;
- focus state: accent halo and thicker stroke for the current replay object.

Labels remain secondary. They identify objects, but they should not overpower
geometry or constraint structure.

## Geometry Encoding

Geometry type is encoded by form before text:

- point: circular marker with a subtle light halo;
- line: solid segment with small endpoint anchors;
- plane: translucent square patch in 3D, square marker in projected views;
- rigid-set ownership: fill or stroke color from `RIGID_SET_COLORS`.

The graph view mirrors this language:

- point nodes are circles;
- line nodes are diamonds;
- plane nodes are squares;
- node size increases modestly from point to plane.

## Constraint Encoding

Constraint type is encoded primarily by line style:

- coincident: dotted;
- parallel: long dashed;
- perpendicular: dash-dot;
- distance: solid;
- angle: short dashed.

Constraint color remains available for recognition, but stroke style, width,
and alpha carry the important distinction. This keeps the viewport usable even
when many rigid-set colors are present.

## Visual States

The renderer accepts an optional `focus` dictionary:

- `constraint_ids`: constraints that should be emphasized;
- `geometry_ids`: geometries that should be emphasized;
- `rigid_set_ids`: rigid sets that should be emphasized;
- `mode`: currently `replay` or `selection`.

The initial implementation uses this for history replay. The same contract can
later serve selection, validation, solve diagnostics, and violated constraints
without changing renderer ownership.

Focus rules:

- focused geometry receives an accent halo and slightly larger marker/stroke;
- focused constraints receive accent overlay, stronger alpha, and thicker
  stroke;
- non-focused objects remain visible; they are not hidden or aggressively
  dimmed.

## Replay Mapping

During history replay, `platform_gui.py` maps the current history entry to a
focus dictionary and passes it through `viewer_bridge.render_graph_view`.

Mapping:

- `AddRigidSet` / `RemoveRigidSet`: focus the rigid set id;
- `AddGeometry` / `RemoveGeometry`: focus the geometry id and its rigid set;
- `AddConstraint` / `RemoveConstraint` / `UpdateConstraint`: focus the
  constraint id and all referenced geometries;
- `Solve`: no object focus; title and log carry the temporal event.

`viewer_bridge.py` remains read-only. It only forwards focus to renderer
functions and may host stateless helper mapping later if duplicated elsewhere.

## Non-Goals

- no new dependencies;
- no browser or external viewer;
- no hit testing;
- no persisted selected-state schema;
- no solver diagnostic overlay yet;
- no left inspector rewrite.

## Acceptance Checks

- focused replay steps visibly identify the object being introduced or changed;
- normal viewport state remains calm and uncluttered;
- graph, 3D, and three-view renderers share geometry and constraint semantics;
- renderer functions still draw onto a provided `Figure`;
- touched Python parses with `ast.parse`;
- focused `git diff --check` passes for touched files.
