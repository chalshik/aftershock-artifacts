**Decision: APPROVE**, on the conditions below, for appending REG-21 (draft 5, code at `69ffedd`) with its delegate decision and computing batch 1 once. The approval lapses if the adversarial review of draft 5 requires a change to the judged path.

**Reasons**

1. **Scope: inside the delegation.**
   - An analysis-only registration at 0 GPU h is delegated (FILE(docs/decisions.md:4233)). It edits no run, used config or old entry.
   - REG-19's runs are read only after REG-19's result heading exists. `batch2_runs` raises before that, whatever `AFTERSHOCK_UNSEAL` holds (FILE(analysis/k3w.py:342), FILE(analysis/withheld.py:46)).
   - No clause is outside it, because the entry computes and reports only and every claim edit needs its own decision (FILE(docs/drafts/review_bundles/reg21_r3/registration_draft5.md:61)).
   - One clause comes close: batch 2 computes `k1.cold_backlogged` on REG-19's burst runs, the readout REG-20's gate is to compute once (condition 12).

2. **Rule A5: honest, and sufficient with two additions.**
   - No tolerance has moved. 0.05, 0.05 and reuse ≤ 0.05 are in the first committed code (`72fafb5`). Busy ≥ 0.99 and groups of three came in `3f5c84a`, and gauge coverage and the narrower pooled median in `69ffedd`. Each removes runs from the judged set and none widens a tolerance (`git show`, read today).
   - "What was known" checks out against the published tables. The λ = 2.0 rates are the span means of REG-17 and REG-18, and they give 1.02 to 1.05 over 1.681 with median 1.04 (DERIVED: 1.720, 1.748, 1.753, 1.761, 1.769 ÷ 1.681).
   - Calling batch 1 a retrospective consistency reading is the standard the plan sets for step B (FILE(docs/experiment-plan.md:413)).
   - Batch 2 is protected against accident, not against intent. The heading test and the guard work as written (31 synthetic tests pass; I ran them). "Computed once" and the commit order rest on the log, and nothing in the text keeps the judged code fixed between the batches (condition 10).
   - "The only item on unread data is batch 2's J1" omits one fact. REG-19's `continue` flag after seed 17 was True with two seeds left (FILE(docs/probe/20261111_reg19/ops/queue_run4_output.txt:5)), which needs at least one pass among seeds 15 to 17 (DERIVED from FILE(analysis/gate.py:1710)). So one batch-2 run is known to have ended stuck, with a line that never emptied and a completion rate over W below 2.0. That only bounds its r below about 1.19 (DERIVED: 2.0 ÷ 1.681), so the tolerance was not fitted to it.

3. **The departure: adequately argued, stated plainly, and it may go ahead.**
   - The argument rests on evidence newer than the owner's last choice, as rule A4 asks:
     - The review of draft 1 showed that the mix tilts alike for any overloaded closed-loop queue (FILE(docs/drafts/scratchpad-2026-11-12/round1.md:18)).
     - Committed tests show that a 64-slot running batch moves the mix while r stays at 1.00 (FILE(tests/test_k3w.py:163), FILE(tests/test_k3w.py:169)).
     - The judged readout is in the owner's own list, described there as not depending on the mix (FILE(docs/experiment-plan.md:409)).
     - The owner accepted the same argument for E1 (FILE(docs/decisions.md:4264)).
   - The text of the review of draft 2 is not on file. I found only its scripts (`docs/drafts/scratchpad-2026-11-12/review2/`) and a one-line summary (FILE(docs/status.md:17)), yet the registration cites it as the argument.
   - The cost is acceptable without the owner, who asked that nothing wait for them (FILE(docs/decisions.md:4232)) and can overrule.
     - Batch 1 reads no REG-19 run. The owner's option to have the mix or the session rates judged there ends with REG-19's own result, which prints each seed's completion rate over W and first-turn share (FILE(docs/decisions.md:3799)).
     - On the 13 runs already seen, what is lost is a retrospective label on readouts whose main input, the request rate, is already published.
   - Not stated: K3 lists four quantities and asks for a tolerance per quantity (FILE(docs/claims.md:63), FILE(docs/claims.md:65)). REG-21 judges none of them, only the premise they share.

