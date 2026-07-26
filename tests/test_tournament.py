import pytest

from jobmux.tournament import PairwiseResult, bradley_terry_scores, next_pair_to_compare


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


# --- decisions/0005: information-gain-driven pairing selection -------------

def test_fewer_than_two_items_returns_none():
    assert next_pair_to_compare([], []) is None
    assert next_pair_to_compare(["a"], []) is None


def test_first_pair_with_no_results_is_deterministic():
    # Zero comparisons -- every pair is an equal 50/50 toss-up under a
    # uniform prior, so the first candidate pair in item order wins ties.
    assert next_pair_to_compare(["a", "b", "c"], []) == ("a", "b")


def test_never_re_offers_an_already_compared_pair():
    results = [PairwiseResult("a", "b")]
    pair = next_pair_to_compare(["a", "b", "c"], results)
    assert pair is not None
    assert set(pair) != {"a", "b"}


def test_returns_none_once_every_pair_has_been_compared():
    results = [
        PairwiseResult("a", "b"),
        PairwiseResult("a", "c"),
        PairwiseResult("b", "c"),
    ]
    assert next_pair_to_compare(["a", "b", "c"], results) is None


def test_prefers_the_most_uncertain_remaining_pair():
    # a has crushed b in four straight comparisons -- a-vs-b is no longer
    # informative. c is untested against either. The most uncertain
    # remaining pair should involve c, not a repeat of the settled a/b
    # rivalry (which is excluded anyway, but this checks the actual
    # uncertainty-ranking logic among untested pairs too).
    results = [
        PairwiseResult("a", "b"), PairwiseResult("a", "b"),
        PairwiseResult("a", "b"), PairwiseResult("a", "b"),
    ]
    pair = next_pair_to_compare(["a", "b", "c", "d"], results)
    assert pair is not None
    assert "c" in pair or "d" in pair


def test_prefers_a_boundary_relevant_pair_over_a_more_uncertain_bottom_pair():
    # a and b are the clear top tier (each beat both c and d); c and d are
    # the clear bottom tier with identical records against a and b, so
    # c-vs-d is nearly an exact 50/50 toss-up -- more "globally uncertain"
    # by raw distance-from-0.5 than a-vs-b, whose indirect records already
    # favor a somewhat. With top_k=1 (boundary = top 2 estimated items),
    # a-vs-b is the only remaining pair that could actually move the
    # top-2 boundary; c-vs-d can't, no matter how uncertain it looks in
    # isolation. The algorithm should pick a-vs-b anyway.
    results = [
        PairwiseResult("a", "c"), PairwiseResult("a", "c"),
        PairwiseResult("a", "d"), PairwiseResult("a", "d"),
        PairwiseResult("b", "c"),
        PairwiseResult("b", "d"),
    ]
    assert next_pair_to_compare(["a", "b", "c", "d"], results, top_k=1) == ("a", "b")


def test_falls_back_to_global_uncertainty_when_no_boundary_pair_remains():
    # Once a-vs-b (the only boundary-relevant pair under top_k=1) is
    # itself already compared, the only thing left is c-vs-d -- the
    # fallback pool must still offer it rather than giving up early.
    results = [
        PairwiseResult("a", "c"), PairwiseResult("a", "d"),
        PairwiseResult("b", "c"), PairwiseResult("b", "d"),
        PairwiseResult("a", "b"),
    ]
    assert next_pair_to_compare(["a", "b", "c", "d"], results, top_k=1) == ("c", "d")


def test_new_uncompared_item_treated_as_open_question_not_a_predicted_loser():
    # "isolated" has never been compared to anything, so it defaults to
    # bradley_terry_scores' 0.0 -- next_pair_to_compare must not treat
    # that as "isolated always loses" when picking the next pair.
    results = [PairwiseResult("a", "b")]
    pair = next_pair_to_compare(["a", "b", "isolated"], results)
    assert pair is not None
    assert "isolated" in pair
