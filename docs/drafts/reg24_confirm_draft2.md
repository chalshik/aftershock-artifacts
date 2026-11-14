# REG-24 draft 2: C1's confirmation run at λ = 2.0 (not registered)

Draft for rule F round 2 and the owner-proxy. It is not a decisions.md entry. Nothing in it is approved, and no GPU run follows from it. Written 2026-11-14 ≈ 03:20 UTC (`date -u`) by the draft writer, at HEAD `b46c279`.

- **What changed from draft 1:** every required item of rule F round 1 (RE1–RE9) and all eight of its optional items (RE-O1–RE-O8). Some were taken with a departure, each named. One row per item, with each departure, is in `docs/drafts/reg24_confirm_draft2_itemmap.md`.
- **Code, as two patches against `b46c279`** (folder `docs/drafts/reg24_r2/`, `SHA256SUMS.txt`). Each applies alone, and the two apply together:
  - `reg24.patch`: four new files, `analysis/confirm.py`, `tests/test_confirm.py` and the two configs;
  - `withheld.patch`: the two seal rows in `analysis/withheld.py` and their tests in `tests/test_withheld.py`.
- **Line numbers** in `FILE(docs/decisions.md:…)`, `FILE(agent/…)` and `FILE(PROTOCOL.md:…)` refer to `b46c279`. `docs/decisions.md` is append-only, so the lines stay valid later.
- **The owner's open question, the drop length** (FILE(agent/FOR_AUTHOR.md:11), item −18), is not decided here. This draft is complete under option (a), the 9000 s drop that the frozen rule picked. "Under option (b)" says exactly what changes with PROTOCOL's 1800 s. The choice between (a), (b) and (c) is the owner's.

---

## <date> · [REG] REG-24: C1's confirmation at λ = 2.0, seed 43: a no-burst control, then the burst run on the same schedule, each with a 4500 s watch, then λ = 1 for 9000 s, then back to λ = 2.0 for 1500 s (GPU, ≈ 9.1 h for both runs)

- **ID and scope.** REG-24 is confirmatory for C1's conditions 5 and 6 (PROTOCOL §3) at one load, λ = 2.0, in one seed (FILE(PROTOCOL.md:37), FILE(PROTOCOL.md:38)).
  - It does not test C1 as a whole. Condition 3 is REG-19's `supports` (FILE(docs/decisions.md:16517)). Condition 4's order clause is judged by no registration and waits for the owner (FILE(agent/FOR_AUTHOR.md:18), item −13).
- **Not approved.** No GPU run happens before an approving entry. The drop departs from PROTOCOL §3 item 6, which is the owner's alone (FILE(agent/FOR_AUTHOR.md:11)). So the delegate cannot approve REG-24 until the owner has ruled on the drop ("Open points", item 1).

### What REG-24 can change, and what it cannot (rule A1, said first)

- **What it can change** (rule F round 1, RE6 and §3):
  - the paper's sentence on C1 at λ = 2.0;
  - C1's line in `docs/claims.md`, after the owner's review;
  - one point of K3's model-against-measurement figure (FILE(agent/DECISION_TREE.md:64)).
- **What it does not change:**
  - **D1 and D2.** They are registered at λ = 2.0 whatever REG-24 gives (FILE(agent/DECISION_TREE.md:21)). The plan runs them before the confirmation (FILE(agent/DECISION_TREE.md:72), item 5 before item 6).
  - **No second confirmation seed** is drafted on any label unless the owner asks for one.
  - **No rerun** follows from any label.
- **Weighing it.** Under (a), the pair costs ≈ 9.1 GPU h if both runs are made, ≈ 8.4 h expected and ≈ 27.3 h at most ("Cost"). What it buys is one replicated premise sentence and one K3 point. Whether that is worth the hours is the owner's to weigh. Rule F round 1 did not object (its §3).

### Why now

- **REG-19 gave `supports`, 5 of 5,** under its whole-window test (FILE(docs/decisions.md:16517)). Its registered branch for `supports` (FILE(docs/decisions.md:3803), quoted at FILE(docs/decisions.md:16565)) reads: "draft C1's confirmation at λ = 2.0 for the owner: a 4500 s watch, then a drop to λ = 1 long enough for the line to empty (REG-16's calibration), then the return (conditions 5–6), on a seed chosen by a rule fixed before its schedule is read."
- **The two sources on timing** (rule F round 1, RE-O7):
  - The decision tree's P0 row says to run the confirmation after REG-20's gate (FILE(agent/DECISION_TREE.md:13)). That gate gave `may_start` True (PROBE(docs/probe/reg20/gate_20261113T230307Z.txt)).
  - Its GPU order puts the confirmation after E1 → E2 and after D1/D2 (FILE(agent/DECISION_TREE.md:72), items 4–6).
  - The order actually applied is set by E1's rule ("Order against E1, REG-20 arm A and D1", below). The owner can set another one.
- **What only this run separates.** REG-19's alternative 1 names it: "a state that holds only while the load stays at 2.0 from one that also outlasts a lower load. Only C1's confirmation with its drop and return (conditions 5–6) separates them" (FILE(docs/decisions.md:16555)).

### Question

At λ = 2.0 with closed-loop turns (L1, 350 W):

- **(5)** After the 180 s burst, is the server still `stuck` 4500 s after the burst ends? Three things must hold through the whole watch: it never recovered, its waiting line never emptied, and it completed less than the planned load.
- **(6)** λ then drops to 1 req/s for 9000 s and returns to 2.0 for 1500 s.
  - During the drop, does the waiting line empty, and does the total line drain?
  - Are the return's last 600 s `recovered` against the original baseline?
- **(control)** On the identical session schedule without a burst, does the server stay warm for the whole 16080 s?

### Setup

- **Burst run:** `configs/confirm_l1pl350cl_r2.0_s43.yaml`.
  - It extends `burst_l1pl350cl_r2.0_s2.yaml`, the parent of REG-19's λ = 2.0 burst configs.
  - It sets `seed: 43`, `workload.duration_s: 16080`, `workload.steps: [{at_s: 5580, rate: 1}, {at_s: 14580, rate: 2.0}]` and `verdict.watch_s: 4500`.
- **Control:** `configs/stage2_control_l1pl350cl_r2.0_long_s43.yaml`.
  - It extends `stage2_control_l1pl350cl_r2.0_s2.yaml`, the parent of REG-19's controls, and sets the same four values.
- **Only five keys differ** from each of REG-19's ten configs, resolved: `name`, `seed`, `workload.duration_s`, `workload.steps` and `verdict.watch_s` (`test_registered_configs_are_the_design_at_the_pick`).
  - So both runs are L1, with the 350 W check, closed-loop turns, force_close and dev mode.
  - The burst run's burst starts at 900 s and lasts 180 s, at 2.4 req/s with 2944-token prompts, with `burst_min_kv_max` 0.95.
  - The control has no trigger, and its `control_t_s` is 1080.
  - No config in the chain has changed since REG-19's pin: `git diff --diff-filter=MDR a7bb77a b46c279 -- configs/` is empty (DERIVED).
  - No harness, check or threshold changes. `workload.steps` is the existing load-step mechanism that REG-15 and REG-16 used.
- **One schedule for both runs.** The control's 23194 session requests equal the burst run's session rows, row for row, on `t_planned`, session, turn and prompt length (DERIVED, `confirm.inputs`, `control_schedule_same` True). The burst draws 463 requests from its own generator.
  - A shorter control could not share the schedule, because `build_schedule` draws every segment from one generator (FILE(docs/decisions.md:3151)).
- **Phases** (absolute s; DERIVED, `confirm.phases`):

  | phase | span |
  |---|---|
  | baseline | 300–900 |
  | burst | 900–1080 |
  | watch | 1080–5580 |
  | cold side's window (RE1) | 1680–5580 |
  | drop at λ = 1 | 5580–14580 |
  | return at λ = 2.0 | 14580–16080 |
  | return's end | 15480–16080 |

  - The control uses the same phases.
  - Its `load.verdict` is judged at 1080 + 4500 s against its own baseline, 480–1080 s.
- **Judged windows.** `verdict.end_s` is 600 in the resolved config.
  - The burst run's verdict judges the end window 4980–5580 and the previous window 4380–4980.
  - Condition 6 judges 15480–16080.
  - `test_load_verdict_judges_the_registered_windows` calls `load.verdict` itself on a synthetic run at this config.
- **Owner approval needed, named separately** (rule F round 1, RE8): the 9000 s drop at λ = 1, against PROTOCOL §3 item 6's 1800 s (FILE(PROTOCOL.md:38)).
  - If the owner approves it, the owner adds this row to PROTOCOL §6:

    | Condition 6's drop at λ = 2.0 (REG-24) lasts 9000 s, not 1800 s | Under closed-loop turns the total line at the watch's end is about 1670 requests (request model) and needs about 2130–4080 s at λ = 1 (the two models, optimistic to pessimistic). REG-15's 1800 s drop was `drop_inconclusive`. Among 3600–9000 s, the seed rule's window test chose 9000 s | 2026-11-1x [REG] REG-24 (owner) |

  - The 2026-11-12 design entry already says that the drop is sized beforehand from the expected backlog and the cold floor with a factor of two, and that "1800 s was too short and 9000 s enough in those two runs" (FILE(docs/decisions.md:3948), in the entry at FILE(docs/decisions.md:3946)). It does not change PROTOCOL.

### The harness REG-24 runs on

- **Facts.**
  - REG-19's runs ran at `a7bb77a` (FILE(docs/decisions.md:17031)).
  - REG-24 runs at its registered commit. That commit's harness includes `5ee6e38`: a recorder that survives a half-written line and logs its death, stricter `recorder` and `gpu_steady` checks, and a session cap in the load generator that is off unless `workload.sessions.cap` is set (FILE(docs/decisions.md:17031), FILE(docs/decisions.md:4209)).
  - `git diff --stat a7bb77a b46c279 -- harness/` gives 4 files, 163 lines in and 29 out (DERIVED).
  - REG-24's configs set no cap. Their resolved keys differ from REG-19's only in the five keys above, and REG-19's family has no cap key (DERIVED, the five-key test).
  - E1 is the first GPU run on this harness (FILE(docs/decisions.md:17031)). REG-24 would be the second item.
- **What follows:**
  - **Within REG-24, nothing.** The control and the burst run share one build (RE4, "Result").
  - **Across registrations, a confound.** Every comparison with REG-19's numbers crosses this harness change: the cold completion rate c 1.703–1.800 (FILE(docs/decisions.md:16539)), the controls' peaks, and the total lines. Alternatives 1 and 2 use those numbers, and say so.
