## 2026-11-13 · [REG] REG-22 (C2, condition 4): is the stuck state a memory-limited loop and not just a queue? The registered levels at the end of the watch, and the loop's four links in every span after the burst's own requests have left; the plan's trace order is reported, not judged, because it was written for a wipe; batch 1, a retrospective reading on the 13 burst runs made before REG-19, batch 2 on REG-19's burst runs once REG-19 has reported (0 GPU h)

- **ID:** REG-22. An analysis of existing runs, 0 GPU h. Draft 2 (draft 1 is `docs/drafts/reg22_draft1.md`; it was not reviewed; what changed is listed at the end). Code: `analysis/c2.py` at the commit named at the end.
- **What this is, in one line:** a retrospective reading on runs that have all been reported (batch 1), and the same table once on runs nobody has read (batch 2). Batch 1 is not called a test below.
- **This registration covers computing and reporting only.** Every edit to `docs/claims.md`, `docs/paper/` or PROTOCOL, and the registration of D1 and D2, needs its own decision with its own reviews. The lines under "Decision under each outcome" are a ceiling on what may be said.
- **Question:** in the burst runs that the registered verdict calls `stuck`, is the KV pool full, is the running batch at least twice its baseline and below the 256 cap (the registered levels), and do the loop's links (cache lost, prompts recomputed, large batch, full pool) hold together in every span once no burst request is left in the system?
- **Claim tested:** C2 (`docs/claims.md`), its first test: "in stuck runs … condition 4 (mean KV ≥ 0.80, mean N ≥ 2 × baseline, N below the 256 cap)". PROTOCOL §3 condition 4 adds "and the traces follow the plan's order".
- **What this registration changes, and why it needs the delegate's decision.** The plan's order (`docs/experiment-plan.md`, "Showing the loop": the hit rate drops, recomputed prefill rises, the batch grows, KV fills, the hit rate stays low) describes a cache wipe, where the loss comes first. A burst of one-off prompts fills the pool itself: on a burst run the first events are the trigger's (batch and KV up), and the hit rate falls after them. Judging the literal order would fail every burst run for a reason that says nothing about the loop. So for burst runs condition 4's last clause is read as **`sustain`** below, and the onset times are **reported with the order found**. This is a reading of a PROTOCOL rule fixed before it is applied to any run. **It is a change to how a PROTOCOL rule is read, which CLAUDE.md C reserves for the owner; here it is the delegate's, and it is listed for the owner.** If this registration is approved, PROTOCOL §3 gets a dated note pointing here, as its own entry.

