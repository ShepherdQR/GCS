# E002 Research Roadmap

Research roadmap date: 2026-05-24.

## Purpose

This roadmap turns E002, Phase-Step Summary-Update-Commit-Continue, from a
promoted experience into an executable agentic operating discipline.

E002 extends E001. E001 closes a whole task session. E002 closes the inner
steps and phases of long-running work, so a task can survive context loss,
review pauses, handoff, and changing evidence.

## Roadmap Overview

| Phase | Name | Goal | Primary Artifacts | Status |
| --- | --- | --- | --- | --- |
| 1 | Theory formalization | Define the formal model, state machine, invariants, boundaries, and failure taxonomy. | `research/02-phase-step-formal-model.md` | complete |
| 2 | Templates and protocol | Make the model directly usable through durable step, phase, and status templates. | `templates/*.md` | complete |
| 3 | Tooling | Add minimal generator, validator, and resume-query support to `agentic_toolkit.py`. | `tools/agentic_design/agentic_toolkit.py`, tests | complete |
| 4 | Empirical validation | Test whether E002 improves resumption, reviewability, commit hygiene, and plan adaptation. | Pilot report and eval rubric | remaining |
| 5 | Promotion and gates | Decide whether E002 should become a project skill, task-card field, completed-task scorer dimension, or CI-quality gate. | Skill or gate proposal | remaining |

## Current Remaining Plan

Phases 4 and 5 are the active remaining plan.

- Phase 4 should run empirical pilots before any new mandatory gate is added.
- Phase 5 should only promote E002 into skills, task-card fields, scorer
  dimensions, reviewer checklists, or CI/toolkit gates after Phase 4 evidence
  shows the process overhead is justified.

## Phase 1: Theory Formalization

Goal: make E002 precise enough that different agents apply the same rule.

Questions:

- What exactly is a phase?
- What exactly is a step?
- Which transitions are allowed between planned, ready, in-progress,
  summarized, updated, committed, and next-declared states?
- Where does E001 end and E002 begin?
- Which failure modes does E002 prevent?
- Which invariants must never be weakened for convenience?

Planned steps:

1. Define phase, step, summary, update, commit, and continue.
2. Define phase and step state machines.
3. Define E001/E002 boundary rules.
4. Define failure taxonomy and countermeasures.
5. Summarize implications for later templates and tooling.

Completion test:

- A future agent can read the formal model and determine whether a task should
  use E002.
- The model names required state transitions and failure modes.
- Later templates and tooling can quote the model without reinterpreting it.

## Phase 2: Templates And Protocol

Goal: make E002 usable by agents without requiring them to reconstruct the
theory.

Planned steps:

1. Strengthen the phase-step plan template.
2. Add a step closure record template.
3. Add a phase summary template.
4. Add a current-status template for resumable handoff.
5. Cross-link templates from the E002 README.

Completion test:

- A long task can keep phase, step, evidence, update, commit, and next-step
  state in durable Markdown artifacts.
- A fresh agent can resume from the current-status template without chat
  history.
- The templates distinguish completed work from future work.

## Phase 3: Tooling

Goal: make the first E002 workflow layer executable.

Candidate commands:

- `new-phase-step-plan`: create a phase-step plan skeleton.
- `validate-phase-step-plan`: check required sections and placeholders.
- `show-next-step`: print the next-step declaration from a current status or
  phase-step plan.

Initial scope:

- Standard-library Python only.
- Markdown structure checks, not semantic judgment.
- No solver runtime dependency.
- No CI requirement until the commands have been used in real work.

Completion test:

- The toolkit can generate a usable E002 plan skeleton.
- The validator accepts real E002 artifacts and rejects obvious placeholders.
- Unit tests cover generator, validator, and next-step extraction behavior.

## Phase 4: Empirical Validation

Goal: measure whether E002 is worth its overhead.

Pilot questions:

- Does E002 reduce time-to-resume for a later agent?
- Does it reduce giant diffs and unclear commit boundaries?
- Does it make completed-task reports easier to write?
- Does it produce meaningful plan updates instead of ritual summaries?
- Does it help reviewers find skipped checks and residual risk?

Candidate measures:

- Resume latency: minutes from fresh context to correct next action.
- Boundary quality: changed files per step commit and unrelated-file leakage.
- Evidence quality: count and specificity of commands, artifacts, or reports.
- Plan adaptation: number of explicit step updates that change, add, defer, or
  confirm remaining work.
- Reviewer load: number of questions needed before acceptance.

Completion test:

- At least two substantial tasks have used E002.
- A pilot report compares E002 against an ordinary plan-only baseline or a
  historical completed task.
- The report recommends whether to promote, revise, or keep E002 as optional.

## Phase 5: Promotion And Gates

Goal: decide how much institutional weight E002 should carry.

Promotion options:

- Candidate project skill for long-horizon continuation.
- Optional `phase_step_plan` field in task cards.
- Completed-task scorer dimension for intermediate step closure.
- Reviewer checklist item for high-risk or multi-phase work.
- CI or toolkit gate for E002 artifacts, if the format stabilizes.

Completion test:

- Promotion decision names the target: skill, template, tool, eval, gate, or
  no further promotion.
- Any new gate is justified by empirical evidence and does not punish small
  one-step tasks.
- Module-agent guidance explains when to use E002 and when E001 alone is
  enough.

## Phase 1 Summary

Phase 1 produced `research/02-phase-step-formal-model.md`. The model defines
E001/E002 boundaries, phase and step state machines, transition rules, failure
taxonomy, and tooling implications. This confirms that Phase 2 templates should
carry explicit frontmatter and sections for phase id, step id, evidence,
summary, phase update, commit boundary, and next-step declaration.

## Phase 2 Summary

Phase 2 strengthened `templates/phase-step-plan-template.md` and added three
protocol artifacts:

- `templates/step-closure-record-template.md`
- `templates/phase-summary-template.md`
- `templates/current-status-template.md`

The templates encode Phase 1's model into durable Markdown records with
frontmatter, evidence sections, update sections, commit-boundary sections, and
next-step declarations.

## Phase 3 Summary

Phase 3 added the first executable E002 tooling layer:

- `new-phase-step-plan` creates a phase-step plan skeleton.
- `validate-phase-step-plan` checks E002 phase-step, step-closure,
  phase-summary, and current-status records.
- `show-next-step` extracts the next-step declaration for resumable handoff.

The validator is intentionally structural. It checks frontmatter, required
headings, placeholder removal, and next-step presence, but it does not judge
semantic plan quality.

## Step 0 Summary

This roadmap defines the five-stage E002 research and implementation path. The
next immediate step is Phase 1: formalize E002 into a state machine, boundary
model, invariants, and failure taxonomy.

## Update To Remaining Work

The initial five phases remain valid. Phase 4 should now run empirical pilots
before any CI gate or mandatory skill promotion is introduced.
