#!/usr/bin/env python3
"""Agentic design utilities for the GCS architecture rewrite.

The toolkit intentionally uses only the Python standard library so module
agents can run it in restricted local environments.
"""

from __future__ import annotations

import argparse
import datetime as _datetime
import glob
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = ROOT / "tools" / "agentic_design" / "module_inventory.json"
AGENTIC_TASK_DIR = ROOT / "docs" / "agentic" / "tasks"
COMPLETED_TASK_DIR = ROOT / "docs" / "completed-tasks"
E002_EXPERIENCE_DIR = ROOT / "docs" / "agentic" / "experience" / "002-phase-step-summary-update-commit-continue"
PR_AUDIT_SCHEMA_VERSION = "gcs.pr-audit.v1"
PR_AUDIT_SCHEMA_PATH = ROOT / "docs" / "agentic" / "schemas" / "pr-audit.schema.json"
NIGHTLY_RUNS_DIR = ROOT / "docs" / "agentic" / "nightly-runs"
CURRENT_TASK_FILE = ROOT / ".claude" / "current-task"


PR_CLASS_PRIORITY = {
    "docs-only": 10,
    "exploratory": 20,
    "agentic-process": 40,
    "architecture": 50,
    "quality-gate": 60,
    "scene-exploration": 80,
    "solver-contract": 90,
    "repair": 100,
}


RISK_PRIORITY = {
    "low": 10,
    "medium": 20,
    "high": 30,
}


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    message: str


@dataclass(frozen=True)
class GateResult:
    gate_id: str
    ok: bool
    duration_seconds: float
    command: str
    exit_code: int


@dataclass(frozen=True)
class GateCommand:
    gate_id: str
    command: list[str | os.PathLike[str]]


@dataclass(frozen=True)
class ScoreDimension:
    name: str
    score: int
    reason: str


