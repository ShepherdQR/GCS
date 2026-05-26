# Repository Audit Statistics Architecture

Status: proposed architecture.

Date: 2026-05-25

Source research: `docs/research/20260525/repository-audit-statistics/README.md`.

## Purpose

GCS needs a reproducible repository audit layer that can answer:

- how many files and lines exist by language, extension, directory, artifact
  class, and GCS module;
- which growth belongs to authored solver source, tests, fixtures,
  architecture docs, research notes, generated evidence, skills, or completed
  task archives;
- whether each target module still has expected source, interface,
  implementation, contract-test, skill, and architecture coverage;
- what changed in a task, branch, or pull request compared with a base
  revision;
- which repository-shape risks should be reviewed before commit or push.

This layer is an audit and evidence system. It must not become production
solver policy.

## Ownership

The repository audit system belongs to the support-tool boundary:

```text
tools/repository_audit/
  -> reads git, filesystem metadata, module_inventory.json, architecture docs
  -> writes JSON snapshots and Markdown reports
  -> feeds agentic quality gates and completed-task evidence
```

It may be coordinated from `tools/agentic_design/agentic_toolkit.py`, but the
collector itself should live in a focused package:

```text
tools/repository_audit/
  gcs_repository_audit/
    __init__.py
    collect.py
    classify.py
    metrics.py
    report.py
    diff.py
    registry.py
    policy.py
  repository_audit.py
tests/tools/test_repository_audit.py
```

Rationale:

- `tools/agentic_design` already owns module inventory, dependency checks,
  task cards, completed-task reports, and quality-gate orchestration.
- A separate `tools/repository_audit` package keeps metric logic cohesive and
  prevents `agentic_toolkit.py` from growing into a monolith.
- The solver core under `src/gcs/*` must never import or depend on repository
  audit tooling.

## Dependency Boundary

Allowed inputs:

- Git tracked-file lists and selected revision metadata.
- `tools/agentic_design/module_inventory.json`.
- `.gitignore` and optional future `.gitattributes`.
- Files under repo root, read-only.
- Optional external tool outputs from `cloc`, `tokei`, `github-linguist`,
  CodeQL, OpenSSF Scorecard, or SCA tools when explicitly enabled.

Disallowed behavior:

- No mutation of solver files.
- No hidden network access in the default local audit.
- No hard dependency on GitHub APIs for local quality gates.
- No build-output scanning unless an explicit `--include-build-output` flag is
  passed.
- No default failure thresholds until baseline history and exemptions exist.

## Data Flow

```text
repo root + git revision
  -> tracked path collector
  -> path classifier
  -> text/binary and language detector
  -> line/byte/extension metrics
  -> module inventory join
  -> policy checks
  -> RepositoryAuditSnapshot JSON
  -> RepositoryAuditReport Markdown
  -> optional diff against base snapshot or base revision
```

The canonical artifact is JSON. Markdown is a human projection.

## Canonical Commands

Initial CLI:

```bat
python tools\repository_audit\repository_audit.py collect --output var\repository-audit\latest.snapshot.json
python tools\repository_audit\repository_audit.py report --snapshot var\repository-audit\latest.snapshot.json --output docs\reports\repository-audit\2026-05-25\README.md
python tools\repository_audit\repository_audit.py diff --base origin/master --head HEAD --output var\repository-audit\diff.json
python tools\repository_audit\repository_audit.py check --snapshot var\repository-audit\latest.snapshot.json
python tools\repository_audit\repository_audit.py index --reports-root docs\reports\repository-audit --output docs\reports\repository-audit\README.md
python tools\repository_audit\repository_audit.py accepted-trend --reports-root docs\reports\repository-audit --output docs\reports\repository-audit\trend.md
```

Agentic toolkit integration:

```bat
python tools\agentic_design\agentic_toolkit.py repository-audit collect
python tools\agentic_design\agentic_toolkit.py repository-audit report
python tools\agentic_design\agentic_toolkit.py repository-audit diff --base origin/master
python tools\agentic_design\agentic_toolkit.py repository-audit check
```

The direct script should remain available so the audit package can be tested
without the full agentic toolkit.

