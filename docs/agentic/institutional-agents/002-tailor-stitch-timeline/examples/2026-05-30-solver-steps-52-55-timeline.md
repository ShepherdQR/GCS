# Timeline Entry: 2026-05-30 Solver Algorithm Deepening — Steps 52-55

Scope: solver algorithm, decomposition planning, incidence graph, spanning tree patterns

Updated: 2026-05-30

Maintainer role: `Tailor: Cut-Stitch Timeline`

## Timeline

| Date | Event | Evidence | Consequence | Open Thread | Confidence |
| --- | --- | --- | --- | --- | --- |
| 2026-05-27 | Spanning forest contract types and planner skeleton were introduced during narrative weakness execution. | Commit `91838fe`; `src/gcs/decomposition_planner/` — RigidSetSpanningForestPlan, plan_spanning_forest(), validate_spanning_forest() | Decomposition planner gained spanning-forest data structures but all constraints remained "unsupported" — contract-only, not wired to real patterns. | LGS M1 was intentionally contract-only; real patterns deferred to later steps. | high |
| 2026-05-30 | Step 52: Tarjan biconnected decomposition added to `gcs.incidence_graph` and wired into `plan_decomposition()`. | Commit `736b215`; `src/gcs/incidence_graph/incidence_graph.cppm` (+30 new types: BiconnectedComponent, ArticulationPoint, BiconnectedDecomposition); `src/gcs/incidence_graph/incidence_graph.cpp` (+150 Tarjan DFS); `tests/contracts/incidence_graph/incidence_graph_contract_tests.cpp` (+5 tests) | Articulation entities produce overlap contexts and boundary projections in SolveDAG edges. Connected-component split is now a fallback behind finer-grained biconnected decomposition. Showcase and fixed-entity tests updated from 2- to 4-subproblem expectations. | Large graphs (>1000 entities) not stress-tested. | high |
| 2026-05-30 | Step 53: First spanning tree pattern — point-to-point distance between rigid sets. | Commit `59f1fe9`; `src/gcs/decomposition_planner/decomposition_planner.cpp` — match_forest_pattern() recognizing distance constraint groups; +5 spanning forest tests | Distance constraints between rigid sets now classified as `absorbed_by_tree_pattern` with 1 translational DOF removed, weight=1 (preferred in Kruskal). | Mixed constraint groups (distance + parallel) remain unsupported — all-or-nothing matching contract. | high |
| 2026-05-30 | Step 54: Parallel and perpendicular spanning tree patterns. | Commit `ab5dbef`; `src/gcs/decomposition_planner/decomposition_planner.cpp` — parallel (line-line, plane-plane) and perpendicular (line-plane) patterns; +2 tests with inline EntityDraft/ConstraintDraft | Oriented constraints now absorb 1 rotational DOF each. Pattern catalog reached 3 patterns. | Coincident and angle patterns remain in backlog. | high |
| 2026-05-30 | Step 55: Spanning forest plan wired into PlannerOutput. | Commits `fb52a9c` (implementation), `45ec143` (test verification); `src/gcs/decomposition_planner/decomposition_planner.cpp` — plan_decomposition() now calls plan_spanning_forest() and populates PlannerOutput::spanning_forest_plan; +1 test | Spanning forest absorption evidence is now available in planner output for downstream consumers. | Numeric task construction does not yet consume spanning forest absorption. Planner produces evidence; runtime ignores it. | high |
| 2026-05-30 | Steps 52-55 archive completed. CTest: 128 tests (up from 109), 0 failures. | Commit `cee11e2`; `docs/completed-tasks/2026-05-30-steps-52-55-articulation-spanning-tree/README.md`; quality gates: all C++ gates pass | Closed the articulation-and-spanning-tree task arc with full evidence bundle, decisions log, and residual risk documentation. | Push was deferred alongside the scene-generation pipeline work due to proxy issues. | high |

## Decision Threads

| Thread | Started | Current state | Evidence |
| --- | --- | --- | --- |
| Spanning forest absorption pipeline | 2026-05-27 | active; planner produces evidence, numeric task does not consume it | `src/gcs/decomposition_planner/decomposition_planner.cpp`; `docs/completed-tasks/2026-05-30-steps-52-55-articulation-spanning-tree/README.md` |
| Biconnected decomposition on large graphs | 2026-05-30 | open; tested only on small contract-test graphs | Tarjan DFS on entity-to-entity adjacency — bipartite approach not needed with current 2-entity constraints |
| Incremental pattern catalog | 2026-05-30 | active; 3 patterns exist, coincident and angle remain in backlog | `docs/architecture/68-forward-execution-plan-2026-05-24.md` |
| Articulation overlap context gluing | 2026-05-30 | active; works for current fixtures, degenerate models not explored | `src/gcs/decomposition_planner/decomposition_planner.cpp` |

## Gaps

| Gap | Impact | Repair action |
| --- | --- | --- |
| Spanning forest absorption not wired into numeric task active equations. | Planner produces DOF absorption evidence, but runtime solves ignore it. Numeric tasks may be larger than necessary. | Next solver step: consume spanning_forest_plan in numeric task construction, removing absorbed DOFs from active equations. |
| Coincident and angle spanning-tree patterns not implemented. | Constraint groups with coincident (2 translational DOF) or angle (1 rotational DOF) remain unsupported. | Add after first numeric-task wiring confirms the absorption contract is correct. |
| Biconnected decomposition not stress-tested on large/dense graphs. | Performance and correctness of Tarjan DFS on >1000-entity graphs are unknown. | Generate dense synthetic graphs and measure decomposition wall time. |
| Push deferred. | All 7 commits (Steps 52-55 + scene pipeline) are local-only. | Push when proxy issues are resolved; commits are on `master`. |

## Handoffs

| Finding | Handoff |
| --- | --- |
| Incremental pattern approach (one pattern at a time, test in isolation) is a reusable methodology. | Candidate experience: "incremental-pattern-catalog" — could be forged into `Bladesmith` note. |
| Spanning forest evidence generation separated from consumption is a clean contract boundary. | `gcs-decomposition-planning-steward` and `gcs-numeric-engine-steward` for the next wiring step. |
| CTest expansion from 109 to 128 with 0 regressions validates the step-by-step approach. | `gcs-quality-steward` — baseline growth is a positive quality signal. |
| Biconnected decomposition takes precedence over connected-component split. | `docs/architecture/67-current-progress-and-next-steps.md` — architecture decision recorded. |
