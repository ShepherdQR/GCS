from __future__ import annotations

import datetime as _datetime
import json
import subprocess
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Iterable

from .classify import (
    classify_path,
    extension_for,
    language_hint_for,
    lifecycle_layer_for,
    normalize_path,
    top_level_for,
)
from .models import (
    SCHEMA_VERSION,
    TOOL_VERSION,
    AuditFinding,
    CountingContract,
    FileMetric,
    GitInfo,
    GroupMetric,
    ModuleMetric,
    RepositoryAuditSnapshot,
)
from .policy import check_snapshot


def git_output(repo_root: Path, args: list[str]) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return result.stdout


def collect_tracked_paths(repo_root: Path) -> list[str]:
    output = git_output(repo_root, ["-c", "core.quotepath=false", "ls-files", "-z"])
    paths = output.decode("utf-8", errors="surrogateescape").split("\0")
    return sorted(normalize_path(path) for path in paths if path)


def collect_revision_paths(repo_root: Path, revision: str) -> list[str]:
    output = git_output(
        repo_root,
        ["-c", "core.quotepath=false", "ls-tree", "-r", "-z", "--name-only", revision],
    )
    paths = output.decode("utf-8", errors="surrogateescape").split("\0")
    return sorted(normalize_path(path) for path in paths if path)


def collect_git_info(repo_root: Path, base: str | None = None) -> GitInfo:
    def text(args: list[str]) -> str | None:
        try:
            return git_output(repo_root, args).decode("utf-8", errors="replace").strip() or None
        except subprocess.CalledProcessError:
            return None

    head = text(["rev-parse", "HEAD"])
    branch = text(["branch", "--show-current"])
    dirty_output = text(["status", "--porcelain"]) or ""
    return GitInfo(head=head, branch=branch, dirty=bool(dirty_output), base=base)


def collect_revision_git_info(repo_root: Path, revision: str, base: str | None = None) -> GitInfo:
    try:
        head = git_output(repo_root, ["rev-parse", revision]).decode("utf-8", errors="replace").strip()
    except subprocess.CalledProcessError:
        head = revision
    return GitInfo(head=head or revision, branch=None, dirty=False, base=base)


def load_inventory(repo_root: Path) -> dict:
    path = repo_root / "tools" / "agentic_design" / "module_inventory.json"
    if not path.exists():
        return {"modules": []}
    return json.loads(path.read_text(encoding="utf-8"))


def module_for_path(path: str, inventory: dict) -> str | None:
    path = normalize_path(path)
    for module in inventory.get("modules", []):
        source_dir = normalize_path(str(module.get("source_dir", ""))).rstrip("/")
        contract_test = normalize_path(str(module.get("contract_test", "")))
        skill = normalize_path(str(module.get("skill", ""))).rstrip("/")
        if source_dir and path.startswith(source_dir + "/"):
            return str(module.get("id"))
        if contract_test and path == contract_test:
            return str(module.get("id"))
        if skill and path.startswith(skill + "/"):
            return str(module.get("id"))
    return None


def is_text_extension(extension: str, contract: CountingContract) -> bool:
    return extension.lower() in set(contract.text_extensions)


def count_lines(data: bytes) -> int:
    if not data:
        return 0
    return len(data.splitlines())


def metric_for_data(path: str, data: bytes, inventory: dict, contract: CountingContract) -> FileMetric:
    normalized = normalize_path(path)
    artifact_class = classify_path(normalized)
    extension = extension_for(normalized)
    is_text = is_text_extension(extension, contract)
    byte_count = len(data)
    physical_lines = count_lines(data) if is_text else 0

    return FileMetric(
        path=normalized,
        artifact_class=artifact_class,
        lifecycle_layer=lifecycle_layer_for(artifact_class),
        gcs_module=module_for_path(normalized, inventory),
        extension=extension or "<none>",
        bytes=byte_count,
        physical_lines=physical_lines,
        is_text=is_text,
        is_binary=not is_text,
        is_generated=artifact_class == "generated_store",
        is_fixture=artifact_class == "fixture",
        is_documentation=artifact_class in {
            "agentic_process_doc",
            "architecture_doc",
            "completed_task_archive",
            "project_report",
            "research_doc",
        },
        language_hint=language_hint_for(normalized),
    )


def metric_for_path(repo_root: Path, path: str, inventory: dict, contract: CountingContract) -> FileMetric:
    normalized = normalize_path(path)
    full_path = repo_root / Path(*normalized.split("/"))
    data = b""
    if full_path.exists() and full_path.is_file():
        data = full_path.read_bytes()
    return metric_for_data(normalized, data, inventory, contract)


def metric_for_revision_path(
    repo_root: Path,
    revision: str,
    path: str,
    inventory: dict,
    contract: CountingContract,
) -> FileMetric:
    normalized = normalize_path(path)
    data = git_output(repo_root, ["show", f"{revision}:{normalized}"])
    return metric_for_data(normalized, data, inventory, contract)


def group_metrics(files: Iterable[FileMetric], key_fn) -> list[GroupMetric]:
    groups: dict[str, GroupMetric] = {}
    accum: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for metric in files:
        key = key_fn(metric) or "<none>"
        accum[key]["files"] += 1
        accum[key]["bytes"] += metric.bytes
        accum[key]["text_files"] += 1 if metric.is_text else 0
        accum[key]["binary_files"] += 1 if metric.is_binary else 0
        accum[key]["physical_lines"] += metric.physical_lines

    for key, values in accum.items():
        groups[key] = GroupMetric(
            key=key,
            files=values["files"],
            bytes=values["bytes"],
            text_files=values["text_files"],
            binary_files=values["binary_files"],
            physical_lines=values["physical_lines"],
        )
    return [groups[key] for key in sorted(groups)]


