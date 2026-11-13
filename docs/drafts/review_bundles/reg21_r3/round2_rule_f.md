REG-21 draft 4, round-2 adversarial review: NOT READY (7 small required changes). The statistic and both raises are coded as written and every round-1 item was acted on, but two are only partly fixed and the "live" claims are overstated.

Scripts (synthetic only; no run folder opened; `find_runs` replaced before any call that could reach it), all in `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r2_scratch/`:
- `a_cfg_numbers_busy.py` (script a)
- `b_judge_ref_batch2_vj.py` (script b)
- `c_pair_json_edges.py` (script c)

The 25 repo tests pass. `analysis/k3w.py` and `tests/test_k3w.py` equal HEAD (last touched in 3f5c84a). Nothing in the repo was modified by me; `analysis/e1.py`, `tests/test_e1.py` and `tests/test_withheld.py` already showed as modified at my first `git status` (another session).

**1. Round-1 required items 1–9**

1. FIXED. `k3w.py:52` `"busy_min": 0.99`, `busy_share` (94–100), `row` (211–214) for both batches; test `test_a_server_that_idles_in_W_is_not_judged`. New holes in §2 A–C.
2. FIXED. `k3w.py:54–56` pinned ids, 110–114 raise, 122–126 per-run `U_by_end`, busy, running, waiting, kv, `preempt_per_s`, `redo_share`.
3. FIXED. `k3w.py:286–297`. Left, minor: a prefix of 1 or 2 seeds is accepted, and the heading test is a substring match (§2 G).
4. FIXED. `k3w.py:63, 261` (`min_group_runs` 3), 249–253 (min, max, sd, dates), Alternatives 2, "by load or by day".
5. PARTLY. High and low are rewritten and J1 with J2 outside is covered. Left:
   - "If they disagree" is undefined: it does not say which batch-1 label is compared when batch 1 is "not_pooled", or whether "undefined" counts as disagreeing.
   - "batch 2 governs what the paper says about λ = 2.0" leaves J2 unaddressed, although J2 was computed with batch 1's 2.0 group.
   - J2 outside with every group inside has no branch (§2 D1).
6. PARTLY. "J2's statement is the assumption that makes them one population" covers 2.0 and 2.4 only. "The two runs at λ = 2.2 … enter a pooled median" has no assumption behind it, and the pair can decide the label (§2 D2).
7. FIXED. "from 1.5 % below to 0.4 % above"; "All five count, whatever their own gauges say".
8. FIXED. `k3w.py:84–86`. It is stricter than asked: any ok request in the run, not only in the window.
9. FIXED. `tests/test_k3w.py:134–153, 162–166`; the "(the latter moves …)" sentence.

**2. Traces on which a label comes out wrong**

A. Busy precondition: a saturated all-miss server left out as "idle in W" (script b §4).
- Same FIFO trap at 1.681, r = 0.9993 to 1.0004. The gauge is recomputed as max(0, requests at the server − N_run), i.e. what an engine with N_run requests in its running batch would report. Configs have `--max-num-seqs: 256`.
- λ 2.0 seed 2, N_run 90: busy_W 0.9856, "idle in W", while end-window waiting is 57.5 (selection says backlogged).
- λ 2.0 seed 3, N_run 110: busy_W 0.9900, judged. One seed in, one out at the same engine.
- N_run 140: λ 2.0 seeds 2 and 3 read 0.42 and 0.64 (out); λ 2.4 seed 2 reads 1.00 (in); the 3000 s config seed 15 reads 0.90 (out). The exclusion depends on load, so J2 goes undefined or compares a selected 2.0 group.
- N_run 256: busy 0.00 everywhere.
- On the tests' own definition of waiting (sent and not in service) a model-F trap never comes near the threshold: line minimum 38–171 in W for FIFO and batches of 16–128 (script a §2). So the precondition bites only where the real engine is not the synthetic one.
- What `vllm:num_requests_waiting` counts is not tagged SOURCE anywhere in the text or code. The text's own "REG-18's seeds 3 and 6 each had one quiet span" says real lines do touch 0 in stuck runs. BELIEF: the gauge is "beyond the running batch"; I could not check it.

