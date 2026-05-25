# Experience Forging Note: Repository Cleanup Fixture Hygiene

Date: 2026-05-25

Role: `Bladesmith: Quench-Forge`

Status: provisional

## Source Scope

- Session/task: `2026-05-25-repository-cleanup-scene-fixture-hygiene`
- Time range: 2026-05-25
- Source artifacts:
  - `docs/agentic/tasks/2026-05-25-repository-cleanup-scene-fixture-hygiene.md`
  - `docs/completed-tasks/2026-05-25-repository-cleanup-scene-fixture-hygiene/README.md`
  - `docs/agentic/institutional-agents/002-tailor-stitch-timeline/examples/2026-05-25-repository-cleanup-timeline.md`
  - `fixtures/scene/milestone/manifest.json`
  - `fixtures/scene/counterexamples/manifest.json`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | `master` was pushed to `origin/master`; stale local and remote child branches were deleted; new generated scratch output was separated from durable fixtures. |
| Decisions | `.codex_scene_generation_store/` is scratch for new outputs; milestone and counterexample fixtures remain visible under `fixtures/scene/`. |
| Preferences | Keep repository status readable before starting new Agentic SE loops. |
| Hypotheses | A fixture-library audit command will be a better long-term guard than manually inspecting manifests. |
| Open questions | Whether older tracked scratch-store files should remain in Git history as durable provenance or be moved out in a dedicated cleanup. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Branch cleanup needs a Tailor pass before deletion. | A child branch is stale but not merged by hash. | Fetch, compare range/diff, identify superseding master commits, then delete. | Do not delete a branch just because names look similar. | `git range-diff 67c0719..37cd216 67c0719..128d4e4` | Applies to cleanup, not to active feature branches. |
| Generated data must be split into scratch and fixtures before commit. | Scene generation produces many store files plus a small promoted set. | Ignore scratch roots and commit only documented fixture assets. | Do not hide `fixtures/scene/` outputs as scratch. | `.gitignore`, milestone/counterexample manifests | Applies after promotion evidence exists. |
| Expected-failure fixtures need status metadata. | A generated scene is valuable but currently fails the solver. | Keep the scene only with manifest and metadata that name current status and promotion condition. | Do not put expected failures into green smoke gates without an expectation wrapper. | `fixtures/scene/counterexamples/manifest.json` | Does not replace automated fixture gates. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| All `.codex_scene_generation_store` content should be deleted immediately. | Some historical files are already tracked and may encode prior provenance. | A dedicated migration decision comparing tracked store files with promoted fixtures. |
| Every milestone fixture must solve successfully. | `all_types_10g18c_20260524` captures catalog coverage and current solver boundary evidence. | A milestone policy or fixture audit that distinguishes accepted milestones from boundary milestones. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale: the durable lesson is a guardrail for generated artifact cleanup.
Future lifecycle docs should remind agents to split scratch stores from
promoted fixtures before staging.

## Follow-Up

- Add a fixture-library audit command for milestone and counterexample
  manifests.
- Decide historical scratch-store retention separately from normal task cleanup.
