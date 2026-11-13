# Owner-proxy delta pass on REG-21 draft 9 (agent a4122f052f465a926), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input), no word changed. A delta to the round-4 approval (`proxy-reg21-draft6-r4.md`); code at `8164211`.

---

**Decision: APPROVE**, with conditions C1–C6 below. This approves REG-21 draft 9 (FILE(docs/drafts/reg21_draft9.md), byte-identical to the bundle copy) with code at `8164211`, as a delta to the round-4 approval. Round-4 conditions 1 and 7–12 stay in force unchanged. Conditions 2–6 are met (reason 6). As before, this approval has no effect while rule F on draft 9 is outstanding or NOT READY.

State at my check: HEAD `59e1d49`; it moved from `d170f2f` during the pass. `git diff 8164211 HEAD` is empty for `analysis/k3w.py`, `withheld.py`, `k1.py`, `load.py`, `gate.py`, `margin.py`, `stats.py`, `derived.py` and `tests/test_k3w.py`. Since `8164211` only `analysis/c2.py`, `analysis/k5.py` and their tests have changed. The bundle diff equals `diff reg21_draft6.md reg21_draft9.md`.

**Reasons:**

1. **(A1) Every raise of batch 2's selection after REG-19's final result gives "not computed", with no fix (draft 9:27, 105; also 75, 84): accepted.**
   - The two new causes are real, as far as the code shows.
     - `find_runs` loads every matching folder that has a `config.yaml` before it filters on validity. `load_run` reads `env.json` without a guard (FILE(analysis/load.py:32), FILE(analysis/load.py:42)), so a cut-off folder makes it raise.
     - `lifted` accepts only `## <date> · [RESULT] REG-19` (FILE(analysis/withheld.py:46)).
   - The rule is right, and more needed than the text says. REG-19's [RESULT] publishes each seed's completion rate c over W (FILE(docs/decisions.md:3799)), and REG-19's W is REG-21's batch-2 window, 1680–4080 s (FILE(docs/decisions.md:3778)). r ≈ (c ÷ 1.681) × a prompt factor of 0.98–1.00 (draft 9:51). So once REG-19 reports, batch 2's r is close to known (DERIVED). Any later act that decides whether batch 2 exists, or what it holds, is then made knowing its outcome.
   - What it costs: batch 2 can be lost to a slip, such as a malformed heading or a lost burst folder copied into `runs/`. That is the right trade. Two gaps remain, closed by C1:
     - REG-19 ending without a table;
     - a breach of duty (a), which has no stated consequence.

2. **(A2) The two duties done by hand (draft 9:106): accepted, with C1.**
   - (b) is round 4's comparison, with both lists recorded.
   - (a)'s copy clause fits the owner's resume decision. That decision puts lost folders into `runs/` only after REG-19's [RESULT], with no deadline (FILE(docs/drafts/reg19_resume_decision_draft5.md:70), FILE(docs/drafts/reg19_resume_decision_draft5.md:72)). The lost folders so far are controls, which the batch-2 pattern does not match (FILE(analysis/k3w.py:65)).
   - Gap: "the seeds REG-19's final [RESULT] counts" has no defined meaning when REG-19 ends on an operational stop. REG-19 then has no table (FILE(docs/decisions.md:3808)). This case is likely:
     - 2 of REG-19's 8 launches were lost (DERIVED from FILE(docs/decisions.md:4308)), and seed 18's control has one attempt left;
     - in that case `batch2_runs` returns seeds 15–17 without raising, so whether batch 2 is computed would hang on how one word is read, after the outcomes are public.

3. **(A3) "The owner can overrule … before batch 1 is computed" (draft 9:55): accepted, but this point is not the only one that should close the window (C2).**
   - Moving the point earlier is stricter, and it is right under rule A5: after batch 1, one side of the 0.05 contrast is known.
   - But batch 1 is not the only thing that reveals it:
     - REG-22's batch 1, planned before REG-21's (FILE(docs/drafts/reg22_draft4.md:88)), prints an uncached-token rate (`c2.session_uncached_rate`, FILE(analysis/c2.py:68)) on the same 13 runs. That rate is U without the burst rows.
     - REG-19's [RESULT] gives batch 2's side (reason 1).
   - If batch 1 waits for REG-22 (A5), the window as written could stay open past both.
   - The owner keeps the right to overrule at any time (FILE(docs/decisions.md:4236)). What must be fixed is when an overrule counts as blind.

