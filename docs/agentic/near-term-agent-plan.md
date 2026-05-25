# Near-Term Agent Execution Plan

Snapshot: 2026-05-25.

## Purpose

This plan turns the current agent discussion into immediate, reviewable work.
It covers the next few GCS agentic-SE sessions. The goal is not to create more
agent names. The goal is to make the existing agent system executable,
auditable, and useful in real project work.

## Current Facts

- The agentic operating layer exists under `docs/agentic/`.
- The lifecycle roadmap exists in `docs/agentic/agile-pdca-roadmap.md`.
- The first institutional-agent directory exists under
  `docs/agentic/institutional-agents/`.
- `I001 刀匠: 淬炼-锻打` and `I002 裁缝: 裁剪-缝合` are the first core seed
  institutional agents.
- `I003 Atelier Steward: Calibrate-Review` and
  `I004 Art Director: Frame-Judge` exist as visual-system seed agents and need
  to be kept indexed and evaluated rather than overwritten.
- Step 46 is marked done in the implementation roadmap. This plan reconciled
  the earlier PDCA drift by recording that no matching Step 46 task card or
  archive was found and by moving the next real lifecycle sample to Step 47 or
  the next high-risk engineering task.
- Step 47 has now completed the full lifecycle: task card, implementation,
  tests, completed-task archive, roadmap update, closure score, and a real
  `刀匠` example. `裁缝` was intentionally skipped for that sample, then later
  used for an explicit local repository stitch timeline.
- Step 48 has now completed the paired engineering/process lifecycle:
  runtime replay evidence is exposed through a viewer/report adapter and CLI
  `--replay-evidence`, while S1-03 produced the task-to-archive checklist.
- S1-05 has reviewed the first two lifecycle archives with E001, Step 49 chose
  the saved replay evidence report artifact, S3-02 added a negative E001 eval,
  S1-04 defined the low-risk chat-only boundary, and Step 50 kept saved replay
  evidence as a CLI/report artifact for now.
- S2-02 and S2-03 have implemented opt-in task-card and completed-report
  include gates. Step 51 has implemented a focused promoted fixture-library
  gate. I003/I004 now have conservative seed packages and remain seed roles.

## Execution Principle

Near-term work follows this order:

```text
sync truth -> make seed agents verifiable -> validate closure on real work
  -> add opt-in gates -> promote only from evidence
```

## Workstream A: Roadmap Truth Sync

Goal: keep agentic roadmaps aligned with implementation reality.

| ID | Task | Status | Output |
| --- | --- | --- | --- |
| A1 | Record that Step 46 implementation is done but the S1-02 lifecycle sample was not found as a task/archive pair. | done in this plan | This plan's Current Facts section. |
| A2 | Decide whether to backfill a Step 46 retrospective archive or use Step 47 as the next true lifecycle sample. | done in this plan | `agile-pdca-roadmap.md` update. |
| A3 | Update the PDCA queue after A2. | done in this plan | Roadmap C002 update. |
| A4 | Record Step 47 lifecycle completion and move the queue to S1-03. | done in this plan | Roadmap C003 update and this plan. |
| A5 | Record Step 48 and S1-03 completion, then move the queue to S1-05 and Step 49. | done in this plan | Roadmap C004 update and Step 48 archive. |
| A6 | Record S1-05 and Step 49 completion, then move the queue to S3-02, S1-04, and Step 50. | done in this plan | S1-05 calibration note and Step 49 archive. |
| A7 | Record S3-02, S1-04, and Step 50 completion, then move the queue to S2-01, S3-04, S4-05, and Step 51. | done in this plan | Negative eval, low-risk boundary, Step 50 archive, and roadmap C008 update. |
| A8 | Record S2-01 opt-in gate policy completion, then move Phase 2 to S2-02. | done in this plan | `quality-gate-opt-in-policy.md` and roadmap C009 update. |
| A9 | Record S2-02, S2-03, Step 51, and I003/I004 seed-package integration. | done in this plan | `agile-pdca-roadmap.md` C012 update. |

Decision rule: do not fabricate lifecycle evidence. If no task card or archive
exists, mark it as an escaped lifecycle sample and use the next high-risk task
to prove the loop.

## Workstream B: Make Seed Institutional Agents Verifiable

Goal: each seed institutional agent should have a prompt, output template, and
at least one eval that can fail.

