# Owner-proxy delta pass on REG-22 draft 5 (agent a43b6d3c375ffd53e), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input), no word changed. A delta to its round-1 approval of draft 4; code at `ffc76b3`.

---

**Decision: APPROVE**, on the conditions below. This approves REG-22 draft 5 (FILE(docs/drafts/reg22_draft5.md), byte-identical to the bundle copy) with `analysis/c2.py` and `tests/test_c2.py` at commit `ffc76b3`. It is a delta to my round-1 approval of draft 4 at `727d1f2`.
- Draft 5 meets round-1 conditions 1–7, with residual tag fixes (D1).
- The stopping-rule change (a) is approved.
- My round-1 conditions 8–16 stay in force.
- The re-reading of PROTOCOL §3 condition 4 is still not approved. Draft 5 now leaves it with the owner as a proposal, which is what I asked for.
- This approval has no effect while rule F round 3 on draft 5 is outstanding or NOT READY.

**Reasons**

1. **Round-1 conditions 1–7, checked against draft 5 (line numbers of `registration_draft5.md`).**
   - **Condition 1: met.**
     - Line 20: "REG-22 changes no rule … It does not judge the order clause on any run."
     - Line 21: `sustain` is a proposal, in force only after a `[DECISION] (owner)`.
     - Line 22: no entry, status line, claims line, definition or paper text says condition 4 is met, "with or without a qualifier"; not counted towards the six conditions; the two names.
     - Line 15: an edit to PROTOCOL needs the owner.
     - Line 1: the title says "condition 4's registered levels".
     - Line 17: C2's test and its "Supports" line are quoted, and "REG-22 makes no loop figure".
     - A grep finds no "delegate's", "dated note" or "as read by".
     - Nit: line 17's "in full" stops before the last sentence of FILE(docs/claims.md:25).
   - **Condition 2: met** (line 15).
   - **Condition 3: met.** a in lines 89–92, b in 94, c in 95, d in 96, e in 97, f in 98, g in 99 and 52, h in 100 and 108. Line 101 adds a lower ceiling for batches that disagree.
   - **Condition 4: met.**
     - Line 11: P(all eleven `loop`) ≈ 0.8, the likeliest outcome changes no decision, 0.05 and 0.07.
     - Lines 68–76: the published spans, the exit, what was not published. Line 72: REG-15's earlier levels.
     - Lines 79–80: `continue` and the interim look.
     - Lines 79 and 84: the batch-2 prediction made conditional, and three runs exist.
     - The arithmetic is corrected in lines 25, 83, 84 and 108.
   - **Condition 5: met, with residuals (D1).** Lines 9, 10, 26 and 37 tag rule F's computations to its file. Lines 58–60 give run ids. Lines 62, 68–74 and 12 are tagged. Line 52 has the tally sentence, line 106 "single same-seed control", line 116 alternative 3. The residuals:
     - FILE(analysis/c2.py:307) is stale at `ffc76b3`, where line 307 is inside `control_readout`. `REG22` is at line 382 and its runs at line 387.
     - Line 110 cites `agent/theory/k1_held_prefix.md` without the FILE form.
   - **Condition 6: met verbatim** (lines 122–124). REG-21 draft 10 carries the mirror rule (FILE(docs/drafts/reg21_draft10.md:100), FILE(docs/drafts/reg21_draft10.md:109)).
   - **Condition 7: met as text** (lines 152–154). It is due in the commit that holds the entry.
   - **Conditions 8–16 are carried:** lines 4, 64, 128–133, 136–146 and 15. One gap is under condition 8. The list of what changed after rule F round 1 (R1–R10, FILE(docs/drafts/reg22_draft4.md:104) to :115) is cut to one line (line 163). docs/process.md §3 requires it after the review (D3).

2. **The code: no judged function changed.**
   - The bundle's patch equals `git diff 727d1f2 ffc76b3` for the two files (`cmp`).
   - Nothing else under `analysis/`, `tests/`, `harness/` or `configs/` changed between the two commits apart from `k5.py` and `test_k5.py`. Nothing changed from `ffc76b3` to HEAD `802bb99`.
   - A syntax-tree comparison of every top-level function and constant of `c2.py` finds these identical: `C2`, `REG22`, `windows`, `gauge`, `reuse_in`, `session_uncached_rate`, `baseline`, `levels`, `last_burst_end`, `links`, `sustain`, `onsets`, `batch_runs`, `reg22_table`, `row_counts`, `eviction_readout`, `turn_spacing`.
   - Changed:
     - `condition4`, only in the readout tuple, after the label;
     - `control_readout`, `histogram_delta` and `__main__`.
   - New: `PLAN_ORDER`, `planned_rates`, `onset_reading`, `reported_counts`.
   - The new readouts read and do not write. `later_turns` copies; `planned_session_rate`, `gauge` and `baseline` filter. So `reg22_table`'s second pass cannot change a label.
   - `uv run --offline --frozen pytest tests/test_c2.py -q -p no:cacheprovider`: 29 passed (my run).

