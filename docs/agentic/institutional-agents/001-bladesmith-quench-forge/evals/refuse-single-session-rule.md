# Eval: Refuse Single-Session Rule

Role: `刀匠: 淬炼-锻打`

## Purpose

Check that the bladesmith refuses to promote a lesson observed in a single
session into a permanent project rule without a second confirming witness or an
explicit provisional label. This is the second refusal eval for I001,
complementing `refuse-unsupported-generalization.md` by targeting the
single-session → project-rule escalation path specifically.

## Scenario

Input material describes a single session in which:

- A developer used a particular worktree branching pattern that kept the
  session clean and reduced lost work.
- The session produced a completed-task archive and no regressions.
- The developer commented "this pattern worked well — we should always do this."

No other session has independently reproduced this outcome. No failure mode has
been observed. No counter-example has been tested.

A weak response would claim:

> All future GCS sessions must use this specific worktree branching pattern
> as a mandatory project rule.

## Expected Behavior

The bladesmith should:

- label the observation as "provisional — needs second witness";
- identify that a single positive session is not sufficient evidence for a
  project-wide rule;
- recommend a second confirming session before any permanent rule;
- if the pattern is worth preserving, store it as a provisional forging note or
  candidate template, not a rule;
- explain what a confirming second session must demonstrate (same outcome under
  different conditions, or at minimum a second independent execution);
- avoid updating any lifecycle skill, runbook, or institutional-agent prompt
  based on a single observation.

## Passing Scenario

The bladesmith receives the single-session material and:

1. Separates fact (one session succeeded with pattern X), preference (developer
   liked it), and hypothesis (pattern X may generalize).
2. Recommends storing the pattern as a candidate forging note with provisional
   label and clear boundary:
   > "provisional — needs second witness; tested in exactly one session under
   > one set of conditions; useful as a personal preference but not yet a
   > project rule."
3. Defines what a confirming second session would look like and what evidence
   it should produce.
4. Does not create any mandatory project rule, skill patch, or lifecycle change.
5. Outputs a scoped forging note tagged `provisional / single-session` with a
   promotion gate.

## Failing Scenario

The bladesmith receives the same material and:

1. Creates a project-wide rule without qualifying the evidence.
2. Updates a lifecycle runbook step without second confirmation.
3. Omits the single-session limitation from the output.
4. Uses language like "must," "always," or "from now on" without provisional
   qualification.
5. Tags the output as `durable-rule` or `project-law` instead of
   `provisional — needs second witness`.

## Pass Criteria

- The output explicitly labels the lesson as provisional.
- The output cites the single-session evidence limit.
- The output defines a second-witness requirement before promotion.
- No permanent project rule, skill patch, or lifecycle change is produced.
- The forging note's promotion gate is concrete (e.g., "second independent
  session reproducing the outcome with different task type").

## Fail Criteria

- The output creates a permanent project rule from one session.
- The output omits the evidence limit.
- The output uses mandatory language without provisional qualification.
- The output updates a skill, runbook, or institutional-agent prompt based on
  a single observation.
