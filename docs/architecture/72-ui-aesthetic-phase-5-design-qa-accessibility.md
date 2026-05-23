# UI Aesthetic Phase 5: Design QA And Accessibility

## Goal

Codify visual quality gates so future GUI work preserves the quiet technical
atelier direction.

This phase adds documentation and lightweight checks. It should not require a
display server or external visual tooling to provide useful feedback.

## Core States

Design QA covers these states:

- empty model;
- loaded small fixture such as `triangle_003.json`;
- model with multiple rigid sets and constraints;
- history replay active;
- solve success;
- solve warning or violation;
- narrow desktop window.

Manual screenshot review remains useful, but automated checks should catch
basic regressions before manual review.

## Accessibility Rules

- text must use theme tokens with adequate contrast;
- status color cannot be the only meaning carrier;
- command labels must remain readable without emoji/glyph support;
- table headings and row heights must remain legible at default font size;
- model name and DOF status must be visible without scrolling.

## Lightweight Automated Checks

Add a non-GUI validation script that can run in CI-like environments:

- parse key GUI modules;
- validate theme tokens exist and are valid hex colors;
- validate required renderer focus keys are documented;
- validate architecture docs for Phases 3-5 exist;
- optionally render with Matplotlib when the dependency is installed, but skip
  gracefully when it is unavailable.

The script should report actionable failures and avoid writing generated assets
by default.

Initial implementation path:

- `tools/ui_qa/gcs_ui_qa.py`;
- `tests/tools/test_gcs_ui_qa.py`;
- `fixtures/scene/ui_qa/mixed_geometry_constraints.json`.

## Manual Review Checklist

The design QA document should include a checklist for reviewers:

- viewport background is warm and calm;
- constraints remain inspectable;
- active replay object is clearly visible;
- inspector summary is visible;
- solve/replay summaries are not hidden in logs;
- narrow layout does not overlap text;
- no in-app explanatory marketing copy is added.

## Non-Goals

- no pixel-perfect screenshot baseline yet;
- no new GUI dependency;
- no browser conversion;
- no automated OS screenshot requirement.

## Acceptance Checks

- design QA doc exists and names core UI states;
- lightweight validation script runs without a display;
- validation script exits successfully on the current tree;
- failures are specific enough for future contributors;
- no generated screenshots are committed unless explicitly requested.
