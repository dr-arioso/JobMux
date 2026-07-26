# JobMux — Board-Heuristic Module (Reference Implementation)

**Companion to `design/concept.md`, `design/architecture.md`, `reference/verification-escalation-policy.md`, and `decisions/0004-board-heuristic-foundation-and-source-consent.md`.** This file instantiates the evidence-gathering module `design/architecture.md` §1.2 names **board-heuristic**: common job boards and ATS platforms, queried with a fixed, defined set of search terms and criteria decided in advance — algorithmic tier (§2.3), no model judgment deciding what counts as a match. It is scoped narrowly, the same way the other module files are: the **board-ML module** (the same sources, but with an LLM judging relevance and refining search terms — frontier tier) is a separate reference implementation, not written yet. `reference/adaptive-module.md`'s employer-directory-first method is a different tool for a different trigger condition; this file's per-ATS scraper layer (§2) is what that module's employer-direct checks actually call, but the discovery method itself lives there, not here.

**Foundation note.** `decisions/0004-board-heuristic-foundation-and-source-consent.md` decided this module's concrete technical foundation: `python-jobspy` (aggregators) and `kalil0321/ats-scrapers` (ATS-specific and employer-direct), both real, MIT-licensed, actively maintained libraries — not something to re-derive from first principles. This file is the method for using them inside JobMux's own discipline (fixed criteria, no persistence without the false-positive registry, verification before any status change), not a description of either library's own API — see that ADR for the research behind the choice, including the real verification failure it corrected mid-research and the bot-evasion-tooling finding that motivates §3 below.

As with the companion files: this file states the current template as decided. When it changes, rewrite the relevant section in place.

## 0. When this module runs

Unlike `reference/adaptive-module.md`, which triggers only on a specific fragmented-sector condition, board-heuristic is close to universal. `design/architecture.md` §1.2 is explicit about this: it is "not an alternative offered only to candidates who don't need the rest of JobMux — it's a necessary component of nearly every case strategy, since even an adaptive search should sweep the well-indexed subset of its market before spending effort on the part that isn't." A candidate whose dominant decision nodes are closer to "open to relocation, industry-agnostic, needs a compensation floor met" may need little beyond this module; every other case layers its own module on top of this one, not instead of it.

Concretely: this module runs as the cheap first pass for any candidate, as soon as the elicitation layer (`reference/elicitation.md`) has produced a context pack (`design/architecture.md` §2.2) with at least one attested-attribute schema and one active priority to search against. It does not wait for a decision node to resolve toward it the way `reference/adaptive-module.md` §0 does — the default is to run it, and the open question is only ever *what else* layers on top, never *whether this runs at all*.

## 1. Two sources, two search shapes

**Aggregator sweep — `python-jobspy`.** Keyword-and-location search across mainstream aggregators (Indeed, LinkedIn, ZipRecruiter, Glassdoor, Google Jobs) concurrently, using the candidate's attested-attribute schema (location, employment type, salary floor where the aggregator supports server-side filtering) to constrain the query itself rather than filtering purely after the fact — cheaper and reduces how much irrelevant volume the false-positive registry (§4) ever has to see. This is the module's default entry point for a candidate with no specific known employer in mind yet.

**ATS-specific sweep — `ats-scrapers`, two distinct layers:**

- **Dataset-client layer** (`search()`, `find_company()`, `list_ats()`). Queries a hosted, pre-scraped snapshot — no live scraping happens on this call. This is the right tool for a broad, cross-employer keyword sweep across the ATS-specific sources JobSpy's aggregators don't reach on their own terms (Greenhouse, Lever, Ashby, Workday, SmartRecruiters, and the rest of the ~50 mainstream platforms the library covers), and for resolving a named employer to its ATS and slug (`find_company("openai")` → `ats="ashby", slug="openai"`) before ever needing the scraper layer below.
- **Per-ATS scraper layer** (`BaseScraper`/`ScraperRegistry`, e.g. `GreenhouseScraper("anthropic").fetch()`, or `get_scraper_for_url(careers_url)` when only a careers URL is known). This is a live, on-demand call against the employer's own API, not a dataset query — the right tool once a specific employer is already identified and a fresh, right-now check is what's needed, rather than a periodic snapshot. `reference/adaptive-module.md`'s employer-direct verification checks are the module that actually needs this layer most; board-heuristic's own use of it is narrower — mainly the hub-employer broad-department-scan pattern that module's §4 describes, applied here when a hub employer's ATS is already known.

Both sources normalize into `jobmux/`'s internal shape via the small-model-tier structured-data-extraction step (`design/architecture.md` §2.3) — neither library's own schema is used as JobMux's tracking schema directly.

