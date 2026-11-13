# Owner-proxy delta pass on REG-21 draft 10 (agent a4122f052f465a926), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input), no word changed. A delta to the round-4 approval and to the delta pass on draft 9; code at `8164211`.

---

**Decision: APPROVE**, with conditions D1–D3 below. This approves REG-21 draft 10 (FILE(docs/drafts/reg21_draft10.md), byte-identical to the bundle copy) with code at `8164211`, as a delta to the round-4 approval and to my delta pass on draft 9.
- Round-4 conditions 1 and 7–12 stay in force, condition 10 included (D2).
- My C1–C6 are met in the text.
- The approval has no effect while rule F round 7 on draft 10 is outstanding or NOT READY.

What I checked first, at HEAD `358418e`:
- `git diff 8164211 HEAD` is empty for `analysis/k3w.py`, `withheld.py`, `k1.py`, `load.py`, `gate.py`, `margin.py`, `stats.py`, `derived.py` and `tests/test_k3w.py`. Since `8164211` only `analysis/c2.py`, `analysis/k5.py` and their tests changed.
- The bundle diff equals a fresh `diff` of drafts 9 and 10.
- The saved copy of my draft-9 verdict equals the reviews copy, and five sentences I spot-checked are as I sent them.

**Reasons:**

1. **(1) My conditions against draft 10, one line each:**
   - **C1, met.**
     - Line 105 adds three "not computed" cases: REG-19 ends without its table, a later entry changes the counted seeds or a flag, or duty (a) is breached.
     - Line 106 defines "counts".
     - Line 59 gives 0.4 (BELIEF), with 2 lost launches beside 6 valid runs.
   - **C2, met and wider (line 55).**
     - The window closes at the first print of U, an uncached-token rate or r on any batch-1 run, not just λ = 2.0.
     - It also closes when REG-19's table is computed or read, not only at its [RESULT].
   - **C3, met (line 100).**
   - **C4, met (line 109).**
   - **C5, C6 and my recommendation, met** (lines 110, 111, 108).

2. **(2a) Rule F round 6, item 1 (the overrule window): accepted.** It is my C2 with a stricter end point.

3. **(2b) Rule F round 6, item 2 (line 105): accepted, with D1.**
   - **What changes.** Draft 9 put a raise in `reference`, `select`, `row` or `judge`, or in batch 1's recomputation, under the fix clause (line 104): a reviewed fix, then a rerun. Draft 10 makes each of them "not computed".
   - **Why that is right.** After REG-19's table, batch 2's r is fixed to about ±1 %. REG-19's c is over the same W (FILE(docs/decisions.md:3778), FILE(docs/decisions.md:3799)), and r ≈ c ÷ 1.681 × 0.98–1.00 (line 51, DERIVED). So whether to fix, and how (which reference run, which request), would be chosen with the answer nearly known.
   - **The heading rule** ("not computed whether or not the command was run") gives one answer to a typo whatever the order of events. Line 108's check before commit makes a typo unlikely.
   - **Why D1 is needed.** "Every raise of `uv run python -m analysis.k3w reg21 2` … wherever it comes from" also reads as covering raises that compute nothing:
     - the clean-tree gate: `_dirty` raises `SystemExit` before `reg21_table` (line 120, FILE(analysis/k3w.py:462));
     - a bad batch argument;
     - an environment or import failure;
     - an interrupt.
     
     None of these carries outcome information, and a rerun changes nothing in the computation. Yet the literal text ends batch 2 on them. This case is reachable. Rule F round 6 found the tree dirty with another session's `c2.py` work, so `_dirty` would refuse the command today.

4. **(2c) Rule F round 6, item 3 (the readouts claim, line 157): accepted.** It adds a reporting duty only: the diff of `k3.py` and `modelf_sim.py`, and readouts marked when computed with changed code. That lowers a ceiling and needs no pass.

