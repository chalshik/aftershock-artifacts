# Draft: terms that `docs/definitions.md` gains when REG-21 and REG-22 are registered (rule J)

Not in force. Each block is appended to the section "Terms of the revised Stage 2" of `docs/definitions.md` in the same commit as its registration's [DECISION] (delegate). "Text" quotes the registration; the line numbers of `docs/decisions.md` are filled in then.

## With REG-21

### uncached-token work rate U
- **Text:** "uncached prompt tokens per second, Σ (prompt_tokens − cached_tokens) over ok requests, session and burst, whose first token falls in the window". decisions.md 2026-11-13 [REG] REG-21, Statistic.
- **Code:** `k3w.work_rate` (`analysis/k3w.py`). It raises if an ok request has no first-token time or no prompt length. The same quantity by end time (`by="t_end"`) is reported, never judged.
- **Not the same as:** the session uncached prefill rate of REG-22 (below), which leaves the burst's requests out.

### cache-off work rate U_off
- **Text:** "the mean of U over REG-8's five saturated cache-off runs, pinned by id, each over its measured window". Same entry.
- **Code:** `k3w.reference`; the five run ids are `k3w.REG21["ref_runs"]`. It raises unless exactly those five are there and valid.

### work-rate ratio r
- **Text:** "r = U over W ÷ U_off, per run. W = [burst end + 600 s, burst end + watch)". Same entry.
- **Code:** `k3w.row` (`"r"`), with W from `k3w.window`.

### busy share
- **Text:** "at least one request waiting in at least 0.99 of the scrapes of W, and the gauge covers W: a scrape within 10 s of each end and no gap above 10 s". Same entry, Runs and preconditions.
- **Code:** `k3w.busy_share` on `vllm:num_requests_waiting`; coverage by `load._covered` with `k3w.REG21["gauge_max_gap_s"]`. Without coverage the share is NaN and the run is listed as "no waiting gauge in W".
- **What the gauge counts:** the scheduler's waiting queues without the deferred requests; no request of the running set (vLLM 0.32.0 `v1/core/sched/scheduler.py`, `Scheduler.make_stats` and `Scheduler.get_request_counts`).

## With REG-22 (as in REG-22 draft 5; owner-proxy round 1, condition 9)

### condition-4 levels ⚠ (two computations on record; left for the owner, rule J)
- **Text:** "in the end window, mean KV ≥ 0.80, mean N ≥ 2 × its baseline mean, maximum N < 256". decisions.md 2026-11-13 [REG] REG-22, Statistic; thresholds from decisions.md 2026-11-01. The order clause of PROTOCOL §3 condition 4 ("and the traces follow the plan's order") is not part of this term and has no code.
- **Code:** `c2.levels`, with the baseline from `c2.baseline` ([burst start − 600 s, burst start)) and every gauge value through `c2.gauge` (coverage as for the busy share).
- **Second computation:** REG-15's [RESULT] computed the same three levels over the watch's last 1500 s (decisions.md 2026-11-10 [RESULT] REG-15, "Condition 4"), not the last 600 s.
- **Never written here or anywhere under REG-22:** that condition 4 is met, holds or is passed.

### the exit
- **Text:** "the moment the last burst request ended; missing if a burst request never ended, ended with an error status, or the run has no burst rows". Same entry.
- **Code:** `c2.last_burst_end`. The eviction readout uses the burst's end where the exit is missing.

### reuse of later turns, with a minimum of turns ⚠ (two computations)
- **Text:** as "reuse (prefix reuse of later turns)" above, with at least 20 later turns in the window, else missing. Same entry.
- **Code:** `c2.reuse_in` (with `min_turns`); `k1.reuse` computes the same quantity with no minimum.

