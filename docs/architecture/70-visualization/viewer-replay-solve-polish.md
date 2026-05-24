# Viewer Replay And Solve Polish

Snapshot date: 2026-05-24.

This note completes the documentation part of P3.4. It records the transient
replay and solve evidence polish applied to the Tk viewer.

Governing conventions:

- **GCS Evidence-First Interface Grammar**
- **GCS Warm Evidence Tokens**
- **GCS Visual Integrity Gate**

## Changes

- Replay and solve rail labels now keep widget references so transient state
  can set foreground colors from `STATE_COLORS`.
- Solve summaries use consistent labels: `Solving`, `Solved`, `Solve warning`,
  `Solve error`, and `Solve status`.
- Solve warning summaries put violation evidence first before global status.
- Replay messages use consistent phrasing: `Replay starting`, `Replay step`,
  and `Replay complete`.

## Boundary

This is UI evidence polish only:

- no solver command behavior changed;
- no history replay persistence changed;
- no scene schema changed;
- no renderer mutation ownership changed.

P4/P5 can later promote the same state vocabulary into figure QA and screenshot
baselines.
