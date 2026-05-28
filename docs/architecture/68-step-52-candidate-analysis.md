# Step 52 Candidate Analysis

Date: 2026-05-28
Status: analysis
Prepared for: Next implementation planning after Steps 1-51

## 1. Current Solver State Summary

### 1.1 Module Inventory (src/gcs/)

All 9 target C++23 modules are compiled and contract-tested:

| Module | Status | Key Capability |
|--------|--------|---------------|
| `gcs.kernel` | Canonical | Stable IDs, snapshots, contexts, deltas, validation, diffs |
| `gcs.constraint_catalog` | Active | 5 constraint types (coincident, parallel, perpendicular, distance, angle), residual/Jacobian evaluation, finite-difference checks, degeneracy probes |
| `gcs.incidence_graph` | Active | Hypergraph, reverse indices, rigid-body graph, connected components, rigid-set pair grouping, graph dumps, spanning-tree support types |
| `gcs.decomposition_planner` | Active | Connected-component cover plan, boundary projections, SolveDAG, solve order, spanning forest plan (all patterns unsupported), cover/solve-order/DAG validation |
| `gcs.numeric_engine` | Active | Dense damped Gauss-Newton local solve, free/frozen column rank evidence, max-absolute residual convergence, trust-region backtracking, equation assembly through catalog |
| `gcs.diagnostics` | Active | Pre/post-local-solve diagnostics, gluing, obstruction, conflict/redundancy search with entity subjects, status precedence, DOF/rank/residual reports |
| `gcs.session_runtime` | Active | Command validation, transaction isolation, stage traces, atomic commit, rollback, history, replay evidence export, rank evidence projection, post-local diagnostics |
| `gcs.io_adapters` | Active | Text/JSON scene IO, schema registry (gcs-0.3), canonical digests, migration reports, behavior round-trip |
| `gcs.viewer_bridge` | Active | Scene projection, diagnostic overlays, interaction command drafts, history frame projection, replay evidence summary/report artifact, snapshot summaries |

### 1.2 Contract Test Baseline

109 CTest-discovered GTest cases across all modules. Default quality gate is `run-quality-gates`.

### 1.3 Constraint Type Coverage

Only 5 built-in constraint types:
- coincident (entity-entity)
- parallel (line/plane direction alignment)
- perpendicular (line/plane direction orthogonality)
- distance (scalar distance between points, point-line, point-plane)
- angle (scalar angle between lines/planes)

### 1.4 Decomposition Depth

The planner currently does a simple split: either whole-model (single component) or per-connected-component decomposition. There is no articulation-based or biconnected decomposition. The spanning forest plan implementation exists but marks ALL edge patterns as unsupported (comment: "no real pattern catalog exists yet").

### 1.5 Numeric Solver Depth

The numeric engine uses a single algorithm: dense damped Gauss-Newton with backtracking line search. There is no sparse solver, no Levenberg-Marquardt variant, no construction-based solving, and no caching of numeric results across solve calls.

### 1.6 What the Past 10 Steps (42-51) Were Doing

Steps 42-51 were infrastructure and evidence-chain hardening, not solver algorithm deepening:
- Steps 42-45: Scene behavior, cross-language compatibility, history/replay policy
- Steps 46-50: Runtime replay evidence export and CLI consumer paths
- Step 51: Promoted fixture library gate

The last algorithm-deepening steps were 33-38 (decomposition SolveDAG, boundary-aware diagnostics, conflict/redundancy deepening, numeric robustness, fixture corpus expansion, viewer evidence surfaces).

---

## 2. Candidate Directions for Step 52

### Candidate A: Articulation and Biconnected Decomposition

**What it is:** Implement Tarjan's algorithm for biconnected components and articulation points (cut vertices) on the incidence graph, then use those separators to build finer-grained context covers. The decomposition planner would decompose a connected component at its articulation points instead of treating it as a monolithic subproblem.

**Files to touch:**
- `src/gcs/incidence_graph/incidence_graph.cppm` -- add articulation/biconnected types and functions
- `src/gcs/incidence_graph/incidence_graph.cpp` -- implement Tarjan biconnected decomposition + articulation point detection
- `src/gcs/decomposition_planner/decomposition_planner.cppm` -- might need minor extensions to PlannerOutput for articulation-aware covers
- `src/gcs/decomposition_planner/decomposition_planner.cpp` -- wire biconnected results into plan_decomposition
- `tests/contracts/incidence_graph/incidence_graph_contract_tests.cpp` -- articulation/biconnected tests
- `tests/contracts/decomposition_planner/decomposition_planner_contract_tests.cpp` -- cover shape tests for biconnected splits

