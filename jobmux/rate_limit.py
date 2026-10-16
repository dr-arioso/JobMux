"""Rate-limit pacing for live verification loads.

Surfaced by a real failure, not designed speculatively: the 2026-10-15
case-1 recheck verified listings by loading Indeed job pages in a headless
browser 2-3 at a time with a ~5-second gap. Indeed served roughly 30 pages
normally, then switched every further request to a sign-in / Cloudflare
"Additional Verification Required" wall. The session kept requesting into
the wall instead of backing off, which wasted the rest of its Indeed budget
and left several rows unverifiable. That's `reference/verification-escalation-policy.md`'s
"unable to verify" outcome, reached through avoidable tooling behavior
rather than anything about the listings themselves.

This module is the mechanical fix. It decides *whether and when* the next
request to a host may go out and *whether a response is a block signal*,
and leaves the request itself to the caller. Like every module here it is pure:
no network, no sleeping, no clock reads, no randomness of its own. The
caller supplies `now` (epoch seconds) and a uniform `jitter_draw` in
[0, 1), so behavior is fully deterministic under test.

What to verify first when the budget can't cover everything is a separate
question, already answered by `scheduling.order_by_information_gain_per_cost`
/ `select_within_budget`. Order the work with those, then pace it with this.
When a host's budget runs out or a block persists, the rows left over fall
back to whatever search-level evidence already exists and are labelled as
such, never silently promoted to "verified" (the project-wide
signal-vs-finding rule).

The default numbers in `INDEED_POLICY` are a first instantiation from one
real observation (~30 requests at ~2/min concurrency before blocking), not
measured thresholds. They're flagged the same way `scoring.py`'s formula is.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from enum import Enum
from urllib.parse import urlparse


class ResponseSignal(Enum):
    OK = "ok"
    BLOCKED = "blocked"  # bot wall, captcha, auth redirect, 429 -- back off
    ERROR = "error"  # timeout / 5xx / DNS -- not evidence of blocking


#: Body-text markers of a bot wall, observed on real sessions in this
#: project (Indeed/Cloudflare, careers.mn.gov's PerimeterX/ShieldSquare,
#: Bolton & Menk's Cloudflare edge) plus common generic phrasing.
#: Matched case-insensitively. A list, not a closed taxonomy: extend it
#: when a new wall's wording turns up.
BLOCK_BODY_MARKERS: tuple[str, ...] = (
    "additional verification required",
    "performing security verification",
    "verify you are human",
    "verifying you are human",
    "are you a robot",
    "unusual traffic",
    "access denied",
    "px-captcha",
    "shieldsquare",
    "request unsuccessful. incapsula",
)

#: Final-URL markers of a bot-driven redirect, e.g. Indeed's
#: `secure.indeed.com/auth?...&from=bot-detection-anonymous`.
BLOCK_URL_MARKERS: tuple[str, ...] = (
    "bot-detection",
    "captcha",
    "/cdn-cgi/challenge",
)

_BLOCK_STATUSES = frozenset({401, 403, 429})


def classify_response(
    status: int | None,
    final_url: str = "",
    body_text: str = "",
    requested_url: str = "",
) -> ResponseSignal:
    """Classify one page load as OK, BLOCKED, or ERROR.

    `status=None` means the load never completed (timeout, DNS failure).
    That's an ERROR, not a block: a timeout says nothing about whether the
    host is rate-limiting this client, and treating it as one would turn a
    flaky site into a cooldown. A 401/403 is treated as a block only when
    it also redirected or shows a wall marker. A bare 403 with real
    content (some employer sites send 403 to unfamiliar user agents but
    still render) is not assumed to be a wall. 429 is always a block.
    """
    body = body_text.lower()
    url = final_url.lower()
    if any(m in body for m in BLOCK_BODY_MARKERS) or any(m in url for m in BLOCK_URL_MARKERS):
        return ResponseSignal.BLOCKED
    if status is None:
        return ResponseSignal.ERROR
    if status == 429:
        return ResponseSignal.BLOCKED
    if status in _BLOCK_STATUSES:
        redirected_to_auth = bool(requested_url) and _host(final_url) != _host(requested_url) and (
            "auth" in url or "login" in url or "signin" in url
        )
        if redirected_to_auth or not body.strip():
            return ResponseSignal.BLOCKED
        return ResponseSignal.OK
    if status >= 500:
        return ResponseSignal.ERROR
    return ResponseSignal.OK


@dataclass(frozen=True)
class RateLimitPolicy:
    """Pacing rules for one host.

    `min_gap_s`/`max_gap_s`: the wait between consecutive requests is drawn
    uniformly from this range (jitter avoids a machine-regular cadence).
    `block_cooldown_s`: first back-off after a block; doubles per
    consecutive block, capped at `max_cooldown_s`.
    `max_requests`: per-session cap on *successful-or-attempted* requests
    (None = uncapped). `max_consecutive_blocks`: after this many blocks in
    a row, stop for the session rather than keep cooling down.
    """

    min_gap_s: float
    max_gap_s: float
    block_cooldown_s: float = 900.0
    max_cooldown_s: float = 3600.0
    max_requests: int | None = None
    max_consecutive_blocks: int = 2

    def __post_init__(self) -> None:
        if not 0 <= self.min_gap_s <= self.max_gap_s:
            raise ValueError("need 0 <= min_gap_s <= max_gap_s")
        if self.block_cooldown_s < 0 or self.max_cooldown_s < self.block_cooldown_s:
            raise ValueError("need 0 <= block_cooldown_s <= max_cooldown_s")
        if self.max_requests is not None and self.max_requests < 0:
            raise ValueError("max_requests must be >= 0 or None")
        if self.max_consecutive_blocks < 1:
            raise ValueError("max_consecutive_blocks must be >= 1")


#: Aggregator job pages (Indeed). Serial, 20-45 s apart, at most 20 per
#: session, 15-minute first cooldown, give up after 2 blocks in a row.
INDEED_POLICY = RateLimitPolicy(
    min_gap_s=20.0, max_gap_s=45.0, block_cooldown_s=900.0, max_cooldown_s=3600.0,
    max_requests=20, max_consecutive_blocks=2,
)

#: Employer-owned boards and small civic sites. Each host typically gets
#: one or two requests per pass, so pacing mostly matters for portals
#: queried repeatedly (GovernmentJobs cross-tenant search, UKG boards).
DEFAULT_POLICY = RateLimitPolicy(min_gap_s=3.0, max_gap_s=8.0, block_cooldown_s=600.0, max_cooldown_s=1800.0)


@dataclass(frozen=True)
class HostState:
    """Per-host, per-session pacing state. Start from `HostState()`."""

    requests_made: int = 0
    next_allowed_at: float = 0.0
    consecutive_blocks: int = 0
    stopped: bool = False


class Action(Enum):
    PROCEED = "proceed"  # send the request now
    WAIT = "wait"  # wait until `Decision.not_before`, then ask again
    STOP = "stop"  # done with this host for the session


class StopReason(Enum):
    BUDGET_EXHAUSTED = "budget_exhausted"
    REPEATED_BLOCKS = "repeated_blocks"


@dataclass(frozen=True)
class Decision:
    action: Action
    not_before: float | None = None  # set for WAIT
    stop_reason: StopReason | None = None  # set for STOP


def decide(state: HostState, policy: RateLimitPolicy, now: float) -> Decision:
    """May the next request to this host go out at `now`?"""
    if state.stopped:
        reason = (
            StopReason.REPEATED_BLOCKS
            if state.consecutive_blocks >= policy.max_consecutive_blocks
            else StopReason.BUDGET_EXHAUSTED
        )
        return Decision(Action.STOP, stop_reason=reason)
    if policy.max_requests is not None and state.requests_made >= policy.max_requests:
        return Decision(Action.STOP, stop_reason=StopReason.BUDGET_EXHAUSTED)
    if now < state.next_allowed_at:
        return Decision(Action.WAIT, not_before=state.next_allowed_at)
    return Decision(Action.PROCEED)


def record_response(
    state: HostState,
    policy: RateLimitPolicy,
    signal: ResponseSignal,
    now: float,
    jitter_draw: float,
) -> HostState:
    """Fold one completed request into the host's state.

    `jitter_draw` is a caller-supplied uniform draw in [0, 1) choosing
    where in `[min_gap_s, max_gap_s]` the next gap lands.
    """
    if not 0.0 <= jitter_draw < 1.0:
        raise ValueError("jitter_draw must be in [0, 1)")
    made = state.requests_made + 1
    if signal is ResponseSignal.BLOCKED:
        blocks = state.consecutive_blocks + 1
        if blocks >= policy.max_consecutive_blocks:
            return replace(state, requests_made=made, consecutive_blocks=blocks, stopped=True)
        cooldown = min(policy.block_cooldown_s * 2 ** (blocks - 1), policy.max_cooldown_s)
        return replace(state, requests_made=made, consecutive_blocks=blocks, next_allowed_at=now + cooldown)
    gap = policy.min_gap_s + jitter_draw * (policy.max_gap_s - policy.min_gap_s)
    # ERROR doesn't reset the block streak (it's no evidence the wall
    # lifted) but doesn't extend it either.
    blocks = 0 if signal is ResponseSignal.OK else state.consecutive_blocks
    return replace(state, requests_made=made, consecutive_blocks=blocks, next_allowed_at=now + gap)


def host_of(url: str) -> str:
    """Pacing key for a URL: its lowercased hostname minus a leading `www.`."""
    return _host(url)


def policy_for(url: str, overrides: dict[str, RateLimitPolicy] | None = None) -> RateLimitPolicy:
    """Pick the policy for a URL: an explicit per-host override, else
    `INDEED_POLICY` for any indeed.com host, else `DEFAULT_POLICY`."""
    host = _host(url)
    if overrides and host in overrides:
        return overrides[host]
    if host == "indeed.com" or host.endswith(".indeed.com"):
        return INDEED_POLICY
    return DEFAULT_POLICY


def _host(url: str) -> str:
    h = (urlparse(url).hostname or "").lower()
    return re.sub(r"^www\.", "", h)
