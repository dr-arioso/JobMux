# Job-search & recruiting terminology glossary

**Status:** Candidate research material, not yet mapped onto JobMux's own
design docs or code. This is raw vocabulary from a blind subagent plus a
sourced audit — not a decision, and nothing here has been folded into
`design/concept.md`, `design/architecture.md`, `reference/`, or any
`decisions/` ADR. It lives in `research/` rather than `reference/`
deliberately: per `decisions/0001-repo-directory-structure.md`,
`reference/` is for "living reference-implementation docs a future
`SKILL.md` points into" — material already adopted into the build. This
hasn't been adopted into anything yet.

**Why this exists and where it also lives.** This glossary was produced as
part of a much longer terminology-gathering exercise in a *different*
project, `notnotthere-reboot` (the design record for `nnthere`, a search-
and-absence-reasoning toolkit). Bill named JobMux as one of the projects
that inspired `nnthere`, and asked for this domain — job-search vocabulary,
covering both how a candidate is characterized and how a job posting's own
state is characterized — to be produced for JobMux specifically, using the
same method already established there: a subagent with no repository
access produces the raw vocabulary, then a second pass audits it against
real sources.

**This file and its twin in `notnotthere-reboot`'s `docs/proposals/` are
independent copies of the same content, by Bill's explicit instruction —
there is no cross-reference between them, and they are expected to drift
out of sync over time as each project's own needs diverge.** JobMux's
needs may or may not end up coinciding with `nnthere`'s; that's an open
question, not an assumption either way.

**No session log exists in this repo, so this document does not follow
`notnotthere-reboot`'s session-log convention.** Per `CLAUDE.md`'s own
instruction ("update this list as work lands so a new session doesn't
have to reconstruct status from `git log`"), this addition is recorded in
`CLAUDE.md`'s "Where the build actually is" section instead, in that
document's own style.

## What the subagent could and could not see

Dispatched as a `general-purpose` subagent in the `notnotthere-reboot`
session, no isolation, no tool use permitted or exercised (`tool_uses: 0`
in the run). It had no access to either repository — not `nnthere`'s
design record, not JobMux's `design/`, `reference/`, `decisions/`, or
`jobmux/` code. It was kept blind on the same theory used throughout that
project's terminology series: domain vocabulary arrives uncontaminated by
either project's own schema, and any mapping onto a specific data model is
a separate, later, non-blind pass.

**Reading list back:** none. The agent used no tools and read no files —
everything below is claimed as the model's own domain knowledge, not
research.

## The prompt, verbatim

> You are acting as an experienced talent-acquisition/recruiting
> professional who also does career coaching and job-search strategy —
> someone who has sat on both sides of the hiring process (screening
> candidates via an ATS, and separately coaching job seekers on strategy)
> — being asked to brief a colleague who is building software tooling in
> this space but hasn't worked on this side of it. Answer from your own
> domain knowledge — do not use any tools to search the web, read files,
> or inspect any codebase or repository. You have not been given and must
> not infer anything about the specific software project this is for.
>
> **The scenario, in plain terms:** Someone is building a tool that helps
> a job seeker search for roles — including ones that wouldn't turn up on
> a standard job board — and needs vocabulary for two different
> characterization tasks: (1) describing what *kind* of searcher a
> candidate is and what they're actually looking for (beyond a job
> title), and (2) describing what state a given job posting is actually
> in, since "found a listing" and "this role is genuinely open and worth
> applying to" are very different claims.
>
> **Scope:** Default to US white-collar/professional hiring practice (the
> ATS-mediated, LinkedIn/Indeed/Greenhouse-adjacent world). Flag other
> regions or blue-collar/hourly-hiring practice only where the mechanics
> genuinely diverge in a way this kind of tool would have to account for.
>
> **Explicitly worth being thorough about — this is likely the most
> load-bearing part of the glossary:** the vocabulary for a posting's
> actual validity/freshness state. "Listed" covers wildly different
> realities: a role that's genuinely open and being actively filled, a
> "ghost job" posted with no real intent to hire, a backfill for someone
> who hasn't left yet, an evergreen posting that's always up for
> pipeline-building, a role that's already been filled internally but the
> posting wasn't taken down, a repost of a role that failed to fill the
> first time. A tool whose whole value proposition is confirming a role
> is still real needs this vocabulary precise.
>
> **Your task:** Produce a glossary of the terminology real recruiters,
> ATS/HR-tech people, and career coaches use. Cover, at minimum:
> - How a candidate's search status and behavior gets characterized
>   (active vs. passive candidate, boomerang employee, career
>   pivot/changer, underemployment, ghosting — in both directions)
> - How a candidate's fit/preferences get characterized beyond a job
>   title (must-haves vs. nice-to-haves, deal-breakers, comp
>   expectations/bands, culture fit, values-based or priorities-based
>   search as distinct from keyword/title search)
> - How a job posting's validity/freshness state gets characterized (the
>   ghost-job/backfill/evergreen/already-filled/repost vocabulary flagged
>   above, and any signals practitioners actually use to tell these
>   apart)
> - How a posting's own content gets characterized and classified
>   (seniority/level banding, requisition/req, headcount approval,
>   remote/hybrid/onsite classification, comp-range disclosure norms)
> - ATS mechanics relevant to both sides (how a requisition moves through
>   the system, how candidates get screened or auto-rejected, what
>   recruiters and candidates each can and can't see about a listing's
>   real status)
> - Practitioner shorthand/slang from both the recruiter side and the
>   job-seeker side that wouldn't appear in a textbook but that people in
>   the field would actually say out loud
>
> Size the glossary to what the domain actually needs to be covered well —
> there is no fixed target count. Do not pad it to hit a number, and do
> not truncate it to be brief; completeness for this scope matters more
> than length.
>
> **For each term, give:**
> 1. The term itself (and any common variant names for the same thing)
> 2. A plain-English definition, as you'd explain it to a smart
>    non-specialist
> 3. One line on why it would matter to a tool that searches for and
>    validates job opportunities specifically (as opposed to why it
>    matters to recruiting/HR generally)
> 4. A sourcing label: mark each term as either (a) standard/settled
>    terminology any practitioner would recognize — no citation needed, or
>    (b) a convention, rule of thumb, or piece of practitioner judgment
>    that varies by industry/company/practitioner or isn't formally
>    codified — flagged explicitly as such rather than stated as settled
>    fact
>
> **Format:** A flat list (not nested by category), one entry per term, in
> the 1–4 structure above. Do not organize it into a workflow narrative.
>
> **At the end**, list separately: (a) any terms you were genuinely unsure
> how to define precisely and flagged rather than guessed at, and (b) any
> terms you considered including but excluded as out of scope, with a
> one-line reason.
>
> Do not attempt to guess what software schema or data model this glossary
> will feed into. Just produce the practitioner vocabulary.

