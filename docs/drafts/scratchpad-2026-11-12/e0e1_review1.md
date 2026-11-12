## Rule F review of E1 and E0 (drafts of 2026-11-12)

Scope: I read only the draft, analysis/{e1,k2,modelf_sim}.py, tests/test_{e1,k2}.py, the gate, tables and load functions they call, harness/{workload,loadgen}.py, and the configs. No file under runs/ or docs/ was read, and `observed` was not called. All numbers marked **synthetic** come from replays run by the scripts in /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/fdf13821-770b-43f6-866b-c82b3bbdc140/scratchpad/review_e0e1/ (perturb.py, mu_lifo.py, noise.py, share.py, pred.py, k2pred.py). Each replay uses seed 0, onset 2.0 and the T1 threshold −0.198. `uv run pytest tests/test_e1.py tests/test_k2.py -q`: 13 passed.

### 1. Traces on which the label is wrong

**E1**
- **Model F false, label "tilted".** The tilt does not depend on model F's FIFO queue. Synthetic d_k for each server:
  - model F: −0.392
  - 8 FIFO slots: −0.384
  - 25 slots: −0.378
  - 25 slots plus 5 s decode residence: −0.363
  - 10 s residence: −0.382
  - superlinear cost (L + L²/3072): −0.373
  - **LIFO: −0.365**
  
  All are "tilted". DERIVED reason: in closed loop, turn k is released only after turn k−1 ends. Any saturated, work-conserving server that holds throughput near μ while sessions start at λ/8 must therefore serve more early turns. That is a precedence constraint, not a queue discipline. The draft's alternative 4 is also wrong as stated: 10 s of residence weakens the tilt by about 3 % (synthetic), not materially.
- **Model F true in closed loop, label "unresolved" or "flat".** The open-loop arm is the fragile side. Under unbounded processor sharing (synthetic):
  - The closed-loop slope is −0.47, stronger than F.
  - Open-loop k̄ falls from 4.39 to 3.81 (short requests finish first), and open-loop throughput collapses.
  - Result: d_k = −0.198, labelled "unresolved"; d_X = +0.39.
  
  Any open-loop departure from planned completion order pushes d toward "flat" while the closed-loop mechanism still holds. An example is skipping a waiting head request that does not fit the KV pool. The draft's reading of "flat" ("closed-loop structure fails") would then be wrong.
- **Noise.** Gaussian per-run noise σ on k̄, F true (synthetic):

  | σ | "unresolved", onset 2.0 | "unresolved", onset 3.0 |
  |---|---|---|
  | 0.08 | 24 % | 67 % |
  | 0.15 | 64 % | 77 % |

  With no true tilt, onset 3.0 and σ = 0.15, 4 % of trials read "tilted". The "2 SE" rule applies a normal quantile to residual SEs with 3 df (onset 2.0) or 1 df (onset 3.0). The t quantiles are 3.18 and 12.7.
- **Onset failure.** E1's 1.5 row has a planned rate of 1.606, so the line is 0.95 × 1.606 = 1.526 (DERIVED; the replay reads 1.485). If that row has KV ≥ 0.85 and throughput ≥ 1.526, `cold_floor` returns "not_monotone". Then:
  - the onset is NaN, so T1 and T2 are not judged;
  - F is undefined, so E0 has no ratio₈ and `k2.observed` gives R = NaN with label "nan".
  
  Neither draft registers a fallback for this.
- **Unlisted confounds.**
  - E1 sets `loadgen_force_close: true`; REG-8 did not (configs/sweep_l1pl350cl_pc_off.yaml:8 against sweep_l1pl350_pc_off_b.yaml).
  - REG-8 is a historical arm, run days earlier.
  - In both sweeps the rate is confounded with run order (ascending), so drift within a sweep enters the slopes and cancels only if it is alike in both.

**E0**
- **The gate turns on one grid step.** Measured R = (c₁₆/f₁₆)(f₈/2.4). At the predicted f₁₆/f₈ = 0.821 (fixed model, closed-loop floors), DERIVED:
  - c₁₆ = 2.0 gives R = 1.016 ("unresolved");
  - c₁₆ = 2.4 gives 1.219 ("widens");
  - c₁₆ = 2.6 gives 1.32.
  
  So the label is in effect "does the 16-turn warm sweep pass 2.4?", provided f₁₆/f₈ ≤ 1/1.083 = 0.923.
- **True widening, label "unresolved".** A true c₁₆ in [2.13, 2.4) gives a true R of 1.08–1.22, but it is read as 2.0, so R = 1.016. The fixed model's true c₁₆ is 2.568, only 7 % above 2.4, and that is before the KV blind spot. The grid's 0.4-wide gap is exactly where the decision turns.
- **No true widening, label "widens".** This needs a true c₁₆ ≤ 0.82 c₈ (about 2.0–2.1) together with a lucky pass at 2.4, as REG-13 passed at 0.9503. g covers the 8-turn rounding only: it does not cover a lucky 16-turn pass or noise in the floors. This trace is less likely than the previous one.
- **The prediction is stated on a different scale from the gate.** The table gives the true R (1.30 / 1.76). The same models predict a measured R of 1.219 (fixed: c₁₆ reads 2.4) and 1.62 (proportional: c₁₆ reads 3.0). DERIVED.
- **Overload range.** Replay floors by onset (fixed model): f₁₆ = 1.431, 1.458, 1.476 at onsets 1.5, 2.0, 2.5; f₈ = 1.744, 1.755, 1.765 at 2.0, 2.5, 3.0. A mismatch in onsets moves R by at most about 3 %, which does not decide the label given the discreteness above.
- **Missing data is labelled as a result.** k2.py:137 treats any NaN warm₁₆ as "below the grid" and labels it "unresolved" or "does_not_widen". A NaN also arises when E2-on has no valid run at all (tables.py:113-114), or when 2.0 has no valid run (the chain ends, load.py:274).

