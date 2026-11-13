# Rule F, round 6, on REG-21 draft 9 (agent a1bce48befd9127b9), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input), no word changed. Bundle: `docs/drafts/review_bundles/reg21_r6/`; code at `8164211`.

---

REG-21 draft 9, round-6 adversarial review (rule F): NOT READY. Five of round 5's six required changes are fixed as worded. Item 4 is only partly fixed: the owner's overrule window can still fall after REG-19's table is public. The changed sentences leave two more rules open, and one changed sentence claims something the code does not do. All three are text-only fixes. No ceiling is raised, and no code has to change.

How I worked: I used synthetic run folders and config files only. Nothing under `runs/` (or any worktree's `runs/`) was opened or listed. Under `docs/` I read only the bundle; for two cited review files I only tested that they exist. `load.find_runs` and `load.load_run` were wrapped to refuse any path outside the scratch folder before `analysis.k3w` was imported, and `load.RUNS` and `withheld.DECISIONS` pointed at scratch files. Nothing in the repo was changed. Line numbers below are those of `registration_draft9.md`.

Code and bundle:
- `git diff 8164211 HEAD` is empty for the nine files named, and also for `analysis/k3.py` and `analysis/modelf_sim.py`. HEAD moved to `59e1d49` during the review; the diff was still empty at the end.
- `tests/test_k3w.py`: 35 pass.
- The bundle's diff equals a fresh `diff` of the two drafts.
- The working tree now holds a modified `analysis/c2.py` and `tests/test_c2.py` (another session's work), so `_dirty` would refuse the REG-21 command today. This is not a fault of the registration.

Script and output:
- /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r6_scratch/r6_check.py
- /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r6_scratch/r6_check.out
- Round 5's B4 (no REG-19 seed is exposed: peaks 2.833 to 3.092 against `surge_tip` 3.2) is reused, not rerun.

**1. Round 5's six required changes**

1. **One rule for a seed with a valid burst run that REG-19 does not count: FIXED** (lines 27 and 106).
   - Both places now give "not computed".
   - Line 106 says the comparison is made by hand, by the person running batch 2, before the command, on folder names and `valid` only. Both lists go into the batch-2 [RESULT].
   - The code makes no such comparison (`k3w.py:341–357`). R2: with seeds 15–17 counted and a valid seed-18 burst run, `batch2_runs` returns [15, 16, 17, 18].
   - One small inexactness, under Optional: the function "returns it all the same" only while the seeds still form a prefix; otherwise it raises on the gap, which gives the same outcome.

2. **Every raise of the batch-2 selection gives "not computed": FIXED for `batch2_runs`** (line 105).
   - "Whatever its cause" covers every raise I traced: `lifted` → `find_runs` → `keep`/`sealed_by`/`unsealed_ids` → `load_run`/`guard` → `yaml.safe_load` → `_jsonl` (JSONDecodeError) → `env.json` (FileNotFoundError) → `checks["valid"]` → `int(cfg["seed"])` → the gap, duplicate and too-few checks.
   - The parenthetical about raising "before REG-19's final result" agrees with "computed once". With line 108's heading rule kept, the only raise possible then is the seal's `RuntimeError` at `k3w.py:345–346`, before any folder is read.
   - Two gaps remain beside this item; they are required change 2 below.

3. **The judged path: FIXED** (line 102). The call trace on synthetic folders (P) found:
   - Nothing runs on the judged path in either batch that the list does not name.
   - Every listed name runs in batch 2. In batch 1, `batch2_runs`, `withheld.lifted` and `withheld.unsealed_ids` do not run: no batch-1 name matches a seal pattern.
   - `_gauges`, `_metric_mean` and `k3.counter_rate` run only inside `reference`'s `try` (`k3w.py:149–152`), so "`reference` without its gauges" is exact.

4. **"The owner can overrule this before batch 1 is computed": PARTLY fixed** (line 55).
   - It is fixed as round 5 worded it. But round 5's own reason named two facts, batch 1's median and REG-19's table, and the new wording closes the window only on the first.
   - REG-19's table gives each burst run's completion rate over [end + 600, end + 3000) (`gate.py:1834–1855`, `reg19_table` rows' `c`). That is batch 2's W, [1680, 4080) s (line 19).
   - By line 51 (DERIVED), r ≈ (that rate ÷ 1.681) × 0.98 to 1.00. So REG-19's table fixes batch 2's r to about ±1 %.
   - If REG-19's final result comes after this entry is committed but before batch 1 is computed, an overrule can be chosen knowing batch 2's side of the contrast (rule A5, research rule 7). This order is reachable: batch 1 waits on the definitions step (line 114), and the GPU "can return at any time".
   - This is required change 1.

5. **REG-11's r from 1.00 to 1.06: FIXED** (line 58). 1.02 × 0.98 = 0.9996 and 1.06 × 1.00 = 1.06. This matches line 51.

6. **`_dirty` runs before the table: FIXED** (line 117). `_dirty` is at `k3w.py:462–463`, `reg21_table` at 465, `vj_counts` at 466 and `reported_spans` at 467.

**2. The other changed sentences**

The new bullet "Two things the person running batch 2 does by hand first" (line 106):

- **(a) can be kept, and does not conflict with any other sentence of draft 9.**
  - It agrees with line 105's "no folder is added, moved or changed". It is neither of research rule 4's cases: the folder is kept, just on the VM.
- **(a)'s first clause can be checked from the record through (b), provided (b) compares by name.**
  - A flag change that matters changes the list of valid folders, and (b) records that list and compares it.
  - A change from "no `checks.json`" to `valid: false` is invisible to (b), and harmless: `find_runs` keeps neither.
- **(a)'s second clause cannot be checked from the record.**
  - (b) lists valid folders only, so an invalid folder copied into `runs/` is recorded nowhere.
  - If that folder is readable, it has no effect. If it is unreadable, it shows up only as the reason for a raise; a JSONDecodeError message does not name the folder.
  - The clause also has no start date: a folder copied before this entry would already break it. I could not see whether one exists.
- **(a) has no stated consequence of its own, but every violation of it has a determined outcome**: either (b) finds a difference, or line 105's raise applies, or the violation has no effect.
- **(b) is well defined after a futility stop after seed 18.**
  - `reg19_step`'s `done` and the table's `seeds_run` are [15, 16, 17, 18]. `excluded` is empty because no seed is exposed (round 5's B4), so `n` = 4.
  - The valid folders are the same four (R1). Batch 2 is computed on four runs, and `batch2_runs` accepts them as a prefix.
  - Seed 19 cannot have a folder: the queue's only look between seeds (`gate.py:2022–2041`) stops it from starting.

Raises inside `reg21_table(2)` after `batch2_runs` has returned (Q):
- **Q1:** an ok request without a first-token time raises ValueError in `_judged → row → work_rate`. That is the registered raise (line 17).
- **Q2:** a new valid folder matching `*_sweep_l1pl350_pc_off_r*` at a rate of 2.0 or more raises in `reference`.
- **Q3:** an invalid, cut folder matching that pattern raises JSONDecodeError in `reference → find_runs → load_run → _jsonl`.
- None of these is a raise of `batch2_runs`. Line 105 does not name them, and line 104's fix clause covers them only by elimination.
- For `reference`, line 105's "a batch 1 that cannot be recomputed for the contrast" can also be read to cover it. That reading gives "not computed, fix clause does not apply"; line 104 gives "reviewed fix, rerun". These are opposite answers.
- Q2 and Q3 can happen: running the used config `configs/sweep_l1pl350_pc_off.yaml` again makes matching folders. (The `_a` and `_b` configs do not match the pattern.)
- Required change 2.

A result heading the seal does not accept (line 105):
- If the command is run first, it raises, and the answer is "not computed".
- If the typo is noticed first (the person reads that entry for (b)), nothing in draft 9 forbids appending a correctly typed heading. Line 108 forbids such lines only before the final result, and line 105's "no change … of a heading" applies only after a raise. The command then lifts the seal.
- So the same typo gives either outcome, chosen by the operator after REG-19's outcomes are public. Required change 2.

Line 154 (and line 163): "nothing is changed in `analysis/k3w.py` between the batches, so that both batches' readouts are computed alike".
- This is not so. The readouts call `analysis/k3.py` (`completed`, `counter_rate`, `d_obs`, `hl_rule`, `kbar_obs`, `lam_w`, `long_run`, `x_obs`, …), `analysis/modelf_sim.py` (`simulate`, `as_run`, `schedule`) and `gate.shock_size` (S).
- `k3.py` and `modelf_sim.py` are not in line 102's diff list. `gate.shock_size` lies outside the judged path, so line 102 allows it to change.
- Required change 3.

Checked and could not break:
- Line 3: the new review file exists, and the header is accurate.
- Line 58's numbers.
- Line 71, "whose r had not been computed": consistent with line 49 (BELIEF).
- Line 84's new sentence agrees with line 76. The governing comparison rests on the printed `fixed_load_contrast.difference` in both.
- Line 117, "the constants named there": in the context of k3w.py this means `REG21` and `EPS`.
- The new heading for the owner-proxy's verdict on draft 6 (line 144) is in its own section now.
- No number disagrees with its neighbours, and no ceiling is raised.

**3. Verdict: NOT READY.** Three changes are required, all in the text. With them made as worded below, I would call it READY.

1. **Line 55, the overrule window** (round-5 item 4, PARTLY fixed). Replace the last sentence with:
   "The owner can overrule this only while batch 1 has not been computed and REG-19's table has not been computed or read by anyone, for example with "batch 2 always governs". After batch 1, its side of the contrast is known exactly; REG-19's table gives each batch-2 run's completion rate over the same W, which fixes r's first factor (line 51)."

2. **Line 105, one answer for every failure of the batch-2 command after REG-19's final result.** Replace its first sentence with:
   "After REG-19's final result, every raise of `uv run python -m analysis.k3w reg21 2` before the judged table exists, wherever it comes from (`batch2_runs` with all it calls, `reference`, `select`, `row`, `judge`, or batch 1's recomputation for the contrast), gives "batch 2: not computed", with the reason: for example a gap in the seeds, two valid runs of a seed, fewer than three seeds, a folder matching either pattern that cannot be loaded (`find_runs` loads every matching folder before it looks at validity), an ok request without a first-token time, a sixth valid reference run, or a result heading the seal does not accept."
   Delete "So does a batch 1 that cannot be recomputed for the contrast." Then add:
   "If the heading of REG-19's final [RESULT] is one that `withheld.lifted('[RESULT] REG-19')` does not accept, batch 2 is not computed whether or not the command was run; no heading is added to make the seal lift."
   An alternative I would also accept: one sentence that puts every raise outside `batch2_runs` under line 104's fix clause, provided it says so in these terms and adds that such a fix is made with REG-19's table public. A mistyped heading would then need one answer that does not depend on whether the command was run first.

3. **Line 154, the readouts claim.** Replace "so that both batches' readouts are computed alike" with:
   "That keeps the code of `reported_spans`, `vj_counts` and the readouts in that file the same for both batches. The readouts also call `analysis/k3.py`, `analysis/modelf_sim.py` and `gate.shock_size`, which the stopping rule's diff check does not hold fixed; the batch-2 [RESULT] shows the `git diff` of `analysis/k3.py` and `analysis/modelf_sim.py` between the two commits, and marks any readout computed with changed code."
   In line 163, write "no change to `analysis/k3w.py` between the batches" in place of "no later code change to the readouts between the batches".

Optional:
- Line 157 points to "Batch 2 not computed" for the hand comparison; it is now in line 106's bullet.
- Line 106 (b): list every folder matching the pattern with its `valid` (true, false, or no `checks.json`). That records (a)'s second clause too. Also say:
  - which `runs/` is meant: the one `load.RUNS` names in the checkout the command runs from (REG-19 is computed from the worktree at `a7bb77a`);
  - that the lists are compared by name;
  - that every valid REG-19 burst folder is copied in before (b);
  - that (b) is made once and a difference is final.
- Line 106 (a): say it applies from this entry on, and that the [RESULT] lists any such folder already present.
- Line 84: the check of `batch1_median` has no stated consequence. As written, line 76 makes the printed difference govern anyway; say so, or say what a mismatch does.
- Line 27: write "would return it (or raise on a gap)".
- Line 105's parenthetical: "the seal's raise" is exact.
- Line 102 allows hunks in `k3w.py` outside the judged path, while line 154 promises none; align them.
- Line 59's 0.25 for "never computed" counts only a missing final result. (b) and line 105 add routes, for example a valid seed-18 burst run whose control is lost.
- Line 117 calls `_dirty` "reported only"; it is a gate.

**4. What I could not check**

- **Any real run:**
  - whether any folder matching the batch-2 or the reference pattern is unreadable or invalid today;
  - whether `runs/` already holds an invalid REG-19 burst folder;
  - whether the `a7bb77a` worktree's `runs/` is the main repo's.
- **Anything in `docs/` outside the bundle:**
  - REG-19's own entries and resume rules: whether REG-19 requires invalid folders to be copied before its [RESULT];
  - `manifests/` and the copy practice;
  - the other cited reviews' contents.
- **Not run:** the full `uv run pytest`, `tests/test_withheld.py`, and `python -m analysis.k3w reg21`.
- **REG-19's actual run order within a seed (control or burst first)**, which decides how often required change 2's cases and (b)'s "differ" case occur.
