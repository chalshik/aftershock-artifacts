Rule F review of E1 and E0/E2 (draft 3), full text: NOT READY, 9 required changes. (Resend of my earlier message 4f19e289, same content, in case it did not arrive.)

**1. Traces on which a label or a stop comes out wrong**

Everything below is synthetic or from configs; no run folder was read. Scripts, both in /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/e0e1_scratch/: `r3_traces.py` (labels A, floors B, capacity C, seals D) and `r3_pred_sched.py` (prediction, replays, schedules).

Gate `k2.decide`:
- **T1, "widens" with no warm gain (r3_pred_sched).** Seed 0 is not paired across turns. Realized planned rate in [240, 900) and max 120 s surge:

  | sweep | nominal | planned | surge |
  |---|---|---|---|
  | 8 turns (REG-13) | 2.4 | 2.529 | 3.19 |
  | 8 turns (REG-13) | 2.6 | 2.758 | 3.76 |
  | 16 turns (E2-on) | 2.4 | 2.523 | 3.13 |
  | 16 turns (E2-on) | 2.6 | 2.674 | 3.40 |
  | 16 turns (E2-on) | 2.8 | 2.856 | 3.60 |

  The capacity rule judges `against: planned_rate`, so the 8-turn capacity lies in [2.529, 2.758) planned. The 16-turn "2.6" is 2.674, inside that interval, with a surge 9.5 % lower. True warm8 2.70 and true warm16 2.68 (planned units) read 2.4 and 2.6, so the label is "widens" (R 1.320 at floor ratio 0.821). The sentence "a measured R ≥ g still implies a true R ≥ 1" and the clause warm16 > warm8 hold in nominal units only.
- **T2, the same cause breaks the prediction table.** In planned units the fixed model gives 1.0702 × [2.529, 2.758) = [2.707, 2.952). That passes the 16-turn 2.6 always and 2.8 when warm8 ≥ 2.669, so it reads 2.6 or 2.8 and the label is "widens" (R 1.320 or 1.421), not "floor_only". DERIVED; it assumes capacity is a threshold in realized planned rate (BELIEF), but the table's nominal rounding is no less a BELIEF.
- **T3, "does_not_widen" with a true widening.** There is no guard for the 16-turn rounding. True warm16 2.19 reads 2.0; at floor ratio 0.84 the true R is 1.086 (above g) and the gate's R is 0.992. The symmetric bound R × 2.2/2.0 is 1.091.
- **T4, a hole reads as a result.** The server passes 2.0–2.6 but 2.2 has no valid run after two reruns: `load.capacity` returns 2.0, giving "unresolved" (1.015) at floor ratio 0.821 and "does_not_widen" (0.992) at 0.84. The truth is "widens". "missing" covers only the lowest rate. A heat stop before 2.6 does the same.
- **T5, lowest rate fails alone.** 2.0 valid, fails on queue slope only (0.0145) or a NaN slope, while 2.2–2.6 pass: warm16 is NaN, `low16_measured` is True, R_upper 0.992 gives "does_not_widen" at 0.84 (1.015 "unresolved" at 0.821). The 16-turn 2.0 schedule is burstier than the 8-turn one (60 s dispersion 10.8 against 5.6, surge 2.95 against 2.82).
- **T6, the rows averaged decide "does_not_widen" against "unresolved".** Label map (A1): at warm16 ≤ 2.0 the label is "does_not_widen" iff floor16/floor8 ≥ 0.8333; at 2.2 it is "floor_only" iff ≤ 0.846. Model F's own floor ratio:

  | model | registered rows (16t 1.5–3.0, 8t 2.0–4.0) | same rates 2.0–3.0 | E1's 1.5 row counted |
  |---|---|---|---|
  | fixed | 0.8208 | 0.8456 (+3.0 %) | 0.8419 |
  | proportional | 0.7719 | 0.8002 | 0.7932 |

  The unequal grids bias the ratio down, toward a larger R. B3/B4: E1's 1.5 row at 1.50 against 1.53 (line 1.526), or KV 0.84 against 0.85, gives 1.725 "ok" against 1.770 "tail_ok" (2.6 %).
- **T7, REG-13's 0.9503.** With warm8 2.0 instead of 2.4 and the same 16-turn data (floors 1.431/1.744), warm16 2.2 or 2.4 is "widens" (R 1.341, 1.462; g 1.200) instead of "floor_only".
- **T8, minor.** R = g exactly gives "unresolved" (1.0833333333333333 < 1.0833333333333335; only at equal floors). `decide(f16=0)` raises ZeroDivisionError. `gate_factor(nan)` is inf and ends in "missing", which is fine. The "missing" branch and `low16_measured` behave as written.

