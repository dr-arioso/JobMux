from datetime import date

from jobmux.verification import (
    ConstraintKind,
    NearMiss,
    ThresholdDirection,
    diff_ledger_value,
    is_listing_stale,
    refilter_near_misses,
)


def test_is_listing_stale_true_when_closing_date_in_past():
    assert is_listing_stale(closing_date=date(2026, 3, 1), as_of=date(2026, 7, 23)) is True


def test_is_listing_stale_false_when_closing_date_in_future():
    assert is_listing_stale(closing_date=date(2026, 12, 1), as_of=date(2026, 7, 23)) is False


def test_is_listing_stale_false_on_exact_closing_date():
    d = date(2026, 7, 23)
    assert is_listing_stale(closing_date=d, as_of=d) is False


def test_diff_ledger_value_detects_change():
    diff = diff_ledger_value("OPEN", "CLOSED")
    assert diff.changed is True
    assert diff.old_value == "OPEN"
    assert diff.new_value == "CLOSED"


def test_diff_ledger_value_no_change():
    diff = diff_ledger_value("OPEN", "OPEN")
    assert diff.changed is False


def test_refilter_near_misses_resurrects_passing_minimum_direction():
    near_misses = [
        NearMiss("listing-1", "salary", ConstraintKind.THRESHOLD, failed_value=55000, required_value=60000),
        NearMiss("listing-2", "salary", ConstraintKind.THRESHOLD, failed_value=40000, required_value=60000),
    ]
    resurrected = refilter_near_misses(near_misses, "salary", new_required_value=50000)
    assert resurrected == ["listing-1"]


def test_refilter_near_misses_maximum_direction():
    near_misses = [
        NearMiss(
            "listing-1", "commute_miles", ConstraintKind.THRESHOLD,
            failed_value=45, required_value=30, direction=ThresholdDirection.MAXIMUM,
        ),
    ]
    # loosen the commute ceiling to 50 miles — 45 now passes
    resurrected = refilter_near_misses(near_misses, "commute_miles", new_required_value=50)
    assert resurrected == ["listing-1"]


def test_refilter_near_misses_ignores_other_constraints():
    near_misses = [
        NearMiss("listing-1", "salary", ConstraintKind.THRESHOLD, failed_value=55000, required_value=60000),
    ]
    resurrected = refilter_near_misses(near_misses, "commute_miles", new_required_value=999)
    assert resurrected == []


def test_refilter_near_misses_skips_mandatory_kind():
    near_misses = [
        NearMiss("listing-1", "must_be_remote", ConstraintKind.MANDATORY, failed_value=0, required_value=1),
    ]
    resurrected = refilter_near_misses(near_misses, "must_be_remote", new_required_value=0)
    assert resurrected == []


def test_refilter_near_misses_qualification_kind_behaves_like_threshold():
    near_misses = [
        NearMiss(
            "listing-1", "years_experience", ConstraintKind.QUALIFICATION,
            failed_value=2, required_value=3,
        ),
    ]
    resurrected = refilter_near_misses(near_misses, "years_experience", new_required_value=2)
    assert resurrected == ["listing-1"]
