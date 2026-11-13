REG-21 draft 8, round-5 adversarial review (rule F): NOT READY. Round 4's three required changes are made as round 4 worded them, the code is unchanged and no ceiling is raised. Six text changes remain: three rules that draft 8's new sentences leave open or set against each other, and three small corrections. No code has to change.

How I worked: synthetic inputs and config files only. No folder under `runs/` was opened or listed. `load.find_runs` and `load.load_run` were replaced before `analysis.k3w` was imported; in script a they were wrapped to refuse any path outside the scratch folder, with `load.RUNS` and `withheld.DECISIONS` pointed at scratch files. Under `docs/` I read only the bundle; for the seven cited review files I tested existence only. The bundle's diff equals `diff` of the two drafts. Nothing in the repo was changed.

Code: `git diff 8164211 HEAD` is empty for the eight files named and for `analysis/derived.py`. HEAD moved during the review (`b1a6eb0`, `727d1f2`, `aa77e9c`); the diff was empty at the last. `tests/test_k3w.py`: 35 pass. Line numbers of the registration are those of `registration_draft8.md`.

Scripts:
- /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r5_scratch/a_path.py
- /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r5_scratch/b_rules.py
- /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r5_scratch/c_sentences.py
- Round 4's scripts i, j and m were rerun unchanged and gave round 4's numbers.

**1. Round 4's three required changes**

The four sentences: all FIXED.
- U's spans, line 17. `span_values` gives U per span with the lowest and highest (`k3w.py:403–411`).
- A run that did not enter, line 33. `reported_spans` loops over every run of the batch and never calls `select` (`k3w.py:419–425`). On a 900 s W, `r_first` equals r to the last digit (script c, C1).
- The reference's 60 s span, line 85. The window is 240 to 900 s; the spans are 300, 300 and 60 s, and the 60 s span enters the lowest and highest (scripts b, B5 and c, C2).
- "A pass (`pass_clear` or `pass_warm_edge`)", line 54. The two added conditions are right (`gate.py:1690–1693`, `1707–1710`).

The three numbers: all FIXED.
- Seed 1's first factor, line 51: 1.72 ÷ 1.681 = 1.023 and 1.79 ÷ 1.681 = 1.065.
- The pooled level as a range naming REG-11's run, line 58: 0.20 to 0.845 over seed 1's rate of 1.72 to 1.79. The same sentence has one new slip (required change 5).
- "The likeliest outcome" with five runs only, line 71: inside 0.50 against undefined 0.24 with five runs, 0.37 against 0.44 with four, 0.18 against 0.73 with three. With line 59's 0.25 for "never computed", inside is still the likeliest with five (0.37 against 0.25 and 0.18).

The judged path: FIXED as round 4 worded it; two gaps are new.
- The definition is in lines 102, 104 and 116.
- Every name round 4 gave is listed, and all 30 listed functions run before the first readout (script a, a call trace of `reg21_table(1)` and `(2)` on synthetic folders).
- The list is still three functions short, which round 4's list also missed (required change 3).
- Listed but not on the path: `derived.py` (imported only) and `stats.py` (the text says so). Both are harmless.
- The rule on raises is in line 105 and says the fix clause of line 104 does not apply, so the two agree. Its gaps come from sentences new in draft 8 (required changes 1 and 2).

**2. The other changed sentences**

I could not break these:
- **"The two batches", lines 72–75.** Agree, disagree and "at the tolerance" split every pair of defined labels with no gap and no overlap (script b, B1: 491,401 pairs of medians). Two outside labels on opposite sides are always more than 0.05 apart, so "the labels differ" is enough in the second bullet.
- **The comparison with `EPS`.** The rule is complete, and `analysis/k3w.py:91` is right. The code compares the contrast with nothing (`EPS` is used at `k3w.py:233`, `286`, `323`), so a person applies it; the printed float has full precision.
- **Line 55's numbers.** For batch 1 at 1.02 to 1.04, batch 2 reads "at the tolerance" from above 1.05 up to 1.07 to 1.09 (B2).
- **The contrast, line 76.** "Its size against 0.05 decides whether batch 2 governs" is the text's rule; the code computes the difference only (`k3w.py:387–391`), under the key the text names.
- **Line 59.** The arithmetic is consistent. The 0.25 and its three facts are BELIEF, and I could not check them.
- **Line 27, "selects on burst runs alone".** This is what the code does (script a, A5).
- **Line 26, what the schedules share.** Starts nested for seeds 2–6, burst identical, 0 of 400 first turn gaps shared.
- **Line 44, the counts' n.** A run with no r counts as False, and a rule that raised is not counted (script c, C3).
- **Line references.** `tests/test_k3w.py:438` and `:201` are right; the test at 201 asserts r below 0.9.
- **Ceilings.** None is raised. Five are lowered: lines 66, 71, 74, 75 and 76.

**3. Verdict: NOT READY**

Required, all text. It is READY when these six are made.

