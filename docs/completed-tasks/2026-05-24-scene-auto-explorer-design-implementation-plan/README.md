---
task_id: 2026-05-24-scene-auto-explorer-design-implementation-plan
status: complete
session_goal: "Audit, redesign, implement, validate, push, and plan the next phase of the GCS scene auto explorer."
archive_target: docs/completed-tasks/2026-05-24-scene-auto-explorer-design-implementation-plan/
related_design:
  - docs/architecture/scene-generation-tools.md
  - docs/architecture/81-scene-generation-next-phase-plan.md
  - tools/scene_generation/tools.md
---

# Scene Auto Explorer Design, Implementation, And Next-Phase Plan

## Task Objective

Turn the existing `tools/scene_generation` prototype into a durable scene auto
exploration capability, then preserve the conversation outcome as project
memory. The work covered design audit, detailed architecture updates, local
explorer implementation, promotion-package behavior, tests, push status, and a
next-phase research/execution plan.

## Scope And Non-Goals

In scope:

- audit the current scene generation command set;
- decide what can be reused and what must be rewritten;
- update durable design docs;
- implement a complete local scene auto explorer;
- preserve old command compatibility;
- add tests and run validation;
- push the completed implementation when explicitly authorized;
- store next-phase plans in Markdown;
- archive this session under `docs/completed-tasks`.

Out of scope:

- moving generator policy into solver, runtime, GUI, viewer, or scene IO
  modules;
- default promotion into `fixtures/scene`;
- treating unsupported gates as promotion success;
- rewriting unrelated dirty files in the checkout;
- storing raw chat logs instead of distilled decisions and evidence.

## Interaction Summary

The session began with a request to analyze the current scene auto explorer and
confirm whether it had a complete design. The audit found that the old
`tools/scene_generation/tools.py` was useful as a command family, but not
complete as an auto explorer. It could generate skeletons, lift them to GCS,
assign parameters, validate schemas, project graphs, repair candidates, and
emit reports, but it lacked search state, coverage goals, candidate scoring,
rejection evidence, exploration traces, and promotion packages.

The first completed task was a design rewrite. The architecture document was
expanded into a detailed contract for scene auto exploration, including
structured requests/results, candidate provenance, coverage axes, validation
gates, failure taxonomy, storage layout, search strategy, repair policy,
promotion packages, migration plan, and acceptance tests. The implementation
notes in `tools/scene_generation/tools.md` were aligned with the new direction.

The user then requested a direct implementation. The implementation added
`explore_scene_space` and `promote_candidate`, kept the existing CLI surface
compatible, produced deterministic candidates and negative evidence, wrote
exploration traces and promotion packages, and added Python unittest coverage.
The implementation was validated locally and pushed after explicit user
approval.

Later status checks showed the scene generation tool had been split further
into `gcs_scene_generation/` package modules and had broadened public promotion
gate behavior. The user then asked for current plans and a next-stage research
and execution scheme. A dedicated next-phase plan was written in
`docs/architecture/81-scene-generation-next-phase-plan.md`, and this completed
task archive records the full session.

## Work Completed

- Audited the existing `tools/scene_generation` command family.
- Confirmed the old implementation was reusable but not a complete auto
  explorer.
- Updated `docs/architecture/scene-generation-tools.md` with the durable
  design and current implementation status.
- Updated `tools/scene_generation/tools.md` with implementation-side notes,
  command references, package split status, and tests.
- Implemented `explore_scene_space`.
- Implemented `promote_candidate`.
- Added structured exploration request/result handling.
- Added stable candidate IDs, seed paths, provenance bundles, and digests.
- Added coverage goals, deterministic scoring, stop reasons, and negative
  evidence.
- Added local validation gates and promotion-package gate behavior.
- Preserved old commands for manual generation, lift, parameter assignment,
  validation, projection, reporting, repair, serialization, list, and delete.
- Added and ran scene explorer unittest coverage.
- Pushed the implementation commit after explicit authorization.
- Wrote `docs/architecture/81-scene-generation-next-phase-plan.md`.
- Added this completed-task archive and linked it from the completed-task
  index.

## Files And Artifacts

Design and plan:

- `docs/architecture/scene-generation-tools.md`
- `docs/architecture/81-scene-generation-next-phase-plan.md`
- `tools/scene_generation/tools.md`

Implementation:

- `tools/scene_generation/tools.py`
- `tools/scene_generation/gcs_scene_generation/contracts.py`
- `tools/scene_generation/gcs_scene_generation/storage.py`
- `tools/scene_generation/gcs_scene_generation/topology.py`
- `tools/scene_generation/gcs_scene_generation/gcs_model.py`
- `tools/scene_generation/gcs_scene_generation/validation.py`
- `tools/scene_generation/gcs_scene_generation/projection.py`
- `tools/scene_generation/gcs_scene_generation/parameterization.py`
- `tools/scene_generation/gcs_scene_generation/reporting.py`
- `tools/scene_generation/gcs_scene_generation/repair.py`
- `tools/scene_generation/gcs_scene_generation/explorer.py`
- `tools/scene_generation/gcs_scene_generation/promotion.py`
- `tools/scene_generation/gcs_scene_generation/promotion_package.py`

Tests:

- `tests/tools/test_scene_generation_explorer.py`

Archive:

