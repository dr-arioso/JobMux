"""Verification — architecture.md §1.3 (staleness dates, ledger diffing)
and §1.2 (near-miss re-filtering, false-positive exclusion matching).

Every function here is deliberately narrow and mechanical. The actual
judgment calls in verification-escalation-policy.md — which escalation
step to run, whether a signal is trustworthy enough to record, how to
reconcile conflicting signals — stay frontier-tier (architecture.md §2.3)
and out of scope here; this module only implements the parts architecture
doc §2.3 explicitly calls algorithmic.

False-positive matching revised per `decisions/0003-attribute-
reconciliation-and-false-positive-matching.md` (action items 1-2): word-
boundary + optional fuzzy matching on normalized text (fixing a real
precision bug in the original plain-substring version), plus a
schema.org-`occupationalCategory`/SOC-code path that's checked first when
a listing's structured data supplies one. Confirming that a given result
actually *is* a false positive stays frontier-tier regardless of which
matching mechanism is used — unchanged by this revision.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from difflib import SequenceMatcher
from enum import Enum
from typing import Any


def is_listing_stale(closing_date: date, as_of: date) -> bool:
    """architecture.md §1.3: "always read the date field, don't trust that
    a page loading means it's current." Pure comparison — does not fetch
    or render anything; the caller supplies an already-located date field
    from an already-loaded page (verification-escalation-policy.md §1's
    signal/finding discipline applies to obtaining that date, not to this
    function)."""
    return closing_date < as_of


@dataclass(frozen=True)
class LedgerDiff:
    changed: bool
    old_value: Any
    new_value: Any


def diff_ledger_value(old_value: Any, new_value: Any) -> LedgerDiff:
    """architecture.md §1.4: "diffing an old ledger value against a new one
    to decide what gets flagged as changed." This is the mechanical half
    of "status changes are revised in place with visible prior-value
    history, never silently deleted" — recording `old_value` as the
    ledger's `prior_status` field is the caller's job, not this
    function's."""
    return LedgerDiff(changed=old_value != new_value, old_value=old_value, new_value=new_value)


class ConstraintKind(Enum):
    THRESHOLD = "threshold"
    QUALIFICATION = "qualification"
    MANDATORY = "mandatory"


class ThresholdDirection(Enum):
    MINIMUM = "minimum"  # value must be >= required_value to pass (e.g. a salary floor)
    MAXIMUM = "maximum"  # value must be <= required_value to pass (e.g. a commute ceiling)


@dataclass(frozen=True)
class NearMiss:
    """A rejected listing tagged with which constraint it failed and by
    how much (architecture.md §1.2, adaptive-module.md §7)."""
    listing_id: str
    failed_constraint_name: str
    failed_constraint_kind: ConstraintKind
    failed_value: float
    required_value: float
    direction: ThresholdDirection = ThresholdDirection.MINIMUM


def refilter_near_misses(
    near_misses: list[NearMiss],
    changed_constraint_name: str,
    new_required_value: float,
) -> list[str]:
    """Given a changed threshold or qualification requirement, return the
    listing_ids of near-misses that would now pass — cheaply resurrecting
    them from cache rather than forcing a full re-search (architecture.md
    §1.2).

    Only THRESHOLD- and QUALIFICATION-kind near-misses are re-checkable
    this way, where "passing" is well-defined as `failed_value` clearing
    `new_required_value`. A MANDATORY (target-match) near-miss has no
    partial-credit continuum to re-check against a numeric value — it
    either stays rejected, or the mandatory flag itself was removed
    entirely, which is a different, larger operation than a numeric
    threshold change and out of scope for this function.
    """
    resurrected = []
    for nm in near_misses:
        if nm.failed_constraint_name != changed_constraint_name:
            continue
        if nm.failed_constraint_kind is ConstraintKind.MANDATORY:
            continue
        if nm.direction is ThresholdDirection.MINIMUM:
            passes = nm.failed_value >= new_required_value
        else:
            passes = nm.failed_value <= new_required_value
        if passes:
            resurrected.append(nm.listing_id)
    return resurrected


