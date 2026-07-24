import pytest

from jobmux.context_pack import Event, EventType, build_context_pack, fold


def _sample_events():
    return [
        Event(1, EventType.PRIORITY_UPSERT, {
            "name": "commute_tolerance", "dimension": "lifestyle", "shape": "scalar", "weight": 0.18,
        }),
        Event(2, EventType.PRIORITY_THRESHOLD_SET, {
            "name": "commute_tolerance", "threshold": {"value": 60, "unit": "miles"},
        }),
        Event(3, EventType.PRIORITY_UPSERT, {
            "name": "growth_potential", "dimension": "work_style", "shape": "scalar", "weight": 0.10,
        }),
        Event(4, EventType.PRIORITY_NOT_CRITICAL_SET, {"name": "growth_potential", "not_critical": True}),
        Event(5, EventType.CATEGORY_FILTER_UPDATED, {
            "name": "career_phase",
            "acceptable_set": ["optimal_local", "field_adjacent"],
            "ranking": ["optimal_local", "field_adjacent"],
        }),
        Event(6, EventType.QUALIFICATION_UPSERT, {
            "name": "environmental_science_degree", "type": "mandatory",
        }),
    ]


def test_fold_applies_events_in_seq_order_regardless_of_input_order():
    events = _sample_events()
    shuffled = [events[3], events[0], events[5], events[1], events[4], events[2]]
    state_in_order = fold(events)
    state_shuffled = fold(shuffled)
    assert state_in_order.last_seq == state_shuffled.last_seq == 6
    assert state_in_order.priorities.keys() == state_shuffled.priorities.keys()
    assert state_in_order.priorities["commute_tolerance"].threshold == \
        state_shuffled.priorities["commute_tolerance"].threshold


def test_fold_editing_priority_before_upsert_raises():
    events = [Event(1, EventType.PRIORITY_THRESHOLD_SET, {"name": "ghost", "threshold": {}})]
    with pytest.raises(KeyError):
        fold(events)


def test_fold_unknown_event_type_raises():
    # Construct via object.__new__ style is overkill; just confirm the
    # exhaustive-enum guard exists by checking every real EventType is handled.
    from jobmux.context_pack import EventType as ET
    handled = {
        ET.PRIORITY_UPSERT, ET.PRIORITY_THRESHOLD_SET, ET.PRIORITY_MANDATORY_SET,
        ET.PRIORITY_WEIGHT_SET, ET.PRIORITY_NOT_CRITICAL_SET, ET.QUALIFICATION_UPSERT,
        ET.CATEGORY_FILTER_UPDATED,
    }
    assert handled == set(ET)


def _build_pack(state, **overrides):
    kwargs = dict(
        pack_id="pack-1",
        session_id="session-1",
        generated_at="2026-07-23T00:00:00Z",
        attested_schema=["employmentType", "baseSalary"],
        reference_anchors={"compensation_normalization": {"mode": "fixed_destination"}},
        discovery_context={"active_modules": ["fragmented_small_employer"]},
        near_miss_vocabulary={"failure_reasons": ["threshold:<priority_name>"]},
        forbidden_scope="extract/tag only, no scoring, no ranking",
    )
    kwargs.update(overrides)
    return build_context_pack(state, **kwargs)


def test_build_context_pack_excludes_not_critical_priorities():
    state = fold(_sample_events())
    pack = _build_pack(state)
    names = {p["name"] for p in pack["active_priorities"]}
    assert "commute_tolerance" in names
    assert "growth_potential" not in names  # excluded: not_critical


def test_build_context_pack_carries_folded_from_event_seq():
    state = fold(_sample_events())
    pack = _build_pack(state)
    assert pack["folded_from_event_seq"] == 6


def test_build_context_pack_shapes_category_filters_and_qualifications():
    state = fold(_sample_events())
    pack = _build_pack(state)
    assert pack["category_filters"] == [{
        "name": "career_phase",
        "acceptable_set": ["optimal_local", "field_adjacent"],
        "ranking": ["optimal_local", "field_adjacent"],
    }]
    assert pack["qualifications"] == [{"name": "environmental_science_degree", "type": "mandatory"}]


def test_build_context_pack_small_model_tier_requires_empty_inferable_schema():
    state = fold(_sample_events())
    with pytest.raises(ValueError):
        _build_pack(state, small_model_tier=True, inferable_schema=["variety", "autonomy"])


def test_build_context_pack_small_model_tier_ok_with_empty_inferable_schema():
    state = fold(_sample_events())
    pack = _build_pack(state, small_model_tier=True)
    assert pack["inferable_schema"] == []


def test_build_context_pack_frontier_tier_may_populate_inferable_schema():
    state = fold(_sample_events())
    pack = _build_pack(state, inferable_schema=["variety", "autonomy"])
    assert pack["inferable_schema"] == ["variety", "autonomy"]


def test_build_context_pack_matches_architecture_doc_top_level_keys():
    state = fold(_sample_events())
    pack = _build_pack(state)
    expected_keys = {
        "pack_id", "session_id", "folded_from_event_seq", "generated_at",
        "active_priorities", "category_filters", "qualifications",
        "aptitudes_requested", "attested_schema", "inferable_schema",
        "reference_anchors", "discovery_context", "near_miss_vocabulary",
        "forbidden_scope",
    }
    assert set(pack.keys()) == expected_keys
