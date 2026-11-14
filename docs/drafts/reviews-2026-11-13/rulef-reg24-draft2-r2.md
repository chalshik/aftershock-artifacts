# Rule F review: REG-24 draft 2 (C1's confirmation at λ = 2.0, seed 43), round 2

Reviewer: an independent rule F pass (CLAUDE.md F; docs/process.md §3), 2026-11-14. Read-only on the repository: nothing edited, staged or committed; no GPU, VM, ssh or network; nothing under `runs/` opened or listed; no `analysis/` function run on a run folder; no sealed pattern touched.

## 0. What this review saw, and what it ran

- **Under review, at HEAD `872bc18`** (all `SHA256SUMS.txt` lines `OK`, PROBE: `shasum -a 256 -c docs/drafts/reg24_r2/SHA256SUMS.txt`):
  - `docs/drafts/reg24_confirm_draft2.md`, sha256 `de0a1cee11dd1df894df5aa3b78455a191a88e27f69c194bd2dc2f31083714f4`;
  - its item map (`5bd585e5…`);
  - `reg24.patch` (`be8f5746…`) and `withheld.patch` (`a020a335…`);
  - `frozen/` (`confirm_frozen.py` `6801457c…`, the freeze record, the rule's output, `compare_frozen.py`, `frozen_to_draft2.diff`).
- **Read for context:**
  - round 1 (`rulef-reg24-draft1-r1.md` and its patch);
  - PROTOCOL.md §3 (lines 25–43), §4 and §6's heading (line 87);
  - `docs/claims.md` C1 (lines 1–30) and K4 (lines 71–76);
  - `docs/definitions.md` (the ⚠ convention, lines 6–7, and the "trigger end (two copies of one rule)" precedent, line 68);
  - `docs/process.md` §1–§3;
  - `agent/DECISION_TREE.md` and `agent/FOR_AUTHOR.md` −13 to −20.
- **`docs/decisions.md` at `b46c279`, at these lines:**
  - REG-15's [RESULT] heading and both [CORR]s (3085, 3128–3137);
  - REG-16's design and calibration (3151–3167), its [RESULT] (3369–3410) and the 2026-11-10 [CORR] (3417–3427);
  - REG-18's and REG-19's outcome branches (3596, 3795–3807);
  - REG-19's [RESULT] (16517–16566);
  - E1's [REG] (17020, 17031, 17056, 17072, 17076, 17083) and its approval (18286, 18433).
- **Code read:**
  - `analysis/gate.py`: `owed_backlog`, `completion_rate`, `planned_session_rate`, `recovered_against`, `watch_broken`, `cold_windows`, `cold_persistent`, `reg16_control_outcome`, `reg17_outcome`, `reg18_seed_outcome`, `surge_run`, `reg19_cold_side`, `reg19_emptyings`;
  - `analysis/load.py`: `_level`, `verdict`, `find_runs`;
  - `harness/loadgen.py` `session_chain`, and the whole `git diff a7bb77a 872bc18 -- harness/`.
- **A disclosure on process.md §3.** That section gives this pass "only the registration text and the code diff", and no "results". As the brief asked, this round read REG-15's, REG-16's and REG-19's [RESULT]s, which round 1 did not. They are other registrations' results. REG-24 has no data, so nothing read here can bias its verdict. The owner may still count it as a departure.
- **Ran, on scratch exports of `872bc18`** (`git archive | tar -x`, then the patches with `git apply`; the repo's `.venv` python; the export as cwd; `runs/` holds only `.gitkeep`):
  - Both patches: `tests/test_confirm.py tests/test_withheld.py` gave **71 passed**, as the draft states.
  - `compare_frozen.py`, frozen file against draft 2's `confirm.py`: the output is line-identical to the writer's `compare_20261114T033233Z.txt` (PROBE: `diff`).
  - `confirm.seed_rule()` on the export, **with no monkeypatch**, picks `{'seed': 43, 'drop_s': 9000.0}` after 16 rows. No config sets a seed ≥ 20 except REG-24's own two, which are left out (PROBE: stdout).
  - `git log --since='2026-11-13 20:00'` on `analysis/gate.py`, `harness/workload.py`, the two parent configs, `l1_base.yaml`, `base.yaml` and `defaults.yaml`: empty. The rule's dependencies have not changed since before the freeze (PROBE).
  - `git diff --diff-filter=MDR a7bb77a 872bc18 -- configs/` is empty, and `pyproject.toml`, `uv.lock` and `.python-version` are unchanged (PROBE).
  - A schedule-only sketch of the total line (§1, T-C): `rev2_scripts/owed_sketch.py`.
  - A synthetic trace on draft 2's own `burst_table` (§1, T-A): `rev2_scripts/trace_late_rewarm.py`.
  - These two are one-off scripts in this review's scratch folder, so they are **not provenance under rule I**. The trace is also turned into a test in the reviewer patch.
  - **The reviewer patch** `rulef-reg24-draft2-r2.patch` (§5, appendix), on a fresh export with both of the draft's patches: `tests/test_confirm.py tests/test_withheld.py` **74 passed**, and `tests/test_gate.py -k "reg15 or reg16 or reg19"` 39 passed.
  - The full suite with all three patches, `--ignore=tests/test_check_docs.py`: 583 passed, 1 skipped (§7).
- **Not run:** `reg24_tilt` over the 160 candidate seeds (the brief). §4.1 says what it would show and why.
- **HEAD moved during the review.** It is now `25ad86e`. The two commits since `872bc18` (`d0d6b5c`, `25ad86e`) change only `agent/FOR_AUTHOR.md` item −20 among the files reviewed here (PROBE: `git diff --stat 872bc18 HEAD`). Item −18 and every file above are unchanged.

## Summary

Draft 2 applies RE1–RE9 faithfully, and its code matches its text in all but two places (DK2, DK-O1). The seed rule is byte-identical to the frozen file, and the pick reproduces on today's tree. Seven things still need fixing:

- **T-A, a false `confirms` on draft 2's code.** RE1's whole-window cold side averages over 3900 s. A partial re-warm at λ = 2.0 that begins about 1200–1800 s before the drop leaves `load.verdict` `stuck`: the closed-loop gauge falls too slowly for its 3600 s horizon, and the hit does not climb between its two windows. The whole-window average still holds, although the total line is shrinking at a rate that would empty it within that horizon. **DK1** closes it with the same test on the verdict's end window. That costs a truly cold server nothing.
- **The drop's ruling is not gated mechanically** (DK3). The proposed `DROP_PAT` accepts any owner ruling on the drop, an 1800 s one included. The [REG] may also land before the ruling, although an 1800 s ruling would void it, and decisions.md is append-only.
- **A decision REG-24 can change is missing** (DK4). REG-24's control is built to have no 120 s surge ≥ 3.2. If it tips, that is the event REG-17, REG-18 and REG-19 each registered as `surge_reading_wrong`, and it is K4's refuting case. The draft says that "in no case" does REG-24 change any other decision.
- **The owner's question still carries draft 1's error** (DK5). `agent/FOR_AUTHOR.md` −18 says "about 1 GPU h cheaper". The figure is ≈ 2 h, and the question also lacks option (b)'s main facts.
- **The harness section is incomplete** (DK6). It names the REG-19 comparisons only partly, says "Alternatives 1 and 2 … say so" (alternative 2 does not), and leaves out that the drain models and K3's band cross older harnesses.
- **Rule I** (DK7). The `confirms` sentence may cite a one-off script's count.
- **A promised readout is missing** (DK2). The `drop_inconclusive` reading promises the total line at the drop's end, which the code does not compute.

Verdict: **NOT READY** (§8).

## 1. Traces on which the verdict is wrong

### T-A (decisive, false `confirms`): a partial re-warm late in the watch

- **The mechanism** (DERIVED from FILE(harness/loadgen.py:139-165)):
  - Under closed-loop turns, each session has at most one turn released and not completed. So the waiting gauge plus the running gauge equals the number of sessions in service, not the total line.
  - When completions c exceed the planned rate λp, the total line falls at c − λp. Sessions finish faster than they start, so the gauge falls only at about (c − λp) / 8, with 8 turns per session (BELIEF as a model).
  - `load.verdict`'s drain sign reads the gauge, `q / −q_slope ≤ 3600 s` (FILE(analysis/load.py:239)). With q ≈ 200 waiting and a total line ≈ 1000, a total line that would empty in about 2250 s at λ reads as ≈ 3600 s on the gauge, so the sign stays off (DERIVED: 200 × 8 / 1000 = 1.6, and 3600 / 1.6 = 2250).
  - RE1's cold side averages completions over [1680, 5580). If the server was cold (c ≈ 1.75, REG-19's band) until about 4200 s, the average stays below λ = 2.0 even when the last 1200–1400 s ran above λp. For example, (1.75 × 2700 + 2.35 × 1200) / 3900 = 1.935 < 2.0 (DERIVED).
  - Hit does not climb between the verdict's windows if the re-warm began before the previous window (4380–4980). pf by `t_planned` stays near 0 in both windows, because the requests sit behind a queue of ≈ 200.
- **On draft 2's code** (synthetic run at draft 2's test scale: one planned session request per second, λp 1.0). The run is cold (hit 0, c 0.85) from the burst to 4380 s. It is then partly warm (hit 0.72 against a 0.84 baseline, so still ≤ base − 0.06; c 1.15) to the watch's end, with the gauge falling at −0.033/s. The drop drains it and the return is warm (`rev2_scripts/trace_late_rewarm.py`, run against the export with only the draft's two patches):
  ```
  verdict stuck | end hit 0.72 prev hit 0.72 end pf 0.00 prev pf 0.00 q 170.3 q_slope -0.0330 -> q/-slope 5161 s
  cold side over [1680, 5580): c 0.942 lam_p 1.000 holds True
  cold side over the last 1200 s: c 1.150 holds False; over the end window [4980, 5580): c 1.150 holds False
  total line: trigger 1, re-warm start 523, watch end 343; shrink rate 0.150/s; empty at that rate in 2280 s
  watch broken False emptyings watch [] drop first [6440.0] drained_drop_s 860.0 return True
  OUTCOME confirms
  ```
