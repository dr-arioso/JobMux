# JobMux — Verification & Escalation Policy (Reference Implementation)

**Companion to `concept.md`, `architecture.md`, `fragmented-employer-module.md`, and `signal-fusion-module.md`.** This file instantiates the verification/trust layer named in `architecture.md` §1.3 as a standing, fixed policy — the general form that every evidence-gathering module applies rather than re-deriving for itself. `fragmented-employer-module.md` §6 and `signal-fusion-module.md` §2–§3 already contain module-specific instantiations of this same policy (a guessed-careers-page ladder, an analog-lead ladder); this file is the canonical general version those sections instantiate, not a replacement for either. A future evidence-gathering module (broad ATS/job-board, values-research) should instantiate this policy the same way, rather than writing its own verification rules from scratch.

As with the companion files: this file states the current policy as decided. When it changes, rewrite the relevant section in place.

## 0. Scope

This policy governs how any result from any evidence-gathering module (`architecture.md` §1.2) becomes trustworthy enough to reach the plan stage (`architecture.md` §1.4). It applies uniformly across all four evidence kinds `architecture.md` §1.1 defines — attested attributes, inferable attributes, reference-data lookups, and analog-sourced signals — and across every module, not just the two with reference implementations written so far. Nothing about this policy is module-specific; what's module-specific is *how* a given module instantiates the escalation ladder (§2) for its own typical failure mode, which is exactly what `fragmented-employer-module.md` §6 and `signal-fusion-module.md` §2 already do.

## 1. The core rule: a signal can motivate a check, it can never be the check

Anything not directly loaded, confirmed, or obtained through direct human contact is a **signal**, not a **finding** — a search-tool snippet, a cached search-index result, a directory listing not yet independently confirmed, a rumor or tip obtained through AnalogSearch (`architecture.md` §1.2). A signal is real information and a legitimate reason to spend effort checking further. It is never, by itself, sufficient grounds to record a status change.

**This cuts both ways.** A result that looks newly gone gets the same direct confirmation as a result that looks newly available. There is no structural reason to be more suspicious of good news than bad, and treating the two asymmetrically — demanding proof a listing reopened while accepting a search snippet's word that it closed — is itself a bias this policy exists to rule out. The discipline is the same regardless of which direction the apparent change points.

This rule extends without modification to analog-sourced signals (`signal-fusion-module.md` §1–§2): a lead obtained through direct human contact is still a signal until it's been reconciled and recorded as a finding, not automatically upgraded to a finding just because it came from a human rather than a search tool. Two unconfirmed signals held together are still two signals, not one finding — see `signal-fusion-module.md` §3 for what reconciling them into a single confidence-rated status actually requires.

## 2. The escalation ladder (general form)

When a source comes up empty, broken, or unreachable on a first attempt, the failure is treated as **inconclusive**, not as confirmation that nothing is there. Work through the following in order and stop at whichever step resolves it:

1. **Re-derive from the source's own structure.** If a guessed path, URL, or query came up empty, don't re-guess a second variant blindly — go to the source's own navigation, structure, or index (a site's actual menu or footer links, a platform's own search or browse feature) and read what it actually offers.
2. **Run a targeted, scoped search.** A search restricted to the specific source (a site-scoped search, a platform-internal search) surfaces material that isn't linked from the source's own current navigation, or catches cases where the source has moved without carrying old paths forward.
3. **Check a trusted third-party directory for that category**, if one exists — an association's member directory, a licensing or governing body's roster, a category-specific aggregator. These are often more current than a single source's own structure, particularly for a small or informally-run source.
4. **If none of the above resolves it, record the result distinctly as unresolved** — never silently as a confirmed negative, and never folded into the same bucket as a result that was actually confirmed empty or closed. "Nobody could find it" and "there is definitely nothing there" are different findings; recording them identically destroys information a later pass would need.

