# Current Progress And Next Steps

## Status As Of 2026-05-24

The implementation is in the second algorithm-deepening batch. The initial
C++23 module architecture batch is complete through kernel, constraint catalog,
incidence graph, decomposition planner, numeric engine, diagnostics, session
runtime, IO adapters, viewer bridge, contract tools, dependency audits, and
cross-module quality gates.

Completed algorithm-deepening steps:

- Step 14: replaced the numeric identity local-section placeholder with a
  dense damped Gauss-Newton local solve.
- Step 15: added JSON scene reading, explicit schema migration reports, JSON
  round-trip support, and malformed JSON negative fixtures.
- Step 16: promoted diagnostics conflict and redundancy candidates from typed
  placeholders into public diagnostic tools.
- Step 17: expanded reusable fixture corpus and golden report digests with
  typed fixture expectations and cross-module evidence checks.
- Step 18: promoted contract, dependency, fixture, scene, and CLI checks into
  a single CI-ready quality gate command.
- Step 19: connected scene auto explorer promotion packages to public IO,
  kernel, runtime, diagnostics, and viewer gate adapters.
- Step 20: started the scene-generation package split by extracting
  contracts, storage, and public promotion adapters from the CLI facade.
- Step 21: continued the scene-generation package split by extracting
  topology and GCS model helpers while preserving manual generation flow.
- Step 22: extracted validation and projection helpers with focused structured
  contract tests.
- Step 23: extracted parameterization and reporting helpers with deterministic
  structured tests.
- Step 24: extracted repair policy with structured edit-list tests.
- Step 25: split scene-generation explorer and promotion orchestration from
  the CLI facade.
- Step 26: contained scene-generation scratch-store and path policy behind
  `SceneGenerationStore`.
- Step 27: hardened public promotion gates so structured runtime/diagnostics
  evidence is preferred before executable smoke fallback.
- Step 28: refined numeric rank/nullity evidence so boundary-frozen variables
  are excluded from rank estimation while full variable shape remains reported.
- Step 29: synchronized the architecture atlas and Figure 1 assets with
  scene-generation promotion boundaries, contract tools, and free/frozen rank
  evidence.
- Step 30: propagated numeric full/free/frozen rank dimensions through
  diagnostics rank evidence.
- Step 31: exposed preserved rank evidence through runtime projections and
  viewer overlay/summary contracts.
- Step 32: made scene-generation promotion gates consume structured rank
  evidence from public runtime/viewer reports.
- Step 33: added typed SolveDAG evidence for decomposition boundary
  projection dependencies.
- Step 34: added boundary-aware post-local diagnostics to session runtime
  command results and stage traces.
- Step 35: deepened diagnostics conflict and redundancy evidence with
  residual entity subjects and exact duplicate constraint signatures.
- Step 36: hardened numeric convergence and condition evidence by using
  max-absolute residual tolerance and suppressing condition estimates for
  singular free Jacobians.
- Step 37: expanded reusable contract-tools fixtures for boundary-frozen,
  tolerance-edge, and separator-chain scenarios.
- Step 38: exposed residual, conflict, redundancy, and obstruction evidence
  through structured viewer overlays and summaries.

Current validation baseline:

- C++23 module build passes through `scripts\build_clang_ninja.cmd`.
- Contract test baseline is 100 CTest-discovered GTest cases.
- Representative CLI fixture `fixtures\scene\basic\g1.txt` solves and commits
  through session runtime.
- Architecture docs, module inventory, and dependency boundary checks pass.
- Default quality gate entry point:
  `python tools\agentic_design\agentic_toolkit.py run-quality-gates`.

## Completed Step 17

Step 17 expands the reusable fixture corpus and golden report digest surface.
The goal is to stop relying on ad hoc test-local model construction for core
negative, singular, redundant, inconsistent, migration, and gluing-obstruction
scenarios.

Delivered:

- Extend `gcs.contract_tools` fixture kinds with reusable under-constrained,
  over-constrained, redundant, inconsistent, singular, and gluing-obstruction
  model bundles.
- Add typed corpus generation contracts so tests can request a deterministic
  suite rather than listing fixture kinds manually.
- Strengthen golden report summaries so digest inputs include fixture class,
  provenance, schema version, expected status, structural counts, and report
  codes.
- Keep pure mathematical negative fixtures in contract-tool builders and rely
  on the existing JSON scene migration corpus for persistence-format cases.
