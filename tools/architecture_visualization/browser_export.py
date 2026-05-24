#!/usr/bin/env python3
"""Export browser-flowed GCS figure HTML to review artifacts.

This is intentionally dependency-light: it first tries an installed Chromium
browser CLI such as Chrome or Edge, and records a skipped manifest when no
browser backend is available. The HTML remains the editable source artifact.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

import figure71_html_compositor as figure71


ROOT = Path(__file__).resolve().parents[2]
SPEC_ROOT = ROOT / "tools" / "architecture_visualization" / "specs"
DEFAULT_VIEWPORT = (1600, 2200)
REQUIRED_HTML_TOKENS = (
    "--gcs-surface-paper",
    "--gcs-surface-panel",
    "--gcs-text-primary",
    "--gcs-token-fill",
    "--gcs-token-stroke",
)
DEFAULT_BROWSER_CANDIDATES = (
    "msedge",
    "microsoft-edge",
    "chrome",
    "google-chrome",
    "chromium",
    "chromium-browser",
)
WINDOWS_BROWSER_PATHS = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
)


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain an object")
    return data


def root_path(path_value: object) -> Path:
    path = Path(str(path_value))
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def resolve_spec(args: argparse.Namespace) -> Path:
    if args.spec:
        spec_path = args.spec
    else:
        spec_path = SPEC_ROOT / f"{args.figure}.yaml"
    return spec_path if spec_path.is_absolute() else ROOT / spec_path


def spec_export_path(
    spec: dict[str, object],
    key: str,
    fallback_name: str,
) -> Path:
    exports = spec.get("exports", {})
    if isinstance(exports, dict) and key in exports:
        return root_path(exports[key])
    return ROOT / "docs" / "architecture" / "70-visualization" / "assets" / fallback_name


def ensure_html(spec: dict[str, object], html_path: Path, render_html: bool) -> None:
    if html_path.exists() and not render_html:
        return
    theme_path = root_path(spec.get("theme", ""))
    steps = figure71.parse_source_steps(spec)
    colors = figure71.load_theme(theme_path)
    html = figure71.render_html(spec, steps, colors)
    html = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8", newline="\n")


def check_html_tokens(html_path: Path) -> list[dict[str, object]]:
    html = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
    return [
        {
            "token": token,
            "passed": token in html,
        }
        for token in REQUIRED_HTML_TOKENS
    ]


def find_browser(explicit_browser: Path | None) -> Path | None:
    if explicit_browser is not None:
        return explicit_browser if explicit_browser.exists() else None
    for candidate in DEFAULT_BROWSER_CANDIDATES:
        located = shutil.which(candidate)
        if located:
            return Path(located)
    if os.name == "nt":
        for candidate in WINDOWS_BROWSER_PATHS:
            path = Path(candidate)
            if path.exists():
                return path
    return None


def browser_version(browser: Path) -> str:
    try:
        result = subprocess.run(
            [str(browser), "--version"],
            cwd=ROOT,
            capture_output=True,
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"unavailable: {exc}"
    raw = result.stdout or result.stderr or b""
    for encoding in ("utf-8", "gbk", "mbcs"):
        try:
            value = raw.decode(encoding).strip()
            break
        except (LookupError, UnicodeDecodeError):
            value = ""
    match = re.search(r"(?:Chrome|Chromium|Edge)[^\d]*(\d+(?:\.\d+)+)", value)
    if match:
        return match.group(0)
    return "version unavailable from browser CLI"


def sanitize_diagnostic(value: object, limit: int = 400) -> str:
    text = str(value or "")
    text = text.replace(str(ROOT), "<repo>")
    text = text.replace(str(ROOT).replace("\\", "/"), "<repo>")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[: limit - 3].rstrip() + "..."
    return text


def run_browser_command(command: list[str], timeout_seconds: int) -> dict[str, object]:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "exit_code": -1,
            "stdout": exc.stdout or "",
            "stderr": f"timeout after {timeout_seconds}s",
        }
    except OSError as exc:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": str(exc),
        }
    return {
        "exit_code": result.returncode,
        "stdout": (result.stdout or "").strip(),
        "stderr": (result.stderr or "").strip(),
    }


def export_with_chromium_cli(
    browser: Path,
    html_path: Path,
    outputs: dict[str, Path],
    formats: Iterable[str],
    viewport: tuple[int, int],
    timeout_seconds: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    artifacts: list[dict[str, object]] = []
    unsupported: list[dict[str, object]] = []
    url = html_path.as_uri()
    width, height = viewport

    with tempfile.TemporaryDirectory(prefix="gcs-browser-export-") as profile_dir:
        common = [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--hide-scrollbars",
            f"--user-data-dir={profile_dir}",
            f"--window-size={width},{height}",
        ]
        for fmt in formats:
            fmt = fmt.lower()
            if fmt == "png":
                out_path = outputs[fmt]
                out_path.parent.mkdir(parents=True, exist_ok=True)
                command = [*common, f"--screenshot={out_path}", url]
            elif fmt == "pdf":
                out_path = outputs[fmt]
                out_path.parent.mkdir(parents=True, exist_ok=True)
                command = [
                    *common,
                    "--no-pdf-header-footer",
                    "--print-to-pdf-no-header",
                    f"--print-to-pdf={out_path}",
                    url,
                ]
            else:
                unsupported.append({
                    "format": fmt,
                    "reason": "Chromium CLI supports PNG screenshots and PDF print output for this smoke gate.",
                })
                continue

            result = run_browser_command(command, timeout_seconds)
            exists = out_path.exists()
            artifacts.append({
                "format": fmt,
                "path": display_path(out_path),
                "exists": exists,
                "bytes": out_path.stat().st_size if exists else 0,
                "exit_code": result["exit_code"],
                "diagnostic": sanitize_diagnostic(result["stderr"] or result["stdout"]),
            })
    return artifacts, unsupported


def build_manifest(
    spec_path: Path,
    spec: dict[str, object],
    html_path: Path,
    requested_formats: list[str],
    browser: Path | None,
    artifacts: list[dict[str, object]],
    unsupported: list[dict[str, object]],
    token_checks: list[dict[str, object]],
    require_browser: bool,
) -> dict[str, object]:
    token_passed = all(bool(check["passed"]) for check in token_checks)
    exported = [artifact for artifact in artifacts if artifact.get("exists")]
    failed = [artifact for artifact in artifacts if not artifact.get("exists")]

    if browser is None:
        status = "failed" if require_browser else "skipped"
        reason = "No Chrome/Edge/Chromium executable was found."
    elif failed:
        status = "failed" if require_browser else "partial"
        reason = "At least one requested browser export did not produce an artifact."
    elif exported:
        status = "exported"
        reason = "Browser CLI produced all supported requested artifacts."
    else:
        status = "skipped"
        reason = "No supported formats were requested."

    return {
        "figure": spec.get("id", spec_path.stem),
        "schema_version": spec.get("schema_version"),
        "spec": display_path(spec_path),
        "html": display_path(html_path),
        "requested_formats": requested_formats,
        "status": status,
        "reason": reason,
        "browser": {
            "backend": "chromium-cli" if browser is not None else "none",
            "executable": browser.name if browser is not None else "",
            "version": browser_version(browser) if browser is not None else "",
        },
        "html_token_checks": token_checks,
        "html_tokens_passed": token_passed,
        "exports": artifacts,
        "unsupported_formats": unsupported,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Browser-export a GCS HTML figure to review artifacts.")
    parser.add_argument("--figure", default="figure71", help="Figure id, resolved to specs/<figure>.yaml.")
    parser.add_argument("--spec", type=Path, help="Explicit spec path.")
    parser.add_argument("--formats", default="png,pdf", help="Comma-separated export formats: png,pdf,svg.")
    parser.add_argument("--browser-exe", type=Path, help="Explicit Chrome/Edge/Chromium executable.")
    parser.add_argument("--manifest", type=Path, help="Output manifest path. Defaults to spec exports.browser_manifest.")
    parser.add_argument("--render-html", action="store_true", help="Regenerate the HTML source before export.")
    parser.add_argument("--require-browser", action="store_true", help="Fail when browser artifacts cannot be produced.")
    parser.add_argument("--viewport", default="1600x2200", help="Viewport as WIDTHxHEIGHT for PNG export.")
    parser.add_argument("--timeout-seconds", type=int, default=60, help="Per-export browser timeout.")
    return parser.parse_args()


def parse_formats(value: str) -> list[str]:
    formats = [item.strip().lower() for item in value.split(",") if item.strip()]
    return formats or ["png", "pdf"]


def parse_viewport(value: str) -> tuple[int, int]:
    if "x" not in value.lower():
        return DEFAULT_VIEWPORT
    raw_width, raw_height = value.lower().split("x", 1)
    try:
        return int(raw_width), int(raw_height)
    except ValueError:
        return DEFAULT_VIEWPORT


def main() -> int:
    args = parse_args()
    spec_path = resolve_spec(args)
    spec = load_json(spec_path)
    figure_id = str(spec.get("id", spec_path.stem))
    html_path = spec_export_path(spec, "html", f"{figure_id}.html")
    manifest_path = args.manifest
    if manifest_path is None:
        manifest_path = spec_export_path(spec, "browser_manifest", f"{figure_id}-browser-export.json")
    elif not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path
    formats = parse_formats(args.formats)
    viewport = parse_viewport(args.viewport)

    ensure_html(spec, html_path, args.render_html)
    token_checks = check_html_tokens(html_path)
    browser = find_browser(args.browser_exe)
    outputs = {
        "png": spec_export_path(spec, "review_png", f"{figure_id}-review.png"),
        "pdf": spec_export_path(spec, "review_pdf", f"{figure_id}-review.pdf"),
    }

    artifacts: list[dict[str, object]] = []
    unsupported: list[dict[str, object]] = []
    if browser is not None:
        artifacts, unsupported = export_with_chromium_cli(
            browser,
            html_path,
            outputs,
            formats,
            viewport,
            args.timeout_seconds,
        )
    else:
        unsupported = [
            {
                "format": fmt,
                "reason": "No Chrome/Edge/Chromium executable was found.",
            }
            for fmt in formats
        ]

    manifest = build_manifest(
        spec_path,
        spec,
        html_path,
        formats,
        browser,
        artifacts,
        unsupported,
        token_checks,
        args.require_browser,
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(manifest, indent=2))

    failed = manifest["status"] == "failed" or not manifest["html_tokens_passed"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
