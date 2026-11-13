# K5 (lead times and early warning): design note for the registration (not a registration)

Written 2026-11-13 so that the design survives a context change. Nothing computed. To become `docs/drafts/reg_k5_draft1.md` + `analysis/k5.py` + tests, then rule F, owner-proxy, [REG].

**Events.** Natural departures from the warm state, no burst: every valid closed-loop L1 run at 350 W without a trigger (controls and cache-on sweep runs; sealed runs excluded) whose KV onset is finite (`gate.kv_onset`, the rule `gate.surge_run` calls `tipped`). Expected: REG-12's controls of seeds 4, 5 (6?), REG-13 at 2.6, 2.8, 3.0, REG-16. Burst runs are reported apart: their onset is the trigger's.

**Signals** (server-side, what an operator has; trailing 30 s on a 5 s grid from the 1 s scrapes): H counter hit rate (Δhits / Δqueries); U recomputed prefill tokens/s (Δprompt_tokens − Δcached); Q mean waiting; N mean running; server TTFT mean (Δsum / Δcount of `vllm:time_to_first_token_seconds`); and A, the session request rate over a trailing 120 s (the trivial warning: K4's surge).

**Reference window** per event: [240 s, KV onset − 240 s), at least 120 s long; otherwise the event is listed as "no reference".

**Onset rules** (to be fixed in the [REG]): H below reference mean − max(4 SD, 0.06); U above mean + max(4 SD, 0.5 × mean); Q ≥ 1; TTFT above max(mean + 4 SD, 1.0 s, the SLO); A ≥ 3.2 req/s (`gate.SURGE`'s tip reading). An onset must hold at t and at t + 15 s.

**Lead** of X = onset(TTFT) − onset(X). Statement per signal: median lead and k of n events with a positive lead. Label "leads" only if every event with both onsets (at least 5) has a positive lead; "no_lead" if the median is ≤ 0; else "mixed".

**False alarms.** The same rules on runs that never tipped (REG-14, REG-17, REG-18 controls; REG-12 controls of seeds 2, 3), reference [240, 540) s, scanned from 540 s: onsets per hour not followed by a KV onset within 600 s. A lead is called usable only below one false alarm per hour.

**Critical slowing down.** Per event, on 10 s bins of H, U, Q in [onset − 360, onset − 60): variance and lag-1 autocorrelation, second half minus first half. The same on [1200, 1500) of the never-tipped controls as the null. Reported as counts; no claim unless every event rises and at most a quarter of the null windows do.

**The honest comparator.** If A leads TTFT by more than H and U do, cache signals add nothing over watching arrivals; the paper says so.

**Decision (rule A1).** "leads" with a usable false-alarm rate: K5 stays as a claim with its measured lead. Anything else: K5 leaves the claims and is one sentence in the limitations.

**Not blind.** Timelines of REG-13 and REG-16 were printed in their [RESULT] entries (300 s windows); no onset at 5 s resolution has been computed.