- **E1's validity record gates REG-24.** E1's [REG] says: "If `recorder` or `gpu_steady` is in `failed` of any E1 run, or a run ends without `checks.json` on an unchanged boot id, no registration runs on this harness until the cause is found and recorded" (FILE(docs/decisions.md:17056)). REG-24 is such a registration ("What must exist before the first launch").

### Drop length: derivation (draft 1's, unchanged but for RE-O5's numbers)

- **Why 1800 s failed.** REG-15's 1800 s drop at λ = 2.2 never emptied the line (`drop_inconclusive`, FILE(docs/decisions.md:3085)). Its two [CORR]s say why:
  1. The clients lagged 856–930 s, not the 4–6 minutes assumed (FILE(docs/decisions.md:3129)).
  2. The server received 1.582 req/s during the drop, not ≈ 1, because sessions were still releasing turns planned before the drop. A drop length "must come from the total backlog (server waiting plus turns not yet released), computed by a committed function" (FILE(docs/decisions.md:3135), FILE(docs/decisions.md:3136)).
- **Model 1: REG-16's request model, unchanged.** It is `gate.reg16_empty_time`, copied as `confirm.empty_time_requests` to run on a schedule already built. The test checks that it equals the original on REG-16's configs and gives REG-16's published 4340 s and 5540 s.
  - It takes the owed backlog at the trigger (28), adds every request planned since (session and burst), and subtracts completions at REG-15's cold rates: 1.758 req/s to the watch's end and 1.672 in the drop (RUN(20261110-085730_confirm_l1pl350cl_r2.2_s12, gate.reg16_calibration), FILE(docs/decisions.md:3156)).
  - **Pessimistic version:** REG-15's lowest 600 s rate per phase, lowered by `c_pessimism` 0.05 (FILE(docs/decisions.md:3159)). That gives 1.678 in the watch and 1.587 in the drop.
- **Model 2: a token model.** This is the decision tree's K3 row: "The confirmation run's drop is sized from U_off and the mean served prompt" (FILE(agent/DECISION_TREE.md:59)). It is `confirm.empty_time_tokens`.
  - Every prompt token planned since the trigger (session and burst, no cache hit) is owed work.
  - The cold engine does that work at U = r × U_off, where U_off is 5164.76 uncached tokens/s: the mean over REG-8's five saturated cache-off runs (PROBE(docs/probe/reg21/batch1_20261113T224220Z.txt), `k3w.reference`).
  - The drop's empty time is when the work owed since the trigger is done.
  - **Expected r:** 1.021, the λ = 2.0 group's median in REG-21's batch 1 (FILE(docs/decisions.md:16444)). `REG24["r_expected"]` holds it unrounded, 1.0209631954979448, which gives U 5273.03.
  - **Pessimistic and optimistic r:** 0.95 and 1.05, REG-21's J1 tolerance. That gives U 4906.52 and 5423.00 (DERIVED, `confirm.u_rate`).
  - **The band is a tolerance, not a prediction interval** (rule F round 1, RE-O4 and §4.4). J1's 0.05 is a tolerance on a median over runs. The per-run spread of r on record is much narrower: at λ = 2.0, r ran from 1.020 to 1.025 (SD 0.0021, n 5) in batch 1 (FILE(docs/decisions.md:16444)) and from 1.023 to 1.029 in batch 2 (FILE(docs/decisions.md:16798)).