4. **Template and rules: gaps, by rule.**
   - **Rules E and F:** the entry holds no review verbatim (line 3 cites paths), and the changes made after the draft-3 review are not listed (FILE(docs/process.md:78)).
   - **Rule H, shared seeds:** line 25 says the schedules at two loads "are not the same draws". That is false.
     - For seeds 2 to 6, every session start of the λ = 2.0 schedule is also a session start of the λ = 2.4 schedule of the same seed: 627 of 627, 603 of 603, 698 of 698, 670 of 670, 648 of 648. Seed 2's schedule at 2.2 lies between them.
     - Cause: the count is drawn first, then that many uniform times from the same stream (FILE(harness/workload.py:55)).
     - Evidence: DERIVED from the configs with `analysis.modelf_sim.schedule`, no run read. Script: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r3_proxy/schedule_nesting.py
     - So J2's two groups are paired by seed, and the pooled 11 runs hold six distinct seeds (FILE(docs/process.md:92)).
   - **Rule H, means:** a mean over a window is reported with its minimum span or distribution (FILE(docs/process.md:94)). Line 16 declines this for U.
   - **Rule A1:** there is no line for batch 2's J1 inside, the likeliest outcome of the one judged item on unread data.
   - **Rule B:** not tagged, or tagged in no listed form:
     - `ls runs` (line 24);
     - reviews cited by bare file name (lines 31, 82);
     - the hit-share sentence, and "94 to 154", which is the range over all spans; the two quiet spans read 121 and 101 (line 52);
     - two statements that cannot be checked, on what was never computed and never read (lines 48, 103).
   - **Rule J:** the four definitions are drafted (FILE(docs/drafts/definitions_reg21_reg22.md:7)) but not in `docs/definitions.md`. The counter-based `recomputed_prefill_tok_s` (FILE(analysis/load.py:75)) is a further computation that U's definition does not name.
   - **Rule I and the ledger:** model F has no ledger row (FILE(docs/model.md:67)). The Clopper–Pearson count of line 43 is not produced by the registered command.
   - **Present and adequate:** numeric predictions, six alternatives with their readouts, the pooling assumption, the stopping rule, named functions, the cost.

5. **Decision table: acceptable as a ceiling.**
   - No line edits a claim by itself (line 61).
   - "Batch 2 governs what is said about λ = 2.0" is acceptable. It is fixed in advance, favours the runs not read when the tolerance was fixed, and applies only if the commit order holds. Both medians, n and the windows (2400 s against 900 s) are still printed.
   - The fixed-load contrast only weakens what may be said, so its reading is acceptable.
   - Four lines say more than the data can carry (condition 5):
     - line 70 is silent on a small contrast;
     - line 66 takes the spread as the error at another load;
     - line 68 calls a non-empty line "not idle time";
     - line 63 states two later choices as settled.

6. **The ten conditions of the earlier pass.**
   1. Partly. The re-review is under way. The reviews are still cited, not placed in the entry.
   2. Met.
   3. Met in the text (lines 53, 91). It can be shown true only at batch 2.
   4. Met in the text (lines 4, 69). It falls due in the [RESULT].
   5. Met (lines 48 to 52), apart from the loose range and the untagged sentence above.
   6. Met (lines 8 to 13).
   7. Met (lines 62, 65).
   8. Met (line 61).
   9. Partly. Present: model F's number, the run lists by file and line, the commit, counts with their bound, U named as a window mean. Missing or wrong: the shared-seed sentence, some tags, the definitions in force.
   10. Met in the text (lines 90 to 93). The three registered files are unchanged since `69ffedd`. Untracked `analysis/k5.py` and `tests/test_k5.py` appeared while I worked, so `analysis/` and `tests/` are not clean now.

7. **What the text does not tell the owner:** the items under reasons 2 to 4 and the notes below.

**Conditions**

Before the entry is appended:

1. The rule F review of draft 5 does not return NOT READY and requires no change to the judged path. The entry holds this verdict and the rule F reviews of drafts 3, 4 and 5, verbatim, each followed by what was changed because of it. Every quoted line is prefixed so that none begins a heading.
2. Line 25 is replaced by the nesting fact, shown by a committed test or function (my script is not provenance), and by its consequence: groups paired by seed, six distinct seeds in the pooled 11.
3. "What was known" adds or corrects:
   - REG-19's three `continue` flags and what they imply;
   - that busy ≥ 0.99 was fixed with REG-19's schedule published, seed 18's first span of W planned at 1.32 req/s (FILE(docs/decisions.md:3785));
   - the quiet spans' values in place of "94 to 154";
   - a tag on the hit-share sentence;
   - BELIEF on the two statements that cannot be checked.
4. "How this differs" adds:
   - the evidence by file (the draft-1 review and the two tests named in reason 3);
   - that the draft-2 review's text is not on file, or its path;
   - that none of K3's four listed quantities is judged.
5. The decision table changes as follows:
   - **New line, batch 2's J1 inside:** at most "at λ = 2.0, in n runs not read when the tolerance was fixed, the cold, backlogged engine's uncached-token rate was within 0.05 of the cache-off sweep's", with median, range and window, and nothing about other loads or K3's listed quantities.
   - **Line 70:** a contrast of 0.05 or less is not evidence against a day or window effect, and J2 stays "load or day" under either label.
   - **Line 66:** "at least the spread", between 2.0 and 2.4 only.
   - **Line 68:** "the line was not empty", with redone prefill as one alternative among those listed.
   - **Line 63:** marked as intent that this entry does not decide.
