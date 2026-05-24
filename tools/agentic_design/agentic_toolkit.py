#!/usr/bin/env python3
"""Agentic design utilities for the GCS architecture rewrite.

The toolkit intentionally uses only the Python standard library so module
agents can run it in restricted local environments.
"""

from __future__ import annotations

import argparse
import datetime as _datetime
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = ROOT / "tools" / "agentic_design" / "module_inventory.json"
AGENTIC_TASK_DIR = ROOT / "docs" / "agentic" / "tasks"
COMPLETED_TASK_DIR = ROOT / "docs" / "completed-tasks"


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


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists; pass --force to overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


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
        results.append(CheckResult(True, f"task-card: {path.relative_to(ROOT)} passed"))
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
    target = repo_path(args.output) if args.output else AGENTIC_TASK_DIR / f"{today}-{slug}.md"
    text = task_card_template(args)
    if args.write:
        write_text(target, text, args.force)
        print(f"wrote {target.relative_to(ROOT)}")
    else:
        print(f"# target: {target.relative_to(ROOT)}")
        print(text)
    return 0


def validate_task_card_command(args: argparse.Namespace) -> int:
    paths = [repo_path(path) if not Path(path).is_absolute() else Path(path) for path in args.paths]
    results: list[CheckResult] = []
    for path in paths:
        results.extend(validate_task_card_file(path))
    return run_checks(results)


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
            r"PostLocalDiagnosticsPreserveNumericEvidence)"
        ),
        (
            r"ViewerBridgeContract\."
            r"(OverlayProjects.*Evidence|"
            r"ShowcaseFixtureProjectsBoundaryRankAndResidualEvidence)"
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
            "python.gcs_viz_algebra",
            [python, "-m", "unittest", "tests.tools.test_gcs_viz_algebra"],
        ))

    if not args.skip_build:
        commands.append(GateCommand("cmake.configure", ["cmake", "--preset", args.preset]))
        commands.append(GateCommand("cmake.build", ["cmake", "--build", "--preset", args.preset]))

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

    return commands


def run_quality_gates(args: argparse.Namespace) -> int:
    script = Path(__file__).resolve()
    python = sys.executable
    build_dir = repo_path(args.build_dir)
    exe_name = "GCS.exe" if os.name == "nt" else "GCS"
    cli_exe = build_dir / exe_name
    results: list[GateResult] = []

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

    score_closure = subparsers.add_parser(
        "score-closure-report",
        help="Emit a heuristic E001 closure-quality score for a completed-task report",
    )
    score_closure.add_argument("path")
    score_closure.add_argument("--min-score", type=int, default=0)

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
    if args.command == "new-task-card":
        return new_task_card(args)
    if args.command == "new-completed-task-report":
        return new_completed_task_report(args)
    if args.command == "validate-completed-task-report":
        return validate_completed_task_report_command(args)
    if args.command == "score-closure-report":
        return score_closure_report(args)
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