| ID | Task | Status | Output |
| --- | --- | --- | --- |
| B1 | Add invoke prompt for `刀匠`. | done in this plan | `001-bladesmith-quench-forge/prompts/invoke.md` |
| B2 | Add experience-forging note template for `刀匠`. | done in this plan | `001-bladesmith-quench-forge/templates/experience-forging-note.md` |
| B3 | Add unsupported-generalization eval for `刀匠`. | done in this plan | `001-bladesmith-quench-forge/evals/refuse-unsupported-generalization.md` |
| B4 | Add invoke prompt for `裁缝`. | done in this plan | `002-tailor-stitch-timeline/prompts/invoke.md` |
| B5 | Add timeline-entry template for `裁缝`. | done in this plan | `002-tailor-stitch-timeline/templates/timeline-entry.md` |
| B6 | Add invented-causality eval for `裁缝`. | done in this plan | `002-tailor-stitch-timeline/evals/refuse-invented-causality.md` |
| B7 | Add a real filled example for `刀匠`. | done in this plan | Step 47 lifecycle forging note. |
| B8 | Add a real filled example for `裁缝`. | done in local stitch | `002-tailor-stitch-timeline/examples/2026-05-24-local-repo-stitch-timeline.md` |
| B9 | Add similar prompt/template/eval packages for I003 and I004 if a real visual task invokes them. | done in this plan | I003/I004 prompts, templates, evals, and Figure 72 seed examples. |

Definition of done for B: each core seed agent can be invoked by reading its
README plus `prompts/invoke.md`, can emit a structured artifact using its
template, and has a refusal eval that prevents overreach.

## Workstream C: Validate E001 Session Closure

Goal: prove that task-scoped closure improves future resumption, not just that
the templates exist.

| ID | Task | Status | Output |
| --- | --- | --- | --- |
| C1 | Identify two completed archives to score with E001. | done in this plan | C001 and Step 47 are the first candidate pair. |
| C2 | Score the archives and compare with human review notes. | done in this plan | `experience/001-task-scoped-session-closure/calibration/2026-05-24-s1-05-first-archive-review.md` |
| C3 | Add one negative eval for archive pollution or false completion. | done in this plan | `experience/001-task-scoped-session-closure/evals/2026-05-25-false-completion-archive-pollution.md`. |
| C4 | Decide whether to promote E001 into an installed project skill. | done in this plan | `.codex/skills/task-scoped-session-closer` and E001 promotion decision. |

## Workstream D: Opt-In Agentic Quality Gates

Goal: make agentic artifacts checkable without forcing ceremony on every small
task.

| ID | Task | Status | Output |
| --- | --- | --- | --- |
| D1 | Design `--include-task-cards` and `--include-completed-reports`. | done in this plan | `docs/agentic/quality-gate-opt-in-policy.md`. |
| D2 | Add task-card validator tests for missing fields and high-risk gates. | done in this plan | `tests/tools/test_agentic_toolkit.py` cases and `agentic.task-cards`. |
| D3 | Add completed-report validator tests for new reports only. | done in this plan | `tests/tools/test_agentic_toolkit.py` cases and `agentic.completed-task-reports`. |
| D4 | Define legacy archive exemption or migration policy. | next | `docs/completed-tasks/README.md` update. |

## Workstream E: Fuzzy Description To Agent Package

Goal: prove that a vague role idea can become a usable agent package through
the generator protocol.

| ID | Task | Status | Output |
| --- | --- | --- | --- |
| E1 | Use `templates/role-card-generator-prompt.md` on one real fuzzy role request. | pending | Generated decision and role package. |
| E2 | Check whether the result should be candidate, seed, or update-existing. | pending | Fit-check record. |
| E3 | Add one accepted example and one rejected example to the generation pipeline. | pending | Generator examples. |

## Immediate Next Task

Start with S2-04 for Agentic SE tooling. Choose the next GCS implementation
candidate after the parallel item 4 session lands:

1. Define legacy archive exemption or migration policy.
2. Keep E001 out of default quality gates until S2-05.
3. Rerun I003/I004 only on rendered visual artifacts before promotion.
4. Review the parallel item 4 output before claiming the next solver step.

## Superseded Immediate Task Note

Start with S1-03:

1. Convert C001, C002, and Step 47/C003 into a task-to-archive checklist.
2. Add one checked example using the Step 47 task card and completed-task
   archive.
3. Keep the checklist lightweight and path-scoped so it helps high-risk tasks
   without forcing ceremony on small work.
4. Use the new `裁缝` local repository stitch as the first real timeline
   example, but continue avoiding invented causality.

## Acceptance Gate

This near-term plan is working when:

- the roadmap no longer points at stale Step 46 work as if it were still next;
- `刀匠` and `裁缝` each have prompt, template, and eval seed;
- at least one real filled example exists for both `刀匠` and `裁缝`;
- S1-03's task-to-archive checklist exists and has been used on a real
  engineering/process closure;
- E001 has at least two scored archives;
- no new institutional-agent directory is created without generator fit-check
  evidence.