- `docs/completed-tasks/2026-05-24-scene-auto-explorer-design-implementation-plan/README.md`

## Evidence

Audit evidence:

```text
python tools\scene_generation\tools.py list
Passed and listed existing scratch graphs.

python tools\scene_generation\tools.py validate_gcs_schema --input "{\"gcs_graph_id\":\"codex_verify_0520b_gcs_repaired\"}"
Passed with "valid": true.

Manual generate/lift validation showed lifted graphs may fail before
assign_geometry_parameters, confirming the old chain was not self-contained.
After assign_geometry_parameters, schema validation, biconnectivity, report,
and serialization passed for the smoke candidate.
```

Implementation validation:

```text
python tools\scene_generation\tools.py --help
Passed and listed explore_scene_space and promote_candidate.

python -m unittest tests.tools.test_scene_generation_explorer
Initially passed 2 tests for the local v1 explorer.

python -m unittest tests.tools.test_scene_generation_explorer
Later status check passed 13 tests after package split and public gate
hardening.

python -c "import ast, pathlib; ast.parse(pathlib.Path('tools/scene_generation/tools.py').read_text(encoding='utf-8'))"
Passed.

git diff --check -- scene-generation related paths
Passed with CRLF normalization warnings only when warnings appeared.
```

Promotion evidence:

```text
promote_candidate with default promotion gate:
status = promotion_blocked when public gates were not fully satisfied.

promote_candidate with gate_profile local_only:
status = promotion_package_written.

Later package status documented public promotion smoke gates and structured
runtime/diagnostics/rank evidence behavior.
```

Push evidence:

```text
git push origin master
Everything up-to-date
```

## Relevant Commits

Key observed scene-generation commits:

- `d3e6700 docs: redesign scene generation explorer`
- `19a4f2d feat: add scene auto explorer`
- `db4117f feat: wire scene promotion public gates`
- `9202303 refactor: split scene generation support modules`
- `8edfdb1 refactor: split scene generation topology helpers`
- `aee9ecb refactor: split scene generation validation modules`
- `295a79f refactor: split scene generation parameterization`
- `3fa82bf refactor: split scene generation repair policy`
- `6d312fa refactor: split scene generation orchestration`
- `790b69d refactor: contain scene generation store access`
- `cc08a1e feat: prefer structured promotion gate evidence`
- `ef97e67 feat: gate promotion rank evidence`

## Decisions

- Decision: preserve existing CLI command compatibility.
  Rationale: existing generation, validation, projection, report, and repair
  workflows are useful for manual candidate construction and smoke checks.

- Decision: implement a complete local explorer before direct cross-module
  certification.
  Rationale: deterministic exploration, coverage, provenance, and negative
  evidence are prerequisites for durable promotion gates.

- Decision: separate exploration from fixture promotion.
  Rationale: scratch candidates should not become fixtures until promotion
  evidence passes.

- Decision: keep generator policy inside `tools/scene_generation`.
  Rationale: solver, runtime, diagnostics, IO, and viewer modules own domain
  truth and public reports; the generator should consume those reports, not
  duplicate their semantics.

- Decision: make unsupported or missing public evidence explicit.
  Rationale: promotion packages should block or skip with typed evidence
  rather than silently treating absent gates as success.

- Decision: store next-phase planning in architecture docs.
  Rationale: cross-module promotion certification is a durable design concern,
  not just a local implementation note.

## Current Status

The scene explorer is complete as a local v1 and has package-level tests. It
can explore, score, accept/reject, retain negative evidence, write traces, and
produce promotion packages.

It is not yet a fully certified cross-module fixture promotion system. Runtime
and diagnostics promotion gates can consume structured reports or use an
executable fallback, but the next phase should bind them to direct public
contract adapters as those APIs stabilize.

## Next-Phase Plan

The next-phase plan is stored in:

- `docs/architecture/81-scene-generation-next-phase-plan.md`

Next focus:

- cross-module promotion certification;
- public gate inventory;
- promotion evidence schema hardening;
- direct public gate adapters;
- deterministic corpus campaigns;
- quality gates and golden promotion package digests;
- fixture promotion dry run only after gates pass.

## Skipped Checks And Risks

- Full C++ build and CTest were not rerun as part of this archive request.
  Scene explorer unit tests were run and passed.
- The checkout contains unrelated modified and untracked files outside
  scene-generation and completed-task archive paths. They were not modified by
  this archive task.
- Public promotion gates still depend on available structured reports or a
  solver executable for some evidence paths.
- The next phase should prevent scratch exploration artifacts from drifting
  into durable fixtures without explicit promotion review.

## Follow-Up

- Complete the gate contract inventory from
  `81-scene-generation-next-phase-plan.md`.
- Prefer direct runtime/diagnostics/viewer public adapters over executable
  smoke output.
- Add campaign-level corpus reports and selected promotion candidate sets.
- Add golden digest checks for representative promotion packages.
- Decide when and how selected generated candidates should move into
  `fixtures/scene`.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-24-scene-auto-explorer-design-implementation-plan/`
- Durable design:
  `docs/architecture/scene-generation-tools.md`
- Next-phase plan:
  `docs/architecture/81-scene-generation-next-phase-plan.md`
- Tooling:
  `tools/scene_generation/`
- Tests:
  `tests/tools/test_scene_generation_explorer.py`