3. **The stopping-rule change (a): approved.** Line 64 lists four cases in which batch 2 is "not computed":
   - REG-19 ends without its table;
   - the folders differ from the seeds in n of that table;
   - `batch_runs(2)` raises;
   - a later entry changes the counted seeds or a matching run's validity.

   Why it is acceptable:
   - Each case can only remove batch 2. None picks runs.
   - The first three are blind to outcome: whether REG-19 gets a table depends on the VM.
   - The fourth gives the writer of a later entry, who has seen REG-19's result, an option to remove batch 2. Removal is the right answer. Recomputing on a corrected set would be a selection after the outcome. The removal must be reported with its cause (D8). Marking a run invalid beyond the automatic checks needs the owner (FILE(CLAUDE.md:19)).
   - It is the same rule as the REG-21 proxy's C1 (FILE(docs/drafts/reviews-2026-11-13/proxy-reg21-draft9-delta.md:68)) and defines "counts" the same way.
   - Cost: batch 2 is lost more often. The draft's own estimate is P ≈ 0.6 that it is computed (line 84, BELIEF).
   - One gap: a slip loses batch 2 here too. If a lost burst folder is copied into `runs/`, `load_run` can raise. REG-21's C5 guards this only until REG-21's batch 2 is computed (D6).

4. **Point (b): the correction of my reason 3 is right, and I accept it.**
   - `pass` needs only one span that holds (FILE(analysis/gate.py:126), FILE(analysis/gate.py:150)). So the published `pass` of REG-12's seeds 2 and 3 does not bound their exit, and my round-1 reason 3 was wrong to include them.
   - The bound for REG-14 stands. A span that "counts" there is one that holds (FILE(analysis/gate.py:144)).
   - The rest of reason 3 does not rest on the exit. Hit 0.000 and KV 0.95 are published in every span (FILE(docs/decisions.md:2480), FILE(docs/decisions.md:3747)).

