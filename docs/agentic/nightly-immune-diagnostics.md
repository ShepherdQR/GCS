# GCS Nightly Immune Diagnostics

Status: proposed v1.
Date: 2026-05-25.

Installed automation:

- ID: `gcs-nightly-immune-diagnostics`
- Schedule: daily at `02:30 Asia/Shanghai`
- Execution environment: Codex worktree automation
- Created from task:
  `docs/agentic/tasks/2026-05-25-agentic-pr-governance-nightly-diagnostics.md`

## Purpose

Nightly immune diagnostics is a recurring agentic maintenance workflow for GCS.
It searches for early signs of process, documentation, quality-gate,
scene-exploration, fixture, and contract drift, then writes a dated report that
humans can inspect in the morning.

The workflow is intentionally conservative. It may detect, classify, analyze,
summarize, and propose repairs. It may prepare low-risk patch candidates in an
isolated worktree when safe. It must not merge, approve, force-push, delete
branches, promote fixtures, or mutate high-risk solver contracts unattended.

## Default Schedule

Run once per night at `02:30 Asia/Shanghai`.

Rationale:

- avoids foreground development time;
- leaves enough time for morning review;
- keeps each run independent and easy to compare by date.

## Execution Environment

Use a Codex project automation in worktree mode.

Reason:

- background edits do not interfere with local work;
- the diff is inspectable;
- the run can be discarded if noisy;
- this matches the GCS lifecycle worktree rule.

## Output Location

Each run writes:

```text
docs/agentic/nightly-runs/YYYY-MM-DD/
  README.md
  findings.json
  commands.md
  repair-plan.md
  task-card-candidate.md        # optional
  patch.diff                    # optional
```

The directory root also keeps a generated index:

```text
docs/agentic/nightly-runs/README.md
```

Refresh it with:

```bat
python tools\agentic_design\agentic_toolkit.py update-nightly-index --force
```

The index summarizes run status, finding counts, severity counts, skipped
checks, category totals, and calibration notes. It is informational only and
does not approve, merge, force-push, delete branches, or promote fixtures.

If there are no findings, the run still writes `README.md` with:

- run ID;
- commit SHA;
- checks attempted;
- skipped checks;
- "no actionable findings";
- residual uncertainty.

## Pipeline

```text
automatic scene exploration
  -> automatic defect discovery
  -> defect classification
  -> defect analysis and summary
  -> repair recommendation
  -> optional safe repair candidate
  -> whole-run summary and next actions
```

## Stages

### 1. Intake And Workspace Snapshot

Record:

- date/time and timezone;
- branch/worktree;
- current commit SHA;
- `git status --short --branch`;
- automation prompt version if available.

Stop if the repository is not readable or git state cannot be inspected.

### 2. Agentic Artifact Checks

Run lightweight checks:

```bat
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
```

If a command is unavailable, record `environment_setup` instead of inventing a
pass.

### 3. Scene Exploration And Existing Corpus Health

Use existing scene-generation tools where feasible:

```bat
python tools\scene_generation\tools.py list
python -m unittest tests.tools.test_scene_generation_explorer
```

If a promoted fixture gate is feasible in the local environment:

```bat
python tools\scene_generation\fixture_library_gate.py --gcs-exe out\build\clang-ninja\GCS.exe
```

Do not generate durable fixtures. Do not promote scratch scene outputs.

### 4. Focused Quality Gate

Prefer an affordable gate first:

```bat
python tools\agentic_design\agentic_toolkit.py run-quality-gates --skip-build --skip-ctest --skip-cli --continue-on-failure
```

Run the full quality gate only when the environment is already provisioned and
the previous stage suggests it is worth the cost. If the full gate is skipped,
record the reason and risk.

### 5. Defect Discovery

Collect:

- failing commands;
- missing command dependencies;
- stale local docs links;
- task/archive validation failures;
- repeated skipped checks;
- generated artifact drift;
- scene explorer failures;
- fixture promotion failures;
- dependency boundary failures;
- suspicious untracked generated outputs.

