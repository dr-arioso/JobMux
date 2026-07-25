import pytest

from jobmux.signal_fusion import (
    Assertion,
    EvidenceSignal,
    Outcome,
    SignalSource,
    SignalState,
    reconcile,
)


def _signal(source, state, assertion=None, reliability=1.0):
    return EvidenceSignal(source=source, state=state, assertion=assertion, reliability=reliability)


# --- EvidenceSignal validation ---------------------------------------------

def test_confirmed_signal_without_assertion_raises():
    with pytest.raises(ValueError):
        EvidenceSignal(source=SignalSource.ADAPTIVE, state=SignalState.CONFIRMED)


def test_superseded_signal_without_assertion_raises():
    with pytest.raises(ValueError):
        EvidenceSignal(source=SignalSource.BOARD_HEURISTIC, state=SignalState.SUPERSEDED)


def test_pending_signal_with_assertion_raises():
    with pytest.raises(ValueError):
        EvidenceSignal(
            source=SignalSource.ANALOG, state=SignalState.PENDING, assertion=Assertion.AVAILABLE
        )


def test_unable_to_obtain_signal_with_assertion_raises():
    with pytest.raises(ValueError):
        EvidenceSignal(
            source=SignalSource.ANALOG,
            state=SignalState.UNABLE_TO_OBTAIN,
            assertion=Assertion.UNAVAILABLE,
        )


def test_pending_signal_without_assertion_is_valid():
    EvidenceSignal(source=SignalSource.ANALOG, state=SignalState.PENDING)  # no raise


def test_reliability_below_zero_raises():
    with pytest.raises(ValueError):
        EvidenceSignal(
            source=SignalSource.ADAPTIVE,
            state=SignalState.CONFIRMED,
            assertion=Assertion.AVAILABLE,
            reliability=-0.1,
        )


def test_reliability_above_one_raises():
    with pytest.raises(ValueError):
        EvidenceSignal(
            source=SignalSource.ADAPTIVE,
            state=SignalState.CONFIRMED,
            assertion=Assertion.AVAILABLE,
            reliability=1.1,
        )


def test_reliability_of_exactly_zero_is_valid():
    # Legitimately "on the record, currently trusted not at all" — distinct
    # from PENDING/UNABLE_TO_OBTAIN, which never had an assertion at all.
    EvidenceSignal(
        source=SignalSource.ADAPTIVE,
        state=SignalState.CONFIRMED,
        assertion=Assertion.AVAILABLE,
        reliability=0.0,
    )


# --- reconcile() input validation -------------------------------------------

def test_reconcile_rejects_zero_confirmed_mass():
    with pytest.raises(ValueError):
        reconcile([], confirmed_mass=0.0)


def test_reconcile_rejects_confirmed_mass_above_one():
    with pytest.raises(ValueError):
        reconcile([], confirmed_mass=1.1)


def test_reconcile_accepts_confirmed_mass_of_exactly_one():
    reconcile([], confirmed_mass=1.0)  # no raise — upper bound is inclusive


def test_reconcile_rejects_negative_conflict_threshold():
    with pytest.raises(ValueError):
        reconcile([], conflict_threshold=-0.01)


def test_reconcile_rejects_conflict_threshold_above_one():
    with pytest.raises(ValueError):
        reconcile([], conflict_threshold=1.01)


# --- The six named outcomes (signal-fusion-module.md §3) -------------------

def test_empty_signal_set_is_unable_to_verify():
    result = reconcile([])
    assert result.outcome is Outcome.UNABLE_TO_VERIFY
    assert result.confidence == 0.0
    assert result.conflict_mass == 0.0


def test_concordant_confirmation_digital_and_analog_agree():
    signals = [
        _signal(SignalSource.ADAPTIVE, SignalState.CONFIRMED, Assertion.AVAILABLE),
        _signal(SignalSource.ANALOG, SignalState.CONFIRMED, Assertion.AVAILABLE),
    ]
    result = reconcile(signals)
    assert result.outcome is Outcome.CONCORDANT_CONFIRMATION
    # Two independent, fully-reliable, agreeing 0.9-mass signals combine
    # above either alone.
    assert result.confidence == pytest.approx(0.99)
    assert result.conflict_mass == pytest.approx(0.0)