6. Rule H: the entry registers, as reported and never judged, U and reuse over consecutive 300 s spans of W, and U over 300 s spans of each reference window, with each run's minimum and maximum.
   - They are computed in the same single computation by committed code outside the judged path.
   - The entry names the new commit, and the rule F pass has seen that diff.
7. The remaining tags of reason 4 are added.

Before batch 1 is computed:

8. All of the following hold:
   - the four definitions are in `docs/definitions.md`, with U naming its computations;
   - `docs/model.md` has a ledger row for REG-21;
   - `docs/status.md` names draft 5's state;
   - the delegate [DECISION] heading carries one bracketed tag, and its body has a bullet on the departure with its deadline, REG-19's result;
   - the commit holding both entries exists and its hash is recorded;
   - `analysis/` and `tests/` have no modified or untracked file;
   - `uv run pytest` and `python3 tools/check_docs.py` pass.

Later:

9. The batch-1 [RESULT]:
   - keeps the wording rules of lines 4, 62 and 69;
   - lists each run left out with every reason and its r;
   - names the commit;
   - gives counts as k of n per load with `stats.cp_upper`, the computation shown;
   - repeats the seed pairing beside J2 and the pooled median;
   - says that five of the plan's six readouts are reported without a tolerance by the delegate's decision;
   - marks the two runs whose verdict was `bad_baseline` (REG-12 seed 5, REG-18 seed 5).

   Any edit to `docs/claims.md` or `docs/paper/` needs its own decision, rule F review and proxy pass.
10. Batch 2 is computed once, after REG-19's final result. Its [RESULT] shows two things:
    - **Commit order:** `git merge-base --is-ancestor` holds from REG-21's entry commit to the commit that adds REG-19's result heading, and REG-19's entry gives the time its table was first computed, later than REG-21's commit. If this fails, batch 2 is labelled retrospective and does not govern.
    - **Unchanged judged path:** `git diff` between the batch-1 and batch-2 commits is empty for every function on the judged path. If it is not, rule F and a proxy pass come before batch 2.
11. If either command raises, a fix outside the judged path is a [CORR]. A fix on the judged path needs rule F and a proxy pass before the rerun.
12. REG-20's gate (`python -m analysis.k1 reg20_a_may_start`) is computed before batch 2, or both results state the order.

**Which later changes need a new proxy pass.**
- **Needed** for any change to:
  - U, U_off, r or W;
  - the entry rule, the two preconditions and their numbers, both tolerances, the minimum counts;
  - the run lists, patterns and reference set;
  - the pooling rule, the rule on which batch governs, the stopping rule, the heading test;
  - any function on the judged path;
  - wording that raises a ceiling of the decision table.
- **The judged path** is `REG21`, `window`, `work_rate`, `busy_share`, `reference` up to its mean, `_why`, `row`'s judged values, `_median`, `_level`, `judge`, `select`, `batch1_runs`, `batch2_runs`, `_judged`, `reg21_table`, and what they call in `k1`, `load`, `gate`, `margin` and `withheld`.
- **Not needed** for: conditions 1 to 8 as written, further tags, a lower ceiling, or a reported-only readout registered before batch 1 with code outside the judged path.

**Notes for the owner**

- Look first at the departure (FILE(agent/FOR_AUTHOR.md:7)). If you want the mix or the session rates judged on REG-19's runs, register that before REG-19's result.
- After REG-21, K3's own four quantities still have no judged comparison on any existing run.
- Expect little. Batch 1's labels are nearly fixed in advance. By the delegate's own estimate batch 2's J1 is undefined with probability 0.25 to 0.45. An "inside" near 1.03 still means about 3 % more token work than the reference.
- Batch 1's table will show KV, running batch, preemptions and uncached rates on the runs that draft REG-22 means to judge. REG-22 must list that under what was known, or be registered first.
- REG-21 does not read the cold stretches without a burst (REG-16, REG-12's seed-5 control), though the plan's list names REG-16. They stay unread.
- The reference is five runs of one day and one seed and is not held to the busy rule. Its λ = 2.0 run completed 1.5 % under their mean.
- Preferences, not conditions: list the 13 run ids in the entry, and save the command's JSON output with each [RESULT].

**Not checked by me**

- Nothing under `runs/` or the backups was opened. So I did not check that the run ids exist and are valid, that no run was read while drafting, or that U, r, reuse and the busy share were never computed.
- The rule F reviews of drafts 3 to 5 were not read, as instructed. A grep showed me two lines of the draft-3 review, about the reference's λ = 2.0 run; no reason above rests on them.
- The pinned vLLM source for the gauge, the preprints and model F's equations.
- The full `uv run pytest` and `tools/check_docs.py`, which list `runs/`.
- The helpers below `k3w.py` line by line (`k3`, `modelf_sim`, `gate.burst_end`, `load._level`).
- The rates 1.656 and 1.688 on line 45 are in no decisions.md entry. I found them only in a local snapshot under `docs/paper/`.
