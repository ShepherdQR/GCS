# Pipeline Defect Register

Known issues discovered during pipeline experiments, not yet fixed.

Convention: each entry has a unique ID, source experiment, severity, and status.
Severity: `P0` (crash/block), `P1` (wrong result), `P2` (usability), `P3` (cosmetic).

---

## Open

| ID | Source | Sev | Title | Status |
|----|--------|-----|-------|--------|
| PD-001 | [001](001-10-pipeline-parallel-smoke/README.md) | P2 | defect-discovery smoke preset enumerates 0 graphs | open |
| PD-002 | [001](001-10-pipeline-parallel-smoke/README.md) | P2 | contract-compliance: aliased imports flagged as violations | open |
| PD-003 | [001](001-10-pipeline-parallel-smoke/README.md) | P2 | contract-compliance: relative imports (empty string) flagged | open |
| PD-004 | [001](001-10-pipeline-parallel-smoke/README.md) | P2 | contract-compliance: cross-module internal deps not in allowed graph | open |
| PD-005 | [002](002-10-pipeline-post-fix-smoke/README.md) | P2 | cross-solver-compare requires external solver spec bootstrap | open |
| PD-006 | [002](002-10-pipeline-post-fix-smoke/README.md) | P2 | benchmark report: solved count is 0 because it counts exit=0 only; accepted-with-warnings scenes are misclassified as failed | open |

## Closed

| ID | Source | Sev | Title | Fixed in |
|----|--------|-----|-------|----------|
| PD-001-R1 | 001 | P0 | 5 pipelines crash on missing required args (default_config gap) | `7b55b95` |
| PD-002-R1 | 001 | P0 | scene_gen: CoverageSpec.rigid_sets AttributeError | `7b55b95` |
| PD-003-R1 | 001 | P1 | diagnostic-cert: 2/6 false negatives (alternate codes gap) | `7b55b95` |
| PD-004-R1 | 001 | P1 | contract-compliance: 656 false positives (stdlib whitelist gap) | `7b55b95` |
| PD-005-R1 | 001 | P2 | repo-audit: AuditReport missing summary() | `7b55b95` |
| PD-006-R1 | 001 | P2 | run.py dispatch IDs mismatch registry keys | `7b55b95` |
| PD-007-R2 | 002 | P1 | baseline.json pollutes solver-regression fixture corpus | `5f65d18` |
| PD-008-R2 | 002 | P1 | baseline.json pollutes performance-benchmark corpus | `5f65d18` |
| PD-009-R2 | 002 | P2 | StabilityResult missing summary() | `5f65d18` |
| PD-010-R2 | 002 | P2 | SceneGenReport missing summary() | `5f65d18` |
