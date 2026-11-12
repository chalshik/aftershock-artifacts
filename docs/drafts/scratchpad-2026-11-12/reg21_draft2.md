## 2026-11-12 · [REG] REG-21 (K3, step B, draft): model F replayed on each closed-loop stuck run's own schedule; judged by the all-miss capacity it implies (from the served-turn mix and from the throughput), whether one capacity fits every load and the open-loop floor, and, blind, E1's closed-loop cache-off floor (0 GPU h)
- **Owner (2026-11-12):** chose "Register now, mix primary" for step B, then, after the rule F review of the first draft, "Rebuild around per-run sim". 0 GPU h.
- **Claim tested:** K3 (`docs/claims.md`): the published models describe this setup's stuck state within a tolerance fixed before the comparison is computed. Model F (Valse and Jannesari, arXiv 2611.08902 §3; BELIEF as to the model, open-questions A16): one server, first come first served, every turn a miss; a closed-loop session's next turn joins the queue after its previous turn ends. One quantity describes the server: its all-miss capacity μ at the stationary turn mix.
- **Not blind, said plainly:** every run below has been reported. First-turn shares of completions were reported for REG-11 (0.155, 0.179, 0.148), REG-14 (0.14–0.16) and REG-16's cold windows (0.149–0.156); the agent saw end-window first-turn shares of six runs (0.125–0.160) and sessions in service (12–14 → 149–226) in its REG-20 smoke check (session transcript only); span completion rates of 1.73–1.81 req/s were reported for REG-14 and REG-17. Nobody has computed the capacities this registration judges, but the readouts they are fitted to are close to seen ones. J1–J3 are therefore consistency checks; only J4 (E1) is blind.

