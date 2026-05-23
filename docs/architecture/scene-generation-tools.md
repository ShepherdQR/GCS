# Scene Generation And Auto Exploration

`tools/scene_generation` is local research, scenario exploration, and
fixture-authoring tooling. It is not part of solver runtime, GUI state, or the
scene IO contract. Its durable job is to produce reproducible candidate
scenes, validate them through public contracts, explain why they are useful,
and prepare promotion evidence for `fixtures/scene` when a human chooses to
promote a candidate.

## Current Audit

Audit date: 2026-05-24. Implementation refresh: 2026-05-24.

The pre-refresh `tools/scene_generation/tools.py` implementation was useful,
but it was not a complete scene auto explorer. The refreshed v1 now includes
`explore_scene_space`, `promote_candidate`, structured coverage, negative
evidence, deterministic traces, and promotion packages while keeping the older
single-step commands as compatibility wrappers.

Reusable pieces:

- deterministic scratch store under `tools/scene_generation/.store`;
- stable command entry point:
  `python tools\scene_generation\tools.py <command> --input "<json>"`;
- skeleton graph generation for `cycle_plus_chords` and `ear_decomposition`;
- Tarjan articulation and biconnected-component verifier;
- GCS lift from skeleton vertices to geometries and edges to constraints;
- constraint signature table for `Point`, `Line`, `Plane` pairs;
- rigid-set recoloring for cross-rigid-set constraint invariants;
- geometry parameter assignment for non-degenerate points, lines, and planes;
- schema validation for IDs, references, signatures, arity, geometry
  degeneracy, distance values, angle ranges, and rigid-set membership;
- projections for `geometry_primal`, `incidence_bipartite`, and
  `rigidset_quotient`;
- machine-readable graph report and canonical JSON/text serialization.

Original observed limits:

- The command family was a collection of single-step tools, not an explorer.
  This is addressed by `explore_scene_space`.
- `lift_skeleton_to_gcs` intentionally creates zero-valued geometry vectors.
  A lifted graph may fail schema validation until
  `assign_geometry_parameters` runs.
- Reports summarized one candidate, but did not compare candidates or explain
  why a scenario covers a missing solver behavior. The v1 explorer now tracks
  coverage goals and candidate contributions.
- The validator is generator-local. It does not yet round-trip through the
  C++ scene IO, kernel, runtime, diagnostics, or viewer contracts before a
  candidate is considered promotion-ready.
- Repair can make a graph pass local invariants, but it does not produce a
  minimal or semantically classified repair plan.
- There was no corpus manifest, provenance bundle, rejection corpus, or
  reproducible exploration trace. The v1 explorer writes request/result,
  candidate provenance, rejected-candidate evidence, and `trace.jsonl`.
- There were no tests around the Python generator itself. The v1 explorer has
  unittest coverage for determinism, negative evidence, and promotion gates.

Implemented public adapter gates:

- `scene_io_round_trip` writes a public `gcs-0.3` scene and verifies canonical
  JSON replay inside the promotion package.
- `kernel_validation` checks stable entity, constraint, rigid-set, and
  parameter-vector shape before promotion.
- `runtime_smoke` runs the configured solver command against the public scene.
- `diagnostics_evidence` verifies runtime output carries status and diagnostic
  stage evidence.
- `viewer_projection` binds the promotion package to the geometry-primal
  projection artifact.

Remaining limits:

- The runtime and diagnostics public gates require a local solver command.
  Without `GCS_EXE` or `public_gate_config.solver_command`, promotion remains
  blocked by explicit runtime/diagnostic gate evidence.
- The implementation still keeps parameterization, reporting, and exploration
  orchestration in `tools.py`, but Steps 20-22 have extracted contracts,
  storage rules, promotion adapters, topology helpers, GCS model helpers,
  validation, and projection into `gcs_scene_generation/`.
- Repair is still candidate-level and explicit. It is not a semantic minimal
  repair planner.

## Completeness Bar

The scene auto explorer is considered detailed enough only when it defines all
of the following:

- mission, non-goals, ownership boundary, and dependency direction;
- structured request and result schemas with stable IDs, seeds, budgets, and
  side-effect policy;
- candidate provenance from topology seed through serialized scene digest;
- explicit exploration objectives, coverage axes, novelty metrics, and stop
  conditions;
- local generator validation plus public contract validation through IO,
  kernel, runtime, diagnostics, and viewer boundaries where applicable;
