from datetime import date

from jobmux.verification import (
    ConstraintKind,
    FalsePositivePattern,
    NearMiss,
    OccupationalCategoryExclusion,
    ThresholdDirection,
    diff_ledger_value,
    is_confirmed_false_positive,
    is_confirmed_false_positive_with_category,
    is_excluded_by_occupational_category,
    is_listing_stale,
    purge_false_positives,
    purge_false_positives_with_category,
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


def _hospital_env_services_pattern():
    return FalsePositivePattern(
        pattern="environmental services",
        field="title",
        reason="hospital housekeeping department, not environmental science",
        added_at=date(2026, 7, 25),
    )


def test_is_confirmed_false_positive_matches_title_case_insensitive():
    fp = _hospital_env_services_pattern()
    match = is_confirmed_false_positive("Environmental Services Technician", "Mankato Hospital", [fp])
    assert match is fp


def test_is_confirmed_false_positive_returns_none_when_no_pattern_matches():
    fp = _hospital_env_services_pattern()
    match = is_confirmed_false_positive("Environmental Scientist", "MN DNR", [fp])
    assert match is None


def test_is_confirmed_false_positive_matches_employer_field():
    fp = FalsePositivePattern(
        pattern="staffing solutions inc",
        field="employer",
        reason="generic staffing agency reposting unrelated roles",
        added_at=date(2026, 7, 25),
    )
    match = is_confirmed_false_positive("Environmental Specialist", "Staffing Solutions Inc.", [fp])
    assert match is fp


def test_purge_false_positives_returns_only_matching_listing_ids():
    fp = _hospital_env_services_pattern()
    listings = [
        ("listing-1", "Environmental Services Technician", "Mankato Hospital"),
        ("listing-2", "Environmental Scientist", "MN DNR"),
    ]
    assert purge_false_positives(listings, [fp]) == ["listing-1"]


# --- decisions/0003: word-boundary + fuzzy matching -------------------------

def test_is_confirmed_false_positive_ignores_punctuation_and_extra_whitespace():
    fp = _hospital_env_services_pattern()
    match = is_confirmed_false_positive("Environmental-Services,  Tech.", "Mankato Hospital", [fp])
    assert match is fp


def test_short_pattern_does_not_match_inside_an_unrelated_word():
    # decisions/0003's motivating bug: plain substring containment let
    # "aid" match inside "maid" — word-boundary matching on normalized
    # tokens fixes this, and the pattern is short enough that fuzzy
    # matching's own min_fuzzy_pattern_length guard keeps it from sneaking
    # back in through that door either.
    fp = FalsePositivePattern(
        pattern="aid", field="title", reason="unrelated short pattern", added_at=date(2026, 7, 25)
    )
    match = is_confirmed_false_positive("Maid Services", "Clean Sweep Inc", [fp])
    assert match is None


def test_fuzzy_matching_catches_an_abbreviated_phrasing():
    # "Svcs" for "Services" — a real phrasing-drift case, not a literal
    # substring of the confirmed pattern.
    fp = _hospital_env_services_pattern()
    match = is_confirmed_false_positive("Environmental Svcs Technician", "Mankato Hospital", [fp])
    assert match is fp


def test_fuzzy_matching_does_not_conflate_a_genuinely_different_title():
    # Unchanged from before this revision: "Environmental Scientist" must
    # still NOT match "environmental services" — this is exactly the
    # boundary decisions/0003's default fuzzy_threshold (0.85) was chosen
    # to respect (the real similarity ratio here is ~0.80).
    fp = _hospital_env_services_pattern()
    match = is_confirmed_false_positive("Environmental Scientist", "MN DNR", [fp])
    assert match is None


def test_fuzzy_threshold_of_one_disables_fuzzy_matching_entirely():
    fp = _hospital_env_services_pattern()
    match = is_confirmed_false_positive(
        "Environmental Svcs Technician", "Mankato Hospital", [fp], fuzzy_threshold=1.0
    )
    assert match is None


# --- decisions/0003: schema.org occupationalCategory / SOC-code exclusion --

def _hospital_soc_exclusion():
    return OccupationalCategoryExclusion(
        soc_code="37-2011.00",  # Janitors and Cleaners
        reason="hospital housekeeping/environmental-services department",
        added_at=date(2026, 7, 25),
    )


def test_is_excluded_by_occupational_category_matches_exact_soc_code():
    excl = _hospital_soc_exclusion()
    assert is_excluded_by_occupational_category("37-2011.00", [excl]) is excl


def test_is_excluded_by_occupational_category_none_when_code_not_listed():
    excl = _hospital_soc_exclusion()
    assert is_excluded_by_occupational_category("19-2041.00", [excl]) is None


def test_is_excluded_by_occupational_category_none_when_listing_has_no_code():
    excl = _hospital_soc_exclusion()
    assert is_excluded_by_occupational_category(None, [excl]) is None


def test_with_category_matches_via_soc_code_even_when_text_would_not():
    excl = _hospital_soc_exclusion()
    match = is_confirmed_false_positive_with_category(
        "Facilities Support Technician",  # no text pattern would catch this
        "Mankato Hospital",
        "37-2011.00",
        text_patterns=[],
        category_exclusions=[excl],
    )
    assert match is excl


def test_with_category_falls_back_to_text_matching_when_code_absent():
    fp = _hospital_env_services_pattern()
    match = is_confirmed_false_positive_with_category(
        "Environmental Services Technician",
        "Mankato Hospital",
        None,
        text_patterns=[fp],
        category_exclusions=[_hospital_soc_exclusion()],
    )
    assert match is fp


def test_with_category_still_checks_text_when_code_present_but_not_excluded():
    fp = _hospital_env_services_pattern()
    match = is_confirmed_false_positive_with_category(
        "Environmental Services Technician",
        "Mankato Hospital",
        "19-2041.00",  # a real SOC code, just not one that's been excluded
        text_patterns=[fp],
        category_exclusions=[_hospital_soc_exclusion()],
    )
    assert match is fp


def test_with_category_none_when_neither_signal_matches():
    match = is_confirmed_false_positive_with_category(
        "Environmental Scientist",
        "MN DNR",
        "19-2041.00",
        text_patterns=[_hospital_env_services_pattern()],
        category_exclusions=[_hospital_soc_exclusion()],
    )
    assert match is None


def test_purge_false_positives_with_category_uses_both_signals():
    fp = _hospital_env_services_pattern()
    excl = _hospital_soc_exclusion()
    listings = [
        ("listing-1", "Facilities Support Technician", "Mankato Hospital", "37-2011.00"),
        ("listing-2", "Environmental Services Technician", "Mankato Hospital", None),
        ("listing-3", "Environmental Scientist", "MN DNR", "19-2041.00"),
    ]
    result = purge_false_positives_with_category(listings, [fp], [excl])
    assert result == ["listing-1", "listing-2"]