## Returned glossary

*Everything below this line is the subagent's output, verbatim. Each entry
carries its own sourcing label — (a) standard/settled, or (b) practitioner
convention/judgment, unsourced. Nothing here has been independently
verified except where the audit section below says so.*

A flat list of practitioner terminology for a tool that helps candidates
find and validate roles, including ones off the standard job boards.
Sourcing labels: **(a)** = standard/settled, any practitioner would
recognize it; **(b)** = convention/judgment/rule-of-thumb that varies by
company, industry, or practitioner, flagged as such.

---

**1. ATS (Applicant Tracking System)**
The software a company uses to post jobs, collect applications, move candidates through stages, and store hiring data (Greenhouse, Workday, iCIMS, Lever, Taleo, etc.). Nearly every mechanism below either lives inside or is visible through an ATS.
*Tool relevance:* The tool's whole validation problem is downstream of ATS behavior — postings, statuses, and "freshness" are ATS artifacts, not ground truth about hiring intent.
*(a)*

**2. Requisition ("req") / Req ID**
The internal record authorizing a role to be filled — distinct from the public job posting, which is marketing copy generated from (or loosely tied to) the req. A req has its own lifecycle, approvals, and internal notes the public posting never shows.
*Tool relevance:* This is the central object a validity-checking tool is really trying to infer the state of; the posting is just its shadow.
*(a)*

**3. Headcount approval / "approved to hire"**
Finance/leadership sign-off that a role can actually be filled and paid for. A req can exist and even get posted before this is final, or can lose approval (frozen) after posting.
*Tool relevance:* Explains why a live-looking posting may have no funded seat behind it — a root cause of "ghost"-like postings that isn't malicious, just organizational lag.
*(a)*

**4. Req lifecycle / req status (draft → approved/open → on hold → filled → closed/canceled)**
The internal state machine a requisition moves through in the ATS. Public postings usually reflect only "open," and often fail to update when the internal state changes.
*Tool relevance:* This mismatch between internal req status and external posting status is the mechanical explanation for most "stale listing" problems the tool needs to detect.
*(a)*

**5. Job description (JD) vs. job posting**
The JD is the internal, often boilerplate document defining a role's duties/requirements; the "posting" is the external, marketing-adjusted version published to boards, sometimes rewritten by a recruiter or generated/optimized by software. They can drift apart.
*Tool relevance:* Parsing the posting text is not the same as reading the actual req — matters for a tool trying to infer real requirements versus SEO-oriented posting copy.
*(a)*

**6. Sourcer**
A recruiting function (sometimes a distinct role from "recruiter") focused on proactively finding and reaching passive candidates, often before or without a public posting existing.
*Tool relevance:* Sourcer outreach is one of the main channels through which "hidden" roles reach candidates — relevant to a tool trying to model the non-board path.
*(a)*

