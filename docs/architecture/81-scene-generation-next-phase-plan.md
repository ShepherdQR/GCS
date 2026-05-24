# Scene Generation Next Phase Plan

Date: 2026-05-24.

This document stores the current plan for the scene auto explorer and defines
the next research and execution phase. The source implementation is
`tools/scene_generation`, with durable design context in
`docs/architecture/scene-generation-tools.md`.

## Current State

The scene explorer is complete as a local v1:

- `explore_scene_space` explores candidate scenes from structured requests.
- `promote_candidate` writes promotion packages.
- The compatibility commands still support manual generate, lift,
  parameterize, validate, project, report, and serialize workflows.
- `gcs_scene_generation/` owns package boundaries for contracts, storage,
  topology, GCS model helpers, validation, projection, parameterization,
  reporting, repair, explorer orchestration, promotion adapters, and promotion
  packages.
- Exploration artifacts are written under
  `.store/explorations/<exploration_id>/`.
- Promotion artifacts are written under `.store/promotions/<promotion_id>/`.
- Tests cover deterministic exploration, negative evidence, storage safety,
  public scene conversion, promotion blocking, runtime/diagnostics evidence,
  and rank evidence shape.

The explorer is not yet a fully certified cross-module fixture promotion
system. Runtime and diagnostics gates can consume structured reports or fall
back to a solver command, but they are not yet direct in-process public
contract adapters.

## Stored Plan

Near-term plan:

- Keep `tools.py` as the CLI dispatcher and compatibility facade.
- Keep generation and repair policy in `tools/scene_generation`.
- Broaden public promotion gates from smoke checks and structured report
  parsing into direct public contract adapters.
- Prefer structured runtime, diagnostics, rank, and viewer evidence over
  command-output parsing.
- Preserve local-only promotion packages for research use, but do not treat
  them as durable fixtures.

Mid-term plan:

- Promote accepted exploration candidates into a managed scenario corpus only
  after promotion gates pass.
- Add richer coverage targets for large graphs, near-degenerate geometry,
  rank evidence, diagnostics conflicts, redundancy, and obstruction examples.
- Connect scene explorer outputs to quality gates and golden report digests.
- Add corpus-level reports that compare accepted candidates instead of only
  reporting one candidate at a time.

Non-goals:

- Do not move generator policy into `kernel`, `io_adapters`, runtime,
  diagnostics, viewer, or GUI modules.
- Do not write to `fixtures/scene` by default.
- Do not count unsupported gates as promotion success.
- Do not make fixture promotion depend on prose-only explanations.

## Next Phase Focus

The next phase is cross-module promotion certification.

Goal: make a candidate produced by `explore_scene_space` promotable only when
its evidence passes public scene IO, kernel, runtime, diagnostics, rank, and
viewer gates with structured machine-readable reports.

Primary outcome:

```text
explore_scene_space
  -> accepted candidate
  -> promote_candidate
  -> public gate evidence
  -> promotion package
  -> optional fixture promotion
```

Success means a promotion package can explain every gate outcome without
scraping ad hoc text or relying on hidden generator assumptions.

## Research Questions

1. Public scene contract:
   What is the minimal `gcs-0.3` scene payload that public IO accepts and
   round-trips canonically for generated candidates?

2. Kernel validation contract:
   Which kernel-facing model invariants can be checked from the public scene
   without importing generator-local policy?

3. Runtime evidence contract:
   What structured `RuntimeCommand` or CLI result shape should promotion
   consume to prove command execution, stage status, state version, and failure
   reason?

4. Diagnostics evidence contract:
   Which diagnostics reports are required for valid, under-constrained,
   over-constrained, redundant, inconsistent, singular, and gluing-obstruction
   generated scenes?

5. Rank evidence contract:
   What public `RankEvidenceProjection` shape should be treated as stable for
   promotion, viewer overlay, and golden-report checks?

6. Viewer projection contract:
   Which geometry-primal and overlay evidence is enough to prove that a
   promoted scene remains inspectable by the viewer bridge?

7. Corpus governance:
   Which generated candidates deserve promotion into `fixtures/scene`, and
   which should remain scratch exploration artifacts?

## Execution Plan

### Phase 1: Gate Contract Audit

Deliverables:

- Inventory public inputs and outputs for IO, kernel, runtime, diagnostics,
  rank evidence, and viewer projection.
- Map each promotion gate to a stable public contract and fallback state.
- Record any missing public reports as explicit blockers.

Acceptance:

- A table lists every gate, its authoritative module, its structured input,
  its structured output, and whether it is direct, fallback, or blocked.
- No gate depends on generator-local assumptions for solver truth.

### Phase 2: Promotion Evidence Schema

Deliverables:

- Define promotion evidence records for:
  `scene_io_round_trip`, `kernel_validation`, `runtime_smoke`,
  `diagnostics_evidence`, `rank_evidence`, and `viewer_projection`.
