## 2026-11-12 · [REG] E1 (draft 2): the closed-loop cache-off sweep of L1 at 350 W, which measures K2's 8-turn closed-loop floor (≈ 2.1 GPU h)
- **Owner (2026-11-12):** "go ahead with 2, 3 and 4". After the rule F review, the owner chose **"Floor only"**: E1 carries no K3 test. This is a draft; nothing runs before the owner approves it.
- **Config:** `configs/sweep_l1pl350cl_pc_off.yaml`. It is REG-8's cache-off sweep (seed 0, 900 s per rate, warm-up 240 s, drain 300 s) with REG-13's two changes, closed-loop turns and `loadgen_force_close: true`, at REG-8 part b's rates [1.5, 2, 2.5, 3, 3.5, 4]. At every rate the schedule equals REG-8's (`tests/test_e1.py::test_e1_schedules_equal_reg8_part_b_at_every_rate`). The longest prompt is 3968 tokens.
- **What is measured:** the closed-loop cold floor, `e1.floor`.
  - **Rule:** `gate.cold_floor` with REG-8's settings (KV ≥ 0.85, at least 2 runs, throughput < 0.95 × planned).
  - **Registered fallback** (review, recommendation 5): if and only if that rule returns "not_monotone", `e1.floor_tail` is used. Its λ_sat is the lowest rate from which every row is saturated, and its floor is their mean, from at least 2 rows. Its status is "tail_ok", "tail_too_few" or "tail_unsaturated", so a fallback floor cannot be mistaken for cold_floor's own.
  - **Example of where the fallback matters:** the 1.5 row has planned rate 1.606, so it counts as saturated only below 1.526. If it is full but keeps up, cold_floor alone would leave the floor undefined.
  - **No floor:** any status other than "ok" or "tail_ok" means E1 gives no floor, and E0 reads "missing".
