---
task_id: 2026-05-26-next-stage-mainline-evidence
status: complete
session_goal: "Complete the next-stage mainline tasks from the GCS narrative map: fixture corpus maturity ladder, demo ladder, permission threat matrix, and 20-minute contributor path."
archive_target: docs/completed-tasks/2026-05-26-next-stage-mainline-evidence/
experience_links:
  - docs/architecture/96-fixture-corpus-maturity-ladder.md
  - docs/product/gcs-demo-ladder.md
  - docs/agentic/permission-threat-matrix.md
  - docs/product/20-minute-contributor-path.md
---

# Next-Stage Mainline Evidence

## Task Objective

Execute the next-stage mainline from the GCS narrative map by turning the
identified weak or partial narrative lines into active, evidence-oriented
project docs.

## Scope And Non-Goals

In scope:

- Fixture corpus maturity ladder.
- Demo ladder from CLI evidence to Solver Evidence Workbench.
- Agent permission threat matrix.
- 20-minute contributor path.
- Safe updates to clean active docs and entry points.
- Validation, scoped commit, and push.

Out of scope:

- Solver/runtime/IO/viewer behavior changes.
- New fixtures, generated scenes, or code changes.
- Default quality-gate enforcement changes.
- Staging unrelated dirty repository-audit, AI-governance, or OpusTime work.

## Interaction Summary

The user asked to complete the next-stage mainline tasks according to the
agent's rhythm and push when appropriate. The work followed the active
narrative map: strengthen corpus, demo, governance, and onboarding paths while
keeping the evidence-first solver arc as the main line.

## Work Completed

- Added a fixture corpus maturity ladder that classifies smoke,
  verification, generated, milestone, counterexample, showcase, and benchmark
  candidate scenes.
- Added a product demo ladder from repository orientation through CLI,
  diagnostic, replay, corpus, workbench, showcase, and external comparison
  levels.
- Added a permission threat matrix connecting agent powers to data,
  untrusted content, outbound actions, git actions, dependency actions,
  fixture promotion, and protected semantics.
- Added a 20-minute contributor path for technical reviewers.
- Updated clean active entry points and plan docs where safe.

## Files And Artifacts

- `docs/architecture/96-fixture-corpus-maturity-ladder.md`: corpus maturity
  levels, promotion contracts, transition rules, and next actions.
- `docs/product/gcs-demo-ladder.md`: demo maturity levels and demo package
  contract.
- `docs/agentic/permission-threat-matrix.md`: concrete risk matrix for agent
  permissions and governance gates.
- `docs/product/20-minute-contributor-path.md`: one-sitting technical reviewer
  path.
- `docs/architecture/95-gcs-narrative-map.md`: phase status and next queue
  updated after the new docs.
- `docs/architecture/README.md`: index entry for the corpus maturity ladder.
- `docs/product/README.md`: index entries for product docs.
- `docs/product/gcs-product-user-brief.md`: next product tasks updated after
  first follow-ups.
- `docs/agentic/agent-permission-policy.md`: linked to the threat matrix.
- `docs/agentic/metrics-dashboard.md`: current snapshot updated.
- `docs/agentic/tasks/2026-05-26-next-stage-mainline-evidence.md`: task card
  and evidence bundle.
- `docs/completed-tasks/2026-05-26-next-stage-mainline-evidence/README.md`:
  this archive.

## Evidence

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-next-stage-mainline-evidence.md
[OK] task-card passed.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-next-stage-mainline-evidence\README.md
[OK] completed-task-report passed.

python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed.

python tools\agentic_design\agentic_toolkit.py validate-inventory
[OK] inventory: structured module inventory passed.

python tools\agentic_design\agentic_toolkit.py validate-skills
[OK] skills: all module skills passed.

python tools\agentic_design\agentic_toolkit.py check-dependencies
[OK] dependencies: import boundaries passed.

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-next-stage-mainline-evidence\README.md --min-score 30
Closure score: 38/40 after final evidence rewrite.
```

## Decisions

- Kept the batch documentation-only so it would not disturb solver/runtime
  behavior.
- Treated corpus and demo ladders as the main connection back to real solver
  evidence.
- Added the permission matrix under `docs/agentic/` because it governs agentic
  workflow, not solver architecture.
- Added contributor onboarding under `docs/product/` because it is audience and
  adoption truth, not module contract truth.
- Did not update `docs/completed-tasks/README.md` because it had pre-existing
  unrelated local modifications when this task began.

## Skipped Checks And Risks

- Build, CTest, and UI checks were skipped because this batch changed only
  documentation and active planning artifacts.
- The new demo ladder names future demo packages but does not yet include a
  command transcript or screenshots.
- The corpus ladder defines promotion criteria but does not promote or
  reclassify fixtures in this batch.

## Follow-Up

- Add D1 smoke demo note with command transcript.
- Add D2 diagnostic classification demo package.
- Add release-readiness checklist.
- Add external solver comparison and benchmark plan.
- Add negative evals for unrelated dirty-file staging and automated audit
  overclaiming human approval.

## Archive Handoff

- Archive path: `docs/completed-tasks/2026-05-26-next-stage-mainline-evidence/`
- Related active docs:
  - `docs/architecture/96-fixture-corpus-maturity-ladder.md`
  - `docs/product/gcs-demo-ladder.md`
  - `docs/agentic/permission-threat-matrix.md`
  - `docs/product/20-minute-contributor-path.md`
- Skill, eval, fixture, or tool update needed:
  - Future eval candidates are listed under follow-up; no immediate skill
    update is required.
