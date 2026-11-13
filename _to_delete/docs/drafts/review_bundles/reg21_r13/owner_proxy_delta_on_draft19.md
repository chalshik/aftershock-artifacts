# Owner-proxy delta pass on REG-21 draft 19 (agent a4122f052f465a926), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:41:54Z), no word changed. A delta to the round-4 approval and to the passes on drafts 9, 10, 12, 14, 15 and 17; code at `8164211`.

---

**Decision: APPROVE**, with three wording conditions (P1–P3), all due before the entry is appended. This approves REG-21 draft 19 (FILE(docs/drafts/reg21_draft19.md)), with code at `8164211`, text only. It is a delta to the round-4 approval and to my passes on drafts 9, 10, 12, 14, 15 and 17.

Integrity checks, at HEAD `2bf6a90`:
- The bundle copy is byte-identical to the draft, and the bundle diff equals a fresh diff of draft 17 against draft 19.
- `git diff 8164211 HEAD` is empty for `analysis/k3w.py`, `k1.py`, `load.py`, `gate.py`, `margin.py`, `stats.py`, `derived.py` and `withheld.py`.
- `state/` holds no `reg19_final_*` file (I checked names only).

**Reasons** (line numbers are draft 19's)

1. **proxy-H1 is met.**
   - Line 107 compares the two times "as instants (the committer time as git's `%ct`, epoch seconds; the stamp read as UTC …); a commit in the same second as the stamp counts as after".
   - Line 55 adds "(compared as instants, as 'Batch 2 not computed' says)".
   - Lines 54, 104 and 108 (a) use line 107's test by reference.
   - The change log names it (the section after line 198).

2. **K1 is accepted. The record is the saved stdout of the first run that gave the table. If that run was not saved there is no record, and a later saved run does not take its place (line 107).**
   - This is stricter than draft 17 and brings back draft 15's single reading.
   - It cannot be used as a kill switch after the data: whether to save the output is decided before the output exists.
   - Cost: one unsaved run ends batch 2 (see the notes for the owner).

3. **K2 is accepted. Any output with a non-empty `seeds_run`, from any checkout and at any point of the matrix, is REG-19's table.**
   - Only `final.sh` runs `analysis.gate reg19` (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:29)). The queue scripts run only `reg19_step` (FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:77); `queue_reg19*.sh`).
   - A record from the middle of the matrix ends batch 2 through (b)'s third list. That is stricter than needed (an earlier cut would be enough), but the rule was set before the data and it deters a look in the middle of the matrix, which would also affect REG-19. I do not ask for the looser version.

4. **K3 is accepted. It replaces G3 of REG-22's round 4 and turns my G1 from a definition into a duty.**
   - **Why:**
     - Under G3, whoever commits the record could void it after seeing the table by adding one file. That is a choice made after the data, and the delegate may not make those (rule A5 is not delegated).
     - It would not even need intent. In this repo every commit that has added files under `ops_r3/state/` also carried 6 to 8 other files (rule F round 11, K3).
   - **G1's purpose is kept.** G1 exists so that nothing in the record's commit counts as before the cut. Under K3:
     - the cut is the stamp, fixed before any output exists;
     - "before" needs a strict ancestor of the record's commit with an earlier committer time;
     - the other changes in the record's own commit count as after.
   - **A late commit cannot move the cut,** because a late commit fails the time test.
   - G1 is met in this form. One lever is left; P3 closes it.

5. **The stamp may be "taken no later than the command's start".**
   - **Accepted:** an earlier stamp moves the cut earlier, which is stricter. `final.sh` stamps after its check for earlier files (:18–19) and before the recheck (:25) and the table (:29).
   - **Two problems remain (P1 and P2):**
     - **The phrase "was not saved under its start time"** in the no-record sentence can be read to say that `final.sh`'s stamp does not qualify. That reading gives "no record, not computed", and someone could choose it after seeing the table.
     - **A stamp later than the record commit's committer time is a stamp that cannot be true.** The draft says this is a breach "reported the same way", so under K3 the record stands and the cut is that stamp. The cut then moves later: rule F's J1 again, done by hand, the one direction this passage exists to stop. Draft 17 had the same gap without naming it.

