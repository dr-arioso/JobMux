# CLAUDE.md — JobMux session notes

Environment and tooling notes for any session working in this repo — not design content. For the actual design, read `design/concept.md` and `design/architecture.md`; `design/concept.md` §6 has the bootstrapping instructions for a new session.

## Git in this repo — known issue and workaround

This repo lives in a Dropbox-synced folder. The mount allows creating and modifying files but not deleting them — the same restriction that applies to Dropbox-synced output folders elsewhere. Git's normal commit flow creates a `.lock` file (`.git/index.lock`, `.git/HEAD.lock`, `.git/refs/heads/<branch>.lock`) and deletes it when done; the delete step fails here (`Operation not permitted`), leaving the lock file behind and permanently blocking any future git command that needs to create that same lock file again.

**Symptom:** `git add` or `git commit` fails with `fatal: Unable to create '.git/index.lock': File exists` (or the same for `HEAD.lock`), even with no other git process running.

**Workaround, in order:**

1. **Staging (`git add`):** point `GIT_INDEX_FILE` at a temp path outside the mounted folder (e.g. `/tmp/jobmux-work/temp-index`, first seeded with `cp .git/index /tmp/jobmux-work/temp-index`) so git never touches the stuck `.git/index.lock`.
2. **Committing:** don't run `git commit` directly — it still needs to lock `HEAD` or `refs/heads/<branch>`. Use plumbing instead: `git write-tree` (against the temp index), then `git commit-tree <tree> -p <parent-sha> -m "<message>"` to create the commit object without touching any ref lock, then overwrite `.git/refs/heads/<branch>` directly with the new commit hash — a plain file write/modify, not a delete, so it isn't blocked.
3. Afterward, `cp` the temp index back over `.git/index` so a plain `git status` or `git add` from a later session reads correctly without needing the env var.

Each commit made this way still leaves one new stale `.lock` file behind, since git always tries and fails to clean up after itself — that's expected, not a sign something's wrong. Don't spend time trying to `rm` it; it can't be removed through this mount. The workaround above routes around each stuck file rather than needing it gone.

## The mount blocks deletion generally — not just git's lock files

The restriction described above isn't git-specific; it's a property of the Dropbox mount itself, and it's worth knowing before it costs time on some future task. Confirmed directly (2026-07-23, during the `design/`/`reference/` restructure): plain `mv` works fine on this mount — renaming or relocating a file is a legitimate write operation and always succeeded, including moving all six root-level docs into subdirectories in one pass. But `rm`, `unlink`, and Python's `os.remove()` all fail identically with `Operation not permitted`, regardless of which tool issues the call — this is a filesystem-level block, not something a different command happens to route around.

**Practical implication:** reorganizing, renaming, or restructuring files from a sandbox session is safe and unrestricted. Actually deleting a file is not possible from here under any method — don't spend time retrying `rm` with different flags or tools if it fails once, the same way the git section above already says not to fight the stale `.lock` files. If a file genuinely needs to be gone rather than moved (a stray test artifact, a file created by mistake), the only fix is deleting it from the user's own machine, where the same Dropbox folder allows normal deletion. Leave it named plainly (don't bury it) and tell the user, rather than working around it silently.

## Never `git push` from this sandbox — and `git fetch`/`git pull` won't work either

No credentials are available here: `git fetch` fails with `fatal: could not read Username for 'https://github.com': No such device or address`, and `git push` would fail the same way. Committing locally and stopping there is correct every time — leave push/pull for the user to run from their own machine.

**Don't mistake a Dropbox sync for a fetch.** Because the whole `.git` directory lives inside the same Dropbox-synced folder as the working tree, `.git/refs/remotes/origin/<branch>` can appear to change between sessions — or even mid-session — with no `git fetch` or `git push` ever run from here. That's Dropbox syncing the user's own local git activity (a real push or fetch they ran on their own machine) into this shared `.git` folder, not evidence of a network operation happening in this sandbox. If `origin/<branch>` looks unexpectedly ahead, behind, or different from what this session's own commits would produce, that's the expected explanation — don't spend time treating it as a bug or trying to verify it by fetching (verify against the real GitHub repo in a browser instead, if it matters).

## `internal/` is private and gitignored

`internal/traceability.md` (and anything else under `internal/`) cites real project-internal material — actual case-1 specifics (employer names, place names, real findings) explicitly not meant for open-source release. `.gitignore` already excludes the whole directory. Never reference its specifics in any file meant to be committed, and never take any action that would push it anywhere.

## Where the build actually is

`design/concept.md` §6 lists the build order. As of 2026-07-23:

- **(a) elicitation layer** — done (`reference/elicitation.md`).
- **(b) evidence-gathering modules** — done: fragmented-small-employer module (`reference/fragmented-employer-module.md`) and signal-fusion module (`reference/signal-fusion-module.md`), both reference implementations §6 step (b) calls for.
- **(c) verification/escalation policy doc** — done (`reference/verification-escalation-policy.md`) — generalizes `design/architecture.md` §1.3 into the same fixed template-instantiation format; the two module files' own escalation-ladder instantiations (`reference/fragmented-employer-module.md` §6, `reference/signal-fusion-module.md` §2) now point back to it as the canonical general form rather than standing as independent policies.
- **(d) recombination/tracking schema template, (e) SKILL.md assembly, (f) plain-repo sanity check** — not started. Note for step (d): four open questions across the existing reference docs (`reference/fragmented-employer-module.md` §10, `reference/signal-fusion-module.md` §3 and §7, `reference/verification-escalation-policy.md` §7) all converge on the same undecided piece — a closed confidence-label vocabulary for the tracking schema — and should be resolved together as one decision, not four.

Update this list as work lands so a new session doesn't have to reconstruct status from `git log`.
