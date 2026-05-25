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
- initial warning/error findings.

It does not implement report generation, diff mode, external adapters, or
default quality-gate enforcement yet.
