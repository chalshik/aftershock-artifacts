# Owner-proxy, first pass on REG-22 draft 4 (agent a43b6d3c375ffd53e), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input), no word changed. Inputs: `docs/drafts/reg22_draft4.md`, `analysis/c2.py` and `tests/test_c2.py` at `727d1f2`; checked at HEAD `e3bedf1`.

---

**Decision: APPROVE**, on the conditions below: REG-22 draft 4 (FILE(docs/drafts/reg22_draft4.md), byte-identical to the bundle copy) with `analysis/c2.py` and `tests/test_c2.py` at commit `727d1f2` may be appended with its [DECISION] (delegate), and batch 1 computed once.

The approval covers computing and reporting. It does not cover the re-reading of PROTOCOL §3 condition 4 (draft 4:12), which is outside the delegation and stays with the owner (conditions 1 and 2). It has no effect while the adversarial review of draft 4 is outstanding or NOT READY (condition 8).

**Reasons**

1. **State at my check (HEAD `e3bedf1`).**
   - `analysis/c2.py`, `tests/test_c2.py`, `k1.py`, `margin.py`, `load.py`, `stats.py`, `k3w.py` and `withheld.py` are identical at `727d1f2` and at HEAD (`git diff --stat`, empty). The bundle's patch equals `git diff f0ba24e 727d1f2` for the two c2 files (`cmp`).
   - `uv run --offline --frozen pytest tests/test_c2.py -q -p no:cacheprovider`: 22 passed (my run). Draft 4's count is right.
   - The label map of draft 4:31–36 matches the code cell by cell (FILE(analysis/c2.py:179)).
   - `docs/decisions.md` holds no REG-21 entry, no REG-22 entry and no line that begins as REG-19's result heading does (grep). REG-21 is at draft 9 after a fifth NOT READY (commit `e3bedf1`).

2. **Scope (question 1): the analysis is delegated, the re-reading is not.**
   - Delegated: "analysis-only registrations" and "changes to paper claims or their status" (FILE(docs/decisions.md:4233)).
   - Not delegated: "changes to PROTOCOL" is on the owner's list (FILE(CLAUDE.md:19)) and is not among the items the delegation names. The delegation takes GPU runs and claim changes from that list and leaves PROTOCOL, verdict code, thresholds and checks behind.
   - A decisions entry that says how a PROTOCOL rule is read changes the rule in force, because the newer entry rules (CLAUDE.md, Precedence). So "here it is the delegate's" (draft 4:12) claims an approval that a proxy pass cannot supply.
   - The owner's latest word points the other way: "Verdict rules and the six conditions (PROTOCOL §3) | Unchanged; they judge every P0 run" (FILE(docs/experiment-plan.md:390); FILE(PROTOCOL.md:16)).
   - The order is also in the claim's own test: "the loop figure (helper metrics in the plan's order)" and "stuck runs that show the order and the memory limit" (FILE(docs/claims.md:25), FILE(docs/claims.md:26)). Draft 4:11 quotes the test with an ellipsis over these words and gives the order to PROTOCOL alone.
   - The analysis need not wait, because nothing it computes depends on who owns the reading:
     - `c2.levels` is condition 4's levels as registered on 2026-11-01 (FILE(docs/decisions.md:285), FILE(analysis/c2.py:85)). The thresholds are unchanged, the end window is the config's 600 s (FILE(configs/stage2_cap_base.yaml:8)), and "N below the cap" is read as the maximum, the strict reading.
     - `sustain` is a new statistic with its own labels.
     - The onsets report the order.
   - With conditions 1 to 3 this is the narrower registration in substance: the registered levels, REG-22's own description beside them, the order reported. A registration with no label on `sustain` would also be approvable; I do not require it.
   - The proposal is not foreign to the plan, which says "They should move in this order and then stay there" (FILE(docs/experiment-plan.md:285)). `sustain` reads the second half. Whether the first half may be dropped for a burst is the owner's choice.
   - The owner asked that nothing wait and can overrule (FILE(docs/decisions.md:4232), FILE(docs/decisions.md:4236)).
   - "It is listed for the owner" (draft 4:12) is not yet true: `agent/FOR_AUTHOR.md` has no line on REG-22 (grep at HEAD).

