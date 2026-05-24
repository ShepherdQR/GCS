# E002 Formal Model

Research phase: 1, theory formalization.

## Purpose

This note defines E002 precisely enough for agents, templates, and tools to
apply it consistently.

E002 is the phase-step continuation discipline for long agentic work. It does
not replace E001 task-scoped closure. It provides the inner transactional loop
for work that cannot be safely completed as one uninterrupted session.

## Core Definitions

| Term | Definition | Required Artifact |
| --- | --- | --- |
| Task | The user-facing unit of accountable work. | Task card, completed-task report, or explicit no-archive reason. |
| Phase | A bounded hypothesis about a coherent part of the task. | Phase plan and phase summary. |
| Step | The smallest reviewable work unit inside a phase. | Step declaration, evidence, summary, update, commit note, next-step declaration. |
| Summary | Durable account of what changed, what was learned, and what remains uncertain. | Step or phase summary section. |
| Update | Explicit revision or confirmation of the remaining plan after evidence arrives. | Current phase update or downstream phase update. |
| Commit | Repository boundary that records the step's changed files when state permits. | Commit hash or reason no commit was made. |
| Continue | The next executable handoff point. | Next-step declaration with target artifact and first action. |

## E001 And E002 Boundary

E001 answers: "When is this whole task session closed?"

E002 answers: "How does a long task make safe progress before final closure?"

Use E001 alone when:

- the task has one small artifact;
- the plan will not meaningfully change after intermediate evidence;
- the work can be verified and summarized in one closure report.

Use E001 plus E002 when:

- there are multiple phases or several reviewable artifacts;
- later work depends on what an earlier step discovers;
- a future agent may need to resume from the middle;
- commit boundaries matter for review or rollback;
- the task touches agentic process, architecture planning, generated assets, or
  multi-module implementation.

## Phase State Machine

```text
planned
  -> open
  -> replanning
  -> complete
  -> promoted | deferred
```

| State | Meaning | Exit Criteria |
| --- | --- | --- |
| `planned` | Phase goal, scope, and first steps are known. | First step is ready to start. |
| `open` | At least one step is ready or in progress. | A completed step forces an update, or all required steps are done. |
| `replanning` | Evidence changed the phase shape. | Remaining steps are revised, confirmed, deferred, or superseded. |
| `complete` | Required phase outputs exist and are summarized. | Downstream phases have been replanned. |
| `promoted` | The phase result updated a durable project mechanism. | Promotion artifact exists. |
| `deferred` | The phase remains useful but is intentionally paused. | Deferral reason and resume condition are recorded. |

Invalid transitions:

- `planned -> complete` without step evidence.
- `open -> complete` without phase summary.
- `complete -> next phase` without downstream replanning.
- `replanning -> open` without recording what changed.

## Step State Machine

```text
declared
  -> in_progress
  -> artifact_ready
  -> verified
  -> summarized
  -> phase_updated
  -> committed
  -> next_declared
```

Alternative terminal states:

```text
blocked | superseded | deferred
```

| State | Meaning | Exit Criteria |
| --- | --- | --- |
| `declared` | The step goal, artifact, and first action are known. | Work starts in the named scope. |
| `in_progress` | The agent is producing the step artifact. | Artifact exists or blocker is found. |
| `artifact_ready` | The promised artifact exists. | Minimal useful verification is run or explicitly skipped. |
| `verified` | Evidence has been collected. | Summary records result and risk. |
| `summarized` | The step has a durable account. | Current phase plan is updated. |
| `phase_updated` | Remaining phase steps are revised or confirmed. | Step boundary can be committed or marked uncommitted with reason. |
| `committed` | Commit hash or no-commit reason is recorded. | Next step is declared. |
| `next_declared` | A fresh agent can resume. | Step closure is complete. |
| `blocked` | Work cannot continue safely. | Blocker and needed decision are recorded. |
| `superseded` | Step is no longer the right work. | Replacement step and reason are recorded. |
| `deferred` | Step remains valid but is intentionally postponed. | Resume condition is recorded. |

## Transition Rules

### Declaration

A step may be declared only when it names:

- phase id;
- step id;
- target artifact;
- first action;
- out-of-scope boundary;
- expected verification.

### Verification

Verification can be:

- a command;
- a diff check;
- a generated report;
- a rendered artifact inspection;
- a reasoned skip note for documentation-only steps.

The verification must be small enough to match the step.

### Summary

A step summary must answer:

- What changed?
- What was learned?
- What remains uncertain?
- What risk or skipped check remains?

It fails E002 if it merely says "done" or repeats the step title.

### Update

After every step, the remaining phase plan must be updated by one of:

- confirm: keep the plan as written and say why;
- change: revise the next step or later step;
- add: introduce a missing step revealed by evidence;
- defer: postpone a step with a resume condition;
- supersede: replace a step that no longer fits.

### Commit

The commit boundary must record:

- branch at commit time;
- staged files or exact path scope;
- commit hash or no-commit reason;
- whether unrelated dirty files existed.

A commit does not replace the summary. A summary explains intent; a commit
records state.

### Continue

A next-step declaration must include:

- next step id;
- target artifact;
- purpose;
- first action;
- blockers or gates.

If there is no next step because the phase is complete, the phase summary must
name the next phase or state that downstream work is deferred.

## Failure Taxonomy

| Failure | Symptom | Countermeasure |
| --- | --- | --- |
| Stale phase plan | Later work follows assumptions contradicted by evidence. | Mandatory update after each step. |
| Giant diff | Many unrelated artifacts land in one commit. | Step-sized artifacts and path-scoped commits. |
| Fake summary | Summary repeats the title without insight. | Summary must state changed state, learning, uncertainty, and risk. |
| Commit theater | Commit exists but no rationale or next action survives. | Commit plus durable summary and next-step declaration. |
| Uncommitted boundary | Artifact exists but no commit or no-commit reason is recorded. | Commit boundary section. |
| Handoff fog | Fresh agent cannot identify current phase or next action. | Current-status artifact and next-step declaration. |
| Infinite replanning | Agent keeps revising plans without artifacts. | Each step must produce an artifact, blocker, or supersession. |
| Over-ceremony | Tiny edit spends more effort on process than substance. | Use E001 alone for one-step low-risk tasks. |

## Tooling Implications

The first E002 tooling layer should check structure, not semantics.

Useful machine checks:

- required headings exist;
- frontmatter identifies `record_type`, `phase_id`, `step_id`, and status;
- placeholder text is gone before validation passes;
- current status contains a next-step declaration;
- step closure contains summary, phase update, and commit boundary sections.

Not useful yet:

- judging whether a plan update is wise;
- forcing every task to use E002;
- making CI fail for optional research notes before the format stabilizes.

## Phase 1 Summary

Phase 1 formalized E002 as a nested transaction model. It defined the E001/E002
boundary, phase and step state machines, transition rules, failure taxonomy,
and tooling implications.

## Update To Remaining Phases

Phase 2 should now encode the model into templates with explicit frontmatter
and required sections. Phase 3 should implement only minimal structural
tooling: generator, validator, and next-step extraction.