- typed failure taxonomy and rejected-candidate evidence;
- deterministic trace and replay data;
- fixture promotion gate that is separate from scratch generation;
- tests that prove determinism, validation behavior, rejection behavior, and
  promotion evidence.

Current maturity is L3-L4 for the local explorer: structured contracts,
scratch corpus management, coverage accounting, local gates, traces, promotion
packages, public smoke gates, and tests exist. It remains below full L4 for
cross-module promotion because runtime/diagnostic proof depends on an external
solver command rather than a fully in-process contract adapter.

## Ownership Boundary

Owned by `tools/scene_generation`:

- synthetic topology generation;
- GCS candidate construction policy;
- candidate repair policy for scratch graphs;
- exploration plans, queues, traces, reports, and scratch storage;
- machine-readable candidate evidence and promotion packages.

Not owned by `tools/scene_generation`:

- solver-domain truth in `kernel`;
- residual definitions and signatures in `constraint_catalog`;
- structural graph contracts in `incidence_graph`;
- decomposition, numeric solve, diagnostics, runtime transactions, or viewer
  projection semantics;
- scene schema migration and canonical scene IO behavior.

The explorer may call public tools or executable checks from those modules, but
it must not copy their policy into generator-local truth.

## Target Workflow

The target auto-exploration path is:

```text
ExploreRequest
  -> build_exploration_plan
  -> generate_candidate_topology
  -> lift_candidate_to_gcs
  -> assign_candidate_parameters
  -> validate_candidate_locally
  -> run_public_contract_gates
  -> score_candidate
  -> keep_or_reject_candidate
  -> write_exploration_trace
  -> emit ExploreResult
```

Fixture promotion is a separate manual or explicit command path:

```text
PromotionRequest
  -> load accepted candidate
  -> re-run validation gates
  -> canonical serialize
  -> compute digest
  -> write promotion package
  -> optionally copy into fixtures/scene
```

No default exploration command should write to `fixtures/scene`.

## Structured Requests

The main command should be `explore_scene_space`. Compatibility commands such
as `generate_skeleton_graph`, `lift_skeleton_to_gcs`, and
`generate_graph_report` should continue to work.

Target request shape:

```json
{
  "exploration_id": "coverage_small_v1",
  "seed": 52024,
  "budget": {
    "max_candidates": 64,
    "max_accepts": 8,
    "max_seconds": 30
  },
  "topology_policy": {
    "vertex_counts": [3, 4, 5, 8, 12],
    "methods": ["cycle_plus_chords", "ear_decomposition"],
    "extra_edge_range": [0, 8],
    "require_vertex_biconnected": true
  },
  "gcs_policy": {
    "geometry_types": ["Point", "Line", "Plane"],
    "constraint_types": [
      "Coincident",
      "Parallel",
      "Perpendicular",
      "Distance",
      "Angle"
    ],
    "rigid_set_counts": [2, 3, 4],
    "require_cross_rigid_set_constraints": true
  },
  "parameter_policy": {
    "layouts": ["circular", "grid", "random"],
    "avoid_degenerate_geometry": true,
    "value_tolerance": 1e-9
  },
  "coverage_goals": [
    "all_geometry_types",
    "all_constraint_types",
    "mixed_rigid_sets",
    "biconnected_geometry_primal",
    "invalid_signature_negative_case",
    "same_rigid_set_negative_case",
    "io_round_trip_candidate"
  ],
  "gate_profile": "local_plus_public_smoke",
  "write_policy": {
    "store": "scratch",
    "keep_rejected": true,
    "promote": false
  }
}
```

Budgets must be honored deterministically. If time budget is used, the result
must still record how many candidates were attempted and why exploration
stopped.

## Structured Results

Target result shape:

```json
{
  "exploration_id": "coverage_small_v1",
  "status": "accepted_with_rejections",
  "seed": 52024,
  "stop_reason": "max_accepts",
  "summary": {
    "attempted": 17,
    "accepted": 8,
    "rejected": 9
  },
  "coverage": {
    "satisfied_goals": ["all_geometry_types"],
    "missing_goals": ["io_round_trip_candidate"],
    "histograms": {}
  },
  "accepted_candidates": [
    {
      "candidate_id": "coverage_small_v1_c0007",
      "gcs_graph_id": "coverage_small_v1_c0007_gcs",
      "score": 0.83,
      "schema_valid": true,
      "geometry_primal_biconnected": true,
      "digest": "sha256:..."
    }
  ],
  "rejected_candidates": [
    {
      "candidate_id": "coverage_small_v1_c0002",
      "reason_code": "invalid_constraint_signature",
      "evidence_ids": ["coverage_small_v1_c0002_validation"]
    }
  ],
  "trace_id": "coverage_small_v1_trace"
}
```

