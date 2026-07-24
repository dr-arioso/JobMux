# ADR-0002: Build sequencing, test strategy, and topology for remaining work

**Status:** Accepted
**Date:** 2026-07-23
**Deciders:** Bill

## Context

Two facts about the project's actual state should drive how the remaining build steps get sequenced, more than `concept.md` §6's original suggested order does on its own:

First, nothing in this repo is runnable software yet. `elicitation.md`, `fragmented-employer-module.md`, `signal-fusion-module.md`, and `verification-escalation-policy.md` are prose a model follows at runtime, not code. The one part of the design that's ordinary, deterministic software — `architecture.md` §2.3's algorithmic tier (proportional reallocation, Bradley-Terry conversion, Chebyshev-style scoring, context-pack generation via event-log fold, date-diffing, cost-of-living ratio conversion) — hasn't been implemented at all.

Second, `internal/traceability.md` (not open-source material, but a legitimate internal check on the design) shows real validation is concentrated almost entirely in case 1, run manually, not through a Skill. Two pieces have **zero** real-world mileage: architecture §1.5 (subagent-based model tiering, scheduled-tasks-driven autonomy) and the actual fusion mechanism in `reference/signal-fusion-module.md` (the digital-trace failure mode is validated; reconciling it against an independent analog lead has never been run for real).

`concept.md` §6 step 5's original order finishes (d) the recombination/tracking schema, then (e) `SKILL.md` assembly, then (f) a sanity check — all before any of this gets exercised. That's a reasonable default but it defers all empirical feedback to the very end, right where the two least-proven pieces most need early signal, and risks (d)'s schema getting finalized against assumptions about runtime behavior that haven't actually been tested.

## Decision

Combine two of the strategies considered below: **risk-first spikes** on layer 1.5 and the case-4 fusion mechanism, run as a parallel track alongside an **algorithmic-tier-first** implementation of §2.3's deterministic functions. Both proceed before (d) the recombination/tracking schema is finalized, so that schema reflects what the spikes actually learn rather than what the design docs currently assume.

Sequencing: (1) algorithmic tier, as pure functions with a real test suite — unblocked, doesn't depend on anything else, cheapest possible win. (2) In parallel or immediately after: a throwaway spike of layer 1.5 (wire one subagent call with a model override, one `scheduled-tasks`-triggered recheck) and a throwaway pilot of the case-4 fusion mechanism (one real or simulated digital-trace-plus-analog-lead reconciliation, run end to end). (3) Only then, write (d)'s schema, informed by whatever the spikes surfaced. (4) (e) `SKILL.md` assembly. (5) (f) plain-repo sanity check.

Test strategy: the algorithmic tier gets a conventional unit-test suite (pytest or equivalent) — it's the one place in this project where the standard test pyramid applies cleanly. The spikes get no formal test suite; a spike's success criterion is "did we learn something," not "does it pass," consistent with XP spike discipline — findings get written down and feed (d), the throwaway code itself doesn't need to survive.

POCs: the two spikes *are* the POCs — a real (or clearly-labeled-simulated) run of subagent tiering plus scheduled-recheck autonomy, and a real (or clearly-labeled-simulated) run of digital-trace/analog-lead reconciliation producing one of `reference/signal-fusion-module.md` §3's confidence-rated outcomes.

Topology: narrow-and-deep for the two spikes (one unknown at a time, full depth, explicitly throwaway); the algorithmic tier is its own small, complete, real module — narrow in scope but built to keep, not to throw away.

## Options Considered

### Option 1: Spec-complete-first (concept.md §6's literal order)

| Dimension | Assessment |
|---|---|
| Risk timing | Worst — all empirical feedback deferred to the end |
| Cost if wrong | High — (d)'s schema and (e)'s assembly both get built on untested assumptions |
| Effort to reach first working thing | Highest |

**Pros:** simplest to describe, no reordering to justify, consistent with existing discipline of finishing what's started.
**Cons:** classic Brooks "second-system" shape — maximal design maturity before any working software exists.

### Option 2: Risk-first spikes (Boehm spiral / XP spike) — adopted, combined with Option 5

Attack the two zero-validated unknowns first, narrow and deep, throwaway.

**Pros:** directly matches `internal/traceability.md`'s own stated priority — the layer with the least real evidence gets attention first. Cheap: a spike is explicitly not meant to be polished.
**Cons:** spike code doesn't ship; some effort produces no lasting artifact beyond what was learned.

### Option 3: Walking skeleton / tracer bullet (Cockburn; Hunt & Thomas)

One trivial synthetic candidate wired through every layer at minimum depth, kept and grown.

