# Session Transaction Theory

## Purpose

This note deepens E001 from a useful workflow into a first-principles theory of
agentic-SE sessions. The practical rule is simple: a non-trivial session must
have a task objective, multi-turn execution, a task execution report, and an
archive handoff. The deeper claim is stronger:

```text
An agentic-SE session is a bounded transaction over project state.
```

The transaction begins when human intent is accepted as a task objective. It
ends only when the project has a durable account of the resulting state,
evidence, risks, and learned memory.

## First Principles

### Software Engineering Is State Change Under Accountability

Software engineering changes a shared state: source files, docs, tests,
fixtures, architecture, expectations, and team knowledge. A change is
engineering rather than mere activity when it is accountable: a reviewer can
ask what changed, why it changed, how it was checked, and what remains risky.

Agentic software engineering adds a new hazard. Much of the reasoning happens
inside an interactive conversation. If that reasoning is not externalized, the
project receives changed files but loses the decision path that made those
changes meaningful.

### A Session Must Have Conservation Laws

A good agentic session conserves four things:

- intent: the final work still corresponds to the task objective;
- scope: expansion is explicit rather than accidental;
- evidence: claims are backed by checks, diffs, or named limitations;
- memory: durable lessons move from chat into repository artifacts.

When these conservation laws break, the session may still feel productive, but
it becomes hard to review, resume, or improve.

### Closure Is A Semantic Commit

Version control commits persist file changes. Session closure persists task
meaning. The execution report is therefore not bureaucracy; it is the semantic
commit message for the whole agentic interaction.

In a mature workflow, "done" should mean:

```text
the project state changed, and the meaning of that change is now inspectable.
```

## Transaction Model

```text
open
  -> bind objective
  -> establish scope and evidence contract
  -> execute bounded interaction
  -> collect changed state and observed evidence
  -> reconcile against objective
  -> write closure report
  -> archive or intentionally discard
  -> promote reusable lessons
closed
```

### Open State

The session is open while the task objective, scope, or evidence remains
unsettled. Exploration is allowed, but the agent should not pretend the work is
ready for durable acceptance.

Open-state questions:

- What is the task trying to make true?
- What project state may change?
- What evidence would make completion credible?
- What would count as scope drift?

### Bound State

The session becomes bound when it has a working objective and a plausible
verification path. The objective can still be refined, but refinements should
be visible.

Bound-state obligations:

- keep actions tied to the objective;
- announce material scope changes;
- distinguish investigation from implementation;
- preserve user decisions that alter the task contract.

### Closing State

The session enters closing state when the work is functionally done but not yet
archived. This is the most commonly missed phase. An agent often wants to stop
here because the visible edit is complete. E001 says the task is still open.

Closing-state obligations:

- summarize the work;
- list changed paths and artifacts;
- list commands and evidence;
- name skipped checks;
- name residual risks;
- decide whether the result belongs in completed-task archive, experience
  archive, both, or neither.

### Closed State

The session is closed when the report is durable enough for a future reviewer
or agent to resume without reading the conversation. A closed session can still
have follow-up work. Follow-up is not a closure failure if it is explicitly
separated from the completed objective.

## Cognitive Stack

The session transaction can be understood at five cognitive levels.

| Level | Question | Artifact |
| --- | --- | --- |
| Intent | What should become true? | Task objective or task card |
| Control | How do we keep work on course? | Updates, plan, user feedback |
| Evidence | How do we know what happened? | Commands, diffs, checks |
| Memory | What should future work remember? | Execution report, archive |
| Evolution | What should the system learn? | Experience, skill, eval, tool |

Deep agentic-SE work requires all five. A session that edits files but lacks
memory is shallow. A session that writes a beautiful report but lacks evidence
is decorative. A session that learns a lesson but never promotes it is wasted
cognition.

## Formal Contract

Let a session be:

```text
S = <I, C, A, E, R, M>
```

Where:

- `I` is intent: the human objective and acceptance condition.
- `C` is context: files, docs, skills, constraints, and prior state read by the
  agent.
- `A` is action: edits, commands, analysis, and decisions made during the
  session.
- `E` is evidence: command results, review findings, generated artifacts, and
  named skipped checks.
- `R` is residual risk: what remains uncertain or intentionally deferred.
- `M` is memory: archived report and any promoted experience.

A session is well closed when:

```text
I is explicit
A is scoped by I
E supports the completion claim
R is visible
M can be found without chat history
```

This compact definition gives the project a way to reason about closure
quality independent of any specific tool or model.

## Core Insight

The highest-level lesson is not "write reports." The lesson is:

```text
Agentic work becomes engineering memory only when interaction is converted
into evidence-bearing, archived state.
```

That conversion is the essence of session closure.

## Research Questions

- How small can the closure artifact be while still preserving accountability?
- Which session types need full reports, and which need only final summaries?
- Can an agent detect when it is about to close without enough evidence?
- Can closure quality predict future maintainability or review cost?
- What parts of closure can be validated mechanically without making the
  workflow heavy?

## Engineering Implications

- Task cards define the opening contract.
- Execution reports define the closing contract.
- Completed-task archives preserve task memory.
- Experience folders preserve generalized process memory.
- Validators and evals should target closure failures, not only code failures.
