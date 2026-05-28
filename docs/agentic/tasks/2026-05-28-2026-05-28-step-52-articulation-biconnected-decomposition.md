---
task_id: 2026-05-28-2026-05-28-step-52-articulation-biconnected-decomposition
status: draft
request: "Implement Step 52: Articulation and Biconnected Decomposition. Add Tarjan biconnected decomposition algorithm (BiconnectedComponent, ArticulationPoint, BiconnectedDecomposition, decompose_biconnected()) to gcs.incidence_graph, then wire the results into gcs.decomposition_planner to create articulation-aware context covers with overlap contexts for shared boundary entities. See docs/architecture/68-step-52-candidate-analysis.md for the full plan."
scope: implementation
risk: medium
owning_agent: gcs-cpp-solver-maintainer
specialist_agents:
  - none
affected_contracts:
  - none
affected_paths:
  - src/gcs/incidence_graph/
  - src/gcs/decomposition_planner/
  - tests/contracts/incidence_graph/
  - tests/contracts/decomposition_planner/
  - docs/architecture/
required_evidence:
  - validate-docs
  - validate-inventory
  - check-dependencies
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-28-2026-05-28-step-52-articulation-biconnected-decomposition

## Scope

**Step 52a** — Add Tarjan biconnected decomposition to `gcs.incidence_graph`:
- `BiconnectedComponent`, `ArticulationPoint`, `BiconnectedDecomposition` types
- `decompose_biconnected(model, incidence_indices)` function
- Contract tests for chain, triangle, dumbbell, tree, deterministic output

**Step 52b** — Wire articulation into `gcs.decomposition_planner`:
- Use biconnected decomposition to create fine-grained subproblems
- Create overlap contexts for articulation entities shared across components
- Build SolveDAG edges from biconnected subproblems to overlap contexts
- Contract tests for articulation-aware cover shapes

**Intentionally out of scope:**
- Gluing assembly changes (uses existing infrastructure)
- Spanning tree pattern catalog
- New constraint types
- Solver runtime semantics changes

## Non-Goals

- Do not change solver runtime semantics.
- Do not redefine architecture contracts in `docs/agentic`.

## Context To Read

- `docs/architecture/README.md`
- Owning skill: `gcs-cpp-solver-maintainer`

## Acceptance Gates

- The owning boundary is clear.
- Required evidence is produced or a reason is recorded.
- Residual risks are named.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-28-2026-05-28-step-52-articulation-biconnected-decomposition.md
```

## Evidence Bundle

- Build: `scripts\build_clang_ninja.cmd` — pass
- CTest: full suite — pass (109 existing + new tests)
- Quality gate: `python tools\agentic_design\agentic_toolkit.py run-quality-gates` — pass
- Task card validation: pass
- Changed: `src/gcs/incidence_graph/incidence_graph.cppm`, `src/gcs/incidence_graph/incidence_graph.cpp`, `src/gcs/decomposition_planner/decomposition_planner.cpp`, `tests/contracts/incidence_graph/incidence_graph_contract_tests.cpp`, `tests/contracts/decomposition_planner/decomposition_planner_contract_tests.cpp`

## Residual Risks

- Articulation entity in overlap contexts may need gluing contract clarification — currently covered by existing BoundaryAgreementReport
- Large/degenerate graphs (single entity, no constraints) need defensive handling
- The planner currently treats articulation decomposition as optional (only applies to connected components that are not biconnected); single-edge or fully-cyclic components produce 1 subproblem (no-op)