3. **Rule A1 (question 2): it may be registered and run, but batch 1 is more settled than the text says.**
   - Worth computing at 0 GPU h:
     - the levels fill a gap the claims file names, "condition 4 has not been computed on them" (FILE(docs/claims.md:31));
     - batch 2 is on unread data;
     - the eviction histograms read the eviction link directly, with a forecast that can fail (draft 4:75–77);
     - the same-seed control's links are the one readout here that bears on overload against a loop.
   - Published values already fix most of batch 1's `sustain`:
     - Sessions' hit share is 0.000 and KV about 0.95 in every published span of every burst run (FILE(docs/decisions.md:2316), FILE(docs/decisions.md:2480), FILE(docs/decisions.md:2840), FILE(docs/decisions.md:3546), FILE(docs/decisions.md:3747)).
     - For REG-15: "Every 300 s window from 1200 s to the end has hit 0.000 and KV 0.947–0.955" (FILE(docs/decisions.md:3105)).
     - A span `holds` in `gate.burst_backlog` only if no burst request ended in it (FILE(analysis/margin.py:76)). So for REG-11, REG-14 and REG-12's seeds 2 and 3 the exit lies before 1680 s, unless a burst request never ended.
     - REG-18's seeds 3 and 6, named as candidates (draft 4:56, 60), had hit 0.000 and a waiting line of 121 and 101 in their quiet spans (FILE(docs/decisions.md:3743), FILE(docs/decisions.md:3745), FILE(docs/decisions.md:3747)).
   - No table shows the span [1380, 1680) s of the twelve 1500 s runs, N per span for most runs, or the uncached rate, which follows from hit 0.000 and the completion rates.
   - So "where an outcome is open" (draft 4:56) overstates. The likeliest outcome of batch 1, `loop` in all eleven, changes no decision, and the text gives no probability for an outcome that does.

4. **Rule A5 (question 2): no threshold is widened; the description is honest but incomplete.**
   - The levels' thresholds predate every stuck run (FILE(docs/decisions.md:285)).
   - New here: 2 × for the uncached rate, two judged spans, 20 later turns, one failing span decides, three stuck runs for a sentence, "more than half". None widens an existing threshold.
   - For batch 1 they are fixed after the runs were reported. The study's standard for that is a retrospective reading that is never called a test (FILE(docs/experiment-plan.md:413), FILE(docs/claims.md:82)), and draft 4:4 adopts it. For batch 2 they are fixed before the data, if the commit order holds.
   - The arithmetic checks out (DERIVED, recomputed): 30.2 and 42 requests in the pool; 6.19; 4.46 to 5.61; 0.807; 0.658 to 0.767; lags of 4.3, 15 and 56 s; 0.97⁹ = 0.76.
   - Three errors:
     - "1500 s (eleven runs)" (draft 4:15) should be twelve of the 13 runs, ten of the eleven stuck ones (DERIVED from FILE(configs/stage2_base.yaml:13) and FILE(configs/confirm_l1pl350cl_r2.2_s12.yaml:13)).
     - "2 of about 58 judged spans" (draft 4:60) should be at most 54 (DERIVED: 10 × 4 + 14). That is 3.7 %, and 0.963⁹ = 0.71.
     - The uncached rate's lag uses a rise of 4.4 to 5.2 (draft 4:74). The 4.5 to 5.6 × of draft 4:27 gives 3.5 to 4.6, so 13 to 17 s (DERIVED: 60 / 4.6, 60 / 3.5).
   - Missing from "What was known":
     - the per-span values of reason 3;
     - the interim look at seed 17's control (FILE(docs/decisions.md:4276)), a run that batch 2's control readout reads;
     - that `continue` True also means the seeds so far gave neither `surge_reading_wrong` nor `controls_not_healthy` (FILE(analysis/gate.py:1703));
     - that condition 4's levels were computed once before on another window, the last 1500 s of REG-15's watch (FILE(docs/decisions.md:3108)).