- **How wide the hole is** (same script, re-warm start varied):
  - 3600 s gives `stuck_not_cold`: RE1 catches it, with whole-window c 1.002.
  - **3800, 4000, 4200 and 4380 s give `confirms`.**
  - 4500, 4700 and 4800 s give `not_persistent`: the verdict's hit climb catches them.
- **Why the label is wrong.** The total line was shrinking over the watch's last 1200 s, fast enough to empty within the 3600 s horizon that PROTOCOL's `slow_drain` uses for "a queue that would empty". The server had begun to leave the cold state at λ = 2.0 before the drop. So condition 5 rests on the gauge's slow fall, and condition 6's reading ("the exit needed the lower load") is not shown. This is round 1's T1, moved to the end of the watch, where the whole-window average dilutes it.
- **How likely it is: BELIEF, low.** Under alternative 8, the backlog's working set (≈ 209 sessions × 3000 tokens against a 96,656-token pool) makes a partial re-warm at λ = 2.0 unlikely. But the rule should not depend on it, and the fix is free.
- **The fix, DK1.** REG-19's own test (completions below min(λ, λp)) over the verdict's end window [4980, 5580) as well. Seed 43's end window is planned at λp 2.068, so the test is c < 2.0 there (DERIVED: min(2.0, 2.068)).
  - A cold server completes at most its all-miss rate. All 40 of REG-19's 300 s spans had c 1.703–1.800 (FILE(docs/decisions.md:16539)), so a cold server's end window falls ≥ 120 completions short of failing (DERIVED: (2.0 − 1.800) × 600). The test costs no power against the hypothesis it protects.
  - There is no new number: the window is the verdict's, and the test is REG-19's.
  - With the patch, T-A at 4380 s gives `stuck_not_cold`, and a run cold to the watch's end still gives `confirms` (`test_end_window_cold_side_catches_a_late_rewarm`).

### T-B (A1, a decision the draft says REG-24 cannot change): the no-burst control tips without a surge

