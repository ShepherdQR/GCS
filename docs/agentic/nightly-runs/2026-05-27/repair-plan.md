# Repair Plan - 2026-05-27

## Minimal repair

1. Fix the local command-execution sandbox so a trivial command can launch in this worktree.
2. Confirm local file reads work for:
   - `docs/agentic/nightly-immune-diagnostics.md`
   - `docs/agentic/pr-audit-governance.md`
3. Rerun the nightly workflow with the same command list and no repo edits outside the dated run directory unless a human explicitly broadens scope.

## Why this is minimal

- The failure occurred before any repo-specific diagnostic command launched.
- No evidence currently points to a repository defect; the blocker is the execution environment.
- The correct next step is to restore command launch capability and rerun, not to infer repo health from missing evidence.

## Required validation after repair

1. Capture branch, commit SHA, and `git status --short --branch`.
2. Run:
   - `python tools\agentic_design\agentic_toolkit.py validate-docs`
   - `python tools\agentic_design\agentic_toolkit.py validate-inventory`
   - `python tools\agentic_design\agentic_toolkit.py validate-skills`
   - `python tools\agentic_design\agentic_toolkit.py check-dependencies`
   - `python tools\scene_generation\tools.py list`
   - `python -m unittest tests.tools.test_scene_generation_explorer`
   - `python tools\agentic_design\agentic_toolkit.py run-quality-gates --skip-build --skip-ctest --skip-cli --continue-on-failure`
3. Reclassify findings from actual command evidence instead of provisional blocked-run evidence.

## Notes for the next run

- Treat missing dependencies as evidence, not as success.
- Keep this first-calibration constraint: do not edit files outside the dated run directory and do not create commits.
