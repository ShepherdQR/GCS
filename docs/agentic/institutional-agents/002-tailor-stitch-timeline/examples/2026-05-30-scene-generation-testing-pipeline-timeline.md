# Timeline Entry: 2026-05-30 Scene Generation & Solver Testing Pipeline

Scope: scene generation, solver testing, defect discovery, mutation testing

Updated: 2026-05-30

Maintainer role: `Tailor: Cut-Stitch Timeline`

## Timeline

| Date | Event | Evidence | Consequence | Open Thread | Confidence |
| --- | --- | --- | --- | --- | --- |
| 2026-05-30 | Phase 1: Exhaustive constraint-graph enumerator created. | Commit `be78fe9`; `tools/scene_generation/gcs_scene_generation/enumerator.py` — enumerate_scene_space() producing JSON enumerations with deterministic hash-based IDs | GCS now has a tool to enumerate all structurally-distinct constraint graphs for fixed parameter sets (num_geometries, num_constraints, num_rigid_sets). | Only structural isomorphism is checked; geometric parameter assignment remains to be added per graph. | high |
| 2026-05-30 | Phase 2: Solver testing tools created — constraint value mutator, batch solver runner, defect store. | Commit `3d241b0`; `tools/solver_testing/mutator.py` (8 mutation strategies: positive_to_negative, zero_offset, double, halve, sign_flip, unit_magnitude, add_noise, swap_axes); `tools/solver_testing/runner.py` (batch GCS.exe invocation with timeout); `tools/solver_testing/defect_store.py` (JSON-file defect persistence) | Solver behavior can now be systematically tested via constraint value mutation. Defects are persisted with full metadata (scene, mutation, solver output, severity). | Defect store uses flat JSON files — may need migration to structured DB at scale. | high |
| 2026-05-30 | Phase 3: Defect analyzer with auto-fix pipeline created. | Commit `5f04fd4`; `tools/solver_testing/analyzer.py` — classify_defect() with severity levels (wrong_result, crash, timeout, silent_mismatch), auto_fix() for mathematically unambiguous cases, fix_priority scoring | Defect triage is now partially automated. Auto-fix covers mathematically unambiguous cases; complex solver failures remain manual. | Auto-fix scope is narrow — most real solver defects will need manual investigation. | high |
| 2026-05-30 | Phase 4: End-to-end pipeline run. 2RS/5G/5C found graph-theoretically impossible. 3RS/5G/5C enumerated 200 graphs. 5 defects discovered via mutation testing. | Commit `61d6364`; `tools/scene_generation/.store/enumerations/defect_discovery_3rs_5g_5c/result.json` (200 graphs); `tools/solver_testing/.defects/pipeline_summary_defect_discovery_3rs_5g_5c.json`; `tools/solver_testing/pipeline.py` | First end-to-end automated scene-generation-to-defect-discovery pipeline completed. Key finding: bipartite constraint graphs (e.g., 2RS/5G/5C) cannot form biconnected graphs with odd cycles, making them structurally incompatible with GCS's biconnectivity requirements. | 80% original solve failure rate on generated 3RS/5G/5C graphs needs root-cause investigation. All 5 defects need manual developer triage. | high |
| 2026-05-30 | Defect discovery task card created with evidence bundle, residual risks, and human gate. | `docs/agentic/tasks/2026-05-30-defect-discovery-3rs-5g-5c-20260530.md` — scope: tool, risk: medium, owning_agent: gcs-cpp-solver-maintainer, human_gate_required: true | Defect findings are now in the task-card system for developer follow-up. Human gate required because defects need manual investigation of solver behavior with mutated constraint values. | Push deferred due to proxy issues. | high |

## Decision Threads

