# REG-24 draft 1: C1's confirmation run at λ = 2.0 (not registered)

Draft for rule F (adversarial review) and the owner-proxy. It is not a decisions.md entry. Nothing in it is approved, and no GPU run follows from it. Its code, configs and tests come as one patch, `docs/drafts/reg24_r1/reg24.patch`, made against `a7bb77a`. The patch adds four new files and changes no existing file.

Line numbers in `FILE(docs/decisions.md:…)` refer to the main checkout's decisions.md. Lines up to 3910 are the same at `a7bb77a`, since the log is append-only.

---

## 2026-11-14 · [REG] REG-24 (draft): C1's confirmation at λ = 2.0, seed 43: a no-burst control, then the burst run on the same schedule, each with a 4500 s watch, then λ = 1 for 9000 s, then back to λ = 2.0 for 1500 s (GPU, ≈ 9.1 h for both runs)

- **ID and scope.** REG-24 is confirmatory for C1's conditions 5 and 6 (PROTOCOL §3) at one load, λ = 2.0, in one seed (FILE(PROTOCOL.md:37), FILE(PROTOCOL.md:38)).
  - It does not test C1 as a whole. Condition 3 is REG-19's `supports` (FILE(docs/decisions.md:16517)). Condition 4's order clause is judged by no registration.
  - **Not approved.** No GPU run happens before the owner approves this entry.

- **Why now.**
  - REG-19 gave `supports`, 5 of 5, under its whole-window test (FILE(docs/decisions.md:16527)).
  - Its registered branch for `supports` reads (FILE(docs/decisions.md:16565), quoting FILE(docs/decisions.md:3803)): "draft C1's confirmation at λ = 2.0 for the owner: a 4500 s watch, then a drop to λ = 1 long enough for the line to empty (REG-16's calibration), then the return (conditions 5–6), on a seed chosen by a rule fixed before its schedule is read."
  - `agent/DECISION_TREE.md` gives the order: register the confirmation, then run it after REG-20's gate (FILE(agent/DECISION_TREE.md:13)). That gate has been computed: `may_start` True (PROBE(docs/probe/reg20/gate_20261113T230307Z.txt), FILE(docs/decisions.md:16729)).
  - REG-19's own alternative 1 names what only this run separates: "a state that holds only while the load stays at 2.0 from one that also outlasts a lower load. Only C1's confirmation with its drop and return (conditions 5–6) separates them" (FILE(docs/decisions.md:16555)).

- **Question.** At λ = 2.0 with closed-loop turns (L1, 350 W):
  - **(5)** After the 180 s burst, is the server still `stuck` 4500 s after the burst ends? It must not have recovered, and its waiting line must not have emptied, at any point in the watch.
  - **(6)** λ then drops to 1 req/s for 9000 s and returns to 2.0 for 1500 s. Does the waiting line empty during the drop? Are the return's last 600 s `recovered` against the original baseline?
  - **(control)** On the identical session schedule without a burst, does the server stay warm for the whole 16080 s?

### Setup

- **Burst run:** `configs/confirm_l1pl350cl_r2.0_s43.yaml`.
  - It extends `burst_l1pl350cl_r2.0_s2.yaml`, the parent of REG-19's λ = 2.0 burst configs.
  - It sets `seed: 43`, `workload.duration_s: 16080`, `workload.steps: [{at_s: 5580, rate: 1}, {at_s: 14580, rate: 2.0}]` and `verdict.watch_s: 4500`.
- **Control:** `configs/stage2_control_l1pl350cl_r2.0_long_s43.yaml`.
  - It extends `stage2_control_l1pl350cl_r2.0_s2.yaml`, the parent of REG-19's controls, with the same four values.
- **Only five keys differ.** Resolved, each file differs from each of REG-19's ten configs only in `name`, `seed`, `workload.duration_s`, `workload.steps` and `verdict.watch_s`.
  - Test: `test_registered_configs_are_the_design_at_the_pick`, which compares every pair against `seed 15–19`.
  - So both runs are L1, the 350 W check, closed-loop turns, force_close and dev mode.
  - The burst run's burst starts at 900 s and lasts 180 s, at 2.4 req/s with 2944-token prompts, with `burst_min_kv_max` 0.95.
  - The control has no trigger and `control_t_s` 1080.
  - No harness, check or threshold changes. `workload.steps` is the existing load-step mechanism that REG-15 and REG-16 used.
- **One schedule for both runs.** The control's 23194 session requests equal the burst run's session rows, row for row, on `t_planned`, session, turn and prompt length (DERIVED, `confirm.inputs`, `control_schedule_same` True). The burst draws 463 requests from its own generator.
  - A shorter control could not share the schedule: `build_schedule` draws every segment from one generator (FILE(docs/decisions.md:3151)).
- **Phases** (absolute s; DERIVED, `confirm.phases`):

  | phase | span |
  |---|---|
  | baseline | 300–900 |
  | burst | 900–1080 |
  | watch | 1080–5580 |
  | drop at λ = 1 | 5580–14580 |
  | return at λ = 2.0 | 14580–16080 |
  | return's end | 15480–16080 |

  The control uses the same phases. Its `load.verdict` is judged at 1080 + 4500 s against its own baseline, 480–1080 s.
- **Judged windows.** `verdict.end_s` is 600 in the resolved config.
  - The burst run's verdict judges the end window 4980–5580 and the previous window 4380–4980.
  - Condition 6 judges 15480–16080.
  - `test_load_verdict_judges_the_registered_windows` calls `load.verdict` itself on a synthetic run at this config.