This ladder generalizes directly from real, repeated failures where a step-1 guess came up empty and was wrongly treated as a confirmed negative, when the real material was one step further down this same ladder. It is stated here in its general form specifically so a new module doesn't have to rediscover that pattern independently — `fragmented-employer-module.md` §6 and `signal-fusion-module.md` §2 are this ladder instantiated for two different typical failure shapes (a guessed employer careers-page path; an unobtained analog lead), not two different policies.

## 3. "Unable to verify" is a real, distinct outcome

Step 4 of the ladder above produces a status that must be recorded as its own thing, not as a variant of "confirmed closed" or quietly dropped from a report. A result that stays unresolved after the full ladder is genuinely different from one that resolved negative, and collapsing the two together removes exactly the information a later recheck or a human reviewer would need to know where to spend more effort. This is not a hedge to soften an otherwise-confident report — it is the accurate description of what's actually known.

## 4. Volatility tiers relate to trust as a scheduling tool, not a stability claim

A volatility tier (`architecture.md` §1.4) governs how often a row gets rechecked. It says nothing about how much a currently-recorded status should be trusted between checks. A row tagged as low-volatility is not thereby a row that's safe to skip when other, higher-tier rows are already being checked in the same pass — the tier exists to allocate scheduling effort under time pressure, not to license skipping a check that's already cheap to run. Treating a low-volatility tag as a confidence claim rather than a scheduling default is a category error this policy explicitly rules out: a tier is a statement about how often a *type* of source tends to change, derived from limited data early in a search and refined as more checks accumulate — never a statement that a specific row's current status is more likely correct.

This applies with equal force to `signal-fusion-module.md`'s **Conflicting** and **Unable to verify** outcomes: neither should be read as low-priority simply because they don't yet carry a volatility tier of their own (see that file's §7, an open question this policy doc does not resolve).

## 5. Rigor is never traded for time or budget

Cost-aware strategy selection (`architecture.md` §1.5) governs *how much* gets searched and how many strategies get tried under a given budget — it never governs *how rigorously* any single finding gets confirmed once a check is actually being run. A tight budget is a legitimate reason to check fewer rows; it is never a legitimate reason to check more rows at reduced rigor. Where a genuine time constraint means full verification isn't possible for everything a task would otherwise cover, the correct response is to verify a smaller set completely and say so plainly — not to quietly apply a lighter standard across a larger set and let hedged language stand in for the gap. A time or budget constraint is a reason to narrow scope explicitly, never a reason to silently narrow rigor.

## 6. Worked walkthrough (hypothetical, not a validated case)

The following is invented for illustration and marked as such throughout — it is not a report of anything actually run.

> Suppose a guessed URL for a small employer's careers page returns a 404. Per §2, the next step is not a second guess at a different path — it's loading the employer's actual homepage and reading its real navigation, which turns up a careers page under a menu label that didn't match the first guess at all.
>
> Suppose, separately, a search-tool result surfaces a snippet suggesting a previously-closed listing has been reposted. Per §1, that snippet is a signal, not a finding — a direct page load is required before recording any status change, exactly as it would be required if the snippet instead suggested a listing had newly closed.
>
> Suppose a full pass through §2's ladder for a third source — re-derived navigation, a scoped search, a trusted directory — still turns up nothing conclusive. Per §3, this gets recorded as **unable to verify**, distinct from a confirmed-closed status, flagged for a future pass rather than folded silently into either bucket.

## §7 — open question

`architecture.md` §1.4 and `fragmented-employer-module.md` §10 both leave the closed vocabulary for confidence labels undecided (how a directly-confirmed result, an analog-resolved result, and an unable-to-verify result should each be distinctly tagged in the tracking schema itself, versus recorded as free text). This policy doc depends on that vocabulary existing — §3's "unable to verify" and §1's signal/finding distinction both need a place to actually live in the schema — but, consistent with the discipline both prior flags already established, deciding it here would preempt the recombination/tracking layer (`concept.md` §6, step d), where it's already been correctly deferred. Restated here rather than silently assumed resolved: the session that writes the recombination/tracking template should treat this policy's §1 and §3, `fragmented-employer-module.md` §10, and `signal-fusion-module.md` §3 and §7 as the full set of inputs to that one decision, not four separate open questions to resolve independently.
