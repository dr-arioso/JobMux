"""JobMux algorithmic tier — architecture.md §2.3.

Every function in this package is deterministic, pure, and runs as literal
code, never a model call — architecture.md §2.3's own dividing line: "no
model call needed... implemented as literal deterministic code run via the
execution sandbox, never as a model call asked to perform arithmetic or
lookup." This is what keeps the tier distinction real rather than
aspirational.

Status: first real code in this repo (decisions/0002-build-sequencing-strategy.md,
action item 1). Everything else so far — elicitation.md, the evidence-gathering
modules, the verification/escalation policy — is prose a model follows at
runtime, not software. See jobmux/README.md for module map and open flags.
"""

from jobmux.compensation import normalize_compensation
from jobmux.context_pack import (
    Event,
    EventType,
    SessionState,
    build_context_pack,
    fold,
)
from jobmux.reallocation import ReallocationStrategy, reallocate
from jobmux.scheduling import (
    CandidateAction,
    VolatilityTier,
    next_recheck_date,
    order_by_information_gain_per_cost,
    select_within_budget,
)
from jobmux.scoring import (
    QualificationCheck,
    QualificationKind,
    QualificationResult,
    ScoredPriority,
    chebyshev_weighted_score,
    qualification_completion,
    weighted_sum_score,
)
from jobmux.tournament import PairwiseResult, bradley_terry_scores
from jobmux.verification import (
    ConstraintKind,
    LedgerDiff,
    NearMiss,
    ThresholdDirection,
    diff_ledger_value,
    is_listing_stale,
    refilter_near_misses,
)

__all__ = [
    "normalize_compensation",
    "Event",
    "EventType",
    "SessionState",
    "build_context_pack",
    "fold",
    "ReallocationStrategy",
    "reallocate",
    "CandidateAction",
    "VolatilityTier",
    "next_recheck_date",
    "order_by_information_gain_per_cost",
    "select_within_budget",
    "QualificationCheck",
    "QualificationKind",
    "QualificationResult",
    "ScoredPriority",
    "chebyshev_weighted_score",
    "qualification_completion",
    "weighted_sum_score",
    "PairwiseResult",
    "bradley_terry_scores",
    "ConstraintKind",
    "LedgerDiff",
    "NearMiss",
    "ThresholdDirection",
    "diff_ledger_value",
    "is_listing_stale",
    "refilter_near_misses",
]
