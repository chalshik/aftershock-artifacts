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