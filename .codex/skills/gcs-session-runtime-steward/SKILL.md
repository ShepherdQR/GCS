---
name: gcs-session-runtime-steward
description: Project-specific skill for designing or reviewing GCS session runtime. Use when work touches RuntimeCommand, command preconditions, transactions, pipeline orchestration, dependency-injected services, atomic commit, rollback, stage traces, history, undo/redo, replay, or post-commit verification.
---

# GCS Session Runtime Steward

## Start Here

Use this skill for `gcs.session_runtime` target design. Runtime orchestrates
specialist modules and is the only owner of durable commit.

Read:

- `docs/architecture/62-module-agents.md` -> `Session Runtime Agent`
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`
  -> `Session Runtime Target Design`
- `docs/architecture/20-solver-pipeline/pipeline.md`

## Workflow

1. Define command shape, preconditions, transaction policy, and injected module
   services.
2. Plan stage ordering and required report from each stage.
3. Preserve transaction isolation: rejected commands do not mutate durable
   snapshot state.
4. Commit only after diagnostics and gluing accept the proposal.
5. Name tests for invalid commands, stage stops, rollback, state-version
   advancement, replay, and undo/redo.

## Own

- `RuntimeCommand`, `CommandResult`, `TransactionTrace`.
- Atomic commit, rollback, history, replay, post-commit verification.
- Orchestration of kernel, graph, planner, numeric, diagnostics, IO, and viewer
  adapters through typed services.

## Refuse

- Residual definitions, graph algorithms, gluing math, IO schema policy.
- Partial durable mutation on rejected commands.

## Required Output

Return a structured design report with:

- command contracts;
- transaction and rollback semantics;
- stage trace schema;
- service boundaries;
- acceptance gates;
- required runtime contract tests.
