---
name: gcs-ui-design-steward
description: UI design convention governance for GCS. Invoke when planning, reviewing, or implementing GUI aesthetics, visual tokens, viewer layout, diagnostic overlays, figure taste, design-system naming, visual QA, accessibility, or any change that should comply with GCS Quiet Technical Atelier, GCS Warm Evidence Tokens, GCS Evidence-First Interface Grammar, GCS Scientific Figure Pipeline, or GCS Visual Integrity Gate.
---

# GCS UI Design Steward

## Required Reading

Read these in order:

1. `docs/architecture/75-ui-design-system-conventions.md`
2. `docs/architecture/76-ui-design-system-execution-plan.md`
3. `docs/architecture/72-ui-aesthetic-roadmap.md`
4. `docs/architecture/73-gcs-visual-taste-guide.md`
5. `docs/architecture/74-scientific-figure-production-paradigm.md` when dense
   figures or generated visual artifacts are involved.

## Operating Rule

Every UI or figure change must name its governing convention:

- **GCS Quiet Technical Atelier** for overall taste;
- **GCS Warm Evidence Tokens** for palette, typography, stroke, radius, and
  state tokens;
- **GCS Evidence-First Interface Grammar** for solver state and evidence
  semantics;
- **GCS Scientific Figure Pipeline** for dense project/research figures;
- **GCS Visual Integrity Gate** for QA checks;
- **GCS Art Director Review** for independent judgment.

If the change cannot name a convention, treat it as a prototype.

## Workflow

1. Classify the change: GUI surface, figure pipeline, visual token, QA gate,
   documentation, or review.
2. Identify the governing convention names.
3. Check existing phase and step in
   `docs/architecture/76-ui-design-system-execution-plan.md`.
4. Keep solver truth out of UI. Viewer code may observe snapshots, histories,
   reports, and overlays, but it must not become durable solver state.
5. Make the smallest coherent change.
6. Summarize the completed step, update the remaining steps if needed, run
   checks, and commit before starting the next step.

## Review Checklist

- Does color encode semantic evidence rather than decoration?
- Does text fit at target display size?
- Are dense figures produced from specs and layout-aware composition?
- Are diagnostics, rank, residual, gluing, obstruction, or quality evidence
  visible when solver credibility is the subject?
- Are generated artifacts rebuildable?
- Did the work update the execution plan when it changed future steps?

## Claude Code Integration

When invoked for UI design work:
- Use `Read` on the required reading list before proposing visual changes.
- Use `Grep` to verify that UI code does not mutate solver state directly.
- When making visual changes, use the `mcp__Claude_Preview__preview_*` tools
  to inspect rendered output and verify design conventions.
- Use the `mcp__Claude_Preview__preview_screenshot` tool to capture visual
  evidence of UI changes.
- Every UI change must name its governing convention in the commit or PR
  description.
- For figure work, also use `gcs-scientific-figure-producer`.
- Run visual QA checks before claiming completion.
