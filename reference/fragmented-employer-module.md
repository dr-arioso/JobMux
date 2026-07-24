# JobMux — Fragmented-Small-Employer Discovery Module (Reference Implementation)

**Companion to `design/concept.md`, `design/architecture.md`, and `reference/elicitation.md`.** This file instantiates one evidence-gathering module named in `design/architecture.md` §1.2 — the fragmented-small-employer discovery module — as the fixed, human-reviewed method a model follows when running it. It does not restate what the module is for; `design/architecture.md` §1.2 already does that. It is scoped narrowly: the broad ATS/job-board module, the values-research module, and the signal-fusion module are separate reference implementations, not covered here.

This module has real search history behind it — it is the most exercised part of the evidence-gathering layer to date. That history lives in a project-internal traceability file that is explicitly not open-source material: real employer names, real place names, and real hit-rate numbers from one candidate's search. Nothing from that file appears below. Everything here is the generalized method those findings validated, not the findings themselves. Worked examples use an invented, explicitly hypothetical sector and place, chosen to be structurally similar to what's been validated without reusing it.

As with the companion files: this file states the current template as decided. When it changes, rewrite the relevant section in place.

## 0. When this module runs

The elicitation layer (`reference/elicitation.md`) hands this module a resolved decision node, not a request to run by default. The trigger condition, stated generally: a candidate's search is anchored (by a hard-line or gradated-tolerance geographic constraint, or an equivalent binding scope) into a sector whose typical employers are small, independently run, and not reliably indexed by mainstream job boards. `design/concept.md` §4.3's own test for whether a sector qualifies is the test this module uses too, not a separate one: *does the sector's typical employer run its own small-scale, uncentralized hiring process, and is there a professional or trade association plausibly serving as an informal distribution layer a general search wouldn't see?* If the answer to both is no, the broad ATS module (a separate reference implementation) is the right tool on its own, and this module doesn't run.

This module is never the only thing that runs for a candidate it does apply to. It layers on top of a cheap broad-pass sweep (§2), not instead of one.

## 1. Core discipline: employer-directory-first, not keyword-first

Keyword search over common job boards assumes an employer has already listed a role somewhere those boards crawl. That assumption fails specifically — not randomly — for small civic, nonprofit, and joint-powers employers, and for firms that rely on a professional association's private channel instead of maintaining their own public listings. The failure is employer-specific, not size-based: two similarly small employers in the same sector can differ completely in whether a mainstream board indexes them at all. This means a confirmed zero-result keyword search is real evidence about *that specific employer's* indexing, not evidence the sector has nothing open — and must never be reported as the latter.

The method: build a candidate employer list first, independent of whether any of them currently show an opening, then check each one's own hiring channel directly. Build the list from:

- **Trade or professional association member directories** for the sector — often the single highest-yield source, since an association's member list is usually more complete than any search-engine index of the same employer category.
- **A governing or licensing body's own roster**, where the sector is licensed or chartered (a state agency's list of certified providers, a professional board's registrant list).
- **A larger, already-known employer's own published vendor, partner, or member list**, where one exists — small employers in a fragmented sector often show up as named partners of a larger anchor institution before they show up anywhere searchable on their own.
- **Cross-referencing employers already found in one adjacent sub-sector against the candidate's actual acceptable range** — a directory built for one purpose (e.g., a licensing roster) often names employers relevant to a nearby but distinct decision node too.

Do not substitute a title-keyword sweep for this step and call it discovery. A keyword sweep is real, necessary work — but it's the broad ATS module's job (§2), and conflating the two is exactly the mistake this module exists to correct.

## 2. Cheap-first-pass discipline

Before spending employer-directory effort, run one broad, low-cost keyword pass across the well-indexed job boards for the sector's common title language, including titles surfaced by the search tool's own query-similarity features (a "people also searched" list, or equivalent) to grow the title list outward from a small seed set. This skims off whichever subset of the fragmented market *is* indexed, cheaply, before any per-employer effort begins.