**Pros:** proves the layers compose at all; contract-testable at each seam (does elicitation's output validate against §2.2's context-pack shape?).
**Cons:** doesn't specifically target the two known-riskiest unknowns — a thin path through all layers could pass without ever exercising layer 1.5's autonomy or the fusion mechanism's actual judgment call.

### Option 4: Horizontal/shallow-everywhere prototyping

Stub every remaining piece (values-research module, broad-ATS module, tracking schema, a `SKILL.md` draft) simultaneously, at fake depth.

**Pros:** cheap way to surface interface mismatches and vocabulary collisions early — the kind of thing the real Branch-A/Bridge-B naming collision in `internal/traceability.md` was.
**Cons:** reveals nothing about whether any mechanism actually works, since nothing has real behavior.

### Option 5: Algorithmic-tier-first — adopted, combined with Option 2

Build §2.3's deterministic functions as a small, real, unit-tested library, independent of everything else.

**Pros:** the only part of this system amenable to conventional software testing; nearly free; doesn't block or get blocked by any other option.
**Cons:** de-risks nothing about the model-run layers, which are where the actual uncertainty lives.

### Option 6 — spicy, considered and deferred (not rejected): kill the spec, ship an ugly tracer bullet this week

Stop writing reference docs; in real, throwaway code, fake most of the sophistication (hardcode a persona instead of running the interview, hardcode weights instead of Bradley-Terry, fake AnalogSearch with a canned response) and get one candidate from input to a ranked list in an afternoon.

**Pros:** fastest possible empirical signal on whether the overall architecture holds together; directly counters the second-system risk Option 1 represents.
**Cons:** higher-variance bet — a fake AnalogSearch response can't actually validate the fusion mechanism's real judgment call, so it risks producing false confidence rather than real signal on the two things that most need it. Left off this decision as the chosen path because Option 2 already targets the same two unknowns with real (not faked) spikes at similar cost; Option 6 remains available if 2+5 stalls or the faster, cruder signal becomes worth more than the more targeted one.

## Trade-off Analysis

Option 1 is the only option that produces zero working software or empirical signal before (d) is finalized — given how concentrated the unvalidated risk already is (two specific, named layers, not the whole system), that's not a trade worth making. Option 5 is nearly free and adds real, lasting infrastructure regardless of what else happens, so it's included unconditionally rather than argued over. Between Options 2, 3, and 4 for the risk-bearing work: 3 and 4 both produce useful integration signal but neither specifically targets layer 1.5 or the fusion mechanism — a walking skeleton could technically "pass" without ever really exercising either. Option 2 is the only one of the three that's aimed directly at the two things `internal/traceability.md` flags as actually unproven, so it's the one adopted. Option 6 is the most aggressive de-risking move available but trades precision for speed in a way that could manufacture false confidence on exactly the mechanism (fusion) where that's most costly; it's recorded as a live alternative, not discarded.

## Consequences

- `concept.md` §6 step 5 (suggested build order) is rewritten in place to reflect this sequencing, per that file's own stated discipline of revising decisions rather than narrating them.
- (d)'s schema work is explicitly blocked on the two spikes' findings, not just the completion of (b)/(c) as the original order implied.
- The algorithmic tier becomes the first real code in this repo — a meaningful shift from "100% design/reference prose" to a project with an actual, if small, working component.
- Two pieces of throwaway spike code will exist briefly and then not ship — expected, not a sign of wasted effort, consistent with spike discipline.
- We'll need to revisit: whether the fusion-mechanism spike's real-world attempt (an actual analog contact, if one is available and appropriate to pursue) is feasible within this project's actual constraints, or whether it has to run simulated/hypothetical — and if simulated, how much weight its findings can actually carry into (d)'s schema design.

## Action Items

1. [x] Implement `architecture.md` §2.3's algorithmic tier as a small pure-function library with a unit-test suite — done, `jobmux/` (68 tests). Surfaced one open flag: `scoring.chebyshev_weighted_score()`'s formula is a first concrete instantiation of §1.1's required behavior, not a settled decision — see `jobmux/README.md`.
2. [ ] Spike layer 1.5: one subagent call via the Agent tool's model override, one scheduled-tasks-triggered recheck, written up as findings (not shipped code)
3. [ ] Pilot the case-4 fusion mechanism once, real or clearly-labeled-simulated, producing one of `reference/signal-fusion-module.md` §3's confidence-rated outcomes, written up as findings
4. [ ] Revise `reference/verification-escalation-policy.md` §7 and `reference/signal-fusion-module.md` §7's open questions in light of what the fusion pilot actually surfaces
5. [ ] Write (d) the recombination/tracking schema template, informed by 1–4
6. [ ] Proceed to (e) `SKILL.md` assembly and (f) the plain-repo sanity check
