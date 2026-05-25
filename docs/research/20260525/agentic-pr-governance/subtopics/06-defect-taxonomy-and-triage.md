# Defect Taxonomy And Triage

Date: 2026-05-25

## Question

How should GCS classify defects found by automated exploration and nightly
diagnostics?

## Pattern

Defects should be normalized before repair. A good taxonomy lets the agent
route work to the right owner, choose the right evidence, avoid duplicate
reports, and decide whether a finding is safe for automated repair.

## Base Taxonomy

| Category | Meaning | Default owner |
| --- | --- | --- |
| `environment_setup` | Missing tools, build dir, dependency, or path issue | task-scoped session closer or tool owner |
| `docs_link` | Broken local links, stale paths, bad index references | architecture or agentic docs owner |
| `task_archive` | Task card/archive mismatch, missing evidence, weak closure | task-scoped session closer |
| `architecture_boundary` | Solver/UI/IO/agentic dependency or ownership drift | gcs-architecture-steward |
| `quality_gate` | Test/gate missing, failing, or incorrectly skipped | gcs-quality-steward |
| `scene_explorer` | Scene generation, exploration, validation, promotion package issue | gcs-scene-generation-engineer |
| `fixture_promotion` | Generated artifact lacks provenance or promotion evidence | gcs-quality-steward plus scene generation |
| `solver_contract` | Stable ID, report code, snapshot, residual, runtime, IO contract issue | owning module steward |
| `diagnostic_evidence` | Missing rank/residual/gluing/obstruction evidence | gcs-diagnostics-certification-steward |
| `security_permission` | Network, secrets, destructive command, dependency, or policy risk | third-party/security governance |
| `pr_audit` | PR lacks review focus, evidence, risk tier, or correct owner | PR audit governance |
| `transient` | One-off network, timing, cache, or flaky setup issue | nightly automation |
| `unknown` | Evidence insufficient for classification | human triage |

## Severity Rules

| Severity | Rule |
| --- | --- |
| P0 | Potentially unsafe merge, destructive action, secret risk, protected-branch risk, or high-risk contract mutation without evidence |
| P1 | Concrete failure in validation, CI, runtime contract, fixture promotion, or task/archive closure |
| P2 | Missing review clarity, weak evidence, stale docs, broad diff, repeated warning |
| P3 | Low-risk polish or informational drift |

## Repairability

| Repair class | Meaning |
| --- | --- |
| `auto_report_only` | The automation may only report; human decision required |
| `auto_patch_candidate` | The automation may produce a local diff in its worktree |
| `task_card_required` | Promote to a formal task before editing |
| `human_gate_required` | Human must approve before any fix attempt |
| `ignore_with_reason` | Known false positive or accepted risk |

High-risk categories such as `solver_contract`, `security_permission`, and
`fixture_promotion` default to `task_card_required` or `human_gate_required`.

## Deduplication

Findings should be deduplicated by:

- category;
- normalized affected paths;
- command or evidence source;
- stable subject ID when available;
- previous run references.

Repeated P2 findings across three runs should be escalated to P1 process debt
because the project is ignoring a stable signal.

## GCS Decision

Nightly diagnostics should classify first, then repair. A finding without a
category, severity, owner, and repairability label is not ready for automated
repair.
