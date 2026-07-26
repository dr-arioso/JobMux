# ADR-0004: Board-heuristic's technical foundation, and consent for ToS-ambiguous sources

**Status:** Accepted
**Date:** 2026-07-25
**Deciders:** Bill

## Context

Per `decisions/0002-build-sequencing-strategy.md`'s Boehm-spike-driven build
order, work reached the board-heuristic module once `jobmux/`'s algorithmic
tier and the adaptive/signal-fusion reference implementations were done. This
session set out to answer what board-heuristic — the fixed-criteria,
algorithmic-tier half of what `design/architecture.md` §1.4's terminology
rename split off from the old "broad ATS/job-board" search — should actually
be built on, rather than assumed to be a thin wrapper around whatever library
came to mind first.

Getting a trustworthy answer required correcting a real research failure
mid-session: an initial claim about a library called "jobhive" /
"stapply-ai/ats-scrapers" was investigated via `WebSearch`/`web_fetch`, which
returned internally inconsistent numbers across repeated fetches of the
supposedly same static README (86,000 vs. 400,000+ companies; 47 vs. 31 ATS
platforms) — a strong signal of unreliable tool output, not necessarily a
fabricated project. Decisive re-verification used channels other than the
tools that produced the inconsistency: `git ls-remote` against GitHub's own
git protocol, `curl` against `raw.githubusercontent.com` and PyPI's JSON API
directly, and libraries.io as a third independent source. All three agree:
the project is real. `kalil0321/ats-scrapers` (`stapply-ai/ats-scrapers`
redirects to it — a renamed org, not a different project) is an actively
maintained repo (hundreds of real branches/PRs, semantic-versioned
`CHANGELOG.md`, real GitHub issue numbers cited in that changelog) published
to PyPI under two names across its history: `jobhive-py` (0.1.0, its original
name) and `ats-scrapers` (0.1.0/0.2.0, current). The differing numbers across
fetches reflect an actively growing hosted dataset at different points in
time, not an inconsistent static file.

A second, real library — `python-jobspy` — was independently verified the
same decisive way (`pip install python-jobspy` succeeded outright; real
author Cullen Watson, real GitHub repo, MIT license) and was never in doubt.

With both libraries confirmed real, the question became which to build
board-heuristic on, and — once inspecting `ats-scrapers`' actual scraper
list surfaced that a handful of its adapters use bot-detection-evasion
tooling — how to treat that.

## Decision

**Adopt both libraries, for two different halves of coverage:**

- **`python-jobspy`** for general job-board aggregators (Indeed, LinkedIn,
  ZipRecruiter, Glassdoor, Google Jobs). MIT licensed. Flat `JobPost` schema.
- **`ats-scrapers`** for ATS-specific and employer-direct search. MIT
  licensed (Kalil Bouzigues, 2026). Richer `Job` schema than JobSpy's
  (structured salary with currency/period/min/max rather than a string;
  `requisition_id` as a genuine cross-ATS dedup signal — the same role
  posted on two different ATSes shares it even though `ats_id` differs).
  Two usage layers, both real code, not a hypothetical: a **dataset-client**
  layer (`search()`, `find_company()`, `list_ats()`) that queries a free
  hosted snapshot with no scraping on our end, and a **per-ATS scraper**
  layer (`BaseScraper`/`ScraperRegistry`, e.g. `GreenhouseScraper`) for
  direct, on-demand access once a specific employer's ATS and slug are
  known — the layer `reference/adaptive-module.md`'s employer-direct checks
  would actually call.

