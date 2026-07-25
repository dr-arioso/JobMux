# ADR-0003: Attribute-level reconciliation (deferred) and the false-positive matching mechanism

**Status:** Accepted
**Date:** 2026-07-25
**Deciders:** Bill

## Context

`jobmux/signal_fusion.py`'s SUPERSEDED/discounting revision (same-day, this
session) left two open flags recorded in `jobmux/README.md`'s open-flags
section:

1. **Attribute-level reconciliation.** `reconcile()`'s frame of discernment
   is binary (available/unavailable). A disagreement about a specific
   attested-attribute *value* — two different closing dates, two different
   salary figures — only ever enters that frame via each source's downstream
   implication for status; the literal values in conflict are never
   reconciled directly.
2. **The false-positive matching mechanism.** `verification.py`'s
   `is_confirmed_false_positive()` is plain case-insensitive substring
   containment on a listing's title or employer field — a first
   instantiation flagged since its own commit, with SOC-code alignment
   (`design/architecture.md` §1.6) named as a live but unbuilt candidate.

A design discussion examined several resolution paths for each, including at
least one deliberately aggressive ("spicy") option per issue, before deciding
what to build now versus record for later.

## Decision

**Attribute-level reconciliation: defer, with a recommended shape recorded
for whenever it's actually needed.** No new machinery gets built now. A
specific value disagreement stays recorded only in each signal's `basis`
(quoted text), left to frontier-tier judgment to read and weigh — the same
treatment any other signal-level judgment call already gets. If a real,
recurring case later demonstrates this is a genuine problem (the same bar
case 1's SWCD sweep had to clear before `reference/adaptive-module.md` got
written), the recommended shape is *not* a family of bespoke per-attribute
reconcilers, but a generalization of `reconcile()` itself into an n-ary
evidential reconciliation function — `reconcile_attribute(signals, equals)`,
where `equals` is a caller-supplied comparison (exact match for a categorical
field, day-tolerance for a date, percentage-tolerance for currency) — that
clusters signals by that equality, weighs each cluster by reliability the
same way `reconcile()` already does, and returns either a clear winner or an
explicit `Disputed` result carrying every distinct value and who's behind
each one. This keeps the codebase's one evidential-combination idea reused
rather than reinvented per attribute type.

**The false-positive matching mechanism: three concrete, complementary
actions, and one explicit non-action.**

1. **Harden the existing substring matching.** Normalize case and
   punctuation, match on word boundaries rather than raw containment, and
   add light fuzzy tolerance for phrasing drift ("Environmental Svcs" vs.
   "Environmental Services"). This is worth doing on its own merits — this
   discussion surfaced a real, live precision bug in the current
   implementation (a short pattern like `"aid"` matches inside `"maid"`
   under plain substring containment), which needs fixing regardless of
   anything else decided here.
2. **Consume schema.org's `occupationalCategory` field when present.**
   schema.org's own `JobPosting` spec recommends populating this field with
   an O*NET-SOC code — `design/architecture.md` §2.3 already designates
   "extracting a schema.org JobPosting block from structured data when
   present" as small-model-tier work, so this is close to a drop-in win
   wherever a listing's structured data actually carries it, falling back
   to (1) when it doesn't. This is SOC-alignment's real, buildable form —
   not a separate classification pipeline, which the original "SOC-based
   matching" framing would have required for the common case where no
   structured `occupationalCategory` is supplied at all.
3. **Scope board-heuristic/board-ML queries to the source platform's own
   category/occupation facet at query time**, where the platform exposes
   one. Independent of the registry and worth doing regardless of anything
   else — it prevents most category errors from ever entering the pipeline
   for that subset of results, rather than catching them after the fact.
   Does not touch the adaptive module's employer-direct checks at all
   (those have no category facet to filter by), so it complements the
   registry rather than retiring it.
4. **Not doing, absent concrete need: moving pattern-matching itself to a
   small-model semantic check.** This would be a real, documented departure
   from `design/architecture.md` §2.3's classification of "matching a
   listing against an already-confirmed exclusion pattern" as
   algorithmic-tier, not a same-tier refinement — it changes the tier, not
   just the technique. Worth revisiting only if (1)+(2)+(3) demonstrably
   aren't enough in practice, not adopted preemptively.

## Options Considered

### Issue 1 — attribute-level reconciliation

**Option A — status quo, prose-only (chosen, for now).** No new
abstractions; a value disagreement lives only in free-text `basis`.
Doesn't scale past a handful of listings, but nothing about this project's
current scale has demonstrated it needs to yet.

**Option B — generalize `reconcile()` into an n-ary evidential function
(recommended shape, if/when built).** One reused mechanism instead of N
bespoke ones; the real cost is that combining more than two competing
hypotheses is a bigger lift than the current binary-frame code, and the
`equals` comparison still needs per-type tuning even if the surrounding
machinery isn't bespoke.

**Option C — bespoke reconciliation per attribute type.** More precise
per type (dates, currency, and categorical fields don't share comparison
semantics), more code to maintain, and the option most likely to sprawl.

