## 2026-11-13 · [REG] REG-23 (K5): do the cache signals warn before latency and the queue, and earlier than watching arrivals? Onsets on the six runs that went cold without a trigger, false alarms on the runs that stayed warm; a retrospective reading (0 GPU h)

- **ID:** REG-23. An analysis of existing runs, 0 GPU h. Draft 5, the second sent to review (round 1 on draft 4: rule F NOT READY, CA1–CA6; owner-proxy APPROVE with conditions CB1–CB8; both saved verbatim in `docs/drafts/reviews-2026-11-13/rulef-reg23-draft4-r1.md` and `proxy-reg23-draft4.md`). What changed and why is listed at the end ("Changes from draft 4"). Code: `analysis/k5.py`, `tests/test_k5.py` (15 tests), at commit `63e8c65`.
- **What this is, in one line:** a retrospective reading that decides whether K5 stays in the paper as a claim, and in which words, or becomes one sentence in the limitations. It is not called a test below.
- **This registration covers computing and reporting only.** The edit to `docs/claims.md` and the paper that follows from it needs its own decision.
- **Question:** when the warm server goes cold with no trigger, do the hit rate (H) and the recomputed prefill rate (U) move before latency (L) and the waiting line (Q) do, with few false alarms, and earlier than the arrival rate (A) moves?
- **Claim:** K5 (`docs/claims.md`): "recomputed prefill tokens per second and the hit rate change before latency and queue length do; the contribution is the measured lead time."

### How this differs from what was asked
- **From the claim's stated test.** `docs/claims.md` says "a registered onset rule per signal, applied to stuck runs" (FILE(docs/claims.md:82)). Burst runs are not computed here: in a burst run the trigger itself raises the recomputed prefill rate and the running batch at once, so a "lead" there is the shape of the burst, not a warning. The events are the runs that went cold with no trigger. That population still holds stuck runs: REG-12's seed-5 control and REG-16's control went cold, full and backlogged, and REG-12's seed-4 control was `stuck` by the thresholds but only partly degraded (FILE(docs/decisions.md:2477), FILE(docs/decisions.md:2478); decisions.md 2026-11-10 [RESULT] REG-16). So the departure is the burst runs, not the stuck state.
- **From the owner's start prompt** (`docs/FABLE_PROMPT.md`, untracked, item 4 of its work list, FILE(docs/FABLE_PROMPT.md:105)): it asks for "the onset rules and a critical-slowing-down test (rising variance and lag-1 autocorrelation of hit rate, uncached prefill and queue before the tip), then compute on the stuck runs and the no-trigger tips (REG-12 s4/s5, REG-13 r2.6–3, REG-16)". Two parts are left out:
  - **The burst runs,** for the reason above.
  - **Critical slowing down.** Every one of these tips followed an external 120 s arrival surge (decisions.md 2026-11-10 [CORR]), so rising variance before the onset would be the surge's own variance; and three of the six references are only about 120–360 s long (below). Any later CSD reading of these runs needs its own [REG] and lists this result as known.
  - Both departures are the delegate's and are listed for the owner in `agent/FOR_AUTHOR.md` with this entry.

### Events and quiet runs (`k5.candidates`, `k5.event`, `k5.quiet`)
- **Candidates** (`k5.K5["runs"]`, 19 folder names): every closed-loop L1 run at 350 W without a trigger made before REG-19: the controls of REG-11, REG-12, REG-14, REG-16, REG-17 and REG-18 and REG-13's cache-on sweep. A candidate must be valid; the function raises if a folder is missing. `20261109-134250_stage2_control_l1pl350cl_r2.4_s6` is invalid (FILE(docs/decisions.md:2451)) and drops out, so 18 are expected. REG-19's controls are withheld and are not candidates.
- **An event** is a candidate whose KV pool fills: `gate.kv_onset` is finite (the first scrape whose trailing 60 s mean KV is ≥ 0.9, the rule `gate.surge_run` uses for `tipped`).
- **A quiet run** is a candidate that never reaches that onset.
- **Left out, with the reason:** an event whose reference window is shorter than 120 s ("no reference"); a run with a missing metric or a counter that goes down.