**Neither library closes two gaps `jobmux/verification.py` already cares
about.** Neither schema maps to schema.org's `validThrough` (closing date)
or `occupationalCategory` (SOC code, ADR-0003's exclusion path). Both
remain dependent on a listing's own schema.org structured data, extracted
separately (`design/architecture.md` §2.3's small-model tier), regardless
of which library sources the base listing. This is a known, unclosed gap,
not something this decision resolves.

**Bot-evasion / ToS-ambiguous sources: not JobMux's call to make silently,
in either direction.** `ats-scrapers`' own `models.py` groups 8 of its 50+
scrapers under the comment "Big-tech custom careers systems (single-tenant,
bespoke APIs)" — Meta, Tesla, Apple, Amazon, Google, ByteDance, TikTok,
Uber — and its `pyproject.toml` documents `cloakbrowser` (stealth Chromium)
and `httpcloak` (TLS/HTTP2 impersonation) as existing specifically because
these platforms' bot detection blocks plain HTTP clients. Independent
verification directly confirmed two of the eight: Meta's `robots.txt` is an
explicit, written prohibition on automated collection without permission
("Collection of data on Facebook through automated means is prohibited
unless you have express written permission..."); Tesla's edge (Akamai)
blocked even a plain `robots.txt` fetch outright. The other six share the
evasion-tooling dependency and the library's own single-tenant/bespoke-API
grouping, but were not each independently confirmed the same way — the
honest label for the bucket as a whole is **ToS-ambiguous**, not
**confirmed-violating**. The other ~50 mainstream ATS platforms (Greenhouse,
Lever, Ashby, Workday, SmartRecruiters, and the rest) have `robots.txt` that
either explicitly permits this exact use or is silent while the platform
itself officially documents the endpoint being called.

Bill's framing, adopted close to verbatim: **the data already exists whether
or not JobMux queries it, so this isn't JobMux's ethical call to make on the
candidate's behalf — it's the candidate's.** Rather than a build-time
inclusion/exclusion decision baked into board-heuristic's code, this becomes
a one-time, plainly-worded consent question:

> Some JobMux tools query a public jobs database. It is unclear whether job
> postings from the following employers were collected in accordance with
> their website's terms of service: `<Meta, Tesla, Apple, Amazon, Google,
> ByteDance, TikTok, Uber>`. Exclude these employers from results?

This is new territory for the elicitation layer — not a candidate job-search
preference (`reference/elicitation.md` §1–5's entire subject matter) but a
one-time data-source consent choice tied to a specific evidence-gathering
module's specific dependency. Recorded here as an **open placement
question**, not resolved by this ADR: the natural home is most likely
`reference/board-heuristic-module.md` itself (a first-run setup step that
module states before ever querying a big-tech employer through
`ats-scrapers`), rather than folded into the candidate interview — but this
should be confirmed, not assumed, by whoever writes that reference file.

## Options Considered

### Issue 1 — which library(ies) to build on

**Option A — `python-jobspy` only.** Already fully verified, already the
tool this session started from. Covers general aggregators well but has no
ATS-specific adapters and no employer-direct capability at all — leaves
`reference/adaptive-module.md`'s employer-direct checks with nothing to
call.

**Option B — `ats-scrapers` only.** Covers ATS-specific and employer-direct
search well, including the exact `GreenhouseScraper` shape
`reference/adaptive-module.md` would want. Has no coverage of general
aggregators (Indeed, LinkedIn, etc.) at all — the other real half of what
board-heuristic needs.

**Option C — both, scoped by role (adopted).** JobSpy for aggregators,
`ats-scrapers` for ATS-specific/employer-direct — each covers the half the
other doesn't, and both are independently real, MIT-licensed, and actively
maintained. The cost is two dependencies with two schemas to normalize
against `jobmux/`'s internal shape instead of one.

**Option D — spicy, considered and not adopted: vendor `ats-scrapers`'
source directly into this repo instead of depending on the published
package.** MIT license permits it outright. Would insulate JobMux from the
upstream package disappearing, changing license, or drifting incompatibly,
and would let JobMux exclude the big-tech scrapers by literally not copying
those files in, rather than by a runtime consent gate. Not adopted: it
forfeits upstream bugfixes/new-platform coverage for a project that's
still under 3.11-only Python support and clearly under active development
(0.2.0 shipped mid-session), and duplicates real maintenance burden this
project doesn't need to take on for a dependency this cleanly separable.

### Issue 2 — bot-evasion / ToS-ambiguous sources

**Option A — exclude the big-tech bucket entirely at the code level.**
Simple, defensible, matches this project's generally conservative posture.
Considered, not adopted: it makes the exclusion JobMux's decision rather
than the candidate's, for data the candidate might have entirely legitimate
reasons to want included (e.g., already knowing about and accepting the
provenance question themselves).

**Option B — dataset-client only, never call scraper classes directly for
any platform.** Keeps JobMux from ever executing a live scrape itself,
mainstream or not. Considered, not adopted: it throws away real, on-demand,
clean capability (a fresh Greenhouse/Lever/Ashby check for one employer
right now) to solve a problem that only actually applies to 8 of 50+
platforms — solving the specific problem by giving up unrelated capability.

**Option C — spicy, considered and not adopted: avoid the library
entirely**, on the theory that a dependency shipping bot-evasion tooling
anywhere in its tree is disqualifying regardless of whether JobMux's code
path ever imports it. Considered, not adopted: this project's own build
sequencing (`decisions/0002`) already favors validated, real, existing
tools over hand-rolled reimplementations wherever the fit is genuine — and
here 42+ of 50 adapters have a clean, independently-verified `robots.txt`
story. Treating the whole dependency as tainted by 8 of its adapters
discards real, checked-out fit for the great majority to avoid a problem
that a narrower boundary already solves.

**Option D — user-elicited consent, scoped to the ambiguous bucket
(adopted).** Neither JobMux nor this ADR decides inclusion or exclusion;
the candidate does, once, via a plainly-worded question naming the
uncertainty honestly rather than either asserting a violation or asserting
a clean bill of health. Keeps the great majority of the library's coverage
fully available by default, while giving the one party whose job search
this actually is the actual choice.

## Trade-off Analysis

Issue 1's real cost is maintaining two schema-normalization paths instead
of one — accepted because the two libraries' actual coverage doesn't
overlap in the part that matters (aggregators vs. ATS-specific), so
Option C is closer to "the sum of what's needed" than either single option
alone. Option D (vendoring) is recorded as the fallback if `ats-scrapers`
ever becomes unmaintained or changes license, not adopted preemptively —
the same "record the shape, don't build it speculatively" discipline
`decisions/0003` used for attribute-level reconciliation.

Issue 2's options split on who gets to decide, not on the facts — all four
options agree on what's factually known (2 of 8 sources directly confirmed
ambiguous/blocked, 6 inferred by association, ~50 sources clean). Options A
and B resolve the question by removing capability from JobMux itself,
foreclosing it for every candidate regardless of their own view. Option C
forecloses it more broadly still. Option D is the only one that treats the
uncertainty as something to disclose rather than something to resolve on
the candidate's behalf — consistent with `reference/elicitation.md`'s
existing discipline of surfacing an open question as a live, revisable
state (§1.3's "resolved as open") rather than forcing a resolution that
isn't genuinely settled.

## Consequences

- `reference/board-heuristic-module.md` does not exist yet. When it's
  written, it needs: (1) `python-jobspy` + `ats-scrapers` named as its
  concrete technical foundation per this ADR; (2) the ToS-ambiguous-source
  consent question, in the language recorded above, as an explicit
  first-run step before any big-tech-bucket scraper is ever invoked; (3)
  the open placement question (elicitation.md vs. this file) resolved one
  way or the other rather than left for a third file to guess at.
- `jobmux/README.md`'s open-flags section should note, once board-heuristic
  code lands: schema.org `validThrough`/`occupationalCategory` still aren't
  populated by either library, so `verification.py`'s existing staleness
  and SOC-code paths (ADR-0003) still depend entirely on a listing's own
  structured data being present and extracted, independent of this
  decision.
- No code changes land as part of this ADR — unlike `decisions/0003`,
  which implemented its accepted actions same-day, this decision has no
  corresponding module to modify yet (`reference/board-heuristic-module.md`
  doesn't exist). Action items below are for whoever writes it.
- `CLAUDE.md`'s build-order status and `decisions/README.md`'s index need
  updating to record this ADR (done as part of writing it, per the
  established practice from `decisions/0003`).

## Action Items

1. [ ] Write `reference/board-heuristic-module.md`, naming `python-jobspy`
   and `ats-scrapers` as its concrete technical foundation, per this ADR's
   Decision section.
2. [ ] Instantiate the ToS-ambiguous-source consent question as a concrete,
   first-run step in that module — exact placement (elicitation.md vs.
   board-heuristic-module.md) to be confirmed when it's written, not
   assumed here.
3. [ ] Once board-heuristic code exists, add a `jobmux/`-tier exclusion
   filter for the candidate's consent answer — structurally similar to
   `verification.py`'s `OccupationalCategoryExclusion` pattern (a known
   list, checked before a listing is surfaced), not a new mechanism
   invented from scratch.
4. [ ] Revisit the "6 of 8 inferred, not independently confirmed"
   characterization if any of Apple/Amazon/Google/ByteDance/TikTok/Uber's
   actual `robots.txt`/ToS is ever directly checked — this ADR's language
   should stay honest about what was and wasn't independently verified.
