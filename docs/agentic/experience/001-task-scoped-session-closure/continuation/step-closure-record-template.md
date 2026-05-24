# Step Closure Record Template

Use this template whenever an E001 continuation research step is completed.
The record can live inside the phase roadmap for small steps or as a separate
file under a future `continuation/records/` folder for larger steps.

```yaml
---
step_id: phase-N-step-M
phase: N
step: M
status: completed
branch_before_commit: "<branch name>"
commit_hash: "<hash after commit>"
artifact_paths:
  - docs/agentic/experience/001-task-scoped-session-closure/continuation/<artifact>.md
next_step: phase-N-step-M-plus-1
---
```

## Step Objective

What single step was supposed to become true?

## Artifact Produced

- `path/to/artifact`: what it now contains and why it matters.

## Summary

Summarize the completed step in a few sentences. The summary should make the
step understandable without reading the full chat.

## State Transition

Record the state movement:

```text
ready -> in_progress -> artifact_ready -> summarized -> phase_updated -> committed -> next_declared
```

If the step was blocked or superseded, record the alternate transition.

## Phase Update

What did this step change about the remaining steps in the current phase?

- Step removed:
- Step added:
- Step reordered:
- Risk changed:
- Scope changed:

If nothing changed, explicitly say that the remaining phase plan still holds.

## Commit Boundary Check

- Current branch before commit:
- Staged files inspected:
- Unrelated staged files excluded:
- Commit command used exact paths:
- Commit hash:

## Evidence

```text
<command or observation>
<result summary>
```

For documentation-only research steps, evidence can be the artifact path,
staged path list, commit result, and any validation command that applies.

## Residual Risk

- What remains uncertain?
- What should the next step avoid assuming?
- Is a later validator, eval, or skill update implied?

## Next-Step Declaration

Next step:

```text
<phase-step id and artifact target>
```

Immediate first action:

```text
<one concrete action>
```

## Template Guardrails

- Do not paste raw chat logs.
- Do not describe future work as completed work.
- Do not commit without inspecting the current branch and staged paths.
- Do not leave the next step implicit.
- Do not let the template become theater; every filled section must either
  transfer state or explain risk.

## Step 1.3 Summary

This template translates the phase-step state machine into a reusable closure
record. It forces each step to preserve objective, artifact, state transition,
phase update, commit boundary, evidence, residual risk, and next-step
declaration.

## Update To Remaining Phase 1 Steps

Only Phase 1 Step 1.4 remains. It should summarize Phase 1, decide whether the
roadmap, state machine, and template are enough to open Phase 2, and replan the
steps in Phase 2 based on what Phase 1 learned.
