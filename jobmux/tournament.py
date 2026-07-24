"""Tournament — architecture.md §1.1.

Converts pairwise forced-choice results from a tournament (elicitation.md
§2.6) into cardinal weights via a Bradley-Terry-style model — "this retains
information the tournament already generates; no separate elicitation step
is needed" — rather than just reading off the final win-count order.

Uses the standard iterative MM (minorization-maximization) algorithm for
the Bradley-Terry model (Zermelo 1929; Hunter 2004, "MM algorithms for
generalized Bradley-Terry models"). The tournament itself may stop early
once a stable top two or three holds (elicitation.md §2.6) — this module
doesn't assume every pair was compared, and handles a sparse or
disconnected comparison graph explicitly rather than silently.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class PairwiseResult:
    winner: str
    loser: str


def bradley_terry_scores(
    items: list[str],
    results: list[PairwiseResult],
    *,
    max_iterations: int = 1000,
    tolerance: float = 1e-9,
) -> dict[str, float]:
    """Estimate Bradley-Terry strength scores from pairwise results.

    Scores are normalized to a mean of 1.0 each iteration (Bradley-Terry
    strengths are only defined up to a multiplicative constant, so this
    just keeps the iteration numerically stable — callers who need a
    weight in [0, 1] should normalize the returned scores themselves,
    e.g. by dividing by their sum).

    Items that were never compared to anything (isolated in the comparison
    graph — the tournament stopped before reaching them) cannot be
    estimated by this model. They're returned with a score of 0.0 rather
    than silently omitted from the result, so a caller iterating
    `items` always gets every item back.
    """
    if not items:
        return {}
    if len(set(items)) != len(items):
        raise ValueError("items must not contain duplicates")

    wins: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in results:
        if r.winner not in items or r.loser not in items:
            raise ValueError(f"Result references item not in `items`: {r}")
        if r.winner == r.loser:
            raise ValueError(f"A result cannot have the same winner and loser: {r}")
        wins[r.winner][r.loser] += 1

    win_totals = {i: sum(wins[i].values()) for i in items}
    games: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for i in items:
        for j in items:
            if i == j:
                continue
            games[i][j] = wins[i][j] + wins[j][i]

    compared = {i for i in items if any(games[i][j] for j in items if j != i)}
    uncompared = set(items) - compared

    if not compared:
        return {i: 0.0 for i in items}

    strengths = {i: 1.0 for i in compared}

    for _ in range(max_iterations):
        new_strengths = {}
        for i in compared:
            denom = sum(
                games[i][j] / (strengths[i] + strengths[j])
                for j in compared
                if j != i and games[i][j]
            )
            new_strengths[i] = max(win_totals[i] / denom, 1e-12) if denom > 0 else strengths[i]

        mean = sum(new_strengths.values()) / len(new_strengths)
        if mean > 0:
            new_strengths = {i: v / mean for i, v in new_strengths.items()}

        max_delta = max(abs(new_strengths[i] - strengths[i]) for i in compared)
        strengths = new_strengths
        if max_delta < tolerance:
            break

    result = dict(strengths)
    for i in uncompared:
        result[i] = 0.0
    return result
