## 2026-11-12 · [REG] REG-20 (K1, draft): REG-19's burst runs with open-loop turns on the same seeds, judged against REG-19's closed-loop burst runs by one readout defined alike in both arms; a second open-loop load at the same share of the warm capacity, run only if the first arm has no cold run (GPU, ≈ 8.6–9.9 h expected)

- **Claim tested:** K1 (`docs/claims.md`): with open-loop turns a session's next turn arrives while its previous turn still runs, so its prefix is held and cannot be evicted, and the stuck state does not hold; with closed-loop turns it can. Premise stated by Lu et al. (§9) and Huang and Liu (§2, §7), tested by neither (BELIEF, open-questions A16).
- **Why this design and not the plan's step C (2026-11-12):** step C compared C1's strict per-seed pass rate between arms. REG-18 passed that test in 1 of 4 seeds; at 2 of 5 closed passes against 0 of 5 open the one-sided Fisher p is 0.222, at 3 of 5 0.083 (`stats.fisher_one_sided`, DERIVED), so the likeliest result was "nothing shown". The plan also named a headroom confound and did not address it: λ = 2.0 is 0.67 of the open-loop warm capacity (3.0, REG-8) and 0.83 of the closed-loop one (≈ 2.4, REG-13).

### Runs
- **Closed arm:** REG-19's burst runs (`*_burst_l1pl350cl_r2.0_w3000_s{15..19}`), as many as REG-19's futility stop leaves valid. Not rerun. Their end windows will have been seen in REG-19's [RESULT] before REG-20 is computed; the risk this test takes is on the open arm, which no one has seen.
- **Open arm A:** `configs/burst_l1pl350ol_r2.0_w3000_s{n}.yaml`, for each seed n that REG-19 ran. Each extends its REG-19 partner and sets `workload.sessions.closed_loop: false`, the only change; the planned schedule is identical (duration 4080 s kept, because `harness/workload.py` `_poisson_times` draws the Poisson count from rate × duration first; `tests/test_k1.py` checks schedule and config equality).
- **Open arm B (headroom check):** `configs/burst_l1pl350ol_r2.5_w3000_s{15,16,17}.yaml`: arm A's burst runs at λ = 2.5 (= 0.83 × 3.0), the burst unchanged. Margin over the open-loop cold floor 2.5 / 1.681 = 1.49 (DERIVED), so by M2 a stuck state is possible there. Runs only if `k1.b_may_start` (arm A final, no cold-backlogged open run).
- **Controls, conditional:** `configs/stage2_control_l1pl350ol_r{2.0,2.5}_w3000_s{n}.yaml` run only for an open-arm seed whose burst run is cold-backlogged, to separate overload of the open-loop warm state from a stuck state. A recovered open run carries its own pre-burst baseline and needs none.
- **Order:** arm A in REG-19's run order, then arm B seeds 15, 16, 17; a conditional control right after its burst partner is computed.
- **Standing instructions** as for REG-17 to REG-19: 350 W read before every launch; idle GPU ≤ 45 °C; clean tree at the registered commit; one rerun of a run that is invalid by the automatic checks; stop and ask on a client error, a burst that does not fill the pool, or an unexpected pre-launch check.

