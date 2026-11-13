# Rule F review of REG-22, draft 3 (first review): NOT READY

Ten required changes, all text or small code; no threshold has to move. On a run that is cold, full and backlogged in every span I could not produce a wrong label: the margins are wide (uncached rate 4.5–5.6 × against 2, N 4.9 × against 2, KV 0.95 against 0.80, reuse 0 against 0.94).

## 0. What this pass saw and ran

- **Read:** the bundle, `analysis/c2.py` and `tests/test_c2.py`, the helpers named in the brief, `analysis/gate.py` and `analysis/derived.py` (code only), `harness/loadgen.py`, `harness/workload.py`, `harness/config.py`, the configs, and the pinned vLLM source.
- **Not read:** `runs/`, `docs/decisions.md`, `status.md`, `claims.md`, PROTOCOL, the plan.
- **Code identity:** the two files in place equal commit `f0ba24e` and the bundle's patch (empty diff). `uv run --offline pytest tests/test_c2.py -q -p no:cacheprovider` gives 14 passed.
- **Limits kept:** every script replaces `find_runs` before any call; batch 2 was exercised with `k3w.find_runs` and `withheld.lifted` replaced. `git status` is the same as at the start.

Scripts (synthetic inputs only):
- [t00] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r1_scratch/t00_configs_arith.py`
- [fk] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r1_scratch/fk.py` (run generator)
- [t01] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r1_scratch/t01_label_map.py`
- [t02] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r1_scratch/t02_sustain.py`
- [t03] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r1_scratch/t03_levels.py`
- [t04] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r1_scratch/t04_table.py`
- [t05] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r1_scratch/t05_hist_onsets.py`
- [t06] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r1_scratch/t06_overload_onsets.py`
- [t07] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r1_scratch/t07_batch2_json.py`
- [t08] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r1_scratch/t08_partial_warm.py`
- [t09] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r1_scratch/t09_silent.py`
- [t10] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r1_scratch/t10_interruptions.py`

"Exit" below means the moment the last burst request ended (`c2.last_burst_end`).

## 1. Is the statistic what the text says?

| Function (`analysis/c2.py`) | Matches the text? | What differs, or what the text does not say |
|---|---|---|
| `windows` (41–45) | Yes | All 13 batch-1 and 5 batch-2 configs resolve to baseline [300, 900), warm-up 240 s, `end_s` 600, `stuck_hit_drop` 0.06. Watches are 1500 s (11 runs), 4500 s (REG-15) and 3000 s (batch 2), all multiples of 300 [t00]. |
| `gauge` (48–59) | Yes | Coverage works as described [t01, t05]. |
| `reuse_in` (62–65) | Yes, same as `k1.reuse` | No minimum number of turns in the judged path (the onsets need 20). A later turn whose previous turn has no prompt length is left out of both sums; a missing `cached_tokens` counts as a miss [t09]. |
| `session_uncached_rate` (68–75) | Yes | Returns 0.0, not missing, for an empty window. Fills a missing `cached_tokens` with 0 (line 75). A request with a first token that never finished is not counted [t09]. |
| `baseline` (78–81) | Yes | None. |
| `levels` (84–92) | Yes | A baseline N of 0 passes any N (line 91) [t03]; not reachable. |
| `last_burst_end` (95–101) | Mostly | Also missing when a burst request ended with an error status or there are no burst rows; the text says only "never ended". |
| `links` (104–114) | Yes | None. |
| `sustain` (117–129) | Yes for the rule; no for the Question | Spans sit on a fixed grid from 1080 s; a span that starts before the exit is dropped, so up to 299 s after the burst left are never judged [t02 S2]. One missing span hides a failing one (line 125) [t01 D]. |
| `condition4` (154–174) | **No** | See R1. |
| `onsets` (132–151) | Yes as defined | Equal grid times are ordered by signal name (line 150). Crossing lags differ by construction (R9). |
| `histogram_delta`, `turn_spacing`, `eviction_readout` (196–250) | Yes | Median bucket is right for cumulative buckets; edges 5 and 30 exist (SOURCE(vLLM 0.32.0 vllm/v1/metrics/buckets.py:KV_CACHE_RESIDENCY_BUCKETS)). A counter reset returns the same as "nothing sampled", and a reset followed by more samples is not seen [t05 H3]. No coverage rule for the first and last scrape [t05 H4]. |
| `batch_runs` (266–278) | Yes [t07] | Batch 2 takes its pattern, seeds, minimum of 3 and heading from `k3w.REG21` (FILE(analysis/k3w.py:65–67, 85)). An interim heading "[RESULT] REG-19 interim…" lifts the guard, as the text admits [t07]. |
| `reg22_table` (281–298) | Yes | One raise in one run aborts the whole batch [t04 B3]. The main block has no dirty-tree check; `k3w.py:462` has one. |

