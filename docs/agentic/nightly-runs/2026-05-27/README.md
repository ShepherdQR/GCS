# Nightly Immune Diagnostics - 2026-05-27

## Status

- Overall result: blocked before diagnostics execution.
- Worktree: `C:\Users\QR\.codex\worktrees\216a\GCS`
- Governing docs requested for this run:
  - `docs/agentic/nightly-immune-diagnostics.md`
  - `docs/agentic/pr-audit-governance.md`

## What happened

This run could not complete the required preflight capture or any of the affordable diagnostics because every local command entrypoint failed before command execution began. The shared failure signature was:

```text
windows sandbox: setup refresh failed with status exit code: 1
```

That failure affected:

- PowerShell command execution via the normal shell tool
- Node REPL fallback used to read local files and invoke commands

Because of that execution-layer failure, this run could not record:

- branch name
- commit SHA
- `git status --short --branch`

It also could not read the governing docs during the run, so any finding taxonomy in this folder is marked as provisional evidence rather than as a policy-confirmed classification.

## Diagnostics outcome

- `validate-docs`: not executed
- `validate-inventory`: not executed
- `validate-skills`: not executed
- `check-dependencies`: not executed
- `scene_generation list`: not executed
- `tests.tools.test_scene_generation_explorer`: not executed
- `run-quality-gates --skip-build --skip-ctest --skip-cli --continue-on-failure`: not executed

See [commands.md](/C:/Users/QR/.codex/worktrees/216a/GCS/docs/agentic/nightly-runs/2026-05-27/commands.md) for the attempted commands and exact evidence, [findings.json](/C:/Users/QR/.codex/worktrees/216a/GCS/docs/agentic/nightly-runs/2026-05-27/findings.json) for the structured finding, and [repair-plan.md](/C:/Users/QR/.codex/worktrees/216a/GCS/docs/agentic/nightly-runs/2026-05-27/repair-plan.md) for the minimal rerun plan.