### Model F replayed on the run's schedule (`analysis/modelf_sim.py`)
The first draft compared each run with model F's long-run values; the review showed that a 900 s window ending 1500 s after the burst is not in the long run (with model F exactly true, a 6/s burst alone put every judged quantity outside) and that the 5 s turn gaps matter (review T1, T2). The replay removes both: it rebuilds the run's schedule from its config (`harness.workload.build_schedule`, the harness's own code and seeds; no run output read) and serves it through model F's server: one request at a time in release order; session starts and burst requests at their planned times; turn k released at the end of turn k − 1 plus the schedule's gap (`harness/loadgen.py:101`; exponential, mean 5 s, in all 13 configs, `configs/gap5_base.yaml:9`; review recommendation 2); cost (a + b L) / ((a + b · 3072) μ) seconds for L tokens to prefill; warm until the burst starts (later turns prefill only their new tokens), every request a miss from then on. Two cost models: proportional (a, b) = (0, 1), and 0.18 s + 0.135 ms per token (`k3.REG21["costs"]`). The burst (2.4 req/s for 180 s from 900 s in all 13 configs) is replayed as scheduled.

### Runs
- **Batch 1 (`k3.REG21["batch1"]`):** the 13 valid closed-loop L1 burst runs at 350 W before REG-19: REG-11 (λ = 2.4, seed 1), REG-12 (2.4, seeds 2–6), REG-14 (2.2, seed 2), REG-15 (2.2, seed 12, 4500 s watch), REG-17 (2.0, seed 2), REG-18 (2.0, seeds 3–6). A run enters if `k1.cold_backlogged` holds in its own end window; it enters J1–J3 only if it is all-miss in W: the prefix reuse of later turns in W (`k1.reuse`) ≤ 0.05 (review T6, recommendation 3). Runs left out are listed with the reason.
- **Batch 2:** REG-19's five burst runs, computed only after REG-19's [RESULT], reported separately.
- No-burst runs that went cold (REG-12's seed-5 control, REG-16) are left out: the replay needs a burst to start the miss phase.

### Readouts and fitted capacities (`k3.observed`, `k3.fit`)
W = [burst end + 600 s, burst end + watch) ([1680, 2580) s; [1680, 5580) s for REG-15). Observed in W, session requests only: k̄ (mean turn index 1–8 of the turns completed ok, by t_end), X (session turns completed ok per second), d (sessions whose last turn completed in W over sessions whose turn 0 is planned in W).
- **μ_k:** the μ at which the replay's k̄ in W equals the observed k̄. **μ_X:** the same for X. Searched on μ ∈ [1.30, 2.40] in steps of 0.01 (`k3.local_fit`): from the grid point whose replay value is nearest the observed one, a least-squares line through the replay values within ±0.10 req/s, solved for the observed value, re-centred once if the solution falls outside that stretch. A sign-change search is not used: the replay's k̄ jitters by 0.005–0.01 as μ changes (it is one discrete trajectory) and crosses a target several times (`tests/test_k3.py::test_local_fit_on_a_jittered_curve`). Each fit reports its status ("ok", "no_slope", "edge", "nan") and the line's residual SD.

### Judged (`k3.judge` per cost model, `k3.overall` across them; registered before any μ_k or μ_X is computed on a real run)
Each item is judged under both cost models; its label is "inside" if it is inside under at least one (as J4), "outside" if outside under every model with a label (`k3.overall`, `tests/test_k3.py::test_overall_label_is_inside_under_either_cost_model`). Both per-model labels are reported.
| # | Statement | inside if | why it can fail |
|---|---|---|---|
| J1 | one all-miss capacity fits every load | the medians of μ_k in the groups λ = 2.0 (5 runs), 2.2 (REG-14), 2.4 (6 runs) and REG-15 (its own group, 3900 s W) differ by at most 0.10 (max − min) | model F's μ is a property of the server; a trap whose mix depends on load beyond model F's dependence gives different μ_k by load (review T5) |
| J2 | the mix and the throughput imply the same capacity | the median over runs of μ_k − μ_X lies within ±0.08 | a server that is not first come first served, or whose turn costs differ from the model's, reproduces one readout at one μ and the other at another |
| J3 | that capacity is the open-loop cache-off floor | the median of μ_k − 1.681 lies within ±0.08 | under model F a saturated open-loop cache-off sweep serves the planned, stationary mix, so its throughput is μ itself (`tests/test_k3.py::test_open_loop_cache_off_replay_saturates_at_mu_and_closed_loop_above_it`: the replay of `configs/sweep_l1pl350_pc_off.yaml` at 2.0 and 3.0 req/s saturates at μ within 2 %); a closed-loop all-miss server that is faster or slower than the open-loop one fails it |
| J4 (blind) | E1's closed-loop cache-off floor | E1's registered floor statistic within ±0.08 of the replay of E1's own configs at the pooled μ_k, for either cost model (`k3.reg21_e1`, computed once from E1's configs before E1 runs and entered in `docs/model.md`'s ledger) | E1 has not run; `separates` reports whether the replay at μ_k and at 1.681 differ by more than 0.08, i.e. whether E1 can tell the two apart at all |

E1's statistic is, by default, `gate.cold_floor`'s mean saturated throughput (the rule that gave 1.681), read on the replay without its KV condition; if E1's [REG] registers another statistic, `k3.e1_statistic` is replaced before E1 runs, never after. This answers review T7: the prediction is made in E1's own units (a closed-loop sweep serves a mix tilted to young turns; the replay shows its saturated throughput above μ).

**Tolerance arithmetic (DERIVED from replays at known μ on the study's configs, before any real run):** μ_k reads back with errors −0.025 to +0.021 over four cases (tests at abs 0.03; one trajectory's k̄ departs from its smooth trend by 0.01–0.02), μ_X within ±0.006 (±0.015 with a 6/s burst) (`test_fit_reads_a_replay_back_to_its_floor`, `test_fit_with_a_larger_burst_still_reads_back`); fitting with the wrong cost model moves μ_k by < 0.05 (`test_wrong_cost_model_moves_the_fit_little`), which the either-model rule absorbs; a cold state that begins at the burst's end instead of its start moves μ_k by up to +0.03 and μ_X by < 0.005 (scratchpad probe on BURST20 and BURST24, cold from 900/990/1080 s: μ_k 1.677/1.706/1.730 and 1.693/1.696/1.715, μ_X 1.698–1.703; the agent's session only, not a committed test). The burst and the gaps are replayed, not approximated. ±0.08 for J2 and J3 is read-back (0.03) plus cold-onset bias (0.03) plus 0.02 for the run-to-run spread of a median over about 12 runs; this is a BELIEF about the real runs' spread, which no replay measures. ±0.10 for J1: two single-run groups (REG-14, REG-15) can differ by read-back 2 × 0.03 plus a cold-onset difference of 0.03.

### Reported, never judged
The first draft's quantities against the replay at 1.681 and at μ_k (k̄, X and d), and against model F's long-run values (`k3.long_run`); per-run μ_k and μ_X with statuses and residual SDs; uncached prompt tokens per second in W against REG-8's five saturated cache-off sweeps (`k3.cacheoff_uncached`); Huang and Liu's rule (arXiv 2611.13412 §3: persistently degraded if every non-overlapping 5-minute window aligned to the trigger's end, from the first with token-weighted hit ratio < 0.5 to the end, has hit ratio < 0.5); preemptions per second in W; k̄ in each half of W; burst requests completed in W; `gate.shock_size` (review recommendation 9).

### Prediction (BELIEF)
11–13 runs enter; all-miss in W for each ≈ 0.85 (REG-18's seeds 3 and 6 partly re-warmed in spans). J3 inside ≈ 0.6 (the seen first-turn shares sit near model F at 1.681; the seen span rates, 1.73–1.81, sit near the replay's X at μ ≈ 1.70–1.78). J2 inside ≈ 0.6. J1 inside ≈ 0.55 (the λ = 2.4 runs are at the closed-loop warm capacity, where REG-12's controls were not healthy). `separates` ≈ 0.3.

### Alternatives to state with any result
1. **Not first come first served:** vLLM preempts running requests when the pool is full and batches prefills (chunked prefill). Separated by J2 and by preemptions per second in W.
2. **Turn costs not proportional to the prompt:** attention grows faster than linearly with length. Bounded by the fixed-cost model; E1 measures the closed-loop all-miss throughput directly.
3. **Partial hits in W** (an effective floor, not the all-miss one; review T6): excluded by the precondition; uncached tokens per second against the cache-off sweeps reported.
4. **When the cache went cold:** the replay turns cold at the burst's start; bounded at +0.03 on μ_k.

### Decision that changes (rule A1)
- **J1 or J2 outside:** no single all-miss capacity describes the trap, so model F's structure does not transfer to this setup; K3 reports it, and model F is not used for K2's or K4's predictions.
- **J3 outside:** the trap's capacity is not the open-loop floor. E1 then decides between "the closed-loop all-miss server runs at a different rate" (E1 near the replay at μ_k; K2's gate must use E1's floor, not 1.681) and "model F misdescribes the trap" (E1 near the replay at 1.681). In both cases the paper's statement that the stuck state completes "near the cache-off floor" is reworded.
- **All inside:** model F is consistent with the stuck runs on these readouts, and E1 is K3's first blind test at no extra GPU cost (E1 runs in any case; decisions.md 2026-11-12 [DECISION], K2 staged), unless `separates` is false, in which case E1 cannot test it and K3's blind test must come from REG-20's open arm or K2's 16-turn sweeps.

### Cost
0 GPU h; `python -m analysis.k3 reg21` (batch 1, about 2 minutes), then `python -m analysis.k3 reg21 2` after REG-19's [RESULT]; each computed once.

### Code and tests (uncommitted at drafting)
`analysis/modelf.py` and `tests/test_modelf.py` (model F's long-run values, 14 tests); `analysis/modelf_sim.py` (the replay); `analysis/k3.py` (this registration); `tests/test_k3.py` (30 tests: the replay serves each request once, one at a time, in release order; closed-loop release equals the previous end plus the schedule gap; warm then all-miss costs; caching off misses from the start; replays at known μ read back through `fit` (1.681, 1.78 at λ = 2.0; 1.70 at 2.4; a 6/s burst; the wrong cost model); partial hits fail the precondition; the window values differ from the long-run ones; the open-loop cache-off replay saturates at μ and the closed-loop one above it; E1's prediction and hit; the judge's labels, groups and lists; the either-model rule; `local_fit` on a jittered curve). No run folder was read by the code or tests while drafting; the 13 runs' config files were read to build W.

### Adversarial review, round 1 (separate subagent; it saw the first draft, its code and the code it calls; no runs, no docs). Verbatim:
**Rule F review of the REG-21 draft (K3 step B)**

I read only the files in the brief and opened nothing under runs/, docs/ or configs/. The 32 tests pass. To test the readouts I wrote a model-F simulator in the scratchpad, `sim/sim.py` and `sim/sim2.py`. It runs one FIFO server where every turn misses after the burst starts (warm service before it), closed-loop turns, a burst at 900–1080 s, the 1500 s watch, and the k3 readouts. It gives 40 seeds per case.
- PROBE(/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/fdf13821-770b-43f6-866b-c82b3bbdc140/scratchpad/sim/sim.py), PROBE(.../sim/sim2.py)
- These are synthetic numbers only, with a sequential server, not vLLM's batched one.

**1. Cases where the verdict is wrong**

- **T1. Model F is exactly true, the verdict says "outside" (the burst sets the result).** Every judged prediction is the long-run, self-similar value (k3.py:172-174). W ends 1500 s after the burst. That is about one sojourn: a session takes about 8 cycles of about 120 s each. The turns completed in W belong to sessions that started around the burst. In the simulator, model F holds by construction, at λ = 2.0:
  - burst of 3/s: Q2′ +0.038, d_obs 0.789 against 0.751.
  - burst of 6/s: Q1 −0.126, Q2′ −0.165, Q2 −0.286, μ̂ 1.51 against a true 1.681. All three are outside.
  - burst of 1/s, or a 4500 s watch: everything is within 0.01.
  So the result depends on burst size and on how long after the burst W ends, not only on model F. REG-15's 3900 s W and the 900 s Ws estimate different quantities, and they are pooled with equal weight.
- **T2. Model F's mechanism is true, the verdict says "outside" (turn gap).** Model F has the session rejoin the queue at once. The harness releases the next turn at the previous end plus the planned gap (loadgen.py:100-101). In the simulator:
  - 30 s exponential gap: Q2′ −0.061 at 2.0 and −0.117 at 2.4, both outside. μ̂ is 1.750 and 1.814, so `excludes_open_loop_floor` comes out true and E1 "misses" even though every turn misses.
  - 10 s gap: μ̂ +0.04.
  I did not read `turn_gap_s` in the configs. This needs checking.
- **T3. Model F is wrong, the verdict says "inside" (Q2′ is pure queue kinematics).** I made the server not all-miss: μ_true = 2.0 at λ = 2.4. Q2′ came out +0.031, inside. Q2′ checks that turns rejoining the back of a growing queue give a mix tilted to young turns and d = z^-8. That holds for any overloaded closed-loop queue, whatever the cache is doing. Separately, μ_true = 1.78 at λ = 2.0 gives Q1 +0.04, inside, so Q1 cannot tell the open-loop floor from a floor 6% higher.
- **T4. μ̂ pooling.** k3.py:181 sets μ̂ to NaN when k̄_obs ≥ 4.5, and `_pool` (k3.py:212) drops it without comment. Near ρ = 1, μ̂ approaches λ_W. So the runs with the weakest tilt are either dropped (pooled μ̂ biased down) or dominate the mean.
- **T5. Pooling across λ.** The label is the pooled mean only (k3.py:236-239). The per-run k of n is reported but does not enter the label. Errors of opposite sign at 2.4 (six runs, near the closed-loop warm capacity of about 2.4, where REG-12's seed-5 control went cold with no burst) and at 2.0 can cancel.
- **T6. Selection and the all-miss premise.** `cold_backlogged` asks only that reuse in the end window be at most baseline − 0.06 (k1.py:85), not that it be near zero. The end window overlaps W. So entered runs can still have partial hits. μ̂ then estimates an effective floor, not the cache-off capacity E1 measures.
- **T7. E1's units.** μ_off is defined at the stationary turn mix (modelf.py:15-16). A saturated closed-loop cache-off sweep serves a mix tilted to young turns, which lifts req/s by Γ ≈ 1.6–3.4%. That uses up to 0.06 of the 0.08 tolerance unless E1's capacity rule corrects for it.
- **Tolerance arithmetic.**
  - The pooled ±0.08 for Q1 allows for the floor (0.06) and for sampling, but not for burst-size or gap bias (T1, T2).
  - In the simulator the per-run SD of d_obs is 0.086–0.096, about 12%, against the draft's 8%.
  - The SD of μ̂ (0.05–0.10) matches the draft.
  - k̄_obs tracks λ_W: the SD of k̄_obs − k̄_F is 0.044, smaller than either alone. So using λ_W helps.
- **Checked, no defect.** Burst identification: a session's turn 3 has 2944 tokens but turn ≠ 0, so it is not flagged as a burst request. Counting by t_end does not censor W. λ_W counts open-loop turn-0 starts correctly.

**2. Strongest alternative explanation**

The trap could be any capacity deficit with closed-loop turns rejoining the queue (partial hits, overload at λ = 2.4, preemption churn), with service at an effective μ somewhere between μ_off and the warm capacity. That gives model-F-like numbers for Q1 (within about 6% of the floor) and Q2′ (for any μ), as T3 shows. Only the floor-anchored quantities separate it:
- reuse or uncached tokens per second in W, compared with the cache-off sweeps;
- X/μ_off against Γ;
- Q2, and E1.

All four are reported-only, labelled weak, or still to come.

**3. Can any outcome change a decision?**

- **Q1 cannot fail where it matters.** The first-turn shares already seen (0.125–0.179) place k̄ at about 4.1–4.5 under the geometric mix, and the ±0.08 was set knowing this. So "outside with no tilt" is all but ruled out already. An "outside" from T1 or T2 would not be a failure of the mechanism. No decision changes.
- **Q2′ is unseen, but it does not test the mechanism (T3).** It does respond to burst size and gap (T1, T2). Also, μ̂ is computed and recorded whether or not Q1 and Q2′ pass, so the "inside → register the blind test" branch changes only a label.
- **Q2** is weak by the draft's own account. It cannot change a decision.
- **E1 is the only quantity that can change a decision**, and as specified a miss is confounded with gap, transient and floor-definition effects. A hit can come from the gap bias by coincidence: the simulated 30 s gap puts μ̂ at 1.75–1.81, which is exactly the predicted 1.70–1.80.

**4. Recommendations**

1. **Simulate each run instead of using long-run values.** Write a model-F simulator for each run (0 GPU h): that run's own schedule, burst requests and turn gaps, every turn missing, service proportional to the prompt and calibrated to μ_off. Judge Q1, Q2′ and μ̂ against the values it gives in W, with tolerances taken from its spread over seeds.
2. **Put the turn gap into model F or the simulator,** state `turn_gap_s` in the [REG], and report how much it moves μ̂.
3. **Register an all-miss precondition in W:** reuse at most a fixed value, or uncached tokens per second within x% of the cache-off sweeps. Runs that fail it are reported, not judged. Otherwise call μ̂ an "effective floor".
4. **Judge per λ, with REG-15 kept separate.** Either require every λ group to be inside, or write down how the per-run k of n enters the label (k3.py:234-245).
5. **Fix μ̂ pooling.** Compute μ̂ from the pooled k̄ per λ, or use the median. Report runs with k̄_obs ≥ 4.5 as μ̂ ≥ λ_W rather than dropping them (k3.py:181, 212).
6. **Fix E1's capacity rule to the stationary turn mix,** or divide out Γ, before E1 is registered.
7. **Reclassify Q1 as reported** (its main input has been seen) and Q2 as reported. Say in the [REG] that Q2′ tests queue kinematics, not the cache mechanism.
8. **Add tests where the code meets runs that break model F's assumptions:** a large burst, a gap > 0, a server that is not all-miss. `trapped_run` (test_k3.py:16-53) lays completions down from model F's own formula, so the current tests cannot catch a misspecified model.
9. **Report burst size per run** (`gate.shock_size`) next to every row; T1's bias depends on it.

### Changed because of round 1
1–2 (simulate each run; gaps): the replay on each run's own schedule, burst and gaps replaces the long-run values; judged items are capacities, not mixes. 3 (all-miss precondition): adopted (reuse ≤ 0.05 in W). 4 (per-λ judging, REG-15 apart): J1 is judged by λ group, REG-15 its own group. 5 (μ̂ pooling): μ̂ is gone; μ_k and μ_X are pooled by median, and unfitted runs are listed with their fit status, not dropped. 6 (E1's units): the E1 prediction is the replay of E1's own configs read by E1's statistic, so the tilt Γ is in the prediction rather than divided out. 7 (reclassify Q1, Q2; Q2′ is kinematics): Q1, Q2′ and Q2 are reported only. 8 (tests where the model is wrong): partial hits, a larger burst, the wrong cost model, a late cold onset (in the tolerance arithmetic), and a jittered curve. 9 (burst size): `gate.shock_size` reported per run.