5. **Template and rules B, H, I, J (question 3).**
   - **Rules E and F:** the entry cites the draft-3 review by path (draft 4:3) and does not hold it.
   - **Rule A1:** the batch-2 prediction is not conditional on batch 2 being computed, and gives no chance that it has fewer than three stuck runs.
   - **Rule B,** not tagged or tagged in no listed form:
     - "RUN(REG-12's five burst runs, …)" and its like name no run id (draft 4:42, 56, 80), and the verdicts come from `load.verdict`;
     - "the review's computation, same file" and "the review's trace E" name no file (draft 4:7, 26);
     - the 42 requests and "above 15" are DERIVED without the tag (draft 4:16);
     - "Both ended cold, full and backlogged" (draft 4:43);
     - "The other [RESULT] entries report hit 0 and KV 0.95 at the end" (draft 4:53), which also understates: in every span;
     - "New in batch 1" (draft 4:54) cannot be checked and is BELIEF;
     - the eviction forecast cites a file without the FILE form (draft 4:76).
   - **Rule H:**
     - the command's `by_load` groups by load alone (FILE(analysis/c2.py:344)), so its 2.2 row counts the 1500 s and the 4500 s run together, against draft 4:38;
     - the pooled `counts` carry the prediction with no word that they are a tally over six distinct seeds;
     - each run has a single same-seed control, not labelled as such.
   - **Rule J:**
     - the levels have a second computation on record (REG-15's, reason 4);
     - the uncached rate has three: `c2.session_uncached_rate`, `k3w.work_rate` and `recomputed_prefill_tok_s` (FILE(analysis/load.py:75));
     - R, the block idle time, is defined with "Code: none" (FILE(docs/definitions.md:104)) and gains code here;
     - "metastable failure" says "Code: none" (FILE(docs/definitions.md:136));
     - the drafted block covers none of these (FILE(docs/drafts/definitions_reg21_reg22.md:27)).
   - **Ledger:** the drafted row differs from draft 4:60–61 in every number (FILE(docs/drafts/definitions_reg21_reg22.md:45)).
   - **Alternative 3** has no separating evidence here: the registered preemption comparison has no code and no registration (FILE(docs/definitions.md:102)).
   - **Present and adequate:** the question, numeric predictions, six alternatives, named functions with lines that resolve, counts with both bounds, no pooling across loads in the text, the stopping rule, the cost.

6. **Decision lines (question 4): four say more than the data carry, and the qualifier is not enough.**
   - "Condition 4, as read by REG-22, met" (draft 4:66) will be shortened to "condition 4 met". Under condition 1 the phrase goes.
   - The same line allows a status sentence for λ = 2.4, a load whose matrix came out `controls_not_healthy` and "cannot speak to C1" (FILE(docs/decisions.md:2462), FILE(docs/decisions.md:2484)).
   - It does not say which batch the status rests on, or what is said if the batches differ.
   - `not_memory_limited` (draft 4:67) calls "the stuck runs at that load" backlog states without saying how many must carry the label.
   - `not_sustained` (draft 4:68) words only the reuse and the uncached rate. A quiet span can fail N or KV with the cache still lost; REG-19's seed 18 plans 1.32 req/s in one span (FILE(docs/decisions.md:3785)).
   - The label `loop` names a finding that the entry's first paragraph disowns (draft 4:6).
   - Adequate: draft 4:9 (computing and reporting only), the wording by the level or link that failed, the onset ceiling of draft 4:74.

7. **The order against REG-21 (question 5): right in one direction, missing in the other.**
   - REG-21's command prints U and the reuse over the same three spans of the same runs (FILE(analysis/k3w.py:403), FILE(analysis/k3w.py:414)). After the exit that U is REG-22's session uncached rate, since no burst row is left (FILE(analysis/k3w.py:104), FILE(analysis/c2.py:68)).
   - So REG-22's batch 1 also prints the numerator of REG-21's judged r for eleven of its 13 runs. Draft 4:88 computes it "before REG-21's batch 1" and does not ask that REG-21 be registered first. REG-21 is not registered.
   - The fallback of draft 4:55 adds REG-21's table to what was known, but leaves REG-22's judged path free to change afterwards.

8. **Batch 2 (question 6): protected against accident, with four gaps.**
   - The guard works as described. `batch2_runs` raises before the heading whatever `AFTERSHOCK_UNSEAL` holds (FILE(analysis/k3w.py:345), FILE(analysis/withheld.py:46)), and its test passes.
   - "No selection after a raise" is in the text (draft 4:44, 92).
   - The freeze list (draft 4:91) names what `reg22_table` calls. "Outside that path" should mean outside everything it reaches.
   - Gaps:
     - no comparison of the runs read with the runs REG-19's final result counts;
     - no proof of the commit order in the [RESULT];
     - no order with REG-20's gate, whose inputs (reuse and KV at the end of REG-19's closed runs) batch 2 prints;
     - no saved output, so "computed once" rests on the log alone.

**Conditions**

BEFORE the entry is appended:

1. **The reading.** Draft 4:12 is replaced by text that says, in these words or narrower:
   - "REG-22 changes no rule. PROTOCOL §3 condition 4 and C2's test in `docs/claims.md` stay as written, the order clause included. REG-22 computes condition 4's registered levels and reports the onset order. It does not judge the order clause on any run."
   - "`sustain` and the four labels are REG-22's own description. That `sustain` could stand for the order clause on burst runs is a proposal to the owner. It is in force only after an entry headed `[DECISION] (owner)` says so."
   - "Until then no entry, status line, claims line, definition or paper text says that condition 4 is met, holds or is passed for any run or load, with or without 'as read by REG-22'. No REG-22 label is counted towards the six conditions of PROTOCOL §3."

   Also:
   - "here it is the delegate's" and the sentence promising a note in PROTOCOL §3 are deleted;
   - draft 4:9 says that an edit to PROTOCOL needs the owner, not a delegate decision;
   - "condition 4, as read by REG-22" (draft 4:12, 66, 110) becomes "condition 4's registered levels" for `levels` and "the links in every judged span" for `sustain`;
   - draft 4:11 quotes C2's test and its "Supports" line in full, and says that REG-22 makes no loop figure.

2. **PROTOCOL.md is not edited under REG-22,** by note or by pointer. Neither is `docs/experiment-plan.md`.

3. **Decision lines,** each a lower ceiling:
   - **a. The `loop` line.** A status sentence says at most: "condition 4's registered levels held at the end of the watch, and all four links were present in every 300 s span after the burst's requests had left, in k of n stuck runs at λ = x (both bounds); the order clause is not judged and no loop figure exists; an overload gives the same picture; the loop-cut controls are not run." It also gives:
     - the batch and its standing: batch 1 "thresholds fixed after these runs were reported"; batch 2 "registered before REG-19's table", only if the commit order of condition 14 holds;
     - how many of the k runs have a same-seed control that is `recovered` and holds all four links in no judged span (REG-15's run has no control);
     - "batch 2 pending" while batch 2 does not exist; afterwards both batches' counts side by side, with no summary across them.
   - **b. λ = 2.4** is given with the words "at the closed-loop warm capacity; three of five controls did not stay healthy (REG-12)". It is the overload comparison and is not cited as support in C2's status.
   - **c. `loop` is a code label.** Headings, status, claims and paper text spell the outcome out as in (a). None says the loop was shown, found, present or confirmed.
   - **d. `not_memory_limited`:** the sentence is about the runs that carry the label. "Against C2 for that load" and "D1 and D2 not proposed as planned" need KV < 0.80 in more than half of at least three stuck runs at the load.
   - **e. `not_sustained`:** where only N or KV failed, the wording is "the batch (or the pool) was below its level in span …, with the reuse still lost", with the span's planned session rate beside it.
   - **f.** Any sentence that gives a `loop` count gives the other three counts of that load and batch beside it.
   - **g.** The entry says that the command's `by_load` row for 2.2 counts two watch lengths together and is never quoted.
   - **h. Onsets:** the [RESULT] gives, per stuck run, the order found beside the plan's order, and one tally over the runs (the plan's order beyond the lags; not distinguishable from simultaneous; differs). No pass or fail is attached.

4. **"What it can and cannot show", "What was known" and the prediction** add or correct:
   - the published per-span values of reason 3, with their lines, and what they leave unpublished; draft 4:56 is rewritten to match;
   - a probability (BELIEF) that all eleven runs are `loop`, and for each batch a probability that any decision changes; the sentence that the likeliest outcome of batch 1 changes none;
   - the interim look at seed 17's control and the second meaning of `continue` True;
   - REG-15's earlier computation of the levels over the last 1500 s;
   - the batch-2 prediction made conditional on batch 2 being computed, with a probability (BELIEF) that it is not and that it has fewer than three stuck runs, and the fact that three burst runs exist today;
   - the three arithmetic errors of reason 4, with the prediction restated to match.

5. **Rules B and H, and alternative 3:**
   - every item of reason 5's rule B list is tagged, with run ids or FILE(docs/decisions.md:line) in place of "REG-12's five burst runs";
   - every FILE(path:line) is resolved again at the commit that holds the entry;
   - the 13 run ids are listed, or FILE(analysis/c2.py:307) is cited;
   - "a tally, no bound; the eleven runs hold six distinct seeds" stands beside the pooled counts;
   - "single same-seed control" stands beside the control readout;
   - alternative 3 says that this registration does not separate it, and that the registered comparison has no code and no registration.

