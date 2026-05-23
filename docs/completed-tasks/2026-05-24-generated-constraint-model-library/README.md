# Generated Constraint Model Library Report

Date: 2026-05-24

## Task Request

The task was to use the existing scene auto-explorer to generate 10 more
complex GCS constraint graphs, estimate the time required to generate one
graph, collect the resulting models into a durable model-file library, and
record the task requirements, goals, issues, handling methods, and key findings
as a persistent Markdown report.

## Goals

- Generate 10 valid, non-trivial constraint-graph models with more complexity
  than the small verification fixtures.
- Prefer the existing `tools/scene_generation/tools.py explore_scene_space`
  and `promote_candidate` commands instead of ad hoc graph construction.
- Keep generated scratch data separate from durable model-library files.
- Promote accepted candidates into public `gcs-0.3` scene files for long-term
  maintenance.
- Preserve provenance, validation gates, digests, and a human-readable index so
  future tasks can reuse and extend the model library.

## Exploration Configuration

The exploration batch used explicit deterministic run IDs and seeds:

- exploration IDs: `codex_complex10_20260524_run00` through
  `codex_complex10_20260524_run09`;
- seeds: `6202400` through `6202409`;
- topology sizes: 10, 12, and 14 vertices;
- topology methods: `cycle_plus_chords` and `ear_decomposition`;
- extra-edge range: 5 to 8;
- geometry types: `Point`, `Line`, and `Plane`;
- constraint types: `Coincident`, `Parallel`, `Perpendicular`, `Distance`, and
  `Angle`;
- requested rigid-set counts: 3, 4, and 5;
- parameter layouts: `circular`, `grid`, and `random`;
- coverage goals: `mixed_rigid_sets` and `biconnected_geometry_primal`;
- promotion profile used for durable library files: `local_only`.

## Outputs

The durable model library was written under:

- `fixtures/scene/generated/README.md`
- `fixtures/scene/generated/manifest.json`
- `fixtures/scene/generated/*.gcs.json`
- `fixtures/scene/generated/metadata/*.metadata.json`

The library contains 10 public `gcs-0.3` scene files. Each model has a matching
metadata package with source exploration ID, source GCS graph ID, topology
policy, promotion ID, validation gates, and canonical digests.

The completed-task report is this file:

- `docs/completed-tasks/2026-05-24-generated-constraint-model-library/README.md`

## Key Findings

- The generated batch contains 10 accepted models.
- Model complexity range:
  - 10 to 14 geometries;
  - 18 to 33 constraints;
  - 4 to 5 rigid sets.
- Batch timing:
  - total generation time: about 1.50 seconds;
  - average generation time: about 0.15 seconds per accepted model.
- All durable models are public `gcs-0.3` scenes.
- All 10 promoted library entries passed the local validation gates:
  - `local_schema_validation`;
  - `geometry_primal_projection`;
  - `geometry_primal_biconnectivity`;
  - `canonical_serialization`.

## Model Summary

| Fixture | Geometries | Constraints | Rigid sets | Topology |
| --- | ---: | ---: | ---: | --- |
| `codex_complex10_20260524_run00_c0000.gcs.json` | 14 | 32 | 4 | `ear_decomposition`, extra=7, circular |
| `codex_complex10_20260524_run01_c0000.gcs.json` | 14 | 31 | 4 | `ear_decomposition`, extra=6, circular |
| `codex_complex10_20260524_run02_c0000.gcs.json` | 14 | 32 | 5 | `ear_decomposition`, extra=7, circular |
| `codex_complex10_20260524_run03_c0000.gcs.json` | 14 | 33 | 4 | `ear_decomposition`, extra=8, grid |
| `codex_complex10_20260524_run04_c0000.gcs.json` | 14 | 21 | 5 | `cycle_plus_chords`, extra=7, circular |
| `codex_complex10_20260524_run05_c0000.gcs.json` | 14 | 33 | 4 | `ear_decomposition`, extra=8, grid |
| `codex_complex10_20260524_run06_c0000.gcs.json` | 14 | 20 | 5 | `cycle_plus_chords`, extra=6, random |
| `codex_complex10_20260524_run07_c0000.gcs.json` | 10 | 18 | 4 | `cycle_plus_chords`, extra=8, random |
| `codex_complex10_20260524_run08_c0000.gcs.json` | 10 | 18 | 5 | `cycle_plus_chords`, extra=8, circular |
| `codex_complex10_20260524_run09_c0000.gcs.json` | 14 | 20 | 5 | `cycle_plus_chords`, extra=6, grid |

## Issues Found And Handling

1. Scratch-store write location

   The default `tools/scene_generation/.store/explorations` path could not be
   created in the current Windows sandbox. To keep the exploration moving while
   preserving the tool contract that scratch stores are not durable fixtures,
   the batch used `GCS_SCENE_GENERATION_STORE_DIR=.codex_scene_generation_store`.
   Accepted candidates were then promoted into `fixtures/scene/generated`.

2. Explorer facade import gaps

   During the first run, the explorer path exposed missing runtime imports for
   `time.monotonic()` and `Counter()` in the current tool facade. The local
   working tree was adjusted so the exploration could complete. The durable
   output records the issue because future cleanup should keep the explorer
   facade and package modules import-complete before relying on batch
   generation in CI.

3. Runtime smoke gate unavailable

   Full promotion with public runtime smoke was blocked because the expected
   solver executable was not available to the promotion command. The durable
   library therefore used `local_only` promotion. This preserves schema,
   projection, biconnectivity, and canonical serialization evidence without
   falsely treating an unavailable runtime as a model failure.

4. Acceptance strategy

   A single exploration can stop accepting once coverage goals are satisfied.
   To reliably produce exactly 10 accepted models, the batch ran 10 deterministic
   explorations and kept the first accepted positive candidate from each run.

## Validation Evidence

After promotion, a lightweight library audit checked:

- `manifest.json` contains 10 entries;
- 10 `.gcs.json` model files exist;
- 10 matching metadata files exist;
- every model has `format_version = gcs-0.3`;
- every manifest entry records the four local gates as `passed`.

Result: all checks passed.

## Maintenance Policy

Future generated models should follow the same path:

1. Run `explore_scene_space` with explicit seeds and stable exploration IDs.
2. Keep scratch exploration artifacts out of durable fixture locations.
3. Promote accepted candidates through `promote_candidate`.
4. Store public `.gcs.json` files in `fixtures/scene/generated`.
5. Store promotion metadata under `fixtures/scene/generated/metadata`.
6. Refresh `fixtures/scene/generated/manifest.json` and
   `fixtures/scene/generated/README.md`.
7. Record batch-level findings in `docs/completed-tasks`.

## Follow-Up Work

- Add a repo-level model-library maintenance command so future batches can
  refresh the manifest and README without hand-written shell glue.
- Decide whether the scratch exploration store should be ignored explicitly in
  `.gitignore`.
- Re-run promotion with public runtime smoke when `GCS.exe` is available in the
  expected location or through `public_gate_config.solver_command`.
