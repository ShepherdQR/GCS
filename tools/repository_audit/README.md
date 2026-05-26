# GCS Repository Audit

This support tool collects deterministic repository-shape snapshots for GCS.
It is read-only with respect to solver code and uses only the Python standard
library.

## Commands

Collect a JSON snapshot:

```bat
python tools\repository_audit\repository_audit.py collect --output var\repository-audit\latest.snapshot.json
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
- initial warning/error findings.

It does not implement external adapters, historical trend charts, or default
quality-gate enforcement yet.