**7. Corporate/in-house recruiter vs. agency/third-party recruiter**
In-house recruiters are employed by the hiring company; agency recruiters work for a staffing/search firm and are paid a fee (contingency or retainer) by the client company, not the candidate.
*Tool relevance:* Agency-posted roles are more prone to duplicate/stale listings (same req posted by multiple agencies or re-posted after the agency's exclusivity window ends) — a real source of the "repost" confusion.
*(a)*

**8. Contingency recruiter vs. retained recruiter ("headhunter") / container search**
Contingency firms are paid only if their candidate is hired (often used for lower/mid-level, high-volume, or less exclusive searches — a signal correlated, not proof, of a less "locked-in" search). Retained firms are paid an upfront/progress fee regardless of outcome, typically for senior/executive confidential searches, which correlates with the role being more genuinely committed. "Container" search is a hybrid retainer-lite model.
*Tool relevance:* The retained-vs-contingency distinction is one of the few practitioner-known proxies for "how real is this search," especially for senior roles that never appear on a public board at all.
*(b) — the correlation with search seriousness is a heuristic, not a guarantee; plenty of contingency searches are entirely real.*

**9. RPO (Recruitment Process Outsourcing)**
A vendor that runs some or all of a company's recruiting function under contract, as opposed to an in-house team.
*Tool relevance:* RPO-run reqs are sometimes higher-volume and more templated, which practitioners anecdotally associate with a higher rate of postings that outlive their actual need.
*(b) — anecdotal, not a documented rate.*

**10. Applicant vs. candidate**
"Applicant" is anyone who submitted an application; "candidate" usually implies someone actually being considered/screened. The gap between the two counts is often huge (hundreds of applicants, a handful of candidates).
*Tool relevance:* A tool reporting "applicant volume" as a validity signal should be clear it's not measuring the more meaningful "candidate" funnel.
*(a)*

**11. Knockout question / screening question**
A yes/no or short-answer question in the application flow (work authorization, required certification, minimum salary) used to auto-filter applicants before a human ever looks.
*Tool relevance:* Explains a large share of instant, silent rejections that look like "the role went nowhere" to a candidate but are just automated filtering.
*(a)*

**12. Auto-reject / auto-disqualify / auto-advance**
ATS rules that reject or advance applicants automatically based on parsed resume data or knockout answers, without recruiter review.
*Tool relevance:* A candidate (and a naive tool) can't distinguish "the role isn't real" from "you got auto-rejected in nine seconds" — both look identical from outside.
*(a)*

**13. Resume parsing / ATS parsing**
The automated extraction of structured data (titles, dates, skills, education) from a submitted resume, which then drives matching/scoring and knockout logic.
*Tool relevance:* Parsing failures (bad formatting, tables, headers) are a common false-negative cause a tool built for candidates should account for, separate from the role's own validity.
*(a)*

**14. Keyword optimization / "ATS-proofing" a resume**
Candidate-side practice of tailoring resume language to match a posting's likely parsed keywords, to survive automated screening.
*Tool relevance:* Directly actionable output for a candidate-facing tool — matching the posting's real language, not just the job title.
*(a)*

**15. Pipeline / candidate pipeline stages**
The ordered stages a candidate moves through: sourced → applied/screened → phone screen → interview loop → offer → hired (naming varies by ATS). "In the pipeline" means actively being considered.
*Tool relevance:* Candidates never see this internal stage; a tool inferring "is this role progressing" is essentially trying to reconstruct pipeline movement from external signals alone.
*(a)*

**16. Silver medalist**
A strong finalist who didn't get an offer for one req but is proactively recontacted when a similar or the same role reopens.
*Tool relevance:* A real (if minor) channel for roles being filled without ever going through a fresh public posting — relevant to "hidden opportunity" modeling.
*(a)*

**17. Talent pool / talent community**
A standing database of candidates a company has sourced or who've expressed interest, kept "warm" for future openings rather than a specific current req.
*Tool relevance:* Explains part of why evergreen postings exist — they're partly a pipelining mechanism, not always a live opening.
*(a)*

**18. Employee referral**
A candidate submitted by a current employee, usually routed through a formal ATS referral process with a bonus incentive; referred candidates are statistically much more likely to be interviewed than cold applicants.
*Tool relevance:* One of the highest-leverage "off-board" paths — relevant if the tool coaches candidates toward strategies beyond applying cold.
*(a)*

**19. Warm introduction / warm intro / warm outreach**
An informal (non-ATS) connection to a hiring manager or employee at a target company, arranged through a mutual contact, as opposed to a cold application.
*Tool relevance:* Core vocabulary for the "beyond the job board" half of the tool's mission — this is literally how a large share of unlisted or under-listed roles get filled.
*(a)*

**20. Cold outreach**
Direct, unsolicited contact to a hiring manager, recruiter, or employee with no prior connection — via email, LinkedIn message, etc.
*Tool relevance:* A lower-conversion but real alternative discovery/application channel a search tool might help structure or track.
*(a)*

**21. Hidden job market / unadvertised vacancy**
Roles filled without ever being publicly posted — through referral, direct outreach, internal promotion, or a recruiter's existing pipeline. Frequently invoked with a specific percentage of "all jobs" filled this way.
*Tool relevance:* This is the explicit premise of half the tool's stated purpose (finding roles that don't show up on a job board), so getting the term's actual epistemic status right matters — see caveat below.
*(b) — the concept is standard and widely used, but the commonly cited statistics (e.g., "70–80% of jobs are filled through networking") are frequently repeated without a solid, reproducible empirical source; treat the number as folklore even though the phenomenon it describes is real.*

**22. Active candidate**
Someone currently and visibly searching — applying to postings, updating LinkedIn, telling their network.
*Tool relevance:* Determines whether a tool should optimize for volume/speed (active) versus discretion/selectivity (passive) in how it surfaces and pushes opportunities.
*(a)*

**23. Passive candidate**
Someone not actively looking but potentially open to the right opportunity if approached; the classic target of recruiter sourcing outreach.
*Tool relevance:* A passive-candidate-oriented tool behaves very differently (fewer, higher-fit alerts; more discretion) than an active-search tool.
*(a)*

**24. "Open to Work" (OTW) / "open to opportunities" signal**
LinkedIn's explicit banner/flag (public or recruiter-only) indicating job-search status; recruiters treat public OTW banners as a weak signal sometimes penalized by hiring managers as a sign of unemployment.
*Tool relevance:* A real, if imperfect, external signal of candidate intent the tool could read or expose, with the caveat about how it's perceived.
*(b) — the "penalized by hiring managers" perception is widespread practitioner folklore, not a documented universal rule.*

**25. Boomerang employee**
Someone who leaves a company and later returns, often in a different or higher role.
*Tool relevance:* A distinct candidate-search motive/status (re-approaching a former employer) that a generic "new job title" search framing wouldn't capture.
*(a)*

**26. Career pivot / career changer**
A candidate moving into a substantially different function, industry, or field rather than a lateral or upward move within one.
*Tool relevance:* Pivoters need transferable-skill framing and often can't be searched by title-matching alone — directly relevant to "beyond the job title" characterization.
*(a)*

**27. Underemployment**
Working in a role below one's skill level, experience, or credential (part-time when full-time is wanted, or a job well below one's prior seniority/pay).
*Tool relevance:* A distinct search motivation from unemployment — the person has income but is job-searching for fit/level reasons, which changes urgency and target criteria.
*(a)*

**28. Ghosting (candidate ghosts employer / employer ghosts candidate) / "flaky" / no-show**
Either party abruptly cutting off communication without explanation — a candidate stops responding after interviews or after accepting, or (far more commonly complained about by candidates) a company goes silent after interviews with no rejection notice. "No-show" specifically means missing a scheduled interview without notice.
*Tool relevance:* Employer-side ghosting is one of the most common candidate complaints and is functionally indistinguishable, from outside, from "this req quietly died" — relevant to how a tool should interpret silence.
*(a)*

**29. Renege / reneging on an accepted offer**
Either the candidate or the employer backing out after an offer has been formally accepted (before start date).
*Tool relevance:* Explains a subset of "role reopens shortly after being marked filled" cases a validity tool might otherwise misclassify as a fresh repost of a fake role.
*(a)*

**30. Job hopper / job hopping**
A candidate with a pattern of short tenures across multiple employers; historically viewed skeptically, though norms have loosened somewhat, especially in tech.
*Tool relevance:* A recruiter-facing screening heuristic a candidate-facing tool might want to help a user preempt or contextualize in materials.
*(b) — how harshly it's judged varies significantly by industry, seniority, and current labor market tightness.*

**31. Flight risk**
An employee (current, not necessarily a job-seeker) judged likely to leave soon — a term recruiters/managers use when deciding who to proactively retain or, conversely, whom a sourcer might target as a likely-receptive passive candidate.
*Tool relevance:* Frames a passive-candidate targeting logic — "likely to move" is a distinct, useful candidate attribute beyond stated search status.
*(a)*

