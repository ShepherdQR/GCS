# Recent Lite Token Diagnostic

Run id: `token-diagnostic-1-lite`  
Lane: Lite  
Task pair: `token-diagnostic-1`  
Controller task card: `docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md`

## Source

Command:

```bat
python tools\token_audit\cache_hit_experiment.py list-sessions --limit 5 --format json
```

The command was run against `C:\Codes\AI\GCS_A` because this worktree's local
`tools\token_audit\audit.db` is zero bytes and has no `sessions` table.

## Selected Session

Session: `5cc71ca0-85ef-427e-aa1c-31b60ecb4b63`  
Started: `2026-05-30T12:53:43.004Z`  
Project: `GCS-A`  
Model: `deepseek-v4-pro`

| Metric | Value |
| --- | ---: |
| Input tokens | 141,061 |
| Output tokens | 50,164 |
| Cache-read tokens | 13,104,000 |
| Cache-read / input | 92.90x |
| Cache-read share of input+cache-read | 98.94% |
| Output / input | 35.56% |
| BEI composite | 0.6365 |
| Token leverage ratio | 0.3556 |

## Interpretation

This recent session is strongly cache-dominated: nearly all context volume came
from cache reads, while fresh input stayed modest relative to the reused prefix.
The output/input ratio and BEI are midrange rather than extreme, so the Lite
evidence suggests healthy prefix reuse but does not by itself prove whether the
cached material was necessary.

## Caveats

- Lite lane evidence is limited to `list-sessions` output.
- No transcript, task artifact, baseline report, or DB schema inspection was
  used for qualitative validation.
- DeepSeek cache creation tokens are not visible here, so this diagnosis uses
  cache-read dominance rather than a full raw cache-hit calculation.

## Suggested Run Metadata

| Field | Suggested value |
| --- | ---: |
| audit_score_0_5 | 4 |
| validation_passed | true |
| rework_turns | 0 |
| defect_or_reopen_count | 0 |
