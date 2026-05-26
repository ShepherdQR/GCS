# GCS Nightly Immune Diagnostics - 2026-05-26

## Run status

This calibration run is blocked by the local execution environment.

- Local date: `2026-05-26`
- Repository: `C:\Users\QR\.codex\worktrees\d8aa\GCS`
- Policy documents intended for this run:
  - `docs/agentic/nightly-immune-diagnostics.md`
  - `docs/agentic/pr-audit-governance.md`
- Constraint followed: no edits were made outside this dated run directory.

## What was attempted

The run attempted to start local command execution in order to:

1. Record branch/worktree, commit SHA, and `git status --short --branch`
2. Read the nightly diagnostics governance documents
3. Execute the requested affordable diagnostics

Every command invocation failed before process start with the same sandbox error:

```text
windows sandbox: setup refresh failed with status exit code: 1
```

Because the failure happened before command start, the run could not confirm:

- current branch name
- current commit SHA
- git status
- policy taxonomy/severity labels from the local docs
- availability of any requested Python tooling

## Outcome

- No diagnostic command was executed successfully.
- No success claims are made for any check.
- The environment failure is preserved as evidence in `findings.json` and `commands.md`.

## Residual uncertainty

The repository may contain actionable issues, but this run could not distinguish them from environment setup failures. A follow-up run from a working local execution environment is required.
