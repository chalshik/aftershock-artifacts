# Owner-proxy delta pass on REG-22 draft 10 (agent a43b6d3c375ffd53e), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:37:49Z), no word changed. It replaces the proxy's draft-9 verdict. The agent calls its conditions 1–6 "T1–T6".

---

**Decision: APPROVE**, as a delta pass on REG-22 draft 10 (FILE(docs/drafts/reg22_draft10.md), byte-identical to docs/drafts/review_bundles/reg22_r5/registration_draft10.md) at code `ffc76b3`. This verdict replaces my draft-9 verdict. HEAD is `2bf6a90`; `git diff ffc76b3 HEAD -- analysis harness tests` is empty. Draft 10 differs from draft 9 only in lines 3 and 133 and the new change-list line 184 (text_diff_draft9_to_draft10.diff).

The approval has no effect while rule F round 5 is outstanding or NOT READY. Round 1's conditions 8–16, D1–D8 and Q1–Q7 stay in force. The PROTOCOL re-reading is still not approved.

**Q1–Q7:** confirmed as in my draft-9 verdict (lines 11, 36, 64, 101, 124 and 133), with one exception: draft 10 drops part of Q7. See condition 3.

**Reasons:**
1. **K1 is stricter.**
   - The record is "the saved stdout of the first run that gave REG-19's table". An unsaved first run means no record and no batch 2, and "a later saved run does not take its place".
   - This leaves one reading only, and it is the strict one.
2. **K2 is stricter, and no REG-19 script triggers it.**
   - Any output with a non-empty `seeds_run`, from any checkout, counts as REG-19's table. A mid-matrix record, saved or not, ends batch 2.
   - Only final.sh:29 runs `analysis.gate reg19`, and final.sh refuses unless all five seeds were run or a futility stop occurred (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:17)).
   - The queue uses `reg19_step`, which prints only `done` and `continue` (FILE(analysis/gate.py:2022–2041)).
   - `reg19_inputs` reads configs only (FILE(analysis/gate.py:2081–2105)).
   - No module outside gate.py computes `reg19_pair` or `reg19_table` (grep of analysis/ and tools/).
   - The pin worktree has no `withheld.py`.
   - gate's `__main__` is identical at HEAD and at the pin, and prints once, at the end.
3. **K3 over G3: I agree, and I change position from my draft-9 verdict.**
   - The cut is the stamp, so extra content in the record's commit cannot move it. Under K3 every other change in that commit counts as after the cut, so a frozen-file change there still makes batch 2 retrospective, and a seed or validity change still makes it not computed (line 64).
   - G3's voiding added no protection. It did add a post-table lever: commit one more file and batch 2 ends.
   - In my draft-9 verdict I called G3 "removal only" and accepted it. That was true but beside the point, because a removal a person can choose after seeing REG-19's table is an outcome-dependent lever. The better argument is rule F round 11's K3 trace (rule A4).
4. **The passage is shared in substance.**
   - I extracted the record passage from REG-22 draft 10 and REG-21 draft 19 and diffed them sentence by sentence.
   - They differ only in the cross-references: which sections the cut applies to, and the name of the not-computed list. Both carry the same gap in the retrospective list (condition 3).
5. **The rest of the new text:**
   - "Same second counts as after", `%ct` against the UTC stamp, "set aside" moving both files out of `state/` (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:18)), and the full path are all stricter or neutral.
   - My draft-9 condition 5 (list every `reg19_final_*` file, and say that no earlier run is known) is now in the text.
   - My draft-9 condition 3 ("adds" against "changes") is moot under K3.
   - Today no `reg19_final_*` file exists in `state/` (file names listed only).

**Conditions:**
1. **BEFORE the entry is appended (carried from draft 9; line 132 is unchanged):** in the freeze's parenthesis:
   - replace "whose diff rule F has seen" with "whose diff a rule F review has passed with no open required item";
   - limit "reported-only readout" to the bodies of `onsets`, `onset_reading`, `planned_rates`, `control_readout` and `reported_counts`. This excludes `__main__` and anything the judged path reaches;
   - test "before batch 1" the way order (b) tests "before a batch-1 table exists".
