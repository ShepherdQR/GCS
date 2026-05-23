---
name: gcs-diagnostics-certification-steward
description: Project-specific skill for designing or reviewing GCS diagnostics. Use when work touches DOF reports, rank evidence, residual analysis, gluing, boundary agreement, obstruction reports, conflict sets, redundancy sets, gauge checks, diagnostic phases, or status precedence.
---

# GCS Diagnostics Certification Steward

## Start Here

Use this skill for `gcs.diagnostics` target design. Diagnostics explains and
certifies status; it does not mutate state or run numeric iterations.

Read:

- `docs/architecture/62-module-agents.md` -> `Diagnostics Certification Agent`
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`
  -> `Diagnostics Target Design`
- `docs/architecture/00-foundations/topos-semantic-model.md`
- `docs/architecture/30-contracts/solver-contracts.md`

## Workflow

1. Identify the diagnostic phase: pre-solve, post-local-solve, gluing, or
   verification.
2. Define typed requests and reports for DOF, rank, residual, boundary
   agreement, gluing, conflicts, redundancy, and obstructions.
3. Keep structural and numeric evidence separate until status precedence.
4. Produce obstruction reports for failed gluing or certification.
5. Name tests for accepted gluing, failed boundary agreement, minimal evidence,
   deterministic status precedence, conflicts, and redundancy.

## Own

- `DiagnosticReport`, `DofReport`, `RankReport`, `ResidualReport`.
- `BoundaryAgreementReport`, `GluingReport`, `ObstructionReport`.
- `ConflictSet`, `RedundancySet`, `StatusPrecedenceTrace`.

## Refuse

- Durable state mutation.
- Numeric iteration policy.
- Accepting failed gluing as solved.

## Required Output

Return a structured design report with:

- phase and inputs;
- evidence reports;
- status precedence;
- obstruction and subject IDs;
- required negative tests;
- handoffs to planner or numeric.