### Readout (analysis/k1.py, `cold_backlogged`)
In the burst run's end window [burst end + watch − end_s, burst end + watch) = [3480, 4080) s, against its own baseline [300, 900) s, by `load._level`:
- hit ≤ baseline hit − `stuck_hit_drop` (0.06; the `stuck` rule's hit part);
- mean waiting > baseline + `recovered_q_excess` (1.0; the negation of the `recovered` queue part);
- mean KV ≥ `gate.SURGE["kv_onset"]` (0.9; the tip level registered for REG-16/17).
All three thresholds are read from where they were registered before any K1 run; none is new. No latency enters, so the readout means the same in both arms (`docs/definitions.md`, percent fast: latency is measured from the planned time in one arm and from the release time in the other). A NaN input gives None (`unclear`); such a seed leaves n in both arms and is reported.

Mechanism readout: `gate.overlap_share` over [burst end, burst end + 600) s in each open run (REG-7's rule, threshold 0.5).

Open-arm labels (`k1.open_seed`): `recovered_open`; `pending_control` (cold, control not yet run); `stuck_open` (cold, its control not cold over the same windows); `overload_open` (both cold); `unclear`.

### Decision (`k1.k1_outcome`, on seeds with a valid run in both arms; rules in this order)
| Outcome | Rule | Decision that follows |
|---|---|---|
| `too_few` | fewer than 2 matched seeds | report; no K1 statement |
| `pending_controls` | an open cold run without its control | run the control, then compute again |
| `open_arm_overload` | an open run and its control both cold | report; the open-loop cell is not warm-healthy, K1 is not testable at it; owner decides |
| `closed_not_cold` | no closed run cold-backlogged | report; REG-19's cell does not hold the state; K1 is not testable at it |
| `refutes` | open cold in ≥ 3, or open cold ≥ closed cold | K1 is reported as refuted at this cell and leaves the paper's core claims |
| `supports` | one-sided Fisher p ≤ 0.05 (closed vs open counts), and overlap share > 0.5 in every recovered open run | K1 stated for this cell, with mechanism; arm B may start |
| `supports_no_mechanism` | p ≤ 0.05, overlap not shown | K1's outcome stated without the mechanism; the wording drops "held prefix" as shown |
| `inconclusive` | otherwise | report; owner decides between more seeds and dropping K1 as a core claim |

Arm B (`k1.b_outcome`): `headroom_weakened` if all 3 seeds are `recovered_open`; `headroom_open` if any is cold (K1's wording must then state the confound); `incomplete` otherwise.

Power (DERIVED, `stats.fisher_one_sided`): with 0 open cold, p = 0.222 / 0.083 / 0.024 / 0.004 at 2 / 3 / 4 / 5 of 5 closed; at n = 4 only 4 of 4 reaches p ≤ 0.05 (0.014); at n = 3 only 3 of 3 (0.050). REG-19's futility stop can leave n at 3 or 4.

### Prediction (BELIEF)
- Each closed burst run cold-backlogged ≈ 0.85 (REG-17 and REG-18: 5 of 5 burst runs at λ = 2.0 ended cold, full and backlogged; decisions.md 2026-11-11 [RESULT] REG-18).
- Each open run at λ = 2.0 cold-backlogged ≈ 0.10 (REG-10, open-loop at 2.4: drained within 393 s at c_b 3.40, `overlap_share` 0.608).
- Outcome at n = 5 (DERIVED from those two numbers under the rules, mechanism aside): `supports` or `supports_no_mechanism` ≈ 0.64, `inconclusive` ≈ 0.35, `refutes` ≈ 0.01. At n = 4: ≈ 0.34 / 0.65 / 0.01; at n = 3: ≈ 0.45 / 0.52 / 0.03.
- Overlap share > 0.5 in every recovered open run ≈ 0.6 (one prior value, 0.608 at λ = 2.4; at 2.0 the slowdown after the burst is smaller).
- Arm B, each seed cold ≈ 0.15; `headroom_weakened` ≈ 0.6.

### Alternatives to state with any result
1. **Headroom, not held prefixes:** the open arm recovers because λ = 2.0 is farther from its warm capacity. Arm B tests it at the same share; the overlap readout gives the mechanism.
2. **Different shock:** with open-loop turns the burst meets a different server state (more running requests, some prefixes held), so the post-burst backlog differs in size. Report shock size (`gate.shock_size`) per arm.
3. **Different load:** open-loop turns keep the offered load at λ during a slowdown, closed-loop turns lower it. An open arm that recovers does so under more load, which works against the hypothesis, not for it; an open arm that gets stuck could be overload, which the conditional control separates.
4. **REG-19's closed arm selected by its stop:** the futility stop fires on low passes, not on the K1 readout, but it decides n.

### Cost
Run length 4080 s; ≈ 1.07–1.23 GPU h per run with start-up (REG-19's estimate, 10.7–12.3 h for 10 runs). Arm A 5 runs ≈ 5.4–6.2 h; arm B 3 runs ≈ 3.2–3.7 h; ≈ 1.1 h per conditional control. Expected ≈ 8.6–9.9 h; at most ≈ 18 h if every open run needs its control.

### Code and configs
`analysis/k1.py` (new), `analysis/stats.py` (`fisher_one_sided`), `tests/test_k1.py` (36 tests: the readout, each label, each decision rule, Fisher values, and schedule and config identity of every open config with its partner), 16 configs `configs/*_l1pl350ol_*`. No harness, check, threshold or `uv.lock` change.
