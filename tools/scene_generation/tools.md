# Scene Generation Tool Notes

This file is the implementation-side note for `tools.py`. The durable design
source is:

```text
docs/architecture/scene-generation-tools.md
```

The current implementation is a useful compatibility command set and prototype
algorithm library. It is not yet the full scene auto explorer described in the
architecture document.

## Compatibility Flow

The supported manual flow is:

```text
generate_skeleton_graph
  -> lift_skeleton_to_gcs
  -> assign_geometry_parameters
  -> validate_gcs_schema
  -> project_gcs_graph
  -> check_vertex_biconnected
  -> generate_graph_report
  -> serialize_gcs_graph
```

`lift_skeleton_to_gcs` creates topology and typed entities, but it leaves
geometry vectors at zero. A lifted graph may fail schema validation until
`assign_geometry_parameters` has run.

Repair is available as an alternate branch:

```text
validate_gcs_schema
  -> repair_gcs_graph
  -> assign_geometry_parameters
  -> validate_gcs_schema
  -> project_gcs_graph
  -> check_vertex_biconnected
```

## Commands

Run commands through:

```bat
python tools\scene_generation\tools.py <command> --input "{\"graph_id\":\"example\"}"
```

Supported commands:

- `generate_skeleton_graph`
- `lift_skeleton_to_gcs`
- `assign_geometry_parameters`
- `project_gcs_graph`
- `check_vertex_biconnected`
- `validate_gcs_schema`
- `repair_gcs_graph`
- `serialize_gcs_graph`
- `generate_graph_report`
- `list`
- `delete`

Outputs are JSON. Scratch artifacts are written to
`tools/scene_generation/.store`.

## Reusable Implementation Pieces

Keep these pieces when rewriting the explorer structure:

- deterministic JSON save/load helpers;
- edge canonicalization and sorted graph traversal;
- connected-component and Tarjan biconnectivity checks;
- skeleton generators for `cycle_plus_chords` and `ear_decomposition`;
- geometry and constraint signature tables;
- rigid-set coloring and repair helpers;
- local schema validation;
- geometry-primal, incidence-bipartite, and rigid-set quotient projections;
- parameter assignment for non-degenerate point, line, and plane data;
- canonical JSON and custom text serialization.

## Missing Explorer Pieces

The rewrite needs to add:

- `explore_scene_space` command;
- structured exploration request/result schemas;
- candidate provenance bundles;
- coverage goals and novelty scoring;
- explicit budgets and deterministic stop reasons;
- rejected-candidate evidence;
- exploration trace and replay;
- public validation gate adapters;
- promotion packages separate from scratch generation;
- deterministic tests for command compatibility and explorer behavior.

## Rewrite Direction

Recommended package split:

```text
tools/scene_generation/
  tools.py              # CLI facade and compatibility commands
  scene_generation/
    store.py
    topology.py
    gcs_model.py
    validation.py
    projection.py
    parameterization.py
    reporting.py
    explorer.py
```

The first rewrite should preserve command compatibility while moving logic out
of the monolithic `tools.py`. Do not move generation or repair policy into the
solver, GUI, or scene IO modules.