### Signals (`k5.signals`)
Server-side only, what an operator has: trailing means over 30 s on a 5 s grid, from the 1 s scrapes.
- **H:** counter hit rate, Δhits ÷ Δqueries.
- **U:** recomputed prefill tokens per second, (Δprompt tokens − Δcached tokens) ÷ time.
- **Q:** mean requests waiting. **N:** mean requests running.
- **L:** latency, the server's mean time to first token, Δsum ÷ Δcount of `vllm:time_to_first_token_seconds`. Two levels are applied to this one series (below): L with the 1.0 s SLO as its floor, and **Lr**, relative to the warm mean, for latency's first move.
- **A:** session requests **sent** per second over a trailing 120 s (`t_sent`, what reaches the server). It is the trivial warning: every no-trigger collapse on record followed a 120 s surge of **planned** arrivals (decisions.md 2026-11-10 [CORR]).
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
  | L | above max(mean + 4 SD, 1.0 s) | 1.0 s is the SLO: L's onset is an SLO breach |
  | Lr | above mean + max(4 SD, 0.5 × mean) | U's rule, applied to latency: its first move (rule F CA1) |
  | A | ≥ 3.2 req/s | `gate.SURGE`'s tip reading, a data-chosen readout (below) |

- **Onset** (`k5.crossings`): the first grid time after the reference window from which the signal stays beyond its level for 15 s (at every grid time of that stretch).
- **Leads of a warner X:** over latency, onset(L) − onset(X) (`leads`) and onset(Lr) − onset(X) (`leads_rel`); over the queue, onset(Q) − onset(X); over arrivals, onset(A) − onset(X) (`lead_over_A`), per event. Where A has no onset in an event, X counts as earlier there (+∞, "A silent"); where X has none, the event gives no pair.
- **A lead counts only above 30 s, the length of the trailing window.** Signals that step at the same instant cross their levels at different times: a trailing mean crosses after window × (level − before) ÷ (after − before), which is about 2 s for H (30 × 0.06 / 0.84), 4 s for U, 6 s for Q and 9 s for L for steps of the size seen in cold runs (DERIVED, with the cold values of the published spans). Left alone, that would hand H and U a "lead" over latency of a few seconds with nothing behind it (FILE(tests/test_k5.py), `test_signals_that_step_together_do_not_lead`). The same argument applied to A's longer window: a step from λ 2.4 to 3.5 crosses 3.2 after 120 × 0.8 / 1.1 ≈ 87 s (DERIVED, rule F CA2), so X must beat A by more than A's 120 s window.

### Judged (`k5.judge`)
- **Per signal and comparator (`_lead_label`):** `too_few` below 5 events with both onsets (checked first); `leads` if every one of them has a lead above 30 s; `no_lead` if the median lead is ≤ 0; `within_window` if the median is above 0 and not above 30 s; otherwise `mixed`.
- **False alarms:** the same rules on the quiet runs, each re-referenced on its own [240, 540) s, scanned from 540 s to the end of arrivals. Per signal: onsets, onsets per hour, the one-sided 95 % Poisson upper bound of that rate (`stats.poisson_rate_upper`), and the **alarm share**, the share of scanned grid time inside a stretch beyond the level that lasts at least 15 s (`k5.in_alarm`), so that one alarm that never ends is not counted as one event (rule F CA4).
- **Usable:** a signal that `leads` both latency (L) and the queue, whose false-alarm upper bound is below 1 per hour, and whose alarm share is below 0.05.
- **For H and U, the reasons they fail** (`k5.REASONS`, a fixed list, in this order): `too_few_events` (fewer than 5 pairs over L or over the queue); `too_few_quiet_hours` (0 alarms would still give an upper bound ≥ 1 per hour); `latency:no_lead|within_window|mixed`; `queue:no_lead|within_window|mixed`; `false_alarms`; `alarm_share`; `arrivals_not_compared` (A has an onset in fewer than 5 events); `arrivals_first` (the median paired lead over A is not above 120 s); `slo_only` (fewer than 5 pairs over Lr, or their median lead not above 30 s).
- **K5's label:**
  - `too_few_events` if both H and U have `too_few_events`;
  - `cache_signal_leads` if H or U fails nothing;
  - `leads_slo_only` if H or U fails only `slo_only`;
  - `no_usable_cache_lead` otherwise.
- No pooling across loads is assumed for the label beyond this: an event is an event at whatever load it happened; the loads of the events are listed, and the leads are listed per event (rule H). False alarms are also reported per load.

