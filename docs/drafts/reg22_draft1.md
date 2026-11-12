## 2026-11-13 · [REG] REG-22 (C2, condition 4): is the stuck state a memory-limited loop and not just a queue? The registered levels at the end of the watch, and the loop's four links in every span after the burst's own requests have left; the plan's trace order is reported, not judged, because it was written for a wipe (0 GPU h)

- **ID:** REG-22. An analysis of existing runs, 0 GPU h. Draft 1.
- **Question:** in the burst runs that the registered verdict calls `stuck`, is the KV pool full, is the running batch at least twice its baseline and below the 256 cap (the registered levels), and do the loop's links (cache lost, prompts recomputed, large batch, full pool) hold together in every span once no burst request is left in the system?
- **Claim tested:** C2 (`docs/claims.md`), its first test: "in stuck runs … condition 4 (mean KV ≥ 0.80, mean N ≥ 2 × baseline, N below the 256 cap)". PROTOCOL §3 condition 4 adds "and the traces follow the plan's order".
- **What this registration changes, and why it needs the delegate's decision.** The plan's order (`docs/experiment-plan.md`, "Showing the loop": the hit rate drops, recomputed prefill rises, the batch grows, KV fills, the hit rate stays low) describes a cache wipe, where the loss comes first. A burst of one-off prompts fills the pool itself: on a burst run the first events are the trigger's (batch and KV up), and the hit rate falls after them. Judging the literal order would fail every burst run for a reason that says nothing about the loop. So for burst runs condition 4's last clause is read as **`sustain`** below, and the onset times are **reported with the order found**. This is a reading of a PROTOCOL rule fixed before it is applied to any run; PROTOCOL §3 gets a dated note pointing here.