5. **(3) The rest of the 9 → 10 diff: one change of the governing rule, rejected as written (D2). Nothing else moves a rule.**
   - **Line 84** now says that a mismatch between the printed `batch1_median` and batch 1's [RESULT] "changes nothing else", and that "the printed difference governs either way".
     - This contradicts round-4 condition 10, which is in force and goes into the entry verbatim: "If not, it is reported as a deviation and batch 2 does not govern."
     - The code and the runs are held fixed between the batches, so a mismatch means an undetected change in the judged computation. That is the case in which the unread batch should not govern.
     - Rule F's optional item allowed either answer. The draft picked the one that conflicts with a condition in force.
   - **Everything else is one of the following:**
     - exactness (27, 102's parenthetical, 120);
     - the prediction (59);
     - C1–C6;
     - stricter wording of the hand duties (106: every matching folder listed, which `runs/` is meant, compared by name, done once, a difference final; (a) applies from this entry on).
   - **Unchanged:** U, U_off, r, W, the preconditions, the tolerances, the 0.05, the minimum counts, the run lists, the pooling rule and the judged path. No other ceiling is raised.

6. **A gap opened by C3.** Batch 1 now waits on REG-22 (line 100), so REG-19 can report first. Nothing says that batch 2 waits for batch 1's [RESULT]. Lines 84 and 102 and round-4 condition 10 all presuppose that order (D3).

**Conditions:**

BEFORE the entry is appended:
- **D1 (line 105).** "Not computed" covers raises once `reg21_table(2)` has been entered: `batch2_runs` and all it calls, `reference`, `select`, `row`, `judge`, and batch 1's recomputation, the seal included. The following compute nothing and follow line 104's fix clause, with no change to the judged path or to `analysis/k3w.py`; then the command is run again:
  - the clean-tree refusal (`_dirty`);
  - a batch argument other than 2;
  - a failure before `reg21_table` is entered (`uv`, the environment, an import);
  - an interruption from outside the code (a signal, a killed process, a machine that stops).
- **D2 (line 84).** "The printed difference governs either way … changes nothing else" is replaced by round-4 condition 10's rule. A mismatch is reported first, as a deviation, and batch 2 does not govern. The ceiling of "At the tolerance" applies (line 74):
  - both batches are reported together;
  - no sentence on λ = 2.0 rests on one batch;
  - the line "Batch 2's J1 inside" does not apply;
  - K3's status names the deviation and is not worded as inside.
- **D3 (line 101).** Batch 2 is computed only after batch 1's [RESULT] is appended.

D1–D3 are stricter text and need no further proxy pass. The [DECISION] (delegate) names the sentence that meets each, as for C1–C6.

**Which later changes need another proxy pass:**
- **Needed:** every item on round 4's "needed" list and on my draft-9 list, plus the sentences of D1–D3. In particular:
  - any change that moves a case between "computed" and "not computed";
  - the governing or pooling rule, the mismatch rule included;
  - the overrule window;
  - the order clauses (REG-22 and batch 1, batch 1 and batch 2);
  - the hand duties;
  - the judged path, a tolerance, a precondition or the run lists.
- **Corrections from rule F round 7:** wording, tags, line references, lower ceilings and reported-only duties need no pass. Anything on the "needed" list does. In doubt, it needs one.
- **A further text-only round of rule F** needs me again only if it touches the "needed" list.

**Notes for the owner:**
- **Batch 2 can now be lost to more causes:** any raise inside the command after REG-19's result, and a mistyped heading. That is the price of making no choice when its r is nearly known. D1 keeps it from being lost to the clean-tree gate. P(never computed) is now 0.4 (BELIEF).
- **Recommendation:** no rerun of `configs/sweep_l1pl350_pc_off.yaml` before batch 2. A sixth valid run, or a cut folder, of that config would end batch 2 and stop batch 1.
- **The heading clause** "no heading is added to make the seal lift" (105) also binds REG-19's rerun from `main` and REG-20's reads. Batch 2's outcome is already fixed "whether or not the command was run", so the clause could be narrowed to "a heading added later changes nothing for batch 2". That narrowing needs no proxy pass.
- **Your window** to overrule the rule on the two batches closes at the first of three events (line 55). It may close before you are back.

**Not checked by me:**
- Nothing under `runs/` or the backups was opened. So I did not check whether any folder matching the reference or batch-2 pattern is unreadable or invalid today.
- I read rule F round 6 (an input this time) but did not rerun its synthetic traces (R1, R2, Q1–Q3). I did not see round 7.
- I did not read REG-22 draft 5 (only its commit message), so I did not check that it keeps the order "both ways" that C3 relies on.
- I did not run pytest; the code is unchanged since `8164211`, where round 6 ran 35 passing tests.

Scratch: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r6_proxy/d9d10.diff
