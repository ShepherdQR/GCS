# Cache-Hit Pilot Runbook: Eight Full/Lite Pairs

Date: 2026-05-31

Controller task card:
`docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md`

This runbook defines the first real paired pilot for the cache-hit diagnosis
experiment. The current planning/setup session is explicitly excluded from the
pilot dataset. Only dedicated task sessions that start from one of the run
prompts below should be recorded in `experiment-runs.csv`.

## Run Rules

1. Use one dedicated Codex thread/session per run.
2. Start the first user prompt with the run header:
   `CACHE_HIT_EXPERIMENT_RUN <run_id> <task_pair> <mode>`.
3. Use the controller task card above for the whole pilot. Individual runs do
   not create new task cards unless the run unexpectedly expands in scope.
4. Do not record the row from inside a background worktree. The controller
   imports telemetry and appends the row after the run finishes.
5. Keep artifacts under
   `docs/research/20260530/cache-hit-diagnosis-experiment/pilot-artifacts/`.
6. Commit only the files created for that run if the run makes a commit.
7. Record failures honestly. A failed validation is still useful evidence.

## Lane Contracts

### Full Lane

- Read the relevant project context before acting.
- Invoke the directly relevant GCS steward skill if one applies.
- Use the existing task card as the governing scope.
- Capture validation evidence in the artifact.
- Name residual risk and auditability notes.

### Lite Lane

- Read only the target files and the minimal command output needed.
- Invoke only a directly necessary skill; otherwise proceed with local context.
- Use the existing task card as the governing scope.
- Run the smallest acceptance command that proves the artifact.
- Keep the final report compact.

Lite is reduced context, not no governance.

## Pair Matrix

| Pair | Order | Full run | Lite run | Risk | Acceptance |
|---|---|---|---|---|---|
| `docs-index-1` | Full then Lite | Index `docs/architecture/30-contracts/` into `pilot-artifacts/docs-index/contracts-index-full.md`. | Index `docs/architecture/20-solver-pipeline/` into `pilot-artifacts/docs-index/pipeline-index-lite.md`. | low | Artifact has file list, 3-5 key themes, stale-link notes, and command evidence. |
| `token-diagnostic-1` | Lite then Full | Diagnose one recent high-cache session using DB inspection plus baseline/diagnostic context into `pilot-artifacts/token-diagnostics/high-cache-full.md`. | Diagnose one recent session using only `list-sessions` output into `pilot-artifacts/token-diagnostics/recent-lite.md`. | low | Artifact contains session id, token ratios, interpretation, and caveats. |
| `repo-audit-1` | Full then Lite | Run repository audit check and write a scoped docs/findings readout into `pilot-artifacts/repository-audit/docs-scope-full.md`. | Run repository audit check and write a compact tools/findings readout into `pilot-artifacts/repository-audit/tools-scope-lite.md`. | low | Artifact records command, pass/fail, finding count if available, and next action. |
| `task-card-audit-1` | Lite then Full | Audit `2026-05-30-cache-hit-diagnosis-experiment.md` against lifecycle expectations into `pilot-artifacts/task-card-audit/diagnosis-card-full.md`. | Audit `2026-05-30-cache-hit-experiment-implementation.md` against visible acceptance gates into `pilot-artifacts/task-card-audit/implementation-card-lite.md`. | low | Artifact scores scope clarity, evidence, residual risk, and replayability. |
| `completed-archive-audit-1` | Full then Lite | Review `docs/completed-tasks/2026-05-30-cache-hit-diagnosis-experiment/README.md` into `pilot-artifacts/completed-archive-audit/diagnosis-archive-full.md`. | Review `docs/completed-tasks/2026-05-30-cache-hit-experiment-implementation/README.md` into `pilot-artifacts/completed-archive-audit/implementation-archive-lite.md`. | low | Artifact records closure evidence quality and missing follow-up signals. |
| `fixture-inventory-1` | Lite then Full | Inventory `fixtures/scene/json/` fixtures with scene-behavior context into `pilot-artifacts/fixture-inventory/json-fixtures-full.md`. | Inventory `fixtures/scene/basic/` fixtures using directory/file inspection only into `pilot-artifacts/fixture-inventory/basic-fixtures-lite.md`. | low | Artifact lists files, likely format, intended use, and validation command. |
| `python-gui-smoke-1` | Full then Lite | Compile `python/gcs_viz`, inspect bridge-facing modules, and write `pilot-artifacts/python-gui-smoke/bridge-modules-full.md`. | Compile `python/gcs_viz`, inspect screen modules only, and write `pilot-artifacts/python-gui-smoke/screens-lite.md`. | low | Artifact includes compile command result and module responsibility summary. |
| `cpp-module-map-1` | Lite then Full | Map `src/gcs/kernel` and `src/gcs/numeric_engine` module files with solver-maintainer context into `pilot-artifacts/cpp-module-map/kernel-numeric-full.md`. | Map `src/gcs/io_adapters` and `src/gcs/session_runtime` module files with direct file inspection into `pilot-artifacts/cpp-module-map/io-session-lite.md`. | low | Artifact lists module files, exported boundary hints, and compile/build caveat. |

The order alternates enough to reduce simple learning/order effects while
keeping the first run easy to inspect.

## Run Prompts

Use these prompts as the first message in a dedicated run thread. Replace only
the branch/worktree details if needed.

