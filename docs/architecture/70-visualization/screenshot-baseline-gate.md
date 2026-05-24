# Screenshot Baseline Gate

Governing conventions:

- **GCS Visual Integrity Gate**
- **GCS Scientific Figure Pipeline**
- **GCS Warm Evidence Tokens**

P5.4 defines the first stable screenshot-baseline policy for GCS visual
artifacts. The policy is intentionally repo-native: a committed manifest records
the expected PNG path, dimensions, byte count, minimum byte count, and SHA256
digest, and a standard-library checker verifies those facts during default
quality gates.

## Baseline Manifest

The source of truth is:

- `docs/architecture/70-visualization/assets/screenshot-baselines.json`

The first baseline is:

- `figure71.execution_map.review_png.desktop_1600x2200`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.review.png`

That artifact is the browser-rendered Figure 71 review PNG promoted during
P4.4. It gives P5 a concrete pixel artifact without introducing a new browser,
Figma, or visual-regression service dependency.

## Checker

Run:

```bat
python -B tools\ui_qa\gcs_screenshot_baseline.py
```

The checker validates:

- manifest schema version;
- at least one baseline entry;
- unique baseline IDs;
- PNG signature and IHDR dimensions;
- exact width, height, byte count, and SHA256 digest;
- minimum byte count, to catch accidental tiny placeholder exports.

## Change Rule

Baseline updates must be deliberate. If a screenshot changes, the update must
include:

- the task card that names the intended visual change;
- archive evidence explaining why the new baseline is better or necessary;
- visual-integrity checks for token lint, text overflow, overlap/contrast, and
  screenshot baseline validation;
- roadmap updates that state whether the change affects future P6 showcase or
  Figma MCP decisions.

## Boundary

This is not a perceptual pixel-diff backend. It is the first stable contract for
review artifacts. A future backend may compare rendered pixels or perceptual
hashes, but it should read the same manifest family rather than inventing a
separate screenshot registry.
