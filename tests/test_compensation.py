import pytest

from jobmux.compensation import normalize_compensation


def test_higher_cost_of_living_anchor_increases_equivalent_salary():
    # listing is in a cheaper area (index 90) than the anchor (index 120)
    result = normalize_compensation(listing_salary=60000, listing_col_index=90, anchor_col_index=120)
    assert result == pytest.approx(60000 * (120 / 90))
    assert result > 60000


def test_lower_cost_of_living_anchor_decreases_equivalent_salary():
    result = normalize_compensation(listing_salary=60000, listing_col_index=120, anchor_col_index=90)
    assert result < 60000


def test_equal_indices_returns_same_salary():
    result = normalize_compensation(listing_salary=60000, listing_col_index=100, anchor_col_index=100)
    assert result == pytest.approx(60000)


def test_rejects_nonpositive_indices():
    with pytest.raises(ValueError):
        normalize_compensation(60000, 0, 100)
    with pytest.raises(ValueError):
        normalize_compensation(60000, 100, -5)


def test_rejects_negative_salary():
    with pytest.raises(ValueError):
        normalize_compensation(-1000, 100, 100)