- **The model checked out of sample, as a readout and not a gate** (draft 1's numbers, unchanged; `confirm.model_check_reg19`, schedules only). The request model's expected owed backlog on REG-19's five λ = 2.0 schedules, against the total line that REG-19 measured (FILE(docs/decisions.md:16533)–FILE(docs/decisions.md:16537)):

  | time | model, seeds 15–19 | measured, seeds 15–19 | model minus measured |
  |---|---|---|---|
  | 4080 s | 1342, 1271, 1539, 1049, 1171 | 1320, 1226, 1511, 1050, 1155 | −1 to +45 |
  | 1680 s | 577, 601, 860, 655, 466 | 555, 551, 811, 612, 444 | +22 to +50 |

  - The difference column is DERIVED. The model errs a little towards a longer drain.
  - The measured values cross the harness change named above.
- **REG-16's measured drain supports `warm_watch_s` 1200 s.**
  - REG-16's control was cold with a queue of 113 at the drop's start. The queue fell to 0.000 in 6600–6900 s, and hit came back to 0.840 in that same 300 s window (FILE(docs/decisions.md:3387)–FILE(docs/decisions.md:3390)).
  - So 1200 s after the drain leaves four such windows (DERIVED).
- **For seed 43 at 9000 s** (DERIVED, `confirm.inputs`, saved as `docs/drafts/reg24_r2/inputs_43_9000_20261114T033247Z.txt`; times in s into the drop):

  | model | optimistic | expected | pessimistic |
  |---|---|---|---|
  | requests (owed backlog at 5580 s: 1670 expected, 2043 pessimistic) | n/a | 2490 | 3550 |
  | tokens (excess work at 5580 s: 4.883 / 5.585 / 7.300 M tokens) | 2130 | 2560 | 4080 |

- **The factor of two of FILE(docs/decisions.md:3948) also holds** (RE-O5; now in code):
  - Twice the later expected time plus 1200 s is 2 × 2560 + 1200 = 6320 s, which is ≤ 9000 (DERIVED).
  - Against the open-loop cold floor 1.681 (`k2.E0["floor_8"]`, FILE(analysis/k2.py:24)): 2 × 1670 / (1.681 − 0.99367) = 4859 s, which is ≤ 9000 (DERIVED, `confirm.inputs` `factor_two_s` 4859.36, with the drop's λp unrounded).
  - Draft 1's 2431 s and 4862 s rounded λp to 0.994 first. Corrected to 2430 s and 4859 s.
- **Planned λp per 600 s window of the drop,** from 5580 s (DERIVED, `confirm.inputs` `drop_by_600`), on the planned schedule:

  1.082, 0.967, 0.920, 1.055, 0.917, 1.135, 1.053, 0.875, 0.920, 0.982, 0.885, 0.885, 1.168, 1.045, 1.017

  - Their mean is 0.994.
  - The highest 120 s window inside the drop lies below 2.158. The 2.158 window, [5460, 5580), ends where the drop starts, so it belongs to the watch (DERIVED, `confirm.inputs`; `rolling_rate` windows are [g − 120, g), FILE(analysis/gate.py:1356)).
  - At first the server will receive more than planned, as in REG-15 (1.58), because sessions are still releasing turns planned before the drop. Both models count those turns as owed.

### Under option (b), 1800 s: what changes

This section is for the owner's choice (FILE(agent/FOR_AUTHOR.md:11), item −18). It is not a design this draft proposes. No schedule at 1800 s was built or read for it; every number is taken from draft 1's tables or from the cost arithmetic.

- **The frozen rule gives no design at 1800 s.** Its drop candidates are 3600, 5400, 7200 and 9000 s (FILE(docs/drafts/reg24_r2/frozen/confirm_frozen.py:42)), and `confirm.phases` refuses any other drop.
  - The drop changes the whole schedule (Setup), so seed 43 at 1800 s is a schedule the rule never judged. Its W (judged windows within ± 5 %) and E (no 120 s peak ≥ 3.2) are unknown.
  - F fails, by every row on record: on seed 43's four judged schedules the pessimistic empty times are 3270–3550 s (requests) and 3760–4080 s (tokens; "never" within the 3600 s drop). The rule needs them to be at most 1800 − 1200 = 600 s (DERIVED, the rule table below).
  - As base rates over the 160 candidate seeds, W passed for 5–7 per drop and E for 141–144 (DERIVED, draft 1's post-pick scan). So an unjudged schedule would fail W with P ≈ 0.96 and E with P ≈ 0.1. The judged windows would then likely sit outside REG-15's ± 5 % of λ.
  - Keeping seed 43 at 1800 s would therefore be a new choice, made after the scan (rule A5). It would be the owner's, and it must be named as such. Any other seed would need a new rule. This draft writes neither.
- **What changes in code and configs (a reviewed change):**
  - `REG24["drop_s"]` becomes 1800;
  - `phases` accepts 1800;
  - both configs get `workload.duration_s: 8880` and `steps: [{at_s: 5580, rate: 1}, {at_s: 7380, rate: 2.0}]`;
  - `test_registered_configs_are_the_design_at_the_pick` and `test_inputs_schedule_facts_at_the_pick` are pinned anew;
  - the K3 band is recomputed. It is likely `undefined` by construction: on seed 43's 9000 s schedule even the optimistic token model drains 2130 s into the drop, past 1800 s, and `empty_time_tokens` returns NaN for an empty time outside the drop. So K3's point is lost.
- **The expected `drop_inconclusive`** (BELIEF): P ≈ 0.70, given a warm control and a valid burst run. That is ≈ 0.92 of the burst runs that reach the drop stuck and cold.
  - Both models put the drain at 2130–4080 s into the drop on seed 43's judged schedule, and the four rows for seed 43 give expected times of 2390–2490 s (requests) and 2430–2560 s (tokens) (DERIVED, draft 1's rule table).
  - REG-15's 1800 s drop at 2.2 did not drain (FILE(docs/decisions.md:3085)).
  - Unconditionally (validity and control included), P(`drop_inconclusive`) ≈ 0.53 and P(`confirms`) ≈ 0.03 ("Prediction", table (b)).
- **The cost:** ≈ 5.10 GPU h for the pair, ≈ 4.6 h expected, ≈ 15.3 h at most ("Cost"). That is ≈ 4.0 h less than (a) for the pair (DERIVED: 9.10 − 5.10).
- **The outcomes that stay informative under (b):**
  - **Condition 5,** in full: the watch, its windows, the cold side and the same-schedule control are the same as under (a). `not_persistent`, `reformed`, `emptied_in_watch` and `stuck_not_cold` mean what they mean under (a). A burst run that reaches the drop stuck, cold and never emptied shows persistence through 4500 s. Without W, though, its end window's load is not matched to λ within ± 5 %.
  - **Condition 6,** only if the line drains within 1800 s (P ≈ 0.06 that it drains and the run reaches `confirms` or `no_return`). Otherwise `drop_inconclusive` is the expected result, not a failure of the models.
  - **K3's point:** lost (above).
- **What does not change under (b):**
  - the outcome code, apart from `phases`' drop candidates;
  - the seal and the order;
  - the stopping rule;
  - the decision table, except that `drop_inconclusive` is reported as expected.

### Seed and drop: the rule, fixed before any candidate's schedule was read

- **Rule** (`confirm.seed_rule`, `confirm.design_row`; byte-identical to the frozen file, "Timing"):
  - The candidates are seeds 40–199 that no config uses. REG-24's own two configs are left out, so the rule gives the same pick once they exist.
  - Seeds are tried in order. For each seed, the drop candidates are tried in order: 3600, 5400, 7200, 9000 s.
  - The pick is the first (seed, drop) whose burst config's schedule passes all three tests:
    - **W:** each of the four judged windows (baseline 300–900, previous, end, return's end) has planned session λp within ± 5 % of 2.0. This is REG-15's `window_tol` (FILE(docs/decisions.md:2886)).
    - **E:** the highest 120 s planned rate anywhere from 240 s to the end of arrivals is below `surge_tip` 3.2. That is REG-17's value (FILE(analysis/gate.py:1474)), on REG-18/19's exposure grid.
    - **F:** the later of the two pessimistic empty times, plus `warm_watch_s` 1200 s (REG-16's), fits in the drop.
  - Seeds come before drops. That order was set before the freeze. REG-16's review N5 is the nearest precedent: "the lowest-seed rule picks the seed with less room" (FILE(docs/decisions.md:3167)).
    - Draft 1 paraphrased N5 as "taking the shortest drop first picks the lightest schedule that fits it". The line does not say that, so this draft quotes it instead.
    - The frozen `seed_rule` docstring carries the same paraphrase ("answers REG-16's review N5: drop-first picks the lightest schedule that fits the shortest drop"). It is left as frozen, so that `seed_rule` stays byte-identical. This text is the correction.
- **Collision with REG-20b.** REG-20b, if it is ever registered, takes "seeds 20, 21, … (the first unused)" (FILE(agent/DECISION_TREE.md:33)). REG-24 starts at 40 and leaves 20–39 to REG-20b. If REG-20b ever needed more, "first unused" skips 43. No config at `b46c279` other than REG-24's sets seed 43 (`test_seed_range_is_unused_and_outside_reg20b`).
- **Timing** (rule F round 1, RE7). The timing is BELIEF: the evidence is the agent's scratchpad, not a commit.
  - **The record.** The seed rule's code and tests were frozen at 2026-11-13 23:23:39 UTC, and the rule ran once, 23:23:45–23:23:47 UTC (the files' modification times and `freeze_20261113T232339Z.txt`).
  - **Two of the frozen files survive in that scratchpad and are copied unchanged into this draft's folder:**
    - `docs/drafts/reg24_r2/frozen/confirm_frozen.py`, sha256 `6801457c1b7aec9ef429e4d11a01828ff2ba730f21bb60e920ddaa08bf49c268`, the value draft 1 gave;
    - `docs/drafts/reg24_r2/frozen/freeze_20261113T232339Z.txt`, the freeze record, which lists both files' sha256.
  - **The rule's saved output** is copied as `docs/drafts/reg24_r2/frozen/seed_rule_20261113T232345Z.txt`. Its stderr, one `uv` warning line, is beside it.
  - **The frozen `tests/test_confirm.py`** (sha256 `867aba60…` in the freeze record) was not found in the scratchpad or in the agent's worktree. The claim that the tests were frozen at that time is BELIEF, resting on the freeze record alone.
  - **The check that draft 1's reviewer could not run, now runnable.** `python3 -I docs/drafts/reg24_r2/frozen/compare_frozen.py <frozen> <later>` compares the two files' top-level functions, assignments and `REG24` keys by source text. Its output is `docs/drafts/reg24_r2/frozen/compare_20261114T033233Z.txt` (PROBE):
    - **Frozen file → draft 1's `confirm.py`** (sha256 `5ba55384…`): only `REG24['seed']`, `REG24['drop_s']` (with their comment) and `inputs` changed. That is draft 1's statement, now checked.
    - **Frozen file → draft 2's `confirm.py`:** 48 symbols are the same:
      - `CONFIGS`, and all 26 other `REG24` keys;
      - `_resolved`, `burst_cfg`, `control_cfg`, `phases`, `judged_windows` and `_rate`;
      - both models (`empty_time_requests`, `owed_requests_model`, `u_rate`, `excess_tokens`, `empty_time_tokens`);
      - `used_seeds`, `candidate_seeds`, `design_row`, `seed_rule`, `seed_scan` and `model_check_reg19`;
      - `emptyings`, `_flat`, `check` and `_one`.
    - **12 changed:**
      - `REG24` (its seed and drop only), and `inputs` (readouts);
      - `BURST_LABELS`, `burst_outcome`, `pair_outcome`, `burst_table`, `control_table`, `step` and `table` (RE1–RE4, RE-O1, RE-O2, RE-O8);
      - `k3_band`'s docstring only.
    - **11 added:** `READOUT` and its two keys, `tilt_scan`, `owed_series`, `drained_at`, `cold_side`, `control_outcome`, `released_after`, `cotenant` and `implied_r`.
    - `frozen_to_draft2.diff` beside it is the unified diff.
  - **Set before the freeze,** after REG-15/16/19's results and before any candidate schedule was read: the seed range 40–199 and the 3600 s candidate, the token model and its band, and the order of seed first, then drop.
- **The rule's output, every row up to the pick** (DERIVED, `confirm.seed_rule`, the saved output above; λp in req/s; empty times in s into the drop, pessimistic in brackets):

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

  - **The pick: seed 43 with a 9000 s drop** (`test_seed_rule_picks_seed_43_at_9000_s`, with the candidates pinned to 40–199 as the rule saw them, RE-O3).
    - Seeds 40, 41 and 42 fail W at every drop, on their baselines (2.52–2.55, 1.81–1.84 and 2.26–2.29).
    - Seed 43 fails W at 3600, 5400 and 7200 s, each time only on the return's end (2.173, 1.828, 1.693).
  - **W alone decides the pick.** Every row before it fails W, so any variant of F or E that passes at (43, 9000) gives the same pick, the factor-two form included (DERIVED).
  - **The 9000 s drop is forced by the return's end window, not by the drain.**
    - On seed 43's three schedules that drain, the later pessimistic time plus 1200 s is 4960, 5060 and 5280 s (DERIVED, the table above: 3760, 3860 and 4080 plus 1200).
    - Draft 1 gave "about 3600–5300 s". Its lower end has no row behind it.
- **Post-pick scan** (draft 1's readout, computed after the pick, `confirm.seed_scan`, 160 candidate seeds; not run again for this draft):

  | drop | W | E | F | all three | lowest seeds passing all | median pessimistic empty, requests / tokens |
  |---|---|---|---|---|---|---|
  | 3600 | 7 | 144 | 0 | 0 | none | 3190 / 3250 |
  | 5400 | 6 | 142 | 117 | 4 | 61, 68, 173 | 3370 / 3890 |
  | 7200 | 5 | 141 | 160 | 5 | 68, 79, 81 | 3360 / 3855 |
  | 9000 | 7 | 144 | 160 | 7 | 43, 61, 68 | 3410 / 3840 |

  - A drop-first rule (REG-16's form) would have picked seed 61 at 5400 s, ≈ 2 GPU h cheaper for the pair (DERIVED: 2 runs × 3600 s = 7200 s). Draft 1 said "about 1 GPU h", which was an arithmetic error.
  - **The frozen rule stands.** Switching now would be a choice made after seeing the scan (rule A5). Rule F round 1 agreed (its §4.2).

### Design inputs for seed 43, 9000 s

All values in this section are DERIVED from the configs alone with `python -m analysis.confirm reg24_inputs` (`confirm.inputs`, saved as `docs/drafts/reg24_r2/inputs_43_9000_20261114T033247Z.txt`). They are draft 1's values, plus RE1's λp and RE-O5's factor-two length.

- **Requests:** 23194 session and 463 burst. The control's schedule equals the burst run's session rows.
- **Planned λp by phase:**

  | phase | λp |
  |---|---|
  | baseline (300–900) | 2.022 |
  | watch | 2.015 (thirds 1.969, 2.035, 2.039) |
  | cold side's window (1680–5580; RE1) | 2.045 |
  | drop | 0.994 |
  | return | 1.999 |
  | the control's own `load.verdict` baseline (480–1080) | 2.017 |

- **Judged windows:** baseline 2.022, previous 1.985, end **2.068**, return's end **1.903**.
- **The watch's 300 s windows,** from 1080 s:

  1.800, 1.840, 2.260, 1.830, 2.117, 1.943, 2.113, 1.803, 2.243, 2.073, 2.090, 1.827, 2.143, 2.013, 2.123

  - The lowest, 1.800, is the first window (1080–1380). A break there would be read as a delayed onset, not a re-formed collapse (REG-15's N3). It still scores `reformed`, which works against `confirms`.
  - **The planned dips do not reach the server directly** (rule F round 1, RE-O6). Under closed-loop turns the server receives released turns, not planned ones, so the watch's planned dips reach it only once the total line is small. In REG-19's five runs the total line was 444–811 requests 600 s after the burst and 1050–1511 at 3000 s (FILE(docs/decisions.md:16533)–FILE(docs/decisions.md:16537)). The request model puts seed 43's at 1670 at the watch's end. So an emptying in the watch is unlikely (BELIEF).
- **Highest 120 s windows by phase:**

  | phase | peak | window, s |
  |---|---|---|
  | before the burst | 2.442 | [180, 300) |
  | watch | 2.733 | [2330, 2450) |
  | drop | 2.158 | [5460, 5580), the watch's tail |
  | return | 2.650 | [14630, 14750) |

  - None reaches 3.2. REG-19's five controls carried 2.833–3.092 without tipping (FILE(docs/decisions.md:16542)), under the earlier harness.
- **The heavier judged window is the one judged `stuck`.** The highest 120 s window inside the end window is 2.408, and inside the return's end 2.292 (`peak_120s_inside_judged`).
  - **This is the opposite of REG-15's bias** (FILE(docs/decisions.md:2895)). The end window carries 8.7 % more planned load than the return's end (DERIVED: 2.068 / 1.903 = 1.087). Both are inside ± 5 % of λ, but the heavier side is the one judged `stuck`, so the planned load favours `confirms`.
  - **The tilt from a committed function** (rule F round 1, RE9): `confirm.tilt_scan`, CLI `reg24_tilt`; schedules only, computed after the pick; a readout.
    - On seeds 43 and 61 (`test_tilt_scan_on_the_pick_and_seed_61`), the end window's λp minus the return's end's is +0.165 req/s for the pick. Seed 61's two W-passing rows have +0.107 at 5400 s (the drop-first pick) and +0.083 at 9000 s. W allows at most 0.200 (DERIVED, `confirm.tilt_scan(seeds=(43, 61))`).
    - **Over all 640 candidate schedules, by rule F round 1's one-off script (not provenance under rule I):** 25 pass W, none of them has a larger tilt than the pick, the median is +0.003, and 13 of the 25 are positive (FILE(docs/drafts/reviews-2026-11-13/rulef-reg24-draft1-r1.md:100)).
    - **Not yet run:** `reg24_tilt` over all 160 seeds would put those numbers on committed code. This draft did not run it, because the brief for draft 2 said not to re-run the seed scan. The [REG] quotes its output if the lead or the owner allows that one schedule-only run, and otherwise keeps the reviewer's numbers marked as above (open point 5).
  - **The design's answer is twofold.** First, the same-schedule control (Design B). Second, the cold side (d2): REG-19 measured c 1.703–1.800 in all 40 spans of W (FILE(docs/decisions.md:16539)), below both 2.068 and 1.903, so a cold server falls behind in either window and a warm one carries both. The `confirms` sentence gives both windows' λp.
- **The models' predictions at the watch's end:** owed backlog 1670 expected and 2043 pessimistic; excess token work 5.585 M at the expected U.

### Designs: with and without a same-seed control (draft 1's, unchanged)

| design | runs | GPU h | what it can show | what it cannot show |
|---|---|---|---|---|
| **A: burst run only** (REG-15's design) | 1 | ≈ 4.6 | Conditions 5 and 6 in one run. | Whether the warm server carries this schedule's 4500 s watch. No λ = 2.0 control has run longer than 4080 s (DERIVED, resolved configs). REG-16 showed a no-burst control going cold on a long schedule at 2.2 (FILE(docs/decisions.md:3373)). The heavier window is the one judged `stuck`. No early stop. |
| **B: control first, then the burst run** (REG-16 then REG-17, as planned at 2.2) | 2 | ≈ 9.1 (≈ 8.4 expected) | Everything A shows, plus that the same arrivals without the burst stay warm through the watch, the drop and the return. If the control goes cold, the burst run is not made, which saves ≈ 4.6 h. | More than one seed (n = 1 per run; rule H: a single control). Run order (the control always runs first, about 4.6 h earlier). |

- **Recommendation: B.** Condition 6 is the test that separates two states at one load from overload (FILE(docs/decisions.md:3948)). With the tilt above, only a warm control on the identical schedule keeps a `confirms` from being explained by load. B is the design the study already chose at 2.2 (REG-16), where the control is what turned out to matter (FILE(docs/decisions.md:3408)).
- **The code implements B.** `confirm.table` needs the control's run, and `confirm.step` is the only look between the two runs.

### Result: computed once, after the runs are valid and copied

- **Commands,** each from a worktree at the registered commit (RUNBOOK §5), whose `runs/` is a real folder holding links to REG-24's two folders only (as E1's "Result, computed once", FILE(docs/decisions.md:17083)):
  - **The queue's only look between the two runs:** `AFTERSHOCK_UNSEAL=REG-24 uv run python -m analysis.confirm reg24_step` (`confirm.step`). It prints `control_done` and `continue` only. `continue` is True only if the control's outcome is `control_warm`. It computes the control's outcome and nothing else (RE-O8, `confirm.control_outcome`).
  - **After the last run, once, by the ops folder's final script only:** `AFTERSHOCK_UNSEAL=REG-24 uv run python -m analysis.confirm reg24` (`confirm.table`).
  - No other command sets `AFTERSHOCK_UNSEAL=REG-24` (RE5).
- **The code is the registered code.** The files printed by `python3 docs/probe/20261113_freeze/closure.py --at <registered commit> analysis/confirm.py` are unchanged from the registered commit to the result's commit, except for rows added to `analysis/withheld.py`'s `SEALS`. The approval entry quotes that list, and the [RESULT] quotes `git diff --stat <registered commit> <its commit> -- <those files>`. This is E1's rule (FILE(docs/decisions.md:17083)).
- **Run checks** (`confirm.check`). It refuses:
  - a run that `checks.json` does not mark valid;
  - a run whose config differs from the registered file on any key that file sets (as `gate.reg16_check`);
  - a burst run without the burst, or a control with any trigger.

  `gate.reg12_only` requires exactly one valid run per pattern.
- **Both runs from one build** (rule F round 1, RE4). `confirm.table` gives `not_same_build`, and no other label, unless both runs' `env.json` `git_commit` are set and equal (`test_table_refuses_a_pair_from_two_builds`). The ops scripts also refuse a valid run made at any commit other than the registered one, as REG-19's queue did.
- **Control** (`confirm.control_outcome`): REG-16's outcome (`gate.reg16_control_outcome`, FILE(docs/decisions.md:3194)) on REG-24's phases, against the 300–900 s baseline.
  - **Cold window:** a 300 s window from 1080 to 16080 s with hit ≤ base − 0.06 and pf (by send time) ≤ base − 0.10.
  - **Persistent:** a cold window that ends a phase (5580, 14580 or 16080 s), or a cold stretch of at least 1500 s (`persistent_s`).
  - **`control_warm`** requires all of:
    - baseline pf ≥ 0.98, and the watch verdict's own baseline (480–1080 s) not `bad_baseline`;
    - no cold window;
    - no window with hit ≤ base − 0.06 and waiting > base + 1;
    - `load.verdict` at 1080 + 4500 s `recovered`;
    - the return's end `recovered_against` the baseline.

  Otherwise the outcome is `bad_baseline`, `inconclusive`, `control_cold_persistent`, `control_cold_transient`, `control_unclear` or `control_not_recovered`, in REG-16's order.
- **Burst run** (`confirm.burst_outcome`): REG-15's labels and order (`gate.reg15_outcome`, FILE(docs/decisions.md:2908)), with REG-19's emptying in place of REG-15's single zero scrape, REG-19's whole-window cold side, and the drop's drain on the total line.
  - **Emptying** (`gate.reg19_emptyings`'s rule): 0 waiting at a scrape and for the next 30 s. A new emptying counts only after the line has refilled.
  - **One emptying pass** (rule F round 1, RE2). `burst_table` computes the emptyings once, over 1080–14580 s. An emptying that starts before 5580 s belongs to the watch even if its 30 s hold runs past 5580 s. The rest belong to the drop.
  - **The cold side** (RE1, `confirm.cold_side`, REG-19's `reg19_cold_side`, FILE(analysis/gate.py:1834)). W runs from the burst's end + 600 s (`gate.REG19["window"][0]`, FILE(analysis/gate.py:1796)) to the watch's end, [1680, 5580). The test is that completions (session and burst, by `t_end`) fall below min(λ, λp), where λp is the planned session rate in W (2.045 for seed 43, DERIVED above).
  - **The total line and the drain** (RE3):
    - The total line is `gate.owed_backlog`: requests planned before t and not completed by t, the clients' unreleased turns included (FILE(analysis/gate.py:1079)). `confirm.owed_series` is its vectorized form (`test_owed_series_is_gate_owed_backlog`).
    - The drain (`confirm.drained_at`) is the first 10 s grid time in the drop at which the total line is at or below its own level at the trigger (900 s). That is the event both drain models predict: the work owed since the trigger done.
  - **The labels, in order** (`BURST_LABELS`):
    1. **`bad_baseline`:** `load.verdict` of the 4500 s watch is `bad_baseline` (baseline pf < 0.98).
    2. **`not_persistent`:** the watch's verdict is `recovered` or `slow_drain`.
    3. **`inconclusive`:** `unclear`.
    4. **`reformed`:** `stuck` at the watch's end, but some 300 s window of the watch passed `recovered_against` the baseline (`gate.watch_broken`; each window's λp is reported).
    5. **`emptied_in_watch`:** stuck and never recovered, but the line emptied somewhere in the watch (one pass, RE2).
    6. **`inconclusive`:** the cold side's c or λp is NaN.
    7. **`stuck_not_cold`** (RE1): stuck, never recovered and never emptied in the watch, but completions over [1680, 5580) s were not below min(λ, λp). This is REG-19's `stuck_not_cold`: the total line was not growing, so the `stuck` verdict may be a long drain. Condition 5 is not shown.
    8. **`drop_inconclusive`:** in 5580–14580 s, no emptying, or the total line never drained (RE3). PROTOCOL §3 says "inconclusive, not passed".
    9. **`inconclusive`:** the return's end has a missing value.
    10. **`no_return`:** the line emptied and drained in the drop, but the return's end is not `recovered`.
    11. **`confirms`:** everything below holds.
  - **Agreement with REG-15.** `test_burst_outcome_keeps_reg15s_order_where_the_tests_agree` checks that this order equals `gate.reg15_outcome` wherever the emptying tests agree and the cold side holds.
- **Every threshold, and its source.** Nothing is new except RE3's drain rule, whose level is the run's own value and not a constant.
  - **From `configs/stage2_base.yaml`, unchanged:**
    - `min_baseline_pf` 0.98;
    - `recovered_pf_drop` 0.02, `recovered_hit_drop` 0.06, `recovered_q_excess` 1;
    - `stuck_pf_drop` 0.10, `stuck_hit_drop` 0.06;
    - `pf_climb` 0.05, `hit_climb` 0.06;
    - `drain_horizon_s` 3600.
  - **From REG-15:** 300 s watch windows.
  - **From REG-16:** 300 s cold windows, `persistent_s` 1500 and the 10 s grid (`grid_s`).
  - **From REG-19:** the 30 s emptying hold, and the whole-window cold side starting 600 s after the burst's end.
  - **RE3's drain rule** (the total line back at or below its level at the trigger) is new in draft 2. Rule F round 1 wrote it before any REG-24 run, to match the event both models predict. It is stricter than draft 1's: it adds a condition to (g).
  - **Readout settings, which judge nothing:** `READOUT["floor_8"]` 1.681 (`k2.E0["floor_8"]`) and the bisection bracket [0.5, 1.5] × U_off for the implied r (RE-O4, the reviewer's).
  - **Schedule-only values:** the seed rule's 5 % (REG-15), 3.2 (REG-17) and 1200 s (REG-16) judge the schedule only, never an outcome.
- **What `confirms` requires, all of it:**
  - (a) Both runs are valid, pass `confirm.check`, and come from one build (RE4).
  - (b) The control is `control_warm`.
  - (c) The burst run's baseline pf (300–900 s) is ≥ 0.98.
  - (d) `load.verdict` of the 4500 s watch is `stuck` on the end window 4980–5580 against 300–900:
    - pf ≤ base − 0.10 and hit ≤ base − 0.06;
    - no recovery sign against the previous window 4380–4980: hit up < 0.06, pf up < 0.05, and the queue would not empty within 3600 s.
  - (d2) REG-19's whole-window cold side holds over [1680, 5580) s (`confirm.cold_side`): completions (session and burst, by `t_end`) below min(λ, λp), with λp the planned session rate in that window. If either rate is NaN, the label is `inconclusive`. If the rate is not below, the label is `stuck_not_cold` (RE1).
  - (e) None of the 15 windows of 300 s in 1080–5580 s passes `recovered_against` the baseline.
  - (f) No emptying starts in 1080–5580 s; its 30 s hold may run past 5580 s. The drop's emptyings are counted in the same pass, so an emptying that continues from the watch into the drop belongs to the watch (RE2).
  - (g) In 5580–14580 s, two things happen (RE3). There is at least one emptying, a 30 s zero of the waiting gauge (PROTOCOL's "the line reached 0"). And the total line (`gate.owed_backlog`: planned and not completed, the clients' unreleased turns included) is back at or below its level at the trigger (900 s), on the 10 s grid (`confirm.drained_at`). If the line drains only after 14580 s, the label is `drop_inconclusive`.
  - (h) The return's end, 15480–16080 s, passes `recovered_against` the baseline: pf ≥ base − 0.02, hit ≥ base − 0.06, mean waiting ≤ base + 1.
- **The pair's outcome** (`confirm.pair_outcome`, then `confirm.table`):
  - The burst run's own label stands whatever the control when the burst run fails condition 5 or has a gap of its own: `bad_baseline`, `not_persistent`, `reformed`, `emptied_in_watch`, `stuck_not_cold` or `inconclusive`.
  - Otherwise the label stands only beside `control_warm`.
  - A non-warm control gives `control_not_warm`, and the burst run is then not made (`step`).
  - Two builds give `not_same_build` (RE4).
- **Readouts, never decisive** (`confirm.burst_table`, `confirm.control_table`):
  - every emptying in the watch and the drop;
  - the cold side's c and λp;
  - the owed backlog at the trigger, at the watch's end, at the first emptying in the drop and 600 s after it;
  - **`after_empty`** (RE3): hit in [drain + 600, + 1200) against the control's hit in the same window, read as `warmed` or `cold_after_empty`. The drain is `drained_at`, not the first zero of the gauge, so `cold_after_empty` means a cold cache with the total line drained.
  - the drop's last 600 s;
  - condition 4's levels over the watch's last 1500 s (KV, N, N / baseline N, max N against 256);
  - `release_delay` at each phase's end;
  - the judged windows' λp from the run's own requests;
  - **the end window's mix** (RE-O1, `confirm.released_after`): the share of the end window's requests released in the drop, and pf by send time in the previous and end windows. If `not_persistent` comes only from the pf-climb sign and more than half of the end window's requests were released in the drop, the report says so (rule F round 1, T4).
  - **the co-tenant readout** (RE-O2, `confirm.cotenant`), for both runs. PROTOCOL §4 says the GPU is shared with another user (FILE(PROTOCOL.md:53)). The readout gives per phase the GPU's used memory max minus min (`gpu.jsonl` `mem_used_mib`), and the compute processes listed at launch (`env.json` `gpu_processes`) and at the end (event `gpu_processes_end`, FILE(harness/run.py:214)).
  - the 300 s timeline;
  - for the control: its cold windows, `window_mix` and `surge_run`;
  - `gate.reg19_baseline_pair`, the run-order readout of REG-19's alternative 5.
- **K3's blind prediction** (FILE(agent/DECISION_TREE.md:64); `confirm.k3_band`). The drain is compared once with the token model's band:
  - **The measured value** is `drained_drop_s`: the time into the drop at which the total line is back at its level at the trigger (RE3). This is the event both drain models predict.
  - **The waiting gauge's first 30 s zero** is reported beside it with its own band label (`label_first_empty`), as a readout. Under closed-loop turns it can come while turns are still owed (rule F round 1, T3).
  - **Band:** [2130, 4080] s into the drop, with point prediction 2560 s. Labels: `inside`, `outside_early`, `outside_late`, or `undefined` if there is no drain.
  - **The implied r** (RE-O4, `confirm.implied_r`): the r that makes the token model's empty time equal the measured drain, found by bisection on [0.5, 1.5] × U_off. It is reported beside REG-21's per-run spread (1.020–1.025 and 1.023–1.029 at λ = 2.0; FILE(docs/decisions.md:16444), FILE(docs/decisions.md:16798)).
  - **It decides nothing here.** It enters the model-against-measurement figure. Batch 2 of REG-21 gives r 1.028 on REG-19's runs (FILE(docs/decisions.md:16798)), which would move the point prediction to 2450 s (DERIVED, `confirm.empty_time_tokens` at 1.028 × U_off, draft 1). The band does not depend on r.

### Prediction (BELIEF)

- **Each run valid on a given attempt:** ≈ 0.7 (range 0.5–0.8), draft 1's figure.
  - REG-19 lost two attempts to power-offs (FILE(docs/decisions.md:4284), FILE(docs/decisions.md:4293)).
  - Counted per wall-clock hour over REG-19's queue (≈ 40 h), P(no power-off in 4.6 h) ≈ 0.80. Counted per GPU hour (≈ 13 h), it is ≈ 0.50 (DERIVED: exp(−2 × 4.6 / 40), exp(−2 × 4.6 / 13)).
  - With up to three attempts, P(a valid run of a config) ≈ 0.97 (DERIVED: 1 − 0.3³).
- **The control `control_warm`:** ≈ 0.85 under (a).
  - **For it:**
    - All five of REG-19's controls stayed warm through 4080 s, with higher peaks (2.833–3.092) than this schedule's 2.733.
    - Every no-burst tip on record followed a 120 s peak of 3.24–3.49, REG-16's included (FILE(docs/decisions.md:3423)). This schedule stays below 3.2.
  - **Against it:**
    - This run is four times longer.
    - The surge reading is a readout found in the data, not a threshold (FILE(docs/decisions.md:3426)).
    - The harness is new.
  - **A correction to draft 1:** it gave "REG-16 went cold at 2.2 after a 2.78 peak". That is the figure the 2026-11-10 [CORR] withdrew (FILE(docs/decisions.md:3417), FILE(docs/decisions.md:3419)). The tip followed a 120 s peak of 3.45 (FILE(docs/decisions.md:3422)). P stays at 0.85: the corrected figure argues for a warm control, and the run's length argues against.
- **Given a warm control, a valid burst run and one build:**

  | outcome | p, (a) 9000 s | p, (b) 1800 s | why |
  |---|---|---|---|
  | `bad_baseline` | ≈ 0.08 | ≈ 0.08 | REG-19's baselines were 0.984–0.998; REG-18 had one at 0.978 |
  | `not_persistent` | ≈ 0.04 | ≈ 0.04 | |
  | `inconclusive` (all three places) | ≈ 0.02 | ≈ 0.02 | |
  | `reformed` | ≈ 0.03 | ≈ 0.03 | |
  | `emptied_in_watch` | ≈ 0.03 | ≈ 0.03 | draft 1 had 0.05. Lowered on rule F round 1's argument (RE-O6): with the total line in the hundreds to above a thousand, planned dips do not reach the server |
  | `stuck_not_cold` | ≈ 0.04 | ≈ 0.04 | new label (RE1). REG-19: c 1.740–1.758 against λp 1.923–2.077 in 5 of 5 (FILE(docs/decisions.md:16533)–FILE(docs/decisions.md:16537)); seed 43's window is longer (3900 s against 2400 s) at λp 2.045 |
  | `drop_inconclusive` | ≈ 0.06 | ≈ 0.70 | (a): draft 1 had 0.05, raised for RE3's stricter drain test; the models drain at 2130–4080 s against 9000. (b): the drain is predicted past 1800 s |
  | `no_return` | ≈ 0.08 | ≈ 0.02 | |
  | `confirms` | ≈ 0.62 | ≈ 0.04 | the remainder |

- **The whole pair, unconditionally** (DERIVED from the rows above; rounded):

  | outcome | (a) 9000 s | (b) 1800 s |
  |---|---|---|
  | not tested: `control_missing` (0.03), `burst_missing` (0.97 × P(warm) × 0.03); `not_same_build` and queue stops not counted | ≈ 0.05 | ≈ 0.05 |
  | `control_not_warm` | ≈ 0.15 (0.97 × 0.15) | ≈ 0.19 (0.97 × 0.20) |
  | a burst-run label (the table above) | ≈ 0.80 (0.97 × 0.85 × 0.97) | ≈ 0.75 (0.97 × 0.80 × 0.97) |
  | of which `confirms` | ≈ 0.50 (0.80 × 0.62) | ≈ 0.03 (0.75 × 0.04) |
  | of which `drop_inconclusive` | ≈ 0.05 (0.80 × 0.06) | ≈ 0.53 (0.75 × 0.70) |

- **P(`control_warm`) under (b): ≈ 0.80** (BELIEF).
  - The control is shorter (8880 s), so it has less time to go cold.
  - But E has not judged its schedule, and over the candidates a 120 s peak ≥ 3.2 has a base rate of ≈ 0.1 (Option (b) section).
  - P(valid) per attempt is kept the same for both options. Under (b) it is likely higher, because a shorter run is less exposed to power-offs. That would raise the burst-run rows a little and would change no decision.

- **K3, given a drain:** `inside` ≈ 0.7, `outside_early` ≈ 0.15, `outside_late` ≈ 0.15 (draft 1's numbers).
  - **Biases in opposite directions.** RE3 removes the gauge's early bias. Hits returning as the line shrinks would make the drain early against the all-miss model, and a slower engine would make it late. With no new evidence on their sizes, the numbers stay as they were.
- **Implied r, given a drain:** ≈ 0.95–1.05 (BELIEF; REG-21's range on REG-19's runs is 1.023–1.029).

### Decision under each outcome (rule F round 1, RE6)

- **What REG-24 can change, and what it cannot:** as in "What REG-24 can change, and what it cannot" above.
- **Per cell** (rule H): k of n, with the one-sided 95 % Clopper–Pearson upper bound (`analysis.stats.cp_upper(k, 1, 0.95)`, FILE(analysis/stats.py:9)).
  - 1 of 1 gives 1.00, with the lower bound 0.05 reported beside it (DERIVED: 0.05^(1/1)).
  - 0 of 1 gives 0.95 (DERIVED: 1 − 0.05).
  - One seed, with a single same-schedule control (rule H).
- **`confirms`:** "At λ = 2.0, in one seed (43), beside one no-burst control on the same arrivals:
  - after the burst the server stayed stuck for 4500 s, its line never emptying and its completions below the planned load;
  - its total line drained [drained_drop_s] s into a 9000 s drop to λ = 1;
  - the last 600 s of the return to λ = 2.0 were recovered against the pre-burst baseline;
  - the control stayed warm throughout.

  The stuck window was planned at λp 2.068 and the recovered window at 1.903, [the largest such difference among the [n_windows_ok] schedules that the seed rule's window test admitted: `reg24_tilt`'s `n_larger` 0, or the reviewer's statement as such, open point 5]. The control carried both windows warm. 1 of 1 (one-sided 95 % Clopper–Pearson upper bound 1.00, lower bound 0.05). This meets C1's conditions 5 and 6 at this cell. It does not test C2's chain."
  - With REG-19 (condition 3) and REG-22's levels (condition 4, its order clause unjudged), C1 then lacks only condition 4's order clause at this cell.
  - `docs/claims.md` changes only after the owner reviews it.
  - `control_warm` says the warm state lasts on this schedule, not at λ = 2.0 in general (rule F round 1, §2). This schedule's largest 120 s peak is 2.733, lighter than REG-19's 2.833–3.092.
- **`not_persistent`, `reformed`, `emptied_in_watch`, `stuck_not_cold`:** "At λ = 2.0 the state held for 3000 s in 5 of 5 seeds (REG-19) but not for 4500 s in the confirmation seed ([what happened, and when]). C1's condition 5 is not met at this cell (0 of 1; upper bound 0.95)."
  - The paper describes the cell as "entered and held for 3000 s; persistence beyond it not shown".
  - Under `stuck_not_cold`, the sentence names the cold side's c and λp.
  - Under `not_persistent`, it says whether the end window's mix (RE-O1) points to a pf measured in the drop.
- **`drop_inconclusive`:**
  - **Under (a):** "Condition 5 held; condition 6 is inconclusive: the total line did not drain within 9000 s at λ = 1, more than twice both models' pessimistic drain times." K3's point is `undefined`, and both models are reported as failed for this state. The owed backlog and `release_delay` at the drop's end show which part, server or clients, held.
  - **Under (b):** "Condition 5 held; condition 6 is inconclusive: the total line did not drain within PROTOCOL's 1800 s at λ = 1, as both models predicted (drain at 2130–4080 s)."
  - Either way it is reported, with no automatic longer drop. The owner decides.
- **`no_return`,** read by `after_empty`:
  - `warmed`: "the server left the stuck state at λ = 1 and re-tipped on the return, where the control did not. Condition 6 is not met (0 of 1)."
  - `cold_after_empty`: "the cache stayed cold after the total line had drained at λ = 1: the cold state was not held by load." Reported as found; no claim is widened on it.
  - None: "condition 6 not met; the reading is undefined."
- **`control_not_warm`:** "On seed 43's 16080 s schedule the no-burst control did not stay warm ([outcome]). The confirmation is void at this cell, and λ = 2.0 is reported as not reliably warm over 4.5 h, as REG-16 reported 2.2."
- **`bad_baseline`, `inconclusive`, `not_same_build`, `burst_missing`, `control_missing`, or a queue stop** (a `client_error`, `burst_min_kv_max`, a limit other than 350 W, three invalid attempts of either run): "C1's conditions 5–6 were not tested at λ = 2.0 ([reason])."
- **In no case** does REG-24 start, stop or size another run (rule F round 1, §3).

### Alternatives (rule A2) and what separates them

1. **Load, not history.**
   - The end window is 8.7 % heavier than the return's end (peaks 2.408 against 2.292), the largest tilt among the W-passing schedules by the reviewer's count. So a server with no memory could be stuck at 4980–5580 and warm at 15480–16080.
   - **Separated by the control:** under `control_warm` it has no cold window on the identical arrivals, the end window included.
   - **And by the cold rate:** a cold server is below both windows' λp (REG-19's c 1.70–1.80, under the earlier harness), so it cannot be `recovered` in either. What `recovered` needs is a warm cache. Condition (d2) now also requires the burst run to be below λp over [1680, 5580).
2. **A long drain read as stuck** (rule F round 1, T1).
   - `load.verdict` counts a line that would empty within 3600 s as `slow_drain`. `emptied_in_watch` catches a line that empties.
   - **`stuck_not_cold` (RE1)** catches a total line that is not growing: a partly warm server that keeps up with λp at a hit just under baseline − 0.06.
   - The models put the owed backlog at the watch's end at 1670–2043, growing (REG-19's ratio 1.94–2.51 over W, FILE(docs/decisions.md:16533)).
3. **The clients, not the server, hold the line in the drop** (REG-15's two [CORR]s; rule F round 1, T3).
   - (g) and K3 read the total line, which counts unreleased turns (RE3). A 30 s zero of the gauge while hundreds of turns are owed no longer counts as the drain.
   - The owed backlog and `release_delay` at the first emptying and at the drop's end separate a server that cannot drain from clients that are still releasing.
4. **The cache never re-warms** (against condition 6's reading).
   - Separated by `after_empty`, read after the drain, against the control's hit in the same window.
   - REG-16's control re-warmed within one 300 s window of its line emptying (FILE(docs/decisions.md:3390)).
5. **Run order, time and heat.**
   - The control runs ≈ 4.6 h before the burst run on the same card.
   - `reg19_baseline_pair` compares pf, clock, TTFT and temperature over 300–900 s.
   - Power-offs are more likely over two 4.6 h runs (open question A18). A lost run is never opened, so a loss selects on power events, not on outcomes.
6. **A seed rule that selects an outcome.**
   - The rule judges the schedule only: its windows, its peaks and the modelled drain.
   - The pick's watch is not lighter than average (λp 2.015, peak 2.733).
   - Its one tilt is the end-versus-return gap, which favours `confirms` and which alternative 1 answers.
7. **A co-tenant on the shared GPU** (rule F round 1, RE-O2).
   - The harness lists compute processes at launch (`env.json` `gpu_processes`, FILE(harness/env_snapshot.py:44)) and at the end (event `gpu_processes_end`, FILE(harness/run.py:214)), but not during the run.
   - Rule F round 1 wrote "read only before launch (FILE(harness/run.py:97))". Line 214 shows a second read, at the end.
   - The co-tenant readout reports the GPU's used memory per phase and both process lists, for both runs.
8. **The persistence is held by the clients' backlog against the pool size, not by the loop C2 states** (rule F round 1, §2; not ruled out).
   - At the watch's end the model owes ≈ 1670 requests, so at least 209 sessions hold owed turns. Their contexts, ≈ 0.63 M tokens, exceed the 96,656-token pool (DERIVED by the reviewer: 1670 / 8, 209 × 3000). Each turn arrives after its prefix was evicted.
   - Under this reading, `confirms` is C1 met but says nothing about C2's chain (PROTOCOL §2). REG-24 cannot separate the two readings.
   - The readouts that bear on it: condition 4's levels, `release_delay`, and the total line's growth over the watch.
   - The tests that bear on it lie outside REG-24: REG-20's open-loop arm (K1) and condition 4's order clause. The `confirms` sentence therefore ends "It does not test C2's chain."
9. **Limits, not alternatives:**
   - one seed, one load, closed-loop turns, L1, 350 W, one GPU, dev mode;
   - a harness newer than REG-19's ("The harness REG-24 runs on");
   - the 9000 s drop against PROTOCOL's 1800 s (Setup).

### Stopping rule

REG-19's (FILE(docs/decisions.md:3766), its "Stopping rule"), with E1's rules for a harness on its first GPU uses (FILE(docs/decisions.md:17072)) and RE6's `burst_missing`:

- **Order.** The control runs first, then `reg24_step`. The burst run follows only on `continue` True. On `continue` False the queue ends (`QUEUE END control not warm`), and `reg24` then computes the control's table alone.
- **Reruns.**
  - Each run is made once. An invalid run (other than on `burst_min_kv_max`) is rerun unchanged, at most twice: three attempts per config.
  - A heat-invalid run (`gpu_steady`, which since `5ee6e38` also covers sample coverage) is rerun once, after cooling to ≤ 45 °C. A second `gpu_steady` failure stops the queue.
  - There is no rerun on any verdict or label.
- **The queue pauses after any invalid run** (E1's R2). It starts again only after an [OPS] entry that quotes the `RUN … INVALID failed=…` line.
- **These stop the queue for a decision:**
  - a `client_error` (`no_errors` in `failed`);
  - a burst that does not fill the pool (`burst_min_kv_max`);
  - a limit other than 350 W (`power_limit`);
  - a run that ends without `checks.json`;
  - one check name in `failed` of two of REG-24's runs (E1's `MAX_SAME`: on a new harness, a check that fails twice is a question about the harness, not a rerun);
  - a valid run made at a commit other than the registered one;
  - the owner's halt, an entry headed `## <date> · [DECISION] (owner) REG-24 halted`.
- **A failed pre-launch check** (limit, temperature after 30 min, a compute process, a tmux session, the tree, `uv.lock`, the boot id, free disk) launches nothing and spends no attempt. The queue is started again once the cause is removed (E1's DA3; draft 1 had called it a stop).
- **Reads.** A rerun decision reads only `valid` and `failed` of `checks.json`. While diagnosing a stop, only these may be read: `tmux has-session`, folder names, `valid` and `failed`, and in a launch log the lines holding `run_id` or `[run] checks`. There is no look beyond `reg24_step`'s two fields before `reg24`.
- **Missing runs.** A control with no valid run after three attempts gives `control_missing`, and the result is "not run", with the reason. A burst run with no valid run after three attempts gives `burst_missing` (RE6).
- **REG-24 holds the VM** from its `vm_checkout.sh` until its end entry. The end entry is headed `## <date> · [OPS] REG-24: the queue ended (QUEUE DONE)`, `… (QUEUE END control not warm)`, `… (QUEUE END attempts spent)`, or `## <date> · [OPS] REG-24 ended by a stop: <the stop line>`. A pause, or a stop that waits for a decision, is not an end.

### Order against E1, REG-20 arm A and D1

**The rule.** E1's [REG] states it, and its approval applied it (FILE(docs/decisions.md:17076), FILE(docs/decisions.md:18433)):

> "Approved first" is read from the committed `docs/decisions.md`: the item whose last required heading has the earlier line is first; an item's required headings are those its scripts need before their first launch.

Each later item launches only after the earlier item's end entry. RUNBOOK §5 states it for E1 and REG-20 arm A (FILE(agent/RUNBOOK.md:66)). This draft applies it to all four items.

**The required headings of each item:**

- **E1:** `## <date> · [DECISION] (owner|delegate) E1 approved`. It is at line 18286 (`git grep` at `b46c279`).
  - The VM was checked out at E1's commit `ce5f842` (FILE(docs/decisions.md:19394)).
  - E1 was running at 02:54 UTC (FILE(docs/decisions.md:19452), "with E1 running"). Its state now is BELIEF.
  - It holds the VM until its end entry (FILE(docs/decisions.md:17076)). At `b46c279` no E1 end entry is in the log (`git grep` for `[OPS] E1: the queue ended` and `[OPS] E1 ended by a stop`: no match).
- **REG-20 arm A:** REG-19's [RESULT] (present), the owner's rulings entry (`RULINGS_PAT`) and the start entry (`START_PAT`) (FILE(docs/probe/20261113_reg20/ops/common.sh:39-41)). At `b46c279` neither of the last two matches (`git grep`).
- **D1:** no [REG] and no ops scripts yet (draft 1 is NOT READY on rule F round 1). Its place is left to RUNBOOK §5 at its approval (FILE(docs/drafts/d1_draft1.md:95)).
- **REG-24, proposed for its ops scripts** (`common.sh` patterns, as E1's `REG_PAT` and `APPROVE_PAT`, FILE(docs/probe/20261113_e1/ops/common.sh:39-40)):
  - (i) `## <date> · [REG] REG-24` (`REG_PAT`);
  - (ii) the owner's ruling on the drop: a heading `## <date> · [DECISION] (owner) REG-24 approved…`, or `## <date> · [DECISION] (owner) REG-24: the drop…` (`DROP_PAT`);
  - (iii) `## <date> · [DECISION] (owner|delegate) REG-24 approved`, after (i) and (ii) (`APPROVE_PAT`). It may be the same heading as (ii).
  - **E1's end entry** is checked by REG-24's scripts too (`END_E1_PAT`, E1's three end headings). It is not one of REG-24's own required headings for this rule, since otherwise every item after E1 would be ordered by E1's end and not by its own approval. The end entries of REG-20 arm A or D1, if either is first, are checked by hand, as E1's rule does for REG-20 (FILE(docs/decisions.md:17076)).

**The order at `b46c279`:**
- E1 is first: its required heading is at line 18286, and no other item has all of its own.
- REG-20 arm A, D1 and REG-24 have none of their own headings yet. Their order is set when those headings land. The item whose last own required heading has the earlier line runs next, after E1's end entry, and so on.
- Which lands first is BELIEF:
  - REG-20 arm A waits for the owner's rulings entry (`RULINGS_PAT`, FILE(docs/probe/20261113_reg20/ops/common.sh:40)) and the owner's decision on the VM's disk (FILE(agent/FOR_AUTHOR.md:7));
  - D1 waits for its draft 2 and its reviews;
  - REG-24 waits for the owner's ruling on the drop.
- The decision tree's GPU order puts D1/D2 before the confirmation (FILE(agent/DECISION_TREE.md:72)). By E1's rule, REG-24 runs before D1 if its ops are approved first. The two disagree only if REG-24 is approved first. The owner may set another order by an entry (open point 3).

**Two interactions with REG-20 arm A,** if arm A is approved first:
- **The seal waits.** Arm A's operations draft 3 forbids new `SEALS` rows during its hold: "REG-24's row waits until final.sh's files are committed, and lands before REG-24's first run" (FILE(docs/drafts/reg20_ops_decision_draft3.md:564), not approved). REG-24's seal commit, and so its approval ("What must exist before approval"), then waits for arm A's `final.sh` files.
- **The VM moves forward.** Arm A moves the VM back to its pin. REG-24's `vm_checkout.sh` then moves it forward from that commit to REG-24's registered commit, which must be a descendant of it.

**For the approval commit:** RUNBOOK §5's row 6 ("Confirmation run | not registered", FILE(agent/RUNBOOK.md:69)) becomes:

> REG-24 (E1, REG-20 arm A, D1 and REG-24: whichever has its ops approved first runs first, by E1's rule; each other launches only after the previous item's end entry) | `docs/probe/<date>_reg24/ops/queue.sh` | `AFTERSHOCK_UNSEAL=REG-24 uv run python -m analysis.confirm reg24`, once, by the ops folder's final script | [RESULT] REG-24

### Withheld until the [RESULT] of REG-24

- **The two run folders** (rule F round 1, RE5; `withheld.patch`):

  ```
      ("REG-24", "*_confirm_l1pl350cl_r2.0_s43", "[RESULT] REG-24"),                 # C1's confirmation, burst run
      ("REG-24", "*_stage2_control_l1pl350cl_r2.0_long_s43", "[RESULT] REG-24"),     # and its same-schedule control
  ```

- **The tests.** `test_reg24_seal_covers_exactly_its_two_configs` checks the configs' names, over every config present: exactly these two are sealed, whether or not their files are in the tree yet. `test_reg24_seal_lifts_only_on_its_result` checks that the seal lifts only on a heading that is REG-24's [RESULT].
- **The patterns overlap no other seal.** They do not match REG-15's `20261110-085730_confirm_l1pl350cl_r2.2_s12`, REG-16's design, or D1's drafted `*_burst_l1pl350cl_r2.0_w3000_s1[5-9]_cap` (FILE(docs/drafts/d1_r1/withheld.patch:4)).
- **While sealed,** only `valid` and `failed` of `checks.json` are read, and only `reg24_step` and `reg24` set `AFTERSHOCK_UNSEAL=REG-24`.

### What must exist before approval, and before the first launch (RE5)

**Before the approving entry** (no approval is written until each of these is committed, or is in the approval's own commit):

1. **The configs, the code and the tests:** `reg24.patch` applied (`analysis/confirm.py`, `tests/test_confirm.py`, the two configs). Its tests pass at that commit, and so does `uv run pytest` in full.
2. **The seal:** `withheld.patch` applied (the two `SEALS` rows and their tests). If REG-20 arm A's hold is in force, this waits for the hold's end (above).
3. **The ops scripts** in `docs/probe/<date>_reg24/ops/` (sketch below), with:
   - `reg24_commit.txt` reading `UNSET`;
   - a sandbox run on fakes, saved as `sandbox_<stamp>.txt`;
   - their own rule F pass and owner-proxy pass, recorded verbatim, as E1's scripts had (FILE(docs/decisions.md:17085)). REG-24's [REG] text and the scripts are reviewed together.
4. **The owner's ruling on the drop** (Setup; "Open points", item 1). Under (a), the PROTOCOL §6 row is added in the same commit.
5. **The texts for the approval commit** ("For the approval commit", below).

**Before the first launch:**

6. `reg24_commit.txt` names the approval's commit, committed alone (E1's step 3, FILE(docs/probe/20261113_e1/ops/README.md:36)).
7. E1's end entry, and E1's validity record without a harness fault, or the cause recorded (FILE(docs/decisions.md:17056)). Also the end entry of any other item that is first by the rule.
8. `vm_checkout.sh`'s output committed with an [OPS] entry, then the session probe's file.
9. Free disk on the VM for both runs ("Cost"). That is the owner's issue −20 (FILE(agent/FOR_AUTHOR.md:7)).

### Operations: a sketch (the scripts are not part of this draft)

- **Where they come from.** The folder `docs/probe/<date>_reg24/ops/` is derived from E1's `docs/probe/20261113_e1/ops/` (README, `common.sh`, `launch.sh`, `queue.sh`, `session_probe.sh`, `vm_state.py`, `vm_checkout.sh`, `test_sandbox.sh`). It takes the single-run form and the step from REG-19's `ops_r3/` (`queue.sh`'s per-seed loop and `reg19_step` record; `final.sh` once, from the worktree).
- **`common.sh`** holds:
  - every parameter: the two config names, the registered commit read from `reg24_commit.txt`, and the patterns `REG_PAT`, `DROP_PAT`, `APPROVE_PAT` and `END_E1_PAT`, plus a halt pattern;
  - `mac_checks`. It refuses while `reg24_commit.txt` is `UNSET`, or while any script differs from its text at that commit. It also refuses unless HEAD's `analysis/withheld.py` seals both names, checked by importing `analysis.withheld` and calling `sealed_by` on the two names with no unseal variable.
- **`launch.sh <config>`** runs the read-only pre-launch checks: limit 350.00 W, ≤ 45 °C (waiting up to 30 min), no compute process, no tmux session, the VM's tree and `uv.lock` at the registered commit, the boot id, and free disk for a 16080 s run. It writes the attempt record, starts `uv run python -m harness.run configs/<config>.yaml` in tmux, and waits.
- **`queue.sh`** runs these steps, idempotent across restarts:
  1. settle the control (valid from `checks.json` only, via `vm_state.py`);
  2. pause after an invalid run;
  3. copy the run to the Mac and verify every file's sha256;
  4. update the manifest;
  5. link the folder into the worktree at the registered commit;
  6. run `reg24_step` once from the worktree with `AFTERSHOCK_UNSEAL=REG-24`, keeping only its two fields in `state/reg24_step.txt`;
  7. on `'continue': True`, the burst run, settled, copied and linked the same way, then `QUEUE DONE`;
  8. on `'continue': False`, `QUEUE END control not warm`.
- **`final.sh`** runs `reg24` once, from the worktree. It runs only after `QUEUE DONE` or `QUEUE END control not warm`, and refuses if a table file exists. Its output is committed alone.
- **`vm_checkout.sh`** moves the VM forward to the registered commit. It starts from whichever commit the VM was left at, which must be an ancestor: E1's `ce5f842` (FILE(docs/decisions.md:19394)), REG-20 arm A's pin, or D1's commit.
- **The VM pin** (rule F round 1, RE4, its text): "Both runs run from commit `<the registration commit>`, checked out clean on the VM. Reruns use the same commit. `confirm.table` gives `not_same_build` if the two runs' `env.json` commits differ; the owner decides then, and no rerun follows from it. Other work's harness changes (E1, D1/D2) do not enter the VM checkout until REG-24's last run is copied."
  - Here, "the registration commit" is the commit in `reg24_commit.txt`, the approval's.
- **`test_sandbox.sh`** runs on fake `ssh`, `rsync`, `uv`, `tmux` and `nvidia-smi`, as E1's.
- **Cost of writing them:** 0 GPU h.

### Cost (DERIVED)

- **Overheads measured in REG-19's queue,** from its run folders' start stamps (FILE(docs/decisions.md:16536), FILE(docs/decisions.md:16537)):
  - seed 18's control slot was 4195 s for 4080 s of arrivals: + 115 s;
  - its burst slot was 4559 s: + 479 s, which includes the step, the drain and the copy.

| | (a) 9000 s drop: 16080 s of arrivals | (b) 1800 s drop: 8880 s of arrivals |
|---|---|---|
| control, one attempt | 16080 + 115 = 16195 s ≈ 4.50 h | 8880 + 115 = 8995 s ≈ 2.50 h |
| burst run, one attempt | 16080 + 479 = 16559 s ≈ 4.60 h | 8880 + 479 = 9359 s ≈ 2.60 h |
| both runs | ≈ 9.10 h | ≈ 5.10 h |
| expected, no reruns (P(`control_warm`) 0.85 / 0.80) | 4.50 + 0.85 × 4.60 ≈ 8.41 h | 2.50 + 0.80 × 2.60 ≈ 4.58 h |
| expected with reruns (≈ 1.39 attempts per run at p_valid 0.7: 1 + 0.3 + 0.09) | ≈ 11.7 h | ≈ 6.4 h |
| at most (three attempts of each) | 3 × 9.10 ≈ 27.3 h | 3 × 5.10 ≈ 15.3 h |
| disk per run (BELIEF: REG-19's estimate of ≈ 240 MB per 4080 s run, itself scaled from REG-18's ≈ 150 MB, FILE(docs/decisions.md:3819), scaled again) | ≈ 0.95 GB (240 × 16080 / 4080) | ≈ 0.52 GB (240 × 8880 / 4080) |
| disk, both runs / at most six attempts | ≈ 1.9 / 5.7 GB | ≈ 1.0 / 3.1 GB |

- **Notes.**
  - A lost attempt usually ends early, so the expected-with-reruns rows are upper values.
  - Waits for ≤ 45 °C keep the GPU idle and are not counted.
  - Under (a), design A alone would be ≈ 4.60 h, at most ≈ 13.8 h.
  - The VM had 4.05 GB free with E1 running (FILE(agent/FOR_AUTHOR.md:7)). REG-24's ceiling under (a) exceeds that unless the owner frees space (item −20).

### Code and tests (`docs/drafts/reg24_r2/`)

- **`reg24.patch`** (new files; it applies alone to `b46c279`):
  - **`analysis/confirm.py`.** Draft 1's functions, plus rule F round 1's patch merged:
    - `tilt_scan` (RE9);
    - `owed_series` and `drained_at` (RE3);
    - `cold_side` and the label `stuck_not_cold` (RE1);
    - one emptying pass and the drain in `burst_table` (RE2, RE3);
    - `not_same_build` in `table` (RE4).

    And this draft's own additions:
    - `READOUT` (RE-O5, kept out of `REG24` so that `REG24` stays the frozen text);
    - `inputs`' `lam_p_cold_side` and `factor_two_s`;
    - `released_after` and `burst_table`'s `end_window_mix` (RE-O1);
    - `cotenant` (RE-O2);
    - `implied_r` (RE-O4);
    - `control_outcome`, which `step` now calls alone (RE-O8);
    - `tilt_scan`'s median and positive count;
    - docstrings.
  - **`tests/test_confirm.py`, 55 tests as pytest collects them.** That is draft 1's 42, plus 8 from the reviewer's patch and 5 from this draft (DERIVED: `pytest --collect-only` on both exports):
    - **The reviewer's 8:** four new tests, `test_burst_table_rules_of_rule_f_round_1`, `test_owed_series_is_gate_owed_backlog`, `test_table_refuses_a_pair_from_two_builds` and `test_tilt_scan_on_the_pick_and_seed_61`; three new parametrized rows of `test_burst_outcome_order`; and one of `test_pair_outcome`.
    - **This draft's 5:** `test_step_computes_no_readout`, `test_released_after_counts_late_and_unsent_requests`, `test_cotenant_readout`, `test_implied_r_inverts_the_token_model` and `test_readout_constants_are_the_studys`. New assertions in `test_inputs_schedule_facts_at_the_pick`, `test_burst_table_on_a_synthetic_confirming_run` and `test_tilt_scan_on_the_pick_and_seed_61`. RE-O3's changes to `test_seed_range_is_unused_and_outside_reg20b` and `test_seed_rule_picks_seed_43_at_9000_s`, and `test_step_continues_only_after_a_warm_control` rewritten for `control_outcome`.
    - No test reads `runs/`.
  - **The two configs,** whose comment now names draft 2.
- **`withheld.patch`** (it applies alone to `b46c279`): the two `SEALS` rows, and `tests/test_withheld.py`'s two new tests (16 tests in the file).
- **Tests run on scratch exports of `b46c279`** (`git archive b46c279 | tar -x`, then the patches by `git apply`; the repo's `.venv` python; the export as cwd; `runs/` holds only the tracked empty `.gitkeep`). The outputs are saved in `docs/drafts/reg24_r2/` and named in `SHA256SUMS.txt`:
  - **Targeted runs,** in `tests_targeted_20261114T033203Z.txt`, on the patches as saved (their sha256 are in the file's header):
    - both patches: `tests/test_confirm.py` and `tests/test_withheld.py`, 71 passed, and `tests/test_gate.py -k reg15`, 6 passed;
    - `reg24.patch` alone: `tests/test_confirm.py` with HEAD's `tests/test_withheld.py`, 69 passed;
    - `withheld.patch` alone: `tests/test_withheld.py`, 16 passed.
  - **The full suite with both patches,** `--ignore=tests/test_check_docs.py`, in `pytest_full_20261114T033150Z.txt`: 580 passed and 1 skipped in 657 s, rc 0 (its header gives both patches' sha256).
    - The skip is `test_reg17_cold_side_and_drain_time_on_reg14s_burst_run`, which skips when its run folder is absent (FILE(tests/test_gate.py:1024)). The export's `runs/` is empty.
  - **Superseded outputs, kept and named in `SHA256SUMS.txt`:**
    - `tests_targeted_20261114T031012Z.txt`: its first block passed `-k` across several files, so it deselected tests.
    - `tests_targeted_20261114T032400Z.txt`, `pytest_full_20261114T031003Z.txt` (580 passed, 1 skipped), `inputs_43_9000_20261114T031548Z.txt` and `frozen/compare_20261114T031618Z.txt`. All four were made on the earlier `reg24.patch`.
    - That patch differed from the saved one only in `cotenant`'s docstring. The docstring said the process list is "checked only before launch", which `harness/run.py:214` contradicts.
    - The inputs output line and the comparison's symbol lines are identical across the two versions (DERIVED, `diff`). Only the comparison's sha256 line differs.

### For the approval commit (texts; this draft edits none of these files)

- **PROTOCOL §6**, under (a) and only by the owner: the row in Setup (RE8).
- **RUNBOOK §5**, row 6: the text in "Order".
- **`docs/definitions.md`**, three entries (rule J):
  - **total line (owed backlog):** "requests planned before t and not completed by t: server waiting and running, plus closed-loop turns not yet released." Code: `gate.owed_backlog` (FILE(analysis/gate.py:1079)), and its vectorized form `confirm.owed_series`, which a test shows equal.
  - **emptying ⚠ two codes for one rule:** "0 waiting at a scrape and for the next 30 s; a new emptying counts only after the line refilled."
    - Code: `gate.reg19_emptyings` (relative to the burst's end, with the hold ending by the end of arrivals) and `confirm.emptyings` (absolute, with the hold ending by the window's end; REG-24 uses one window from the burst's end to the drop's end).
    - The two differ only in that end bound. Whether that counts as one computation is the owner's (rule J).
  - **drained (REG-24):** "the first 10 s grid time in [a, b) at which the total line is at or below its level at the trigger." Code: `confirm.drained_at`.
- **`docs/model.md`'s prediction ledger:** a row for the "Prediction" above, with the K3 band and the implied-r readout.
- **`docs/status.md`:** "REG-24 holds the VM" from its `vm_checkout.sh` to its end entry, and the seal in "Watch".

### Adversarial review (rule F, `docs/process.md` §3)

- **Round 1, on draft 1:** `docs/drafts/reviews-2026-11-13/rulef-reg24-draft1-r1.md` (sha256 `ae2dd4bca475f766d1953bd0aa23854f52e9682d72e40f8ad41ffb251e32ff85`), NOT READY on RE1–RE9. Its patch is `rulef-reg24-draft1-r1.patch` (sha256 `291e478a12f9ee30d2e5ccbcc77ed60bf58183d293a58e07418111e201b9ec00`). The [REG] quotes the round verbatim, as E1's did (FILE(docs/decisions.md:17094)).
- **What was changed because of it:** every required item and all eight optional items. Each item, with its departures, is listed in `docs/drafts/reg24_confirm_draft2_itemmap.md`. In short:
  - **RE1:** (d2) and `stuck_not_cold`;
  - **RE2:** (f) and one pass;
  - **RE3:** (g), K3 and `after_empty` on the drain;
  - **RE4:** `not_same_build`, and the pin in "Result" and in the stopping rule;
  - **RE5:** the seal patch and "What must exist";
  - **RE6:** "Decision under each outcome", "What REG-24 can change" and `burst_missing`;
  - **RE7:** the frozen files and their check;
  - **RE8:** the owner's approval and the §6 row;
  - **RE9:** `tilt_scan`, with its full-scan number left open.
- **Round 2:** this draft and its two patches, with the ops scripts reviewed together once they are written (RE5).

### Not changed

- REG-15's, REG-16's and REG-19's results and runs;
- every threshold;
- `analysis/gate.py`, `analysis/load.py` and `harness/`;
- every used config;
- PROTOCOL;
- `docs/claims.md`;
- the seed rule and both models (byte-identical to the frozen file, "Timing").

### Open points for the reviewer and the owner

1. **The drop length, (a), (b) or (c)** (FILE(agent/FOR_AUTHOR.md:11)). This is the owner's alone. Under (a), the owner also adds the §6 row and either approves REG-24 directly or rules on the drop and leaves the approval to the delegate.
2. **Under (b), seed 43 at 1800 s is a schedule the frozen rule never judged** (W and E unknown; F fails on every row on record). Keeping it, or writing a new rule, is a choice made after the scan, and the owner's.
3. **The order.** By E1's rule, the first of REG-20 arm A, D1 and REG-24 whose ops are approved runs after E1. The decision tree planned D1/D2 before the confirmation. The owner may fix another order.
4. **The harness.** REG-24 runs on `5ee6e38`'s harness, not REG-19's `a7bb77a`. Within REG-24 one build is enforced (RE4). Comparisons with REG-19's numbers cross the change. E1's validity record gates REG-24.
5. **RE9's full number.** `reg24_tilt` over all 160 seeds (640 schedules, schedule only) was not run, because draft 2's brief said not to re-run the seed scan. The lead or the owner decides whether it is run once and quoted. Otherwise the `confirms` sentence cites the reviewer's one-off count as such.
6. **The frozen test file** (`867aba60…`) was not found. The tests' freeze is BELIEF, on the freeze record alone. The rule's code is checkable (RE7).
7. **The 8.7 % heavier end window favours `confirms`.** The design relies on the control and on (d2) to answer it.
8. **Disk** (item −20). REG-24's ceiling under (a) is ≈ 5.7 GB (BELIEF).
9. **`emptying` has two codes** (definitions entry above, ⚠). Rule J leaves that to the owner.
10. **Condition 4's order clause** (FILE(agent/FOR_AUTHOR.md:18), item −13). Even under `confirms`, C1 lacks it at this cell.
11. **C1's line in `docs/claims.md`** changes only after the owner reviews a `confirms`. No label edits it automatically.