### What was known when the levels were fixed
- **The events are known by name and count.** `gate.surge_table`, the same `kv_onset` rule, gives exactly six no-trigger tips among the closed-loop L1 350 W runs before REG-17: REG-12's controls of seeds 4 and 5, REG-13's runs at 2.6, 2.8 and 3.0, and REG-16 (FILE(docs/decisions.md:3423)). REG-17's control did not tip (FILE(docs/decisions.md:3540)) and none of REG-18's four did (FILE(docs/decisions.md:3747)). So six events are expected, and the rule of five was fixed knowing that.
- **The KV onsets known before this entry:** REG-16's is 4433 s (FILE(docs/decisions.md:3422)), so its reference is [240, 4193) s, 3953 s long. The other five are not in any doc and are not computed before this entry, because they are part of this registration's computation. What is published bounds them: REG-13's backlogs began at 842 s (λ = 2.6), 810 s (2.8) and 608 s (3.0) (FILE(docs/decisions.md:2642), FILE(docs/decisions.md:2643), FILE(docs/decisions.md:2644)). If each KV onset lies near its backlog start (BELIEF), their references are about 362, 330 and 128 s long (DERIVED: onset − 480).
  - **`ref_min_s` = 120 is a knife-edge for REG-13's λ = 3 run**, and was set knowing that. It is not changed. If that event has no reference, five events remain, and every one of them must then lead above 30 s for `leads`.
  - REG-12's seed 4 and 5 controls ran 2580 s; their onsets are not published. Seed 4's control passed a 3.32 planned peak without tipping and tipped later after 3.49 (FILE(docs/decisions.md:3423)).
- **The quiet runs and their hours, from the configs alone** (DERIVED; `duration_s` 2580 s for the controls, 900 s for REG-13's sweep, `configs/stage2_control_l1pl350cl_*.yaml`, `configs/base.yaml:29`): 12 quiet runs if every valid candidate other than the six is quiet: 10 controls × (2580 − 540) s + 2 sweep runs × (900 − 540) s = 5.87 h; by load, λ = 2.4: 2.37 h (5 runs), 2.2: 0.57 h (1), 2.0: 2.93 h (6). With the upper-bound rule, 0 alarms give 0.51 per hour, 1 alarm 0.81, 2 alarms 1.07 (DERIVED, `stats.poisson_rate_upper(n, 5.87)`): **at most one false alarm per signal passes.** The events are at λ 2.2–3.0, the quiet hours mostly at 2.0 and 2.4.
- **Known quiet-run behaviour:** REG-12's seed-6 control lost 0.081 of hit rate by its end window (FILE(docs/decisions.md:2479)), so H very likely has at least one false alarm there. REG-18's seed-4 control went through a 3.217 planned surge without tipping (FILE(docs/decisions.md:3753)), so A may alarm there.
- **A's level and A's statistic.** 3.2 is one of `gate.SURGE`'s readout settings, "chosen with the data in view" (FILE(analysis/gate.py:1342)), 0.04 below the lowest known tipping peak, 3.24. Those peaks are on `t_planned` (FILE(analysis/gate.py:1385)); A here is the sent rate, which closed-loop release delays (a later turn is sent at the previous turn's end plus its gap, FILE(harness/loadgen.py:158)), so A's crossings in these events are **not** known. Each event's peak A over [b, KV onset) on both `t_sent` and `t_planned` is reported. The comparison with A was added knowing that every event followed a surge.
- **Timelines at 300 s resolution** of REG-13's and REG-16's runs are printed in their [RESULT] entries. They cannot order onsets that are tens of seconds apart.
- **REG-22's control readout** (`c2.control_readout`, REG-22 draft 15, in review) prints, for the same-seed control of each stuck batch-1 burst run (the controls of REG-11, REG-12, REG-14, REG-17 and REG-18, candidates here), the reuse, the session uncached rate, N and KV per 300 s span from about 1380 s on, and the control's verdict. At 300 s resolution it cannot order onsets tens of seconds apart. **Any output on a candidate run computed between draft 4 and this entry, REG-21's or REG-22's batch 1 included, is listed here with its file and commit when the entry is appended**, and counts as known when the levels were fixed.
- **Not computed by anyone:** any of the signals on a 5 s grid, any onset, any lead, any false alarm. The transcript search (`docs/probe/20261113_transcript_search/search.py`, rerun at the append) finds no run of `analysis.k5`; its one `k5` hit is this session's text edit of k5.py's source, where the import sits inside a string. The round-1 reviewers ran `k5` only on hand-made data.