Floor rule (`e1.floor`, B):
- No rows at all returns "unsaturated" (B1), the same status as a grid that did not reach the floor.
- One KV dip removes the floor: 0.84 at 3.5 gives "tail_too_few", at 4.0 "tail_unsaturated", with all five upper rows behind (B6, B7). E2 then never runs.
- A NaN row is dropped silently ("ok", n 4; B8). Two rates with no valid run still give "ok" with λ_sat 3.0 and n 3 (B9); `cold_floor` has no swept-rates check, unlike `capacity`.
- Two valid rows at one rate: `cold_floor` and `capacity` raise ValueError (B2, C5). `floor_tail` has no check but is reached only after `cold_floor`.
- A single saturated row gives "too_few" (B10); a full row that keeps up goes to the tail (B4, B11). Both as registered.

Stops:
- **Both can fire wrongly on a missing variable.** Without `AFTERSHOCK_UNSEAL=E0`, `find_runs` drops E2-off, the rows are empty, the status is "unsaturated", and the cache-on sweep is not run. The same happens to `e1 floor` without `=E1` ("E1 gives no floor", E2 not run). The only sign is one stderr line.
- **Both are label-neutral.** k2.py:102 returns "missing" for a NaN floor whatever warm16 is.
- **The status leaks about one bit.** "ok" against "tail_ok" says whether the lowest full row kept up (at 16 turns, floor16 below or above about 1.526). Nothing can be tuned afterwards, so it is harmless.
- **The real leak is `checks.json`.** "A rerun decision reads only checks.json" contradicts "No interim look": the file holds `no_errors.detail` = {"ok", "unfinished"}, `accounting.detail.ok` and `release_chain.detail.unsent_later_turns` (harness/checks.py:67-83, 172-174). ok ÷ run length is the floor of a saturated run, and unfinished > 0 says a cache-on rate collapsed.

Seals (D):
- `AFTERSHOCK_UNSEAL=E1 … analysis.e1 floor` reads E1's and REG-8's runs; E2 and REG-19 stay sealed. Correct.
- `AFTERSHOCK_UNSEAL=E0 … analysis.k2 observed` reads E2. E1 is readable only if a `## ` heading contains exactly "[RESULT] E1"; a heading worded "E1 [RESULT]" keeps the seal, floor8 becomes "unsaturated" and the label is "missing", silently.
- The E2 flag (`python -m analysis.e1 status sweep_l1t16pl350cl_pc_off`) cannot work without `AFTERSHOCK_UNSEAL=E0`. The registration names neither the command nor the variable.
- `tests/test_withheld.py::test_e1_and_e2_seals_cover_exactly_their_sweeps` will fail once a registered rerun config exists: the stem `sweep_l1pl350cl_pc_off_rerun1a` is sealed "E1", so the set is no longer `{"sweep_l1pl350cl_pc_off"}`. Same for E0.

Stopping rule:
- An invocation that ends early (VM off, crash, KeyboardInterrupt at run.py:220) leaves rates never started. The rule covers only "an invalid rate"; relaunching the full config makes duplicates, and both rules raise.
- No rule says which of two valid runs counts.
- "Clean at the commit that holds this registration's approval" cannot hold for a rerun, which needs a new config file and so a new commit.
- A rate with no valid run after two reruns is covered by T4 and B9.

**2. Code against the text**
- `tests/test_e1.py` has 8 tests, not 7. `test_k2.py` has 9, as stated. All 31 pass (8 + 9 + 14 in `test_withheld.py`).
- E1's code list omits `report`, `work_rates` and `floor_status`. The registered command prints `report()`, not `observed()`.
- "`e1.observed`: the floor, its status, the rows" is wrong: no rows are returned, and `e1.prediction` is not printed.
- The E0/E2 section has no confounds paragraph, though "Changed" item 6 says one was added. E1's paragraph says the confounds touch "the reported tilt and the comparison of the floor with 1.681 only". That is false for E0: warm8 is REG-13's historic run and enters R and the warm clause directly.
- Three removals from draft 2 are not listed under "Changed": the "Overload range" bullet (the subject of T6), the 72k/54k KV arithmetic, and "the closed-loop floor correction" in the no-decision list.
- Prediction table recomputed from `k2.predict`, `closed_loop_floors` and `predict_measured`: every cell matches except rounding, 1.2183 (text 1.219) and 1.6195 (text 1.619). But see T2: "read on the grid" ignores the realized planned rates.
- Verified as stated:
  - tokens: 3968 and 6016 longest; 3072/4096 cold, 496/376 warm;
  - cost model: 0.180 s + 0.135 ms per token;
  - floors: 1.744/1.771 and 1.431/1.367;
  - g = 1.0833; E1's 1.5 row at 1.606 planned, line 1.526;
  - both grids and the `extends` chain;
  - costs: 2.1, 1.75, 2.45 and 4.2 h;
  - REG-8's floor settings (gate.py:180) and the seal patterns.
- Stale docstrings:
  - k2.py:93-95 says "the owner decides" (text: the delegate);
  - k2.py:1-4 says "Nothing here reads a run folder" and "E2's 16-turn shock matrix" (text: E3);
  - e1.py:1 says "draft, not registered";
  - tests/test_e1.py:1 says "blind K3 test".