- **Numbers.** The control's highest 120 s planned rate anywhere is 2.733 (DERIVED, `confirm.inputs`, the draft's table). E guarantees it is below `surge_tip` 3.2.
- **Trace.** Suppose the control goes cold at, say, 3900 s and stays cold to 5580 s. Then `control_outcome` gives `control_cold_persistent`, and `control_table`'s `surge` readout (`gate.surge_run`) gives `tipped` True with `peak_tip` < 3.2.
- **That event has a registered meaning in this study:**
  - REG-17, REG-18 and REG-19 each read it as `control_cold_no_surge` → `surge_reading_wrong`: "stop; rethink before anything else is drafted" (FILE(docs/decisions.md:3596), FILE(docs/decisions.md:3807), `gate.reg17_outcome` FILE(analysis/gate.py:1509-1511)).
  - The decision tree says "Write a [CORR] on the surge readout before anything else is drafted" (FILE(agent/DECISION_TREE.md:18)).
  - K4 lists "tips without a surge" as refuting (FILE(docs/claims.md:76)).
- **What the draft does with it.** Its `control_not_warm` sentence reads it only as "λ = 2.0 … not reliably warm over 4.5 h". Its "What it does not change" and "In no case does REG-24 start, stop or size another run" contradict the study's standing branch. D1's draft also leans on REG-19's control peaks staying warm below 3.2 (FILE(docs/drafts/d1_draft2.md:64)).
- **This is not a false label but a false A1 statement. DK4.**

### T-C (the drain level checked; no false `drop_inconclusive` from it; a missing readout)

- **What the drain test measures.** `drained_at` asks for the total line at or below its value at 900 s. That holds exactly when completions since 900 s ≥ requests planned since 900 s (DERIVED: owed(t) − owed(900) = planned[900, t) − completed[900, t)). This is the token model's event in request units.
  - It needs every completion to come after its own `t_planned`. That holds: `t_released ≥ t_planned` by `session_chain`'s release rule (FILE(harness/loadgen.py:148,160)), and `t_end > t_released`.
- **The worry.** A single instantaneous level at λ = 2.0 warm could sit below what a cold-but-caught-up server at λ = 1 holds. The drain would then never register, which would give a false `drop_inconclusive` on exactly the run where the cache stays cold without a backlog. The draft would mislabel the most interesting `no_return` / `cold_after_empty` case.
- **Checked on schedules only** (`rev2_scripts/owed_sketch.py`). A constant e2e latency e gives owed(t) = #{t_planned < t ≤ t_planned + (turn + 1)·e}.
  - At e = 2.5 s, REG-15's schedule gives owed(900) = 28, the published calibration (FILE(docs/decisions.md:3156)).
  - On seed 43 at e = 2.5 s, owed(900) = 22.
  - In the drop after the backlog clears (8000–14580 s), the line's minimum is 0, 1, 1, 3, 3, 5, 7 and 12 at e = 2.5, 3, 4, 5, 6, 7, 8 and 10 s. That is below 22 even at 4 × the warm latency (DERIVED, schedule only; BELIEF that e2e is near constant).
  - So the level is sound: closed-loop noise at λ = 1 carries the line below the trigger's level soon after the backlog is gone.
- **The gap that remains is a readout.**
  - Draft 2's `drop_inconclusive` sentence says "The owed backlog and `release_delay` at the drop's end show which part, server or clients, held".
  - `burst_table` computes the owed backlog only at the trigger, the watch's end, the first emptying and 600 s after it (FILE: draft 2 `analysis/confirm.py`, `out["owed"]`).
  - **DK2** adds the drop's end, and the line's lowest point in the drop with its time. With that, a `drop_inconclusive` whose line came within a few requests of the level can be told from one that never drained.

### T-D (an exception, not a label): no valid control

- `table()` calls `_one("control")`, which raises when no valid control exists (`gate.reg12_only`, FILE(analysis/gate.py:471-476)).
- The draft says that this case "gives `control_missing`" ("Missing runs"). `pair_outcome`'s `control_missing` branch is unreachable from `table()`.
- The same holds for the ops sketch: `final.sh` runs "only after `QUEUE DONE` or `QUEUE END control not warm`". So after `QUEUE END attempts spent` on the burst run, `burst_missing` and the control's table (a 16080 s no-surge control, K4 data) are never computed.
- **DK-O1** (code in the patch).

### Checked and found as stated

