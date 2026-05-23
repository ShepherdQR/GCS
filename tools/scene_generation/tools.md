# Scene Generation Tool Notes

This file is the implementation-side note for `tools.py`. The durable design
source is:

```text
docs/architecture/scene-generation-tools.md
```

The current implementation includes the compatibility command set plus a
complete local v1 scene auto explorer. The explorer is complete for local
generation, coverage, local validation, negative evidence, deterministic trace,
promotion-package creation, and public promotion smoke gates. Runtime and
diagnostics gates require a configured solver executable.

Step 20 starts the package split. `tools.py` remains the compatibility CLI
facade, while stable helper boundaries now live under
`gcs_scene_generation/`:

- `contracts.py`: generated graph constants, type maps, failure taxonomy, and
  signature validation.
- `storage.py`: deterministic store paths, JSON IO, trace append, safe IDs,
  and digests.
- `promotion.py`: public `gcs-0.3` scene conversion, kernel-shape validation,
  solver command normalization, and runtime smoke execution.
- `topology.py`: edge canonicalization, adjacency, connected components, and
  Tarjan biconnected-component evidence.
- `gcs_model.py`: geometry-primal edges, rigid-set rebuilding, geometry maps,
  rigid-set invariant checks, graph coloring, and rigid-set assignment.
- `validation.py`: generator-local schema validation for IDs, references,
  signatures, arity, degeneracy, scalar ranges, and rigid-set memberships.
- `projection.py`: geometry-primal, incidence-bipartite, and rigid-set
  quotient projection builders.
- `parameterization.py`: deterministic layout positions, geometry vectors,
  distance values, and angle values.
- `reporting.py`: machine-readable summaries, validation summaries,
  projection statistics, biconnectivity evidence, histograms, and rigid-set
  summaries.
- `repair.py`: generated-candidate repair policy, deterministic rigid-set
  recoloring, constraint-signature replacement, biconnectivity repair, and
  structured edit lists.

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
- `explore_scene_space`
- `promote_candidate`
- `list`
- `delete`

Outputs are JSON. Scratch artifacts are written to
`tools/scene_generation/.store`.

`GCS_SCENE_GENERATION_STORE_DIR` can point commands and tests at an alternate
scratch store.

## Auto Explorer

`explore_scene_space` accepts a structured request with:

- `exploration_id`;
- deterministic `seed`;
- `budget.max_candidates`, `budget.max_accepts`, and optional
  `budget.max_seconds`;
- topology, GCS, and parameter policies;
- explicit `coverage_goals`;
- `gate_profile`: `local_only`, `local_plus_public_smoke`, or `promotion`;
- `write_policy.keep_rejected`.

The command writes:

```text
.store/
  explorations/<exploration_id>/
    request.json
    result.json
    trace.jsonl
    candidates/<candidate>/
      provenance.json
      gcs.json
      geometry_primal.json
      report.json
```

Accepted candidates must pass local schema validation and geometry-primal
biconnectivity. Negative candidates are retained when requested by coverage
goals, including invalid constraint signatures and same-rigid-set constraints.

`promote_candidate` reloads an accepted candidate and writes a promotion package
under `.store/promotions/<promotion_id>/`. The default `promotion` gate profile
now converts the generator graph into a public `gcs-0.3` scene and runs public
adapter gates:

- scene JSON round trip;
- kernel-shape validation over the public scene;
- structured runtime evidence from `public_gate_config.runtime_report` or
  `public_gate_config.runtime_report_path`, with executable smoke fallback
  through `GCS.exe` or `public_gate_config.solver_command`;
- diagnostics evidence from structured runtime reports or fallback runtime
  output;
- viewer projection evidence from the generated geometry-primal projection.

Pass `public_gate_config.runtime_report` or
`public_gate_config.runtime_report_path` when structured runtime/diagnostics
evidence is already available. Otherwise set `GCS_EXE` or pass
`public_gate_config.solver_command` when the default
`out/build/clang-ninja/GCS.exe` is not available. Use
`gate_profile: "local_only"` for a local-only promotion package.

## Reusable Implementation Pieces

Keep these pieces when rewriting the explorer structure:

- deterministic JSON save/load helpers;
- `SceneGenerationStore` adapter for scratch-store path policy, graph IO,
  exploration roots, promotion roots, candidate roots, trace append, and
  digests;
- edge canonicalization and sorted graph traversal in
  `gcs_scene_generation.topology`;
- connected-component and Tarjan biconnectivity checks in
  `gcs_scene_generation.topology`;
- skeleton generators for `cycle_plus_chords` and `ear_decomposition`;
- geometry and constraint signature tables in `gcs_scene_generation.contracts`;
- rigid-set coloring and GCS model helpers in `gcs_scene_generation.gcs_model`;
- local schema validation in `gcs_scene_generation.validation`;
- geometry-primal, incidence-bipartite, and rigid-set quotient projections in
  `gcs_scene_generation.projection`;
- parameter assignment for non-degenerate point, line, and plane data in
  `gcs_scene_generation.parameterization`;
- graph reporting in `gcs_scene_generation.reporting`;
- repair policy in `gcs_scene_generation.repair`;
- exploration request/result orchestration, candidate construction, coverage
  accounting, negative evidence, and trace writing in
  `gcs_scene_generation.explorer`;
- promotion package writing, public gate reports, and blocking rules in
  `gcs_scene_generation.promotion_package`;
- structured runtime/diagnostics report preference before executable smoke
  fallback in `gcs_scene_generation.promotion_package`;
- canonical JSON and custom text serialization;
- public scene conversion and solver smoke adapters in
  `gcs_scene_generation.promotion`.

## Implemented Explorer Pieces

The v1 explorer now provides:

- `explore_scene_space` command;
- structured exploration request/result schemas;
- stable candidate IDs and provenance bundles;
- coverage goals and deterministic scoring;
- explicit budgets and stop reasons;
- rejected-candidate evidence;
- deterministic `trace.jsonl`;
- local validation gates and public promotion smoke gates;
- `promote_candidate` package generation separate from fixture copying;
- Python unittest coverage for determinism, negative evidence, and promotion
  gate behavior;
- package-boundary coverage for contracts, storage safety, and public scene
  conversion.
- direct package-boundary coverage for explorer request normalization,
  coverage evidence, and promotion package blocking contracts.

## Rewrite Direction

Recommended package split:

```text
tools/scene_generation/
  tools.py              # CLI facade and compatibility commands
  gcs_scene_generation/
    contracts.py        # implemented
    storage.py          # implemented, includes SceneGenerationStore
    promotion.py        # implemented
    topology.py         # implemented
    gcs_model.py        # implemented
    validation.py       # implemented
    projection.py       # implemented
    parameterization.py # implemented
    reporting.py        # implemented
    repair.py           # implemented
    explorer.py         # implemented
    promotion_package.py # implemented
```

The current v1 keeps command compatibility inside `tools.py`. Step 20 moved
contracts/storage/promotion helpers, Step 21 moved topology plus GCS model
helpers, Step 22 moved validation plus projection helpers, Step 23 moved
parameterization plus reporting helpers, Step 24 moved repair policy, and
Step 25 moved explorer plus promotion-package orchestration. Step 26 contained
scratch-store path and IO policy behind `SceneGenerationStore`; public command
compatibility still flows through `tools.py`. Step 27 hardened promotion gates
by preferring structured runtime/diagnostics reports before executable smoke
fallback. Solver algorithm deepening remains the next structural split. Do not
move generation policy into the solver, GUI, or scene IO modules.

## Tests

Run the local explorer tests with:

```bat
python -m unittest tests.tools.test_scene_generation_explorer
```
