# LGS Spanning-Tree Design Readiness Confirmation

Date: 2026-05-25
Status: design-preparation complete; implementation not started
Decision: pause spanning-tree work after this confirmation

## Confirmation Summary

The spanning-tree design and preparation work is complete for now.

This confirmation closes the current research/design thread without starting
development. The next implementation task, `Rigid-set spanning-tree plan
contracts`, is ready to be opened later, but it has not been implemented in
this session.

## What Is Complete

The following design artifacts are complete and persisted:

- `01-paper-analysis.md`: source-aware analysis of the LGS spanning-tree paper.
- `02-gcs-adoption-proposal.md`: proposal for mapping the method into GCS.
- `03-feasibility-analysis.md`: feasibility, risk, and staged adoption
  analysis.
- `04-detailed-implementation-plan.md`: detailed phased implementation plan.
- `05-design-readiness-confirmation.md`: this readiness and pause report.

The design now covers:

- architecture placement;
- module ownership;
- dependency boundaries;
- task-start prerequisites;
- acceptance criteria;
- unit-test design;
- quality gates;
- residual risks;
- explicit non-development status.

## What Is Not Complete

`Rigid-set spanning-tree plan contracts` are not complete.

Current repository confirmation:

- no `RigidSetSpanningForestPlan` or equivalent planner contract exists in
  `src/gcs/decomposition_planner/`;
- no `SpanningTreePattern` or equivalent pattern metadata exists in
  `src/gcs/constraint_catalog/`;
- no rigid-set pair constraint grouping implementation exists for this method;
- no maximum-weight spanning forest builder exists;
- no absorbed/closure/unsupported partition validator exists;
- no spanning-tree contract tests exist in `tests/contracts/*`;
- no numeric-engine reduced task implementation exists;
- no diagnostics revalidation implementation exists.

The current work is therefore a completed design-preparation package, not a
completed implementation package.

## Task-Start Prerequisites

Before starting the future `Rigid-set spanning-tree plan contracts` task, the
following prerequisites should be true:

1. Create a fresh implementation task card.
2. Use an appropriate worktree or confirm a single-session local workspace.
3. Re-read:
   - `docs/research/20260525/lgs-spanning-tree/01-paper-analysis.md`;
   - `docs/research/20260525/lgs-spanning-tree/02-gcs-adoption-proposal.md`;
   - `docs/research/20260525/lgs-spanning-tree/03-feasibility-analysis.md`;
   - `docs/research/20260525/lgs-spanning-tree/04-detailed-implementation-plan.md`;
   - `docs/architecture/20-solver-pipeline/decomposition-planning.md`;
   - `docs/architecture/30-contracts/solver-contracts.md`.
4. Use these owning skills:
   - `gcs-decomposition-planning-steward`;
   - `gcs-incidence-structure-steward`;
   - `gcs-constraint-semantics-steward`;
   - `gcs-quality-steward`.
5. Keep the first implementation task contract-only.
6. Do not change numeric solving in the first implementation task.
7. Do not introduce supported absorbed constraints until pattern metadata and
   refusal semantics are tested.

## Future Task Boundary

Recommended future task:

```text
Title:
Rigid-set spanning-tree plan contracts

Goal:
Add deterministic planner-side evidence for rigid-set maximum-weight spanning
forest planning, including rigid-set pair grouping, pattern match stubs,
absorbed/closure/unsupported constraint partitioning, and unsupported reports.
Do not change numeric solving.
```

Initial affected modules:

- `src/gcs/incidence_graph/`
- `src/gcs/decomposition_planner/`
- `src/gcs/constraint_catalog/`
- `tests/contracts/incidence_graph/`
- `tests/contracts/decomposition_planner/`
- `tests/contracts/constraint_catalog/`

Out of scope for the future first task:

- reduced numeric solving;
- diagnostics revalidation;
- runtime commit behavior;
- viewer projection;
- broad LGS 3D pattern catalog;
- performance claims.

## Acceptance Criteria

The future `Rigid-set spanning-tree plan contracts` task is complete only when:

1. rigid-set pair groups are deterministic;
2. candidate edges have deterministic weights and tie breaks;
3. selected forest is acyclic;
4. every active cross-rigid-set constraint appears exactly once in one of:
   - absorbed evidence;
   - closure residual evidence;
   - unsupported evidence;
5. unsupported cases return typed report codes;
6. current component-cover planner behavior remains unchanged;
7. no numeric-engine behavior changes;
8. no lower solver module imports IO, viewer, CLI, app lifecycle, or UI code;
9. focused contract tests pass.

## Unit-Test Design

The unit-test design for the future first implementation task is complete.

Required tests:

- `graph_groups_constraints_by_rigid_set_pair_deterministically`
- `graph_ignores_same_rigid_set_constraints_for_tree_edges`
- `planner_spanning_forest_selects_maximum_weight_edges`
- `planner_spanning_forest_tie_break_is_deterministic`
- `planner_spanning_forest_keeps_cycle_edges_as_closure_constraints`
- `planner_spanning_forest_partitions_every_active_constraint_once`
- `planner_spanning_forest_reports_unsupported_pattern`
- `planner_spanning_forest_does_not_change_existing_component_cover_behavior`
- `catalog_spanning_tree_pattern_stub_refuses_unsupported_signature`
- `catalog_spanning_tree_pattern_stub_reports_stable_code`

Recommended negative tests:

- malformed constraint references;
- missing rigid-set references;
- disconnected rigid-set graph;
- all unsupported edge groups;
- cycle where the highest-weight edge choice must leave one closure residual;
- deterministic tie with same weight and different constraint IDs.

## Quality Gates

For the future implementation task:

```bat
cmake --build out\build\clang-ninja
ctest --test-dir out\build\clang-ninja --output-on-failure
python tools\agentic_design\agentic_toolkit.py run-quality-gates
```

For this current confirmation task:

- build and CTest are intentionally skipped because no source code, fixtures,
  schemas, or runtime behavior changed.
- documentation confirmation is sufficient.

## Evidence Query

The current state can be reconfirmed with:

```bat
rg -n "RigidSetSpanning|SpanningTreePattern|spanning_tree|absorbed_constraint|closure_constraint|RigidSetTreeEdge" src tests docs\research\20260525\lgs-spanning-tree
```

Expected interpretation:

- hits in `docs/research/20260525/lgs-spanning-tree/` are design references;
- absence of hits in `src/` and `tests/` means implementation has not started.

## Pause Decision

Spanning-tree work is paused after this report.

The project now has enough design material to start the future contract-only
task cleanly, but no implementation work should be inferred from this closeout.
When work resumes, it should begin with `Rigid-set spanning-tree plan
contracts` and should not jump directly to reduced numeric solving.