6. **The freeze now runs "From this entry to batch 2" (REG-22's G2). Accepted; it is stricter.**
   - The batch-1 [RESULT] shows the diff from the entry to batch 1, with each hunk's review (line 113).
   - Line 105's fix clause and line 104's exception still require rule F and a proxy pass for a change made before the cut. After the cut, no review restores batch 2.
   - "Between batch 1 and batch 2" now appears only in the change log (lines 192, 195 and 204), not in any rule text.

7. **O3 is accepted. G2's notice in `docs/status.md` is due in the append commit (line 112).** That is earlier, so stricter, and needed, because REG-19's final run may come before batch 1. G2 is met once that commit carries the notice.

8. **Duty (a)'s list gives names and whether a `checks.json` exists (line 108). Accepted.**
   - No rule read the old `valid` field. "Already present" is used only in line 108.
   - Seeing a silent flag flip before the cut was the only thing the old list offered. `final.sh`'s recheck covers that: it refuses the table if a stored flag differs from today's checks (final.sh:21–27). (b)'s third list catches flips after the cut.
   - Tag issue: the reason given cites `docs/FABLE_PROMPT.md`, which is untracked. The repository source is FILE(docs/decisions.md:4256): "`checks.json`, which a rerun decision reads". This is optional to fix.

9. **The batch-2 [RESULT] must cite the record (line 107; REG-22's Q7). Accepted; it lowers a ceiling.**
   - "Missing from the citation → retrospective" and "not committed → no record → not computed" produce the same governing outcome: batch 2 governs nothing either way. So the two readings do not matter for K3.

10. **One record passage serves both registrations.**
    - I compared line 107 with REG-22 draft 10's line 133, sentence by sentence. They are identical except for references to each registration's own sections (duty (b), against "Runs").
    - REG-22 draft 10 keeps G3's voiding wording only in its change log (line 184).
    - So rule F's concern that the two must change in step is met today.

11. **Nothing else moves a rule.** Line 3 is bookkeeping.

**Conditions**

BEFORE the entry is appended (line 107; the G2 notice in line 112 for P1):

- **P1.** Replace "was not saved under its start time" with "was not saved under a stamp taken as this bullet requires (no later than the command's start; `final.sh`'s stamp qualifies)". In the G2 notice, replace "under the start stamp" with "under a stamp taken no later than the command's start".
- **P2.** Replace "A stamp later than the record commit's committer time is a breach too, reported the same way." with: "If the record's stamp is later than its commit's committer time, the breach is reported and batch 2 is labelled retrospective: the cut is never later than the true start, and no other time takes the stamp's place."
  - The only way to trigger this after the data is a backdated commit, which line 107 already forbids. It adds no new lever.
  - I deliberately do not tie a missing command-line quote to this. The quote is written after the table, so tying it in would create a kill switch.
- **P3.** After "a later saved run does not take its place", add: "A saved record that is not yet committed when batch 2 is to be computed or declared not computed is committed first (late: a breach, reported, and still the record). 'No record' never follows from leaving a saved file uncommitted, and no saved `reg19_final_*` file is deleted or moved out of the repository, except a failed run's pair as 'set aside' says."
  - This is K3's own logic: without it, whoever holds the file can end batch 2 after seeing the table by not committing it.

P1–P3, written as given, need no further proxy pass. The [DECISION] (delegate) names their sentences and carries E2, F1, G1 (now a duty), G2 (at the append), proxy-H1 and P1–P3. The same words should go into REG-22's line 133 so the passage stays identical. That is for REG-22's proxy to approve; if REG-22 ends up with different words, the agent brings the two into line, and any REG-21 change that is not word for word mine needs a pass.

**Which later changes need another proxy pass**
- **Needed:**
  - everything on the earlier lists;
  - what makes a file the record, and when there is none (K1–K3, P1, P3);
  - the cut and the test for "before" (H1, P2);
  - where the freeze starts;
  - moving G2's notice later than the append;
  - any rule that reads a `valid` from duty (a)'s list.
- **Corrections from the parallel rule F round:** wording, tags, line references, lower ceilings and reported-only duties need no pass. Anything on the needed list does, including other words for P1–P3. If in doubt, it needs one.
- **A further text-only round** needs me only if it touches that list.

**Notes for the owner**
- **One unsaved run of `analysis.gate reg19` ends batch 2 of REG-21 and of REG-22.** That holds at any point, from any checkout, including the pinned worktree, which has no seal. A saved run from the middle of the matrix ends it too. Run the table only through `final.sh`, once, at the end, and commit its two files at once, alone, on `main`.
- **K3 over G3 was the right call:** G3 gave whoever commits the record a one-file kill switch after seeing the table.
- **Each strict rule here adds a way to lose batch 2; none lets it be won after the data.**
- **Earlier notes still stand:**
  - no history rewriting on `main`;
  - a clock readout registered before batch 1;
  - no rerun of the cache-off sweep before batch 2;
  - REG-20's changes to the named `k1` functions go into new functions or wait until after batch 2. The freeze now starts at the entry, not at batch 1.

**Not checked by me**
- I opened nothing under `runs/`, the backups, `state/` file contents or probe outputs. I did not read `docs/FABLE_PROMPT.md`, rule F's parallel round, or REG-22's proxy verdict on draft 9.
- I cannot tell whether anyone has already run `analysis.gate reg19` without saving it; if so, K1 already applies.
- I cannot tell whether commits are ever made on the VM, whose clock the time test does not cover.
- A stamp moved later but still earlier than the record's commit is caught only by the quoted command line, which depends on honesty.
- I did not run pytest or any analysis. The code is unchanged since `8164211`.