6. **The order with REG-21, in both directions.** This replaces the last sentence of draft 4:55 and "before REG-21's batch 1" in draft 4:88.
   - **a.** Neither batch 1 is computed until both registrations are committed with their [DECISION] (delegate) entries. After that the order of the two computations is free.
   - **b.** If REG-21 is not registered when REG-22 is ready, REG-22's batch 1 waits. The one exception: a [DECISION] (delegate) entry records that REG-21 is deferred and names the commit at which REG-21's judged path stands, and REG-21's draft gains REG-22's table under "What was known".
   - **c.** If REG-21's batch 1 is computed before REG-22's entries are committed, REG-22's "What was known" gains REG-21's table, and REG-22's constants, label map and judged functions must be those of `727d1f2`. A change to them after that table exists is a threshold chosen after its data (rule A5, not delegated): batch 1 is then reported as values without labels, or waits for the owner. Batch 2 keeps its labels if the commit order of condition 14 holds.

7. **The owner is told,** in the same commit:
   - `agent/FOR_AUTHOR.md`, at the top and under "Decisions you may want to overrule": the proposal of condition 1; the three choices (accept `sustain` for burst runs; have the literal order judged; drop the order clause for bursts); and the deadline of the second: a blind order test on REG-19's runs must be registered before REG-22's batch 2 prints their onsets;
   - `docs/status.md`, open risks: condition 4's order clause is unjudged on every run and waits for the owner;
   - `docs/open-questions.md`: the BELIEF of draft 4:12 (on a burst run the trigger's own signals come first) as an open item that the onsets answer.

8. **Reviews:**
   - The adversarial review of draft 4 has returned and is not NOT READY. If it is NOT READY, nothing is appended. A new draft goes to rule F again, and to a proxy only if a change is on the "needed" list below.
   - The entry holds, verbatim and with every quoted line prefixed, the rule F reviews of drafts 3 and 4 and of any later draft, each followed by what was changed because of it.
   - This verdict is verbatim in the entry or in the [DECISION] (delegate).
   - The [DECISION] (delegate) lists, for each of conditions 1 to 7, the sentence or file line that meets it, and has a bullet "For the owner: condition 4's order clause".

BEFORE batch 1 is computed:

9. All of the following hold:
   - condition 6a or 6b;
   - `docs/definitions.md` has the terms of draft 4:96 and, marked ⚠ where a term has more than one computation:
     - the levels, naming REG-15's window;
     - the session uncached prefill rate, naming `k3w.work_rate` and `recomputed_prefill_tok_s`;
     - the reuse with its minimum of turns, and the exit;
     - R with its code, and the turn spacing;
   - "metastable failure" there says that condition 4's levels have code and its order clause has none; no definition says condition 4 is met;
   - `docs/model.md` has the ledger row, equal to the entry's prediction;
   - `docs/status.md` names the registration's state;
   - the commit holding both entries exists and its hash is recorded;
   - `git diff 727d1f2 <that commit>` is empty for `analysis/c2.py`, `k1.py`, `margin.py`, `load.py`, `stats.py`, `k3w.py` and `withheld.py`, or each hunk is shown to lie outside everything `reg22_table` reaches;
   - `git diff` for `PROTOCOL.md` over the same range is empty, or its hunks belong to an owner's entry;
   - `analysis/` and `tests/` have no modified or untracked file; `uv run pytest` and `python3 tools/check_docs.py` pass.

LATER, in a [RESULT]:

10. Each batch's command output is saved verbatim in a committed file. The [RESULT] quotes from it and gives its path, its sha256 and the commit. A second run of a batch's command is a deviation and is logged.

11. The batch-1 [RESULT]:
    - keeps the wording of conditions 1 and 3;
    - confirms 11 stuck runs and the two `bad_baseline` runs left out, as the entry names them; a difference is a deviation, reported first;
    - gives k of n per load with both bounds (`stats.cp_upper`), and names the computation of every quoted value;
    - gives every span of every run with its judged flag, the exit and the row counts;
    - gives the control readout per run with the words "single same-seed control";
    - repeats the seed pairing beside the loads' counts;
    - says that most of the table restates published values, and names what was new;
    - scores the prediction and updates the ledger.

12. Batch 2 is computed once, after REG-19's final result. Before the command runs, the valid folders matching the batch-2 pattern (names and `valid` only) are compared with the burst runs REG-19's final [RESULT] counts. If they differ, or `batch2_runs` raises, batch 2 is not computed and is reported so. No pattern, function or validity flag changes afterwards.

13. REG-20's gate (`python -m analysis.k1 reg20_a_may_start`) is computed before REG-22's batch 2, or both results state the order.

14. The batch-2 [RESULT] shows:
    - **the commit order:** REG-22's entry commit is an ancestor of the commit that adds REG-19's result heading, and REG-19's entry gives the time its table was first computed, later than REG-22's commit. If not, batch 2 is labelled retrospective;
    - that the heading which lifted the seal is REG-19's final result;
    - **the unchanged judged path:** an empty `git diff` for the files of condition 9 between the batch-1 and batch-2 commits, or every hunk outside everything `reg22_table` reaches. If not, rule F and a proxy pass come first;
    - the run comparison of condition 12;
    - both batches' counts side by side (condition 3a).

15. If a command raises, a fix outside the judged path is a [CORR] before the table is read. A fix on the judged path needs rule F and a proxy pass before the rerun. The raises of condition 12 are excepted.

16. Any edit to `docs/claims.md` or `docs/paper/` that rests on REG-22 needs its own decision, rule F review and proxy pass, and stays under the ceilings of conditions 1 and 3. An edit to PROTOCOL needs the owner.

**Which later changes need another proxy pass.**
- **Needed** for any change to:
  - the constants of `c2.C2`, the reuse drop of 0.06, the windows, the span grid, the exit and the rule for a judged span;
  - the label map, "one failing span decides", the minimum of two judged spans and of 20 turns;
  - the selection by the verdict `stuck`, the run lists, the batch-2 pattern, seeds and minimum, the heading test and the seal;
  - "at least 3 stuck runs", "more than half", and the rule that loads and batches are not pooled;
  - the stopping rule and the freeze between the batches;
  - the behaviour of any function on the judged path;
  - the `__main__` block, beyond adding a reported key or a refusal;
  - wording that raises a ceiling of conditions 1 and 3, or that puts the proposal of condition 1 in force.
- **The judged path** is the list of draft 4:91 and everything those functions reach.
- **Not needed** for:
  - conditions 1 to 9 as written;
  - further tags, or corrected arithmetic that moves no threshold;
  - a lower ceiling;
  - a reported-only readout registered before batch 1 with code outside the judged path, once rule F has seen the diff;
  - a change limited to comments and docstrings;
  - renaming the label string `loop` with its tests, if the label map is otherwise unchanged and rule F has seen the diff.
- **Corrections the parallel adversarial review may still require** follow the same split. Wording, tags, a lower ceiling and reported-only code need no proxy pass. A change to a judged function, a threshold, the label map, the run lists or the stopping rule needs one. In doubt, it needs one.
- **After batch 1 is computed,** any change to the judged path or the label map needs a proxy pass, and the batch-2 [RESULT] says it was made knowing batch 1.

**Notes for the owner**

- The first thing to decide is condition 4's order clause for burst runs. Until you do, no run in this study has condition 4 met, and the six conditions of PROTOCOL §3 cannot be claimed at any load.
- Your documents pull two ways. The revised plan's figures and done list no longer hold the loop figure or the order (FILE(docs/experiment-plan.md:397)); PROTOCOL §3 and C2's test still do.
- Expect "all eleven" from batch 1. Published tables nearly imply it, and λ = 2.4, an overloaded cell, will carry the same label. It is no evidence for a loop over an overload.
- Batch 2 is the only part on unread data. It exists only after REG-19's final result, and a sentence about it needs three stuck runs.
- I read the delegation as not covering PROTOCOL. The agent's plan assumed a proxy pass would do (FILE(agent/STATE.md:45)). If you meant PROTOCOL notes to be delegated, one entry settles it.
- The registered preemption comparison of 2026-11-01 still has no code and no registration.
- REG-22's control readout prints per-span reuse, uncached rate, N and KV of controls that draft REG-23 (K5) means to read. REG-23 must list that as known, or be registered first.
- Preferences, not conditions: rename the label `loop`; add each span's lowest KV and N as a reported readout; date the heading on the day it is appended.

**Not checked by me**

- Nothing under `runs/` or the backups was opened. So I did not check that the 13 runs exist and are valid, their verdicts under today's code, that no run was read while drafting, or that the exits, onsets and uncached rates were never computed.
- The rule F reviews were not read, the bundle's `round1_rule_f.md` included. So I did not check "NOT READY, ten items", the mapping R1 to R10, or the numbers quoted as the review's (trace E, the 70 s, "about half of the offered rate").
- The pinned vLLM source for the eviction histogram and its 1 % sampling, and `agent/theory/k1_held_prefix.md`.
- The full `uv run pytest` and `tools/check_docs.py`, which list `runs/`.
- `load.verdict`, `load.find_runs`, `load.load_run` and `stats.cp_upper` line by line.
