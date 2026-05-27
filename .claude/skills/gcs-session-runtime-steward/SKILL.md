---
name: gcs-session-runtime-steward
description: Session runtime design and review for GCS. Invoke when work touches RuntimeCommand, command preconditions, transactions, pipeline orchestration, dependency-injected services, atomic commit, rollback, stage traces, history, undo/redo, replay, or post-commit verification.
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

## Claude Code Integration

When invoked for session runtime work:
- Use `Read` on architecture docs before modifying command or transaction
  semantics.
- Use `Grep` to trace all command handlers and verify that rejected commands
  cannot produce partial durable mutations.
- When adding a new command type, `Grep` for existing command patterns to follow
  the established shape.
- Use `Bash` to run contract tests that exercise transaction rollback and
  replay paths.
- Transaction isolation is the hardest boundary to verify; prefer explicit
  negative tests for partial-mutation scenarios.
