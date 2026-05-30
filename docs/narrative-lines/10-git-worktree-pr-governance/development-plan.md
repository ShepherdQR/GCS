# 10 — Git/Worktree/PR Governance

Status: active
Date: 2026-05-30
Parent map: `docs/architecture/95-gcs-narrative-map.md`

## Current Level

**Strong (4.0)**

## Current State

Worktree, branch, PR audit, permissions, threat matrix, repository-audit
policies, and exercised governance eval evidence exist. Scoped staging,
safe push payloads, and preservation of unrelated dirty files are enforced
by convention and documented policy.

## Main Gap

E-GOV-001 is ready for validator-candidate design, but no validator is
implemented yet. Governance evals are prompt-level only; no automated check
exists.

## Evidence Artifact

Permission policy, threat matrix, PR audit docs, scoped commits, and
`docs/agentic/evals/governance/exercised-evidence-20260526.md`.

## Promotion Gate

Build E-GOV-001 validator candidate with false-positive notes.

## Next Move

Convert E-GOV-001 into a scoped validator candidate.

## Development Plan

### Short-term (next 2-4 weeks)

1. Build E-GOV-001 validator candidate:
   - Python tool at `tools/governance/check_staged_scope.py`.
   - Compares `git diff --cached --name-only` against task-card affected paths.
   - Returns PASS (all staged files in scope), FAIL (staged file outside scope
     with no allowlist entry), or SKIP (no task card found).
   - Document false-positive cases.
   - Add a test that verifies detection of unrelated dirty-file staging.
2. Run the validator on the last 5 commits to calibrate false-positive rate.

### Medium-term (4-8 weeks)

3. Design E-GOV-002 (refuse audit approval overclaim) as the next validator
   candidate, based on exercised evidence from the eval corpus.
4. Add a "governance health" field to the metrics dashboard: which validators
   are active, what is their pass/fail rate.

### Long-term (8+ weeks)

5. When E-GOV-001 has run clean for 10+ sessions, consider promoting it from
   L3 (advisory) to L2 (default gate with opt-out).
6. Build a pre-push hook that runs all active governance validators.

## Dependencies

- Agentic-SE operating layer (06): governance is a subsystem of the operating
  layer.
- Quality gates (07): governance validators are a quality gate category.

## Related

- Arc 3: Agentic Organization
- `docs/agentic/permission-threat-matrix.md`
- `docs/agentic/evals/governance/`
- `docs/agentic/ai-governance-execution-plan-2026-05-26.md`
