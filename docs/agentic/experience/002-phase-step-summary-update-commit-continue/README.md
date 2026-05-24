---
experience_id: E002-phase-step-summary-update-commit-continue
source: project-practice
status: promoted
root_cause: ambiguous_task
affected_modules:
  - agentic_lifecycle
promotion_target: lifecycle_runbook
---

# E002: Phase-Step Summary-Update-Commit-Continue

Chinese alias: "阶段-步骤-总结-更新-提交-继续".

## Thesis

Long-horizon agentic work should be controlled as nested transactions:

```text
task objective
  -> phase plan
  -> step plan
  -> step execution
  -> step summary
  -> update remaining steps in the current phase
  -> scoped commit
  -> next step declaration
  -> phase summary
  -> downstream phase replanning
```

A phase is a temporary hypothesis about how the task should be decomposed. A
step is the smallest reviewable artifact that can produce evidence, summary,
and a commit. The plan is expected to change, but only through explicit update
points.

## Problem

Large agent sessions fail less often because the first plan is wrong and more
often because the plan is not revisited after evidence arrives. Common failure
modes include:

- stale plans that keep executing after a step changes the problem;
- long diffs that have no intermediate review boundary;
- hidden context drift across many turns;
- useful discoveries that remain only in chat;
- later agents that cannot tell which step was completed, verified, or
  committed;
- phase transitions that happen by momentum instead of decision.

E001 closes the overall session as a bounded task transaction. E002 adds the
inner loop needed when a task is too large to finish safely in one undivided
execution burst.

## Practice

Use E002 for work that has more than one meaningful artifact, more than one
phase, or any significant chance that step evidence should change the next
move.

Required moves after each step:

1. Write or update the promised step artifact.
2. Summarize what changed, what was learned, and what remains uncertain.
3. Recheck the remaining steps in the current phase.
4. Update the current phase plan, even if the update is "no change".
5. Verify the step at the smallest useful evidence level.
6. Create a path-scoped commit for the step when repository state permits.
7. Declare the next step with its target artifact and first action.

Required moves after each phase:

1. Summarize the phase result.
2. State what the phase invalidated or changed in the old plan.
3. Replan downstream phases and their first steps.
4. Decide whether the phase output should update a skill, template, tool, eval,
   or lifecycle rule.

## Operating Invariants

- Every phase has a goal, scope boundary, expected artifacts, and completion
  test.
- Every step has one primary artifact or one recorded blocker.
- Step summaries are durable and do not rely on chat history.
- Remaining steps are re-evaluated after each step.
- Commits are scoped to the step and avoid unrelated dirty worktree changes.
- The next step is declared before stopping or switching context.
- A phase cannot close until downstream phases are replanned.
- A commit is evidence of a boundary, not a substitute for a summary.

## Pattern Fit

E002 is a compound operating pattern. It combines:

- plan-and-solve decomposition for multi-step reasoning;
- prompt chaining with explicit gates between steps;
- ReAct-style grounding through tool results and environment evidence;
- evaluator-optimizer discipline when a reviewer or rubric critiques each
  step;
- Reflexion-style durable memory when summaries are carried forward;
- worktree, branch, and commit governance for reviewable state changes.

## When To Use

Use E002 for:

- architecture roadmaps and research programs;
- multi-module solver or IO changes;
- documentation sets that create several linked artifacts;
- generated fixture or figure campaigns;
- long GUI and behavior-polish work;
- any task where a future agent may need to resume mid-stream.

Do not use the full E002 ceremony for tiny single-file edits where E001 closure
is enough. The ceremony should buy reviewability, not create paperwork.

## Materials

- Roadmap: `research/phase-step-research-roadmap.md`
- Research report: `research/01-session-agent-patterns-report.md`
- Formal model: `research/02-phase-step-formal-model.md`
- Phase-step template: `templates/phase-step-plan-template.md`
- Step closure template: `templates/step-closure-record-template.md`
- Phase summary template: `templates/phase-summary-template.md`
- Current status template: `templates/current-status-template.md`
- Agent role card: `agents/phase-step-continuation-agent.md`

## Validation And Future Gates

Near-term validation can be manual:

- Does every step have a summary and a current phase update?
- Can a future agent resume from the next-step declaration without chat
  history?
- Does each commit contain only the step boundary it claims?
- Did the phase close with downstream replanning?

Future hardening could add:

- a `phase_step_plan` section to agentic task cards;
- a validator for phase-step records under `docs/agentic/experience/` or
  `docs/agentic/tasks/`;
- a completed-task scorer dimension for intermediate step closure;
- a skill promotion that teaches module agents when to use E002.
