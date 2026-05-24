#!/usr/bin/env python3
"""Compose Figure 71 as browser-flowed HTML from a semantic figure spec.

The spec file is JSON-compatible YAML, so this first landing stays dependency
free. A future version can switch to real YAML once third-party governance
approves a parser.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPEC = ROOT / "tools" / "architecture_visualization" / "specs" / "figure71.yaml"


@dataclass(frozen=True)
class Step:
    number: int
    status: str
    focus: str
    core: str
    evidence: str


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain an object")
    return data


def load_theme(path: Path) -> dict[str, str]:
    fallback = {
        "ink": "#181715",
        "muted": "#5f5b53",
        "quiet": "#8b867a",
        "rule": "#d8d1c4",
        "rule_soft": "#ece7dd",
        "panel": "#fffefa",
        "paper": "#f7f4ec",
        "surface": "#fffdf7",
        "domain": "#e7edf8",
        "domain_stroke": "#435f8c",
        "graph": "#efe7f3",
        "graph_stroke": "#765d87",
        "planner": "#e3f0e4",
        "planner_stroke": "#477861",
        "numeric": "#edf2df",
        "numeric_stroke": "#5e7d43",
        "diagnostic": "#f6e7cf",
        "diagnostic_stroke": "#a36b32",
        "failure": "#f3ddd7",
        "failure_stroke": "#a94c43",
        "boundary": "#efede6",
        "boundary_stroke": "#777166",
        "accent": "#c8643f",
        "point": "#334c78",
        "constraint": "#b97834",
        "ok": "#4b8a64",
    }
    if not path.exists():
        return fallback
    raw = load_json(path)
    colors = raw.get("colors", {})
    if not isinstance(colors, dict):
        return fallback
    merged = dict(fallback)
    merged.update({str(key): str(value) for key, value in colors.items()})
    return merged


def parse_steps(report_path: Path) -> list[Step]:
    steps: list[Step] = []
    for line in report_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not cells[0].isdigit():
            continue
        steps.append(Step(
            number=int(cells[0]),
            status=cells[1],
            focus=cells[2],
            core=cells[3],
            evidence=cells[4],
        ))
    return steps


def steps_for_arc(steps: Iterable[Step], arc: dict[str, object]) -> list[Step]:
    raw_range = arc.get("range", [])
    if not isinstance(raw_range, list) or len(raw_range) != 2:
        return []
    start, end = int(raw_range[0]), int(raw_range[1])
    return [step for step in steps if start <= step.number <= end]


def root_path(path_value: object) -> Path:
    path = Path(str(path_value))
    return path if path.is_absolute() else ROOT / path


def token_style(token: str, colors: dict[str, str]) -> str:
    fill = colors.get(token, colors["surface"])
    stroke = colors.get(f"{token}_stroke", colors["rule"])
    return f"--token-fill:{fill};--token-stroke:{stroke};"


def render_step(step: Step, colors: dict[str, str]) -> str:
    done = step.status.lower() == "done"
    status_class = "done" if done else "pending"
    marker = (
        '<span class="status-mark" aria-label="done"></span>'
        if done else '<span class="pending-mark" aria-label="pending"></span>'
    )
    return f"""
      <article class="step-card {status_class}">
        <div class="step-head">
          <span class="step-number">{step.number}</span>
          {marker}
        </div>
        <h4>{escape(step.focus)}</h4>
        <p>{escape(step.evidence)}</p>
      </article>
    """


def render_arc(arc: dict[str, object], arc_steps: list[Step], colors: dict[str, str]) -> str:
    token = str(arc.get("token", "boundary"))
    panel_type = str(arc.get("panel_type", "module-grid"))
    title = str(arc.get("title", "Untitled"))
    claim = str(arc.get("claim", ""))
    range_label = ""
    raw_range = arc.get("range", [])
    if isinstance(raw_range, list) and len(raw_range) == 2:
        range_label = f"Steps {raw_range[0]}-{raw_range[1]}"
    elif str(arc.get("id")) == "showcase":
        range_label = "after Step 40"
    cards = "\n".join(render_step(step, colors) for step in arc_steps)
    if panel_type == "domain-sketch":
        cards = render_showcase(colors)
    return f"""
    <section class="panel panel-{escape(str(arc.get('id', 'panel')))} {escape(panel_type)}" style="{token_style(token, colors)}">
      <header class="panel-header">
        <div>
          <p class="panel-kicker">{escape(range_label)}</p>
          <h2>{escape(title)}</h2>
        </div>
        <span class="token-chip">{escape(token)}</span>
      </header>
      <p class="panel-claim">{escape(claim)}</p>
      <div class="panel-body">
        {cards}
      </div>
    </section>
    """


def render_showcase(colors: dict[str, str]) -> str:
    return f"""
      <div class="showcase-layout">
        <svg class="domain-sketch-svg" viewBox="0 0 260 170" role="img" aria-label="showcase constraint sketch">
          <rect x="10" y="10" width="120" height="120" rx="20" fill="{colors['planner']}" stroke="{colors['planner_stroke']}" stroke-dasharray="5 5"/>
          <rect x="90" y="28" width="130" height="112" rx="20" fill="{colors['domain']}" stroke="{colors['domain_stroke']}" stroke-dasharray="5 5"/>
          <path d="M55 120 L118 48 L198 118 L124 142 Z" fill="none" stroke="{colors['constraint']}" stroke-width="3"/>
          <path d="M55 120 L198 118" fill="none" stroke="{colors['failure_stroke']}" stroke-width="2.5" stroke-dasharray="6 5"/>
          <circle cx="55" cy="120" r="8" fill="{colors['point']}"/>
          <circle cx="118" cy="48" r="8" fill="{colors['point']}"/>
          <circle cx="198" cy="118" r="8" fill="{colors['point']}"/>
          <circle cx="124" cy="142" r="8" fill="{colors['point']}"/>
        </svg>
        <div class="evidence-stack">
          <span>free rank <strong>8 / 10</strong></span>
          <span>frozen cols <strong>2</strong></span>
          <span>gluing <strong>ok</strong></span>
          <span>obstruction <strong>variant</strong></span>
        </div>
      </div>
    """


def css(colors: dict[str, str]) -> str:
    return f"""
    :root {{
      --ink: {colors['ink']};
      --muted: {colors['muted']};
      --quiet: {colors['quiet']};
      --rule: {colors['rule']};
      --rule-soft: {colors['rule_soft']};
      --paper: {colors['paper']};
      --panel: {colors['panel']};
      --surface: {colors['surface']};
      --accent: {colors['accent']};
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: "Anthropic Sans", Inter, "Segoe UI", Arial, sans-serif;
    }}
    .figure-shell {{
      inline-size: min(1600px, 100vw);
      margin: 0 auto;
      padding: 48px;
    }}
    .figure-title {{
      display: flex;
      justify-content: space-between;
      gap: 28px;
      align-items: end;
      border-bottom: 1px solid var(--rule);
      padding-block-end: 22px;
    }}
    h1 {{
      margin: 0;
      font-family: "Anthropic Serif", Georgia, Cambria, serif;
      font-size: clamp(30px, 3vw, 48px);
      line-height: 1.02;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin: 10px 0 0;
      color: var(--muted);
      font-size: 15px;
      max-inline-size: 820px;
      line-height: 1.45;
    }}
    .meta {{
      color: var(--muted);
      font-size: 12px;
      text-align: right;
      min-inline-size: 240px;
    }}
    .claim-band {{
      margin-block: 26px;
      padding: 18px 20px;
      border: 1px solid var(--rule);
      border-radius: 8px;
      background: var(--surface);
    }}
    .claim-band p {{
      margin: 6px 0 0;
      font-size: clamp(17px, 1.4vw, 22px);
      font-weight: 650;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }}
    .claim-label {{
      margin: 0;
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .figure-grid {{
      display: grid;
      grid-template-columns: repeat(12, minmax(0, 1fr));
      gap: 22px;
      align-items: stretch;
    }}
    .panel {{
      min-block-size: 290px;
      border: 1px solid var(--rule);
      border-radius: 8px;
      background: var(--panel);
      padding: 22px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .panel-foundation {{ grid-column: span 4; }}
    .panel-algorithm {{ grid-column: span 4; }}
    .panel-scene_generation {{ grid-column: span 4; }}
    .panel-rank_spine {{ grid-column: span 5; }}
    .panel-closure {{ grid-column: span 3; }}
    .panel-showcase {{ grid-column: span 4; }}
    .panel-header {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: start;
    }}
    .panel-kicker {{
      margin: 0 0 5px;
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
    }}
    h2 {{
      margin: 0;
      font-size: 19px;
      line-height: 1.16;
      letter-spacing: 0;
    }}
    .panel-claim {{
      margin: 0;
      color: var(--muted);
      line-height: 1.4;
      overflow-wrap: anywhere;
    }}
    .token-chip {{
      flex: none;
      border: 1px solid var(--token-stroke);
      background: var(--token-fill);
      color: var(--token-stroke);
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 11px;
      font-weight: 700;
    }}
    .panel-body {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(132px, 1fr));
      gap: 10px;
      margin-block-start: auto;
    }}
    .step-card {{
      min-block-size: 86px;
      border: 1px solid var(--token-stroke);
      border-radius: 7px;
      background: color-mix(in srgb, var(--token-fill) 66%, white);
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      overflow-wrap: anywhere;
    }}
    .step-card.pending {{
      background: var(--surface);
      border-style: dashed;
    }}
    .step-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
    }}
    .step-number {{
      color: var(--token-stroke);
      font-weight: 750;
      font-size: 13px;
    }}
    .status-mark,
    .pending-mark {{
      inline-size: 16px;
      block-size: 16px;
      flex: none;
      border-radius: 50%;
      border: 1px solid var(--token-stroke);
      background: var(--panel);
    }}
    .status-mark::after {{
      content: "";
      display: block;
      inline-size: 8px;
      block-size: 4px;
      border-inline-start: 2px solid var(--token-stroke);
      border-block-end: 2px solid var(--token-stroke);
      transform: rotate(-45deg);
      margin: 4px 0 0 3px;
    }}
    .pending-mark {{
      border-style: dashed;
    }}
    h4 {{
      margin: 0;
      font-size: 11px;
      line-height: 1.2;
    }}
    .step-card p {{
      margin: 0;
      color: var(--muted);
      font-size: 10px;
      line-height: 1.25;
    }}
    .evidence-spine .panel-body {{
      grid-template-columns: 1fr;
    }}
    .horizon .panel-body {{
      grid-template-columns: 1fr;
    }}
    .showcase-layout {{
      display: grid;
      grid-template-columns: minmax(180px, 1.4fr) minmax(120px, .8fr);
      gap: 16px;
      align-items: center;
    }}
    .domain-sketch-svg {{
      inline-size: 100%;
      block-size: auto;
      border: 1px solid var(--rule-soft);
      border-radius: 8px;
      background: #fbfaf5;
    }}
    .evidence-stack {{
      display: grid;
      gap: 9px;
    }}
    .evidence-stack span {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      border: 1px solid var(--rule-soft);
      border-radius: 7px;
      padding: 9px 10px;
      background: var(--surface);
      color: var(--muted);
      font-size: 12px;
    }}
    .evidence-stack strong {{
      color: var(--ink);
    }}
    @media (max-width: 1100px) {{
      .figure-shell {{ padding: 28px; }}
      .figure-title {{ align-items: start; flex-direction: column; }}
      .meta {{ text-align: left; min-inline-size: 0; }}
      .panel-foundation,
      .panel-algorithm,
      .panel-scene_generation,
      .panel-rank_spine,
      .panel-closure,
      .panel-showcase {{ grid-column: 1 / -1; }}
    }}
    """


def render_html(spec: dict[str, object], steps: list[Step], colors: dict[str, str]) -> str:
    arcs = spec.get("arcs", [])
    if not isinstance(arcs, list):
        raise ValueError("spec arcs must be a list")
    arc_markup = "\n".join(
        render_arc(arc, steps_for_arc(steps, arc), colors)
        for arc in arcs
        if isinstance(arc, dict)
    )
    title = str(spec.get("title", "GCS Figure"))
    subtitle = str(spec.get("subtitle", ""))
    done_count = sum(1 for step in steps if step.status.lower() == "done")
    claim = "canonical contracts -> executable solver evidence -> public promotion gates -> viewer-visible diagnostics -> post-Step-40 showcase"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>{css(colors)}</style>
</head>
<body>
  <main class="figure-shell" data-figure-id="{escape(spec.get('id', 'figure'))}">
    <header class="figure-title">
      <div>
        <h1>Figure 71 | {escape(title)}</h1>
        <p class="subtitle">{escape(subtitle)}</p>
      </div>
      <p class="meta">Source: {escape(spec.get('source_report', ''))}<br>{done_count} done / {len(steps) - done_count} pending</p>
    </header>
    <section class="claim-band">
      <p class="claim-label">Procedure claim</p>
      <p>{escape(claim)}</p>
    </section>
    <section class="figure-grid" aria-label="Figure 71 panels">
      {arc_markup}
    </section>
  </main>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compose Figure 71 as HTML/CSS from its semantic spec.")
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC, help="JSON-compatible YAML figure spec.")
    parser.add_argument("--out", type=Path, help="Output HTML path. Defaults to spec exports.html.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spec_path = args.spec if args.spec.is_absolute() else ROOT / args.spec
    spec = load_json(spec_path)
    report_path = root_path(spec["source_report"])
    theme_path = root_path(spec.get("theme", ""))
    out_path = args.out
    if out_path is None:
        exports = spec.get("exports", {})
        if not isinstance(exports, dict) or "html" not in exports:
            raise ValueError("spec must define exports.html when --out is omitted")
        out_path = root_path(exports["html"])
    elif not out_path.is_absolute():
        out_path = ROOT / out_path
    steps = parse_steps(report_path)
    colors = load_theme(theme_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = render_html(spec, steps, colors)
    payload = "\n".join(line.rstrip() for line in payload.splitlines()) + "\n"
    out_path.write_text(payload, encoding="utf-8", newline="\n")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
