"""Signal fusion — architecture.md §1.4's evidence-signal-set reconciliation,
instantiated for signal-fusion-module.md §3's six named outcomes.

architecture.md §1.4: "characterize the set as concordant (agreeing confirmed
signals) or discordant (disagreeing confirmed signals), then derive two things
from that characterization — a human-readable outcome label... and a numeric
confidence value." Both are algorithmic-tier (§2.3) once every signal's own
state is already known — judging what state an individual signal deserves
stays frontier-tier and out of scope for this module, exactly like
verification.py's FalsePositivePattern confirmation and near-miss tagging.

Revision (2026-07-25, second pass — design discussion, not this module's own
initiative). The first version of this module was quietly lossy in a way
that runs against the project's own persistence discipline (architecture.md
§2.4: "structurally impossible to lose a prior value") and against the
JobMux name itself — a multiplexer combines channels, it doesn't discard
them. Two changes follow from that discussion:

1. **CONTRADICTED renamed to SUPERSEDED, and narrowed.** The original
   CONTRADICTED state conflated two different things: a signal directly,
   self-refuted by re-examining that *same* source (a page's own date field
   proving it's past due) versus a signal merely outweighed by a
   *different* source's disagreeing claim (an aggregator's mirrored closing
   date vs. the employer's own, more recently edited page). SUPERSEDED now
   covers only the first case — a signal retired by a *later reading from
   the same `source`*, matched by that source's own stable ID for the
   listing (architecture.md §1.4's own ledger field already calls for one).
   A real wrinkle this rename doesn't resolve on its own: a repost of the
   same underlying opening sometimes gets reissued a brand-new ID by the
   aggregator, so "same ID" isn't an airtight test on its own — telling a
   genuine repost from a supersession of the same posting can itself need
   judgment. A signal retired this way is safe to fully exclude from
   combination: it isn't independent evidence being discarded, it's an
   outdated reading of the *same* channel being replaced by that channel's
   own newer reading — including both would double-count one source, not
   add a second one. Two *different* sources that simply disagree are
   never superseded this way; both stay CONFIRMED and are reconciled via
   discounting (below), never by unilaterally retiring the one judged less
   authoritative.

2. **Per-signal `reliability` (Shafer discounting) replaces the flat
   `digital_only_cap`.** The first version applied one hardcoded confidence
   ceiling to any lone digital confirmation, regardless of how trustworthy
   that specific signal actually was — which meant a disagreement from a
   less-authoritative source either got fully counted or fully discarded,
   nothing in between. `EvidenceSignal` now carries a `reliability`
   coefficient (0.0-1.0, default 1.0), applied via Shafer's own discounting
   operation (Shafer, 1976, ch. 11) before a signal's mass enters
   combination: the discounted mass is `reliability x` the signal's raw
   mass, with the discounted-away belief folded into ignorance (the full
   frame), never into the opposing hypothesis. A less-trusted source still
   contributes real evidentiary mass; it's weighted down, not zeroed, and
   any disagreement it carries still shows up in the combined result
   rather than vanishing. Judging what reliability a given signal deserves
   is frontier-tier work, same as judging its state (architecture.md §1.4,
   §2.3) — this module never assigns reliability itself, only combines
   whatever value it's given. This also relocates where "a digital trace of
   this module's own trigger shapes is a weak proxy" (signal-fusion-
   module.md §0) gets encoded: it's now the frontier-tier judgment's job to
   assign such a signal a reliability below 1.0 when tagging it CONFIRMED,
   not this module's job to discount it afterward by source type.

   One consequence: with every disagreeing signal now contributing some
   discounted mass rather than being all-or-nothing included, a strict "any
   mass on both sides" test would flag nearly every real disagreement as
   CONFLICTING, however lopsided the discount. `reconcile()` now takes a
   `conflict_threshold` instead — only once the *minority* hypothesis's
   mass clears that threshold does the disagreement get reported as
   CONFLICTING; below it, the majority hypothesis's own combined belief
   (already reduced by whatever residual disagreement survived) is
   reported as confidence, the same as any other outcome. Concordance, per
   architecture.md §1.4's "characterize the set as concordant... or
   discordant," is evaluated on this reliability-weighted combined
   evidence, not on whether every individual signal's raw assertion happens
   to match literally — a heavily-discounted lone dissent doesn't prevent
   an otherwise-decisive set from being characterized as concordant, it
   just measurably (if slightly) lowers the confidence value under that
   label, which is exactly the "weighted, not discarded" property this
   revision was for.

   Every branch now reports confidence the same way — max(m_available,
   m_unavailable) from the actual combined masses — rather than a
   per-outcome formula, so the six labels differ in *when* they apply,
   never in *how* the number under them is computed.

A persistence note carried over from this discussion but not this module's
own job to enforce: every *salient* signal a source produces — everything
not already purged by the false-positive exclusion registry (architecture.md
§1.2, verification.py's confirmed-category-error purge) — belongs in the
tracking ledger regardless of what reconcile() concludes about it. A
discounted, outvoted, or superseded signal doesn't stop existing in the
record; it just contributed less (or, if superseded, nothing) to one
combined number. reconcile() itself never mutates or drops anything from
the list it's given — that discipline has to hold one layer up, in
whatever writes the ledger.
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
    """architecture.md §1.4's per-signal state vocabulary. SUPERSEDED
    (module docstring, revision 1) replaces the earlier CONTRADICTED,
    narrowed to a signal retired by a *later reading from the same
    source* — never by a different source's disagreeing claim, which
    stays CONFIRMED on both sides and is reconciled via discounting
    instead. PENDING is signal-fusion-module.md §3's "identified and
    drafted but not yet executed" — the no-irreversible-actions rule
    (architecture.md §1.2) means AnalogSearch's outreach is handed to the
    candidate, not run by the system, so a real gap in time can sit at
    this state."""
    CONFIRMED = "confirmed"
    SUPERSEDED = "superseded"
    PENDING = "pending"
    UNABLE_TO_OBTAIN = "unable-to-obtain"


class Assertion(Enum):
    """Not part of architecture.md §1.4's literal `(source, state,
    timestamp or quoted basis)` schema — added here to make "agreeing" vs.
    "disagreeing" computable. See jobmux/README.md's open-flags section."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class EvidenceSignal:
    """One tagged entry in architecture.md §1.4's open evidence-signal set.

    `reliability` (0.0-1.0, default 1.0) is this specific signal's Shafer
    discounting coefficient (module docstring, revision 2) — how much of
    the generic `confirmed_mass` ceiling (see `reconcile()`) this
    particular signal actually earns, as judged by whoever assigned its
    state. Only consulted for CONFIRMED signals; harmless but inert on
    every other state.

    `basis` holds the quoted basis or timestamp architecture.md §1.4's
    schema calls for; this module doesn't parse or compare it — recency
    and specificity judgments are frontier-tier (signal-fusion-module.md
    §1) and already baked into `state`, `assertion`, and `reliability` by
    the time a signal reaches this module.
    """
    source: SignalSource
    state: SignalState
    assertion: Assertion | None = None
    reliability: float = 1.0
    basis: str = ""

    def __post_init__(self) -> None:
        needs_assertion = self.state in (SignalState.CONFIRMED, SignalState.SUPERSEDED)
        if needs_assertion and self.assertion is None:
            raise ValueError(f"a {self.state.value} signal must carry an assertion")
        if not needs_assertion and self.assertion is not None:
            raise ValueError(f"a {self.state.value} signal cannot yet carry an assertion")
        if not (0.0 <= self.reliability <= 1.0):
            raise ValueError("reliability must be between 0.0 and 1.0")


class Outcome(Enum):
    """signal-fusion-module.md §3's six named outcomes — "worked examples of
    the general model's output, not a separate closed enumeration of their
    own" (architecture.md §1.4), but the fixed vocabulary this module's
    reconcile() actually returns. DIGITAL_ONLY_CAPPED keeps its name from
    that decided vocabulary even though this revision replaces the
    hardcoded confidence cap it originally implied with per-signal
    `reliability` — "capped" now describes the outcome's meaning (only one
    channel ever weighed in), not a fixed ceiling this module enforces."""
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
    that drove (or, below `conflict_threshold`, didn't drive) a CONFLICTING
    outcome, kept for anyone reviewing the row later rather than discarded
    once the label is chosen."""
    outcome: Outcome
    confidence: float
    conflict_mass: float


def _is_digital(signal: EvidenceSignal) -> bool:
    return signal.source in DIGITAL_SOURCES


def _signal_mass(signal: EvidenceSignal, confirmed_mass: float) -> tuple[float, float, float]:
    """A single CONFIRMED signal's basic probability assignment (BPA) over
    {available}, {unavailable}, and the full frame (residual ignorance) —
    returned as (m_available, m_unavailable, m_frame).

    `confirmed_mass` is the generic ceiling any single direct confirmation
    can contribute to its own assertion before any per-signal discount is
    applied; `signal.reliability` is that discount (Shafer, 1976) — the
    effective mass is `confirmed_mass * signal.reliability`, with the
    remainder left as ignorance, never assigned to the opposite hypothesis,
    since a confirmed-but-discounted signal says nothing *against* the
    alternative — it just doesn't rule out being wrong, more so than a
    fully-trusted signal would."""
    mass = confirmed_mass * signal.reliability
    if signal.assertion is Assertion.AVAILABLE:
        return mass, 0.0, 1 - mass
    return 0.0, mass, 1 - mass


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
    """Combine every CONFIRMED signal's (already reliability-discounted)
    BPA in sequence. Dempster's rule is associative and commutative, so
    combining pairwise in list order and accumulating total conflict as
    `1 - product(1 - K_i)` gives the same result as combining all masses
    at once. An empty or single-signal list is the base case: no evidence
    combined yet means full ignorance and no conflict; one signal combined
    with nothing is just that signal's own mass."""
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
    conflict_threshold: float = 0.1,
) -> Reconciliation:
    """architecture.md §1.4 / signal-fusion-module.md §3: derive an outcome
    label and a numeric confidence value from an already-characterized
    signal set. Every signal's own `state`, `assertion`, and `reliability`
    must already be judged (that part is frontier-tier, signal-fusion-
    module.md §3) — this function only combines values that are already
    known. A SUPERSEDED signal contributes nothing (module docstring,
    revision 1) — it's a same-source signal already replaced by a newer
    reading of that same source, not independent evidence to weigh.

    `confirmed_mass` (0.0-1.0] is the generic ceiling a single, fully-
    reliable CONFIRMED signal contributes to its own assertion, before any
    per-signal `reliability` discount. `conflict_threshold` (0.0-1.0) is
    how much residual mass the *minority* hypothesis has to retain, after
    every signal's own reliability discount is applied, before the set is
    reported as CONFLICTING rather than resolved with reduced confidence —
    see the module docstring's revision 2 for why a plain nonzero check
    would flag nearly every real disagreement once discounting is in play.
    """
    if not (0.0 < confirmed_mass <= 1.0):
        raise ValueError("confirmed_mass must be in (0.0, 1.0]")
    if not (0.0 <= conflict_threshold <= 1.0):
        raise ValueError("conflict_threshold must be between 0.0 and 1.0")

    confirmed = [s for s in signals if s.state is SignalState.CONFIRMED]
    m_available, m_unavailable, _m_frame, conflict = _combine_confirmed(signals, confirmed_mass)
    confidence = max(m_available, m_unavailable)

    analog_pending = any(
        s.source is SignalSource.ANALOG and s.state is SignalState.PENDING for s in signals
    )
    digital_confirmed = [s for s in confirmed if _is_digital(s)]
    analog_confirmed = [s for s in confirmed if s.source is SignalSource.ANALOG]

    # Genuine, non-trivial disagreement among confirmed signals — never
    # averaged away (signal-fusion-module.md §1: "a disagreement... is
    # itself a finding"). Both sides must have actually confirmed something
    # (not just be near-zero from an empty combination), and the minority
    # side's mass must clear the threshold to count as meaningful conflict
    # rather than a discounted dissent that lost.
    if m_available > 0 and m_unavailable > 0 and min(m_available, m_unavailable) >= conflict_threshold:
        return Reconciliation(Outcome.CONFLICTING, confidence=confidence, conflict_mass=conflict)

    # The confirmed evidence, taken together, decisively favors one
    # hypothesis, and more than one signal contributed to that.
    if len(confirmed) >= 2:
        return Reconciliation(Outcome.CONCORDANT_CONFIRMATION, confidence=confidence, conflict_mass=conflict)

    # Exactly one confirmed signal, and it's analog — the digital trace
    # never independently confirmed anything (ambiguous, superseded, or
    # absent).
    if len(confirmed) == 1 and analog_confirmed:
        return Reconciliation(Outcome.ANALOG_RESOLVED, confidence=confidence, conflict_mass=conflict)

    # An analog lead is drafted but execution is still pending a human
    # (architecture.md §1.2's no-irreversible-actions rule) — this fact
    # controls the outcome regardless of whether digital independently
    # confirmed anything yet.
    if analog_pending:
        return Reconciliation(Outcome.ANALOG_PENDING, confidence=confidence, conflict_mass=conflict)

    # Exactly one confirmed signal, and it's digital, with no analog
    # confirmation or pending outreach to weigh against it.
    if len(confirmed) == 1 and digital_confirmed:
        return Reconciliation(Outcome.DIGITAL_ONLY_CAPPED, confidence=confidence, conflict_mass=conflict)

    # Nothing confirmed and nothing pending: the escalation ladder
    # (verification-escalation-policy.md §2) has nothing left to try.
    return Reconciliation(Outcome.UNABLE_TO_VERIFY, confidence=confidence, conflict_mass=conflict)