### Prediction (BELIEF)
Six events, perhaps five (the knife-edge). H and U move before latency's SLO breach in most events, by 5 to 100 s; against Lr and the queue the leads shrink. A on the sent times crosses 3.2 in fewer than five events about as often as not. So: `no_usable_cache_lead` ≈ 0.8 (first reasons most likely `latency:within_window` / `mixed`, `queue:*`, `false_alarms` or `arrivals_*`); `too_few_events` ≈ 0.12; `leads_slo_only` ≈ 0.04; `cache_signal_leads` ≈ 0.04.

### Decision under each outcome (rule A1)
- **`cache_signal_leads`:** K5 may stay, worded as a retrospective measurement on n no-trigger cold onsets, k of them REG-13's 900 s sweeps planned above the measured throughput, each following a 120 s planned-arrival surge of 3.24–3.49 req/s, above the closed-loop warm capacity as REG-13's rule reads it (no collapse without such a surge is on record). The levels were fixed with the events known. It reports the signal, its median and least lead over latency's first move (Lr), over the 1.0 s TTFT breach (L) and over the queue, k of n above 30 s with the Clopper–Pearson bounds, the false alarms per hour with their upper bound over the quiet hours, and A's paired lead beside it, with A's level found on these runs.
- **`leads_slo_only`:** K5 may stay only reworded as "before the mean TTFT passes the 1.0 s SLO", with latency's first move (Lr) reported beside it and the same caveats.
- **`too_few_events`:** K5 leaves the claims as not testable on the runs on record (n events). The limitations say "not measured", not "no lead".
- **`no_usable_cache_lead`:** K5 leaves the claims. The limitations sentence gives, for H and for U, the first reason the table shows, worded as fixed here:
  - `too_few_events`: "too few no-trigger collapses on record to measure it (n)";
  - `too_few_quiet_hours`: "the runs that stayed warm were too short to show fewer than one false alarm per hour";
  - `latency:no_lead` / `queue:no_lead`: "it did not move before latency / the waiting line (median lead ≤ 0)";
  - `latency:within_window` / `queue:within_window`: "it moved with latency / the waiting line, within one 30 s averaging window";
  - `latency:mixed` / `queue:mixed`: "it moved more than 30 s before latency / the waiting line in k of n collapses, not in all";
  - `false_alarms`: "on the runs that stayed warm it also crossed its level, k times in h hours (upper bound u per hour)";
  - `alarm_share`: "on the runs that stayed warm it stayed beyond its level for a share s of the time";
  - `arrivals_not_compared`: "the sent arrival rate crossed 3.2 req/s in fewer than five collapses, so it was not compared with watching arrivals";
  - `arrivals_first`: "watching arrivals warned as early (median paired lead m s, not above A's 120 s window); A's level 3.2 was found on these same runs (decisions.md 2026-11-10 [CORR])".
- K5 is also "kept only if K1–K3 leave room" (FILE(docs/claims.md:83)); that decision is separate and not taken here.
- Either way no run is started, stopped or sized by this.

### Reported, never judged
Per event: its load, KV onset, reference window, every level and onset, every lead (L, Lr, queue, A), which onsets fall on the scan's first grid time (`at_scan_start`: there the signal was already beyond its level, "already up", not "warned"; rule F CA-O1), which signals are still beyond their level at the KV onset (`beyond_at_kv`, a transient that recovered is not a warning; CA-O2), and the peak 120 s arrival rate over [b, KV onset) by `t_sent` and by `t_planned`, of the same rows (`gate.surge_run` also drops rows without a turn and uses its own grid, so its published peaks may differ slightly). Per quiet run: its load, hours, onsets and in-alarm seconds per signal, and in the [RESULT] its published verdict. Per signal: k of n above 30 s per comparator with the one-sided 95 % Clopper–Pearson upper bound (rule H) and lower bound; false alarms per load with their upper bound; A's own false alarms. The number of onsets at the scan start. N and Q as warners. The events and quiet runs left out, with the reason.

