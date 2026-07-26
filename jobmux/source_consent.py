"""Source consent — decisions/0004 action item 3.

ADR-0004 decided that JobMux never silently includes or excludes
`ats-scrapers`' ToS-ambiguous "big-tech custom careers systems" bucket
(Meta, Tesla, Apple, Amazon, Google, ByteDance, TikTok, Uber) — the
candidate answers a one-time consent question
(`reference/board-heuristic-module.md` §3), and their answer is enforced
mechanically from then on. This module is that mechanical enforcement,
deliberately shaped like `verification.py`'s `OccupationalCategoryExclusion`
pattern rather than invented from scratch (ADR-0004 action item 3 names
that pattern explicitly as the intended shape).

Confirming *which* sources are ToS-ambiguous in the first place is a
recorded, human-reviewed decision (ADR-0004), not something this module
computes — matching this module against a listing's source is algorithmic
(architecture.md §2.3); deciding the exclusion list's membership was not.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SourceConsentExclusion:
    """One candidate's "exclude" answer to the ToS-ambiguous-source consent
    question (`reference/board-heuristic-module.md` §3), recorded as live,
    revisable state (architecture.md §1.1) — not a global, candidate-
    independent policy. `excluded_sources` names the specific source
    identifiers this candidate opted to exclude (ADR-0004's big-tech bucket
    by default, but recorded as an explicit list rather than a hardcoded
    constant so a future session isn't forced to touch this module's code
    just to adjust which sources the question covers)."""

    excluded_sources: frozenset[str]
    reason: str
    recorded_at: date


#: ADR-0004's own ToS-ambiguous bucket, as source identifiers matching
#: `ats-scrapers`' `ATSType` values for the "big-tech custom careers
#: systems" group. Exposed as a named default so a caller building a
#: `SourceConsentExclusion` from the candidate's "yes, exclude" answer
#: doesn't have to re-type the list, without forcing every future
#: candidate to necessarily get the same set — `excluded_sources` on the
#: exclusion itself is still the actual source of truth at match time.
ADR_0004_TOS_AMBIGUOUS_SOURCES: frozenset[str] = frozenset(
    {"meta", "tesla", "apple", "amazon", "google", "bytedance", "tiktok", "uber"}
)


def is_excluded_by_source_consent(
    listing_source: str | None,
    exclusion: SourceConsentExclusion | None,
) -> bool:
    """True if `listing_source` is on this candidate's consent-driven
    exclusion list. Returns `False` (never excluded) when either
    `listing_source` or `exclusion` is `None` — no consent answer on file
    is not itself grounds to exclude anything (ADR-0004: silence isn't a
    default toward exclusion any more than it's a default toward
    inclusion; the candidate has to actually be asked and actually
    answer). Matching is case-insensitive since ATS-type identifiers are
    conventionally lowercase but callers may pass either case through."""
    if listing_source is None or exclusion is None:
        return False
    return listing_source.lower() in exclusion.excluded_sources


def purge_by_source_consent(
    listings: list[tuple[str, str]],
    exclusion: SourceConsentExclusion | None,
) -> list[str]:
    """`listings` is a list of (listing_id, source) tuples. Returns the
    listing_ids that should be purged under this candidate's consent
    answer — the same division of labor as `verification.py`'s purge
    functions: this computes what changed, the caller applies it to the
    real tracking store. Consistent with architecture.md §1.2's exclusion-
    registry discipline: this purges prospectively and retroactively the
    same way a confirmed false-positive pattern does, since a "yes,
    exclude" consent answer is itself a confirmed, permanent-until-revised
    exclusion criterion, not a per-listing near-miss judgment call."""
    if exclusion is None:
        return []
    return [
        listing_id
        for listing_id, source in listings
        if is_excluded_by_source_consent(source, exclusion)
    ]