## Snapshot Schema

`RepositoryAuditSnapshot`:

```json
{
  "schema_version": "gcs-repository-audit-0.1",
  "tool_version": "0.1",
  "generated_at": "2026-05-25T00:00:00+08:00",
  "repo_root": "C:/Codes/Trae/s002_GCS/GCS",
  "git": {
    "head": "<sha>",
    "branch": "<branch>",
    "dirty": true,
    "base": null
  },
  "counting_contract": {
    "tracked_files_only": true,
    "include_untracked": false,
    "include_build_output": false,
    "excluded_roots": ["out", "outputs", "var", ".git"],
    "text_extensions": [".cpp", ".cppm", ".py", ".md", ".json", ".txt", ".yaml"]
  },
  "totals": {
    "files": 0,
    "bytes": 0,
    "text_files": 0,
    "binary_files": 0,
    "physical_lines": 0
  },
  "groups": {
    "by_artifact_class": [],
    "by_top_level": [],
    "by_extension": [],
    "by_gcs_module": [],
    "by_lifecycle_layer": []
  },
  "files": [],
  "findings": []
}
```

`FileMetric`:

```json
{
  "path": "src/gcs/kernel/kernel.cppm",
  "artifact_class": "solver_source",
  "lifecycle_layer": "product",
  "gcs_module": "kernel",
  "extension": ".cppm",
  "bytes": 0,
  "physical_lines": 0,
  "is_text": true,
  "is_binary": false,
  "is_generated": false,
  "is_fixture": false,
  "is_documentation": false,
  "language_hint": "C++"
}
```

`AuditFinding`:

```json
{
  "id": "unexpected-build-output-tracked",
  "severity": "warning",
  "confidence": "high",
  "path": "out/example.bin",
  "message": "Build output is tracked by git.",
  "recommendation": "Remove from git or add an explicit exemption."
}
```

## Artifact Classes

The classifier should emit exactly one primary `artifact_class` per file:

| Class | Examples | Default report behavior |
| --- | --- | --- |
| `solver_source` | `src/gcs/**/*.cpp`, `src/gcs/**/*.cppm` | counted in source and module metrics |
| `application_shell` | `apps/gcs_cli/**` | counted separately from solver source |
| `viewer_python` | `python/gcs_viz/**` | counted as product-adjacent viewer code |
| `tooling` | `tools/**`, `scripts/**` | counted as support tooling |
| `contract_test` | `tests/contracts/**` | joined to module coverage |
| `tool_test` | `tests/tools/**` | support test evidence |
| `fixture` | `fixtures/**` | counted as evidence/data, not source LOC |
| `architecture_doc` | `docs/architecture/**` | durable architecture |
| `product_doc` | `docs/product/**` | product-facing briefs and usage narratives |
| `research_doc` | `docs/research/**` | background research |
| `agentic_process_doc` | `docs/agentic/**` | workflow and lifecycle |
| `completed_task_archive` | `docs/completed-tasks/**` | historical memory |
| `project_report` | `docs/reports/**` | durable generated or curated project reports |
| `codex_skill` | `.codex/skills/**` | agent skill surface |
| `generated_store` | `.codex_scene_generation_store/**` | generated scene evidence store |
| `visual_asset` | `.png`, `.jpg`, `.svg`, `.pdf`, `.pptx`, `.webp` | counted by bytes and file count |
| `repo_root_config` | `CMakeLists.txt`, `.gitignore`, `README.md` | counted as repo root support |
| `unknown` | any unmatched path | warning until classified or exempted |

## GCS Module Join

The audit must use `tools/agentic_design/module_inventory.json` as the first
source of truth for module ownership:

- `source_dir` maps source files to module IDs.
- `contract_test` maps contract tests to module IDs.
- `skill` maps physical skill files to module IDs.
- `allowed_imports` feeds dependency-boundary findings.

The module report should include:

| Field | Meaning |
| --- | --- |
| `module_id` | target module, e.g. `kernel` |
| `source_files` | files under module `source_dir` |
| `interface_files` | `.cppm` files |
| `implementation_files` | `.cpp` files |
| `source_lines` | physical lines in source files |
| `contract_test_files` | files under the registered contract test path |
| `contract_test_lines` | physical lines in contract tests |
| `skill_files` | files under the registered skill directory |
| `architecture_refs` | docs that mention the module heading or module ID |
| `findings` | missing source, missing test, forbidden import, or orphan docs |