- Add contract tests that verify each fixture class produces the expected
  structured status/report evidence through public module APIs.

## Completed Step 18

Step 18 promotes contract, dependency, fixture, scene, and CLI checks into
CI-ready quality gates.

Delivered:

- Add `run-quality-gates` to `tools/agentic_design/agentic_toolkit.py`.
- Add Windows wrappers under `scripts/`.
- Run agentic docs, inventory, skill, and dependency validation by default.
- Run scene-generation Python tests by default.
- Run CMake configure/build, full CTest, explicit `ContractToolsContract`
  fixture corpus tests, and a representative CLI smoke fixture by default.
- Document the gate contract in
  `docs/architecture/69-ci-ready-quality-gates.md`.

## Completed Step 19

Step 19 replaces scene-generation promotion placeholders with public adapters.

Delivered:

- Convert generated candidates into public `gcs-0.3` scene artifacts.
- Add promotion gates for scene IO round trip, kernel-shape validation,
  runtime smoke, diagnostics evidence, and viewer projection.
- Let tests and CI inject `public_gate_config.solver_command`, while local use
  defaults to `GCS_EXE` or `out/build/clang-ninja/GCS.exe`.
- Write `public_scene.gcs.json` into promotion packages.
- Extend scene-generation tests with fake-solver public promotion coverage.

## Completed Step 20

Step 20 starts the scene-generation package split while preserving the existing
CLI command surface.

Delivered:

- Add `gcs_scene_generation.contracts` for type maps, signature validation,
  and stable failure taxonomy.
- Add `gcs_scene_generation.storage` for safe IDs, deterministic JSON IO,
  scratch-store layout, trace append, and digests.
- Add `gcs_scene_generation.promotion` for public `gcs-0.3` scene conversion,
  public kernel-shape validation, solver command resolution, and runtime smoke.
- Keep `tools.py` as the compatibility CLI facade.
- Extend scene-generation unit tests with package-boundary coverage.

## Completed Step 21

Step 21 moves the next pure helper layer out of the scene-generation CLI
facade.

Delivered:

- Add `gcs_scene_generation.topology` for edge canonicalization, adjacency,
  connected components, and Tarjan biconnected-component evidence.
- Add `gcs_scene_generation.gcs_model` for geometry-primal edges, rigid-set
  rebuilding, geometry maps, invariant checks, graph coloring, and rigid-set
  assignment.
- Keep `tools.py` as the CLI facade through compatibility wrappers.
- Extend tests with a manual generate -> lift -> parameterize -> validate ->
  project -> biconnectivity path.

## Completed Step 22

Step 22 moves validation and projection helpers out of the scene-generation
CLI facade.

Delivered:

- Add `gcs_scene_generation.validation` for IDs, references, signatures,
  arity, degeneracy, scalar ranges, and rigid-set membership validation.
- Add `gcs_scene_generation.projection` for geometry-primal,
  incidence-bipartite, and rigid-set quotient projection builders.
- Keep `tools.py` as the CLI facade through compatibility wrappers.
- Extend tests with invalid-signature evidence and projection shape checks.

## Completed Step 23

Step 23 moves parameterization and reporting helpers out of the
scene-generation CLI facade.

Delivered:

- Add `gcs_scene_generation.parameterization` for deterministic layout
  positions, geometry vectors, distance values, and angle values.
- Add `gcs_scene_generation.reporting` for graph summaries, validation
  summaries, projection statistics, biconnectivity evidence, histograms, and
  rigid-set summaries.
- Keep `tools.py` as the CLI facade through compatibility wrappers.
- Extend tests with deterministic parameter assignment and report summary
  checks.

## Completed Step 24

Step 24 moves repair policy out of the scene-generation CLI facade.

Delivered:

- Add `gcs_scene_generation.repair` for constraint-signature replacement,
  deterministic rigid-set recoloring, biconnectivity repair, and structured
  edit lists.
- Keep `tools.py` as the CLI facade through a compatibility wrapper around
  `repair_gcs_graph`.
- Extend tests with direct repair-module input/output checks and post-repair
  validation.

## Completed Step 25

Step 25 split explorer and promotion orchestration from `tools.py`.

Delivered:

- Add `gcs_scene_generation.explorer` for structured exploration request
  normalization, candidate construction, candidate gates, coverage scoring,
  negative evidence, trace writing, and `ExploreResult` assembly.