### loop links and sustain
- **Text:** "in every span that starts at or after the exit, all four hold: reuse of later turns ≤ baseline − 0.06; session uncached prefill ≥ 2 × baseline; mean N ≥ 2 × baseline; mean KV ≥ 0.80. At least two such spans are needed; one failing span decides." Same entry. REG-22's own description; it does not stand for condition 4's order clause unless an entry headed `[DECISION] (owner)` says so.
- **Code:** `c2.links` (one span), `c2.sustain` (every span); the label by `c2.condition4`.

### session uncached prefill rate ⚠ (three computations)
- **Text:** "prompt tokens not served from the cache, session requests only, per second, by first token". Same entry.
- **Code:** `c2.session_uncached_rate`. It raises if an ok session request has no first-token time or no prompt length.
- **Other computations:** `k3w.work_rate` (U of REG-21: the burst's requests too, by first token); `load.rates` `recomputed_prefill_tok_s` (from the server's counters, all requests, per scrape interval, `load.py:75`).

### turn spacing
- **Text:** the median time between the first tokens of consecutive turns of a session, over later turns whose first token falls in the window. Same entry, eviction readout.
- **Code:** `c2.turn_spacing`.

### onset reading
- **Text:** each onset minus the lag a trailing 60 s mean has for a step from the baseline value to the end-window value; pairs in the plan's order compared with a 10 s tolerance; readings `plan_order_beyond_lags`, `not_distinguishable_from_simultaneous`, `differs`, `incomplete`. Reported only; not a reading of the order clause. Same entry.
- **Code:** `c2.onset_reading`, on `c2.onsets`.

### Changes to existing entries, in the same commit
- **R (block idle time before eviction):** "Code: none" becomes: `c2.histogram_delta` reads the sampled histogram's buckets from the raw `metrics.jsonl` (gain over a window, the median's bucket with both edges, the shares at or below 5 s and 30 s; a window in which any bucket goes down is flagged `reset` and not read); `load.metrics_wide` still drops the buckets.
- **metastable failure:** gains the line "Condition 4's levels have code (`c2.levels`, REG-22); its order clause has none. No definition here says condition 4 is met."

## Ledger rows for `docs/model.md` (added with each registration, before its first batch is computed)

Columns: # | Date | Model | Prediction (registered before the run) | Observed | Hit / miss | Runs.

- **REG-21** (next number 24): `| 24 | 2026-11-13 | K3 step B (REG-21: uncached-token work rate of the cold, backlogged burst runs against the saturated cache-off sweep, L1, 350 W, closed loop; model F: r = 1.00 at every load) | Batch 1 (13 runs, retrospective): J2 inside ≈ 0.86, outside ≈ 0.13, undefined ≈ 0.01 or less; λ = 2.0 group inside ≈ 0.9 or more; λ = 2.4 group inside ≈ 0.05, otherwise outside high; slope +0.05 to +0.10 per req/s. Batch 2 (REG-19's burst runs): never computed ≈ 0.4; if computed, J1 undefined ≈ 0.24 with five runs, 0.44 with four, 0.73 with three; otherwise inside ≈ 0.65, outside high ≈ 0.3, outside low ≈ 0.05 | — | Open | decisions.md 2026-11-13 [REG] REG-21 |`
- **REG-22** (the number after): `| 25 | 2026-11-13 | C2, condition 4's registered levels and the loop's links (REG-22: the levels at the end of the watch and the four links in every span after the burst's requests left, stuck burst runs, L1, 350 W, closed loop; the order clause not judged) | Batch 1 (13 runs, retrospective; 11 stuck): `loop` in 9–11 (all eleven ≈ 0.8), `not_sustained` 0–2, `not_memory_limited` 0, `undefined` 0–1; `onset_reading` `differs` in ≥ 8 of 11 ≈ 0.7. Batch 2: computed ≈ 0.6, with ≥ 3 stuck runs ≈ 0.7 of that; then `loop` in about seven tenths of the stuck runs | — | Open | decisions.md 2026-11-13 [REG] REG-22 |`
