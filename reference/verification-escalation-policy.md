# JobMux — Verification & Escalation Policy (Reference Implementation)

**Companion to `design/concept.md`, `design/architecture.md`, `reference/adaptive-module.md`, and `reference/signal-fusion-module.md`.** This file instantiates the verification/trust layer named in `design/architecture.md` §1.3 as a standing, fixed policy — the general form that every evidence-gathering module applies rather than re-deriving for itself. `reference/adaptive-module.md` §6 and `reference/signal-fusion-module.md` §2–§3 already contain module-specific instantiations of this same policy (a guessed-careers-page ladder, an analog-lead ladder); this file is the canonical general version those sections instantiate, not a replacement for either. A future evidence-gathering module (board-heuristic, board-ML, values-research) should instantiate this policy the same way, rather than writing its own verification rules from scratch.

As with the companion files: this file states the current policy as decided. When it changes, rewrite the relevant section in place.

## 0. Scope

This policy governs how any result from any evidence-gathering module (`design/architecture.md` §1.2) becomes trustworthy enough to reach the plan stage (`design/architecture.md` §1.4). It applies uniformly across all four evidence kinds `design/architecture.md` §1.1 defines — attested attributes, inferable attributes, reference-data lookups, and analog-sourced signals — and across every module, not just the two with reference implementations written so far. Nothing about this policy is module-specific; what's module-specific is *how* a given module instantiates the escalation ladder (§2) for its own typical failure mode, which is exactly what `reference/adaptive-module.md` §6 and `reference/signal-fusion-module.md` §2 already do.

## 1. The core rule: a signal can motivate a check, it can never be the check

Anything not directly loaded, confirmed, or obtained through direct human contact is a **signal**, not a **finding** — a search-tool snippet, a cached search-index result, a directory listing not yet independently confirmed, a rumor or tip obtained through AnalogSearch (`design/architecture.md` §1.2). A signal is real information and a legitimate reason to spend effort checking further. It is never, by itself, sufficient grounds to record a status change.

**This cuts both ways.** A result that looks newly gone gets the same direct confirmation as a result that looks newly available. There is no structural reason to be more suspicious of good news than bad, and treating the two asymmetrically — demanding proof a listing reopened while accepting a search snippet's word that it closed — is itself a bias this policy exists to rule out. The discipline is the same regardless of which direction the apparent change points.

This rule extends without modification to analog-sourced signals (`reference/signal-fusion-module.md` §1–§2): a lead obtained through direct human contact is still a signal until it's been reconciled and recorded as a finding, not automatically upgraded to a finding just because it came from a human rather than a search tool. Two unconfirmed signals held together are still two signals, not one finding — see `reference/signal-fusion-module.md` §3 for what reconciling them into a single confidence-rated status actually requires.

## 2. The escalation ladder (general form)

When a source comes up empty, broken, or unreachable on a first attempt, the failure is treated as **inconclusive**, not as confirmation that nothing is there. Work through the following in order and stop at whichever step resolves it:

1. **Re-derive from the source's own structure.** If a guessed path, URL, or query came up empty, don't re-guess a second variant blindly — go to the source's own navigation, structure, or index (a site's actual menu or footer links, a platform's own search or browse feature) and read what it actually offers.
2. **Run a targeted, scoped search.** A search restricted to the specific source (a site-scoped search, a platform-internal search) surfaces material that isn't linked from the source's own current navigation, or catches cases where the source has moved without carrying old paths forward.
3. **Check a trusted third-party directory for that category**, if one exists — an association's member directory, a licensing or governing body's roster, a category-specific aggregator. These are often more current than a single source's own structure, particularly for a small or informally-run source.
4. **If none of the above resolves it, record the result distinctly as unresolved** — never silently as a confirmed negative, and never folded into the same bucket as a result that was actually confirmed empty or closed. "Nobody could find it" and "there is definitely nothing there" are different findings; recording them identically destroys information a later pass would need.

This ladder generalizes directly from real, repeated failures where a step-1 guess came up empty and was wrongly treated as a confirmed negative, when the real material was one step further down this same ladder. It is stated here in its general form specifically so a new module doesn't have to rediscover that pattern independently — `reference/adaptive-module.md` §6 and `reference/signal-fusion-module.md` §2 are this ladder instantiated for two different typical failure shapes (a guessed employer careers-page path; an unobtained analog lead), not two different policies.

## 3. "Unable to verify" is a real, distinct outcome

