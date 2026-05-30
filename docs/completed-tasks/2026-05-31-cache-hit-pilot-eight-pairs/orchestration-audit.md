---
task_id: 2026-05-31-cache-hit-pilot-eight-pairs
audit_type: orchestration
status: complete
---

# Cache-Hit Pilot Orchestration Audit

## Scope

This audit reviews the orchestration shape of the cache-hit Full/Lite pilot:
sixteen dedicated worker sessions produced paired artifacts and JSONL token
telemetry; the controller session collected artifacts, recorded rows, generated
the summary, and wrote the closure archive.

It does not re-score the solver or mutate historical transcripts.

## Task Structure

| Subtask | Dependency | Result |
|---|---|---|
| Freeze baseline and design runbook | none | completed before worker dispatch |
| Run paired worker sessions | runbook | 16 rows across 8 pairs |
| Collect artifacts and JSONL telemetry | worker completion | completed by controller |
| Summarize and classify pairs | collected rows | 8/8 pairs complete |
| Close task and record learning | final summary | completed archive and experience candidate |

Dependency structure: **merge**. The worker tasks were independent once the
runbook fixed each artifact path and lane contract; all evidence converged into
one controller synthesis step.

## Architecture Decision

| Field | Value |
|---|---|
| Architecture | parallel workers plus centralized synthesis |
| Worker count | 16 total dedicated runs, dispatched in batches |
| Controller role | verify scope, collect outputs, record JSONL metrics, summarize |
| Evidence source | per-run artifacts plus Codex Desktop JSONL `token_count` events |
| Synthesis artifact | `pilot-summary.md`, `pilot-summary.json`, and closure README |

The architecture was appropriate because the paired runs had clean interfaces:
each worker wrote exactly one artifact and did not append
`experiment-runs.csv`. The controller owned all row recording, which prevented
CSV conflicts and kept scoring consistent.

## Verification Findings

| Gate | Finding |
|---|---|
| Scope | Workers generally stayed inside assigned artifact paths. |
| Evidence | Each accepted run produced a concrete Markdown artifact and final audit fields. |
| Honesty | The GUI Lite run reported a real dependency failure instead of smoothing it over. |
| Completeness | All eight pairs have Full and Lite rows. |
| Cross-worker conflicts | No semantic conflict between accepted artifacts; one duplicate archive Lite run was stopped and excluded. |
| Shared-state control | Workers did not write the experiment CSV; controller-only recording worked. |

## Orchestration Issues

| Issue | Impact | Handling |
|---|---|---|
| Duplicate `completed-archive-audit-1-lite` thread | Could have double-counted one run | Controller ignored the duplicate and used the earliest completed valid run. |
| Final batch briefly exceeded the orchestrator skill's preferred 5-worker cap | Increased coordination risk | Outputs were centrally verified; future batches should cap concurrent workers at 5. |
| Path packaging changed from the original experiment root into `cache-hit-rate-full-lite-pilot/` | Risk of stale links and deleted old paths | Current reports now point at the package path; path move should be reviewed before merge. |
| `.git/config` ended with a truncated `[b` line during closeout | Git status failed | Removed the local malformed line; no tracked source file was affected. |
| GUI Lite reported missing `matplotlib` | One Lite validation failure and defect | Kept as the key healthy-institutionalization signal rather than fixing it inside the experiment. |

## Experience / Skill / Agent Review

| Material | Decision | Rationale |
|---|---|---|
| Experience | promote candidate note | The session demonstrates a reusable pattern for independent experimental worker runs with controller-owned telemetry collection. |
| Skill | no active promotion | Existing `orchestrator`, `gcs-token-audit-steward`, and `task-scoped-session-closer` cover the workflow. Add a future dispatch template only after another clean run. |
| Agent | no new agent | The work needs a controller pattern, not a persistent institutional role. |
| Audit | keep task-class policy boundary | Aggregate evidence supports Lite for low-risk classes, but GUI/environment-sensitive work still requires Full context. |

## Orchestration Record

- Task structure: merge.
- Architecture: parallel workers plus single controller synthesis.
- Agent count: 16 worker sessions total, batched.
- Models used: controller and workers used Codex GPT-5.5.
- Evidence: 16 recorded rows, 8 complete pairs, artifact package, generated
  summary, validated closure archive.
- Failures: one duplicate worker stopped; one Lite GUI validation failure kept
  as evidence; one local Git config corruption repaired.
- Learning record: `docs/agentic/experience/007-parallel-experiment-worker-orchestration/README.md`.

## Audit Conclusion

The orchestration succeeded because shared mutable state was centralized in the
controller. The main improvement for future use is stricter batch sizing: keep
parallel worker batches at five or fewer unless the runbook explicitly justifies
more, and require the controller to verify path moves before committing.
