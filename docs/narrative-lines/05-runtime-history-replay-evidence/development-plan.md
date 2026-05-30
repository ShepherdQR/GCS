# 05 — Runtime/History/Replay Evidence

Status: active
Date: 2026-05-30
Parent map: `docs/architecture/95-gcs-narrative-map.md`

## Current Level

**Strong (4.0)**

## Current State

Replay evidence, saved-report workflow, and D3 schema-aware checker are now
concrete differentiators. The D3 replay evidence package demonstrates
end-to-end replay.

## Main Gap

The checker is not yet wired into an R2 release gate. Replay evidence exists
but is not a required step in the release pipeline.

## Evidence Artifact

`docs/product/demos/d3-replay-evidence/`, replay JSON, and
`g1-replay-evidence.check.json`.

## Promotion Gate

Wire the replay checker into R2 release-readiness evidence.

## Next Move

Use replay evidence as the trust bridge between solver behavior and agentic
governance.

## Development Plan

### Short-term (next 2-4 weeks)

1. Wire the D3 schema-aware replay checker into the R2 release-readiness
   checklist as a required gate.
2. Document what the checker validates (schema conformance, history integrity,
   report field presence) and what it does not (semantic correctness of
   numeric values).
3. Add a negative test case: a malformed replay file that the checker must
   reject.

### Medium-term (4-8 weeks)

4. Extend replay evidence to cover multi-step sessions (solve → modify →
   re-solve → compare).
5. Add replay evidence to the D5 Solver Evidence Workbench package as a
   viewer-visible layer.

### Long-term (8+ weeks)

6. Build a replay diff tool: given two replay files for the same scene,
   highlight what changed and why (parameter change, constraint change,
   solver version change).

## Dependencies

- Solver evidence (01): replay is the evidence storage format.
- UI/viewer (08): viewer projection of replay history.
- Release/packaging (12): R2 release gate wiring.

## Related

- Arc 2: Evidence Workbench
- `docs/product/demos/d3-replay-evidence/`
- `docs/architecture/97-ui-viewer-figure-integration-plan.md`
