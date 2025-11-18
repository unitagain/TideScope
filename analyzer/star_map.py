"""Build the Project Task StarMap from DebtItems."""

from __future__ import annotations

from math import tau
from typing import Iterable, List

from .models import DebtItem, StarMapData, StarMapNode


def _normalize(values: Iterable[float]) -> List[float]:
    items = list(values)
    if not items:
        return []
    minimum = min(items)
    maximum = max(items)
    if maximum - minimum == 0:
        return [0.5 for _ in items]
    return [(value - minimum) / (maximum - minimum) for value in items]


def build_star_map(debts: List[DebtItem]) -> StarMapData:
    if not debts:
        return StarMapData(nodes=[], metadata={"note": "No debts available"})

    sorted_debts = sorted(debts, key=lambda debt: debt.priority.total, reverse=True)
    normalized_priority = _normalize([debt.priority.total for debt in sorted_debts])

    nodes: List[StarMapNode] = []
    total = len(sorted_debts)
    for index, debt in enumerate(sorted_debts):
        priority_factor = normalized_priority[index] if normalized_priority else 0.5
        radius = max(0.8, 4.5 - priority_factor * 3.5)
        angle = (index / total) * tau
        size = 10 + priority_factor * 12

        nodes.append(
            StarMapNode(
                id=debt.id,
                label=debt.title,
                module=debt.module,
                category=debt.category,
                source_type=debt.source_type,
                reference_id=debt.reference_id,
                priority=debt.priority.total,
                radius=round(radius, 3),
                angle=round(angle, 3),
                size=round(size, 3),
                status=debt.status,
                assignees=debt.assignees,
                skills=debt.skills,
                difficulty=debt.difficulty,
                html_url=debt.html_url,
                recommendation=debt.recommendation,
            )
        )

    metadata = {
        "node_count": str(total),
        "description": "Higher-priority tasks sit closer to the center.",
    }

    return StarMapData(nodes=nodes, metadata=metadata)

