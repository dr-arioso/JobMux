# ADR-0001: Repo directory structure

**Status:** Accepted (implemented 2026-07-23, commit `33f1794`)
**Date:** 2026-07-23
**Deciders:** Bill

**Note on this record:** this decision was made and executed in the same session it was proposed, before this decision log existed — it's backfilled here so ADR-0002 and everything after it has a coherent log to sit in, not because the reasoning changed after the fact.

## Context

At the time of this decision, the repo held 8 files flat at root: two decided-design docs (`concept.md`, `architecture.md`), two meta docs (`README.md`, `CLAUDE.md`), four reference-implementation docs (`elicitation.md`, `fragmented-employer-module.md`, `signal-fusion-module.md`, `verification-escalation-policy.md`), plus a gitignored `internal/`.

`concept.md` §6's own build order implied near-future growth: two more module reference implementations (broad ATS/job-board, values-research), a recombination/tracking schema template, and `SKILL.md` itself — roughly 12 root-level files by the time `SKILL.md` assembly (step e) landed. Two things made this a real fork rather than a non-issue: `SKILL.md` packaging has a de facto convention (a short eagerly-loaded manifest plus a `references/`-style subdirectory loaded on demand for context economy), and the repo hadn't committed to a shape that convention drops into cleanly. Retrofitting at step (e) — after more files had accumulated flat — would have been more expensive than deciding the shape early.

## Decision

Group files by the distinction that already existed conceptually: `design/` for decided-design docs, rarely touched once written; `reference/` for living, versioned reference-implementation docs a future `SKILL.md` points into; root kept for meta docs (`README.md`, `CLAUDE.md`) and, eventually, `SKILL.md` itself as the manifest.

## Options Considered

### Option A: Group by function now (design / reference / root) — chosen

| Dimension | Assessment |
|---|---|
| Complexity | Low — one level of nesting |
| Skill-convention fit | High — matches the standard manifest + references/ shape |
| Portability (plain-repo sanity check, step f) | Good — both subfolders read fine with zero Skill-specific framing |
| Churn required | Small, one-time — rewrite in-file cross-references to add a path segment |

**Pros:** separates "why" from "what the model runs" from "manifest," matching real change cadence and audience differences. Matches the shape step (e) needs anyway, avoiding a second restructuring.
**Cons:** touches every existing cross-reference; adds nesting for what was, at decision time, still only 8 files.

### Option B: Stay flat, restructure only at step (e)

Defer the folder question until `SKILL.md`'s real packaging shape is known, rather than guessing it now.

**Pros:** avoids guessing wrong and paying for it twice.
**Cons:** root stays cluttered (10–12 mixed-purpose files, no grouping signal) for however long steps (b)–(d) take; a future session bootstrapping per `concept.md` §6 has to read more filenames to orient.

### Option C — spicy: single structured source, generate the markdown

Stop hand-maintaining `.md` files as the source of truth; define the design as structured data and generate `SKILL.md` and each reference doc from it via a build step.

**Pros:** would structurally prevent the class of bug already seen twice in this project — several open questions across different files turning out to be one undecided vocabulary, or the real Branch-A/Bridge-B naming collision documented in `internal/traceability.md` — by making cross-file drift a build error instead of a someday-noticed inconsistency.
**Cons:** directly contradicts `concept.md`'s own decided position that reference docs stay "plain markdown, not skill-specific syntax... so they can be lifted into a tool-agnostic repo later." Real tooling burden disproportionate to a one-Skill, one-maintainer project still in design/architecture phase.

## Trade-off Analysis

Option A costs a small, one-time cross-reference rewrite in exchange for landing exactly where step (e) needs the repo to be anyway — versus Option B's guaranteed second restructuring pass, or Option C's real but currently disproportionate fix for a problem that had shown up twice, not yet chronically.

## Consequences

- Cross-file references now use root-relative paths (`design/architecture.md`, `reference/elicitation.md`, etc.), normalized to a single backtick-wrapped citation style across every doc, including `internal/traceability.md`.
- `SKILL.md` assembly (step e) can drop `SKILL.md` at root and point into `reference/` without restructuring anything.
- Confirmed as a side effect of doing this restructuring: `mv` works fine on this repo's Dropbox mount, but `rm`/`unlink`/`os.remove` are blocked outright regardless of tool — documented in `CLAUDE.md`.

## Action Items

1. [x] Create `design/` and `reference/`, move files
2. [x] Rewrite all cross-references
3. [x] Update `CLAUDE.md` build-order status and mount-quirks notes
4. [x] Commit locally via the `CLAUDE.md`-documented git workaround