4. **(A4) The judged path listed function by function (draft 9:102): accepted.**
   - At `8164211` I traced the calls of `reg21_table` → `_judged`, `select`, `row`, `reference`, `batch1_runs`, `batch2_runs`:
     - `k1.cold_backlogged` → `_state` → `load._level`, `reuse` → `later_turns` → `margin.is_burst_request`; `windows`; `SURGE["kv_onset"]`;
     - `gate.burst_end`; `load._covered`;
     - `find_runs` → `withheld.keep`/`sealed_by`/`lifted`/`unsealed_ids`, `load_run` → `guard`, `_jsonl`, `metrics_wide`.
   - Every one is named in the list, and I found nothing on the path that it leaves out.
   - The list is wider than draft 6's, and the fix clause now uses "judged path" (draft 9:104). Both are stricter.

5. **(A5) Batch 1 only after REG-22 is registered: an acceptable order, and it must be written into REG-21's entry (C3, C4).**
   - The conflict runs both ways: each table prints values the other judges (FILE(docs/drafts/reg22_draft4.md:55)). The safe order is that both [REG]s are committed before either batch 1 is computed. Then both sets of thresholds are fixed blind, and the order of the computations matters only for the overrule window (C2).
   - A plan held outside the entry is not evidence (rule B), so the entry has to state it.
   - It needs a way out so that a stalled REG-22 cannot block REG-21 forever. Batch 2 cannot run before batch 1's [RESULT] (draft 9:84).
   - Its mirror image is a precondition on REG-21's own append: its "U … r have not been computed" (draft 9:49) must still be true when the entry is appended.

6. **(B) Round-4 conditions 2–6 against draft 9, one line each.**
   - **2, met (72–76):** the ceiling "at the tolerance", with everything given together; no "within 0.05" or "r times" from one batch; K3's status wording; batch 2's label always stated; `EPS` in the comparison (FILE(analysis/k3w.py:91) resolves to it); the contrast's description (76, 84).
   - **3, met (55).**
   - **4, met (27, 75, 84, 105, 106, 59):** every raise; "not computed" treated as "undefined"; the fix clause excluded; the flag rule and the hand comparison; the prediction conditional on batch 2, with P(not computed) and "three burst runs exist today".
   - **5, met (76, 85):** `r_first` for every run of either batch, which the code does (`reported_spans` loops over the whole batch); "tells" removed.
   - **6, met in the text (53, 54, 9, 26, 32, 89, 117, 44):** I spot-checked 24 line references at HEAD and all resolve (status.md:21 holds the draft-2 review summary). `vj_counts` does what line 44 says.
     - Line 83 moves "busy 0.947, r 0.969" from the draft-3 review to the round-3 review's trace C. I could not check this (see "Not checked by me").
   - **Nothing else in the diff moves a ceiling or a rule.** U, U_off, r, W, the preconditions, both tolerances, the 0.05, the minimum counts, the run lists, the pooling rule and the governing rule (beyond condition 2) are unchanged. Every other hunk is one of:
     - a tag or line number;
     - a prediction;
     - a description of reported-only code;
     - a lower ceiling: 66, "outside low" worded per group; 71, "whose r had not been computed" and the note on REG-19's flag;
     - a stricter stopping rule: 102, 104.

**Conditions:**

BEFORE the entry is appended:
- **C1. Text added to draft 9:106 and draft 9:59:**
  - "Counts" means the seeds in n of the table that `analysis.gate reg19` computes, as REG-19's final [RESULT] reports it.
  - Batch 2 is not computed, with the reason, in each of these cases:
    - REG-19 ends without that table (an operational stop or spent attempts);
    - before batch 2, a later entry changes the seeds that table counts or the validity flag of a matching run;
    - duty (a) is breached.
  - The prediction's P(batch 2 never computed) is restated with this case counted, as BELIEF, citing 2 lost launches of 8.
