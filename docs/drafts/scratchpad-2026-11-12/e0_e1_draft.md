## 2026-11-12 · [REG] E1 (draft): the closed-loop cache-off sweep of L1 at 350 W; its floor for K2, and a blind K3 test: does a saturated all-miss server with closed-loop turns serve a mix that tilts toward early turns as the load rises, as model F says? (≈ 2.1 GPU h)
- **Owner (2026-11-12):** "go ahead with 2, 3 and 4" (item 2: draft E0 and E1). The revised plan runs E1 in any case (decisions.md 2026-11-12 [DECISION] "K2 staged"). This entry is a draft; nothing runs before the owner approves it.
- **Why a new blind test:** the REG-21 round-2 review (scratchpad/review2/, synthetic) showed that REG-21's J4 (E1's floor against a replay at the fitted μ_k) cannot change a decision. The statistic moves only 0.78 per unit of μ, so `separates` is false whenever J3 is inside. E1 can carry a sharper test of model F's queue structure. REG-21 v3 will drop J4 and point here (owner's decision with REG-21).
- **Config:** `configs/sweep_l1pl350cl_pc_off.yaml`. It is REG-8's cache-off sweep (`sweep_l1pl350_pc_off.yaml`: seed 0, 900 s per rate, warm-up 240 s, drain 300 s) with REG-13's two changes: `closed_loop: true` and `loadgen_force_close: true`. The rates are REG-8 part b's, [1.5, 2, 2.5, 3, 3.5, 4]. Each rate is paired with REG-8's open-loop run at the same rate and seed (`sweep_l1pl350_pc_off`, valid 6 of 6 in part b, decisions.md 2026-11-07 [RESULT] REG-8). The schedules are equal by construction: `build_schedule` reads no `closed_loop`, `harness/workload.py`. Checked: all six schedules build, with longest prompt 3968.
- **Claim tested:** K3 (`docs/claims.md`). Model F (Valse and Jannesari §3; BELIEF as to the model):
  - **Closed loop:** a saturated all-miss FIFO server serves the turns that rejoin the queue. Sessions with long backlogs advance slowly, so the served mix tilts toward a session's early, short turns, and the tilt grows with the backlog, i.e. with the offered rate.
  - **Open loop:** the same server serves the planned mix whatever the backlog.
  - **What this tests:** the engine's queue structure under all-miss load (caching is off). It does not test the cache mechanism itself.

