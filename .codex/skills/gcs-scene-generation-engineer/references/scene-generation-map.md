# Scene Generation Map

## Current Layout

- `tools/scene_generation/tools.py`: command dispatcher and implementations
  for graph generation, GCS lifting, validation, repair, serialization, and
  reports.
- `tools/scene_generation/tools.md`: design notes for the tool family.
- `tools/scene_generation/.store`: local generated JSON graph store used by
  the tools. Treat this as scratch state unless a generated graph is promoted.
- `fixtures/scene/`: durable scene fixtures consumed by the solver and GUI.

## Typical Flow

Create a validated generated GCS graph:

```text
generate_skeleton_graph
lift_skeleton_to_gcs
assign_geometry_parameters
validate_gcs_schema
project_gcs_graph
check_vertex_biconnected
generate_graph_report
serialize_gcs_graph
```

Repair an existing generated graph:

```text
validate_gcs_schema
repair_gcs_graph
validate_gcs_schema
project_gcs_graph
check_vertex_biconnected
generate_graph_report
```

## Command Notes

- `generate_skeleton_graph`: create an ordinary graph skeleton. Prefer
  `cycle_plus_chords` for simple deterministic biconnected examples; use
  explicit seeds for repeatability.
- `lift_skeleton_to_gcs`: convert skeleton vertices to geometries and edges to
  constraints while respecting type signatures.
- `assign_geometry_parameters`: populate geometry vectors and constraint
  values so schema validation can catch real issues instead of default zeros.
- `project_gcs_graph`: derive `geometry_primal`, `incidence_bipartite`, or
  `rigidset_quotient` views.
- `check_vertex_biconnected`: use this verifier before claiming a generated
  projection is biconnected.
- `validate_gcs_schema`: check IDs, references, arity, type signatures,
  degenerate lines, plane normals, distances, and angle values.
- `repair_gcs_graph`: apply requested repairs, then re-run validation and
  topology checks.
- `serialize_gcs_graph`: produce text or JSON output suitable for fixture
  promotion.
- `generate_graph_report`: prefer this machine-readable report as the basis for
  human summaries.

## Fixture Promotion

Only move generated outputs from `.store` into `fixtures/scene/` when they
serve a lasting test or demo purpose. Before promotion, verify schema validity,
canonical serialization, and compatibility with the readers that will consume
the fixture.