Step 4 of the ladder above produces a status that must be recorded as its own thing, not as a variant of "confirmed closed" or quietly dropped from a report. A result that stays unresolved after the full ladder is genuinely different from one that resolved negative, and collapsing the two together removes exactly the information a later recheck or a human reviewer would need to know where to spend more effort. This is not a hedge to soften an otherwise-confident report — it is the accurate description of what's actually known.

## 4. Volatility tiers relate to trust as a scheduling tool, not a stability claim

A volatility tier (`design/architecture.md` §1.4) governs how often a row gets rechecked. It says nothing about how much a currently-recorded status should be trusted between checks. A row tagged as low-volatility is not thereby a row that's safe to skip when other, higher-tier rows are already being checked in the same pass — the tier exists to allocate scheduling effort under time pressure, not to license skipping a check that's already cheap to run. Treating a low-volatility tag as a confidence claim rather than a scheduling default is a category error this policy explicitly rules out: a tier is a statement about how often a *type* of source tends to change, derived from limited data early in a search and refined as more checks accumulate — never a statement that a specific row's current status is more likely correct.

This applies with equal force to `reference/signal-fusion-module.md`'s **Conflicting** and **Unable to verify** outcomes: neither should be read as low-priority simply because they don't yet carry a volatility tier of their own (see that file's §7, an open question this policy doc does not resolve).

## 5. Rigor is never traded for time or budget

Cost-aware strategy selection (`design/architecture.md` §1.5) governs *how much* gets searched and how many strategies get tried under a given budget — it never governs *how rigorously* any single finding gets confirmed once a check is actually being run. A tight budget is a legitimate reason to check fewer rows; it is never a legitimate reason to check more rows at reduced rigor. Where a genuine time constraint means full verification isn't possible for everything a task would otherwise cover, the correct response is to verify a smaller set completely and say so plainly — not to quietly apply a lighter standard across a larger set and let hedged language stand in for the gap. A time or budget constraint is a reason to narrow scope explicitly, never a reason to silently narrow rigor.

## 6. Worked walkthrough (hypothetical, not a validated case)

The following is invented for illustration and marked as such throughout — it is not a report of anything actually run.

> Suppose a guessed URL for a small employer's careers page returns a 404. Per §2, the next step is not a second guess at a different path — it's loading the employer's actual homepage and reading its real navigation, which turns up a careers page under a menu label that didn't match the first guess at all.
>
> Suppose, separately, a search-tool result surfaces a snippet suggesting a previously-closed listing has been reposted. Per §1, that snippet is a signal, not a finding — a direct page load is required before recording any status change, exactly as it would be required if the snippet instead suggested a listing had newly closed.
>
> Suppose a full pass through §2's ladder for a third source — re-derived navigation, a scoped search, a trusted directory — still turns up nothing conclusive. Per §3, this gets recorded as **unable to verify**, distinct from a confirmed-closed status, flagged for a future pass rather than folded silently into either bucket.

## §7 — resolved

Previously an open question: the closed vocabulary for confidence labels (how a directly-confirmed result, an analog-resolved result, and an unable-to-verify result should each be distinctly tagged in the tracking schema itself, versus recorded as free text) was left undecided by both `design/architecture.md` §1.4 and `reference/adaptive-module.md` §10. `design/architecture.md` §1.4 now resolves it, as the one place this policy doc's §1 and §3, `reference/adaptive-module.md` §10, and `reference/signal-fusion-module.md` §3 all pointed to: every evidence signal is tagged `(source, state, timestamp or quoted basis)`, with `state` one of confirmed / superseded / pending / unable-to-obtain (renamed from "contradicted" 2026-07-25 and narrowed to a signal retired by a later reading from the *same* source — never by a different source's disagreeing claim, which stays confirmed on both sides and is reconciled by reliability weighting instead; see `design/architecture.md` §1.4) — this policy's §3 "unable to verify" outcome and §1's signal/finding distinction are both direct instances of that vocabulary, not separate labels needing their own schema slot. A human-readable outcome label and a numeric confidence value are then derived algorithmically from a set of already-stated signal states (`design/architecture.md` §1.4, §2.3). What remains open — flagged, not resolved, in `reference/signal-fusion-module.md` §7 — is a narrower scheduling question: whether specific unresolved/contradictory outcomes should get a shorter recheck interval than their ordinary volatility tier. That's a §1.5 question, distinct from the vocabulary question this section was about.