1. **Lines 27 and 105 give opposite answers for one case.**
   - Line 27 says a seed whose burst run is valid "counts here even if REG-19 … does not count that seed". Line 105 says that if the valid folders differ from the burst runs REG-19's final [RESULT] counts, "batch 2 is not computed".
   - For a seed with a valid burst run and no valid control, the first puts the run in batch 2 and the second cancels batch 2. Which rules would be settled after REG-19's outcomes are public.
   - The code does what line 27 says: `batch2_runs` returned seeds 15 to 18 with no control folder present (A5). It makes no comparison with REG-19's result, so the comparison is a step for the person running the command. Line 105 does not say that.
   - Fix: say in line 27 that the stopping rule's comparison then gives "not computed", or drop the comparison. Say in line 105 that it is made by hand, and where the two lists are recorded.
   - I could not make "counts" ambiguous. No seed of 15–19 is exposed (peaks 2.83 to 3.09 against 3.2; B4), so none can leave REG-19's n by the surge exclusion (`gate.py:1684`).

2. **Line 105, "every raise of `batch2_runs` (a gap…, two valid runs…, fewer than three seeds)".**
   - The function raises in other ways. `load.find_runs` loads every matching folder before it filters on validity (`load.py:42–44`).
   - One invalid folder of a lost burst run stops the selection: a cut last line gives `JSONDecodeError`, a missing `env.json` gives `FileNotFoundError` (script a, A4). The seal's `RuntimeError` after a mistyped final heading is a third way.
   - The text does not say whether these give "not computed" or fall under line 104's fix clause. Under the fix clause the repair would be to `load._jsonl`, which the list does not name (item 3). It could then pass as a [CORR] with no review.
   - Fix: write "whatever its cause" and name these, or say which clause they fall under.

3. **Line 102 (and 116): the list is short.**
   - Missing functions: `load._jsonl` (`load.py:14`, which parses every file of every run), `withheld.guard` (`load.py:20`), and `withheld.unsealed_ids` (`withheld.py:57`, in batch 2 only).
   - Missing constants: `load.RUNS` and `withheld.DECISIONS`.

4. **Line 55, "The owner can overrule this before batch 2".**
   - By then batch 1's median is known exactly and REG-19's table is public. Its completion rates bound batch 2's r, which is line 54's own argument.
   - The rule on which batch governs would be chosen knowing both sides of the contrast it judges (research rule 7).
   - Fix: write "before batch 1 is computed", or strike the sentence.

5. **Line 58, "leaves its r anywhere from 1.02 to 1.06".** That is the first factor. With line 51's second factor of 0.98 to 1.00, r is 1.00 to 1.06. The range 0.2 to 0.85 was computed with the second factor and stands.

6. **Line 116, "`_dirty`, with the changed `__main__` block that calls them after the judged table exists".** `_dirty` runs before `reg21_table` (`k3w.py:462–463` against `465`), as line 103 needs. Only `vj_counts` and `reported_spans` run after it.

If item 1 or 2 is closed in code instead, the diff needs a review: `batch2_runs` and `find_runs` are on the judged path.

Optional:
- Line 84 keeps the contrast under "Reported, never judged", as do `k3w.py:35` and `tests/test_k3w.py:383`. Say there that its size decides which batch governs, and that the [RESULT] shows the comparison.
- Line 102, "`reference` up to its mean": the gauges run before the mean (`k3w.py:150`, `153`). "Without its gauges" is exact.
- Line 27 names two raises as "not computed" and line 105 names three; align them.
- Line 71, "runs whose outcomes had not been read", sits beside a note that one outcome was known. "Whose r had not been computed" is exact.
- Have the batch-2 [RESULT] show that `batch1_median` equals the λ = 2.0 median of batch 1's [RESULT].
- Line 152: say when the later [CORR] to `reported_spans` may come, so that both batches' spans are computed alike.
- Line 143 stands under the heading "reviews of draft 5"; line 116 names `REG21` twice.

**4. What I could not check**

- **Any real run:**
  - that three of REG-19's burst runs exist;
  - whether any folder matching the batch-2 pattern is unreadable;
  - the hit share of 0.000 (line 53, changed from "0.000 to 0.003");
  - the 13 + 5 folders.
- **Anything in `docs/` outside the bundle:**
  - `docs/status.md:21` (line 9);
  - the traces a1, a2 and C in the cited reviews (lines 32, 83, 89);
  - what draft 5 read (line 55);
  - the owner-proxy's conditions (line 143);
  - line 106's `withheld.lifted(...)` gave False, which I did not run because it reads `docs/decisions.md`.
- **The VM's history in line 59.**
- **Not run:** the full `uv run pytest`, `tests/test_withheld.py`, and `python -m analysis.k3w reg21`.
- **Reachability of item 2's cut line.** The harness flushes each line (`harness/loadgen.py:174`), so it needs a power loss. Whether one has left such a folder I could not see.