### Alternatives to state with any result
1. **The arrival surge comes first.** A is in the table for that reason, compared per event and against its own window; a cache lead that does not beat it is not a contribution.
2. **A lead can be the levels, not the order.** H's floor is 0.06 and L's is the 1.0 s SLO; a sensitive level crosses earlier whatever the mechanism. Lr separates the SLO floor from latency's first move (rule F CA1); the floors of H and U remain, and the levels and each signal's reference mean and SD are reported so a reader can see how far each level sits from its noise.
3. **The trailing window.** A 30 s mean delays a step by up to 30 s and a ramp by less; signals that step (H) and signals that ramp (L) are not delayed alike. The 30 s floor on a lead covers the step case; a ramp in latency against a step in H can still give a lead above 30 s over L that is the ramp's shape. Lr's lower level shortens that.
4. **Short references.** REG-13's runs last 900 s and tip early, so their reference windows are about 120 to 360 s long; REG-16's is 3953 s.
5. **Overload, not a tip.** REG-12's controls and REG-13's runs at 2.6 and above sit at or above the closed-loop warm capacity as REG-13's rule reads it (FILE(docs/claims.md:45)); REG-16 tipped after a 3.45 surge. Every event followed such a load; there the order of signals is the order of an overload, and no event tests a collapse below it (rule F CA6).
6. **Few events.** With five or six events, one event decides between `leads` and `mixed`, and between `too_few` and a label.
7. **Latency is recorded late.** L is the time to the first token, recorded when that token arrives, so for queued requests it lags by their wait. Any signal recorded at scheduling time leads it by construction. The lead over the queue is the guard (owner-proxy CB4).
8. **Hit-rate counting in a backlog** (BELIEF, open question): if vLLM counts prefix-cache queries again for a waiting request that fails to allocate, H is tied to Q in a backlog. Not checked against the pinned source.

### Not in this registration
Critical slowing down (variance and autocorrelation before the onset); burst runs. Nothing is computed or claimed about them.

