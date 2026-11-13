# Rule F, round 2, on REG-22 draft 4 (agent a0fd29b2b40338bb5), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input), no word changed. Bundle: `docs/drafts/review_bundles/reg22_r2/`; code at `727d1f2`. The uncommitted change it saw in the working tree is the agent's draft-5 readouts, written while it ran.

---

# Rule F review of REG-22, draft 4 (round 2): NOT READY

None of the round-1 required items is still missing outright. R5, R6, R7 and R9 are only partly fixed. I could not produce a wrong label on any synthetic run.

- **Label map:** draft 4's six cases and the code at commit 727d1f2 agree in all 18 cells checked.
- **Changed rules:** on 960 synthetic runs, every label change from f0ba24e to 727d1f2 comes from the two announced rule changes (one failing span decides; at least 20 later turns).
- **What is still required:** nine changes, all of them text. No threshold moves. The next round can be limited to a text diff, provided the code stays at commit 727d1f2.

## 0. What this pass saw and ran

- **Read:**
  - the bundle in full;
  - `analysis/c2.py` and `tests/test_c2.py` at commit 727d1f2;
  - the helpers they call (`k1`, `margin`, `load`, `stats`, `k3w`, `withheld`) and the cited regions of `gate.py`;
  - the configs (through `harness.config`);
  - pinned vLLM 0.32.0: `v1/core/kv_cache_metrics.py`, `v1/core/block_pool.py:666–750`, `v1/metrics/buckets.py:135–157`.
- **Not read:** `runs/`, everything under `docs/` outside the bundle, and the backups.
- **Code identity:**
  - The bundle's patch equals `git diff f0ba24e 727d1f2 -- analysis/c2.py tests/test_c2.py`.
  - Between those two commits, `analysis/c2.py` and `tests/test_c2.py` are the only analysis or test files that changed.
  - `uv run --offline pytest tests/test_c2.py -q -p no:cacheprovider` gave 22 passed on a clean tree.
- **The working tree changed during this review.** The coordinator's message says nothing changed; that is not so.
  - At 16:28 another session modified `analysis/c2.py` and `tests/test_c2.py`, uncommitted, 117 lines added.
  - HEAD moved from 4af12e7 to 59e1d49.
  - Traces t01–t07 ran between 12:04 and 12:13. The tree was clean then: `k3w._dirty()` returned empty after t06.
  - Trace t08 ran on a `git archive` snapshot of 727d1f2: `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r2_scratch/snap727`.
  - **I did not review the uncommitted changes.** This review covers commit 727d1f2 only.
- **Limits kept:**
  - Every script replaces `find_runs` in both `analysis.c2` and `analysis.k3w` before any call.
  - `withheld` was exercised only on made-up folder names, against a temporary decisions file.
  - I wrote nothing into the repo.

