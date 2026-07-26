# jobmux/ — the algorithmic tier

Deterministic pure functions implementing architecture.md §2.3's algorithmic
tier — the parts of the design explicitly marked "no model call needed."
This is the first real, runnable code in this repo; everything else
(`reference/elicitation.md`, the evidence-gathering modules, the verification/
escalation policy) is prose a model follows at runtime, not software.

Built per `decisions/0002-build-sequencing-strategy.md` action item 1, as an
unblocked parallel track alongside the layer-1.5 and case-4-fusion spikes —
it depends on none of the design's still-unvalidated pieces.

## Modules

| Module | Covers | architecture.md |
|---|---|---|
| `reallocation.py` | Proportional / equal-split / protect-top-K weight redistribution | §1.1 |
| `tournament.py` | Pairwise win-counts → Bradley-Terry cardinal ranks; `next_pair_to_compare()` (decisions/0005) picks the next pair via information-gain-driven adaptive pairing (Crowd-BT-style) rather than round-robin | §1.1 |
| `scoring.py` | Chebyshev-style weighted scoring; qualification met/unmet percentage | §1.1 |
| `scheduling.py` | Volatility-tier recheck cadence; information-gain-per-cost action ordering (architecture.md §1.5 designates this the eventual consumer of §1.4's numeric confidence value, once something produces one — the code itself is unchanged and doesn't reference confidence yet) | §1.4, §1.5 |
| `verification.py` | Listing staleness date check; ledger value diffing; near-miss re-filtering; false-positive exclusion matching | §1.3, §1.2 |
| `compensation.py` | Cost-of-living salary normalization | §1.2 |
| `context_pack.py` | Event-log fold → the §2.2 context-pack JSON contract | §2.2, §2.4 |
| `signal_fusion.py` | Evidence-signal-set reconciliation — outcome label + numeric confidence value | §1.4 |
| `source_consent.py` | ToS-ambiguous-source exclusion filter, mechanical enforcement of a candidate's consent answer (decisions/0004 action item 3) | §1.2 |
| `consistency.py` | Mechanical mismatch detection between a priority's stated importance and its tournament-derived rank (decisions/0005 action item 5) | §1.1 |

## Running the tests

```
pip install pytest --break-system-packages   # or a normal venv
pytest
```

138 tests, all passing as of the 2026-07-26 `decisions/0005` spike-implementation pass (132 from the `decisions/0004`-item-3 exclusion filter and the `decisions/0005`-item-5 mismatch detector, plus 6 covering the new Crowd-BT-style pairing selection in `tournament.py`).

## Open flags surfaced by this work