### Statistic (`analysis/c2.py`)
Baseline: the 600 s before the burst starts ([300, 900) s). End window: the last 600 s of the watch. Spans: the watch cut into 300 s spans from the burst's end.
- **levels** (`c2.levels`, the thresholds of decisions.md 2026-11-01): in the end window, mean KV ≥ 0.80, mean running batch N ≥ 2 × its baseline mean, and maximum N < 256.
- **A gauge value needs coverage** (`c2.gauge`): scrapes within 10 s of each end of its window and no gap above 10 s (`load._covered`); otherwise the value is missing and the run is `undefined`, never judged on the scrapes that happen to exist. The uncached rate raises if an ok session request has no first-token time or prompt length.
- **sustain** (`c2.sustain`): in **every** span that starts at or after the moment the last burst request ended (`c2.last_burst_end`), all four hold (`c2.links`):
  1. reuse of later turns (`k1.reuse`'s statistic: cached tokens over the previous prompt, by first token) ≤ baseline − 0.06 (the verdict's `stuck_hit_drop`, read from the run's config);
  2. session uncached prefill (prompt tokens not served from the cache, session requests only, per second, by first token) ≥ 2 × baseline;
  3. mean N ≥ 2 × baseline;
  4. mean KV ≥ 0.80.
  At least two such spans are needed. With fewer, or with a burst request that never ended, or with a missing value, the run is `undefined`.
- **Why 2 × for the uncached rate (fixed here, before any run is read):** DERIVED from the L1 schedule. Warm, a session of 8 turns prefills 2176 + 7 × 256 = 3968 tokens; cold, 24,576. At equal request rates the cold rate is 6.2 × the warm one (DERIVED: 24,576 / 3968); at the cold completion rates on record (1.73 to 1.81 req/s at λ = 2.0 and 2.2, RUN(20261110-182920_burst_l1pl350cl_r2.0_s2, gate.reg17_gate), RUN(20261110-063647_burst_l1pl350cl_r2.2_s2, gate.reg14_gate)) against 2.0 to 2.4 req/s offered it is about 4.5 to 5.6 × (DERIVED). With half of the sessions hitting, the ratio at equal request rates is (0.5 × 3968 + 0.5 × 24,576) / 3968 = 3.6; it falls to 2 when the share hitting reaches 0.81 (DERIVED: 24,576 − 20,608 h = 2 × 3968). So 2 × is passed by a cold server with a wide margin and failed only by a span in which about four fifths or more of the turns hit.

### Labels (`c2.condition4`)
`loop` (levels and sustain hold); `not_memory_limited` (the levels fail: by PROTOCOL "a backlog state, not this loop"); `not_sustained` (the levels hold, a link is missing in some span after the burst's requests left); `undefined`. Reported per run and as counts; k of n `loop` with its one-sided 95 % Clopper–Pearson upper bound per load (`stats.cp_upper`, rule H), never pooled across loads. Seeds 2–6 were run at both λ = 2.0 and 2.4 and seed 2 also at 2.2; this is stated, not used.

### Runs
- **Batch 1** (`c2.batch_runs(1)`, `c2.REG22["runs"]`): the 13 closed-loop L1 burst runs at 350 W made before REG-19 (REG-11, REG-12 seeds 2–6, REG-14, REG-15, REG-17, REG-18 seeds 3–6). The function raises unless all 13 are there and valid.
- **Batch 2** (`c2.batch_runs(2)`, which is `k3w.batch2_runs`): REG-19's burst runs, one valid run per seed, a prefix of seeds 15–19 and at least three. It raises before REG-19's result heading is in `docs/decisions.md`. The batches are reported apart and never pooled.
- A run is judged only if `load.verdict` gives `stuck`; the others are listed with their verdict.

### Not blind, said plainly
Every batch-1 run has been reported, and every threshold here was fixed knowing these numbers.
- **The levels are known for two runs and expected for the rest.** REG-15's last 1500 s: KV 0.949, N 30.3, which is 4.93 × its baseline of 6.1, maximum N 34 (RUN(20261110-085730_confirm_l1pl350cl_r2.2_s12, gate.reg15_table)). REG-17's end window: KV 0.949, 30.0 running (RUN(20261110-182920_burst_l1pl350cl_r2.0_s2, gate.reg17_gate)). The other [RESULT] entries report hit 0 and KV 0.95 at the end. So **the levels are expected to hold** (BELIEF, P ≈ 0.95 per stuck run), and their thresholds, registered on 2026-11-01 before any stuck run existed, are far from these values. Draft 1 cited a running batch of "about 65": that is the default pool (open-questions S7), not this setup.
- **Not computed by anyone:** the links per span, when the last burst request ended, the onsets, the eviction histograms.
- **Where an outcome is open:** REG-18's seeds 3 and 6 were reported as failing the cold side in one quiet span each (RUN(REG-18's burst runs, gate.reg18_table)), so `not_sustained` is possible for them; and a burst request that ends late leaves fewer than two spans in a 1500 s watch.
- **The only table on unread data is batch 2's.** For it to be read as such, this [REG] and its delegate [DECISION] are committed before REG-19's table is computed or read by anyone; otherwise batch 2 is labelled retrospective as well.

### Prediction (BELIEF)
Batch 1: 10–12 runs have the verdict `stuck`. Of these: `loop` in 8–11; `not_sustained` in 0–2 (REG-18 seeds 3 and 6 are the candidates); `not_memory_limited` in 0–1; `undefined` in 0–1 (a burst tail that leaves fewer than two spans). Onset order most often N, KV, reuse, uncached rate. Batch 2: of REG-19's burst runs with the verdict `stuck`, `loop` in at least four fifths (BELIEF).

### Decision under each outcome (rule A1)
- **`loop` in most stuck runs at a load (more than half):** it may be said that condition 4 is met at that load for the runs on record, k of n with its bound; C2's status may then read "condition 4 met in k of n stuck runs, read retrospectively; the loop-cut controls not yet run". D1 and D2 are proposed on the session population as planned.
- **`not_memory_limited` in most:** the stuck runs are backlog states, not this loop; by `docs/claims.md` that is against C2 for these cells. D1 and D2 are then not proposed as planned, and the paper would report the cold state as a queue without a memory limit. This is the outcome that would change a claim; it is not expected (above).
- **`not_sustained` in most:** the levels hold but the loop has gaps: the paper says the cold state is interrupted by re-warming spans, and the confirmation run's registration must read every span, not only the end window.
- **Mixed or `undefined`:** reported per run; C2 stays "untested" for that load.

### Reported, never judged
The onset time of each of the four signals after the burst's start (first 10 s grid time at which the trailing 60 s crosses: KV ≥ 0.9; N ≥ 2 × baseline; reuse ≤ baseline − 0.06 with at least 20 turns; session uncached rate ≥ 2 × baseline) and their order; every span's four values; when the last burst request ended.

