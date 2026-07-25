"""Signal fusion — architecture.md §1.4's evidence-signal-set reconciliation,
instantiated for signal-fusion-module.md §3's six named outcomes.

architecture.md §1.4: "characterize the set as concordant (agreeing confirmed
signals) or discordant (disagreeing confirmed signals), then derive two things
from that characterization — a human-readable outcome label... and a numeric
confidence value." Both are algorithmic-tier (§2.3) once every signal's own
state is already known — judging what state an individual signal deserves
stays frontier-tier and out of scope for this module, exactly like
verification.py's FalsePositivePattern confirmation and near-miss tagging.

Two things this module needs that architecture.md §1.4 doesn't spell out,
flagged here the same way jobmux/scoring.py's Chebyshev formula is flagged —
first instantiations, not settled decisions (see jobmux/README.md):

1. **The `assertion` field.** architecture.md §1.4's decided signal shape is
   `(source, state, timestamp or quoted basis)` — it says signals can
   "agree" or "disagree" but doesn't say what a signal's content actually
   is, which is what agreement has to be computed over. This module adds a
   fourth field, `assertion` (available / unavailable), carried only by
   CONFIRMED and CONTRADICTED signals (a PENDING or UNABLE_TO_OBTAIN signal
   hasn't produced a usable claim yet). A future session could reasonably
   decide a richer assertion vocabulary is needed (e.g. distinguishing
   "evergreen, no specific confirmation" from a flat "unavailable") — this
   implementation found the binary sufficient for every outcome
   signal-fusion-module.md §3 names, including the evergreen case (which
   maps to an analog signal stuck at UNABLE_TO_OBTAIN, not to a third
   assertion value), but that's an empirical finding from building this
   module, not a guarantee it stays sufficient.

2. **The confidence formula.** Rather than a hand-picked number per outcome
   label, this implementation combines every CONFIRMED signal's evidence via
   Dempster-Shafer combination (Shafer, *A Mathematical Theory of Evidence*,
   1976) over the simple two-hypothesis frame {available, unavailable} — a
   real, standard technique for combining independent evidence sources that,
   unlike a plain average, produces an explicit conflict mass when sources
   disagree instead of quietly splitting the difference. This is the same
   discipline scoring.py follows: name a real technique, expose its
   parameters (`confirmed_mass`, `digital_only_cap` below) rather than
   hardcoding them, and say plainly that the formula family itself is open
   to revision. One useful property this formula gets "for free," precisely
   because it's one combination rule applied uniformly rather than one
   constant per label: a single analog-only confirmation naturally lands
   at `confirmed_mass` (~0.9), and two independent agreeing signals combine
   to something higher (~0.99) without a second constant needing to be
   chosen for the concordant case.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SignalSource(Enum):
    """architecture.md §1.4: "source names which evidence-gathering module
    or technique produced the signal." An analog signal may be
    system-orchestrated (AnalogSearch) or candidate-volunteered — both use
    this same ANALOG tag; the distinction isn't a separate source."""
    BOARD_HEURISTIC = "board-heuristic"
    BOARD_ML = "board-ml"
    ADAPTIVE = "adaptive"
    ANALOG = "analog"


DIGITAL_SOURCES = frozenset({SignalSource.BOARD_HEURISTIC, SignalSource.BOARD_ML, SignalSource.ADAPTIVE})


class SignalState(Enum):
    """architecture.md §1.4's per-signal state vocabulary. PENDING is
    signal-fusion-module.md §3's "identified and drafted but not yet
    executed" — the no-irreversible-actions rule (architecture.md §1.2)
    means AnalogSearch's outreach is handed to the candidate, not run by
    the system, so a real gap in time can sit at this state."""
    CONFIRMED = "confirmed"
    CONTRADICTED = "contradicted"
    PENDING = "pending"
    UNABLE_TO_OBTAIN = "unable-to-obtain"


