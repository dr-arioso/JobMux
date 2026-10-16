import pytest

from jobmux.rate_limit import (
    DEFAULT_POLICY,
    INDEED_POLICY,
    Action,
    HostState,
    RateLimitPolicy,
    ResponseSignal,
    StopReason,
    classify_response,
    decide,
    host_of,
    policy_for,
    record_response,
)

POLICY = RateLimitPolicy(min_gap_s=10, max_gap_s=20, block_cooldown_s=100, max_cooldown_s=300,
                         max_requests=5, max_consecutive_blocks=3)


# --- classify_response: cases observed on the real 2026-10-15 pass ----------------------------

def test_indeed_bot_detection_auth_redirect_is_blocked():
    url = ("https://secure.indeed.com/auth?hl=en_US&continue2=https%3A%2F%2Fwww.indeed.com%2Fviewjob"
           "&from=bot-detection-anonymous")
    assert classify_response(401, url, "Ready to take the next step? Create an account or sign in.",
                             "https://www.indeed.com/viewjob?jk=abc") is ResponseSignal.BLOCKED


def test_cloudflare_additional_verification_is_blocked():
    assert classify_response(403, "https://www.indeed.com/viewjob?jk=abc",
                             "Find jobs ... Additional Verification Required Your Ray ID") is ResponseSignal.BLOCKED


def test_cloudflare_interstitial_blocked_even_with_200():
    assert classify_response(200, "https://www.bolton-menk.com/careers/",
                             "Performing security verification. This website uses a security service"
                             ) is ResponseSignal.BLOCKED


def test_normal_job_page_is_ok():
    assert classify_response(200, "https://www.indeed.com/viewjob?jk=abc",
                             "Environmental Technician - Stack Tester ... Full job description") is ResponseSignal.OK


def test_404_is_ok_not_blocked():
    # A 404 is a real answer about the page (escalation-ladder territory), not a wall.
    assert classify_response(404, "https://example.org/careers", "Page Not Found") is ResponseSignal.OK


def test_timeout_is_error_not_block():
    assert classify_response(None, "", "") is ResponseSignal.ERROR


def test_5xx_is_error():
    assert classify_response(503, "https://example.org", "Service Unavailable") is ResponseSignal.ERROR


def test_429_always_blocked():
    assert classify_response(429, "https://example.org", "slow down") is ResponseSignal.BLOCKED


def test_bare_403_with_real_content_is_not_assumed_blocked():
    assert classify_response(403, "https://example.org/jobs", "Current openings: Lab Technician",
                             "https://example.org/jobs") is ResponseSignal.OK


def test_403_with_empty_body_is_blocked():
    assert classify_response(403, "https://example.org/jobs", "   ") is ResponseSignal.BLOCKED


def test_block_markers_case_insensitive():
    assert classify_response(200, "https://x.org", "ADDITIONAL VERIFICATION REQUIRED") is ResponseSignal.BLOCKED


# --- decide / record_response -----------------------------------------------------------------

def test_fresh_state_proceeds():
    assert decide(HostState(), POLICY, now=0).action is Action.PROCEED


def test_ok_response_sets_jittered_gap():
    s = record_response(HostState(), POLICY, ResponseSignal.OK, now=1000, jitter_draw=0.5)
    assert s.next_allowed_at == 1015
    assert s.requests_made == 1
    d = decide(s, POLICY, now=1010)
    assert d.action is Action.WAIT and d.not_before == 1015
    assert decide(s, POLICY, now=1015).action is Action.PROCEED


def test_jitter_bounds():
    lo = record_response(HostState(), POLICY, ResponseSignal.OK, now=0, jitter_draw=0.0)
    hi = record_response(HostState(), POLICY, ResponseSignal.OK, now=0, jitter_draw=0.999999)
    assert lo.next_allowed_at == 10
    assert 19.99 < hi.next_allowed_at < 20


@pytest.mark.parametrize("bad", [-0.1, 1.0, 2])
def test_jitter_draw_out_of_range_rejected(bad):
    with pytest.raises(ValueError):
        record_response(HostState(), POLICY, ResponseSignal.OK, now=0, jitter_draw=bad)


