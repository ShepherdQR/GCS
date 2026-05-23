"""Geometry parameter assignment for generated GCS graphs."""

from __future__ import annotations

import copy
import math
import random

from .gcs_model import geometry_map


def vec_sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def vec_add(a, b):
    return [a[i] + b[i] for i in range(3)]


def vec_scale(a, scale):
    return [a[i] * scale for i in range(3)]


def vec_len(a):
    return math.sqrt(sum(a[i] * a[i] for i in range(3)))


def vec_normalize(a):
    length = vec_len(a)
    if length < 1e-12:
        return [0.0, 0.0, 1.0]
    return [a[i] / length for i in range(3)]


def vec_dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def angle_between_vectors(a, b):
    na = vec_normalize(a)
    nb = vec_normalize(b)
    cos_value = max(-1.0, min(1.0, vec_dot(na, nb)))
    return math.degrees(math.acos(cos_value))


def line_direction(line_v):
    return vec_sub(line_v[3:6], line_v[:3])


def plane_normal(plane_v):
    return plane_v[3:6]


def layout_positions(geometries, layout: str, layout_params: dict, rng: random.Random) -> dict:
    center = layout_params.get("center", [0.0, 0.0, 0.0])
    positions = {}
    if layout == "circular":
        radius = float(layout_params.get("radius", 2.0))
        plane = layout_params.get("plane", "xy")
        n = max(1, len(geometries))
        for index, geometry in enumerate(sorted(geometries, key=lambda g: g["id"])):
            angle = 2.0 * math.pi * index / n
            if plane == "xz":
                pos = [center[0] + radius * math.cos(angle), center[1], center[2] + radius * math.sin(angle)]
            elif plane == "yz":
                pos = [center[0], center[1] + radius * math.cos(angle), center[2] + radius * math.sin(angle)]
            else:
                pos = [center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle), center[2]]
            positions[geometry["id"]] = pos
    elif layout == "random":
        radius = float(layout_params.get("radius", 3.0))
        for geometry in sorted(geometries, key=lambda g: g["id"]):
            positions[geometry["id"]] = [
                center[0] + rng.uniform(-radius, radius),
                center[1] + rng.uniform(-radius, radius),
                center[2] + rng.uniform(-radius, radius),
            ]
    elif layout == "grid":
        spacing = float(layout_params.get("spacing", 2.0))
        cols = max(1, int(math.ceil(math.sqrt(len(geometries)))))
        for index, geometry in enumerate(sorted(geometries, key=lambda g: g["id"])):
            row = index // cols
            col = index % cols
            positions[geometry["id"]] = [center[0] + col * spacing, center[1] - row * spacing, center[2]]
    else:
        raise ValueError(f"Unknown layout: {layout}")
    return positions


def assign_geometry_parameters(gcs: dict, layout: str, layout_params: dict, rng: random.Random) -> dict:
    gcs = copy.deepcopy(gcs)
    positions = layout_positions(gcs.get("geometries", []), layout, layout_params, rng)

    for geometry in sorted(gcs.get("geometries", []), key=lambda g: g["id"]):
        pos = positions[geometry["id"]]
        if geometry["type"] == "Point":
            geometry["v"] = [pos[0], pos[1], pos[2], 0.0, 0.0, 0.0]
        elif geometry["type"] == "Line":
            direction = vec_normalize([rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0)])
            half_len = rng.uniform(0.5, 1.5)
            start = vec_sub(pos, vec_scale(direction, half_len))
            end = vec_add(pos, vec_scale(direction, half_len))
            geometry["v"] = [*start, *end]
        elif geometry["type"] == "Plane":
            normal = vec_normalize([rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0), rng.uniform(0.3, 1.0)])
            geometry["v"] = [pos[0], pos[1], pos[2], *normal]

    geom_by_id = geometry_map(gcs)
    for constraint in sorted(gcs.get("constraints", []), key=lambda c: c["id"]):
        gids = constraint.get("geometry_ids", [])
        if len(gids) < 2 or gids[0] not in geom_by_id or gids[1] not in geom_by_id:
            continue
        g1 = geom_by_id[gids[0]]
        g2 = geom_by_id[gids[1]]
        if constraint["type"] == "Distance":
            constraint["value"] = round(vec_len(vec_sub(g1["v"][:3], g2["v"][:3])), 6)
        elif constraint["type"] == "Angle":
            if g1["type"] == "Line" and g2["type"] == "Line":
                value = angle_between_vectors(line_direction(g1["v"]), line_direction(g2["v"]))
            elif g1["type"] == "Line" and g2["type"] == "Plane":
                value = abs(90.0 - angle_between_vectors(line_direction(g1["v"]), plane_normal(g2["v"])))
            elif g1["type"] == "Plane" and g2["type"] == "Line":
                value = abs(90.0 - angle_between_vectors(plane_normal(g1["v"]), line_direction(g2["v"])))
            elif g1["type"] == "Plane" and g2["type"] == "Plane":
                value = angle_between_vectors(plane_normal(g1["v"]), plane_normal(g2["v"]))
            else:
                value = rng.uniform(15.0, 75.0)
            constraint["value"] = round(max(0.0, min(180.0, value)), 6)
        else:
            constraint["value"] = 0.0

    gcs["status"] = "parameters_assigned"
    return gcs

