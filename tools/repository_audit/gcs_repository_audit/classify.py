from __future__ import annotations

from pathlib import PurePosixPath


ASSET_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".pdf",
    ".png",
    ".pptx",
    ".svg",
    ".webp",
}

LANGUAGE_BY_EXTENSION = {
    ".cmd": "Batch",
    ".cpp": "C++",
    ".cppm": "C++",
    ".gitignore": "Git Ignore",
    ".json": "JSON",
    ".jsonl": "JSON Lines",
    ".md": "Markdown",
    ".ps1": "PowerShell",
    ".py": "Python",
    ".txt": "Text",
    ".yaml": "YAML",
    ".yml": "YAML",
}

ROOT_CONFIG_FILES = {
    ".gitignore",
    "CMakeLists.txt",
    "CMakePresets.json",
    "GCS.code-workspace",
    "README.md",
}

ARTIFACT_LAYERS = {
    "application_shell": "product",
    "agentic_process_doc": "process",
    "architecture_doc": "architecture",
    "codex_skill": "skill",
    "completed_task_archive": "archive",
    "contract_test": "test",
    "fixture": "evidence",
    "generated_store": "generated_evidence",
    "product_doc": "product",
    "project_report": "report",
    "repo_root_config": "configuration",
    "research_doc": "research",
    "solver_source": "product",
    "tool_test": "test",
    "tooling": "support",
    "unknown": "unknown",
    "viewer_python": "product",
    "visual_asset": "asset",
}


def normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def extension_for(path: str) -> str:
    name = PurePosixPath(path).name
    if name.startswith(".") and name.count(".") == 1:
        return name.lower()
    return PurePosixPath(path).suffix.lower()


def top_level_for(path: str) -> str:
    return normalize_path(path).split("/", 1)[0]


def language_hint_for(path: str) -> str:
    name = PurePosixPath(path).name
    if name == "CMakeLists.txt":
        return "CMake"
    return LANGUAGE_BY_EXTENSION.get(extension_for(path), "Unknown")


def classify_path(path: str) -> str:
    path = normalize_path(path)
    ext = extension_for(path)
    name = PurePosixPath(path).name

    if ext in ASSET_EXTENSIONS:
        return "visual_asset"
    if path.startswith(".codex_scene_generation_store/"):
        return "generated_store"
    if path.startswith(".codex/skills/"):
        return "codex_skill"
    if path.startswith("src/gcs/") and ext in {".cpp", ".cppm"}:
        return "solver_source"
    if path.startswith("apps/gcs_cli/"):
        return "application_shell"
    if path.startswith("python/gcs_viz/"):
        return "viewer_python"
    if path.startswith("tests/contracts/"):
        return "contract_test"
    if path.startswith("tests/tools/"):
        return "tool_test"
    if path.startswith("fixtures/"):
        return "fixture"
    if path.startswith("docs/completed-tasks/"):
        return "completed_task_archive"
    if path.startswith("docs/architecture/"):
        return "architecture_doc"
    if path == "docs/current-model.md":
        return "architecture_doc"
    if path.startswith("docs/product/"):
        return "product_doc"
    if path.startswith("docs/reports/"):
        return "project_report"
    if path.startswith("docs/research/"):
        return "research_doc"
    if path.startswith("docs/agentic/"):
        return "agentic_process_doc"
    if path.startswith("tools/") or path.startswith("scripts/"):
        return "tooling"
    if path == "python/requirements.txt":
        return "repo_root_config"
    if "/" not in path and (name in ROOT_CONFIG_FILES or ext in {".json", ".md", ".txt"}):
        return "repo_root_config"
    return "unknown"


def lifecycle_layer_for(artifact_class: str) -> str:
    return ARTIFACT_LAYERS.get(artifact_class, "unknown")