- "Without a floor from E1, E2 does not run" is procedure only; no code enforces it.

**3. The strongest alternative explanations**
- **"widens":** the 16-turn seed-0 schedule at 2.6 is lighter than the 8-turn 2.6 that failed (planned −3.0 %, surge −9.5 %; T1). Second: warm8 is one historic near-threshold pass under older loadgen code. Separating evidence: the schedule table (0 GPU h), a second seed, or an 8-turn 2.4/2.6 rerun under today's code.
- **"floor_only":** a warm gain below the grid step, not "only because the floor fell" (a true +7 % reads as none); plus T7.
- **"does_not_widen":** the 16-turn rounding (T3), one bursty low rate (T5), or the rows averaged (T6).
- **E1's floor ≠ 1.681:** besides the mix tilt, a different running batch and preemption rate in closed loop (the server queue is bounded by live sessions), connection overhead, code or day, and the 900 s transient. U separates mix from batching and is reported; preemptions and mean running are not.
- **Named confounds are not enough.** Missing:
  - schedules unpaired across turns (T1);
  - warm8 historic and near-threshold in E0 (T7);
  - unequal floor rate ranges (T6).

**4. Can each outcome change a decision?**
- **Label map (A1):** the label is "widens" iff warm16 reads ≥ 2.6, for any floor16/floor8 ≤ 1.0 (at 2.6) or ≤ 1.077 (at 2.8); it is never "widens" at ≤ 2.4. With cold prompts 33 % longer, floor16 > floor8 is nearly unreachable.
- **So the matrix decision is "does E2-on pass 2.0, 2.2, 2.4 and 2.6 on seed 0".** E1 (2.1 h) and E2-off (1.75 h) cannot change it; they can only block it through "missing".
- **E1 and E2-off decide wording only** ("floor_only" / "does_not_widen" / "unresolved") and K2's reported ratio. As decision inputs they should not be proposed; they are defensible only as K2's measurement, and the registration should say so.
- **E2-on (2.45 h) is a real decision run**, but "the fixed model already predicts floor_only" does not hold on seed 0's schedules (T2), and a "widens" from it is confounded (T1). It should not run until the warm clause is fixed.
- **"does_not_widen"** needs warm16 ≤ 2.0 and a floor ratio ≥ 0.833, which is 1.5 % above the fixed prediction and inside T6's 3 %. Its split from "unresolved" is noise.

**5. Verdict: NOT READY**

Required:
1. Put the planned-rate and surge table of both cache-on sweeps in the [REG]. Define the warm clause and g's guarantee in realized planned rate (on seed 0 that means warm16 ≥ 2.8, planned 2.856 > 2.758), or reword what "widens" shows. Redo `predict_measured` and the table. This changes a threshold, so it is the owner's choice.
2. Compute both floors over the common saturated rates (2.0, 2.5, 3.0), or register both readings with "unresolved" when they disagree. Restore the overload-range caveat.
3. Give "does_not_widen" a 16-turn rounding guard (R × next16/warm16 ≤ 1), or rename it "not shown to widen".
4. A swept E2-on rate with no valid run below the first failing rate gives "missing". State whether floors may have holes, and report n and the rates used.
5. Name the flag command with `AFTERSHOCK_UNSEAL=E0`. Make `floor`, `floor_status` and `k2.observed` fail loudly on a parent with zero rows. Fix the seal test for rerun stems.
6. Rerun decisions read only `valid` and `failed` (the harness's VALID/INVALID line), not the details in `checks.json`.
7. Stopping rule: rates never started run from a config listing only them; say which of two valid runs counts, or that duplicates end in "missing"; allow a descendant commit that adds only rerun configs.
8. Text: 8 tests; the code list; `report` and what it prints; a confounds paragraph in E0 (warm8 historic at 0.9503, T7); the unlisted removals; the docstrings.
9. Say in both rule A1 paragraphs that E1 and E2-off cannot change the matrix decision.

Optional:
- Have the flag print a boolean instead of the status.
- Add a tolerance at R ≥ g and guard f16 = 0.
- Register a rule for a single KV dip (B6, B7).
- Report preemptions and mean running beside U.
- An 8-turn 2.4/2.6 control under today's code (about 0.7 GPU h, the owner's call).

Could not check:
- REG-13's stopping-rule text, the delegation entry (CLAUDE.md C puts GPU runs and `sudo` under "ask the owner first"), and `docs/claims.md`.
- Whether REG-21 is registered before E1's U is computed; `e1.report` computes REG-21's statistic on new data.
- What the recorder prints on the console (run.py:177), which could be an interim look.
- The 40,960 limit (not in configs or harness).
- REG-13's 0.9503 and every real run, by design.
- I skipped the session-start reading on purpose, per rule F.