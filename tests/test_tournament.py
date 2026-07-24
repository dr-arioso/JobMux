import pytest

from jobmux.tournament import PairwiseResult, bradley_terry_scores


def test_empty_items_returns_empty():
    assert bradley_terry_scores([], []) == {}


def test_duplicate_items_rejected():
    with pytest.raises(ValueError):
        bradley_terry_scores(["a", "a"], [])


def test_result_referencing_unknown_item_rejected():
    with pytest.raises(ValueError):
        bradley_terry_scores(["a", "b"], [PairwiseResult("a", "c")])


def test_self_comparison_rejected():
    with pytest.raises(ValueError):
        bradley_terry_scores(["a", "b"], [PairwiseResult("a", "a")])


def test_clear_total_order_recovered():
    # a beats b beats c, consistently and repeatedly
    results = [
        PairwiseResult("a", "b"), PairwiseResult("a", "b"), PairwiseResult("a", "b"),
        PairwiseResult("b", "c"), PairwiseResult("b", "c"), PairwiseResult("b", "c"),
        PairwiseResult("a", "c"), PairwiseResult("a", "c"), PairwiseResult("a", "c"),
    ]
    scores = bradley_terry_scores(["a", "b", "c"], results)
    assert scores["a"] > scores["b"] > scores["c"]


def test_symmetric_ties_produce_equal_scores():
    results = [
        PairwiseResult("a", "b"), PairwiseResult("b", "a"),
        PairwiseResult("a", "b"), PairwiseResult("b", "a"),
    ]
    scores = bradley_terry_scores(["a", "b"], results)
    assert scores["a"] == pytest.approx(scores["b"], abs=1e-6)


def test_uncompared_item_gets_zero_not_omitted():
    results = [PairwiseResult("a", "b")]
    scores = bradley_terry_scores(["a", "b", "isolated"], results)
    assert set(scores.keys()) == {"a", "b", "isolated"}
    assert scores["isolated"] == 0.0


def test_all_uncompared_returns_all_zero():
    scores = bradley_terry_scores(["a", "b", "c"], [])
    assert scores == {"a": 0.0, "b": 0.0, "c": 0.0}


def test_sparse_tournament_stopped_early_still_orders_compared_items():
    # elicitation.md §2.6: tournament stops once a stable top holds, not a
    # full round-robin. Only a-vs-b and a-vs-c were run; b-vs-c never was.
    results = [
        PairwiseResult("a", "b"), PairwiseResult("a", "b"),
        PairwiseResult("a", "c"), PairwiseResult("a", "c"),
    ]
    scores = bradley_terry_scores(["a", "b", "c"], results)
    assert scores["a"] > scores["b"]
    assert scores["a"] > scores["c"]


def test_never_returns_negative_or_nan():
    import math
    results = [
        PairwiseResult("a", "b"), PairwiseResult("b", "c"),
        PairwiseResult("c", "a"),  # a cycle — no consistent total order
    ]
    scores = bradley_terry_scores(["a", "b", "c"], results)
    for v in scores.values():
        assert v >= 0.0
        assert not math.isnan(v)