### `docs-index-1-full`

```text
CACHE_HIT_EXPERIMENT_RUN docs-index-1-full docs-index-1 Full

You are executing a Full lane cache-hit pilot run in C:\Codes\AI\GCS_A.
Use the existing controller task card docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md; do not create a new task card unless the scope unexpectedly expands.

Task: index docs/architecture/30-contracts/ into docs/research/20260530/cache-hit-diagnosis-experiment/pilot-artifacts/docs-index/contracts-index-full.md.

Full lane rules: read the relevant experiment runbook and enough architecture/contract context to make the artifact auditable; invoke applicable GCS stewardship if triggered; include validation evidence and residual risk.

Acceptance: the artifact contains a file list, 3-5 key themes, stale-link or uncertainty notes, and command evidence. Commit only the run artifact if you commit. Do not append experiment-runs.csv. Final response must include suggested audit_score_0_5, validation_passed, rework_turns, defect_or_reopen_count, and changed files.
```

### `docs-index-1-lite`

```text
CACHE_HIT_EXPERIMENT_RUN docs-index-1-lite docs-index-1 Lite

You are executing a Lite lane cache-hit pilot run in C:\Codes\AI\GCS_A.
Use the existing controller task card docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md; do not create a new task card unless the scope unexpectedly expands.

Task: index docs/architecture/20-solver-pipeline/ into docs/research/20260530/cache-hit-diagnosis-experiment/pilot-artifacts/docs-index/pipeline-index-lite.md.

Lite lane rules: read only the target files and minimal command output needed; keep the artifact compact; include the smallest command evidence that proves the file set was inspected.

Acceptance: the artifact contains a file list, 3-5 key themes, stale-link or uncertainty notes, and command evidence. Commit only the run artifact if you commit. Do not append experiment-runs.csv. Final response must include suggested audit_score_0_5, validation_passed, rework_turns, defect_or_reopen_count, and changed files.
```

### `token-diagnostic-1-lite`

```text
CACHE_HIT_EXPERIMENT_RUN token-diagnostic-1-lite token-diagnostic-1 Lite

Execute a Lite lane cache-hit pilot run. Use only tools/token_audit/cache_hit_experiment.py list-sessions --limit 5 --format json plus minimal local inspection.

Task: choose one recent session from the command output and write a compact diagnostic to docs/research/20260530/cache-hit-diagnosis-experiment/pilot-artifacts/token-diagnostics/recent-lite.md.

Do not append experiment-runs.csv. Final response must include suggested audit_score_0_5, validation_passed, rework_turns, defect_or_reopen_count, and changed files.
```

### `token-diagnostic-1-full`

```text
CACHE_HIT_EXPERIMENT_RUN token-diagnostic-1-full token-diagnostic-1 Full

Execute a Full lane cache-hit pilot run. Read the experiment runbook, baseline, and first-pass diagnostic before acting.

Task: choose one recent high-cache session from token-audit DB inspection and write an auditable diagnostic to docs/research/20260530/cache-hit-diagnosis-experiment/pilot-artifacts/token-diagnostics/high-cache-full.md.

Include token ratios, interpretation, caveats, and command evidence. Do not append experiment-runs.csv. Final response must include suggested audit_score_0_5, validation_passed, rework_turns, defect_or_reopen_count, and changed files.
```

### Remaining Pair Prompts

For the remaining six pairs, use the Pair Matrix as the task source and this
template:

```text
CACHE_HIT_EXPERIMENT_RUN <run_id> <task_pair> <Full|Lite>

Execute the <Full|Lite> lane exactly as defined in docs/research/20260530/cache-hit-diagnosis-experiment/pilot-runbook-8-pairs.md.
Use the existing controller task card docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md.
Create only the artifact path named in the Pair Matrix for <run_id>.
Run the listed acceptance command or the smallest equivalent command.
Do not append experiment-runs.csv.
Final response must include suggested audit_score_0_5, validation_passed, rework_turns, defect_or_reopen_count, and changed files.
```

## Controller Recording Commands

After a dedicated run finishes, the controller imports telemetry, identifies the
finished session, records the row, and refreshes the summary:

```bat
python -m tools.token_audit db import --all
python tools\token_audit\cache_hit_experiment.py list-sessions --limit 12 --format json
python tools\token_audit\cache_hit_experiment.py record --session-id <session-id> --run-id <run-id> --task-pair <task-pair> --mode <Full|Lite> --task-type <docs|audit|fixture|tool> --risk low --audit-score <0-5> --validation-passed <true|false> --rework-turns <n> --defect-or-reopen-count <n> --notes "<short note>"
python tools\token_audit\cache_hit_experiment.py summarize --runs docs\research\20260530\cache-hit-diagnosis-experiment\experiment-runs.csv --output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md --json-output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json
```

## Scoring Defaults

- Start from audit score `4` when the artifact is complete and validation is
  replayable.
- Use `5` only if another reviewer can reproduce the result without reading
  chat context.
- Use `3` if the artifact is adequate but weakly justified.
- Use `2` or lower when command evidence or scope is unclear.

## Stop Conditions

- Stop a run and record failure if validation cannot run.
- Stop the pilot before policy conclusions if fewer than six pairs are complete.
- Stop and review if Lite produces any defect/reopen on a medium-risk task.
