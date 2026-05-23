---
name: gcs-incidence-structure-steward
description: Project-specific skill for designing or reviewing GCS structural graph contracts. Use when work touches incidence hypergraphs, reverse indices, connected components, rigid-set or body graphs, articulation or biconnected decomposition, separators, malformed-edge reports, or deterministic graph dumps.
---

# GCS Incidence Structure Steward

## Start Here

Use this skill for `gcs.incidence_graph` target design. Structural graph facts
must be deterministic projections of a validated snapshot.

Read:

- `docs/architecture/62-module-agents.md` -> `Incidence Structure Agent`
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`
  -> `Incidence Graph Target Design`
- `docs/architecture/20-solver-pipeline/decomposition-planning.md`

## Workflow

1. Identify the structural projection needed by planner or diagnostics.
2. Define typed build requests, options, outputs, and malformed-reference
   reports.
3. Preserve deterministic ordering in all indices and graph dumps.
4. Keep coordinate mutation, numeric rank, and planning decisions out of this
   module.
5. Name tests for coverage, reverse incidence, invalid references, and dumps.

## Own

- `IncidenceHypergraph`, entity and constraint incidence indices.
- `RigidBodyGraph`, connected components, separators, graph dumps.
- Malformed-edge quarantine and structural reports.

## Refuse

- Solver policy, gauge selection, numeric conditioning, runtime commit.
- Graph algorithms that depend on vector position rather than stable IDs.

## Required Output

Return a structured design report with:

- graph input and output contracts;
- deterministic ordering rules;
- structural invariants;
- report codes for invalid references;
- planner and diagnostics consumers;
- required contract tests.