**Pros:**
- Makes the local-to-global architecture real: smaller subproblems, more parallelism opportunities
- Directly addresses a documented gap ("Incidence-level separator or biconnected reports remain queued" from Step 33)
- The incidence graph module already has the graph structure; Tarjan is a well-understood algorithm
- Foundation for later: Laman-style rigidity tests need the block tree
- Testable with controlled graph fixtures (chain, tree, cycle, dumbbell)

**Cons:**
- Requires extending the cover plan model -- multiple biconnected components sharing an articulation entity
- Numeric solve already handles the whole component; biconnected decomposition may not change the solve result for small models
- Overlap/gluing contract must handle articulation-owned entities carefully (entity belongs to multiple subproblems)

**Risk:** Medium. The algorithm is well-known, but the cover/gluing contract extension has semantic risk.

**Estimated scope:** 1-2 sessions (types + algorithm + tests + wiring into planner).

---

### Candidate B: Spanning Tree Pattern Catalog -- First Real Pattern

**What it is:** Implement the first supported spanning-tree pattern. The existing `plan_spanning_forest` infrastructure marks all patterns unsupported. A "pattern" declares how a cross-rigid-set constraint (or small constraint group) absorbs DOFs, enabling the solver to build a rigid-set spanning tree and partition constraints into "absorbed by tree" and "closure residuals."

The first pattern could be "point-to-point distance" between two rigid sets, which is the simplest and most common cross-rigid-set constraint. It absorbs 1 DOF (translational along the distance direction).

**Files to touch:**
- `src/gcs/decomposition_planner/decomposition_planner.cppm` -- extend `SpanningTreePatternId` with a concrete pattern enum, add pattern catalog types
- `src/gcs/decomposition_planner/decomposition_planner.cpp` -- implement pattern matching, DOF accounting, weight assignment
- `tests/contracts/decomposition_planner/decomposition_planner_contract_tests.cpp` -- patterns, DOF removal, tree edge orientation tests

**Pros:**
- The infrastructure (types, Kruskal, BFS orientation, report types) already exists
- This is the path toward Laman-style rigidity counts and generically-rigid detection
- Directly helps the solver handle multi-rigid-set scenes correctly
- Low-risk: one pattern at a time, clear exit criteria

**Cons:**
- Patterns are enumeration-based; the full catalog will take many steps
- A single pattern doesn't dramatically change solver behavior for the current fixture corpus
- The spanning forest plan isn't consumed by plan_decomposition yet -- the planner ignores it

**Risk:** Low. The types and infrastructure are already in place; adding one pattern is well-scoped.

**Estimated scope:** 1 session (pattern match + DOF accounting + tests).

---

### Candidate C: New Constraint Type -- Tangency or Symmetry

**What it is:** Add a 6th built-in constraint type. Tangency is the most natural next constraint for a CAD solver: point-on-circle, line-tangent-to-circle, circle-tangent-to-circle. Alternatively, symmetry (point reflected across plane/line) is fundamental.

**Files to touch:**
- `src/gcs/kernel/kernel.cppm` -- add `tangency` or `symmetry` to `ConstraintKind` enum
- `src/gcs/constraint_catalog/constraint_catalog.cppm` -- add entity signature, parameter schema, residual dimension
- `src/gcs/constraint_catalog/constraint_catalog.cpp` -- implement residual evaluator, Jacobian (finite-difference baseline is acceptable)
- `tests/contracts/constraint_catalog/constraint_catalog_contract_tests.cpp` -- validation, residual, Jacobian tests
- Possibly `fixtures/scene/` for new test scenes

**Pros:**
- Visible user-facing progress: solver handles more constraint types
- Each new constraint type is self-contained and adds to the solver's expressiveness
- Tests are straightforward (known geometry, expected residual/Jacobian shape)
- Tangency or symmetry are both geometric, well-defined, and documented in literature

**Cons:**
- Tangency requires a circle entity type, which doesn't exist yet (point, line, plane only). Symmetry could work with existing entity types but needs careful entity-signature design.
- Constraint types without the decomposition/spanning-tree work are "islands" -- the solver can evaluate them but can't plan well for them
- Doesn't deepen algorithm quality; broadens the solver instead

**Risk:** Medium. Tangency requires circle support (new GeometryKind). Symmetry could be done with existing kinds but the entity signature is non-trivial.

**Estimated scope:** 1-2 sessions (constraint type + tests + fixtures).

---

### Candidate D: Gluing Assembly Deepening -- Boundary-Aware Assembly