- **C2. Text replacing the overrule sentence at draft 9:55:** the owner's overrule counts as made blind only before the first of:
  - REG-21's batch 1;
  - any computation that prints U, an uncached-token rate or r on a λ = 2.0 batch-1 run (REG-22's batch 1 does);
  - REG-19's final [RESULT].
  
  A change made after that point is labelled in the batch-2 [RESULT] with what was public at the time. If the delegate makes it, it needs rule F and a proxy pass.
- **C3. Text added to the stopping rule (draft 9:100):** batch 1 is not computed before REG-22's [REG] and its delegate [DECISION] are committed, unless a [DECISION] records that REG-22 is withdrawn or will list REG-21's batch-1 table as known.
- **C4. Checked at append and stated in the [DECISION] (delegate):** no computation has yet printed U, an uncached-token rate, `k1.reuse` or the busy share on a batch-1 or reference run, REG-22's batch 1 included. If one has, the entry is not appended as written: "What was known" is rewritten, and the draft goes to rule F and a proxy pass.

BEFORE batch 1 is computed:
- **C5.** The `docs/status.md` line of round-4 condition 8 also says this: no lost or invalid folder of a REG-19 burst config enters `runs/` until REG-21's batch 2 has been computed or declared not computed.

LATER:
- **C6. Batch-1 [RESULT]:** states whether any computation printed an uncached-token rate on these runs before it (REG-22's batch 1 included), naming the commit.
- **C6. Batch-2 [RESULT]:** states that REG-19's [RESULT] had published c over the same W, so batch 2's r was roughly implied when computed. It keeps the wording at draft 9:71 exactly.

C1–C4 are stricter text and need no further proxy pass. The [DECISION] (delegate) lists the sentence that meets each, as round-4 condition 7 requires for conditions 2–6.

**Which later changes need another proxy pass:**
- **Needed:** every item on round 4's "needed" list, plus any change to:
  - the "Batch 2 not computed" bullet;
  - the two hand duties;
  - C1's definition of "counts";
  - the overrule window;
  - the order with REG-22.
- **Rule F corrections from the parallel review:**
  - Wording, tags, line references, lower ceilings and reported-only readouts need no pass.
  - Anything that touches the stopping rule needs one. That includes making batch 2 computed in a case that draft 9:105 or C1 makes "not computed", or the reverse. So does anything touching the governing or pooling rule, the judged path, a tolerance, a precondition or the run lists.
  - In doubt, it needs one.
- **A further text-only round of rule F** needs me again only if it changes one of the items under "Needed".

**Notes for the owner:**
- Under C2, your window to overrule "the two batches" (for example with "batch 2 always governs") closes at the first of the three events. That may be before you are back. If you want a change, write it now.
- Once REG-19 reports, batch 2's r is close to known from REG-19's own c over the same W. Batch 2 is "r not computed when the tolerance was fixed", not "unread". That is why every choice after the result is closed.
- P(batch 2 never computed) is likely above 0.25. A third loss of seed 18's control ends REG-19 without a table, and under C1 it ends batch 2 too (DERIVED: 0.25 per launch; 1 − 0.75² ≈ 0.44 over two more launches, 1 − 0.75⁴ ≈ 0.68 over four, if each loss ends REG-19; BELIEF). A decision allowing more attempts keeps batch 2 alive.
- Recommendation, not a condition: whoever appends REG-19's [RESULT] runs `withheld.lifted('[RESULT] REG-19')` before committing it. Under draft 9:105, a heading the seal rejects ends batch 2 for good.
- REG-20's code sits in `k1.py`. If REG-20 changes `cold_backlogged`, `reuse`, `later_turns`, `_state` or `windows` between the batches, batch 2 needs a review made after REG-19's outcomes are public, or it becomes retrospective. Putting REG-20's changes in new functions avoids that.

**Not checked by me:**
- I opened nothing under `runs/` or the backups, so the existence and validity of the runs are unchecked.
- I read no `rulef-*` file, so these are unchecked: the change in who is credited for "busy 0.947, r 0.969" (draft 9:83), and whether the items of rounds 4 and 5 are met.
- I did not run pytest; no judged code changed since `8164211`, where round 4 ran 35 passing tests.
- I spot-checked 24 line references at HEAD, not all of them, and not at the commit that will hold the entry.
- I checked the judged path by reading the code, not with a call-graph tool.
- I read REG-22 draft 4 only for its lines on REG-21, so I did not check which windows its uncached rate uses.

Scratch copy of the draft 6→9 diff: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r6_proxy/d6d9.diff
