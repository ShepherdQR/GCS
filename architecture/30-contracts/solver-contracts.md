# Solver Contracts

## Planner Contract

```text
PlannerInput:
  model_snapshot
  incidence_indices
  diagnostic_hints
  solve_intent

PlannerOutput:
  solve_plan
  subproblems
  gauge_policy
  structural_report
```

The planner chooses a strategy. It does not mutate geometry.

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
  conflict_sets
  redundancy_sets
  warnings
```

Diagnostics should be usable before solving, after solving, and on isolated
subproblems.

## Numeric Engine Contract

```text
NumericTask:
  problem_snapshot
  active_variables
  active_equations
  parameterization
  tolerances
  initial_state
  solve_limits

NumericReport:
  result_code
  proposed_delta_or_state
  residual_metrics
  rank_metrics
  iteration_trace_summary
  failure_cause
```

The engine returns a proposal and report. It does not commit durable state.

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
  user_visible_status
```

The runtime is responsible for transaction semantics, undo history, and
coordinating reports into a coherent result.

## Boundary Contract

IO and visualization must use public runtime or report APIs. They must not
reach into numeric-engine internals or mutate kernel state directly.
