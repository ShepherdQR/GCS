# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in GCS, please report it privately.
Do not open a public issue.

Send a report describing:
- The affected component (kernel, IO, graph, numeric engine, diagnostics, CLI)
- Steps to reproduce, including a minimal fixture if possible
- The observed behavior vs. expected behavior
- Whether the issue is a crash, memory safety violation, undefined behavior,
  or diagnostic misclassification

## Response SLA

- Acknowledgment within 5 business days.
- Status update within 14 business days.
- If accepted, a fix timeline will be communicated.
- If declined, a rationale will be provided.

## Scope

In scope:
- Solver crash or hang on valid input
- Memory safety violations (out-of-bounds access, use-after-free, etc.)
- Undefined behavior that affects solver correctness
- Diagnostic misclassification that could lead to incorrect solver claims
- IO parser vulnerabilities on malformed input

Out of scope:
- Unsupported scene classes (documented limitations)
- Benchmark disagreements or performance comparisons
- Feature requests disguised as security issues
- Build environment or dependency chain issues outside GCS source

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest commit on `main` | Yes |
| Tagged releases (R2+) | Yes, within the release's documented support window |
| R1 researcher preview | Best-effort only |

## Disclosure Policy

- The reporter will be credited in the fix commit and release notes unless they
  request anonymity.
- Public disclosure will occur after a fix is merged and a release note is
  published.
- Critical vulnerabilities may warrant a dedicated security advisory.
