---
experience_id: E007-parallel-experiment-worker-orchestration
source: cache-hit-pilot-session
status: candidate-experience
root_cause: independent-experiment-runs-with-shared-telemetry-state
affected_modules:
  - agentic_dispatch
  - token_audit
  - task_closure
promotion_target: orchestrator-dispatch-template-after-second-confirmation
---

# E007: Parallel Experiment Worker Orchestration

## Thesis

When an experiment needs many independent task runs but one shared result
ledger, use parallel workers for isolated artifacts and a single controller for
telemetry import, scoring, summarization, and closure.

## Problem

If every worker writes the shared CSV or summary, the experiment risks row
collisions, duplicate samples, inconsistent scoring, and noisy commits. If the
controller runs all tasks serially, the experiment wastes time and loses the
main benefit of context isolation.

## Practice

Use this structure:

1. Write a runbook with stable `run_id`, `task_pair`, lane, artifact path, and
   acceptance evidence for every worker.
2. Dispatch each worker with a self-contained prompt.
3. Tell workers to create only their assigned artifact and report audit fields.
4. Keep JSONL transcript parsing, row append, summary generation, and closure
   in the controller session.
5. Verify every worker output for scope, evidence, honesty, and completeness
   before recording it.
6. Record duplicates or failed validations as experiment evidence, not as
   material to hide.

## Evidence

This experience comes from the cache-hit Full/Lite pilot:

- Task card: `docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md`
- Archive: `docs/completed-tasks/2026-05-31-cache-hit-pilot-eight-pairs/README.md`
- Orchestration audit: `docs/completed-tasks/2026-05-31-cache-hit-pilot-eight-pairs/orchestration-audit.md`
- Run package: `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/`

Concrete results:

| Metric | Value |
|---|---:|
| Worker runs recorded | 16 |
| Complete Full/Lite pairs | 8 |
| Shared CSV writers | 1 controller |
| Duplicate worker rows accepted | 0 |
| Validation failures preserved | 1 |
| Aggregate classification | `redundant-overhead` |

## When To Use

- A pilot needs many independent worker runs with comparable acceptance gates.
- Each worker can write exactly one artifact without reading another worker's
  result.
- A controller can record telemetry from immutable transcripts after the fact.
- The experiment needs honest failure rows, not only successful outputs.

## When Not To Use

- Workers need to coordinate a shared design in real time.
- Worker outputs must be consumed by later workers.
- The shared ledger must be updated live by every worker.
- The batch cannot be centrally verified before synthesis.

## Skill Or Agent Decision

Do not promote a new active skill or institutional agent yet.

- Existing `orchestrator` owns architecture selection and central synthesis.
- Existing `gcs-token-audit-steward` owns token telemetry and experiment rows.
- Existing `task-scoped-session-closer` owns durable closure.

Candidate future improvement: add an orchestrator dispatch template for
experiment workers after one more pilot confirms the same pattern with a
different metric surface.

## Promotion Threshold

Promote this candidate only after another experiment uses the same pattern with:

- five or fewer concurrent workers per batch, or explicit justification for
  more;
- zero shared-ledger writes outside the controller;
- all accepted worker outputs verified before row recording;
- a completed-task archive that includes an orchestration audit.