- **What the floor is for:** ratio₈ in E0's gate, and the floor quoted for closed-loop cells. 1.681 is then written as "the open-loop floor" only.
- **Model F's value, reported only:** 1.744 (fixed cost) or 1.771 (proportional), from the replay of E1's config at μ = 1.681 over rates ≥ 2.0 (`k2.closed_loop_floors`). It is not judged: the closed-loop cold spans of REG-11 to REG-18 (1.72–1.81 req/s at λ = 2.0–2.4) already anticipate a value above 1.681.
- **Reported, never judged (the owner's choice):** the served-mix tilt against REG-8, `e1.tilt` over the rates both sweeps have from their common onset, with `e1.prediction` as its description. The review showed it is generic. FIFO, many slots, residence, superlinear cost and LIFO all give d_k of −0.36 to −0.39 per req/s, against model F's −0.39 (synthetic). The cause is within-session precedence plus work conservation, so it cannot separate model F from other servers. The REG-11 to REG-18 first-turn shares already showed its sign. REG-21 v3 will drop J4 for the same reason. **K3 gets no blind test from E1.** The paper says model F's mix prediction was not tested separately.
- **Confounds, named** (review, recommendation 6):
  - E1 opens a new connection per request and REG-8 did not.
  - REG-8 ran on 2026-11-07, so it is a historical arm.
  - Both sweeps run their rates in ascending order, so drift within a sweep enters any slope.
  
  All three touch the reported tilt and the floor's comparison with 1.681 only.
- **Prediction (BELIEF):** P(floor status "ok") ≈ 0.75; P("tail_ok") ≈ 0.2; floor 1.70–1.80.
- **Decision that changes (rule A1):** none of E1's own outcomes is a decision by itself. E1 runs in any case (decisions.md 2026-11-12 [DECISION] "K2 staged"), and its floor is a required input to E0's gate, which is a decision (8–12 GPU h). A floor E1 cannot define makes E0 "missing".
- **Cost:** 6 runs × (900 + 300 + about 60 s) ≈ 2.1 GPU h, or ≈ 4.2 h with one rerun per rate. It needs 350 W, needs no REG-19 result, and runs after REG-19's queue.
- **Code and tests:**
  - `analysis/e1.py`: `floor`, `floor_tail`, `saturated`, `onset`; reported only: `tilt`, `fit`, `prediction`, `replay_rows`, `observed`.
  - `tests/test_e1.py`, 7 tests: fit and its SE; the tilt over common rates (no `judge`); the floor rule and its fallback; onset; the replay's tilt in closed loop and not in open loop; the prediction table; the schedule equality with REG-8.

---

## 2026-11-12 · [REG] E0 (draft 2): K2's gate. Does the window widen from 8 to 16 turns per session, with the warm side gaining too? It decides whether the 16-turn shock matrix (8–12 GPU h) runs (0 GPU h; E2 ≈ 4.2 GPU h, approved separately)
- **Owner (2026-11-12):** "go ahead with 2, 3 and 4". After the review, the owner chose **"Add 2.2"**: E2's warm grid gets 2.2, and "widens" requires the warm side to gain. Rule G: registered before E1 or E2 runs.
- **Claim:** K2's first half (`docs/claims.md`).
- **Statistic:** R = ratio₁₆ / ratio₈, where ratio = closed-loop warm capacity ÷ closed-loop floor. R is reported together with its two factors, warm₁₆/warm₈ and floor₁₆/floor₈ (`k2.decide`, `k2.observed`).
  - Warm capacities use the configs' rule (`tables.sweep_capacity`), seed 0. warm₈ is REG-13's `sweep_l1pl350cl_pc_on` (2.4, seen); warm₁₆ is E2's `sweep_l1t16pl350cl_pc_on` at rates [2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2].
  - Floors use `e1.floor`: floor₈ from E1, and floor₁₆ from E2's `sweep_l1t16pl350cl_pc_off` at rates [1.0, 1.5, 2.0, 2.5, 3.0].
  - The E2 configs are REG-13's and E1's with `turns: 16`. The longest prompt is 6016 + 128 tokens, against the 40,960 limit.

### The rule (`k2.decide`)
- **g = 1 + (next REG-13 grid rate above warm₈ − warm₈) / warm₈ = 1 + 0.2/2.4 = 1.083.** It is computed from the measured warm₈ and REG-13's grid. A measured R ≥ g still implies a true R ≥ 1 after the 8-turn rounding. g does not cover a lucky pass at one grid rate (REG-13's 2.4 passed at 0.9503 against 0.95) or noise in the floors.
- **Labels:**
  - **"widens":** R ≥ g **and** warm₁₆ > warm₈. Only this label lets the 16-turn shock matrix be registered.
  - **"floor_only":** R ≥ g but warm₁₆ ≤ warm₈. The window widened only because the cold floor fell (cold prompts 3072 → 4096 tokens). No matrix (review, recommendation 2).
  - **"does_not_widen":** R ≤ 1. K2's first half is refuted for L1 at sweep cost. No matrix.
  - **"unresolved":** 1 < R < g. No matrix; the owner decides.
  - **"missing":** a needed input is undefined for want of data: no valid run at E2-on's lowest rate, no valid E2-on run at all, or a floor that `e1.floor` leaves undefined. No matrix; the owner decides (review, recommendation 5).
- **E2-on's lowest rate (2.0) measured and failed:** R is bounded above by its value at 2.0 (`R_upper`): "does_not_widen" if R_upper ≤ 1, otherwise "unresolved".
- **Surge sensitivity, stated:** both setups use the same rule on seed 0, so R compares setups under one rule. It is not a sustained capacity.

### Prediction (DERIVED, `k2.predict`, `k2.closed_loop_floors`, `k2.predict_measured`; BELIEF as a forecast)
The cost per request is a + b × (tokens to prefill), at the stationary mix. Cold tokens are 3072 at 8 turns and 4096 at 16; warm uncached tokens are 496 and 376. Model F's closed-loop floors are replayed at onsets 2.0 (8 turns) and 1.5 (16 turns).

