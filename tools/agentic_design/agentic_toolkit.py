#!/usr/bin/env python3
"""Agentic design utilities for the GCS architecture rewrite.

The toolkit intentionally uses only the Python standard library so module
agents can run it in restricted local environments.
"""

from __future__ import annotations

import argparse
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


def load_inventory(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def repo_path(path: str | Path) -> Path:
    return ROOT / path


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


def module_by_id(inventory: dict[str, Any], module_id: str) -> dict[str, Any]:
    for module in inventory["modules"]:
        if module["id"] == module_id:
            return module
    known = ", ".join(module["id"] for module in inventory["modules"])
    raise KeyError(f"unknown module '{module_id}'. Known modules: {known}")


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


def run_quality_gates(args: argparse.Namespace) -> int:
    script = Path(__file__).resolve()
    python = sys.executable
    build_dir = repo_path(args.build_dir)
    exe_name = "GCS.exe" if os.name == "nt" else "GCS"
    cli_exe = build_dir / exe_name
    results: list[GateResult] = []

    commands: list[tuple[str, list[str | os.PathLike[str]]]] = []
    if not args.skip_agentic:
        for command in [
            "validate-docs",
            "validate-inventory",
            "validate-skills",
            "check-dependencies",
        ]:
            commands.append((f"agentic.{command}", [python, script, command]))

    if not args.skip_python_tools:
        commands.append((
            "python.scene_generation_explorer",
            [python, "-m", "unittest", "tests.tools.test_scene_generation_explorer"],
        ))

    if not args.skip_build:
        commands.append(("cmake.configure", ["cmake", "--preset", args.preset]))
        commands.append(("cmake.build", ["cmake", "--build", "--preset", args.preset]))

    if not args.skip_ctest:
        commands.append((
            "ctest.contracts",
            ["ctest", "--test-dir", build_dir, "--output-on-failure", "--no-tests=error"],
        ))
        commands.append((
            "ctest.fixture_corpus",
            [
                "ctest",
                "--test-dir",
                build_dir,
                "-R",
                "ContractToolsContract",
                "--output-on-failure",
                "--no-tests=error",
            ],
        ))

    if not args.skip_cli:
        commands.append((
            "cli.basic_scene",
            [cli_exe, repo_path("fixtures/scene/basic/g1.txt")],
        ))

    for gate_id, command in commands:
        result = run_process_gate(gate_id, command)
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