Other sentences the code or the sources do not support are R2, R3, R4, R6, R7 and R10 below. One small one: "when a sampled **cached** block is evicted" is not quite the source. The event is recorded when any sampled block is taken for a new allocation, before the hash check (SOURCE(vLLM 0.32.0 vllm/v1/core/block_pool.py:_maybe_evict_cached_block, line 742)). No effect on this workload (BELIEF).

## 2. Traces

| # | Synthetic input | Label produced | Right label | Likelihood on real data | Smallest fix |
|---|---|---|---|---|---|
| A [t01 A–C] | End-window KV 0.5 (or N 1.5 × baseline), and a burst request never ended, or one span only, or a scrape gap in a span | `not_memory_limited` | The text says `undefined`; I think the code is defensible | Low: needs the levels to fail | R1 |
| B [t01 D] | Levels hold, one span re-warmed, another span has a scrape gap | `undefined` | `not_sustained` | Low (BELIEF) | Optional O2 |
| C [t02 S1] | Exit at 1085 s; cache back in [1090, 1370) | `loop`; the unjudged stretch has reuse 0.947 and fails | `not_sustained` by the Question's wording | Low (BELIEF: the backlog is largest then) | Optional O1 |
| D [t02 S2] | Exit at 1981 s on a 1500 s watch | `undefined` with 599 s after the burst | Conservative, not wrong | Low (BELIEF); the registration names it | None |
| E [t10] | The state recovers fully for x seconds inside one span, then returns | `loop` for x ≤ 69 s. From 75 s only the KV link fails; the reuse link holds even with the cache back for 280 of 300 s | `not_sustained` | Plausible in batch 2 (BELIEF): `gate.py:1803` has outcome names for a line that empties and re-tips | R6; optional O3 |
| F [t02 S6, S7] | A cold span with little work done (0.55 req/s), or a span where the batch shrinks to 10 and KV to 0.6 with reuse 0 | `not_sustained` | Label is right; the decision line "interrupted by re-warming spans" is wrong | S7 plausible in a schedule lull (BELIEF); S6 unlikely | R6 |
| G [t03 L1] | Baseline N 15.5, end N 30, KV 0.95 | `not_memory_limited` | Pool is full; "a queue without a memory limit" is false | Low (baseline 6.1 at 2.2 per the registration) | R6 |
| H [t08] | 70–75 % of later turns hit in every span at the offered rate, or 85–90 % while serving faster than baseline | `loop` | `loop` by the thresholds, but not "cold" | Low in batch 1, unknown in batch 2 | R10 |
| I [t04 B2] | A load with 2 stuck runs both `loop`, or 1 of 1 | "loop in most", so "condition 4 is met at that load" | No load-level statement | Certain at 2.2 (two registered runs) | R5 |
| J [t06 B] | All four signals step at the same second | Order reported: reuse, n, u, kv (the plan's order). KV filling 40 s before the cache is lost is reported as reuse first | Simultaneous, or KV first | Certain to bias any real order by up to about 52 s | R9 |
| K [t06 A, C] | A twin with no burst rows; a queue that drains at 2700 s | Twin's links hold in every span; `loop` within the watch | See section 3 | Reachable at 2.4 | Named by the registration |

Checked and not reachable in the registered runs [t00, t02 S3, t03]:
- A warm-up inside the baseline window.
- A watch that is not a multiple of 300 s (the short last span is handled correctly).
- A baseline N of 0 or missing.
- The 256 cap: the pool holds 42 requests at the smallest prompt, so the clause cannot fail here.

Two facts from the configs that shape everything else [t00]:
- The pool holds 96,656 / (3072 + 128) = 30.2 requests at the mean prompt, which is the N of 30.0–30.3 the registration quotes. So N follows from KV, and "N ≥ 2 × baseline" can only fail if baseline N exceeds 15.
- The uncached-rate link follows from the reuse link unless throughput falls below 46 % of the offered rate. The "four links" are about two independent facts: reuse ≤ 0.94 and KV ≥ 0.80.

The arithmetic 3968, 24,576, 6.2 ×, 4.5–5.6 ×, 3.6 and 0.81 reproduces [t00], with one exception in R10.

## 3. The reading of PROTOCOL's order clause

- **Weaker or stronger.** `sustain` is stronger than the end-window levels in duration and weaker than an order test in kind. It tests that the levels co-occur in every 300 s span; it tests no direction. At 300 s resolution it misses a full recovery of up to 69 s [t10].
- **Pure overload.** Yes, it gets `loop` [t06 A, C]. Nothing in the label uses the control, the warm capacity or the schedule.
- **Does the registration name it.** Yes, in Alternatives 2, for λ = 2.4 only. It does not compute the cheap separators that exist: the same-seed control's links at the same absolute spans, and the control's verdict per judged run.
- **The premise is untagged.** "On a burst run the first events are the trigger's … and the hit rate falls after them" carries no evidence tag, and the registration says nobody computed the onsets. The only evidence it will produce on this is the readout of trace J, which is biased towards the plan's order.

## 4. "What was known" and the prediction

"Not computed by anyone … it cannot be checked from a file" is wrong on both counts. Registered functions already run on these runs compute:
- **Per-span KV, N, cached share, cold flag and burst completions** for [1680, 1980), [1980, 2280) and [2280, 2580), which are three of REG-22's five grid spans: FILE(analysis/margin.py:66–79) through FILE(analysis/gate.py:91–103, 139, 400), used by the gates of REG-11, 12, 14, 17 and 18. If the exit falls in (1380, 1680], these are exactly the judged spans [t02 S2].
- **For REG-15:** `watch_broken` on REG-22's exact grid, a 300 s timeline of KV and N, and the span test over the watch (FILE(analysis/gate.py:949–964, 989–1008)).
- **Burst first tokens in the end window** (FILE(analysis/gate.py:479–494)), which decides the "fewer than two spans" case.
- **The KV onset**, same 60 s window and same 0.9 level (FILE(analysis/gate.py:1361–1370, 1386)).

Whether those values were printed in the [RESULT] entries I may not read. What is new is the uncached rate, reuse in the first two spans, the exact exit, three of the four onsets and the histograms.

Other gaps:
- The description of REG-21 omits that its command also prints the uncached rate and reuse per 300 s span on the same grid (FILE(analysis/k3w.py:403–434, 467)): REG-22's first two links.
- "10–12 runs have the verdict stuck" forecasts a reported fact. The brief for this review says two of the 13 are `bad_baseline`; if so, 12 is impossible.
- P ≈ 0.95 for the levels is understated: KV 0.95 at the end is reported for every run, and N follows from KV. `not_memory_limited` is close to excluded for batch 1 before computing.
- The batch-2 forecast (at least four fifths `loop`) ignores exposure. Batch-1 runs have at most 4 judged spans, batch 2 has 9, REG-15 has 14 [t02 S4]. "0–2 `not_sustained`" in batch 1 implies up to about 5 % per span, which gives P(no failing span in 9) = 0.63. The two forecasts agree only below about 2.4 % per span. REG-15's run, the most exposed, is not listed as a candidate.

## 5. Strongest alternative for each label

- **`loop`:** a queue persists in a pool that holds 30 requests, and everything else follows mechanically: a queue fills the pool, a full pool evicts prefixes. Overload, a slowly draining queue or a slower GPU give the same picture. Separators: the control at the same spans, the load against the warm capacity, GPU clock per span (`gate.span_clock`), conditions 5–6, the loop-cut controls. Also selection: `stuck` already requires a low hit rate at the end.
- **`not_memory_limited`:** a high baseline N near capacity (trace G), or a lull in the last 600 s. Separator: which of the three levels failed, and per-span values.
- **`not_sustained`:** a schedule lull in one span (separator: planned session rate per span next to the links), a throughput dip with a cold cache (trace F), or more spans giving more chances to fail.
- **`undefined`:** the deepest backlogs have the longest burst tails, so the most stuck runs are the likeliest to drop out of k of n. Separator: report the links for the spans that exist, and the burst rows by status.

## 6. Can each outcome change a decision? Should it run?

- `not_memory_limited` would change a claim but is close to excluded for batch 1.
- `not_sustained` changes the confirmation run's registration.
- `loop` moves a status line and proposes D1 and D2.
- Batch 1 is largely a restatement of values the gates already computed. Batch 2 is the only reading with thresholds fixed first: one load, at most 5 runs.

The decision lines claim more than the labels carry in four places: the per-load sentence at n ≤ 2; "a queue without a memory limit"; "interrupted by re-warming spans"; and "condition 4 met" without saying the order clause was not judged.

It should run after the changes below: 0 GPU hours, and `not_sustained` or `undefined` are informative. Batch 1 should be worded as description.

## 7. Verdict: NOT READY

**REQUIRED**

- **R1.** Text and code differ on `undefined` (FILE(analysis/c2.py:161–164), trace A). State that failing levels give `not_memory_limited` whatever `sustain` is, or change the code. Add a test for that cell. Say that an errored burst request also gives a missing exit.
- **R2.** "Every span's four values": the code reports only judged spans (lines 123–124). Fix the text or report all spans with a judged flag.
- **R3.** Replace "Not computed by anyone … cannot be checked from a file" with the list in section 4, and add REG-21's per-span output.
- **R4.** Replace "10–12 runs have the verdict stuck" with the reported verdicts per load.
- **R5.** Fix a minimum n per load for any "at that load" sentence (REG-21 used 3). Below it, report per run only. λ = 2.2 has two runs with different watches (4 against 14 spans), which rule H does not let pool without a stated assumption.
- **R6.** Tie each decision line to the component that failed: "without a memory limit" only if KV < 0.80; "re-warming" only if the reuse link failed; "condition 4 met" must say "as read by REG-22, the plan's order not judged".
- **R7.** The freeze list between batches omits `windows`, `reuse_in`, `session_uncached_rate`, `REG22`, and the helpers: `k1.later_turns`, `margin.is_burst_request`, `load._covered`, `load.verdict`, `load._level`, `load.find_runs`, `stats.cp_upper`, `k3w.batch2_runs` with its `REG21` keys, and `withheld`. Complete it.
- **R8.** "An exception is fixed and logged as a [CORR]" does not say what review a fix to a judged function needs. Say it, and that no fix drops a request or run silently.
- **R9.** Onsets: report ties as ties. State the built-in lags for steps of the expected size (reuse 3.6 s, uncached rate 11.6 s, N 15 s, KV 55 s) or use levels at the same relative position. Tag the premise in section 3 as BELIEF, and say what is reported if the order found is the plan's.
- **R10.** "Failed only by a span in which about four fifths or more of the turns hit" holds at equal request rates only. At the registration's own cold completion rates the share is 0.66–0.77 [t00].

READY when all ten are in the text or code, R1 has its test, and a second pass sees the diff.

**OPTIONAL**

- **O1.** Report the links over the stretch from the exit to the first judged span.
- **O2.** One failing span decides `not_sustained` even if another is missing.
- **O3.** Report the longest stretch with nothing waiting inside the judged spans, and state the 300 s resolution.
- **O4.** A minimum number of turns for the judged reuse.
- **O5.** Add each judged run's control verdict, and the control's links at the same spans.
- **O6.** Report the left-out runs' values as a contrast.
- **O7.** Give the lower Clopper–Pearson bound beside the upper one; the upper is 1.0 whenever k = n [t04 B1].
- **O8.** Histograms: flag a reset, add a coverage rule, and say what is done when the turn spacing falls inside the median's bucket [t05 H2].
- **O9.** A dirty-tree check in the main block, and tests for batch 2 and the 4500 s watch.
- **O10.** Count ok rows with a missing `cached_tokens`.

## 8. What I could not check

- **Anything in `runs/`:** the 13 runs' validity and verdicts; whether the first-token, prompt and cached fields are complete; whether `metrics.jsonl` holds the three histograms; whether other closed-loop burst runs exist (configs exist for seed 7 at 2.0 and for a seed-14 long confirmation).
- **`decisions.md`, `claims.md`, PROTOCOL and the plan:** the quoted wording of condition 4 and the order; the 2026-11-01 thresholds; what earlier results printed; whether REG-21's batch 1 has been computed; the "two of 13 `bad_baseline`" in the brief.
- **Every number with a RUN tag** (0.949, 30.3, 6.1, 4.93, 34, 30.0, 1.73–1.81). 30.3 / 6.1 is 4.97, not 4.93, on the rounded inputs.
- **`agent/theory/k1_held_prefix.md`:** the 64 s and 1 s derivation.
- **`load.verdict` on real data**, and the run time of the full table.
