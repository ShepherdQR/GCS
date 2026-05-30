# 03 — Implementation Roadmap

Status: active
Date: 2026-05-30
Parent map: `docs/architecture/95-gcs-narrative-map.md`

## Current Level

**Strong (4.0)**

## Current State

Step history and upcoming solver work are recorded in depth. Step execution
reports document completed work with evidence bundles.

## Main Gap

New readers need a compressed view of roadmap arcs. The detailed step history
is thorough but not easy to browse from a high level.

## Evidence Artifact

Step execution reports and the narrative map itself.

## Promotion Gate

Add a compressed roadmap arc when the next solver milestone closes.

## Next Move

Maintain the narrative map as the one-page entry point and keep details in the
step-level roadmap.

## Development Plan

### Short-term (next 2-4 weeks)

1. After the next solver milestone closes (any step that changes
   solver/diagnostic behavior), add a compressed "arc summary" paragraph to
   this plan and update the narrative map.
2. Ensure each completed step has a clear trace from step number → commit →
   task card → completed-task archive.

### Medium-term (4-8 weeks)

3. Produce a one-page "solver roadmap at a glance" that lists completed steps,
   each with one sentence of outcome ("Step 52: end-to-end defect discovery
   pipeline operational").
4. Identify the next 3-5 planned solver steps and add brief scope notes.

### Long-term (8+ weeks)

5. When the solver reaches a natural phase boundary (e.g., all planned
   diagnostic phases complete), produce a roadmap retrospective that
   summarizes the arc from step 1 to that point.

## Dependencies

- Solver evidence (01): solver milestones produce the evidence that roadmap
  arcs summarize.
- Module contracts (02): contract alignment is a constraint on roadmap execution.

## Related

- Arc 1: Solver Evidence
- `docs/architecture/20-solver-pipeline/`
- `docs/completed-tasks/`
