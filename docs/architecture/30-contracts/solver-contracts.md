# Solver Contracts

## Planner Contract

```text
PlannerInput:
  model_snapshot
  incidence_indices
  diagnostic_hints
  solve_intent

PlannerOutput:
  cover_plan
  solve_plan
  solve_dag
  subproblems
  overlap_contexts
  boundary_projections
  gauge_policy
  structural_report
```

The planner chooses a strategy. It does not mutate geometry. `solve_dag`
records local solve nodes, aggregation contexts, and boundary-projection edges
so downstream runtime and diagnostics can explain local-to-global dependency
order without reinterpreting planner internals.

## Diagnostic Contract

```text
DiagnosticInput:
  model_snapshot
  optional_subproblem
  optional_numeric_report

DiagnosticOutput:
  status_code
  dof_report
  rank_report
  residual_report
  gluing_report
  obstruction_report
  conflict_sets
  redundancy_sets
  warnings
```

Diagnostics should be usable before solving, after solving, and on isolated
subproblems.

`rank_report` must preserve structural and numeric evidence separately.
Numeric evidence must include full active variable dimension, free variable
dimension after boundary variables are frozen, frozen variable dimension,
residual dimension, rank, nullity, singularity, over-constraint,
under-constraint, and condition evidence when available.

`conflict_sets` and `redundancy_sets` must name the smallest stable subject
sets known to diagnostics. Residual conflicts name unsatisfied constraint IDs
and their owning entity IDs. Redundancy evidence first reports exact duplicate
constraint signatures such as duplicate distance constraints, then preserves
broader over-constrained context candidates when rank or DOF evidence supports
them.

## Numeric Engine Contract

```text
NumericTask:
  problem_snapshot
  context_snapshot
  active_variables
  active_equations
  boundary_variables
  parameterization
  tolerances
  initial_state
  solve_limits

NumericReport:
  result_code
  local_section
  proposed_delta_or_state
  residual_metrics
  rank_metrics
  iteration_trace_summary
  failure_cause
```

The engine returns a proposal and report. It does not commit durable state.

## Gluing Contract

```text
GluingInput:
  model_snapshot
  cover_plan
  local_sections
  boundary_projections
  gauge_policy
  tolerances

GluingReport:
  accepted
  proposed_global_state
  overlap_statuses
  boundary_residuals
  gauge_consistency
  obstruction_report
```

Assembly checks whether local sections agree on every declared overlap and
whether the remaining free motion is compatible with the solve intent. A
failed gluing step should identify the smallest known boundary, entity, or
constraint set responsible for the obstruction.

## Runtime Contract

```text
Command:
  command_id
  solve_intent
  model_edit_or_solve_request

CommandResult:
  accepted
  new_state_version
  stage_reports
  post_local_diagnostics
  gluing_report
  obstruction_report
  user_visible_status

RankEvidenceProjection:
  local_report_index
  source
  context_id
  result_status
  numeric full/free/frozen dimensions
  residual dimension, rank, nullity
  under/over/singular flags
  condition evidence
```

The runtime is responsible for transaction semantics, undo history, and
coordinating reports into a coherent result.

`post_local_diagnostics` records diagnostics-owned rank and residual evidence
after each successful local numeric solve and before gluing. Blocking
post-local diagnostic statuses roll back before durable commit; warning
statuses may still commit as accepted-with-warnings.

Rank evidence is exposed through `runtime::project_rank_evidence` returning
`runtime::RankEvidenceProjection` records. Viewer, promotion, and reporting
tools should consume this public projection rather than reading
numeric-engine reports directly.

## Boundary Contract

IO and visualization must use public runtime or report APIs. They must not
reach into numeric-engine internals or mutate kernel state directly.