- **RE2's one pass:**
  - Emptyings are computed once over [1080, 14580) and split at 5580 s by start time.
  - The 5560 s edge gives `emptied_in_watch` (the draft's test).
  - `confirm.emptyings(run, burst end, end of arrivals)` equals `burst end + gate.reg19_emptyings(run)` element by element (`test_emptyings_are_reg19s_on_reg19s_window`, in the patch).
- **`owed_series` equals `gate.owed_backlog`** (the draft's test).
- **`not_same_build`:** decided before any label, and it overrides even the labels that stand whatever the control. That is conservative.
- **The configs:** `test_registered_configs_are_the_design_at_the_pick` passes, and only the five keys differ from REG-19's ten configs.

## 2. The strongest alternative explanation of a `confirms`

- **(A) Mechanistic, likeliest, not ruled out by REG-24: the cold state is held by the closed-loop clients' lagged backlog against the pool.**
  - At the watch's end the request model owes ≈ 1670 requests, so at least 209 sessions are in service (FILE: the draft, Design inputs).
  - Each lagged session's next turn arrives after its prefix was evicted.
  - The drop clears the state only because λ = 1 is below the cold rate (c_drop 1.672, FILE(docs/decisions.md:3156)).
  - Under this reading, `confirms` shows two states at one load for **vLLM plus closed-loop clients**: any server whose service rate falls once its queue fills the pool would show the same drop and return. It shows nothing about C2's chain, nor that the state exists with open-loop turns.
  - **What separates it:**
    - inside REG-24, as readouts: `release_delay` at the watch's end (expected ≈ owed / c ≈ 950 s, round 1's T4), turn-0 share, and condition 4's N against 256;
    - outside REG-24: REG-20 arm A (K1, open-loop turns).
  - The draft has this as alternative 8, and the `confirms` sentence ends "It does not test C2's chain". That is enough, provided the paper's sentence also keeps "with closed-loop turns", which the draft's Question has.
- **(B) External, and the one a same-schedule control cannot answer: a slowdown confined to the burst run's watch.**
  - Examples: a co-tenant on the shared GPU (PROTOCOL §4, FILE(PROTOCOL.md:53)), or a host event.
  - The control ran ≈ 4.6 h earlier.
  - No check fails a run for a foreign compute process during the run. The process list is taken at launch and at the end only (FILE(harness/run.py:214), FILE(harness/env_snapshot.py:44)), and `checks.py` has no process check (PROBE: `grep -n gpu_processes harness/*.py`).
  - **What separates it from the all-miss server:**
    - the watch's c, over W and over the end window (DK1), against REG-19's per-span band 1.703–1.800 (FILE(docs/decisions.md:16539));
    - the implied r against REG-21's per-run 1.020–1.029 (FILE(docs/decisions.md:16444), FILE(docs/decisions.md:16798));
    - the co-tenant readout's memory range in the watch.
  - A co-tenant lowers c below the all-miss band and r below 0.95. The all-miss server does not.
  - **DK-O5** asks that the [RESULT] set these numbers beside a `confirms`.

## 3. Can the run change any decision? (rule A1)

**Yes. Three decisions, one of which the draft leaves out.**

| outcome | what changes | P (a) 9000 s | P (b) 1800 s |
|---|---|---|---|
| `confirms` | **C1's status** in `docs/claims.md` (after the owner's review): conditions 3, 5 and 6 met at λ = 2.0 in one seed. It cannot read "all six" while condition 4's order clause is unjudged (FILE(agent/FOR_AUTHOR.md:18), item −13). Also the paper's P0 sentence, and K3's point | ≈ 0.50 | ≈ 0.03 |
| `drop_inconclusive` | the paper's sentence only: persistence to 4500 s shown, condition 6 untested. C1's status does not change | ≈ 0.05 | ≈ 0.53 |
| `not_persistent`, `reformed`, `emptied_in_watch`, `stuck_not_cold` | the paper's sentence: "held 3000 s (REG-19), not 4500 s in the confirmation seed". C1's status does not change | ≈ 0.11 | ≈ 0.11 |
| `no_return` | the paper's sentence (condition 6 not met), read by `after_empty` | ≈ 0.06 | ≈ 0.02 |
| a control tip (`control_cold_*`, no 120 s peak ≥ 3.2 by E) | **the surge reading and K4** (T-B): REG-17–19's `surge_reading_wrong` branch and K4's refuting case. The draft omits this | ≈ 0.10 of the ≈ 0.15 `control_not_warm` (BELIEF) | ≈ 0.10 of the ≈ 0.19, but under (b) E never judged the schedule, so a tip may follow a surge and decide nothing |
| `control_warm` throughout | K4 gains 16080 s (or 8880 s) of no-surge warm time at λ = 2.0: exploratory data on the "stays warm" side | ≈ 0.85 | ≈ 0.80 |
| not tested (`bad_baseline`, `inconclusive`, missing runs, `not_same_build`, stops) | nothing | the remainder | the remainder |

- **The numbers.** P for the burst-run labels is the draft's conditional table times its ≈ 0.80 / 0.75 for reaching a burst label (BELIEF, the draft's; DERIVED products, rounded). The split of `control_not_warm` is this review's BELIEF: if the surge reading is right, a no-surge schedule should not tip. The draft's 0.15 rests on the run's length and the new harness, so most of it is a tip.
- **Which outcome changes C1's status:** only `confirms`, and only through the owner's review.
- **Under (b):** P(`confirms`) ≈ 0.03. The pair's ≈ 5.1 GPU h then buy mainly condition 5 at 4500 s, which (a) also gives at P ≈ 0.55 or more (DERIVED: 0.50 + 0.05).
- **Under (a):** ≈ 9.1 GPU h for the pair, ≈ 8.4 h expected and ≈ 27.3 h at most (DERIVED, the draft's Cost table, checked: 16195 + 16559 = 32754 s). It makes condition 6 decidable both ways. P(`no_return`) rises from ≈ 0.02 to ≈ 0.06 as P(`confirms`) rises, so choosing (a) is not choosing the outcome's direction.
- **Whether the hours are worth one replicated premise sentence, K3's point and K4's datum** is the owner's to weigh. This review does not object to (a). Under (b) the run is proposable only as a condition-5 test (DK-O6).

## 4. The six points the brief asked about

### 4.1 The seed and the frozen rule

- **Byte-identical: yes.**
  - All 26 rule keys of `REG24` and the functions `_resolved`, `burst_cfg`, `control_cfg`, `phases`, `judged_windows`, `_rate`, both models, `used_seeds`, `candidate_seeds`, `design_row`, `seed_rule` and `seed_scan` are `same` (PROBE: `compare_frozen.py`, frozen file against draft 2's `confirm.py`, identical to the writer's output).
  - `REG24`'s text differs only in `seed`/`drop_s` and their comment, which were `None` in the frozen file (FILE(docs/drafts/reg24_r2/frozen/confirm_frozen.py:63)).
  - The rule's dependencies outside the file (gate.py's `_burst_cfg`, `rolling_rate` and `SURGE`; `harness/workload.py`; the parent configs) have no commit since 2026-11-13 20:00 UTC+6, which is before the freeze (PROBE: `git log`).
  - The pick reproduces on `872bc18` without the test's monkeypatch (PROBE).
- **Nothing in draft 2 is a choice made after the scan: none found.**
  - (d2)'s window extends REG-19's W start (burst end + 600 s) to the watch's end. The drain level is the run's own value. The `stuck_not_cold` position is round 1's. `READOUT` judges nothing.
  - Under (b), the draft names keeping seed 43 as a post-scan choice that would be the owner's. That is correct.
- **`tilt_scan` on seeds 43 and 61 biases nothing.**
  - It reads schedules after a frozen pick, and the tilt enters no label. Seed 61 was chosen because round 1 named it (the drop-first pick), not because of its tilt. The test's `n_larger` 0 of 3 is correctly not presented as the 25-schedule number.
  - The look is not a bias but a provenance gap: the `confirms` sentence would cite "0 of 25" from round 1's one-off script (rule I; **DK7**).