def _normalize(text: str) -> str:
    """Lowercase and collapse punctuation/whitespace to single spaces, so
    matching (decisions/0003) is robust to trailing periods, hyphens, and
    extra whitespace instead of only exact substring containment."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _tokens(text: str) -> list[str]:
    normalized = _normalize(text)
    return normalized.split() if normalized else []


def _contains_phrase(haystack_tokens: list[str], pattern_tokens: list[str]) -> bool:
    """Word-boundary containment: true only if `pattern_tokens` appears as
    a contiguous run of *whole* tokens inside `haystack_tokens`. This is
    what actually fixes decisions/0003's "aid matches inside maid" bug —
    plain substring containment on unnormalized text has no concept of a
    word boundary at all."""
    n, m = len(haystack_tokens), len(pattern_tokens)
    if m == 0 or m > n:
        return False
    return any(haystack_tokens[i : i + m] == pattern_tokens for i in range(n - m + 1))


def _fuzzy_phrase_match(
    haystack_tokens: list[str],
    pattern_tokens: list[str],
    *,
    threshold: float,
    min_pattern_length: int,
) -> bool:
    """decisions/0003's "light fuzzy tolerance" for phrasing drift
    ("Environmental Svcs" vs. "Environmental Services") — slides a
    same-length window across `haystack_tokens` and compares each window's
    joined text against the pattern via `difflib.SequenceMatcher.ratio()`
    (the standard library's Ratcliff/Obershelp string-similarity
    implementation), rather than reaching for a new fuzzy-matching
    dependency.

    `min_pattern_length` is a deliberate guard, not an incidental detail:
    a short pattern's similarity ratio against an unrelated word that
    happens to contain it as a substring can itself clear a plausible-
    looking threshold — `SequenceMatcher(None, "aid", "maid").ratio()` is
    ~0.857, *higher* than `SequenceMatcher(None, "environmental services",
    "environmental svc").ratio()` at ~0.872 is only barely above. Fuzzy
    tolerance on very short patterns would silently reintroduce the exact
    bug it exists to fix. A pattern shorter than this is only ever matched
    exactly, via `_contains_phrase`, never fuzzily.
    """
    pattern_text = " ".join(pattern_tokens)
    if len(pattern_text) < min_pattern_length:
        return False
    m, n = len(pattern_tokens), len(haystack_tokens)
    if m == 0 or m > n:
        return False
    return any(
        SequenceMatcher(None, pattern_text, " ".join(haystack_tokens[i : i + m])).ratio() >= threshold
        for i in range(n - m + 1)
    )


@dataclass(frozen=True)
class FalsePositivePattern:
    """A confirmed category-error exclusion (architecture.md §1.2) — not a
    near-miss, a listing that was never a legitimate candidate for this
    search at all (the canonical case: a hospital's "Environmental
    Services" posting surfacing under an environmental-science search).

    Confirming that a given result actually *is* a false positive, rather
    than a genuine (if unusual) near-miss, is frontier-tier judgment
    (architecture.md §2.3) and out of scope for this module. What's
    algorithmic, and implemented below, is matching listings against a
    pattern once it's already been confirmed.

    `field` is "title" or "employer"; `pattern` is matched against that
    field on normalized (lowercased, punctuation-collapsed) text, requiring
    a whole-word-boundary match, with an optional fuzzy fallback for
    phrasing drift (decisions/0003) — revised from the original plain
    case-insensitive substring containment, which had a real precision bug
    (a pattern like "aid" matched inside "maid"). This remains a first
    instantiation of the matching mechanism, not a settled decision —
    SOC-code alignment (`OccupationalCategoryExclusion` below) is the
    stronger signal when a listing's structured data supplies one; this
    text-based mechanism is the fallback for when it doesn't."""
    pattern: str
    field: str
    reason: str
    added_at: date


def is_confirmed_false_positive(
    listing_title: str,
    listing_employer: str,
    patterns: list[FalsePositivePattern],
    *,
    fuzzy_threshold: float = 0.85,
    min_fuzzy_pattern_length: int = 6,
) -> FalsePositivePattern | None:
    """Return the first matching pattern, or None if the listing matches
    none of them. Never persisted as a NearMiss regardless of match — a
    false positive is excluded from the tracking store entirely, not
    tagged and kept (architecture.md §1.2).

    `fuzzy_threshold` and `min_fuzzy_pattern_length` are exposed rather
    than hardcoded, the same spirit as this codebase's other
    first-instantiation constants (scoring.py's `top_k`/`lambda_`,
    signal_fusion.py's `conflict_threshold`) — pass `fuzzy_threshold=1.0`
    to disable fuzzy matching entirely and fall back to exact
    word-boundary containment only.
    """
    title_tokens = _tokens(listing_title)
    employer_tokens = _tokens(listing_employer)
    for fp in patterns:
        haystack_tokens = title_tokens if fp.field == "title" else employer_tokens
        pattern_tokens = _tokens(fp.pattern)
        if _contains_phrase(haystack_tokens, pattern_tokens):
            return fp
        if fuzzy_threshold < 1.0 and _fuzzy_phrase_match(
            haystack_tokens,
            pattern_tokens,
            threshold=fuzzy_threshold,
            min_pattern_length=min_fuzzy_pattern_length,
        ):
            return fp
    return None


def purge_false_positives(
    listings: list[tuple[str, str, str]],
    patterns: list[FalsePositivePattern],
    *,
    fuzzy_threshold: float = 0.85,
    min_fuzzy_pattern_length: int = 6,
) -> list[str]:
    """architecture.md §1.2: a confirmed false-positive pattern is "applied
    retroactively to purge anything already in the cache matching the
    pattern." `listings` is a list of (listing_id, title, employer)
    tuples; returns the listing_ids that match and should be purged.

    The actual purge (deleting or tombstoning the row) is the caller's
    job, not this function's — the same division of responsibility as
    diff_ledger_value above: this module computes what changed, the caller
    applies it to the real tracking store."""
    return [
        listing_id
        for listing_id, title, employer in listings
        if is_confirmed_false_positive(
            title,
            employer,
            patterns,
            fuzzy_threshold=fuzzy_threshold,
            min_fuzzy_pattern_length=min_fuzzy_pattern_length,
        )
        is not None
    ]


@dataclass(frozen=True)
class OccupationalCategoryExclusion:
    """decisions/0003, Issue 2 Option B: a confirmed false-positive keyed
    by SOC code rather than text pattern. schema.org's
    `JobPosting.occupationalCategory` property is recommended by
    schema.org's own spec to hold an O*NET-SOC code (architecture.md §1.6
    already adopts SOC as this project's occupation vocabulary) — when a
    listing's structured data actually supplies one, comparing it directly
    against a confirmed exclusion list is stronger evidence than any
    text-based matching, since it isn't inferring a category from free-text
    phrasing at all."""
    soc_code: str
    reason: str
    added_at: date


def is_excluded_by_occupational_category(
    listing_soc_code: str | None,
    exclusions: list[OccupationalCategoryExclusion],
) -> OccupationalCategoryExclusion | None:
    """Direct SOC-code comparison — no text matching involved. Returns
    `None` both when nothing matches *and* when `listing_soc_code` is
    `None`: a listing's structured data not supplying a code is not
    evidence either way, not grounds to treat it as clear. The caller
    falls back to `is_confirmed_false_positive`'s text-based matching in
    that case (decisions/0003), rather than skipping the check entirely."""
    if listing_soc_code is None:
        return None
    for exclusion in exclusions:
        if exclusion.soc_code == listing_soc_code:
            return exclusion
    return None


def is_confirmed_false_positive_with_category(
    listing_title: str,
    listing_employer: str,
    listing_soc_code: str | None,
    text_patterns: list[FalsePositivePattern],
    category_exclusions: list[OccupationalCategoryExclusion],
    *,
    fuzzy_threshold: float = 0.85,
    min_fuzzy_pattern_length: int = 6,
) -> FalsePositivePattern | OccupationalCategoryExclusion | None:
    """decisions/0003: check the structured-data signal first when a
    listing supplies one (a direct classification, not an inference from
    free text), then check text patterns regardless — a SOC-code match is
    stronger evidence than a text match, but a listing carrying a SOC code
    that isn't yet on the exclusion list can still be caught by an
    existing text pattern, so the text check is never skipped just
    because a code happened to be present."""
    if listing_soc_code is not None:
        by_category = is_excluded_by_occupational_category(listing_soc_code, category_exclusions)
        if by_category is not None:
            return by_category
    return is_confirmed_false_positive(
        listing_title,
        listing_employer,
        text_patterns,
        fuzzy_threshold=fuzzy_threshold,
        min_fuzzy_pattern_length=min_fuzzy_pattern_length,
    )


def purge_false_positives_with_category(
    listings: list[tuple[str, str, str, str | None]],
    text_patterns: list[FalsePositivePattern],
    category_exclusions: list[OccupationalCategoryExclusion],
    *,
    fuzzy_threshold: float = 0.85,
    min_fuzzy_pattern_length: int = 6,
) -> list[str]:
    """As `purge_false_positives`, but each `listings` row carries a fourth
    element — the listing's schema.org `occupationalCategory` SOC code, or
    `None` when its structured data doesn't supply one (decisions/0003)."""
    return [
        listing_id
        for listing_id, title, employer, soc_code in listings
        if is_confirmed_false_positive_with_category(
            title,
            employer,
            soc_code,
            text_patterns,
            category_exclusions,
            fuzzy_threshold=fuzzy_threshold,
            min_fuzzy_pattern_length=min_fuzzy_pattern_length,
        )
        is not None
    ]
