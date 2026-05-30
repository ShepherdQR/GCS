---
task_id: 2026-05-30-2026-05-28-step-53-spanning-tree-pattern
status: draft
request: "Implement Step 53: First spanning tree pattern — point-to-point distance between two rigid sets. Add a real pattern to the existing spanning forest infrastructure (types, Kruskal, BFS orientation) so that cross-rigid-set distance constraints are classified as absorbed_by_tree_pattern instead of all unsupported. This is the first concrete DOF-accounting pattern in the spanning tree catalog."
scope: implementation
risk: low
owning_agent: gcs-cpp-solver-maintainer
specialist_agents:
  - none
affected_contracts:
  - none
affected_paths:
  - src/gcs/decomposition_planner/
  - tests/contracts/decomposition_planner/
  - docs/architecture/
required_evidence:
  - validate-docs
  - validate-inventory
  - check-dependencies
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-30-2026-05-28-step-53-spanning-tree-pattern

## Scope

**Step 53** — First real spanning tree pattern:
- Add pattern matching function to `plan_spanning_forest()` that inspects constraint groups for known patterns
- First pattern: point-to-point distance between two rigid sets → absorbed_by_tree_pattern, removes 1 translational DOF, weight = 1
- Update candidate edge creation to use pattern matching instead of marking all unsupported
- Single-pattern risk: everything not matching the distance pattern remains unsupported
- Contract tests for pattern matching, DOF accounting, and supported edge selection

**Intentionally out of scope:**
- Additional patterns (parallel, perpendicular, coincident, angle)
- Changing solver runtime to consume spanning forest plan
- Spanning forest validation changes beyond pattern support checks

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
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-30-2026-05-28-step-53-spanning-tree-pattern.md
```

## Evidence Bundle

- Build: `scripts\build_clang_ninja.cmd` — pass
- CTest: full suite — pass (120 + new tests)
- Quality gate: `python tools\agentic_design\agentic_toolkit.py run-quality-gates` — pass
- Changed: `src/gcs/decomposition_planner/decomposition_planner.cpp`, `tests/contracts/decomposition_planner/decomposition_planner_contract_tests.cpp`, docs

## Residual Risks

- Single pattern does not dramatically change solver behavior — spanning forest plan is not yet consumed by runtime
- Patterns with >2 rigid sets (e.g., symmetry) would need multi-rigid-set constraint analysis
- Distance constraint absorbs 1 DOF only; rigid-body DOF accounting (6 per body) is correct but simplified
