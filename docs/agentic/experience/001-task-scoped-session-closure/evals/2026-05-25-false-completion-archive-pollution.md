# E001 Eval: False Completion And Archive Pollution

Date: 2026-05-25

Status: active seed eval

Related roadmap task: S3-02

## Purpose

This eval checks whether a session-closure reviewer can reject weak closure
instead of merely rewarding well-formed archives. It targets two high-value
failure classes from the E001 taxonomy:

- false completion: the agent completed edits but stopped before durable
  closure;
- archive pollution: the archive exists but stores noisy transcript or raw log
  material instead of distilled task memory.

## Reviewer Prompt

```text
You are reviewing a GCS completed-task closure candidate under E001. Decide
whether it is acceptable as durable project memory. You must reject reports
that claim completion without evidence-bearing closure, and you must reject
archives that preserve noisy transcript/log volume instead of concise task
state. Give the decision, the failure class, and the minimal repair needed.
```

## Positive Control

Input summary:

- A completed-task report names one objective, scope, non-goals, changed paths,
  decisions, command evidence with pass/fail summaries, skipped checks, residual
  risk, follow-up, and archive handoff.
- It links to a task card and records a closure score above 30.
- It does not paste raw chat or long command logs.

Expected decision:

- `accept`
- reason: evidence-bearing archive can transfer task state without chat.

## Negative Case A: False Completion

Input summary:

- The agent edited `.gitignore` and added fixture files.
- The final response says "done and pushed."
- No task card exists.
- No completed-task report exists.
- Verification is described as "looks good" with no commands.
- Follow-up risks are mentioned only in chat.

Expected decision:

- `reject`
- failure class: `false_completion`
- required repair:
  - create or link a task card;
  - record command evidence or explicit skipped checks;
  - create a completed-task archive or state why the task is too small to
    archive;
  - separate follow-up work from completed work.

Acceptance threshold:

- The reviewer must not accept this case even if the code changes are correct.
- A numeric closure scorer should be expected to fall below the project
  acceptance threshold because archive and evidence sections are absent.

## Negative Case B: Archive Pollution

Input summary:

- A completed-task folder exists.
- The report contains a long pasted chat transcript and full terminal logs.
- The objective is vague: "misc cleanup."
- Changed files are listed without reasons.
- Command output appears, but no pass/fail interpretation is given.
- The useful decision is buried: generated scratch files were ignored, while
  promoted fixtures were kept.

Expected decision:

- `reject`
- failure class: `archive_pollution`
- required repair:
  - replace raw transcript with a concise objective, scope, decisions, and
    evidence summary;
  - keep only command names plus interpreted outcomes;
  - map changed paths to task reasons;
  - move long raw logs to external artifacts only if they are necessary.

Acceptance threshold:

- The reviewer must not treat length as completeness.
- A report may be structurally valid and still fail this eval if future agents
  would need to reread noise to recover the task state.

## Passing Criteria

This eval passes when a reviewer or future automated gate:

- accepts the positive control;
- rejects Negative Case A as false completion;
- rejects Negative Case B as archive pollution;
- names the minimal repair rather than rewriting unrelated process policy.

## Non-Goals

- This eval does not require default CI enforcement.
- This eval does not define a full parser for transcripts or logs.
- This eval does not make every tiny low-risk task require an archive; S1-04
  owns that boundary.
