"""Reallocation — architecture.md §1.1.

Redistributes a fixed weight budget across the members of a dimension (or
across dimensions themselves, one level up — "the same mechanism reused at
a coarser grain") whenever one member's weight changes.

Three strategies. Only PROPORTIONAL is ever the silent default —
EQUAL_SPLIT and PROTECT_TOP_K are, per architecture.md §1.1 and
elicitation.md §2.7, "named, confirmed alternatives, never a silent
default swap." Callers must opt into them explicitly.

Marking a priority "not critical" (architecture.md §1.1) reuses this as a
weight-zeroing event — call reallocate() with new_weight=0.0.
"""

from __future__ import annotations

from enum import Enum


class ReallocationStrategy(Enum):
    PROPORTIONAL = "proportional"
    EQUAL_SPLIT = "equal_split"
    PROTECT_TOP_K = "protect_top_k"


def reallocate(
    weights: dict[str, float],
    changed_key: str,
    new_weight: float,
    *,
    strategy: ReallocationStrategy = ReallocationStrategy.PROPORTIONAL,
    protected_keys: frozenset[str] = frozenset(),
) -> dict[str, float]:
    """Redistribute weight budget after one member's weight changes.

    `weights` is the full set of members sharing a fixed budget (a
    dimension's priorities, or the dimensions themselves one level up) —
    the budget is `sum(weights.values())`, preserved across the call.

    PROPORTIONAL (default): the remaining budget after `changed_key` takes
    `new_weight` redistributes across the others in proportion to their
    current relative shares — "new weight = old weight ÷ sum-of-others ×
    remaining budget." Doesn't silently reorder priorities the candidate
    didn't touch.

    EQUAL_SPLIT: the remaining budget splits evenly across the others,
    ignoring their prior relative shares.

    PROTECT_TOP_K: `protected_keys` keep their exact original weights
    unchanged; only the non-protected "absorbers" redistribute the
    remainder proportionally among themselves. Useful when one preference
    is near-non-negotiable without having been marked mandatory or given a
    threshold (elicitation.md §2.7).
    """
    if changed_key not in weights:
        raise KeyError(f"{changed_key!r} is not a member of this weight set")
    if changed_key in protected_keys:
        raise ValueError(
            f"{changed_key!r} cannot be both the changed key and a protected key"
        )

    total_budget = sum(weights.values())
    if not (-1e-9 <= new_weight <= total_budget + 1e-9):
        raise ValueError(
            f"new_weight {new_weight} must be between 0 and the total budget "
            f"{total_budget}"
        )
    new_weight = max(0.0, new_weight)

    others = {k: v for k, v in weights.items() if k != changed_key}
    remaining_budget = total_budget - new_weight

    if not others:
        return {changed_key: new_weight}

    if strategy is ReallocationStrategy.PROPORTIONAL:
        redistributed = _proportional(others, remaining_budget)
    elif strategy is ReallocationStrategy.EQUAL_SPLIT:
        redistributed = _equal_split(others, remaining_budget)
    elif strategy is ReallocationStrategy.PROTECT_TOP_K:
        redistributed = _protect_top_k(others, remaining_budget, protected_keys)
    else:  # pragma: no cover - exhaustive Enum guard
        raise ValueError(f"Unknown strategy: {strategy}")

    redistributed[changed_key] = new_weight
    return redistributed


def _proportional(others: dict[str, float], remaining_budget: float) -> dict[str, float]:
    sum_others = sum(others.values())
    if sum_others <= 0:
        # No relative shares to proportion by (e.g. every remaining member
        # was already at zero) — fall back to equal split rather than
        # dividing by zero.
        return _equal_split(others, remaining_budget)
    return {k: (v / sum_others) * remaining_budget for k, v in others.items()}


def _equal_split(others: dict[str, float], remaining_budget: float) -> dict[str, float]:
    share = remaining_budget / len(others)
    return {k: share for k in others}


def _protect_top_k(
    others: dict[str, float],
    remaining_budget: float,
    protected_keys: frozenset[str],
) -> dict[str, float]:
    if not protected_keys:
        raise ValueError("protect_top_k strategy requires at least one protected key")
    unknown = protected_keys - others.keys()
    if unknown:
        raise KeyError(f"protected_keys not present in weights: {sorted(unknown)}")

    protected_total = sum(others[k] for k in protected_keys)
    absorbers = {k: v for k, v in others.items() if k not in protected_keys}
    absorbers_budget = remaining_budget - protected_total
    if absorbers and absorbers_budget < -1e-9:
        raise ValueError(
            "protected weights alone exceed the remaining budget; cannot "
            "protect them without also changing a protected weight"
        )
    absorbers_budget = max(0.0, absorbers_budget)

    result = {k: others[k] for k in protected_keys}
    if absorbers:
        result.update(_proportional(absorbers, absorbers_budget))
    return result
