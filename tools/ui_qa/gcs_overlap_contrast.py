from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HTML_PATHS = [
    REPO_ROOT
    / "docs"
    / "architecture"
    / "70-visualization"
    / "assets"
    / "figure71-gcs-step-1-40-evidence-map.html",
    REPO_ROOT
    / "docs"
    / "architecture"
    / "70-visualization"
    / "assets"
    / "figure72-gcs-integrated-showcase-scene.html",
]


@dataclass(frozen=True)
class LayoutBox:
    label: str
    group: str
    x: float
    y: float
    width: float
    height: float
    line: int

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height


@dataclass(frozen=True)
class ContrastTarget:
    label: str
    foreground: str
    background: str
    minimum: float
    line: int


@dataclass
class OverlapContrastResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    boxes_checked: int = 0
    contrast_checked: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors


class IntegrityParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.boxes: list[LayoutBox] = []
        self.contrasts: list[ContrastTarget] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value for key, value in attrs}
        line, _ = self.getpos()
        if "data-gcs-box" in values:
            box = parse_box(
                values.get("data-gcs-box") or "",
                values.get("data-gcs-box-label") or f"{tag}-line-{line}",
                values.get("data-gcs-box-group") or "default",
                line,
            )
            if isinstance(box, str):
                self.errors.append(box)
            else:
                self.boxes.append(box)
        if "data-gcs-contrast-fg" in values or "data-gcs-contrast-bg" in values:
            target = parse_contrast(values, tag, line)
            if isinstance(target, str):
                self.errors.append(target)
            else:
                self.contrasts.append(target)


def parse_box(raw: str, label: str, group: str, line: int) -> LayoutBox | str:
    try:
        values = [float(part.strip()) for part in raw.split(",")]
    except ValueError:
        return f"line {line}: {label} has invalid data-gcs-box {raw!r}"
    if len(values) != 4:
        return f"line {line}: {label} data-gcs-box must have four numbers"
    x, y, width, height = values
    if width <= 0 or height <= 0:
        return f"line {line}: {label} box width and height must be positive"
    return LayoutBox(label=label, group=group, x=x, y=y, width=width, height=height, line=line)


def parse_contrast(values: dict[str, str | None], tag: str, line: int) -> ContrastTarget | str:
    label = values.get("data-gcs-contrast-label") or f"{tag}-line-{line}"
    foreground = values.get("data-gcs-contrast-fg") or ""
    background = values.get("data-gcs-contrast-bg") or ""
    if not is_hex_color(foreground) or not is_hex_color(background):
        return f"line {line}: {label} contrast colors must be #RRGGBB values"
    try:
        minimum = float(values.get("data-gcs-contrast-min") or "4.5")
    except ValueError:
        return f"line {line}: {label} has invalid contrast minimum"
    return ContrastTarget(
        label=label,
        foreground=foreground,
        background=background,
        minimum=minimum,
        line=line,
    )


def is_hex_color(value: str) -> bool:
    if len(value) != 7 or not value.startswith("#"):
        return False
    return all(char in "0123456789abcdefABCDEF" for char in value[1:])


def boxes_overlap(left: LayoutBox, right: LayoutBox) -> bool:
    return (
        left.x < right.right
        and left.right > right.x
        and left.y < right.bottom
        and left.bottom > right.y
    )


def color_channel(value: str) -> tuple[float, float, float]:
    raw = value.lstrip("#")
    return tuple(int(raw[index:index + 2], 16) / 255.0 for index in (0, 2, 4))


def linear(channel: float) -> float:
    if channel <= 0.03928:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def contrast_ratio(foreground: str, background: str) -> float:
    fg = color_channel(foreground)
    bg = color_channel(background)
    fg_luminance = 0.2126 * linear(fg[0]) + 0.7152 * linear(fg[1]) + 0.0722 * linear(fg[2])
    bg_luminance = 0.2126 * linear(bg[0]) + 0.7152 * linear(bg[1]) + 0.0722 * linear(bg[2])
    lighter = max(fg_luminance, bg_luminance)
    darker = min(fg_luminance, bg_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def repo_relative(path: Path, repo_root: Path = REPO_ROOT) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def iter_html_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file() and path.suffix.lower() in {".html", ".htm"}:
            yield path
        elif path.is_dir():
            for candidate in path.rglob("*"):
                if candidate.is_file() and candidate.suffix.lower() in {".html", ".htm"}:
                    yield candidate


def parse_integrity(path: Path) -> IntegrityParser:
    parser = IntegrityParser()
    parser.feed(path.read_text(encoding="utf-8-sig"))
    parser.close()
    return parser


def run_checks(paths: Iterable[Path] | None = None,
               repo_root: Path = REPO_ROOT) -> OverlapContrastResult:
    result = OverlapContrastResult()
    html_paths = list(iter_html_files(paths or DEFAULT_HTML_PATHS))
    if not html_paths:
        result.errors.append("No HTML files were found for overlap/contrast checks")
        return result

    for path in html_paths:
        parser = parse_integrity(path)
        for error in parser.errors:
            result.errors.append(f"{repo_relative(path, repo_root)}: {error}")
        if not parser.boxes:
            result.errors.append(f"{repo_relative(path, repo_root)}: no data-gcs-box markers found")
        if not parser.contrasts:
            result.errors.append(f"{repo_relative(path, repo_root)}: no data-gcs-contrast markers found")
        result.boxes_checked += len(parser.boxes)
        result.contrast_checked += len(parser.contrasts)
        check_box_overlaps(path, parser.boxes, result, repo_root)
        check_contrast_targets(path, parser.contrasts, result, repo_root)
    return result


def check_box_overlaps(path: Path,
                       boxes: list[LayoutBox],
                       result: OverlapContrastResult,
                       repo_root: Path) -> None:
    for index, left in enumerate(boxes):
        for right in boxes[index + 1:]:
            if left.group != right.group:
                continue
            if boxes_overlap(left, right):
                result.errors.append(
                    f"{repo_relative(path, repo_root)}:{right.line}: "
                    f"layout boxes overlap in group {left.group!r}: {left.label!r} and {right.label!r}"
                )


def check_contrast_targets(path: Path,
                           targets: list[ContrastTarget],
                           result: OverlapContrastResult,
                           repo_root: Path) -> None:
    for target in targets:
        ratio = contrast_ratio(target.foreground, target.background)
        if ratio < target.minimum:
            result.errors.append(
                f"{repo_relative(path, repo_root)}:{target.line}: "
                f"{target.label} contrast is {ratio:.2f}, expected >= {target.minimum:.1f}"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check GCS HTML overlap and contrast markers")
    parser.add_argument("paths", nargs="*", type=Path, help="HTML files or directories to scan")
    args = parser.parse_args(argv)

    result = run_checks(args.paths if args.paths else DEFAULT_HTML_PATHS)
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.ok:
        print(
            f"GCS overlap/contrast checks passed "
            f"({result.boxes_checked} boxes, {result.contrast_checked} contrast targets)"
        )
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
