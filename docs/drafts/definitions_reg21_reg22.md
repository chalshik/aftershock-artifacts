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

## With REG-22

### condition-4 levels
- **Text:** "in the end window, mean KV ≥ 0.80, mean running batch N ≥ 2 × its baseline mean, and maximum N < 256". decisions.md 2026-11-13 [REG] REG-22, Statistic; thresholds from decisions.md 2026-11-01.
- **Code:** `c2.levels`, with the baseline from `c2.baseline` ([burst start − 600 s, burst start)) and every gauge value through `c2.gauge` (coverage as for the busy share).

### loop links and sustain
- **Text:** "in every span that starts at or after the moment the last burst request ended, all four hold: reuse of later turns ≤ baseline − 0.06; session uncached prefill ≥ 2 × baseline; mean N ≥ 2 × baseline; mean KV ≥ 0.80. At least two such spans are needed." Same entry.
- **Code:** `c2.links` (one span), `c2.sustain` (every span), `c2.last_burst_end`; the label by `c2.condition4`.

### session uncached prefill rate
- **Text:** "prompt tokens not served from the cache, session requests only, per second, by first token". Same entry.
- **Code:** `c2.session_uncached_rate`. It raises if an ok session request has no first-token time or no prompt length.
- **Not the same as:** U of REG-21 (above), which counts the burst's requests too.

## Ledger rows for `docs/model.md` (added with each registration, before its first batch is computed)

Columns: # | Date | Model | Prediction (registered before the run) | Observed | Hit / miss | Runs.

- **REG-21** (next number 24): `| 24 | 2026-11-13 | K3 step B (REG-21: uncached-token work rate of the cold, backlogged burst runs against the saturated cache-off sweep, L1, 350 W, closed loop; model F: r = 1.00 at every load) | Batch 1 (13 runs, retrospective): J2 inside ≈ 0.85, outside ≈ 0.13, undefined ≈ 0.02; λ = 2.0 group inside ≈ 0.85; λ = 2.4 group inside ≈ 0.05, outside high ≈ 0.95. Batch 2 (REG-19's burst runs): J1 undefined ≈ 0.24 with five runs, 0.44 with four; otherwise inside ≈ 0.65, outside high ≈ 0.3, outside low ≈ 0.05 | — | Open | decisions.md 2026-11-13 [REG] REG-21 |`
- **REG-22** (the number after): `| 25 | 2026-11-13 | C2 condition 4 (REG-22: levels at the end of the watch and the loop's four links in every span after the burst's requests left, stuck burst runs, L1, 350 W, closed loop) | Batch 1 (13 runs, retrospective): 10–12 with the verdict `stuck`; of these `loop` in 8–11, `not_sustained` in 0–2, `not_memory_limited` in 0–1, `undefined` in 0–1. Batch 2: `loop` in at least four fifths of the stuck runs | — | Open | decisions.md 2026-11-13 [REG] REG-22 |`
