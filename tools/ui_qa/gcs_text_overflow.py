from __future__ import annotations

import argparse
import re
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
]


@dataclass
class TextBudget:
    label: str
    budget: int
    text: str
    line: int

    @property
    def normalized(self) -> str:
        return re.sub(r"\s+", " ", self.text).strip()

    @property
    def length(self) -> int:
        return len(self.normalized)


@dataclass
class OverflowResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    budgets_checked: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors


class BudgetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[dict[str, object]] = []
        self.budgets: list[TextBudget] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value for key, value in attrs}
        budget = values.get("data-gcs-text-budget")
        label = values.get("data-gcs-text-label")
        if budget is None:
            return
        line, _ = self.getpos()
        try:
            budget_value = int(budget)
        except ValueError:
            budget_value = -1
        self.stack.append({
            "tag": tag,
            "label": label or f"{tag}-line-{line}",
            "budget": budget_value,
            "line": line,
            "parts": [],
        })

    def handle_data(self, data: str) -> None:
        for item in self.stack:
            parts = item["parts"]
            assert isinstance(parts, list)
            parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] != tag:
                continue
            item = self.stack.pop(index)
            parts = item["parts"]
            assert isinstance(parts, list)
            self.budgets.append(TextBudget(
                label=str(item["label"]),
                budget=int(item["budget"]),
                text="".join(str(part) for part in parts),
                line=int(item["line"]),
            ))
            return

    def close(self) -> None:
        super().close()
        while self.stack:
            item = self.stack.pop()
            parts = item["parts"]
            assert isinstance(parts, list)
            self.budgets.append(TextBudget(
                label=str(item["label"]),
                budget=int(item["budget"]),
                text="".join(str(part) for part in parts),
                line=int(item["line"]),
            ))


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


def parse_budgets(path: Path) -> list[TextBudget]:
    parser = BudgetParser()
    parser.feed(path.read_text(encoding="utf-8-sig"))
    parser.close()
    return parser.budgets


def run_checks(paths: Iterable[Path] | None = None,
               repo_root: Path = REPO_ROOT) -> OverflowResult:
    result = OverflowResult()
    html_paths = list(iter_html_files(paths or DEFAULT_HTML_PATHS))
    if not html_paths:
        result.errors.append("No HTML files were found for text overflow checks")
        return result

    for path in html_paths:
        budgets = parse_budgets(path)
        if not budgets:
            result.errors.append(f"{repo_relative(path, repo_root)}: no data-gcs-text-budget markers found")
            continue
        result.budgets_checked += len(budgets)
        for budget in budgets:
            if budget.budget < 1:
                result.errors.append(
                    f"{repo_relative(path, repo_root)}:{budget.line}: "
                    f"{budget.label} has invalid text budget {budget.budget}"
                )
                continue
            if budget.length > budget.budget:
                result.errors.append(
                    f"{repo_relative(path, repo_root)}:{budget.line}: "
                    f"{budget.label} text length {budget.length} exceeds budget {budget.budget}: "
                    f"{budget.normalized!r}"
                )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check GCS HTML text overflow budgets")
    parser.add_argument("paths", nargs="*", type=Path, help="HTML files or directories to scan")
    args = parser.parse_args(argv)

    result = run_checks(args.paths if args.paths else DEFAULT_HTML_PATHS)
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.ok:
        print(f"GCS text overflow checks passed ({result.budgets_checked} budgets)")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
