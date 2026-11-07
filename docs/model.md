# Models and prediction ledger

Every model used to choose a run or read a result, with its equations, the evidence for each input, what it has predicted, and how that came out. Created 2026-11-04. A model that predicts is updated here before the run; the ledger row is closed by the `[RESULT]` entry.

## M1. Memory fit (F + W)

**Use:** where in λ two states could coexist, from memory alone. First written 2026-11-01 (decisions.md, "Tightening before the Stage 2 controls"); code since 2026-11-04.

- C: KV pool in tokens, from the run's `server.log` (96,656 default; 72,480 at `--kv-cache-memory-bytes 10687610880`).
- W(t) = Σ over active sessions of the latest planned prompt length; a session is active from its first to its last planned turn. `derived.working_set` (FILE(analysis/derived.py:63)).
- F = mean `kv_cache_usage_perc` × C over a window: the running batch's footprint (usage counts only blocks held by running requests, SOURCE(vLLM 0.32.0 v1/core/block_pool.py:get_usage)). `derived.kv_footprint` (FILE(analysis/derived.py:76)). F_warm from a cache-on sweep run, F_cold from the cache-off run at the same λ.
- **Warm state fits** if F_warm + W ≤ C. **Cold state holds** if F_cold + W > C. Two states are possible where both hold.

**Known flaws** (decisions.md 2026-11-01, 2026-11-02): F and W overlap, since running requests hold part of their own prefix; caching-off runs only approximate a cold cache and were still changing at 900 s; means hide spikes; the warm test is too strict (λ = 4 was healthy for 900 s with F_warm + W ≈ 1.32 C); the inputs come from 900 s sweeps whose load rises through the window (M4).

## M2. Completion-rate margin (bistability needs a capacity loss)

**Use:** whether a stuck state can exist at λ at all, independent of memory details. Feasibility gate (process.md §4). Item 25 of the 2026-11-04 audit. Assumption A was tested by REG-1 (inconclusive); the gate for setup L1 is REG-7 (decisions.md 2026-11-05). Corrected 2026-11-05 [CORR]: this line said "not yet registered or tested".

- The waiting line obeys dQ/dt = λ − c(s), where c(s) is the completion rate in server state s.
- A run can stay stuck after a trigger only if the post-trigger state s* has c(s*) < λ for as long as it lasts; otherwise the line drains, N and KV fall, eviction pressure goes, and S11 (self-refill, `docs/open-questions.md`) restores the cache.
- The warm state must keep up at the same λ: c_warm(λ) ≥ λ, shown by a `recovered` no-trigger control.
- **Two states at λ need** c(s*) < λ ≤ c_warm. As a capacity loss: s* must complete at least a share 1 − λ / c_max less than the best the server can do.

**Inputs, default pool, 20 s gaps** (all `load.summarize` `throughput`, completions/s in the measured window; every input below was measured at a 420 W power limit, so none carries over to setup L1 at 350 W, REG-8):

| State | λ | c (req/s) | Evidence |
|---|---|---|---|
| Cache on, best observed | 6 | 4.735 | RUN(20261030-143358_sweep_pc_on_r6, load.summarize) |
| Cache on | 5 | 4.723 | RUN(20261030-141658_sweep_pc_on_r5, load.summarize) |
| Cache on, deepest valid overload | 10 | 4.185 | RUN(20261030-151441_sweep_pc_on_r10, load.summarize) |
| Cache off | 4 / 5 / 6 / 8 | 3.453 / 3.511 / 3.521 / 3.533 | RUN(20261030-163358_sweep_pc_off_r4 … 20261030-173356_sweep_pc_off_r8, load.summarize) |
| Highest healthy test load | 3.5 | control `recovered` | RUN(20261101-190602_stage2_control_cap_r3.5, load.verdict) |

- DERIVED: capacity loss needed for two states at λ = 3.5 is 1 − 3.5 / 4.735 = 0.261. The loss observed from λ = 6 to λ = 10, cache on, is 1 − 4.185 / 4.735 = 0.116.
- **Assumption A** (BELIEF, untested): no post-trigger state completes less than the λ = 10 overload state. Under A, c(s*) ≥ 4.185 > 3.5, so no stuck state is possible at any healthy test load of this setup, and the 12 default-pool shock runs at λ = 3 and 3.5 were bound to recover. The other setups need their own inputs (below).
- **Weaker floor** (BELIEF): a state with some cache hits completes no less than the cache-off saturation, about 3.5 req/s. Under this floor alone, λ = 3 cannot be stuck; λ = 3.5 is at the edge.
- **Per setup:** 72,480-token pool: cache on at λ = 5 completes 4.567 (RUN(20261102-194816_sweep_kv72k_pc_on_r5, load.summarize)), cache off at λ = 4 3.449 (RUN(20261102-214207_sweep_kv72k_pc_off_r4, load.summarize)); no deep-overload run, so c(s*) has no measured floor. 5 s gaps: cache on keeps up to λ = 7 (7.185, RUN(20261103-132357_sweep_gap5_pc_on_r7, load.summarize)) and cache off was not swept past 3.5, so neither bound is measured.
- **Test of A:** REG-1 (2026-11-04) found no span that was backlogged, cold and burst-free at once, so A is **untested**. Wipes built no backlog; bursts were cold and backlogged only while their own requests still completed. Testing A needs a run that holds a cold backlog for minutes (GPU, owner).