## 2. Fixed-criteria discipline

Search terms, locations, and filters are decided in advance from the context pack (`design/architecture.md` §2.2) and applied mechanically — this is what keeps the module algorithmic-tier (§2.3: "running the board-heuristic module's fixed-criteria board query" is explicitly listed as no-model-call work). Judging whether a given result is *actually* relevant, or growing the term list based on what a search surfaces, is board-ML's job, not this module's — a result this module returns is a candidate for the false-positive registry and the verification layer to work on, never a result this module itself decides is a good or bad match.

Do not silently expand a fixed criterion mid-sweep because a term "seems like it should" catch more results. If the current fixed criteria are producing thin results, that's real information to report — "zero found under the current fixed terms" is a legitimate outcome, the same discipline `design/architecture.md` §1.2's "evidence, not advice" already requires — not a license to start improvising broader terms, which is exactly the frontier-tier judgment call board-ML exists to make deliberately, not one this module backs into by accident.

## 3. Source consent for ToS-ambiguous employers

`decisions/0004` found that 8 of `ats-scrapers`' 50+ scraper adapters — Meta, Tesla, Apple, Amazon, Google, ByteDance, TikTok, Uber, the library's own "big-tech custom careers systems" bucket — rely on bot-detection-evasion tooling (a stealth browser, TLS/HTTP2 impersonation) to reach platforms whose own operators actively block plain automated access. Meta's `robots.txt` is a direct, written prohibition; Tesla's edge blocks even a plain fetch. The other six share the evasion dependency and the library's own grouping but weren't each independently confirmed the same way — this bucket is **ToS-ambiguous**, not confirmed-violating, and that distinction matters for the wording below.

Per that ADR's resolution: this isn't JobMux's decision to make silently in either direction — the data exists whether or not JobMux queries it, so it's the candidate's call. This file resolves the ADR's open placement question by instantiating the consent step here, as a first-run gate specific to this module's own dependency, rather than folding it into `reference/elicitation.md`'s candidate-preference interview — it's a data-source disclosure tied to one module's specific tooling, not a job-search preference the candidate would otherwise think to raise.

**Trigger.** Before this module's first call into any `ats-scrapers` scraper class or dataset-client query whose result could include a listing from the big-tech bucket named above, and only once per candidate (not per search):

**Verbatim consent prompt:**

> Some JobMux tools query a public jobs database. It is unclear whether job postings from the following employers were collected in accordance with their website's terms of service: Meta, Tesla, Apple, Amazon, Google, ByteDance, TikTok, Uber. Exclude these employers from results?

Record the candidate's answer as live state, the same way any other category filter is (`design/architecture.md` §1.1) — revisable at any point by the candidate saying so, never re-asked by default once answered. A "yes, exclude" answer is enforced mechanically: a `jobmux/`-tier exclusion filter, structurally the same shape as `jobmux/verification.py`'s `OccupationalCategoryExclusion` registry (a known list, checked before a listing is surfaced or persisted) — not yet implemented; `decisions/0004`'s action item 3 tracks this. A "no, include" answer means this module's normal fixed-criteria sweep proceeds unrestricted, including the big-tech bucket.

Do not soften the prompt's "unclear" language into either a confirmed-violation framing or a clean-bill-of-health framing — both would misstate what was actually verified (§ above, and `decisions/0004`'s Decision section in full).

## 4. Persistence and false-positive handling

