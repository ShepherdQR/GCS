"""GCS graph model helpers used by the scene-generation facade."""

from __future__ import annotations

import random
from collections import Counter, defaultdict

from .topology import build_adjacency, sort_key, unique_edges


def geometry_primal_edges(gcs: dict) -> list[list[int]]:
    edges = []
    for constraint in gcs.get("constraints", []):
        gids = constraint.get("geometry_ids", [])
        for i in range(len(gids)):
            for j in range(i + 1, len(gids)):
                edges.append([gids[i], gids[j]])
    return unique_edges(edges)


def rebuild_rigid_sets(gcs: dict, num_rigid_sets: int | None = None) -> None:
    if num_rigid_sets is None:
        existing = [rs.get("id") for rs in gcs.get("rigid_sets", []) if "id" in rs]
        geom_rs = [g.get("rigid_set_id") for g in gcs.get("geometries", []) if "rigid_set_id" in g]
        ids = sorted(set(existing + geom_rs))
    else:
        ids = list(range(num_rigid_sets))

    rigid_sets = [{"id": rs_id, "geometry_ids": []} for rs_id in ids]
    rs_by_id = {rs["id"]: rs for rs in rigid_sets}
    for geometry in sorted(gcs.get("geometries", []), key=lambda g: g["id"]):
        rs_id = geometry["rigid_set_id"]
        if rs_id not in rs_by_id:
            rs_by_id[rs_id] = {"id": rs_id, "geometry_ids": []}
            rigid_sets.append(rs_by_id[rs_id])
        rs_by_id[rs_id]["geometry_ids"].append(geometry["id"])
    gcs["rigid_sets"] = sorted(rigid_sets, key=lambda rs: rs["id"])
    gcs["num_rigid_sets"] = len(gcs["rigid_sets"])


def geometry_map(gcs: dict) -> dict:
    return {g["id"]: g for g in gcs.get("geometries", [])}


def constraint_has_distinct_rigid_sets(constraint: dict, geom_by_id: dict) -> bool:
    rigid_set_ids = []
    for gid in constraint.get("geometry_ids", []):
        geometry = geom_by_id.get(gid)
        if geometry is None:
            continue
        rigid_set_ids.append(geometry.get("rigid_set_id"))
    return len(rigid_set_ids) == len(set(rigid_set_ids))


def graph_coloring(vertices, edges, requested_colors: int, rng: random.Random, randomize: bool = False) -> dict | None:
    adj = build_adjacency(vertices, edges)
    color_counts = Counter()
    colors = {}

    def uncolored_order():
        remaining = [v for v in vertices if v not in colors]
        if randomize:
            buckets = defaultdict(list)
            for vertex in remaining:
                saturation = len({colors[n] for n in adj[vertex] if n in colors})
                buckets[(saturation, len(adj[vertex]))].append(vertex)
            best_key = max(buckets)
            bucket = sorted(buckets[best_key], key=sort_key)
            rng.shuffle(bucket)
            return bucket + [v for v in sorted(remaining, key=sort_key) if v not in bucket]
        return sorted(
            remaining,
            key=lambda v: (-len({colors[n] for n in adj[v] if n in colors}), -len(adj[v]), sort_key(v)),
        )

    def search() -> bool:
        if len(colors) == len(vertices):
            return True
        vertex = uncolored_order()[0]
        forbidden = {colors[n] for n in adj[vertex] if n in colors}
        choices = [c for c in range(requested_colors) if c not in forbidden]
        choices.sort(key=lambda c: (color_counts[c], c))
        for color in choices:
            colors[vertex] = color
            color_counts[color] += 1
            if search():
                return True
            color_counts[color] -= 1
            del colors[vertex]
        return False

    if len(vertices) > 32:
        order = sorted(vertices, key=lambda v: (-len(adj[v]), sort_key(v)))
        if randomize:
            rng.shuffle(order)
            order.sort(key=lambda v: -len(adj[v]))
        for vertex in order:
            forbidden = {colors[n] for n in adj[vertex] if n in colors}
            choices = [c for c in range(requested_colors) if c not in forbidden]
            if not choices:
                return None
            choices.sort(key=lambda c: (color_counts[c], c))
            colors[vertex] = choices[0]
            color_counts[choices[0]] += 1
        return colors

    return colors if search() else None


def assign_rigid_sets_for_edges(
    vertices,
    edges,
    requested_count: int,
    rng: random.Random,
    assignment: str,
    allow_new_rigid_sets: bool,
) -> tuple[dict, int, bool]:
    if requested_count < 1:
        raise ValueError("num_rigid_sets must be >= 1")
    if edges and requested_count < 2 and not allow_new_rigid_sets:
        raise ValueError("At least 2 rigid sets are required for constrained graphs")

    start = max(1, requested_count)
    stop = len(vertices) if allow_new_rigid_sets else requested_count
    randomize = assignment == "random_balanced"
    for color_count in range(start, stop + 1):
        colors = graph_coloring(vertices, edges, color_count, rng, randomize=randomize)
        if colors is not None:
            return colors, color_count, color_count != requested_count
    raise ValueError(
        f"Could not assign rigid sets for {len(vertices)} vertices and {len(edges)} edges "
        f"with requested num_rigid_sets={requested_count}"
    )