- **What the full `reg24_tilt` would show:**
  - `n_windows_ok` 25: the same `design_row` W flags as `seed_scan`'s committed post-pick table, 7 + 6 + 5 + 7 (FILE(docs/drafts/reg24_confirm_draft2.md:247-250)).
  - `pick_tilt` +0.165 (the draft's test).
  - By round 1's script on the same rows, `n_larger` 0, median +0.003 and `n_positive` 13 (FILE(docs/drafts/reviews-2026-11-13/rulef-reg24-draft1-r1.md:100)).
  - Why it would match: `tilt_scan` is a pure function of `design_row`'s `lam_p`, which is byte-identical to the frozen code, and round 1 computed the same difference on the same rows. A mismatch would mean a bug in one of the two.
  - Running it costs minutes on the Mac and 0 GPU h, and can change no label.
- **One skeptic's note (DERIVED, with an exchangeability BELIEF).** If the tilt is unrelated to seed order, the first W-admitted schedule in seed order is the most tilted of 25 with P = 1/25 = 0.04.
  - That alone is not evidence of tuning: the tilt is one of many schedule properties.
  - But it is the property most favourable to `confirms`, and the freeze's timing is BELIEF. So the design must answer the tilt without relying on the freeze. It does: the same-schedule control, and the cold side, now also in the end window (DK1). This is why DK1 matters more on this seed than on a neutral one.

### 4.2 RE1–RE3's new conditions

- **Traces:**
  - T-A gives a false `confirms` through RE1's average (DK1).
  - T-C finds the drain level sound, with a readout missing (DK2).
  - A false `stuck_not_cold` exists, but only in the conservative direction. Seed 43's W is planned at λp 2.045 > λ, so the test is c < 2.0. A server at c ∈ [2.0, 2.045) still has a total line growing by up to 0.045 req/s, and is labelled `stuck_not_cold`, "the total line was not growing". That clause is then false: the test is REG-19's, and its wording should be (DK-O3).
- **The one emptying pass** is correct, and is shown equal to REG-19's code (above).
- **"Emptying" with two codes: not a real conflict.**
  - `confirm.emptyings` over [burst end, end of arrivals) is `gate.reg19_emptyings` shifted to absolute time (test in the patch).
  - REG-24 calls it once, over [1080, 14580) (draft 2 `burst_table`). In use, the only difference is that a zero whose 30 s hold would cross 14580 s is left out. That zero can decide (g) only if the line drained with no earlier 30 s zero in the drop.
  - **The verdict uses `confirm.emptyings`.** This is the "trigger end ⚠ (two copies of one rule)" case (FILE(docs/definitions.md:68)), and the entry can say so and cite the test (DK-O2).
- **(g)'s two parts are independent in time:** a gauge emptying anywhere in the drop and a drain anywhere in it. RE3 intended that, and it is sound. The flicker case of round 1's T3 now needs the drain too (the draft's test).
- **"The event both drain models predict"** is exact for the token model. The request model's event is the total line at 0 (`owed_at_trigger + planned − done ≤ 0`, draft 2 `empty_time_requests`). That is ≈ 40 s after the trigger-level crossing at λp 0.994 and c_drop 1.672 (DERIVED: 28 / (1.672 − 0.994) = 41 s). K3 uses only the token model, so this is wording (DK-O3).

### 4.3 The PROTOCOL departure

- **Stated in text: yes.** It appears in the Setup bullet "Owner approval needed, named separately", in "Not approved … the delegate cannot approve REG-24 until the owner has ruled on the drop", and in "What must exist", item 4.
- **Gated mechanically: no.** DK3 has the fixes. Four gaps:
  1. The sketched `DROP_PAT` matches any heading `[DECISION] (owner) REG-24: the drop…`, an owner ruling for (b) included. A delegate approval of the 9000 s [REG] after such a heading would pass the scripts' check.
  2. The required headings are ordered (i) [REG], (ii) ruling, (iii) approval, with (iii) after (i) and (ii). So (i) may be committed before (ii). Under a (b) or (c) ruling, the append-only [REG] would then describe a design never run, and would need a [CORR] and a new [REG].
  3. The PROTOCOL §6 row is "added in the same commit", which leaves it unclear which commit, and no script checks it.
  4. `agent/FOR_AUTHOR.md` −18, the text the owner rules on, is stale (DK5).

### 4.4 The missing frozen test file

- **What it does not weaken.** The pick depends on the rule's code, which is byte-identical and reproduces, and on dependencies the freeze record never hashed (gate.py, `build_schedule`, the configs, numpy's generator), which a test file would not have hashed either. The pick is therefore as checkable without the test file as with it.
- **What it weakens:**
  - only the claim that the tests were frozen with the rule, which the draft already marks BELIEF;
  - and with it, any reading of the pinned values in the tests as written before the scan. The draft treats them as regression guards, which needs no freeze.
- **What stays BELIEF in either case:** that no candidate schedule was read before 23:23:39 UTC. Mtimes in a scratchpad are not a witness. Draft 1's commit (`56820bd`, 2026-11-14 01:22 UTC, PROBE: `git log`) bounds only when the frozen hash existed, not the order of freeze and scan.
- **So the [REG] should cite the freeze for nothing beyond "the rule's code is byte-identical and reproduces"**, which draft 2 already does ("Timing"). No item.

### 4.5 The harness

- **The diff** (`git diff a7bb77a 872bc18 -- harness/`, PROBE, read in full):
  - With `workload.sessions.cap` unset, `session_chain`'s release, send and timing are unchanged. Only the flush of a `client_error` line moved, and a new `finally` releases a cap that is never held (FILE(harness/loadgen.py:138-178)).
  - The recorder's scrape grid is unchanged; it now survives a half-written line and a failed GPU read (FILE(harness/recorder.py)).
  - The `recorder` and `gpu_steady` checks add coverage tests (FILE(harness/checks.py:92-138)).
  - So the change bears on which runs are valid and on the recorder process, not on the arrival process (DERIVED, this review's reading of the diff).
- **Comparisons with REG-19 that cross it:**
  - c 1.703–1.800: alternatives 1 and 2, the `stuck_not_cold` row, and DK1's margin;
  - the total lines 444–811 / 1050–1511 and their ratio 1.94–2.51: alternative 2, the RE-O6 bullet, and the model-check table;
  - the controls' peaks 2.833–3.092 and their five no-tips: the `control_warm` prediction and the peaks table.
- **What the draft says:** it names c (alternative 1), the model-check table and the peaks table, plus "The harness is new" under P(`control_warm`). It says "Alternatives 1 and 2 use those numbers, and say so". Alternative 2 does not, and neither do the RE-O6 bullet or the `stuck_not_cold` row.
- **What it leaves out:** both drain models and K3's band cross older harnesses still:
  - REG-15's calibration (2026-11-10);
  - REG-8's U_off;
  - REG-21's r_expected, from batch 1 on the 13 closed-loop burst runs made before REG-19 (FILE(docs/decisions.md:9731));
  - and the surge readout's 21 runs (FILE(docs/decisions.md:3423)).
- **DK6.**

### 4.6 Rule A1

See §3. The draft's A1 section is right on C1 and K3, and wrong in "What it does not change … In no case", which T-B and DK4 correct. Under (b) the run is designed to be inconclusive on its main question: P(`drop_inconclusive` | reaches the drop stuck and cold) ≈ 0.92, the draft's figure. So (b) should be registered as what it can decide (DK-O6).

## 5. Required items

### DK1 (code and text; stricter rule): REG-19's cold side over the verdict's end window as well (T-A)

- **Code:** the reviewer patch. `burst_table` adds `cs_end = cold_side(run, *judged_windows(cfg)["end"])` and passes `cold` = False if either window is False, None if either is None (and neither False), else True. The result is reported as `cold_side_end`. Tested by `test_end_window_cold_side_catches_a_late_rewarm`.
- **Replace (d2) in "What `confirms` requires" with:**

  > - (d2) REG-19's whole-window cold side holds over [1680, 5580) s and over the verdict's end window [4980, 5580) s (`confirm.cold_side`): in each, completions (session and burst, by `t_end`) below min(λ, λp), with λp the planned session rate in that window (2.045 and 2.068 for seed 43, DERIVED, schedule only). The end window keeps a total line that shrinks over the watch's last windows, a partial re-warm at λ that the closed-loop waiting gauge shows only as a slow fall (rule F round 2, T-A), from being averaged away by the cold part of W. A cold server completes at most its all-miss rate: REG-19's 40 spans had c 1.703–1.800 (FILE(docs/decisions.md:16539)), at least 120 completions short of 2.0 over 600 s. If any rate is NaN, the label is `inconclusive`; if either window's rate is not below, `stuck_not_cold` (RE1).

- **Replace label 7's text with:**

  > 7. **`stuck_not_cold`** (RE1; rule F round 2, DK1): stuck, never recovered and never emptied in the watch, but completions over [1680, 5580) s or over the end window [4980, 5580) s were not below min(λ, λp). This is REG-19's `stuck_not_cold`: the `stuck` verdict may be a long drain. Condition 5 is not shown.

- **In "Every threshold, and its source", under "From REG-19":** "the whole-window cold side, from the burst's end + 600 s (`gate.REG19["window"][0]`), and the same test over `load.verdict`'s end window (no new number)".
- **In Alternatives 2, after the `stuck_not_cold` bullet:** "and, over the verdict's end window, a server that began to re-warm at λ before the drop (rule F round 2, T-A)".

### DK2 (code; reporting duty): the total line at the drop's end and its lowest point in the drop (T-C)

- **Code:** the reviewer patch adds `out["owed"]["drop_end"]`, `["min_drop"]` and `["t_min_drop_s"]` (from `owed_series` on the 10 s grid of the drop).
- **In "Readouts, never decisive", replace** "the owed backlog at the trigger, at the watch's end, at the first emptying in the drop and 600 s after it" **with:**

  > the owed backlog at the trigger, at the watch's end, at the first emptying in the drop and 600 s after it, at the drop's end, and its lowest value in the drop with the time it was reached (rule F round 2, DK2)

- **Append to the `drop_inconclusive` (a) sentence:**

  > The report gives the total line's lowest value in the drop, and when it was reached, against its level at the trigger.

### DK3 (wording, and the ops scripts' patterns): the drop's ruling gated mechanically, before the [REG]

- **Replace "What must exist before approval", item 4 with:**

  > 4. **The owner's ruling on the drop,** committed in `docs/decisions.md` **before** `[REG] REG-24`. The one exception: the owner approves REG-24 directly, and the [REG] and that approval are committed together. Its heading names the drop: `## <date> · [DECISION] (owner) REG-24: the drop is 9000 s …` or `## <date> · [DECISION] (owner) REG-24 approved … 9000 s …`. Under (a), PROTOCOL §6 holds the row in Setup at the approval's commit. Under any other ruling, this draft is redrafted and reviewed again, and no [REG] of it is committed.

- **In "Order", the required headings of REG-24** become, in this order: (i) the drop's ruling (`DROP_PAT`), (ii) `## <date> · [REG] REG-24` (`REG_PAT`), (iii) `## <date> · [DECISION] (owner|delegate) REG-24 approved` (`APPROVE_PAT`). (i) and (iii) may be one heading, and (ii) and (iii) one commit.
- **In the ops sketch's `common.sh` bullet, add:**

  > `DROP_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[DECISION\] \(owner\) REG-24([^0-9]|$).*9000 s'` and `PROTOCOL_ROW="| Condition 6's drop at λ = 2.0 (REG-24) lasts 9000 s, not 1800 s |"`. `mac_checks` refuses unless `git grep -nE "$DROP_PAT"` at the registered commit matches in `docs/decisions.md` at a line no later than `REG_PAT`'s, or on the approval heading itself, and unless `git show <registered commit>:PROTOCOL.md | grep -F "$PROTOCOL_ROW"` matches.

### DK4 (A1; wording): a tip of the no-surge control bears on the surge reading and on K4 (T-B)

- **Add to "What it can change", after K3's bullet:**

  > - **the surge reading and K4** (FILE(docs/claims.md:71-76)). The control's schedule has no 120 s planned peak ≥ 3.2 anywhere (E; its highest is 2.733). A tip of the control (`control_cold_persistent` or `control_cold_transient`, with `control_table`'s `surge` readout `tipped` True) is the event REG-17, REG-18 and REG-19 each registered as `control_cold_no_surge` → `surge_reading_wrong`: "stop; rethink before anything else is drafted" (FILE(docs/decisions.md:3596), FILE(docs/decisions.md:3807), FILE(agent/DECISION_TREE.md:18)). It is also K4's refuting case ("tips without a surge"). A warm control adds 16080 s of no-surge warm time at λ = 2.0, exploratory K4 data.

- **Replace the `control_not_warm` sentence with:**

  > - **`control_not_warm`:** "On seed 43's 16080 s schedule the no-burst control did not stay warm ([outcome]). The confirmation is void at this cell, and λ = 2.0 is reported as not reliably warm over 4.5 h, as REG-16 reported 2.2." If the control tipped (`surge.tipped` True), the sentence adds: "with no 120 s planned surge above 3.2 req/s in its schedule (its highest 2.733), so the surge reading of the earlier collapses does not hold here (K4's refuting case)". The agent then drafts a [CORR] on the surge readout for the owner before any registration whose design rests on `surge_tip` or on λ = 2.0 controls staying warm below it is approved (D1/D2 included, FILE(docs/drafts/d1_draft2.md:64)). This follows REG-17–19's branch; the owner may overrule it by an entry.

- **Replace "In no case does REG-24 start, stop or size another run" with:**

  > REG-24 starts, stops or sizes no run by itself. Its one effect on other work is the surge-reading [CORR] above, after a tip of the control.

- **In "What it does not change", D1 and D2:** add "(except as above, after a tip of the control)".
- **In the Prediction:** split `control_not_warm` ≈ 0.15 into "a tip of the control ≈ 0.10" and "other non-warm outcomes ≈ 0.05" (BELIEF, the writer may set the split).

### DK5 (wording; rule A6): the owner's question corrected before the owner rules

- `agent/FOR_AUTHOR.md` −18 still says draft 1 is "not reviewed yet" and that seed 61 at 5400 s is "about 1 GPU h cheaper" (FILE(agent/FOR_AUTHOR.md:11)). Draft 2's W2 corrects the figure to ≈ 2 h, but only in the item map. Below is the text that replaces item −18 (or a new top item that supersedes it, as the file's convention prefers), committed before the owner is asked again:

  > **C1's confirmation at λ = 2.0 (REG-24) needs one decision of yours before any approval: the drop length.** Draft 2 (`docs/drafts/reg24_confirm_draft2.md`; rule F round 1 NOT READY on draft 1; round 2 on draft 2: [its verdict]) keeps seed 43 with a 9000 s drop, picked by a rule frozen before its scan, and design B (a no-burst control on the same schedule, then the burst run). PROTOCOL §3 item 6 says 1800 s (FILE(PROTOCOL.md:38)); REG-15's 1800 s drop at 2.2 did not empty the line (`drop_inconclusive`). A PROTOCOL change is yours alone, so no delegate approval is possible before you rule. **Yours:**
  > - **(a) 9000 s on seed 43:** ≈ 9.1 GPU h for the pair (≈ 8.4 h expected, at most ≈ 27.3 h). P(`confirms`) ≈ 0.50 and P(`drop_inconclusive`) ≈ 0.05 (BELIEF, the draft). You add the PROTOCOL §6 row in draft 2's Setup.
  > - **(b) 1800 s:** ≈ 5.1 h for the pair. The frozen rule never judged seed 43 at 1800 s (its windows and peaks are unknown), so keeping seed 43 is a choice made after the scan, and yours. Both drain models put the drain at 2130–4080 s into the drop, so P(`drop_inconclusive`) ≈ 0.53 and P(`confirms`) ≈ 0.03 (BELIEF): condition 6 is very likely untested, and K3's point is lost.
  > - **(c) something else.** For example, the drop-first pick, seed 61 at 5400 s: ≈ 7.1 h for the pair, ≈ 2.0 h less than (a) (DERIVED: 2 × (12480 s of arrivals) + 115 + 479 s, against 9.10 h; draft 1 wrote "about 1 GPU h", an arithmetic error that draft 2 corrects, W2). It is also a choice made after the scan, and it needs its own design rows and review.
  >
  > Under (b) or (c), the draft is redrafted and reviewed again before its [REG].

