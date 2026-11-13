# Owner-proxy delta pass on REG-21 draft 12 (agent a4122f052f465a926), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input), no word changed. A delta to the round-4 approval and to the passes on drafts 9 and 10; code at `8164211`.

---

**Decision: APPROVE**, with conditions E1–E2 below. This approves REG-21 draft 12 (FILE(docs/drafts/reg21_draft12.md), byte-identical to the bundle copy) with code at `8164211`, as a delta to the round-4 approval and to my passes on drafts 9 and 10.
- Round-4 conditions 1 and 7–12 stay in force, condition 10 included. So do my C1–C6 and D1–D3, all now met in the text. E2 qualifies one round-4 sentence.
- The approval has no effect while rule F round 8 on draft 12 is outstanding or NOT READY.

What I checked first, at HEAD `5956ddb`:
- `git diff 8164211 HEAD` is empty for the nine named files. Since `8164211` only `c2.py`, `k5.py` and their tests have changed.
- The bundle diff equals a fresh `diff` of drafts 10 and 12.
- The saved copies of my draft-10 verdict and of rule F round 7 equal their copies in `reviews-2026-11-13/`.

**Reasons:**

1. **D1–D3 are met.**
   - D1, line 107: "once `reg21_table(2)` has been entered", the seal included. The clean-tree refusal, a wrong batch argument, a failure before the table and an outside interruption follow the fix clause, and the command is run again.
   - D2, line 84: a mismatch means batch 2 does not govern, under the "At the tolerance" ceiling, as round-4 condition 10 says.
   - D3, line 103.

2. **R1, line 55 (a change after the window closes governs nothing, and the delegate makes none): accepted. It corrects my own error.**
   - My C2 ended with "if the delegate makes it, it needs rule F and an owner-proxy pass". That let the delegate drop or replace the 0.05 contrast rule after the data are public.
   - The delegation excludes exactly that: "Not delegated: … choosing or widening a threshold after seeing the data it judges (rule A5)" (FILE(docs/decisions.md:4235)). Rule F's F1 is right.
   - R1 keeps the registered reading as the only one that governs. It leaves your power intact: an entry that says it overrides the sentence.

