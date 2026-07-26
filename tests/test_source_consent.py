from datetime import date

from jobmux.source_consent import (
    ADR_0004_TOS_AMBIGUOUS_SOURCES,
    SourceConsentExclusion,
    is_excluded_by_source_consent,
    purge_by_source_consent,
)


def _default_exclusion():
    return SourceConsentExclusion(
        excluded_sources=ADR_0004_TOS_AMBIGUOUS_SOURCES,
        reason="candidate answered 'exclude' to the ToS-ambiguous-source consent question",
        recorded_at=date(2026, 7, 26),
    )


def test_is_excluded_by_source_consent_true_for_excluded_source():
    assert is_excluded_by_source_consent("meta", _default_exclusion()) is True


def test_is_excluded_by_source_consent_is_case_insensitive():
    assert is_excluded_by_source_consent("Meta", _default_exclusion()) is True
    assert is_excluded_by_source_consent("TESLA", _default_exclusion()) is True


def test_is_excluded_by_source_consent_false_for_clean_source():
    assert is_excluded_by_source_consent("greenhouse", _default_exclusion()) is False


def test_is_excluded_by_source_consent_false_when_no_exclusion_on_file():
    # No consent answer recorded yet -- not itself grounds to exclude.
    assert is_excluded_by_source_consent("meta", None) is False


def test_is_excluded_by_source_consent_false_when_listing_source_is_none():
    assert is_excluded_by_source_consent(None, _default_exclusion()) is False


def test_custom_exclusion_set_not_limited_to_adr_0004_default():
    custom = SourceConsentExclusion(
        excluded_sources=frozenset({"acmecorp"}),
        reason="candidate-specific opt-out, not the ADR-0004 default bucket",
        recorded_at=date(2026, 7, 26),
    )
    assert is_excluded_by_source_consent("acmecorp", custom) is True
    assert is_excluded_by_source_consent("meta", custom) is False


def test_purge_by_source_consent_returns_only_matching_listing_ids():
    listings = [
        ("listing-1", "meta"),
        ("listing-2", "greenhouse"),
        ("listing-3", "tesla"),
        ("listing-4", "lever"),
    ]
    result = purge_by_source_consent(listings, _default_exclusion())
    assert result == ["listing-1", "listing-3"]


def test_purge_by_source_consent_empty_when_no_exclusion_on_file():
    listings = [("listing-1", "meta")]
    assert purge_by_source_consent(listings, None) == []


def test_adr_0004_default_bucket_matches_the_adr_named_sources():
    assert ADR_0004_TOS_AMBIGUOUS_SOURCES == frozenset(
        {"meta", "tesla", "apple", "amazon", "google", "bytedance", "tiktok", "uber"}
    )
