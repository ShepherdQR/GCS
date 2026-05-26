# Repair Plan

## Minimal repair

1. Fix the local Codex sandbox/process-launch layer so commands can start in this worktree.
2. Re-run the nightly immune diagnostics workflow without changing the requested command set.
3. Replace this blocked calibration bundle with a normal evidence bundle for the same date only if a human explicitly wants that overwrite.

## Required validation after repair

1. `git status --short --branch` returns successfully and can be recorded.
2. `git rev-parse HEAD` returns successfully and can be recorded.
3. Both policy docs are readable:
   - `docs/agentic/nightly-immune-diagnostics.md`
   - `docs/agentic/pr-audit-governance.md`
4. Each requested diagnostic command runs and is classified as success, failure, or environment-missing-dependency evidence.
5. The regenerated `findings.json` uses the exact taxonomy and severity vocabulary from the local nightly diagnostics policy.

## Decision notes

- No dependencies were installed.
- No commits were created.
- No branches were modified.
- No fixtures were promoted.
- No network access was used.
