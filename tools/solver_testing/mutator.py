"""Constraint value mutation strategies for solver defect discovery.

Each strategy takes a constraint dict and returns a list of mutated
constraint dicts, each annotated with the mutation metadata.
"""

from __future__ import annotations

import copy
import math
import random
from dataclasses import dataclass
from typing import Callable

from tools.scene_generation.gcs_scene_generation.contracts import (
    CONSTRAINT_TYPES,
    GEOMETRY_TYPE_MAP,
)


@dataclass(frozen=True)
class Mutation:
    strategy: str
    constraint_id: int
    original_value: float
    mutated_value: float
    constraint_type: str


def _safe_float(value) -> float:
    return float(value)


# ---------------------------------------------------------------------------
# Per-strategy mutation functions
# ---------------------------------------------------------------------------


def _zero_to_nonzero(constraint: dict, rng: random.Random) -> list[dict]:
    value = _safe_float(constraint.get("value", 0.0))
    if abs(value) > 1e-12:
        return []
    mutated = copy.deepcopy(constraint)
    mutated["value"] = round(rng.uniform(0.1, 10.0), 6)
    mutated["_mutation"] = {
        "strategy": "zero_to_nonzero",
        "original_value": value,
    }
    return [mutated]


def _positive_to_negative(constraint: dict, rng: random.Random) -> list[dict]:
    """Only meaningful for Distance constraints (distance must be >= 0)."""
    if constraint.get("type") != "Distance":
        return []
    value = _safe_float(constraint.get("value", 0.0))
    if value <= 0:
        return []
    mutated = copy.deepcopy(constraint)
    mutated["value"] = -value
    mutated["_mutation"] = {
        "strategy": "positive_to_negative",
        "original_value": value,
    }
    return [mutated]


def _small_to_large(constraint: dict, rng: random.Random) -> list[dict]:
    value = _safe_float(constraint.get("value", 0.0))
    if abs(value) < 1e-12:
        return []
    mutated = copy.deepcopy(constraint)
    mutated["value"] = round(value * 100.0, 6)
    mutated["_mutation"] = {
        "strategy": "small_to_large",
        "original_value": value,
    }
    return [mutated]


def _large_to_small(constraint: dict, rng: random.Random) -> list[dict]:
    value = _safe_float(constraint.get("value", 0.0))
    if abs(value) < 1e-12:
        return []
    mutated = copy.deepcopy(constraint)
    mutated["value"] = round(value / 100.0, 6)
    mutated["_mutation"] = {
        "strategy": "large_to_small",
        "original_value": value,
    }
    return [mutated]


def _angle_out_of_range(constraint: dict, rng: random.Random) -> list[dict]:
    """Angle constraints should be in [0, pi]. Push outside that range."""
    if constraint.get("type") != "Angle":
        return []
    value = _safe_float(constraint.get("value", 0.0))
    results = []
    for offset in [math.pi, -math.pi]:
        mutated = copy.deepcopy(constraint)
        mutated["value"] = round(value + offset, 6)
        mutated["_mutation"] = {
            "strategy": "angle_out_of_range",
            "original_value": value,
            "offset": offset,
        }
        results.append(mutated)
    return results


def _epsilon_perturb(constraint: dict, rng: random.Random) -> list[dict]:
    value = _safe_float(constraint.get("value", 0.0))
    eps = 1e-6 if abs(value) < 1e-12 else abs(value) * 1e-3
    mutated = copy.deepcopy(constraint)
    mutated["value"] = round(value + eps * rng.choice([-1, 1]), 12)
    mutated["_mutation"] = {
        "strategy": "epsilon_perturb",
        "original_value": value,
        "epsilon": eps,
    }
    return [mutated]


def _extreme_value(constraint: dict, rng: random.Random) -> list[dict]:
    results = []
    for extreme in [1e6, -1e6]:
        mutated = copy.deepcopy(constraint)
        mutated["value"] = float(extreme)
        mutated["_mutation"] = {
            "strategy": "extreme_value",
            "original_value": _safe_float(constraint.get("value", 0.0)),
            "extreme": extreme,
        }
        results.append(mutated)
    return results


def _zero_value(constraint: dict, rng: random.Random) -> list[dict]:
    """Set constraint value to exactly zero."""
    value = _safe_float(constraint.get("value", 0.0))
    if abs(value) < 1e-12:
        return []
    mutated = copy.deepcopy(constraint)
    mutated["value"] = 0.0
    mutated["_mutation"] = {
        "strategy": "zero_value",
        "original_value": value,
    }
    return [mutated]


# ---------------------------------------------------------------------------
# Strategy registry
# ---------------------------------------------------------------------------

MUTATION_STRATEGIES: dict[str, Callable] = {
    "zero_to_nonzero": _zero_to_nonzero,
    "positive_to_negative": _positive_to_negative,
    "small_to_large": _small_to_large,
    "large_to_small": _large_to_small,
    "angle_out_of_range": _angle_out_of_range,
    "epsilon_perturb": _epsilon_perturb,
    "extreme_value": _extreme_value,
    "zero_value": _zero_value,
}


def mutate_constraint_values(
    gcs_graph: dict,
    strategies: list[str] | None = None,
    seed: int = 0,
) -> list[tuple[dict, list[Mutation]]]:
    """Apply mutation strategies to each constraint independently.

    Returns a list of (mutated_gcs_graph, mutations_applied) tuples.
    Each tuple represents one mutated copy of the input graph with one
    constraint's value changed.
    """
    if strategies is None:
        strategies = list(MUTATION_STRATEGIES)

    unknown = [s for s in strategies if s not in MUTATION_STRATEGIES]
    if unknown:
        raise ValueError(f"Unknown mutation strategies: {unknown}")

    rng = random.Random(seed)
    constraints = gcs_graph.get("constraints", [])
    results = []

    for constraint in constraints:
        for strategy_name in strategies:
            strategy_fn = MUTATION_STRATEGIES[strategy_name]
            mutated_constraints = strategy_fn(constraint, rng)
            for mut_c in mutated_constraints:
                mutation_meta = Mutation(
                    strategy=mut_c["_mutation"]["strategy"],
                    constraint_id=constraint["id"],
                    original_value=mut_c["_mutation"]["original_value"],
                    mutated_value=mut_c["value"],
                    constraint_type=constraint.get("type", "?"),
                )
                del mut_c["_mutation"]
                new_gcs = copy.deepcopy(gcs_graph)
                for i, c in enumerate(new_gcs.get("constraints", [])):
                    if c["id"] == mut_c["id"]:
                        new_gcs["constraints"][i] = mut_c
                        break
                results.append((new_gcs, [mutation_meta]))

    return results
