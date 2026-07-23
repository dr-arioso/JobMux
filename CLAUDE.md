# CLAUDE.md — JobMux session notes

Environment and tooling notes for any session working in this repo — not design content. For the actual design, read `concept.md` and `architecture.md`; `concept.md` §6 has the bootstrapping instructions for a new session.

## Git in this repo — known issue and workaround

This repo lives in a Dropbox-synced folder. The mount allows creating and modifying files but not deleting them — the same restriction that applies to Dropbox-synced output folders elsewhere. Git's normal commit flow creates a `.lock` file (`.git/index.lock`, `.git/HEAD.lock`, `.git/refs/heads/<branch>.lock`) and deletes it when done; the delete step fails here (`Operation not permitted`), leaving the lock file behind and permanently blocking any future git command that needs to create that same lock file again.

**Symptom:** `git add` or `git commit` fails with `fatal: Unable to create '.git/index.lock': File exists` (or the same for `HEAD.lock`), even with no other git process running.

**Workaround, in order:**

1. **Staging (`git add`):** point `GIT_INDEX_FILE` at a temp path outside the mounted folder (e.g. `/tmp/jobmux-work/temp-index`, first seeded with `cp .git/index /tmp/jobmux-work/temp-index`) so git never touches the stuck `.git/index.lock`.
2. **Committing:** don't run `git commit` directly — it still needs to lock `HEAD` or `refs/heads/<branch>`. Use plumbing instead: `git write-tree` (against the temp index), then `git commit-tree <tree> -p <parent-sha> -m "<message>"` to create the commit object without touching any ref lock, then overwrite `.git/refs/heads/<branch>` directly with the new commit hash — a plain file write/modify, not a delete, so it isn't blocked.
3. Afterward, `cp` the temp index back over `.git/index` so a plain `git status` or `git add` from a later session reads correctly without needing the env var.

Each commit made this way still leaves one new stale `.lock` file behind, since git always tries and fails to clean up after itself — that's expected, not a sign something's wrong. Don't spend time trying to `rm` it; it can't be removed through this mount. The workaround above routes around each stuck file rather than needing it gone.

## Never `git push` from this sandbox — and `git fetch`/`git pull` won't work either

No credentials are available here: `git fetch` fails with `fatal: could not read Username for 'https://github.com': No such device or address`, and `git push` would fail the same way. Committing locally and stopping there is correct every time — leave push/pull for the user to run from their own machine.

**Don't mistake a Dropbox sync for a fetch.** Because the whole `.git` directory lives inside the same Dropbox-synced folder as the working tree, `.git/refs/remotes/origin/<branch>` can appear to change between sessions — or even mid-session — with no `git fetch` or `git push` ever run from here. That's Dropbox syncing the user's own local git activity (a real push or fetch they ran on their own machine) into this shared `.git` folder, not evidence of a network operation happening in this sandbox. If `origin/<branch>` looks unexpectedly ahead, behind, or different from what this session's own commits would produce, that's the expected explanation — don't spend time treating it as a bug or trying to verify it by fetching (verify against the real GitHub repo in a browser instead, if it matters).

## `internal/` is private and gitignored

`internal/traceability.md` (and anything else under `internal/`) cites real project-internal material — actual case-1 specifics (employer names, place names, real findings) explicitly not meant for open-source release. `.gitignore` already excludes the whole directory. Never reference its specifics in any file meant to be committed, and never take any action that would push it anywhere.

## Where the build actually is

`concept.md` §6 lists the build order. As of 2026-07-23:

- **(a) elicitation layer** — done (`elicitation.md`).
- **(b) evidence-gathering modules** — partial: fragmented-small-employer module done (`fragmented-employer-module.md`); signal-fusion module, the other reference implementation §6 step (b) calls for, not started.
- **(c) verification/escalation policy doc, (d) recombination/tracking schema template, (e) SKILL.md assembly, (f) plain-repo sanity check** — not started.

Update this list as work lands so a new session doesn't have to reconstruct status from `git log`.
