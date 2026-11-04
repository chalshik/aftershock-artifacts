> **DRAFT. Not registered.** Nothing here is a registration, a threshold or a result. It is the audit addendum (items 34–43) as handed to the study owner on 2026-11-04, copied unchanged below this box.
> - The owner's decisions on it are in `docs/decisions.md`, 2026-11-04: "[DECISION] Owner's decisions on audit items 38–42", and the [CORR]/[DECISION] entries for items 35–37 and 43. Where this draft and those entries differ, the entries rule.
> - The `recovered/` folder this draft mentions is now `analysis/recovered/`.
> - REG-2 and REG-3 below are early drafts; the versions sent for review replace them.

# Audit addendum: items 34–43 (Phase 1 rows and Phase 2 proposal), 2026-11-04

Read alongside the main report, `PROPOSAL.md` in session `4de6c4e2`'s scratchpad. Its Phase 3 was committed while this was written (`eb1d5b6` … `d7e427c`), so this addendum is checked against **HEAD = `d7e427c`**, not `46f81cf`.

**Nothing in the repo was changed:** no commit, no push, nothing in `runs/` or `configs/`, no edit to `verdict`. The only things computed were these:
- hit rates and throughputs that are already published, recomputed with existing functions;
- prompt-length and arrival counts from `schedule.parquet` (inputs, not outcomes);
- one `verdict` call on a wipe-test run.

**μ_sat,off (items 38, 40, 41) was not computed** (`analysis/CLAUDE.md`: no analysis under a pending `[REG]`).

Recovered originals: `recovered/` next to this file: 19 tool calls (command + output), one scratch `judge.py`, and `INDEX.md`.

## Phase 1: rows 34–43

Severity: V = VALIDITY, W = WEAKENS, H = HYGIENE.

