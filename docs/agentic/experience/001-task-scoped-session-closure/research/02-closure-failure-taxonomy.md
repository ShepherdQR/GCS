# Closure Failure Taxonomy

## Purpose

This note classifies how agentic-SE sessions fail when they do not close as
bounded, evidence-bearing task transactions. The taxonomy is meant to support
review, eval design, and future validators.

The governing question is:

```text
What makes a session impossible or expensive to trust after the chat ends?
```

## Failure Map

| Failure Class | Short Definition | Primary Damage |
| --- | --- | --- |
| Objective drift | Work silently moves away from the original goal | Review cannot tell what was accepted |
| Scope bleed | Related work enters without being named | Change set becomes hard to bound |
| Evidence gap | Completion claims lack checks or artifacts | Trust depends on agent confidence |
| Decision loss | Important reasoning stays in chat | Future maintainers re-litigate choices |
| False completion | Agent stops after editing, before closure | Task state is ambiguous |
| Archive loss | Durable result is not stored where future work can find it | Project memory decays |
| Archive pollution | Raw transcript or noisy material is stored | Memory becomes hard to use |
| Lesson leakage | Reusable learning is not promoted | The same failure repeats |
| Risk burial | Skipped checks or uncertainty are hidden | Review receives optimistic fiction |
| Tool trace opacity | Commands are mentioned without meaningful result | Evidence cannot be interpreted |

## 1. Objective Drift

Objective drift occurs when the session starts with one task and ends with
another, without an explicit rebinding step.

Symptoms:

- final summary emphasizes work not requested;
- changed files do not match the original goal;
- acceptance criteria are invented after implementation;
- the user would need to read the whole chat to know when the goal changed.

Root causes:

- vague initial request;
- agent over-association with adjacent improvements;
- missing task card for non-trivial work;
- failure to pause when user feedback changes the target.

Prevention:

- write a one-sentence task objective before deep work;
- restate material scope changes;
- keep final report anchored to the objective;
- put unrelated discoveries into follow-up, not completed work.

Top cognitive move:

```text
Treat goal change as a transaction rebind, not as conversational drift.
```

## 2. Scope Bleed

Scope bleed occurs when the agent performs plausible but unrequested adjacent
work. Unlike objective drift, the primary goal may still be completed, but the
change set becomes wider than the task contract.

Symptoms:

- unrelated files appear in the diff;
- documentation refactors accompany a small requested change;
- tests or generated artifacts change without explanation;
- final report groups unrelated edits as if they were necessary.

Root causes:

- local cleanup temptation;
- insufficient non-goals;
- no explicit touched-path boundary;
- conflation of "noticed" with "must fix now."

Prevention:

- name non-goals for tasks that touch shared docs or architecture;
- list files changed with a reason per file;
- move adjacent ideas into follow-up;
- preserve unrelated user changes.

Top cognitive move:

```text
Use scope as a trust boundary, not just as a planning convenience.
```

## 3. Evidence Gap

An evidence gap occurs when the final answer claims completion but does not
record what was run, observed, skipped, or produced.

Symptoms:

- final report says "verified" without commands;
- no pass/fail status is recorded;
- generated files are not named;
- skipped checks are absent even when obvious.

Root causes:

- confusing task completion with edit completion;
- no evidence section in the closure template;
- excessive reliance on conversational confidence;
- commands fail or are expensive, so they are quietly omitted.

Prevention:

- require command summaries or explicit skipped-check notes;
- distinguish static review from executable validation;
- include failure output only in summarized form;
- make "not run" an acceptable but visible state.

Top cognitive move:

```text
Evidence is not decoration after work; it is part of the work product.
```

## 4. Decision Loss

Decision loss occurs when important rationale remains only in the interaction
and is not preserved in a durable artifact.

Symptoms:

- future agents repeat context discovery;
- reviewers ask why a directory, template, or approach was chosen;
- a convention exists but its rationale is missing;
- user decisions are remembered socially but not in the repo.

Root causes:

- chat feels like memory during the session;
- reports list outputs but not decisions;
- no distinction between transient conversation and source of truth.

Prevention:

- add a "Decisions" section to reports;
- preserve only decisions that affect future work;
- link decisions to files and constraints;
- avoid raw transcript storage.

Top cognitive move:

```text
Preserve decision compression, not conversation exhaust.
```

## 5. False Completion

False completion is the central E001 failure. The agent treats "I made the
change" as equivalent to "the task is complete."

Symptoms:

- final response arrives before evidence is gathered;
- no archive is created for durable work;
- follow-up risks are discovered only in later sessions;
- report writing is treated as optional ceremony.

