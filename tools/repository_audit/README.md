# GCS Repository Audit

This support tool collects deterministic repository-shape snapshots for GCS.
It is read-only with respect to solver code and uses only the Python standard
library.

## Commands

Collect a JSON snapshot:

```bat
python tools\repository_audit\repository_audit.py collect --output var\repository-audit\latest.snapshot.json
```

Collect a JSON snapshot from a committed revision:

```bat
python tools\repository_audit\repository_audit.py collect --revision HEAD --output docs\reports\repository-audit\2026-05-26\snapshot.json
```

Check a snapshot:

```bat
python tools\repository_audit\repository_audit.py check --snapshot var\repository-audit\latest.snapshot.json
```

Render a Markdown project overview from the current repository:

```bat
python tools\repository_audit\repository_audit.py report --output docs\reports\repository-audit\2026-05-26\README.md
```

Render a Markdown report from a saved snapshot:

```bat
python tools\repository_audit\repository_audit.py report --snapshot var\repository-audit\latest.snapshot.json --output docs\reports\repository-audit\2026-05-26\README.md
```

Compare two saved snapshots:

```bat
python tools\repository_audit\repository_audit.py diff --base-snapshot var\repository-audit\base.snapshot.json --head-snapshot var\repository-audit\head.snapshot.json --output var\repository-audit\diff.json
```

Compare two committed Git revisions:

```bat
python tools\repository_audit\repository_audit.py diff --base HEAD~1 --head HEAD --output var\repository-audit\diff.json
```

Render a Markdown report from a saved diff:

```bat
python tools\repository_audit\repository_audit.py diff-report --diff var\repository-audit\diff.json --output var\repository-audit\diff.md
```

Render a Markdown trend report from two or more snapshots:

```bat
python tools\repository_audit\repository_audit.py trend --snapshot var\repository-audit\base.snapshot.json --snapshot var\repository-audit\head.snapshot.json --output var\repository-audit\trend.md
```

Render the accepted snapshot index:

```bat
python tools\repository_audit\repository_audit.py index --reports-root docs\reports\repository-audit --output docs\reports\repository-audit\README.md
```

Run focused tests:

```bat
python -m unittest tests.tools.test_repository_audit
```

## Scope

The MVP implements:

- `RepositoryAuditSnapshot` JSON output;
- tracked-file collection through `git -c core.quotepath=false ls-files -z`;
- artifact classification;
- basic module inventory joins from `tools/agentic_design/module_inventory.json`;
- Markdown overview report generation;
- JSON diff output for saved snapshots or committed Git revisions;
- Markdown diff report generation from saved JSON diffs;
- Markdown trend report generation from snapshot series;
- accepted snapshot manifests and a registry index under
  `docs/reports/repository-audit/`;
- initial warning/error findings.

It does not implement external adapters, historical charts, token-efficiency
joins, or default quality-gate enforcement yet.
