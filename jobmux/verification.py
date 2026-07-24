"""Verification — architecture.md §1.3 (staleness dates, ledger diffing)
and §1.2 (near-miss re-filtering).

Every function here is deliberately narrow and mechanical. The actual
judgment calls in verification-escalation-policy.md — which escalation
step to run, whether a signal is trustworthy enough to record, how to
reconcile conflicting signals — stay frontier-tier (architecture.md §2.3)
and out of scope here; this module only implements the parts architecture
doc §2.3 explicitly calls algorithmic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any


def is_listing_stale(closing_date: date, as_of: date) -> bool:
    """architecture.md §1.3: "always read the date field, don't trust that
    a page loading means it's current." Pure comparison — does not fetch
    or render anything; the caller supplies an already-located date field
    from an already-loaded page (verification-escalation-policy.md §1's
    signal/finding discipline applies to obtaining that date, not to this
    function)."""
    return closing_date < as_of


@dataclass(frozen=True)
class LedgerDiff:
    changed: bool
    old_value: Any
    new_value: Any


def diff_ledger_value(old_value: Any, new_value: Any) -> LedgerDiff:
    """architecture.md §1.4: "diffing an old ledger value against a new one
    to decide what gets flagged as changed." This is the mechanical half
    of "status changes are revised in place with visible prior-value
    history, never silently deleted" — recording `old_value` as the
    ledger's `prior_status` field is the caller's job, not this
    function's."""
    return LedgerDiff(changed=old_value != new_value, old_value=old_value, new_value=new_value)


class ConstraintKind(Enum):
    THRESHOLD = "threshold"
    QUALIFICATION = "qualification"
    MANDATORY = "mandatory"


class ThresholdDirection(Enum):
    MINIMUM = "minimum"  # value must be >= required_value to pass (e.g. a salary floor)
    MAXIMUM = "maximum"  # value must be <= required_value to pass (e.g. a commute ceiling)


@dataclass(frozen=True)
class NearMiss:
    """A rejected listing tagged with which constraint it failed and by
    how much (architecture.md §1.2, fragmented-employer-module.md §7)."""
    listing_id: str
    failed_constraint_name: str
    failed_constraint_kind: ConstraintKind
    failed_value: float
    required_value: float
    direction: ThresholdDirection = ThresholdDirection.MINIMUM


def refilter_near_misses(
    near_misses: list[NearMiss],
    changed_constraint_name: str,
    new_required_value: float,
) -> list[str]:
    """Given a changed threshold or qualification requirement, return the
    listing_ids of near-misses that would now pass — cheaply resurrecting
    them from cache rather than forcing a full re-search (architecture.md
    §1.2).

    Only THRESHOLD- and QUALIFICATION-kind near-misses are re-checkable
    this way, where "passing" is well-defined as `failed_value` clearing
    `new_required_value`. A MANDATORY (target-match) near-miss has no
    partial-credit continuum to re-check against a numeric value — it
    either stays rejected, or the mandatory flag itself was removed
    entirely, which is a different, larger operation than a numeric
    threshold change and out of scope for this function.
    """
    resurrected = []
    for nm in near_misses:
        if nm.failed_constraint_name != changed_constraint_name:
            continue
        if nm.failed_constraint_kind is ConstraintKind.MANDATORY:
            continue
        if nm.direction is ThresholdDirection.MINIMUM:
            passes = nm.failed_value >= new_required_value
        else:
            passes = nm.failed_value <= new_required_value
        if passes:
            resurrected.append(nm.listing_id)
    return resurrected