Results from either source get the same three-way persistence treatment `design/architecture.md` §1.2 defines for every module: a real result failing a specific threshold or qualification is a **near-miss**, tagged with what it failed (`jobmux/verification.py`'s `NearMiss`/`refilter_near_misses`); a title/category collision unrelated to the candidate's actual target occupation is a **false positive**, checked against `jobmux/verification.py`'s exclusion registry — including the SOC-code path (`OccupationalCategoryExclusion`, `decisions/0003`) when a listing's structured data supplies an `occupationalCategory` code, since neither JobSpy's nor `ats-scrapers`' own schema populates that field itself; a structural priority shift is a **domain-gap**, requiring a repeat sweep rather than a refilter.

This module is a likely source of the exact false-positive shape `decisions/0003` fixed the matching bug for — a keyword sweep across two large, heterogeneous sources is more likely to surface a title collision than a narrow, hand-built employer directory would, precisely because breadth is the point of running this module at all.

## 5. Schema gaps, unresolved by library choice

Neither `python-jobspy` nor `ats-scrapers` maps to schema.org's `validThrough` (closing date) or `occupationalCategory` (SOC code) — `decisions/0004` confirmed this for both rather than assuming JobSpy's known gap wouldn't recur in `ats-scrapers`. Both remain dependent on a listing's own schema.org structured data, extracted by the existing small-model-tier step (`design/architecture.md` §2.3), regardless of which library sourced the base listing. A listing from either source with no structured `validThrough` field falls back to the same staleness discipline `jobmux/verification.py`'s `is_listing_stale` already implements for any other source once a closing date is found some other way (page text, direct confirmation) — this module doesn't get a different staleness rule just because it's the algorithmic-tier one.

## 6. Verification

Every result this module returns is a signal, not a finding, per `reference/verification-escalation-policy.md` §1 — the fact that a query is fixed-criteria and mechanical says nothing about whether the underlying data is current; a hosted dataset snapshot in particular can lag the live listing by however old the snapshot is. `reference/verification-escalation-policy.md` §2's general escalation ladder applies without a module-specific rewrite for this module's typical failure mode (a source returns zero results under the current fixed criteria):

1. Re-derive from the source's own structure — confirm the fixed search terms and filters were actually passed as intended (a malformed location string, an overly narrow employment-type filter) before concluding the source has nothing.
2. Try the same fixed criteria against the other source (JobSpy vs. `ats-scrapers`) — a zero-result sweep on one says nothing about the other, since their coverage doesn't overlap.
3. Check whether a broader, still-pre-approved term already exists in the fixed criteria list for this search (not a model-judged new term — that would cross into board-ML) and hasn't yet been tried.
4. If none of the above resolves it, record **unable to verify** distinctly — the same discipline every other module in this project already follows, never silently folded into "confirmed nothing there."

## 7. Recheck cadence

Standard volatility-tier scheduling applies (`design/architecture.md` §1.4, §1.5). Mainstream aggregators and ATS platforms typically turn over faster than the small, fragmented-sector employers `reference/adaptive-module.md` covers — a tighter default volatility tier for board-heuristic-sourced rows than for adaptive-sourced rows is a reasonable starting assumption, though `design/architecture.md` doesn't currently pin an exact default interval for either, and this file doesn't invent one here rather than leave it to the same open scheduling question §9 below already flags.

## 8. Worked walkthrough (hypothetical, not a validated case)

The following is invented for illustration and marked as such throughout — it is not a report of anything actually run.

> Suppose a candidate's context pack carries a location target, a compensation floor, and an employment-type filter of "full time" only, with no employer-directory-first trigger from `reference/adaptive-module.md` §0. Board-heuristic runs as the default first pass: a `python-jobspy` sweep across the mainstream aggregators for the location and compensation floor, run concurrently with an `ats-scrapers` dataset-client `search()` call for the same criteria across its ~50 ATS sources. Suppose the consent question (§3) hasn't been asked yet and one aggregator result happens to be a Meta posting surfaced by JobSpy (not `ats-scrapers` — JobSpy's aggregator sources aren't part of the big-tech-bucket question at all, since that finding is specific to `ats-scrapers`' own scraper adapters) — this is a case where the consent gate correctly doesn't trigger, since the trigger is tied to a specific library's specific tooling, not to any listing that happens to mention a big-tech employer's name.
>
> Suppose a later sweep, this time using `ats-scrapers`' `find_company()` to resolve a specific employer the candidate named, returns a match whose ATS happens to be one in the big-tech bucket. This is the actual trigger condition for §3's consent question, asked once, before that specific scraper class is ever invoked.
>
> Suppose the aggregator sweep returns a result whose title is a near-exact match for the candidate's target occupation but whose employer field matches a pattern already on the false-positive exclusion registry from an earlier, unrelated search — §4 applies, and the result is purged rather than surfaced or persisted as a near-miss.

## §9 — open questions

Two things `decisions/0004` left open remain open here too, not resolved by this file:

- **Whether the "6 of 8 inferred, not independently confirmed" characterization in §3 should be tightened.** If a future session directly checks Apple/Amazon/Google/ByteDance/TikTok/Uber's own `robots.txt`/ToS the way Meta's and Tesla's were checked, §3's consent-prompt language and this section's honesty caveat should both be revisited together, not just one of them.
- **The exclusion-filter mechanism itself (`decisions/0004` action item 3) is not yet built.** This file specifies its intended shape (mirroring `verification.py`'s `OccupationalCategoryExclusion` pattern) but doesn't implement it — the same "record the shape, don't build it speculatively" discipline `decisions/0003` used for attribute-level reconciliation applies here until board-heuristic has any real code to attach it to.
- **No default volatility-tier interval is pinned for board-heuristic-sourced rows** (§7) — flagged, not decided, consistent with how `design/architecture.md` §1.4/§1.5 leave this open for every module rather than singling this one out.
