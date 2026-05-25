---
task_id: 2026-05-25-repository-cleanup-scene-fixture-hygiene
status: complete
session_goal: "Clean branch/worktree state, push local master, preserve useful generated scene fixtures, hide scratch scene output, and archive the lifecycle evidence."
archive_target: docs/completed-tasks/2026-05-25-repository-cleanup-scene-fixture-hygiene
experience_links:
  - docs/agentic/institutional-agents/002-tailor-stitch-timeline/examples/2026-05-25-repository-cleanup-timeline.md
  - docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-25-repository-cleanup-fixture-hygiene-forging-note.md
---

# Repository Cleanup And Scene Fixture Hygiene

## Task Objective

Use Tailor to reconcile branch history, push retained local work, delete stale
child branches after checking for useful content, then clean the scene
generation working state before continuing the Agentic SE queue.

## Scope And Non-Goals

In scope:

- push `master` to `origin/master`;
- delete stale local and remote child branches after comparison with `master`;
- keep newly generated scratch scene files out of future status noise;
- preserve generated milestone and counterexample fixtures as durable assets;
- create task card, Tailor timeline, completed-task archive, and Bladesmith
  learning note.

Out of scope:

- no solver, runtime, IO, viewer, or schema behavior change;
- no migration of historical tracked `.codex_scene_generation_store` files;
- no default quality-gate promotion for the new milestone/counterexample
  fixture directories.

## Interaction Summary

The user asked to use Tailor on the repository, verify child branches had no
useful remaining content before deletion, push local work, clean the working
tree, and then continue later tasks using the task-card-to-Bladesmith loop.
The branch cleanup completed first; scene generated outputs were then
classified as scratch or durable fixture assets.

## Work Completed

- Pushed `master` so `origin/master` now points at `ec096f8`.
- Removed stale local branches:
  - `codex-ui-design-plan-archive`;
  - `codex/2026-05-24-git-worktree-protocol`.
- Removed remote branches with the same names.
- Removed the clean linked worktree under
  `.codex/worktrees/2026-05-24-git-worktree-protocol`.
- Added `.codex_scene_generation_store/` to `.gitignore` so new scratch output
  no longer pollutes `git status`.
- Added `fixtures/scene/milestone/README.md` to classify milestone fixture
  status and promotion policy.
- Preserved `fixtures/scene/counterexamples/` as expected-failure scene
  evidence.
- Added a Tailor timeline and Bladesmith forging note.

## Files And Artifacts

- `.gitignore`
- `fixtures/scene/milestone/README.md`
- `fixtures/scene/milestone/manifest.json`
- `fixtures/scene/milestone/*.gcs.json`
- `fixtures/scene/milestone/*.metadata.json`
- `fixtures/scene/counterexamples/README.md`
- `fixtures/scene/counterexamples/manifest.json`
- `fixtures/scene/counterexamples/*.gcs.json`
- `fixtures/scene/counterexamples/*.metadata.json`
- `fixtures/scene/counterexamples/*.solver.txt`
- `docs/agentic/tasks/2026-05-25-repository-cleanup-scene-fixture-hygiene.md`
- `docs/agentic/institutional-agents/002-tailor-stitch-timeline/examples/2026-05-25-repository-cleanup-timeline.md`
- `docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-25-repository-cleanup-fixture-hygiene-forging-note.md`
- `docs/completed-tasks/2026-05-25-repository-cleanup-scene-fixture-hygiene/README.md`

## Evidence

```text
git fetch --prune
Passed: remote refs synchronized before branch deletion.

git branch --merged master
Passed: `codex-ui-design-plan-archive` was merged into master.

git range-diff 67c0719..37cd216 67c0719..128d4e4
Passed: `codex/2026-05-24-git-worktree-protocol` was superseded by the
master-side worktree protocol commit and later master commits.

git push origin master
Passed: `origin/master` advanced from `67c0719` to `ec096f8`.

git branch -d codex-ui-design-plan-archive
git branch -D codex/2026-05-24-git-worktree-protocol
Passed after elevated `.git/refs` access: local stale branches removed.

git push origin --delete codex-ui-design-plan-archive codex/2026-05-24-git-worktree-protocol
Passed: remote stale branches removed.
```

Additional fixture and lifecycle validation evidence is recorded in the task
card and final session handoff after commands are run.

```text
python -c "<json audit over milestone/counterexample manifests, metadata, and scenes>"
Passed: json-ok 8 files.

out\build\clang-ninja\GCS.exe fixtures\scene\milestone\milestone_20g40c_20260524.gcs.json
Passed: current accepted milestone confirmed with Status: AcceptedWithWarnings.

out\build\clang-ninja\GCS.exe fixtures\scene\milestone\all_types_10g18c_20260524.gcs.json
Expected failure confirmed: Status: Failed, native exit code 2,
obstruction `runtime.numeric_failure`.

out\build\clang-ninja\GCS.exe fixtures\scene\counterexamples\mixed_geometry_20g40c_singular_20260524.gcs.json
Expected failure confirmed: Status: NumericallySingular, native exit code 2,
obstruction `runtime.post_local_diagnostics_blocked`.

python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-repository-cleanup-scene-fixture-hygiene.md
Passed: task card validation.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-repository-cleanup-scene-fixture-hygiene\README.md
Passed: completed-task archive validation.

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-repository-cleanup-scene-fixture-hygiene\README.md --min-score 30
Passed: closure score 36/40.

python tools\agentic_design\agentic_toolkit.py validate-docs
Passed: docs validation.
```

## Decisions

- The worktree protocol child branch was deleted despite not being merged by
  hash because its useful content was superseded by `master` commit `128d4e4`
  and the later Step 48/49/next-queue commits.
- `.codex_scene_generation_store/` is scratch. Future generated candidates
  should be promoted into `fixtures/scene/` through a scene-generation task
  before commit.
- `fixtures/scene/milestone/` is allowed to contain both accepted and
  currently failing milestone scenes when metadata records the expected current
  solver status.
- `fixtures/scene/counterexamples/` is the right place for expected-failure
  solver-boundary scenes that should not make CI red simply by existing.

## Skipped Checks And Risks

- Full `run-quality-gates` was not required for the branch cleanup itself.
- Historical tracked scratch-store files remain in the repository; this task
  only prevents new scratch output from appearing as untracked noise.
- The new fixture directories are documented but need a later automated
  fixture-library gate if the project wants them continuously verified.

## Follow-Up

- Add a fixture-library audit command for milestone/counterexample manifests.
- Decide whether historical tracked `.codex_scene_generation_store` files
  should be migrated, archived elsewhere, or removed in a dedicated cleanup.
- Continue the Agentic SE queue with S3-02 negative E001 eval and S1-04
  low-risk chat-only boundary.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-25-repository-cleanup-scene-fixture-hygiene`
- Related experience:
  - Tailor repository cleanup timeline.
  - Bladesmith fixture hygiene note.
- Skill, eval, fixture, or tool update needed: add a future fixture-library
  audit command; no new institutional agent is needed.