2. **BEFORE the entry is appended (carried; line 135 is unchanged):** the fix clause refers to line 132. A [CORR]-only fix to a frozen readout before the cut, and any judged-path fix after the cut, makes batch 2 retrospective even when batch 1 needs the fix.
3. **BEFORE the entry is appended (Q7 regression, both registrations):** the last sentence of the record passage reads "if the record's file name, its commit, the ancestry check or the committer times are missing, batch 2 is labelled retrospective".
   - Draft 9 had all four. Draft 10 still requires the times to be cited, but no longer attaches any consequence to their absence. Without the times, the time half of the before-the-cut test is unverified.
   - The same words go into REG-21's copy.
4. **BEFORE the entry is appended (both registrations):** "A stamp later than the record commit's committer time is a breach too, reported the same way" becomes "… is a breach; the cut cannot then be trusted, and batch 2 is labelled retrospective".
   - With such a stamp, every ancestor of the record's commit passes the time test, so only ancestry remains. That reopens J1 by hand: a change made after the true start but committed before the record counts as before.
   - This adds no new lever. A post-cut frozen-file change already makes batch 2 retrospective, and faking a stamp is deliberate, not habit.
5. **BEFORE the entry is appended, and in any case before REG-19's queue is relaunched:** correct agent/RUNBOOK.md §3 step 4 (line 44) to run `final.sh`.
   - As written, it runs `analysis.gate reg19` in the pin worktree with output to `docs/probe/20261113_reg19/reg19_table.txt`. That file has no stamp and is outside `state/`.
   - If anyone follows it first, it is the first run that gave REG-19's table, not saved under its start time. Under K1 there is then no record, and REG-21's and REG-22's batch 2 are both lost.
   - final.sh's guard (:18) would not see that file.
   - Correcting a stale doc is within the delegation; it goes in its own [OPS] or [CORR] entry.
6. **BEFORE the entry is appended (both registrations):** define "REG-19's table" by what is printed, not by the entry point. It covers any output, by any entry point (`python -m analysis.gate reg19`, `python -c`, a REPL, another module), of `reg19_table()` or of `reg19_pair`'s result for a REG-19 seed, apart from `reg19_step`'s `done` and `continue`.
   - The pin has no seal, so a hand call there is the one route the current wording misses.
   - This only removes, it is blind to the outcome, and it is consistent with K1 and K2.

**Which later changes need another proxy pass:**
- My earlier list: the stopping rule, the not-computed cases (other than adding one), the record and its cut, the freeze and its interval, the order rules, the judged path and any threshold.
- Now also: the reported-only exemption beyond condition 1, and any change to the shared record passage that is not made identically in both registrations.
- Rule F round 5 corrections need no pass if they are wording, tags, arithmetic, a lower ceiling, a narrower exemption, or an added not-computed or retrospective case. They need one if they let a voided or later run become the record, move the cut, or widen the exemption.

**Notes for the owner:**
- **Until condition 5 is done, the RUNBOOK step is the most likely way to lose batch 2 of both analyses.**
- **One lever remains that no wording can close.** Whoever sees REG-19's table can end batch 2 by never committing the record. Under draft 10 that has to be reported as "not computed" with the reason, so it is visible only through the reporter's honesty.
- **REG-22 must be appended before REG-19's table is computed,** or batch 2 is retrospective (the commit-order bullet). With the VM off and seeds 18–19 pending, that gives a deadline.
- **I changed position on G3 (reason 3).** My draft-9 verdict endorsed it. The better argument came from REG-21's rule F round 11.

**Not checked by me:**
- `runs/`, the backups and any `state/reg19_*` file contents (file names only).
- Rule F round 5.
- Whether anyone has already run REG-19's table to a terminal or by hand at the pin. I found no command line recording one, only plans (agent/PLAN.md:56, agent/RUNBOOK.md:44, docs/decisions.md:3818, docs/probe/20261111_reg19/ops/RESUME.md:33). The last two run from the main repo, where the seal holds until the heading; I did not re-verify that by running.
- The full `uv run pytest` and `check_docs`.
- That commits are never made on the VM.
