# Pipeline Docs Index Lite

Run: `CACHE_HIT_EXPERIMENT_RUN docs-index-1-lite docs-index-1 Lite`

Scope: compact index of `docs/architecture/20-solver-pipeline/`.

## File List

| File | Focus |
| --- | --- |
| `docs/architecture/20-solver-pipeline/decomposition-planning.md` | Decomposition planner purpose, structural layers, `CoverPlan` output, cover rules, rigidity principles, and planner boundaries. |
| `docs/architecture/20-solver-pipeline/numerical-solving.md` | Numeric task contract, engine responsibilities, current dense C++ baseline behavior, report metrics, manifold updates, and proposal-only acceptance. |
| `docs/architecture/20-solver-pipeline/pipeline.md` | End-to-end pipeline stages, stage contracts, failure model, local-to-global rule, transaction rule, and observability rule. |

## Key Themes

1. Pipeline work is staged and report-bearing: intake through report has explicit inputs and outputs, and failures should preserve the most specific status plus responsible stage.
2. Decomposition provides local-to-global semantics through context covers, overlap contexts, boundary projections, gauge policy, solve order, and fallback strategy.
3. Numeric solving is intentionally proposal-only: it solves prepared local tasks, emits `NumericReport` evidence, and leaves gluing, verification, command semantics, and commits to later pipeline/runtime stages.
4. Boundary discipline is central: planners do not evaluate residuals or mutate coordinates, numeric engines do not own graph decomposition or IO, and session/runtime logic commits only verified proposals.
5. Replayability and diagnostics are first-class: stage reports, iteration traces, rank/DOF evidence, residual metrics, and serialized inputs/configuration are expected to support deterministic tests and debugging.

## Stale-Link Or Uncertainty Notes

- No Markdown links were present in the inspected files, so no stale-link candidates were found in this Lite pass.
- The phrase "Current C++23 baseline" in `numerical-solving.md` may drift as implementation evolves; this index records it as architecture-doc content, not as freshly verified source-code behavior.
- The docs name target contracts such as `CoverPlan`, `GluingReport`, and `NumericReport`; this Lite pass did not inspect implementation locations or schemas.

## Command Evidence

Smallest file-set inspection evidence:

```powershell
PS> rg --files docs\architecture\20-solver-pipeline
docs\architecture\20-solver-pipeline\decomposition-planning.md
docs\architecture\20-solver-pipeline\numerical-solving.md
docs\architecture\20-solver-pipeline\pipeline.md
```
