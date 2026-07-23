# JobMux

Turns what you value into job titles you've never heard of, finds them where other tools can't look, and confirms they're still open.

## How do you find a job you didn't know you wanted?

JobMux starts with a thoughtful interview and a quick read of how the relevant market is structured — sliders for what you'd trade off, hard lines for what you won't — to help you figure out what you're actually looking for, even a kind of job you've never heard of. Plenty of early-career searchers and mid-career changers don't know the job title they want; they know what they value and what they like doing. JobMux is built to work from that end: crystallizing plausible job categories out of priorities, not just filtering listings against a title you already had in mind.

## Why not just use an existing tool?

For some career paths, the job you want can't reliably be scraped from Indeed or Glassdoor — government and hyper-local employers, mission-driven organizations, small nonprofits and civic bodies running their own private hiring channel, careers that don't map to any common search term. That's where JobMux is strongest, and it's not a matter of choosing JobMux instead of a tool like career-ops: broad job-board scanning with common (and actively-discovered) search terms is part of nearly every JobMux search, not a separate alternative to it. JobMux adds what that scanning alone misses — postings that never made it to an aggregator, employers a keyword search would never guess — and checks for validation signals that each one is still genuinely open, instead of wasting your time on an application for a job that's already filled.

It also doesn't do everything. Resume tailoring, cover letters, and ATS auto-fill are real, useful features other tools already handle well, and JobMux isn't trying to replace them — likely never will. The bet here is narrower and complementary: a deeper, more customizable, more exploratory search *strategy*, not a full application pipeline.

## How it learns as it searches

Every result teaches the search something, match or not — and different kinds of results call for different responses:

A false-positive title — "environmental services" turning out to mean hospital housekeeping — gets filtered out for good, and that correction applies retroactively to everything already found, not just what comes next.

A dead end on one search strategy doesn't just get marked "no results" — it's a signal to try a genuinely different approach, or dig into a different phase of the search, rather than repeating the same query and expecting new results.

A listing that reveals a hidden assumption — like discovering people in this field commute or travel further than expected — doesn't just get filed away; it prompts a fresh pass with the corrected assumption, since a wrong assumption about scope means real matches were never searched for in the first place, not just mis-scored.

These are two different moves, not one: re-scoring evidence you already have is cheap and happens automatically; re-running a search phase to find evidence you don't have yet costs real time, so it's proposed, not assumed — "want me to re-check the coverage now that we know X?"

## What the search journey tells you about yourself

The values pass and the learned-insight mechanism build a real model of what you react to, not just what you said in the first conversation. Along the way, JobMux shows you its own ranking of what it found and asks how you'd rank the same jobs yourself. Where the two agree, that's confirmation. Where they don't, the gap is data — about a weight that's off, a quality that got mis-tagged, or a preference you hadn't quite put into words until you saw it sitting at the top, or bottom, of your own list.

## Priorities aren't fixed

People's priorities shift mid-search, and JobMux notices rather than assumes. If your reactions start drifting from what you originally said mattered — often the same gap described above, between how JobMux ranked things and how you'd rank them yourself — it shows you both: here's how your priorities are set today, and here's what today's session suggests they might look like instead. You can adopt the new version (nothing gets overwritten — your prior settings stay on record, not deleted), adjust it yourself, or leave it alone. Adopting triggers the same refilter-or-repeat-search logic described above: a fast rescore of what's already been found, plus a suggestion to search further if the shift means real gaps in what's been looked at so far. Nothing gets reweighted on its own initiative, and no adjustment is ever silent.

## You're always driving

Finding a job you didn't know you wanted can take some serious firepower — cutting-edge frontier-model reasoning, not just keyword matching. But JobMux won't use a bazooka to swat a fly: if you already know what you want and it's realistically easy to find, the tool downshifts to plain orchestration and organizing, and gives you reliable results, fast and cheap. Underneath, JobMux can call on a range of AI tools — a frontier-level model for judgment calls, smaller and cheaper models for routine extraction, plain logic needing no model at all — tuned to how much you want spent on thoroughness versus speed, based on your own cost tolerance. And AI-enhanced doesn't mean out of your control: nothing that costs you money, time, or opportunity happens without your say-so. JobMux drafts and recommends; you decide what actually gets sent.

## Future muxes

A search strategy for one job could become a career strategy over time. The growth-track and stretch-pitch dispositions — jobs that aren't a fit today but might be later, or are worth a stretch pitch if they linger open — already point that way; the natural extension is having them persist and resurface the next time you're searching, not just within one search but years out, whenever your situation changes.

JobMux is being built Cowork/Claude-Code-native first, for speed — but the reference material is written in plain markdown on purpose, not skill-specific syntax, so it can extend to other frontier LLMs later, or stand alone as a prompting methodology outside any particular tool, without a rewrite. A fuller, less LLM-reliant UI is the long-term direction; starting lean now is a sequencing choice, not the ceiling.

None of this is designed in full yet — directions, not current features.

## Status

Design/architecture phase — no implementation yet. Current plan: Claude Skills, with subagent-based model tiering and Cowork's scheduled-tasks primitive handling autonomy and recheck cadence — no custom backend appears necessary for what's currently envisioned. Full technical design lives in `concept.md` (background, landscape, use cases, naming) and `architecture.md` (the four reusable layers, format and infrastructure options).
