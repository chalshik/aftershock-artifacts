REG-21 draft 6, round-4 adversarial review (rule F): NOT READY. Three required changes, all in the text; no code has to change. The six round-3 items are done as round 3 worded them (five fixed, one partly), and the judged functions are text-identical to those of `69ffedd`. What is left: four sentences the code contradicts, three numbers that draft 6's own additions made wrong, and a list of "judged functions" that leaves out part of the judged path, on which the new stopping rule depends.

How I worked: synthetic inputs and config files only. No run folder was opened or listed; `load.find_runs` and `load.load_run` were replaced before `analysis.k3w` was imported in every script; `withheld.DECISIONS` pointed at a temp file. Under `docs/` I read only the bundle (for the cited files I tested existence, not content); `round3_owner_proxy.md` was not read. Nothing in the repo was changed (scripts h and n wrote a throwaway git repository and two file copies to the system temp folder). Code reviewed: `8164211`. HEAD is now `85aa9b2`; `git diff 8164211 HEAD` is empty for `analysis/k3w.py`, `analysis/withheld.py`, `tests/test_k3w.py` and every helper I read. `tests/test_k3w.py`: 35 pass (32 functions).

Scripts, all in `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r4_scratch/`: `g_unchanged.py`, `h_newcode.py`, `i_schedules.py`, `j_numbers.py`, `k_rules.py`, `m_misc.py`, `n_seal.py`. Line numbers of the registration are those of `registration_draft6.md`.

**1. The six round-3 items**

1. FIXED, line 65 (with 41, 52, 68). The rule is complete and I could not break it. Script k (K1), 18,312 random tables with J2 inside:
   - a judged group is never undefined (a group and a level both need 3 runs);
   - the pooled median always lies between the group medians;
   - "every group has the pooled label and side" is the same condition as "the groups share one label and side". Groups that differ always get per-group sentences.
   - One gap with no reach: line 65 words no pooled sentence for "outside low" in both groups. Line 69 calls that out of reach in batch 1, and I agree.
2. FIXED, line 71. Complete.
   - "Labels differ and the contrast is NaN" cannot occur. The contrast is NaN exactly when one side is undefined (`k3w.py:388–389`; `min_runs` and `min_group_runs` are both 3; script k, K2, all 36 count combinations), and "undefined" has its own sentence.
   - When the labels differ and the contrast is 0.05 or less, the two medians always straddle one edge (K3, 8,242 of 8,242).
   - Two notes. A median can then sit 0.05 from the edge and still be called "at the tolerance" (1.005 against 1.054). The text's "above 0.05" has no rounding margin, and 1.10 − 1.05 is 0.050000000000000044 in floats (K4).
3. FIXED, line 31 and `k3w.py:17–21`. The pinned source agrees: `scheduler.py:2610` and `2943–2948`; `loggers.py:1150–1154`, inside `PrometheusStatLogger`.
4. FIXED in line 27; one clause is missing in line 100 (required change 3).
   - `batch2_runs` raises on a gap and on two valid runs of a seed (`k3w.py:351–356`). The text says batch 2 is then not computed and no rule picks runs.
   - Line 100 still says, of any raise, that a fix is logged or reviewed "before the rerun", and does not exempt these two. A fix "outside the judged functions" can change which runs are found: the validity filter is in `load.find_runs` (`load.py:41–44`), which line 110 does not list.
   - What the rule costs: batch 2 selects on burst runs alone, REG-19 on pairs (`gate.py:2022–2040`). A seed whose pair was run twice with a valid burst each time means batch 2 is never computed. Whether that is the state now I could not check.
5. PARTLY, line 57. The two numbers round 3 named now follow from the text's bounds; a third one no longer does (section 3). Scripts j (J4) and m (M1), with REG-11's run at the rate line 50 now cites:

   | | text | recomputed |
   |---|---|---|
   | P(J2 inside) | 0.85 | 0.84–0.98 |
   | P(J2 outside) | 0.13 | 0.02–0.16 |
   | P(λ = 2.4 group inside) | 0.05 | 0.00–0.19 |
   | P(pooled inside, given J2 inside) | 0.3 | 0.20–0.85 |

   The sums are 1.00. Batch 2: 0.8 × 0.95 × 0.85 = 0.646; P(undefined) is 0.235, 0.437, 0.725 with five, four, three runs.
6. FIXED as asked.
   - Line 33 matches `_why` (`k3w.py:238–251`) and `judge` (`k3w.py:298`). The new code has since made its last clause wrong (section 3).
   - Lines 80 and 82 match `k3w.py:387`.
   - Lines 27, 97 and 101 match `withheld.py:46–47`. Script n: an interim heading and `REG-19b` lift the seal; a prefixed or indented line does not; draft 6 and the round-3 review, pasted as they are, lift nothing.

**2. The code diff**

