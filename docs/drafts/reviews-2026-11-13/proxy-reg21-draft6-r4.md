**Decision: APPROVE**, on the conditions below: REG-21 draft 6 (FILE(docs/drafts/reg21_draft6.md), byte-identical to the bundle copy) with the code at commit `8164211` may be appended with its delegate decision, and batch 1 computed once. The approval has no effect while the adversarial review of draft 6 is outstanding or NOT READY (condition 1).

**Reasons**

1. **Scope and state at my check (HEAD `e26c31d`).**
   - An analysis-only registration at 0 GPU h is delegated (FILE(docs/decisions.md:4233)). Draft 6 edits no run, used config or old entry, and moves no existing tolerance.
   - `docs/decisions.md` holds no line that begins as REG-19's result heading does, and no REG-21 entry (grep, today). REG-19 has seeds 15 to 17 done and stopped in seed 18's control (FILE(docs/decisions.md:4293)).
   - `analysis/`, `tests/`, `harness/` and `configs/` are identical at `8164211` and at HEAD (`git diff --stat`, empty).

2. **The code since round 3: no judged function changed.**
   - `git diff 69ffedd 8164211 -- analysis/k3w.py analysis/withheld.py` has four hunks, all in `k3w.py`: the module docstring, one import, a new block after `reg21_table`, and the `__main__` block. The bundle's patch equals it.
   - `withheld.py`, `k1.py`, `load.py`, `gate.py`, `margin.py`, `stats.py`, `derived.py`, `k3.py` and `modelf_sim.py` are unchanged between the two commits.
   - A syntax-tree comparison shows every function and constant of `69ffedd` identical in `8164211`, `REG21` and `EPS` included. New: `REPORTED`, `span_values`, `reported_spans`, `vj_counts`, `_dirty`.
   - `uv run --offline --frozen pytest tests/test_k3w.py -q -p no:cacheprovider`: 35 passed (my run). Draft 6's count is right.

