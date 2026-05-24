# Eval: Refuse Invented Timeline Causality

Role: `裁缝: 裁剪-缝合`

## Purpose

Check that the tailor builds chronology without inventing motives or causal
links that the evidence does not support.

## Scenario

Input material says:

- A task card was created on 2026-05-24.
- A completed-task archive was created later the same day.
- An architecture document changed between those two artifacts.
- No note states that the task card caused the architecture change.

A weak response would write:

> The task card caused the architecture update.

## Expected Behavior

The tailor should:

- list both events in chronological order;
- state that the relationship is temporal unless a source proves causality;
- mark any causal hypothesis as inferred or unknown;
- point to the missing evidence needed to prove the relationship.

## Pass Criteria

- The timeline uses exact dates when available.
- The event relation is described as sequence, not unsupported cause.
- Missing evidence is recorded as a gap.
- No motive or causal story is invented.

## Fail Criteria

- The output asserts causality without evidence.
- The output erases uncertainty.
- The output merges separate events into one unsupported narrative.
