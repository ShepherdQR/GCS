# GCS Session Efficiency

This support tool renders non-blocking session-efficiency reports from durable
JSON records. It does not infer exact token counts and does not define solver
policy.

## Commands

Render a report:

```bat
python tools\session_efficiency\session_efficiency.py report --record docs\reports\session-efficiency\2026-05-26\session-efficiency.json --output docs\reports\session-efficiency\2026-05-26\README.md
```

Write an enriched JSON record with derived metrics:

```bat
python tools\session_efficiency\session_efficiency.py enrich --record docs\reports\session-efficiency\2026-05-26\session-efficiency.json --output var\session-efficiency\latest.enriched.json
```

## Policy

- Unknown token counts are allowed and reported as `n/a` for value-per-token
  fields.
- Compare records inside similar task classes only.
- Review repository-audit deltas, closure score, and validation evidence
  alongside any token metric.
