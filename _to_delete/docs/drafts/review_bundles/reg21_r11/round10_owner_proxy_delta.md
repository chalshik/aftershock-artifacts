# Owner-proxy delta pass on REG-21 draft 15 (agent a4122f052f465a926), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:17:53Z), no word changed. A delta to the round-4 approval and to the passes on drafts 9, 10, 12 and 14; code at `8164211`.

---

**Decision: APPROVE**, with conditions G1 (before the append) and G2 (before batch 1). This approves REG-21 draft 15 (FILE(docs/drafts/reg21_draft15.md), byte-identical to the bundle copy) with code at `8164211`, as a delta to the round-4 approval and my passes on drafts 9, 10, 12 and 14.
- All earlier conditions stay in force. E2 is still due in the [DECISION] (delegate).
- The approval has no effect while rule F round 10 on draft 15 is outstanding or NOT READY.

What I checked first, at HEAD `ab6988f`:
- `git diff 8164211 HEAD` is empty for the nine named files. Since `8164211` only `c2.py`, `k5.py` and their tests have changed, and nothing under `harness/`.
- The bundle diff equals a fresh `diff` of drafts 14 and 15.
- The bundle's copies of my draft-14 verdict, rule F round 9 and REG-19's `final.sh` equal their sources.

**Reasons:**

1. **F1 is met.**
   - Line 84: the `batch1_median` check and the comparison with 0.05 are made on the saved files. A quote that differs from its file is corrected by a [CORR] and never read as a mismatch.
   - Line 113: each batch's output is saved as unedited stdout under `docs/probe/` and committed. Batch 1's is named in its [RESULT] with a sha256; batch 2's is committed before any reading is written.

2. **H1, the cut's time comes from a record (lines 107, 54, 55, 108 (a)): accepted, with G1.**
   - **It is stricter and removes rule F's T1 case.** The time is a commit, not a memory, and the default is "after".
   - **It is practical.** `final.sh` already writes the table's output to `state/reg19_final_<UTC stamp>.txt` (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20), FILE(docs/probe/20261113_reg19/ops_r3/final.sh:29)), and `state/` is tracked by git.
   - **The record holds what (b) needs.** `gate.py` is identical at `a7bb77a` and `8164211`, and `reg19_table`'s rows carry `runs`.
   - **Gap 1: a commit is its own ancestor in git.** `git merge-base --is-ancestor HEAD HEAD` exits 0 (my run). So an entry that changes a flag or the counted seeds, committed together with the record, counts as "before" the table. That is the very change, made after seeing the table, that the cut exists to catch.
   - **Gap 2: no record.** If the table is computed and no record is made, (b)'s new third comparison cannot be made, and the text does not say what follows. The reader would decide with REG-19 public.

3. **Duty (b) compares three lists, and any difference ends batch 2: accepted.**
   - It catches a `valid` flag rewritten in `checks.json` with no entry; `runs/` is not in git, so nothing else would record that.
   - The outcome is fixed in advance.

4. **Line 104, a judged-path change committed after the record makes batch 2 retrospective with no review route: accepted.**
   - This moves a case from "a review may keep batch 2" to "retrospective". It applies E2 and R1: once REG-19's table is public, batch 2's r is close to known, and whether batch 2 governs should not be settled by a review made then.
   - A change committed before the record keeps the review route. Its review is of a change made blind.
   - **The cost is real.** REG-20's code lives in `analysis/k1.py`. Batch 2 can only run from a checkout whose `docs/decisions.md` holds REG-19's heading, because the seal reads that checkout's own file (FILE(analysis/withheld.py:23)). A worktree pinned at batch 1's commit would hit the seal and give "not computed". So a REG-20 commit to `cold_backlogged`, `reuse`, `later_turns`, `_state` or `windows` before batch 2 now makes batch 2 retrospective with no remedy (G2).

5. **The rest of the 14 → 15 diff moves no rule.**
   - "REG-19's table" means `analysis.gate reg19`'s output, not the step's flag (55, 107). This is clearer.
   - Line 98's new citation resolves: FILE(configs/stage2_l1pl350_base.yaml:6).
   - Line 3 gains a comma.
   - **Unchanged:** U, U_off, r, W, the preconditions, the tolerances, the 0.05, the minimum counts, the run lists, the pooling rule and the judged path. No ceiling is raised.

**Conditions:**

BEFORE the entry is appended:
- **G1 (line 107).** The text says both of the following:
  - The record's commit adds the table's output file and its stderr file and nothing else. "Before" means a strict ancestor of the record's commit; anything in the record's own commit counts as after.
  - If REG-19's table is computed or read and no record is made, batch 2 is not computed, with that reason (the third list of duty (b) does not exist).

BEFORE batch 1 is computed:
- **G2 (the `docs/status.md` line of line 110).** That line also says:
  - whoever first runs `analysis.gate reg19` commits its output at once, alone; that commit is the record;
  - until batch 2 is computed or declared not computed, a commit in the checkout batch 2 runs from that changes a function or constant named on the judged path (REG-20's work in `analysis/k1.py` included) makes batch 2 retrospective if it lands after the record.
  
  This is a notice; it adds no rule.

G1 and G2 are stricter text and need no further proxy pass. The [DECISION] (delegate) names their sentences.

**Which later changes need another proxy pass:**
- **Needed:** every item on the earlier lists, plus:
  - the definition of the record and of "before" (G1);
  - the three-list rule in (b);
  - line 104's route for a judged-path change.
- **Corrections from rule F round 10:** wording, tags, line references, lower ceilings and reported-only duties need no pass. Anything on the "needed" list does. In doubt, it needs one.
- **A further text-only round of rule F** needs me again only if it touches that list.

**Notes for the owner:**
- **The record.** REG-19's `final.sh` saves the table's output by itself. The only new step is to commit that file alone, at once. If that step is skipped, batch 2 is lost (G1).
- **REG-20 and batch 2.** REG-20's changes to the five `k1` functions named on the judged path, committed before batch 2, would make batch 2 retrospective. Running batch 2 from an older worktree is not a way around it, because the seal reads that worktree's `decisions.md`. Putting REG-20's changes in new functions, or making them after batch 2, avoids this.
- **Earlier notes still stand:**
  - a clock readout registered before batch 1;
  - no rerun of `configs/sweep_l1pl350_pc_off.yaml` before batch 2;
  - the clause "no heading is added" could be narrowed;
  - a `MemoryError` that persists has no stated end.

**Not checked by me:**
- I opened nothing under `runs/` or the backups.
- I did not run `final.sh` or `analysis.gate reg19`, and I cannot tell whether anyone has already run the latter outside `final.sh`. That would already have been the "first" computation, with no record.
- I did not read REG-22. I did not run pytest; the code is unchanged since `8164211`. I did not see rule F round 10.
- The [DECISION] (delegate) that must carry E2, F1's sentence list, G1 and G2 does not exist yet.
