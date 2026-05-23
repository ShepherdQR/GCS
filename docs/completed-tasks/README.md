# Completed Tasks

This directory stores durable records for completed project tasks. Each task
gets its own folder so the archive can grow without turning into a single
chronological scratchpad.

## Folder Contract

Use this shape for every completed task:

```text
docs/completed-tasks/
  YYYY-MM-DD-short-task-slug/
    README.md
    artifacts.md      # optional, when the task has many generated assets
    evidence.md       # optional, when validation output is worth preserving
```

The task `README.md` should answer:

- what problem the task solved;
- what durable files, scripts, docs, or assets were produced;
- what validation was run;
- what commits or branches matter;
- what follow-up work remains.

Do not store raw chat logs here. Preserve decisions, outputs, acceptance
evidence, and links to project files.

## Index

| Date | Task | Status |
| --- | --- | --- |
| 2026-05-24 | [GCS architecture visualization and SVG editing workflow](2026-05-24-gcs-architecture-visualization-svg-workflow/README.md) | done |
