"""Scheduling — architecture.md §1.4 (volatility-tier recheck cadence) and
§1.5 (information-gain-per-cost action ordering).

Volatility tier is explicitly a scheduling tool, never a stability claim
(architecture.md §1.4; verification-escalation-policy.md §4) — nothing in
this module ever decides whether a check happens or how rigorously; it
only ever decides how often.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum


class VolatilityTier(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


_DEFAULT_INTERVAL_DAYS = {
    VolatilityTier.HIGH: 7,
    VolatilityTier.MEDIUM: 14,
    VolatilityTier.LOW: 30,
}


def next_recheck_date(
    tier: VolatilityTier,
    last_checked: date,
    *,
    known_cycle_date: date | None = None,
    lead_days_before_cycle: int = 7,
) -> date:
    """adaptive-module.md §8: "where a funding or cycle date is
    discoverable for a given employer or sector..., schedule that
    employer's next check to land shortly before the relevant date, rather
    than defaulting to a generic calendar interval. Where no such date is
    known, the generic volatility tier applies."
    """
    if known_cycle_date is not None and known_cycle_date > last_checked:
        cycle_based = known_cycle_date - timedelta(days=lead_days_before_cycle)
        if cycle_based > last_checked:
            return cycle_based
    return last_checked + timedelta(days=_DEFAULT_INTERVAL_DAYS[tier])


@dataclass(frozen=True)
class CandidateAction:
    name: str
    expected_information_gain: float
    cost: float


def order_by_information_gain_per_cost(
    actions: list[CandidateAction],
) -> list[CandidateAction]:
    """architecture.md §1.5: "order candidate actions... by expected
    information gain divided by cost, and spend the budget on the best
    ratios first." A zero-cost action with positive expected gain sorts
    first (infinite ratio); a zero-cost, zero-gain action sorts last among
    zero-cost actions rather than raising, since it's a legitimate,
    if useless, action."""
    if any(a.cost < 0 or a.expected_information_gain < 0 for a in actions):
        raise ValueError("expected_information_gain and cost must be non-negative")

    def ratio(a: CandidateAction) -> float:
        if a.cost == 0:
            return float("inf") if a.expected_information_gain > 0 else 0.0
        return a.expected_information_gain / a.cost

    return sorted(actions, key=ratio, reverse=True)


def select_within_budget(
    actions: list[CandidateAction], budget: float
) -> list[CandidateAction]:
    """"Cost is not an object" isn't a separate mode — it's the same
    ordering with the budget parameter set arbitrarily high, which
    naturally reduces to running every action with positive expected
    value (architecture.md §1.5). This function is that same ordering;
    passing a very large `budget` is how the "cost is not an object" case
    is expressed, not a separate code path."""
    if budget < 0:
        raise ValueError("budget must be non-negative")
    ordered = order_by_information_gain_per_cost(actions)
    selected: list[CandidateAction] = []
    remaining = budget
    for a in ordered:
        if a.cost <= remaining:
            selected.append(a)
            remaining -= a.cost
    return selected