3. **R2, line 103 (batch 2 not before batch 1's [RESULT] is committed): accepted.**
   - It is D3 with the reason added. `reg21_table(2)` recomputes batch 1 and prints `fixed_load_contrast.batch1_median` and every reference run's U (FILE(analysis/k3w.py:385), FILE(analysis/k3w.py:390), read at `8164211`). So the order with REG-22 has to bind batch 2 as well.

4. **R3, line 107 (only an entry after REG-19's final [RESULT] ends batch 2; a flag set before it is part of what that result counts): accepted, with E1.**
   - It moves a case from "not computed" (one reading of "later") to "computed". That is right:
     - REG-19's own process settles validity before its table, so a flag set then is set blind. The checks in force are applied before each step and before the table, and "a ruling on a run's validity made after the table is read is made knowing the outcome" (FILE(docs/drafts/reg19_resume_decision_draft5.md:61), FILE(docs/drafts/reg19_resume_decision_draft5.md:66)).
     - Hand comparison (b) then checks the folders against what REG-19 counted.
   - But the cut is in the wrong place. REG-19's outcomes are known from the moment its table is computed, in the worktree, before any [RESULT] heading exists. A flag changed in between would be informed, and R3 would let it stand. Line 55 already closes the window at "REG-19's table being computed or read by anyone"; this cut should match it.

5. **R4, line 108 (a) (the folders "already present" are listed in the [DECISION] at the append): accepted.**
   - It fixes the list before anything is known, so no one chooses at batch-2 time which case applies (rule F's F4).
   - Folder names and the `valid` field are reads the seal allows (FILE(analysis/withheld.py:7)). I expect the list to hold seeds 15–17's valid burst folders (BELIEF: "six valid runs", FILE(docs/decisions.md:4308)).

6. **The rest of the 10 → 12 diff.**
   - **F6**, "before the table is printed" (107): this moves raises after `reg21_table` returns into "not computed". Those are the second `batch2_runs` call in `reported_spans` and `vj_counts`. Accepted: that code will already have run on batch 1, so only a data-dependent raise remains, and fixing one would be a choice about whether batch 2 exists, made with REG-19 public.
   - **Stricter, accepted:**
     - F11 (110): an early heading makes batch 2 retrospective;
     - F7 (102): the escape now needs REG-22 to list "REG-21's tables";
     - F8 (111) and F9 (55).
   - **Reported-only or text, no pass needed:** F10 (exactness); R5 (159, reported-only diffs plus a clean `harness/`); alternatives 10 and 11 (lines 98–99, text that adds caveats). The line references I checked hold: FILE(harness/checks.py:15), FILE(harness/checks.py:16), FILE(harness/recorder.py:66).
   - **Unchanged:** U, U_off, r, W, the preconditions, the tolerances, the 0.05, the minimum counts, the run lists, the pooling rule and the judged path. No ceiling is raised.

**Conditions:**

BEFORE the entry is appended:
- **E1 (lines 107 and 108 (a)).** Where the text says "after REG-19's final [RESULT]" for a validity flag or the counted seeds, it says instead "after REG-19's table is first computed or read by anyone (its final [RESULT] at the latest)". The parenthetical becomes: "a flag set before that is part of what that table counts and does not end batch 2". The batch-2 [RESULT] gives the time REG-19's table was first computed. REG-19's entry has to give it anyway, under round-4 condition 10.
- **E2. The [DECISION] (delegate) records three things:**
  - My C2's clause "if the delegate makes it, it needs rule F and an owner-proxy pass" is withdrawn as the proxy's error (rule A6), and R1 replaces it.
  - R1 prevails over round-4's bullet "After batch 1 is computed, a change to the governing, pooling or stopping rule needs a proxy pass". The delegate makes no change (rule A5, not delegated):
    - to the rule on the two batches, once line 55's window has closed;
    - to the pooling rule, once batch 1 has been computed;
    - to the stopping rule, once REG-19's table has been computed or read.
  - Round 4's bullet still applies to stopping-rule changes made before REG-19's table is computed or read.

E1 and E2 are stricter text and need no further proxy pass. The [DECISION] (delegate) names the sentence that meets each.

**Which later changes need another proxy pass:**
- **Needed:** every item on round 4's "needed" list and on my earlier lists, plus the sentences that carry R1–R4, E1 and E2. In particular:
  - any change that moves a case between "computed" and "not computed";
  - the cut-off points (line 55's window, E1's cut);
  - the order clauses;
  - the hand duties and the list made at the append;
  - the governing and mismatch rules;
  - the judged path, a tolerance, a precondition or the run lists.
- **Corrections from rule F round 8:** wording, tags, line references, lower ceilings and reported-only duties need no pass. Anything on the "needed" list does. In doubt, it needs one.
- **A further text-only round of rule F** needs me again only if it touches that list.

**Notes for the owner:**
- **Only you can change the rule on the two batches** once line 55's window has closed, by an entry that says it overrides that sentence. If you want "batch 2 always governs", write it before the first of: batch 1, any print of U or r on a batch-1 or reference run, REG-19's table.
- **The GPU clock is not measured.** Alternative 10 names it as the likeliest cause of a non-zero fixed-load contrast. The data exist in each run's `gpu.jsonl`. A reported-only clock readout registered before batch 1 would let both [RESULT]s address it; added later, it is exploratory only. The delegate declined it; it is your call.
- **Batch 2 now waits on** REG-22's [REG] (or its withdrawal), then batch 1's [RESULT], then REG-19's final result. P(never computed) is 0.4 (BELIEF).
- **Two earlier notes still stand:**
  - do not rerun `configs/sweep_l1pl350_pc_off.yaml` before batch 2;
  - the clause "no heading is added to make the seal lift" also binds REG-19 and REG-20, and could be narrowed to "changes nothing for batch 2" without a pass.

**Not checked by me:**
- I opened nothing under `runs/` or the backups, so I have not seen the folder list R4 requires.
- I did not read REG-22's drafts 5 and 6, so F7's statements about `c2.py`'s batch 2 are unchecked.
- I compared drafts 10 and 12, not draft 11 on its own.
- I did not rerun rule F round 7's traces, and I did not run pytest; the code is unchanged since `8164211`. I did not see rule F round 8.