## Initial Policy Checks

Version `0.1` should keep checks small and mostly warning-level:

| Finding ID | Severity | Rule |
| --- | --- | --- |
| `unknown-artifact-class` | warning | A tracked file does not match a known class. |
| `tracked-build-output` | error | A file under `out/`, `outputs/`, or `var/` is tracked without exemption. |
| `large-text-file` | warning | A text file exceeds configured line or byte thresholds. |
| `large-binary-file` | warning | A binary asset exceeds configured byte threshold. |
| `module-missing-interface` | error | A C++ module has no `.cppm` file. |
| `module-missing-implementation` | warning | A C++ module has no `.cpp` file. |
| `module-missing-contract-test` | error | Inventory names no existing contract test. |
| `contract-test-without-module` | warning | A contract suite is not mapped to an inventory module or external target. |
| `forbidden-cxx-import` | error | Existing `check-dependencies` rule fails. |
| `generated-store-growth` | info | `.codex_scene_generation_store` crosses configured growth band. |

No warning should fail the default gate. Error-level checks can be opt-in until
the first baseline is accepted.

## Report Shape

Generated Markdown report:

```markdown
# GCS Repository Audit

Date:
Revision:
Schema:

## Executive Summary
## Counting Contract
## Totals
## Artifact Class Breakdown
## GCS Module Coverage
## Top Growth/Risk Files
## Findings
## Delta From Base
## Reproduction
```

The report should include the exact command used and the source revision. If
the worktree is dirty, it must say so.

## Storage Policy

Use three levels:

```text
var/repository-audit/
  latest.snapshot.json
  latest.report.md
  diff.json

docs/reports/repository-audit/YYYY-MM-DD/
  README.md
  snapshot.json
  manifest.json

docs/reports/repository-audit/
  README.md

docs/research/YYYYMMDD/repository-audit-statistics/
  source-aware research and architecture background
```

Rules:

- `var/` is local scratch and should not normally be committed.
- `docs/reports/` is for accepted durable snapshots, release reports, and
  major milestone audits.
- `manifest.json` records that a snapshot is accepted, which committed Git
  revision it measures, who or what accepted it, and which report projection
  belongs to it.
- `docs/reports/repository-audit/README.md` is the registry index generated
  from accepted manifests.
- `docs/research/` is for source-aware studies and design rationale.
- Completed task archives link to the research/report artifacts but do not
  duplicate full generated tables unless they are needed as evidence.

## Quality Gate Integration

Phase 1 should add an opt-in gate:

```bat
python tools\agentic_design\agentic_toolkit.py run-quality-gates --include-repository-audit
```

The gate should run:

```bat
python tools\repository_audit\repository_audit.py check
```

Default gate promotion requires:

- at least three accepted snapshots across meaningful repository changes;
- documented exemptions for generated stores and binary assets;
- tests for classifier, module join, dirty worktree handling, and diff mode;
- no false-positive error findings on `origin/master`;
- architecture README and quality-gate docs updated with the default behavior.

Implementation note, 2026-05-26: repository audit is available as an opt-in
quality gate through
`python tools\agentic_design\agentic_toolkit.py run-quality-gates --include-repository-audit`.
The gate runs `repository_audit.py check` and remains non-default while baseline
history and exemptions are still being calibrated.

## Implementation Phases

### Phase 1: Contract And Collector

- Define `RepositoryAuditSnapshot`, `FileMetric`, `AuditFinding`, and
  `CountingContract` dataclasses.
- Collect tracked files through `git -c core.quotepath=false ls-files -z`.
- Classify paths into artifact classes.
- Emit JSON snapshots.
- Unit test path classification, non-ASCII paths, Windows separators, and
  generated-store handling.

### Phase 2: Reports And Module Join

- Generate Markdown reports from snapshots.
- Join module data from `module_inventory.json`.
- Report source/test/skill/doc coverage per module.
- Add top-file and top-directory summaries.
- Add task-card evidence examples.