| cost model | warm₁₆/warm₈ (true) | warm₁₆, true → read on the grid | floor₁₆/floor₈ (closed loop) | R, true | **R as the gate reads it** | **label** |
|---|---|---|---|---|---|---|
| fixed (0.180 s + 0.135 ms/token; REG-8's two capacities) | 1.070 | 2.57 → 2.4 | 1.431/1.744 = 0.821 | 1.304 | **1.219** | **floor_only** |
| proportional | 1.319 | 3.17 → 3.0 | 1.367/1.771 = 0.772 | 1.709 | **1.619** | **widens** |

- **Primary model:** the fixed model, calibrated on two measured capacities, predicts **"floor_only"**: the floor falls about 18 %, and the warm capacity rises only 7 %, which the grid reads as no change.
- **Calibration caveat** (review, §3): both models scale the warm side from the open-loop 4.047. The closed-loop warm capacity (2.4, 59 % of it) is limited by something other than per-request token cost, so the warm-side prediction is weak. At equal session counts the 16-turn live context is about a third larger (≈ 72k of 96,656 tokens at λ = 3.2, against ≈ 54k at 8 turns; DERIVED, sessions in service ≈ λ × (gap + latency)). That pressure could lower warm₁₆ further.
- **Overload range:** E2-off's saturated rows sit at ρ ≈ 1.05–2.1 against its predicted floor of 1.431, and E1's at ≈ 1.15–2.3 against 1.744. A mismatch in onset moves R by at most about 3 % (review, synthetic; `by_onset`).
- **P (BELIEF):** "widens" ≈ 0.3, "floor_only" ≈ 0.3, "does_not_widen" ≈ 0.2, "unresolved" ≈ 0.1, "missing" ≈ 0.1.

### Not blind
REG-13's 2.4 and REG-8's 1.681 and 4.047 are seen, and they are inputs. E1 and E2 are unseen.

### Decision that changes (rule A1)
Only "widens" opens the 8–12 GPU h 16-turn shock matrix. Every other label stops K2 at about 6.3 GPU h (E1 + E2). "floor_only" and "does_not_widen" are written up as K2 results; the 4-turn point is considered only after "widens". The prediction table, the P values, the closed-loop floor correction and the KV arithmetic change no decision.

### Cost
E0 costs 0 GPU h. E2 is 12 runs × about 1260 s ≈ 4.2 GPU h, needs its own approval, and runs after E1.

### Code and tests
- `analysis/k2.py`: `shape`, `cold_tokens`, `warm_tokens`, `token_gap`, `calibrate_fixed`, `predict`, `closed_loop_floors`, `predict_measured`, `gate_factor`, `decide`, `observed` (`gate`, R against g alone, is kept for the table).
- `tests/test_k2.py`, 9 tests: the token gaps; L1's mean tokens; the calibration; R at 16 turns; `decide`'s labels, including "floor_only", "missing" and `R_upper`; the prediction on the gate's scale; the gate factor; the E2 configs; the closed-loop floors.
- Configs: `sweep_l1t16pl350cl_pc_{on,off}.yaml` (2.2 added to on).

---

### Adversarial review, round 1 (separate subagent; it saw draft 1, its code and configs; no runs, no docs). Verbatim:
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

### Changed because of round 1
- **E1:**
  - Recommendation 3, and §1/§3 (the tilt is generic): the owner chose "Floor only". The tilt is reported and never judged; `e1.judge` is removed.
  - Recommendation 4 (t quantiles): moot, since nothing is judged on a slope.
  - Recommendation 5: the "not_monotone" fallback `e1.floor_tail` is registered.
  - Recommendation 6: the confounds are named.
  - Recommendation 7: the preemption and in-service readouts are dropped (no code).
  - Recommendation 8: the test count, the `e1.py` docstring and the ρ range are corrected.
  - §2.4: the tilt is fitted over the rates both sweeps have.
- **E0:**
  - Recommendation 1: the owner chose to add 2.2 to E2-on's grid.
  - Recommendation 2: "widens" now needs warm₁₆ > warm₈, and the two factors of R are reported. "floor_only" is a label of its own.
  - Recommendation 5: "missing" is separated from "below the grid".
  - §2.6: g is computed from the measured warm₈.
  - §1 (scale): the prediction is given as the gate will read it.
- **Not adopted:** recommendation 9 (does vLLM's FCFS scheduler skip a waiting head that does not fit the pool?). It bore only on the open-loop arm of the tilt, which is no longer judged. It goes to `docs/open-questions.md` as A17.
