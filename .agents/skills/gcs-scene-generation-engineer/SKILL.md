---
name: gcs-scene-generation-engineer
description: Synthetic graph and scene generation for GCS. Invoke when editing tools/scene_generation, generating skeleton graphs or GCS graphs, assigning geometry parameters, checking vertex biconnectivity, repairing generated graphs, serializing generated scenes, producing graph reports, or promoting generated outputs into fixtures.
---

# GCS Scene Generation Engineer

## Start Here

Use this skill for the Python generation and research tooling under
`tools/scene_generation`. Read `references/scene-generation-map.md` before
changing `tools.py` or creating durable generated graph data.

If generated output is promoted into `fixtures/scene/`, changes scene schemas,
or must round-trip through C++/Python scene IO, also use
`gcs-scene-behavior-steward`. If the work changes solver meaning,
diagnostics, or target module boundaries, also use `gcs-cpp-solver-maintainer`
and `gcs-architecture-steward`.

## Workflow

1. Classify the task as skeleton generation, GCS lift, parameter assignment,
   projection, validation, repair, serialization, or report generation.
2. Prefer the existing command in `tools/scene_generation/tools.py` over
   one-off scripts.
3. Keep generated data deterministic when it may be compared or reused: pass
   explicit `graph_id` values and seeds.
4. Validate after every generation, lift, repair, or parameter assignment. Use
   schema validation for GCS graphs and biconnectivity checks when topology is
   part of the claim.
5. Treat `tools/scene_generation/.store` as scratch generated state. Promote
   data to `fixtures/scene/` only when the user asks or the fixture serves a
   durable verification purpose.
6. When promoting data, use canonical serialization and verify the relevant
   C++ and Python loaders when feasible.

## Command Pattern

Use the repository tool directly:

```bat
python tools\scene_generation\tools.py <command> --input "{\"graph_id\":\"example\"}"
```

Common commands include:

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

## Guardrails

- Keep generation and repair policy in `tools/scene_generation`; do not move
  it into the solver, GUI, or scene IO layers.
- Use tool-produced certificates, validation results, and reports instead of
  manually asserting graph properties.
- Preserve constraint type signatures, geometry parameter validity, stable IDs,
  and deterministic output.
- Do not add third-party dependencies to the generator without explicit user
  approval and a clear reason.

## Validation

Use the tool's own commands for behavior checks:

```bat
python tools\scene_generation\tools.py list
python tools\scene_generation\tools.py validate_gcs_schema --input "{\"gcs_graph_id\":\"example\"}"
```

For newly generated durable examples, run the full generate/lift/parameterize/
validate/project/report path with explicit IDs and seeds, then verify promoted
fixtures with the scene IO checks from `gcs-scene-behavior-steward`.

## Codex Integration

When invoked for scene generation work:
- Use `Read` on `references/scene-generation-map.md` before modifying
  generation logic.
- Use `Bash` to run generation commands through the existing `tools.py` CLI
  rather than writing one-off scripts.
- When promoting generated data to fixtures, use `Bash` to verify C++ and
  Python loaders.
- Use `Grep` to verify that generated outputs match expected schema before
  promotion.
- Keep `.store` as scratch; only promote to `fixtures/scene/` with explicit
  user approval and a durable verification purpose.