Human-readable summaries may be produced from this result, but the result
itself must not depend on prose for correctness.

## Candidate Model

Each candidate should be represented by one provenance bundle:

```json
{
  "candidate_id": "coverage_small_v1_c0007",
  "parent_exploration_id": "coverage_small_v1",
  "seed_path": {
    "exploration_seed": 52024,
    "topology_seed": 5202407,
    "lift_seed": 5202408,
    "parameter_seed": 5202409
  },
  "artifacts": {
    "skeleton_graph_id": "coverage_small_v1_c0007_skel",
    "gcs_graph_id": "coverage_small_v1_c0007_gcs",
    "projection_ids": ["coverage_small_v1_c0007_geom_primal"]
  },
  "policies": {},
  "reports": {},
  "digest": "sha256:..."
}
```

Stable IDs must be generated from `exploration_id`, candidate index, and
artifact role. Random generated IDs are acceptable only for ad hoc scratch
commands, never for replayable exploration or fixture promotion.

## Coverage Axes

The explorer should track at least these axes:

- topology size: vertex count, edge count, density, articulation status, and
  biconnected-component count;
- projection behavior: geometry primal, incidence bipartite, and rigid-set
  quotient summaries;
- geometry inventory: point, line, plane counts and mixed-type combinations;
- constraint inventory: type histogram and endpoint signature histogram;
- rigid-set structure: number of rigid sets, per-set geometry counts, and
  cross-rigid-set edge coverage;
- parameter behavior: non-degenerate lines, non-zero plane normals, distance
  ranges, angle ranges, and near-degenerate cases;
- expected validity: positive candidates, negative schema candidates, and
  repairable candidates;
- downstream gates: IO round trip, kernel validation, runtime command smoke,
  diagnostics report, and viewer projection when those checks are available.

Coverage goals should be explicit. A candidate is valuable only when it closes
at least one missing goal, improves distribution balance, or is retained as a
negative example with typed evidence.

## Validation Gates

Gate profiles:

- `local_only`: generator schema validation, projection, biconnectivity, and
  report generation.
- `local_plus_public_smoke`: `local_only` plus canonical serialization and any
  available public scene/kernel smoke checks.
- `promotion`: all local gates, canonical digest stability, scene IO
  round-trip, kernel validation, contract-tool invariant checks, and viewer
  projection if the fixture is meant for GUI consumption.

Every gate returns:

- `gate_id`;
- `status`: `passed`, `failed`, `skipped`, or `unsupported`;
- `reason_code`;
- `evidence`;
- `artifact_ids`;
- `duration_ms` when measured.

Unsupported gates are allowed during early implementation, but they must be
visible in reports and cannot be counted as promotion success.

## Failure Taxonomy

The explorer should use typed reason codes:

- `invalid_request`;
- `budget_exhausted`;
- `unknown_geometry_type`;
- `unknown_constraint_type`;
- `invalid_constraint_signature`;
- `constraint_same_rigid_set`;
- `degenerate_line`;
- `zero_plane_normal`;
- `negative_distance`;
- `invalid_angle_range`;
- `topology_not_connected`;
- `topology_has_articulation`;
- `io_round_trip_failed`;
- `kernel_validation_failed`;
- `runtime_smoke_failed`;
- `diagnostics_evidence_failed`;
- `viewer_projection_failed`;
- `promotion_gate_unsupported`.

The local validator may keep richer violation records, but these reason codes
are the stable cross-command taxonomy.

## Storage Layout

Scratch storage remains under `tools/scene_generation/.store`, but it should be
organized by exploration:

```text
tools/scene_generation/.store/
  explorations/
    coverage_small_v1/
      request.json
      result.json
      trace.jsonl
      candidates/
        c0007/
          skeleton.json
          gcs.json
          geometry_primal.json
          report.json
          provenance.json
```

The current flat-file store may remain for compatibility wrappers. New
exploration commands should use the structured layout.

Rejected candidates should be retained only when `write_policy.keep_rejected`
is true. Rejection records can omit full serialized graphs when storage size
matters, but must keep enough evidence to reproduce the failure from seeds and
policies.