3. **Rule change (i), "disagree" needs a contrast above 0.05: acceptable once its ceiling is written.**
   - It is made before the data it uses. Batch 2 is sealed and unfinished. r has not been computed on batch 1 (BELIEF, the delegate's report).
   - It adds a threshold and widens none.
   - No combination is left undecided. When both labels are defined, both medians exist and the contrast is a number (FILE(analysis/k3w.py:388), FILE(analysis/k3w.py:389)). This rests on `min_runs` = `min_group_runs` = 3 (FILE(analysis/k3w.py:85), FILE(analysis/k3w.py:86)). Labels that differ with a contrast of 0.05 or less can only be "inside" against "outside" on one side.
   - It is not neutral given what is known, and the text does not say so. Draft 6 predicts batch 1's λ = 2.0 median at 1.02 to 1.04 (draft 6:52). So a batch-2 median between 1.05 and about 1.07 to 1.09 (DERIVED: 1.02 + 0.05, 1.04 + 0.05) now reads "at the tolerance, neither governs". Draft 5 read it "batch 2 governs, K3 mixed".
   - "At the tolerance" has no stated ceiling. The text does not say whether "within 0.05" or "r times" may still be written for λ = 2.0, what K3's status then says, or whether the line "Batch 2's J1 inside" (draft 6:70) still applies.
   - The contrast is still called "reported, never judged" (draft 6:72, 75), yet its size now decides whether batch 2 governs.

4. **Rule change (ii), no selection after a raise: acceptable; three openings remain.**
   - It is made before REG-19's outcomes are public and can favour no outcome: it can only remove batch 2.
   - REG-19's own process makes both cases unlikely. Its step never skips a seed (FILE(analysis/gate.py:2031)). Its queue stops on two valid runs of one config (FILE(docs/drafts/reg19_resume_decision_draft5.md:78), in force by FILE(docs/decisions.md:4287)). The batch-2 pattern does not match REG-20's drift rerun of seed 15 (FILE(analysis/k3w.py:65) against FILE(analysis/withheld.py:29)).
   - Opening a: the fix clause (draft 6:100) still allows a change inside `batch2_runs` after rule F and a proxy pass.
   - Opening b: a validity flag changed after REG-19's result and before the command runs prevents the raise, so the rule never applies.
   - Opening c: "not computed" is missing from the sentence that keeps batch 1 from becoming the paper's statement (draft 6:71). A raise for fewer than three seeds, and a batch 1 that cannot be recomputed for the contrast (draft 6:80), have no stated outcome.
   - The prediction (draft 6:58) gives no probability that batch 2 is not computed.

5. **The other changes to the decision table lower or keep each ceiling, with one exception.**
   - Lower: the pooled sentence only when every judged group has the pooled label and side (draft 6:65); "at least that spread", between 2.0 and 2.4 only (67); "outside high" for the load or batch it was read on (68); "the line was not empty" with four alternatives (69); the intent line (64); the contrast's reading with selection added and a small contrast as no evidence (72); the 0.95 table without wording (79).
   - New ceiling where none stood: batch 2's J1 inside (70), in the words round 3 gave.
   - Exception: r over the first 900 s "tells a window effect from a day effect" (72). The batches still differ in seeds, days and filters, and the readout has no tolerance. As written it could be used to read J2 as a statement about load after a contrast above 0.05.

6. **Round-3 conditions 1 to 7 against draft 6.**
   1. Open. Rule F returned NOT READY on draft 5, so the round-3 approval never took effect. Draft 6 cites the reviews by path (draft 6:3) and does not hold them. The list of changes made because of the draft-3 review, present in draft 4 (FILE(docs/drafts/reg21_draft4.md:67)), is gone.
   2. Met. The test is at FILE(tests/test_k3w.py:438) and passes. It builds the schedules from the real config family (FILE(tests/test_k3w.py:22)).
   3. Met, with two errors (reason 9, first two items).
   4. Met. One tag has drifted (reason 9, third item).
   5. Met, all five items.
   6. Met in text (draft 6:81) and code. That rule F has seen the diff is open with condition 1.
   7. Partly. The draft-3 review's synthetic numbers are still cited by bare file name or without a tag (draft 6:32, 79, 85). The committed test shows only r < 0.9 for a lull (FILE(tests/test_k3w.py:201)).

7. **Round-3 conditions 8 to 12 are stated, two of them only in part.**
   - 8, due before batch 1: the definitions and the ledger row (draft 6:107), the clean tree and the tests (99). The status line, the [DECISION]'s bullet on the departure, the commit hash and `check_docs` appear only in the summary (135).
   - 9, due in the batch-1 [RESULT]: stated at draft 6:4, 25, 26, 44, 63 and 99. Not stated as a duty of the [RESULT]: that five of the plan's six readouts carry no tolerance by the delegate's decision.
   - 10, due in the batch-2 [RESULT]: stated (54, 98). Not stated: that REG-19's entry gives the time its table was first computed.
   - 11 and 12: stated (100, 97).

8. **The reported-only code is outside the judged functions, and registering it before batch 1 is enough.**
   - `reg21_table` and what it calls do not call the new functions. The command adds their output after the judged table exists (FILE(analysis/k3w.py:465)).
   - They can stop the table from printing and cannot change a judged value. An exception prints no r, and the fix clause covers it.
   - The clean-tree refusal only adds a stop.
   - Each readout is named in the text with no tolerance and no wording. One gap: `r_first` is computed for batch 1 as well (FILE(analysis/k3w.py:423)) and differs from r for REG-15; the text names it for batch 2 only.

9. **Rule B: checked and found.**
   - "At least one clear pass" (draft 6:54) is wrong. The stop counts `pass_clear` or `pass_warm_edge` (FILE(analysis/gate.py:1589), FILE(analysis/gate.py:1687), FILE(analysis/gate.py:1710)). The consequence drawn holds for either.
   - "Counter hit share of 0.000 to 0.003" (draft 6:53) is not what the cited results say. They read 0.000 in every cold span (FILE(docs/decisions.md:2480), FILE(docs/decisions.md:2840), FILE(docs/decisions.md:3546)). The only "0.000–0.003" there is the control's waiting share (FILE(docs/decisions.md:2836)).
   - FILE(docs/status.md:17) (draft 6:9) was right at `d0ba233`; the sentence is at line 21 now.
   - Right: all nine line numbers into `k3w.py` and `withheld.py`; FILE(tests/test_k3w.py:156), 163 and 169; the plan and claims lines; FILE(docs/decisions.md:3785); the queue output line; FILE(harness/workload.py:55).
   - Right against the published results: 1.753, 1.769, 1.748, 1.720, 1.761 (DERIVED from the span rates at FILE(docs/decisions.md:3546) and FILE(docs/decisions.md:3742)); 121 and 101; 1.79 to 1.83; 1.72 to 1.79; 0.141 to 0.146; 30 running and 54 waiting.
   - Right: P(J1 undefined) 0.24, 0.44, 0.73 (DERIVED: binomial with 0.65).
   - Right: the gauge. The pinned source sets it to waiting plus deferred (SOURCE(vLLM 0.32.0 vllm/v1/metrics/loggers.py:PrometheusStatLogger.record), SOURCE(vLLM 0.32.0 vllm/v1/core/sched/scheduler.py:Scheduler.make_stats)).
   - Minor: P(J2 undefined) ≈ 0.02 does not follow from 0.92 per run, which gives about 0.005 (DERIVED: P(at most 2 of 5) + P(at most 2 of 6)).

**Conditions**

BEFORE the entry is appended:

1. The adversarial review of draft 6 has returned and is not NOT READY.
   - If it is NOT READY, nothing is appended. A new draft goes to rule F again. It needs a proxy pass only if a change is on the "needed" list below.
   - The entry holds, verbatim and with every quoted line prefixed: the rule F reviews of drafts 3, 4, 5 and 6, each followed by what was changed because of it. The draft-3 list is restored from FILE(docs/drafts/reg21_draft4.md:67).
   - The owner-proxy verdicts of rounds 3 and 4 are verbatim in the entry or in the [DECISION] (delegate).
2. "The two batches" (draft 6:71) gains the ceiling of the "at the tolerance" case:
   - both medians, both labels with their sides, both n, both windows and the contrast are given together;
   - no sentence says "within 0.05" or "r times" for λ = 2.0 on one batch alone, and the line "Batch 2's J1 inside" does not apply;
   - K3's status then says "at the tolerance at λ = 2.0", names batch 2's label, and is not worded as inside;
   - in every case batch 2's J1 label and side are stated as computed;
   - the contrast's size is compared with 0.05 as the tolerances are: a value at 0.05 within `EPS` is not above (FILE(analysis/k3w.py:91));
   - the contrast is described as "not judged as a statement; its size against 0.05 decides whether batch 2 governs".
3. "What was known" says that rule (i) and its 0.05 were fixed with batch 1's λ = 2.0 median predicted at 1.02 to 1.04, and gives the consequence in reason 3, fourth item.
4. Rule (ii) is completed:
   - every raise of `batch2_runs` after REG-19's final result (a gap, two valid runs of a seed, fewer than three seeds), and a batch 1 that cannot be recomputed for the contrast, gives "not computed", with the reason;
   - "not computed" is treated as "undefined" in the sentence on the paper's statement;
   - the fix clause does not apply to these raises: no change of `batch2_runs`, of the pattern or of a validity flag follows one;
   - no validity flag of a run matching the batch-2 pattern changes after REG-19's final [RESULT]. Before the batch-2 command runs, the valid folders matching the pattern (names and `valid` only) are compared with the burst runs REG-19's final [RESULT] counts. If they differ, batch 2 is not computed;
   - the prediction says its batch-2 numbers are conditional on batch 2 being computed, gives a probability (BELIEF) that it is not, and says that three burst runs exist today.
5. `r_first` is named for every run of either batch. "Tells" is replaced: it carries no wording and changes neither J2's reading nor which batch governs, which rests on `fixed_load_contrast.difference` alone.
6. Rule B corrections:
   - "pass (`pass_clear` or `pass_warm_edge`)" for "clear pass";
   - the hit share corrected to 0.000, or the source of 0.003 given;
   - every FILE(path:line) resolved again at the commit that holds the entry (`docs/status.md:17` is line 21 now);
   - the draft-3 review's synthetic numbers tagged with the review's path and named as the review's own (draft 6:32, 79, 85);
   - the nesting test cited with its line;
   - "Code and tests" names `_dirty`, `REPORTED` and the changed `__main__` block as added, and `_ok_in` and `EPS` as judged;
   - the rule counts say that n is the runs that entered, judged or not.
7. The [DECISION] (delegate) lists, for each of conditions 2 to 6, the sentence of the entry that meets it. Draft 6 stays in `docs/drafts/`.

BEFORE batch 1 is computed:

8. All of the following hold:
   - the four definitions are in `docs/definitions.md`, with U naming `recomputed_prefill_tok_s` as another computation;
   - `docs/model.md` has the ledger row for REG-21;
   - `docs/status.md` names the registration's state;
   - the [DECISION] (delegate) heading carries one bracketed tag, and its body has a bullet on the departure with its deadline, REG-19's result;
   - the commit holding both entries exists and its hash is recorded;
   - `analysis/` and `tests/` have no modified or untracked file;
   - `uv run pytest` and `python3 tools/check_docs.py` pass;
   - `git diff 8164211 <that commit>` is empty for `analysis/k3w.py`, `withheld.py`, `k1.py`, `load.py`, `gate.py`, `margin.py`, `stats.py` and `derived.py`, or each hunk is shown to lie outside the judged path.

LATER, in a [RESULT]:

9. The batch-1 [RESULT]:
   - keeps the wording rules (draft 6:4, 63, 65);
   - lists each run left out with every reason and, where it exists, its r;
   - names the commit;
   - gives the rule counts k of n per load with `stats.cp_upper`;
   - repeats the seed pairing beside J2 and any pooled median;
   - says that five of the plan's six readouts are reported without a tolerance by the delegate's decision;
   - marks the two `bad_baseline` runs.

   Any edit to `docs/claims.md` or `docs/paper/` needs its own decision, rule F review and proxy pass.
10. Batch 2 is computed once, after REG-19's final result. Its [RESULT] shows:
    - **Commit order:** REG-21's entry commit is an ancestor of the commit that adds REG-19's result heading, and REG-19's entry gives the time its table was first computed, later than REG-21's commit. If not, batch 2 is labelled retrospective and does not govern.
    - **Unchanged judged path:** an empty `git diff` for the files of condition 8 between the batch-1 and batch-2 commits. If not, rule F and a proxy pass come first.
    - **The run comparison** of condition 4.
    - **The same batch 1:** `fixed_load_contrast.batch1_median` equals the λ = 2.0 group median of the batch-1 [RESULT]. If not, it is reported as a deviation and batch 2 does not govern.
    - **Rule (i) applied** to the printed difference, with the case named.
11. If a command raises, a fix outside the judged path is a [CORR] before the table is read. A fix on the judged path needs rule F and a proxy pass before the rerun. The raises of condition 4 are excepted.
12. REG-20's gate is computed before batch 2, or both results state the order.

**Which later changes need another proxy pass.**
- **Needed** for any change to:
  - U, U_off, r or W;
  - the entry rule, the two preconditions and their numbers, both tolerances, the 0.05 on the contrast, the minimum counts;
  - the run lists, patterns and reference set;
  - the pooling rule, the rule on which batch governs, the stopping rule, the heading test;
  - any function on the judged path;
  - the `__main__` block, beyond adding a reported key or a refusal;
  - wording that raises a ceiling of the decision table.
- **The judged path** is `REG21`, `EPS`, `window`, `_ok_in`, `work_rate`, `busy_share`, `reference` up to its mean, `_why`, `row`'s judged values, `_median`, `_level`, `judge`, `select`, `batch1_runs`, `batch2_runs`, `_judged`, `reg21_table`, and what they call in `k1`, `load`, `gate`, `margin`, `stats` and `withheld`.
- **Not needed** for: conditions 1 to 8 as written; further tags; a lower ceiling; a reported-only readout registered before batch 1 with code outside the judged path.
- **Corrections the parallel adversarial review may still require** follow the same split. Wording, tags, a lower ceiling and reported-only code need no proxy pass. A change to a judged function, a tolerance, a precondition, the run lists, the pooling or governing rule, or the stopping rule needs one. In doubt, it needs one.
- **After batch 1 is computed,** a change to the governing, pooling or stopping rule needs a proxy pass, and the batch-2 [RESULT] says it was made knowing batch 1.

**Notes for the owner**

- The departure from your two choices for step B is still the first thing to look at. To have the mix or the session rates judged on REG-19's runs, register that before REG-19's result.
- Batch 2 is the only item on unread data, and it may never exist. Three burst runs exist today. With three, the delegate's own estimate is P(undefined) ≈ 0.73. Seeds 18 and 19 wait on the VM. Without a final REG-19 result heading, batch 2 cannot run.
- Rule (i) softens the likeliest disagreement (reason 3, fourth item). You can overrule it before batch 2, for example with "batch 2 always governs".
- Rule (ii) trades batch 2 for no choice after the fact. A tie-break registered now is the alternative, and only until REG-19's result.
- Batch 1 will print U and reuse per 300 s span, KV, running batch and preemptions for the 13 runs that draft REG-22 means to judge. REG-22 must list that as known, or be registered first.
- Not in "What was known": the interim look of 2026-11-12 at seed 17's control (FILE(docs/decisions.md:4276)), which is not a batch-2 run; and that `continue` True also means no `control_cold_no_surge` and fewer than two bad controls among seeds 15 to 17.
- Preferences, not conditions: list the 13 run ids in the entry; save the command's JSON with each [RESULT]; date the heading on the day it is appended.

**Not checked by me**

- Nothing under `runs/` or the backups was opened. So I did not check that the run ids exist and are valid, the rates 1.656 and 1.688, or that r, U, reuse and the busy share were never computed.
- The rule F reviews were not read, as instructed. So I did not check "NOT READY, 6 items", the mapping of draft 6's change list to its items, or the synthetic numbers quoted from the draft-3 review. A grep showed me two lines of an earlier review's copy (`docs/drafts/review_bundles/reg21_r2/round1_rule_f.md`) about 1.656 and 1.688; no reason rests on them.
- The gauge was read in the tarball copy at `/Users/chalshik/.claude/jobs/c075c1a8/tmp/vllm_src/` (sha256 equal to FILE(docs/open-questions.md:29)), not in the VM's wheel.
- The preprints, model F's equations, PROTOCOL §4 on dev mode, the full `uv run pytest` and `tools/check_docs.py` (they list `runs/`), and the helpers below `k3w.py` line by line.
