# JobMux — Elicitation Layer (Reference Implementation)

**Companion to `concept.md` and `architecture.md`.** Those files state the design as decided; this file is the first template-instantiation artifact built from that design (`concept.md` §6, step a). It is not a description of how the elicitation layer works — `architecture.md` §1.1 already does that. This is the fixed, human-reviewed text a model runs verbatim during a real interview and values pass: the actual prompts, question patterns, forbidden moves, and worked slot-filling examples. Where architecture.md states a rule, this file instantiates it as language a model says out loud to a candidate.

As with the two companion files: this file states the current template as decided. When the template changes, rewrite the relevant section in place. Worked examples throughout use invented, generic placeholder candidates — none of them are the real candidate who motivated this project, and none of the four job-type categories, geographic anchors, or industries from that search appear here. Where an example needs a concrete decision node, career-phase stop, or dimension, it uses a different shape each time specifically so this file doesn't quietly canonicalize one candidate's answers as a template default.

## 0. How to use this file

Each section below is a **module**: an opening frame the model delivers close to verbatim, a small set of question patterns with slots to fill from what the candidate has said so far, and explicit stop conditions. Modules are not a fixed script order beyond the sequencing constraints stated in each section — the interview follows the candidate's thread within a module, and the values pass only starts once the interview module says it's done.

Slots are written `<like this>`. A slot is filled from the candidate's own words already on record, or by asking the smallest possible clarifying question. Never fill a slot with a guess dressed as a paraphrase.

## 1. The interview module

### 1.1 Opening frame (verbatim)

> I'm going to ask you a handful of questions to figure out what's actually going to decide this job search for you — not a checklist, just following where your answers lead. I'll ask one thing at a time, and I'll tell you when I think I've found something that seems to matter a lot to you, so you can correct me if I've got it wrong. I won't make any claims about what jobs exist or what the market looks like while we're doing this — that's a separate step, after we're done here.

This frame commits the model to three forbiddens that hold for the entire interview:

- **One question per turn.** Never stack two questions in one message, even two that feel related. If a candidate's answer surfaces a second question, hold it for the next turn.
- **No market claims, no recommendations, while interviewing.** Not "there's probably demand for that near you," not "a lot of people in your position end up doing X," not naming an employer, an industry trend, or a typical salary range — even if true, even if it would reassure the candidate. This discipline is what keeps discovery a separate, later, evidence-gathering step (architecture.md §1.1); breaking it here contaminates that separation permanently for this candidate.
- **Confirmation counts; the brief said so does not.** A working hypothesis about a decision node is only promoted to "resolved" when the candidate has said something that directly confirms it, in their own words, not when it seems implied or when an assumption from setup would make the interview shorter.

### 1.2 Working hypotheses — stated up front, explicitly revisable

Before the first substantive question, the model states its starting hypotheses about what might matter, framed as guesses, not findings:

> Just so you know how I'm thinking about this going in — based on <what's known so far, e.g. the reason the candidate said they're job-hunting, or nothing at all if this is a cold start>, I'd guess the two or three things that might end up deciding this search are <hypothesis A>, <hypothesis B>, maybe <hypothesis C>. I could easily be wrong about all three — tell me if something else entirely is actually driving this for you.

If nothing is known yet (a genuine cold start), the model says so plainly instead of inventing plausible-sounding hypotheses to fill the slot:

> I don't have anything to go on yet for what might matter most to you, so I'm not going to guess — let's just start and see what comes up.

Each hypothesis is revisited explicitly as the interview proceeds — promoted, demoted, or dropped — never silently abandoned. A hypothesis that turns out wrong is named as wrong before moving on: "Okay — sounds like <hypothesis A> isn't actually a big deal for you. Noted, moving on."

### 1.3 Finding decision nodes — the method, not a list

A **decision node** is a question whose answer would materially change which jobs even belong in this search, not just how they'd be ranked. The method for finding one:

1. Ask an open question about what's driving the search or what's non-negotiable, in the candidate's own words. Do not offer a menu of common decision-node types (geography, compensation, values-fit, schedule, credentialing) unless the candidate is visibly stuck — offering the menu first anchors the answer to the menu instead of surfacing what's actually on the candidate's mind.
2. Listen for language that implies a **binary or near-binary fork** — a point where two answers would send the search in genuinely different directions, not just adjust a preference. "I'd rather have more flexibility" is a preference (values pass, §2). "I can't move, period" or "I won't work somewhere that does X" is a decision node.
3. State the candidate's own fork back to them as a hypothesis, and ask which side of it they're actually on:

   > It sounds like <restated fork, e.g. "whether you're open to relocating at all, or whether staying in <place the candidate named> is fixed"> might be one of the things that decides this search. Is that a hard line, or is there some flexibility in it?

4. If the candidate confirms a hard line, the decision node is **resolved**. If they describe something in between, keep narrowing with follow-up questions until the actual shape of the constraint is clear enough to act on later (a hard boundary vs. a gradated tolerance vs. a genuine toss-up) — this is itself new information the tractability check and the values pass will need, not just interview color.
5. If the candidate's answer stays genuinely ambivalent after reasonable narrowing, resolve it as **open** rather than pushing for a false resolution:

   > It sounds like this one's genuinely up in the air for you right now, and that's fine — I'll carry it forward as open and we'll build a plan that works either way, rather than forcing an answer.

   A decision node resolved as open is written into the plan with a conditional recommendation per branch (concept.md §1, item 1) — this is a legitimate finding, never reframed later as an interview that didn't dig hard enough.

### 1.4 Child decision nodes

A decision node may unlock child questions only once it resolves in a direction that makes the child relevant. Do not ask a child question speculatively "just in case." Pattern:

> Parent decision node: <e.g. "whether the candidate needs to stay in one fixed metro area">
> Resolves "yes, that's a hard constraint" → child becomes askable: <e.g. "is the fixed area a hard boundary, or a radius you'd stretch for the right opportunity?">
> Resolves "no" or "open" → the child question about boundary-shape never comes up; asking it anyway would presuppose a resolution the candidate didn't give.

Worked example, deliberately not geography, to keep this file's own vocabulary from silently narrowing to one candidate's case:

> Parent: "Does this need to be a role you can do without additional credentialing, or are you open to going back for a license or certification first?"
> If resolved "must be immediately workable, no new credentialing": child unlocks — "Is that because of time, money, or something else? That'll matter for how we think about roles that are close but not quite in-scope."
> If resolved "open to credentialing": a different child unlocks instead — "Is there a ceiling on how long a credentialing path you'd take on — a few months, a year, longer?"

### 1.5 Closing the interview module

The interview module ends when every decision node the model surfaced is either resolved (confirmed, in either direction) or explicitly resolved-as-open, and the candidate confirms there's nothing else driving the search that hasn't come up. Close with a plain summary, not a sales pitch for how well the interview went:

> Here's what I've got: <decision node 1> — <resolution>. <decision node 2> — <resolution>. <any open ones> — still open, and that's fine. Does that match how you'd describe it?

Only after explicit candidate confirmation of this summary does the values pass begin.

## 2. The values pass

### 2.1 Opening frame (verbatim)

> Now I want to figure out what you actually care about most when comparing two jobs that both clear your basic requirements — not the hard lines we just covered, but the stuff that makes one offer better than another for you specifically. This part's a little more structured: I'll walk you through some head-to-head comparisons rather than asking you to rank a big list all at once, since most people find pairwise comparisons easier and more honest than ranking ten things in the abstract.

### 2.2 Establishing the starter set

Offer a small starter set of candidate priorities, adjusted for domain if the interview surfaced one, and invite the candidate to add, rename, split, or discard:

> Here's a starter list of things people often weigh in a job search: <5–7 domain-adjusted starter priorities, e.g. "how much variety is in the day-to-day," "how much say you have over your own schedule," "how much of the work is solo vs. with other people," "how structured vs. self-directed the role is," "compensation," "how much room there is to grow into more responsibility"> — some of these might not matter to you at all, and there might be something real missing. What would you add, cut, or rename before we start comparing?

### 2.3 Determining shape — target, scalar, or polarity

Shape is never assigned from a lookup keyed on the priority's name (architecture.md §1.1) — it's read off how the candidate actually talks about it. The model listens for the grammatical and logical shape of the candidate's own language:

- **Target-shaped language** names a specific point or identity value and talks about closeness or match to it, not amount: "I want to end up in <specific place/role/industry>," "it needs to basically be <X>." → shape: **target**.
- **Scalar-shaped language** talks about more-or-less along a single axis, often with an implied floor or ceiling: "the more of X the better, up to a point," "I need at least <N>," "past a certain amount it stops mattering." → shape: **scalar**.
- **Polarity-shaped language** names two opposed qualities and places the candidate somewhere between them: "I'd rather have structure than total freedom," "I lean toward variety over doing the same thing really well." → shape: **polarity**.

When a candidate's language is ambiguous, the model asks a shape-clarifying question rather than guessing:

> When you say <priority name> matters to you — is that more like "I want it to specifically be <a particular thing>," or more like "more of this is just better, up to a point," or more like "I lean one way on a spectrum between <X> and <Y>"?

Worked example (deliberately using a domain-neutral priority, not one from any real search):

> Candidate says: "I really don't want a job where I'm just doing the same three tasks on repeat."
> Model: "So that sounds like a spectrum between doing a wide variety of different things and doing a narrow set really well — where would you say you lean, and how strongly?"
> → shape: polarity, dimension likely "work style" (final dimension name and grouping confirmed with the candidate, not assumed).

### 2.4 Thresholds and mandatory flags

Once a priority's shape is set, ask whether it carries a cutoff:

For scalar or polarity priorities:

> Is there a point on this where, past it, a job's basically off the table regardless of everything else — or is it more just "better is better" without a hard cutoff?

For target priorities, ask about mandatory status instead of a threshold, since a target has no continuum to hang a graded cutoff on. The candidate-facing term for this flag is **non-negotiable**, not "mandatory" — "mandatory" is internal vocabulary, not language to use in conversation:

> Is matching this one non-negotiable for you — a deal-breaker if it's not there — or would you still consider something close?

If the candidate confirms a cutoff or non-negotiable flag, name it back and record it as live state:

> Got it — <priority> becomes a hard stop at <threshold value/unit>, meaning anything past that point is out regardless of how good the rest of the offer looks. That's the kind of thing you can loosen or tighten anytime just by telling me.

### 2.5 Dimensions

Group confirmed priorities into named dimensions, proposing groupings rather than dictating them:

> These three — <priority>, <priority>, <priority> — seem like they cluster together as <proposed dimension name, e.g. "work style">. Does that grouping make sense, or would you split them up differently?

### 2.6 The pairwise tournament

Run the tournament within each dimension first, then run a second tournament across dimensions themselves (architecture.md §1.1 — the same mechanism reused at a coarser grain).

**Turn pattern (verbatim shape, slot-filled):**

> Between <priority A> and <priority B> — if a job was great on one of these but only okay on the other, which one would you rather it be great on?

Record each answer as a single pairwise result. Do not ask the candidate to rank the whole set directly, and do not ask for a numeric weight directly — the cardinal weight is derived afterward from the win-rate pattern via a Bradley-Terry-style conversion (architecture.md §1.1), not elicited as a number in conversation.

**Stopping condition.** The tournament runs until a stable top two or three emerges — not a full sort of the tail. The model tracks this algorithmically (a comparison stops changing the current leader once enough pairs have been run) and stops asking once that stability is reached, rather than running every possible pair out of thoroughness:

> I think I've got a clear read on what tops your list for <dimension> — I'll skip grinding through every remaining combination since the lower end doesn't change the plan much. Let me know if you want to keep going anyway.

**Closing a dimension's tournament (verbatim):**

> So for <dimension>, it sounds like <top priority> matters most, then <second>, and the rest are close enough that I won't force an exact order. Sound right?

Once every dimension's internal tournament is done, run the same pattern one level up, comparing dimensions against each other instead of priorities:

> Now the same kind of comparison, but between the groups themselves — between <dimension A> and <dimension B>, if you had to give up ground on one to protect the other, which would you protect?

### 2.7 Reallocation, stated to the candidate

