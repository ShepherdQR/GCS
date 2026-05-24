from __future__ import annotations

import argparse
import ast
import importlib.util
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
COLOR_SCHEME = REPO_ROOT / "python" / "gcs_viz" / "color_scheme.py"
FIGURE_THEME = REPO_ROOT / "tools" / "architecture_visualization" / "figure1.theme.json"

DEFAULT_SCAN_PATHS = [
    REPO_ROOT / "python" / "gcs_viz",
    REPO_ROOT / "tools" / "architecture_visualization",
    REPO_ROOT / "tools" / "ui_qa",
]
DEFAULT_RAW_HEX_SOURCES = {COLOR_SCHEME, FIGURE_THEME}
FIGURE_COLOR_ALIASES = {
    "line",
    "plane",
    "fixed",
    "positive",
    "negative",
    "chip",
    "component_a",
    "component_b",
}
TEXT_SUFFIXES = {".py", ".pyi", ".json", ".yaml", ".yml", ".css", ".html"}
PYTHON_SUFFIXES = {".py", ".pyi"}
HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}\b")
SPEC_TOKEN_RE = re.compile(r'["\']?canonical_token["\']?\s*[:=]\s*["\']([^"\']+)["\']')


@dataclass
class TokenLintResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class TokenRegistry:
    token_keys: set[str]
    theme_keys: set[str]
    state_keys: set[str]
    figure_color_keys: set[str]

    @property
    def canonical_tokens(self) -> set[str]:
        values = set(self.token_keys)
        for token in self.token_keys:
            if token.endswith((".fill", ".stroke", ".color", ".lineStyle", ".graphStyle")):
                values.add(token.rsplit(".", 1)[0])
        return values


def repo_relative(path: Path, repo_root: Path = REPO_ROOT) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def import_color_scheme(path: Path = COLOR_SCHEME):
    spec = importlib.util.spec_from_file_location("gcs_token_lint_color_scheme", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_registry(repo_root: Path = REPO_ROOT) -> TokenRegistry:
    module = import_color_scheme(repo_root / "python" / "gcs_viz" / "color_scheme.py")
    theme_path = repo_root / "tools" / "architecture_visualization" / "figure1.theme.json"
    return TokenRegistry(
        token_keys=set(module.GCS_TOKENS),
        theme_keys=set(module.GCS_THEME),
        state_keys=set(module.STATE_COLORS),
        figure_color_keys=_load_figure_color_keys(theme_path) | FIGURE_COLOR_ALIASES,
    )


def _load_figure_color_keys(path: Path) -> set[str]:
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    colors = data.get("colors", {}) if isinstance(data, dict) else {}
    if not isinstance(colors, dict):
        raise ValueError(f"{repo_relative(path)} must define a colors object")
    return {str(key) for key in colors}


def iter_scan_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file():
            if path.suffix in TEXT_SUFFIXES:
                yield path
            continue
        if not path.exists():
            continue
        for candidate in path.rglob("*"):
            if not candidate.is_file() or candidate.suffix not in TEXT_SUFFIXES:
                continue
            if any(part in {".git", "__pycache__", "node_modules", "out"} for part in candidate.parts):
                continue
            yield candidate


def normalized_allowed_sources(paths: Iterable[Path]) -> set[Path]:
    return {path.resolve() for path in paths}


def check_raw_hex(path: Path,
                  text: str,
                  allowed_sources: set[Path],
                  result: TokenLintResult,
                  repo_root: Path) -> None:
    if path.resolve() in allowed_sources:
        return
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in HEX_RE.finditer(line):
            result.errors.append(
                f"{repo_relative(path, repo_root)}:{line_number}: raw hex {match.group(0)} "
                "must move to GCS Warm Evidence Tokens"
            )


def check_python_tokens(path: Path,
                        text: str,
                        registry: TokenRegistry,
                        result: TokenLintResult,
                        repo_root: Path) -> None:
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        result.errors.append(f"{repo_relative(path, repo_root)}:{exc.lineno}: Python syntax error: {exc.msg}")
        return

    known_name_keys = {
        "GCS_TOKENS": registry.token_keys,
        "GCS_THEME": registry.theme_keys,
        "STATE_COLORS": registry.state_keys,
        "COLORS": registry.figure_color_keys,
    }

    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript) or not isinstance(node.value, ast.Name):
            continue
        if node.value.id not in known_name_keys:
            continue
        key = string_subscript_key(node.slice)
        if key is None:
            continue
        known = known_name_keys[node.value.id]
        if key not in known:
            result.errors.append(
                f"{repo_relative(path, repo_root)}:{getattr(node, 'lineno', 1)}: "
                f"unknown {node.value.id} token {key!r}"
            )


def string_subscript_key(slice_node: ast.AST) -> str | None:
    if isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, str):
        return slice_node.value
    if isinstance(slice_node, ast.Index):
        return string_subscript_key(slice_node.value)
    return None


def check_spec_tokens(path: Path,
                      text: str,
                      registry: TokenRegistry,
                      result: TokenLintResult,
                      repo_root: Path) -> None:
    if path.suffix not in {".yaml", ".yml", ".json"}:
        return
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = SPEC_TOKEN_RE.search(line)
        if not match:
            continue
        token = match.group(1)
        if token not in registry.canonical_tokens:
            result.errors.append(
                f"{repo_relative(path, repo_root)}:{line_number}: "
                f"unknown canonical_token {token!r}"
            )


def run_checks(paths: Iterable[Path] | None = None,
               allowed_raw_hex_sources: Iterable[Path] | None = None,
               repo_root: Path = REPO_ROOT) -> TokenLintResult:
    registry = load_registry(repo_root)
    result = TokenLintResult()
    scan_paths = list(paths) if paths is not None else list(DEFAULT_SCAN_PATHS)
    allowed_sources = normalized_allowed_sources(
        allowed_raw_hex_sources
        if allowed_raw_hex_sources is not None
        else [repo_root / "python" / "gcs_viz" / "color_scheme.py",
              repo_root / "tools" / "architecture_visualization" / "figure1.theme.json"]
    )

    seen: set[Path] = set()
    for path in iter_scan_files(scan_paths):
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        text = path.read_text(encoding="utf-8-sig")
        check_raw_hex(path, text, allowed_sources, result, repo_root)
        if path.suffix in PYTHON_SUFFIXES:
            check_python_tokens(path, text, registry, result, repo_root)
        check_spec_tokens(path, text, registry, result, repo_root)

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint GCS UI and figure token usage")
    parser.add_argument("paths", nargs="*", type=Path, help="Files or directories to scan")
    parser.add_argument(
        "--allow-raw-hex-source",
        action="append",
        type=Path,
        default=[],
        help="Additional file that may contain raw #RRGGBB values",
    )
    args = parser.parse_args(argv)

    paths = args.paths if args.paths else DEFAULT_SCAN_PATHS
    allowed = list(DEFAULT_RAW_HEX_SOURCES) + args.allow_raw_hex_source
    result = run_checks(paths=paths, allowed_raw_hex_sources=allowed)
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.ok:
        print("GCS token lint passed")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
