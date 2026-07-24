"""Context pack — architecture.md §2.2.

A context pack is "a single canonical object per session revision,
computed as a fold over the §2.4 event log and regenerated whenever that
fold changes... never on a fixed timer." This module implements the fold
(event log → current live state) and the serializer that shapes that
state into the exact JSON contract architecture.md §2.2 fixes as decided.
(The context-pack *contract* is decided; the underlying recombination/
tracking *schema* — architecture.md's step (d), not yet written — is a
separate, still-open decision this module doesn't preempt.)

Two disciplines architecture.md §2.2 states should be structural, not just
instructional, and this implementation preserves both as real validation
rather than a comment:
  - `inferable_schema` must be empty for any pack built for a small-model-
    tier subagent — inferable-attribute tagging requires a quoted basis
    and is frontier-tier only (architecture.md §2.3).
  - `active_priorities` only ever includes live, not-critical-excluded
    priorities — a subagent never spends extraction effort on a dimension
    nobody's scoring against (architecture.md §1.5's cost-awareness
    applied as pack-trimming).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventType(Enum):
    PRIORITY_UPSERT = "priority_upsert"
    PRIORITY_THRESHOLD_SET = "priority_threshold_set"
    PRIORITY_MANDATORY_SET = "priority_mandatory_set"
    PRIORITY_WEIGHT_SET = "priority_weight_set"
    PRIORITY_NOT_CRITICAL_SET = "priority_not_critical_set"
    QUALIFICATION_UPSERT = "qualification_upsert"
    CATEGORY_FILTER_UPDATED = "category_filter_updated"


@dataclass(frozen=True)
class Event:
    """One immutable entry in the append-only event log (architecture.md
    §2.4). `payload` keys required per event_type:
      PRIORITY_UPSERT: name, dimension, shape, (weight)
      PRIORITY_THRESHOLD_SET: name, threshold
      PRIORITY_MANDATORY_SET: name, mandatory
      PRIORITY_WEIGHT_SET: name, weight
      PRIORITY_NOT_CRITICAL_SET: name, not_critical
      QUALIFICATION_UPSERT: name, type, (floor)
      CATEGORY_FILTER_UPDATED: name, acceptable_set, ranking
    """
    seq: int
    event_type: EventType
    payload: dict[str, Any]


@dataclass
class _PriorityState:
    name: str
    dimension: str
    shape: str
    threshold: dict | None = None
    mandatory: bool = False
    not_critical: bool = False
    weight: float = 0.0


@dataclass
class SessionState:
    priorities: dict[str, _PriorityState] = field(default_factory=dict)
    qualifications: dict[str, dict[str, Any]] = field(default_factory=dict)
    category_filters: dict[str, dict[str, Any]] = field(default_factory=dict)
    last_seq: int = 0


def fold(events: list[Event]) -> SessionState:
    """Reduce an ordered event log into current live state.

    Events are applied in ascending `seq` order regardless of the order
    they're passed in — the log's sequence numbers are the source of
    truth, not whatever order a caller happens to iterate them in.
    """
    state = SessionState()
    for event in sorted(events, key=lambda e: e.seq):
        _apply(state, event)
        state.last_seq = event.seq
    return state


def _apply(state: SessionState, event: Event) -> None:
    p = event.payload
    if event.event_type is EventType.PRIORITY_UPSERT:
        state.priorities[p["name"]] = _PriorityState(
            name=p["name"],
            dimension=p["dimension"],
            shape=p["shape"],
            weight=p.get("weight", 0.0),
        )
    elif event.event_type is EventType.PRIORITY_THRESHOLD_SET:
        _priority(state, p["name"]).threshold = p.get("threshold")
    elif event.event_type is EventType.PRIORITY_MANDATORY_SET:
        _priority(state, p["name"]).mandatory = p["mandatory"]
    elif event.event_type is EventType.PRIORITY_WEIGHT_SET:
        _priority(state, p["name"]).weight = p["weight"]
    elif event.event_type is EventType.PRIORITY_NOT_CRITICAL_SET:
        _priority(state, p["name"]).not_critical = p["not_critical"]
    elif event.event_type is EventType.QUALIFICATION_UPSERT:
        state.qualifications[p["name"]] = {k: v for k, v in p.items() if k != "name"}
    elif event.event_type is EventType.CATEGORY_FILTER_UPDATED:
        state.category_filters[p["name"]] = {
            "acceptable_set": p["acceptable_set"],
            "ranking": p["ranking"],
        }
    else:  # pragma: no cover - exhaustive Enum guard
        raise ValueError(f"Unknown event type: {event.event_type}")


def _priority(state: SessionState, name: str) -> _PriorityState:
    if name not in state.priorities:
        raise KeyError(
            f"Cannot edit priority {name!r} before it exists — expected a "
            "PRIORITY_UPSERT event first"
        )
    return state.priorities[name]


def build_context_pack(
    state: SessionState,
    *,
    pack_id: str,
    session_id: str,
    generated_at: str,
    attested_schema: list[str],
    reference_anchors: dict[str, Any],
    discovery_context: dict[str, Any],
    near_miss_vocabulary: dict[str, Any],
    forbidden_scope: str,
    inferable_schema: list[str] | None = None,
    aptitudes_requested: list[str] | None = None,
    small_model_tier: bool = False,
) -> dict[str, Any]:
    """Shape folded state into architecture.md §2.2's exact JSON contract.

    Raises if `small_model_tier` is True and `inferable_schema` is
    non-empty — a pack built for a small-model call structurally can't
    hand it a task it isn't allowed to attempt.
    """
    inferable_schema = list(inferable_schema or [])
    if small_model_tier and inferable_schema:
        raise ValueError(
            "inferable_schema must be empty for a small-model-tier pack — "
            "inferable-attribute tagging requires a quoted basis and is "
            "frontier-tier only (architecture.md §2.3)"
        )

    active_priorities = [
        {
            "name": pr.name,
            "dimension": pr.dimension,
            "shape": pr.shape,
            "threshold": pr.threshold,
            "mandatory": pr.mandatory,
            "not_critical": pr.not_critical,
            "weight": pr.weight,
        }
        for pr in state.priorities.values()
        if not pr.not_critical
    ]
    category_filters = [
        {"name": name, **cf} for name, cf in state.category_filters.items()
    ]
    qualifications = [
        {"name": name, **q} for name, q in state.qualifications.items()
    ]

    return {
        "pack_id": pack_id,
        "session_id": session_id,
        "folded_from_event_seq": state.last_seq,
        "generated_at": generated_at,
        "active_priorities": active_priorities,
        "category_filters": category_filters,
        "qualifications": qualifications,
        "aptitudes_requested": list(aptitudes_requested or []),
        "attested_schema": list(attested_schema),
        "inferable_schema": inferable_schema,
        "reference_anchors": reference_anchors,
        "discovery_context": discovery_context,
        "near_miss_vocabulary": near_miss_vocabulary,
        "forbidden_scope": forbidden_scope,
    }
