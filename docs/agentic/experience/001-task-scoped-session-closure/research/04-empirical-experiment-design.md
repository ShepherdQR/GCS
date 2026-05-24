# Empirical Experiment Design

## Purpose

This note designs experiments for testing whether E001 improves real
agentic-SE work. The goal is to move from plausible principle to observed
engineering effect.

The research question:

```text
Does task-scoped session closure reduce future review, resumption, and
rediscovery cost?
```

## Hypothesis

Structured closure reports improve agentic-SE outcomes by preserving:

- task intent;
- changed-state rationale;
- verification evidence;
- decisions and risks;
- archive location;
- reusable lessons.

The expected effect is not that every task becomes faster immediately. The
expected effect is that future work becomes easier to trust, resume, and learn
from.

## Experimental Conditions

Compare three closure styles across similar project tasks.

| Condition | Description |
| --- | --- |
| A: No durable closure | Final chat summary only; no archived report |
| B: Lightweight closure | Short archive note with objective, files, and evidence |
| C: Structured closure | Full E001 template with decisions, risks, follow-up, and promotion check |

The comparison should focus on non-trivial tasks. Tiny typo fixes are not good
subjects because closure overhead can dominate the signal.

## Candidate Task Types

Use tasks similar enough that comparison is fair:

- documentation architecture updates;
- new agentic workflow templates;
- support-tool changes;
- fixture-generation workflow changes;
- focused GUI or viewer behavior adjustments;
- narrow contract-test additions.

Avoid initially:

- large solver semantic changes;
- emergency CI repairs;
- highly exploratory research without deliverable;
- tasks that cannot be archived for confidentiality reasons.

## Measurements

### Resumption Test

Ask a future agent or reviewer to resume the task from the archive alone.

Measurements:

- time to state task objective;
- time to list changed files and why;
- number of missing-context questions;
- correctness of reconstructed decisions;
- ability to identify next follow-up.

Success signal:

```text
Structured closure should reduce missing-context questions and improve
decision reconstruction.
```

### Review Test

Ask an independent reviewer to evaluate the task.

Measurements:

- time to review readiness;
- number of unclear scope questions;
- number of evidence-gap findings;
- number of hidden-risk findings;
- reviewer confidence rating.

Success signal:

```text
Structured closure should make review findings more substantive and less about
basic reconstruction.
```

### Learning Test

Track whether reusable lessons become durable artifacts.

Measurements:

- number of repeated mistakes;
- number of experience records created;
- number of candidate skill/template/eval updates proposed;
- number of promotions accepted after review.

Success signal:

```text
Structured closure should increase useful promotion without polluting the
archive.
```

### Maintenance Test

After a delay, revisit archived tasks.

Measurements:

- can the archive still explain the task without chat history;
- are links still valid;
- did follow-up items become actionable;
- did the report prevent repeated discovery.

Success signal:

```text
Useful reports should age well. Weak reports should decay into ambiguity.
```

## Study Protocol

1. Select 9-15 comparable completed tasks.
2. Assign or classify them into conditions A, B, and C.
3. For each task, hide chat history from the reviewer when possible.
4. Ask the reviewer to reconstruct:
   - objective;
   - changed state;
   - evidence;
   - key decisions;
   - residual risks;
   - follow-up.
5. Score using `03-closure-quality-rubric.md`.
6. Record time, questions, errors, and confidence.
7. Compare patterns by condition.

## Data Capture Template

```yaml
task_id:
condition: A | B | C
reviewer:
archive_path:
chat_hidden: true
time_to_objective_minutes:
time_to_changed_state_minutes:
missing_context_questions:
incorrect_reconstructions:
evidence_gap_findings:
risk_gap_findings:
rubric_score:
reviewer_confidence_1_to_5:
promotion_candidate: true | false
notes:
```

## Expected Failure Modes In The Experiment

### Closure Overhead Dominates

For small tasks, structured reports may cost more than they save. This should
not invalidate E001; it should refine the threshold for "non-trivial."

Mitigation:

- define a lightweight closure path;
- reserve full reports for tasks with future retrieval value.

### Reports Become Formulaic

Agents may fill headings without real evidence.

Mitigation:

- score with the rubric;
- penalize vague evidence and decision sections;
- add evals for hollow reports.

### Archive Becomes Too Large

If every task is archived at full depth, future retrieval may suffer.

Mitigation:

- index aggressively;
- require concise reports;
- separate task archives from generalized experiences;
- prune or summarize low-value material if needed.

### Reviewers Prefer Chat Context

Reviewers may want to inspect the chat anyway.

Mitigation:

- allow chat as secondary evidence;
- still measure whether the archive alone is sufficient for baseline
  reconstruction.

## Tooling Opportunities

The experiment can inform deterministic tools:

- `validate-completed-task-report`: checks required headings and index link.
- `score-closure-report`: produces a first-pass rubric scaffold for reviewer
  completion.
- `new-completed-task-report`: creates a report from the E001 template.
- `detect-closure-gap`: checks whether changed docs lack archive handoff.
- `suggest-experience-promotion`: reads task reports and proposes candidate
  experience records.

The first three commands are now implemented in
`tools/agentic_design/agentic_toolkit.py`. They should not replace judgment.
They catch missing structure so humans and agents can spend attention on
meaning.

## Minimal Pilot

A useful first pilot for GCS:

1. Take three recent completed-task archives.
2. Score each with the closure rubric.
3. Ask one fresh agent session to reconstruct each task from archive only.
4. Record missing-context questions.
5. Improve the template based on the most common gaps.

This is small enough to run without creating a research project around the
research project. A pleasant little recursion, kept on a short leash.

## Core Insight

E001 should be judged by retrieval quality. The question is not whether the
report looks professional on the day it is written. The question is whether it
lets future work recover intent, evidence, risk, and learning with less
cognitive friction.
