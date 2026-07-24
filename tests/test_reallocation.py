import pytest

from jobmux.reallocation import ReallocationStrategy, reallocate


def test_proportional_redistributes_by_relative_share():
    weights = {"a": 0.5, "b": 0.3, "c": 0.2}
    result = reallocate(weights, "a", 0.7)
    assert result["a"] == pytest.approx(0.7)
    # remaining budget 0.3, split between b (0.3) and c (0.2) in 3:2 ratio
    assert result["b"] == pytest.approx(0.3 * (0.3 / 0.5))
    assert result["c"] == pytest.approx(0.3 * (0.2 / 0.5))
    assert sum(result.values()) == pytest.approx(sum(weights.values()))


def test_proportional_falls_back_to_equal_split_when_others_sum_to_zero():
    weights = {"a": 0.5, "b": 0.0, "c": 0.0}
    result = reallocate(weights, "a", 0.2)
    assert result["a"] == pytest.approx(0.2)
    assert result["b"] == pytest.approx(0.15)
    assert result["c"] == pytest.approx(0.15)


def test_equal_split_ignores_prior_shares():
    weights = {"a": 0.5, "b": 0.3, "c": 0.2}
    result = reallocate(weights, "a", 0.7, strategy=ReallocationStrategy.EQUAL_SPLIT)
    assert result["b"] == pytest.approx(0.15)
    assert result["c"] == pytest.approx(0.15)


def test_protect_top_k_keeps_protected_weight_exactly():
    weights = {"a": 0.5, "b": 0.3, "c": 0.2}
    result = reallocate(
        weights, "a", 0.6,
        strategy=ReallocationStrategy.PROTECT_TOP_K,
        protected_keys=frozenset({"b"}),
    )
    assert result["b"] == pytest.approx(0.3)
    assert result["a"] == pytest.approx(0.6)
    assert result["c"] == pytest.approx(0.1)
    assert sum(result.values()) == pytest.approx(1.0)


def test_protect_top_k_requires_protected_keys():
    weights = {"a": 0.5, "b": 0.3, "c": 0.2}
    with pytest.raises(ValueError):
        reallocate(weights, "a", 0.6, strategy=ReallocationStrategy.PROTECT_TOP_K)


def test_protect_top_k_raises_if_protected_alone_exceeds_remaining_budget():
    weights = {"a": 0.5, "b": 0.3, "c": 0.2}
    with pytest.raises(ValueError):
        reallocate(
            weights, "a", 0.9,
            strategy=ReallocationStrategy.PROTECT_TOP_K,
            protected_keys=frozenset({"b"}),
        )


def test_not_critical_is_a_weight_zeroing_event():
    weights = {"a": 0.5, "b": 0.3, "c": 0.2}
    result = reallocate(weights, "a", 0.0)
    assert result["a"] == 0.0
    assert sum(result.values()) == pytest.approx(1.0)


def test_changed_key_must_exist():
    with pytest.raises(KeyError):
        reallocate({"a": 1.0}, "nonexistent", 0.5)


def test_changed_key_cannot_also_be_protected():
    weights = {"a": 0.5, "b": 0.5}
    with pytest.raises(ValueError):
        reallocate(
            weights, "a", 0.3,
            strategy=ReallocationStrategy.PROTECT_TOP_K,
            protected_keys=frozenset({"a"}),
        )


def test_new_weight_out_of_range_raises():
    weights = {"a": 0.5, "b": 0.5}
    with pytest.raises(ValueError):
        reallocate(weights, "a", 2.0)


def test_single_member_no_others():
    result = reallocate({"a": 1.0}, "a", 0.4)
    assert result == {"a": 0.4}


def test_dimension_level_reallocation_same_mechanism():
    # "The same rule applies one level up when a dimension's rank changes
    # relative to other dimensions" (architecture.md §1.1) — no separate
    # function needed, same call shape at the coarser grain.
    dimension_weights = {"work_style": 0.4, "lifestyle": 0.35, "compensation": 0.25}
    result = reallocate(dimension_weights, "compensation", 0.5)
    assert result["compensation"] == pytest.approx(0.5)
    assert sum(result.values()) == pytest.approx(1.0)