| ID | Area | Finding | Evidence | Sev | Proposed fix | Owner? |
|---|---|---|---|---|---|---|
| 34 | Ops | **Confirmed, and now wider.** `origin/main` = `47984d5`. Local `main` = `d7e427c`, which is 7 commits ahead: `46f81cf` plus Phase 3's 6. The `vm` tracking ref says `46f81cf`, but `git fetch vm` fails ("Permission denied (publickey)"; the `vm` remote doesn't use `~/.ssh/id_ed25519_vllm`). So the vm state is unverified. | `git rev-parse origin/main main vm/main`; `git rev-list --count origin/main..main` = 7 | H | Your item as written: `git push origin 46f81cf:main`. Or push all of `main` once Phase 3 is accepted. Not pushed: pushing is outward-facing and wasn't approved yet. Fix the vm remote's key with `git config core.sshCommand` or an ssh alias | yes |
| 35 | Analysis | **Premise partly refuted.** The default-pool values 0.767 / 0.661 / 0.525 **do** match a computation: `whole_run_hit_rate`, i.e. the first-to-last counter **over the whole run**, not the windowed counter (0.766 / 0.644 / 0.510). Their source is the original F script, which printed `hit` as `(h[-1]-h[0])/(q[-1]-q[0])` on the unwindowed metrics: 0.767 / 0.661 / 0.525 (`recovered/…173632_toolu_015jLzJd…`, lines 68–70 of its output). The 72k entry copied them. **Already corrected** in decisions (4) (`46f81cf`), with −0.07 to −0.12 like for like. **New, not yet corrected:** "hit 0.757 at λ = 7 against about 0.42 at λ = 5" (2026-11-03) mixes methods too. 0.757 is a mean of ratios; 0.42 matches the windowed counter (0.424) or the ramp-peak `_level` (0.419 / 0.407). Like for like: mean of ratios 0.757 vs 0.378; windowed counter 0.785 vs 0.424; whole run 0.785 vs 0.446. | Mean of ratios / whole run / windowed counter, for `sweep_pc_on_r2,r3,r4,r5`, `sweep_kv72k_pc_on_r2,r3,r4`, `sweep_gap5_pc_on_r4,r7` (functions `load.summarize`, `load.whole_run_hit_rate`, and a counter over `load.window`): 0.732/0.767/0.766, 0.627/0.661/0.644, 0.490/0.525/0.510, 0.378/0.446/0.424; 0.658/0.698/0.687, 0.511/0.552/0.526, 0.397/0.430/0.415; 0.786/0.800/0.800, 0.757/0.785/0.785 | W | One `[CORR]`, text below. Pool effect by one method: windowed counter −0.079 / −0.118 / −0.095 (λ = 2 / 3 / 4); mean of ratios −0.074 / −0.116 / −0.093 | no |
| 36 | Docs | **Confirmed, and already logged** in decisions (7) (`46f81cf`; five schedules, share ≤ 1408 is 0.502–0.510). Recounted today: p50 = 1408 over session rows. Share ≤ 1408 is 0.508 for `20261101-215502_stage2_control_cap_r3_rerun` (turn counts 901, 895, 890, 880, 872, 865, 859, 855) and 0.531 for `20261102-131353_burst_r3_s1`. **Caveat:** the burst count includes the burst rows, so the session-only share there is lower; (7) is the correct count. **It's a knife edge, and your mechanism is right:** with no truncation the share would be exactly 0.5, and pandas' `median` would give 1536. Over t ≥ 240 s only, (7) found 1664 in 3 of 5 | `schedule.parquet` of both runs (an input). `FILE(harness/workload.py:97-108)` | H | definitions.md "session median": the p50 (pandas `median`, linear interpolation) of `prompt_len` over every scheduled **session** request of the whole schedule, warm-up and truncated sessions included, burst rows excluded. Note that it's 1664 over the measured window. This is not a `[CORR]`, since nothing was wrong; it goes in the definitions commit | no |
| 37 | Provenance | **Originals recovered for most figures** (`recovered/INDEX.md`). Of the 25 differing rows in decisions (6), **14 are explained**: the reconstruction used a reading the original didn't (grid step, window, start time). **6 are rounding or hand arithmetic** on the published side. **4 have no original**, and **1 is still unexplained**. Every recovered original reproduces its published value, up to that rounding (table below). **Not found:** F_warm 6.4k / 8.7k, the 72k spans (0.11–0.28, 0.43), the 60 s hit SD 0.045, and the λ = 3.5 seed-3 first minute | Transcripts `c075c1a8…`, `f5298640…` (tool ids in the index); `analysis.recompute_published` at `d7e427c`: 79 ok, 25 differ, unchanged | W | Commit `analysis/recovered/` verbatim. A [CORR] to decisions (6): "unexplained" → explained, with the readings. Add an "original" column to `recompute_published` that re-executes the recovered code | no |
| 38 | Design | **[REG] draft below. Not blind for the default pool.** Its inputs are already public: cache-off KV means 0.415 (λ = 3) and 0.867 (λ = 4) in decisions 2026-11-01, and cache-off throughputs 3.453 / 3.511 / 3.521 / 3.533 in `docs/model.md` M2. So the 0.85 threshold picks λ = 4 there, as would any threshold in (0.42, 0.86). μ_sat,off ≈ 3.50 is effectively known (DERIVED: mean of the four = 3.5045). The 72k and 5 s-gap values are not published as far as I can see, so those are real tests. **Logic:** under B, λ > μ_sat,off is *necessary* for stuck, not sufficient. The classification says which runs **could not** have been tests | `docs/model.md` M2 rows (RUN tags there); decisions.md 2026-11-01 F table | V | Register first (rule E, F review), then compute | yes (registration) |
| 39 | Design | [REG] draft below. The prediction is plausible but not novel. N1 already says the 900 s run's last 150 s carried 3.52 req/s planned. The run tests whether the cache-off capacity seen in 900 s sweeps is a sustained capacity | `docs/model.md` M4; decisions.md 2026-11-04 [RESULT] (N1) | V | as drafted | yes (GPU) |
| 40 | Design | [REG] draft below. **Inconsistent with 38:** 38 defines saturation at KV ≥ 0.85, while 40 stops at KV ≥ 0.9. Pick one stopping rule before running. 5 s-gap cache-off was swept only to λ = 3.5 (throughput 3.26 req/s against nominal 3.5) | `sweep_gap5_pc_off.yaml` rates [2, 2.5, 3, 3.5]; `load.summarize` throughput of `20261103-142848_sweep_gap5_pc_off_r3.5` | W | as drafted | yes (GPU) |
| 41 | PROTOCOL | Consequences below. It's a post-results change, and it cuts both ways (see below). The upper edge, μ_warm, has the same N1 problem and should be decided at the same time | as below | V | owner decision | yes |
| 42 | Capacity | **Confirmed.** 5 s-gap cache-on throughput/λ is 1.017–1.040 at all 8 loads; cache-off is 1.030 at λ = 2 and 2.5. Seed 0's planned rate in 240–900 s is 1.019–1.047 λ at 5 s gaps, against 0.996–1.013 λ at 20 s gaps. **Cause:** one arrival realization per setup, not noise that averages out. The 5 s schedule differs from the 20 s one, since the gap draws shift the random stream (BELIEF; a check of `build_schedule` would settle it) | `load.summarize` throughput; `schedule.parquet` count of `t_planned` in [240, 900) / 660, all gap5 and four default/72k sweeps | W | Future sweeps: throughput ≥ 0.95 × the realized planned rate over the same window. It doesn't fix N1's within-window rise; only more seeds do (A1). **Disclosure:** to check the premise I computed throughput / realized for past sweeps. I did not apply the rule to them, and it can't now be registered blind for them, so it is for future sweeps only | yes |
| 43 | Configs | **Confirmed, with one more reason.** `configs/stage2_base.yaml:10-22` has no `pf_climb`, `hit_climb` or `drain_horizon_s`. It has `q_slope`, which `verdict` does not use, and `climb`, and the "req/s^2" comment at :21. Used by `wipe_test_preempt`, `wipe_test_idle` and the stopped `stage2_control_r1.5`. **`verdict` fails on the wipe tests even before the missing keys:** they are 900 s runs with the wipe at 450 s, so the 1500 s watch is empty and `np.polyfit` raises `TypeError: expected non-empty vector`. The KeyError on `pf_climb` would come next. The units comment is already recorded (decisions.md:654); the missing keys are not | `FILE(configs/stage2_base.yaml:10)`, :21; `load.verdict` on `20261101-144335_wipe_test_preempt` → TypeError; `FILE(configs/stage2_cap_base.yaml:7-13)` supplies the keys for every other Stage 2 run | H | definitions.md "Used configs that cannot be fixed" (text below), plus one [CORR]. Config untouched. Overlaps N7 (`verdict` on an empty window) | no |

