REG-21 draft 3 adversarial review: NOT READY (9 required changes); the statistic is coded as written, but selection, the reference and the decision table have holes.

Scripts (all synthetic, no run read): /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21/reviewer_scratch/ — common.py (the test's `truth`, extended), s0_cfg.py, s1_reference.py, s2_breaks.py, s3_code.py, s4_power.py, modelf_sim_old.py (HEAD copy). The 18 repo tests pass. The bundle's k3w.py and test_k3w.py equal the working tree.

**1. Traces on which a label comes out wrong.**

(a) The stuck server IS the all-miss server at the cache-off rate, label says outside
- a1. Preempted prefill done twice, unequally in the two arms (s2_breaks.py §A). Same engine speed in both arms; tokens counted once, by first token.
  - reference redo share 0.08, stuck 0.00: r 1.077, 1.077, 1.078 → J1 outside high
  - reference 0.00, stuck 0.08: r 0.930, 0.929, 0.925 → J1 outside low
  - 0.08 in both: r 1.002, 1.002, 0.997 → inside
  - BELIEF (pinned source not read in this pass): with caching on, a preempted request resumes on its own just-freed blocks, with caching off it re-prefills in full, and `cached_tokens` is set at first scheduling only, so neither U nor `reuse` sees it. Direction r > 1. Chance it moves r by ≥ 0.03: 0.2–0.3 (BELIEF).
  - Fix: `reference()` returns preemptions/s, running, waiting, KV and U by end per reference run; report preemptions/s × mean prompt ÷ U for both arms; name this under "outside high".
- a2. An all-miss server at exactly 1.681 that idles in part of W yet is backlogged in the end window (s2 §B).
  - lull to 0.8 req/s over [1200, 1900): r 0.908 / 0.858 (seeds 2, 3); line empty in 17 % / 24 % of W; end-window waiting 10.5 / 23.8 against base 0.0 / 0.1 → "backlogged".
  - lull to 0.5 over [1150, 2050): r 0.692 / 0.689.
  - Selection looks only at the last 600 s: 67 % of W in batch 1, 25 % for REG-19's runs, 15 % for REG-15.
  - Likelihood (BELIEF): batch 1 ≈ 0.1 that any run idles ≥ 5 % of W; batch 2 ≈ 0.3 for at least one run (3000 s watch at the load nearest the floor; REG-19's own test has "emptied" labels).
  - Fix: a registered precondition, e.g. judged only if `vllm:num_requests_waiting` > 0 on ≥ 99 % of scrapes in W, else listed "idle in W".
- a3. An ok request with null `prompt_tokens` or null `t_first_token` is dropped silently: 600 instead of 900 tokens/s (s2 §F). Unlikely (< 0.02). Fix: raise.
- a4. What did not break (s1_reference.py, s2 §F, §I):
  - Reference U per rate 2–4 within 0.16 % under prop, 30 % fixed and 50 % fixed cost.
  - All-miss stuck truth on the 5/2/6 layout: median r 1.000 / 0.991 / 0.986, J2 spread 0.0002 / 0.0026 / 0.0050.
  - First token stamped at the end of prefill in 64 slots: r 1.003 / 0.998.
  - Burst requests in W: 0. `cached_tokens` all null or absent: correct. The clip never acts.
- a5. The real reference is not the synthetic one. The registration's own numbers give 1.656 at λ = 2.0 against 1.688 at 2.5; the FIFO model gives 1.686 at 2.0 with the line never under 36. So the real 2.0 run is partly unsaturated, or the cache-off rate itself rises ≈ 2 % from 2.0 to 2.5, which is what J2 judges. Effect on U_off ≈ −0.3 %.

(b) NOT the all-miss server, labels say inside
- b1. A work rate that rises with load (s2 §C): 1.66 / 1.70 / 1.74 req/s at 2.0 / 2.2 / 2.4 → group medians 0.987 / 1.011 / 1.035, spread 0.048 → J2 inside, J1 inside (1.011). Elasticity 0.26; the same law gives 1.918 req/s at λ = 3.5 against 1.681. Likely: the published span rates already look like this. Fix: report the slope of r on λ; limit the J2-inside wording to 2.0–2.4.
- b2. A server 5.9 % faster (mu 1.78, true r 1.059, should be outside high) with the a2 lull reads 0.913 / 0.892; a shorter lull reads inside. Same fix as a2.
- b3. Hits under the precondition (s2 §J): hit_frac 0.04 / 0.05 → reuse 0.040 / 0.050, all-miss True, r 1.000, yet the session-turn rate is 1.771 / 1.787 against 1.722. r cannot see hits, so the title question is answered by the precondition, not by J1. Wording fix.

(c) Selection
- Lets in runs with an idle W (a2).
- Takes every valid match: a second valid run of a seed in batch 2, or of a rate in the reference, enters silently (n 6, no raise, s3 §R). `k1._runs` raises on that; k3w does not.
- A run with no later turn in W is listed as "not all-miss in W" (wrong reason, cosmetic).
- Runs just over 0.05 reuse are dropped but stay in `rows` with their r: fine.

(d) Grouping (s2 §E, s4_power.py)
- 2.0 at 1.01 ×5, 2.4 at 1.04 ×6, the 2.2 pair at 1.02 and 0.95 → J2 outside (0.055). If the 0.95 run fails the precondition the group drops → J2 inside (0.030). One run decides J2 either way.
- A 2.2 pair at 0.90 and 1.10 → group median 1.00 → J2 inside, spread 0.000.
- The pair has different windows (900 s and 3900 s).
- Monte Carlo on the layout, no load effect: run sd 0.025 → J2 outside 4.8 %, label changes without the pair 4.2 %; add a day sd of 0.02 → outside 21–29 %, changes 12–17 %.
- Fix, chosen now: `min_group_runs` 3 (the pair is reported, not judged), or keep 2 and register the leave-pair-out spread and the wording when the label depends on it.

(e) Median and bimodal sets (s2 §D)
- 7 runs at 1.00 and 6 at 1.12 → median 1.000, J1 inside; J2 then reads outside (0.060) with no load effect.
- 7 at 0.96 and 6 at 0.80 → J1 inside.
- Load and date coincide (ids in `k3.REG21["batch1"]`): six 2.4 runs on 20261109, both 2.2 on 20261110, 2.0 one on 20261110 and four on 20261111. A day effect of 1.07 / 1.03 / 1.00 gives J2 outside (0.070). The text budgets 0.01 for days and Alternative 6 mentions days only against the reference.
- Likelihood (BELIEF): a 0.12 split ≤ 0.1; a day sd of 0.02 ≈ 0.2.
- Fix: report min, max, SD per group and each run's date; the 2.0 group's own day contrast (seed 2 against seeds 3–6); word J2 outside as "load or day".

**2. Is the statistic what the text says?**

Matches:
- `work_rate`: `(q.status == "ok") & (q[by] >= a) & (q[by] < b)`, session and burst, `fillna(0)`, clip, ÷ (b − a), NaN on an empty window.
- `window`: [1680, 2580), [1680, 5580), [1680, 4080) from the resolved configs (s0_cfg.py); REG-15's step to λ = 1 is at 5580, the end of W.
- `row`: r = U ÷ U_off; all-miss is `ru <= 0.05` and not NaN.
- `judge`: `abs(med - 1) <= tol + EPS`; under 3 runs undefined; groups by `f"{lam:.1f}"` with ≥ 2 runs; under 2 groups undefined; batch 2 has no J2; left-out rows carry a reason.
- `select`, the 13 ids, the `_drift` run not matched.
- Nothing judged depends numerically on the replay.

Disagreements:
- "the five runs of `sweep_l1pl350_pc_off`": `reference()` checks no count. A missing run gives n 4, a rerun n 6, none n 0 and NaN; none raises (s3 §R).
- Alternatives 2: "The running batch, KV and preemptions per second are reported for both." `reference()` returns only `{"runs", "n", "mean", "sd", "spread"}`.
- Alternatives 5: "U by first token and by end time are both reported." Only for the stuck runs.
- "within about ±1 % of their mean (1.656 and 1.688 …)": 1.656 ÷ 1.681 = 0.985, i.e. −1.5 %.
- "a running batch of 16 or 64 slots (which moves the mean served turn index by more than 0.03 …)": the test asserts it for 64 only.
- J1's median pools 5 + 2 + 6 runs over three loads with no stated assumption (rule H); the assumption is J2 itself.

Batch 2 before its seal lifts: it cannot be computed. `find_runs` drops the sealed folders, `rows = []`, and `judge([], loads=False)` gives "undefined" with exit 0 after printing the reference. That uses up "computed once" silently. With `AFTERSHOCK_UNSEAL=REG-19` in the shell the seal is bypassed. No check of one valid run per seed.

Readouts: `row()` calls `readouts()` inline, so an exception in a reported readout aborts the judged table (s3 §S: metrics without a waiting column → KeyError in the `shock_size` path). The stopping rule covers it. `mean_prompt` is by first token; `kbar`, `turn0_share`, `d`, `X_*` are by end time.

`simulate(decode_s=0)`: identical to HEAD. Every numeric column is byte-identical, status and CSV bytes equal on three configs (s3 §G2); `.equals` is True on five (s2 §G; that section's "byte-identical False" line is my script's error on the string column). The repo test compares new default against new `decode_s=0.0`, so it cannot detect a change from the old code.

`decode_s` branch: right as specified (s2 §H). Residence exactly `decode_s`, next turn released at `t_end` + planned gap, server free at prefill end, U ÷ U_off 0.9995 / 1.0003 / 0.9998 at 0 / 7 / 40 s. One wart: `first = t_free if decode_s else st` stamps the plain replay at the START of service and the residence replay at the END of prefill (0.52 s apart; 1e-12 flips it). The tests' `truth` also stamps at service start.

Tests: `reference()` and `select()` have none (both monkeypatched where reached); the `u_off` fixture is one rate (3.0) at prop cost.

**3. The strongest alternative explanation**

- J1 inside: already fixed by what has been read. r ≈ X ÷ 1.681 × mean-prompt factor; X seen at 1.70–1.84 and a factor of 0.954–0.998 (synthetic) give r 0.965–1.092, centre 1.01–1.04 (s3 §T). Second: compensation (cheap resume after preemption up; idle and fixed cost down, −0.009 to −0.014). Separators: batch 2; redo share in both arms; share of W with an empty line; E1's U and step D's U.
- J1 outside high: the reference pays full re-prefill after preemption and the stuck server does not (a1). Not "closed loop", so E1 (cache off) would not remove it. Then: the 2.0 reference run is low; dev mode; day. Separators: preemptions/s in both arms; r against the 2.0 and 2.5 reference runs alone; E1 against step D.
- J1 outside low: idle time in W (a2), not recomputed prefill; the text's BELIEF points the wrong way if resumed prefills hit their own blocks. Separator: share of scrapes in W with waiting = 0.
- J2 outside: day (fully confounded with load), then the group of two with unequal windows, then a bimodal set. Separators: the 2.0 group's day contrast; per-group min and max; leave-pair-out spread; dates.

**4. Can any outcome change a decision?**

- J1 inside and J2 inside: wording of K3 and of the paper sentence. The drop "sized from U_off and the reported mean served prompt" equals the measured cold completion rate ÷ r, within 5 % of the other branch by the definition of inside. Not a different decision.
- J1 outside high: "E1's closed-loop floor only (E1 runs in any case)". If E1 runs anyway, margins go against it anyway; this changes only if the text says 1.681 stays for closed-loop margins under "inside". Drop sizing differs ≤ 5 % in rate (≈ 11 % in drain time between 1.70 and 1.78): take the lower in both branches and the branch vanishes. Mostly wording.
- J1 outside low: a real decision (a judged item in a later registration), but unreachable on batch 1. It needs X ≤ 1.60–1.67 and the lowest seen is 1.70, so P ≈ 0, not 0.05. On batch 2 it is reachable mainly through idle time, for which the decision would be wrong.
- J2 outside: real (model F dropped across loads, K3's claim changes). But it is batch 1 only, confounded with day, and near a coin flip if the true effect is 0.05 (P outside 0.52; at 0.03, 0.03–0.14).
- Tolerance 0.05: J1 on batch 1 is nearly certain inside or borderline high. Under noise alone P(J1 outside) ≤ 0.03 at centre 1.02 and 0.11–0.17 at centre 1.04 (s4).
- Missing: which batch governs when they disagree; J1 when J2 is outside; that J2 inside says nothing beyond 2.0–2.4.
- Should it run: yes, at 0 GPU h, but only batch 2's J1 and batch 1's J2 are live; batch 1's J1 changes nothing. The registration should say so.

**5. Verdict: NOT READY**

Required:
1. Register a "no idle in W" precondition with its threshold, for both batches (a2, b2).
2. `reference()`: pin the five run ids, raise unless exactly those five are valid; return per-run preemptions/s, running, waiting, KV and U by end, as Alternatives 2 and 5 already promise.
3. Batch 2: raise unless `withheld.lifted("[RESULT] REG-19")`; require one valid run per seed; name the seeds expected.
4. J2: fix the group-of-two rule now (`min_group_runs` 3, or a registered leave-pair-out readout and wording); add the load-date confound to Alternatives; report per-group min, max, SD and dates; word J2 outside as "load or day".
5. Decision table: say which batch governs; cover J1 with J2 outside; rewrite outside-high (E1 does not separate the preemption alternative; drop-sizing rule) and outside-low (idle first; unreachable on batch 1, P corrected).
6. State the pooling assumption behind J1's median over three loads (rule H).
7. Correct "within about ±1 %" (it is −1.5 % at 2.0) and say whether the 2.0 reference run counts if its line empties in its window.
8. `work_rate`: raise on an ok request in the window with null `prompt_tokens` or `t_first_token`.
9. Tests: `reference()` on fake runs (rate boundary, count, raise); correct the "16 or 64" sentence or assert it for 16.

Optional:
- Compute the judged table before the readouts and catch readout errors per run.
- Stamp the plain replay's first token at the prefill end too.
- Report the slope of r on λ with its interval.
- Report r against the 2.0 and 2.5 reference runs.
- A frozen-output test for `simulate(decode_s=0)`.
- The reason "no later turn in W" in `left_out`.

Could not check:
- The pinned vLLM source: resume after preemption, when `cached_tokens` is set, first-chunk timing, the step budget. Everything about the real engine above is BELIEF and belongs in open-questions.
- Any real run, so nothing about `k1.cold_backlogged` or `gate.secondary_cb` on real metric frames.
- docs/ (definitions, claims, model M5): not read, per the brief. The CLAUDE.md session-start reading was skipped for the same reason (rule F pass).
- The fixed-cost share 0.18 s: taken from the code's constant.