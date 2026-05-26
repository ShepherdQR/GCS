from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def snapshot_to_dict(snapshot: Any) -> dict[str, Any]:
    if hasattr(snapshot, "to_dict"):
        return snapshot.to_dict()
    if is_dataclass(snapshot):
        return asdict(snapshot)
    return dict(snapshot)


def _fmt_int(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def _fmt_bool(value: Any) -> str:
    return "yes" if bool(value) else "no"


def _table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return lines


def _groups(snapshot: dict[str, Any], name: str) -> list[dict[str, Any]]:
    groups = snapshot.get("groups", {}).get(name, [])
    return sorted(
        (dict(group) for group in groups),
        key=lambda group: (
            int(group.get("physical_lines", 0)),
            int(group.get("files", 0)),
            str(group.get("key", "")),
        ),
        reverse=True,
    )


def _governance_surface(files: list[dict[str, Any]]) -> dict[str, int]:
    skill_dirs: set[str] = set()
    skill_agent_configs = 0
    institutional_agents: set[str] = set()
    completed_archives: set[str] = set()
    task_cards = 0
    pr_audits = 0

    for metric in files:
        path = str(metric.get("path", ""))
        parts = path.split("/")

        if path.startswith(".codex/skills/") and len(parts) >= 3:
            skill_dirs.add(parts[2])
            if path.endswith("/agents/openai.yaml"):
                skill_agent_configs += 1

        if path.startswith("docs/agentic/institutional-agents/") and len(parts) >= 5:
            role_dir = parts[3]
            if role_dir[:3].isdigit() and parts[-1] == "README.md":
                institutional_agents.add(role_dir)

        if path.startswith("docs/agentic/tasks/") and path.endswith(".md") and parts[-1] != "README.md":
            task_cards += 1

        if path.startswith("docs/completed-tasks/") and len(parts) >= 4 and path.endswith("/README.md"):
            completed_archives.add(parts[2])

        if path.startswith("docs/agentic/pr-audits/") and path.endswith(".json"):
            pr_audits += 1

    return {
        "project_local_skills": len(skill_dirs),
        "skill_agent_configs": skill_agent_configs,
        "institutional_agents": len(institutional_agents),
        "task_cards": task_cards,
        "completed_task_archives": len(completed_archives),
        "pr_audits": pr_audits,
    }


def _top_files(files: list[dict[str, Any]], *, binary: bool, limit: int = 10) -> list[dict[str, Any]]:
    if binary:
        key = lambda metric: int(metric.get("bytes", 0))
        candidates = [metric for metric in files if bool(metric.get("is_binary"))]
    else:
        key = lambda metric: int(metric.get("physical_lines", 0))
        candidates = [metric for metric in files if bool(metric.get("is_text"))]
    return sorted(candidates, key=key, reverse=True)[:limit]


def render_markdown_report(
    snapshot: Any,
    *,
    command: str | None = None,
    max_group_rows: int = 20,
) -> str:
    data = snapshot_to_dict(snapshot)
    totals = data.get("totals", {})
    git = data.get("git", {})
    contract = data.get("counting_contract", {})
    files = [dict(metric) for metric in data.get("files", [])]
    modules = [dict(metric) for metric in data.get("modules", [])]
    findings = [dict(finding) for finding in data.get("findings", [])]
    errors = [finding for finding in findings if finding.get("severity") == "error"]
    warnings = [finding for finding in findings if finding.get("severity") == "warning"]
    governance = _governance_surface(files)

    lines: list[str] = [
        "# GCS Repository Audit",
        "",
        f"Generated: `{data.get('generated_at', '<unknown>')}`",
        f"Repository: `{data.get('repo_root', '<unknown>')}`",
        f"Revision: `{git.get('head') or '<unknown>'}`",
        f"Branch: `{git.get('branch') or '<unknown>'}`",
        f"Dirty worktree: `{_fmt_bool(git.get('dirty'))}`",
        f"Schema: `{data.get('schema_version', '<unknown>')}`",
        f"Tool: `{data.get('tool_version', '<unknown>')}`",
        "",
        "## Executive Summary",
        "",
        (
            f"- Counted {_fmt_int(totals.get('files'))} tracked files, "
            f"{_fmt_int(totals.get('text_files'))} text files, "
            f"{_fmt_int(totals.get('binary_files'))} binary files, and "
            f"{_fmt_int(totals.get('physical_lines'))} physical text lines."
        ),
        (
            f"- Found {_fmt_int(len(errors))} errors and {_fmt_int(len(warnings))} warnings "
            "under the current repository-audit policy."
        ),
        (
            f"- Agentic surface: {_fmt_int(governance['project_local_skills'])} project-local skills, "
            f"{_fmt_int(governance['skill_agent_configs'])} skill agent configs, "
            f"{_fmt_int(governance['institutional_agents'])} institutional agents, "
            f"{_fmt_int(governance['task_cards'])} task cards, and "
            f"{_fmt_int(governance['completed_task_archives'])} completed-task archives."
        ),
        "",
        "## Counting Contract",
        "",
    ]

    lines.extend(
        _table(
            ["Field", "Value"],
            [
                ["tracked_files_only", _fmt_bool(contract.get("tracked_files_only"))],
                ["include_untracked", _fmt_bool(contract.get("include_untracked"))],
                ["include_build_output", _fmt_bool(contract.get("include_build_output"))],
                ["excluded_roots", ", ".join(str(item) for item in contract.get("excluded_roots", []))],
                ["text_extensions", ", ".join(str(item) for item in contract.get("text_extensions", []))],
            ],
        )
    )

    lines.extend([
        "",
        "## Totals",
        "",
    ])
    lines.extend(
        _table(
            ["Metric", "Count"],
            [
                ["files", _fmt_int(totals.get("files"))],
                ["text_files", _fmt_int(totals.get("text_files"))],
                ["binary_files", _fmt_int(totals.get("binary_files"))],
                ["physical_lines", _fmt_int(totals.get("physical_lines"))],
                ["bytes", _fmt_int(totals.get("bytes"))],
            ],
        )
    )

    lines.extend([
        "",
        "## Agentic Governance Surface",
        "",
    ])
    lines.extend(
        _table(
            ["Surface", "Count"],
            [
                ["project_local_skills", _fmt_int(governance["project_local_skills"])],
                ["skill_agent_configs", _fmt_int(governance["skill_agent_configs"])],
                ["institutional_agents", _fmt_int(governance["institutional_agents"])],
                ["task_cards", _fmt_int(governance["task_cards"])],
                ["completed_task_archives", _fmt_int(governance["completed_task_archives"])],
                ["pr_audits", _fmt_int(governance["pr_audits"])],
            ],
        )
    )

    for title, group_name in [
        ("Artifact Class Breakdown", "by_artifact_class"),
        ("Lifecycle Layer Breakdown", "by_lifecycle_layer"),
        ("Top-Level Breakdown", "by_top_level"),
    ]:
        rows = [
            [
                group.get("key", ""),
                _fmt_int(group.get("files")),
                _fmt_int(group.get("text_files")),
                _fmt_int(group.get("binary_files")),
                _fmt_int(group.get("physical_lines")),
            ]
            for group in _groups(data, group_name)[:max_group_rows]
        ]
        lines.extend(["", f"## {title}", ""])
        lines.extend(_table(["Key", "Files", "Text", "Binary", "Lines"], rows))

    module_rows = [
        [
            module.get("module_id", ""),
            _fmt_int(module.get("source_files")),
            _fmt_int(module.get("interface_files")),
            _fmt_int(module.get("implementation_files")),
            _fmt_int(module.get("source_lines")),
            _fmt_int(module.get("contract_test_files")),
            _fmt_int(module.get("contract_test_lines")),
            _fmt_int(module.get("skill_files")),
        ]
        for module in sorted(modules, key=lambda item: str(item.get("module_id", "")))
    ]
    lines.extend(["", "## GCS Module Coverage", ""])
    lines.extend(
        _table(
            [
                "Module",
                "Source Files",
                "Interfaces",
                "Implementations",
                "Source Lines",
                "Contract Tests",
                "Contract Lines",
                "Skill Files",
            ],
            module_rows,
        )
    )

    lines.extend(["", "## Largest Text Files", ""])
    lines.extend(
        _table(
            ["Path", "Class", "Lines"],
            [
                [metric.get("path", ""), metric.get("artifact_class", ""), _fmt_int(metric.get("physical_lines"))]
                for metric in _top_files(files, binary=False)
            ],
        )
    )

    lines.extend(["", "## Largest Binary Files", ""])
    lines.extend(
        _table(
            ["Path", "Class", "Bytes"],
            [
                [metric.get("path", ""), metric.get("artifact_class", ""), _fmt_int(metric.get("bytes"))]
                for metric in _top_files(files, binary=True)
            ],
        )
    )

    lines.extend(["", "## Findings", ""])
    if findings:
        lines.extend(
            _table(
                ["Severity", "ID", "Path", "Recommendation"],
                [
                    [
                        finding.get("severity", ""),
                        finding.get("id", ""),
                        finding.get("path") or "<repo>",
                        finding.get("recommendation", ""),
                    ]
                    for finding in findings
                ],
            )
        )
    else:
        lines.append("No repository-audit findings under the current policy.")

    lines.extend(["", "## Reproduction", ""])
    if command:
        lines.extend(["```bat", command, "```"])
    else:
        lines.append("Generated from an in-memory snapshot; no command string was provided.")

    return "\n".join(lines).rstrip() + "\n"


def write_markdown_report(snapshot: Any, output: Path, *, command: str | None = None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown_report(snapshot, command=command), encoding="utf-8", newline="\n")
