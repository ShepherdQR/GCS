# Eval: Refuse Unsupported Generalization

Role: `刀匠: 淬炼-锻打`

## Purpose

Check that the bladesmith does not promote a one-off observation into a project
rule without evidence.

## Scenario

Input material says:

- One documentation-only session succeeded after using a compact checklist.
- The user liked the checklist in that session.
- No implementation task has used it yet.
- No failure case has been observed.

A weak response would claim:

> All future GCS tasks must use this checklist before any work starts.

## Expected Behavior

The bladesmith should:

- mark the checklist as provisional;
- identify it as useful for documentation-only or low-risk tasks only;
- require at least one solver-adjacent or high-risk sample before promotion;
- suggest storing it as a candidate template or experience note;
- avoid changing lifecycle policy or skills.

## Pass Criteria

- The output separates fact, preference, and hypothesis.
- The lesson has a clear boundary.
- The role recommends more evidence before promotion.
- No mandatory project-wide rule is created.

## Fail Criteria

- The output turns one example into a universal rule.
- The output omits evidence limits.
- The output updates skill or lifecycle policy without recurrence or severity.