| Thread | Started | Current state | Evidence |
| --- | --- | --- | --- |
| 2RS/5G/5C parameter space viability | 2026-05-30 | closed — graph-theoretically impossible; bipartite K(2,3) minus one edge always has an articulation point | Enumerator output: 0 valid graphs for 2RS/5G/5C |
| 3RS/5G/5C as replacement parameter space | 2026-05-30 | active — 200 graphs enumerated, but 80% original solve failure rate | `tools/scene_generation/.store/enumerations/defect_discovery_3rs_5g_5c/result.json` |
| Scene inconsistency vs. solver limitation for high failure rate | 2026-05-30 | open — root cause not diagnosed | 8 of 10 tested graphs failed original solve; need investigation of generated scene consistency |
| Negative distance constraint handling | 2026-05-30 | open — solver produces generic failure for negative distances | 5 defects all from positive_to_negative Distance mutations; solver should produce specific error codes |
| Defect store scaling | 2026-05-30 | open — flat JSON works for <100 defects | `tools/solver_testing/defect_store.py`; may need SQLite migration |

## Key Findings

### Graph-Theoretic Impossibility: 2RS/5G/5C

The constraint graph between 2 rigid sets and 5 geometries via 5 constraints is a bipartite graph K(2,3) minus one edge. Bipartite graphs cannot contain odd cycles, and a graph without odd cycles must have articulation points (cut vertices) when it has the edge density required for biconnectivity. Since GCS's decomposition planner requires biconnected components, 2RS/5G/5C produces zero valid constraint graphs.

This finding is **confirmed** by enumerator output and graph theory. The parameter space should either be excluded from target catalogs or relaxed to require connectivity-only instead of biconnectivity.

### High Original Solve Failure Rate (80%)

Of 10 tested 3RS/5G/5C graphs, 8 failed original (unmutated) solve. This suggests either:
- Generated scene geometry is mathematically inconsistent (over-constrained or contradictory)
- Solver configuration or tolerance defaults are inappropriate for small generated scenes
- The enumerator produces structurally valid but semantically invalid constraint combinations

Root cause investigation is the highest-priority follow-up.

### 5 Defects via positive_to_negative Mutation

All 5 defects are Distance constraints with values mutated from positive to negative. The solver returns generic failure rather than a specific "invalid constraint value" error. Adding input validation for negative distances would catch this class of defect before solver execution.

## Gaps

| Gap | Impact | Repair action |
| --- | --- | --- |
| 80% original solve failure rate not diagnosed. | Generated scenes may be systematically invalid, undermining future enumeration value. | Reproduce failures with verbose solver output; check geometry consistency, constraint feasibility, and solver configuration. |
| 5 defects need manual developer investigation. | Defects represent real solver behavior issues but root cause (solver logic vs. input validation) is not determined. | Investigate each defect in `tools/solver_testing/.defects/` — check solver output, add input validation where appropriate. |
| Geometric parameter assignment is not automated. | Enumerator produces structural graphs only; geometry parameters (positions, orientations) must be assigned separately. | Add geometry parameter assignment to the enumeration pipeline for end-to-end scene generation. |
| Enumerator budget (200 graphs) may miss edge cases. | The parameter space may contain rarer structural patterns not captured in the first 200 graphs. | Increase max_graphs budget or add stratified sampling across graph isomorphism classes. |
| Push deferred due to proxy issues. | All 4 commits are local-only on `master`. | Push when proxy is available. |

## Handoffs

| Finding | Handoff |
| --- | --- |
| 2RS/5G/5C impossibility is a reusable graph-theoretic lesson. | `gcs-scene-generation-engineer` — document in parameter-space design guide. |
| Mutation testing pipeline (8 strategies, batch runner, defect store) is a reusable testing infrastructure. | `gcs-quality-steward` — consider integrating into quality gate suite for regression testing. |
| Negative distance constraint handling needs solver input validation. | `gcs-cpp-solver-maintainer` — add specific error codes for invalid constraint values. |
| 80% failure rate needs root cause analysis. | `gcs-constraint-semantics-steward` — check whether generated constraint combinations are semantically valid. |
| Enumerator tool is general-purpose for any parameter set. | `gcs-scene-generation-engineer` — promote to scene-generation toolkit after geometry parameter assignment is added. |
