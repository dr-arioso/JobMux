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
| `tournament.py` | Pairwise win-counts → Bradley-Terry cardinal ranks | §1.1 |
| `scoring.py` | Chebyshev-style weighted scoring; qualification met/unmet percentage | §1.1 |
| `scheduling.py` | Volatility-tier recheck cadence; information-gain-per-cost action ordering (architecture.md §1.5 designates this the eventual consumer of §1.4's numeric confidence value, once something produces one — the code itself is unchanged and doesn't reference confidence yet) | §1.4, §1.5 |
| `verification.py` | Listing staleness date check; ledger value diffing; near-miss re-filtering; false-positive exclusion matching | §1.3, §1.2 |
| `compensation.py` | Cost-of-living salary normalization | §1.2 |
| `context_pack.py` | Event-log fold → the §2.2 context-pack JSON contract | §2.2, §2.4 |

## Running the tests

```
pip install pytest --break-system-packages   # or a normal venv
pytest
```

72 tests, all passing as of the 2026-07-25 terminology/persistence-taxonomy update (68 from this module's initial commit, plus 4 covering the new false-positive registry).

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
2026-07-25, architecture.md §1.2's persistence taxonomy) match a listing
against a confirmed false-positive pattern via plain case-insensitive
substring containment on the title or employer field — a first
instantiation of the matching mechanism, not a settled decision. A
SOC-code-misalignment-based mechanism (architecture.md §1.6) is a live
candidate to replace substring matching with; *confirming* that a given
result actually is a false positive, as opposed to a genuine near-miss,
stays frontier-tier judgment regardless of which matching mechanism this
module ends up implementing.

Similarly, architecture.md §1.4's evidence-signal-set reconciliation
(deriving an outcome label and a numeric confidence value once each
signal's own state is known) is decided as algorithmic-tier but has no
implementation in this module yet — a candidate for a future
`jobmux/signal_fusion.py`, not yet written.

## Scope note

This module implements what architecture.md §2.3 explicitly lists as
algorithmic. `context_pack.py` builds the already-decided §2.2 JSON
contract, which is a different, narrower thing than the persistence/
tracking schema step (d) defines. Step (d) itself substantially landed
2026-07-25 (`design/architecture.md` §1.2, §1.4 — see `decisions/
0002-build-sequencing-strategy.md` action item 5), but as prose in the
design docs, not as code in this module: the evidence-signal-set
reconciliation and the false-positive matching mechanism it specifies are
only partially implemented here (see the open flags above) — this
module's own code should not be read as having caught up with everything
(d) now decides.
