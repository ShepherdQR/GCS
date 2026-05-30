# 07 — Quality Gates and Evidence

Status: active
Date: 2026-05-30
Parent map: `docs/architecture/95-gcs-narrative-map.md`

## Current Level

**Strong (4.0)**

## Current State

Local validators, contract tests, tool tests, fixture gates, and quality
scripts exist. The agentic toolkit provides validation commands for task
cards, completed-task reports, and architecture docs.

## Main Gap

Trend visibility is still thin. Individual gate results are not yet
aggregated into a visible quality trend over time.

## Evidence Artifact

Agentic toolkit validators and R1 package smoke.

## Promotion Gate

Add trend history after several non-trivial closures.

## Next Move

Maintain `docs/agentic/metrics-dashboard.md` after non-trivial tasks.

## Development Plan

### Short-term (next 2-4 weeks)

1. After each non-trivial task closure, update the metrics dashboard with
   the quality gate results (validation passed/failed, lint clean/dirty,
   test pass/fail).
2. Add a lightweight "quality checkpoint" step to the task-scoped session
   closer that runs applicable validators and records results.

### Medium-term (4-8 weeks)

3. Build a trend view: collect the last N closure quality results and
   render a compact trend (pass rate, common failure categories).
4. Add a pre-commit quality script that runs the minimum viable checks
   (task card validation if a task card is staged, Python compile check
   if Python files are staged).

### Long-term (8+ weeks)

5. Integrate quality trend into the narrative map refresh cycle: when the
   narrative map is reviewed, the quality trend is reviewed alongside it.
6. Add a "quality regression" alert: if a previously passing gate starts
   failing, flag it in the metrics dashboard.

## Dependencies

- Agentic-SE operating layer (06): task closure rhythm drives quality data.
- Fixture corpus (04): fixture gates are a quality gate category.
- Git/worktree governance (10): scoped staging is a quality gate.

## Related

- Arc 2: Evidence Workbench (quality gates produce evidence)
- Arc 3: Agentic Organization (quality gates enforce discipline)
- `docs/agentic/metrics-dashboard.md`
- `tools/agentic_design/agentic_toolkit.py`
