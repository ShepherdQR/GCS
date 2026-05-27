---
name: gcs-repository-audit-steward
description: Repository audit and trend analysis for GCS. Invoke when work touches repository file classification, snapshot collection, diff analysis, accepted-trend reports, repository health checks, audit deltas for completed-task archives, or repository index maintenance.
---

# GCS Repository Audit Steward

## Start Here

Use this skill for repository-level audit work. Repository audit turns repository
shape into reviewable engineering memory — it classifies files, collects
snapshots, compares revisions, builds trends, and integrates with the task
closure lifecycle.

Read:
- `docs/agentic/experience/005-repository-audit-value-loop/README.md`
- `docs/agentic/agentic-organization-operating-map.md`

## Workflow

1. **Classify** the audit need: snapshot, diff, trend, health check, or
   archive delta.
2. **Collect** from accepted baselines (committed revisions), not dirty
   worktrees, for trend analysis. Use worktree or index snapshots for
   pre-commit task-scope diffs.
3. **Compare** snapshots or revisions to produce classified diffs.
4. **Report** findings with severity, category, and repairability.
5. **Integrate** audit deltas into completed-task archives for task-level
   evidence.

## Command Reference

```bat
# Collect a snapshot
python tools\repository_audit\repository_audit.py collect --output <path>

# Check current repository health
python tools\repository_audit\repository_audit.py check

# Generate a Markdown report
python tools\repository_audit\repository_audit.py report --output <path>

# Diff two revisions or snapshots
python tools\repository_audit\repository_audit.py diff --base <rev> --output <path>
python tools\repository_audit\repository_audit.py diff --base-snapshot <path> --head-snapshot <path> --output <path>

# Generate diff report
python tools\repository_audit\repository_audit.py diff-report --diff <path> --output <path>

# Compact archive-delta for task closure
python tools\repository_audit\repository_audit.py archive-delta --diff <path> --output <path>

# Trend from snapshots
python tools\repository_audit\repository_audit.py trend --snapshot <path> [--snapshot <path> ...] --output <path>

# Accepted snapshot index
python tools\repository_audit\repository_audit.py index --output <path>

# Accepted-trend from manifests
python tools\repository_audit\repository_audit.py accepted-trend --output <path>
```

## Own

- Repository snapshot collection and classification.
- File-category inventory (source, test, fixture, tool, doc, agentic, config).
- Diff analysis between accepted baselines.
- Trend reports from accepted snapshot manifests.
- Archive-delta integration with task closure.

## Refuse

- Snapshot collection from uncommitted dirty state for trend analysis.
- Promotion of thresholds without enough comparable samples.
- Treating raw file/line counts as value without classification.

## Guardrails

- Use accepted baselines (committed revisions) for project-level trend.
- Use staged-index diffs for task-level evidence.
- Store compact `repository-audit-delta.md` sections in completed-task archives.
- Mark token telemetry `unknown` when exact counts are unavailable.
- Promote thresholds only after enough comparable samples exist.
- Never edit files based on audit findings without a task card.

## Required Output

Return a structured audit report with:
- snapshot or diff summary;
- file classification breakdown;
- findings by severity and category;
- trend direction (when applicable);
- integration points with task closure.

## Claude Code Integration

When invoked:
- Use `Bash` to run `repository_audit.py` commands.
- Use `Write` to create snapshot files, reports, and archive deltas.
- Use `Read` on existing snapshots and manifest registries before collecting
  new data.
- Use `Grep` to verify that audit deltas reference actual task-scope changes.
- Integrate with `task-scoped-session-closer` for archive-delta insertion
  during task closure.
- Reference `docs/reports/repository-audit/` for accepted snapshot storage.
