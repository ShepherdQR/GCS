# 14b — Commercialization Path

Status: draft
Date: 2026-05-30
Parent: `docs/narrative-lines/14-business-open-source-strategy/development-plan.md`

## Purpose

This document is a standalone commercialization annex to narrative line 14
(business/open-source strategy). While the main development plan addresses
open-source maturation in general, this annex sketches a concrete commercial
trajectory for when the project decides to pursue revenue or industrial
adoption beyond the researcher audience.

## Preconditions (gates before acting on this plan)

1. At least one real external researcher review archived (P2.1 in the weakness
   plan).
2. At least one real external contribution or simulated friction log (P2.2).
3. Reproducible build transcript published (P1.2).
4. Public distribution decision made (P4.1) — the repo must be public before
   dual licensing or open-core can operate.

## Where GCS Stands Today

- **Technically**: architecture mirrors the commercial solver pattern
  (structural model + behavior model, decomposition before numeric solving,
  first-class diagnostics). The numeric solver is a replaceable baseline.
  3D rigid-set assembly solving is not yet implemented.
- **Market**: zero external validation. No external reviews, no external
  contributions, no benchmark comparisons.
- **Positioning**: researcher-first. The product brief explicitly says "do not
  become a polished commercial CAD product before solver evidence is
  trustworthy."

Commercialization does not replace the researcher strategy — it forks from it
after validation.

## Three Commercial Paths

### Path A: Embedded Solver Component (D-Cubed Model)

License GCS as an embeddable solver library to CAD/CAE vendors.

| Dimension | Assessment |
|-----------|------------|
| Revenue model | Per-seat or per-integration license fee |
| Technical barrier | Very high — requires industrial robustness, multi-platform support, ABI compatibility guarantees, integration SDK |
| Market barrier | Very high — CAD vendors changing solvers is a strategic decision requiring years of trust |
| Fit for GCS? | **Not suitable at current stage.** No industrial deployment record, no integration relationships with CAD vendors |

### Path B: Open-Core + Commercial Extensions

Core solver open-source (Apache 2.0 / MIT). Advanced modules under commercial
license.

| Dimension | Assessment |
|-----------|------------|
| Revenue model | Commercial extension subscriptions + support SLAs |
| Technical barrier | Medium — requires clear core/extension boundary, extensions must justify purchase |
| Market barrier | Medium — open-source community is a natural user funnel, but needs community scale |
| Fit for GCS? | **Viable medium-to-long term.** Researcher route naturally builds community trust. Commercial extensions (high-performance parallel solver, CAD plugins, enterprise integrations) are natural upgrade paths |

Candidate commercial extensions:

- High-performance parallel numeric solver
- CAD plugin integrations (FreeCAD, SolveSpace)
- Enterprise scene management and collaboration
- Industry-specific modules (kinematics, tolerance analysis)
- Priority support SLAs and custom development

### Path C: Dual Licensing

Same codebase. Open-source under copyleft (GPL/AGPL). Commercial license for
proprietary use.

| Dimension | Assessment |
|-----------|------------|
| Revenue model | Commercial license fee |
| Technical barrier | Low — same codebase, only license differs |
| Market barrier | Medium — needs legal infrastructure and clear contributor CLA |
| Fit for GCS? | **Viable near-term.** Lightest commercialization start. No additional product development needed, only legal and license decisions |

Trade-offs:

- GPL prevents commercial closed-source wrapping but may deter some CAD vendor
  integration interest.
- MIT/Apache encourages wider adoption but generates no direct revenue.
- AGPL is stronger for SaaS protection but may be perceived as aggressive.

### Recommended Trajectory: C → B Gradual

```
Phase 0 (current):     Researcher preview, internal repository
Phase 1 (6-12 months): Public open-source (GPL/AGPL), build researcher credibility
Phase 2 (12-18 months): Dual licensing active — commercial license available
Phase 3 (18-24 months): Open-core — identify and develop commercializable extensions
```

## Phase 2b: Commercial Foundation (8-12 weeks after public)

Precondition: at least one real external review archived.

1. **License decision.**
   Choose open-source license (GPL v3, AGPL v3, or Apache 2.0 with commercial
   dual-licensing intent). If copyleft: prepare CLA (Contributor License
   Agreement) template. Document rationale at
   `docs/product/license-decision.md`.

2. **Commercial boundary definition.**
   Define what is "Core GCS" (always open) vs. what could be commercial.
   Core GCS already maps to: kernel, IO, graph, numeric engine, diagnostics.
   Potential commercial surface: enterprise integrations, performance modules,
   industry-specific solvers, support SLAs.

3. **Revenue model draft.**
   Target: annual commercial license per integration seat.
   Secondary: support/consulting revenue for custom solver development.
   Document at `docs/product/commercial-model.md`.

## Phase 4b: Commercial Pilot (12+ weeks after public)

Precondition: public repository, at least one commercial inquiry.

4. **First commercial pilot.**
   One organization integrates GCS under commercial license. Scope: technical
   integration support, SLA, feedback loop. Archive the integration case study
   (anonymized if required).

5. **Pricing calibration.**
   Based on pilot outcome: adjust pricing, support tiers, and commercial
   feature scope. Document at `docs/product/pricing-calibration.md`.

## Risks and Anti-Decay Measures

1. **Do not dilute researcher credibility by pursuing revenue too early.**
   If the open-source community perceives that core features are being held
   back for the commercial edition, researcher adoption will suffer. The
   open-core boundary must be transparent and irreversible.

2. **Do not make commercial decisions without external validation.**
   License choice, pricing, and commercial boundary all depend on real user
   feedback. Before the first external review is archived, commercialization
   discussion is internal projection only.

3. **GCS's commercial value is not "better than D-Cubed."**
   It is explainability, diagnostic transparency, and the agentic-SE governance
   model. These are differentiators that existing commercial solvers do not
   offer.

4. **License virality is a double-edged sword.**
   GPL prevents commercial closed-source wrapping but may block some CAD vendor
   integration interest. MIT/Apache encourages broader adoption but generates
   no direct revenue. AGPL is stronger for SaaS protection but may be perceived
   as aggressive.

5. **The agentic-SE governance model is itself a commercial differentiator.**
   For organizations evaluating solver quality and maintainability, the
   evidence-rich task, validation, and archive pipeline is a signal that raw
   benchmark scores cannot replicate. This should be part of the commercial
   narrative.

## Alignment With Related Narrative Lines

| Related line | Commercialization impact |
|-------------|--------------------------|
| 11 (Product/user) | Commercial user needs will reshape the product roadmap, but must not displace the researcher audience |
| 12 (Release/packaging) | Commercial licensing requires stricter release processes and version semantics |
| 13 (Benchmark/comparison) | Benchmark comparisons in commercial contexts need more careful language — avoid marketing claims |
| 06 (Agentic-SE) | Agentic governance is itself a differentiator; can be part of the commercial narrative |
| 04 (Fixture corpus) | Industrial fixture coverage becomes a commercial asset; may justify proprietary fixture sets |

## Non-Goals

- Do not build a commercial CAD product. GCS is a solver component, not an
  end-user CAD application.
- Do not pursue revenue before solver evidence is trustworthy and externally
  validated.
- Do not hide mathematical or numeric uncertainty for commercial positioning.
- Do not let commercial priorities override the contract architecture and
  quality gate discipline that makes GCS credible in the first place.

## Update Rule

Update this document when:
- A real external review or contribution is archived.
- A license decision is made.
- A commercial inquiry arrives.
- The public distribution decision (P4.1) is executed.
- The narrative map baseline is refreshed and line 14's level changes.