The reallocation rule (architecture.md §1.1) is algorithmic — it never needs to be explained in mechanism to the candidate, only surfaced as its effect, at the moment a later change triggers it:

> You just bumped <priority> up. That means the others in <dimension> shift down a bit to make room, in proportion to where they already stood — so <priority X> drops a little more than <priority Y> did, since X was weighted higher to begin with. Here's the new breakdown: <updated weights>. Want to adjust anything else, or leave it here?

If the candidate has previously indicated one priority is close to sacred without marking it mandatory or giving it a threshold, the model may propose protect-top-K instead of proportional reallocation as the redistribution rule for that dimension specifically — but only as a named, confirmed alternative, never a silent default swap:

> Since you've said <priority> is close to non-negotiable for you even though it's not marked as a hard requirement, do you want changes elsewhere in this dimension to always leave that one alone, instead of the usual proportional adjustment?

A candidate can also remove a priority, qualification, or entire dimension from scoring outright without deleting it from the record — flagged **not critical** rather than given a zero weight by hand. This reuses the reallocation rule as a weight-zeroing event rather than a separate mechanism:

> If you'd rather I just stop factoring <priority/dimension> into scoring for now — not delete it, just set it aside — say the word and I'll mark it not critical. Everything else in <dimension> reallocates the same way it would if you'd zeroed it out manually, and you can bring it back in anytime.

## 3. Category filters and career phase

### 3.1 Category filters, generally

A category filter applies when a candidate preference is a fixed, named set of discrete labels rather than a continuous scale or a single target — the candidate keeps a live acceptable subset plus a ranking of the accepted labels (architecture.md §1.1). The model introduces a category filter only once it's clear from the interview or values pass that a preference has this shape, not as a default step for every candidate.

**Turn pattern:**

> For <filter name, e.g. employment type>, here's the full range: <label set>. Which of these would you actually consider right now, and — among the ones you'd consider — which would you take first if more than one were on the table?

For filters with an existing external standard (employment type maps to schema.org `JobPosting.employmentType`; occupation maps to SOC; industry maps to NAICS — architecture.md §1.6), the candidate-facing language uses the plain-language labels; the underlying token is recorded for the evidence-gathering layer, never surfaced to the candidate in raw form.

### 3.2 Career phase — generalized pattern

Career phase is a category filter whose labels describe what role a given opportunity plays in the candidate's career trajectory right now (architecture.md §1.1). **The stops themselves are discovered per candidate, the same way a decision node is discovered — never presented as a fixed universal scale.** Whether career phase matters at all, and how finely to stage it, is itself resolved as a decision node earlier in the interview, not assumed.

**Discovering the stops (verbatim pattern):**

> Thinking about the range of jobs you might end up looking at — from "this is exactly the kind of work I want to be doing" down to "this has basically nothing to do with where I want to end up, but it pays the bills" — how many real, distinct stops does that range have for you? What would you call each one?

Do not offer a pre-built set of stop names before the candidate answers this — if the candidate is stuck, offer the *shape* of an example (a scale from ideal-fit down to unrelated-but-viable) using placeholder language, not a specific named set that could be silently adopted as a default:

> If it helps to have a shape to react to — some people find they've got something like four stops: a role that's a strong direct fit, a role that builds toward their career without being the ideal fit, an enjoyable detour unrelated to any career build, and something that's purely a paycheck. Does something like that fit your situation, or does yours look different — more stops, fewer, different in kind entirely?

Once stops are named, run the same acceptable-subset-plus-ranking pattern as any category filter (§3.1), and flag explicitly that this one is expected to move more than most:

> Career phase is one of the things most likely to shift as this search goes on — as you see what's actually out there, it's normal for where you'd draw these lines to move. I'll check in on this one more than most.

### 3.3 The tractability check

Run this check once the acceptable career-phase subset is set, specifically checking whether a stop that disclaims occupation/industry relevance (a pure-income stop) is in the accepted set (architecture.md §1.1):

> You've said you'd consider <pure-income-type stop> — which makes sense, but it also means career phase alone won't narrow down *what* kind of job we're looking for at that end of the range. For that to work, something else needs to bound the search instead — like a location constraint, a schedule requirement, or a type of employer you'd rule in or out. Do you already have one of those in place, or is that actually still open too?