5. **Nothing else in the diff raises a ceiling, loosens a rule or touches the judged path.**
   - Lower or stricter:
     - line 93: D1 and D2 now "may" be proposed, "by their own decision";
     - line 96: line d needs a count;
     - line 97: wording for an N or KV failure;
     - line 101: batches that disagree;
     - line 64: the not-computed cases;
     - line 128: the order with REG-20;
     - line 129: saved output and a second run logged;
     - line 130: the judged path taken transitively.
   - Two gaps:
     - **The freeze.** Line 131 freezes "everything `reg22_table` reaches", which includes the readouts. But the tallies that lines a and h quote come from `reported_counts`, which `__main__` calls, not `reg22_table`. So a change to them between the batches would pass (D4).
     - **Line 78 drops part of the overlap with REG-21.** REG-21's command also prints KV, the running batch, the waiting line and preemptions over its window W (FILE(analysis/k3w.py:169), FILE(analysis/k3w.py:198)). W contains REG-22's end window, so those are close to REG-22's level values (D2).
   - The new `onset_reading` is reported only. Its rule (each pair in the plan's order, a 10 s tolerance, four readings) is fixed now, before REG-19's data, and its tally is quoted under line h. So after batch 1 it belongs under the freeze, and draft 5 freezes it.
   - Nits:
     - line 53: seed 5 was also run at both loads (`bad_baseline` at both);
     - lines 58 and 60: verdicts cited by end rows; FILE(docs/decisions.md:2467) to :2471 and :3742 to :3745 are the ranges.

**Conditions**

BEFORE the entry is appended:

- **D1. Rule B.**
  - FILE(analysis/c2.py:307) becomes FILE(analysis/c2.py:387) at `ffc76b3`, resolved again at the entry commit, like every other FILE(path:line).
  - The eviction forecast cites FILE(agent/theory/k1_held_prefix.md:<line>), or is marked BELIEF, not reviewed.
  - Line 75 cites FILE(analysis/gate.py:144) for "hold or count".
  - Lines 58 and 60 give the row ranges.
  - Line 53 says "among the stuck runs" and that seed 5 was run at both loads.
  - Line 17 says "its first sentence, in full", or quotes the rest.
- **D2. Line 78** adds that REG-21's command prints, per run, KV, the running batch, the waiting line and preemptions over W, and that W contains REG-22's end window.
- **D3. Reviews in the entry.**
  - The [REG] holds, under the rule F round-1 review, the R1–R10 list of FILE(docs/drafts/reg22_draft4.md:104) to :115 verbatim; under round 2, the list of line 164; under round 3, what changed.
  - The [DECISION] (delegate) holds both owner-proxy verdicts verbatim (round 1 and this delta).
  - The [DECISION] names, for each of round-1 conditions 1–7 and D1–D5, the sentence that meets it. Reason 1 above may be quoted.
- **D4. The freeze** (lines 131 and 133) adds:
  - `reported_counts` and the `__main__` block of `analysis/c2.py`: their hunks between the batches need rule F and a proxy pass;
  - a change to anything `reg22_table` reaches, or to those two, made after REG-19's result heading exists, also labels batch 2 retrospective.
- **D5. Line 92:** once batch 2 is declared not computed, "batch 2 pending" becomes "batch 2 not computed: <reason>", and batch 1's standing is unchanged.

BEFORE batch 1 is computed:

- **D6.** The `docs/status.md` line required by REG-21's C5 also covers REG-22: no lost or invalid folder of a REG-19 burst config enters `runs/` until both REG-21's and REG-22's batch 2 have been computed or declared not computed.

LATER, in a [RESULT]:

- **D7. The batch-2 [RESULT] states what was public when it was computed:**
  - every decisions.md entry committed, and every computation on REG-19's burst runs made, between REG-19's result heading and the batch-2 command (REG-19's table, REG-20's gate, REG-21's batch 2);
  - that REG-19's [RESULT] had already published each run's verdict, end-window values and emptyings, so the labels were partly implied.

  It keeps the standing "registered before REG-19's table" exactly, and does not call batch 2 "unread".
- **D8.** If batch 2 is not computed, a [RESULT] REG-22 entry says so, names the case of line 64 that applied, and names the entry or raise that caused it.

D1–D8 are stricter text or duties and need no further proxy pass.

**Which later changes need another proxy pass.**
- **Needed:**
  - everything on round 1's "needed" list;
  - any change to the four not-computed cases of line 64, or to the definition of "counts" (the seeds in n of REG-19's table). This includes making batch 2 computed in a case now "not computed", or the reverse;
  - the order with REG-21 (lines 122–124);
  - the freeze (D4 included);
  - after batch 1, `onset_reading`, `reported_counts` or any readout `reg22_table` reaches;
  - wording that raises a ceiling of lines a to h or line 101, or that puts the proposal of line 21 in force.
- **Not needed:**
  - D1–D8 as written;
  - tags and line references;
  - a lower ceiling;
  - before batch 1, a reported-only readout outside the judged path whose diff rule F has seen, with the entry naming the new commit.
- **Corrections from rule F round 3:**
  - Wording, tags, line references, lower ceilings and reported-only code (before batch 1, seen by rule F) need no pass.
  - A change to a judged function, a threshold, the label map, the run lists, the stopping rule (the not-computed cases included), the freeze or the order rules needs one.
  - In doubt, it needs one.

**Notes for the owner**

- **The order clause is still yours.** No run has condition 4 met. `onset_reading` is now fixed before REG-19's data. If you want it as the order reading for burst runs, say so before REG-19's result; it stays blind on batch 2 only until then.
- **Batch 2 may never exist.** It is the only reading on runs not seen when its thresholds were fixed. One attempt of seed 18's control is left. A decision allowing more attempts keeps batch 2 alive for REG-21 and REG-22 alike.
- **Once REG-19 reports,** its table implies much of batch 2: verdicts, end-window values, and whether the line emptied and the cache came back.
- **Correction of my own:** round-1 reason 3 was wrong about REG-12's seeds 2 and 3 (reason 4 above).

**Not checked by me**

- Nothing under `runs/` or the backups was opened. Run ids, validity, verdicts and that no run was read are unchecked.
- Rule F round 3 runs in parallel and I have not seen it. I read rule F round 2 (`round2_rule_f.md` in the bundle) only because it was given as an input; no `rulef-*` file was opened. Its traces (t01–t08) were not re-run.
- `agent/theory/k1_held_prefix.md`, the pinned vLLM source, the full `uv run pytest` and `tools/check_docs.py`.
- Whether `analysis.gate reg19` can produce a table after an operational stop on fewer seeds.
