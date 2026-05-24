# Closure Quality Rubric

## Purpose

This rubric turns E001 into an evaluable practice. It scores whether a
non-trivial agentic-SE session has been closed well enough for review,
resumption, and future learning.

The rubric is not meant to reward long reports. It rewards cognitive
compression: the smallest durable artifact that preserves objective, evidence,
decisions, risks, and memory.

## Scoring Model

Score each dimension from 0 to 4.

| Score | Meaning |
| --- | --- |
| 0 | Missing or misleading |
| 1 | Present but too vague to trust |
| 2 | Usable with reviewer reconstruction |
| 3 | Clear and reviewable |
| 4 | Excellent; reusable as a model example |

Recommended interpretation:

| Total | Interpretation |
| --- | --- |
| 0-13 | Not closed |
| 14-21 | Weak closure; needs repair before archive |
| 22-29 | Acceptable closure |
| 30-35 | Strong closure |
| 36-40 | Exemplary closure; candidate training example |

## Dimension 1: Objective Clarity

Question:

```text
Can a reviewer state the task goal in one sentence?
```

Score guide:

- 0: no objective is stated.
- 1: objective is implied but ambiguous.
- 2: objective exists but mixes several goals.
- 3: objective is clear and bounded.
- 4: objective is clear, bounded, and tied to acceptance evidence.

Top cognition:

The objective is the session's north star and its legal contract. Without it,
the report cannot prove the work is relevant.

## Dimension 2: Scope Discipline

Question:

```text
Are in-scope work and non-goals visible?
```

Score guide:

- 0: scope is absent and changed files appear arbitrary.
- 1: scope is loosely implied.
- 2: scope is stated but non-goals or boundaries are weak.
- 3: scope and non-goals are clear.
- 4: scope is clear, non-goals are explicit, and adjacent discoveries are
  separated into follow-up.

Top cognition:

Scope is a trust boundary. It protects reviewers from hidden work and protects
future agents from inheriting accidental precedent.

## Dimension 3: Evidence Completeness

Question:

```text
Does the report show what was checked and what the checks mean?
```

Score guide:

- 0: no evidence is recorded.
- 1: evidence is claimed but not named.
- 2: commands or checks are listed without useful interpretation.
- 3: commands/checks are listed with pass/fail summaries.
- 4: evidence is complete for the task risk, with failures and skipped checks
  interpreted honestly.

Top cognition:

Evidence is not the log. Evidence is the interpreted relation between observed
tool output and the completion claim.

## Dimension 4: Changed-State Traceability

Question:

```text
Can a maintainer map changed files or artifacts to task reasons?
```

Score guide:

- 0: changed paths are missing.
- 1: some files are mentioned without reason.
- 2: major files are listed but minor artifacts are unclear.
- 3: changed files and artifacts are listed with reasons.
- 4: changed-state summary makes ownership, purpose, and future use obvious.

Top cognition:

The project does not only need to know that a file changed. It needs to know
why this task had authority to change that file.

## Dimension 5: Decision Traceability

Question:

```text
Are important choices preserved without requiring chat replay?
```

Score guide:

- 0: decisions are absent.
- 1: decisions are hinted at but not named.
- 2: decisions are named but rationale is weak.
- 3: key decisions and rationale are recorded.
- 4: decisions are recorded at the right abstraction level and linked to
  future consequences.

Top cognition:

The best report compresses reasoning. It does not paste the conversation; it
extracts the decisions that future work must respect.

## Dimension 6: Risk Visibility

Question:

```text
Can a reviewer see what remains uncertain?
```

Score guide:

- 0: risks are hidden or falsely denied.
- 1: vague caveats exist.
- 2: some risks or skipped checks are named.
- 3: skipped checks, reasons, and residual risks are clear.
- 4: risks are prioritized and connected to follow-up or review focus.

Top cognition:

Risk visibility is not pessimism. It is how the project avoids mistaking
unfinished evidence for finished truth.

## Dimension 7: Archive Usefulness

Question:

```text
Can a future agent find and use the report?
```

Score guide:

- 0: no archive exists when one is needed.
- 1: archive exists but is hard to find.
- 2: archive is findable but noisy or incomplete.
- 3: archive is indexed and concise.
- 4: archive is indexed, concise, and connected to related tasks,
  experiences, templates, or skills.

Top cognition:

Memory is operational only when retrieval is cheap. A hidden or noisy archive
does not function as project memory.

## Dimension 8: Learning Promotion

Question:

```text
Does the session identify whether a reusable lesson should be promoted?
```

Score guide:

- 0: reusable lesson is ignored.
- 1: lesson is vaguely mentioned.
- 2: lesson is captured but no promotion path is named.
- 3: promotion target is named: experience, skill, eval, template, fixture, or
  tool.
- 4: promotion target includes validation criteria or future gate.

Top cognition:

Agentic-SE improves when the environment changes after experience. A lesson
that never modifies memory, templates, evals, or tools remains private
intuition.

## Dimension 9: Follow-Up Separation

Question:

```text
Is future work separated from completed work?
```

Score guide:

- 0: incomplete work is described as done.
- 1: follow-up is vague or mixed into completion.
- 2: follow-up exists but lacks owner, trigger, or reason.
- 3: follow-up is clearly separated from completed work.
- 4: follow-up is prioritized and tied to risk, validation, or promotion.

Top cognition:

Good closure does not require everything to be finished. It requires honest
separation between what became true and what should happen next.

## Dimension 10: Concision And Signal

Question:

```text
Is the report short enough to read and rich enough to trust?
```

Score guide:

- 0: absent or unreadable.
- 1: too terse or too noisy.
- 2: usable but padded, repetitive, or missing compression.
- 3: concise and high-signal.
- 4: elegant compression; every section earns its space.

Top cognition:

The target is not maximal documentation. The target is minimal sufficient
memory.

## Review Procedure

1. Read the task objective.
2. Read the changed-file list or diff summary.
3. Read the evidence section.
4. Score dimensions 1-10.
5. Mark any dimension scored 0 or 1 as a repair candidate.
6. If total score is below 22, do not treat the task as cleanly archived.
7. If score is 36 or higher, consider using the report as a positive example.

## Machine-Checkable Signals

Some rubric elements can become validators:

- required headings exist;
- archive path matches folder convention;
- evidence section includes at least one command or explicit skipped-check
  note;
- changed files are listed;
- report contains no raw transcript marker;
- completed-task index links to archive;
- experience links point to existing paths.

Other elements require human or agent judgment:

- whether the objective is truly bounded;
- whether evidence matches risk;
- whether decisions are compressed at the right abstraction level;
- whether risks are honest.

## Core Insight

Closure quality is the quality of state transfer from agent conversation to
project memory. The rubric scores that transfer.
