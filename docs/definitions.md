# Definitions

One entry per term: one text definition, its source, and the code that computes it. Created 2026-11-04 (decisions.md, same date).

- **Which text is given:** where files differ, the newer decisions.md entry rules (`PROTOCOL.md:3`). Older or other wordings are listed under "Other text", not deleted.
- **⚠ more than one computation:** the term is computed in more than one way, and reported numbers may come from either. **No single one has been chosen yet.**
- Line numbers are as of 2026-11-04. Code paths: `load` = `analysis/load.py`, `derived` = `analysis/derived.py`.

## Outcome and capacity

### percent fast ⚠ more than one computation
- **Text:** "a request is fast if its first token arrives within 1.0 s of its planned arrival and it finishes ok. Unfinished requests are misses." `docs/decisions.md:122`. It is counted by arrival time: "Each second, take the requests that **arrived** in that second and count how many met the limit." `docs/experiment-plan.md:115`.
- **Code:**
  - `load.percent_fast` (`load.py:76`): a share for each 1 s arrival bin.
  - `load._level` `"pf"` (`load.py:151`): one share pooled over every request arriving in [a, b). This one feeds `verdict` and `ramp_table`. It counts requests, not bins, and it includes burst requests.
- **Other text:** `analysis/CLAUDE.md:4` ("percent fast per arrival second").

### goodput
- **Text:** "Share of requests that met the speed limit (SLO); the goodput measure from Stage 1". `docs/experiment-plan.md:205`. It is a synonym of percent fast.
- **Code:** none of its own; see percent fast.

### throughput
- **Text:** "completions per second inside the measured window, the plan's definition". `docs/decisions.md:97`.
- **Code:** `load.summarize` `"throughput"` (`load.py:98`): ok requests whose `t_end` falls in [warm-up, end of arrivals), divided by that span.
- **Other text:** the step 4 sweep used an arrival-based count instead (`docs/decisions.md:88`, superseded).

### μ_warm
- **Text:** "μ is the highest swept λ whose run is valid, with throughput ≥ 0.95 λ and waiting-queue slope ≤ 0.01 req/s², both over the measured window", with prefix caching on. `docs/decisions.md:61`.
- **Code:** `load.capacity` (`load.py:208`), on `load.summarize` rows.
- **Other text:** "Highest load the server keeps up with when the cache works" (`docs/experiment-plan.md:201`).

### μ_off
- **Text:** the same rule as μ_warm (`docs/decisions.md:61`), with prefix caching off.
- **Code:** `load.capacity` (`load.py:208`).
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
- **Code:** `load.verdict` (`load.py:187-190`): `t_end = trigger end + watch_s`; `end_s` is set in `configs/stage2_cap_base.yaml:8`.
- **Other text:** an `end_s` of 300 s in `configs/stage2_base.yaml:14`, superseded before any verdict. It is still inherited by `wipe_test_*.yaml` and `stage2_control.yaml`, none of which was judged.

### baseline window
- **Text:** "the baseline is the 600 s before the trigger *starts*". `docs/decisions.md:391`.
- **Code:** `load.verdict` (`load.py:188`).
- **Other text:** "the last 600 s before the wipe" (`docs/decisions.md:210`); the 600 s before the trigger's end (the error corrected at `:389`).

### trigger end ⚠ more than one computation (two copies of one rule)
- **Text:** no text definition. Closest: "The baseline ends where the trigger starts; the watch starts where it ends (a successful wipe, a burst, or control_t_s for a control...)" (`analysis/load.py:174-176`).
- **Code:**
  - `load.verdict` (`load.py:179-185`): a wipe ends at the `t_end` of the successful call in `trigger.jsonl`; a burst at `at_s + duration_s` (its planned arrivals end, not its backlog); a control at `control_t_s`.
  - `derived.trigger_times` (`derived.py:20`) is the same rule, copied so that `verdict` stays unchanged.

## Server metrics

### hit rate h ⚠ more than one computation
- **Text:** "Δ`vllm:prefix_cache_hits` ÷ Δ`vllm:prefix_cache_queries`". `docs/experiment-plan.md:125`.
- **Units (source):** tokens. Readmissions of preempted requests are excluded (`docs/open-questions.md`, S8).
- **Code:**
  - `load.rates` `hit_rate` (`load.py:66`): one ratio per scrape interval.
  - `load.summarize` `"hit_rate"` (`load.py:101`): the mean of the per-scrape ratios over the measured window.
  - `load._level` `"hit"` (`load.py:152`), `derived.hit_between` (`derived.py:13`) and `derived.thirds(how="counter")` (`derived.py:37`): the ratio of counter differences over the span. This feeds `verdict`.
  - `load.whole_run_hit_rate` (`load.py:108`): first scrape to last.