This pass is a triage step, not a substitute for §1. It will under-report — plenty of employers with real openings in a genuinely fragmented sector still won't surface this way — and a clean result here must never be recorded as "sector checked, nothing open." Record it plainly as what it is: the indexed subset is covered; the rest still needs direct checking.

## 3. Gatekeeper/network discovery — its own explicit sub-step

This is logically prior to "check the association's private channel," not the same step. The hard part in a fragmented, relational market is usually not building a relationship with a contact already known — it's confirming *which* association or body is even the authoritative one for this sector, before any relationship-building starts. A module that jumps straight to "check the obvious-sounding association" will miss sectors where the obvious-looking body is wrong, defunct, or actively unsafe.

**The three-way trust check, run before treating any association or body as a source:**

- **Wrong** — a similarly-named body that isn't actually the authoritative one for this sector or geography. Confirm authority independently (a cross-reference from a government agency, a licensing body, or another already-trusted source naming this body as the real one), not from the body's own self-description alone.
- **Defunct** — a body that once was authoritative but shows signs of having stopped functioning (stale event listings years out of date, broken internal links across multiple pages, no evidence of recent activity). A defunct body's stated channels shouldn't be relied on even if its homepage still loads.
- **Unsafe** — a body that is otherwise real and legitimate but has a specific compromised page (hijacked content, off-topic spam, a suspicious redirect) rather than being fake outright. This is a real, observed failure mode, not a hypothetical worth skipping: confirm with more than one direct visit before concluding a page is compromised, and once confirmed, avoid that specific page and avoid entering any information into it, without discarding the rest of the (otherwise legitimate) organization's site or contact channels.

Once a body clears this check, confirm whether it runs any **private, non-crawlable distribution channel** — a members-only email list, a phone-tree, a notice posted only at a physical location — that a search engine or job board would never reach. A body's own "member resources" or "about us" material is the first place to check for this; if it isn't documented there, asking the body directly whether an outside candidate can be added to the loop, or whether current postings can be shared on request, is itself the discovery step, not a fallback after discovery has failed. Reaching that channel is AnalogSearch (`design/architecture.md` §1.2) — direct human contact, not a digital query — and produces an analog-sourced signal, which the verification layer (§6) treats with the same scrutiny as any other signal, never as an automatic finding.

## 4. Broad-scan-by-department for larger or hub employers

Not every employer in a fragmented sector is uniformly small. Where the sector includes a larger "hub" employer (a population-center government, a larger institution with its own multi-department structure), don't filter its own job board by the sector's characteristic keyword alone. Scan the whole board's relevant departments broadly instead — the department a sector's roles would sit under generally, not the specific keyword search would guess. A hub employer's relevant opening often carries a generic departmental title that a sector-specific keyword sweep is never going to match, precisely because a bigger institution's title conventions don't track a small, specialized employer's language.

Where a hub employer runs functionally separate hiring systems for different levels of government or administration covering the same geography (a city and the county that contains it, for instance), check each system independently. A confirmed-empty result on one says nothing about the other.

## 5. Discovery vs. monitoring are different problems

The employer-directory build (§1) and the cheap broad pass (§2) are discovery: finding employers and openings not currently known. Once an employer is on the tracked list, checking it again later is monitoring, and calls for a different cadence and a lighter method — reload the known page or channel, don't re-run the full directory-building process. Conflating the two wastes effort in both directions: re-discovering an already-known employer from scratch, or monitoring at discovery-level intensity when a lighter recheck would do.

## 6. Verification, applied to this module's evidence

Every status claim from this module — an opening found, an opening confirmed gone, an association confirmed as gatekeeper or ruled out — follows `design/architecture.md` §1.3 without exception: a signal from a search tool, a directory listing, or an analog lead can motivate a check, never substitute for one. This cuts both ways in this module specifically as much as anywhere else — a listing that looks newly gone from a small employer's own page deserves the same direct reload as one that looks newly posted.

**Escalation ladder, instantiated for this module's most common failure mode — a guessed URL for a small employer's careers page coming up empty:**

