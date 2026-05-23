#!/usr/bin/env python3
"""Sync supported Inkscape SVG geometry back into Figure 1 layout tokens.

The renderer emits stable ``data-layout-key`` attributes for layout-owned
elements. This script reads an edited SVG, extracts supported group transforms
and rectangle geometry, and writes the values into ``figure1.layout.json``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LAYOUT = Path(__file__).with_name("figure1.layout.json")
DEFAULT_SVG = ROOT / "docs" / "architecture" / "70-visualization" / "assets" / "figure1-gcs-local-to-global.svg"


TRANSLATE_PATTERN = re.compile(
    r"translate\(\s*([-+]?\d*\.?\d+)(?:[\s,]+([-+]?\d*\.?\d+))?\s*\)"
)


BINDINGS = {
    "final.panels.geometry": {
        "kind": "translate",
        "path": "final.panels.geometry",
        "attrs": {"x": "x", "y": "y"},
    },
    "final.panels.incidence": {
        "kind": "translate",
        "path": "final.panels.incidence",
        "attrs": {"x": "x", "y": "y"},
    },
    "final.panels.evidence": {
        "kind": "translate",
        "path": "final.panels.evidence",
        "attrs": {"x": "x", "y": "y"},
    },
    "final.panels.pipeline": {
        "kind": "translate",
        "path": "final.panels.pipeline",
        "attrs": {"x": "x", "y": "y"},
    },
    "final.panels.topos": {
        "kind": "translate",
        "path": "final.panels.topos",
        "attrs": {"x": "x", "y": "y"},
    },
    "final.panels.legend": {
        "kind": "translate",
        "path": "final.panels.legend",
        "attrs": {"x": "x", "y": "y"},
    },
    "panels.geometry.plot": {
        "kind": "rect",
        "path": "panels.geometry.plot",
        "attrs": {"x": "x", "y": "y", "width": "width", "height": "height"},
    },
    "panels.geometry.evidence_card": {
        "kind": "rect",
        "path": "panels.geometry.evidence_card",
        "attrs": {"x": "x", "y": "y", "width": "width", "height": "height"},
    },
    "panels.incidence.site": {
        "kind": "rect",
        "path": "panels.incidence.site",
        "attrs": {"x": "x", "y": "y", "width": "width", "height": "height"},
    },
    "panels.evidence.rank_card": {
        "kind": "rect",
        "path": "panels.evidence.rank_card",
        "attrs": {"x": "x", "y": "y", "width": "width", "height": "height"},
    },
    "panels.topos.columns.0": {
        "kind": "rect",
        "path": "panels.topos.columns.0",
        "attrs": {"x": "x", "y": "y", "width": "width", "height": "height"},
    },
    "panels.topos.columns.1": {
        "kind": "rect",
        "path": "panels.topos.columns.1",
        "attrs": {"x": "x", "y": "y", "width": "width", "height": "height"},
    },
    "panels.topos.columns.2": {
        "kind": "rect",
        "path": "panels.topos.columns.2",
        "attrs": {"x": "x", "y": "y", "width": "width", "height": "height"},
    },
    "panels.topos.gluing_report": {
        "kind": "rect",
        "path": "panels.topos.gluing_report",
        "attrs": {"x": "x", "y": "y", "width": "width", "height": "height"},
    },
    "panels.topos.dictionary": {
        "kind": "rect",
        "path": "panels.topos.dictionary",
        "attrs": {"x": "x", "y": "y", "width": "pill_width", "height": "pill_height"},
    },
}


def read_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def normalized_number(value: float) -> int | float:
    rounded = round(value, 3)
    if abs(rounded - round(rounded)) < 1.0e-9:
        return int(round(rounded))
    return rounded


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def layout_key(element: ElementTree.Element) -> str | None:
    for attr_name, attr_value in element.attrib.items():
        if attr_name.endswith("data-layout-key"):
            return attr_value
    return None


def parse_translate(value: str) -> dict[str, float] | None:
    match = TRANSLATE_PATTERN.search(value)
    if not match:
        return None
    x = float(match.group(1))
    y = float(match.group(2)) if match.group(2) is not None else 0.0
    return {"x": x, "y": y}


def rect_geometry(element: ElementTree.Element) -> dict[str, float]:
    values: dict[str, float] = {}
    for attr in ("x", "y", "width", "height"):
        if attr in element.attrib:
            values[attr] = float(element.attrib[attr])
    return values


def container_at(root: dict[str, object], dotted_path: str) -> dict[str, object]:
    current: object = root
    for part in dotted_path.split("."):
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            if part not in current:
                current[part] = {}
            current = current[part]
        else:
            raise TypeError(f"Cannot descend into {dotted_path}")
    if not isinstance(current, dict):
        raise TypeError(f"{dotted_path} does not resolve to a JSON object")
    return current


def apply_binding(layout: dict[str, object], key: str, element: ElementTree.Element) -> bool:
    binding = BINDINGS[key]
    kind = binding["kind"]
    values: dict[str, float] | None = None
    if kind == "translate":
        transform = element.attrib.get("transform", "")
        values = parse_translate(transform)
        if values is None:
            print(f"warning: {key} has unsupported transform: {transform}", file=sys.stderr)
            return False
    elif kind == "rect":
        if local_name(element.tag) != "rect":
            print(f"warning: {key} is not a rect; skipped", file=sys.stderr)
            return False
        values = rect_geometry(element)
    else:
        raise ValueError(f"Unsupported binding kind: {kind}")

    target = container_at(layout, str(binding["path"]))
    changed = False
    for svg_attr, json_attr in dict(binding["attrs"]).items():
        if svg_attr not in values:
            continue
        new_value = normalized_number(values[svg_attr])
        if target.get(str(json_attr)) != new_value:
            target[str(json_attr)] = new_value
            changed = True
    return changed


def sync_layout(svg_path: Path, layout_path: Path) -> tuple[dict[str, object], int, int]:
    layout = read_json(layout_path)
    tree = ElementTree.parse(svg_path)
    seen = 0
    changed = 0
    for element in tree.iter():
        key = layout_key(element)
        if key not in BINDINGS:
            continue
        seen += 1
        if apply_binding(layout, key, element):
            changed += 1
    return layout, seen, changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync Inkscape-edited SVG geometry into Figure 1 layout JSON.")
    parser.add_argument("--svg", type=Path, default=DEFAULT_SVG, help="Edited SVG path.")
    parser.add_argument("--layout", type=Path, default=DEFAULT_LAYOUT, help="Layout JSON path to update.")
    parser.add_argument("--out", type=Path, help="Optional output JSON path. Defaults to updating --layout.")
    parser.add_argument("--dry-run", action="store_true", help="Print updated JSON without writing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    svg_path = args.svg if args.svg.is_absolute() else ROOT / args.svg
    layout_path = args.layout if args.layout.is_absolute() else ROOT / args.layout
    out_path = args.out if args.out is not None else layout_path
    if out_path is not None and not out_path.is_absolute():
        out_path = ROOT / out_path

    layout, seen, changed = sync_layout(svg_path, layout_path)
    payload = json.dumps(layout, indent=2, ensure_ascii=False) + "\n"
    if args.dry_run:
        print(payload, end="")
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload, encoding="utf-8", newline="\n")
    print(f"layout keys seen: {seen}; changed: {changed}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