### Item 37: every published number on which the original, the reconstruction and the published value disagree

- "Original" is the output that the recovered code printed at the time (`recovered/*.out.txt`).
- "Reconstruction" is `analysis.recompute_published` at `d7e427c`, run today.
- "Canonical": for W, F and the spans, the reconstruction **is** the canonical function (`derived.py`). For hit rates no canonical computation is chosen yet (definitions.md ⚠; owner's decision 4).

| Value (decisions.md line) | Published | Original | Reconstruction = canonical | Cause |
|---|---|---|---|---|
| W/C p90, λ = 2.5 (253) | 0.75 | 0.75 | 0.756 | Grid: the original sampled W every **5 s** from 600 s, the reconstruction every 1 s |
| W/C mean, λ = 4 (256) | 1.01 | 1.006 (97,248 tok) | 1.004 | same |
| W tokens, λ = 2 / 2.5 / 3 (405–409) | 47.6k / 59.7k / 73.0k | 47,580 / 59,722 / 72,968 | 47.49k / 59.64k / 72.85k | same; the 72k entry reused the 2026-11-01 output |
| 72,480 / W, λ = 2.5; 96,656 / W, λ = 3 (409) | 1.21; 1.32 | 1.214; 1.325 (DERIVED from the original W) | 1.215; 1.327 | follows from W |
| W tokens, 20 s gaps, λ = 3 (499) | 74.8k | 74,843 | 74.54k | Grid **10 s**, `gap5_base.yaml` with the gap overridden |
| F_warm/C mean, λ = 3 (254) | 0.13 | 0.125 | 0.1246 | Double rounding in the published value; original and reconstruction agree |
| (W+F)/C: λ = 3 warm high, λ = 3 cold low, λ = 4 warm low / high (254–256) | 0.91; 1.16; 1.32 / 1.36 | no code; sums of 2-decimal values (0.75 + 0.16, 0.75 + 0.41, 1.01 + 0.31, 1.01 + 0.35) | 0.918; 1.168; 1.311 / 1.353 | Hand arithmetic on rounded values. At the original's precision: 0.919; 1.170; 1.313 / 1.355 (DERIVED). Every fits/holds yes/no is unchanged |
| F_warm tokens, λ = 2 / 2.5 (405–406) | 6.4k / 8.7k | **not found** | 6.51k or 5.96k / 8.78k or 9.08k | 8.7k = 0.090 × 96,656 = 8,699 (DERIVED). 0.09 is the control r2.5 end-window KV printed to 2 decimals (`…215355_toolu_01ERXSiZ…`); as the origin this is a BELIEF. 6.4k: no source |
| Hit "before", `wipe_test_idle` (226) | 0.773 | 0.773 | 0.771 / 0.774 | Window: the original used **the 120 s before the wipe**, not 240 s → wipe. The preempt value (0.774) matches under both |
| Adjacent-window noise: 300 s rose ≥ 0.02 / p95; 600 s p95 (269) | 0.34 / 0.076; 0.059 | 0.34 / 0.076; 0.059 | none of the tried readings matches all three | Start: the original slid 60 s steps **from t = 600 s** to 7200 − 2w. The reconstruction tried 0 s and 240 s. `hit_climb: 0.06` rests on 0.059, which every reading reproduces |
| Long run, last third, counter (116) | 0.6254 | 0.6254 | 0.62549 | Small window difference; cause not established (`judge.py`) |
| λ = 3 wipe 0–15 s max (339) | 0.30 | 0.295 | 0.295 | Rounding only |

**Effect on results: none.** The verdicts don't use any of these numbers, and the one threshold set from them (`hit_climb`) is reproduced.

## Phase 2: proposal for items 34–43

### Commits (Phase 3, after approval), one entry each
1. **`[CORR]` Hit-rate methods mixed (item 35).**
   - What was wrong: 2026-11-03 "hit 0.757 at λ = 7 against about 0.42 at λ = 5". The first is `load.summarize` (mean of ratios). The second matches a counter ratio: windowed counter 0.424 in `20261030-141658_sweep_pc_on_r5`, or ramp peak `_level` 0.419 / 0.407.
   - Like for like: 0.757 vs 0.378 (mean of ratios); 0.785 vs 0.424 (windowed counter); 0.785 vs 0.446 (whole run).
   - Also states where 0.767 / 0.661 / 0.525 came from: the original F script printed a whole-run counter.
   - Restates the pool effect by one method: windowed counter −0.079 / −0.118 / −0.095.
   - Affects: no result. The direction holds.
   - Rule: J.
2. **`[CORR]` decisions (6): 14 of 25 differences explained by the recovered originals, 6 by rounding (item 37).** Commits `analysis/recovered/` with `INDEX.md`, and adds the "original" column to `recompute_published`.
   - **Deviation from your wording:** "one file per figure" can't be verbatim. Several tool calls print several figures, and one figure (the λ = 3 spans) comes from three calls. So it's one file per tool call, and the index maps figure → file.
3. **`[CORR]` Used configs that cannot be fixed (item 43).** `stage2_base.yaml` lacks `pf_climb`, `hit_climb`, `drain_horizon_s`, and the wipe tests' shape (900 s, wipe at 450 s) can't hold the watch window. So `verdict` cannot judge `wipe_test_*` or `stage2_control_r1.5`. None was meant to be judged (decisions 2026-11-01 "Live wipe test"). Plus the definitions.md section:
   > **Used configs that cannot be fixed (rule 5).** `configs/stage2_base.yaml`: (a) the comment at :21 says "req/s^2"; the unit is req/s (decisions 2026-11-04 [CORR]). (b) `verdict:` lacks `pf_climb`, `hit_climb`, `drain_horizon_s` and keeps the retired `q_slope`, `climb`, `end_s: 300`. Runs that use it directly (`wipe_test_preempt`, `wipe_test_idle`, `stage2_control_r1.5`) cannot be judged by `load.verdict`. Every judged Stage 2 run gets these keys from `stage2_cap_base.yaml:7-13`.
4. **definitions.md "session median"** (item 36), text as in row 36.
5. **`[REG]` REG-2, REG-3, REG-4** (items 38–40), each after its rule-F review. Each review is a separate pass that sees only the registration. That needs a subagent or fresh session, which I won't start without your go-ahead.
6. **`[DECISION]` items 41 and 42**, if you take them.
7. **Push (item 34):** after 1–6, `git push origin main`; or now, `git push origin 46f81cf:main` only.

### REG-2 draft (item 38): cold-state floor, analysis only, 0 GPU h
- **Definition, fixed before computing:**
  - μ_sat,off(setup) = the mean of `load.summarize` throughput over the **valid** cache-off sweep runs at λ ≥ λ_sat. λ_sat is the lowest swept λ whose mean `kv_cache_usage_perc` over 240–900 s is ≥ 0.85.
  - Undefined if no swept λ reaches 0.85, or if only one run qualifies. In that case the setup is "no floor measured".
- **Claim tested:** M2's weaker floor. Under B, a stuck state at λ needs λ > μ_sat,off.
- **Classification band (needs your choice):** "at" if |λ − μ_sat,off| ≤ 0.05 μ_sat,off (the capacity rule's 5 %); else below or above.
  - The alternative is the min–max of the contributing runs.
  - Either way the band is chosen with the default-pool values visible, so state that in the entry.
- **Check of B:** in every window where a cache-on server had a backlog the whole time (waiting ≥ 1 at every scrape), its completions/s must be ≥ μ_sat,off of its setup. Without that condition B "fails" trivially in any lightly loaded window. Windows:
  - the cache-on sweep runs that fail the capacity rule (default λ = 5, 6, 8, 10; 72k λ = 5; 5 s gaps λ = 7);
  - the ramp steps with λ ≥ 4.5;
  - the backlogged spans of all 15 bursts (from burst start until waiting first returns to 0).
- **Predictions, before computing:**
  - default pool: μ_sat,off ≈ 3.50 (DERIVED from published values, so not a test), λ = 3 below (6 runs), λ = 3.5 at (6 runs);
  - 72k: λ = 3 below, if λ ≤ 4 reaches KV 0.85 (the 72k cache-off λ = 4 throughput is 3.449, model.md M2);
  - 5 s gaps: no floor measured (12 runs unclassifiable) → REG-4.
  - **So the expectation is that 0 of the 30 shock runs lie above a measured floor.**
- **Decision under each outcome:**
  - All runs at or below the floor: the negative result is restated as "loads at or below the cold-state floor recover, as M2 requires". PROTOCOL §7's "0 of 30" gets that qualifier, and the gate (rule G) uses μ_sat,off.
  - Some runs above it: those cells are the only real tests, and they get named.
  - B fails anywhere: the floor argument is dropped, M2's ledger is updated, and A becomes the only bound (REG-1).
- **Alternatives:**
  - 900 s cache-off "saturation" is not steady (KV was still rising, N1), so μ_sat,off may overstate the sustained rate (REG-3 tests this);
  - dev mode was off in the sweeps and on in the shocks (A6);
  - the burst mix (1408-token one-offs) differs from session traffic.
- **Output:** a definition, prediction and outcome section in `docs/model.md` (M2b), and a ledger row.

### REG-3 draft (item 39): cache-off λ = 3, 3600 s, default pool (GPU, needs your approval)
- **Config:** a new `configs/long_pc_off_r3.yaml`, extending `base.yaml` like the Stage 1 sweeps:
  - no dev mode, to match μ_sat,off;
  - `--no-enable-prefix-caching`, cap 256 stated, `duration_s: 3600`, `warmup_s: 240`;
  - **seeds 0 and 1.** Seed 0 for comparability with the sweep; seed 1 because of N1, since a single realization is what's in question.
- **Bounded-queue criterion, fixed now.** Judged window 600–3600 s. All three must hold:
  - (i) `load.summarize`-style throughput over the window ≥ 0.95 × the realized planned rate in it;
  - (ii) least-squares waiting slope over the window ≤ 0.01 req/s;
  - (iii) mean waiting over the last 600 s ≤ 5 × max(1, mean waiting over 600–1200 s).
- **"Growing":** (ii) fails and the last 600 s mean exceeds the first 600 s mean. Anything else is "unclear".
- **Prediction:** bounded at both seeds, with throughput ≈ 3.0.
- **Decision under each outcome:**
  - Bounded: λ = 3 is at or below cache-off capacity at the default pool, so the 12 λ = 3 runs are not danger-zone tests. This supports adopting μ_sat,off (item 41).
  - Growing: 900 s cache-off throughput is not a sustained capacity; B or the floor fails; μ_sat,off is not used as an edge; λ = 3 stays in the zone.
  - Split across seeds: the arrival realization matters, and capacity needs more seeds before any edge is moved (A1).
- **Alternatives:** transient excursions at ρ ≈ 0.86 with bursty session arrivals can look like growth over a short span; criterion (ii) over 3000 s is meant to tolerate that.
- **Cost:** about 1.1 GPU h per seed, about 2.2 h in all.

### REG-4 draft (item 40): 5 s-gap cache-off beyond λ = 3.5 (GPU, needs your approval)
- **Config:** a new `configs/sweep_gap5_pc_off_ext.yaml` (λ = 4, 4.5, 5, 6), the same shape as `sweep_gap5_pc_off.yaml`: 900 s, seed 0, no dev mode.
- **Stopping rule:** stop after the **second** λ with mean KV ≥ 0.85. This makes REG-2's definition computable. Your 0.9 would be a stricter variant; choose one.
- **Cost:** about 0.27 h per run, at most 1.1 h.
- **Prediction (BELIEF):** μ_sat,off at 5 s gaps ≈ 3.3–3.5 (throughput was already 3.26 at λ = 3.5).
- **Decision:**
  - If 4.5 > μ_sat,off: the 6 runs at λ = 4.5 with 5 s gaps are the only shock tests above a measured floor, and "0 of 6" there is the study's informative cell.
  - If not: no tested cell is above its floor.
  - Either way, it decides whether 60 s gaps, or a load just above the floor, is the next test.

### Item 41: danger-zone lower edge μ_off → μ_sat,off (your decision; consequences, conditional on REG-2)

| Setup | Zone now | Zone with μ_sat,off | Shock runs that still count as tests |
|---|---|---|---|
| Default pool, 20 s | (2, 4) | about (3.50, 4); λ = 4 is `bad_baseline` | 0 of 12 (λ = 3 below; λ = 3.5 at the edge, out under strict inequality) |
| 72k pool, 20 s | (2.5, 4) | (μ_sat,off, 4), likely about (3.45, 4); λ = 3.5 is `bad_baseline` | 0 of 6 if λ_sat ≤ 4 |
| Default pool, 5 s | (2.5, 6) | unknown until REG-4 | 0–6 (λ = 4.5 only) |

- **For the hypothesis:** with this change, at most 6 of the 30 runs were real tests, and none of the 12 default-pool runs was.
- **Against it:** the edge is being moved after the results, in the direction that explains away nulls. It must be marked **[new]** with this sentence, and PROTOCOL §3's negative-result rule must state both counts.
- Apply the same scrutiny to μ_warm: the 900 s rule with seed 0 also set it, and λ = 4 failed its 2400 s control. A symmetric definition would be "the highest λ with a `recovered` 2400 s no-trigger control".

### Item 42: capacity rule, future sweeps only
- **`[DECISION]` text:** "From the next sweep on, the throughput test is throughput ≥ 0.95 × realized planned arrival rate over the measured window (`schedule.parquet`). Past μ values stand as judged."
- **Code:** a new `load.capacity` argument read from config, so old configs keep the old rule, with a test.

## Where I disagree or had to choose
1. **35 and 36 were largely done** before this addendum, in decisions (4) and (7). 35's "match neither" is wrong: the values match the whole-run counter. The new part is the λ = 7 / λ = 5 pair.
2. **38's threshold isn't blind** for the default pool (row 38). The registration should say so, rather than present the default-pool classification as a test.
3. **38 and 40 use different KV thresholds** (0.85 and 0.9).
4. **I didn't push (34)** and didn't start the rule-F review passes. Both are outward or agent-spawning actions outside "stop after Phase 2".
