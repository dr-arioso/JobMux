"""Compensation normalization — architecture.md §1.2.

Pure arithmetic once both cost-of-living index values are already known —
fetching either index value is a reference-data lookup (small-model tier,
architecture.md §2.3), out of scope here.
"""

from __future__ import annotations


def normalize_compensation(
    listing_salary: float,
    listing_col_index: float,
    anchor_col_index: float,
) -> float:
    """Convert a listing's attested salary into anchor-equivalent terms.

    architecture.md §1.2: "the conversion itself — a listing's salary
    multiplied by the ratio of the anchor's cost-of-living index to the
    listing location's — is pure arithmetic once both index values are
    known." Which location is the anchor (a fixed destination, a
    location-agnostic reference index, or the candidate's current
    location) is decided upstream of this function, by how the geography
    decision node resolved — this function only does the ratio math.
    """
    if listing_col_index <= 0 or anchor_col_index <= 0:
        raise ValueError("cost-of-living index values must be positive")
    if listing_salary < 0:
        raise ValueError("listing_salary must be non-negative")
    return listing_salary * (anchor_col_index / listing_col_index)
