# Owner-proxy delta pass on REG-22 draft 9 (agent a43b6d3c375ffd53e), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:34:14Z), no word changed. Made on draft 9, before the agent's addendum asking for draft 10 reached it. The agent calls its conditions 1–5 "S1–S5".

---

**Decision: APPROVE**, as a delta pass on REG-22 draft 9 (FILE(docs/drafts/reg22_draft9.md), byte-identical to docs/drafts/review_bundles/reg22_r5/registration_draft9.md) at code `ffc76b3`. HEAD is `4ad587d`; `git diff ffc76b3 HEAD -- analysis harness tests` is empty, and tests/test_c2.py gives 29 passed (my run, synthetic only).

This approval has no effect while rule F round 5 is outstanding or NOT READY. Round 1's conditions 8–16, D1–D8 and Q1–Q7 stay in force. The PROTOCOL re-reading is still not approved; it needs the owner.

**Q1–Q7 are confirmed, each met as I worded it:**
- Q1: line 36's last sentence is F2's text.
- Q2: line 101 gives batch 2's per-run labels and says it resolves draft 6's contradiction in favour of line 102 before any batch-2 data.
- Q3: line 101, "neither line a's permission … nor line d's … applies by itself; any wording … waits for a [DECISION] that cites both batches".
- Q4: line 64 cites decisions.md:3788 (no seed exposed) and lists the `reported_counts` raise; line 136 refers back to it.
- Q5: line 124, the [DECISION] "states which of the two it takes", with the consequence for REG-21's batch 2.
- Q6: line 11 shows 0.6 × 0.7 × 0.20 = 0.084 and 1 − 0.05 − 0.084 ≈ 0.87, with no 0.09 or 0.86 left in the draft.
- Q7: line 133 cites the record's hash, file name, `git merge-base --is-ancestor` for this entry and every commit it relies on, and both `%ct` times; if any part is missing, batch 2 is retrospective.

**Reasons:**
1. **G2 is closed. Draft 7 was looser here, and I missed it in my draft-7 verdict.**
   - Line 132 now freezes the interval from this entry to batch 2.
   - A hunk after the cut makes batch 2 retrospective "before or after batch 1".
   - Rule F's trace X (a `c2.links` fix after the cut, before batch 1) now ends retrospective.
   - The test is the net diff from this entry to batch 2. A change made and reverted before batch 2 leaves batch 2's labels on the registered path, which is the right test for batch 2's standing. The batch-1 [RESULT] (line 148) shows the diff from this entry to batch 1 with each hunk's review.
   - The one new exemption (a reported-only readout before batch 1 needs rule F but no proxy) applies only before the cut. It is still stricter than draft 7, which did not cover that interval, and than draft 6, whose test started at REG-19's heading, after the cut.
2. **G3 is closed, and the rule only removes.** The record is the first saved pair holding the table; an uncommitted or mixed commit means no record and no batch 2. No later pair can move the cut. I also missed the two readings in my draft-7 verdict.
3. **The optional items are all stricter or weaker-claiming:**
   - order (b)/(c) is tested like the cut, and output not committed alone makes every change count as after;
   - no rewritten history;
   - the stamp at final.sh:20 comes before the recheck and the table command (:29), so the cut errs early;
   - A19 is left open (lines 21, 156);
   - line 79 is dated.