### Readouts (`analysis/e1.py`)
Rows are read by `gate.sweep_rows` with the floor rule `gate.cold_floor` (REG-8's settings: KV ≥ 0.85, at least 2 runs, throughput < 0.95 × planned).

The **onset** is the lowest rate at which both E1 and REG-8 are saturated by that rule (`e1.onset`). Every slope below is fitted over the rates from the onset up, the same set in both sweeps.

| # | Readout | Judged? | Statistic |
|---|---|---|---|
| T1 | served mix tilt | **judged (blind)** | d_k = slope of k̄ on rate (closed) − the same slope (open), with k̄ the mean turn index (1–8) of the session turns completed ok in [warm-up, duration) of each run (`e1._kbar`) |
| T2 | throughput tilt | **judged (blind)** | d_X = slope of completions/s on rate (closed) − the same (open) |
| F | closed-loop floor | reported; K2's 8-turn reference | `gate.cold_floor` on E1's rows |
| U | uncached prefill tokens/s at the saturated rates | reported | against REG-8's rows (`k3.cacheoff_uncached`) |

Under model F, k̄ is the readout that no token rate of the engine enters, which makes T1 the primary readout. T2 is affected by any engine effect whose throughput changes with the rate. Taking the difference against open loop cancels such an effect to the extent that it acts alike in both loops.

**Prediction** (DERIVED, `e1.prediction()`, before E1 runs, from configs only): the replay of both sweeps' own configs through model F's server (`analysis/modelf_sim.py`) at μ = 1.681, seed 0, both cost models. The spread is over replay seeds 0–19. The threshold is half the model-F value nearer zero.

| onset | T1 d_k, proportional / fixed (replay SD) | T1 threshold | T2 d_X, proportional / fixed (SD) | T2 threshold |
|---|---|---|---|---|
| 2.0 | −0.397 / −0.401 (0.027) | −0.198 | 0.061 / 0.042 (0.004 / 0.003) | 0.021 |
| 2.5 | −0.372 / −0.376 (0.030 / 0.032) | −0.186 | 0.057 / 0.042 (0.004 / 0.003) | 0.021 |
| 3.0 | −0.357 / −0.368 (0.055 / 0.059) | −0.178 | 0.056 / 0.041 (0.008 / 0.007) | 0.021 |

- **Replay seed 0, onset 2.0:**
  - Closed-loop k̄ is 4.30, 4.08, 3.88, 3.70, 3.53 at λ = 2–4.
  - Open-loop k̄ is 4.47–4.50.
  - The closed-loop floor (F) is 1.771 (proportional) or 1.744 (fixed cost), against 1.681 open loop.
- **Labels** (`e1.judge`):
  - "tilted" if d lies on model F's side of the threshold;
  - "flat" if d lies on zero's side;
  - "unresolved" if |d − threshold| < 2 SE. The SE combines the two fits' residual SEs, so the engine's own run-to-run noise sets it, not the replay's.
- **Onset not in the table:** if the onset is not 2.0, 2.5 or 3.0 (fewer than three common saturated rates), T1 and T2 are `no_prediction_for_this_onset`, reported, and not judged.

### Not blind, said plainly
The following have been seen:
- REG-8's open-loop rows. Their throughputs went into 1.681; their k̄ were never computed.
- REG-13's closed-loop cache-on sweep.
- The closed-loop cold spans of REG-11 to REG-18: completions of 1.72–1.81 req/s at λ = 2.0–2.4, and first-turn shares of 0.14–0.18 (decisions.md [RESULT]s).

These are closed-loop all-miss states at loads inside E1's range. F's expected value (above 1.681) is therefore partly anticipated, which is why F is not judged. No closed-loop cache-off sweep has run, and nobody has read k̄ against rate in any sweep.

### Prediction (BELIEF)
- P(T1 "tilted") ≈ 0.7. vLLM's waiting queue is first come first served. Preemption under a full pool sends a recomputed request back to the waiting queue, which may change the mix either way.
- P(T2 "tilted") ≈ 0.5 (engine effects).
- P(onset = 2.0) ≈ 0.7.

### Alternatives to state with any result
1. **Preemption and recompute** at a full KV pool reorder service. Separated by preemptions per second per row (`vllm:num_preemptions_total`), reported.
2. **Rate-dependent engine efficiency** (batch size, chunked prefill). Moves T2, cancelled in the closed-minus-open difference only if alike in both loops; T1 is not moved by it.
3. **Session cut-off at `duration_s`:** late sessions lose their last turns. Present in both loops and in the replay.
4. **A residence time** (B requests in service at once; REG-21 round 2, synthetic) acts like a longer turn gap. In the replay it weakens the tilt. A "flat" T1 is therefore checked against the median in-service time per row (t_end − t_first_token), reported.

### Decision that changes (rule A1)
- **T1 "tilted":** model F's closed-loop queue structure holds on this engine under all-miss load. Its numbers (`docs/model.md` M5) may be used for K2's and K4's predictions. K3 records its first blind hit.
- **T1 "flat":** model F's closed-loop structure fails on vLLM. M5's values are not used as predictions, and the paper says that the published model's mix prediction fails here. That is a K3 result, and a blind one.
- **T1 "unresolved":** K3 gets no blind test from E1. The paper says so.
- **F:** in any case, K2's 8-turn floor (E0) and the floor the paper quotes for closed-loop cells. 1.681 is then written as "the open-loop floor" only.
- **T2:** reported beside T1. It changes no decision alone: engine effects confound it.

### Cost
6 runs × (900 + 300 + about 60 s) ≈ 2.1 GPU h (REG-13's per-run cost). Worst case with one rerun per rate ≈ 4.2 h. The power limit must be 350 W (`checks.expected_power_limit_w`). E1 needs no REG-19 result, and it runs only after REG-19's queue, which is the other session's.

### Code and tests (uncommitted at drafting)
- `analysis/e1.py`: `replay_rows`, `saturated`, `onset`, `fit`, `tilt`, `prediction`, `judge`, `observed`.
- `tests/test_e1.py`, 5 tests:
  - fit and SE on a line;
  - tilt, judge and "unresolved";
  - onset as the later of the two sweeps;
  - the replay tilts the closed-loop mix and not the open-loop one, and open loop saturates at μ;
  - the prediction table.
- `configs/sweep_l1pl350cl_pc_off.yaml`. No run folder was read.

---

## 2026-11-12 · [REG] E0 (draft): K2's gate. Predicted widening of the window from 8 to 16 turns per session, and the rule that decides whether the 16-turn shock matrix (8–12 GPU h) runs (0 GPU h; E2's sweeps ≈ 3.9 GPU h, approved separately)
- **Owner (2026-11-12):** "go ahead with 2, 3 and 4". Rule G: the gate's pass condition is registered before any sweep it judges (E1, E2) runs.
- **Claim:** K2's first half (`docs/claims.md`): the window, i.e. the closed-loop warm capacity over the closed-loop cold floor, widens with the turns per session.
- **Statistic:** R = ratio₁₆ / ratio₈ (`k2.measured_R`, `k2.observed`).
  - Warm capacities use the configs' rule (`tables.sweep_capacity`: `capacity:` block of `l1_base.yaml`, monotone, against the planned rate), seed 0.
  - Floors use `gate.cold_floor` with REG-8's settings.
  - Inputs:
    - ratio₈: REG-13's `sweep_l1pl350cl_pc_on` (2.4, seen) and E1's floor.
    - ratio₁₆: E2's `sweep_l1t16pl350cl_pc_on` (rates 2.0, 2.4, 2.6, 2.8, 3.0, 3.2) and `sweep_l1t16pl350cl_pc_off` (1.0, 1.5, 2.0, 2.5, 3.0).
  - Both E2 configs are REG-13's and E1's with `turns: 16`. Checked: the schedules build; the longest prompt is 6016 tokens plus 128 output, against the model's 40,960 limit.

### Gate (`k2.gate`, `k2.gate_factor`)
- **g = 1 + (next grid rate above c₈ − c₈) / c₈ = 1 + 0.2 / 2.4 = 1.083.**
  - A capacity read by the configs' rule is the highest passing grid rate, so the true 8-turn capacity may lie up to one step above 2.4.
  - Hence measured R ≥ g implies a true R ≥ 1.
  - The 16-turn capacity is rounded down the same way, which can only lower R.
  - Floors are means, not rounded.
- **Labels:**
  - "widens" (R ≥ g): the 16-turn shock matrix may be registered.
  - "does_not_widen" (R ≤ 1): K2's first half is refuted for L1 at sweep cost; no matrix.
  - "unresolved" (1 < R < g): no matrix, and the owner decides.
- **16-turn capacity below the grid** (2.0 fails): R is bounded above by its value at 2.0 (`R_upper`), labelled "does_not_widen" if that bound is ≤ 1, otherwise "unresolved".
- **Not covered by g:** the closed-loop warm capacity is surge-sensitive (decisions.md 2026-11-10 [CORR]: REG-13's 2.4 passed at a throughput ratio of 0.9503 against 0.95). Both setups use the same rule on seed 0, so R compares setups under one rule. It is not a sustained capacity.

### Prediction (DERIVED, `k2.predict`, `k2.closed_loop_floors`; BELIEF as a forecast)
The cost model is per request, a + b × (tokens to prefill), at the stationary turn mix:
- cold: the mean prompt, 3072 tokens at 8 turns and 4096 at 16;
- warm: the mean uncached prompt, 496 at 8 turns and 376 at 16 (`k2.cold_tokens`, `k2.warm_tokens`; L1's session shape from the configs).

| cost model | warm₁₆/warm₈ | floor₁₆/floor₈ (open-loop mix) | R | R with model F's closed-loop floors (onsets 2.0 / 1.5) |
|---|---|---|---|---|
| proportional (a = 0) | 1.319 | 0.750 | 1.758 | **1.709** |
| fixed (0.180 s + 0.135 ms/token) | 1.070 | 0.811 | 1.319 | **1.304** |

- **The fixed model is REG-8's two capacities rewritten:** cost(cold mix) = 1/1.681 and cost(warm mix) = 1/4.047 (`k2.calibrate_fixed`; these are the M5 constants). It is the primary prediction: R = 1.30.
- **Model F's closed-loop floors** (`e1.replay_rows` on E1's and E2's cache-off configs at μ = 1.681): 1.744 and 1.431 (fixed), or 1.771 and 1.367 (proportional). They lower R by 1–3 %, because the closed-loop tilt lifts the 16-turn floor more.
- **Overload range:** E2's off grid puts its saturated rows at ρ ≈ 1.1–2.3 against its own floor, close to E1's 1.15–2.3, so the floors are read over similar overloads. The table `by_onset` gives each floor at every onset.
- **Blind spot:** neither model has a KV pool. At equal session counts, the live context of a 16-turn session is about a third larger. DERIVED: sessions in service ≈ λ × (gap + latency) ≈ 17 at λ = 3.2, holding ≈ 17 × 4224 ≈ 72k of the 96,656-token pool at 16 turns, against ≈ 17 × 3200 ≈ 54k at 8. Idle prefixes in the turn gaps are evicted first, so the 16-turn warm capacity may lose more than either model says.
- **P(BELIEF):** "widens" ≈ 0.55, "unresolved" ≈ 0.2, "does_not_widen" ≈ 0.25.

### Not blind
REG-13's 2.4 and REG-8's 1.681 and 4.047 are seen and are inputs. E1's floor and both E2 sweeps are unseen.

### Decision that changes (rule A1)
The 8–12 GPU h 16-turn shock matrix runs only on "widens". "does_not_widen" ends K2's range half at about 6 GPU h (E1 + E2). The 4-turn point is considered only after a 16-turn pass.

### Cost
E0 costs 0 GPU h. E2 is 11 runs × about 1260 s ≈ 3.9 GPU h, needs its own approval, and runs after E1.

### Code and tests (uncommitted at drafting)
- `analysis/k2.py`: `shape`, `cold_tokens`, `warm_tokens`, `token_gap`, `calibrate_fixed`, `predict`, `gate_factor`, `gate`, `measured_R`, `closed_loop_floors`, `observed`.
- `tests/test_k2.py`, 7 tests:
  - the token gaps 3.48, 6.19, 10.89;
  - L1's mean tokens;
  - the fixed model reproduces REG-8 and M5's constants;
  - R at 16 turns;
  - the gate factor and labels;
  - the E2 configs;
  - closed-loop floors lower R.
- `configs/sweep_l1t16pl350cl_pc_on.yaml`, `configs/sweep_l1t16pl350cl_pc_off.yaml`.