Judged functions: unchanged. Script g compares every top-level function and constant of `k3w.py` at `69ffedd` and `8164211`.
- Identical: the 14 functions line 110 lists, `REG21`, `EPS`, `_ok_in`.
- Changed: the module docstring, one import (`cp_upper`), the `__main__` block.
- Added: `REPORTED`, `span_values`, `reported_spans`, `vj_counts`, `_dirty`. No earlier function names any of them.
- `withheld.py` and every helper file are unchanged.

The new code does what "Reported, never judged" and the stopping rule say, with these findings (script h unless noted):
- **Import:** no run is read at import (H1).
- **Judged values:** the table is identical before and after `vj_counts` and `reported_spans` (H8). There is one print, at the end, so any exception prints nothing.
- **A new way to stop the table:** `reported_spans` calls `batch1_runs()` or `batch2_runs()` a second time, outside its `try` (`k3w.py:419`), and loads every run again. It can raise only if the folders or `decisions.md` change during the run. It fails closed.
- **Batch 2 before REG-19's result:** `reg21_table(2)` raises first and nothing is printed. `reported_spans(2, …)` called alone raises the same `RuntimeError` (H7).
- **Spans:** 3, 13 and 8 spans for W of 900, 3900 and 2400 s (H2). The reference's window is 660 s (240 to 900 s; script i, I7), so its spans are 300, 300 and 60 s, and the 60 s span enters the lowest and highest. On the synthetic server the SD of U over 60 s spans is 8 times that over 300 s spans (0.35 % against 0.05 %, H3).
- **A span with no ok request:** U is NaN and left out of the lowest and highest; reuse is NaN (H4).
- **Reuse on a reference run:** 0.0 on the synthetic cache-off open-loop run. If the `cached_tokens` column is all None or missing, `reuse` raises, the message is kept, and that run's U spans are lost with it (one dict, `k3w.py:409`). `work_rate`, which is judged, is not affected (H5). The pinned source suggests the column holds 0 (`output_processor.py:182`, `completion/serving.py:453–455`; BELIEF, no run read).
- **`r_first`:** equal to r exactly for a W of 900 s, different for a longer W (H6). It is computed for every run of the batch, entered or not, judged or not. No function summarizes it.
- **`vj_counts`:** counts `trapped`, which uses the realized need (`k3w.py:231, 235`), as line 44 says. Its n is the runs that entered, judged or not. A run with no r counts as "does not hold"; a rule that raised is not counted (H8, H9). Line 44 does not say which n.
- **`_dirty`** (H10, in a scratch repository): a clean tree runs; an untracked, modified or staged file under `analysis/` or `tests/` is refused; a missing git or a folder that is no repository raises before any run is read. Not covered: `harness/` (the replays import it, `modelf_sim.py:28`), files git ignores, `uv.lock`. It neither checks nor prints the commit.
- **The nesting test:** sound. It compares session starts only, needs over 500 of them and a proper subset, so it cannot pass vacuously.
  - It overrides rate and seed in one config. Script i (I1, I2) repeats it on the config files the runs used: a seed's two files differ only in name and rate, and the nesting holds for seeds 2–6, with 2.2 between for seed 2. It also holds for seeds 1–40 (I4).
  - Six distinct seeds in the 11 runs is right (I5).
  - What is shared: the start times and the burst, which is identical (its own generator, `workload.py:25`). Not shared: the turn gaps (0 of 400 shared starts have the same first gap; 0 of 4,366 later-turn times coincide; I3).

**3. Sentences the code does not do, wrong numbers, rules left open**

Sentences the code does not do:
1. Line 17: "its lowest span is not reported". It is (`U_min`, `k3w.py:411`), and line 81 says so.
2. Line 33: "a run that did not enter has no r". `reported_spans` prints `r_first` and U by span for every run of the batch, and for a 900 s W `r_first` is r (H6).
3. Line 81: "U over 300 s spans" of each reference run. The third span is 60 s and counts in the lowest and highest.
4. Line 54: "at least one clear pass". `gate.py:1710` needs k of at least 1, and k counts `pass_clear` and `pass_warm_edge` (`gate.py:1687`, `1589`). The conclusion drawn (stuck, a line that never emptied, a completion rate below 2.0) holds for both (`gate.py:1945–1964`).

Wrong numbers:
1. Line 51: "1.06 to 1.09 at λ = 2.4" covers seeds 2–6 only. Seed 1's rate, which line 50 now cites (1.72 to 1.79), gives 1.02 to 1.06.
2. Line 57: "pooled J1 inside ≈ 0.3, outside high ≈ 0.7". With seed 1 in its cited range the text's bounds give 0.20 to 0.85 inside, and 0.49 or more in 15 of 20 settings (script m, M1). 0.3 needs seed 1 at the top of its range. The pooled label turns on that one run. "In most inside tables the λ = 2.4 group is itself outside high" still holds (0.69–0.99).
3. Line 70: "the likeliest outcome". By line 58's own numbers this is true with five runs only (script j, J1):

   | runs | undefined | inside |
   |---|---|---|
   | 5 | 0.24 | 0.50 |
   | 4 | 0.44 | 0.37 |
   | 3 | 0.73 | 0.18 |

