"""Scoring — architecture.md §1.1.

Two functions: a weighted-sum score augmented with a Chebyshev-style
penalty so a candidate's top-ranked priorities can't be fully compensated
by a strong lower-ranked one, and a qualification dimension's met/unmet
percentage.

Formula choice, flagged: architecture.md §1.1 specifies the *behavior*
this scoring function must have — "penalizing the worst-scoring
highly-ranked priority disproportionately (Chebyshev-style) rather than
pure linear weighting, so a candidate's #1 priority can't be fully
cancelled out by a strong #3" — but not an exact formula. This
implementation uses the augmented weighted Tchebycheff scalarization
(Steuer & Choo, 1983, a standard multi-criteria-decision-analysis
technique for exactly this "avoid full compensability while still
respecting weights" property), restricted to the caller-specified top_k
priorities and blended with a plain weighted sum over the rest. This is a
first concrete instantiation, not a settled architecture.md decision —
open to revision the same way an open question elsewhere in this project
gets flagged rather than silently decided.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class ScoredPriority:
    """A priority's rank-ordered position and how well a listing scored on
    it. `score` is normalized to [0.0, 1.0], where 1.0 is the ideal."""
    name: str
    weight: float
    score: float


def weighted_sum_score(priorities: list[ScoredPriority]) -> float:
    """Plain linear weighted average — "lets a strong score on one
    priority compensate for a terrible score on a highly-ranked one"
    (architecture.md §1.1). Used directly for non-top-ranked priorities,
    and as the linear term inside chebyshev_weighted_score below."""
    total_weight = sum(p.weight for p in priorities)
    if total_weight <= 0:
        return 0.0
    return sum(p.weight * p.score for p in priorities) / total_weight


def chebyshev_weighted_score(
    priorities: list[ScoredPriority],
    *,
    top_k: int,
    lambda_: float = 0.5,
    ideal: float = 1.0,
) -> float:
    """Weighted score with an anti-compensability penalty on the top_k
    highest-ranked priorities.

    `priorities` must already be supplied in rank order (highest-ranked
    first) — this function trusts the caller's ordering (produced by
    tournament.bradley_terry_scores, then sorted) rather than re-deriving
    rank itself.

    `lambda_` (0.0-1.0) controls how much weight the penalty term carries
    relative to the plain linear term; 0.0 reduces to weighted_sum_score,
    1.0 makes the result driven entirely by the single worst-scoring
    top-ranked priority (true minimax / Chebyshev behavior).
    """
    if not priorities:
        return 0.0
    if not (0.0 <= lambda_ <= 1.0):
        raise ValueError("lambda_ must be between 0.0 and 1.0")
    if top_k < 0:
        raise ValueError("top_k must be non-negative")

    linear_term = weighted_sum_score(priorities)

    top = priorities[:top_k]
    if not top:
        return linear_term

    max_weighted_gap = max(p.weight * (ideal - p.score) for p in top)
    return (1 - lambda_) * linear_term - lambda_ * max_weighted_gap


class QualificationKind(Enum):
    MINIMUM = "minimum"  # unmet is controlling — excludes the listing
    DESIRED = "desired"  # unmet is non-controlling — a soft signal only


@dataclass(frozen=True)
class QualificationCheck:
    name: str
    met: bool
    kind: QualificationKind = QualificationKind.MINIMUM


@dataclass(frozen=True)
class QualificationResult:
    met_count: int
    total_count: int
    completion_ratio: float
    all_minimums_met: bool


def qualification_completion(checks: list[QualificationCheck]) -> QualificationResult:
    """architecture.md §1.1: "an unmet minimum qualification is
    controlling... an unmet desired qualification is non-controlling, a
    soft signal." `all_minimums_met` is the controlling signal;
    `completion_ratio` is the softer, informational percentage across
    every qualification checked (minimum and desired alike)."""
    if not checks:
        return QualificationResult(met_count=0, total_count=0, completion_ratio=1.0, all_minimums_met=True)
    met_count = sum(1 for c in checks if c.met)
    total = len(checks)
    minimums = [c for c in checks if c.kind is QualificationKind.MINIMUM]
    all_minimums_met = all(c.met for c in minimums)
    return QualificationResult(
        met_count=met_count,
        total_count=total,
        completion_ratio=met_count / total,
        all_minimums_met=all_minimums_met,
    )
