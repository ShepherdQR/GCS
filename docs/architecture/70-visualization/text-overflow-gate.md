# Text Overflow Gate

Snapshot date: 2026-05-24.

This note records the P5.2 `GCS Visual Integrity Gate` landing for explicit
text-budget checks in generated HTML figures.

Governing conventions:

- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**
- **GCS Warm Evidence Tokens**

## Rule

Dense figure HTML must mark key text containers with:

```html
data-gcs-text-label="..."
data-gcs-text-budget="..."
```

The budget is a source-level rendered-layout budget: it records the maximum
normalized text length allowed for a specific figure container. A later pixel
or browser baseline gate may tighten this with exact rendered measurements,
but P5.2 already prevents unbounded text growth in figure labels, panel
claims, chips, and step cards.

## Tool

`tools/ui_qa/gcs_text_overflow.py` checks:

- every scanned HTML file has text-budget markers;
- every budget is a positive integer;
- normalized text length does not exceed its declared budget.

The tool uses only the Python standard library and is part of the default
agentic quality-gate sequence through:

```text
python.gcs_text_overflow
python.gcs_text_overflow_tests
```

## Current Landing

`tools/architecture_visualization/figure71_html_compositor.py` emits text
budgets for Figure 71:

- figure title and subtitle;
- procedure claim;
- panel title, token chip, and panel claim;
- step focus and step evidence text.

The regenerated Figure 71 HTML currently carries 101 checked budgets.

## Acceptance Evidence

- Current Figure 71 HTML passes the overflow gate.
- A forced over-budget fixture fails.
- An HTML fixture with no budget markers fails.
- The gate and its unit tests are in the default quality-gate sequence.

## Future Gates

P5.2 is intentionally budget-based. P5.3 should add overlap and contrast
checks, and P5.4 should decide a stable screenshot/pixel baseline backend.