def test_block_triggers_exponential_cooldown_capped():
    s = record_response(HostState(), POLICY, ResponseSignal.BLOCKED, now=0, jitter_draw=0)
    assert s.next_allowed_at == 100 and s.consecutive_blocks == 1
    s = record_response(s, POLICY, ResponseSignal.BLOCKED, now=100, jitter_draw=0)
    assert s.next_allowed_at == 100 + 200 and s.consecutive_blocks == 2
    capped = RateLimitPolicy(min_gap_s=0, max_gap_s=0, block_cooldown_s=200, max_cooldown_s=300,
                             max_consecutive_blocks=5)
    c = HostState(consecutive_blocks=1)
    c = record_response(c, capped, ResponseSignal.BLOCKED, now=0, jitter_draw=0)
    assert c.next_allowed_at == 300  # 400 capped to 300


def test_repeated_blocks_stop_the_host():
    s = HostState()
    for t in (0, 100, 300):
        s = record_response(s, POLICY, ResponseSignal.BLOCKED, now=t, jitter_draw=0)
    assert s.stopped
    d = decide(s, POLICY, now=10_000)
    assert d.action is Action.STOP and d.stop_reason is StopReason.REPEATED_BLOCKS


def test_ok_resets_block_streak():
    s = record_response(HostState(), POLICY, ResponseSignal.BLOCKED, now=0, jitter_draw=0)
    s = record_response(s, POLICY, ResponseSignal.OK, now=100, jitter_draw=0)
    assert s.consecutive_blocks == 0


def test_error_neither_resets_nor_extends_block_streak():
    s = record_response(HostState(), POLICY, ResponseSignal.BLOCKED, now=0, jitter_draw=0)
    s = record_response(s, POLICY, ResponseSignal.ERROR, now=100, jitter_draw=0)
    assert s.consecutive_blocks == 1 and not s.stopped
    assert s.next_allowed_at == 110  # ordinary gap, not a cooldown


def test_budget_exhaustion_stops():
    s = HostState()
    for i in range(POLICY.max_requests):
        assert decide(s, POLICY, now=s.next_allowed_at).action is Action.PROCEED
        s = record_response(s, POLICY, ResponseSignal.OK, now=s.next_allowed_at, jitter_draw=0)
    d = decide(s, POLICY, now=1e9)
    assert d.action is Action.STOP and d.stop_reason is StopReason.BUDGET_EXHAUSTED


def test_uncapped_policy_never_budget_stops():
    p = RateLimitPolicy(min_gap_s=0, max_gap_s=0)
    s = HostState(requests_made=10_000)
    assert decide(s, p, now=0).action is Action.PROCEED


def test_indeed_scenario_from_real_session_backs_off_instead_of_hammering():
    """Replays the 10/15 failure: the old loop kept sending into the wall.
    Under INDEED_POLICY a single block forces a 15-minute wait, and a second
    consecutive block ends Indeed for the session."""
    s = record_response(HostState(), INDEED_POLICY, ResponseSignal.BLOCKED, now=0, jitter_draw=0)
    assert decide(s, INDEED_POLICY, now=60).action is Action.WAIT
    assert decide(s, INDEED_POLICY, now=900).action is Action.PROCEED
    s = record_response(s, INDEED_POLICY, ResponseSignal.BLOCKED, now=900, jitter_draw=0)
    assert decide(s, INDEED_POLICY, now=99_999).action is Action.STOP


# --- policy validation / selection ------------------------------------------------------------

@pytest.mark.parametrize("kwargs", [
    dict(min_gap_s=5, max_gap_s=1),
    dict(min_gap_s=-1, max_gap_s=1),
    dict(min_gap_s=0, max_gap_s=1, block_cooldown_s=10, max_cooldown_s=5),
    dict(min_gap_s=0, max_gap_s=1, max_requests=-1),
    dict(min_gap_s=0, max_gap_s=1, max_consecutive_blocks=0),
])
def test_invalid_policy_rejected(kwargs):
    with pytest.raises(ValueError):
        RateLimitPolicy(**kwargs)


def test_host_of_strips_www_and_case():
    assert host_of("https://WWW.Indeed.com/viewjob?jk=1") == "indeed.com"
    assert host_of("http://brownswcdmn.org/") == "brownswcdmn.org"


def test_policy_for_indeed_and_default_and_override():
    assert policy_for("https://www.indeed.com/viewjob?jk=1") is INDEED_POLICY
    assert policy_for("https://secure.indeed.com/auth") is INDEED_POLICY
    assert policy_for("https://www.plslwd.org/") is DEFAULT_POLICY
    custom = RateLimitPolicy(min_gap_s=1, max_gap_s=2)
    assert policy_for("https://www.governmentjobs.com/jobs", {"governmentjobs.com": custom}) is custom