def test_concordant_confirmation_beats_a_still_pending_analog_attempt():
    signals = [
        _signal(SignalSource.BOARD_HEURISTIC, SignalState.CONFIRMED, Assertion.AVAILABLE),
        _signal(SignalSource.BOARD_ML, SignalState.CONFIRMED, Assertion.AVAILABLE),
        _signal(SignalSource.ANALOG, SignalState.PENDING),
    ]
    result = reconcile(signals)
    assert result.outcome is Outcome.CONCORDANT_CONFIRMATION
    assert result.confidence == pytest.approx(0.99)


def test_concordant_confirmation_with_a_heavily_discounted_dissent():
    # The "mux, don't discard" case: the employer's own, more recently
    # edited page (adaptive, full reliability) says available; an
    # aggregator's stale mirror (board-heuristic, heavily discounted —
    # judged unreliable relative to the primary source) says unavailable.
    # The dissent doesn't get thrown out (no signal is marked SUPERSEDED —
    # these are two different, independent sources, not the same source
    # re-checking itself) — it just doesn't clear the conflict threshold,
    # so it measurably lowers confidence without flipping the outcome or
    # vanishing from the arithmetic.
    signals = [
        _signal(SignalSource.ADAPTIVE, SignalState.CONFIRMED, Assertion.AVAILABLE, reliability=1.0),
        _signal(
            SignalSource.BOARD_HEURISTIC, SignalState.CONFIRMED, Assertion.UNAVAILABLE, reliability=0.2
        ),
    ]
    result = reconcile(signals)
    assert result.outcome is Outcome.CONCORDANT_CONFIRMATION
    assert result.confidence == pytest.approx(0.8807, abs=1e-3)
    # Lower than a single undisputed 0.9 confirmation — the dissent left a
    # real trace even though it lost.
    assert result.confidence < 0.9
    assert result.conflict_mass > 0.0


def test_analog_resolved_after_digital_trace_superseded():
    # signal-fusion-module.md §6 walkthrough 1: a stale-but-rendering
    # listing's date field is directly re-checked and found past due — the
    # *same* source's own later reading retires its earlier claim — and a
    # department contact confirms it was actually filled.
    signals = [
        _signal(SignalSource.ADAPTIVE, SignalState.SUPERSEDED, Assertion.AVAILABLE),
        _signal(SignalSource.ANALOG, SignalState.CONFIRMED, Assertion.UNAVAILABLE),
    ]
    result = reconcile(signals)
    assert result.outcome is Outcome.ANALOG_RESOLVED
    assert result.confidence == pytest.approx(0.9)


def test_analog_resolved_with_no_digital_signal_at_all():
    signals = [_signal(SignalSource.ANALOG, SignalState.CONFIRMED, Assertion.AVAILABLE)]
    result = reconcile(signals)
    assert result.outcome is Outcome.ANALOG_RESOLVED
    assert result.confidence == pytest.approx(0.9)


def test_digital_only_confidence_is_not_artificially_capped_when_fully_reliable():
    # Revision 2: there's no more hardcoded ceiling on a lone digital
    # confirmation — a fully-reliable digital signal reports the same
    # confidence any other lone confirmed signal would.
    signals = [
        _signal(SignalSource.BOARD_HEURISTIC, SignalState.CONFIRMED, Assertion.AVAILABLE),
        _signal(SignalSource.ANALOG, SignalState.UNABLE_TO_OBTAIN),
    ]
    result = reconcile(signals)
    assert result.outcome is Outcome.DIGITAL_ONLY_CAPPED
    assert result.confidence == pytest.approx(0.9)