Implementation note, 2026-05-26: the first Markdown report projection exists in
`tools/repository_audit/gcs_repository_audit/report.py`. It renders headline
totals, artifact/lifecycle/top-level breakdowns, module coverage, largest
tracked files, findings, and agentic governance counts. Diff mode, historical
trend projections, and quality-gate integration remain later phases.

### Phase 3: Diff And Policy Checks

- Compare two revisions or two snapshots.
- Add initial warnings and error-level findings.
- Integrate existing `check-dependencies` result.
- Add `--include-repository-audit` quality-gate option.

Implementation note, 2026-05-26: the first JSON diff projection exists in
`tools/repository_audit/gcs_repository_audit/diff.py`. It compares saved
snapshots or committed Git revisions and reports total deltas, changed files,
artifact/lifecycle/top-level/module group deltas, and finding deltas. Rename
detection, `check-dependencies` integration, trend storage, and quality-gate
promotion remain later work.

Implementation note, 2026-05-26: diff Markdown projection is available through
`repository_audit.py diff-report`. It reads the canonical diff JSON and renders
human-facing summaries, total deltas, group deltas, largest file deltas,
finding deltas, and reproduction commands.

### Phase 4: External Tool Adapters

- Optional `cloc` or `tokei` adapter for cross-checking LOC categories.
- Optional `github-linguist` adapter for language detection parity with
  GitHub.
- Optional OpenSSF Scorecard, CodeQL, and SCA adapters for public/CI contexts.
- Keep all external adapters disabled by default in local offline runs.

### Phase 5: Trend Reports

- Store milestone snapshots in `docs/reports/repository-audit/`.
- Add growth charts or tables for module source, fixtures, docs, tools, and
  generated evidence.
- Use trend reports for roadmap reviews, not for punitive line-count targets.

Implementation note, 2026-05-26: the first trend projection is available
through `repository_audit.py trend`. It reads two or more saved snapshots and
renders a Markdown series summary, total deltas, and artifact-class deltas.
Chart output and recurring cadence policy remain future work.

Implementation note, 2026-05-26: accepted snapshot manifests and the generated
registry index are available through `repository_audit.py index`. Accepted
snapshots should be collected from committed revisions with
`repository_audit.py collect --revision <rev>` so the durable baseline is not
polluted by unrelated dirty worktree edits.

Implementation note, 2026-05-26: `repository_audit.py accepted-trend` can
render a trend report directly from accepted manifests. With one accepted
snapshot it emits a baseline-only trend; with two or more snapshots it compares
the first and latest accepted baselines. `repository_audit.py archive-delta`
renders a compact completed-task section from a diff JSON, and
`diff --head-index` supports comparing the staged index to a base revision so
archives can record scoped deltas before commit.

## Acceptance Criteria For First Implementation Task

A first implementation task is complete when:

- `tools/repository_audit/repository_audit.py collect` produces a deterministic
  JSON snapshot from tracked files;
- classification tests cover every artifact class in this document;
- non-ASCII tracked paths are handled without Git quote-path corruption;
- module source and contract-test coverage are joined from
  `module_inventory.json`;
- generated Markdown reproduces the headline totals;
- no solver core files are imported or modified by the audit package;
- the completed-task archive records the snapshot command and residual risks.

## Non-Goals

- No direct UI dashboard in the first implementation.
- No default network calls.
- No mandatory SonarQube, Scorecard, CodeQL, or SCA dependency.
- No function-level AST complexity until file-level metrics stabilize.
- No quality-gate failure based only on raw LOC growth.

## Open Decisions

- Whether to add `.gitattributes` so GitHub Linguist and GCS audit categories
  align for generated stores, fixtures, and docs.
- Whether `.codex_scene_generation_store/` should stay tracked or move toward
  promoted fixture-only storage.
- Whether durable snapshots belong in `docs/reports/repository-audit/` for
  every phase close or only major releases.
- Whether ownership routing should remain skill/module based or eventually be
  projected into GitHub CODEOWNERS.
- What cadence should promote accepted snapshots into the default trend series
  after the registry has enough baseline density.
