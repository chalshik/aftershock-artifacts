# FOR THE AUTHOR

What you should know or may want to overrule. The agent never waits on this file. Newest items at the top of each section.

## Top

-5. **If you want the turn mix or the session rates judged on REG-19's runs, say so before REG-19's [RESULT].** REG-21 (draft 5, in review) judges one of step B's six readouts, the uncached-token work rate, and only reports the other five. Once its table is read those five can never be judged on these runs. This departs from your "Register now, mix primary" and "Rebuild around per-run sim".
-4. **Two owner-proxy passes disagreed on one point of the REG-19 resume, and I took the stricter one.** The stricter validity checks of 2026-11-12 (A14) are now applied to every REG-19 run *before* its table is computed, blind to the outcome. If any run's validity changes, no table is computed and it waits for you. The other pass wanted the recheck reported after the result. Draft 3: `docs/drafts/reg19_resume_decision_draft3.md`, item 4.
-3. **A further lost run (no `checks.json`) will stop REG-19 until a new reviewed decision.** Only the rerun of seed 18's control is allowed by the decision in review.
-2. **The VM is back (2026-11-12 19:48 UTC) but no 350 W run can start: `sudo -n nvidia-smi -pl 350` needs a password.** `/etc/sudoers.d/` on the VM holds only its README, so the passwordless rule you meant to allow does not exist. Run `sudo nvidia-smi -pl 350` on the VM, and to let the agent do it after later reboots add `/etc/sudoers.d/nvidia-pl` with the line `chalshik ALL=(root) NOPASSWD: /usr/bin/nvidia-smi -pl 350` (`sudo visudo -f /etc/sudoers.d/nvidia-pl`). The agent watches the limit every two minutes and starts REG-19's queue when it reads 350 W and the resume decision is approved. Also: `ulimit -n` on the VM is 1024; REG-20's open-loop arm must not start below 4096 (its registration), so raise it before that arm (e.g. `ulimit -n 8192` in the shell that starts the harness needs a hard limit that allows it; check `ulimit -Hn`).
-1. **The session stopped on 2026-11-13 because your usage limit was reached.** Three reviews were cut off unfinished, so nothing is registered or approved yet and **REG-19 cannot resume until the resume decision is reviewed** (`agent/STATE.md`, "Next three"). The 30-minute heartbeat is cancelled. To continue: start `claude` in this repo and give it `agent/RESUME_PROMPT.md`.
0. **The agent cannot restart itself after a crash or reboot unless you run three commands.** I wrote and tested the watcher and the resume launcher (launchd can start a headless session; proof in `agent/launchd/README.md`), but Claude Code's permission classifier refused to let me install recurring launchd jobs, and I did not work around it. Until you run the commands in `agent/launchd/README.md`, the study advances only while this interactive session stays open (it has a 30-minute heartbeat and a 15-minute GPU check inside it). Kill switch once installed: `touch agent/STOP`. Also: the Mac has no auto-login, so after a reboot nothing starts until you log in.
1. **No off-machine backup.** No external volume was mounted on 2026-11-13. `runs/` (182 folders, 19 GB) is copied to `/Users/chalshik/aftershock-backups/runs-2026-11-13` on the same disk; that guards against deletion, not against losing the Mac. Verified against the manifest on 2026-11-13: 1831 files listed, 0 missing, 0 different.
2. **The delegation entry was not committed.** Your start prompt says you committed it. It was in the working copy only, and its heading had no `## `. I added the marker and line breaks, changed no word, and committed it (`c94a77d`, decisions.md 2026-11-13 [OPS]). I treat it as in force. If you did not write those seven lines, void it with one entry and tell me to stop.
3. **`DRIVE_COPIES` was not filled in and I could not find the files.** No `context-alignment.md`, and no Drive copy of the paper plan or related work, under `~/Library/CloudStorage/GoogleDrive-…` (depth 8) or the home folder (depth 6). So the Drive-side corrections (P0 cut to the cold side, the corrections on Lu, Huang and Liu, Valse and Jannesari, KAIROS, references pinned to v1) are merged only as far as the repo already had them. Put the files in `docs/paper/drive/` and the next block will merge them.
4. **`PAPERS_DIR` was not filled in.** I used the PDFs an earlier session had downloaded to its scratchpad (2611.02543, 2611.08902, 2611.13412, 2604.16682, 2607.02640, and Schroeder 2006 from another scratchpad). They are now in `docs/paper/pdfs/` (git-excluded). I could not check that 2604.16682 is v2 or that the three preprints are v1 except from the PDFs' own first pages (recorded in `agent/LITERATURE.md`).
5. **The snapshot path differs.** The prompt names `docs/context-pack-2026-11-12-full.md`; the file is `docs/paper/context-pack-2026-11-12.md`. I read that one.

## Decisions you may want to overrule

- **REG-21 no longer has the mix as its primary readout** (your choice of 2026-11-12, "Register now, mix primary"). Draft 3 judges the stuck server's uncached-token work rate against the cache-off sweeps; the mix is reported only. Reason: both review rounds showed the mix follows from queue kinematics and the time in the running batch. Not registered yet.
- **REG-19's analysis will run from a git worktree at `a7bb77a`** (`/Users/chalshik/Projects/aftershock-reg19-pin`), not from `main`, and the VM stays at `a7bb77a` until its [RESULT]. Draft, in review.
- **A new folder outside the repo:** that worktree, and `/Users/chalshik/aftershock-backups/`.
- **A second worktree outside the repo:** `/Users/chalshik/Projects/aftershock-linktest-pin`, at `a7bb77a`, with links to every run folder except REG-19's. It was used once, to show that the pinned code reads runs through links (REG-17's table reproduced). It can be removed (`git worktree remove`); I do not delete.
- **The seal on withheld runs now needs a heading that is the result itself** (`## <date> · [RESULT] REG-19…`); a heading that only quotes those words no longer lifts it (`analysis/withheld.py`, commit `69ffedd`).

## Things left uncommitted on purpose

- `.gitignore` (your line `docs/potential_gaps.md`), as you left it.
- `docs/FABLE_PROMPT.md` is untracked; I did not add it.

## Things moved instead of deleted (`_to_delete/`)

(none)

## Backup

- 2026-11-13: `rsync -a runs/` to `/Users/chalshik/aftershock-backups/runs-2026-11-13` (19 GB, 182 folders). `python3 tools/manifest.py verify` printed: "1831 listed, 0 missing, 0 different, 0 not in the manifest -> OK". The copy includes REG-19's six withheld folders; copying and hashing them reads no outcome.
