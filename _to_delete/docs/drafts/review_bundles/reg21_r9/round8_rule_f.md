# Rule F, round 8, on REG-21 draft 12 (agent a0adfd0cddd98f5fb), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input), no word changed. Bundle: `docs/drafts/review_bundles/reg21_r8/`; code at `8164211`.

---

REG-21 draft 12, round-8 adversarial review (rule F): NOT READY

R1–R5 are fixed as worded; R4 is worded more strictly. F6–F11 are taken. D1 and D3 are consistent with the rest of the text. D2 is not: the `batch1_median` check it now gives a consequence is undefined in one reachable case (batch 1's λ = 2.0 group with fewer than three judged runs) and has no stated precision. In that case it contradicts lines 75–76. New alternative 10 also gets its mechanism wrong for the fixed-load contrast. Both are text-only fixes; no code has to change.

How I worked (same limits as round 7):
- I opened and listed nothing under `runs/` or the backups. Under `docs/` I read only the bundle and checked that the two newly cited review files exist.
- I read code from my `8164211` snapshot (with `harness/` and `configs/`).
- HEAD is `5956ddb`. `git diff 8164211 HEAD` is empty for the nine named files and also for `analysis/k3.py`, `modelf.py`, `modelf_sim.py` and `harness/`.
- The bundle diff equals a fresh `diff`. Draft 12 is byte-identical to `docs/drafts/reg21_draft12.md`, and the draft-10 copy is the one I reviewed.
- I did not rerun the tests: the code is unchanged since round 7, where `tests/test_k3w.py` passed 35.
- New synthetic trace: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r7_scratch/runner/trace_b1_median.py. It uses hand-made rows only, with `find_runs`/`load_run` set to refuse.
- Fresh diff: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r7_scratch/d1012.diff
- Line numbers below are draft 12's.

**1. Round 7's required items**

1. **R1, the overrule window: FIXED, verbatim** (line 55). The window events also take F9 ("batch-1 or reference run").
2. **R2, batch 2 only after batch 1's [RESULT]: FIXED, verbatim** (line 103, last sentence; together with D3 in its first sentence).
3. **R3, "later" means after REG-19's final [RESULT]: FIXED, verbatim** (line 107).
4. **R4, the list of folders already present, made at append: FIXED, stricter** (line 108 (a)). It prints the folder names and the `valid` field alone.
5. **R5, `modelf.py` and `harness/workload.py`, with `harness/` checked clean: FIXED, verbatim** (line 159).

**2. Findings on D1–D3 and the rest of the 10 → 12 diff**

**G1. D2 (line 84): the `batch1_median` check is undefined for a small λ = 2.0 group and has no stated precision, and line 76 still says governance rests on the contrast "alone". Required.**
- Trace, small group:
  - Inputs: in batch 1, REG-18's seeds 3 and 6 are idle in W (the risk line 53 names) and one more λ = 2.0 run is left out. The group then has 2 judged runs, median 1.035, J1 "undefined". Batch 2's J1 is defined.
  - The synthetic run gives batch 1's group "2.0" as {n: 2, median: 1.035, J1: undefined}. Batch 2 prints `batch1_median: nan, difference: nan`, because `reg21_table` sets b1 to NaN when the group has fewer than 3 runs (`k3w.py:387–391`).
  - What the text says:
    - Line 84: NaN ≠ 1.035, so it is a mismatch, batch 2 does not govern, and "Batch 2's J1 inside" does not apply.
    - Line 75: "Undefined … is not a disagreement: the defined one is reported alone", so batch 2's J1 stands and line 71 applies.
  - These are opposite answers. The reading would be chosen after batch 2's J1 is printed.
  - How often: by the draft's 0.92 per run, about 0.005 (DERIVED: Σ over k ≤ 2 of C(5,k) 0.92^k 0.08^(5−k)). If seeds 3 and 6 both fail busy, about 0.22 (DERIVED: 1 − 0.92³).
- Trace, precision:
  - Batch 1's [RESULT] quotes "1.031"; batch 2 prints 1.0310004 after a change the diff check does not see (for example an environment rebuild under D1's fix clause).
  - At three digits they are equal and batch 2 may govern; at full digits they differ and it may not.
  - No precision is stated. The comparison is made by hand with batch 2's J1 and contrast on screen. D2 is what makes this matter: in draft 10 a mismatch "changed nothing else".
- Line 76's "which rests on `fixed_load_contrast.difference` alone" contradicts D2, which adds the check as a second thing that decides governance.
- Line 73 ("then … batch 2 governs") gives no precedence to line 84's rule (Optional below).

**G2. Alternative 10 (line 98) gets the contrast's mechanism wrong. Required (wording only).**
- The text names a clock difference "between the reference's day (2026-11-07) and REG-19's days" as "the likeliest cause of a non-zero fixed-load contrast".
- In the code both batches' r use the same `ref["mean"]` (`k3w.py:383–387`, `row` at `:259–260`). The contrast is b2 − b1, so the reference's day only scales it; it cannot create it.
- What moves the contrast is a clock difference between batch 1's λ = 2.0 days (2026-11-10, 11) and REG-19's days. The reference's day moves J1's level for both batches alike.
- "The likeliest cause" also has no tag.