- Add stable reason codes for blocked, failed, skipped, unsupported, and
  passed states.
- Ensure `promotion_package.json` stores gate evidence without prose-only
  dependencies.

Acceptance:

- Promotion packages remain deterministic for the same candidate and evidence
  input.
- Unsupported gates are visible and block default promotion.
- `local_only` remains available but is clearly marked as not fixture-ready.

### Phase 3: Direct Public Gate Adapters

Deliverables:

- Replace runtime/diagnostics text scraping with structured report inputs
  wherever public APIs are available.
- Add direct adapters for scene IO and kernel-shape validation before runtime
  gates.
- Keep executable smoke fallback for CLI-only environments, but mark fallback
  evidence as lower confidence.

Acceptance:

- Promotion can run with a structured runtime report and no solver executable.
- Promotion can run with a solver executable and produces the same gate schema.
- Malformed structured evidence fails with typed reason codes.

### Phase 4: Corpus Candidate Campaign

Deliverables:

- Run deterministic exploration campaigns for:
  valid small scenes, mixed geometry scenes, near-degenerate geometry,
  invalid signatures, same-rigid-set violations, rank-evidence scenes, and
  diagnostics obstruction scenes.
- Write campaign reports under scratch exploration storage.
- Select a small promotion candidate set for fixture review.

Acceptance:

- Each campaign has request, result, trace, candidate provenance, and summary.
- Accepted candidates close explicit coverage goals.
- Rejected candidates carry stable reason codes and evidence IDs.

### Phase 5: Quality Gates

Deliverables:

- Extend Python tests for public gate adapters and promotion package evidence.
- Add CTest or contract-test integration only when public C++ contracts are
  stable enough to test without private implementation coupling.
- Add golden digest checks for representative promotion packages.

Acceptance:

- `python -m unittest tests.tools.test_scene_generation_explorer` covers the
  direct gate adapters.
- Promotion package digests are stable for deterministic inputs.
- Negative gate tests assert typed failure reason codes.

### Phase 6: Fixture Promotion Dry Run

Deliverables:

- Produce promotion packages for selected candidates.
- Verify canonical scene serialization and public gate reports.
- Prepare a fixture promotion PR or staged fixture directory only after all
  promotion gates pass.

Acceptance:

- No scratch candidate is copied into `fixtures/scene` unless explicitly
  requested and promotion gates pass.
- Promotion package contains source request, provenance, local validation,
  public gates, canonical serialization, digest, and fixture metadata proposal.

## Work Breakdown

P0 tasks:

- Document gate contract inventory.
- Harden promotion evidence schema.
- Add tests for blocked, skipped, failed, and passed gate states.
- Keep CLI examples current in `tools/scene_generation/tools.md`.

P1 tasks:

- Wire direct public report adapters for runtime and diagnostics.
- Add rank evidence corpus examples.
- Add viewer projection evidence checks that consume public overlay shape.
- Add campaign report command or corpus summary output.

P2 tasks:

- Promote selected fixture candidates.
- Add golden promotion package digests.
- Add CI-ready quality gate around scene exploration tests.
- Extend coverage scoring with semantic diagnostics targets.

## Gate Inventory Template

Use this table during Phase 1:

| Gate | Owner | Input | Output | Current state | Next action |
| --- | --- | --- | --- | --- | --- |
| `scene_io_round_trip` | `io_adapters` | public scene JSON | round-trip report | public smoke | bind to canonical IO contract |
| `kernel_validation` | `kernel` | public scene model | validation report | shape check | bind to kernel validation report |
| `runtime_smoke` | `session_runtime` | runtime command/report | command result | structured or executable fallback | prefer direct runtime report |
| `diagnostics_evidence` | `diagnostics` | runtime/diagnostic report | diagnostic evidence | structured or fallback | bind to diagnostics report taxonomy |
| `rank_evidence` | diagnostics/viewer | rank projection | rank evidence | structured optional gate | define stable projection schema |
| `viewer_projection` | `viewer_bridge` | model/projection | viewer projection | geometry-primal evidence | bind to public viewer projection |

## Risks

- Runtime and diagnostics reports may still evolve, so adapters should accept
  explicitly versioned evidence.
- Executable smoke checks are environment-sensitive; keep them as fallback, not
  as the preferred proof path.
- Generated scenes can become fixtures too early. Keep promotion separate from
  exploration and require explicit fixture-copy intent.
- Overfitting coverage scoring to current generator behavior may hide missing
  solver cases. Add campaign-level reports and negative corpora.

## Done Definition

The next phase is done when:

- promotion packages can be generated from structured public evidence;
- unsupported public gates no longer block standard fixture candidates;
- malformed evidence fails with typed reason codes;
- at least one valid candidate and one negative candidate campaign have
  deterministic request, result, trace, and promotion evidence;
- fixture promotion remains explicit and reproducible;
- tests cover the gate adapters and promotion package determinism.
