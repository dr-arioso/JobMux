import pytest

from jobmux.scoring import (
    QualificationCheck,
    QualificationKind,
    ScoredPriority,
    chebyshev_weighted_score,
    qualification_completion,
    weighted_sum_score,
)


def test_weighted_sum_basic():
    priorities = [
        ScoredPriority("a", weight=0.5, score=1.0),
        ScoredPriority("b", weight=0.5, score=0.0),
    ]
    assert weighted_sum_score(priorities) == pytest.approx(0.5)


def test_weighted_sum_zero_total_weight_returns_zero():
    priorities = [ScoredPriority("a", weight=0.0, score=1.0)]
    assert weighted_sum_score(priorities) == 0.0


def test_chebyshev_lambda_zero_equals_weighted_sum():
    priorities = [
        ScoredPriority("a", weight=0.6, score=0.1),  # top-ranked, scores badly
        ScoredPriority("b", weight=0.4, score=1.0),
    ]
    linear = weighted_sum_score(priorities)
    chebyshev = chebyshev_weighted_score(priorities, top_k=1, lambda_=0.0)
    assert chebyshev == pytest.approx(linear)


def test_chebyshev_penalizes_bad_top_ranked_priority_more_than_linear_would():
    # #1 priority scores terribly, #2 (lower weight) scores perfectly.
    # A plain weighted sum lets #2 partially compensate; Chebyshev should
    # score this case lower than the plain linear term.
    priorities = [
        ScoredPriority("top", weight=0.7, score=0.0),
        ScoredPriority("second", weight=0.3, score=1.0),
    ]
    linear = weighted_sum_score(priorities)
    chebyshev = chebyshev_weighted_score(priorities, top_k=1, lambda_=0.5)
    assert chebyshev < linear


def test_chebyshev_top_k_zero_reduces_to_linear():
    priorities = [ScoredPriority("a", weight=1.0, score=0.5)]
    assert chebyshev_weighted_score(priorities, top_k=0) == pytest.approx(
        weighted_sum_score(priorities)
    )


def test_chebyshev_empty_priorities_returns_zero():
    assert chebyshev_weighted_score([], top_k=2) == 0.0


def test_chebyshev_rejects_invalid_lambda():
    priorities = [ScoredPriority("a", weight=1.0, score=0.5)]
    with pytest.raises(ValueError):
        chebyshev_weighted_score(priorities, top_k=1, lambda_=1.5)


def test_chebyshev_rejects_negative_top_k():
    priorities = [ScoredPriority("a", weight=1.0, score=0.5)]
    with pytest.raises(ValueError):
        chebyshev_weighted_score(priorities, top_k=-1)


def test_qualification_completion_all_met():
    checks = [
        QualificationCheck("degree", met=True, kind=QualificationKind.MINIMUM),
        QualificationCheck("license", met=True, kind=QualificationKind.DESIRED),
    ]
    result = qualification_completion(checks)
    assert result.met_count == 2
    assert result.total_count == 2
    assert result.completion_ratio == pytest.approx(1.0)
    assert result.all_minimums_met is True


def test_qualification_completion_unmet_minimum_is_controlling():
    checks = [
        QualificationCheck("degree", met=False, kind=QualificationKind.MINIMUM),
        QualificationCheck("license", met=True, kind=QualificationKind.DESIRED),
    ]
    result = qualification_completion(checks)
    assert result.all_minimums_met is False
    assert result.completion_ratio == pytest.approx(0.5)


def test_qualification_completion_unmet_desired_is_non_controlling():
    checks = [
        QualificationCheck("degree", met=True, kind=QualificationKind.MINIMUM),
        QualificationCheck("license", met=False, kind=QualificationKind.DESIRED),
    ]
    result = qualification_completion(checks)
    assert result.all_minimums_met is True
    assert result.completion_ratio == pytest.approx(0.5)


def test_qualification_completion_empty_checks():
    result = qualification_completion([])
    assert result.all_minimums_met is True
    assert result.completion_ratio == 1.0