- Add `gcs_scene_generation.promotion_package` for public adapter gate
  reports, promotion-package assembly, blocking status rules, promotion
  artifact writing, and candidate provenance loading.
- Keep `tools.py` as the CLI dispatcher and compatibility facade over package
  modules.
- Extend unittest coverage with direct package-boundary checks for explorer
  request/coverage contracts and promotion blocking contracts.

## Completed Step 26

Step 26 contained store/path policy behind `SceneGenerationStore`.

Delivered:

- Add `gcs_scene_generation.storage.SceneGenerationStore` for scratch-store
  path policy, graph IO, safe IDs, JSON IO, exploration roots, candidate
  roots, promotion roots, trace append, and digest helpers.
- Route `tools.py` compatibility storage wrappers through the adapter.
- Route explorer services and promotion-package helpers through the adapter
  instead of raw store-path threading.
- Extend focused unittest coverage for adapter save/load/list plus exploration
  and promotion root contracts.

## Completed Step 27

Step 27 hardened promotion public gates.

Delivered:

- Add `public_gate_config.runtime_report` and
  `public_gate_config.runtime_report_path` as structured runtime/diagnostics
  evidence inputs.
- Prefer structured runtime reports for `runtime_smoke` and
  `diagnostics_evidence` gate evidence.
- Keep `public_gate_config.solver_command`, `GCS_EXE`, and the default
  executable smoke path as fallback behavior.
- Extend focused unittest coverage so structured runtime evidence passes public
  gates even when the fallback executable is missing.

## Completed Step 28

Step 28 resumed solver algorithm deepening in `gcs.numeric_engine`.

Delivered:

- Extend `RankConditionReport` with `free_variable_dimension` and
  `frozen_variable_dimension`.
- Estimate rank, nullity, singularity, under-constrained evidence,
  over-constrained evidence, and condition evidence from only the Jacobian
  columns that are free after applying boundary-variable policy.
- Preserve full `variable_dimension` in the same report so diagnostics can
  distinguish active model shape from numeric solve degrees of freedom.
- Extend numeric engine contract tests with boundary-frozen rank evidence.

## Completed Step 29

Step 29 synchronized the architecture atlas and generated Figure 1 artifacts.

Delivered:

- Update the Mermaid atlas with `contract_tools`, scene-generation package
  boundaries, `SceneGenerationStore`, public promotion gates, and free/frozen
  numeric rank evidence.
- Add a dedicated scene-generation and promotion tooling diagram.
- Document canonical generated SVG assets separately from tracked review
  artifacts.
- Update the Figure 1 renderer and layout so the rank card reports full
  variables, free columns, frozen columns, and nullity.
- Regenerate the main Figure 1 SVG and residual/rank panel SVG.

## Completed Step 30

Step 30 propagated free/frozen numeric rank evidence through diagnostics.

Delivered:

- Extend `diagnostics::RankReport` with
  `numeric_free_variable_dimension` and
  `numeric_frozen_variable_dimension`.
- Populate diagnostics rank evidence from
  `numeric::RankConditionReport` without changing status precedence.
- Add diagnostics contract coverage for a boundary-frozen numeric task.
- Update solver contract docs so diagnostics rank reports preserve structural
  evidence separately from numeric full/free/frozen evidence.

## Completed Step 31

Step 31 exposed full/free/frozen rank evidence through public runtime and
viewer contracts.

Delivered:

- Add `runtime::RankEvidenceProjection` and
  `runtime::project_rank_evidence(const CommandResult&)`.
- Project full variable dimension, free variable dimension, frozen variable
  dimension, residual dimension, rank, nullity, under/over/singular flags, and
  condition evidence from command results.
- Extend viewer diagnostic overlays and command summaries with structured rank
  evidence plus detailed `viewer.rank_evidence` overlay items.
- Keep viewer code on the runtime public projection rather than parsing
  numeric-engine internals directly.
- Add accepted runtime and boundary-frozen viewer contract coverage.

## Completed Step 32

Step 32 made promotion gate rank evidence consumption explicit.

Delivered:

- Add a first-class `rank_evidence` promotion gate for structured runtime
  reports.
- Parse public rank evidence paths including `rank_evidence` and
  `viewer_overlay.rank_evidence`.
- Validate full/free/frozen dimensions, residual dimension, rank, nullity,
  under/over/singular flags, and condition evidence shape.
- Treat missing structured rank evidence as a skipped non-blocking gate while
  failing malformed supplied evidence.
