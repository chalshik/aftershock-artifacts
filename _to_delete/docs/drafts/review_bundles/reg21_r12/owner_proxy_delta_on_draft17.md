# Owner-proxy delta pass on REG-21 draft 17 (agent a4122f052f465a926), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:24:23Z), no word changed. A delta to the round-4 approval and to the passes on drafts 9, 10, 12, 14 and 15; code at `8164211`. Its condition is named H1 by the proxy; the agent calls it proxy-H1 to keep it apart from rule F round 9's H1.

---

**Decision: APPROVE**, with one wording condition (H1 below). This approves REG-21 draft 17 (FILE(docs/drafts/reg21_draft17.md), byte-identical to the bundle copy) with code at `8164211`, as a delta to the round-4 approval and my passes on drafts 9, 10, 12, 14 and 15.
- All earlier conditions stay in force. E2 and G2 are still due in the [DECISION] (delegate) and before batch 1.
- The approval has no effect while rule F round 11 on draft 17 is outstanding or NOT READY.

What I checked first, at HEAD `ac5100d` (it moved from `72d4884` during the pass; draft 17 is unchanged):
- `git diff 8164211 HEAD` is empty for the nine named files.
- The bundle diff equals a fresh `diff` of drafts 15 and 17.
- The bundle's copies of rule F round 10 and of my draft-15 verdict equal their copies in `reviews-2026-11-13/`.
- `state/` holds no `reg19_final_*` file. I counted file names only.

**Reasons:**

1. **G1 is met (line 107).**
   - The record's commit "adds those two files and nothing else".
   - "Before" means a strict ancestor, "an ancestor other than the record's commit itself"; a change in the record's own commit counts as after.
   - With no record, batch 2 is not computed, with that reason.
   - Lines 54 and 104 refer to the same definition.

2. **J1, the cut is the record's UTC start stamp; "before" needs a strict ancestor and an earlier committer time: accepted.**
   - The added time condition can only move a change from "before" to "after", so the rule is stricter than both draft 15 and draft 14.
   - It closes rule F's late-commit case. A slow or forgotten "at once" commit no longer admits a change made after the table was read.
   - The stamp is made by `date -u +%Y%m%dT%H%M%SZ` in `common.sh`'s `stamp` (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:40)), used at FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20), so it is UTC to the second.
   - **One gap: time zones.** Commit times on this Mac carry +0600; `git log` shows `2026-11-13 17:23:14 +0600` for `f748d50`. Comparing the UTC stamp naively with local committer times would put every commit 6 h late. For example, REG-21's own [REG], committed at 18:00 local (12:00Z), against a stamp of 13:00Z would read as "after", and batch 2 would be retrospective. The text should say that the two are compared as instants (H1).

3. **J2, the record is the first saved stdout that holds the table; a failed run printed none: accepted.**
   - This moves draft 15's ambiguous case, where one reading was "not computed", to the successful run.
   - That is right because a failed run reveals nothing. `gate`'s `__main__` prints once, the function's return value, at the end (FILE(analysis/gate.py:2107), read at `8164211`, the same file as at `a7bb77a`).
   - The failed run's files are not hidden: they go in with the [OPS] entry that `final.sh` already requires before a second try (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:31)).

4. **J3, a run with every REG-19 folder sealed (empty `seeds_run`) is not REG-19's table: accepted.**
   - Such a run shows no outcome. Rule F's synthetic trace prints `too_few`, n 0, no rows. Counting it would have ended batch 2 for nothing.
   - Any run with REG-19's runs readable still counts, an unsealed run from `main` or an early run in the worktree included. Unless it is recorded it ends batch 2; if recorded on fewer seeds, (b)'s lists then differ. That is the right, fail-safe answer.
   - (b) now compares against the record's rows less `excluded`, which is exact.

5. **The optional items, and anything else that moves a rule.**
   - Line 54: "the commits of this [REG] and of its delegate [DECISION]". Exact.
   - Line 55: the times of batch 1 and of REG-22's batch 1 come from their output files' start stamps, and an overrule is blind only if committed before each of them. Stricter; it affects only the owner.
   - Line 113: each batch's output file name carries its start time. A reporting duty.
   - **Unchanged:** U, U_off, r, W, the preconditions, the tolerances, the 0.05, the minimum counts, the run lists, the pooling rule, the governing and mismatch rules, and the judged path. No ceiling is raised. Beyond J1–J3 and G1, no case moves between "computed" and "not computed".

**Condition:**

BEFORE the entry is appended:
- **H1 (lines 107 and 55).** Wherever a committer time is compared with a UTC stamp, the text says they are compared as instants: the committer time as git's `%ct` (epoch seconds), the stamp read as UTC. A commit made in the same second as the stamp counts as after.

H1 is wording that fixes a definition, and it needs no further proxy pass. The [DECISION] (delegate) names its sentence.

**Which later changes need another proxy pass:**
- **Needed:** every item on the earlier lists, plus:
  - what makes a file the record (J2, J3);
  - the cut's time and the test for "before" (J1, G1, H1);
  - the windows' times at line 55.
- **Corrections from rule F round 11:** wording, tags, line references, lower ceilings and reported-only duties need no pass. Anything on the "needed" list does. In doubt, it needs one.
- **A further text-only round of rule F** needs me again only if it touches that list.

**Notes for the owner:**
- **No history rewriting on `main` until batch 2.** A rebase or amend gives a commit a new, later committer time. If REG-21's [REG] or [DECISION] were rewritten after REG-19's stamp, batch 2 would become retrospective. Under the rule this errs toward safety, but it would be a needless loss.
- **The record depends on one manual step**: commit the two `final.sh` files alone, on `main`. If no record is made, batch 2 is lost. G2's notice in `docs/status.md` should name the step.
- **Earlier notes still stand:**
  - a clock readout registered before batch 1;
  - no rerun of `configs/sweep_l1pl350_pc_off.yaml` before batch 2;
  - REG-20's changes to the five named `k1` functions go into new functions or wait until after batch 2;
  - the clause "no heading is added" could be narrowed.

**Not checked by me:**
- I opened nothing under `runs/`, the backups, or any `state/` or `docs/probe/` output; I listed and counted only names in `state/`. So "no record exists today" rests on file names only. I cannot tell whether `analysis.gate reg19` was ever run outside `final.sh` without saving its output. That would already be the "first reading", with no record.
- I did not rerun rule F round 10's trace, and I did not run pytest; the code is unchanged since `8164211`.
- I did not read REG-22's draft 7, which adopts the same record rule. I did not see rule F round 11.