- **Setup L1 at 350 W (REG-8, decisions.md 2026-11-07 [RESULT]):** μ_warm 3.0, μ_off 1.0, cold floor μ_sat,off 1.681 (RUN(the 13 REG-8 runs, gate.reg8_zone)). Best cache-on completion rate 4.047 at λ = 4.5 (RUN(20261107-113511_sweep_l1pl350_pc_on_r4.5, load.summarize)). DERIVED capacity loss of the cold state: 1 − 1.681 / 4.047 = 0.585, against 0.116 at the default pool. No λ_test under REG-7's margins (0.8 μ_warm, 1.3 μ_sat,off); the warm side is limited by TTFT (pooled percent fast 0.990 at λ = 3, 0.716 at 3.5).
- **Floor at the default pool (decisions.md 2026-11-04, REG-5 not computed):** DERIVED cache-off saturation ≈ 3.50 req/s. The λ = 3 shock runs lie about 14 % below it; the λ = 3.5 runs lie at it. On B (untested in post-shock states) and on the 900 s saturation being sustained (REG-6), the λ = 3 runs could not have stayed stuck, and the setup has no healthy load clearly above its floor. Nothing follows for λ = 3.5, or for the 72k and 5 s-gap setups.

## M3. Self-refill (why a single wipe may not hold)

**Use:** reading the wipe results. BELIEF built on SOURCE facts; decisions.md 2026-11-04 (5).
- A turn that misses re-caches its own prompt as it is prefilled (S11). So a wipe costs each active session about one turn of hits.
- For the loss to persist, a session's blocks must be evicted within one turn gap, before its next turn; eviction is roughly LRU by release time, tail blocks first (S9).
- Prediction it makes, not yet stated as a number: the hit deficit after a wipe decays within about one session length (≈ 7 turn gaps), unless the free queue turns over faster than a turn gap.

## M4. Capacity measurement (what μ means here)

**Use:** placing test loads. Rule: decisions.md 2026-10-30, `load.capacity`.
- μ is the highest swept λ whose 900 s run keeps up by the rule. It is a property of one arrival realization: every sweep used seed 0, and the planned request rate rises through the measured window in every sweep, from 0.67–0.97 λ in 240–390 s to 1.05–1.34 λ in 750–900 s (`schedule.parquet` of every sweep; 2026-11-04 audit). For λ = 3: 2.49 req/s in 240–390 s and 3.52 req/s in 750–900 s.
- So μ_off = 2 may be low: the cache-off λ = 3 run failed on queue slope (0.0130 against 0.01, RUN(20261030-161749_sweep_pc_off_r3, load.summarize)) while its last 150 s carried 3.52 req/s of planned load, against a cache-off saturation of about 3.5 (above). BELIEF until tested: open-questions.md A1.

## Prediction ledger