- Preserve executable smoke fallback when no structured runtime report is
  supplied.

## Completed Step 33

Step 33 deepened decomposition planner SolveDAG evidence.

Delivered:

- Add `SolveDagNode`, `SolveDagEdge`, `SolveDag`, and
  `SolveDagValidationReport`.
- Extend `PlannerOutput` with `solve_dag`.
- Map component boundary projections into DAG edges from local component
  contexts to the root aggregation context.
- Validate DAG node references, edge node references, projection-to-cover
  consistency, acyclic topological order, and subproblem coverage.
- Add contract coverage for accepted boundary-projection dependencies and
  rejected backward dependency evidence.

## Completed Step 34

Step 34 added boundary-aware runtime diagnostics.

Delivered:

- Add `PostLocalDiagnosticReport`.
- Extend `CommandResult` with `post_local_diagnostics`.
- Run `diagnostics::diagnose(post_local_solve)` after each successful local
  numeric solve.
- Record `post_local_diagnostics` as a transaction stage before gluing.
- Make `runtime::project_rank_evidence` prefer diagnostics-owned post-local
  rank reports with numeric-report fallback for legacy/manual results.
- Preserve rollback semantics for blocking post-local diagnostic statuses.

## Completed Step 35

Step 35 deepened diagnostics conflict and redundancy evidence.

Delivered:

- Extend conflict and redundancy search requests with `ModelSnapshot` so
  public diagnostic tools can resolve constraint/entity subjects and compare
  constraint signatures.
- Enrich `diagnostics.residual_conflict` with the unsatisfied constraint ID
  and owning entity IDs.
- Add exact duplicate distance redundancy evidence through
  `diagnostics.redundant_duplicate_distance`.
- Preserve broad `diagnostics.overconstrained_redundancy_candidate` evidence
  for structurally or numerically over-constrained contexts.
- Keep status precedence and gluing obstruction conflicts stable.

## Completed Step 36

Step 36 hardened numeric residual and condition evidence.

Delivered:

- Use maximum absolute residual value for convergence against residual
  tolerance, while keeping residual norm as report and trace evidence.
- Avoid publishing finite condition estimates when the effective free
  Jacobian is rank deficient.
- Preserve `NumericTask`, `NumericReport`, and `RankConditionReport` public
  shapes.
- Add numeric contract tests for tolerated multi-residual stopping and
  singular-rank condition suppression.

## Completed Step 37

Step 37 expanded the reusable fixture corpus.

Delivered:

- Add `boundary_frozen_distance`, `tolerated_multi_residual_distance`, and
  `separator_chain_distance` fixture kinds.
- Add `boundary_frozen`, `tolerance_edge`, and `separator` fixture classes.
- Encode boundary-frozen solve hints through `ModelSnapshot.solve_intent`.
- Promote the tolerated multi-residual numeric robustness scenario out of a
  local test helper and into public contract tools.
- Increase default generated corpus coverage from 10 to 13 fixture bundles.
- Add contract-tool tests for boundary-frozen solve hints, max-absolute
  residual stopping evidence, and separator-chain subject structure.

## Completed Step 38

Step 38 exposed structured viewer evidence surfaces.

Delivered:

- Add viewer residual evidence projections with per-constraint residual,
  max-absolute residual, tolerance, and satisfaction fields.
- Add viewer responsibility evidence projections for conflicts,
  redundancies, and obstructions.
- Populate `DiagnosticOverlay` and `SnapshotSummary` with those structured
  projections from post-local diagnostics and gluing/obstruction reports.
- Add detailed overlay item codes for residual, conflict, redundancy, and
  obstruction evidence while preserving existing message items.
- Keep Python GUI unchanged for now; the stable C++ viewer bridge contract is
  ready for GUI consumption.

## Next Step 39

The next step is quality gate hardening. Rank, diagnostics, promotion,
fixture corpus, and viewer evidence paths are now public, so deterministic and
affordable checks should be promoted into the default gate where they protect
the Step 31-38 evidence chain.

The registered forward plan is persisted in
`docs/architecture/68-forward-execution-plan-2026-05-24.md`. Steps 1 through
40 are registered in the implementation roadmap; Steps 31 through 40 are
expanded with detailed goal, expected shape, detailed plan, and exit criteria
in the forward plan. After Step 38, the remaining steps were reconsidered;
Step 39 is registered as the next highest-leverage move. A post-Step-40
candidate is also recorded for an integrated feature showcase constraint graph.