def load_inventory(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def repo_path(path: str | Path) -> Path:
    return ROOT / path


def read_current_task() -> dict[str, str] | None:
    """Read .claude/current-task; return None if absent or malformed."""
    if not CURRENT_TASK_FILE.exists():
        return None
    try:
        text = CURRENT_TASK_FILE.read_text(encoding="utf-8")
        result: dict[str, str] = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
        return result if "task_card" in result else None
    except Exception:
        return None


def write_current_task(task_card_path: str) -> None:
    """Write .claude/current-task pointing to the given task card."""
    CURRENT_TASK_FILE.parent.mkdir(parents=True, exist_ok=True)
    CURRENT_TASK_FILE.write_text(
        f"task_card: {task_card_path}\n"
        f"created: {_datetime.date.today().isoformat()}\n",
        encoding="utf-8",
    )


def clear_current_task() -> None:
    """Remove .claude/current-task."""
    if CURRENT_TASK_FILE.exists():
        CURRENT_TASK_FILE.unlink()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def normalize_repo_path(value: str | Path) -> str:
    text = str(value).replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text.strip("/")


def unique_preserve_order(values: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        normalized = str(value).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(normalized)
    return unique


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists; pass --force to overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def resolve_repo_or_absolute(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def has_glob_syntax(pathspec: str) -> bool:
    return any(char in pathspec for char in "*?[")


def normalize_include_pathspecs(pathspecs: list[str] | tuple[str, ...] | None) -> list[str]:
    values: list[str] = []
    for raw in pathspecs or []:
        for item in str(raw).split(","):
            item = item.strip()
            if item:
                values.append(item)
    return values


def quote_for_powershell(value: str | Path) -> str:
    return '"' + str(value).replace('"', '`"') + '"'


def extract_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, flags=re.DOTALL)
    if not match:
        return {}
    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"')
    return frontmatter


def parse_simple_yaml(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def parse_frontmatter_values(text: str) -> dict[str, Any]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, flags=re.DOTALL)
    if not match:
        return {}

    values: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in match.group(1).splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_key:
            current_value = values.setdefault(current_key, [])
            if not isinstance(current_value, list):
                values[current_key] = current_value = []
            current_value.append(stripped[2:].strip().strip('"'))
            continue
        if ":" not in line or line.startswith((" ", "\t")):
            current_key = None
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            values[key] = []
            current_key = key
            continue
        current_key = None
        values[key] = parse_frontmatter_scalar(value)
    return values


def parse_frontmatter_scalar(value: str) -> Any:
    value = value.strip().strip('"')
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"') for item in inner.split(",")]
    return value


def module_by_id(inventory: dict[str, Any], module_id: str) -> dict[str, Any]:
    for module in inventory["modules"]:
        if module["id"] == module_id:
            return module
    known = ", ".join(module["id"] for module in inventory["modules"])
    raise KeyError(f"unknown module '{module_id}'. Known modules: {known}")


def known_skill_names() -> set[str]:
    skill_root = ROOT / ".codex" / "skills"
    if not skill_root.exists():
        return set()
    return {
        path.name
        for path in skill_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    }


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(value)]


def normalize_slug(slug: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-")


def section_body(text: str, heading: str) -> str:
    match = re.search(rf"^{re.escape(heading)}\s*$", text, flags=re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    next_match = re.search(r"^##\s+", text[start:], flags=re.MULTILINE)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end].strip()


def heading_body(text: str, heading: str) -> str:
    match = re.search(rf"^{re.escape(heading)}\s*$", text, flags=re.MULTILINE)
    if not match:
        return ""
    level_match = re.match(r"^(#+)\s+", heading)
    if not level_match:
        return ""
    level = len(level_match.group(1))
    start = match.end()
    next_match = re.search(rf"^#{{1,{level}}}\s+", text[start:], flags=re.MULTILINE)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end].strip()


def has_index_link(path: Path) -> bool:
    index = COMPLETED_TASK_DIR / "README.md"
    if not index.exists():
        return False
    try:
        folder = path.parent.relative_to(COMPLETED_TASK_DIR).as_posix()
    except ValueError:
        return False
    index_text = read_text(index)
    return f"{folder}/README.md" in index_text or f"{folder}\\README.md" in index_text


def validate_skills(inventory: dict[str, Any]) -> list[CheckResult]:
    results: list[CheckResult] = []
    for module in inventory["modules"]:
        skill_dir = repo_path(module["skill"])
        skill_md = skill_dir / "SKILL.md"
        openai_yaml = skill_dir / "agents" / "openai.yaml"

        if not skill_md.exists():
            results.append(CheckResult(False, f"{module['id']}: missing {skill_md}"))
            continue
        if not openai_yaml.exists():
            results.append(CheckResult(False, f"{module['id']}: missing {openai_yaml}"))
            continue

        skill_text = read_text(skill_md)
        frontmatter = extract_frontmatter(skill_text)
        expected_name = Path(module["skill"]).name
        if frontmatter.get("name") != expected_name:
            results.append(CheckResult(
                False,
                f"{module['id']}: SKILL.md name is {frontmatter.get('name')!r}, expected {expected_name!r}",
            ))
        if len(frontmatter.get("description", "")) < 80:
            results.append(CheckResult(False, f"{module['id']}: description is too short"))
        if "TODO" in skill_text or "[TODO" in skill_text:
            results.append(CheckResult(False, f"{module['id']}: template TODO remains in SKILL.md"))

        metadata = parse_simple_yaml(read_text(openai_yaml))
        short = metadata.get("short_description", "")
        prompt = metadata.get("default_prompt", "")
        if not (25 <= len(short) <= 64):
            results.append(CheckResult(False, f"{module['id']}: short_description length is {len(short)}"))
        if f"${expected_name}" not in prompt:
            results.append(CheckResult(False, f"{module['id']}: default_prompt must mention ${expected_name}"))

    if not results:
        results.append(CheckResult(True, "skills: all module skills passed"))
    return results


def validate_docs(inventory: dict[str, Any]) -> list[CheckResult]:
    docs = inventory["docs"]
    agents_doc = read_text(repo_path(docs["module_agents"]))
    target_doc = read_text(repo_path(docs["target_contracts"]))
    physical_doc = read_text(repo_path(docs["physical_skills"]))
    results: list[CheckResult] = []

    required_target_markers = [
        "Structured inputs:",
        "Structured outputs:",
        "Target public API:",
        "Contract tests:",
    ]

    for module in inventory["modules"]:
        agent_heading = f"## {module['agent_heading']}"
        target_heading = f"## {module['target_heading']}"
        skill_path = module["skill"]

        if agent_heading not in agents_doc:
            results.append(CheckResult(False, f"{module['id']}: missing agent heading {agent_heading}"))
        if target_heading not in target_doc:
            results.append(CheckResult(False, f"{module['id']}: missing target heading {target_heading}"))
        if skill_path not in physical_doc:
            results.append(CheckResult(False, f"{module['id']}: missing physical skill catalog entry"))

        target_start = target_doc.find(target_heading)
        next_heading = target_doc.find("\n## ", target_start + 1)
        target_section = target_doc[target_start: next_heading if next_heading != -1 else len(target_doc)]
        for marker in required_target_markers:
            if marker not in target_section:
                results.append(CheckResult(False, f"{module['id']}: missing target marker {marker}"))

    if not results:
        results.append(CheckResult(True, "docs: module design coverage passed"))
    return results


def validate_inventory(inventory: dict[str, Any]) -> list[CheckResult]:
    results: list[CheckResult] = []
    required_module_fields = [
        "id",
        "cxx_module",
        "namespace",
        "source_dir",
        "skill",
        "agent_heading",
        "target_heading",
        "contract_test",
        "structured_inputs",
        "structured_outputs",
        "tools",
        "allowed_imports",
    ]
    seen_ids: set[str] = set()
    seen_modules: set[str] = set()

    for module in inventory["modules"]:
        for field in required_module_fields:
            if field not in module:
                results.append(CheckResult(False, f"{module.get('id', '<unknown>')}: missing inventory field {field}"))
        module_id = module.get("id", "")
        cxx_module = module.get("cxx_module", "")
        if module_id in seen_ids:
            results.append(CheckResult(False, f"{module_id}: duplicate module id"))
        if cxx_module in seen_modules:
            results.append(CheckResult(False, f"{module_id}: duplicate C++ module name {cxx_module}"))
        seen_ids.add(module_id)
        seen_modules.add(cxx_module)

        for collection in ["structured_inputs", "structured_outputs", "tools"]:
            values = module.get(collection, [])
            if not isinstance(values, list) or not values:
                results.append(CheckResult(False, f"{module_id}: {collection} must be a non-empty list"))
            if len(values) != len(set(values)):
                results.append(CheckResult(False, f"{module_id}: {collection} contains duplicate values"))

    if not results:
        results.append(CheckResult(True, "inventory: structured module inventory passed"))
    return results


def cxx_files_under(paths: list[Path]) -> list[Path]:
    extensions = {".cpp", ".cppm", ".ixx", ".cxx", ".cc", ".h", ".hpp"}
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix in extensions:
            files.append(path)
        elif path.is_dir():
            for candidate in path.rglob("*"):
                if candidate.is_file() and candidate.suffix in extensions:
                    files.append(candidate)
    return files


def imports_in_file(path: Path) -> list[str]:
    text = read_text(path)
    return re.findall(r"^\s*import\s+(gcs\.[A-Za-z0-9_\.]+)\s*;", text, flags=re.MULTILINE)


def check_dependencies(inventory: dict[str, Any]) -> list[CheckResult]:
    results: list[CheckResult] = []

    scopes: list[tuple[str, list[Path], set[str]]] = []
    for module in inventory["modules"]:
        scopes.append((
            module["id"],
            [repo_path(module["source_dir"])],
            set(module.get("allowed_imports", [])),
        ))
    for target in inventory.get("external_targets", []):
        scopes.append((
            target["id"],
            [repo_path(path) for path in target["paths"]],
            set(target.get("allowed_imports", [])),
        ))

    for scope_id, paths, allowed in scopes:
        for path in cxx_files_under(paths):
            for imported in imports_in_file(path):
                if imported not in allowed:
                    rel = path.relative_to(ROOT)
                    results.append(CheckResult(
                        False,
                        f"{scope_id}: {rel} imports forbidden module {imported}",
                    ))

    if not results:
        results.append(CheckResult(True, "dependencies: import boundaries passed"))
    return results


def validate_task_card_file(path: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    if not path.exists():
        return [CheckResult(False, f"task-card: missing file {path}")]

    text = read_text(path)
    data = parse_frontmatter_values(text)
    required = [
        "task_id",
        "status",
        "request",
        "scope",
        "risk",
        "owning_agent",
        "affected_paths",
        "required_evidence",
        "human_gate_required",
    ]
    for field in required:
        if field not in data or data[field] in ("", []):
            results.append(CheckResult(False, f"{path}: missing frontmatter field {field}"))

    placeholder_patterns = [
        "<...",
        "TODO",
        "Describe what is in scope",
        "Record commands run",
        "List remaining uncertainty",
        "ContractNameOrNone",
    ]
    for pattern in placeholder_patterns:
        if pattern in text:
            results.append(CheckResult(False, f"{path}: placeholder text remains: {pattern}"))

    task_id = str(data.get("task_id", ""))
    if task_id and not re.match(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*$", task_id):
        results.append(CheckResult(False, f"{path}: task_id must look like YYYY-MM-DD-slug"))

    valid_statuses = {"draft", "ready", "in_progress", "blocked", "complete"}
    status = str(data.get("status", ""))
    if status and status not in valid_statuses:
        results.append(CheckResult(False, f"{path}: status must be one of {sorted(valid_statuses)}"))

    valid_scopes = {
        "architecture",
        "implementation",
        "test",
        "fixture",
        "ci",
        "docs",
        "tool",
        "review",
        "maintenance",
        "release",
    }
    scope = str(data.get("scope", "")).lower()
    if scope and scope not in valid_scopes:
        results.append(CheckResult(False, f"{path}: scope must be one of {sorted(valid_scopes)}"))

    valid_risks = {"low", "medium", "high"}
    risk = str(data.get("risk", "")).lower()
    if risk and risk not in valid_risks:
        results.append(CheckResult(False, f"{path}: risk must be one of {sorted(valid_risks)}"))

    known_skills = known_skill_names()
    owner = str(data.get("owning_agent", ""))
    if owner and known_skills and owner not in known_skills:
        results.append(CheckResult(False, f"{path}: owning_agent {owner!r} is not a known .codex skill"))

    for specialist in normalize_list(data.get("specialist_agents")):
        if specialist.lower() == "none":
            continue
        if known_skills and specialist not in known_skills:
            results.append(CheckResult(False, f"{path}: specialist_agent {specialist!r} is not a known .codex skill"))

    evidence = normalize_list(data.get("required_evidence"))
    if not evidence:
        results.append(CheckResult(False, f"{path}: required_evidence must name at least one gate"))

    affected_paths = normalize_list(data.get("affected_paths"))
    if not affected_paths:
        results.append(CheckResult(False, f"{path}: affected_paths must name at least one path or boundary"))

    human_gate = data.get("human_gate_required")
    if not isinstance(human_gate, bool):
        results.append(CheckResult(False, f"{path}: human_gate_required must be true or false"))
    if risk == "high" and human_gate is not True:
        results.append(CheckResult(False, f"{path}: high-risk tasks require human_gate_required: true"))
    if human_gate is True and not str(data.get("human_gate_reason", "")).strip():
        results.append(CheckResult(False, f"{path}: human gate requires human_gate_reason"))

    required_sections = [
        "## Scope",
        "## Non-Goals",
        "## Acceptance Gates",
        "## Verification Plan",
        "## Evidence Bundle",
        "## Residual Risks",
    ]
    for section in required_sections:
        if section not in text:
            results.append(CheckResult(False, f"{path}: missing section {section}"))

    if not results:
        results.append(CheckResult(True, f"task-card: {display_path(path)} passed"))
    return results


def expanded_task_card_candidates(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted((candidate for candidate in path.glob("*.md") if candidate.is_file()), key=display_path)
    if path.is_file():
        return [path]
    return []


def expanded_completed_report_candidates(path: Path) -> list[Path]:
    if path.is_dir():
        readme = path / "README.md"
        if readme.is_file():
            return [readme]
        return sorted((candidate for candidate in path.glob("*/README.md") if candidate.is_file()), key=display_path)
    if path.is_file():
        return [path]
    return []


def expand_include_pathspecs(pathspecs: list[str] | tuple[str, ...] | None,
                             artifact_name: str,
                             candidate_expander) -> tuple[list[Path], list[CheckResult]]:
    paths: list[Path] = []
    errors: list[CheckResult] = []
    seen: set[str] = set()

    for pathspec in normalize_include_pathspecs(pathspecs):
        base = resolve_repo_or_absolute(pathspec)
        raw_matches = [Path(match) for match in sorted(glob.glob(str(base), recursive=True))] if has_glob_syntax(pathspec) else [base]
        expanded: list[Path] = []
        for raw_match in raw_matches:
            expanded.extend(candidate_expander(raw_match))

        if not expanded:
            errors.append(CheckResult(False, f"{artifact_name}: unmatched include pathspec {pathspec}"))
            continue

        for path in expanded:
            key = str(path.resolve())
            if key in seen:
                continue
            seen.add(key)
            paths.append(path)

    return paths, errors


def validate_task_card_includes(pathspecs: list[str] | tuple[str, ...] | None) -> list[CheckResult]:
    paths, results = expand_include_pathspecs(
        pathspecs,
        "task-card-includes",
        expanded_task_card_candidates,
    )
    for path in paths:
        results.extend(validate_task_card_file(path))
    return results


def validate_completed_report_includes(pathspecs: list[str] | tuple[str, ...] | None,
                                       require_index: bool = True) -> list[CheckResult]:
    paths, results = expand_include_pathspecs(
        pathspecs,
        "completed-report-includes",
        expanded_completed_report_candidates,
    )
    for path in paths:
        results.extend(validate_completed_task_report_file(path, require_index=require_index))
    return results


def design_card(inventory: dict[str, Any], module_id: str) -> dict[str, Any]:
    module = module_by_id(inventory, module_id)
    return {
        "module_name": module["cxx_module"],
        "module_id": module["id"],
        "namespace": module.get("namespace", module["cxx_module"].replace("gcs.", "gcs::")),
        "owner_skill": module["skill"],
        "agent_heading": module["agent_heading"],
        "target_heading": module["target_heading"],
        "source_dir": module["source_dir"],
        "contract_test": module["contract_test"],
        "allowed_imports": module.get("allowed_imports", []),
        "structured_inputs": module.get("structured_inputs", []),
        "structured_outputs": module.get("structured_outputs", []),
        "tools": module.get("tools", []),
        "guardrails": [
            "use public C++23 module contracts",
            "return typed reports instead of prose-only failures",
            "preserve dependency direction",
        ],
        "evals": [module["contract_test"]],
    }


def contract_test_template(module: dict[str, Any]) -> str:
    guard = module["id"].replace("_", " ").title()
    return f"""import {module['cxx_module']};

#include <gtest/gtest.h>

TEST({guard.replace(" ", "")}Contract, DefinesStructuredInputOutputSmoke) {{
    // Replace this smoke placeholder with assertions over public contracts,
    // report codes, stable IDs, and negative cases from the target design.
    SUCCEED();
}}
"""


def module_interface_template(module: dict[str, Any]) -> str:
    namespace = module.get("namespace", module["cxx_module"].replace("gcs.", "gcs::"))
    return f"""module;

export module {module['cxx_module']};

export namespace {namespace} {{

struct ModuleDesignMarker {{
    static constexpr const char* module_id = "{module['id']}";
}};

}}
"""


def module_impl_template(module: dict[str, Any]) -> str:
    return f"""module;

module {module['cxx_module']};
"""


def emit_design_card(args: argparse.Namespace, inventory: dict[str, Any]) -> int:
    card = design_card(inventory, args.module)
    print(json.dumps(card, indent=2, sort_keys=True))
    return 0


def scaffold_contract_test(args: argparse.Namespace, inventory: dict[str, Any]) -> int:
    module = module_by_id(inventory, args.module)
    target = repo_path(module["contract_test"])
    text = contract_test_template(module)
    if args.write:
        write_text(target, text, args.force)
        print(f"wrote {target.relative_to(ROOT)}")
    else:
        print(f"# target: {target.relative_to(ROOT)}")
        print(text)
    return 0


def scaffold_module(args: argparse.Namespace, inventory: dict[str, Any]) -> int:
    module = module_by_id(inventory, args.module)
    source_dir = repo_path(module["source_dir"])
    base_name = source_dir.name
    interface_path = source_dir / f"{base_name}.cppm"
    impl_path = source_dir / f"{base_name}.cpp"
    outputs = [
        (interface_path, module_interface_template(module)),
        (impl_path, module_impl_template(module)),
    ]

    if args.write:
        for path, text in outputs:
            write_text(path, text, args.force)
            print(f"wrote {path.relative_to(ROOT)}")
    else:
        for path, text in outputs:
            print(f"# target: {path.relative_to(ROOT)}")
            print(text)
    return 0


def task_card_template(args: argparse.Namespace) -> str:
    today = args.date or _datetime.date.today().isoformat()
    slug = re.sub(r"[^a-z0-9-]+", "-", args.slug.lower()).strip("-")
    task_id = f"{today}-{slug}"
    human_gate = "true" if args.human_gate or args.risk == "high" else "false"
    human_gate_reason = args.human_gate_reason
    if human_gate == "true" and not human_gate_reason:
        human_gate_reason = "High-risk or explicitly gated task."
    request = args.request.replace('"', '\\"')
    evidence = args.evidence or ["validate-docs", "validate-inventory", "check-dependencies"]
    evidence_lines = "\n".join(f"  - {item}" for item in evidence)
    specialists = args.specialist or []
    specialist_lines = "\n".join(f"  - {item}" for item in specialists)
    if not specialist_lines:
        specialist_lines = "  - none"

    return f"""---
task_id: {task_id}
status: draft
request: "{request}"
scope: {args.scope}
risk: {args.risk}
owning_agent: {args.owner}
specialist_agents:
{specialist_lines}
affected_contracts:
  - none
affected_paths:
  - docs/agentic/
required_evidence:
{evidence_lines}
human_gate_required: {human_gate}
human_gate_reason: "{human_gate_reason}"
---

# {task_id}

## Scope

Describe what is in scope and what is intentionally out of scope.

## Non-Goals

- Do not change solver runtime semantics.
- Do not redefine architecture contracts in `docs/agentic`.

## Context To Read

- `docs/architecture/README.md`
- Owning skill: `{args.owner}`

## Acceptance Gates

- The owning boundary is clear.
- Required evidence is produced or a reason is recorded.
- Residual risks are named.

## Verification Plan

```bat
python tools\\agentic_design\\agentic_toolkit.py validate-task-card docs\\agentic\\tasks\\{task_id}.md
```

## Evidence Bundle

Record commands run, important outputs, changed files, and skipped checks.

## Residual Risks

List remaining uncertainty, review focus, or follow-up work.
"""


def new_task_card(args: argparse.Namespace) -> int:
    today = args.date or _datetime.date.today().isoformat()
    slug = re.sub(r"[^a-z0-9-]+", "-", args.slug.lower()).strip("-")
    if not slug:
        raise ValueError("--slug must contain at least one letter or number")
    task_id = f"{today}-{slug}"
    target = repo_path(args.output) if args.output else AGENTIC_TASK_DIR / f"{task_id}.md"
    text = task_card_template(args)
    if args.write:
        write_text(target, text, args.force)
        task_card_rel = str(target.relative_to(ROOT)).replace("\\", "/")
        write_current_task(task_card_rel)
        print(f"wrote {task_card_rel}")
        print(f"set current-task → {task_card_rel}")
    else:
        print(f"# target: {target.relative_to(ROOT)}")
        print(text)
    return 0


def worktree_task_values(args: argparse.Namespace) -> dict[str, Any]:
    today = args.date or _datetime.date.today().isoformat()
    slug = normalize_slug(args.slug)
    if not slug:
        raise ValueError("--slug must contain at least one letter or number")

    task_id = f"{today}-{slug}"
    branch = args.branch or f"codex/{task_id}"
    base = args.base or "origin/HEAD"
    if args.path:
        worktree_path = resolve_repo_or_absolute(args.path)
    else:
        worktree_path = resolve_repo_or_absolute(Path(args.worktree_root) / task_id)
    target = repo_path(args.output) if args.output else AGENTIC_TASK_DIR / f"{task_id}.md"
    affected_paths = args.affected_path or ["docs/agentic/", "tools/agentic_design/"]
    evidence = args.evidence or ["validate-task-card", "validate-docs", "validate-inventory"]

    return {
        "task_id": task_id,
        "slug": slug,
        "branch": branch,
        "base": base,
        "worktree_path": worktree_path,
        "target": target,
        "affected_paths": affected_paths,
        "evidence": evidence,
    }


def yaml_lines(values: list[str]) -> str:
    return "\n".join(f"  - {value}" for value in values)


def worktree_task_card_template(args: argparse.Namespace, values: dict[str, Any]) -> str:
    human_gate = "true" if args.human_gate or args.risk == "high" else "false"
    human_gate_reason = args.human_gate_reason
    if human_gate == "true" and not human_gate_reason:
        human_gate_reason = "High-risk or explicitly gated task."
    specialists = args.specialist or ["none"]
    request = args.request.replace('"', '\\"')
    worktree_display = display_path(values["worktree_path"])
    target_display = display_path(values["target"])
    root_arg = quote_for_powershell(ROOT)
    worktree_arg = quote_for_powershell(values["worktree_path"])

    return f"""---
task_id: {values["task_id"]}
status: draft
request: "{request}"
scope: {args.scope}
risk: {args.risk}
owning_agent: {args.owner}
specialist_agents:
{yaml_lines(specialists)}
affected_contracts:
  - none
affected_paths:
{yaml_lines(values["affected_paths"])}
required_evidence:
{yaml_lines(values["evidence"])}
human_gate_required: {human_gate}
human_gate_reason: "{human_gate_reason}"
---

# {values["task_id"]}

## Scope

Execute the task in an isolated worktree and keep the resulting diff scoped to
the request.

Request: {args.request}

Worktree plan:

- Base ref: `{values["base"]}`
- Branch: `{values["branch"]}`
- Worktree path: `{worktree_display}`
- Task card: `{target_display}`

## Non-Goals

- Do not switch branches in the shared Local checkout for this task.
- Do not include unrelated dirty files from another session.
- Do not redefine solver architecture contracts unless the task scope names
  that boundary.

## Context To Read

- `docs/agentic/lifecycle-runbook.md`
- `docs/research/20260524/ai-agent-git-worktree-workflow-for-gcs.md`
- Owning skill: `{args.owner}`

## Acceptance Gates

- The worktree path, branch, base ref, and merge order are explicit.
- Implementation stays inside the affected paths or records why scope changed.
- Required evidence is produced or an explicit skip reason is recorded.

## Verification Plan

```bat
python tools\\agentic_design\\agentic_toolkit.py validate-task-card docs\\agentic\\tasks\\{values["task_id"]}.md
```

## Worktree Commands

```powershell
git -C {root_arg} fetch origin
git -C {root_arg} worktree add -b {quote_for_powershell(values["branch"])} {worktree_arg} {quote_for_powershell(values["base"])}
git -C {worktree_arg} status --short --branch
```

After completion:

```powershell
git worktree remove {worktree_arg}
git worktree prune
```

## Evidence Bundle

Evidence will be added after the worktree task runs. At minimum, include the
final `git status --short --branch`, the validation commands, pass/fail
summaries, and any skipped checks.

## Residual Risks

The generated commands do not create the worktree until an operator runs them.
Review the base ref and current dirty-tree state before executing mutating Git
commands.
"""


def new_worktree_task(args: argparse.Namespace) -> int:
    values = worktree_task_values(args)
    text = worktree_task_card_template(args, values)

    if args.write:
        write_text(values["target"], text, args.force)
        print(f"wrote {display_path(values['target'])}")

    commands = [
        f"git -C {quote_for_powershell(ROOT)} fetch origin",
        (
            f"git -C {quote_for_powershell(ROOT)} worktree add -b "
            f"{quote_for_powershell(values['branch'])} "
            f"{quote_for_powershell(values['worktree_path'])} "
            f"{quote_for_powershell(values['base'])}"
        ),
        f"git -C {quote_for_powershell(values['worktree_path'])} status --short --branch",
    ]
    if args.json:
        print(json.dumps({
            "task_id": values["task_id"],
            "task_card": display_path(values["target"]),
            "branch": values["branch"],
            "base": values["base"],
            "worktree_path": str(values["worktree_path"]),
            "commands": commands,
        }, indent=2, sort_keys=True))
    else:
        print(f"task_id: {values['task_id']}")
        print(f"task_card: {display_path(values['target'])}")
        print(f"branch: {values['branch']}")
        print(f"base: {values['base']}")
        print(f"worktree_path: {values['worktree_path']}")
        print("commands:")
        for command in commands:
            print(f"  {command}")
    return 0


def validate_task_card_command(args: argparse.Namespace) -> int:
    paths = [repo_path(path) if not Path(path).is_absolute() else Path(path) for path in args.paths]
    results: list[CheckResult] = []
    for path in paths:
        results.extend(validate_task_card_file(path))
    return run_checks(results)


def validate_task_card_includes_command(args: argparse.Namespace) -> int:
    return run_checks(validate_task_card_includes(args.pathspecs))


COMPLETED_TASK_REQUIRED_SECTIONS = [
    "## Task Objective",
    "## Scope And Non-Goals",
    "## Interaction Summary",
    "## Work Completed",
    "## Files And Artifacts",
    "## Evidence",
    "## Decisions",
    "## Skipped Checks And Risks",
    "## Follow-Up",
    "## Archive Handoff",
]


COMPLETED_TASK_PLACEHOLDERS = [
    "Write the concrete task objective.",
    "Describe what was in scope.",
    "Describe what stayed out of scope.",
    "Summarize the important turns.",
    "List completed work.",
    "path/to/file",
    "<command or check>",
    "<pass/fail summary>",
    "Record key decisions.",
    "Record skipped checks.",
    "Pending:",
    "TODO",
]


def completed_task_report_template(args: argparse.Namespace) -> str:
    today = args.date or _datetime.date.today().isoformat()
    slug = normalize_slug(args.slug)
    task_id = f"{today}-{slug}"
    session_goal = args.session_goal.replace('"', '\\"')
    archive_target = f"docs/completed-tasks/{task_id}/"
    experience_links = args.experience_link or []
    experience_lines = "\n".join(f"  - {item}" for item in experience_links)
    if not experience_lines:
        experience_lines = "  - none"

    return f"""---
task_id: {task_id}
status: {args.status}
session_goal: "{session_goal}"
archive_target: {archive_target}
experience_links:
{experience_lines}
---

# {args.title or task_id}

## Task Objective

Write the concrete task objective.

## Scope And Non-Goals

In scope:

- Describe what was in scope.

Out of scope:

- Describe what stayed out of scope.

## Interaction Summary

Summarize the important turns without copying raw chat logs.

## Work Completed

- List completed work.

## Files And Artifacts

- `path/to/file`: why it changed or why it was produced.

## Evidence

```text
<command or check>
<pass/fail summary>
```

## Decisions

- Record key decisions and their rationale.

## Skipped Checks And Risks

- Record skipped checks, reasons, and residual risks.

## Follow-Up

- Separate future work from completed work.

## Archive Handoff

- Archive path: `{archive_target}`
- Related experience:
{experience_lines}
- Skill, eval, fixture, or tool update needed:
"""


def new_completed_task_report(args: argparse.Namespace) -> int:
    today = args.date or _datetime.date.today().isoformat()
    slug = normalize_slug(args.slug)
    if not slug:
        raise ValueError("--slug must contain at least one letter or number")
    target = repo_path(args.output) if args.output else COMPLETED_TASK_DIR / f"{today}-{slug}" / "README.md"
    text = completed_task_report_template(args)
    if args.write:
        write_text(target, text, args.force)
        print(f"wrote {display_path(target)}")
    else:
        print(f"# target: {display_path(target)}")
        print(text)
    return 0


def validate_completed_task_report_file(path: Path,
                                        require_index: bool = True) -> list[CheckResult]:
    results: list[CheckResult] = []
    if not path.exists():
        return [CheckResult(False, f"completed-task-report: missing file {path}")]
    if path.name.lower() != "readme.md":
        results.append(CheckResult(False, f"{display_path(path)}: completed-task reports must be README.md files"))

    text = read_text(path)
    data = parse_frontmatter_values(text)
    required_fields = [
        "task_id",
        "status",
        "session_goal",
        "archive_target",
    ]
    for field in required_fields:
        if field not in data or data[field] in ("", []):
            results.append(CheckResult(False, f"{display_path(path)}: missing frontmatter field {field}"))

    task_id = str(data.get("task_id", ""))
    if task_id and not re.match(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*$", task_id):
        results.append(CheckResult(False, f"{display_path(path)}: task_id must look like YYYY-MM-DD-slug"))
    if task_id and path.parent.name != task_id:
        results.append(CheckResult(False, f"{display_path(path)}: folder name must match task_id {task_id}"))

    valid_statuses = {"complete", "accepted_with_risk", "blocked", "abandoned"}
    status = str(data.get("status", ""))
    if status and status not in valid_statuses:
        results.append(CheckResult(False, f"{display_path(path)}: status must be one of {sorted(valid_statuses)}"))

    archive_target = str(data.get("archive_target", "")).replace("\\", "/").rstrip("/")
    expected_archive = f"docs/completed-tasks/{path.parent.name}"
    if archive_target and archive_target != expected_archive:
        results.append(CheckResult(
            False,
            f"{display_path(path)}: archive_target {archive_target!r} must be {expected_archive!r}",
        ))

    for section in COMPLETED_TASK_REQUIRED_SECTIONS:
        body = section_body(text, section)
        if not body:
            results.append(CheckResult(False, f"{display_path(path)}: missing or empty section {section}"))

    for pattern in COMPLETED_TASK_PLACEHOLDERS:
        if pattern in text:
            results.append(CheckResult(False, f"{display_path(path)}: placeholder text remains: {pattern}"))

    evidence = section_body(text, "## Evidence")
    if evidence and not (
        "```" in evidence
        or "[OK]" in evidence
        or "Passed" in evidence
        or "Skipped" in evidence
        or "not relevant" in evidence.lower()
    ):
        results.append(CheckResult(
            False,
            f"{display_path(path)}: Evidence section must include commands, pass/fail summaries, or explicit skipped checks",
        ))

    if re.search(r"^\s*(User|Assistant|Tool):", text, flags=re.MULTILINE):
        results.append(CheckResult(False, f"{display_path(path)}: raw chat transcript marker appears in report"))

    for link in normalize_list(data.get("experience_links")):
        if link.lower() == "none":
            continue
        target = repo_path(link)
        if not target.exists():
            results.append(CheckResult(False, f"{display_path(path)}: experience link does not exist: {link}"))

    if require_index and path.is_relative_to(COMPLETED_TASK_DIR) and path != COMPLETED_TASK_DIR / "README.md":
        if not has_index_link(path):
            results.append(CheckResult(False, f"{display_path(path)}: missing index link in docs/completed-tasks/README.md"))

    if not results:
        results.append(CheckResult(True, f"completed-task-report: {display_path(path)} passed"))
    return results


def validate_completed_task_report_command(args: argparse.Namespace) -> int:
    paths = [repo_path(path) if not Path(path).is_absolute() else Path(path) for path in args.paths]
    results: list[CheckResult] = []
    for path in paths:
        results.extend(validate_completed_task_report_file(path, require_index=not args.skip_index_check))
    return run_checks(results)


def validate_completed_report_includes_command(args: argparse.Namespace) -> int:
    return run_checks(validate_completed_report_includes(
        args.pathspecs,
        require_index=not args.skip_index_check,
    ))


def pr_path_metadata(path: str) -> tuple[str, str, str]:
    normalized = normalize_repo_path(path)
    if normalized.startswith("fixtures/scene/"):
        return "scene-exploration", "high", "Scene fixture corpus"
    if normalized.startswith("tools/scene_generation/"):
        return "scene-exploration", "medium", "Scene generation tooling"
    if normalized.startswith(("src/gcs/", "apps/gcs_cli/", "tests/gcs/")):
        return "solver-contract", "high", "Solver public contract or contract tests"
    if normalized.startswith("python/gcs_viz/"):
        return "solver-contract", "high", "Viewer bridge and diagnostic projection contract"
    if normalized in {"CMakeLists.txt", "CMakePresets.json"} or normalized.startswith("cmake/"):
        return "quality-gate", "high", "Build and quality-gate configuration"
    if normalized.startswith("tools/agentic_design/"):
        return "quality-gate", "medium", "Agentic toolkit command surface"
    if normalized.startswith("tests/tools/"):
        return "quality-gate", "medium", "Agentic and support-tool tests"
    if normalized.startswith("docs/architecture/"):
        return "architecture", "medium", "Architecture design contract"
    if normalized.startswith(("docs/agentic/", ".codex/skills/")):
        return "agentic-process", "medium", "Agentic operating layer"
    if normalized.startswith("docs/research/"):
        return "exploratory", "low", "Research and exploratory evidence"
    if normalized.startswith("docs/") or normalized.endswith(".md"):
        return "docs-only", "low", "Documentation"
    return "exploratory", "medium", "Unclassified repository path"


def infer_pr_class(paths: list[str]) -> str:
    if not paths:
        return "exploratory"
    classes = [pr_path_metadata(path)[0] for path in paths]
    return max(classes, key=lambda item: PR_CLASS_PRIORITY.get(item, 0))


def infer_pr_risk(paths: list[str]) -> str:
    if not paths:
        return "medium"
    risks = [pr_path_metadata(path)[1] for path in paths]
    return max(risks, key=lambda item: RISK_PRIORITY.get(item, 0))


def infer_affected_contracts(paths: list[str]) -> list[str]:
    contracts = [pr_path_metadata(path)[2] for path in paths]
    return unique_preserve_order(contracts) or ["none"]


def infer_task_card_from_paths(paths: list[str]) -> str | None:
    for path in paths:
        normalized = normalize_repo_path(path)
        if normalized.startswith("docs/agentic/tasks/") and normalized.endswith(".md"):
            return normalized
    return None


def infer_completed_archive_from_paths(paths: list[str]) -> str | None:
    for path in paths:
        normalized = normalize_repo_path(path)
        match = re.match(r"^(docs/completed-tasks/[^/]+)/README\.md$", normalized)
        if match:
            return match.group(1)
    return None


def recommended_pr_evidence(paths: list[str]) -> list[str]:
    evidence: list[str] = []
    normalized_paths = [normalize_repo_path(path) for path in paths]
    if any(path.startswith("docs/agentic/tasks/") for path in normalized_paths):
        evidence.append("validate-task-card for changed task cards")
    if any(re.match(r"^docs/completed-tasks/[^/]+/README\.md$", path) for path in normalized_paths):
        evidence.append("validate-completed-task-report for changed archives")
        evidence.append("score-closure-report for changed archives")
    if any(path.startswith(("tools/agentic_design/", "tests/tools/")) for path in normalized_paths):
        evidence.append("python -m unittest tests.tools.test_agentic_toolkit")
    if any(path.startswith(("docs/agentic/", "docs/architecture/")) for path in normalized_paths):
        evidence.append("validate-docs")
    if any(path.startswith("tools/scene_generation/") for path in normalized_paths):
        evidence.append("python -m unittest tests.tools.test_scene_generation_explorer")
    if any(path.startswith(("src/gcs/", "apps/gcs_cli/", "fixtures/scene/", "python/gcs_viz/")) for path in normalized_paths):
        evidence.append("focused contract tests or explicit skip risk")
    return unique_preserve_order(evidence)


def parse_skipped_evidence(value: str) -> dict[str, str]:
    parts = value.split("::", 2)
    if len(parts) != 3:
        raise ValueError("--evidence-skipped values must use CHECK::REASON::RISK")
    return {
        "check": parts[0].strip(),
        "reason": parts[1].strip(),
        "risk": parts[2].strip(),
    }


def evidence_item_satisfied(item: str, passed: list[str], failed: list[str], skipped: list[dict[str, str]]) -> bool:
    haystack = passed + failed + [entry.get("check", "") for entry in skipped]
    item_lower = item.lower()
    keys = unique_preserve_order([item_lower, item_lower.split(" for ", 1)[0]])
    return any(
        key and (key in candidate.lower() or candidate.lower() in key)
        for key in keys
        for candidate in haystack
    )


def build_pr_audit(base: str,
                   head: str,
                   changed_paths: list[str],
                   task_card: str | None = None,
                   completed_archive: str | None = None,
                   evidence_passed: list[str] | None = None,
                   evidence_failed: list[str] | None = None,
                   evidence_skipped: list[dict[str, str]] | None = None) -> dict[str, Any]:
    paths = unique_preserve_order([normalize_repo_path(path) for path in changed_paths])
    pr_class = infer_pr_class(paths)
    risk = infer_pr_risk(paths)
    passed = unique_preserve_order(evidence_passed or [])
    failed = unique_preserve_order(evidence_failed or [])
    skipped = list(evidence_skipped or [])
    recommendations = recommended_pr_evidence(paths)

    for item in recommendations:
        if not evidence_item_satisfied(item, passed, failed, skipped):
            skipped.append({
                "check": item,
                "reason": "audit-pr records recommended evidence but does not execute it",
                "risk": "review readiness depends on this evidence",
            })

    task_card = task_card or infer_task_card_from_paths(paths)
    completed_archive = completed_archive or infer_completed_archive_from_paths(paths)
    findings: list[dict[str, str]] = []

    if not paths:
        findings.append({
            "severity": "P2",
            "category": "process",
            "subject": "diff",
            "summary": "No changed paths were found for the requested base/head range.",
        })
    if risk != "low" and not task_card:
        findings.append({
            "severity": "P2",
            "category": "evidence",
            "subject": "task_card",
            "summary": "Medium or high risk PR audit should link a task card or justify why one is absent.",
        })
    if failed:
        findings.append({
            "severity": "P1",
            "category": "evidence",
            "subject": "evidence.failed",
            "summary": "One or more evidence checks are recorded as failed.",
        })
    if any(path.startswith("fixtures/scene/") for path in paths):
        findings.append({
            "severity": "P1",
            "category": "process",
            "subject": "fixtures/scene",
            "summary": "Scene fixture changes require explicit promotion evidence and a human gate.",
        })
    if skipped:
        findings.append({
            "severity": "P2",
            "category": "evidence",
            "subject": "evidence.skipped",
            "summary": "Recommended evidence is missing or explicitly skipped.",
        })

    if not paths:
        decision = "blocked"
        next_action = "revise"
    elif any(item["severity"] in {"P0", "P1"} for item in findings):
        decision = "needs_author_revision"
        next_action = "revise"
    elif risk == "high":
        decision = "needs_human_gate"
        next_action = "human_review"
    elif skipped:
        decision = "needs_author_revision"
        next_action = "run_gate"
    elif pr_class == "exploratory":
        decision = "exploratory_only"
        next_action = "close_exploratory"
    else:
        decision = "ready_for_human_review"
        next_action = "human_review"

    return {
        "schema_version": PR_AUDIT_SCHEMA_VERSION,
        "generated_at": _datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "base": base,
        "head": head,
        "pr_class": pr_class,
        "risk_tier": risk,
        "decision": decision,
        "task_card": task_card,
        "completed_archive": completed_archive,
        "affected_contracts": infer_affected_contracts(paths),
        "affected_paths": paths,
        "evidence": {
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
        },
        "review_focus": infer_affected_contracts(paths)[:5] + paths[:10],
        "forbidden_action_check": {
            "merge": "not_performed",
            "approve": "not_performed",
            "force_push": "not_performed",
            "branch_delete": "not_performed",
            "fixture_promotion": "not_performed",
        },
        "findings": findings,
        "next_action": next_action,
    }


def git_name_only(args: list[str]) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def changed_paths_for_audit(base: str, head: str, include_worktree: bool = False) -> list[str]:
    try:
        paths = git_name_only(["diff", "--name-only", f"{base}...{head}"])
    except RuntimeError:
        paths = git_name_only(["diff", "--name-only", base, head])
    if include_worktree:
        paths.extend(git_name_only(["diff", "--name-only"]))
        paths.extend(git_name_only(["diff", "--cached", "--name-only"]))
        paths.extend(git_name_only(["ls-files", "--others", "--exclude-standard"]))
    return unique_preserve_order([normalize_repo_path(path) for path in paths])


def audit_pr_command(args: argparse.Namespace) -> int:
    skipped = [parse_skipped_evidence(value) for value in args.evidence_skipped]
    audit = build_pr_audit(
        base=args.base,
        head=args.head,
        changed_paths=changed_paths_for_audit(args.base, args.head, args.include_worktree),
        task_card=args.task_card or None,
        completed_archive=args.completed_archive or None,
        evidence_passed=args.evidence_passed,
        evidence_failed=args.evidence_failed,
        evidence_skipped=skipped,
    )
    text = json.dumps(audit, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = resolve_repo_or_absolute(args.output)
        write_text(target, text, args.force)
        print(f"wrote {display_path(target)}")
    else:
        print(text, end="")
    return 0


def validate_pr_audit_record(record: dict[str, Any], source: Path | None = None) -> list[CheckResult]:
    label = display_path(source) if source else "pr-audit"
    results: list[CheckResult] = []
    required_fields = [
        "schema_version",
        "generated_at",
        "base",
        "head",
        "pr_class",
        "risk_tier",
        "decision",
        "task_card",
        "completed_archive",
        "affected_contracts",
        "affected_paths",
        "evidence",
        "review_focus",
        "forbidden_action_check",
        "findings",
        "next_action",
    ]
    for field in required_fields:
        if field not in record:
            results.append(CheckResult(False, f"{label}: missing field {field}"))

    if record.get("schema_version") != PR_AUDIT_SCHEMA_VERSION:
        results.append(CheckResult(False, f"{label}: schema_version must be {PR_AUDIT_SCHEMA_VERSION}"))

    valid_classes = set(PR_CLASS_PRIORITY)
    if record.get("pr_class") not in valid_classes:
        results.append(CheckResult(False, f"{label}: invalid pr_class {record.get('pr_class')!r}"))

    valid_risks = set(RISK_PRIORITY)
    if record.get("risk_tier") not in valid_risks:
        results.append(CheckResult(False, f"{label}: invalid risk_tier {record.get('risk_tier')!r}"))

    valid_decisions = {
        "ready_for_human_review",
        "needs_author_revision",
        "needs_human_gate",
        "exploratory_only",
        "blocked",
    }
    if record.get("decision") not in valid_decisions:
        results.append(CheckResult(False, f"{label}: invalid decision {record.get('decision')!r}"))

    valid_next_actions = {
        "human_review",
        "revise",
        "create_task_card",
        "run_gate",
        "split_pr",
        "close_exploratory",
    }
    if record.get("next_action") not in valid_next_actions:
        results.append(CheckResult(False, f"{label}: invalid next_action {record.get('next_action')!r}"))

    affected_paths = record.get("affected_paths", [])
    if not isinstance(affected_paths, list) or not all(isinstance(path, str) for path in affected_paths):
        results.append(CheckResult(False, f"{label}: affected_paths must be a list of strings"))
        affected_paths = []
    elif not affected_paths and record.get("decision") != "blocked":
        results.append(CheckResult(False, f"{label}: affected_paths must not be empty unless blocked"))

    affected_contracts = record.get("affected_contracts", [])
    if not isinstance(affected_contracts, list) or not all(isinstance(item, str) for item in affected_contracts):
        results.append(CheckResult(False, f"{label}: affected_contracts must be a list of strings"))

    review_focus = record.get("review_focus", [])
    if not isinstance(review_focus, list) or not all(isinstance(item, str) for item in review_focus):
        results.append(CheckResult(False, f"{label}: review_focus must be a list of strings"))

    evidence = record.get("evidence", {})
    if not isinstance(evidence, dict):
        results.append(CheckResult(False, f"{label}: evidence must be an object"))
        evidence = {}
    passed = evidence.get("passed", [])
    failed = evidence.get("failed", [])
    skipped = evidence.get("skipped", [])
    for field, value in [("passed", passed), ("failed", failed)]:
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            results.append(CheckResult(False, f"{label}: evidence.{field} must be a list of strings"))
    if not isinstance(skipped, list):
        results.append(CheckResult(False, f"{label}: evidence.skipped must be a list"))
        skipped = []
    else:
        for index, item in enumerate(skipped):
            if not isinstance(item, dict):
                results.append(CheckResult(False, f"{label}: evidence.skipped[{index}] must be an object"))
                continue
            for field in ["check", "reason", "risk"]:
                if not str(item.get(field, "")).strip():
                    results.append(CheckResult(False, f"{label}: evidence.skipped[{index}] missing {field}"))

    forbidden = record.get("forbidden_action_check", {})
    if not isinstance(forbidden, dict):
        results.append(CheckResult(False, f"{label}: forbidden_action_check must be an object"))
        forbidden = {}
    required_forbidden = ["merge", "approve", "force_push", "branch_delete", "fixture_promotion"]
    for action in required_forbidden:
        if action not in forbidden:
            results.append(CheckResult(False, f"{label}: forbidden_action_check missing {action}"))
    for action in ["merge", "approve", "force_push", "branch_delete"]:
        if forbidden.get(action) != "not_performed":
            results.append(CheckResult(False, f"{label}: unattended {action} is forbidden"))
    if forbidden.get("fixture_promotion") == "performed_without_gate":
        results.append(CheckResult(False, f"{label}: fixture promotion without a gate is forbidden"))
    if forbidden.get("fixture_promotion") not in {"not_performed", "explicitly_authorized", None}:
        if forbidden.get("fixture_promotion") != "performed_without_gate":
            results.append(CheckResult(False, f"{label}: invalid fixture_promotion value {forbidden.get('fixture_promotion')!r}"))

    findings = record.get("findings", [])
    if not isinstance(findings, list):
        results.append(CheckResult(False, f"{label}: findings must be a list"))
        findings = []
    serious_findings = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            results.append(CheckResult(False, f"{label}: findings[{index}] must be an object"))
            continue
        severity = finding.get("severity")
        if severity not in {"P0", "P1", "P2", "P3"}:
            results.append(CheckResult(False, f"{label}: findings[{index}] has invalid severity {severity!r}"))
        if severity in {"P0", "P1", "P2"}:
            serious_findings.append(finding)
        for field in ["category", "subject", "summary"]:
            if not str(finding.get(field, "")).strip():
                results.append(CheckResult(False, f"{label}: findings[{index}] missing {field}"))

    task_card = record.get("task_card")
    if record.get("risk_tier") in {"medium", "high"} and not task_card:
        results.append(CheckResult(False, f"{label}: medium/high risk PR audits require task_card"))
    if isinstance(task_card, str) and task_card:
        task_path = resolve_repo_or_absolute(task_card)
        if not task_path.exists():
            results.append(CheckResult(False, f"{label}: task_card does not exist: {task_card}"))

    completed_archive = record.get("completed_archive")
    if isinstance(completed_archive, str) and completed_archive:
        archive_path = resolve_repo_or_absolute(completed_archive)
        if archive_path.is_dir():
            archive_path = archive_path / "README.md"
        if not archive_path.exists():
            results.append(CheckResult(False, f"{label}: completed_archive does not exist: {completed_archive}"))

    if record.get("risk_tier") == "high" and record.get("decision") == "ready_for_human_review":
        results.append(CheckResult(False, f"{label}: high-risk audit cannot be ready without a human gate"))
    if record.get("decision") == "ready_for_human_review":
        if failed:
            results.append(CheckResult(False, f"{label}: ready audit cannot include failed evidence"))
        if skipped:
            results.append(CheckResult(False, f"{label}: ready audit cannot include skipped evidence"))
        if serious_findings:
            results.append(CheckResult(False, f"{label}: ready audit cannot include P0/P1/P2 findings"))

    if not results:
        results.append(CheckResult(True, f"pr-audit: {label} passed"))
    return results


def validate_pr_audit_file(path: Path) -> list[CheckResult]:
    if not path.exists():
        return [CheckResult(False, f"pr-audit: missing file {path}")]
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        return [CheckResult(False, f"{display_path(path)}: invalid JSON: {exc}")]
    if not isinstance(data, dict):
        return [CheckResult(False, f"{display_path(path)}: top-level JSON must be an object")]
    return validate_pr_audit_record(data, path)


def validate_pr_audit_command(args: argparse.Namespace) -> int:
    paths = [repo_path(path) if not Path(path).is_absolute() else Path(path) for path in args.paths]
    results: list[CheckResult] = []
    for path in paths:
        results.extend(validate_pr_audit_file(path))
    return run_checks(results)


def summarize_nightly_run(run_dir: Path) -> dict[str, Any]:
    findings_path = run_dir / "findings.json"
    summary: dict[str, Any] = {
        "date": run_dir.name,
        "path": display_path(run_dir),
        "status": "missing_findings_json",
        "findings_count": 0,
        "severity_counts": {},
        "category_counts": {},
        "skipped_checks_count": 0,
    }
    if not findings_path.exists():
        return summary

    try:
        data = json.loads(read_text(findings_path))
    except json.JSONDecodeError as exc:
        summary["status"] = "invalid_findings_json"
        summary["error"] = str(exc)
        return summary

    findings = data.get("findings", [])
    skipped_checks = data.get("skipped_checks", [])
    severity_counts = Counter(str(item.get("severity", "unknown")) for item in findings if isinstance(item, dict))
    category_counts = Counter(str(item.get("category", "unknown")) for item in findings if isinstance(item, dict))
    summary.update({
        "status": data.get("status", "unknown"),
        "findings_count": len(findings) if isinstance(findings, list) else 0,
        "severity_counts": dict(sorted(severity_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "skipped_checks_count": len(skipped_checks) if isinstance(skipped_checks, list) else 0,
    })
    return summary


def nightly_index_markdown(runs_dir: Path, generated_at: str | None = None) -> str:
    generated_at = generated_at or _datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    run_dirs = sorted(
        [path for path in runs_dir.iterdir() if path.is_dir() and re.match(r"^\d{4}-\d{2}-\d{2}$", path.name)],
        key=lambda path: path.name,
        reverse=True,
    ) if runs_dir.exists() else []
    summaries = [summarize_nightly_run(path) for path in run_dirs]

    lines = [
        "# GCS Nightly Diagnostic Runs",
        "",
        "Status: calibration in progress.",
        f"Generated: {generated_at}.",
        "",
        "This index is generated from dated `findings.json` files under this directory.",
        "",
    ]

    if not summaries:
        lines.extend([
            "## Runs",
            "",
            "No dated nightly runs have been recorded yet.",
            "",
        ])
    else:
        lines.extend([
            "## Runs",
            "",
            "| Date | Status | Findings | P0 | P1 | P2 | P3 | Skipped Checks |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        for summary in summaries:
            counts = summary.get("severity_counts", {})
            date = summary["date"]
            link = f"[{date}]({date}/README.md)"
            lines.append(
                f"| {link} | {summary['status']} | {summary['findings_count']} | "
                f"{counts.get('P0', 0)} | {counts.get('P1', 0)} | "
                f"{counts.get('P2', 0)} | {counts.get('P3', 0)} | "
                f"{summary['skipped_checks_count']} |"
            )
        lines.append("")

    category_counts: Counter[str] = Counter()
    for summary in summaries:
        category_counts.update(summary.get("category_counts", {}))
    lines.extend([
        "## Category Totals",
        "",
    ])
    if category_counts:
        lines.extend([
            "| Category | Count |",
            "| --- | ---: |",
        ])
        for category, count in sorted(category_counts.items()):
            lines.append(f"| `{category}` | {count} |")
        lines.append("")
    else:
        lines.extend([
            "No categories have been recorded yet.",
            "",
        ])

    lines.extend([
        "## Calibration Notes",
        "",
    ])
    if len(summaries) < 2:
        remaining = 2 - len(summaries)
        lines.append(f"- First-two-run calibration is still open; {remaining} run(s) remain before tuning repair authority.")
    else:
        lines.append("- First-two-run calibration data is available; review true findings versus noise before expanding repair authority.")
    if len(summaries) < 3:
        lines.append("- Repeated-failure detection needs at least three runs.")
    else:
        lines.append("- Three or more runs are available; repeated categories should be checked for task-card promotion.")
    lines.extend([
        "- This index is informational and does not approve, merge, force-push, delete branches, or promote fixtures.",
        "",
    ])

    return "\n".join(lines)


def update_nightly_index_command(args: argparse.Namespace) -> int:
    runs_dir = resolve_repo_or_absolute(args.runs_dir)
    output = resolve_repo_or_absolute(args.output)
    text = nightly_index_markdown(runs_dir) + "\n"
    write_text(output, text, args.force)
    print(f"wrote {display_path(output)}")
    return 0


def score_from_body(body: str, score_if_good: int = 3) -> int:
    if not body:
        return 0
    if len(body) < 40:
        return 1
    if len(body) < 120:
        return 2
    return score_if_good


def closure_score_dimensions(path: Path) -> list[ScoreDimension]:
    if not path.exists():
        return [ScoreDimension("file", 0, f"missing file {path}")]

    text = read_text(path)
    data = parse_frontmatter_values(text)
    objective = section_body(text, "## Task Objective")
    scope = section_body(text, "## Scope And Non-Goals")
    evidence = section_body(text, "## Evidence")
    files = section_body(text, "## Files And Artifacts")
    decisions = section_body(text, "## Decisions")
    risks = section_body(text, "## Skipped Checks And Risks")
    follow_up = section_body(text, "## Follow-Up")
    archive = section_body(text, "## Archive Handoff")
    work = section_body(text, "## Work Completed")

    dimensions: list[ScoreDimension] = []

    objective_score = score_from_body(objective)
    if objective and data.get("session_goal") and len(objective) >= 80:
        objective_score = 4
    dimensions.append(ScoreDimension("objective_clarity", objective_score, "task objective and session_goal coverage"))

    scope_score = score_from_body(scope)
    if "In scope" in scope and "Out of scope" in scope:
        scope_score = min(4, scope_score + 1)
    dimensions.append(ScoreDimension("scope_discipline", scope_score, "scope and non-goal separation"))

    evidence_score = score_from_body(evidence)
    if "```" in evidence and ("[OK]" in evidence or "Passed" in evidence or "Skipped" in evidence):
        evidence_score = 4
    dimensions.append(ScoreDimension("evidence_completeness", evidence_score, "commands and interpreted results"))

    files_score = score_from_body(files)
    if "`" in files and ":" in files:
        files_score = min(4, files_score + 1)
    dimensions.append(ScoreDimension("changed_state_traceability", files_score, "paths mapped to task reasons"))

    decisions_score = score_from_body(decisions)
    if "rationale" in decisions.lower() or "because" in decisions.lower():
        decisions_score = min(4, decisions_score + 1)
    dimensions.append(ScoreDimension("decision_traceability", decisions_score, "durable rationale capture"))

    risk_score = score_from_body(risks)
    if "skipped" in risks.lower() and ("risk" in risks.lower() or "residual" in risks.lower()):
        risk_score = min(4, risk_score + 1)
    dimensions.append(ScoreDimension("risk_visibility", risk_score, "skipped checks and residual risk"))

    archive_score = score_from_body(archive)
    if data.get("archive_target") and has_index_link(path):
        archive_score = min(4, archive_score + 1)
    dimensions.append(ScoreDimension("archive_usefulness", archive_score, "archive target and index discoverability"))

    learning_score = 0
    links = [link for link in normalize_list(data.get("experience_links")) if link.lower() != "none"]
    if links:
        learning_score = 3
    if re.search(r"\b(skill|eval|fixture|tool|experience)\b", archive, flags=re.IGNORECASE):
        learning_score = max(learning_score, 3)
    if links and "needed" in archive.lower():
        learning_score = 4
    dimensions.append(ScoreDimension("learning_promotion", learning_score, "experience or promotion analysis"))

    follow_up_score = score_from_body(follow_up)
    if "future" in follow_up.lower() or "follow" in follow_up.lower():
        follow_up_score = min(4, follow_up_score + 1)
    dimensions.append(ScoreDimension("follow_up_separation", follow_up_score, "future work separated from completed work"))

    report_length = len(text)
    concision_score = 2
    if 1200 <= report_length <= 7000 and work:
        concision_score = 4
    elif 7000 < report_length <= 10000:
        concision_score = 3
    elif report_length < 1200:
        concision_score = 1
    dimensions.append(ScoreDimension("concision_and_signal", concision_score, "rough length and section signal heuristic"))

    return dimensions


def score_closure_report(args: argparse.Namespace) -> int:
    path = repo_path(args.path) if not Path(args.path).is_absolute() else Path(args.path)
    dimensions = closure_score_dimensions(path)
    total = sum(item.score for item in dimensions)
    print(f"Closure score: {total}/40 for {display_path(path)}")
    for item in dimensions:
        print(f"[{item.score:02d}/04] {item.name}: {item.reason}")
    if args.min_score and total < args.min_score:
        print(f"score below required minimum {args.min_score}")
        return 1
    return 0


E002_RECORD_REQUIREMENTS = {
    "e002_phase_step_plan": {
        "frontmatter": ["record_type", "task_id", "status", "current_phase", "current_step", "updated"],
        "headings": [
            "## Task Objective",
            "## Phase Roadmap",
            "## Current Phase",
            "## Step Record",
            "### Step Declaration",
            "### Execution Evidence",
            "### Step Summary",
            "### Current Phase Update",
            "### Commit Boundary",
            "### Next Step Declaration",
            "## Resume Pointer",
        ],
    },
    "e002_step_closure": {
        "frontmatter": ["record_type", "task_id", "phase_id", "step_id", "status", "updated"],
        "headings": [
            "## Step Declaration",
            "## Execution Evidence",
            "## Step Summary",
            "## Current Phase Update",
            "## Commit Boundary",
            "## Next Step Declaration",
        ],
    },
    "e002_phase_summary": {
        "frontmatter": ["record_type", "task_id", "phase_id", "status", "updated"],
        "headings": [
            "## Phase Goal",
            "## Completed Steps",
            "## Phase Result",
            "## Evidence",
            "## Downstream Replanning",
            "## Promotion Decision",
        ],
    },
    "e002_current_status": {
        "frontmatter": ["record_type", "task_id", "status", "current_phase", "current_step", "updated"],
        "headings": [
            "## Current Position",
            "## Completed So Far",
            "## Active Plan",
            "## Next Step Declaration",
            "## Resume Instructions",
        ],
    },
}


E002_PLACEHOLDERS = [
    "replace-with",
    "YYYY-MM-DD",
    "Describe ",
    "Fill ",
    "TODO",
    "TBD",
    "<",
]


def phase_step_plan_template(args: argparse.Namespace) -> str:
    today = args.date or _datetime.date.today().isoformat()
    slug = normalize_slug(args.slug)
    task_id = args.task_id or f"{today}-{slug}"
    title = args.title or f"E002 Phase-Step Plan: {task_id}"
    objective = args.objective.replace('"', '\\"')
    owner = args.owner.replace('"', '\\"')
    phase = args.phase
    step = args.step

    return f"""---
record_type: e002_phase_step_plan
task_id: {task_id}
status: {args.status}
current_phase: {phase}
current_step: {step}
owner: "{owner}"
updated: {today}
---

# {title}

## Task Objective

- Objective: {objective}
- Scope: Describe the work boundary.
- Non-goals: Describe what is intentionally out of scope.
- Acceptance evidence: Describe how completion will be recognized.
- E001 closure target: Describe the final task archive or no-archive reason.

## Phase Roadmap

| Phase | Goal | Initial Steps | Completion Test | Status | Downstream Update Rule |
| --- | --- | --- | --- | --- | --- |
| {phase} | Describe the phase goal. | {step} | Describe the phase completion test. | planned | Replan downstream phases after summary. |

## Current Phase

- Phase id: {phase}
- Phase goal: Describe the phase goal.
- Phase status: planned
- Starting branch: Describe current branch.
- Dirty worktree notes: Describe unrelated worktree state.
- Expected artifacts: Describe expected artifacts.
- Phase completion test: Describe completion test.
- Downstream replanning rule: Describe when downstream phases are updated.

## Step Record

### Step Declaration

- Step id: {step}
- Step status: declared
- Step goal: Describe the step goal.
- Target artifact: Describe target artifact.
- First action: Describe first action.
- Out of scope: Describe exclusions.
- Expected verification: Describe smallest useful check.

### Execution Evidence

- Files changed: TBD
- Commands run: TBD
- Tool observations: TBD
- Verification result: TBD
- Skipped checks: TBD

### Step Summary

- What changed: TBD
- What was learned: TBD
- What remains uncertain: TBD
- Skipped checks: TBD
- Risks: TBD

### Current Phase Update

- Remaining steps before update: TBD
- Changes to remaining steps: TBD
- Newly added steps: TBD
- Deferred steps: TBD
- Superseded steps: TBD
- Reason for update: TBD
- Updated next step: TBD

### Commit Boundary

- Branch checked: TBD
- Staged files inspected: TBD
- Commit scope: TBD
- Commit hash: TBD
- No-commit reason: TBD
- Commit message: TBD

### Next Step Declaration

- Next step id: {step}
- Target artifact: Describe target artifact.
- Purpose: Describe why this step matters.
- First action: Describe first action.
- Blockers or gates: Describe blockers or gates.

## Phase Summary

- Phase result: TBD
- Evidence: TBD
- What changed in downstream plans: TBD
- Deferred work: TBD
- Promotion target considered: TBD
- Next phase: TBD
- Downstream phase updates: TBD

## Resume Pointer

- Current phase: {phase}
- Current step: {step}
- Next action: Describe first action.
- Required context: Describe files to read first.
- Last commit: TBD
"""


def new_phase_step_plan(args: argparse.Namespace) -> int:
    slug = normalize_slug(args.slug)
    if not slug:
        raise ValueError("--slug must contain at least one letter or number")
    today = args.date or _datetime.date.today().isoformat()
    task_id = args.task_id or f"{today}-{slug}"
    target = repo_path(args.output) if args.output else AGENTIC_TASK_DIR / f"{task_id}.phase-step.md"
    text = phase_step_plan_template(args)
    if args.write:
        write_text(target, text, args.force)
        print(f"wrote {display_path(target)}")
    else:
        print(f"# target: {display_path(target)}")
        print(text)
    return 0


def validate_phase_step_record_file(path: Path, allow_placeholders: bool = False) -> list[CheckResult]:
    results: list[CheckResult] = []
    if not path.exists():
        return [CheckResult(False, f"phase-step-record: missing file {path}")]

    text = read_text(path)
    data = parse_frontmatter_values(text)
    record_type = str(data.get("record_type", ""))
    requirements = E002_RECORD_REQUIREMENTS.get(record_type)
    if not requirements:
        known = ", ".join(sorted(E002_RECORD_REQUIREMENTS))
        results.append(CheckResult(False, f"{display_path(path)}: record_type must be one of {known}"))
        return results

    for field in requirements["frontmatter"]:
        if field not in data or data[field] in ("", []):
            results.append(CheckResult(False, f"{display_path(path)}: missing frontmatter field {field}"))

    task_id = str(data.get("task_id", ""))
    if task_id and not allow_placeholders and not re.match(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*$", task_id):
        results.append(CheckResult(False, f"{display_path(path)}: task_id must look like YYYY-MM-DD-slug"))

    for heading in requirements["headings"]:
        body = heading_body(text, heading)
        if not body:
            results.append(CheckResult(False, f"{display_path(path)}: missing or empty heading {heading}"))

    if not allow_placeholders:
        for pattern in E002_PLACEHOLDERS:
            if pattern in text:
                results.append(CheckResult(False, f"{display_path(path)}: placeholder text remains: {pattern}"))

    next_step = extract_next_step_declaration(text)
    if "Next Step Declaration" in "\n".join(requirements["headings"]) and not next_step:
        results.append(CheckResult(False, f"{display_path(path)}: missing next-step declaration body"))

    if not results:
        results.append(CheckResult(True, f"phase-step-record: {display_path(path)} passed"))
    return results


def validate_phase_step_plan_command(args: argparse.Namespace) -> int:
    paths = [repo_path(path) if not Path(path).is_absolute() else Path(path) for path in args.paths]
    results: list[CheckResult] = []
    for path in paths:
        results.extend(validate_phase_step_record_file(path, allow_placeholders=args.allow_placeholders))
    return run_checks(results)


def extract_next_step_declaration(text: str) -> str:
    for heading in ["## Next Step Declaration", "### Next Step Declaration"]:
        body = heading_body(text, heading)
        if body:
            return body
    return ""


def show_next_step(args: argparse.Namespace) -> int:
    path = repo_path(args.path) if not Path(args.path).is_absolute() else Path(args.path)
    if not path.exists():
        print(f"missing file: {display_path(path)}")
        return 1
    next_step = extract_next_step_declaration(read_text(path))
    if not next_step:
        print(f"no next-step declaration found in {display_path(path)}")
        return 1
    print(f"Next step from {display_path(path)}")
    print("==============================")
    print(next_step)
    return 0


def run_checks(checks: list[CheckResult]) -> int:
    failed = False
    for check in checks:
        prefix = "OK" if check.ok else "FAIL"
        print(f"[{prefix}] {check.message}")
        failed = failed or not check.ok
    return 1 if failed else 0


def command_text(command: list[str | os.PathLike[str]]) -> str:
    return " ".join(str(part) for part in command)


def run_process_gate(gate_id: str,
                     command: list[str | os.PathLike[str]]) -> GateResult:
    print(f"[RUN] {gate_id}: {command_text(command)}", flush=True)
    start = time.monotonic()
    completed = subprocess.run(command, cwd=ROOT)
    duration = time.monotonic() - start
    ok = completed.returncode == 0
    prefix = "OK" if ok else "FAIL"
    print(f"[{prefix}] {gate_id}: exit={completed.returncode} duration={duration:.2f}s", flush=True)
    return GateResult(
        gate_id=gate_id,
        ok=ok,
        duration_seconds=duration,
        command=command_text(command),
        exit_code=completed.returncode,
    )


PUBLIC_EVIDENCE_CHAIN_CTEST_REGEX = "|".join(
    [
        (
            r"NumericEngineContract\."
            r"(ConvergesWhenEachResidualIsWithinTolerance|"
            r"SingularRankDoesNotPublishFiniteConditionEstimate|"
            r"RankEvidenceUsesOnlyFreeBoundaryColumns)"
        ),
        (
            r"DiagnosticsContract\."
            r"(PropagatesBoundaryFrozenNumericRankEvidence|"
            r"PromotesNumericResidualBlocks|"
            r"RedundancyCandidatesPreferExactDuplicateConstraints)"
        ),
        (
            r"DecompositionPlannerContract\."
            r"SolveIntentFixedEntitiesBecomeBoundaryVariables"
        ),
        (
            r"IoAdaptersContract\."
            r"(JsonRoundTripPreservesSolveIntentBehavior|"
            r"ShowcaseJsonSceneCarriesSolveIntentBehavior|"
            r"LoadsPythonAuthoredJsonBehaviorScene|"
            r"RejectsShowcaseSceneWithMissingFixedEntity)"
        ),
        (
            r"KernelContract\."
            r"(RejectsSolveIntentMissingReferences|"
            r"RejectsSolveIntentDuplicateReferences)"
        ),
        (
            r"SessionRuntimeContract\."
            r"(ProjectsRankEvidenceFromAcceptedCommandResult|"
            r"PostLocalDiagnosticsPreserveNumericEvidence|"
            r"ReplayArtifactIsRuntimeTraceNotSceneConstructionHistory|"
            r"ReplayEvidenceExportIsDeterministicReportEvidence)"
        ),
        (
            r"ViewerBridgeContract\."
            r"(OverlayProjects.*Evidence|"
            r"ShowcaseFixtureProjectsBoundaryRankAndResidualEvidence|"
            r"RuntimeHistoryFrameProjectsAsReportEvidenceOnly|"
            r"ReplayEvidenceSummaryPreservesRuntimeReportBoundary|"
            r"ReplayEvidenceReportArtifactIsDeterministicAndSceneHistoryFree)"
        ),
        (
            r"ContractToolsContract\."
            r"(BoundaryFrozenFixtureCarriesSolveIntentHint|"
            r"ToleratedResidualFixtureExercisesMaxAbsStopping|"
            r"SeparatorChainFixtureNamesSharedSeparatorEntity|"
            r"IntegratedShowcaseFixtureCarriesPublicEvidenceContract)"
        ),
    ]
)


def ctest_selection_command(build_dir: Path, pattern: str) -> list[str | os.PathLike[str]]:
    return [
        "ctest",
        "--test-dir",
        build_dir,
        "-R",
        pattern,
        "--output-on-failure",
        "--no-tests=error",
    ]


def build_quality_gate_commands(args: argparse.Namespace,
                                script: Path,
                                python: str,
                                build_dir: Path,
                                cli_exe: Path) -> list[GateCommand]:
    commands: list[GateCommand] = []
    if not args.skip_agentic:
        for command in [
            "validate-docs",
            "validate-inventory",
            "validate-skills",
            "check-dependencies",
        ]:
            commands.append(GateCommand(f"agentic.{command}", [python, script, command]))

    task_card_includes = normalize_include_pathspecs(getattr(args, "include_task_cards", []))
    if not task_card_includes:
        current = read_current_task()
        if current and "task_card" in current:
            task_card_includes = [current["task_card"]]
    if task_card_includes:
        commands.append(GateCommand(
            "agentic.task-cards",
            [python, script, "validate-task-card-includes", *task_card_includes],
        ))

    completed_report_includes = normalize_include_pathspecs(getattr(args, "include_completed_reports", []))
    if completed_report_includes:
        commands.append(GateCommand(
            "agentic.completed-task-reports",
            [python, script, "validate-completed-report-includes", *completed_report_includes],
        ))

    if not args.skip_python_tools:
        commands.append(GateCommand(
            "python.scene_generation_explorer",
            [python, "-m", "unittest", "tests.tools.test_scene_generation_explorer"],
        ))
        commands.append(GateCommand(
            "python.agentic_toolkit",
            [python, "-m", "unittest", "tests.tools.test_agentic_toolkit"],
        ))
        commands.append(GateCommand(
            "python.showcase_scene_renderer",
            [python, "-m", "unittest", "tests.tools.test_showcase_scene_renderer"],
        ))
        commands.append(GateCommand(
            "python.showcase_fixture_evidence",
            [python, "tools/architecture_visualization/showcase_fixture_evidence.py"],
        ))
        commands.append(GateCommand(
            "python.showcase_fixture_evidence_tests",
            [python, "-m", "unittest", "tests.tools.test_showcase_fixture_evidence"],
        ))
        commands.append(GateCommand(
            "python.showcase_scene_html_compositor",
            [python, "tools/architecture_visualization/showcase_scene_html_compositor.py", "--check"],
        ))
        commands.append(GateCommand(
            "python.showcase_scene_html_compositor_tests",
            [python, "-m", "unittest", "tests.tools.test_showcase_scene_html_compositor"],
        ))
        commands.append(GateCommand(
            "python.browser_export",
            [python, "-m", "unittest", "tests.tools.test_browser_export"],
        ))
        commands.append(GateCommand(
            "python.gcs_token_lint",
            [python, "tools/ui_qa/gcs_token_lint.py"],
        ))
        commands.append(GateCommand(
            "python.gcs_token_lint_tests",
            [python, "-m", "unittest", "tests.tools.test_gcs_token_lint"],
        ))
        commands.append(GateCommand(
            "python.gcs_text_overflow",
            [python, "tools/ui_qa/gcs_text_overflow.py"],
        ))
        commands.append(GateCommand(
            "python.gcs_text_overflow_tests",
            [python, "-m", "unittest", "tests.tools.test_gcs_text_overflow"],
        ))
        commands.append(GateCommand(
            "python.gcs_overlap_contrast",
            [python, "tools/ui_qa/gcs_overlap_contrast.py"],
        ))
        commands.append(GateCommand(
            "python.gcs_overlap_contrast_tests",
            [python, "-m", "unittest", "tests.tools.test_gcs_overlap_contrast"],
        ))
        commands.append(GateCommand(
            "python.gcs_screenshot_baseline",
            [python, "tools/ui_qa/gcs_screenshot_baseline.py"],
        ))
        commands.append(GateCommand(
            "python.gcs_screenshot_baseline_tests",
            [python, "-m", "unittest", "tests.tools.test_gcs_screenshot_baseline"],
        ))
        commands.append(GateCommand(
            "python.gcs_viz_algebra",
            [python, "-m", "unittest", "tests.tools.test_gcs_viz_algebra"],
        ))
        commands.append(GateCommand(
            "python.gcs_viz_history_replay",
            [python, "-m", "unittest", "tests.tools.test_gcs_viz_history_replay"],
        ))

    if not args.skip_build:
        commands.append(GateCommand("cmake.configure", ["cmake", "--preset", args.preset]))
        commands.append(GateCommand("cmake.build", ["cmake", "--build", "--preset", args.preset]))

    if getattr(args, "include_fixture_library", False):
        commands.append(GateCommand(
            "python.fixture_library_gate",
            [
                python,
                repo_path("tools/scene_generation/fixture_library_gate.py"),
                "--gcs-exe",
                cli_exe,
            ],
        ))

    if getattr(args, "include_repository_audit", False):
        commands.append(GateCommand(
            "python.repository_audit_check",
            [python, repo_path("tools/repository_audit/repository_audit.py"), "check"],
        ))

    if not args.skip_ctest:
        commands.append(GateCommand(
            "ctest.contracts",
            ["ctest", "--test-dir", build_dir, "--output-on-failure", "--no-tests=error"],
        ))
        commands.append(GateCommand(
            "ctest.fixture_corpus",
            ctest_selection_command(build_dir, "ContractToolsContract"),
        ))
        commands.append(GateCommand(
            "ctest.public_evidence_chain",
            ctest_selection_command(build_dir, PUBLIC_EVIDENCE_CHAIN_CTEST_REGEX),
        ))

    if not args.skip_cli:
        commands.append(GateCommand(
            "cli.basic_scene",
            [cli_exe, repo_path("fixtures/scene/basic/g1.txt")],
        ))
        commands.append(GateCommand(
            "cli.showcase_scene",
            [cli_exe, repo_path("fixtures/scene/showcase/integrated_feature_showcase.gcs.json")],
        ))
        commands.append(GateCommand(
            "cli.replay_evidence_basic_scene",
            [cli_exe, repo_path("fixtures/scene/basic/g1.txt"), "--replay-evidence"],
        ))
        commands.append(GateCommand(
            "cli.replay_evidence_report_artifact",
            [
                cli_exe,
                repo_path("fixtures/scene/basic/g1.txt"),
                "--save-replay-evidence",
                build_dir / "replay-evidence-basic.report.json",
            ],
        ))

    return commands


def run_quality_gates(args: argparse.Namespace) -> int:
    script = Path(__file__).resolve()
    python = sys.executable
    build_dir = repo_path(args.build_dir)
    exe_name = "GCS.exe" if os.name == "nt" else "GCS"
    cli_exe = build_dir / exe_name
    results: list[GateResult] = []

    require_card = getattr(args, "require_task_card", False)
    if require_card:
        explicit = normalize_include_pathspecs(getattr(args, "include_task_cards", []))
        if not explicit:
            current = read_current_task()
            if not current:
                print("\n[agentic.task-card] FAIL — --require-task-card set but no task card declared")
                print("  Run 'new-task-card --write' to declare the current task, or use --include-task-cards.")
                return 1

    commands = build_quality_gate_commands(args, script, python, build_dir, cli_exe)

    for gate in commands:
        result = run_process_gate(gate.gate_id, gate.command)
        results.append(result)
        if not result.ok and not args.continue_on_failure:
            break

    failed = [result for result in results if not result.ok]
    print("\nQuality gate summary")
    print("====================")
    for result in results:
        prefix = "OK" if result.ok else "FAIL"
        print(f"[{prefix}] {result.gate_id} ({result.duration_seconds:.2f}s)")

    if failed:
        print("\nFailed gates:")
        for result in failed:
            print(f"- {result.gate_id}: exit={result.exit_code}; command={result.command}")
        return 1

    print("\nAll requested quality gates passed.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GCS agentic design toolkit")
    parser.add_argument(
        "--inventory",
        type=Path,
        default=DEFAULT_INVENTORY,
        help="Path to module_inventory.json",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate-skills", help="Validate physical module skills")
    subparsers.add_parser("validate-inventory", help="Validate structured module inventory")
    subparsers.add_parser("validate-docs", help="Validate architecture design coverage")
    subparsers.add_parser("check-dependencies", help="Check C++23 module import boundaries")

    validate_task = subparsers.add_parser("validate-task-card", help="Validate agentic task-card frontmatter and sections")
    validate_task.add_argument("paths", nargs="+")

    validate_task_includes = subparsers.add_parser(
        "validate-task-card-includes",
        help="Validate task cards selected by explicit file, directory, or glob pathspecs",
    )
    validate_task_includes.add_argument("pathspecs", nargs="+")

    new_task = subparsers.add_parser("new-task-card", help="Create a task-card skeleton")
    new_task.add_argument("--slug", required=True)
    new_task.add_argument("--request", required=True)
    new_task.add_argument("--scope", default="implementation")
    new_task.add_argument("--risk", default="medium")
    new_task.add_argument("--owner", default="gcs-architecture-steward")
    new_task.add_argument("--specialist", action="append", default=[])
    new_task.add_argument("--evidence", action="append", default=[])
    new_task.add_argument("--human-gate", action="store_true")
    new_task.add_argument("--human-gate-reason", default="")
    new_task.add_argument("--date", default="")
    new_task.add_argument("--output", default="")
    new_task.add_argument("--write", action="store_true")
    new_task.add_argument("--force", action="store_true")

    new_worktree = subparsers.add_parser(
        "new-worktree-task",
        help="Create a task card and command plan for an isolated git worktree task",
    )
    new_worktree.add_argument("--slug", required=True)
    new_worktree.add_argument("--request", required=True)
    new_worktree.add_argument("--scope", default="implementation")
    new_worktree.add_argument("--risk", default="medium")
    new_worktree.add_argument("--owner", default="gcs-architecture-steward")
    new_worktree.add_argument("--specialist", action="append", default=[])
    new_worktree.add_argument("--affected-path", action="append", default=[])
    new_worktree.add_argument("--evidence", action="append", default=[])
    new_worktree.add_argument("--human-gate", action="store_true")
    new_worktree.add_argument("--human-gate-reason", default="")
    new_worktree.add_argument("--date", default="")
    new_worktree.add_argument("--base", default="origin/HEAD")
    new_worktree.add_argument("--branch", default="")
    new_worktree.add_argument("--worktree-root", default=".codex/worktrees")
    new_worktree.add_argument("--path", default="")
    new_worktree.add_argument("--output", default="")
    new_worktree.add_argument("--write", action="store_true")
    new_worktree.add_argument("--force", action="store_true")
    new_worktree.add_argument("--json", action="store_true")

    new_completed = subparsers.add_parser(
        "new-completed-task-report",
        help="Create a completed-task execution report skeleton",
    )
    new_completed.add_argument("--slug", required=True)
    new_completed.add_argument("--session-goal", required=True)
    new_completed.add_argument("--title", default="")
    new_completed.add_argument("--status", default="complete")
    new_completed.add_argument("--experience-link", action="append", default=[])
    new_completed.add_argument("--date", default="")
    new_completed.add_argument("--output", default="")
    new_completed.add_argument("--write", action="store_true")
    new_completed.add_argument("--force", action="store_true")

    validate_completed = subparsers.add_parser(
        "validate-completed-task-report",
        help="Validate completed-task report frontmatter, sections, evidence, and archive link",
    )
    validate_completed.add_argument("paths", nargs="+")
    validate_completed.add_argument("--skip-index-check", action="store_true")

    validate_completed_includes = subparsers.add_parser(
        "validate-completed-report-includes",
        help="Validate completed-task reports selected by explicit file, directory, or glob pathspecs",
    )
    validate_completed_includes.add_argument("pathspecs", nargs="+")
    validate_completed_includes.add_argument("--skip-index-check", action="store_true")

    audit_pr = subparsers.add_parser(
        "audit-pr",
        help="Emit a heuristic machine-readable PR audit from a base/head diff",
    )
    audit_pr.add_argument("--base", default="origin/master")
    audit_pr.add_argument("--head", default="HEAD")
    audit_pr.add_argument("--include-worktree", action="store_true")
    audit_pr.add_argument("--task-card", default="")
    audit_pr.add_argument("--completed-archive", default="")
    audit_pr.add_argument("--evidence-passed", action="append", default=[])
    audit_pr.add_argument("--evidence-failed", action="append", default=[])
    audit_pr.add_argument(
        "--evidence-skipped",
        action="append",
        default=[],
        help="Record a skipped check as CHECK::REASON::RISK",
    )
    audit_pr.add_argument("--output", default="")
    audit_pr.add_argument("--force", action="store_true")

    validate_pr_audit = subparsers.add_parser(
        "validate-pr-audit",
        help="Validate PR audit JSON shape, evidence posture, and forbidden action policy",
    )
    validate_pr_audit.add_argument("paths", nargs="+")

    nightly_index = subparsers.add_parser(
        "update-nightly-index",
        help="Generate docs/agentic/nightly-runs/README.md from dated findings.json files",
    )
    nightly_index.add_argument("--runs-dir", default="docs/agentic/nightly-runs")
    nightly_index.add_argument("--output", default="docs/agentic/nightly-runs/README.md")
    nightly_index.add_argument("--force", action="store_true")

    score_closure = subparsers.add_parser(
        "score-closure-report",
        help="Emit a heuristic E001 closure-quality score for a completed-task report",
    )
    score_closure.add_argument("path")
    score_closure.add_argument("--min-score", type=int, default=0)

    new_phase_step = subparsers.add_parser(
        "new-phase-step-plan",
        help="Create an E002 phase-step plan skeleton",
    )
    new_phase_step.add_argument("--slug", required=True)
    new_phase_step.add_argument("--objective", required=True)
    new_phase_step.add_argument("--task-id", default="")
    new_phase_step.add_argument("--title", default="")
    new_phase_step.add_argument("--status", default="draft")
    new_phase_step.add_argument("--owner", default="gcs-architecture-steward")
    new_phase_step.add_argument("--phase", default="phase-1")
    new_phase_step.add_argument("--step", default="step-1")
    new_phase_step.add_argument("--date", default="")
    new_phase_step.add_argument("--output", default="")
    new_phase_step.add_argument("--write", action="store_true")
    new_phase_step.add_argument("--force", action="store_true")

    validate_phase_step = subparsers.add_parser(
        "validate-phase-step-plan",
        help="Validate E002 phase-step, step-closure, phase-summary, or current-status records",
    )
    validate_phase_step.add_argument("paths", nargs="+")
    validate_phase_step.add_argument("--allow-placeholders", action="store_true")

    show_next = subparsers.add_parser(
        "show-next-step",
        help="Print the next-step declaration from an E002 record",
    )
    show_next.add_argument("path")

    gates = subparsers.add_parser(
        "run-quality-gates",
        help="Run CI-ready build, test, scene, and architecture quality gates",
    )
    gates.add_argument("--preset", default="clang-ninja")
    gates.add_argument("--build-dir", default="out/build/clang-ninja")
    gates.add_argument("--skip-agentic", action="store_true")
    gates.add_argument("--skip-python-tools", action="store_true")
    gates.add_argument("--skip-build", action="store_true")
    gates.add_argument("--skip-ctest", action="store_true")
    gates.add_argument("--skip-cli", action="store_true")
    gates.add_argument("--include-task-cards", action="append", default=[])
    gates.add_argument("--include-completed-reports", action="append", default=[])
    gates.add_argument("--include-fixture-library", action="store_true")
    gates.add_argument("--include-repository-audit", action="store_true")
    gates.add_argument("--require-task-card", action="store_true",
        help="Fail if no task card is declared (via --include-task-cards or .claude/current-task) for non-trivial work")
    gates.add_argument("--continue-on-failure", action="store_true")

    card = subparsers.add_parser("emit-design-card", help="Emit JSON design card for a module")
    card.add_argument("--module", required=True)

    test = subparsers.add_parser("scaffold-contract-test", help="Emit or write a contract-test skeleton")
    test.add_argument("--module", required=True)
    test.add_argument("--write", action="store_true")
    test.add_argument("--force", action="store_true")

    module = subparsers.add_parser("scaffold-module", help="Emit or write a C++23 module skeleton")
    module.add_argument("--module", required=True)
    module.add_argument("--write", action="store_true")
    module.add_argument("--force", action="store_true")

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    inventory = load_inventory(args.inventory)

    if args.command == "validate-skills":
        return run_checks(validate_skills(inventory))
    if args.command == "validate-inventory":
        return run_checks(validate_inventory(inventory))
    if args.command == "validate-docs":
        return run_checks(validate_docs(inventory))
    if args.command == "check-dependencies":
        return run_checks(check_dependencies(inventory))
    if args.command == "validate-task-card":
        return validate_task_card_command(args)
    if args.command == "validate-task-card-includes":
        return validate_task_card_includes_command(args)
    if args.command == "new-task-card":
        return new_task_card(args)
    if args.command == "new-worktree-task":
        return new_worktree_task(args)
    if args.command == "new-completed-task-report":
        return new_completed_task_report(args)
    if args.command == "validate-completed-task-report":
        return validate_completed_task_report_command(args)
    if args.command == "validate-completed-report-includes":
        return validate_completed_report_includes_command(args)
    if args.command == "audit-pr":
        return audit_pr_command(args)
    if args.command == "validate-pr-audit":
        return validate_pr_audit_command(args)
    if args.command == "update-nightly-index":
        return update_nightly_index_command(args)
    if args.command == "score-closure-report":
        return score_closure_report(args)
    if args.command == "new-phase-step-plan":
        return new_phase_step_plan(args)
    if args.command == "validate-phase-step-plan":
        return validate_phase_step_plan_command(args)
    if args.command == "show-next-step":
        return show_next_step(args)
    if args.command == "run-quality-gates":
        return run_quality_gates(args)
    if args.command == "emit-design-card":
        return emit_design_card(args, inventory)
    if args.command == "scaffold-contract-test":
        return scaffold_contract_test(args, inventory)
    if args.command == "scaffold-module":
        return scaffold_module(args, inventory)

    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