### 2. Code against the drafts
1. tests/test_e1.py has 6 tests, not the 5 the draft lists; the sixth is the schedule-equality test at line 61. test_k2.py has 7, as stated.
2. The e1.py:7-10 docstring still makes the throughput slope the statistic; the draft makes k̄ primary.
3. Readouts the draft promises but no code produces:
   - U lives in k3.cacheoff_uncached (k3.py:119), not in e1.observed;
   - preemptions per second (alternative 1) and median in-service time (alternative 4) are computed nowhere.
4. e1.fit (e1.py:82) fits each sweep over its own valid rows. The draft's "same set in both sweeps" is not enforced when a rate is invalid in one sweep.
5. The replay's saturation proxy (e1.py:63) fires at 1.5 in both replays (synthetic 1.485 and 1.477 against 1.526), so the replay's onset is 1.5. The prediction is unaffected, because its onsets are fixed (e1.py:111). The docstring claim that cold_floor "applies unchanged" is loose.
6. `gate_factor` in k2.observed uses the hard-coded 2.4 (k2.py:26, 136), not the recomputed warm₈.
7. Verified as stated:
   - every cell of the E1 table, F = 1.771 / 1.744, and the k̄ series;
   - E0's R values 1.758, 1.319, 1.709, 1.304; floors 1.744, 1.431, 1.771, 1.367; g = 1.0833;
   - 3968 and 6016 tokens; token gaps 3.48, 6.19, 10.89;
   - costs of 2.1 h and 3.85 h.
   
   Against the fixed floor of 1.431, E2's ρ range is 1.05–2.10, not "1.1–2.3".

### 3. Strongest alternative explanation of the positive outcome
- **E1 "tilted":** within-session precedence plus work conservation. Every saturated closed-loop server tilts this way; LIFO gives −0.365 (synthetic). The result is also partly anticipated. REG-11–18's first-turn shares of 0.14–0.18 at λ = 2.0–2.4 (draft, "Not blind") match the replay's 0.146 at λ = 2.0 and 0.169 at 2.5. Open loop gives 0.125–0.128 (synthetic). So the sign and the low end of the tilt have already been seen.
- **E0 "widens":** the cold floor falls because cold prompts are 33 % longer (3072 to 4096 tokens), and possibly further from superlinear attention and fewer cold requests per 96,656-token pool. Meanwhile the warm capacities can be measured equal (2.4 = 2.4), so "widens" can pass with no gain on the warm side at all. In addition, the warm-side scaling is calibrated on the open-loop 4.047, while the closed-loop warm capacity is 2.4, i.e. 59 % of that (DERIVED). Whatever limits closed-loop warm capacity is therefore not the per-request token cost the model scales.

### 4. Can each outcome change a decision?
- **E1, T1 "tilted"** is said to let M5's numbers be used for K2 and K4. E0 already uses M5's constants (`k2.calibrate_fixed`) before E1 runs, and E0's gate uses no prediction, so nothing changes for K2. Because "tilted" is near-generic, it also cannot license M5's numbers.
- **E1, "flat" or "unresolved"** change paper text only.
- **E1, items that change no decision:** T2, U, the value of F (it feeds E0 under every T1 outcome), preemptions, and in-service time. E1 runs anyway, so T1 is a free paper-text test, not a decision test.
- **E0, "widens" against the other labels** gates 8–12 GPU h, so it is a real decision. "unresolved" has no registered rule (the owner decides).
- **E0, items that change no decision:** the prediction table, the P values, the closed-loop floor correction, `by_onset`, and the KV blind-spot arithmetic.

### 5. Recommendations
1. E0: add 2.2 to the E2 cache-on grid, and consider 2.3 (about 0.35 GPU h per rate), before E2 is registered. Or register the gate directly as a rule on c₁₆. The decision turns between 2.0 and 2.4.
2. E0: report warm₁₆/warm₈ and f₁₆/f₈ separately. Register now how "widens" with c₁₆ ≤ c₈ (widening from the floor only) is treated, for example as its own label or by requiring c₁₆ > c₈ before the matrix runs.
3. E1: stop "tilted" from licensing M5's numbers. Judge the magnitude instead, against a two-sided band fixed now (for example 0.5–1.5 × d_F). Judge the closed-loop slope on its own, and use the open-loop slope as a validity check with a bound registered now: an open-loop k̄ that is not flat voids T1 rather than reading as "flat".
4. E1: use t quantiles (n−2 df per fit, Welch-combined) instead of 2 SE, or remove onset 3.0 (1 df) from the judged set.
5. Register fallbacks for E1's F or onset being "not_monotone" or "too_few", and for E0 floors that are NaN. Fix k2.py:137 so that "2.0 valid and failed" is distinguished from "no valid run".
6. Name the force-close difference, the historical control and the run-order confounds in the [REG]. A force-close rerun of a REG-8 rate would affect only T2, so it does not meet rule A1; do not propose it.
7. Write the code for the promised preemption and in-service-time readouts before registration, or drop them from the draft.
8. Correct the test count (6), the e1.py docstring and the ρ range.
9. Open question: does vLLM 0.32.0's FCFS scheduler skip a waiting head request that does not fit the KV pool? This needs SOURCE evidence, and it decides whether the open-loop arm stays in planned order.