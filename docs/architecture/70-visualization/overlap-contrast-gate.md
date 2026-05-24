# Overlap And Contrast Gate

Snapshot date: 2026-05-24.

This note records the P5.3 `GCS Visual Integrity Gate` landing for explicit
layout-box overlap and color-contrast checks in generated HTML figures.

Governing conventions:

- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**
- **GCS Warm Evidence Tokens**

## Rule

Generated figure HTML should expose QA metadata for the visual regions and text
contrast targets that matter:

```html
data-gcs-box-label="..."
data-gcs-box-group="..."
data-gcs-box="x,y,width,height"
data-gcs-contrast-label="..."
data-gcs-contrast-fg="#181715"
data-gcs-contrast-bg="#f7f4ec"
data-gcs-contrast-min="4.5"
```

The box coordinates are deterministic design-grid boxes, not screenshots. They
guard the figure's declared layout contract until P5.4 adds screenshot
baselines.

## Tool

`tools/ui_qa/gcs_overlap_contrast.py` checks:

- every scanned HTML file has layout-box markers;
- boxes in the same group do not overlap;
- every scanned HTML file has contrast markers;
- contrast ratios meet each marker's declared minimum.

The tool uses only the Python standard library and is part of the default
agentic quality-gate sequence through:

```text
python.gcs_overlap_contrast
python.gcs_overlap_contrast_tests
```

## Current Landing

`tools/architecture_visualization/figure71_html_compositor.py` emits:

- six Figure 71 panel boxes in the `figure71-grid` group;
- contrast markers for figure title, subtitle, procedure claim, panel titles,
  panel claims, and token chips.

The regenerated Figure 71 HTML currently checks six boxes and 21 contrast
targets.

## Acceptance Evidence

- Current Figure 71 HTML passes overlap and contrast checks.
- A forced overlap fixture fails.
- A forced low-contrast fixture fails.
- A missing-marker fixture fails.
- The gate and its unit tests are in the default quality-gate sequence.

## Future Gates

P5.3 is a source-level layout/contrast gate. P5.4 should add screenshot
baselines so browser-rendered pixels are checked as well.
