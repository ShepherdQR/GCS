---
task_id: 2026-05-25-repository-cleanup-scene-fixture-hygiene
status: complete
request: "Use Tailor to clean repository branches, push local work, preserve useful scene fixtures, and leave Bladesmith learning before continuing the Agentic SE queue."
scope: maintenance
risk: medium
owning_agent: gcs-scene-generation-engineer
specialist_agents:
  - gcs-scene-behavior-steward
  - gcs-architecture-steward
affected_contracts:
  - Scene fixture promotion policy
  - Agentic lifecycle closure
affected_paths:
  - .gitignore
  - fixtures/scene/milestone/
  - fixtures/scene/counterexamples/
  - docs/agentic/
  - docs/completed-tasks/
required_evidence:
  - git branch audit
  - json fixture audit
  - CLI smoke or expected-failure check
  - validate-task-card
  - validate-completed-task-report
  - score-closure-report
  - validate-docs
human_gate_required: false
human_gate_reason: "The user explicitly requested branch cleanup, push, repository hygiene, and continuation through the task-card-to-Bladesmith loop."
---

# Repository Cleanup And Scene Fixture Hygiene

## Scope

Clean the Git branch/worktree state after local commits, classify newly
generated scene artifacts, preserve durable scene fixtures, hide scratch store
outputs, and archive the result through the agentic lifecycle.

In scope:

- push the current `master` commits;
- confirm stale child branches do not contain useful unmerged content;
- remove stale child branches locally and remotely;
- keep generated scratch artifacts out of future `git status` noise;
- preserve promoted milestone and counterexample fixtures with manifest
  evidence;
- create a Tailor timeline, completed-task archive, and Bladesmith note.

## Non-Goals

- Do not remove already tracked historical `.codex_scene_generation_store`
  artifacts in this cleanup commit.
- Do not change solver, IO, runtime, viewer, or scene schema semantics.
- Do not make milestone or counterexample fixtures default quality-gate inputs
  until a later fixture-gate task chooses that policy.

## Context To Read

- `docs/agentic/institutional-agents/002-tailor-stitch-timeline/README.md`
- `docs/agentic/institutional-agents/001-bladesmith-quench-forge/README.md`
- `docs/agentic/task-to-archive-checklist.md`
- `.codex/skills/gcs-scene-generation-engineer/SKILL.md`
- `.codex/skills/gcs-scene-behavior-steward/SKILL.md`

## Acceptance Gates

- `master` is pushed and matches `origin/master`.
- stale child branches are removed after comparison against `master`.
- `.codex_scene_generation_store/` is ignored for new scratch files.
- promoted scene fixture directories are documented and not hidden as scratch.
- task card, archive, Tailor timeline, and Bladesmith note exist.

## Verification Plan

```bat
git status --short --branch
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-repository-cleanup-scene-fixture-hygiene.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-repository-cleanup-scene-fixture-hygiene\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-repository-cleanup-scene-fixture-hygiene\README.md --min-score 30
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

- `git push origin master`: passed; `origin/master` advanced to `ec096f8`.
- `git branch -d codex-ui-design-plan-archive`: passed after elevated refs
  access; branch was already merged into `master`.
- `git branch -D codex/2026-05-24-git-worktree-protocol`: passed after
  elevated refs access; branch was superseded by master-side commit `128d4e4`.
- `git push origin --delete ...`: passed for both stale child branches.
- JSON audit over milestone and counterexample manifests, metadata, and model
  files: passed, 8 files loaded.
- `GCS.exe fixtures\scene\milestone\milestone_20g40c_20260524.gcs.json`:
  passed with `AcceptedWithWarnings`.
- `GCS.exe fixtures\scene\milestone\all_types_10g18c_20260524.gcs.json`:
  expected failure confirmed; status `Failed`, native exit code 2.
- `GCS.exe fixtures\scene\counterexamples\mixed_geometry_20g40c_singular_20260524.gcs.json`:
  expected failure confirmed; status `NumericallySingular`, native exit code 2.
- `validate-task-card`: passed.
- `validate-completed-task-report`: passed.
- `score-closure-report`: passed at 36/40.
- `validate-docs`: passed.

## Residual Risks

- Historical tracked scratch-store files remain in the repository and should be
  handled by a separate migration/removal task if the project wants a fully
  clean fixture store.
- The new milestone and counterexample fixtures are documented but not yet part
  of an automated fixture-library gate.