B. Busy precondition: an idling server passes (script a §3).
- `busy_share` uses the non-NaN scrapes present, with no coverage test (unlike `load._level`'s `_covered`).
- The test's lull server with its 367 empty-line scrapes absent from metrics: busy 1.0, judged, r 0.715, which gives J1 "low".
- Gauge NaN in all but 5 scrapes of W: busy 1.0, judged.
- This relies wholly on the run-validity check for scrape gaps, which I did not read.

C. Wrong reasons (script a §3).
- No metrics, or no waiting column: busy NaN, `why_not` = "idle in W". That is a missing gauge, not idleness.
- A run that is not all-miss and also idle reads "not all-miss in W" only.
- A fourth reason, "no work rate", exists in code and is reachable only with a NaN reference.

D. `judge` (scripts b §5, c).
- D1. "not_pooled" with every group inside: 2.0 at 0.96 ×5 and 2.4 at 1.02 ×6 gives J2 outside (0.06), both groups J1 inside, pooled "not_pooled". The decision table then drops model F's single capacity although each load is "at the cache-off rate" by J1's own tolerance. Also: all runs at 1.00 with the 2.0 group down to 2 judged gives J2 undefined and J1 not_pooled.
- D2. The 2.2 pair decides the pooled J1.
  - 2.0 = {1.03, 1.04, 1.04, 1.05, 1.05}, 2.4 = {1.05, 1.06 ×5}: inside (1.05) without the pair; with a pair at 1.07, 1.08 outside high (1.06).
  - Reverse: 2.0 = {1.05 ×3, 1.06 ×2}, 2.4 = {1.05 ×2, 1.06 ×4}: outside high without; with a pair at 0.90, 0.95 inside.
  - In the shape the text predicts (2.0 at 1.00–1.02, 2.4 at 1.045–1.07, J2 spread exactly 0.05, inside), the pooled median of 13 is its 7th value, i.e. a λ = 2.2 run. Pair (1.03, 1.04) gives inside; pair (1.06, 1.08) gives outside high.
- D3. J2 inside can hide a group that is outside: 2.0 at 1.02, 2.4 at 1.06 gives pooled 1.02 inside while the 2.4 group alone is "outside". By the text only the pooled label counts.
- D4. A group's J1 carries no side (`groups[g]` has "J1" only), yet the decision table has "J1 outside, high (pooled, a group, or batch 2)".
- D5. `_level(nan, 3)` returns ("outside", "low"). Unreachable through `judge` (n = 0 gives undefined first), but latent.
- D6. Per-group J1 uses `min_runs` 3, so a pair is "undefined". Keys by `f"{lam:.1f}"`: 2.15 → "2.1", 2.25 → "2.2", 2.35 → "2.4". No effect at 2.0, 2.2, 2.4.
- D7. A bimodal 2.0 group {0.90, 0.90, 1.00, 1.10, 1.10} against 2.4 at 1.00 gives J2 inside (0.000) and J1 inside. It is caught only by the reported min, max and SD.
- D8. With the two runs the text names as quiet (2.0 seeds 3, 6) out, the 2.0 group is three runs of two dates. 1.00 on 11-10 and 1.06, 1.07 on 11-11 against 2.4 at 1.00 gives J2 outside (0.06) from a day effect inside one load.

E. How often J2 is undefined or outside (script b §5 Monte Carlo, script c).
- From the text's own 0.9 × 0.9 = 0.81 per run: P(J2 undefined) = 0.065. If seeds 3 and 6 are idle: 0.48 (0.81³ = 0.53 that the other three all pass).
- P(J2 outside) with run SD 0.025 and the text's slope of +0.05 per req/s (0.02 between groups): 0.06, or 0.18 with a day SD of 0.02. With no load effect and day SD 0.02: 0.12. It reaches 0.46 only at a slope of 0.125.

F. `reference()` (script b §6).
- A valid run at 2.25 raises; a second valid run at 2.0 raises; a pinned run that is invalid raises; a valid run at 1.9 is ignored. All as the text says.
- `mean_without_2.0` is taken from the config rate ≥ 2.5: fine.
- A pinned id is trusted by name only: one whose config says rate 1.0 is accepted (U 3169, busy 0.32). Harmless while run folders are immutable.
- The reference's readouts are not contained: an ok request without `t_end` raises from `reference()`.

G. `batch2_runs` (script b §7).
- Gap, duplicate, empty and pre-[RESULT] all raise.
- A prefix of one or two seeds is accepted. That gives J1 "undefined" and spends the one computation.
- The seal lifts on any `## ` heading containing the substring: "[RESULT] REG-190", a [CORR] heading that quotes "[RESULT] REG-19", or an interim "[RESULT] REG-19, interim: seeds 15–17". After an interim heading, seeds 18 and 19 never enter.
- `_drift`, `_rerun` and the controls do not match the pattern. `AFTERSHOCK_UNSEAL` does not bypass the raise.

H. `vj_rule` and `sessions_slope` (script b §8).
- Units agree: sessions per second on both sides.
- At exactly λ = 2.0 the need is 0.5 × (0.25 − 0.2101) = 0.0199 sessions/s, i.e. 18 sessions over 900 s.
- `slope_needed` uses the realized starts in W, so at λ = 2.0 it ranges 0.012–0.043 across seeds 2–6. It goes ≤ 0 if a seed has ≤ 189 starts, and then a flat backlog passes.
- On the synthetic trap the slope part is True in 16 of 16 runs (tightest: 0.0218 against 0.0138); on a server that keeps up it is False in 16 of 16. So it is meaningful at 900 s on synthetic data, with a thin margin.
- Sessions cut at `duration_s` (no turn 7) never leave the count: 4 in W for seed 2. None could end inside W, so there is no bias.

I. `reg21_table`: 12 `row()` calls for 6 runs; judged r equals the rows' r; 1.1 s; `json.dumps` of a row and the judged dict works. Any argument other than 1 is treated as batch 2.

**3. Code against the text**

Sentences the code does not do:
- "preemptions per second and the redo proxy (preemptions per second × mean prompt ÷ U)" (per run) and "The redo proxy of both arms is the readout." `redo_share` exists only in `reference()` (`k3w.py:126`); `readouts` and `row` have none (script b §9).
- "A readout that raises is stored as its error message and does not stop the table". True for `vj_rule` and `readouts` (218–222); not for the reference's readouts (117–126).
- "Runs left out are listed with the reason ("not all-miss in W", "idle in W", "no later turn in W")". There is a fourth reason, and a missing gauge is called "idle".
- "at least one request waiting in at least 0.99 of the scrapes". It is 0.99 of the non-NaN scrapes that exist; 5 suffice.
- "J1 outside, high (pooled, a group, or batch 2)". No side is computed for a group.
- "The function raises until `docs/decisions.md` has REG-19's [RESULT] heading". It raises until any heading contains that substring.
- "Batch 1 … the 13 valid … runs". A missing or invalid id does not raise (it is listed in `missing_or_invalid` and the table is computed on fewer), unlike the reference. Configs `burst_l1pl350cl_r2.0_s7` and `confirm_l1pl350cl_r2.2_long_s14` exist; whether runs of them exist, and why they are not in batch 1, I could not check.
- "batch 2's three raises": four are tested. Trivial.

Numbers the text contradicts itself on:
- "P(J2 inside) ≈ 0.6" with "Slope of r on the load ≈ +0.05 per req/s". A slope of 0.05 is 0.02 between the judged groups, which gives P(outside) of 0.06–0.18 (§2 E), not about 0.4.
- No P(undefined) is given for J2.
- Batch 2's 0.7 + 0.25 + 0.05 = 1.00 leaves nothing for "undefined". The text's own 0.81 gives 0.05 with five runs entered, 0.17 with four and 0.47 with three, before counting REG-19 runs that are not cold-backlogged.

Recomputed and found right:
- Windows [1680, 2580), [1680, 5580), [1680, 4080); REG-15's step is at 5580.
- 25 tests.
- "0.69 to 0.91": 0.689, 0.692, 0.858, 0.908.
- "1.10 or 0.92": 1.1004–1.1007 and 0.9219–0.9225.
- "r = 1.00 ± 0.02": FIFO 0.9993 and 1.0004; batch 16 0.9997; batch 64 0.9990; think ×6 0.9996. All have busy 1.0.
- "a fixed cost … under 0.02": 0.9924 at 2.0 and 0.9895 at 2.4 (the latter not in the tests). Against a fixed-cost reference: 0.9927 and 0.9898.
- −1.5 % and +0.4 %: 1.656/1.681 and 1.688/1.681. 0.05/0.15 is a third.
- "about 0.97 to 1.09": holds with the mean-prompt factor implied by first-turn shares of 0.125–0.18 (1.000–0.982 with the other turns even), giving 0.976–1.095. Round 1's factor of 0.954 at 1.67 would give 0.948.

**4. Can any outcome change a decision?**

- J2 inside and J1 inside: wording.
- J1 outside high: wording ("r times the token work").
- J1 outside low: a real decision, unreachable in batch 1 (stated), P ≈ 0.05 in batch 2 by the text. "does less work than a miss explains" should read "is credited with less": prefill redone in the stuck arm reads low with the same engine speed (round 1: 0.93).
- J2 outside: the only claim-changing branch. It is confounded with day (stated), and its consequence (model F not used at other loads) follows from "load", not from "day". It also fires when both groups are inside J1 (D1). No registered readout separates the two, although one exists: batch 2's median minus batch 1's 2.0-group median is the same load on other days.
- Undefined or not_pooled: "nothing follows". P is 0.065–0.48 for J2 (§2 E).

"What is live" is overstated for J2. The text bounds J1 from seen completion rates and first-turn shares; the same arithmetic per run bounds each group's median, and so J2's spread, to roughly ±0.02 (BELIEF as to the width; I have not seen the per-run numbers). The author's "P(J2 inside) ≈ 0.6 (the λ = 2.4 runs reported the highest rates)" uses exactly that knowledge, and the 0.05 was set with it. The only unread item is batch 2's J1, which needs at least 3 of REG-19's runs to be stuck, all-miss and busy over 2400 scrapes.

"Batch 2 governs" is half coherent. It is right to prefer the unread batch, but the comparison is undefined (item 5 above), batch 2's window is 2400 s against 900 s, and a batch-2 median more than 0.05 from batch 1's 2.0 group means a fixed-load effect larger than J2's tolerance, which the text does not connect to J2.

The departure from the owner's "mix primary" is flagged in the text. It needs its own delegate [DECISION]; I did not judge that.

Should it run: yes, at 0 GPU h, as a retrospective measurement (batch 1) plus one blind test (batch 2's J1), after the changes below. Not as "two live items".

**5. Verdict: NOT READY**

Required:
1. The λ = 2.2 pair: leave it out of the pooled median (reported per run and as a group), or state the assumption that covers it. One line in `judge`, one sentence in the text.
2. "What is live": say that J2's spread is bounded from the seen per-run rates and first-turn shares, give that number, and say that 0.05 for J2 was fixed knowing it. Say that 0.99 was fixed knowing seeds 3 and 6 had a quiet span. Name batch 2's J1 as the only unread item.
3. Prediction: add P(J2 undefined) and P(batch 2's J1 undefined); reconcile the slope of +0.05 with P(J2 inside) of 0.6.
4. Decision table:
   - (a) add the branch J2 outside with every judged group inside;
   - (b) define "disagree": which batch-1 label is compared, and that "undefined" is not a disagreement;
   - (c) register now, as reported only, the fixed-load contrast (batch 2's median minus batch 1's λ = 2.0 group median) and the sentence that a contrast above 0.05 means J2 is not read as a load effect. The stopping rule forbids adding it later.
5. Busy precondition:
   - the reason "no waiting gauge in W" when the share is NaN;
   - a registered minimum of scrapes present in W, else that reason;
   - one sentence on what the gauge counts (SOURCE, or BELIEF plus an open question) and that a full batch with an empty line is left out.
6. Add the stuck arm's redo proxy to `readouts`, or strike it from the per-run list and from Alternative 1.
7. Batch 1: raise when one of the 13 ids is missing or invalid, or register that the table is computed on fewer. Say why `r2.0_s7` and `r2.2_long_s14` are not in it.

Optional:
- The side for a group's J1; a NaN guard in `_level`.
- Contain the reference's readouts.
- Anchor the heading match (the [RESULT] tag, with "REG-19" not followed by a digit); a minimum of 3 seeds for batch 2, or say that a short prefix spends the batch.
- A reported-only table of J2 and J1 at `busy_min` 0.95, since P(J2 undefined) may be near 0.5.
- Copy `batch1`, `batch2_pattern` and `costs` as literals into `k3w.py`; they now come from `k3.REG21`, a module the text calls "not registered".
- List both reasons when a run fails both preconditions.
- Give the slope's interval.
- Take `slope_needed` from the configured λ, or report both.
- Reject a batch argument other than 1 or 2.

Could not check:
- Any real run: `k1.cold_backlogged`, `shock_size` and the gauges on real metric frames; the scrape-gap validity check.
- The pinned vLLM source: what `num_requests_waiting` counts, when `cached_tokens` is set, resume after preemption.
- Anything in `docs/` or `agent/`: REG-19's run order and heading; the seen rates and first-turn shares; "U … has not been computed by anyone"; Valse and Jannesari's rule and their 0.95–1.12; the claims.
- `harness/run.py` `load_config` was used, not read. In `gate.py` I read only `burst_end` and `shock_size`.

Script b writes a throwaway `decisions.md` in a `tempfile` directory outside the repo.