1. Re-derive the URL from the employer's own site navigation (its real menu or footer links), not a second blind guess at a different path.
2. Run a site-scoped search (`site:employer-domain.tld <sector keyword>`) if the nav doesn't surface a careers page — this catches pages the site's own navigation doesn't link to, and cases where a site has migrated domains.
3. Check the sector's trusted third-party directory (the same one used to build the employer list in §1, or an equivalent), if one exists — often more current than the employer's own site structure for a small organization.
4. If none of the above resolves it, record the result distinctly — never as a confirmed negative and never silently folded into the same bucket as a genuinely empty result (§7 names the open question this raises).

## 7. Retain near-misses, not just matches

Rejected employers and listings stay tagged with which threshold, non-negotiable target, or qualification they failed, and by roughly how much (`design/architecture.md` §1.2). This is what lets a later constraint change — a threshold loosening, a non-negotiable flag being lifted, a qualification requirement changing — cheaply resurrect a previously-filtered result from the cache instead of forcing a full directory-and-scan re-run. This applies as much to a "confirmed gone" employer as to a filtered-out listing: record why it's out, not just that it's out.

## 8. Recheck cadence — funding/cycle-aware, not calendar-only

Small and fragmented-market employers frequently post and hire on an external clock — a grant renewal, a budget or levy cycle, a fiscal-year opening, an intake or enrollment window — rather than at random. Where a funding or cycle date is discoverable for a given employer or sector (a grant's known renewal month, a public body's budget-approval cycle), schedule that employer's next check to land shortly before the relevant date, rather than defaulting to a generic calendar interval. Where no such date is known, the generic volatility tier applies, with the same caveat `design/architecture.md` §1.4 already states for it: a scheduling tool, not a stability guarantee — a low-volatility tag deprioritizes scheduling under real time pressure, but doesn't excuse skipping a row that's already being checked because nearby rows are.

## 9. Worked walkthrough (hypothetical, not a validated case)

The following is invented for illustration and marked as such throughout — it is not a report of anything actually run.

> Suppose a candidate's search is anchored to a mid-sized regional hub, in a sector whose typical employers are small, independently governed local bodies of a kind that varies significantly in whether they maintain their own web presence — a plausible fit for this module per §0's test. The directory-build step (§1) starts from that sector's statewide or regional association, if one exists, rather than searching town-by-town. A cheap broad pass (§2) across mainstream boards for the sector's common title language runs in parallel, cheaply, before any per-employer site visit. Suppose that pass surfaces one real opening at an employer whose name wasn't yet on the built directory — that's a signal to add the employer to the directory going forward, not just a one-off hit to record and move past.
>
> Suppose the regional association's own site has a page that looks like it should list current openings, but hasn't shown any change in over a year and several of its other links don't resolve — the defunct signal from §3's trust check. A parallel search finds a second, differently-named body that other sources actually cite as the sector's real regional authority. Confirming that second body as the real gatekeeper, and checking whether it runs any private distribution channel, is the actual discovery step here — not the first body's stale page.
>
> Suppose one hub-sized employer within the anchor region turns up nothing under the sector's usual keyword. Scanning that employer's board broadly by its likely home department (§4), rather than by keyword, turns up a relevant opening carrying a generic administrative title with no sector keyword in it at all.

## §10 — open question

`design/architecture.md` §1.4 specifies that the tracking schema carries "a confidence label for how the status was verified" but does not define a closed vocabulary for that label — how a directly-loaded confirmation, an analog-sourced confirmation (§3), and an unresolved "unable to verify" result (§6, step 4) should each be distinctly tagged, versus left as free text per instance. This module's escalation ladder (§6) needs at least a three-way distinction (confirmed-direct, confirmed-analog, unable-to-verify) to avoid the exact failure `design/architecture.md` §1.3 already warns against — an unresolved result silently collapsing into the same bucket as a confirmed negative — but the recombination/tracking layer (`design/architecture.md` §1.4) is where that vocabulary should actually be decided and versioned, not this module in isolation. Flagged here rather than invented silently; the session that writes the recombination/tracking template (`design/concept.md` §6, step d) should either adopt a closed label set explicitly or decide free text is sufficient.