### DK6 (wording; rule B): the harness section names every comparison that crosses a harness change

- **Replace "What follows", second bullet ("Across registrations, a confound…") with:**

  > - **Across registrations.** With `workload.sessions.cap` unset, the closed-loop request path of `5ee6e38`'s load generator is unchanged, except that a `client_error` line is flushed as it is written. The recorder's scrape grid is unchanged; it now survives a half-written line. The `recorder` and `gpu_steady` checks are stricter (DERIVED from `git diff a7bb77a <registered commit> -- harness/`; FILE(harness/loadgen.py:138-178)). So the change bears first on which runs are valid and on the recorder process, not on the arrivals. Comparisons that cross it, named where they are used:
  >   - REG-19's c 1.703–1.800: alternatives 1 and 2, the `stuck_not_cold` row, and (d2)'s margin;
  >   - its total lines 444–811 and 1050–1511, and their ratio 1.94–2.51: alternative 2, "The planned dips", and the model check;
  >   - its controls' peaks 2.833–3.092 and their five no-tips: the `control_warm` prediction and the peaks table.
  >
  >   Comparisons that also cross older harnesses: both drain models and K3's band (REG-15's calibration of 2026-11-10; REG-8's U_off; REG-21's r_expected from batch 1, on the 13 closed-loop runs made before REG-19), and the surge readout's 21 runs (FILE(docs/decisions.md:3423)). K3's point is a model calibrated on those harnesses against a measurement on this one, and the figure says so.

