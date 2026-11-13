## 2026-11-13 · [REG] REG-23 (K5): do the cache signals warn before latency and the queue, and earlier than watching arrivals? Onsets on the runs that went cold without a burst, false alarms on the runs that stayed warm; a retrospective reading (0 GPU h)

- **ID:** REG-23. An analysis of existing runs, 0 GPU h. Draft 2, not reviewed (draft 1 is `docs/drafts/reg23_k5_draft1.md`). Code: `analysis/k5.py`, `tests/test_k5.py` (10 tests), at the commit named when this is sent to review.
- **What this is, in one line:** a retrospective reading that decides whether K5 stays in the paper as a claim or becomes one sentence in the limitations. It is not called a test below.
- **This registration covers computing and reporting only.** The edit to `docs/claims.md` and the paper that follows from it needs its own decision.
- **Question:** when the warm server goes cold by itself, do the hit rate (H) and the recomputed prefill rate (U) move before latency (L) and the waiting line (Q) do, with few false alarms, and earlier than the arrival rate (A) moves?
- **Claim:** K5 (`docs/claims.md`): "recomputed prefill tokens per second and the hit rate change before latency and queue length do; the contribution is the measured lead time."
- **How this differs from the claim's stated test.** `docs/claims.md` says "a registered onset rule per signal, applied to stuck runs". The stuck runs on record are burst runs. In a burst run the trigger itself raises the recomputed prefill rate and the running batch at once, so a "lead" there is the shape of the burst, not a warning. The fair events are the runs that went cold with no trigger. Burst runs are not computed here. This reading is the delegate's and is listed for the owner.

### Events and quiet runs (`k5.candidates`, `k5.event`, `k5.quiet`)
- **Candidates** (`k5.K5["runs"]`, 19 folder names): every closed-loop L1 run at 350 W without a trigger made before REG-19: the controls of REG-11, REG-12, REG-14, REG-16, REG-17 and REG-18 and REG-13's cache-on sweep. A candidate must be valid; the function raises if a folder is missing. REG-19's controls are withheld and are not candidates.
- **An event** is a candidate whose KV pool fills: `gate.kv_onset` is finite (the first scrape whose trailing 60 s mean KV is ≥ 0.9, the rule `gate.surge_run` uses for `tipped`).
- **A quiet run** is a candidate that never reaches that onset.
- **Left out, with the reason:** an event whose reference window is shorter than 120 s ("no reference"); a run with a missing metric or a counter that goes down.

### Signals (`k5.signals`)
Server-side only, what an operator has: trailing means over 30 s on a 5 s grid, from the 1 s scrapes.
- **H:** counter hit rate, Δhits ÷ Δqueries.
- **U:** recomputed prefill tokens per second, (Δprompt tokens − Δcached tokens) ÷ time.
- **Q:** mean requests waiting. **N:** mean requests running.
- **L:** latency, the server's mean time to first token, Δsum ÷ Δcount of `vllm:time_to_first_token_seconds`.
- **A:** session requests sent per second over a trailing 120 s. It is the trivial warning: every no-burst collapse on record followed a 120 s arrival surge (decisions.md 2026-11-10 [CORR]).
A window with fewer than two scrapes, spanning less than 15 s, or with nothing to divide by gives no value.

### Onsets and leads
- **Reference window** of an event: [240 s, KV onset − 240 s). Each signal's mean and SD over it.
- **Levels** (`k5.levels`), fixed here before any onset is computed on any run:

  | signal | moved when | where the number comes from |
  |---|---|---|
  | H | below mean − max(4 SD, 0.06) | 0.06 is the verdict's `stuck_hit_drop` |
  | U | above mean + max(4 SD, 0.5 × mean) | a half more recomputed work than warm |
  | Q | ≥ 1 | one request waiting on average |
  | N | ≥ 2 × mean | condition 4's factor (decisions.md 2026-11-01) |
  | L | above max(mean + 4 SD, 1.0 s) | 1.0 s is the SLO |
  | A | ≥ 3.2 req/s | `gate.SURGE`'s tip reading |

- **Onset** (`k5.crossings`): the first grid time after the reference window from which the signal stays beyond its level for 15 s (at every grid time of that stretch).
- **Lead of X over latency:** onset(L) − onset(X). **Over the queue:** onset(Q) − onset(X).
- **A lead counts only above 30 s, the length of the trailing window.** Signals that step at the same instant cross their levels at different times: a trailing mean crosses after window × (level − before) ÷ (after − before), which is about 2 s for H (30 × 0.06 / 0.84), 4 s for U, 6 s for Q and 9 s for L for steps of the size seen in cold runs (DERIVED, with the cold values of the published spans). Left alone, that would hand H and U a "lead" over latency of a few seconds with nothing behind it (FILE(tests/test_k5.py), `test_signals_that_step_together_do_not_lead`).

### Judged (`k5.judge`)
- **Per signal and comparator:** `leads` only if at least 5 events have both onsets and every one has a lead above 30 s; `no_lead` if the median lead is ≤ 0; `within_window` if the median is above 0 and not above 30 s; `too_few` below 5 events; otherwise `mixed`.
- **False alarms:** the same levels on the quiet runs, with the reference window [240, 540) s, scanned from 540 s to the end of arrivals: onsets per hour, summed over the quiet runs.
- **Usable:** a signal that `leads` both latency and the queue and gives fewer than 1 false alarm per hour.
- **K5's label:** `cache_signal_leads` if H or U is usable and its median lead over latency is above A's; otherwise `no_usable_cache_lead`.
- No pooling across loads is assumed for the label beyond this: an event is an event at whatever load it happened; the loads of the events are listed, and the leads are listed per event (rule H).

