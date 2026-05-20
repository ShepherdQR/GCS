# Solver Pipeline

## Pipeline Stages

```text
1. Intake
2. Normalize
3. Validate
4. Index
5. Decompose
6. Diagnose
7. Plan
8. Solve
9. Assemble
10. Verify
11. Commit or reject
12. Report
```

## Stage Contracts

| Stage | Input | Output |
| --- | --- | --- |
| Intake | File, API command, or UI command. | Raw scene or command payload. |
| Normalize | Raw payload. | Canonical units, IDs, and typed entities. |
| Validate | Canonical model. | Valid model or validation errors. |
| Index | Valid model. | Incidence graph and structural indices. |
| Decompose | Graph indices. | Components, clusters, overlaps, and context candidates. |
| Diagnose | Model, graph, subproblems. | DOF, rank, conflict, redundancy, residual reports. |
| Plan | Diagnostics and decomposition. | `CoverPlan`, ordered solve plan, gauge policy, fallback strategy. |
| Solve | Prepared solve tasks. | Local sections, numeric reports, and proposed coordinate deltas. |
| Assemble | Subproblem results. | `GluingReport` and global proposed state. |
| Verify | Proposed state. | Satisfaction and reliability report. |
| Commit | Current state and verified proposal. | New versioned state or rejection. |
| Report | All stage reports. | User/API/fixture-facing explanation. |

## Failure Model

Failure is not binary. The pipeline should preserve the most specific status:

- invalid model;
- unsupported constraint type;
- structurally disconnected;
- under constrained;
- over constrained;
- inconsistent;
- numerically singular;
- iteration limit reached;
- tolerance not reached;
- accepted with warnings;
- solved and verified.

Every failure should identify the stage that produced it and the smallest known
set of entities or constraints involved.

## Local-To-Global Rule

The pipeline treats decomposition as cover selection and assembly as gluing:

```text
model snapshot
  -> context cover
  -> local solve sections
  -> overlap compatibility checks
  -> global proposed state or obstruction report
```

An accepted numeric result for one subproblem is not sufficient for command
success. The runtime accepts only a globally verified proposal whose local
sections agree on every declared overlap and whose remaining free degrees of
freedom match the solve intent.

## Transaction Rule

Numeric solving proposes state. It does not directly commit durable model
changes. `session_runtime` commits only after post-solve verification and after
attaching reports to the command result.

## Observability Rule

Every stage should be replayable from serialized input plus configuration.
This is the foundation for deterministic tests, visual debugging, and future
bug reports from users.