- **Deviation from PROTOCOL §3's wording, for the owner.** Condition 6 says "λ drops to 1 req/s for 1800 s" (FILE(PROTOCOL.md:38)). This design drops for 9000 s.
  - The owner's delegate already kept conditions 5–6 with a drop "fixed beforehand from the expected backlog and the cold floor with a factor of two; 1800 s was too short and 9000 s enough in those two runs" (FILE(docs/decisions.md:3948)).
  - Approving REG-24 approves this length. PROTOCOL §6 then needs a row for it, which this draft does not write: PROTOCOL is not the agent's to edit.

### Drop length: derivation

- **Why 1800 s failed.** REG-15's 1800 s drop at λ = 2.2 never emptied the line (`drop_inconclusive`, FILE(docs/decisions.md:3085)). Its two [CORR]s say why:
  1. The clients lagged 856–930 s, not the 4–6 minutes assumed (FILE(docs/decisions.md:3129)).
  2. The server received 1.582 req/s during the drop, not ≈ 1, because sessions released turns planned before the drop. A drop length "must come from the total backlog (server waiting plus turns not yet released), computed by a committed function" (FILE(docs/decisions.md:3135), FILE(docs/decisions.md:3136)).
- **Model 1: REG-16's request model, unchanged.** It is `gate.reg16_empty_time`, copied as `confirm.empty_time_requests` on a schedule already built. The test checks it equals the original on REG-16's configs and gives REG-16's published 4340 s and 5540 s.
  - It sums the owed backlog at the trigger (28), every request planned since (session and burst), and subtracts completions at REG-15's cold rates: 1.758 req/s to the watch's end and 1.672 in the drop (RUN(20261110-085730_confirm_l1pl350cl_r2.2_s12, gate.reg16_calibration), FILE(docs/decisions.md:3156)).
  - The owed backlog counts turns planned but not yet released, which answers both [CORR]s. Client lag and the received load enter through what was planned, not through when it was sent.
  - **Pessimistic version:** REG-15's lowest 600 s rate per phase, lowered by `c_pessimism` 0.05 (FILE(docs/decisions.md:3159)). That gives 1.678 in the watch and 1.587 in the drop.
- **Model 2: a token model.** This is the decision tree's K3 row: "The confirmation run's drop is sized from U_off and the mean served prompt" (FILE(agent/DECISION_TREE.md:59)). It is `confirm.empty_time_tokens`.
  - Every prompt token planned since the trigger (session and burst, no cache hit) is owed work.
  - The cold engine does that work at U = r × U_off, with U_off 5164.76 uncached tokens/s. U_off is the mean over REG-8's five saturated cache-off runs (PROBE(docs/probe/reg21/batch1_20261113T224220Z.txt), `k3w.reference`).
  - The drop's empty time is when the work owed since the trigger is done.
  - **Expected:** r 1.021, the λ = 2.0 group's median in REG-21's batch 1 (FILE(docs/decisions.md:16421)). That gives U 5273.03.
  - **Pessimistic and optimistic:** r 0.95 and 1.05, REG-21's J1 tolerance. That gives U 4906.52 and 5423.00 (DERIVED, `confirm.u_rate`).
- **The model checked out of sample, as a readout and not a gate.** No tolerance is judged; the numbers were seen before the test pinning them was written.
  - REG-15's calibration was made at λ = 2.2. On REG-19's five λ = 2.0 schedules (DERIVED, `confirm.model_check_reg19`, schedules only), the request model's expected owed backlog is:
    - at 4080 s: 1342, 1271, 1539, 1049, 1171;
    - at 1680 s: 577, 601, 860, 655, 466.
  - REG-19 measured the total line (waiting, running and unreleased turns; `gate.owed_backlog`, FILE(analysis/gate.py:1079), used at FILE(analysis/gate.py:1995)) for seeds 15–19 (FILE(docs/decisions.md:16533)–FILE(docs/decisions.md:16537)):
    - at 4080 s: 1320, 1226, 1511, 1050, 1155;
    - at 1680 s: 555, 551, 811, 612, 444.
  - The model is higher by −1 to +45 requests at 4080 s and by +22 to +50 at 1680 s (DERIVED). It errs a little towards a longer drain.
  - The pessimistic version gives 1303–1793 at 4080 s, 253–282 above the measured values (DERIVED).
- **REG-16's measured drain supports `warm_watch_s` 1200 s.**
  - REG-16's control was cold with a queue of 113 at the drop's start. The queue fell to 47.6, then 9.0, then 0.000 in 6600–6900 s, and hit came back to 0.840 in that same 300 s window (FILE(docs/decisions.md:3387)–FILE(docs/decisions.md:3390)).
  - The cache re-warmed within one 300 s window of the line emptying, so 1200 s after the predicted empty time leaves four such windows (DERIVED).
- **For seed 43 at 9000 s** (DERIVED, `confirm.inputs`; s into the drop):

  | model | optimistic | expected | pessimistic |
  |---|---|---|---|
  | requests (owed backlog at 5580 s: 1670 expected, 2043 pessimistic) | n/a | 2490 | 3550 |
  | tokens (excess work at 5580 s: 4.883 / 5.585 / 7.300 M tokens) | 2130 | 2560 | 4080 |

- **The factor of two from FILE(docs/decisions.md:3948) also holds** (DERIVED):
  - twice the later expected time plus 1200 s is 2 × 2560 + 1200 = 6320 s, which is ≤ 9000;
  - against the open-loop cold floor, 1670 / (1.681 − 0.994) = 2431 s, and 2 × 2431 = 4862 s, which is ≤ 9000.