### Statistic (`analysis/c2.py`)
Baseline: the 600 s before the burst starts ([300, 900) s). End window: the last 600 s of the watch. Spans: the watch cut into 300 s spans from the burst's end.
- **levels** (`c2.levels`, the thresholds of decisions.md 2026-11-01): in the end window, mean KV ≥ 0.80, mean running batch N ≥ 2 × its baseline mean, and maximum N < 256.
- **sustain** (`c2.sustain`): in **every** span that starts at or after the moment the last burst request ended (`c2.last_burst_end`), all four hold (`c2.links`):
  1. reuse of later turns (`k1.reuse`'s statistic: cached tokens over the previous prompt, by first token) ≤ baseline − 0.06 (the verdict's `stuck_hit_drop`, read from the run's config);
  2. session uncached prefill (prompt tokens not served from the cache, session requests only, per second, by first token) ≥ 2 × baseline;
  3. mean N ≥ 2 × baseline;
  4. mean KV ≥ 0.80.
  At least two such spans are needed. With fewer, or with a burst request that never ended, or with a missing value, the run is `undefined`.
- **Why 2 × for the uncached rate (fixed here, before any run is read):** DERIVED from the L1 schedule. Warm, a session of 8 turns prefills 2176 + 7 × 256 = 3968 tokens; cold, 24,576. At equal request rates the cold rate is 6.2 × the warm one; at the stuck completion rates on record (1.73–1.81 against 2.0–2.4 req/s offered) it is about 4.5–5.6 ×. With half of the sessions hitting, the ratio at equal request rates is (0.5 × 3968 + 0.5 × 24,576) / 3968 = 3.6; it falls to 2 when the share hitting reaches 0.81 (DERIVED: 24,576 − 20,608 h = 2 × 3968). So 2 × is passed by a cold server with a wide margin and failed only by a span in which about four fifths or more of the turns hit.

### Labels (`c2.condition4`)
`loop` (levels and sustain hold); `not_memory_limited` (the levels fail: by PROTOCOL "a backlog state, not this loop"); `not_sustained` (the levels hold, a link is missing in some span after the burst's requests left); `undefined`. Reported per run and as counts; k of n `loop` with its one-sided 95 % Clopper–Pearson upper bound per load (rule H), never pooled across loads.

### Runs
The 13 closed-loop L1 burst runs at 350 W made before REG-19 (`c2.REG22["runs"]`; REG-11, REG-12 seeds 2–6, REG-14, REG-15, REG-17, REG-18 seeds 3–6). A run is judged only if `load.verdict` gives `stuck`; the others are listed with their verdict. REG-19's runs are not read (withheld); they get the same table after REG-19's [RESULT], reported apart.

### Not blind, said plainly
For these runs the [RESULT] entries report hit 0 and KV 0.95 at the end, and `gate.reg15_table` printed REG-15's levels (KV, N, N over baseline). "About 65 requests run in the cold state" is on record (open-questions S7). So the **levels are expected to hold** (BELIEF, P ≈ 0.95 per stuck run). Not computed by anyone: the links per span, when the last burst request ended, the onsets. REG-18's seeds 3 and 6 were reported as failing the cold side in one quiet span each, so `not_sustained` is a live outcome for them.

### Prediction (BELIEF)
10–12 runs have the verdict `stuck`. Of these: `loop` in 8–11; `not_sustained` in 0–2 (REG-18 seeds 3 and 6 are the candidates); `not_memory_limited` in 0–1; `undefined` in 0–1 (a burst tail that leaves fewer than two spans). Onset order most often N, KV, reuse, uncached rate.

### Decision under each outcome (rule A1)
- **`loop` in most stuck runs at a load (more than half):** condition 4 is met at that load for the runs on record; C2's status changes from "untested" to "condition 4 met in k of n stuck runs; the loop-cut controls not yet run". The loop-cut controls D1 and D2 are registered on the session population as planned.
- **`not_memory_limited` in most:** the stuck runs are backlog states, not this loop: by `docs/claims.md` this refutes C2 for these cells. D1 and D2 are not registered as planned; the paper reports the stuck state as a queue without a memory limit and K1's "held prefix" reading is dropped.
- **`not_sustained` in most:** the levels hold but the loop has gaps: the paper says the cold state is interrupted by re-warming spans, and the confirmation run's registration must read every span, not only the end window.
- **Mixed or `undefined`:** reported per run; C2 stays "untested" for that load.

### Reported, never judged
The onset time of each of the four signals after the burst's start (first 10 s grid time at which the trailing 60 s crosses: KV ≥ 0.9; N ≥ 2 × baseline; reuse ≤ baseline − 0.06 with at least 20 turns; session uncached rate ≥ 2 × baseline) and their order; every span's four values; when the last burst request ended.

### Alternatives to state with any result
1. **The preemption cycle of Ao et al.** A full pool with a large batch is also what their limit cycle shows. Preemptions per second in the end window against the same seed's control are the registered comparison (decisions.md 2026-11-01); it is computed in its own registration (the matched-control analysis), and its reading is quoted beside this table.
2. **Overload, not a loop.** At λ = 2.4 the closed-loop warm capacity is reached (REG-13), so there the levels can hold with no history dependence. Condition 4 does not separate these; conditions 2, 5 and 6 do.
3. **The thresholds meet the data where it is easiest.** KV ≥ 0.80 was set from a healthy sweep run's 0.82 (decisions.md 2026-11-01), long before any stuck run existed; 2 × the uncached rate is new and is justified above from the schedule alone.
4. **The burst's tail.** A burst request that ends late shortens the judged part of the watch; the number of judged spans is reported per run.

### Stopping rule
Computed once: `uv run python -m analysis.c2 reg22`, after this registration is approved. No second threshold, window or span length. An exception is fixed and logged as a [CORR] before the table is read.

### Cost
0 GPU h; about a minute of CPU.

### Code and tests
`analysis/c2.py` (`levels`, `links`, `sustain`, `onsets`, `condition4`, `reg22_table`); `tests/test_c2.py`, 8 tests on hand-made runs: a cold, full, backlogged run is `loop`; a low KV, a small batch or a batch at the cap is `not_memory_limited`; a span in which the cache comes back is `not_sustained`; a burst still in the system or leaving too late is `undefined`; the onsets' order; missing metrics; the uncached rate leaves burst requests out; the table judges only stuck runs. No run folder was read while writing this draft or its code.