Scripts (synthetic inputs only). Round 1's `fk.py`, `c2_f0ba24e.py` and `t00_configs_arith.py` were reused.
- [t01] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r2_scratch/r2_t01_label_map.py`
- [t02] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r2_scratch/r2_t02_judged_rules.py`
- [t03] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r2_scratch/r2_t03_control_mapping.py`
- [t04] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r2_scratch/r2_t04_reported_code.py`
- [t05] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r2_scratch/r2_t05_hist_onsets.py`
- [t06] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r2_scratch/r2_t06_judged_path.py`
- [t07] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r2_scratch/r2_t07_thresholds.py`
- [t08] `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r2_scratch/r2_t08_control_baseline.py`

"Line N" below means a line of `registration_draft4.md`. "c2.py:N" means `analysis/c2.py` at 727d1f2.

## 1. R1–R10

| Item | Status | Where |
|---|---|---|
| R1 | **FIXED** | Draft lines 29–36 give the six cases, and line 18 adds the error status. The code matches (c2.py:179–184, 101–108). The cell has its test (tests/test_c2.py:182–190). All 18 cells agree [t01]. |
| R2 | **FIXED** | Draft lines 25 and 72; c2.py:133–136. Every span is reported with `judged`. Nit: in the printed JSON, `judged` comes out as the string "True" or "False" (optional item 3). |
| R3 | **FIXED** | Draft lines 46–57 match round 1's section 4 item by item, including REG-21's per-span U and reuse (`k3w.reported_spans`, k3w.py:414). All cited lines are where the draft says. |
| R4 | **FIXED** | Draft lines 42–43: 11 `stuck` (5 + 2 + 4) and 2 `bad_baseline`, 13 in all. The RUN values themselves are unverifiable here. |
| R5 | **PARTLY** | Line 38 says loads are "never pooled" and that λ = 2.2's two runs "are never counted together". The code does both: `reg22_table` prints `by_load["2.2"]` with n = 2 and both bounds, and an all-load `counts` (c2.py:341–350). On synthetic runs [t04 §7] the 2.2 row prints n 2, loop 2, lower 0.224, upper 1.0. See N1. |
| R6 | **PARTLY** | The `loop` and `not_sustained` lines are tied to the failed component (lines 66 and 68). The `not_memory_limited` line (67) has no count, and the two batches at λ = 2.0 have no rule. See N2 and N3. |
| R7 | **PARTLY** | Line 91 lists every function the trace reached before the first readout [t06]. It omits what `load.load_run` calls: `load._jsonl`, `load.metrics_wide`, `withheld.guard` and `withheld.unsealed_ids` (load.py:18–38, withheld.py:50–66), and the constants `load.RUNS` and `withheld.DECISIONS`. See N4. |
| R8 | **FIXED** | Line 92. |
| R9 | **PARTLY** | Ties are reported as groups (c2.py:168–169; test at 211–216), and the premise is tagged BELIEF (line 12). The lag numbers and the simultaneity rule in line 74 are wrong or open. See N5. |
| R10 | **FIXED** | Line 27 (0.81; 0.66 to 0.77) reproduces [t00]. |

## 2. The label map: text against code

Each cell is a synthetic run through `condition4(..., with_readouts=False)`, compared with draft 4's six ordered cases read literally [t01].

| levels.ok | Judged spans | Code | Text | Agree |
|---|---|---|---|---|
| True | all True (4) | loop | loop | yes |
| True | one False | not_sustained | not_sustained | yes |
| True | one None | undefined | undefined | yes |
| True | one False and one None | not_sustained | not_sustained | yes |
| True | fewer than two (1) | undefined | undefined | yes |
| True | no exit (0) | undefined | undefined | yes |
| False | each of the six | not_memory_limited | not_memory_limited | yes (6 of 6) |
| None | each of the six | undefined | undefined | yes (6 of 6) |

Sub-cells the six cases do not spell out. All follow the case order as written [t01]:
- **(i) Exactly one judged span, and it fails:** `undefined`. Case 3 comes before case 4.
- **(ii) A judged span that provably fails two links** (reuse 0.951 against 0.94; u 1246 against 1984), with a 40 s scrape hole in the same span: `holds` is None, so the run is `undefined`. Any missing value makes the whole span None.
- **(iii) KV provably 0.50 in the end window while N cannot be read there:** `undefined`. Case 1 comes before case 2.

Cases (ii) and (iii) are conservative and consistent with the text (optional item 1).

## 3. Traces and findings on the code

### Judged rules

- **(a) One failing span decides.**
  - A span cannot "fail" because of an unreadable value. Any missing value, the baseline's included, makes `links` return None (c2.py:118–119), never False. With an unreadable baseline every span is None and the run is `undefined` [t01 (iv)].
  - The only partial inputs left are rows without `cached_tokens` and requests that got a first token but never finished. Both push the two cache links towards holding, not failing.
  - **I could not break (a).**
- **The code diff changes labels only as announced.** I compared labels on 960 synthetic runs. The grid crossed the cache state, KV, scrape holes, the exit time, and thinning to 19 later turns. The labels differ in 62 runs [t02 §1], every one explained:
  - 18 runs go from `undefined` to `not_sustained`: a judged span fails while another has a missing value (O2).
  - 44 runs go from `loop` or `not_sustained` to `undefined`: fewer than 20 later turns (O4).
- **(b) The minimum of 20 later turns.**
  - These runs are nowhere near it (DERIVED from the configs: 8 turns, session rate λ/8, cold completion 1.73 req/s). The baseline [300, 900) holds about 1050–1260 later turns. A cold 300 s span holds at least about 430. A 60 s onset window holds at least about 86.
  - A span falls under 20 only if the server nearly stops. That span is then None, so the run is `undefined` rather than `not_sustained`, even though its uncached rate (about 0) would fail link 2. This is consistent with case 5 and not plausible on valid runs (BELIEF).
- **(c) Unjudged spans now computed.** They cannot change a label.
  - A scrape hole, no later turn, or a cache back inside the unjudged span all leave the label at `loop` [t02 §3].
  - `links_failed` collects judged spans only (c2.py:147).
  - The only raise inside `links` is `session_uncached_rate`'s check over the whole run (c2.py:72), and `baseline` makes it first, both before and after the change.

### Reported-only code

- **The readouts cannot change or delay a label.**
  - `condition4(..., with_readouts=False)` calls none of the four readouts and does not call `find_runs` [t04 §1].
  - `reg22_table` computes every label and the counts before the first readout [t04 §2].
  - Each row's label is recomputed in a second pass (c2.py:345), after the earlier runs' readouts have run. It equals the first pass because no real readout changes its inputs (read through: `later_turns` copies; `control_readout` reads `su` only).
  - A readout that did change what it is handed would alter the printed `sustain` beside an unchanged label [t04 §2] (optional item 4).
- **`control_readout` name mapping** [t03]:
  - All 17 burst configs map to an existing control with the same seed, rate, duration, sessions, steps, server arguments, windows, and `control_t_s` = 1080. That covers REG-11 (explicit entry, c2.py:304; the glob does not match the `_s2` controls or the open-loop control) and REG-19's five `w3000` seeds.
  - REG-15's `confirm_…` config gives "this config has no control", which matches line 73. The only 2.2 controls are REG-14's `_s2` and REG-16's `long_s14`.
  - Two valid controls give "2 valid runs of …"; none gives "0 valid runs of …" [t04 §3].
  - The real `load.verdict` runs on a control (control_t_s 1080, verdict baseline [480, 1080)) [t06 V]. The links are taken over the burst run's window [300, 900), on the control's own data.
- **Sealed controls.** A sealed control cannot arise in either batch.
  - REG-19's seal pattern `*_l1pl350cl_r2.0_w3000_s1[5-9]` covers burst runs and controls alike. The heading that lets batch 2 run lifts both [t04 §4].
  - No batch-1 control is sealed.
  - If one were sealed, the readout would say "0 valid runs", the same as absent or invalid; only stderr names the seal.
- **The control readout can point the wrong way** [t08 §1]. Line 73 says "a queue that the load alone explains would show the links in the control too". That holds only if the control's [300, 900) was warm.
  - Synthetic control in the same cold, full state by the load alone, tipping at 1200, 950, 850 or 700 s: `links_hold_in_every_span` True.
  - The same control tipping at 500 or 200 s: False. Its own baseline is already cold or large, so u and N cannot double.
  - Against the burst run's baseline, its links hold in every case.
  - **Likelihood: low for judged runs (BELIEF).** The burst twin had a good baseline on the same schedule. Optional item 2.
- **No-exit runs.** A burst run with no exit gives the control readout no spans and `links_hold_in_every_span` False rather than None [t08 §3].
- **`row_counts` is right** [t04 §5]: 7 rows without `cached_tokens` and 3 unfinished with a first token give 7 and 3; requests that never started are not counted.
- **The `reset` flag does not do what line 75 says.** It compares only the first and last scrape (c2.py:239–242). A restart after which every bucket climbs past its start is not flagged: the count printed is 800 where 1000 + 1300 were gained, and the median and shares come from two unrelated counters [t05 H]. See N8.
- **The lower bound is right.** 1 − cp_upper(n − k, n) equals the one-sided 95 % Clopper–Pearson lower bound to within 5e-16 for n ≤ 14 [t04 §6]. Examples: 3 of 3 gives 0.368; 4 of 5 gives 0.343; 2 of 2 gives 0.224.
- **The clean-tree check is right.** `_dirty` (c2.py:359–361) runs before `reg22_table`. It would refuse to run on the current working tree.

## 4. Sentences the code does not do, wrong numbers, open rules

### Checked and correct
- 30.2 requests; 42 at the smallest prompt (41.95); 6.2 ×; 4.5–5.6 × (4.46–5.61); 0.81 (0.8075); 0.66–0.77 (0.658–0.767); 0.97⁹ = 0.760 as arithmetic [t00, t07].
- N lag 15 s and KV lag 56 s.
- "A full recovery of up to about 70 s does not fail any link": the first failure comes at 65–70 s, by KV [t07 E1].
- "The reuse link holds with the cache back for most of a span": it fails at 285 of 300 s [t07 E2].
- Every line reference: c2.py:48, 85, 101, 111, 125, 172, 284; tests/test_k3w.py:438; margin.py:66; gate.py:91, 479, 949, 989, 1361.
- The judged path of line 91 against what `reg22_table` runs [t06], except N4.

### Wrong numbers
- **Line 26 and line 74, "a baseline near 0.84" for the reuse.** At full reuse the reuse of later turns is 1.0 (DERIVED from the session shape). 0.84 (0.8385) is the token hit rate in the same state, which is the "warm hit rate of 0.84" in line 77.
  - With a baseline of 0.84, the cited test's reuse 0.83 would fail link 1 (threshold 0.78), not "only link 2". The test's own baseline is 1.0.
  - The reuse lag is 3.6 s, not 4.3 s.
- **Line 74, uncached-rate lag "12 to 14 s (60 × 1 / 4.4 to 5.2)".** By the draft's own ratios (4.5 to 6.2 ×), the lag is 60 / (6.2 − 1) to 60 / (4.5 − 1), which is 11.5 to 17.1 s [t05 L].
- **Line 60, "2 of about 58 judged spans".** The maximum is 10 × 4 + 14 = 54; 58 counts REG-15's run twice. So 2/54 = 3.7 %, and line 61 becomes 0.963⁹ ≈ 0.71, not 0.76 [t07 A].

### Sentences the code does not do
- **Line 38:** "never pooled across loads" and "never counted together" (N1).
- **Line 75:** "a counter that goes down inside the window is flagged" (N8).
- **Line 6:** "`loop` says … the cache is lost in every 300 s span". The code certifies only reuse ≤ baseline − 0.06 and u ≥ 2 × baseline per span. Those let through:
  - a span with only the cache back for up to about 240 of 300 s [t07 E2];
  - spans with up to about two thirds of later turns hitting, at the cold completion rates (R10).
  - Line 26 already has the honest version: "no span re-warmed for most of its length".

### Rules left open
- **Simultaneity rule (line 74).** It ignores the 10 s onset grid. For four signals stepping at the same instant, the rule as written calls the order "different from simultaneity" in 2 of 10 step phases, from rounding alone. With one grid step added to each lag difference, 0 of 10 [t05 O]. It also does not say which end of a lag range is used.
- **`not_memory_limited` line (67).** No count. One such run (KV < 0.80) at a load of n ≥ 3 triggers "the stuck runs at that load are backlog states … D1 and D2 are not proposed as planned". At the same load, the `loop` line (3 of 5, say) lets D1 and D2 be proposed as planned.
- **Two batches at λ = 2.0.** Nothing says whether the lines are applied per batch, or what C2's status says when batch 1 and batch 2 disagree.

## 5. Verdict: NOT READY

The judged labels hold up; I found no wrong-label trace on plausible data. What is left is text.

### REQUIRED
- **N1 (R5).** Say that `reg22_table` prints a 2.2 row (n = 2, with bounds) and an all-load `counts`, and that neither is used for any sentence. Or drop both from the code.
- **N2 (R6).** Give the `not_memory_limited` line the same count as the others: "in more than half of the stuck runs at a load (n ≥ 3)"; below that, per run only.
- **N3.** State now that each batch is read by the decision lines on its own, and what C2's status says at λ = 2.0 when batch 1 and batch 2 disagree.
- **N4 (R7).** Add to line 91 `load._jsonl`, `load.metrics_wide`, `withheld.guard`, `withheld.unsealed_ids`, `load.RUNS` and `withheld.DECISIONS`, or write "and everything those call, transitively".
  - As written, a change to `metrics_wide`, which builds every gauge value, would pass between the batches as a hunk "outside that path".
- **N5 (R9).** Fix the onset rule in line 74:
  - uncached-rate lag 11.5 to 17 s;
  - reuse baseline 1.0 at full reuse (DERIVED), lag 3.6 s, or a RUN value;
  - "differs from simultaneity only where two onsets are further apart than the largest difference of their lags plus one grid step (10 s)".
  - Make the same 0.84 → 1.0 correction in line 26.
- **N6.** Line 60: 54 judged spans, 3.7 %. Line 61: about 0.71.
- **N7.** Line 6: replace "the cache is lost in every 300 s span" with line 26's wording ("no 300 s span re-warmed for most of its length, at the registered thresholds").
- **N8.** Line 75: "a bucket that ends lower than it started is flagged; a restart after which the counts climb past their start is not detected". Or check every scrape in the window in the code (reported-only path).

**What makes it READY:** N1–N8 in the text. The next round can be limited to a text diff, provided the code registered is commit 727d1f2.

**The uncommitted changes need their own review.** If the changes in the working tree (`analysis/c2.py`, `tests/test_c2.py`, 16:28) are meant to be registered, that diff needs its own rule F pass. The registration must cite the commit actually reviewed.

### OPTIONAL
1. Let a link that provably fails decide its span, and a failing level decide the levels, even when another value is missing (sub-cells ii and iii).
2. In `control_readout`:
   - also give the control's links against the burst run's baseline, or flag a control whose [300, 900) is not warm;
   - give None, not False, when there is no judged span;
   - tell a sealed control from an absent one.
3. Cast `judged` to `bool` (c2.py:136) so the JSON prints true/false. Now a reader filtering by truthiness keeps 5 of 5 spans [t08 §2].
4. Build `rows` from the first pass (c2.py:340, 345).
5. Give wording for a span that fails only N or KV. That is the first sign of a short full recovery (65–70 s) [t07 E1] or of a schedule lull.
6. In line 25, say that the reported unjudged span mixes time before and after the exit.
7. "N ≥ 2 × baseline can fail only if the baseline N is above 15": by tokens at the mean prompt, N is 24.2 at KV 0.80 and 28.7 at 0.95 [t07 A], so "above about 12 to 15".
8. "At most about 3 %" does not follow from 0–2 `not_sustained` runs: one run can have several failing spans.
9. Lines 42, 56 and 80: the RUN tags name groups of runs, not run ids. The ids are in `c2.REG22["runs"]`.
10. Print the median bucket's lower edge.
11. Line 75 says "after the exit", but with no exit the code uses the burst's end (c2.py:266).
12. Tag the warm KV of 0.20 behind the 56 s lag.

### Should it run?
Yes, after N1–N8, at 0 GPU h. Batch 1 is mostly a restatement and its levels are close to decided before computing. Its new content is:
- the per-span uncached rate and reuse for [1380, 1680);
- the exit;
- the control's links;
- the onsets under the corrected rule;
- the eviction histograms.

Batch 2 is the only reading on data nobody has read. `not_sustained` in more than half at a load changes the confirmation run's registration, so at least one outcome changes a decision.

## 6. What I could not check

- Anything in `runs/`: the 13 runs' validity and verdicts; the RUN-tagged values (0.949, 30.3, 6.1, 34, 30.0, 1.73–1.81); the real baseline reuse and warm KV; whether `metrics.jsonl` holds the histograms; whether a server restart makes a run invalid.
- Files under `docs/` outside the bundle: `decisions.md`, `claims.md:45`, PROTOCOL's wording of condition 4, `agent/theory/k1_held_prefix.md` (the 64 s and 1 s), the probe cited in line 57, and the review file named in line 3.
- What `pass_clear` and `pass_warm_edge` imply about the burst verdict for REG-19 (line 57). I saw only the names in `gate.py`.
- The uncommitted changes to `analysis/c2.py` and `tests/test_c2.py`, and the commits after 4af12e7 (HEAD is now 59e1d49).
- `load.verdict` and the full table on real data, and their run time.
