"""Deterministic store, path, and digest helpers for scene generation."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SceneGenerationStore:
    """Store adapter carrying deterministic path, IO, trace, and digest policy."""

    store_dir: str

    def store_path(self, graph_id: str) -> str:
        return store_path(self.store_dir, graph_id)

    def save_graph(self, graph_id: str, data: dict) -> None:
        save_graph(self.store_dir, graph_id, data)

    def load_graph(self, graph_id: str) -> dict:
        return load_graph(self.store_dir, graph_id)

    def list_graphs(self) -> list[dict]:
        return list_graphs(self.store_dir)

    def delete_graph(self, graph_id: str) -> dict:
        return delete_graph(self.store_dir, graph_id)

    def safe_store_id(self, value: str, field_name: str = "id") -> str:
        return safe_store_id(value, field_name)

    def write_json_file(self, path: str, data: dict | list) -> None:
        write_json_file(path, data)

    def read_json_file(self, path: str) -> dict:
        return read_json_file(path)

    def exploration_root(self, exploration_id: str) -> str:
        return exploration_root(self.store_dir, exploration_id)

    def promotion_root(self, promotion_id: str) -> str:
        return promotion_root(self.store_dir, promotion_id)

    def candidate_slot(self, candidate_id: str) -> str:
        return candidate_slot(candidate_id)

    def candidate_root(self, exploration_id: str, candidate_id: str) -> str:
        return candidate_root(self.store_dir, exploration_id, candidate_id)

    def append_trace(self, trace_path: str, event: dict) -> None:
        append_trace(trace_path, event)

    def sha256_text(self, text: str) -> str:
        return sha256_text(text)


def safe_store_id(value: str, field_name: str = "id") -> str:
    text = str(value)
    if not text:
        raise ValueError(f"{field_name} must not be empty")
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    if any(ch not in allowed for ch in text):
        raise ValueError(f"{field_name} may only contain letters, digits, '.', '_' and '-'")
    if text in {".", ".."} or text.startswith(".") or ".." in text:
        raise ValueError(f"{field_name} must not be a hidden or relative path segment")
    return text


def store_path(store_dir: str, graph_id: str) -> str:
    os.makedirs(store_dir, exist_ok=True)
    return os.path.join(store_dir, f"{graph_id}.json")


def write_json_file(path: str, data: dict | list) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def read_json_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_graph(store_dir: str, graph_id: str, data: dict) -> None:
    write_json_file(store_path(store_dir, graph_id), data)


def load_graph(store_dir: str, graph_id: str) -> dict:
    path = store_path(store_dir, graph_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Graph '{graph_id}' not found in store")
    return read_json_file(path)


def list_graphs(store_dir: str) -> list[dict]:
    os.makedirs(store_dir, exist_ok=True)
    result = []
    for fname in sorted(os.listdir(store_dir)):
        if not fname.endswith(".json"):
            continue
        graph_id = fname[:-5]
        path = os.path.join(store_dir, fname)
        try:
            data = read_json_file(path)
            if "gcs_graph_id" in data:
                graph_type = "gcs"
            elif "projected_graph_id" in data:
                graph_type = "projected"
            elif "graph_id" in data:
                graph_type = "skeleton"
            else:
                graph_type = "unknown"
            result.append({"id": graph_id, "type": graph_type})
        except Exception as exc:
            result.append({"id": graph_id, "type": "error", "error": str(exc)})
    return result


def delete_graph(store_dir: str, graph_id: str) -> dict:
    path = store_path(store_dir, graph_id)
    if not os.path.exists(path):
        return {"error": f"Graph '{graph_id}' not found"}
    os.remove(path)
    return {"deleted": graph_id}


def exploration_root(store_dir: str, exploration_id: str) -> str:
    return os.path.join(store_dir, "explorations", safe_store_id(exploration_id, "exploration_id"))


def promotion_root(store_dir: str, promotion_id: str) -> str:
    return os.path.join(store_dir, "promotions", safe_store_id(promotion_id, "promotion_id"))


def candidate_slot(candidate_id: str) -> str:
    suffix = str(candidate_id).rsplit("_c", 1)[-1]
    if suffix and suffix[0:4].isdigit():
        return f"c{suffix[0:4]}"
    return safe_store_id(candidate_id, "candidate_id")


def candidate_root(store_dir: str, exploration_id: str, candidate_id: str) -> str:
    return os.path.join(exploration_root(store_dir, exploration_id), "candidates", candidate_slot(candidate_id))


def append_trace(trace_path: str, event: dict) -> None:
    os.makedirs(os.path.dirname(trace_path), exist_ok=True)
    with open(trace_path, "a", encoding="utf-8") as f:
        json.dump(event, f, sort_keys=True)
        f.write("\n")


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