**What it is:** The current `glue_local_sections` in diagnostics merges local sections naively (direct parameter transfer). A deeper gluing step would: (1) solve a reduced boundary system over overlap variables, (2) detect boundary disagreement with structured evidence, (3) produce a global proposal that is guaranteed to satisfy boundary constraints within tolerance.

Currently, `BoundaryAgreementReport` exists but the actual assembly implementation is placeholder-level.

**Files to touch:**
- `src/gcs/diagnostics/diagnostics.cppm` -- extend `GluingReport` with assembly strategy evidence
- `src/gcs/diagnostics/diagnostics.cpp` -- implement boundary-aware global assembly
- `tests/contracts/diagnostics/diagnostics_contract_tests.cpp` -- boundary agreement, multi-subproblem assembly tests

**Pros:**
- The local-to-global pipeline's distinguishing feature vs. monolithic solvers
- Directly improves correctness for multi-component models
- Boundary assembly is a well-studied problem (domain decomposition, FETI methods)

**Cons:**
- Requires multiple components to test well; current fixture corpus has mostly single-component scenes
- The existing naive merge may be "good enough" for current small models
- Architectural risk: boundary assembly can be done many ways; choosing the right contract matters

**Risk:** Medium-High. Good design requires clarity on the separation between diagnostics (reporting) and assembly (numerics).

**Estimated scope:** 1-2 sessions (assembly strategy + boundary system solve + tests).

---

### Candidate E: Second Numeric Solver Backend (Levenberg-Marquardt or Sparse)

**What it is:** Add a second local solve algorithm behind the `NumericTask`/`NumericReport` contract. The most useful next backend is Levenberg-Marquardt (variable damping) or a sparse Cholesky-based Newton solver (for larger systems).

**Files to touch:**
- `src/gcs/numeric_engine/numeric_engine.cppm` -- no public API change needed (same contract)
- `src/gcs/numeric_engine/numeric_engine.cpp` -- add second solver, possibly behind a policy enum
- `tests/contracts/numeric_engine/numeric_engine_contract_tests.cpp` -- behavior consistency across backends

**Pros:**
- The contract already supports multiple backends (task/report separation)
- LM is a natural upgrade from damped GN (adaptive damping, better convergence for ill-conditioned problems)
- Sparse would unlock larger scenes

**Cons:**
- The current dense solver handles all current fixtures well
- Dense GN to LM is a marginal improvement without large-scale scenes that expose ill-conditioning
- Sparse requires either an external dependency (Eigen, SuiteSparse) or a hand-rolled sparse linear algebra layer
- Does not address the decomposition depth gap

**Risk:** Low for LM (same dense infrastructure, just change the damping logic). High for sparse (external dependency or substantial new code).

**Estimated scope:** LM: 1 session. Sparse: 3+ sessions.

---

## 3. Recommendation

**Recommendation: Candidate A (Articulation and Biconnected Decomposition).**

### Rationale

1. **Closes the longest-standing documented gap.** The decomposition architecture doc (`20-solver-pipeline/decomposition-planning.md`) lists "Articulation and biconnected structure: split along separators" as the 4th structural layer. The roadmap has listed it since Step 1. Step 33 explicitly deferred it: "Incidence-level separator or biconnected reports remain queued for a later planner/graph batch." This is the natural moment to pay off that debt.

2. **Makes the local-to-global architecture real.** The current planner produces either 1 subproblem (whole model) or N subproblems (one per connected component). For the common case of a single connected component, there is no decomposition at all -- the numeric engine solves everything monolithically. Articulation decomposition would actually produce multiple subproblems with shared boundary entities, exercising the full local-to-global pipeline.

3. **Reasonable risk.** Tarjan's biconnected components and articulation point algorithms are published, provably correct, and O(V+E). The incidence graph module already has the entity-to-constraint incidence data. The cover plan, boundary projection, and overlap context contracts already exist.

4. **Enables follow-on work.** After articulation decomposition lands:
   - The spanning tree pattern catalog (Candidate B) can be tested on separated blocks
   - Gluing assembly (Candidate D) has real multi-subproblem test cases
   - The full pipeline (decompose -> local solves -> glue) actually exercises the architecture

5. **No dependency on external decisions.** Unlike new constraint types (Candidate C, which may need circle geometry) or a sparse backend (Candidate E, which needs external library decisions), articulation decomposition uses only existing types and data.

### Second Choice if A is Deferred

Candidate B (Spanning Tree Patterns) is the next-best option if A proves too risky. It's low-risk, the infrastructure exists, and it unblocks DOF-based plan quality. However, it has less impact than A because the spanning forest plan is not yet consumed by the runtime pipeline.

---

## 4. Rough Implementation Plan for Candidate A