### Stopping rule
- Computed once, after this registration is approved: `uv run python -m analysis.k5 k5`, its output saved as `docs/probe/reg23/k5_<UTC stamp>.txt` and committed alone. The command refuses when `analysis/` or `tests/` holds a modified or untracked file; `uv run pytest` passes before.
- No second level, window, grid, hold time, lead floor, false-alarm rule or event list.
- **Freeze (owner-proxy CB7, rule F CA-O3).** The frozen files are every file the command imports, by the import closure of `analysis/k5.py` at this entry's commit (function-level imports included; computed with Python's `ast`), and the two that fix the environment: `analysis/__init__.py`, `derived.py`, `floor.py`, `gate.py`, `k1.py`, `k3.py`, `k3w.py`, `k5.py`, `load.py`, `margin.py`, `modelf.py`, `modelf_sim.py`, `stats.py`, `tables.py`, `withheld.py` (all under `analysis/`), `harness/__init__.py`, `checks.py`, `config.py`, `recorder.py`, `run.py`, `workload.py` (under `harness/`), `pyproject.toml`, `uv.lock` (23 files; REG-21's 22 and `analysis/k5.py`). Let E be this entry's commit and R the commit at which the command runs. The [RESULT] shows the verbatim output of `git log --oneline E..R -- <the 23 files>` and of `git status --porcelain`. If either prints anything, a rule F review and an owner-proxy pass come before the table is read.
- If the command raises, a fix is a change to a frozen file and goes through rule F and an owner-proxy pass before the rerun, and is logged as a [CORR].
- **No change outside `analysis/k5.py` and `tests/test_k5.py`:** REG-21 and REG-22 (in review) freeze the other 22 files from their entry commits, so a fix that REG-23 needs in a shared function is made as a new function in `analysis/k5.py`.

### Definitions (rule J)
With the registration, `docs/definitions.md` gains: signal onset (`k5.crossings`); lead over latency, over latency's first move, over the queue and over arrivals (`k5.event`); false alarms per hour and their upper bound, and alarm share (`k5.quiet`, `k5.in_alarm`, `k5.judge`).

### Cost
0 GPU h; under a minute of CPU.

### Code and tests
`analysis/k5.py` (`signals`, `reference`, `levels`, `crossings`, `in_alarm`, `event`, `quiet`, `_lead_label`, `_reasons`, `judge`, `candidates`, `k5_table`); `tests/test_k5.py`, 15 tests on hand-made runs: the signals of a steady server; an event's onsets and both leads; an arrival surge as the trivial warning; runs that are not events and why; false alarms from a dip that lasts, none from one that does not, and the time a lasting alarm holds; an onset counted once and re-armed; every label, the reasons and the Clopper–Pearson bounds; false alarms judged on the upper bound and the alarm share, per load; arrivals compared per event and against their own window (rule F's CA2 trace); a lead over the SLO alone (`leads_slo_only`); latency that ramps from the cache step (rule F's CA1 trace: H 905 s, L 1005 s, Lr 925 s, Q 1005 s); the reported flags (scan start, recovery before the KV onset, planned against sent arrivals); signals that step together do not lead; the candidates; the table. No run folder was read while writing this draft or its code.

### Changes from draft 4 (round 1)
- **CA1** (rule F, required): comparator Lr, `leads_rel`, label `leads_slo_only` with its decision; alternative 2 rewritten (the SLO floor is now separated). In code.
- **CA2** (rule F) and **CB3** (owner-proxy): A compared per event (`lead_over_A`, A silent = X earlier), X must beat A by more than 120 s, and the comparison is made only if A has an onset in at least five events (`arrivals_not_compared` otherwise; the loophole `math.isnan(a) or` is gone). A's own false alarms are reported. In code; CB3 said a code fix goes back to rule F, which this round is.
- **CA3** (rule F): `too_few` checked first; label `too_few_events` with its own decision ("not testable", not "no lead"); `judge` returns the failure reasons from the fixed list `REASONS`, and the limitations sentence for each reason is fixed above. The draft-4 sentence "watching arrivals or the queue warned as early" is gone (also CB6).
- **CA4** (rule F): `alarm_share` (`k5.in_alarm`) and its limit 0.05; false alarms with their Poisson upper bound, overall and per load; k of n with Clopper–Pearson bounds. **CA-O4 adopted** (optional): false alarms judged on the upper bound, not the point rate. It was adopted knowing the quiet hours (5.87 h, DERIVED from the configs) and REG-12 seed 6's hit drop, which together mean at most one false alarm per signal passes; it can only make a positive label harder.
- **CA5** (rule F) and **CB3**: the A bullet under "What was known" replaced (data-chosen 3.2, planned against sent, crossings not known, the comparison added knowing every event followed a surge); peak A on `t_sent` and `t_planned` per event, in code.
- **CA6** (rule F) and **CB5** (owner-proxy): the `cache_signal_leads` decision names the overload/surge population and that no collapse without a surge is on record.
- **CB1:** "How this differs from what was asked" adds the start prompt's two parts left out (CSD, burst runs) and why, and that the population still holds stuck runs; both go to FOR_AUTHOR.
- **CB2:** the event count is the published six (no "about seven"); REG-16's onset and reference length are given; the other five onsets are **not** given, because no doc holds them and computing them is this registration's computation; what the published backlog starts bound is given instead, with the `ref_min_s` knife-edge, unchanged; the prediction's "no label" belief is replaced by `too_few_events` with the knife-edge as its main route; REG-12 seed 6's 0.081 hit drop is listed as known. This departs from CB2's letter ("write the six KV onsets from the published values") because only one is published.
- **CB4:** alternative 7; L's onset is called an SLO breach throughout, and the `leads_slo_only` wording is the proxy's.
- **CB6:** the `no_usable_cache_lead` decision gives the reason the table shows, with each sentence fixed above, including `arrivals_not_compared`.
- **CB7** and **CA-O3:** REG-23's own whole-file freeze (23 files) with the two commands in the [RESULT]; the "known" bullet widened to any output on a candidate run between draft 4 and the entry.
- **CB8** (in the [RESULT]): k of n with Clopper–Pearson bounds (now in code), each quiet run's verdict beside its alarms, the number of onsets at the scan start (now in code).
- **CA-O1, CA-O2 adopted** as reported flags (`at_scan_start`, `beyond_at_kv`); neither is judged.
- **Added:** alternative 8, the proxy's unchecked point on hit-rate counting in a backlog, as a BELIEF for `docs/open-questions.md`.
