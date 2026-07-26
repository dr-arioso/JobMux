"""Consistency checking — decisions/0005 action item 5.

ADR-0005 decided that a validity/consistency check's *trigger* should be
mechanical, not a model-judged frequency decision (unbounded, no natural
stopping rule — the same shape as the tournament's own not-yet-fixed
stopping threshold, elicitation.md §7). The check fires only on a
detectable mismatch between two independently-obtained signals about the
same underlying preference: a stated/survey-implied importance level for
a priority, versus that priority's tournament-derived rank once the
tournament actually runs.

Deliberately shaped like `verification.py`'s `diff_ledger_value` — a cheap,
mechanical comparison, not a judgment call. Whatever the model does *with*
a detected mismatch (surface it to the candidate, per elicitation.md
§1.3's "state the candidate's own fork back as a hypothesis" pattern) is
frontier-tier work and out of scope for this module, the same way
`verification.py` computes a diff or a purge list and leaves interpreting
or acting on it to the caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StatedImportance(Enum):
    """A coarse, three-value read on how a candidate described a
    priority's importance before the tournament ran — either in the live
    interview or from a pre-completed survey (decisions/0005: "survey
    strengthens the hypothesis, live process still proves it"). Kept
    coarse rather than numeric on purpose: the interview never asks for a
    numeric weight directly (architecture.md §1.1), so there is no finer-
    grained stated value to compare against in the first place."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ImportanceMismatch:
    """A detected disagreement between a priority's stated importance and
    its tournament-derived rank. `rank` is 1-indexed position within its
    dimension's derived ordering (1 = highest weight) — the caller is
    expected to have already produced this from `jobmux/tournament.py`'s
    `bradley_terry_scores`, not something this module computes itself."""

    priority_name: str
    stated_importance: StatedImportance
    tournament_rank: int
    dimension_size: int


#: A HIGH-stated priority landing outside the top-`_HIGH_RANK_CEILING`
#: positions (regardless of dimension size) counts as a mismatch. A
#: first-instantiation constant, the same spirit as this codebase's other
#: exposed-not-hardcoded thresholds (scoring.py's `top_k`/`lambda_`,
#: signal_fusion.py's `conflict_threshold`) -- not a settled decision.
_HIGH_RANK_CEILING = 2

#: A LOW-stated priority landing inside the top-`_LOW_RANK_FLOOR`
#: positions counts as a mismatch in the other direction -- a candidate
#: who described something as barely mattering, but whose tournament
#: choices consistently favored it, is just as real a disagreement as the
#: reverse case.
_LOW_RANK_FLOOR = 2


def detect_importance_mismatch(
    priority_name: str,
    stated_importance: StatedImportance,
    tournament_rank: int,
    dimension_size: int,
) -> ImportanceMismatch | None:
    """Cheap, mechanical comparison -- not a judgment call. Returns an
    `ImportanceMismatch` only when the two signals actually disagree by
    this module's fixed (if first-instantiation) definition of
    disagreement; returns `None` in the common, consistent case, so a
    caller running this after every tournament pays no cost at all unless
    there is actually something to surface.

    MEDIUM-stated priorities never produce a mismatch here -- "medium" is
    deliberately the non-committal middle value or a genuine cold start
    (elicitation.md §1.2's "I don't have anything to go on yet"), and
    treating an unremarkable rank as a contradiction of a non-claim would
    manufacture disagreements that were never actually stated.
    """
    if tournament_rank < 1 or tournament_rank > dimension_size:
        raise ValueError(
            f"tournament_rank ({tournament_rank}) must be within "
            f"1..dimension_size ({dimension_size})"
        )

    if stated_importance is StatedImportance.HIGH and tournament_rank > _HIGH_RANK_CEILING:
        return ImportanceMismatch(
            priority_name=priority_name,
            stated_importance=stated_importance,
            tournament_rank=tournament_rank,
            dimension_size=dimension_size,
        )
    # A LOW-stated item landing "near the top" is only a meaningful signal
    # if the dimension is big enough for the floor position to actually
    # mean something -- in a dimension no bigger than the floor itself,
    # every rank is trivially within it (e.g. rank 2 of 2 is just last
    # place, not a suspiciously strong showing), so no mismatch is raised.
    if (
        stated_importance is StatedImportance.LOW
        and dimension_size > _LOW_RANK_FLOOR
        and tournament_rank <= _LOW_RANK_FLOOR
    ):
        return ImportanceMismatch(
            priority_name=priority_name,
            stated_importance=stated_importance,
            tournament_rank=tournament_rank,
            dimension_size=dimension_size,
        )
    return None


def detect_importance_mismatches(
    stated_importances: dict[str, StatedImportance],
    tournament_ranks: dict[str, int],
) -> list[ImportanceMismatch]:
    """Batch form over a whole dimension's worth of priorities at once --
    `stated_importances` and `tournament_ranks` are both keyed by priority
    name. A priority present in `tournament_ranks` but absent from
    `stated_importances` is skipped, not an error: `design/architecture.md`
    §1.1's "let the candidate add" means a priority can enter the values
    pass with no prior stated-importance signal at all (nothing to
    mismatch against, per elicitation.md §1.2's cold-start case)."""
    dimension_size = len(tournament_ranks)
    mismatches = []
    for name, stated in stated_importances.items():
        if name not in tournament_ranks:
            continue
        mismatch = detect_importance_mismatch(name, stated, tournament_ranks[name], dimension_size)
        if mismatch is not None:
            mismatches.append(mismatch)
    return mismatches
