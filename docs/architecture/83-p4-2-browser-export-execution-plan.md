# P4.2 Browser Export Execution Plan

Snapshot date: 2026-05-24.

Governing conventions:

- **GCS Quiet Technical Atelier**
- **GCS Warm Evidence Tokens**
- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**

## Objective

Add a thin, dependency-light browser export smoke for Figure 71 so the
tokenized HTML compositor can produce reviewable PNG/PDF artifacts when a
local Chrome, Edge, or Chromium CLI is available.

## Step 47A Definition

This work is named **P4.2 / Step 47A: Browser Export Smoke** to avoid
colliding with the separate runtime **Step 47** replay evidence export task.

Step 47A owns only figure-pipeline export readiness:

- source of truth: semantic figure spec plus HTML compositor;
- editable artifact: HTML/CSS;
- review artifacts: PNG/PDF when browser CLI exists;
- evidence artifact: browser export manifest;
- fallback: skipped manifest with explicit missing-tool reason.

## Execution Sequence

1. Create the task card and identify P4.2 acceptance gates.
2. Add `browser_export.py` as a small export tool, not a broad rendering
   framework.
3. Add manifest paths to `figure71.yaml`.
4. Teach `figure_qa.py` to verify the browser smoke manifest when the spec
   requires it.
5. Run the task-card validator, Python syntax checks, browser smoke, figure QA,
   and whitespace diff check.
6. Archive the completed task, update P4/P5 roadmap docs, and forge one
   Bladesmith lesson.
7. Commit and push only the P4.2 files.

## P4.2 Completion Test

P4.2 is complete when:

- the script can export through an installed Chromium CLI or produce a skipped
  manifest without failing the whole figure pipeline;
- the manifest confirms canonical `--gcs-*` token presence in the HTML source;
- Figure 71 QA reads the manifest and fails if token proof is missing;
- roadmap docs name P5.1 token lint as the next preferred implementation step.

## Updated Follow-Up Bias

After P4.2, the next step should be **P5.1 Token Lint Gate**, because token
linting is cheaper than rebuilding visual assets and protects P4.4 from
drifting back into raw colors.
