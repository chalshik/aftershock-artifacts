# rulef-reg24-draft1-r1 (rule F, round 1 on REG-24 draft 1, C1's confirmation at λ = 2.0), verbatim

Saved by the agent at 2026-11-14 02:03 UTC from the reviewer's own file (an in-process subagent of session 8c5f8396; scratchpad `reviews_r3/rulef-reg24-draft1-r1.md`, 57516 bytes, sha256 9aed2e475ec8a033790275af2ba7a0fd6985870def8f3b05324d5abcef59a3c8, checked on copy; the reviewer's hand-back named the same sha256). Its patch is copied byte for byte to `docs/drafts/reviews-2026-11-13/rulef-reg24-draft1-r1.patch` (sha256 291e478a12f9ee30d2e5ccbcc77ed60bf58183d293a58e07418111e201b9ec00). The reviewer's report follows the line '---' unchanged.

---
# Rule F review: REG-24 draft 1 (C1's confirmation at λ = 2.0), round 1

Reviewer: an independent rule F pass (CLAUDE.md F; docs/process.md §3), 2026-11-14. Read-only on the repository: nothing committed, nothing applied in the main checkout, no GPU, VM or ssh.

## 0. What this review saw, and what it ran

- **Under review:** `docs/drafts/reg24_confirm_draft1.md` and `docs/drafts/reg24_r1/reg24.patch` at `56820bd`. The patch's sha256 is `d0276f70745cd0bc113d26d32dcb43d53ccae6fa1371f79288559a706cdf2d4f`, as stated (PROBE: `shasum -a 256`).
- **Code the diff depends on, read at `56820bd`:** `analysis/gate.py` (REG-15, REG-16 and REG-19 functions, `owed_backlog`, `cold_windows`, `reg16_control_outcome`, `reg19_emptyings`, `reg19_cold_side`, `surge_run`), `analysis/load.py` (`_level`, `verdict`, `load_run`, `find_runs`), `analysis/withheld.py`, `harness/workload.py`, `harness/loadgen.py` (`session_chain`), `harness/run.py`, `harness/env_snapshot.py`, the `k3w.py` docstring (code only; nothing of `k3`/`k3w` was run), `configs/l1_base.yaml`, `tests/test_withheld.py`.
- **Rules cited by the draft, checked at the cited lines:** CLAUDE.md; PROTOCOL.md §3 to §6; docs/process.md §2, §3 and §5; `agent/DECISION_TREE.md` (all 72 lines); docs/decisions.md:3800–3806 (REG-19's registered branches), 3129–3137 (REG-15's [CORR]s), 3946–3948 (the 2026-11-12 design choices); docs/claims.md K3.
- **Not read, by rule F's "no results":** REG-19's, REG-21's and REG-22's [RESULT] lines (decisions.md:16421, 16517–16565, 16729, 16798) and every run folder. Where the draft rests on a number from them, this review says so and does not check it.
- **Ran, in a scratch export** (`git archive 56820bd analysis harness configs tests pyproject.toml`, patch applied with `git apply`, the repo's `.venv` interpreter):
  - `pytest tests/test_confirm.py`: 42 passed.
  - The whole suite without `tests/test_check_docs.py` and `tests/test_manifest.py`, which need `docs/` and `tools/` (not in the export): 558 passed, 1 skipped.
- **Schedule-only scripts** (the configs alone, no run): the scan of the 640 candidate schedules for the tilt between the judged windows (§1, T5; RE9), the token model's sensitivity to r, and the factor-two rule. Synthetic traces on the draft's own `burst_table` (§1). Scripts and outputs are in this review's scratch folder, `rev_scripts/`. They are one-off scripts, so they are **not provenance under rule I**. RE9 moves the one number the [REG] should quote into a committed function.
- **Reviewer patch:** `rulef-reg24-draft1-r1.patch`, next to this file, made against the draft's patch applied to `56820bd`. With it applied, `tests/test_confirm.py` and `tests/test_withheld.py` pass: 65 passed. The whole-suite result is in §7. The patch is reproduced in the Appendix.

## Summary

The design is sound in its frame. Design B (a same-schedule control first, then the burst run) is the right choice, and the seed rule judges schedules only. Five gaps let `confirms` be issued where C1's conditions 5–6 do not hold:

- The decisive rule drops REG-19's whole-window cold side. A `stuck` verdict on a total line that is shrinking, a long drain, can then reach `confirms` (T1).
- An emptying that starts in the last 30 s of the watch is credited to the drop (T2).
- The drop's "line emptied" is a single 30 s zero of the waiting gauge. Under closed-loop turns, that can occur while hundreds of turns are still owed. K3 is measured on it, and so is the `no_return` reading (T3).
- Nothing pins both runs to one build.
- The seal and the queue are not part of the reviewed change.

The decision section also credits `confirms` with something it cannot change: D1/D2 go ahead either way. All of these are fixed by the code and text below.

## 1. Traces on which the verdict is wrong

All three traces T1–T3 were run on the draft's unmodified `confirm.burst_table`, on synthetic runs built with the draft's own `_synthetic_run` (seed 15's burst config at 5400 s; `rev_scripts/traces_on_draft.py`). Each gives `confirms`.

### T1 (decisive, false `confirms`): a long drain read as stuck

The draft's `confirms` needs `load.verdict` = `stuck` at 4980–5580 s, but no growing line. The draft reports REG-19's cold side, completions below min(λ, λp), only as a readout (`burst_table`, `out["cold_side"]`). REG-19's pass required it: its `stuck_not_cold` is not a pass (FILE(analysis/gate.py:1945), `reg19_seed_outcome`). With closed-loop turns, the waiting gauge holds one request per active session, so it can stay flat while the total line (`gate.owed_backlog`) shrinks.

Numbers for seed 43:
- **Baseline, 300–900 s:** pf 0.990, hit 0.838, q 0.4.
- **Previous window, 4380–4980 s:** pf 0.53, hit 0.69.
- **End window, 4980–5580 s:** pf 0.55 (at most 0.89), hit 0.70 (at most 0.778), q 95, q_slope −0.010/s.
- **Verdict on those windows:**
  - q / −slope = 9500 s, over 3600 s, so no drain sign.
  - pf rose by 0.02 (under 0.05) and hit by 0.01 (under 0.06).
  - So `load.verdict` gives `stuck`.
- **(e) and (f):** no 300 s window is `recovered` (hit ≤ 0.72 throughout), and the waiting line never falls below 80.
- **Cold side over [1680, 5580):**
  - The planned session rate is 2.045 (DERIVED, `confirm._rate` on seed 43's schedule, `rev_scripts/lamp_w.py`).
  - A partly warm server at hit 0.70 has about 30 % of its prompt tokens uncached, against 16 % warm. It completes 2.08 req/s (BELIEF as to the level; it lies between the all-miss rate and μ_warm 2.4).
  - The total line therefore shrinks by about (2.08 − 2.045) × 3900 ≈ 137 requests over the watch (DERIVED).
- **Drop:** the line empties, the return's end is `recovered`, and the label is **`confirms`**.

Left at λ = 2.0, this server would have caught up without any drop. It is REG-19's `stuck_not_cold`, a long transient. Condition 5 (persistence) is not shown.

On the draft's code, the synthetic version gives `v5 stuck, c 1.0, λp 1.0, total line 6 at 1680 s and 6 at 5580 s, outcome confirms`. The total line does not grow, and the label is still `confirms`. **RE1.**

### T2 (edge, false `confirms`): an emptying that starts just before the watch's end

`emptyings(run, 1080, 5580)` needs the 30 s hold to end by 5580 s. `emptyings(run, 5580, 14580)` starts with `refilled = True`. A line that empties at 5560 s and stays empty to 5700 s is therefore not in the watch's list. It becomes the drop's first emptying, at 5580 s.

The verdict stays `stuck`: q 99.3, q_slope −0.024, so 4126 s to empty, over 3600. On the draft's code: `watch [] drop [5580.0, 6600.0] outcome confirms`. The line emptied at λ = 2.0, which by REG-19's reading means not stuck through the watch, and the label should be `emptied_in_watch`. **RE2.**

### T3 (false K3 label and false `no_return` reading; edge: false `confirms`): a gauge zero is not a drained line

With closed-loop turns, a turn is released only after the previous turn of its session ends, plus the planned gap (FILE(harness/loadgen.py:139), `session_chain`). The gauge reads 0 once every active session's current request is in the running set. `k3w` says so for vLLM 0.32.0's gauge (FILE(analysis/k3w.py:17)–FILE(analysis/k3w.py:21), citing `Scheduler.get_request_counts`).

Late in the drain, the pool holds the full prompts of only about 24–44 sessions (DERIVED: 96,656 / 3968 and 96,656 / 2176; FILE(configs/l1_base.yaml:16), FILE(harness/workload.py:97)). Each of those sessions can still owe up to 7 turns. So a 30 s zero can come while 100–400 turns are owed and the KV is full and evicting.

Constructed example, in seconds into the drop:
- **Flicker:** a 35 s zero at 1820 s, total line 300, hit 0.25.
- **Refill and drain:** the line refills to 20–40, and the total line reaches its pre-burst level at 3020 s.
- **K3, the draft's way:**
  - The draft measures 1820 s, which is `outside_early` against [2130, 4080].
  - The quantity both models predict (work owed since the trigger done) gives 3020 s, which is `inside`.
- **`after_empty`, the draft's way:**
  - The draft reads [2420, 3020): the line is still owed there and the cache is cold, so it reads `cold_after_empty`.
  - If the return then re-tips at its 2.650 peak, the label is `no_return`.
  - The decision table then says "the cache stayed cold with the line empty at λ ≈ 1. The cold state is then not held by load ... news in itself". That is false: the line was not empty.
- **Edge:** if the total line does not drain within the drop but the return's end is `recovered`, the draft gives `confirms`.
  - On the draft's code: a 40 s zero at 5800 s, total line 469 at 5580 s and 469 at 10970 s, return `recovered`, outcome **`confirms`**, K3 220 s `outside_early`.
  - So the cold state ended only once the load was back at λ = 2.0. That is not condition 6.
  - With a 9000 s drop this edge is unlikely (BELIEF), but the rule should not allow it.

**RE3.**

### T4 (reverse, false `not_persistent`; optional): the end window's pf is measured during the drop

`load._level` takes pf over requests by `t_planned` (FILE(analysis/load.py:167)). TTFT runs from `t_released` (FILE(analysis/load.py:26)).

At the watch's end the release lag is about the total line over the completion rate: 1670 / 1.758 ≈ 950 s (DERIVED, the request model's expected line at 5580 s and REG-15's c_watch; REG-15 measured 856 s at 2.2, FILE(docs/decisions.md:3129)). So nearly all requests planned in 4980–5580 s are released in 5930–6530 s, inside the drop.

If the drop drains faster than both models (waiting near 0 within about 950 s), pf(end) − pf(prev) can reach 0.05. `load.verdict` then gives `slow_drain`, and the label is `not_persistent` for a state that persisted at λ = 2.0. Both models put the drain at 2130–4080 s (DERIVED, `confirm.inputs`), so this is unlikely. It is cheap to show: **RE-O1.**

### T5 (no false label; a selection fact the [REG] must state): the pick has the largest tilt of all admitted schedules

Over the 640 candidate (seed, drop) schedules, 25 pass W. The pick's end-window λp minus its return's-end λp is **+0.165 req/s**. That is the largest of the 25: 0 of 25 are larger; the median is +0.003 and 13 of 25 are positive. The largest tilt W allows is 0.200. Seed 61 at 5400 s, the drop-first pick, has +0.107 (DERIVED, `rev_scripts/scan_tilt.py` and `tilt_summary.py`, schedules only, after the pick).

The rule did not select on tilt; seed order did. But the heavier window is the one judged `stuck`, and this is the most favourable schedule for `confirms` that the rule admits. The draft's answer is the control plus the cold rate. Both stand, and RE1 strengthens the second. The number belongs in the [REG], from a committed function. **RE9.**

## 2. Strongest alternative explanation of the likely outcome

The draft's likely outcome is `confirms`: P ≈ 0.55 for the pair given valid runs (BELIEF, the draft).

**Strongest alternative: the persistence is held by the clients' backlog against the pool size, not by the loop C2 states.**

- **What holds the cold state.** At the watch's end the request model owes about 1670 requests, so at least 209 sessions hold owed turns (DERIVED: 1670 / 8). Their contexts total about 209 × 3000 ≈ 0.63 M tokens against a 96,656-token pool (DERIVED). Each turn arrives about 950 s late (T4), after its prefix has been evicted, so every turn misses. This needs the active-session working set to exceed the pool, not a "big running batch".
- **Why the drop clears it.** It clears because λ = 1 is below the cold completion rate. Then the return finds a warm server.
- **What it means for C1 and C2.** Under this reading, `confirms` is C1 met: two states at one load, persistence, exit at low load. But it says nothing about C2's chain "slow requests → big running batch → KV memory full" (PROTOCOL §2). A reader may take it as support for C2.
- **What separates the two readings:**
  - inside REG-24, as readouts: condition 4's levels over the watch's last 1500 s (N against baseline N, N against 256, KV), `release_delay` at each phase's end, and the total line's slope over the watch;
  - outside REG-24: REG-20's open-loop arm (K1) and condition 4's order clause.
- **What the [REG] should say.** REG-24 cannot separate these readings. Its alternatives should name this one as not ruled out, a limit of what C1 tests (wording; folded into RE6's `confirms` sentence: "C1 ... not C2").

**For the other expected labels:**
- **`control_warm` (draft P 0.85):** the control is warm because the schedule is light in its tipping windows (largest 120 s peak 2.733 against REG-19's 2.833–3.092, a number from REG-19's result that this review did not check). This is not a defect, since it is the burst run's schedule too. It does mean `control_warm` says the warm state lasts on *this* schedule, not at λ = 2.0 in general (wording for the `confirms` sentence; RE6 has it).
- **K3 `inside` (draft P 0.7 given an emptying):** with the draft's measured quantity, a gauge zero, the label is biased early (T3). After RE3 the alternative is the token model's all-miss assumption near the end of the drain, where hits return and U falls as the engine idles. These biases work in opposite directions, and the measured r over the drop (RE-O4) separates them.

## 3. Can the run change any decision?

**Yes, one, narrowly: what the paper and `docs/claims.md` say about C1 at λ = 2.0.**

- **Under `confirms`:** C1 is replicated here by all six conditions, except condition 4's order clause.
- **Under any other label:** conditions 1–4, held 3000 s in 5 of 5 seeds; persistence or two states not shown.
- **Also:** one point of K3's model-against-measurement figure.
- **What it does not change:**
  - D1/D2. They are registered at λ = 2.0 whatever REG-24 gives, by the 2026-11-13 correction (FILE(agent/DECISION_TREE.md:21)), and they run before it (FILE(agent/DECISION_TREE.md:72), item 5 before item 6).
  - Any other run. The draft's "D1/D2 at λ = 2.0 go ahead as `agent/DECISION_TREE.md` plans" under `confirms` must go (RE6).
- **Weighing it.** By rule A1 the run is proposable. The cost is about 9.1 GPU h if both runs are made, about 8.4 h expected, and up to about 27 h in the worst case (DERIVED, the draft). Whether one replicated premise sentence and one K3 point are worth that is the owner's to weigh. This review does not object to it.

## 4. The writer's open points

1. **The 9000 s drop departs from PROTOCOL §3 item 6.** Agreed that it needs the owner. The 2026-11-12 delegate choice already says the drop is sized beforehand and that 1800 s was too short (FILE(docs/decisions.md:3948)). PROTOCOL changes are the owner's (CLAUDE.md C). The §6 row text is given in **RE8**.
2. **W, not the drain, sets 9000 s; drop-first would pick seed 61 at 5400 s.**
   - Keep the frozen rule. Switching after the scan is a choice made after seeing the data it judges (rule A5). The data are schedules, but the rule judges exactly them.
   - T5 does not change this. Seed 61 at 5400 s also tilts towards `confirms` (+0.107), and no admitted alternative is neutral by construction.
3. **F differs from the 2026-11-12 factor-two sizing.** No conflict.
   - The factor-two rule holds: 2 × 1670 / (1.681 − 0.99367) = 2 × 2430 = 4859 s ≤ 9000 (DERIVED, `rev_scripts/r_sens.py`). The draft's 2431 and 4862 round λp to 0.994 first; see RE-O5.
   - W decides the pick under either rule.
   - Put the factor-two number in code (RE-O5).
4. **Pessimistic r = 0.95.** This only matters for K3.
   - F holds at 9000 s for r down to about 0.85: 6960 + 1200 ≤ 9000. At r = 0.80 the line never empties (DERIVED, `confirm.empty_time_tokens` on seed 43; `rev_scripts/r_sens.py`).
   - The band [2130, 4080] corresponds exactly to r ∈ [0.95, 1.05].
   - J1's 0.05 is a tolerance on a median over runs, not a per-run prediction interval. Say so (RE-O4).
5. **Readouts added after the freeze; no commit holds the frozen state.** The draft's check, "revert those two hunks ... and the sha256 above comes back", cannot be run. The patch adds `confirm.py` as a new file, so it has no hunks against the frozen file. This review tried 15 reconstructions of the frozen text (the `seed`/`drop_s` line and its comment, and the five readouts); none hashes to `6801457c…` (PROBE: `rev_scripts`'s `freeze_try_gen.py`). The patch's own `confirm.py` hashes to `5ba55384ae3662f6d021ed410b978e3404ee798c5796319bc41ef030f44b93fb`. **RE7.**
6. **The seal entry and the queue script.** These are required before registration, not after. The seal hunk and its test are in the reviewer patch; the queue script needs its own rule F pass. **RE5.**
7. **Power-off risk.** Accepted as a cost and a validity risk; no design change. A lost run selects on power events, not outcomes (agreed). The stopping rule must say what a burst run with three invalid attempts gives (RE6).
8. **Pinned values in place of a tolerance chosen after the numbers.** Acceptable. The pinned values in `test_request_model_on_reg19s_schedules` judge nothing and only guard against regression; the draft labels them a readout.

## 5. Required items

### RE1: REG-19's whole-window cold side becomes a condition of `confirms` (stricter rule; code change)

Code: the reviewer patch's `confirm.cold_side`, the label `stuck_not_cold` in `burst_outcome` (after `emptied_in_watch`, before `drop_inconclusive`), `pair_outcome`'s list of labels that stand whatever the control, and `burst_table`.

Replacement text in "What `confirms` requires", after (d):

> - (d2) REG-19's whole-window cold side holds over [1680, 5580) s (`confirm.cold_side`, REG-19's `reg19_cold_side` with W from the burst's end + 600 s to the watch's end): completions (session and burst, by `t_end`) below min(λ, λp), where λp is the planned session rate in that window, 2.045 for seed 43 (DERIVED, schedule only). If either rate is NaN, the label is `inconclusive`. If the rate is not below, the label is `stuck_not_cold`: the total line was not growing, so the `stuck` verdict may be a long drain.

Replacement text in the label list, a new item between 5 and 6:

> 6. **`stuck_not_cold`:** stuck, never recovered, never emptied in the watch, but completions over [1680, 5580) s were not below min(λ, λp) (REG-19's `stuck_not_cold`). Condition 5 is not shown.

In "Every threshold, and its source", add under "From REG-19": "the whole-window cold side, from the burst's end + 600 s (`gate.REG19["window"][0]`)". In the prediction table, add a `stuck_not_cold` row; its probability is the writer's.

### RE2: one emptying pass across the watch's end (code change)

Code: `burst_table` computes `emptyings(run, burst_end, drop_end)` once. Emptyings that start before 5580 s go to the watch and the rest to the drop. Tested by `test_burst_table_rules_of_rule_f_round_1`.

Replacement text for (f):

> - (f) No emptying that starts in 1080–5580 s, its 30 s hold allowed to run past 5580 s. The drop's emptyings are counted in the same pass, so an emptying that continues from the watch into the drop belongs to the watch.

### RE3: condition (g), K3 and `after_empty` on the drained total line (stricter rule; code change; reporting duty)

Code:
- `confirm.owed_series`: `gate.owed_backlog` vectorized. `test_owed_series_is_gate_owed_backlog` checks it equals the original.
- `confirm.drained_at`: the first 10 s grid time in the drop at which the total line is at or below its level at the trigger.
- In `burst_table`:
  - (g) needs both a gauge emptying and a drain;
  - K3's `measured_s` is the drain;
  - the gauge's first zero is kept as a readout (`first_empty_s`, `label_first_empty`);
  - `after_empty` is read from the drain.

Replacement text for (g):

> - (g) In 5580–14580 s, at least one emptying (a 30 s zero of the waiting gauge, PROTOCOL's "the line reached 0"), and the total line (`gate.owed_backlog`: planned and not completed, the clients' unreleased turns included) back at or below its level at the trigger (900 s), on the 10 s grid (`confirm.drained_at`). If the line drains only after 14580 s, the label is `drop_inconclusive`.

Replacement text for the K3 paragraph's measurement:

> The measured value is the time into the drop at which the total line is back at its level at the trigger (`drained_drop_s`). This is the event both drain models predict, the work owed since the trigger done. The waiting gauge's first 30 s zero is reported beside it with its own band label, as a readout. Under closed-loop turns it can come while turns are still owed (T3, rule F round 1).

Replacement text for the `no_return` decision:

> `after_empty` is read in [drain + 600, drain + 1200) s, where the drain is `drained_at`, not the first zero of the gauge. `cold_after_empty` then means a cold cache with the total line drained.

### RE4: both runs from one build (stricter rule; code change)

Code: `table()` returns `not_same_build`, and no other label, unless both runs' `env.json` `git_commit` are equal and set. Tested by `test_table_refuses_a_pair_from_two_builds`.

Replacement text under "Operations":

> - **The VM pin.** Both runs run from commit `<the registration commit>`, checked out clean on the VM. Reruns use the same commit. `confirm.table` gives `not_same_build` if the two runs' `env.json` commits differ; the owner decides then, and no rerun follows from it. Other work's harness changes (E1, D1/D2) do not enter the VM checkout until REG-24's last run is copied.

### RE5: the seal and the queue before registration (code change; prerequisite)

Code: two exact `SEALS` entries in `analysis/withheld.py`, and `test_reg24_seal_covers_exactly_its_two_configs`. This is an existing file, so the patch must now be made against main's tip, not `a7bb77a`:

```
    ("REG-24", "*_confirm_l1pl350cl_r2.0_s43", "[RESULT] REG-24"),                 # C1's confirmation, burst run
    ("REG-24", "*_stage2_control_l1pl350cl_r2.0_long_s43", "[RESULT] REG-24"),     # and its same-schedule control
```

Exact patterns are preferred to the draft's `*_l1pl350cl_r2.0_*s43`. Each names one config, and the test checks that over every config, exactly these two are sealed.

Replacement text for "Operations: Seal":

> - **Prerequisites; no run starts before each is committed:**
>   - (1) the two `SEALS` entries and their test (this registration's patch);
>   - (2) the queue script: control, copy, `reg24_step`, burst run, copy; `reg24` only by its final step;
>   - the script has its own rule F pass, recorded in an [OPS] entry.
>
>   `reg24_step` and `reg24` run with `AFTERSHOCK_UNSEAL=REG-24`, and nothing else does.

### RE6: decisions fixed now, with rule H's bound (reporting duty; wording)

Replace "Decision under each outcome" with:

> **What REG-24 can change:** the paper's sentence on C1 at λ = 2.0 and C1's line in `docs/claims.md` (after the owner's review), and one point of K3's model-against-measurement figure.
>
> **What it does not change:**
> - D1/D2. They are registered at λ = 2.0 whatever REG-24 gives (FILE(agent/DECISION_TREE.md:21)), and they run before it (FILE(agent/DECISION_TREE.md:72)).
> - No second confirmation seed is drafted on any label unless the owner asks for one.
> - No rerun follows from any label.
>
> **Per cell:** k of n, with the one-sided 95 % Clopper–Pearson upper bound (`analysis.stats.cp_upper(k, 1, 0.95)`): 1 of 1 gives 1.00 (the lower bound 0.05 is reported beside it); 0 of 1 gives 0.95. One seed, with a single same-schedule control (rule H).
>
> - **`confirms`:** "At λ = 2.0, in one seed (43) beside one no-burst control on the same arrivals:
>   - after the burst the server stayed stuck for 4500 s, without its line emptying and with completions below the planned load;
>   - its total line drained [drained_drop_s] s into a 9000 s drop to λ = 1;
>   - the last 600 s of the return to λ = 2.0 were recovered against the pre-burst baseline;
>   - the control stayed warm throughout.
>
>   The stuck window was planned at λp 2.068 and the recovered window at 1.903, the largest such difference among the 25 schedules the seed rule's window test admitted. The control carried both warm. 1 of 1 (one-sided 95 % Clopper–Pearson upper bound 1.00, lower bound 0.05). This meets C1's conditions 5 and 6 at this cell; it does not test C2's chain."
> - **`not_persistent`, `reformed`, `emptied_in_watch`, `stuck_not_cold`:** "At λ = 2.0 the state held for 3000 s in 5 of 5 seeds (REG-19) but not for 4500 s in the confirmation seed ([what happened, and when]). C1's condition 5 is not met at this cell (0 of 1; upper bound 0.95)." The paper describes the cell as "entered and held for 3000 s; persistence beyond it not shown".
> - **`drop_inconclusive`:** "Condition 5 held; condition 6 is inconclusive: the total line did not drain within 9000 s at λ = 1, more than twice both models' pessimistic drain times." K3's point is `undefined`, and both models are reported as failed for this state.
> - **`no_return`**, by `after_empty`:
>   - `warmed`: "the server left the stuck state at λ = 1 and re-tipped on the return, where the control did not. Condition 6 is not met (0 of 1)."
>   - `cold_after_empty`: "the cache stayed cold after the total line had drained at λ = 1: the cold state was not held by load." Reported as found; no claim is widened on it.
>   - None: "condition 6 not met; the reading is undefined."
> - **`control_not_warm`:** "On seed 43's 16080 s schedule the no-burst control did not stay warm ([outcome]). The confirmation is void at this cell, and λ = 2.0 is reported as not reliably warm over 4.5 h, as REG-16 reported 2.2."
> - **`bad_baseline`, `inconclusive`, `not_same_build`, `burst_missing`, `control_missing`, or a queue stop** (a `client_error`, `burst_min_kv_max`, a limit other than 350 W, three invalid attempts of either run): "C1's conditions 5–6 were not tested at λ = 2.0 ([reason])."

In "Stopping rule", add: "A burst run with no valid run after three attempts gives `burst_missing`."

### RE7: freeze evidence that a reviewer can check (reporting duty)

Either commit the frozen state with the [REG], or downgrade the claim. Replacement text for "Timing":

> - **Timing.** The seed rule's code and tests were frozen at 2026-11-13 23:23:39 UTC and run once, 23:23:45–23:23:47 UTC. The timing is BELIEF: the evidence is the agent's scratchpad, not a commit. The frozen files are committed with this entry, unchanged:
>   - `docs/drafts/reg24_r1/confirm_frozen.py` (sha256 `6801457c1b7aec9ef429e4d11a01828ff2ba730f21bb60e920ddaa08bf49c268`);
>   - `docs/drafts/reg24_r1/test_confirm_frozen.py` (sha256 `867aba60fb93e8c1968e2645ba5006497348ebf8817dc36b5da864ac9a09cf0c`);
>   - the rule's saved output, `docs/drafts/reg24_r1/seed_rule_20261113T232345Z.txt`;
>   - `docs/drafts/reg24_r1/frozen_to_registered.diff`, which shows that `REG24`'s settings, `design_row`, `seed_rule` and both models are byte-identical.

If those files no longer exist, delete "A reviewer can check this: revert those two hunks of the patch's `confirm.py` and the sha256 above comes back". In its place write: "No file holds the frozen state; the claim that the rule was fixed before any candidate schedule was read is BELIEF."

### RE8: the owner's approval of the drop, and the PROTOCOL §6 row (wording)

Add under "Setup" (replacing "Approving REG-24 approves this length ..."):

> - **Owner approval needed, named separately:** the 9000 s drop at λ = 1, against PROTOCOL §3 item 6's 1800 s. If approved, the owner adds this row to PROTOCOL §6:
>
> | Condition 6's drop at λ = 2.0 (REG-24) lasts 9000 s, not 1800 s | Under closed-loop turns the total line at the watch's end is about 1670 requests (request model) and needs about 2130–4080 s at λ = 1 (the two models, optimistic to pessimistic). REG-15's 1800 s drop was `drop_inconclusive`. Among 3600–9000 s, the seed rule's window test chose 9000 s | 2026-11-14 [REG] REG-24 (owner) |

### RE9: the tilt from a committed function, in the [REG] (reporting duty; code change, readout only)

Code: `confirm.tilt_scan` (CLI `reg24_tilt`). Its test pins seeds 43 and 61. Add under "Design inputs", after the 8.7 % paragraph:

> - **Among the schedules W admits, the pick has the largest tilt** (`uv run python -m analysis.confirm reg24_tilt`, `confirm.tilt_scan`; schedules only, computed after the pick; a readout):
>   - Of the 25 (seed, drop) schedules that pass W, none has a larger end-minus-return λp than the pick's +0.165 req/s. W allows up to 0.200.
>   - Seed 61 at 5400 s, the drop-first pick, has +0.107.
>   - The design's answer is the same-schedule control (Design B) and the cold side (d2).
>   - The `confirms` sentence gives both windows' λp.

(This review's values come from a one-off script, `rev_scripts/scan_tilt.py`. The writer quotes the committed function's output, not these.)

## 6. Optional items

- **RE-O1 (reporting duty; code change, readout): the end window measured in the drop (T4).** In `burst_table` add the following:
  ```python
  def released_after(run: dict, a: float, b: float, t: float) -> float:
      """Share of the requests planned in [a, b) that were released (closed loop) or sent at or after t; a request
      never sent counts as after."""
      q = run["requests"]
      s = q[(q.t_planned >= a) & (q.t_planned < b)]
      rel = (s.t_released.fillna(s.t_sent) if "t_released" in s else s.t_sent).astype(float).fillna(np.inf)
      return float((rel >= t).mean()) if len(s) else math.nan
  # in burst_table:
  jw = judged_windows(run["cfg"])
  out["end_window_mix"] = {"released_in_drop": released_after(run, *jw["end"], we),
                           "pf_by_sent_prev": G.pf_by_sent(run, *jw["previous"]),
                           "pf_by_sent_end": G.pf_by_sent(run, *jw["end"])}
  ```
  Text: "If `not_persistent` comes only from the pf-climb sign and more than half of the end window's requests were released in the drop, the report says so."

- **RE-O2 (readout): a co-tenant on the GPU.** PROTOCOL §4 says the GPU is shared. The process list is read only before launch (FILE(harness/run.py:97)). Report `mem_used_mib` max minus min per phase from `run["gpu"]`, for both runs, and the `gpu_processes` field of `env.json`.

- **RE-O3 (test robustness):** `test_seed_rule_picks_seed_43_at_9000_s` and `test_seed_range_is_unused_and_outside_reg20b` fail as soon as any later config sets a seed in 40–42 (`used_seeds` reads the configs present). Monkeypatch `C.candidate_seeds` to `tuple(range(40, 200))` in the pick test, and add a guard: "no config other than REG-24's sets seed 43".

- **RE-O4 (reporting duty): K3's band as an r interval.**
  - The band [2130, 4080] s is r ∈ [1.05, 0.95] × U_off over the drop. J1's 0.05 is a tolerance on a median over runs.
  - Report the r that the measured drain implies: the u that solves `empty_time_tokens(sched, cfg, u) = drained_drop_s`, by bisection on [0.5, 1.5] × U_off.
  - Report REG-21's per-run spread of r beside it.

- **RE-O5 (code, readout; wording):** compute the 2026-11-12 factor-two length in `inputs()`.
  - Add `"floor_8": 1.681` to `REG24`. That is REG-8's open-loop cache-off floor, as `analysis/k2.py` holds it (FILE(analysis/k2.py:24)). `gate` has no constant for it: `gate.reg8_zone` computes it from runs.
  - Add to `inputs()`:
    ```python
    "factor_two_s": 2 * owed_requests_model(sb, b, cal, we) / (REG24["floor_8"] - _rate(tp, *ph["drop"]))
    ```
  - Correct the text's 2431 and 4862 to 2430 and 4859 (λp 0.99367, unrounded).

- **RE-O6 (wording):** the draft says "Five windows sit at 1.80–1.84 ... These are the likeliest places for the line to empty in the watch." Replace with:
  > Under closed-loop turns the server receives released turns, not planned ones. The watch's planned dips reach it only once the total line is small. With about 1000–1700 owed requests through the watch (request model), an emptying in the watch is unlikely (BELIEF).

- **RE-O7 (wording):** "Why now" says the confirmation runs after REG-20's gate. The GPU order puts it after E1 → E2 and D1/D2 (FILE(agent/DECISION_TREE.md:72)). Write both, and keep "The owner sets the order".

- **RE-O8 (code):** `step()` computes the whole `control_table`, including the readouts `surge_run`, `window_mix` and `reg15_timeline`. An exception in a readout would stop the queue. Let `step` compute only what `reg16_control_outcome` needs. (This review ran `control_table` with the real `surge_run` on a synthetic REG-24 control; it worked. The draft's test replaces `surge_run` with a stub.)

## 7. Checks done

- **The patch:**
  - Its sha256 matches.
  - It applies cleanly to an export of `56820bd`.
  - The draft's 42 tests pass.
  - The whole suite passes: 558 passed, 1 skipped, without `test_check_docs.py` and `test_manifest.py`.
- **With the reviewer patch on top:**
  - `tests/test_confirm.py` and `tests/test_withheld.py` pass: 65 passed.
  - Whole suite, with the same two exclusions: see the line below.

  567 passed, 1 skipped. That is a fresh `git archive` of `56820bd`, then the draft's patch, then this patch, the same two files left out (PROBE: pytest stdout).
- **Claims of the draft checked and found as stated:**
  - The control's schedule equals the burst run's session rows.
  - Only five keys differ from REG-19's ten configs.
  - Phases and judged windows.
  - The request model equals `gate.reg16_empty_time` and gives REG-16's 4340 s and 5540 s.
  - The seed rule's 16 rows and the pick (43, 9000).
  - The scan counts: W 7/6/5/7, all three conditions 0/4/5/7.
  - The empty times 2490 (3550) and 2130 / 2560 / 4080.
  - The 300 s watch spans.
  - The 120 s peaks.
  - The factor-two arithmetic, up to rounding.
- **Claims not checked (they rest on [RESULT] lines that rule F does not read):**
  - REG-19's measured total lines.
  - Its c of 1.703–1.800.
  - Its control peaks.
  - REG-21's r of 1.021 and 1.028.
  - U_off.

## Verdict

**NOT READY.** Required: RE1 (cold side decisive), RE2 (one emptying pass across the watch's end), RE3 (drop drain on the total line for (g), K3 and `after_empty`), RE4 (one build for both runs), RE5 (seal and queue before registration), RE6 (decisions fixed now, D1/D2 not contingent, rule H's upper bound), RE7 (checkable freeze evidence), RE8 (owner approval and the §6 row for the 9000 s drop), RE9 (the tilt from a committed function).

## Appendix: reviewer patch

File: `rulef-reg24-draft1-r1.patch`, next to this review. Apply it with `git apply` on top of `docs/drafts/reg24_r1/reg24.patch` applied to `56820bd`. Its sha256 is given in the line below.

sha256 `291e478a12f9ee30d2e5ccbcc77ed60bf58183d293a58e07418111e201b9ec00`; 4 files: `analysis/confirm.py`, `analysis/withheld.py`, `tests/test_confirm.py`, `tests/test_withheld.py`. It is a sketch for the writer, not applied anywhere in the repository.

```diff
diff --git a/analysis/confirm.py b/analysis/confirm.py
index 7915e09..e766e68 100644
--- a/analysis/confirm.py
+++ b/analysis/confirm.py
@@ -269,6 +269,19 @@ def seed_scan(seeds=None) -> dict:
     return out
 
 
+def tilt_scan(seeds=None) -> dict:
+    """Readout only, after the pick (rule F round 1, RE9): over every (seed, drop) whose four judged windows pass W, the
+    end window's λp minus the return's end's (positive favours `confirms`: the window judged `stuck` carries more
+    planned load than the one judged `recovered`), and how many W-passing schedules carry a larger tilt than the pick."""
+    rows = [design_row(sd, d) for sd in (seeds or candidate_seeds()) for d in REG24["drop_candidates"]]
+    tilt = lambda r: r["lam_p"]["end"] - r["lam_p"]["return_end"]
+    w = [r for r in rows if r["windows_ok"]]
+    pick = next(r for r in rows if (r["seed"], r["drop_s"]) == (REG24["seed"], REG24["drop_s"]))
+    return {"n_windows_ok": len(w), "tilts": [(r["seed"], r["drop_s"], tilt(r)) for r in w],
+            "pick_tilt": tilt(pick), "n_larger": sum(tilt(r) > tilt(pick) for r in w),
+            "max_possible": 2 * REG24["window_tol"] * REG24["lam"]}
+
+
 def model_check_reg19() -> list[dict]:
     """Schedule only: the request model's owed backlog (expected and pessimistic) at the start and end of REG-19's
     window W (1680 and 4080 s) on REG-19's five burst configs, to set beside the measured total line that REG-19's
@@ -360,11 +373,37 @@ def emptyings(run: dict, a: float, b: float) -> list[float]:
     return out
 
 
-BURST_LABELS = ("bad_baseline", "not_persistent", "inconclusive", "reformed", "emptied_in_watch",
+BURST_LABELS = ("bad_baseline", "not_persistent", "inconclusive", "reformed", "emptied_in_watch", "stuck_not_cold",
                 "drop_inconclusive", "no_return", "confirms")
 
 
-def burst_outcome(v5: str, broken: bool, emptied_watch: bool, emptied_drop: bool, back: bool | None) -> str:
+def owed_series(run: dict, grid: np.ndarray) -> np.ndarray:
+    """`gate.owed_backlog` at every grid time (requests planned before t and not completed by t), vectorized."""
+    q = run["requests"]
+    tp = np.sort(q.t_planned.to_numpy(float))
+    te = q.t_end.to_numpy(float)
+    te = np.sort(te[np.isfinite(te)])
+    return np.searchsorted(tp, grid) - np.searchsorted(te, grid)
+
+
+def drained_at(run: dict, a: float, b: float, level: float) -> float:
+    """The first time on the grid_s grid in [a, b) at which the total line (`owed_series`) is at or below `level` (the
+    line at the trigger): the event both drain models predict, the work owed since the trigger done. NaN if none."""
+    grid = np.arange(a, b, REG24["grid_s"])
+    i = np.flatnonzero(owed_series(run, grid) <= level)
+    return float(grid[i[0]]) if len(i) else math.nan
+
+
+def cold_side(run: dict, a: float, b: float) -> dict:
+    """REG-19's whole-window test (`gate.reg19_cold_side`) over [a, b): the completion rate (session and burst, by t_end)
+    below min(λ, the planned session rate). `holds` is None if either is NaN."""
+    c, lp = G.completion_rate(run, a, b), G.planned_session_rate(run, a, b)
+    ok = np.isfinite(c) and np.isfinite(lp)
+    return {"window": (a, b), "c": c, "lam_p": lp, "holds": bool(c < min(REG24["lam"], lp)) if ok else None}
+
+
+def burst_outcome(v5: str, broken: bool, emptied_watch: bool, emptied_drop: bool, back: bool | None, *,
+                  cold: bool | None) -> str:
     """The burst run's outcome, REG-15's order (`gate.reg15_outcome`) with REG-19's emptying in place of REG-15's
     single zero scrape, in the watch and in the drop:
     - bad_baseline: v5 (`load.verdict` of the 4500 s watch) `bad_baseline`;
@@ -373,6 +412,9 @@ def burst_outcome(v5: str, broken: bool, emptied_watch: bool, emptied_drop: bool
     - reformed: stuck at the watch's end, but some 300 s window of the watch was `recovered` (`gate.watch_broken`);
     - emptied_in_watch: stuck, never `recovered`, but the waiting line emptied in the watch (REG-19's test: stuck
       through the watch means the line never empties);
+    - inconclusive: the cold side (`cold`) is NaN;
+    - stuck_not_cold: the completion rate over [burst end + 600 s, watch end) is not below min(λ, λp): the total line
+      was not growing, so the `stuck` verdict may be a long drain (REG-19's `stuck_not_cold`; rule F round 1, RE1);
     - drop_inconclusive: the line never emptied in the drop (condition 6 inconclusive, PROTOCOL §3);
     - inconclusive: the return's end has a missing value;
     - no_return: emptied in the drop, but the return's end is not `recovered` against the baseline;
@@ -387,6 +429,10 @@ def burst_outcome(v5: str, broken: bool, emptied_watch: bool, emptied_drop: bool
         return "reformed"
     if emptied_watch:
         return "emptied_in_watch"
+    if cold is None:
+        return "inconclusive"
+    if not cold:
+        return "stuck_not_cold"
     if not emptied_drop:
         return "drop_inconclusive"
     if back is None:
@@ -401,7 +447,8 @@ def pair_outcome(control_label: str | None, burst_label: str | None) -> str:
     - control_not_warm: the control is not `control_warm` (no burst run, or one run against the stopping rule);
     - control_missing: no control label;
     - else the burst run's label (`burst_missing` if the burst run was not run)."""
-    if burst_label in ("bad_baseline", "not_persistent", "reformed", "emptied_in_watch", "inconclusive"):
+    if burst_label in ("bad_baseline", "not_persistent", "reformed", "emptied_in_watch", "stuck_not_cold",
+                       "inconclusive"):
         return burst_label
     if control_label is None:
         return "control_missing"
@@ -484,21 +531,33 @@ def burst_table(run: dict | None = None, control: dict | None = None) -> dict:
     run = run or _one("burst")
     ph, v = phases(run["cfg"]), verdict(run)
     base = v["baseline"]
-    brk = G.watch_broken(run, base, ph["burst_end"], ph["watch_end"])
-    e_watch, e_drop = emptyings(run, ph["burst_end"], ph["watch_end"]), emptyings(run, *ph["drop"])
+    vc, we, de = run["cfg"]["verdict"], ph["watch_end"], ph["drop"][1]
+    brk = G.watch_broken(run, base, ph["burst_end"], we)
+    # one pass from the burst's end to the drop's end (RE2): an emptying that starts in the watch belongs to the watch
+    # even if its 30 s hold runs past the watch's end, and the drop's first emptying needs the line to have refilled
+    e_all = emptyings(run, ph["burst_end"], de)
+    e_watch, e_drop = [t for t in e_all if t < we], [t for t in e_all if t >= we]
     back = G.recovered_against(run, base, *ph["return_end"])
-    label = burst_outcome(v["verdict"], brk["broken"], bool(e_watch), bool(e_drop), back)
+    cs = cold_side(run, ph["burst_end"] + G.REG19["window"][0], we)                       # RE1: REG-19's W start
+    # RE3: the drain both models predict: the total line back at its level at the trigger. Condition (g) needs it as
+    # well as a 30 s zero of the waiting gauge; it is K3's measured value, and the re-warming is read from it, so that
+    # `cold_after_empty` means a cold cache with the line drained
+    t0 = float(run["cfg"]["trigger"]["at_s"])
+    owed0 = G.owed_backlog(run, t0)
+    t_d = drained_at(run, we, de, owed0)
+    emptied_drop = bool(e_drop) and bool(np.isfinite(t_d))
+    label = burst_outcome(v["verdict"], brk["broken"], bool(e_watch), emptied_drop, back, cold=cs["holds"])
     out = {"run": run["dir"].name, "v5": v["verdict"], "baseline": base, "watch_end_level": v["end"],
            "watch_broken": brk, "emptyings_watch": e_watch, "emptyings_drop": e_drop, "return_recovered": back,
-           "return_end_level": _level(run, *ph["return_end"]), "outcome": label, "phases": ph}
-    vc, we, de = run["cfg"]["verdict"], ph["watch_end"], ph["drop"][1]
-    out["owed"] = {"trigger": G.owed_backlog(run, float(run["cfg"]["trigger"]["at_s"])),
-                   "watch_end": G.owed_backlog(run, we)}
+           "return_end_level": _level(run, *ph["return_end"]), "outcome": label, "phases": ph, "cold_side": cs}
+    out["owed"] = {"trigger": owed0, "watch_end": G.owed_backlog(run, we)}
     t_e = e_drop[0] if e_drop else math.nan
     out["first_empty_drop_s"] = t_e - we if np.isfinite(t_e) else math.nan
     if np.isfinite(t_e):
         out["owed"].update(first_empty=G.owed_backlog(run, t_e), first_empty_600=G.owed_backlog(run, t_e + 600))
-        a, b = t_e + 600.0, t_e + 1200.0
+    out["drained_drop_s"] = t_d - we if np.isfinite(t_d) else math.nan
+    if np.isfinite(t_d):
+        a, b = t_d + 600.0, t_d + 1200.0
         if b <= de:
             h = _level(run, a, b)["hit"]
             hc = _level(control, a, b)["hit"] if control is not None else math.nan
@@ -512,14 +571,14 @@ def burst_table(run: dict | None = None, control: dict | None = None) -> dict:
     out["loop"] = {"kv": loop["kv"], "n": loop["n"], "n_over_base": loop["n"] / base["n"], "n_max": n_max,
                    "n_cap": REG24["n_cap"]}
     out["release_delay"] = G.release_delay(run, [(we - 300, we), (de - 300, de), ph["return_end"]], end=0.0)
-    a = ph["burst_end"] + 600.0
-    c, lp = G.completion_rate(run, a, we), G.planned_session_rate(run, a, we)
-    out["cold_side"] = {"c": c, "lam_p": lp, "below": bool(c < min(REG24["lam"], lp))}
     out["judged_lam_p"] = {k: G.planned_session_rate(run, *w) for k, w in judged_windows(run["cfg"]).items()}
     pred = inputs(REG24["seed"], REG24["drop_s"])["empty_s"]
     out["k3"] = {"predicted_s": pred["tokens"], "band_s": (pred["tokens_optimistic"], pred["tokens_pessimistic"]),
-                 "measured_s": out["first_empty_drop_s"],
-                 "label": k3_band(out["first_empty_drop_s"], pred["tokens_optimistic"], pred["tokens_pessimistic"])}
+                 "measured_s": out["drained_drop_s"],
+                 "label": k3_band(out["drained_drop_s"], pred["tokens_optimistic"], pred["tokens_pessimistic"]),
+                 "first_empty_s": out["first_empty_drop_s"],           # readout: the waiting line's first 30 s zero
+                 "label_first_empty": k3_band(out["first_empty_drop_s"], pred["tokens_optimistic"],
+                                              pred["tokens_pessimistic"])}
     out["timeline"] = G.reg15_timeline(run)
     return out
 
@@ -536,12 +595,16 @@ def table() -> dict:
         return {"control": ctl, "burst": None, "outcome": pair_outcome(ctl["outcome"], None)}
     b_run = _one("burst")
     bt = burst_table(b_run, ctl_run)
-    return {"control": ctl, "burst": bt, "outcome": pair_outcome(ctl["outcome"], bt["outcome"]),
+    # RE4: both runs from one build (the VM pin); otherwise the pair says nothing and the owner decides
+    gc, gb = ctl_run["env"].get("git_commit"), b_run["env"].get("git_commit")
+    same = gc is not None and gc == gb
+    return {"control": ctl, "burst": bt, "same_build": same,
+            "outcome": pair_outcome(ctl["outcome"], bt["outcome"]) if same else "not_same_build",
             "baseline_pair": G.reg19_baseline_pair(ctl_run, b_run)}
 
 
 if __name__ == "__main__":
     import sys
     fns = {"reg24_seed_rule": seed_rule, "reg24_inputs": inputs, "reg24_scan": seed_scan,
-           "reg24_model_check": model_check_reg19, "reg24_step": step, "reg24": table}
+           "reg24_model_check": model_check_reg19, "reg24_tilt": tilt_scan, "reg24_step": step, "reg24": table}
     print(fns[sys.argv[1]]())
diff --git a/analysis/withheld.py b/analysis/withheld.py
index 46b42a7..dae4fb3 100644
--- a/analysis/withheld.py
+++ b/analysis/withheld.py
@@ -29,6 +29,8 @@ SEALS: tuple[tuple[str, str, str], ...] = (
     ("REG-20", "*_burst_l1pl350cl_r2.0_w3000_s15_drift", "[RESULT] REG-20"),
     ("E1", "*_sweep_l1pl350cl_pc_off_r*", "[RESULT] E1"),            # the closed-loop cache-off sweep at 8 turns
     ("E0", "*_sweep_l1t16pl350cl_pc_o*_r*", "[RESULT] E0"),          # E2: both 16-turn sweeps, until the gate
+    ("REG-24", "*_confirm_l1pl350cl_r2.0_s43", "[RESULT] REG-24"),                 # C1's confirmation, burst run
+    ("REG-24", "*_stage2_control_l1pl350cl_r2.0_long_s43", "[RESULT] REG-24"),     # and its same-schedule control
 )
 
 
diff --git a/tests/test_confirm.py b/tests/test_confirm.py
index 2aea8af..798944f 100644
--- a/tests/test_confirm.py
+++ b/tests/test_confirm.py
@@ -174,20 +174,23 @@ def test_emptyings_need_30_s_of_zeros_inside_the_window():
     assert C.emptyings(run, 0, 100) == []
 
 
-@pytest.mark.parametrize("v5,broken,ew,ed,back,want", [
-    ("bad_baseline", False, False, True, True, "bad_baseline"),
-    ("recovered", True, True, True, True, "not_persistent"),
-    ("slow_drain", False, False, True, True, "not_persistent"),
-    ("unclear", False, False, True, True, "inconclusive"),
-    ("stuck", True, True, True, True, "reformed"),
-    ("stuck", False, True, True, True, "emptied_in_watch"),
-    ("stuck", False, False, False, True, "drop_inconclusive"),
-    ("stuck", False, False, True, None, "inconclusive"),
-    ("stuck", False, False, True, False, "no_return"),
-    ("stuck", False, False, True, True, "confirms"),
+@pytest.mark.parametrize("v5,broken,ew,ed,back,cold,want", [
+    ("bad_baseline", False, False, True, True, True, "bad_baseline"),
+    ("recovered", True, True, True, True, False, "not_persistent"),
+    ("slow_drain", False, False, True, True, True, "not_persistent"),
+    ("unclear", False, False, True, True, True, "inconclusive"),
+    ("stuck", True, True, True, True, False, "reformed"),
+    ("stuck", False, True, True, True, False, "emptied_in_watch"),
+    ("stuck", False, False, True, True, None, "inconclusive"),
+    ("stuck", False, False, True, True, False, "stuck_not_cold"),
+    ("stuck", False, False, False, True, False, "stuck_not_cold"),
+    ("stuck", False, False, False, True, True, "drop_inconclusive"),
+    ("stuck", False, False, True, None, True, "inconclusive"),
+    ("stuck", False, False, True, False, True, "no_return"),
+    ("stuck", False, False, True, True, True, "confirms"),
 ])
-def test_burst_outcome_order(v5, broken, ew, ed, back, want):
-    assert C.burst_outcome(v5, broken, ew, ed, back) == want
+def test_burst_outcome_order(v5, broken, ew, ed, back, cold, want):
+    assert C.burst_outcome(v5, broken, ew, ed, back, cold=cold) == want
     assert want in C.BURST_LABELS
 
 
@@ -198,7 +201,7 @@ def test_burst_outcome_keeps_reg15s_order_where_the_tests_agree():
         for broken in (False, True):
             for ed in (False, True):
                 for back in (None, False, True):
-                    assert C.burst_outcome(v5, broken, False, ed, back) == G.reg15_outcome(v5, ed, back, broken)
+                    assert C.burst_outcome(v5, broken, False, ed, back, cold=True) == G.reg15_outcome(v5, ed, back, broken)
 
 
 @pytest.mark.parametrize("ctl,burst,want", [
@@ -212,6 +215,7 @@ def test_burst_outcome_keeps_reg15s_order_where_the_tests_agree():
     ("control_cold_transient", "not_persistent", "not_persistent"),
     ("control_warm", "reformed", "reformed"),
     (None, "emptied_in_watch", "emptied_in_watch"),
+    ("control_warm", "stuck_not_cold", "stuck_not_cold"),
     (None, "confirms", "control_missing"),
 ])
 def test_pair_outcome(ctl, burst, want):
@@ -285,15 +289,93 @@ def test_burst_table_on_a_synthetic_confirming_run(monkeypatch):
                                                                      "tokens_pessimistic": 1500.0}})
     cold = lambda t: 0.84 if t < 900 or t >= 6600 else 0.0
     q_ok = lambda t: 0.0 if t < 900 or t >= 6600 else 50.0 + 0.01 * t
-    out = C.burst_table(_synthetic_run(cfg, q_ok, cold))
+    grow = lambda r: _with_backlog(r, 900.0, 5580.0, 0.9, 1.0 + 468.0 / 1020.0)      # the total line grows, drains at 6600 s
+    out = C.burst_table(grow(_synthetic_run(cfg, q_ok, cold)))
     assert out["v5"] == "stuck" and not out["watch_broken"]["broken"] and out["emptyings_watch"] == []
+    assert out["cold_side"]["holds"] is True and out["cold_side"]["window"] == (1680.0, 5580.0)
     assert out["emptyings_drop"][0] == 6600.0 and out["first_empty_drop_s"] == 1020.0
+    assert abs(out["drained_drop_s"] - 1020.0) <= 20.0
     assert out["return_recovered"] is True and out["outcome"] == "confirms" and out["k3"]["label"] == "inside"
     q_dip = lambda t: 0.0 if t < 900 or t >= 6600 or 3000 <= t < 3040 else 50.0 + 0.01 * t
-    assert C.burst_table(_synthetic_run(cfg, q_dip, cold))["outcome"] == "emptied_in_watch"
+    assert C.burst_table(grow(_synthetic_run(cfg, q_dip, cold)))["outcome"] == "emptied_in_watch"
     q_full = lambda t: 0.0 if t < 900 else 50.0
     always = lambda t: 0.84 if t < 900 else 0.0
-    assert C.burst_table(_synthetic_run(cfg, q_full, always))["outcome"] == "drop_inconclusive"
+    assert C.burst_table(grow(_synthetic_run(cfg, q_full, always)))["outcome"] == "drop_inconclusive"
+
+
+def _with_backlog(run, a, we, c_watch, c_drop):
+    """The synthetic run's session requests served first come first served from `a`: at c_watch per second up to `we`,
+    then at c_drop until the line is gone, then at once (1.2 s). The total line (`gate.owed_backlog`) grows in the
+    watch when c_watch is below the 1 req/s planned rate; the waiting gauge (q_fn) is left as it is."""
+    r = run["requests"].copy()
+    tp, te, free = r.t_planned.to_numpy(float), r.t_end.to_numpy(float).copy(), a
+    for i in np.flatnonzero(tp >= a):
+        c = c_watch if max(free, tp[i]) < we else c_drop
+        free = max(free, tp[i]) + 1.0 / c
+        te[i] = free if free > tp[i] + 1.2 else tp[i] + 1.2
+    r["t_end"] = te
+    return {**run, "requests": r}
+
+
+def test_burst_table_rules_of_rule_f_round_1(monkeypatch):
+    """RE1: a `stuck` verdict on a line that is not growing (completions keep up with the planned rate) is
+    `stuck_not_cold`. RE2: a line that empties 20 s before the watch's end and stays empty into the drop emptied in the
+    watch. RE3: a 40 s zero of the waiting gauge early in the drop while the total line is still owed is not the drain
+    K3 measures."""
+    cfg = C.burst_cfg(15, 5400.0)
+    monkeypatch.setitem(C.REG24, "seed", 15)
+    monkeypatch.setitem(C.REG24, "drop_s", 5400.0)
+    monkeypatch.setattr(C, "inputs", lambda seed, drop: {"empty_s": {"tokens": 900.0, "tokens_optimistic": 700.0,
+                                                                     "tokens_pessimistic": 1500.0}})
+    cold = lambda t: 0.84 if t < 900 or t >= 6600 else 0.0
+    q_ok = lambda t: 0.0 if t < 900 or t >= 6600 else 50.0 + 0.01 * t
+    flat = C.burst_table(_synthetic_run(cfg, q_ok, cold))              # 1 completion per second against 1 planned
+    assert flat["v5"] == "stuck" and flat["cold_side"]["holds"] is False and flat["outcome"] == "stuck_not_cold"
+    grow = lambda r: _with_backlog(r, 900.0, 5580.0, 0.9, 1.0 + 468.0 / 1020.0)
+    q_edge = lambda t: 0.0 if t < 900 or 5560 <= t < 5700 or t >= 6600 else 50.0 + 0.01 * t
+    edge = C.burst_table(grow(_synthetic_run(cfg, q_edge, cold)))
+    assert edge["v5"] == "stuck" and edge["emptyings_watch"] == [5560.0] and edge["outcome"] == "emptied_in_watch"
+    q_flick = lambda t: 0.0 if t < 900 or 5800 <= t < 5840 or t >= 6600 else 50.0 + 0.01 * t
+    fl = C.burst_table(grow(_synthetic_run(cfg, q_flick, cold)))
+    assert fl["outcome"] == "confirms" and fl["first_empty_drop_s"] == 220.0
+    assert abs(fl["drained_drop_s"] - 1020.0) <= 20.0 and fl["k3"]["measured_s"] == fl["drained_drop_s"]
+    assert fl["k3"]["label"] == "inside" and fl["k3"]["label_first_empty"] == "outside_early"
+    # a 40 s zero of the gauge in the drop while the total line never drains there (completions only keep up with the
+    # planned rate), and a warm return: the draft's rule gave `confirms`; (g) now also needs the drain
+    stay = lambda r: _with_backlog(r, 900.0, 5580.0, 0.9, 1.0)
+    q_no = lambda t: 0.0 if t < 900 or 5800 <= t < 5840 or t >= 10980 else 50.0
+    cold_no = lambda t: 0.84 if t < 900 or t >= 10980 else 0.0
+    nd = C.burst_table(stay(_synthetic_run(cfg, q_no, cold_no)))
+    assert nd["emptyings_drop"] == [5800.0] and math.isnan(nd["drained_drop_s"]) and nd["return_recovered"] is True
+    assert nd["outcome"] == "drop_inconclusive"
+
+
+def test_owed_series_is_gate_owed_backlog():
+    cfg = C.burst_cfg(15, 5400.0)
+    run = _with_backlog(_synthetic_run(cfg, lambda t: 0.0, lambda t: 0.84), 900.0, 5580.0, 0.9, 1.4)
+    grid = np.array([0.0, 899.0, 1000.0, 3000.5, 5580.0, 6000.0, 7000.0, 12479.0])
+    assert list(C.owed_series(run, grid)) == [G.owed_backlog(run, t) for t in grid]
+
+
+def test_table_refuses_a_pair_from_two_builds(monkeypatch):
+    import analysis.load as L
+    runs = {"control": {"env": {"git_commit": "a" * 40}}, "burst": {"env": {"git_commit": "b" * 40}}}
+    monkeypatch.setattr(C, "_one", lambda kind: runs[kind])
+    monkeypatch.setattr(L, "find_runs", lambda pat: [runs["burst"]])
+    monkeypatch.setattr(C, "control_table", lambda run: {"outcome": "control_warm"})
+    monkeypatch.setattr(C, "burst_table", lambda run, ctl: {"outcome": "confirms"})
+    monkeypatch.setattr(G, "reg19_baseline_pair", lambda c, b: {})
+    assert C.table()["outcome"] == "not_same_build"
+    runs["burst"]["env"]["git_commit"] = "a" * 40
+    assert C.table()["outcome"] == "confirms"
+
+
+def test_tilt_scan_on_the_pick_and_seed_61():
+    """RE9 readout: the pick's end window carries 0.165 req/s more planned load than its return's end (the bound
+    under W is 0.2); seed 61's two W-passing rows carry less."""
+    d = C.tilt_scan(seeds=(43, 61))
+    assert d["n_windows_ok"] == 3 and round(d["pick_tilt"], 3) == 0.165 and d["n_larger"] == 0
+    assert round(d["max_possible"], 3) == 0.2
 
 
 def test_control_table_on_synthetic_runs(monkeypatch):
diff --git a/tests/test_withheld.py b/tests/test_withheld.py
index 17395f9..30e9c85 100644
--- a/tests/test_withheld.py
+++ b/tests/test_withheld.py
@@ -123,3 +123,10 @@ def test_e1_seal_lifts_alone(no_result):
     no_result.write_text("## 2026-11-15 · [RESULT] E1: floor 1.75\n")
     assert W.sealed_by("20261114-000000_sweep_l1pl350cl_pc_off_r2") is None
     assert W.sealed_by("20261115-000000_sweep_l1t16pl350cl_pc_off_r2") == "E0"
+
+
+def test_reg24_seal_covers_exactly_its_two_configs(no_result):
+    sealed = sorted(c.stem for c in CONFIGS.glob("*.yaml") if W.sealed_by(f"20261115-000000_{c.stem}") == "REG-24")
+    assert sealed == ["confirm_l1pl350cl_r2.0_s43", "stage2_control_l1pl350cl_r2.0_long_s43"]
+    assert W.sealed_by("20261110-085730_confirm_l1pl350cl_r2.2_s12") is None              # REG-15's run
+    assert W.sealed_by("20261115-000000_confirm_l1pl350cl_r2.0_s143") is None
```