- **Add "(under REG-19's harness)"** after the REG-19 numbers in alternative 2, in "The planned dips do not reach the server directly", and in the `stuck_not_cold` prediction row.

### DK7 (rule I): the tilt rank from committed code, or not at all

- **Replace the bracket in the `confirms` sentence and open point 5 with:**

  > [the largest such difference among the [`n_windows_ok`] schedules that the seed rule's window test admitted (`reg24_tilt`, `n_larger` 0)]. The clause is printed only if `uv run python -m analysis.confirm reg24_tilt` was run once before the [REG] (schedules only, 0 GPU h; its output saved and named in the [REG]) and gives `n_larger` 0. Otherwise the sentence keeps both windows' λp and "the window judged `stuck` carried 8.7 % more planned load", and cites no count. Round 1's one-off count is not quoted in any doc (rule I, `docs/process.md` §1).

## 6. Optional items

- **DK-O1 (code; ops): `control_missing` and `burst_missing` reachable.**
  - In the patch, `table()` returns `control_missing` when no valid control exists, instead of raising (`test_table_gives_control_missing_without_a_valid_control`).
  - In the ops sketch, `final.sh` also runs after `QUEUE END attempts spent`, whenever the control has a valid run, so that `burst_missing` and the control's table (K4 data) are computed. "Missing runs" then reads as the code does.
- **DK-O2 (definitions text, rule J): the emptying entry.**

  > **emptying ⚠ two copies of one rule:** "0 waiting at a scrape and for the next 30 s, the 30 s inside the window; a new emptying counts only after the line refilled." Code: `gate.reg19_emptyings` (relative to the burst's end, over [burst end, end of arrivals)) and `confirm.emptyings(run, a, b)` (absolute, over [a, b)). On REG-19's window they are equal (`test_emptyings_are_reg19s_on_reg19s_window`). REG-24 uses [1080, 14580), which leaves out a zero whose hold would cross into the return.

- **DK-O3 (wording):**
  - In label 7 and the code's docstring, "the total line was not growing" becomes "completions were not below min(λ, λp) (REG-19's test; with λp above λ, as in seed 43's W, the line can still grow by up to λp − λ)".
  - In "The total line and the drain", "the event both drain models predict" becomes "the token model's event exactly (in requests); the request model's event, the total line at 0, comes ≈ 40 s later at seed 43's drop rates (DERIVED: 28 / (1.672 − 0.994))".
- **DK-O4 (order rule; for the ops round).**
  - "E1's end entry … is not one of REG-24's own required headings" departs from E1's definition ("an item's required headings are those its scripts need before their first launch", FILE(docs/decisions.md:17076)). Name it as a departure, with its reason, and ask that REG-20 arm A's and D1's ops decisions read the rule the same way. Otherwise two items can each read themselves first.
  - REG-24's `vm_checkout.sh` refuses unless the end heading of every item that the rule puts first is in the committed log, by pattern, not by hand: E1's three, REG-20's [RESULT] or its `QUEUE DONE` [OPS]. Otherwise it could move the VM forward under another item's hold.
- **DK-O5 (reporting duty, alternative (B)).** Beside any `confirms`, the [RESULT] gives:
  - c over W and over the end window, against REG-19's per-span band;
  - the implied r against REG-21's per-run 1.020–1.029;
  - the co-tenant readout's memory range in the watch.

  If the memory range in the watch exceeds what one CUDA context takes, or the end-of-run process list shows a process other than the server's, the `confirms` sentence names it. No label changes on it.
- **DK-O6 (A1 under (b)).** If the owner rules (b), the redrafted [REG] is titled and argued as a condition-5 test (persistence through 4500 s, with the same-schedule control), with condition 6 a readout that is expected to be inconclusive. Rule A1 then weighs ≈ 5.1 GPU h against that question, not against C1's status.

## 7. Checks done

- **The draft's patches:**
  - The sha256 values match.
  - Both apply to an export of `872bc18`.
  - 71 passed (`test_confirm.py`, `test_withheld.py`), as stated.
  - The frozen comparison is reproduced, and the pick reproduces without a monkeypatch.
  - Configs and lock are unchanged since `a7bb77a`, and the rule's dependencies have no commit since before the freeze.
- **The reviewer patch** (sha256 below; 2 files, `analysis/confirm.py` and `tests/test_confirm.py`, 106 lines in and 6 out):
  - It applies cleanly on top of both of the draft's patches on a fresh export of `872bc18`.
  - 74 passed there: the draft's 71 plus three new tests.
  - `tests/test_gate.py -k "reg15 or reg16 or reg19"`: 39 passed.
- **The full suite** with all three patches, `--ignore=tests/test_check_docs.py`: **583 passed, 1 skipped**, rc 0, in 657 s. That is the writer's 580 passed and 1 skipped, plus the three new tests (PROBE: `pytest_full_r2rev.txt` beside this file). `test_check_docs.py` was left out because it checks the repository's docs, not the export.
- **The draft's claims checked and found as stated:**
  - the five-key difference;
  - phases and judged windows;
  - the seed rule's 16 rows;
  - the factor-two arithmetic (4859 s);
  - the (b) section's ranges (3270–3550 s and 3760–4080 s);
  - the Cost table (16195 + 16559 s; 8995 + 9359 s);
  - the prediction tables' sums (1.00 under each option) and products;
  - the 26 unchanged `REG24` keys;
  - REG-16's drop drain from a queue of 113 to 0.000 by 6600–6900 s (FILE(docs/decisions.md:3387-3390)), and REG-19's c and total lines (FILE(docs/decisions.md:16533-16539)).
- **The draft's claim found not as stated:** "Alternatives 1 and 2 use those numbers, and say so" (DK6).

## 8. Verdict

**NOT READY.** Required: DK1 (end-window cold side; T-A), DK2 (the drop's total-line readouts), DK3 (the drop's ruling gated, and before the [REG]), DK4 (a tip of the no-surge control changes the surge reading and K4), DK5 (the owner's question corrected), DK6 (harness crossings named), DK7 (tilt rank from committed code, or dropped).

The design (B), the seed and the frozen rule, RE2, RE3's drain level and RE4 stand. With DK1–DK7 applied verbatim, nothing found here would block READY. The ops scripts still need their own pass (RE5).

## Appendix: reviewer patch

`rulef-reg24-draft2-r2.patch`, next to this file. Apply it with `git apply` on top of `docs/drafts/reg24_r2/reg24.patch` (and `withheld.patch`) applied to `872bc18` or `b46c279`. Its sha256 is `571a8b32675524b4d968179215a5ed10de5d0d27a420511a50a199f62c276b88`. It contains:

- `burst_table`: `cold_side_end` and the combined `cold` (DK1); `owed.drop_end`, `owed.min_drop` and `owed.t_min_drop_s` (DK2);
- `table`: `control_missing` (DK-O1);
- the `burst_outcome` docstring;
- three tests: `test_end_window_cold_side_catches_a_late_rewarm` (trace T-A, and DK2's keys), `test_emptyings_are_reg19s_on_reg19s_window` (DK-O2) and `test_table_gives_control_missing_without_a_valid_control` (DK-O1).

It is a sketch for the writer, applied nowhere in the repository.
