from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SCHEMA_VERSION = "gcs-repository-audit-0.1"
TOOL_VERSION = "0.1"


@dataclass(frozen=True)
class CountingContract:
    tracked_files_only: bool = True
    include_untracked: bool = False
    include_build_output: bool = False
    excluded_roots: tuple[str, ...] = ("out", "outputs", "var", ".git")
    text_extensions: tuple[str, ...] = (
        ".cmd",
        ".cmake",
        ".cpp",
        ".cppm",
        ".gitignore",
        ".json",
        ".jsonl",
        ".md",
        ".ps1",
        ".py",
        ".txt",
        ".yaml",
        ".yml",
    )


@dataclass(frozen=True)
class FileMetric:
    path: str
    artifact_class: str
    lifecycle_layer: str
    gcs_module: str | None
    extension: str
    bytes: int
    physical_lines: int
    is_text: bool
    is_binary: bool
    is_generated: bool
    is_fixture: bool
    is_documentation: bool
    language_hint: str


@dataclass(frozen=True)
class GroupMetric:
    key: str
    files: int = 0
    bytes: int = 0
    text_files: int = 0
    binary_files: int = 0
    physical_lines: int = 0


@dataclass(frozen=True)
class ModuleMetric:
    module_id: str
    source_dir: str
    contract_test: str
    skill: str
    source_files: int = 0
    interface_files: int = 0
    implementation_files: int = 0
    source_lines: int = 0
    contract_test_files: int = 0
    contract_test_lines: int = 0
    skill_files: int = 0
    skill_lines: int = 0


@dataclass(frozen=True)
class AuditFinding:
    id: str
    severity: str
    confidence: str
    path: str | None
    message: str
    recommendation: str


@dataclass(frozen=True)
class GitInfo:
    head: str | None
    branch: str | None
    dirty: bool
    base: str | None = None


@dataclass(frozen=True)
class RepositoryAuditSnapshot:
    schema_version: str
    tool_version: str
    generated_at: str
    repo_root: str
    git: GitInfo
    counting_contract: CountingContract
    totals: dict[str, int]
    groups: dict[str, list[GroupMetric]]
    files: list[FileMetric]
    modules: list[ModuleMetric] = field(default_factory=list)
    findings: list[AuditFinding] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