| # | Date | Model | Prediction (registered before the run) | Observed | Hit / miss | Runs |
|---|---|---|---|---|---|---|
| 1 | 2026-11-01 | M1 | Default pool, λ = 3: warm fits ((W+F_warm)/C 0.88–0.91) and cold holds (1.16–1.52), so two states are possible | Stuck in 0 of 3 (wipe) and 0 of 3 (burst) | Miss | RUN(20261102-072216_wipe_preempt_r3_s1, load.verdict), RUN(20261102-053935_wipe_preempt_r3_s2, load.verdict), RUN(20261102-100744_wipe_preempt_r3_s3, load.verdict); bursts `20261102-131353_burst_r3_s1` … `20261102-144008_burst_r3_s3` |
| 2 | 2026-11-01 | M1 | Default pool, λ = 2: cold cannot hold ((W+F_cold)/C 0.60–0.63), so recovers | Not run (matrix stopped) | Untested | — |
| 3 | 2026-11-02 | M1 | 72k pool, λ = 3: warm does not fit (W + F_warm ≈ 86k > 72,480) | Healthy: keeps up by the capacity rule (throughput 3.000, slope 0.000); control `recovered` | Miss | RUN(20261102-190030_sweep_kv72k_pc_on_r3, load.summarize), RUN(20261102-221019_stage2_control_kv72k_r3, load.verdict) |
| 4 | 2026-11-02 | M1 | 72k pool: danger zone around λ = 2.5 | μ_off = 2.5, the zone's low edge | Miss | RUN(20261102-205336_sweep_kv72k_pc_off_r2.5, load.summarize) |
| 5 | 2026-11-02 | none | Bursts at λ = 3, 3.5: no numeric prediction was registered | Stuck in 0 of 6 | — | `20261102-131353_burst_r3_s1` … `20261102-164933_burst_r3.5_s3` |
| 6 | 2026-11-03 | (ramp registration) | "A gap at 300 s only … is expected" (backlog from the peak) | No gap at either dwell at λ ≤ 3.5; λ = 4.5 down at 300 s had percent fast 0.526 but no hit drop | Miss (no lag gap either) | RUN(20261103-043121_ramp_d300, load.ramp_table), RUN(20261103-053730_ramp_d600, load.ramp_table) |
| 7 | 2026-11-03 | W at 5 s gaps (0.19 vs 0.77 of the pool, λ = 3) | Getting stuck is less likely at 5 s gaps | Stuck in 0 of 12 | Hit, but not discriminating: 20 s gaps also gave 0 of 18 | `20261103-161947_burst_gap5_r4.5_s1` … `20261104-000416_wipe_gap5_r3.5_s3` |
| 8 | 2026-11-03 | sweeps | 5 s gaps: recovery, because prefixes survived overload | Stuck in 0 of 12 | Hit | as row 7 |
| 9 | 2026-11-04 | M2 (REG-1) | ≤ 2 of 12 default-pool burst spans and 0 of 12 wipe spans qualify; outcome most likely inconclusive (≈ 0.6); qualifying c in 4.3–4.7 | 0 of 24 qualify (wipes never backlogged; burst spans never burst-free); inconclusive | Hit on qualification and outcome; c range not testable | RUN(the 30 REG-1 runs, margin.reg1_table) |
| 10 | 2026-11-04 | REG-2 (A3) | λ = 4 control: `arrival_driven` ≈ 0.5 (modal); 72k λ = 3.5: `too_few_episodes` ≈ 0.6 (modal), `arrival_driven` ≈ 0.25; `ao_like_cycle` ≤ 0.05 | λ = 4 `arrival_driven` (arrival share exactly at the 2/3 threshold); 72k `arrival_driven` | Hit (λ = 4); miss of the modal prediction (72k) | RUN(20261101-202808_stage2_control_cap_r4, mechanisms.reg2_table), RUN(20261102-225146_stage2_control_kv72k_r3.5, mechanisms.reg2_table) |
| 11 | 2026-11-05 | M2 (REG-7, setup L1) | μ_sat,off ∈ [1.4, 2.2] (point 1.7, DERIVED from 5.3k prefill tok/s ÷ 3070); μ_warm ∈ [3, 6] (point 4.5); λ_test exists p ≈ 0.7 (point 3.5); given G3: `pass` ≈ 0.3, `drains` ≈ 0.45, `control_not_healthy` ≈ 0.1, `inconclusive` ≈ 0.15 | G1 valid at λ = 2–5.5; G2 no valid run (heat), so the floor is unmeasured and REG-7's gate was not computed; superseded by REG-8 (row 12) | Untested | decisions.md 2026-11-06 [OPS] |
| 12 | 2026-11-06 | M2 (REG-8, setup L1 at 350 W) | Part a valid p ≈ 0.75, peak ≈ 74 °C; μ_sat,off ∈ [1.3, 2.1] (point 1.6), floor `ok` p ≈ 0.7; μ_warm ∈ [3, 5.5] (point 4.5); λ_test exists p ≈ 0.6 (point 3.5); given G3′ as row 11; overall `pass` ≈ 0.14. **Added to this ledger late** (2026-11-07 [CORR]); the numbers are REG-8's as committed in `3fa9563`, before any 350 W run | Part a valid, peak 74 °C; μ_sat,off = 1.681 (λ_sat 2.0, n = 5, `ok`); μ_warm 3.0; no λ_test (G3′ not run) | Hit: part a, floor range and status, μ_warm range (at its edge). Miss: μ_warm point (4.5), λ_test point (3.5); λ_test absent (p 0.4) | RUN(20261107-075951_sweep_l1pl350_pc_off_r1, checks.json); RUN(the seven 20261107 `sweep_l1pl350_pc_off` runs, gate.reg8_g1_may_start) |

**Record so far:** M1 is 0 for 3 on tested predictions (rows 1, 3, 4). It should not be used to choose loads again until it is revised and its revision predicts the existing runs it missed.
