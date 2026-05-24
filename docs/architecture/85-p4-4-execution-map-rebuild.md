# P4.4 Execution-Map Figure Rebuild

Snapshot date: 2026-05-24.

Governing conventions:

- **GCS Scientific Figure Pipeline**
- **GCS Warm Evidence Tokens**
- **GCS Visual Integrity Gate**
- **GCS Art Director Review**

## Result

Figure 71 is now displayed from the browser-rendered review artifact produced
by the repo-native scientific figure pipeline:

- source spec: `tools/architecture_visualization/specs/figure71.yaml`
- editable artifact:
  `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.html`
- review PNG:
  `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.review.png`
- review PDF:
  `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.review.pdf`
- browser manifest:
  `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-browser-export.json`
- QA report:
  `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.qa.json`

The old coordinate-drawn SVG remains in the asset folder only as a historical
prototype. It is no longer the display artifact embedded by
`docs/architecture/71-step-1-40-execution-report.md`.

## Rebuild Notes

The first direct browser export attempt refreshed the review artifacts but did
not return cleanly in this Windows desktop session. P4.4 therefore added
`--reuse-existing-artifacts` to `browser_export.py` so constrained sessions can
refresh the manifest from already produced PNG/PDF artifacts while still
checking canonical HTML token presence.

This mode does not replace a real browser export. It is a manifest refresh
fallback for cases where a browser CLI produces files but the shell process
does not exit cleanly.

## Validation

Commands:

```text
python -B tools\ui_qa\gcs_token_lint.py
python -B tools\architecture_visualization\browser_export.py --figure figure71 --formats png,pdf --render-html --reuse-existing-artifacts
python -B tools\architecture_visualization\figure_qa.py --figure figure71
python -m unittest tests.tools.test_browser_export
python -m unittest tests.tools.test_agentic_toolkit
```

Observed evidence:

- token lint passed;
- manifest status is `exported`;
- manifest backend is `existing-artifacts`;
- PNG and PDF review artifacts exist;
- Figure 71 QA passed all schema, coverage, HTML, token, browser manifest, and
  artifact checks;
- the review PNG was visually inspected after regeneration.

## Downstream Update

- P4 can now close after a short phase summary.
- P5.2/P5.3 should add rendered overflow, overlap, and contrast gates before
  the showcase figure is treated as final-quality evidence.
- P6.4 should judge Figma MCP after the repo-native path is stable enough to
  show what external design tooling would add.