**Option D — spicy, considered and not adopted: never collapse attributes
into scalars at all.** Every attested attribute becomes its own permanent,
open evidence-signal set, exactly like status already is; "the current
value" becomes a query-time view function, never a stored field. Maximally
consistent with the project's lossless philosophy, and never needs new
reconciliation code for a new attribute type — but a real architectural
earthquake touching the §2.2 context-pack contract, `scoring.py`'s
scalar-attribute assumption, and every downstream consumer that currently
expects a plain value. Recorded as the honest end state if attribute-level
disagreement is ever established as a chronic problem, not a proportionate
response to a single good hypothetical.

### Issue 2 — false-positive matching mechanism

**Option A — harden substring matching (adopted).** Cheap, stays
algorithmic-tier, and fixes a real correctness bug (`"aid"` inside
`"maid"`) independent of anything else. Still fundamentally lexical and
will always be somewhat brittle against phrasing no pattern list
anticipates.

**Option B — SOC-code alignment via schema.org's `occupationalCategory`
(adopted, opportunistically).** Grounded in a standard already adopted
elsewhere in the project (`design/architecture.md` §1.6); free when
structured data supplies it, via extraction work `architecture.md` §2.3
already designates as small-model-tier. The original framing of this
option (infer a SOC code from title text when none is supplied) doesn't
eliminate the matching problem, it relocates it — not adopted for that
case; falls back to Option A instead.

**Option C — small-model semantic matching against confirmed patterns
(not adopted).** More robust to phrasing variance than any string rule,
but a genuine tier change from what `architecture.md` §2.3 already decided
("matching against an already-confirmed pattern" is algorithmic), with
real per-listing cost and latency at scale. Not adopted without a
concrete demonstration that Options A and B fall short.

**Option D — spicy, adopted as a complement, not a replacement: prevent
false positives at the query rather than catching them after the fact.**
Scope board-heuristic/board-ML queries to the source platform's own
category facet, where one exists. Could eliminate most category errors
for that subset of results at the source. Doesn't touch the adaptive
module's employer-direct checks at all, and trusts a third party's own
classification, which could itself be coarse or wrong — the same
"authority can be wrong" lesson as the SUPERSEDED/discounting revision,
one layer up. Adopted as a genuine complement to the registry, not
framed (as it might first appear) as a way to retire it.

## Trade-off Analysis

Issue 1's options split cleanly on proportionality: Option A costs nothing
and has cost nothing so far, since no real case has yet shown attribute-level
disagreement is a recurring problem (unlike case 1's SWCD sweep, which
concretely forced `reference/adaptive-module.md` into existence before
anyone had to guess). Option D is the philosophically purest answer but the
most expensive one to retrofit later if adopted prematurely, so it's
recorded rather than built. Option B is deliberately named as the *shape* to
reach for the day Option A's cost stops being zero — cheaper to decide now,
while the reasoning is fresh, than to re-derive later.

Issue 2's options aren't mutually exclusive, which is why three of four get
adopted together rather than one being chosen over the others: A fixes a
real bug regardless of anything else; B is free wherever the data already
supports it; D prevents a whole class of error upstream of the registry
entirely, for the subset of results it can reach. C is the only one that
costs a tier violation to adopt, which is why it alone is held back pending
evidence the other three aren't sufficient.

## Consequences

- `jobmux/README.md`'s open-flags section, `CLAUDE.md`'s build-order status,
  and `decisions/README.md`'s index need updating once Action Items 1–2
  below actually land in code (not done as part of writing this ADR).
- Option D for Issue 2 (query-level category scoping) has no artifact to
  attach to yet — `reference/board-heuristic-module.md` and
  `reference/board-ml-module.md` don't exist. This decision is recorded now
  so whoever writes those reference implementations builds the scoping in
  from the start, rather than retrofitting it later.
- Attribute-level reconciliation (Issue 1) stays an open flag in
  `jobmux/README.md`, not a closed one — this ADR records a decision to
  defer, not a decision that resolves it.

## Action Items

1. [ ] Harden `verification.py`'s `FalsePositivePattern`/
   `is_confirmed_false_positive()`: normalize case/punctuation, match on
   word boundaries, add light fuzzy tolerance; fix the `"aid"`-matches-
   `"maid"` precision bug specifically; add regression tests for both the
   hardening and the bug fix.
2. [ ] Extend false-positive matching (and, more generally, occupation-
   category extraction) to consume schema.org's `occupationalCategory`
   when a listing's structured data supplies it, falling back to Action
   Item 1's hardened substring matching when it doesn't.
3. [ ] Not independently actionable yet: when `reference/board-heuristic-
   module.md` and `reference/board-ml-module.md` get written, scope their
   query construction to the source platform's own category/occupation
   facet where one exists (Issue 2, Option D).
4. [ ] No code action for Issue 1 now. Revisit only once a real, recurring
   attribute-level-disagreement case is observed; the recommended shape
   (a generalized `reconcile_attribute()`, Issue 1 Option B) is recorded
   above for that future session.
5. [ ] Once Action Items 1–2 land: update `jobmux/README.md`'s open-flags
   section, `CLAUDE.md`'s build-order status, and this ADR's own
   checkboxes.