- **Different numbers for the same run:** e.g. the long run's last third, 0.6004 (mean of ratios) vs 0.6255 (counters), `docs/decisions.md:116`.

### KV usage
- **Text:** "usage is 1 − free blocks / total ... So usage counts blocks held by running requests, and saved prefixes with no running user count as free." `docs/decisions.md:244`. Source: `vllm/v1/core/block_pool.py` `get_usage`.
- **Code:** the gauge `vllm:kv_cache_usage_perc`, through `load.rates` (`load.py:70-72`); `load._level` `"kv"` (mean, `load.py:154`); `derived.kv_footprint` (`derived.py:76`).

### running batch N
- **Text:** "`vllm:num_requests_running` | How many requests share the GPU". `docs/experiment-plan.md:124`.
- **Code:** gauge; `load._level` `"n"` (mean, `load.py:154`).

### waiting Q
- **Text:** "`vllm:num_requests_waiting` | Whether requests pile up". `docs/experiment-plan.md:123`.
- **Code:** gauge; `load._level` `"q"` (mean) and `"q_slope"` (least-squares slope, `load.py:153`); `load.summarize` `"q_mean"` and `"q_slope_per_s"` (`load.py:102-103`).

### preemption
- **Text:** "report preemptions per minute in the watch window, excluding the wipe's own, against the no-trigger control and the caching-off run at the same λ". `docs/decisions.md:247`. Counter: `vllm:num_preemptions` (`docs/experiment-plan.md:128`).
- **Code:** only the generic `load.rates` `num_preemptions_rate` (`load.py:63`). **No code for the registered comparison.**

### R (block idle time before eviction)
- **Text:** "`vllm:kv_block_idle_before_evict_seconds` | How long a cached prefix survives (R)". `docs/experiment-plan.md:129`. Recorded as a histogram, sampled (`--kv-cache-metrics`, `configs/base.yaml:17`).
- **Code:** **none.** `load.metrics_wide` drops the `_bucket` series, and nothing reads `_sum` or `_count`.

## Run verdicts

All five come from one rule, `docs/decisions.md:272-277`, restated at `PROTOCOL.md:24-28`. Code: `load.verdict` (`load.py:173-205`), with thresholds under `verdict:` in `configs/stage2_base.yaml:10-22` and `configs/stage2_cap_base.yaml:7-13`.

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
- **Code:** `load.verdict`.

### metastable failure
- **Text:** six conditions at one load: trigger over at the same load; control `recovered`; `stuck` in most seeds; a memory-limited loop; persistence over a 4500 s watch; two states at one load. `docs/decisions.md:281-287`, restated at `PROTOCOL.md:30-36`.
- **Code:** none. Only the per-run verdict is coded.
- **Other text:** three conditions (`docs/experiment-plan.md:265`, superseded); "Stuck ... The metastable failure" (`:207`).

## Derived quantities

Added 2026-11-04 with their code. Each is the reading that reproduces the published values (`docs/decisions.md`, 2026-11-04 "Derived figures moved into analysis/").

### W (working set)
- **Text:** "sum of the latest prompt over active sessions from the schedule". `docs/decisions.md:248`.
- **Code:** `derived.working_set` (`derived.py:63`). A session counts as active from its first planned turn to its last.

### F (running-batch footprint)
- **Text:** no definition in the original entry (`docs/decisions.md:248-250`).
- **Code:** `derived.kv_footprint` (`derived.py:76`): mean KV usage × pool size.

### cached-share split
- **Text:** "Mean cached share of the prompt, all later turns vs only those starting after the previous turn had finished". `docs/decisions.md:293`.
- **Code:** `derived.cached_share_split` (`derived.py:93`). "Starting" here means **its first token** at or after the previous turn's end.

### overlap fraction
- **Text:** "Sent before the previous turn's first token". `docs/decisions.md:292`.
- **Code:** `derived.overlap_fraction` (`derived.py:103`).