## Search Strategy

Initial implementation should use deterministic enumerated search before any
agentic or stochastic optimization:

1. Enumerate topology policies in stable order.
2. Derive per-candidate seeds from the exploration seed and candidate index.
3. Generate skeleton and verify required topology.
4. Enumerate or seeded-sample geometry and constraint policies.
5. Parameterize and validate.
6. Score by uncovered goals first, then rarity of covered signatures, then
   graph simplicity.
7. Accept a candidate only if it improves coverage or is an explicitly
   requested negative case.

More advanced search, such as mutation or novelty search, may be added after
the deterministic baseline has tests.

## Repair Policy

Repair is a candidate transformation, not a substitute for generation
correctness.

Allowed scratch repairs:

- replace invalid constraint type with the first valid type for the endpoint
  signature;
- recolor geometry rigid sets so constraints connect distinct rigid sets;
- add valid constraints to make the geometry-primal projection vertex
  biconnected;
- reassign geometry parameters to remove trivial degeneracy.

Repair output must record:

- original candidate ID;
- repaired candidate ID;
- ordered edit list;
- invariant being repaired;
- post-validation gate results.

Promotion packages must identify whether a candidate was repaired.

## Promotion Packages

Promotion does not happen by default. When requested, the tool writes a package
that contains:

- source `ExploreRequest`;
- candidate provenance;
- local validation report;
- public gate reports;
- canonical serialization;
- digest;
- fixture metadata proposal;
- known unsupported gates, if any.

Only after the promotion package passes the `promotion` gate profile may a
human or explicit command copy data into `fixtures/scene`.

## Implementation Migration

Current v1 status:

- `explore_scene_space` and `promote_candidate` are implemented.
- Flat compatibility commands still work.
- `gcs_scene_generation.contracts`, `gcs_scene_generation.storage`, and
  `gcs_scene_generation.promotion` are implemented behind the `tools.py` CLI
  facade.
- `gcs_scene_generation.topology` and `gcs_scene_generation.gcs_model` are
  implemented behind the same facade.
- `gcs_scene_generation.validation` and `gcs_scene_generation.projection` are
  implemented behind the same facade.
- Structured exploration artifacts are written under
  `.store/explorations/<exploration_id>/`.
- Promotion packages are written under `.store/promotions/<promotion_id>/`.
- Deterministic unittest coverage exists for the local explorer and package
  boundaries.

Remaining migration path:

1. Continue extracting pure algorithm helpers from `tools.py` into package
   modules: `parameterization.py`, `reporting.py`, and `explorer.py`.
2. Keep `tools.py` as the CLI dispatcher and compatibility facade.
3. Move flat `.store` compatibility reads behind a store adapter.
4. Harden public gates from executable smoke checks into direct IO, contract
   tools, runtime, diagnostics, and viewer adapters as those APIs stabilize.

This is a rewrite of structure, not a rewrite of all algorithms.

## Acceptance Tests

Minimum tests before calling the explorer complete:

- same `ExploreRequest` and seed produce byte-identical `ExploreResult`;
- different seeds produce different candidate order while preserving validity;
- `local_only` accepts a valid biconnected candidate;
- invalid signature and same-rigid-set candidates are rejected with stable
  reason codes;
- repaired candidates include edit history and pass post-validation;
- coverage goals are marked satisfied only when evidence exists;
- promotion gate refuses unsupported public checks unless explicitly allowed;
- flat compatibility commands still support the documented generate, lift,
  parameterize, validate, project, report, and serialize path.

## Compatibility Command Path

The existing command path remains valid for manual candidate construction:

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

Important rule: a graph returned by `lift_skeleton_to_gcs` is not expected to be
schema-valid until `assign_geometry_parameters` has run.

Repair remains an alternate branch:

```text
validate_gcs_schema
  -> repair_gcs_graph
  -> assign_geometry_parameters
  -> validate_gcs_schema
  -> project_gcs_graph
  -> check_vertex_biconnected
```

## Final Design Decision

The refreshed implementation is sufficient as a complete local scene auto
explorer. It preserves the verified local algorithms, keeps the existing CLI
commands compatible, and adds an explicit exploration contract with coverage,
provenance, gates, traces, negative evidence, and promotion packages.

The next design step is structural: continue the Step 20 package split by
moving topology, lift, validation, projection, parameterization, reporting, and
explorer orchestration behind tested modules while preserving the current CLI
facade.