### The eviction link read directly (reported, never judged; a prediction registered here)
The engine samples 1 % of its KV blocks and, when a sampled cached block is evicted, records the time since its last access, where an access is its allocation or a later cache hit (`vllm:kv_block_idle_before_evict_seconds`; SOURCE(vLLM 0.32.0 v1/core/kv_cache_metrics.py:KVCacheMetricsCollector.on_block_evicted)). No analysis has read these histograms. `c2.eviction_readout` gives, for the baseline and for the stretch after the last burst request, what the histogram gained: the bucket holding the median, the shares at or below 5 s and 30 s, and beside them the median time between the first tokens of a session's consecutive turns (`c2.turn_spacing`), which is how long a prefix must survive to be reused. Also the lifetime and reuse-gap histograms.
- **Prediction (DERIVED in `agent/theory/k1_held_prefix.md` from the pool size, the KV gauge and the allocation rate; BELIEF as a forecast):** warm, an idle prefix is overwritten about 64 s after its release, so the median time from last access to eviction falls in the (60, 120] s bucket, far above a turn spacing of about 7 s; in the stuck state it is overwritten about 1 s after its release, so the median is the time a request holds its blocks plus that, in the (10, 20] or (20, 30] s bucket, and below the turn spacing there (a residence of about 17 s, a 5 s gap and the wait in the line).
- **If it is wrong:** a stuck-state median above the turn spacing would mean prefixes outlive the gap and are still not reused, which the loop does not explain; a warm median below the turn spacing would contradict the warm hit rate of 0.84. Either is reported as against the loop's eviction link, and the paper's loop figure shows these histograms whatever they say.

### Alternatives to state with any result
1. **The preemption cycle of Ao et al.** A full pool with a large batch is also what their limit cycle shows. Preemptions per second in the end window against the same seed's control are the registered comparison (decisions.md 2026-11-01); it is computed in its own registration (the matched-control analysis), and its reading is quoted beside this table.
2. **Overload, not a loop.** At λ = 2.4 the closed-loop warm capacity is reached (REG-13), so there the levels can hold with no history dependence. Condition 4 does not separate these; conditions 2, 5 and 6 do.
3. **The thresholds meet the data where it is easiest.** KV ≥ 0.80 was set from a healthy sweep run's 0.82 (decisions.md 2026-11-01), long before any stuck run existed; 2 × the uncached rate is new and is justified above from the schedule alone.
4. **The burst's tail.** A burst request that ends late shortens the judged part of the watch; the number of judged spans is reported per run.

### Stopping rule
- Batch 1 is computed once, after this registration is approved: `uv run python -m analysis.c2 reg22`.
- Batch 2 is computed once, after REG-19's final [RESULT]: `uv run python -m analysis.c2 reg22 2`. The command raises before.
- Both run from committed code with `analysis/` and `tests/` clean and `uv run pytest` passing; the [RESULT] names the commit and lists the runs left out with their verdict.
- No second threshold, window or span length. An exception is fixed and logged as a [CORR] before the table is read. The labels are computed before any reported readout, and a readout that raises is kept as its message.

### Definitions (rule J)
With the registration, `docs/definitions.md` gains: the condition-4 levels (`c2.levels`), the loop's links and `sustain` (`c2.links`, `c2.sustain`), and the session uncached prefill rate (`c2.session_uncached_rate`).

### Cost
0 GPU h; about a minute of CPU.

### Code and tests
`analysis/c2.py` (`gauge`, `levels`, `links`, `sustain`, `onsets`, `histogram_delta`, `turn_spacing`, `eviction_readout`, `condition4`, `batch_runs`, `reg22_table`); `tests/test_c2.py`, 14 tests on hand-made runs: a cold, full, backlogged run is `loop`; a low KV, a small batch or a batch at the cap is `not_memory_limited`; a span in which the cache comes back is `not_sustained`; a burst still in the system or leaving too late is `undefined`; the onsets' order; missing metrics; the uncached rate leaves burst requests out; the table judges only stuck runs; a histogram's gain over a window, its median bucket and shares; the turn spacing; a gauge that does not cover its window gives `undefined`; an ok request the rate cannot place raises; a failing readout does not take the label with it; the table needs every registered run and gives k of n per load with its bound. No run folder was read while writing this draft or its code.

### Changed from draft 1 (lessons of REG-21's reviews, applied before any review of this one)
Gauge values need coverage; the uncached rate raises on a request it cannot place; batch 1 raises on a missing or invalid run; batch 2 is in the code and guarded as REG-21's; the labels come before the readouts and readout errors are contained; counts per load with their bound; "what was known" with sources, and the wrong "about 65" removed; the decision lines are a ceiling, and claims, paper, PROTOCOL and D1/D2 need their own decisions.
