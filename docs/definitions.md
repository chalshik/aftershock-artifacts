# Definitions

One entry per term: one text definition, its source, and the code that computes it. Created 2026-11-04 (decisions.md, same date).

- **Which text is given:** where files differ, the newer decisions.md entry rules (`PROTOCOL.md:3`). Older or other wordings are listed under "Other text", not deleted.
- **⚠ more than one computation:** the term is computed in more than one way, and reported numbers may come from either. **No single one has been chosen yet.**
- **Rule J (CLAUDE.md):** code must match the definition given here. Where it does not, the term is marked ⚠ and the choice between computations is the owner's; nothing here picks one.
- Line numbers are as of 2026-11-04. Code paths: `load` = `analysis/load.py`, `derived` = `analysis/derived.py`.

## Outcome and capacity

### percent fast ⚠ more than one computation
- **Text:** "a request is fast if its first token arrives within 1.0 s of its planned arrival and it finishes ok. Unfinished requests are misses." `docs/decisions.md:122`. It is counted by arrival time: "Each second, take the requests that **arrived** in that second and count how many met the limit." `docs/experiment-plan.md:115`.
- **Code:**
  - `load.percent_fast` (`load.py:76`): a share for each 1 s arrival bin.
  - `load._level` `"pf"` (`load.py:150`): one share pooled over every request arriving in [a, b). This one feeds `verdict` and `ramp_table`. It counts requests, not bins, and it includes burst requests.
  - **Closed-loop turns** (REG-11, decisions.md 2026-11-09 [REG]; `workload.sessions.closed_loop`): latency (`ttft`, `e2e` in `load.load_run`) is measured from the release time `t_released` instead of `t_planned`. Both computations above still bin by `t_planned`, so a turn released late, or never, counts in the window of its planned time (REG-11 review, T3). Open-loop runs are unchanged (`t_released` is None).
  - `gate.pf_by_sent` (added 2026-11-10 for REG-16, decisions.md [REG] REG-16): one share pooled over the requests **sent** in [a, b), by `t_sent`. Under closed loop a turn is served near its send time, up to 15 min after its planned time, so this computation lines pf up with the scrape-time hit rate. Requests never sent are left out (6.1 % of REG-15's requests; REG-16 review round 2, T3), which leans towards "fast" in a collapse; `gate.window_mix` reports them per window. Used only by REG-16's `cold_windows`, against a baseline pf from `_level`.
- **Other text:** `analysis/CLAUDE.md:4` ("percent fast per arrival second").

### goodput ⚠ two meanings
- **Text:** "Share of requests that met the speed limit (SLO); the goodput measure from Stage 1". `docs/experiment-plan.md:205`. In this repo it is a synonym of percent fast.
- **Other meaning:** completions per second, used outside this repo (the owner's paper notes; not checkable here, BELIEF). The C1 metric, percent fast or completions/s, is the owner's decision (`docs/claims.md`).
- **Code:** none of its own; see percent fast and throughput. **Decided 2026-11-12 (owner):** the paper states C1 in hit rate and percent fast, not completions/s (decisions.md 2026-11-12 [DECISION]). Still write "percent fast" or "completions/s", never "goodput".

### throughput (completion rate c)
- **Text:** "completions per second inside the measured window, the plan's definition". `docs/decisions.md:97`. Written c(s) in `docs/model.md` M2.
- **Code:** `load.summarize` `"throughput"` (`load.py:98`): ok requests whose `t_end` falls in [warm-up, end of arrivals), divided by that span.
- **Other text:** the step 4 sweep used an arrival-based count instead (`docs/decisions.md:88`, superseded).

### μ_warm
- **Text:** "μ is the highest swept λ whose run is valid, with throughput ≥ 0.95 λ and waiting-queue slope ≤ 0.01 req/s², both over the measured window", with prefix caching on. `docs/decisions.md:61`.
- **Code:** `load.capacity` (`load.py:243`), on `load.summarize` rows.
- **Reference for future sweeps (item 42, decisions.md 2026-11-04; code 2026-11-05):** a sweep whose config has a `capacity:` block with `against: planned_rate` is judged against `load.summarize` `planned_rate`, the requests planned in [warm-up, end of arrivals) per second, instead of λ. Read by `tables.capacity_rule` and `tables.sweep_capacity`. Every sweep up to 2026-11-04 has no such block and keeps the 2026-10-30 rule. With `monotone: true`, μ is the highest rate that passes along with every lower swept rate (`load.capacity(monotone=True)`). First used by `configs/l1_base.yaml` (REG-7). **[2026-11-05]** A swept rate with no valid run, after the reruns REG-7 allows, ends the chain like a failing one. The swept rates are the union of `sweep.rates` saved in the parent's runs (`load.capacity(swept_rates=...)` via `tables.sweep_capacity`; decisions.md 2026-11-05 [CORR] and [DECISION]).
- **Other text:** "Highest load the server keeps up with when the cache works" (`docs/experiment-plan.md:201`).

### μ_off
- **Text:** the same rule as μ_warm (`docs/decisions.md:61`), with prefix caching off.
- **Code:** `load.capacity` (`load.py:243`).
- **Other text:** "Highest load the server keeps up with when nothing comes from the cache" (`docs/experiment-plan.md:202`).

### danger zone
- **Text:** "Loads between μ\_off and μ\_warm: fine while the cache works, too much once it is lost". `docs/experiment-plan.md:203`.
- **Code:** none.
- **Other text:** the test loads are the subset "whose no-trigger control is `recovered`" (`PROTOCOL.md:61`).

## Timing windows

### τ (recovery time)
- **Text:** "time from the step until a sliding 180 s span, moved 60 s at a time, has hit rate within ±0.03 and TTFT p50 within ±0.02 s of the settled level. **τ is the larger of the up-step and down-step values.**" `docs/decisions.md:168`.
- **Code:** `load.settling_time` (`load.py:124`); settings under `tau:` in `configs/tau.yaml`.
- **Other text:** "how long the healthy server takes to settle after a normal load change that wipes nothing" (`docs/experiment-plan.md:223`).

### K
- **Text:** "watch window = max(1200 s, 5 τ), so K = 5". `docs/decisions.md:172`.
- **Code:** none. The result, `watch_s: 1500`, is written into `configs/stage2_base.yaml:13`.

### watch window
- **Text:** "Watch window = max(1200 s, 5 × 300 s) = **1500 s**" (`docs/decisions.md:192`). It is judged on "the last 600 s (`end`) against the 600 s before them (`previous`) and the baseline" (`docs/decisions.md:272`).
- **Code:** `load.verdict` (`load.py:197`): `t_end = trigger end + watch_s`; `end_s` is set in `configs/stage2_cap_base.yaml:8`.
- **Other text:** an `end_s` of 300 s in `configs/stage2_base.yaml:14`, superseded before any verdict. It is still inherited by `wipe_test_*.yaml` and `stage2_control.yaml`, none of which was judged.

### baseline window
- **Text:** "the baseline is the 600 s before the trigger *starts*". `docs/decisions.md:391`.
- **Code:** `load.verdict` (`load.py:197`).
- **Other text:** "the last 600 s before the wipe" (`docs/decisions.md:210`); the 600 s before the trigger's end (the error corrected at `:389`).

### trigger end ⚠ more than one computation (two copies of one rule)
- **Text:** no text definition. Closest: "The baseline ends where the trigger starts; the watch starts where it ends (a successful wipe, a burst, or control_t_s for a control...)" (`analysis/load.py:198-200`).
- **Code:**
  - `load.verdict` (`load.py:197`): a wipe ends at the `t_end` of the successful call in `trigger.jsonl`; a burst at `at_s + duration_s` (its planned arrivals end, not its backlog); a control at `control_t_s`.
  - `derived.trigger_times` (`derived.py:20`) is the same rule, copied so that `verdict` stays unchanged.

## Server metrics

### hit rate h ⚠ more than one computation
- **Text:** "Δ`vllm:prefix_cache_hits` ÷ Δ`vllm:prefix_cache_queries`". `docs/experiment-plan.md:125`.
- **Units (source):** tokens. Readmissions of preempted requests are excluded (`docs/open-questions.md`, S8).
- **Code:**
  - `load.rates` `hit_rate` (`load.py:66`): one ratio per scrape interval.
  - `load.summarize` `"hit_rate"` (`load.py:101`): the mean of the per-scrape ratios over the measured window.
  - `load._level` `"hit"` (`load.py:150`), `derived.hit_between` (`derived.py:13`) and `derived.thirds(how="counter")` (`derived.py:37`): the ratio of counter differences over the span. This feeds `verdict`. Since 2026-11-05, `hit_between` is also NaN on a counter decrease or no queries, like `_level` (decisions.md 2026-11-05 [CORR]).
  - `load.whole_run_hit_rate` (`load.py:108`): first scrape to last.
- **Undefined windows (REG-4, 2026-11-04):** `_level` gives NaN hit when the query counter does not rise, a cache counter goes down (restart), or the scrapes don't cover the window (`checks.max_scrape_gap_s`). Before REG-4 a window with no queries gave 0.0.
- **Different numbers for the same run:** e.g. the long run's last third, 0.6004 (mean of ratios) vs 0.6255 (counters), `docs/decisions.md:116`.

### KV usage
- **Text:** "usage is 1 − free blocks / total ... So usage counts blocks held by running requests, and saved prefixes with no running user count as free." `docs/decisions.md:244`. Source: `vllm/v1/core/block_pool.py` `get_usage`.
- **Code:** the gauge `vllm:kv_cache_usage_perc`, through `load.rates` (`load.py:70-72`); `load._level` `"kv"` (mean, `load.py:150`); `derived.kv_footprint` (`derived.py:76`).

### running batch N
- **Text:** "`vllm:num_requests_running` | How many requests share the GPU". `docs/experiment-plan.md:124`.
- **Code:** gauge; `load._level` `"n"` (mean, `load.py:150`).

### waiting Q
- **Text:** "`vllm:num_requests_waiting` | Whether requests pile up". `docs/experiment-plan.md:123`.
- **Queue slope, units:** a least-squares slope of a request count against time, so its unit is **req/s**. The docs write "req/s²" (`docs/decisions.md:21`, `:61` and later); the numbers and thresholds are unchanged, only the unit was misnamed (2026-11-04 audit).
- **Code:** gauge; `load._level` `"q"` (mean) and `"q_slope"` (least-squares slope, `load.py:150`); `load.summarize` `"q_mean"` and `"q_slope_per_s"` (`load.py:102-103`).

### preemption
- **Text:** "report preemptions per minute in the watch window, excluding the wipe's own, against the no-trigger control and the caching-off run at the same λ". `docs/decisions.md:247`. Counter: `vllm:num_preemptions` (`docs/experiment-plan.md:128`).
- **Code:** only the generic `load.rates` `num_preemptions_rate` (`load.py:63`). **No code for the registered comparison.**

### R (block idle time before eviction)
- **Text:** "`vllm:kv_block_idle_before_evict_seconds` | How long a cached prefix survives (R)". `docs/experiment-plan.md:129`. Recorded as a histogram, sampled (`--kv-cache-metrics`, `configs/base.yaml:17`).
- **Code:** **none.** `load.metrics_wide` drops the `_bucket` series, and nothing reads `_sum` or `_count`.

## Run verdicts

All five come from one rule, `docs/decisions.md:272-277`, restated at `PROTOCOL.md:24-28`. Code: `load.verdict` (`load.py:197-241`), with thresholds under `verdict:` in `configs/stage2_base.yaml:10-22` and `configs/stage2_cap_base.yaml:7-13`.

### bad_baseline
- **Text:** "baseline percent fast < 0.98." `docs/decisions.md:273`.
- **Code:** `load.verdict`, `min_baseline_pf`.

### recovered
- **Text:** "percent fast ≥ baseline − 0.02, hit rate ≥ baseline − 0.06, mean waiting ≤ baseline + 1." `docs/decisions.md:274`.
- **Code:** `load.verdict`.
- **Other text:** "Percent fast returns to its pre-trigger level" (`docs/experiment-plan.md:206`); `:259` (superseded).

### slow_drain
- **Text:** "any one sign of recovery: hit rate up ≥ 0.06, or percent fast up ≥ 0.05, or the line shrinking fast enough to empty within 3600 s." `docs/decisions.md:275`.
- **Code:** `load.verdict`, `climbing or draining`.
- **Other text:** `docs/experiment-plan.md:260` asks for all three signs together (superseded).

### stuck
- **Text:** "percent fast ≤ baseline − 0.10 and hit rate ≤ baseline − 0.06, with no sign of recovery." `docs/decisions.md:276`.
- **Code:** `load.verdict`.
- **Other text:** `docs/experiment-plan.md:261` requires a waiting line that is "Flat or growing". The code also accepts a line that shrinks too slowly to empty within 3600 s.

### unclear
- **Text:** "anything else." `docs/decisions.md:277`. "never rounded to another verdict" (`PROTOCOL.md:28`).
- **Also `unclear` (REG-4, 2026-11-04):** a branch that needs a value the window cannot give (NaN). `bad_baseline` and `recovered` are still decided when their own inputs exist; `slow_drain` and `stuck` are not reached if a sign of recovery can't be computed.
- **Code:** `load.verdict`.

### metastable failure
- **Text:** six conditions at one load: trigger over at the same load; control `recovered`; `stuck` in most seeds; a memory-limited loop; persistence over a 4500 s watch; two states at one load. `docs/decisions.md:281-287`, restated at `PROTOCOL.md:30-36`.
- **Code:** none. Only the per-run verdict is coded.
- **Other text:** three conditions (`docs/experiment-plan.md:265`, superseded); "Stuck ... The metastable failure" (`:207`).

## Derived quantities

Added 2026-11-04 with their code. Each is the reading that reproduces the published values (`docs/decisions.md`, 2026-11-04 "Derived figures moved into analysis/").
The original code, recovered verbatim from session transcripts, is in `analysis/recovered/` (INDEX.md there). Where its reading differs from the function below, the entry says so; the function stays the definition (decisions.md 2026-11-04, "[CORR] Derived-figure differences explained by the recovered originals").

### W (working set)
- **Text:** "sum of the latest prompt over active sessions from the schedule". `docs/decisions.md:248`.
- **Code:** `derived.working_set` (`derived.py:63`). A session counts as active from its first planned turn to its last.
- **Original reading:** the same rule sampled every 5 s from t = 600 s (every 10 s for the 5 s-gap comparison), against a 1 s grid here. This explains the ≤ 0.4 % differences in published W values.

### session median (prompt length)
- **Text:** the p50 of `prompt_len` over every scheduled **session** request of a run's whole schedule (`schedule.parquet`): warm-up included, sessions cut off at the end of arrivals included, burst requests excluded. Computed as pandas `median` (linear interpolation).
- **Value:** 1408 tokens (turn 3) in every schedule checked. It is a knife edge: the share of session requests at or below 1408 is 0.502–0.510 (decisions.md 2026-11-04 (7)), because truncated sessions add early turns. A full 8-turn session alone has median 1536, and over the measured window (t ≥ 240 s) the median is 1664 in 3 of 5 schedules.
- **Used by:** the burst size, "1408-token prompts (the session median)" (decisions.md 2026-11-02) and the `burst_*.yaml` comments ("median session prompt").
- **Code:** none; a one-line count on `schedule.parquet`.

### F (running-batch footprint)
- **Text:** no definition in the original entry (`docs/decisions.md:248-250`).
- **Code:** `derived.kv_footprint` (`derived.py:76`): mean KV usage × pool size.

### cached-share split
- **Text:** "Mean cached share of the prompt, all later turns vs only those starting after the previous turn had finished". `docs/decisions.md:293`.
- **Code:** `derived.cached_share_split` (`derived.py:93`). "Starting" here means **its first token** at or after the previous turn's end.

### overlap fraction
- **Text:** "Sent before the previous turn's first token". `docs/decisions.md:292`.
- **Code:** `derived.overlap_fraction` (`derived.py:103`).

### capacity loss
- **Text:** 1 − c(state) / c_max, the share of the best completion rate a state loses. `docs/model.md` M2.
- **Code:** none yet; DERIVED from `load.summarize` throughputs.

### post-trigger margin
- **Text:** completions − λ over a span after a trigger's end. Defined with its windows in the registration REG-1 (`docs/model.md` M2), **not yet computed**.
- **Code:** none yet; to be written only after REG-1 is approved.

## Feasibility gate for setup L1 (REG-7, decisions.md 2026-11-05)

### μ_sat,off (cold floor)
- **Text:** the mean `load.summarize` throughput of a cache-off sweep's valid, finite runs at λ ≥ λ_sat, λ_sat being the lowest swept λ whose measured-window mean `kv_cache_usage_perc` is ≥ 0.85. Every such run must be saturated (KV ≥ 0.85 and throughput < 0.95 × planned_rate). Statuses: `ok`; `unsaturated`, `not_monotone`, `too_few` (< 2 runs), all meaning "unmeasured". Threshold 0.85: owner's decisions on items 38–42 (decisions.md 2026-11-04).
- **Code:** `gate.cold_floor`, inputs from `gate.sweep_rows`.
- **Other text:** the REG-5 draft (`docs/drafts/addendum_34-43.md`), never computed for the default pool (decisions.md 2026-11-04 [DECISION] REG-5).

### λ_test
- **Text:** the largest multiple of 0.5 that is ≤ 0.8 μ_warm and ≥ 1.3 μ_sat,off, stepped down by 0.5 until the cache-on sweep run at the smallest swept rate ≥ λ_test had pooled percent fast ≥ 0.98 at TTFT ≤ 1.0 s, staying ≥ 1.3 μ_sat,off; none if no value fits.
- **Code:** `gate.zone_check`, `gate.slo_feasible`, `gate.choose_lambda`; driver `gate.reg7_zone`.

### c_b (completion rate in the cold backlog) ⚠ more than one computation
- **Text:** completions per second while requests wait and the sessions' cache is cold, against the planned session rate λp of the same span.
- **Code:**
  - `gate.burst_backlog` (via `margin.post_trigger_margin`): per fixed span after a burst, with its 99 % Poisson upper bound, against both λ and the span's planned session rate; decides REG-7's gate together with the matched control span (`gate.control_backlog`).
  - `floor.sustained_capacity`: over backlogged stretches (waiting ≥ 1 for ≥ 30 s); REG-6's measure, and REG-7's secondary readout only.

### gate verdict
- **Text:** `pass`, `drains`, `control_not_healthy` or `inconclusive` (an instrument gap, or a `stuck` burst run that no span confirms), from a control and a burst run with the same seed and duration, the control judged at the burst's end (REG-7).
- **Code:** `gate.gate_verdict`.

### overlap share
- **Text:** of the session cache hits in a span (by first token), the share served while the previous turn was still running: Σ cached tokens of later turns whose first token came before the previous turn's end ÷ Σ cached tokens of all later turns.
- **Code:** `gate.overlap_share`. Related, not the same: `derived.overlap_fraction` (share of turns *sent* before the previous first token) and `derived.cached_share_split` (mean shares over the whole window).

### 120 s surge peak
- **Text:** the highest number of planned session requests (burst requests left out, by `t_planned`) in a trailing 120 s window, per second, on a 5 s grid from 240 s. For a no-burst run that tipped: the peak in the last 180 s of its warm time (`peak_tip`), and before that (`peak_before`). A readout found in the data (decisions.md 2026-11-10 [CORR]), not a threshold, except where a registration fixes one (REG-17's `surge_tip` 3.2).
- **Code:** `gate.rolling_rate`, `gate.surge_run`, `gate.surge_table`; schedule only: `gate.schedule_peak_series`, `gate.surge_hazard`, `gate.pair_schedule`.
- **Other text:** `gate.surge_max` (REG-13) takes the highest planned rate over consecutive, non-overlapping 120 s windows, and REG-16's `peak_120s_before_first_cold` over 120 s windows stepped by 60 s; both can read lower than this on the same run (REG-16: 2.78 against 3.45).

### KV onset
- **Text:** the first scrape time whose trailing 60 s mean KV usage is ≥ 0.9 (at least 30 scrapes in the window); NaN if never. Marks a tip into the cold state; warm time ends 60 s before it.
- **Code:** `gate.kv_onset`.

## Terms of the revised Stage 2 (added 2026-11-12, decisions.md [DECISION] of that date)

None has code yet; each gets its code when the run or analysis that uses it is registered.

### cold floor (all-miss capacity)
- **Text:** the same quantity as μ_sat,off above: the completion rate of the saturated server with caching off. The preprints call it the all-miss capacity. The value on record for L1, 1.681 req/s, was measured with open-loop turns; a closed-loop value is not yet measured.
- **Code:** `gate.cold_floor`.

### margin
- **Text:** the load divided by the cold floor. L1 at λ = 2.0: 2.0 / 1.681 = 1.19 (DERIVED).
- **Code:** none.

### open-loop turns / closed-loop turns
- **Text:** open-loop: each turn is sent at its planned time, the gaps counted from the previous turn's planned time. Closed-loop: a later turn is released at the previous turn's end plus the planned gap (`workload.sessions.closed_loop: true`; FILE(configs/burst_l1pl350cl_r2.4_s1.yaml:6)). Latency is measured from the planned time in the first case and from the release time in the second (percent fast, above), so latency-based readouts are not comparable between the two.
- **Code:** `harness/workload.py`, `harness/loadgen.py`.

### cache gain
- **Text:** the counter hit rate (`load._level` `"hit"`) of a setup's no-trigger control in its warm state.
- **Code:** `load._level`.

### shared-only workload, matched cache gain
- **Text:** shared-only: every reusable token lies in one of a fixed set of prefixes shared across sessions, the set's total size does not change with load or backlog, and no request reuses tokens of its own session's earlier turns. Matched cache gain: two setups' cache gains agree within a tolerance registered beforehand. (`docs/claims.md`, K2.)
- **Code:** none; needs a harness change.

### session cap, sessions in service
- **Text:** a session is in service from its first turn sent to its last reply received. The session cap is a limit on the number of sessions in service, held at the load generator; a session beyond it waits to start. Its value per seed is the highest number of sessions in service at once in the same seed's no-trigger control (decisions.md 2026-11-12 [DECISION], design choices).
- **Code:** none; needs a load-generator change.

## Used configs that cannot be fixed (rule 5)

Used configs are never edited. Their known defects are recorded here instead.

### `configs/stage2_base.yaml`
- **Unit:** the comment at `:21` says "req/s^2". The unit is req/s (queue slope, above; decisions.md 2026-11-04 [CORR]).
- **Verdict block (`:10-22`):** it lacks `pf_climb`, `hit_climb` and `drain_horizon_s`, which `load.verdict` needs (`load.py:197`). It keeps the retired `q_slope`, `climb` and `end_s: 300`.
- **Effect:** the runs that use it directly cannot be judged by `load.verdict`: `20261101-144335_wipe_test_preempt`, `20261101-145940_wipe_test_idle`, and the stopped `20261101-151707_stage2_control_r1.5`. The wipe tests fail even before the missing keys. They are 900 s runs with the wipe at 450 s, so the 600 s baseline and the 1500 s watch do not fit, and `verdict` raises on an empty window. None of these runs was meant to be judged (decisions.md 2026-11-01, "Live wipe test").
- Every judged Stage 2 run gets the missing keys from `configs/stage2_cap_base.yaml:7-13`.