def test_digital_only_confidence_reflects_a_deliberately_low_reliability():
    # The discount signal-fusion-module.md §0's weak-proxy shapes (stale-
    # but-rendering, evergreen) call for now lives in the frontier-tier
    # judgment's choice of `reliability`, not in this module.
    signals = [
        _signal(
            SignalSource.BOARD_HEURISTIC, SignalState.CONFIRMED, Assertion.AVAILABLE, reliability=0.6
        ),
        _signal(SignalSource.ANALOG, SignalState.UNABLE_TO_OBTAIN),
    ]
    result = reconcile(signals)
    assert result.outcome is Outcome.DIGITAL_ONLY_CAPPED
    assert result.confidence == pytest.approx(0.9 * 0.6)


def test_analog_pending_when_digital_confirmed_and_analog_drafted_not_executed():
    signals = [
        _signal(SignalSource.ADAPTIVE, SignalState.CONFIRMED, Assertion.AVAILABLE),
        _signal(SignalSource.ANALOG, SignalState.PENDING),
    ]
    result = reconcile(signals)
    assert result.outcome is Outcome.ANALOG_PENDING
    assert result.confidence == pytest.approx(0.9)


def test_analog_pending_with_nothing_yet_confirmed_digitally():
    signals = [_signal(SignalSource.ANALOG, SignalState.PENDING)]
    result = reconcile(signals)
    assert result.outcome is Outcome.ANALOG_PENDING
    assert result.confidence == 0.0


def test_conflicting_when_digital_and_analog_confirm_opposite_assertions():
    # signal-fusion-module.md §6 walkthrough 3: the listing looks current,
    # but an analog contact independently confirms it was already pulled —
    # both fully reliable, so the disagreement clears the default
    # conflict_threshold.
    signals = [
        _signal(SignalSource.BOARD_HEURISTIC, SignalState.CONFIRMED, Assertion.AVAILABLE),
        _signal(SignalSource.ANALOG, SignalState.CONFIRMED, Assertion.UNAVAILABLE),
    ]
    result = reconcile(signals)
    assert result.outcome is Outcome.CONFLICTING
    assert result.conflict_mass == pytest.approx(0.81)
    assert result.confidence == pytest.approx(0.4737, abs=1e-3)  # low — never averaged away per §1


def test_conflict_threshold_governs_whether_a_discounted_dissent_counts():
    # Same two signals as the concordant-with-discounted-dissent case
    # above, but with conflict_threshold lowered enough that even a fairly
    # weak dissent now counts as genuine conflict — demonstrating the
    # threshold is a real, load-bearing parameter, not window dressing.
    signals = [
        _signal(SignalSource.ADAPTIVE, SignalState.CONFIRMED, Assertion.AVAILABLE, reliability=1.0),
        _signal(
            SignalSource.BOARD_HEURISTIC, SignalState.CONFIRMED, Assertion.UNAVAILABLE, reliability=0.2
        ),
    ]
    result = reconcile(signals, conflict_threshold=0.02)
    assert result.outcome is Outcome.CONFLICTING


def test_unable_to_verify_when_every_channel_comes_up_empty():
    signals = [
        _signal(SignalSource.BOARD_HEURISTIC, SignalState.UNABLE_TO_OBTAIN),
        _signal(SignalSource.ANALOG, SignalState.UNABLE_TO_OBTAIN),
    ]
    result = reconcile(signals)
    assert result.outcome is Outcome.UNABLE_TO_VERIFY
    assert result.confidence == 0.0


def test_unable_to_verify_when_only_a_superseded_signal_remains():
    # A digital trace was found stale by its own later re-check and
    # nothing else was ever obtained — not one of the module's six typical
    # shapes, but the honest fallback: nothing currently confirms
    # availability one way or the other.
    signals = [_signal(SignalSource.ADAPTIVE, SignalState.SUPERSEDED, Assertion.AVAILABLE)]
    result = reconcile(signals)
    assert result.outcome is Outcome.UNABLE_TO_VERIFY
    assert result.confidence == 0.0
