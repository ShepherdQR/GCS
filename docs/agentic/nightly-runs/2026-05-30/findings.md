# Night-Watch Calibration Run — 2026-05-30

## Run Metadata

| Field | Value |
|-------|-------|
| Date | 2026-05-30 |
| Run type | Calibration (first real exercise of night-watch institutional agent) |
| Commit SHA | 61c1498 |
| Branch | master |
| Worktree | C:/Codes/AI/GCS_A (main) |
| Overall status | WARN |

## Checks Executed

### 1. validate-docs — PASS

Command: `python tools/agentic_design/agentic_toolkit.py validate-docs`

Output: `[OK] docs: module design coverage passed`

No anomalies. The tool reports one line; unclear whether it checked all doc directories or only the ones with a known module design pattern. This is a low-concern calibration note.

### 2. git worktree list — WARN

Command: `git worktree list`

Output:
```
C:/Codes/AI/GCS_A                                           61c1498 [master]
C:/Codes/AI/GCS_A/.claude/worktrees/reverent-kepler-c6eee1  a6650d5 [claude/reverent-kepler-c6eee1]
```

One stale worktree detected: `reverent-kepler-c6eee1` on branch `claude/reverent-kepler-c6eee1` at commit a6650d5. It has not been cleaned up. Low risk — human should verify and remove with `git worktree remove`.

### 3. git status — WARN

Command: `git status`

Summary: On master, up to date with origin/master. No staged changes, no unstaged modifications. Many untracked files present (approximately 30+ entries).

Key untracked items:
- `.agents/` — likely a mis-capitalized clone of `.claude/agents/`
- `.codex/agents/` and `.codex/hooks.json` — Codex configuration artifacts
- `AGENTS.md` — possibly a mis-capitalized CLAUDE.md
- `check_balance.py` — ad-hoc script
- `docs/agentic/` — multiple pipeline development plans and task cards
- `docs/architecture/70-visualization/narrative-line-level-baseline-20260530.md`
- `docs/narrative-lines/` — new documentation directory
- `tools/solver_testing/benchmarks/` and `tools/solver_testing/pipelines/` — new tooling
- `tools/token_audit/audit.db.pre-v2-backup` — database backup

The volume of untracked files makes it harder to distinguish deliberate work from accidental artifacts. The `.agents/` directory is particularly suspicious. Medium severity.

### 4. Completed-task archives — WARN

Sampled 5 recent archives plus a glob scan of all 86 archives.

All 86 completed-task archives contain only README.md. Zero contain evidence.md or artifacts.md. The folder contract in `docs/completed-tasks/README.md` lists both as optional, but universal absence suggests either dead spec or embedded evidence. Low severity — may be a false positive.

### 5. .claude/agents/ directory — PASS

Count: 15 agent definition files + 1 README.md = 16 files total. All have non-trivial content. Line counts range from 43 to 100, with core agents at 80-100 lines and lighter agents at 40-47 lines. No anomalies.

### 6. Night-watch agent output template — WARN

Checked: `.claude/agents/night-watch.md`

The agent definition has a "Required Output" section listing file names and what each should contain, but lacks a concrete, reusable output template with placeholders. Recommend adding an `## Output Templates` section to `night-watch.md` with fillable markdown template blocks.

### 7. Institutional agent directory numbering — NOTE

Directories 001 through 008 exist under `docs/agentic/institutional-agents/`. The planned path for night-watch evals (`006-night-watch`) conflicts with existing `006-bookkeeper`. Both share the `006-` prefix. Numbering should be resolved by the next agent reassessment cycle.

## Summary

| Check | Result | Severity |
|-------|--------|----------|
| validate-docs | PASS | — |
| git worktree list | WARN — 1 stale worktree | Low |
| git status | WARN — many untracked files, suspicious .agents/ | Medium |
| Completed-task archives | WARN — all 86 archives README.md only | Low |
| .claude/agents/ count | PASS | — |
| Night-watch output template | WARN — no reusable template block | Low |
| Agent directory numbering | NOTE — 006-night-watch vs 006-bookkeeper | Info |

## Calibration Notes

**What worked:**
- All commands executed successfully in the local environment (unlike the 2026-05-27 sandbox-blocked run).
- The agent definition provides clear enough guidance to structure a patrol run.
- The existing completed-tasks README provides a useful contract to check against.

**What was noisy:**
- The validate-docs tool produces minimal output (one line). Scope is unclear.
- The thin-archive observation may be a false positive: evidence.md and artifacts.md are marked optional.
- Untracked files are numerous; a .gitignore review would reduce noise.

**What to add next time:**
- Check that night-watch.md has been updated with a proper output template.
- Run validate-inventory and validate-skills if they exist and are functional.
- Check whether .agents/ vs .claude/agents/ duplication has been resolved.
- Verify that the stale worktree has been cleaned up.

**What to reconsider:**
- The findings.json format from previous runs is more machine-readable. Future runs could write both.
- A separate commands.md artifact would improve grep-friendliness and reproducibility.
