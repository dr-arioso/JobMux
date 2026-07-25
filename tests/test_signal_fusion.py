import pytest

from jobmux.signal_fusion import (
    Assertion,
    EvidenceSignal,
    Outcome,
    SignalSource,
    SignalState,
    reconcile,
)


def _signal(source, state, assertion=None):
    return EvidenceSignal(source=source, state=state, assertion=assertion)


# --- EvidenceSignal validation ---------------------------------------------

def test_confirmed_signal_without_assertion_raises():
    with pytest.raises(ValueError):
        EvidenceSignal(source=SignalSource.ADAPTIVE, state=SignalState.CONFIRMED)


def test_contradicted_signal_without_assertion_raises():
    with pytest.raises(ValueError):
        EvidenceSignal(source=SignalSource.BOARD_HEURISTIC, state=SignalState.CONTRADICTED)


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


# --- reconcile() input validation -------------------------------------------

def test_reconcile_rejects_zero_confirmed_mass():
    with pytest.raises(ValueError):
        reconcile([], confirmed_mass=0.0)


def test_reconcile_rejects_confirmed_mass_above_one():
    with pytest.raises(ValueError):
        reconcile([], confirmed_mass=1.1)


def test_reconcile_rejects_negative_digital_only_cap():
    with pytest.raises(ValueError):
        reconcile([], digital_only_cap=-0.1)


def test_reconcile_accepts_confirmed_mass_of_exactly_one():
    reconcile([], confirmed_mass=1.0)  # no raise — upper bound is inclusive


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
    # Two independent agreeing 0.9-mass signals combine above either alone.
    assert result.confidence == pytest.approx(0.99)
    assert result.conflict_mass == pytest.approx(0.0)


def test_concordant_confirmation_beats_a_still_pending_analog_attempt():
    # signal-fusion-module.md §6, ordering check: two board-sourced signals
    # already agree even though an analog attempt is still outstanding —
    # concordance among what's confirmed takes priority over the fact that
    # something else is merely pending.
    signals = [
        _signal(SignalSource.BOARD_HEURISTIC, SignalState.CONFIRMED, Assertion.AVAILABLE),
        _signal(SignalSource.BOARD_ML, SignalState.CONFIRMED, Assertion.AVAILABLE),
        _signal(SignalSource.ANALOG, SignalState.PENDING),
    ]
    result = reconcile(signals)
    assert result.outcome is Outcome.CONCORDANT_CONFIRMATION
    assert result.confidence == pytest.approx(0.99)


def test_analog_resolved_after_digital_trace_contradicted():
    # signal-fusion-module.md §6 walkthrough 1: a stale-but-rendering
    # listing's date field is confirmed past due (digital CONTRADICTED —
    # its original "still open" claim was wrong), and a department contact
    # confirms it was actually filled.
    signals = [
        _signal(SignalSource.ADAPTIVE, SignalState.CONTRADICTED, Assertion.AVAILABLE),
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


def test_digital_only_capped_when_analog_channel_unreachable():
    # signal-fusion-module.md §6 walkthrough 2: an evergreen posting, and an
    # analog contact who won't confirm anything more specific than the
    # posting itself already said.
    signals = [
        _signal(SignalSource.BOARD_HEURISTIC, SignalState.CONFIRMED, Assertion.AVAILABLE),
        _signal(SignalSource.ANALOG, SignalState.UNABLE_TO_OBTAIN),
    ]
    result = reconcile(signals)
    assert result.outcome is Outcome.DIGITAL_ONLY_CAPPED
    assert result.confidence == pytest.approx(0.75)  # the explicit cap, below confirmed_mass


def test_digital_only_capped_confidence_never_exceeds_the_cap_even_with_high_confirmed_mass():
    signals = [_signal(SignalSource.ADAPTIVE, SignalState.CONFIRMED, Assertion.AVAILABLE)]
    result = reconcile(signals, confirmed_mass=0.99, digital_only_cap=0.6)
    assert result.confidence == pytest.approx(0.6)


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
    # but an analog contact independently confirms it was already pulled.
    signals = [
        _signal(SignalSource.BOARD_HEURISTIC, SignalState.CONFIRMED, Assertion.AVAILABLE),
        _signal(SignalSource.ANALOG, SignalState.CONFIRMED, Assertion.UNAVAILABLE),
    ]
    result = reconcile(signals)
    assert result.outcome is Outcome.CONFLICTING
    assert result.conflict_mass == pytest.approx(0.81)
    assert result.confidence == pytest.approx(0.19)  # low — never averaged away per §1


def test_unable_to_verify_when_every_channel_comes_up_empty():
    signals = [
        _signal(SignalSource.BOARD_HEURISTIC, SignalState.UNABLE_TO_OBTAIN),
        _signal(SignalSource.ANALOG, SignalState.UNABLE_TO_OBTAIN),
    ]
    result = reconcile(signals)
    assert result.outcome is Outcome.UNABLE_TO_VERIFY
    assert result.confidence == 0.0


def test_unable_to_verify_when_only_a_contradicted_signal_remains():
    # A digital trace was found stale and nothing else was ever obtained —
    # not one of the module's six typical shapes, but the honest fallback:
    # nothing currently confirms availability one way or the other.
    signals = [_signal(SignalSource.ADAPTIVE, SignalState.CONTRADICTED, Assertion.AVAILABLE)]
    result = reconcile(signals)
    assert result.outcome is Outcome.UNABLE_TO_VERIFY
    assert result.confidence == 0.0