def module_metrics(files: list[FileMetric], inventory: dict) -> list[ModuleMetric]:
    by_path = {metric.path: metric for metric in files}
    metrics: list[ModuleMetric] = []
    for module in sorted(inventory.get("modules", []), key=lambda item: str(item.get("id", ""))):
        module_id = str(module.get("id", ""))
        source_dir = normalize_path(str(module.get("source_dir", ""))).rstrip("/")
        contract_test = normalize_path(str(module.get("contract_test", "")))
        skill = normalize_path(str(module.get("skill", ""))).rstrip("/")

        source_files = [
            metric
            for metric in files
            if source_dir and metric.path.startswith(source_dir + "/")
        ]
        contract_files = [
            metric
            for metric in files
            if contract_test and metric.path == contract_test
        ]
        skill_files = [
            metric
            for metric in files
            if skill and metric.path.startswith(skill + "/")
        ]

        # Include direct contract file lookup so missing files stay deterministic.
        if contract_test and contract_test in by_path and by_path[contract_test] not in contract_files:
            contract_files.append(by_path[contract_test])

        metrics.append(
            ModuleMetric(
                module_id=module_id,
                source_dir=source_dir,
                contract_test=contract_test,
                skill=skill,
                source_files=len(source_files),
                interface_files=sum(1 for metric in source_files if metric.extension == ".cppm"),
                implementation_files=sum(1 for metric in source_files if metric.extension == ".cpp"),
                source_lines=sum(metric.physical_lines for metric in source_files),
                contract_test_files=len(contract_files),
                contract_test_lines=sum(metric.physical_lines for metric in contract_files),
                skill_files=len(skill_files),
                skill_lines=sum(metric.physical_lines for metric in skill_files),
            )
        )
    return metrics


def snapshot_groups(files: list[FileMetric]) -> dict[str, list[GroupMetric]]:
    return {
        "by_artifact_class": group_metrics(files, lambda metric: metric.artifact_class),
        "by_extension": group_metrics(files, lambda metric: metric.extension),
        "by_gcs_module": group_metrics(files, lambda metric: metric.gcs_module or "<none>"),
        "by_lifecycle_layer": group_metrics(files, lambda metric: metric.lifecycle_layer),
        "by_top_level": group_metrics(files, lambda metric: top_level_for(metric.path)),
    }


def collect_snapshot(
    repo_root: Path,
    *,
    tracked_paths: list[str] | None = None,
    generated_at: str | None = None,
    git_info: GitInfo | None = None,
    base: str | None = None,
    contract: CountingContract | None = None,
) -> RepositoryAuditSnapshot:
    repo_root = repo_root.resolve()
    contract = contract or CountingContract()
    paths = tracked_paths if tracked_paths is not None else collect_tracked_paths(repo_root)
    paths = sorted(normalize_path(path) for path in paths)
    inventory = load_inventory(repo_root)
    files = [metric_for_path(repo_root, path, inventory, contract) for path in paths]
    totals = {
        "files": len(files),
        "bytes": sum(metric.bytes for metric in files),
        "text_files": sum(1 for metric in files if metric.is_text),
        "binary_files": sum(1 for metric in files if metric.is_binary),
        "physical_lines": sum(metric.physical_lines for metric in files),
    }
    snapshot = RepositoryAuditSnapshot(
        schema_version=SCHEMA_VERSION,
        tool_version=TOOL_VERSION,
        generated_at=generated_at or _datetime.datetime.now(_datetime.UTC).isoformat(),
        repo_root=str(repo_root).replace("\\", "/"),
        git=git_info or collect_git_info(repo_root, base=base),
        counting_contract=contract,
        totals=totals,
        groups=snapshot_groups(files),
        files=files,
        modules=module_metrics(files, inventory),
        findings=[],
    )
    return replace(snapshot, findings=check_snapshot(snapshot))


def collect_revision_snapshot(
    repo_root: Path,
    revision: str,
    *,
    generated_at: str | None = None,
    base: str | None = None,
    contract: CountingContract | None = None,
) -> RepositoryAuditSnapshot:
    repo_root = repo_root.resolve()
    contract = contract or CountingContract()
    paths = collect_revision_paths(repo_root, revision)
    inventory = load_inventory(repo_root)
    files = [metric_for_revision_path(repo_root, revision, path, inventory, contract) for path in paths]
    totals = {
        "files": len(files),
        "bytes": sum(metric.bytes for metric in files),
        "text_files": sum(1 for metric in files if metric.is_text),
        "binary_files": sum(1 for metric in files if metric.is_binary),
        "physical_lines": sum(metric.physical_lines for metric in files),
    }
    snapshot = RepositoryAuditSnapshot(
        schema_version=SCHEMA_VERSION,
        tool_version=TOOL_VERSION,
        generated_at=generated_at or _datetime.datetime.now(_datetime.UTC).isoformat(),
        repo_root=str(repo_root).replace("\\", "/"),
        git=collect_revision_git_info(repo_root, revision, base=base),
        counting_contract=contract,
        totals=totals,
        groups=snapshot_groups(files),
        files=files,
        modules=module_metrics(files, inventory),
        findings=[],
    )
    return replace(snapshot, findings=check_snapshot(snapshot))


def collect_index_snapshot(
    repo_root: Path,
    *,
    generated_at: str | None = None,
    base: str | None = None,
    contract: CountingContract | None = None,
) -> RepositoryAuditSnapshot:
    tree = git_output(repo_root.resolve(), ["write-tree"]).decode("utf-8", errors="replace").strip()
    return collect_revision_snapshot(
        repo_root,
        tree,
        generated_at=generated_at,
        base=base,
        contract=contract,
    )


def write_snapshot(snapshot: RepositoryAuditSnapshot, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(snapshot.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def read_snapshot(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