### What was known when the levels were fixed
- **The KV onsets themselves are on record:** `gate.kv_onset` is the rule `gate.surge_run` applied to these runs for the surge tables (decisions.md 2026-11-10 [CORR]), so each event's onset time and the arrival surge before it are published; A's lead over the KV onset is therefore known, and A leading latency is close to known.
- **Which runs tipped is on record.** Three of REG-12's controls did not recover (RUN(REG-12's five controls, gate.reg12_table)); REG-13's sweep went cold at λ = 2.6, 2.8 and 3 (RUN(REG-13's five runs, gate.reg13_table)); REG-16's control went cold at 4080 to 4380 s (RUN(20261110-122001_stage2_control_l1pl350cl_r2.2_long_s14, gate.reg16_table)). So about seven events are expected, and the rule of five was fixed knowing that.
- **Timelines at 300 s resolution** of REG-13's and REG-16's runs are printed in their [RESULT] entries. They cannot order onsets that are tens of seconds apart.
- **Not computed by anyone:** any of the six signals on a 5 s grid, any onset, any lead, any false alarm.

### Prediction (BELIEF)
Six or seven events; H and U move before latency in most of them, by 5 to 60 s, so `within_window` or `mixed` is the likeliest label for both. The arrival rate leads everything, because these collapses followed arrival surges. So `no_usable_cache_lead` ≈ 0.8 (the leads are inside the window, A warns earlier, or the queue moves with the cache); `cache_signal_leads` ≈ 0.1; no label for want of events ≈ 0.1. False alarms of H and U on the quiet runs: under 1 per hour ≈ 0.7.

### Decision under each outcome (rule A1)
- **`cache_signal_leads`:** K5 may stay as a claim, worded as a retrospective measurement: the signal, its median and least lead over latency and over the queue, n events, the false alarms per hour and the quiet hours behind them, and A's lead beside it.
- **`no_usable_cache_lead`:** K5 leaves the claims. The paper's limitations say what was found: which signal moved first, and that watching arrivals or the queue warned as early.
- Either way no run is started, stopped or sized by this.

### Reported, never judged
Per event: its load, KV onset, reference window, every level and onset, both leads of every signal. Per quiet run: its hours and the onsets each rule gave. N and Q as warners. The events and quiet runs left out, with the reason.

### Alternatives to state with any result
1. **The arrival surge comes first.** A is in the table for that reason; a cache lead that is shorter than A's is not a contribution.
2. **A lead can be the levels, not the order.** H's floor is 0.06 and L's is the 1.0 s SLO; a sensitive level crosses earlier whatever the mechanism. This analysis cannot separate that; the levels and each signal's reference mean and SD are reported so a reader can see how far each level sits from its noise.
3. **The trailing window.** A 30 s mean delays a step by up to 30 s and a ramp by less; signals that step (H) and signals that ramp (L) are not delayed alike. The 30 s floor on a lead covers the step case; a ramp in latency against a step in H can still give a lead above 30 s that is the ramp's shape.
4. **Short references.** REG-13's runs last 900 s and tip early, so their reference windows are 120 to 360 s long; REG-16's is about an hour.
5. **Overload, not a tip.** REG-12's controls and REG-13's runs at 2.6 and above sit at or above the closed-loop warm capacity (FILE(docs/claims.md:45)); there the order of signals is the order of an overload.
6. **Few events.** With about seven events, one event decides between `leads` and `mixed`.

### Not in this registration
Critical slowing down (variance and autocorrelation before the onset). Nothing is computed or claimed about it.

### Stopping rule
Computed once, after this registration is approved: `uv run python -m analysis.k5 k5`. The command refuses when `analysis/` or `tests/` holds a modified or untracked file; `uv run pytest` passes before. No second level, window, grid, hold time or lead floor. If the command raises, a fix outside the judged path (`K5`, `signals`, `reference`, `levels`, `crossings`, `event`, `quiet`, `_lead_label`, `judge`, `candidates`, `k5_table`, and `gate.kv_onset`, `load.find_runs`, `margin.is_burst_request`) is logged as a [CORR] before the table is read; a fix inside it needs rule F and an owner-proxy pass before the rerun.

### Definitions (rule J)
With the registration, `docs/definitions.md` gains: signal onset (`k5.crossings`), lead (`k5.event`), false alarms per hour (`k5.quiet`, `k5.judge`).

### Cost
0 GPU h; under a minute of CPU.

### Code and tests
`analysis/k5.py` (`signals`, `reference`, `levels`, `crossings`, `event`, `quiet`, `judge`, `candidates`, `k5_table`); `tests/test_k5.py`, 10 tests on hand-made runs: the signals of a steady server; an event's onsets and both leads; an arrival surge as the trivial warning; runs that are not events and why; false alarms from a dip that lasts and none from one that does not; an onset counted once and re-armed; every label, the false-alarm limit, arrivals warning earlier, the queue moving first; signals that step together do not lead; the candidates; the table. No run folder was read while writing this draft or its code.
