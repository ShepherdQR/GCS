# Contracts Index Full

Run: `docs-index-1-full`  
Task pair: `docs-index-1`  
Lane: Full  
Date: 2026-05-31  
Controller task card:
`docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md`

## Scope

This artifact indexes `docs/architecture/30-contracts/` for the cache-hit
diagnosis pilot. It is an index and audit aid, not a rewrite of the underlying
contracts.

## Stewardship Context

- `gcs-architecture-steward` was invoked because the target path is an
  architecture contract directory.
- `gcs-kernel-contract-steward` was consulted as relevant context because the
  indexed files cover stable IDs, immutable snapshots, context snapshots,
  tolerances, and state-version semantics.
- The architecture map identifies `30-contracts` as the contract layer for
  `domain-contracts.md` and `solver-contracts.md`.
- The architecture README describes this directory as the fourth stage in the
  target reading order, after foundations, system topology, and solver
  pipeline docs.

## File List

| File | Role | Main sections |
|---|---|---|
| `docs/architecture/30-contracts/domain-contracts.md` | Durable domain model, identity, serialization, and model boundary contract. | Stable Identity; Core Types; Context And Boundary Identity; Model Immutability Boundary; Constraint Semantics; Rigid Set Incidence; Serialization Contract |
| `docs/architecture/30-contracts/solver-contracts.md` | Planner, diagnostics, numeric engine, gluing, runtime, and boundary contracts. | Planner Contract; Diagnostic Contract; Numeric Engine Contract; Gluing Contract; Runtime Contract; Boundary Contract |

## Key Themes

1. Stable identity is the domain anchor.
   Entity, constraint, rigid-set, command, state-version, report, context, and
   cover IDs are durable. Coordinates may change, but IDs should only change
   under explicit topology edits.

2. Solves operate on immutable snapshots and return proposals.
   Durable model state is treated as immutable during a solve. Planner and
   numeric layers produce plans, proposed deltas or states, and reports; the
   runtime owns commit or rollback.

3. Local-to-global decomposition is represented through explicit context and
   boundary contracts.
   `ContextSnapshot`, `CoverPlan`, overlap contexts, boundary projections,
   local sections, gluing reports, and obstruction reports preserve identity
   across local views rather than cloning domain truth.

4. Diagnostics and reports must preserve structured evidence.
   Rank evidence, residual evidence, conflict sets, redundancy sets, gluing
   status, obstruction reports, and viewer-facing projections are typed report
   surfaces. Viewer and reporting tools should consume public projections
   rather than parsing free-form messages or numeric-engine internals.

5. IO and viewer layers are boundary adapters, not owners of solver truth.
   Scene serialization must round-trip stable IDs and deterministic output.
   JSON `behavior` maps to solver intent, scene `history` remains replay
   metadata, and IO/visualization must use public runtime or report APIs.

## Stale-Link And Uncertainty Notes

- No inline Markdown links were found in the two files under
  `docs/architecture/30-contracts/`, so this run did not identify broken local
  links inside the indexed files.
- This index summarizes target architecture contracts only. It does not prove
  current C++ or Python implementation compliance with those contracts.
- Several statements are intentionally target-facing, using `should` and
  `must`; implementation status should be checked through module-specific
  contract tests or implementation audits before treating them as complete.
- `domain-contracts.md` notes that C++ scene IO currently tolerates JSON
  `history` while Python viewer tooling owns history reconstruction. That is a
  deliberate boundary note and remains an area to watch for future migration.

## Command Evidence

```powershell
Get-Content -Path .codex\skills\gcs-architecture-steward\SKILL.md
```

Result: architecture stewardship loaded; workflow says to use
`docs/architecture/` as the source of truth and check dependency direction and
contract boundaries.

```powershell
Get-Content -Path docs\agentic\tasks\2026-05-31-cache-hit-pilot-eight-pairs.md
```

Result: controller task card read; this run is governed by the existing pilot
task card and should not create a new card unless scope expands.

```powershell
Get-Content -Path docs\research\20260530\cache-hit-diagnosis-experiment\README.md
Get-Content -Path docs\research\20260530\cache-hit-diagnosis-experiment\pilot-runbook-8-pairs.md
```

Result: Full-lane rules and the `docs-index-1-full` acceptance gate were read;
artifact path and no-CSV guardrail confirmed.

```powershell
Get-Content -Path .codex\skills\gcs-architecture-steward\references\architecture-map.md
Get-Content -Path docs\architecture\README.md
Get-Content -Path docs\architecture\30-contracts\domain-contracts.md
Get-Content -Path docs\architecture\30-contracts\solver-contracts.md
```

Result: architecture map, repository architecture README, and both contract
files were inspected for source context.

```powershell
rg -n "^#|\]\(|TODO|TBD|uncertain|future|must|should|not" docs\architecture\30-contracts
```

Result: headings and obligation-bearing statements were reviewed; no Markdown
links were reported inside the two contract files.

```powershell
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-31-cache-hit-pilot-eight-pairs.md
```

Result: `[OK] task-card: docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md passed`.

```powershell
git status --short
```

Result: Git emitted warnings about `C:\Users\QR/.config/git/ignore`
permission, but no pre-existing tracked changes were listed before this
artifact was created.

## Validation

- Task card validation passed.
- The requested artifact was created under the required pilot artifact
  directory.
- `experiment-runs.csv` was not appended by this run.

## Residual Risk

- This is a low-risk documentation index, but its correctness depends on the
  two contract files remaining the authoritative contents of
  `docs/architecture/30-contracts/`.
- Because the run intentionally did not audit implementation modules, stale
  implementation-vs-contract drift may still exist outside this artifact.
- Git status had a user-level ignore-file permission warning; it did not block
  the scoped artifact work, but it could obscure future status checks if
  additional filesystem permission issues appear.