Root causes:

- action bias toward editing;
- weak closure habit;
- no explicit done definition;
- pressure to keep final responses short.

Prevention:

- make closure a required phase for non-trivial tasks;
- keep final user-facing response short but archive report complete;
- use a session closure agent or checklist;
- define done as evidence-bearing archive state.

Top cognitive move:

```text
Do not confuse local action completion with global task closure.
```

## 6. Archive Loss

Archive loss occurs when a useful task report or reusable lesson is not stored
in a durable project path.

Symptoms:

- later work cannot find the prior task;
- the same design question is answered again;
- no index points to the completed work;
- a useful experience remains only in chat.

Root causes:

- no archive target in the task flow;
- uncertainty about whether a task deserves archiving;
- lack of folder contract;
- no completed-task index maintenance.

Prevention:

- define archive target during closure;
- use `docs/completed-tasks/` for task memory;
- use `docs/agentic/experience/` for generalized practice;
- update indexes as part of archive.

Top cognitive move:

```text
Memory that cannot be found does not exist operationally.
```

## 7. Archive Pollution

Archive pollution is the opposite of archive loss. Material is stored, but it
is too noisy to become useful memory.

Symptoms:

- raw chat logs are copied into docs;
- reports are long but low-signal;
- duplicated command output hides the result;
- future agents avoid reading the archive.

Root causes:

- confusing completeness with volume;
- no distinction between evidence summary and raw log;
- fear of losing context;
- missing report template.

Prevention:

- store distilled decisions and evidence;
- link or summarize large artifacts instead of pasting them;
- keep reports path-based;
- write for future retrieval, not historical exhaustiveness.

Top cognitive move:

```text
The archive is a retrieval interface, not a transcript warehouse.
```

## 8. Lesson Leakage

Lesson leakage occurs when a repeated or high-value process insight is not
promoted into a reusable artifact.

Symptoms:

- the same mistake recurs;
- agents receive advice in chat but no skill changes;
- templates remain weaker than observed practice;
- evals do not capture known failure modes.

Root causes:

- no promotion tier;
- weak distinction between task report and experience record;
- reluctance to update skills;
- no validation story for the lesson.

Prevention:

- create experience records for durable lessons;
- stage candidate skills inside experience folders;
- promote only after evidence or high severity;
- attach eval or validator ideas to every promoted lesson.

Top cognitive move:

```text
Learning is complete only when the environment changes.
```

## 9. Risk Burial

Risk burial occurs when uncertainty or skipped verification is softened until it
disappears from the durable record.

Symptoms:

- "looks good" replaces "not tested";
- skipped checks are missing from final report;
- residual risk appears only as vague caveat;
- future work assumes a stronger guarantee than exists.

Root causes:

- politeness pressure;
- desire to sound complete;
- weak skipped-check section;
- no norm that visible risk is acceptable.

Prevention:

- make skipped checks a first-class report section;
- record reason and risk separately;
- use accepted-with-risk states when needed;
- avoid optimistic language unsupported by evidence.

Top cognitive move:

```text
Visible uncertainty is safer than hidden confidence.
```

## 10. Tool Trace Opacity

Tool trace opacity occurs when commands are recorded without enough summary to
be meaningful.

Symptoms:

- command names appear without exit status;
- long logs are pasted without interpretation;
- failures are recorded but not classified;
- readers cannot tell whether evidence supports completion.

Root causes:

- treating tool output as self-explanatory;
- no evidence bundle standard;
- excessive log copying;
- lack of result summary discipline.

Prevention:

- record command, result, and implication;
- summarize failure cause when known;
- keep long logs out of the main report;
- distinguish command execution from validation success.

Top cognitive move:

```text
A trace becomes evidence only after interpretation.
```

## Failure Severity

| Severity | Meaning | Example |
| --- | --- | --- |
| P0 | Closure failure can cause wrong future work | Hidden failed verification for semantic change |
| P1 | Closure failure makes review materially harder | Missing decisions for architecture convention |
| P2 | Closure failure causes friction or rediscovery | No archive index entry |
| P3 | Closure failure is cosmetic or low impact | Minor wording noise in report |

## Detection Prompts

Use these during review:

- What was the original objective?
- Did the objective change?
- Are changed files explainable from the objective?
- What evidence supports the completion claim?
- What was not checked?
- What should future agents remember?
- Where is the durable archive?
- Is there a reusable lesson that should become a skill, eval, template, or
  tool?

## Core Insight

Most closure failures are not failures of intelligence. They are failures of
state transfer. The agent knows something at the end of the conversation, but
the project does not. E001 exists to make that transfer deliberate.