4. **Nothing in draft 9 raises a ceiling, widens a threshold or touches the judged path.** Every hunk in text_diff_draft7_to_draft9.diff lowers a ceiling, adds a not-computed case, narrows the record or the freeze, weakens a claim, or fixes arithmetic.
5. **The record rule matches REG-21's current draft.** REG-21 draft 18 (uncommitted) has the same key phrases ("first saved pair", "adds anything besides", "no later than the command", "amended or rebased", `merge-base`, "Mac's clock"). REG-21 draft 17 does not, so "the same as REG-21's" holds only against draft 18.
6. **Not my item, for rule F round 5:** line 180 (rule F round 3's F2 entry) still names line 8 only. G1 asked for it; line 183 says G1 is "met by Q1". This is history-keeping and does not affect any rule.

**Conditions:**
1. **BEFORE the entry is appended (text, no new pass):** in line 132's parenthesis, make three changes.
   - Replace "whose diff rule F has seen" with "whose diff a rule F review has passed with no open required item". As written, a NOT READY review has "seen" the diff.
   - Name what "reported-only readout" covers: the bodies of `onsets`, `onset_reading`, `planned_rates`, `control_readout` and `reported_counts` only. This excludes `__main__`, which prints the labels, and anything the judged path reaches.
   - Test "before batch 1" as order (b) tests "before a batch-1 table exists".
2. **BEFORE the entry is appended (text):** line 135's fix clause refers to line 132.
   - A fix to a frozen readout made with a [CORR] only, and any judged-path fix after the record's cut, makes batch 2 retrospective even when batch 1 needs it.
   - As it stands, a reader following line 135 alone would lose batch 2 without knowing. The conflict is new in draft 9, because the freeze now covers the time before batch 1.
3. **BEFORE the entry is appended (text):** in line 133, write "or its commit changes any path besides those two files" for "adds anything besides those two files". As written, a commit that also modifies a tracked file can be read as adding nothing else. This is the same kind of two readings as G3. The same word goes into REG-21's record text, so the two stay identical.
4. **BEFORE the entry is appended:** check that REG-22's record paragraph and REG-21's, in the versions actually appended, agree in substance. If they differ, drop "(the same as REG-21's)" or align them. If aligning changes the record's definition, that needs a pass.
5. **LATER, at the batch-2 [RESULT]:** list every `reg19_final_*` file that git has ever held, with its stamp and commit (`git log --all --name-status -- 'docs/probe/20261113_reg19/ops_r3/state/reg19_final_*'`), and every [OPS] entry about a `final.sh` try. Show that the record is the earliest saved pair that holds the table. A pair set aside by hand and never committed cannot be detected; say so as a limit.

**Which later changes need another proxy pass:**
- Everything on my earlier lists: the stopping rule, the not-computed cases (other than adding one), the record and its cut, the freeze and its interval, the order rules, the judged path and any threshold.
- New: the reported-only exemption in line 132, beyond conditions 1 and 3.
- Corrections from rule F round 5 need no pass if they are wording, tags, arithmetic, a lower ceiling, a narrower exemption, or an added not-computed case. Anything that widens the exemption, moves the cut, or lets a later pair become the record needs a pass.

**Notes for the owner:**
- **My own errors (for a [CORR]-style note in the [DECISION]):**
  - My draft-7 reason 3 called the freeze "stricter, not looser". It was looser than draft 6 on the interval from the cut to batch 1 (rule F G2).
  - My reason 4 accepted the record without seeing its two readings (rule F G3).
  - Both are fixed in draft 9 without any change from me.
- **Batch 1 may well come after the cut.** Batch 1 waits for REG-21's registration (order a), and REG-19 lacks only seeds 18 and 19. If batch 1 then raises on the judged path, its fix makes batch 2 retrospective. So any batch-1 fix after the cut has a price.
- **Committing the record is still manual.** Whoever runs final.sh must commit the two `state/reg19_final_*` files at once and alone (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:29–31); final.sh does not commit). Otherwise REG-21's and REG-22's batch 2 are both lost. An auto-commit step in final.sh, under its own [OPS] entry before seeds 18–19 finish, would remove that risk; that is your call or the agent's.
- **Different code for the two batches.** If a judged-path change lands before the cut but after batch 1 (rule F plus proxy, allowed), the two batches are judged by different code. The disagreement rule would then compare unlike things. Report batch 1 under both commits if it happens.

**Not checked by me:**
- `runs/`, the backups and any `state/reg19_*` file.
- Rule F round 5.
- Rule F's traces (not re-run).
- The full `uv run pytest` and `check_docs`.
- That both times in the record come from the Mac's clock in practice.
- Whether REG-21's appended text will match draft 18.
