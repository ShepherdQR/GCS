# Claude-Influenced UI Aesthetic Research For GCS Visualization

Research snapshot: 2026-05-24.

## Sources

- [Claude MCP Apps design guidelines](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines)
- [Introducing Claude Design by Anthropic Labs](https://www.anthropic.com/news/claude-design-anthropic-labs?pubDate=20260517)
- [Get started with Claude Design](https://support.claude.com/en/articles/14604416-get-started-with-claude-design)
- [Anthropic Brand Guidelines typography](https://brand.anthropic.com/typography)
- [TASTE: A Designer-Annotated Multi-Dimensional Preference Dataset for AI-Generated Graphic Design](https://arxiv.org/abs/2605.20731)

## Current Aesthetic Diagnosis

The first GCS Figure 1 solved the information architecture problem but still
looked like a technical diagram generator output:

- The palette was dominated by cool whites, blues, and generic diagram colors.
- Panels were visually correct but not emotionally calibrated; the page felt
  more like documentation scaffolding than a deliberate scientific product.
- Typography used a single sans-serif voice everywhere, which made the title,
  panel labels, evidence captions, and mathematical contract names feel too
  similar.
- Semantic colors were present, but not curated into a brand-level visual
  system.
- The diagram had good structure, but not enough editorial atmosphere: no
  warm paper, no quiet typographic contrast, no sense of authored taste.

## Claude / Anthropic Design Direction

The current Claude design language is not simply "beige background and orange
accent." The deeper pattern is:

- Warm, quiet neutrals instead of sterile white or saturated tech gradients.
- Near-black text rather than pure black, with secondary text in warm gray.
- Small, meaningful accent colors used as status or identity, not decoration.
- A restrained typographic system: few sizes, few weights, generous breathing
  room.
- Native-feeling surfaces: subtle borders, limited radius, no heavy shadow
  theatre.
- Conversational iteration around design systems: Claude Design emphasizes
  brand-system inheritance, inline refinement, export/handoff, and feedback
  loops rather than one-shot visual generation.
- Taste is multidimensional. The TASTE design-evaluation work is a useful
  warning: typography, hierarchy, color harmony, layout, and brief fidelity
  must be judged separately instead of collapsed into "looks good."

For GCS, the right adaptation is "scientific Claude": warm editorial clarity,
not consumer-chat cosplay.

## Design Principles For GCS Architecture Figures

1. Use a warm scientific paper surface, but avoid a one-note beige theme.
2. Let typography carry authority: serif or humanist title, restrained sans
   captions, and compact tabular evidence.
3. Keep semantic colors stable:
   - model truth: muted blue;
   - incidence/site: muted violet;
   - cover/gluing: sage;
   - numeric evidence: olive;
   - reports/decision: ochre;
   - obstruction/failure: terracotta;
   - boundaries: warm gray.
4. Prefer thin borders and flat surfaces over gradients, glow, or decorative
   blobs.
5. Make every color justify itself as a contract meaning.
6. Show advanced mathematics through data contracts and visual structure,
   not by adding abstract mathematical ornament.

## Applied Changes To Figure 1

The visualization script now uses a Claude-influenced editorial palette:

- warm paper and panel surfaces;
- near-black ink and warm secondary text;
- curated semantic accents instead of default blue/green/yellow;
- serif-capable figure title and humanist sans body text;
- smaller panel radius and subtler borders;
- more refined diagram fills for domain, site, planning, numeric, diagnostics,
  and obstruction states.

The architecture content remains unchanged: Mermaid atlas is still the
structural source; generated SVG is the editorial artifact.

## Ongoing Aesthetic Gate

Before accepting a future architecture figure, check it on five axes:

- Hierarchy: can a reader tell the main claim in 5 seconds?
- Color: does every accent encode a contract meaning?
- Typography: are title, panel headers, labels, and data visually distinct?
- Density: does the diagram feel rich without becoming crowded?
- Fidelity: does it express GCS local-to-global semantics, not a generic
  software pipeline?
