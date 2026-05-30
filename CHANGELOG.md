# Changelog

All notable changes to GCS are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- R1 researcher preview package (D1, D2, D3 demo artifacts)
- B1 diagnostic classification expected outputs (5 cases)
- B2 research microbenchmark expected outputs (B2-01, B2-02)
- R2 reproducible build transcript (2026-05-27)
- Researcher contribution boundary document
- 20-minute contributor path
- External solver comparison and benchmark plan
- Fixture corpus maturity ladder
- Agentic-SE task card, validation, and archive pipeline
- Narrative map with 14 narrative lines

### Known Limitations
- `AcceptedWithWarnings` is the expected status for accepted cases; post-local
  diagnostics remain warning-level in the current implementation.
- Under-constrained behavior is inferred from rank/nullity evidence rather than
  a distinct top-level status.
- Over-constrained and inconsistent examples may surface as numeric failure
  until the diagnostic taxonomy is refined.
- R1 is a local researcher preview only; no public binary, installer, or
  package manager workflow is supported.
- The spanning forest plan is contract-only evidence; the reduced numeric task
  path is not yet implemented.

## Versioning

Versions will be tagged starting with the first public release. Until then,
all changes are [Unreleased].
