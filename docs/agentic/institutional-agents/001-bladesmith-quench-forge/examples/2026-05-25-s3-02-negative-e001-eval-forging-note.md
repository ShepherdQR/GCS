# Experience Forging Note: S3-02 Negative E001 Eval

Date: 2026-05-25

Role: `Bladesmith: Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-25-s3-02-negative-e001-eval`
- Time range: 2026-05-25
- Source artifacts:
  - `docs/agentic/experience/001-task-scoped-session-closure/evals/2026-05-25-false-completion-archive-pollution.md`
  - `docs/agentic/experience/001-task-scoped-session-closure/research/02-closure-failure-taxonomy.md`
  - `docs/agentic/agile-pdca-roadmap.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | E001 had positive calibration samples before S3-02. |
| Decisions | Add a seed eval with one positive control, one false-completion negative case, and one archive-pollution negative case. |
| Preferences | Keep the eval documentation-level until Phase 2 opt-in gates define enforcement. |
| Hypotheses | A future automated gate can encode the same accept/reject cases. |
| Open questions | Whether S3-04 should promote E001 into an installed project skill after S1-04 completes. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Closure evals need explicit reject cases. | A lifecycle experience has only positive archive examples. | Add a negative case that must fail even if the edited code is correct. | Do not confuse "valid edit" with "valid closure." | S3-02 eval | Applies to lifecycle evaluation, not solver correctness. |
| Archive pollution is a separate failure from archive loss. | A report exists but is noisy or transcript-like. | Require distilled objective, decisions, interpreted evidence, and follow-up. | Do not reward length as completeness. | E001 taxonomy and S3-02 eval | Does not ban necessary links to raw artifacts. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| The eval should become a default gate immediately. | Phase 2 has not designed opt-in artifact checks or legacy exemptions yet. | S2-01 to S2-04 gate design and tests. |
| Every chat-only task is false completion. | S1-04 still owns the low-risk boundary. | Entry criteria for chat-only tasks. |

## Recommended Promotion

Choose one:

- add or update an eval.

Rationale: S3-02 directly hardens E001 by adding failure behavior. No new skill
promotion is justified until S3-04 reviews E001 after the low-risk boundary is
defined.

## Follow-Up

- Complete S1-04 so the eval does not over-reject tiny low-risk tasks.
- Use S2-01 to decide whether this eval becomes an opt-in completed-report
  check.
