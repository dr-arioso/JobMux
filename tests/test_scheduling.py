from datetime import date

import pytest

from jobmux.scheduling import (
    CandidateAction,
    VolatilityTier,
    next_recheck_date,
    order_by_information_gain_per_cost,
    select_within_budget,
)


def test_next_recheck_uses_generic_interval_when_no_cycle_known():
    last = date(2026, 7, 23)
    assert next_recheck_date(VolatilityTier.HIGH, last) == date(2026, 7, 30)
    assert next_recheck_date(VolatilityTier.LOW, last) == date(2026, 8, 22)


def test_next_recheck_schedules_before_known_cycle_date():
    last = date(2026, 7, 1)
    cycle = date(2026, 7, 20)
    result = next_recheck_date(VolatilityTier.LOW, last, known_cycle_date=cycle, lead_days_before_cycle=5)
    assert result == date(2026, 7, 15)


def test_next_recheck_falls_back_to_generic_if_cycle_lead_would_be_before_last_checked():
    last = date(2026, 7, 23)
    cycle = date(2026, 7, 25)  # too close — lead time would land before last_checked
    result = next_recheck_date(VolatilityTier.HIGH, last, known_cycle_date=cycle, lead_days_before_cycle=7)
    assert result == date(2026, 7, 30)  # generic HIGH interval


def test_next_recheck_ignores_cycle_date_in_the_past():
    last = date(2026, 7, 23)
    cycle = date(2026, 1, 1)
    result = next_recheck_date(VolatilityTier.MEDIUM, last, known_cycle_date=cycle)
    assert result == date(2026, 8, 6)


def test_order_by_information_gain_per_cost():
    actions = [
        CandidateAction("cheap_high_gain", expected_information_gain=8.0, cost=1.0),
        CandidateAction("expensive_high_gain", expected_information_gain=8.0, cost=4.0),
        CandidateAction("free_useless", expected_information_gain=0.0, cost=0.0),
        CandidateAction("free_useful", expected_information_gain=5.0, cost=0.0),
    ]
    ordered = order_by_information_gain_per_cost(actions)
    assert ordered[0].name == "free_useful"       # infinite ratio
    assert ordered[1].name == "cheap_high_gain"    # ratio 8.0
    assert ordered[2].name == "expensive_high_gain"  # ratio 2.0
    assert ordered[3].name == "free_useless"       # ratio 0.0


def test_order_rejects_negative_cost_or_gain():
    with pytest.raises(ValueError):
        order_by_information_gain_per_cost([CandidateAction("x", -1.0, 1.0)])
    with pytest.raises(ValueError):
        order_by_information_gain_per_cost([CandidateAction("x", 1.0, -1.0)])


def test_select_within_budget_spends_on_best_ratios_first():
    actions = [
        CandidateAction("a", expected_information_gain=10.0, cost=5.0),  # ratio 2.0
        CandidateAction("b", expected_information_gain=9.0, cost=3.0),   # ratio 3.0
        CandidateAction("c", expected_information_gain=1.0, cost=10.0),  # ratio 0.1
    ]
    selected = select_within_budget(actions, budget=8.0)
    names = {a.name for a in selected}
    assert names == {"b", "a"}  # b first (best ratio), then a (fits in remaining budget)


def test_select_within_budget_arbitrarily_high_selects_everything_with_positive_value():
    # architecture.md §1.5: "cost is not an object" is the same ordering
    # with the budget set arbitrarily high — not a separate mode.
    actions = [
        CandidateAction("a", expected_information_gain=10.0, cost=5.0),
        CandidateAction("b", expected_information_gain=1.0, cost=100.0),
    ]
    selected = select_within_budget(actions, budget=1_000_000.0)
    assert {a.name for a in selected} == {"a", "b"}


def test_select_within_budget_zero_budget_selects_only_free_actions():
    actions = [
        CandidateAction("free", expected_information_gain=1.0, cost=0.0),
        CandidateAction("costly", expected_information_gain=100.0, cost=1.0),
    ]
    selected = select_within_budget(actions, budget=0.0)
    assert [a.name for a in selected] == ["free"]
