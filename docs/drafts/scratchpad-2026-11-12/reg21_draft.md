## 2026-11-12 · [REG] REG-21 (K3, step B, draft): model F against the closed-loop stuck runs already made (served-turn mix primary, floor-free; sessions per arrival from the mix and, weakly, from the open-loop floor) and a blind prediction of E1's closed-loop floor from the mix (0 GPU h)
- **Owner (2026-11-12):** chose "Register now, mix primary" for step B (`docs/experiment-plan.md`, revised Stage 2, step B), after the agent showed that the session completion rate separates model F from the quasi-static reading only with a closed-loop floor (decisions.md 2026-11-12 [CORR], model F moved into `analysis/modelf.py`). 0 GPU h.
- **Claim tested:** K3 (`docs/claims.md`): the published models describe this setup's stuck state within a tolerance fixed before the comparison is computed. Model F (Valse and Jannesari, arXiv 2611.08902 §3; BELIEF as to the model, open-questions A16): a FIFO server on which every turn misses and each session rejoins the queue tail after each turn; in the long-run trapped regime with a fixed turn count T = 8, the served-turn mix is ν_k ∝ z^-k, sessions complete per session arrived at z^-T, and z solves ρ Σ_k w_k z^-k = 1 with ρ = λ / μ_off and w_k ∝ the turn cost.
- **Not blind, said plainly:** every run below has been reported, and parts of the mix have been seen: first-turn shares of completions were reported for REG-11 (0.155, 0.179, 0.148 per span), REG-14 (0.14–0.16) and REG-16's cold windows (0.149–0.156) (decisions.md [RESULT]s), and the agent saw end-window first-turn shares of six runs (0.125–0.160; REG-17, REG-18's four burst runs and REG-10) and sessions in service (12–14 before the burst, 149–226 in the end window, REG-17/18) in its REG-20 smoke check (this session's transcript only, not in the docs). Model F's first-turn share is 0.141, 0.151 and 0.160 at λ = 2.0, 2.2, 2.4 against the open-loop floor (DERIVED, `modelf`). So Q1–Q2 are a consistency check. Only the E1 prediction is blind: E1 has not run.

### Runs
- **Batch 1 (`k3.REG21["batch1"]`):** the 13 valid closed-loop L1 burst runs at 350 W before REG-19: REG-11 (λ = 2.4, seed 1), REG-12 (2.4, seeds 2–6), REG-14 (2.2, seed 2), REG-15 (2.2, seed 12, 4500 s watch), REG-17 (2.0, seed 2), REG-18 (2.0, seeds 3–6). A run enters only if `k1.cold_backlogged` (REG-20's readout, `docs/definitions.md`) holds in its own end window; the others are listed as left out.
- **Batch 2:** REG-19's five burst runs (not the drift rerun), reported separately, computed only after REG-19's [RESULT].
- No-burst runs that went cold (REG-12's seed-5 control, REG-16) are left out: their trap has no burst end to align W to.

### Window and readouts (`analysis/k3.py`, `k3.readouts`)
W = [burst end + 600 s, burst end + watch) on the run's clock: [1680, 2580) s for the 1500 s watches (900 s), [1680, 5580) s for REG-15. Arrivals continue through W in every run (the schedules end at the watch's end; REG-15's drop starts at 5580 s). Session requests only; burst requests are excluded and the number completing in W is reported.
- **Q1 (primary, judged):** k̄_obs, the mean turn index (1 to 8) of the session turns completed ok in W (by t_end). It is the efficient statistic for z under the model's mix. Prediction: k̄_F = Σ k z^-k / Σ z^-k at ρ_W = λ_W / 1.681, with λ_W = 8 × (sessions whose turn 0 is planned in W) / |W| and turn cost proportional to the prompt (4.312, 4.206, 4.108 at λ_W = 2.0, 2.2, 2.4). The no-tilt reading (stationary mix): 4.5.
- **Q2′ (judged):** d_obs = (sessions whose last turn completed in W) / (sessions whose turn 0 is planned in W), against ẑ^-8, where ẑ solves k̄(ẑ) = k̄_obs. Needs no floor and no cost model: it tests model F's tie between the mix and the session rate.
- **Q2 (judged, labelled weak):** d_obs against z(ρ_W)^-8 with μ_off = 1.681 (0.751, 0.638, 0.549 at 2.0, 2.2, 2.4), beside the quasi-static reading 1 / ρ_W (0.840, 0.764, 0.700). Weak: a floor 6 % higher moves model F's value about as far as the gap between the two (0.826 at a floor of 1.78, λ = 2.0; DERIVED, `modelf`). Recomputed once with E1's floor when E1 reports.
- **E1 prediction (blind, judged when E1 reports):** μ̂ = λ_W / ρ(ẑ), the cache-off floor model F infers from the mix, per run and pooled (mean over runs), for turn cost proportional to the prompt and for 0.18 s + 0.135 ms per token. E1 is the closed-loop cache-off sweep at L1 (`docs/experiment-plan.md` step E1, its own [REG]); its capacity is read by E1's registered rule.
- **Reported, never judged:** X / μ_off (session turns completed per second over 1.681; model 1.016, 1.025, 1.034; already seen in span form as 1.73–1.81 req/s); the served-prompt ratio (model 0.984–0.967; too weak to judge); uncached prompt tokens per second in W against the same rate on REG-8's five saturated cache-off sweeps (`k3.cacheoff_uncached`); Huang and Liu's rule (arXiv 2611.13412 §3: persistently degraded if every non-overlapping 5-minute window aligned to the trigger's end, from the first with token-weighted hit ratio < 0.5 to the end, has hit ratio < 0.5), on session turns by t_end through the end of the watch; preemptions per second in W (`vllm:num_preemptions_total`); k̄_obs in each half of W.

### Tolerances and decision (`k3.judge`; registered before Q1, Q2′, Q2 or μ̂ is computed on any real run)
Pooled = mean over the entered runs, equal weight per run. Per-run counts are reported as k of n with the one-sided 95 % Clopper–Pearson upper bound (rule H); runs at different λ are pooled under the stated assumption that model F's deviation does not depend on λ in 2.0–2.4.
| Quantity | inside | per run | other output |
|---|---|---|---|
| Q1 | pooled k̄_obs − k̄_F within ±0.08 | within ±0.15 | the stationary mix is excluded if pooled k̄_obs ≤ 4.40 |
| Q2′ | pooled d_obs − ẑ^-8 within ±0.06 | within ±0.15 | — |
| Q2 (weak) | pooled d_obs − z^-8 within ±0.05 | — | the quasi-static reading is excluded if pooled d_obs − 1/ρ_W is outside ±0.05 |
| E1 | E1's capacity within ±0.08 of pooled μ̂ for either cost model | — | `excludes_open_loop_floor`: neither interval contains 1.681, so E1 can tell model F's floor from "the closed-loop floor equals the open-loop one" |

Where the numbers come from (DERIVED, before any real run): per run W holds about 1500 completed turns (900 s at ≈ 1.7 req/s), so k̄_obs has a sampling SD of about 2.29 / √1500 ≈ 0.06 if turns were independent (they are not: per-run ±0.15 ≈ 2.5 SD); a floor up to 1.78 moves k̄_F by up to +0.06 at λ = 2.0, so the pooled ±0.08 covers that plus pooled sampling (≈ 0.02 over 13 runs); the stationary mix is 0.19 above k̄_F at 2.0. d_obs counts about 170 session completions per run (≈ 8 % sampling SD, so per run ±0.15); pooled ±0.06 and ±0.05. μ̂'s per-run SD is about 0.08 (from k̄'s 0.06 through dρ/dz); the cost model moves it by under 0.03 (`tests/test_k3.py`); ±0.08 is about 3 pooled SDs.

**K3 status after this:** for each of Q1, Q2′ and Q2, "inside" or "outside" its tolerance on batch 1, then batch 2 separately, each reported as a consistency check on seen runs; the E1 prediction is recorded in `docs/model.md`'s ledger and judged once when E1 reports. No result here supports K3 as a blind test.

### Prediction (BELIEF)
Batch 1 enters 11–13 runs. Q1 inside ≈ 0.55 and the stationary mix excluded ≈ 0.6 (the seen first-turn shares lie near model F at 2.2–2.4, two of the six end-window values near the stationary 0.125). Q2′ inside ≈ 0.4: the seen growth of sessions in service (≈ +140 to +210 over ≈ 1680 s at λ = 2.0) is faster than model F's ≈ +105 (DERIVED from d = 0.751: 0.25 × 0.249 × 1680; the in-service count is not the session count of the model, so this is a rough reading). Q2 inside ≈ 0.35. μ̂ pooled ≈ 1.70–1.80 (the seen request rates sit 1–5 % above the model's at 1.681); `excludes_open_loop_floor` ≈ 0.4.

### Alternatives to state with any result
1. **A transient, not the long-run regime:** W starts 600 s after the burst; the age mix left by the burst may not have converged. Separated by k̄_obs in the two halves of W and by batch 2's longer watch (2400 s windows).
2. **Not FIFO:** vLLM preempts running requests when the pool is full and recomputes them, and chunked prefill interleaves long and short prompts; either changes which turns finish first. Separated by preemptions per second in W and by whether the mix tilt is toward young turns at all.
3. **Turn-dependent service beyond the cost model:** longer prompts could take more than proportional time (attention is superlinear in length). Separated by the fixed-cost alternative (it moves μ̂ by < 0.03) and by E1's measured capacity.
4. **Burst residue:** burst requests completing in W shift X but not the session mix; counted and reported.

### Decision that changes (rule A1)
- Q1 outside with no tilt (k̄_obs near 4.5) → model F's mechanism does not describe this trap; its numbers are not used for K3's blind predictions (E1, K2), and the paper says so.
- Q1 and Q2′ inside → the E1 prediction is registered as K3's first blind test, at no extra cost (E1 runs in any case, decisions.md 2026-11-12 [DECISION], K2 staged).
- `excludes_open_loop_floor` false → E1 cannot separate model F's floor from the open-loop floor, and K3's blind test must come from elsewhere (REG-20's open arm or K2's 16-turn sweeps).

### Cost
0 GPU h. The table is `python -m analysis.k3 reg21` (batch 1), then `python -m analysis.k3 reg21 2` after REG-19's [RESULT]; each is computed once.

### Code and tests (uncommitted at drafting)
`analysis/modelf.py` (model F, 14 tests in `tests/test_modelf.py`), `analysis/k3.py` (this registration), `tests/test_k3.py` (18 tests on synthetic runs: model-F runs are read back to their z, floor and z^-8; the floor inferred from the mix follows the true floor; burst requests are excluded; Huang and Liu's rule on cold and warm runs; selection; the judge's labels; the counter's restart flag). No run folder was read by the code or tests while drafting; config files of the 13 runs were read to build W.