**32. Counteroffer / counter**
An employer's offer to retain an employee who has resigned or received an outside offer, typically with a raise or promotion.
*Tool relevance:* A live decision point in a candidate's search that affects whether other in-flight opportunities should be paused or dropped — worth modeling as a search-state event.
*(a)*

**33. Exploding offer**
A job offer with an artificially short acceptance deadline, used to pressure a quick decision and prevent shopping it for a counter or competing offer.
*Tool relevance:* Time-pressure state a coaching-oriented tool would want to flag and help a candidate respond to strategically.
*(a)*

**34. Involuntary vs. voluntary job seeker / "between roles"**
Whether someone is searching because they were laid off/terminated versus by choice; "between roles" is a common softened euphemism for the involuntary case.
*Tool relevance:* Changes search urgency, target breadth, and messaging — a coaching-relevant distinction beyond just "actively searching."
*(a)*

**35. Employment gap**
A period of no formal employment on a resume/timeline, historically flagged by screeners, now more normalized post-2020.
*Tool relevance:* Relevant to how a tool might help a candidate frame timeline in materials or filter roles less likely to screen harshly on it.
*(b) — how much it matters varies enormously by industry, level, and individual recruiter/hiring manager.*

**36. Must-haves vs. nice-to-haves**
The candidate's (or a posting's) requirements split into non-negotiable criteria versus preferred-but-flexible ones.
*Tool relevance:* Core structure for any preference-matching logic beyond a single job title — this is the actual filtering unit both recruiters and coaches use.
*(a)*

**37. Deal-breakers / non-negotiables**
Specific conditions that would cause a candidate to reject an otherwise good-fitting role outright (e.g., no remote option, certain commute, mandatory travel, values conflict).
*Tool relevance:* A distinct, harder-edged filter category from "must-haves" — worth its own field since it triggers outright exclusion rather than scoring.
*(a)*

**38. Comp expectations / comp range / comp band**
What a candidate states (or a company internally sets) as the acceptable salary range for a role; candidates are often asked for a range early ("comp expectations") which recruiters use to screen out mismatches.
*Tool relevance:* Central to any real fit-matching beyond title — mismatched comp expectations is one of the most common reasons a seemingly good-fit role goes nowhere.
*(a)*

**39. Total compensation (TC) vs. base**
Base salary alone versus the full package (base + bonus + equity + benefits value); candidates comparing offers by base alone often make bad comparisons.
*Tool relevance:* A tool doing comp matching or offer comparison needs to normalize on TC, not headline base salary, to be useful.
*(a)*

**40. OTE (on-target earnings)**
Base plus expected/typical commission or bonus at target performance, common in sales-role postings; often quoted instead of, or alongside, base.
*Tool relevance:* A posting quoting OTE without a base breakdown is a specific parsing trap for a comp-matching tool (OTE can look inflated relative to guaranteed pay).
*(a)*

**41. Culture fit vs. culture add**
"Culture fit" (whether a candidate meshes with existing team norms) has been widely criticized as a bias vector; "culture add" (what new perspective/strength a candidate brings) is the more current reframing many practitioners now prefer.
*Tool relevance:* If the tool surfaces "culture fit" as a matchable attribute, it should model it as company-stated values/work style compatibility, not a vague vibe check — and the fit-vs-add distinction is itself a live practitioner debate worth reflecting.
*(b) — "culture add" is a real and increasingly common reframing, but adoption is uneven and far from universal.*

**42. Values-based / priorities-based search (vs. keyword/title search)**
A search strategy organized around what matters to the candidate (mission alignment, autonomy, growth, stability, flexibility) rather than matching job titles or keywords to postings.
*Tool relevance:* This is the conceptual core of "describing what kind of searcher a candidate is beyond a title" — the axis the tool is explicitly trying to model.
*(b) — this is standard career-coaching methodology (used in frameworks like values-card sorts, "Designing Your Life"-style exercises), but it's coaching practice, not a formally codified industry standard the way ATS mechanics are.*

**43. Target company list**
A candidate-curated (often coach-assisted) list of specific companies of interest, used to drive networking and direct outreach rather than reactive job-board browsing.
*Tool relevance:* A structural alternative to keyword search that a tool could support directly — monitoring/outreach against a company list rather than a title query.
*(a)*

**44. Ideal candidate profile (ICP)**
Recruiter-side term for the specific profile a hiring team is trying to fill a role with (skills, background, sometimes even unstated preferences like company pedigree) — the mirror image of a candidate's target-role profile.
*Tool relevance:* Understanding that a posting's stated requirements often understate the real ICP (unstated preferences) explains a chunk of "well-qualified but rejected" outcomes a tool shouldn't over-attribute to fakeness.
*(a)*

**45. Golden handcuffs**
Financial incentives (unvested equity, deferred bonus, pension cliff) that make leaving a current job costly, discouraging an otherwise willing candidate from moving.
*Tool relevance:* A real constraint on search behavior/timing worth modeling for passive candidates — explains slow-moving or stalled searches that aren't about fit.
*(a)*

**46. Trailing spouse / relocation constraint**
A candidate search constrained by a partner's job location or family relocation limits.
*Tool relevance:* A geographic hard-constraint category distinct from generic "remote preference," relevant to filtering out roles that require relocation.
*(a)*

**47. Level match / leveling equivalence**
Mapping a candidate's title/level at one company to the equivalent level at another, since titles aren't standardized (a "Senior Manager" at one company might equal a "Director" at another).
*Tool relevance:* Essential for any cross-company title matching — searching by literal title without leveling equivalence produces both false matches and missed ones.
*(b) — informal cross-company leveling guides (e.g., crowdsourced comparison charts) exist and are widely used, but there's no authoritative standard; it's practitioner consensus at best.*

**48. Title inflation / title deflation**
The practice (common at smaller companies, startups, or certain industries) of giving out senior-sounding titles for junior-level scope, or vice versa (some large, conservative companies under-title relative to actual scope).
*Tool relevance:* Undermines pure title-based search/matching — reinforces why the tool needs scope/responsibility signals, not just title strings.
*(b) — widely observed and discussed but not something with a formal measurement; direction and magnitude vary heavily by company size, industry, and geography.*