### 6. Defect Classification

Use this taxonomy:

| Category | Meaning |
| --- | --- |
| `environment_setup` | Missing local tool, build output, dependency, or path |
| `docs_link` | Broken docs link or stale path |
| `task_archive` | Task card/archive/closure evidence problem |
| `architecture_boundary` | Module ownership or dependency direction drift |
| `quality_gate` | Test, CTest, CI, fixture, or gate failure |
| `scene_explorer` | Scene generation or exploration tool issue |
| `fixture_promotion` | Promoted fixture/corpus evidence issue |
| `solver_contract` | Public solver contract or report evidence issue |
| `diagnostic_evidence` | Residual, rank, gluing, obstruction, or status evidence issue |
| `security_permission` | Network, secret, destructive action, or dependency governance risk |
| `pr_audit` | PR/task evidence mismatch or review-readiness issue |
| `transient` | Likely one-off network/cache/timing issue |
| `unknown` | Insufficient evidence |

Severity:

- `P0`: unsafe action, protected branch risk, secret risk, high-risk missing
  gate.
- `P1`: concrete failed validation or contract/gate regression.
- `P2`: weak evidence, broad drift, missing clarity, repeated warning.
- `P3`: low-risk polish or informational note.

### 7. Repair Recommendation

Every finding gets:

- owner or steward;
- repairability label;
- minimal suggested fix;
- required validation;
- whether a task card is required.

Repairability labels:

| Label | Meaning |
| --- | --- |
| `auto_report_only` | Report only; no patch |
| `auto_patch_candidate` | Low-risk patch may be prepared in worktree |
| `task_card_required` | Create task card before editing |
| `human_gate_required` | Human approval before command or edit |
| `ignore_with_reason` | Known false positive or accepted risk |

### 8. Optional Safe Repair Candidate

Allowed only for:

- docs typo/path fixes;
- local report formatting;
- adding missing links to newly created docs;
- updating the current run's own artifacts.

Forbidden:

- solver/runtime/IO/viewer semantic changes;
- fixture promotion;
- dependency installation;
- network-dependent edits;
- branch deletion;
- merge/approve/force-push;
- modifying protected branch state.

### 9. Summary And Handoff

Write:

- high-signal summary;
- command table;
- finding table;
- repair plan;
- suggested next task card or PR action;
- skipped checks and residual risk.

If repeated failures occur across three runs, recommend a formal task card.

## `findings.json` Schema

```json
{
  "run_id": "nightly-YYYY-MM-DD",
  "date": "YYYY-MM-DD",
  "timezone": "Asia/Shanghai",
  "commit": "git-sha",
  "status": "no_findings | findings | failed",
  "findings": [
    {
      "id": "NID-YYYY-MM-DD-001",
      "category": "quality_gate",
      "severity": "P1",
      "confidence": "high",
      "affected_paths": ["path"],
      "affected_contracts": ["contract"],
      "evidence": "command or artifact",
      "summary": "short finding",
      "repairability": "task_card_required",
      "recommended_action": "next step"
    }
  ],
  "skipped_checks": [
    {
      "check": "full ctest",
      "reason": "build output not present",
      "risk": "contract regressions may remain undetected"
    }
  ]
}
```

## Automation Prompt Contract

The automation prompt must say:

- run in worktree mode;
- write dated artifacts;
- do not commit or push unless a human explicitly asks for that run;
- do not merge, approve, force-push, delete branches, or promote fixtures;
- classify before repairing;
- stop on high-risk findings and create a task-card candidate;
- record skipped checks as risk;
- report no findings only after commands or explicit lightweight inspection.

## First Two Runs

The first two scheduled runs are calibration runs:

- do not auto-patch beyond the run directory;
- focus on signal/noise;
- compare findings with human review;
- tune taxonomy and gate selection before allowing low-risk patch candidates.

## Relationship To PR Audit

Nightly diagnostics may create PR audit findings, but it should not review its
own repair PR as an approval. If it creates a repair branch in the future, a
separate human review or separate non-author audit pass must inspect it.