### Step 52a: Incidence Graph -- Biconnected Components and Articulation Points

**New types in `incidence_graph.cppm`:**
```
struct BiconnectedComponent {
    int index = 0;
    std::vector<EntityId> entity_ids;
    std::vector<ConstraintId> constraint_ids;
};

struct ArticulationPoint {
    EntityId entity_id;
    std::vector<int> biconnected_component_indices;
};

struct BiconnectedDecomposition {
    std::vector<BiconnectedComponent> components;
    std::vector<ArticulationPoint> articulation_points;
    bool is_biconnected = true;
    StageReport report;
};
```

**New function:** `gcs::kernel::ContractResult<BiconnectedDecomposition> decompose_biconnected(const ModelSnapshot& model, const IncidenceIndices& incidence);`

**Algorithm:** Standard Tarjan DFS (finding articulation points via `low[v] >= disc[u]`, biconnected components via edge stack). Operate on the bipartite entity/constraint incidence graph, treating all entities and constraints as vertices. An articulation entity whose removal disconnects the constraint graph is a natural candidate for a separator context.

**Tests:**
- Simple chain (3 entities, 2 constraints) -> 2 biconnected components, 1 articulation
- Triangle (3 entities, 3 constraints) -> 1 biconnected component (it's a cycle)
- Dumbbell (two triangles connected by a shared entity) -> 2 components, 1 articulation
- Tree (star or chain) -> N-1 components for N constraints
- Single constraint -> 1 biconnected component, no articulation
- Deterministic output (same input -> same decomposition)
- Incidence consistency (every entity/constraint appears in at least one component)

### Step 52b: Decomposition Planner -- Articulation-Aware Cover

**Logic change in `plan_decomposition()`:**
After computing connected components, for each component, check if it contains articulation points. If so, split the component into biconnected subproblems with overlap contexts for the articulation entities:
- Articulation entity belongs to ALL subproblems that share it
- Overlap context represents the articulation entity as shared boundary
- Each biconnected subproblem is a SolveDagNode
- SolveDagEdge from each subproblem to the overlap context

**Gluing/assembly implications:**
- Post-solve, the articulation entity's parameters from different local solves must agree
- The existing `GluingReport` and `BoundaryAgreementReport` structures already support this
- If disagreements exist, they become obstruction evidence

**Tests:**
- A 3-entity chain: 2 biconnected subproblems, 1 overlap context for the middle entity, 2 boundary projections
- Dumbbell: 2 subproblems sharing an articulation
- Cover validation still passes for articulation-aware covers
- SolveDAG is acyclic with overlap nodes
- Deterministic plan output

### Expected Files Changed

| File | Change |
|------|--------|
| `src/gcs/incidence_graph/incidence_graph.cppm` | Add `BiconnectedComponent`, `ArticulationPoint`, `BiconnectedDecomposition`, `decompose_biconnected()` |
| `src/gcs/incidence_graph/incidence_graph.cpp` | Implement Tarjan biconnected decomposition + articulation point detection |
| `src/gcs/decomposition_planner/decomposition_planner.cpp` | Wire biconnected decomposition into `plan_decomposition()`, create overlap contexts for articulation entities |
| `tests/contracts/incidence_graph/incidence_graph_contract_tests.cpp` | Add biconnected decomposition tests (chain, triangle, dumbbell, tree, deterministic output) |
| `tests/contracts/decomposition_planner/decomposition_planner_contract_tests.cpp` | Add articulation-aware cover tests (subproblem count, overlap contexts, SolveDAG shape) |
| `docs/architecture/66-implementation-execution-roadmap.md` | Mark Step 52 complete |
| `docs/architecture/67-current-progress-and-next-steps.md` | Add Step 52 summary |
| `docs/architecture/68-forward-execution-plan-2026-05-24.md` | Register Step 52 details |

### Estimated Scope

- 1-2 sessions (incidence graph algorithm + planner wiring + tests)
- ~200-300 lines of new C++ in incidence_graph.cpp
- ~100-150 lines of new/modified C++ in decomposition_planner.cpp
- ~150-200 lines of new test code
- No API breaking changes to existing types
- No external dependencies

### Exit Criteria

1. `gcs.incidence_graph` exposes a `decompose_biconnected()` function that returns deterministic biconnected components and articulation points
2. `gcs.decomposition_planner` uses biconnected decomposition to create fine-grained subproblems with overlap contexts for articulation entities
3. Contract tests cover: chain, triangle, dumbbell, tree graphs; deterministic output; cover plan shape for articulation-aware plans
4. Build, CTest, and quality gate pass
5. No regression in existing 109 CTest cases