- **Planned λp per 600 s window of the drop**, from 5580 s (DERIVED, `confirm.inputs` `drop_by_600`), on the planned schedule (REG-15's review N1):

  1.082, 0.967, 0.920, 1.055, 0.917, 1.135, 1.053, 0.875, 0.920, 0.982, 0.885, 0.885, 1.168, 1.045, 1.017

  - Mean 0.994. The highest 120 s window starting inside the drop is below 2.158. The 2.158 window itself, [5460, 5580), ends where the drop starts, so it belongs to the watch (DERIVED, `confirm.inputs` `peak_120s`, `t_peak_120s`; `rolling_rate` windows are [g − 120, g), FILE(analysis/gate.py:1356)).
  - What the server receives in the drop will be higher than planned at first, as in REG-15 (1.58), because turns planned before it are still being released. Both models count those turns as owed.

### Seed and drop: the rule, fixed before any candidate's schedule was read

- **Rule** (`confirm.seed_rule`, `confirm.design_row`):
  - The candidates are seeds 40–199 that no config uses. REG-24's own two configs are left out, so the rule gives the same pick once they exist.
  - Seeds are tried in order. For each seed, the drop candidates are tried in order: 3600, 5400, 7200, 9000 s.
  - The pick is the first (seed, drop) for which the burst config's schedule passes all of:
    - **W:** each of the four judged windows (baseline 300–900, previous, end, return's end) has planned session λp within ± 5 % of 2.0. This is REG-15's `window_tol` (FILE(docs/decisions.md:2886)).
    - **E:** the highest 120 s planned rate anywhere from 240 s to the end of arrivals is below `surge_tip` 3.2 (REG-17's, FILE(analysis/gate.py:1474); REG-18/19's exposure grid). Neither run is then exposed to a self-tipping surge, the return included.
    - **F:** the later of the two pessimistic empty times, plus `warm_watch_s` 1200 s (REG-16's), fits in the drop.
  - Seeds come before drops. REG-16's review N5 noted that taking the shortest drop first picks the lightest schedule that fits it (FILE(docs/decisions.md:3167)).
- **Collision with REG-20b.** REG-20b, if it is ever registered, takes "seeds 20, 21, … (the first unused)" (FILE(agent/DECISION_TREE.md:33)).
  - REG-20's gate passed, so REG-20b now follows only REG-20's `inconclusive` (FILE(agent/DECISION_TREE.md:37)).
  - REG-24 starts at 40 and leaves 20–39 to REG-20b. Even at REG-18's cold share of 1 in 4, the 20 seeds needed for "5 cold closed runs expected" fit in 20–39 (DERIVED: 5 / 0.25 = 20).
  - If REG-20b ever needed more, "first unused" skips 43, because REG-24's configs set it.
  - In the main checkout no config sets any seed above 19 (DERIVED, the configs' `seed:` lines).
- **Timing.** The code and its tests were frozen at 2026-11-13 23:23:39 UTC:
  - `analysis/confirm.py` sha256 `6801457c1b7aec9ef429e4d11a01828ff2ba730f21bb60e920ddaa08bf49c268`, with `seed` and `drop_s` set to None;
  - `tests/test_confirm.py` sha256 `867aba60fb93e8c1968e2645ba5006497348ebf8817dc36b5da864ac9a09cf0c`.

  The rule ran once, 23:23:45–23:23:47 UTC, rc 0, and its output was saved in the agent's scratchpad (not committed).
  - **After the freeze `confirm.py` changed in two places only:**
    - the `seed` and `drop_s` values were filled in;
    - readouts were added to `inputs()`: `watch_spans_300`, `watch_lowest_span`, `t_peak_120s`, `peak_120s_inside_judged` and `lam_p_control_own_baseline`.
  - `seed_rule`, `design_row`, both models and every setting are byte-identical. A reviewer can check this: revert those two hunks of the patch's `confirm.py` and the sha256 above comes back.
  - The tests gained the pick's tests (below).
  - Set before the freeze, after REG-15/16/19's results and before any candidate schedule was read:
    - the seed range 40–199 and the 3600 s candidate;
    - the token model and its band;
    - the order of seed first, then drop.
- **Output, every row up to the pick** (DERIVED, `confirm.seed_rule`; λp req/s; empty times in s into the drop, pessimistic in brackets):

  | seed | drop | baseline | previous | end | return's end | 120 s peak (at s) | empty, requests | empty, tokens | W | E | F |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | 40 | 3600 | 2.548 | 1.992 | 1.943 | 2.030 | 3.292 (10540) | 2140 (3050) | 2190 (3540) | no | no | no |
  | 40 | 5400 | 2.530 | 1.973 | 1.983 | 1.892 | 3.267 (725) | 2290 (3140) | 2370 (3560) | no | no | yes |
  | 40 | 7200 | 2.550 | 1.977 | 1.957 | 2.120 | 3.175 (745) | 2410 (3260) | 2440 (3650) | no | yes | yes |
  | 40 | 9000 | 2.523 | 1.955 | 1.968 | 2.208 | 3.175 (645) | 2580 (3490) | 2610 (3830) | no | yes | yes |
  | 41 | 3600 | 1.808 | 2.060 | 1.865 | 2.007 | 2.975 (9620) | 1740 (2610) | 1810 (3180) | no | yes | no |
  | 41 | 5400 | 1.843 | 2.057 | 1.863 | 2.178 | 2.850 (3960) | 1890 (2680) | 1970 (3240) | no | yes | yes |
  | 41 | 7200 | 1.835 | 2.062 | 1.853 | 1.960 | 2.850 (14120) | 1940 (2650) | 2040 (3080) | no | yes | yes |
  | 41 | 9000 | 1.828 | 2.040 | 1.875 | 2.167 | 2.825 (3960) | 1690 (2690) | 1760 (3140) | no | yes | yes |
  | 42 | 3600 | 2.263 | 2.135 | 2.075 | 1.805 | 2.983 (675) | 2400 (3450) | 2460 (never) | no | yes | no |
  | 42 | 5400 | 2.275 | 2.117 | 2.072 | 1.868 | 2.950 (810) | 2510 (3560) | 2650 (3870) | no | yes | yes |
  | 42 | 7200 | 2.293 | 2.118 | 2.067 | 1.902 | 2.867 (670) | 2610 (3760) | 2640 (4170) | no | yes | yes |
  | 42 | 9000 | 2.275 | 2.138 | 2.060 | 1.997 | 2.875 (780) | 2630 (3530) | 2670 (4090) | no | yes | yes |
  | 43 | 3600 | 2.032 | 2.008 | 2.047 | 2.173 | 2.942 (10505) | 2390 (3310) | 2430 (never) | no | yes | no |
  | 43 | 5400 | 2.025 | 2.012 | 2.050 | 1.828 | 2.800 (2450) | 2450 (3270) | 2520 (3760) | no | yes | yes |
  | 43 | 7200 | 2.057 | 1.998 | 2.057 | 1.693 | 2.892 (13560) | 2430 (3470) | 2500 (3860) | no | yes | yes |
  | **43** | **9000** | **2.022** | **1.985** | **2.068** | **1.903** | **2.733 (2450)** | **2490 (3550)** | **2560 (4080)** | **yes** | **yes** | **yes** |

  - **The pick: seed 43 with a 9000 s drop** (`test_seed_rule_picks_seed_43_at_9000_s`).
    - Seeds 40, 41 and 42 fail W at every drop, on their baselines (2.52–2.55, 1.81–1.84 and 2.26–2.29).
    - Seed 43 fails W at 3600, 5400 and 7200 s, each time only on the return's end (2.173, 1.828, 1.693).
    - The drop changes the whole schedule (Setup), so each row is a different schedule.
  - **W alone decides the pick.** Every row before it fails W. Any variant of F or E that passes at (43, 9000) gives the same pick, including the factor-two form of FILE(docs/decisions.md:3948) (DERIVED).
  - The 9000 s drop is forced by the return's end window, not by the drain. The drain needs about 3600–5300 s (the later pessimistic time plus 1200 s).
- **Post-pick scan** (readout only, computed after the pick; `confirm.seed_scan`, 160 candidate seeds):

  | drop | W | E | F | all three | lowest seeds passing all | median pessimistic empty, requests / tokens |
  |---|---|---|---|---|---|---|
  | 3600 | 7 | 144 | 0 | 0 | none | 3190 / 3250 |
  | 5400 | 6 | 142 | 117 | 4 | 61, 68, 173 | 3370 / 3890 |
  | 7200 | 5 | 141 | 160 | 5 | 68, 79, 81 | 3360 / 3855 |
  | 9000 | 7 | 144 | 160 | 7 | 43, 61, 68 | 3410 / 3840 |

  - W is the binding condition: 5–7 of 160 seeds pass it at each drop.
  - A drop-first rule (REG-16's form) would have picked seed 61 at 5400 s, about 1 GPU h cheaper for the pair (DERIVED: 2 × 3600 s). The frozen rule stands.
  - The cost of the pick against seed 61 is ≈ 1.0 GPU h, for which the drop has about 3700 s more margin than F needs (DERIVED: 9000 − 4080 − 1200 = 3720).
  - The owner may prefer the cheaper design. That would be a change of rule after seeing the scan, so it must be named as one.

### Design inputs for seed 43, 9000 s

All values are DERIVED from the configs alone with `uv run python -m analysis.confirm reg24_inputs` (`confirm.inputs`).

- **Requests:** 23194 session and 463 burst. The control's schedule equals the burst run's session rows.
- **Planned λp by phase:**

  | phase | λp |
  |---|---|
  | baseline (300–900) | 2.022 |
  | watch | 2.015 (thirds 1.969, 2.035, 2.039) |
  | drop | 0.994 |
  | return | 1.999 |
  | the control's own `load.verdict` baseline (480–1080) | 2.017 |

  The control's own baseline has no tilt; REG-16's had 2.430 against 2.210.
- **Judged windows:** baseline 2.022, previous 1.985, end **2.068**, return's end **1.903**.
- **The watch's 300 s windows** from 1080 s:

  1.800, 1.840, 2.260, 1.830, 2.117, 1.943, 2.113, 1.803, 2.243, 2.073, 2.090, 1.827, 2.143, 2.013, 2.123

  - The lowest, 1.800, is the first window (1080–1380). A break there would be read as a delayed onset, not a re-formed collapse (REG-15's N3). It still scores `reformed`, which works against `confirms`.
  - Five windows sit at 1.80–1.84, near REG-19's cold completion rate of 1.703–1.800 (FILE(docs/decisions.md:16539)). These are the likeliest places for the line to empty in the watch.
- **Highest 120 s windows by phase:**

  | phase | peak | window, s |
  |---|---|---|
  | before the burst | 2.442 | [180, 300) |
  | watch | 2.733 | [2330, 2450) |
  | drop | 2.158 | [5460, 5580), the watch's tail |
  | return | 2.650 | [14630, 14750) |

  - None reaches 3.2. REG-19's five controls carried 2.833–3.092 without tipping (FILE(docs/decisions.md:16542)).
- **The heavier judged window is the one judged `stuck`.** The highest 120 s window lying inside each judged window (`peak_120s_inside_judged`): end window 2.408, return's end 2.292.
  - **This is the opposite of REG-15's bias** (FILE(docs/decisions.md:2895)). The end window carries 8.7 % more planned load than the return's end (DERIVED: 2.068 / 1.903 = 1.087). Both are inside ± 5 % of λ, and the heavier side is the one judged `stuck`, so the planned load favours `confirms`.
  - The tolerance (REG-15's) admits it. The design answers it with the control (Designs, below) and with the cold completion rate. REG-19 measured c 1.703–1.800 in all 40 spans of W (FILE(docs/decisions.md:16539)), below both 2.068 and 1.903. So a cold server falls behind in either window, and a warm one carries both.
- **The models' predictions at the watch's end:**
  - owed backlog 1670 expected, 2043 pessimistic;
  - excess token work 5.585 M at expected U.

### Designs: with and without a same-seed control

| design | runs | GPU h (DERIVED below) | what it can show | what it cannot show |
|---|---|---|---|---|
| **A: burst run only** (REG-15's design) | 1 | ≈ 4.6 | Conditions 5 and 6 in one run: stuck through 4500 s, the line empties at λ ≈ 1, the return's end `recovered`. | Whether the warm server carries this schedule's 4500 s watch. No λ = 2.0 control has run longer than 4080 s: the λ = 2.0 control configs have `duration_s` 2580 (REG-17/18, seeds 2–7) or 4080 (REG-19, seeds 15–19) (DERIVED, resolved configs). REG-16 showed a no-burst control going cold on a long schedule at 2.2 (FILE(docs/decisions.md:3373)). So a stuck end window cannot be told apart from what this schedule does to a warm server, and the end window is the heavier one (8.7 %, above). It also cannot stop early: the full 4.6 h is spent whatever happens. |
| **B: control first, then the burst run** (REG-16 then REG-17, as planned at 2.2) | 2 | ≈ 9.1 (≈ 8.4 expected) | Everything A shows, plus that the same arrivals without the burst stay warm through the watch, the drop and the return. The pair then isolates the burst's history: same load, two states. If the control goes cold, the burst run is not made, which saves ≈ 4.6 h, and the cell is reported as unstable at 4.5 h. | More than one seed (n = 1 per run; rule H: "single control"). Run order: the control always runs first, ≈ 4.6 h earlier (`reg19_baseline_pair` reads it). Whether a cold state survives a drop that is shorter than needed to empty it. |

- **Recommendation: B.**
  - Condition 6 is the test that separates two states at one load from overload (FILE(docs/decisions.md:3948)). With the load tilt above, only a warm control on the identical schedule keeps a `confirms` from being explained by load.
  - The extra 4.5 h also buys an early stop.
  - B is the design the study already chose at 2.2 (REG-16), where the control is what turned out to matter (FILE(docs/decisions.md:3408)).
- **The code implements B.** `confirm.table` needs the control's run; `confirm.step` is the only look between the two runs. Design A would need `table` to skip the control (a code change, reviewed again).

### Result: computed once, after the runs are valid and copied

- **Commands.**
  - The queue's only look between the two runs: `uv run python -m analysis.confirm reg24_step` (`confirm.step`). It prints `continue` only, True only if the control's outcome is `control_warm`.
  - After the last run: `uv run python -m analysis.confirm reg24` (`confirm.table`).
  - In the main checkout both run with `AFTERSHOCK_UNSEAL=REG-24` (Operations).
- **Run checks** (`confirm.check`). It refuses:
  - a run that `checks.json` does not mark valid;
  - a run whose config differs from the registered file on any key that file sets (as `gate.reg16_check`): seed, λ, closed loop, force_close, 350 W, the steps and the watch;
  - a burst run without the burst, or a control with any trigger.

  `confirm.phases` refuses any other design. `gate.reg12_only` requires exactly one valid run per pattern, since reruns follow only invalid runs.
- **Control** (`confirm.control_table`): REG-16's outcome (`gate.reg16_control_outcome`, FILE(docs/decisions.md:3194)) on REG-24's phases, against the 300–900 s baseline.
  - **Cold window:** a 300 s window from 1080 to 16080 s with hit ≤ base − 0.06 and pf (by send time) ≤ base − 0.10.
  - **Persistent:** a cold window that ends a phase (5580, 14580 or 16080 s), or a cold stretch of at least 1500 s (`persistent_s`).
  - **`control_warm`** requires all of:
    - baseline pf ≥ 0.98, and the watch verdict's own baseline (480–1080 s) not `bad_baseline`;
    - no cold window;
    - no window with hit ≤ base − 0.06 and waiting > base + 1;
    - `load.verdict` at 1080 + 4500 s `recovered`;
    - the return's end `recovered_against` the baseline.

  Otherwise the outcome is `bad_baseline`, `inconclusive`, `control_cold_persistent`, `control_cold_transient`, `control_unclear` or `control_not_recovered`, in REG-16's order.
- **Burst run** (`confirm.burst_outcome`): REG-15's labels and order (`gate.reg15_outcome`, FILE(docs/decisions.md:2908)), with REG-19's emptying in place of REG-15's single zero scrape.
  - **Emptying** (`gate.reg19_emptyings`'s rule): 0 waiting at a scrape and for the next 30 s, inside the window. A new emptying counts only after the line has refilled.
  - REG-19's test made "stuck through the watch" mean "the line never empties", so an emptying in the watch gets its own label.
  - The labels, in order:
    1. **`bad_baseline`:** `load.verdict` of the 4500 s watch is `bad_baseline` (baseline pf < 0.98).
    2. **`not_persistent`:** the watch's verdict is `recovered` or `slow_drain`.
    3. **`inconclusive`:** `unclear`.
    4. **`reformed`:** `stuck` at the watch's end, but some 300 s window of the watch passed `recovered_against` the baseline (`gate.watch_broken`; each window's λp is reported).
    5. **`emptied_in_watch`:** stuck, never recovered, but the line emptied somewhere in 1080–5580 s.
    6. **`drop_inconclusive`:** the line never emptied in 5580–14580 s (PROTOCOL §3: "inconclusive, not passed").
    7. **`inconclusive`:** the return's end has a missing value.
    8. **`no_return`:** the line emptied in the drop, but the return's end is not `recovered`.
    9. **`confirms`:** everything below holds.
  - `test_burst_outcome_keeps_reg15s_order_where_the_tests_agree` checks that this order equals `gate.reg15_outcome` wherever the two emptying tests agree.
- **Every threshold, and its source.** Nothing is new.
  - From `configs/stage2_base.yaml`, unchanged:
    - `min_baseline_pf` 0.98;
    - `recovered_pf_drop` 0.02, `recovered_hit_drop` 0.06, `recovered_q_excess` 1;
    - `stuck_pf_drop` 0.10, `stuck_hit_drop` 0.06;
    - `pf_climb` 0.05, `hit_climb` 0.06;
    - `drain_horizon_s` 3600.
  - From REG-15: 300 s watch windows.
  - From REG-16: 300 s cold windows and `persistent_s` 1500.
  - From REG-19: 30 s emptying hold.
  - The seed rule's 5 % (REG-15), 3.2 (REG-17) and 1200 s (REG-16) judge the schedule only, never an outcome.
- **What `confirms` requires, all of it:**
  - (a) Both runs are valid and pass `confirm.check`.
  - (b) The control is `control_warm`.
  - (c) The burst run's baseline pf (300–900 s) is ≥ 0.98.
  - (d) `load.verdict` of the 4500 s watch is `stuck` on the end window 4980–5580 against 300–900:
    - pf ≤ base − 0.10 and hit ≤ base − 0.06;
    - no recovery sign against the previous window 4380–4980: hit up < 0.06, pf up < 0.05, and the queue would not empty within 3600 s.
  - (e) None of the 15 windows of 300 s in 1080–5580 s passes `recovered_against` the baseline.
  - (f) No emptying in 1080–5580 s.
  - (g) At least one emptying in 5580–14580 s.
  - (h) The return's end, 15480–16080 s, passes `recovered_against` the baseline: pf ≥ base − 0.02, hit ≥ base − 0.06, mean waiting ≤ base + 1.
- **The pair's outcome** (`confirm.pair_outcome`).
  - The burst run's own label stands whatever the control, when the burst run fails condition 5 or has a gap of its own: `bad_baseline`, `not_persistent`, `reformed`, `emptied_in_watch` or `inconclusive`.
  - Otherwise the label stands only beside `control_warm`.
  - A non-warm control gives `control_not_warm`; the burst run is then not made (`step`).
- **Readouts, never decisive** (`confirm.burst_table`, `confirm.control_table`):
  - every emptying in the watch and the drop;
  - the owed backlog (`gate.owed_backlog`) at the trigger, at the watch's end, at the first emptying in the drop and 600 s after it;
  - **`after_empty`**: hit in [first emptying + 600, + 1200) against the control's hit in the same window, read as `warmed` or `cold_after_empty`. This is REG-16's planned split for `no_return`.
  - the drop's last 600 s;
  - condition 4's levels over the watch's last 1500 s (KV, N, N / baseline N, max N against 256);
  - `release_delay` at each phase's end;
  - the cold side over [1680, 5580) s (c against min(λ, λp));
  - the judged windows' λp from the run's own requests;
  - the 300 s timeline;
  - for the control: its cold windows, `window_mix` and `surge_run`;
  - `gate.reg19_baseline_pair` (the run-order readout of REG-19's alternative 5).
- **K3's blind prediction** (FILE(agent/DECISION_TREE.md:64); `confirm.k3_band`). The first emptying in the drop is compared once with the token model's band:
  - band [2130, 4080] s into the drop; point prediction 2560 s;
  - labels `inside`, `outside_early`, `outside_late`, or `undefined` if there is no emptying.
  - It decides nothing here. It enters the model-against-measurement figure.
  - Batch 2 of REG-21 gives r 1.028 on REG-19's runs (FILE(docs/decisions.md:16798)), which would move the point prediction to 2450 s (DERIVED, `confirm.empty_time_tokens` at 1.028 × U_off). The band does not depend on r.

### Prediction (BELIEF)

- **Each run valid on a given attempt:** ≈ 0.7, with a range of 0.5–0.8.
  - REG-19 lost two attempts to power-offs (FILE(docs/decisions.md:4284), FILE(docs/decisions.md:4293)).
  - Counted per wall-clock hour over REG-19's queue (≈ 40 h), P(no power-off in 4.6 h) ≈ 0.80. Counted per GPU hour (≈ 13 h), it is ≈ 0.50 (DERIVED: exp(−2 × 4.6 / 40), exp(−2 × 4.6 / 13)).
  - REG-15 and REG-16, both long runs, were valid on the first attempt (FILE(docs/decisions.md:3082), FILE(docs/decisions.md:3366)).
- **The control `control_warm`:** ≈ 0.85.
  - All five of REG-19's controls stayed warm through 4080 s with higher peaks (2.833–3.092) than this schedule's 2.733.
  - This run is four times longer, and REG-16 went cold at 2.2 after a 2.78 peak.
- **Given a warm control and a valid burst run:**

  | outcome | p | why |
  |---|---|---|
  | `bad_baseline` | ≈ 0.08 | REG-19's baselines were 0.984–0.998; REG-18 had one at 0.978 |
  | `not_persistent` | ≈ 0.04 | |
  | `reformed` | ≈ 0.03 | |
  | `emptied_in_watch` | ≈ 0.05 | five windows at 1.80–1.84 |
  | `inconclusive` | ≈ 0.02 | |
  | `drop_inconclusive` | ≈ 0.05 | the models put the empty time 2130–4080 s against a 9000 s drop |
  | `no_return` | ≈ 0.08 | |
  | `confirms` | ≈ 0.65 | |

  So P(the pair `confirms`) ≈ 0.55 (DERIVED: 0.85 × 0.65), given valid runs.
- **K3, given an emptying:** `inside` ≈ 0.7, `outside_early` ≈ 0.15, `outside_late` ≈ 0.15.
  - The emptying is a 30 s hold of 0 waiting. The model predicts the work owed since the trigger being done. Turns still unreleased at a 30 s zero would make the measurement early.

### Decision under each outcome

- **`confirms`** (with `control_warm`):
  - C1's conditions 5 and 6 hold at λ = 2.0 in one seed. After the burst the server stayed stuck through 4500 s and left the stuck state when the load dropped. The same arrivals without the burst stayed warm throughout.
  - With REG-19 (condition 3) and REG-22's levels (condition 4; order clause unjudged), C1 then lacks only condition 4's order clause.
  - Report it with "1 of 1, single seed and single control (rule H)" and the bound (one-sided 95 % Clopper–Pearson lower bound 0.05, DERIVED: 0.05^(1/1)).
  - `docs/claims.md` changes only after the owner reviews it.
  - D1/D2 at λ = 2.0 go ahead as `agent/DECISION_TREE.md` plans.
- **`not_persistent`, `reformed` or `emptied_in_watch`:**
  - Persistence beyond REG-19's 3000 s is not shown at λ = 2.0. The cell is "stuck for 3000 s in 5 of 5, not through 4500 s in the confirmation seed".
  - The timeline says when the state ended.
  - No rerun on the label. The owner chooses between a second confirmation seed (a new registration) and reporting the cell as a long transient. C1 is not met at this cell.
- **`drop_inconclusive`:** the line did not empty in 9000 s. That is more than twice the pessimistic model, so the models are wrong for this state.
  - The owed backlog at the drop's end and `release_delay` show which part (server or clients) held.
  - Reported. The owner decides; there is no automatic longer drop.
- **`no_return`:** `after_empty` splits it.
  - **`cold_after_empty`:** the cache stayed cold with the line empty at λ ≈ 1. The cold state is then not held by load, which goes against condition 6's reading and is news in itself.
  - **`warmed`, then cold at the return's end:** a re-trigger on the return (peak 2.650), against a control that carried the same return warm.
  - The owner decides. No further run follows automatically.
- **`control_not_warm`** (the burst run is not made):
  - At λ = 2.0 the warm state does not last on this 16080 s schedule. REG-19's 4080 s controls do not cover a 4500 s watch.
  - Report λ = 2.0 as REG-16 reported 2.2. The owner chooses between another seed by the same rule and the report.
- **`bad_baseline` in either run:** not rerun (REG-19's rule). The owner decides.
- **`inconclusive`:** reported, not rerun (REG-19: "no rerun on any verdict or label"). The owner decides.

### Alternatives (rule A2) and what separates them

1. **Load, not history.**
   - The end window is 8.7 % heavier than the return's end (peaks 2.408 against 2.292), so a server with no memory could be stuck at 4980–5580 and warm at 15480–16080.
   - Separated by the control: under `control_warm` it has no cold window, including the end window, on the identical arrivals.
   - Also by the cold rate: REG-19's c of 1.70–1.80 is below both windows' λp, so a cold server cannot be `recovered` in either. What `recovered` needs is a warm cache.
2. **A long drain read as stuck.**
   - `load.verdict` counts a line that would empty within 3600 s as `slow_drain`. `emptied_in_watch` catches a line that empties.
   - The models put the owed backlog at the watch's end at 1670–2043, growing (REG-19's ratio 1.94–2.51 over W).
3. **The clients, not the server, hold the line in the drop** (REG-15's two [CORR]s).
   - Both models count unreleased turns as owed.
   - The owed backlog and `release_delay` at the first emptying and at the drop's end separate a server that cannot drain from clients that are still releasing.
4. **The cache never re-warms** (against condition 6's reading).
   - `after_empty` against the control's hit in the same window.
   - REG-16's control re-warmed within one 300 s window of its line emptying (FILE(docs/decisions.md:3390)).
5. **Run order, time and heat.**
   - The control runs ≈ 4.6 h before the burst run on the same card.
   - `reg19_baseline_pair` compares pf, clock, TTFT and temperature over 300–900 s.
   - Power-offs are more likely over two 4.6 h runs (open question A18). A lost run is never opened, so a loss selects on power events, not on outcomes.
6. **A seed rule that selects an outcome.**
   - The rule judges the schedule only: its windows, its peaks and the modelled drain.
   - The pick's watch is not lighter than average (λp 2.015, peak 2.733).
   - Its one tilt is the end-versus-return gap, which favours `confirms` and which alternative 1 answers.
7. **Limits, not alternatives:** one seed, one load, closed-loop turns, L1, 350 W, one GPU, dev mode, and the 9000 s drop against PROTOCOL's 1800 s (Setup).

### Stopping rule

REG-19's, unchanged (FILE(docs/decisions.md:3766), its "Stopping rule"):

- The control runs first, then `reg24_step`. The burst run follows only on `continue` True.
- Each run is made once. An invalid run (other than on `burst_min_kv_max`) is rerun unchanged, at most twice.
- No rerun on any verdict or label.
- A heat-invalid run is rerun once, after cooling to ≤ 45 °C. A second heat failure stops.
- These stop the queue:
  - a `client_error`;
  - a burst that does not fill the pool (`burst_min_kv_max`);
  - a limit other than 350 W;
  - an unexpected pre-launch check.
- A rerun decision reads only `checks.json`. No look beyond `reg24_step`'s `continue` before `reg24`.
- A control with no valid run after three attempts stops REG-24. The result is "not run", with the reason.

### Cost (DERIVED)

- **Overheads measured in REG-19's queue, from its run folders' start stamps** (FILE(docs/decisions.md:16536), FILE(docs/decisions.md:16537)):
  - seed 18's control slot, 16:55:16 → 18:05:11, was 4195 s for 4080 s of arrivals: + 115 s;
  - its burst slot, 18:05:11 → 19:21:10, was 4559 s: + 479 s, including the step, the drain and the copy;
  - seed 19's control slot, 19:21:10 → 20:31:08, was 4198 s.
  - REG-15's burst run recorded 9185 samples for 8880 s of arrivals (FILE(docs/decisions.md:3082)). REG-16's control recorded 16109 for 16080 (FILE(docs/decisions.md:3366)).
- **Per run:** control 16080 + 115 = 16195 s ≈ 4.50 h; burst run 16080 + 479 = 16559 s ≈ 4.60 h.
- **Design B:** ≈ 9.10 h if both run.
  - Without reruns, expected 4.50 + 0.85 × 4.60 ≈ 8.41 h.
  - With p_valid 0.7 and up to two reruns, ≈ 1.39 attempts per run, ≈ 11.7 h. This is an upper value, since a lost attempt usually ends early.
  - Worst case: 3 × 9.10 ≈ 27.3 h, plus cooling.
- **Design A:** ≈ 4.60 h; worst ≈ 13.8 h.
- **Disk:** ≈ 0.9 GB per run. This is BELIEF, scaled from REG-19's ≈ 240 MB per 4080 s run (FILE(docs/decisions.md:3766), its "Cost"): 240 × 16080 / 4080 ≈ 946 MB.

### Operations (not in the patch; for the owner)

- **Seal.** The main checkout's `analysis/withheld.py` (not present at `a7bb77a`) needs one entry before either run exists:

  ```
  ("REG-24", "*_l1pl350cl_r2.0_*s43", "[RESULT] REG-24")
  ```

  The pattern covers both `*_confirm_l1pl350cl_r2.0_s43` and `*_stage2_control_l1pl350cl_r2.0_long_s43`; two exact patterns would do as well.
  - `reg24_step` and `reg24` then run with `AFTERSHOCK_UNSEAL=REG-24`.
  - This draft cannot add the entry: the file is outside the patch's base and is not new.
- **A queue script** in the manner of REG-19's `ops_r3` (control, copy, step, burst run, copy, then `reg24` by its final script only) is not written yet.
- **The VM pin:** the runs must run from a tree with these configs committed and clean (rule 6).
- **GPU order:** `agent/DECISION_TREE.md` lists the confirmation run after E1/E2 and D1/D2 (FILE(agent/DECISION_TREE.md:72)). The owner sets the order.

### Code and files (`docs/drafts/reg24_r1/reg24.patch`, new files only)

- `analysis/confirm.py`, with:
  - `REG24`;
  - configs and phases: `burst_cfg`, `control_cfg`, `phases`, `judged_windows`;
  - the drain models: `empty_time_requests`, `owed_requests_model`, `u_rate`, `excess_tokens`, `empty_time_tokens`;
  - the seed rule: `used_seeds`, `candidate_seeds`, `design_row`, `seed_rule`, `seed_scan`, `model_check_reg19`, `inputs`;
  - the outcome: `emptyings`, `burst_outcome`, `pair_outcome`, `k3_band`, `check`, `control_table`, `step`, `burst_table`, `table`;
  - the CLI: `reg24_seed_rule`, `reg24_inputs`, `reg24_scan`, `reg24_model_check`, `reg24_step`, `reg24`.
- `tests/test_confirm.py`, 42 tests:
  - settings equal to the earlier registrations';
  - the seed range unused and outside 20–39;
  - each config against REG-19's, on the five keys;
  - the shared schedule;
  - phases and refusals;
  - `load.verdict` judging the windows;
  - the request model equal to `gate.reg16_empty_time`, with REG-16's numbers;
  - the token model;
  - the seed rule's order and its pick;
  - the schedule facts above;
  - the REG-19 model check (pinned readout);
  - emptyings, outcome order, agreement with `reg15_outcome`, the pair outcome, the K3 band, `check` and `step`;
  - synthetic burst and control tables.

  No test reads `runs/`.
- `configs/confirm_l1pl350cl_r2.0_s43.yaml` and `configs/stage2_control_l1pl350cl_r2.0_long_s43.yaml`.
- **Tests at `a7bb77a` plus the patch** (worktree):
  - `uv run pytest -q tests/test_confirm.py`: 42 passed;
  - `uv run pytest -q tests/test_gate.py -k reg15`: 6 passed;
  - `uv run pytest -q`: 334 passed, 1 skipped (run before the last three assertions were added to one test; `test_confirm.py` passed 42 of 42 again after them).
- **The patch applies cleanly:**
  - to an export of `a7bb77a`, where `tests/test_confirm.py` passed 42 of 42;
  - to an export of `main`'s tip, where it also passed 42 of 42.

  Patch sha256 `d0276f70745cd0bc113d26d32dcb43d53ccae6fa1371f79288559a706cdf2d4f`.

### Not changed

REG-15, REG-16 and REG-19's results and runs; every threshold; `analysis/gate.py`, `analysis/load.py` and `harness/`; every used config; PROTOCOL; claims.md.

### Open points for the reviewer and the owner

1. **The 9000 s drop deviates from PROTOCOL §3's 1800 s** (Setup). It needs the owner's approval and a §6 row.
2. **The return's end decides the drop length** (W), not the drain. A drop-first rule gives seed 61 at 5400 s for ≈ 1 GPU h less. Switching now would be a choice made after seeing the scan.
3. **The 8.7 % heavier end window favours `confirms`.** The design relies on the control (B) to answer it. Under A it stays open.
4. **The token model's pessimistic r is 0.95,** REG-21's J1 tolerance. It is a design choice, not a measured spread.
5. **The model check on REG-19 is a readout,** with its numbers seen before its test was pinned.
6. **`withheld.py`'s seal entry** and the queue script are still to be written.
7. **The freeze evidence is the agent's scratchpad** plus the patch: the hashes above, and the two post-freeze hunks. No commit holds the frozen state.