class Assertion(Enum):
    """See module docstring, flag 1 — not part of architecture.md §1.4's
    literal schema, added here to make "agreeing" vs. "disagreeing"
    computable."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class EvidenceSignal:
    """One tagged entry in architecture.md §1.4's open evidence-signal set.

    `basis` holds the quoted basis or timestamp architecture.md §1.4's
    schema calls for; this module doesn't parse or compare it — recency and
    specificity judgments are frontier-tier (signal-fusion-module.md §1) and
    already baked into `state` and `assertion` by the time a signal reaches
    this module.
    """
    source: SignalSource
    state: SignalState
    assertion: Assertion | None = None
    basis: str = ""

    def __post_init__(self) -> None:
        needs_assertion = self.state in (SignalState.CONFIRMED, SignalState.CONTRADICTED)
        if needs_assertion and self.assertion is None:
            raise ValueError(f"a {self.state.value} signal must carry an assertion")
        if not needs_assertion and self.assertion is not None:
            raise ValueError(f"a {self.state.value} signal cannot yet carry an assertion")


class Outcome(Enum):
    """signal-fusion-module.md §3's six named outcomes — "worked examples of
    the general model's output, not a separate closed enumeration of their
    own" (architecture.md §1.4), but the fixed vocabulary this module's
    reconcile() actually returns."""
    CONCORDANT_CONFIRMATION = "concordant-confirmation"
    ANALOG_RESOLVED = "analog-resolved"
    DIGITAL_ONLY_CAPPED = "digital-only-capped-confidence"
    ANALOG_PENDING = "analog-pending"
    CONFLICTING = "conflicting"
    UNABLE_TO_VERIFY = "unable-to-verify"


@dataclass(frozen=True)
class Reconciliation:
    """The two things architecture.md §1.4 says get derived from a
    characterized signal set. `conflict_mass` is exposed alongside the two
    required outputs — it's the Dempster-Shafer conflict term (`K` below)
    that drove a CONFLICTING outcome, kept for anyone reviewing the row
    later rather than discarded once the label is chosen."""
    outcome: Outcome
    confidence: float
    conflict_mass: float


def _is_digital(signal: EvidenceSignal) -> bool:
    return signal.source in DIGITAL_SOURCES


def _signal_mass(signal: EvidenceSignal, confirmed_mass: float) -> tuple[float, float, float]:
    """A single CONFIRMED signal's basic probability assignment (BPA) over
    {available}, {unavailable}, and the full frame (residual ignorance) —
    returned as (m_available, m_unavailable, m_frame). `confirmed_mass` is
    the fixed per-signal belief a CONFIRMED signal contributes to its own
    assertion; the residual `1 - confirmed_mass` is left as ignorance,
    never assigned to the opposite hypothesis, since a confirmed signal
    says nothing against the alternative — it just doesn't rule out being
    wrong. This module doesn't vary `confirmed_mass` per signal (that would
    mean re-judging an individual signal's reliability, which is
    frontier-tier and already done by the time `state` is set) — it's one
    fixed constant applied uniformly."""
    if signal.assertion is Assertion.AVAILABLE:
        return confirmed_mass, 0.0, 1 - confirmed_mass
    return 0.0, confirmed_mass, 1 - confirmed_mass


def _combine(
    m1: tuple[float, float, float], m2: tuple[float, float, float]
) -> tuple[float, float, float, float]:
    """Dempster's rule of combination (Shafer, 1976) for two BPAs over a
    two-hypothesis frame. Returns (m_available, m_unavailable, m_frame, K)
    where K is the conflict mass — probability assigned to the empty set
    before normalization, i.e. how much the two sources actively disagree.
    A fully-conflicting pair (K == 1) is returned as maximal ignorance
    rather than raising, since "signals disagree completely" is itself a
    real, expected outcome (CONFLICTING) — not an error condition."""
    a1, u1, t1 = m1
    a2, u2, t2 = m2
    conflict = a1 * u2 + u1 * a2
    norm = 1 - conflict
    if norm <= 0:
        return 0.0, 0.0, 1.0, 1.0
    combined_a = (a1 * a2 + a1 * t2 + t1 * a2) / norm
    combined_u = (u1 * u2 + u1 * t2 + t1 * u2) / norm
    combined_t = (t1 * t2) / norm
    return combined_a, combined_u, combined_t, conflict


def _combine_confirmed(
    signals: list[EvidenceSignal], confirmed_mass: float
) -> tuple[float, float, float, float]:
    """Combine every CONFIRMED signal's BPA in sequence. Dempster's rule is
    associative and commutative, so combining pairwise in list order and
    accumulating total conflict as `1 - product(1 - K_i)` gives the same
    result as combining all masses at once. An empty or single-signal list
    is the base case: no evidence combined yet means full ignorance and no
    conflict; one signal combined with nothing is just that signal's own
    mass."""
    confirmed = [s for s in signals if s.state is SignalState.CONFIRMED]
    if not confirmed:
        return 0.0, 0.0, 1.0, 0.0

    mass = _signal_mass(confirmed[0], confirmed_mass)
    total_conflict = 0.0
    for signal in confirmed[1:]:
        combined_a, combined_u, combined_t, step_conflict = _combine(
            mass, _signal_mass(signal, confirmed_mass)
        )
        mass = (combined_a, combined_u, combined_t)
        total_conflict = 1 - (1 - total_conflict) * (1 - step_conflict)
    return mass[0], mass[1], mass[2], total_conflict


def reconcile(
    signals: list[EvidenceSignal],
    *,
    confirmed_mass: float = 0.9,
    digital_only_cap: float = 0.75,
) -> Reconciliation:
    """architecture.md §1.4 / signal-fusion-module.md §3: derive an outcome
    label and a numeric confidence value from an already-characterized
    signal set. Every signal's own `state` must already be judged (that
    part is frontier-tier, signal-fusion-module.md §3) — this function only
    combines states that are already known.

    `confirmed_mass` (0.0-1.0) is how much belief a single CONFIRMED signal
    contributes to its own assertion, before combining with any other
    signal — see `_signal_mass`. `digital_only_cap` is signal-fusion-
    module.md §3's explicit discount for **Digital-only, capped confidence**
    ("this outcome is not treated as equivalent to a normal direct-load
    confirmation... recorded with the cap explicit") — a digital-only
    result never reports a confidence above this ceiling, regardless of
    `confirmed_mass`.
    """
    if not (0.0 < confirmed_mass <= 1.0):
        raise ValueError("confirmed_mass must be in (0.0, 1.0]")
    if not (0.0 <= digital_only_cap <= 1.0):
        raise ValueError("digital_only_cap must be between 0.0 and 1.0")

    confirmed = [s for s in signals if s.state is SignalState.CONFIRMED]
    m_available, m_unavailable, _m_frame, conflict = _combine_confirmed(signals, confirmed_mass)

    analog_pending = any(
        s.source is SignalSource.ANALOG and s.state is SignalState.PENDING for s in signals
    )
    digital_confirmed = [s for s in confirmed if _is_digital(s)]
    analog_confirmed = [s for s in confirmed if s.source is SignalSource.ANALOG]

    # Genuine disagreement among confirmed signals — never averaged away
    # (signal-fusion-module.md §1: "a disagreement... is itself a finding").
    if m_available > 0 and m_unavailable > 0:
        return Reconciliation(Outcome.CONFLICTING, confidence=max(0.0, 1 - conflict), conflict_mass=conflict)

    # Every signal in the set agrees, and there's more than one of them.
    if len(confirmed) >= 2:
        return Reconciliation(
            Outcome.CONCORDANT_CONFIRMATION, confidence=max(m_available, m_unavailable), conflict_mass=conflict
        )

    # Exactly one confirmed signal, and it's analog — the digital trace
    # never independently confirmed anything (ambiguous, stale, or absent).
    if len(confirmed) == 1 and analog_confirmed:
        return Reconciliation(
            Outcome.ANALOG_RESOLVED, confidence=max(m_available, m_unavailable), conflict_mass=conflict
        )

    # An analog lead is drafted but execution is still pending a human
    # (architecture.md §1.2's no-irreversible-actions rule) — this fact
    # controls the outcome regardless of whether digital independently
    # confirmed anything yet.
    if analog_pending:
        confidence = max(m_available, m_unavailable) if confirmed else 0.0
        return Reconciliation(Outcome.ANALOG_PENDING, confidence=confidence, conflict_mass=conflict)

    # Exactly one confirmed signal, and it's digital, with no analog
    # confirmation or pending outreach to weigh against it.
    if len(confirmed) == 1 and digital_confirmed:
        capped = min(max(m_available, m_unavailable), digital_only_cap)
        return Reconciliation(Outcome.DIGITAL_ONLY_CAPPED, confidence=capped, conflict_mass=conflict)

    # Nothing confirmed and nothing pending: the escalation ladder
    # (verification-escalation-policy.md §2) has nothing left to try.
    return Reconciliation(Outcome.UNABLE_TO_VERIFY, confidence=0.0, conflict_mass=conflict)
