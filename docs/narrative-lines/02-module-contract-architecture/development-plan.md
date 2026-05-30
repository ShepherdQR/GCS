# 02 — Module Contract Architecture

Status: active
Date: 2026-05-30
Parent map: `docs/architecture/95-gcs-narrative-map.md`

## Current Level

**Very strong (5.0)**

## Current State

Target modules, dependency direction, and contract-test posture are explicit.
Module design docs and `docs/architecture/30-contracts/` define clear
boundaries.

## Main Gap

Prototype names and detailed implementation may still lag target vocabulary.
New implementation code does not always map back to target contracts explicitly.

## Evidence Artifact

`docs/architecture/30-contracts/` and module design docs.

## Promotion Gate

Keep new implementation changes mapped to target contracts and report surfaces.
(At very strong, the gate is maintenance rather than promotion.)

## Next Move

Keep every new change mapped to target module, report surface, and contract
evidence.

## Development Plan

### Ongoing

1. Before merging any C++ change that introduces a new class, function, or
   module, verify its name aligns with the target vocabulary in
   `docs/architecture/30-contracts/`.
2. If a contract doc is outdated by an implementation change, update the
   contract doc in the same commit or an immediately following commit.
3. Run contract tests (`docs/architecture/63-target-contract-interface-implementation-test-design.md`)
   when module boundaries shift.

### Short-term (next 2-4 weeks)

4. Audit current implementation names against target vocabulary; list any
   drift that has accumulated.
5. Add a contract-to-implementation traceability note for the
   kernel and numeric modules, which are the highest-risk for drift.

### Medium-term (4-8 weeks)

6. Extend traceability notes to IO, graph, and viewer-bridge modules.
7. Consider a compact "module boundary inventory" script that lists every
   file against its target module.

## Dependencies

- Implementation roadmap (03): roadmap execution drives implementation
  changes that must stay aligned with contracts.
- Quality gates (07): contract tests are the enforcement mechanism.

## Related

- Arc 1: Solver Evidence
- `docs/architecture/30-contracts/`
- `docs/architecture/62-module-agents.md`
