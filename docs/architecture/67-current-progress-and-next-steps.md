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

Current validation baseline:

- C++23 module build passes through `scripts\build_clang_ninja.cmd`.
- Contract test baseline is 84 CTest-discovered GTest cases.
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

## Next Step 26

The next step is store adapter containment: reduce remaining direct `.store`
path knowledge in `tools.py` and package helpers while preserving flat command
compatibility.

The registered forward plan is persisted in
`docs/architecture/68-forward-execution-plan-2026-05-24.md`. Steps 25 through
29 were registered there and in the implementation roadmap. After Step 25, the
remaining steps were reconsidered; Steps 26 through 29 remain registered, with
Step 26 still the next highest-leverage move.