**49. Ghost job**
A job posting kept live with no genuine, current intent to hire for it — reasons cited by practitioners include projecting growth to investors/customers, building a resume database, satisfying legal posting requirements, or simple neglect (nobody took it down). The term itself is media/practitioner-coined, not a formal HR or legal category, and has fuzzy edges.
*Tool relevance:* This is the single term the tool most needs to operationalize precisely, and it needs to be decomposed into its actual sub-causes (see 50–58) rather than treated as one binary flag, since "ghost" covers genuinely different underlying realities with different detection signals.
*(b) — the phenomenon is widely reported (including by ATS vendors' own posting-age data) but there is no standardized definition or agreed threshold for when a stale posting "counts" as a ghost job; estimates of prevalence vary widely by source and methodology.*

**50. Evergreen posting / evergreen req**
A posting deliberately kept open on an ongoing basis, not tied to one specific current opening — used for continuous pipeline-building in roles with constant or predictable turnover (e.g., sales, retail, delivery/warehouse, nursing).
*Tool relevance:* Structurally different from a ghost job — there is genuine hiring intent, just not for a single discrete slot with a closing date, which changes what "applying" even means and what a candidate should expect.
*(a) — the term itself is standard; in high-turnover blue-collar/hourly contexts (retail, food service, logistics) "always open" postings are the structural norm rather than an ambiguous edge case, unlike in white-collar hiring where an evergreen posting is more often mistaken for (or functions similarly to) a ghost job.*

**51. Backfill**
A req opened to replace someone who is leaving, being managed out, or has already left — as opposed to a net-new headcount role. Sometimes posted before the incumbent has formally departed or even been told.
*Tool relevance:* A backfill posted pre-departure is genuinely open but highly sensitive (confidential timing), which affects how a candidate should approach outreach and how a tool should characterize "how real/how urgent" the role is.
*(a)*

**52. Repost / reposted listing / "bumped"**
A posting taken down and republished (sometimes verbatim) — either because it failed to fill the first time, to reset its "posted date" so it appears newer/ranks higher in job-board algorithms, or as part of a compliance cycle.
*Tool relevance:* Reposting-for-algorithmic-freshness is a specific, known board-gaming tactic; a tool computing "posting age" naively will be fooled by this unless it tracks req identity across reposts, not just the visible post date.
*(b) — that reposting is sometimes done specifically to game freshness ranking is well-known practitioner lore and is plausible given how boards rank by recency, but companies don't publish their motive, so any individual repost's cause is inferred, not confirmed.*

**53. Already filled internally (a.k.a. "zombie listing")**
A posting still live on a board or company career page after the role has actually been filled — usually because nobody remembered to take it down, or because of syndication lag (see 59).
*Tool relevance:* This is the purest "false positive" case for a validation tool — genuinely dead, purely due to administrative lag rather than any hiring-intent ambiguity, and in principle the most detectable case if the tool can cross-reference posting age against company news, LinkedIn hires, etc.
*(a) — the phenomenon is standard and well understood; "zombie listing" as a specific label for it is informal/practitioner slang rather than a formal industry term.*

**54. Internal-only requisition / internal posting**
A role posted for current employees only, not meant to be visible or applicable to external candidates — sometimes leaks onto external aggregators due to feed misconfiguration.
*Tool relevance:* An external-facing tool scraping or aggregating postings needs to be able to detect and exclude these, since applying externally to one is a dead end regardless of how "fresh" it looks.
*(a)*

**55. Compliance posting / PERM labor certification posting**
A legally required external posting where an employer must advertise a role to the general labor market even though they already intend to hire a specific person — most concretely, the U.S. PERM process for sponsoring a foreign worker's green card requires a genuine-looking recruitment process and posting, even though the outcome is effectively predetermined. Similar dynamics (lighter-weight) exist under some internal-promotion and government/public-sector posting rules.
*Tool relevance:* This is a legally mandated, procedurally real posting that is nonetheless not a genuine opportunity for an external applicant — a distinct category from "ghost job" (no deception/neglect involved, it's compliance) that a validity tool should be able to name separately rather than lumping in with fakes.
*(a) — the PERM mechanism itself is a well-documented, standard legal process; recognizing a specific posting as a PERM ad from its content/pattern is practitioner pattern-matching, flagged as such.*

**56. Confidential search / stealth req**
A search where the hiring company's identity, the role's existence, or both are deliberately not disclosed publicly — common in executive search, sensitive replacements, or pre-announcement restructuring.
*Tool relevance:* By definition these roles won't appear on a job board at all, so this term marks the outer edge of what a posting-scraping tool can ever see — the true "hidden" category, reachable only through relationships/retained search firms.
*(a)*

**57. Req on hold / frozen req**
A previously approved, actively-being-worked req that is paused — due to budget freeze, reorg, or a hiring manager change — without being formally canceled.
*Tool relevance:* Explains "the posting is up but nothing is moving" cases distinct from ghost jobs — there is real intent, just stalled, and it may resume without any visible signal change.
*(a)*

**58. Req reopened**
A req that was closed (filled or canceled) and is later reactivated — sometimes because the hire fell through, reneged, or didn't work out during probation.
*Tool relevance:* A legitimate reason the "same role" reappears after a gap, which a tool shouldn't automatically read as suspicious repost/ghost behavior.
*(a)*

**59. Feed / syndication lag**
The delay (sometimes days, sometimes indefinite if a sync breaks) between a req's status changing in the ATS and that change propagating to the company's careers page and third-party boards (LinkedIn, Indeed) that pull from an XML/API feed.
*Tool relevance:* A key mechanical, non-conspiratorial explanation for stale-looking listings — directly useful for a tool to cite rather than implying deception when it's often just a broken or slow integration.
*(b) — the mechanism is standard and well understood by ATS/HR-tech practitioners, but there's no public data on how common or how long lags typically run; it varies by vendor and integration quality.*

**60. Job board aggregator staleness**
Boards like Indeed that aggregate listings from many other sources (company sites, other boards, Google for Jobs) can display postings well after the original source removed them, since aggregator refresh cycles lag the source.
*Tool relevance:* Means "found on Indeed" is a weaker freshness signal than "found on the company's own careers page" — a concrete, checkable heuristic for the tool to apply.
*(a)*

**61. Posting age / "days since posted" signal**
The most basic freshness proxy — how long ago a listing first appeared, shown by most boards ("Posted 30+ days ago").
*Tool relevance:* The most obvious signal, but easily gamed by reposting (52) and undermined by feed lag (59) — useful only in combination with other signals, not alone.
*(a)*

**62. Applicant count as freshness/competition signal**
Some boards display how many people have applied ("over 200 applicants"); practitioners read very high counts on an old posting as a soft signal of either evergreen status or neglect, though it's also just a function of how visible/popular the board is.
*Tool relevance:* A concrete, scrapable data point, but a weak and confoundable one that shouldn't be over-weighted alone.
*(b) — used informally by job seekers and coaches as a rough heuristic; not a validated signal, and confounded heavily by board popularity and title commonality.*

**63. "Actively hiring" / "actively recruiting" platform badge**
Icons/labels some platforms (notably LinkedIn) attach to a posting or a recruiter's profile suggesting recent hiring activity — the exact computation behind the badge (e.g., recent messages sent, recent hires made) is not publicly documented.
*Tool relevance:* A platform-native "freshness" signal a tool might want to surface, with the important caveat that its underlying logic is opaque and not independently verifiable.
*(b) — flagged explicitly: the precise algorithm behind these platform badges is not public, so their reliability as a validity signal can't be independently assessed.*

**64. Time-to-fill**
The average duration from a req opening to an accepted offer, tracked internally by recruiting teams and varying widely by role/level/industry.
*Tool relevance:* Useful as a rough prior for how long a listing "should" reasonably stay open before its continued presence starts looking anomalous relative to its role type.
*(a) — the metric itself is standard; specific benchmark numbers vary by industry/level and are proprietary to individual companies' internal reporting, so any general figure a tool uses should be treated as an approximation.*

**65. Recruiter responsiveness as a validity signal**
Practitioner/coaching heuristic: if a recruiter or hiring manager responds promptly and specifically to outreach about a posted role, that's a strong positive signal the req is real and active; silence or generic auto-replies are a negative signal (though also just consistent with a busy recruiter).
*Tool relevance:* One of the few genuinely reliable validity checks available to an individual candidate, and something a coaching-oriented tool can explicitly instruct a user to attempt (e.g., "message the recruiter directly and ask").
*(b) — this is coaching practice/rule of thumb, not a measurable or standardized signal.*

**66. Networking-based confirmation ("ask a human")**
The practitioner fallback for validating any ambiguous listing: use a personal or LinkedIn-adjacent connection at the company to ask directly whether a role is genuinely open, rather than trusting the posting alone.
*Tool relevance:* Represents the ceiling of confidence achievable and is worth the tool explicitly recommending/facilitating when its own automated signals are inconclusive.
*(a)*

**67. Seniority/level banding**
Standardized internal bands (e.g., IC1–IC6, L3–L8, "Associate/Senior/Staff/Principal") mapping to scope, pay range, and title, used to classify a posting's actual level independent of its external title.
*Tool relevance:* Necessary for matching candidates to postings on actual seniority rather than title string alone, given how much title inflation/deflation (48) varies.
*(a) — the practice is standard; the specific band structure and naming is company-specific and not standardized across the industry.*

**68. Job architecture / job family**
A company's overall taxonomy of role types and levels (e.g., "Engineering," "Product," each with its own ladder) used to structure job codes, pay bands, and career paths.
*Tool relevance:* Underlies how a company's own postings get organized/labeled internally, which can help explain oddities in how similar-sounding roles are titled differently across teams.
*(b) — a real and common HR practice, but implementation varies enormously by company; there's no universal standard job architecture.*

**69. IC track vs. management track**
Individual Contributor (technical/specialist) career path versus People Manager path — often diverge above a certain level, with parallel title/level ladders.
*Tool relevance:* A necessary disambiguator for senior-title matching (e.g., "Staff Engineer" IC vs. "Engineering Manager" — same seniority, very different job).
*(a)*

**70. Remote / hybrid / onsite classification (incl. "remote-first" vs. "remote-friendly" vs. "remote-eligible")**
Categorical labels for work-location policy, but with meaningfully different and inconsistently used definitions across companies: "remote-first" generally implies remote is the default/primary mode even for those near an office; "remote-friendly" often just means remote is permitted, not optimized for; "hybrid" ranges from a strict mandated N-days-in-office to fully flexible; "remote-eligible" can mean only within a specific country/state/time-zone band.
*Tool relevance:* One of the highest-value fields to get precisely right for a "beyond the title" search tool, since the same word ("remote") can mean structurally different day-to-day realities — and the labels are also one of the first things that goes stale after a policy change.
*(b) — none of these labels are standardized across companies; each is a marketing/HR term interpreted differently company to company, which is exactly why they need careful, explicit handling rather than a single boolean.*

**71. RTO mandate (return-to-office)**
A policy requiring previously remote/hybrid employees back into the office some or all of the time, often announced after a role was originally posted or hired for under different terms.
*Tool relevance:* A posting's stated remote/hybrid policy can go stale specifically because of an RTO mandate issued after posting — a distinct freshness-accuracy problem from the posting simply being old.
*(a)*

**72. Comp range disclosure / pay transparency laws**
A growing set of U.S. state/city laws (California, Colorado, New York, Washington, and others) requiring employers to disclose a salary range in job postings; the EU's Pay Transparency Directive imposes similar obligations across EU member states with a 2026 transposition deadline.
*Tool relevance:* Directly determines whether comp data can even be scraped from a posting at all — jurisdiction matters, and a tool should expect comp fields to be present for some postings and absent for others purely due to where the job/company is legally required to post.
*(a) — the laws themselves are a matter of public record; which specific jurisdictions currently require it is a moving target and should be verified against current statute, not assumed static.*

**73. Range padding / compliance-range widening**
The practice of posting an unrealistically wide salary range (e.g., $80K–$180K for one role) to technically satisfy a pay-transparency law without disclosing the actual expected/target pay.
*Tool relevance:* Means a disclosed "comp range" field can be nearly useless for matching purposes even when present and legally compliant — a tool should treat very wide ranges as a lower-confidence data point.
*(b) — widely discussed and observed by practitioners and in trade press, but not something companies label or admit to; inferred from range width, not confirmed motive.*

**74. Boilerplate JD / templated JD**
A job description built from a reused company or ATS-provided template with minimal role-specific customization, often signaled by generic mission-statement paragraphs and copy-pasted "requirements" lists across many postings from the same employer.
*Tool relevance:* Boilerplate-heavy postings carry less real signal about the actual day-to-day role than a bespoke one — worth a tool distinguishing when assessing how much to trust the posting text as ground truth.
*(b) — a real and commonly observed pattern, but "how boilerplate is too boilerplate" is a judgment call, not a defined threshold.*

**75. Kitchen-sink JD / "unicorn" requirement**
A posting listing an unrealistic combination of requirements (e.g., 10+ years of experience with a technology that's existed for 5, or a senior individual contributor expected to also manage a team and do strategy) — usually a sign of a poorly scoped role or multiple stakeholders' wishlists merged without editing, rather than necessarily a fake posting.
*Tool relevance:* Distinguishes "poorly written but real" from "fake" — a tool should be careful not to flag an unrealistic requirements list as a validity red flag on its own, since it's extremely common in genuine postings.
*(b) — a widely recognized pattern among recruiters and candidates, but informal; no formal threshold for "unrealistic."*

**76. Years-of-experience (YOE) requirement**
A stated minimum years of experience, notoriously inconsistent as a seniority proxy (a YOE cutoff says nothing about what was actually done in those years) and often set arbitrarily high by hiring managers or generated automatically by JD-writing tools.
*Tool relevance:* A weak, gameable field for level-matching that a tool should weight below actual scope/responsibility signals in the posting.
*(a) — the field itself is standard; its unreliability as a true seniority signal is well-known practitioner consensus, flagged as judgment rather than a measured fact.*

**77. Purple squirrel**
Recruiter slang for an idealized candidate who fits every listed requirement — implying such a person is functionally nonexistent (or grossly underpaid relative to their actual worth if they do exist), and that the posting's requirements are unrealistic.
*Tool relevance:* Direct vocabulary link to "kitchen-sink JD" (75) — a term the tool's output or a coaching layer might use when explaining to a candidate why they shouldn't be discouraged from applying despite not meeting every listed bullet.
*(a) — genuinely standard recruiter slang, universally recognized in the field.*

**78. Spray and pray**
Slang used on both sides: candidate-side, it means mass-applying to large numbers of postings with the same generic resume rather than tailoring applications; recruiter-side, it can also describe blasting the same InMail/outreach message to a large, untargeted list of candidates.
*Tool relevance:* Names the low-quality, low-conversion search behavior a coaching-oriented tool should generally be steering candidates away from, in favor of targeted, tailored applications and networking.
*(a)*

**79. Black hole / "application black hole" / "resume black hole"**
Candidate-side slang for the experience of submitting an application and receiving no further response of any kind, ever — not even an automated rejection.
*Tool relevance:* The subjective candidate experience that motivates demand for exactly this kind of validation tool in the first place — silence being uninterpretable is the core pain point.
*(a)*

**80. Bait-and-switch posting**
A posting that substantially misrepresents the actual role, pay, or conditions to attract applicants, only for the real terms to be revealed later (e.g., commission-only "base salary" jobs, or a posting for one role that's actually recruiting for a different, less desirable one) — distinct from a ghost job because there IS a real position, just not the one advertised.
*Tool relevance:* A third distinct "posting is misleading" category alongside ghost jobs and stale listings — the role is real and fillable, but validating it requires checking the terms match the pitch, not just checking that hiring intent exists.
*(a) — the pattern is well recognized, especially associated historically with certain commission-based sales/insurance recruiting; the term itself is informal/practitioner slang rather than a codified category.*

---

### Terms flagged as genuinely uncertain rather than guessed at

- The "70–80% of jobs are filled through networking / never posted" statistic underlying "hidden job market" (#21) — ubiquitous in career-coaching content, but flagged as lacking confident empirical grounding or a single traceable, methodologically sound source; the underlying phenomenon is real, the specific number is folklore.
- The exact computation behind platform "actively hiring/recruiting" badges (#63), e.g., LinkedIn's — the subagent knows these exist and roughly what they're meant to signal, but not the underlying algorithm.
- Any precise, current legal/regulatory definition of "ghost job" — as far as the subagent knows there is none in U.S. law; it's a practitioner/media-coined term with fuzzy, contested boundaries.
- Current jurisdiction list for pay-transparency laws (#72) — named examples with confidence, but did not attempt a complete, currently-accurate list, since that would need verification against current statute.

### Terms considered and excluded as out of scope

- Quiet hiring / quiet quitting — internal talent-management strategy, not a job seeker's search behavior or an external posting's validity state.
- OFCCP/EEO compliance reporting categories — protected-class reporting obligations, not search characterization or posting-validity detection.
- Interview-process vocabulary (loop, panel interview, case interview, take-home assignment) — happens after a posting/req is already confirmed real.
- Onboarding/pre-boarding terminology — post-offer process, downstream of search-and-validate.
- Specific ATS product stage-naming conventions — implementation detail of individual software products, not cross-industry vocabulary.
- Equity/compensation-structure minutiae (vesting cliffs, ISO vs. RSU tax treatment, 409A valuations) — relevant to offer negotiation once a real opportunity is in hand, not to searching for or validating that it exists.

## Audit (second pass, 2026-09-15)

Checked against reputable sources via live web search. Priority given to
the domain's own self-identified most-load-bearing area (ghost jobs and
posting-validity signals, which is close to the core of what JobMux's
signal-fusion/adaptive modules already try to do) and to concrete,
checkable claims elsewhere in the glossary.

**Confirmed exactly:**

- **"Purple squirrel" (#77).** Confirmed as genuine, standard recruiter
  slang — and more precisely sourced than the glossary's own (a) label
  claimed: the term was specifically coined by A. Camilleri in 2000, not
  just organically emergent jargon. Source:
  [Taggd, "What Is a Purple Squirrel?"](https://taggd.in/hr-glossary/purple-squirrel-perfect-candidate/).
- **"Silver medalist" (#16).** Confirmed exactly as described — a
  finalist candidate not hired for one req, deliberately tagged and
  re-engaged for future openings. Source:
  [Lever, "Why You Should Prioritize Silver-Medalist Candidates"](https://www.lever.co/blog/silver-medalist-candidates/).
- **PERM labor certification (#55).** Confirmed accurate in every
  specific: DOL process, employer must prove no minimally qualified U.S.
  worker is available, mandatory 30-consecutive-day state job order plus
  10-business-day physical posting notice, three of ten additional
  recruitment methods, genuine-review and documentation requirements,
  followed by Form I-140. Source:
  [Nolo, "PERM Recruitment Requirements and Process for Foreign Hires"](https://www.nolo.com/legal-encyclopedia/employer-recruitment-requirements-under-perm.html).

**One correction — a hedge that's now resolvable, and the resolution is
messier than "confirmed":**

- **EU Pay Transparency Directive (#72).** The glossary's "2026
  transposition deadline" hedge was correct to flag as needing
  verification, and the actual situation is more specific and more
  fragmented than a flat "2026 deadline" suggests. The deadline was **7
  June 2026** — which has already passed as of today — and compliance is
  scattered: only **4 of 27** member states (Slovakia, Italy, Lithuania,
  Malta) met it; several (Netherlands, Sweden, Czech Republic, Denmark)
  delayed to 1 January 2027; Sweden has paused implementation entirely
  pending EU-level renegotiation; roughly ten states have no published
  draft at all as of the search date. **Practical implication:** whether
  a given EU job posting is currently subject to enforced
  pay-transparency requirements depends heavily on which member state
  it's in *right now*, not on the Directive's mere existence — a tool
  built assuming uniform EU-wide comp disclosure by this point would be
  wrong for the large majority of member states, which matters directly
  if JobMux's board-heuristic/board-ML modules ever ingest EU postings and
  try to read a comp field from `schema.org`'s `baseSalary` or similar.
  Source:
  [Morgan Lewis, "EU Pay Transparency Directive: The Deadline for Transposition Has Passed—What Now?"](https://www.morganlewis.com/pubs/2026/06/eu-pay-transparency-directive-the-deadline-for-transposition-has-passed-what-now);
  [Trusaic, Member State Transposition Monitor](https://trusaic.com/resources/resources-eu-pay-transparency-directive-member-state-transposition-monitor/).

**A completeness addition to the domain's own flagged priority area:**

- **Ghost job prevalence (#49).** The glossary appropriately declined to
  cite a prevalence figure, noting "no standardized definition... estimates
  vary widely." That caution holds up and is reinforced, not contradicted,
  by what this audit found: real, dated, named surveys exist with
  concrete numbers, but they don't agree with each other because they
  measure different things under the same word. Clarify Capital's January
  2025 survey of 1,000 employers found roughly one in three admit posting
  with no current intent to hire, and 43% admitted doing so partly to
  project growth; separately, MyPerfectResume's June 2025 analysis found
  roughly 30% of postings (over 2.2 million roles) never resulted in a
  hire, describing a stable 28–38% "phantom gap" since 2021. These are two
  different measurements — self-reported employer intent versus
  observed hire outcomes — that happen to land on similar-sounding
  round numbers, which risks a tool treating them as the same statistic
  when they aren't. Worth adding to the entry as a concrete illustration
  of exactly the definitional inconsistency the glossary already warned
  about, not as a settled prevalence rate. Sources:
  [MyPerfectResume, "Ghost Job Economy" release](https://www.prweb.com/releases/myperfectresume-reveals-the-ghost-job-economy-1-in-3-us-job-listings-lead-nowhere-302609641.html);
  secondary reporting on the Clarify Capital survey cross-checked across
  multiple trade outlets rather than traced to a single primary report —
  flagged as such rather than treated as fully verified.

**Not independently re-verified:**

- **ATS vendor names and general mechanics** (#1–#15) — extremely
  well-known, not individually re-sourced.
- **"Culture add" as a reframing of "culture fit" (#41)** — consistent
  with widely reported HR-industry discourse; not independently
  re-sourced to a specific origin.
- **U.S. state-level pay-transparency laws named (#72)** — California,
  Colorado, New York, Washington are all real and current per general
  knowledge; not individually re-verified against current statute text
  in this pass, unlike the EU directive which was checked in detail.

**Net result:** the domain's own self-identified hardest area (ghost-job
vocabulary and validity signals) held up well — no term was found wrong,
and the one prevalence-statistics addition reinforces rather than
undermines the glossary's own caution. The one real correction (the EU
directive) is a hedge about an approaching deadline that has since passed
— and passed messily rather than cleanly, which is itself worth knowing
rather than assuming a clean "in force now."

## Not yet done

- **Mapping onto JobMux's own schema.** `design/architecture.md` §1.4's
  confidence-label vocabulary (source: board-heuristic/board-ML/
  adaptive/analog; state: confirmed/contradicted[now superseded]/
  pending/unable-to-obtain) and §1.2's near-miss/false-positive/
  domain-gap persistence taxonomy are the two places this glossary's
  terms would most plausibly connect — several entries here (feed/
  syndication lag, #59; already-filled-internally/"zombie listing", #53;
  req-on-hold/frozen req, #57) look like they could map onto specific
  evidence-signal states or specific reasons a listing lands in one of
  those three persistence buckets, but no such mapping has been attempted
  in this pass.
- **Cross-check against `jobmux/verification.py`'s existing false-positive
  matching** (word-boundary text matching plus `OccupationalCategoryExclusion`)
  — this glossary's ghost-job/backfill/evergreen/repost taxonomy (#49–58)
  is a different kind of false-positive than the title-matching false
  positives that module currently handles (e.g., "aid" matching inside
  "maid"), and whether/how the two taxonomies should relate is an open
  question, not assumed either way.
- **Whether `schema.org`'s `validThrough` gap** (already a known,
  independently-confirmed gap per `CLAUDE.md`'s build-order notes, in both
  JobSpy and `ats-scrapers`) is best closed using any of this glossary's
  freshness signals (posting age, feed lag, applicant count) as a
  fallback proxy, or left as a known limitation — not decided here.
