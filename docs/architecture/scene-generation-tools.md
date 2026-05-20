# Scene Generation Tools

`tools/scene_generation` is a local research and fixture-authoring tool family.
It is not part of the solver runtime, GUI, or scene IO contract. Its job is to
produce deterministic candidate graphs, validate them, repair common synthetic
graph defects, and emit reports that can justify fixture promotion.

## Goals

- Generate ordinary skeleton graphs with explicit certificates for structural
  claims such as vertex biconnectivity.
- Lift skeleton vertices into GCS geometries and skeleton edges into
  constraints while preserving stable IDs.
- Assign geometry parameters that avoid trivial degeneracies before schema
  validation.
- Project GCS graphs into ordinary graph views used by incidence and topology
  checks.
- Validate and repair generated GCS graphs without leaking generator policy into
  `kernel`, `io_adapters`, `viewer_bridge`, or the GUI.
- Keep every generated artifact reproducible from explicit IDs, seeds, and
  command input.

## Data Flow

The intended path is:

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

Repair is an alternate branch after validation:

```text
validate_gcs_schema
  -> repair_gcs_graph
  -> assign_geometry_parameters
  -> validate_gcs_schema
  -> project_gcs_graph
  -> check_vertex_biconnected
```

The durable invariant for generated GCS graphs is that every constraint connects
geometries from different rigid sets. The generator must satisfy this during
lift, validation must reject violations, and repair must either separate the
rigid-set assignments or avoid adding invalid constraints.

## Command Interface

The stable entry point remains:

```bat
python tools\scene_generation\tools.py <command> --input "{\"graph_id\":\"example\"}"
```

Input may also be provided by `--input-file` or stdin. Outputs are JSON and
should be machine-readable.

Supported command names remain:

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

Commands should prefer explicit `graph_id`, `gcs_graph_id`, and
`projected_graph_id` parameters. When IDs are omitted, generated IDs are local
scratch IDs and should not be used for fixture promotion.

## Storage Layout

`tools/scene_generation/.store` is scratch generated state. Files are JSON,
named by graph ID, and written with deterministic key ordering. Stored objects
use one of these shapes:

- skeleton graph: `graph_id`, `num_vertices`, `edges`, certificate metadata;
- GCS graph: `gcs_graph_id`, `rigid_sets`, `geometries`, `constraints`;
- projected graph: `projected_graph_id`, `vertices`, `edges`,
  `projection_rule`;
- report-like data only when a command explicitly writes an artifact.

Generated data is not a fixture until a human intentionally promotes it outside
this directory. Promotion should use canonical serialization and independent IO
round-trip checks.

## Validation And Repair

Schema validation checks:

- unique and present IDs;
- valid geometry, constraint, and rigid-set references;
- rigid-set membership consistency;
- constraint arity and duplicate endpoints;
- supported constraint type signatures;
- cross-rigid-set constraint endpoints;
- non-degenerate lines and non-zero plane normals;
- non-negative distances and angle values in `[0, 180]`.

Repair is allowed to modify generated scratch graphs. It should report explicit
edits and set `post_validation_required` so callers keep validation as the
source of truth. Repair policies may:

- replace invalid constraint types with the first valid type for the endpoint
  signature;
- recolor or move geometry rigid-set assignments so all constraints cross rigid
  sets;
- add valid cross-rigid-set constraints to make the geometry-primal projection
  vertex-biconnected.

Repair should not silently weaken the invariant or write promoted fixtures.

## Determinism

Generation and parameter assignment must use local seeded random state rather
than process-global random state. Lists are serialized in stable ID order.
Topology algorithms sort vertices, neighbors, and edges before traversal. Given
the same command input, seed, and store contents, the resulting JSON and report
should be stable.

## Fixture Promotion Boundary

Promotion from `.store` into `fixtures/scene` is outside the generator's normal
write boundary. Before promotion, a graph should have:

- valid GCS schema;
- satisfied cross-rigid-set constraint invariant;
- expected projection and biconnectivity report;
- canonical serialization checksum;
- explicit graph ID and seed recorded in the generation metadata;
- scene IO compatibility checks when the fixture will be consumed by C++ or the
  Python viewer.

The scene-generation tools may produce promotion candidates and reports, but
fixture ownership remains with the scene IO and verification workflow.
