# Owner-proxy delta pass on REG-21 draft 14 (agent a4122f052f465a926), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:11:37Z), no word changed. A delta to the round-4 approval and to the passes on drafts 9, 10 and 12; code at `8164211`.

---

**Decision: APPROVE**, with one condition (F1 below). This approves REG-21 draft 14 (FILE(docs/drafts/reg21_draft14.md), byte-identical to the bundle copy) with code at `8164211`, as a delta to the round-4 approval and my passes on drafts 9, 10 and 12.
- All earlier conditions stay in force. E2 is still due in the [DECISION] (delegate) before the append.
- The approval has no effect while rule F round 9 on draft 14 is outstanding or NOT READY.

What I checked first, at HEAD `929a507`:
- `git diff 8164211 HEAD` is empty for the nine named files. Since `8164211` only `c2.py`, `k5.py` and their tests have changed, and nothing under `harness/`.
- The bundle diff equals a fresh `diff` of drafts 12 and 14.
- The saved copies of my draft-12 verdict and of rule F round 8 equal their copies in `reviews-2026-11-13/`.

**Reasons:**

1. **E1 is met.**
   - Line 107: the cut is "after REG-19's table is first computed or read by anyone (its final [RESULT] at the latest)". A flag set before that is part of what the table counts, and the batch-2 [RESULT] gives the time.
   - Line 108 (a) uses the same cut.
   - E2 belongs in the [DECISION] (delegate), as line 184 says. I can check it only when that entry exists.

2. **G1, the `batch1_median` check (lines 84, 76, 73, 113): accepted.**
   - **The NaN case.** Rule F is right that draft 12 gave opposite answers when batch 1's λ = 2.0 group has fewer than three judged runs. The code sets `batch1_median` to NaN in that case (FILE(analysis/k3w.py:388), read at `8164211`):
     - line 84 then read the NaN as a mismatch (batch 2 does not govern);
     - line 75 read it as "undefined" (batch 2 stands alone).
   - **Draft 14 resolves it toward line 75**, which has been in force since draft 6. That is right: the NaN comes from batch 1's small group by construction, not from a failed reproduction.
   - **The check still tests reproduction.** It requires NaN in that case, so a group that changes size between the two commands is still a mismatch, in either direction.
   - **The precision.** Within `EPS` (1e-9), against the median as printed:
     - the same code, the same runs and the pinned lock give the same float, so `EPS` absorbs only float noise;
     - any real change shows up as a mismatch.
   - **The other lines.** "Unless the check fails" (73) and "the difference and the check alone" (76) now agree with D2.
   - **One choice point is left:** the check is made against a figure typed into batch 1's [RESULT]. A typo there would be noticed, and its reading chosen, with REG-19 public. F1 closes this.

3. **The optional items that touch a rule: accepted.**
   - **`MemoryError` and `KeyboardInterrupt` count as interruptions (107).** Nothing is printed before the end, and a rerun computes the same values, so no value can be chosen. Before this, the same cause could fall on either side of the rule, depending on whether the OS killed the process.
   - **A table printed under a stray early heading ends batch 2 for good (110).** This lowers a ceiling and closes rule F's G5.
   - **`reported_spans`' own run list (86)** ends the command before the print. That agrees with line 107.
   - **Stricter or clearer:** "committed" in both sentences (103); the same `runs/` in (a) and (b) (108).

4. **The rest of the 12 → 14 diff moves no rule.**
   - **Alternative 10 is corrected (G2), and it is right.** Both batches divide by the same `ref["mean"]` (FILE(analysis/k3w.py:383)), so the reference's day cancels from the contrast. Its new citations resolve: FILE(configs/l1_pl350_base.yaml:7), FILE(harness/checks.py:188).
   - **Line 59** adds a route to "never computed": REG-22 never registered.
   - **Line 99** gains a BELIEF tag.
   - **Unchanged:** U, U_off, r, W, the preconditions, the tolerances, the 0.05, the minimum counts, the run lists, the pooling rule and the judged path. No ceiling is raised.

**Conditions:**

BEFORE the entry is appended:
- **F1 (lines 84 and 113).** The text says all of the following:
  - Batch 1's command output is saved verbatim (unedited stdout) to a file that is committed with batch 1's [RESULT] and named in it. The `batch1_median` check compares against that file.
  - The [RESULT]'s quote is for the reader. If the quote and the file differ, a [CORR] corrects the quote; the difference is never read as a mismatch.
  - Batch 2's output is saved and committed the same way before any reading of it is written. The hand comparison of the contrast with 0.05 is made on that file.

F1 is stricter text and needs no further proxy pass. The [DECISION] (delegate) names its sentence.

**Which later changes need another proxy pass:**
- **Needed:** every item on the earlier lists, plus:
  - line 84's NaN rule and its `EPS` precision;
  - line 73's precedence;
  - what the check compares against (F1);
  - which failures count as interruptions (107).
- **Corrections from rule F round 9:** wording, tags, line references, lower ceilings and reported-only duties need no pass. Anything on the "needed" list does. In doubt, it needs one.
- **A further text-only round of rule F** needs me again only if it touches that list.

**Notes for the owner:**
- **Batch 2 alone at λ = 2.0.** If batch 1's λ = 2.0 group ends with fewer than three judged runs, batch 2's J1 stands alone there and there is no contrast. Rule F puts this at P ≈ 0.005, or ≈ 0.22 if REG-18's seeds 3 and 6 both fail the busy test (DERIVED).
- **A `MemoryError` that persists** after the machine's other work is stopped has no stated end. If it happens, the decision is yours.
- **Earlier notes still stand:**
  - a clock readout registered before batch 1 is the only way to address alternative 10;
  - do not rerun `configs/sweep_l1pl350_pc_off.yaml` before batch 2;
  - the clause "no heading is added to make the seal lift" could be narrowed.

**Not checked by me:**
- I opened nothing under `runs/` or the backups.
- The [DECISION] (delegate) that must carry E2 does not exist yet.
- I did not read REG-22's drafts.
- I did not rerun rule F round 8's trace, and I did not run pytest; the code is unchanged since `8164211`. I did not see rule F round 9.