If the candidate has a qualifying mandatory flag or tight threshold elsewhere (already resolved via §1 or §2.4), name it as the thing doing that job:

> Good — since <priority> is a hard requirement for you, that's what keeps this end of the search bounded even without career phase doing it.

If nothing qualifies, this becomes a new decision node in its own right, fed back into §1's method rather than resolved silently:

> That means we've actually got a new open question to run down: what's really bounding this side of your search? Let's treat that like any other decision node.

## 4. Qualifications

Distinct from a priority: a qualification compares the candidate's own attested fact against a listing's stated requirement, with the cutoff supplied by the listing rather than the candidate (architecture.md §1.1). The model gathers the candidate's side of this comparison directly, without yet knowing what any specific listing requires:

> Are there any licenses, certifications, degrees, or minimum years of experience that you already have, or are working toward, that are worth me tracking? These matter because postings often set them as a strict minimum — meeting or missing one can decide whether a listing is even in play, separate from how good a fit it is otherwise.

For each qualification named, capture whether it's boolean (held or not — behaves like mandatory) or graded with a floor (years of experience, degree level — behaves like threshold):

> For <qualification> — is that a yes-or-no thing, or is it more like a number that could be higher or lower (like years of experience)?

Close by naming the asymmetry the candidate should expect later, so a future "unmet desired qualification" doesn't read as a rejection:

> One thing worth knowing going in: a lot of listings separate a strict minimum from a "nice to have." Missing a stated minimum usually knocks a listing out; missing something listed as merely desired doesn't — it's just a softer signal. I'll keep that distinction when I score things later.

## 5. Aptitudes

Distinct from both a priority (what the candidate wants) and a qualification (a fact checked against a requirement): an aptitude is the candidate's own self-rated trait strength, nonpolar — rating one trait says nothing about another (architecture.md §1.1). This module is explicitly optional and self-report only:

> This last part's optional, and it's a bit different from what we've covered — instead of what you want, it's about what you're naturally strong at. Things like attention to detail, how well you handle a fast-changing or high-pressure environment, how independently you like to work, how naturally cooperative or team-oriented you are. Want to rate yourself on a few of these? It can help surface roles that fit your strengths even if you wouldn't have thought to look for them, but it's genuinely skippable if it doesn't feel useful.

If the candidate opts in, rate each named trait independently, not against each other:

> On <trait> — where would you place yourself: about average, above average, or exceptional? And separately, don't worry about whether that trades off against any other trait — it doesn't have to.

If the candidate opts out, record that plainly and move on without pressing:

> No problem — I'll leave this out. You can always come back to it later if you change your mind.

## 6. Closing the elicitation pass

Once §1–§5 are complete (or explicitly skipped where skippable), the model delivers a single consolidated summary and asks for one final confirmation before this state is treated as live and handed to evidence-gathering:

> Here's everything I've got: <decision nodes and resolutions>, <dimensions and top priorities in each, with any thresholds or non-negotiable flags>, <career phase stops and current acceptable set/ranking>, <qualifications>, <aptitudes if given>. Everything here is something you can revise anytime just by telling me — nothing is locked in. Does this all sound right as a starting point?

Only after this confirmation does the context pack (architecture.md §2.2) get generated from the resulting state.

## §7 — open question

Architecture.md §1.1 specifies that the tournament "runs until a stable top two or three holds" but does not specify the exact stopping rule (e.g., how many consecutive pairwise comparisons without a leader change count as "stable," or how ties are broken when the tournament stops early). This file's §2.6 states the stopping condition to the candidate in plain language and defers the precise algorithmic threshold to the algorithmic tier (architecture.md §2.3), consistent with that section's own discipline that tournament-to-Bradley-Terry conversion is deterministic code, not a model judgment call — but the specific numeric stability criterion itself is not yet decided anywhere in the existing docs. Flagged here rather than guessed at silently; the next session touching architecture.md §2.3 or §1.1 should either fix a concrete rule (e.g., "stop once the top-ranked item hasn't changed across the last 2×N comparisons, N = current field size") or explicitly decide it's fine to leave as an implementation-time judgment call.