Numbers recomputed and right: 2.0 ÷ 1.681 = 1.19; every line reference into `k3w.py`, `withheld.py`, `tests/test_k3w.py`, `workload.py:55` and `gate.py:1710`; 35 tests; seed 18's first span of W planned at 1.32 req/s (from its config, I6); the scrape-gap limit of 2 s; `loadgen_force_close` in the burst configs only; busy 0.947 with r 0.969 (script m, M2).

Rule left open:
- Line 110's list of judged functions is not the judged path. Lines 98 and 100 use it to decide what must not change between the batches and which fixes need only a [CORR].
  - Missing inside `k3w.py`: `_ok_in` (called by `work_rate`, `k3w.py:110`) and `EPS`.
  - Missing in other files: `k1.reuse`, `later_turns`, `cold_backlogged`, `_state`, `windows`; `load.find_runs`, `load_run`, `metrics_wide`, `_covered`, `_level`; `gate.burst_end`, `gate.SURGE`; `margin.is_burst_request`; `withheld.lifted`, `keep`, `sealed_by`, `SEALS`.
  - Reachable: `k1.py:1` calls REG-20 a draft, so `cold_backlogged` may still change. A change there between the batches alters which REG-19 runs enter, while the registered check (an empty diff for the listed functions) passes.
  - Line 133 treats `withheld.lifted` as judged; line 110 does not list it.

Still claiming more than the data carry in "Decision under each outcome":
- Line 70: "runs not read when the tolerance was fixed", although line 54 says their gate flag was known.
- Line 72: `r_first` "tells a window effect from a day effect". It is printed per run with no registered summary. No registered wording depends on it.
- I found nothing else. Lines 65, 67, 68, 69 and 71 hold on every table I could build.

**4. Verdict: NOT READY**

Required. It is READY when these three are done; all are text.
1. Make four sentences exact: line 17 (strike the clause), line 33 (where a run that did not enter gets `r_first` and spans), line 81 (the reference's 60 s span), line 54 ("a pass, clear or warm-edge").
2. Correct three numbers: line 51 (seed 1's first factor), line 57 (the pooled split, as a range that names REG-11's run), line 70 ("the likeliest outcome" with five runs).
3. Lines 98, 100 and 110: define the judged path as everything `reg21_table` runs before the readouts, and name the missing functions above. In line 100, add that a raise of `batch2_runs` on a gap or on two valid runs is followed by no fix and no rerun, and that no folder or validity flag is changed to make the selection pass.

If any of these is done in code instead (for example, limiting `reported_spans` to runs that entered), the diff needs another look.

Optional:
- Line 44: say n is the runs that entered and that a run with no r counts as "does not hold".
- Line 72: say which runs' `r_first` is read, or that it is not summarized.
- Compute U and reuse of a span in separate `try` blocks, and pass the loaded runs to `reported_spans`.
- Line 71: apply the judged 1e-9 margin to the contrast; say batch 2's own label is still printed.
- Line 65: add "outside low in both".
- Line 79: the lull numbers are the round-3 review's (a lull from 1200 to 1700 s), not the draft-3 review's.
- Line 26: say the turn gaps are other draws and the burst is identical.
- Line 27: say batch 2 counts a seed whose burst is valid even if REG-19 does not count its pair.
- Print HEAD's hash in the table; cover `harness/` in `_dirty`.
- Record in the [REG] that `withheld.lifted('[RESULT] REG-19')` printed False.
- Line 57: "λ = 2.0 inside ≈ 0.85" is 0.92–1.00 on the text's bounds; a spread of 0.02–0.05 is a slope of 0.05–0.125.
- "Alternatives" is numbered 1–5, 7, 8, 9, 6.

**5. What I could not check**

- Any real run:
  - whether `cached_tokens` is 0 or None in the cache-off runs;
  - how many valid burst runs each REG-19 seed has;
  - the 13 + 5 folders.
- Anything in `docs/` outside the bundle:
  - the cited lines of `experiment-plan.md`, `claims.md`, `status.md`, `round1.md` and `decisions.md:3785`;
  - the published rates (1.72–1.79 for seed 1; 121 and 101 waiting);
  - the two `bad_baseline` verdicts;
  - REG-19's `continue` flags;
  - whether `decisions.md` already holds a line that lifts REG-19's seal.
- The owner-proxy's twelve conditions (not read, as instructed), so line 135 is unchecked.
- Not run: `tests/test_withheld.py` and the full `uv run pytest` (both read the real docs), and `python -m analysis.k3w reg21`. I ran the command's statements by hand on stubs.
- Why the Poisson draw leaves the stream at the same place for two rates: I did not read numpy's sampler. The nesting is shown by construction for seeds 1–40 only.
- "Not computed by anyone" and "no run folder was read" are the author's reports.