`scoring.chebyshev_weighted_score()` implements architecture.md §1.1's
required *behavior* ("penalizing the worst-scoring highly-ranked priority
disproportionately... so a candidate's #1 priority can't be fully
cancelled out by a strong #3") using the augmented weighted Tchebycheff
scalarization (Steuer & Choo, 1983) — a real, standard multi-criteria
technique for exactly this property, but architecture.md itself doesn't
pin an exact formula. This is a first concrete instantiation, not a
settled decision. Two parameters (`top_k`, the number of top-ranked
priorities the penalty applies to, and `lambda_`, how strongly the penalty
term counts against the plain weighted sum) are exposed rather than
hardcoded, so this can be tuned or replaced without changing every call
site — but the choice of formula family itself should be confirmed or
revised by a future session touching architecture.md §1.1, the same way
every other open question in this project gets flagged rather than
silently decided.

`verification.FalsePositivePattern`/`is_confirmed_false_positive()` (added
2026-07-25, architecture.md §1.2's persistence taxonomy; revised same day
per `decisions/0003-attribute-reconciliation-and-false-positive-matching.md`
action items 1-2) no longer does plain case-insensitive substring
containment — that had a real precision bug (a pattern like `"aid"`
matched inside `"maid"`). Matching is now word-boundary containment on
normalized text, with an optional fuzzy fallback (`difflib.SequenceMatcher`,
stdlib) for phrasing drift, gated by a `min_fuzzy_pattern_length` guard
specifically so short patterns can't reintroduce the same bug through the
fuzzy path. `OccupationalCategoryExclusion`/`is_excluded_by_occupational_
category()`/`is_confirmed_false_positive_with_category()` add the SOC-code
path ADR-0003 recommended: schema.org's `JobPosting.occupationalCategory`
(recommended by schema.org's own spec to hold an O*NET-SOC code) is checked
first when a listing's structured data supplies one, falling back to the
hardened text matching when it doesn't — not a separate classification
pipeline, since architecture.md §2.3 already designates structured-data
extraction as small-model-tier work. All of this remains a first
instantiation of the matching mechanism, not a settled decision — moving
pattern-matching itself to a small-model semantic check was considered and
explicitly not adopted (ADR-0003) without concrete evidence this isn't
enough, since it would be a real tier violation, not a same-tier
refinement. *Confirming* that a given result actually is a false positive,
as opposed to a genuine near-miss, stays frontier-tier judgment regardless
of which matching mechanism this module implements.

`signal_fusion.py`'s `reconcile()` (added 2026-07-25, architecture.md §1.4's
evidence-signal-set reconciliation) implements the first concrete instantiation
of the numeric-confidence derivation formula action item 5 of `decisions/
0002-build-sequencing-strategy.md` left open. It went through two passes the
same session, the second prompted by a design discussion that caught a real
lossiness bug in the first (see the module's own docstring, "Revision" — the
first version's CONTRADICTED state silently zeroed out a disagreeing signal
instead of weighting it, in tension with architecture.md §2.4's "structurally
impossible to lose a prior value" and with the JobMux name itself: a
multiplexer combines channels, it doesn't discard them). Three things about
the current version are flagged the same way as scoring.py's formula and
verification.py's matching mechanism — first instantiations, not settled
decisions:

- **The confidence formula itself.** `reconcile()` combines every CONFIRMED
  signal's evidence via Dempster-Shafer combination (Shafer, 1976) over a
  binary {available, unavailable} frame, with each signal discounted by its
  own `reliability` coefficient (Shafer's own discounting operation) before
  combination, rather than a hand-picked number per outcome label. Three
  parameters (`confirmed_mass`, `conflict_threshold`, and each signal's own
  `reliability`) are exposed rather than hardcoded, in the same spirit as
  `chebyshev_weighted_score`'s `top_k`/`lambda_` — open to being replaced
  with a different formula family by a future session touching
  architecture.md §1.4, not a closed decision. The original `digital_only_cap`
  parameter is gone — a lone digital confirmation's discount is now
  whatever `reliability` its frontier-tier judgment assigned it, not a
  flat constant applied to every digital-only case regardless of context.
- **The `assertion` field.** architecture.md §1.4's decided signal shape is
  `(source, state, timestamp or quoted basis)` — it doesn't specify what a
  signal actually asserts, which reconciliation has to know to tell
  "agreeing" from "disagreeing." `signal_fusion.py` adds a fourth field
  (`assertion`: available / unavailable) to make this computable. This
  implementation found the binary sufficient for every outcome
  signal-fusion-module.md §3 names, but a future session could reasonably
  decide a richer vocabulary is needed — this is a gap-filling addition to
  the decided schema, not itself part of what architecture.md §1.4 settled.
  Related, and deliberately deferred rather than addressed
  (`decisions/0003-attribute-reconciliation-and-false-positive-matching.md`):
  a disagreement over a specific attested-attribute *value* (two different
  closing dates, say) is only captured here via each source's downstream
  available/unavailable implication, not the literal values in conflict —
  ADR-0003 records the recommended shape for reconciling attribute-level
  facts directly (a generalized `reconcile_attribute()`) for whenever a
  real recurring case actually calls for it, rather than building it
  speculatively now.
- **CONTRADICTED renamed to SUPERSEDED, and narrowed** (architecture.md
  §1.4) — reserved for a signal retired by a *later reading from the same
  `source`* (matched by that source's stable ID for the listing), never
  for a different source's disagreeing claim. Two different sources that
  disagree both stay CONFIRMED and get reconciled by reliability weighting
  instead of either one replacing the other. A repost occasionally getting
  reissued a new ID by the aggregator even for the same underlying opening
  is a real wrinkle this rename doesn't resolve — telling a genuine repost
  from a supersession can itself need judgment, not a pure ID match.

`source_consent.py` and `consistency.py` (added 2026-07-26, a token-budget-
constrained autonomous pass implementing two of `decisions/0004`/`0005`'s
still-open action items) are both deliberately narrow, mechanical modules
shaped after an existing pattern rather than invented from scratch —
`source_consent.py` mirrors `verification.py`'s `OccupationalCategoryExclusion`;
`consistency.py` mirrors `diff_ledger_value`. `consistency.py`'s own test
suite caught a real bug before commit: a `StatedImportance.LOW` priority
landing in last place within a very small (size-2) dimension was being
flagged as a false mismatch, since the floor threshold didn't yet account
for a dimension being too small for "near the top" to mean anything —
fixed by requiring the dimension be bigger than the floor itself.
`tournament.py`'s `next_pair_to_compare()` is the same pass's stretch goal
(decisions/0005 action item 3) — implemented and tested, not just
designed. `decisions/0005`'s other action items (revising
`design/architecture.md` and `reference/elicitation.md` in place, and
building the YAML topic library) remain open.

## Scope note

This module implements what architecture.md §2.3 explicitly lists as
algorithmic. `context_pack.py` builds the already-decided §2.2 JSON
contract, which is a different, narrower thing than the persistence/
tracking schema step (d) defines. Step (d) itself substantially landed
2026-07-25 (`design/architecture.md` §1.2, §1.4 — see `decisions/
0002-build-sequencing-strategy.md` action item 5), and as of
`signal_fusion.py`'s addition (2026-07-25) its evidence-signal-set
reconciliation is now real code here too, not just prose. The false-
positive matching mechanism (`verification.py`) is likewise caught up as
of `decisions/0003`'s action items 1-2 (same day) — hardened text
matching plus a SOC-code/`occupationalCategory` path, both real code now,
not a flagged gap. What remains open is attribute-level reconciliation
(`decisions/0003`'s deferred half) — not caught up because it was
deliberately not built yet, not because it was missed.
