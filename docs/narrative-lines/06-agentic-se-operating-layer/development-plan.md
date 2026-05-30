# 06 — Agentic-SE Operating Layer

Status: active
Date: 2026-05-30
Parent map: `docs/architecture/95-gcs-narrative-map.md`

## Current Level

**Very strong (5.0)**

## Current State

Task cards, runbooks, archives, quality gates, PR audit, institutional agents,
and an operating map exist. The agentic organization has documented workflows
for the full task lifecycle.

## Main Gap

The next risk is process sprawl rather than absence. As more agents, skills,
and gates are added, the operating layer could become complex enough to deter
use.

## Evidence Artifact

Task cards, completed archives, operating map, governance roadmap, and
exercised governance evidence note.

## Promotion Gate

Convert only the highest-signal exercised eval into a validator candidate.
(At very strong, the gate is about proving the layer works, not adding more.)

## Next Move

Keep `docs/agentic/agentic-organization-operating-map.md` as the compact entry
point.

## Development Plan

### Ongoing

1. Before adding any new agent, skill, gate, or workflow step, check whether
   it earns its place in the operating map. If not, defer.
2. Keep the operating map under 200 lines; push detail to linked docs.
3. After each non-trivial task closure, update the metrics dashboard.

### Short-term (next 2-4 weeks)

4. Audit the current operating layer for unused or underused artifacts
   (skills never invoked, agents with zero examples, gates never exercised).
   Archive or remove dead weight.
5. Ensure every active skill has a clear invocation trigger in CLAUDE.md.

### Medium-term (4-8 weeks)

6. Run a "fresh clone" exercise: from a clean checkout, follow the lifecycle
   runbook to close one non-trivial task. Record every friction point.
7. Simplify the runbook based on friction findings.

## Dependencies

- Quality gates (07): the operating layer defines how gates are exercised.
- Institutional agents (09): agents are governed by the operating layer.
- Git/worktree governance (10): session hygiene is enforced by the operating
  layer.

## Related

- Arc 3: Agentic Organization
- `docs/agentic/agentic-organization-operating-map.md`
- `docs/agentic/lifecycle-runbook.md`
- `docs/agentic/metrics-dashboard.md`
