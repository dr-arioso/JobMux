import pytest

from jobmux.consistency import (
    ImportanceMismatch,
    StatedImportance,
    detect_importance_mismatch,
    detect_importance_mismatches,
)


def test_high_stated_importance_landing_last_is_a_mismatch():
    result = detect_importance_mismatch("compensation", StatedImportance.HIGH, 4, 4)
    assert result == ImportanceMismatch("compensation", StatedImportance.HIGH, 4, 4)


def test_high_stated_importance_landing_top_is_not_a_mismatch():
    assert detect_importance_mismatch("compensation", StatedImportance.HIGH, 1, 4) is None


def test_high_stated_importance_at_the_ceiling_is_not_a_mismatch():
    # rank 2 is still within the top-2 ceiling for a HIGH claim.
    assert detect_importance_mismatch("compensation", StatedImportance.HIGH, 2, 5) is None


def test_high_stated_importance_just_past_the_ceiling_is_a_mismatch():
    assert detect_importance_mismatch("compensation", StatedImportance.HIGH, 3, 5) is not None


def test_low_stated_importance_landing_first_is_a_mismatch():
    result = detect_importance_mismatch("commute", StatedImportance.LOW, 1, 4)
    assert result == ImportanceMismatch("commute", StatedImportance.LOW, 1, 4)


def test_low_stated_importance_landing_last_is_not_a_mismatch():
    assert detect_importance_mismatch("commute", StatedImportance.LOW, 4, 4) is None


def test_medium_stated_importance_never_mismatches_regardless_of_rank():
    for rank in range(1, 5):
        assert detect_importance_mismatch("variety", StatedImportance.MEDIUM, rank, 4) is None


def test_out_of_range_rank_raises():
    with pytest.raises(ValueError):
        detect_importance_mismatch("compensation", StatedImportance.HIGH, 0, 4)
    with pytest.raises(ValueError):
        detect_importance_mismatch("compensation", StatedImportance.HIGH, 5, 4)


def test_batch_detects_only_the_real_mismatches():
    stated = {
        "compensation": StatedImportance.HIGH,
        "variety": StatedImportance.MEDIUM,
        "commute": StatedImportance.LOW,
    }
    ranks = {"compensation": 3, "variety": 2, "commute": 1}
    mismatches = detect_importance_mismatches(stated, ranks)
    names = {m.priority_name for m in mismatches}
    assert names == {"compensation", "commute"}


def test_batch_skips_priorities_with_no_stated_importance_on_file():
    # "growth" was added to the values pass with no prior stated signal
    # (architecture.md Section 1.1's "let the candidate add") -- nothing
    # to mismatch against, not an error.
    stated = {"compensation": StatedImportance.HIGH}
    ranks = {"compensation": 1, "growth": 2}
    mismatches = detect_importance_mismatches(stated, ranks)
    assert mismatches == []


def test_batch_empty_when_everything_agrees():
    stated = {"compensation": StatedImportance.HIGH, "commute": StatedImportance.LOW}
    ranks = {"compensation": 1, "commute": 2}
    assert detect_importance_mismatches(stated, ranks) == []
