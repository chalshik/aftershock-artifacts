# rulef-reg23-draft4-r1 (rulef-reg23-r1), verbatim

Saved by the agent from the teammate message received in the main session transcript, 2026-11-13 between 12:42 and 12:51 UTC (the senders' idle notifications). Item names as given by the reviewer (prefixes BA, BB, BC, BD, CA, CB were assigned in the review prompts).

---

Rule F review of REG-23 draft 4 (bundle reg23_r1; code aa77e9c, identical to the bundle and unchanged at HEAD): NOT READY. Six required items (CA1–CA6), four optional.

Checks: the bundle files equal `git show aa77e9c:` for both files. `uv run pytest tests/test_k5.py -q` gives 10 passed. The traces below ran on modified `tests.test_k5.fake_run` data in a scratchpad outside the repo; no run folder was read. Code against text: the signals, reference window, levels, the 15 s forward hold, the leads and the `_lead_label` order all match. Two wording gaps. "The same levels on the quiet runs" really means the same rules, re-referenced on [240, 540) (FILE(analysis/k5.py:196)). The text never says that A having no onset in any event counts as H/U being earlier (FILE(analysis/k5.py:239)).

**CA1. The latency comparator's SLO floor creates leads.** Trace (DERIVED, synthetic): H and U step at 900 s. L starts rising at the same instant and ramps from 0.2 to 3.0 s over 300 s. Q steps at 1000 s. Onsets: H 905, L 1005 (the 1.0 s floor, FILE(analysis/k5.py:146)), Q 1005. Five such events, no A onset, 5.3 quiet hours: `leads`/`leads`, K5 = `cache_signal_leads`. Yet L at mean + 4 SD crosses at 905. K5's text says "change before latency" (FILE(docs/claims.md:80)), so this label is wrong for the claim. Alternative 2 says the confound "cannot be separated". It can.
Fix (in k5.py): add the comparator L_rel = mean + max(4 SD, 0.5 × mean), the same rule as U. Compute `leads_rel` beside `leads`. `cache_signal_leads` then also needs a median lead over L_rel above 30 s. Otherwise the label is `leads_slo_only`, with this decision: "K5 may stay only reworded as 'before the mean TTFT passes the 1.0 s SLO', with latency's first move reported."

**CA2. The comparison with A is unpaired and ignores A's longer window.** Trace (synthetic, `judge`): five events with H leads 100, 100, 100, 40, 40. A has onsets only in the last two, 90 s each. H's median is 100 against A's 90, so the label is `cache_signal_leads`, although A warned 50 s before H in every event where A warned at all. Also, A is a trailing 120 s rate while H is a 30 s mean. A step from λ 2.4 to 3.5 crosses 3.2 after 120 × 0.8/1.1 ≈ 87 s (DERIVED), so H can come out "earlier than A" from the window alone. That is the registration's own 30 s argument, applied to the longer window.
Fix: in `event`, store `lead_over_A = onset(A) − onset(X)` per event. NaN onset(A) is reported as "A silent" and counted as X earlier. `cache_signal_leads` needs the median of that paired lead above `arr_roll_s` (120 s). Report A's false alarms beside it; A is not exempt from the reporting.

**CA3. "Too few events" is reported as if it were a measured failure.** Trace (synthetic): four events give `too_few`, which gives `no_usable_cache_lead`. K5 then leaves the claims with the sentence "watching arrivals or the queue warned as early" (registration lines 60–61), which no data showed. The prediction lists a third outcome ("no label for want of events ≈ 0.1") that the code cannot produce. `no_usable_cache_lead` is also reached through false alarms, `mixed` or `within_window`, and each of these needs a different limitation sentence.
Fix: label `too_few_events` when H and U each have fewer than 5 paired events on either comparator. Decision: "K5 leaves the claims as not testable on the runs on record (n events)". `judge` returns the reason for failure of H and U (within_window / mixed / queue first / arrivals first / false alarms / too few), and the limitations sentence is picked from that list, fixed now.

**CA4. The false-alarm rule misses a persistent alarm, and rule H is unmet.** Trace (synthetic): a quiet run whose H falls by 0.1 at 600 s and never returns counts as one alarm (FILE(analysis/k5.py:164,201)). Take 4 of 9 quiet controls in alarm for the whole run: 4 / (9 × 0.567 h) = 0.78/h, so the signal is `usable`. Quiet hours ≈ 9 × (2580−540)/3600 + 2 × (900−540)/3600 ≈ 5.3 h (DERIVED from the resolved configs, assuming the registration's seven events). Five alarms pass "< 1/h", but their one-sided 95 % Poisson upper bound is 1.98/h (DERIVED, `stats.poisson_rate_upper(5, 5.3)`). `k_above_window`/`n` carries no Clopper–Pearson bound; 5 of 5 has a one-sided 95 % lower bound of 0.55 (DERIVED). The quiet hours are mostly λ = 2.0 runs, while the events are at 2.2–3.0.
Fix: report `alarm_share` (the share of scanned quiet grid time held beyond the level). `usable` also needs `alarm_share < 0.05`. Report false alarms per load with the Poisson upper bound, and `cp_upper` with every k of n.

**CA5. "What was known" is incomplete and overstates what is known about A.**
(i) 3.2 is one of `gate.SURGE`'s readout thresholds, which gate.py says were "chosen with the data in view" (FILE(analysis/gate.py:1342-1344)). It sits 0.04 below the lowest known tipping peak, 3.24 (docs/status.md headline; decisions.md 2026-11-10 [CORR]).
(ii) Those peaks are on `t_planned` (FILE(analysis/gate.py:1385)), but A uses `t_sent` (FILE(analysis/k5.py:117)). In closed loop, a later turn is sent at the previous turn's end plus the gap (FILE(harness/loadgen.py:158-160)). So whether A crosses in each event is not known, contrary to "A leading latency is close to known".
(iii) The comparison with A was added knowing that every event followed a surge.
Replacement bullet: "A's level 3.2 is a data-chosen readout of gate.SURGE, set 0.04 below the lowest known tipping peak of the planned rate. A here is the sent rate, which closed-loop release delays, so A's crossings in these events are not known. Each event's peak A on both t_sent and t_planned over [b, KV onset) is reported."

**CA6. Every event is an overload, and the decision text hides that.** Six of the seven expected events are at λ ≥ 2.4, the closed-loop warm capacity (FILE(docs/claims.md:45)). REG-16 tipped after λp 2.46–2.71 (status.md). No event tests a collapse below capacity, so `cache_signal_leads` would place a paper claim on overload collapses. Replacement for the decision under `cache_signal_leads`: "… worded as a retrospective measurement on collapses that followed load at or above the warm capacity; no event below it is on record."

**Optional.**
- CA-O1: an onset at the scan start b is left-censored (FILE(analysis/k5.py:164)). Q's absolute level of 1 makes onset(Q) = b in any overload event whose queue is already up, so every lead over the queue is ≤ 0 by construction. Flag `at_scan_start` per onset and say "the queue was already up", not "warned".
- CA-O2: a first onset that recovers before the KV onset is a transient that inflates the lead. Flag whether the signal is still beyond its level at the KV onset.
- CA-O3: the [RESULT] should quote an empty `git diff aa77e9c --` for k5.py, gate.py, load.py, margin.py and withheld.py. `_dirty` is imported from REG-21's `k3w` (FILE(analysis/k5.py:271)).
- CA-O4: judge false alarms on the Poisson upper bound rather than the point estimate.

**Can it change a decision?** Formally yes: K5 stays as a claim or moves to the limitations. In practice:
- With the code as it stands, `cache_signal_leads` is reachable mostly through artifacts (CA1, CA2, CA4).
- After the fixes, BELIEF: P(`cache_signal_leads`) ≲ 0.1, because the arrival surge comes before the cache goes cold. The run then mainly sets the content of the limitations sentence. That is worth 0 GPU h, but it should be registered as such.
- One outcome changes nothing today: `too_few` → the same decision as a measured failure (CA3).
- K5 is also "kept only if K1–K3 leave room" (FILE(docs/claims.md:83)), so `no_usable_cache_lead` and "K1–K3 leave no room" lead to the same decision.

**Not checked:** how any real run behaves (forbidden); whether `kv_onset` picks out the seven expected events; warm-up stationarity of [240, 540); the vLLM semantics of `kv_cache_usage_perc` and the TTFT histogram (pinned source not opened); NaN stretches in L during stalls; REG-22's readout file; whether the candidate list misses folders that no doc names (runs/ was not listed).