**G3. D1 (line 107): consistent; no rule left open that matters.**
- The four non-computing failures follow line 106's fix clause and are rerun, with the judged path and `k3w.py` unchanged. That agrees with "computed once", because nothing was printed.
- "Once `reg21_table(2)` has been entered and before the table is printed" covers raises in `vj_counts` and `reported_spans` too (`k3w.py:466–468`); "wherever it comes from" covers them.
- Edge (Optional): a `MemoryError` raised in the code gives "not computed", while the OS killing the process for lack of memory is an "interruption" and is rerun. The same cause gives opposite answers, and the operator does not choose which.

**G4. D3 with R2 (line 103): consistent.**
- The bullet says "appended" in its first sentence and "committed" in its last. Batch 2 needs both, so the stricter one governs. No contradiction.
- Line 84's check now has a batch-1 [RESULT] to compare with.

**G5. F11 (line 110): "while it stood" leaves a gap.** A stray heading put into the working copy, a run made while `lifted` reads it as True, then the heading deleted before commit: the peek is labelled, but a later run after REG-19's final result, which computes the same values, would govern (Optional).

**Checked and could not break:**
- F7 (lines 102, 113), F8 (line 111), F10 (line 107).
- The header's two new review files exist.
- Alternative 10's citations resolve: `harness/checks.py:15–16`, `recorder.py:66` (`sm_clock_mhz`).
- "The run checks enforce the power limit" holds through `expected_power_limit_w: 350` in `configs/l1_pl350_base.yaml:7` (the reference sweep's parent) and `stage2_l1pl350_base.yaml:6`. It was added in REG-8's [REG] commit `3fa9563`.
- Alternative 11's last sentence matches line 33.
- No ceiling is raised by the diff.

**3. Verdict: NOT READY.** Two changes are required. Under the proxy's own list, G1 touches the mismatch rule and needs an owner-proxy pass. G2 is wording and needs none.

- **Required 1 (line 84, line 76, line 113).**
  - In line 84, replace "with the check that the printed `batch1_median` equals the λ = 2.0 median of batch 1's [RESULT]. If they differ, it is reported first, …" with:
    "with the check that the printed `batch1_median` equals, within `EPS`, the λ = 2.0 group median that batch 1's command printed, which batch 1's [RESULT] quotes in full. If batch 1's λ = 2.0 group had fewer than three judged runs, `batch1_median` is NaN by construction (`k3w.reg21_table`) and the check is that it is NaN; that is not a mismatch, and "Undefined or not computed" (the two batches) applies. If they differ otherwise, it is reported first, …" (the rest unchanged).
  - In line 76, replace "which rests on `fixed_load_contrast.difference` alone" with "which rests on `fixed_load_contrast.difference` and the check of `batch1_median` ("Reported", the fixed-load contrast) alone".
  - In line 113, add "The batch-1 [RESULT] quotes each load group's median as printed, in full."
- **Required 2 (line 98).** Replace "Prefill is compute-bound, so r would move about one-for-one with the clock ratio (BELIEF); a few percent between the reference's day (2026-11-07) and REG-19's days is the size of the tolerance, and the likeliest cause of a non-zero fixed-load contrast." with:
  "Prefill is compute-bound, so U would move about one-for-one with the SM clock (BELIEF). A clock difference between the reference's day (2026-11-07) and the cold runs' days moves r, and so J1's level, for both batches alike; a clock difference between batch 1's λ = 2.0 days (2026-11-10 and 11) and REG-19's days moves the fixed-load contrast, from which the reference cancels (both medians are over the same U_off). A few percent is the size of either tolerance (BELIEF as to the size)."

Optional:
- **Line 73:** add "unless the check of `batch1_median` fails (the fixed-load contrast, under Reported)".
- **Line 107 (D1):** say on which side a `MemoryError` and a `KeyboardInterrupt` fall, for example "a `MemoryError` or a kill by the OS counts as an interruption".
- **Line 110 (F11):** add "if that output printed a table, no later computation of batch 2 governs".
- **Line 86:** add "and `reported_spans`' own call of the batch's run list (`k3w.py:419`), whose raise ends the command before the print".
- **Line 108 (a):** "every folder then in the `runs/` that `load.RUNS` names in the checkout the command will run from", the same `runs/` as (b).
- **Line 103:** use one word, "committed", in both sentences.
- **Line 98:** cite `harness/checks.py:188` and `configs/l1_pl350_base.yaml:7` for the power-limit check.
- **Line 99:** tag "biases J1's median low by a fraction of the run-to-run SD" as BELIEF.
- **Line 59:** a REG-22 that never registers, with no [DECISION], now also blocks batch 2 (through D3). Name it among the routes.
- **Line 3:** "rounds 4 to 6 the owner-proxy delta's" needs a comma.

**4. What I could not check**
- **Real runs:**
  - whether any folder matching either pattern is invalid or unloadable today;
  - whether each REG-8 reference run's `checks.json` holds the power-limit check (it depends on the VM's clock against commit `3fa9563` at 13:57 +0600);
  - how much the SM clock differs between days.
- **docs/ outside the bundle:**
  - draft 11 (draft 12 includes it, by the bundle's diff);
  - round-4 condition 10's verbatim text beyond the proxy's quote;
  - REG-22's text on the order;
  - the format batch 1's [RESULT] will use.
- **Not rerun:** the round-7 traces and pytest (the code is unchanged; 35 tests passed in round 7). Not run: `python -m analysis.k3w reg21`.
