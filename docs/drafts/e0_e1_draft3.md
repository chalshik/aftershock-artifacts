# Draft 3 (2026-11-13) of the E1 and E0/E2 registrations, for review

Draft 2 is `docs/drafts/scratchpad-2026-11-12/e0_e1_draft2.md` (with the round-1 review, verbatim, and what was changed because of it). The round-2 review's text was lost with the session that ran it; only its script survives (`docs/drafts/scratchpad-2026-11-12/review_e0e1_r2/traces.py`). This draft is draft 2 with the changes listed at its end; it gets a fresh rule F round.

---

## 2026-11-13 · [REG] E1: the closed-loop cache-off sweep of L1 at 350 W, which measures K2's 8-turn closed-loop floor (GPU, ≈ 2.1 h)

- **ID:** E1 (step E1 of `docs/experiment-plan.md`, "Stage 2, revised"). Runs after REG-19's queue has ended and its [RESULT] is written; needs no REG-19 result.
- **Owner's choice (2026-11-12, logged in decisions.md 2026-11-13 [CORR]):** "Floor only": E1 carries no K3 test.
- **Question:** what does the saturated L1 server complete per second with caching off when turns are closed-loop?
- **Claim served:** K2 (`docs/claims.md`): the 8-turn reference of the window ratio in E0's gate; and the floor quoted for closed-loop cells, so that 1.681 is written as "the open-loop floor" only.
- **Config:** `configs/sweep_l1pl350cl_pc_off.yaml` (committed, unused). It is REG-8's cache-off sweep (seed 0, 900 s per rate, warm-up 240 s, drain 300 s) with REG-13's two changes, closed-loop turns and `loadgen_force_close: true`, at REG-8 part b's rates [1.5, 2, 2.5, 3, 3.5, 4]. At every rate the planned schedule equals REG-8's (`tests/test_e1.py::test_e1_schedules_equal_reg8_part_b_at_every_rate`). The longest prompt is 3968 tokens.
- **What is measured:** the closed-loop cold floor, `e1.floor`.
  - **Rule:** `gate.cold_floor` with REG-8's settings (mean KV ≥ 0.85, at least 2 runs, throughput < 0.95 × planned rate).
  - **Registered fallback:** if and only if that rule returns "not_monotone", `e1.floor_tail` is used: λ_sat is the lowest rate from which every row is saturated, and the floor is the mean over those rows, from at least 2. Its status is "tail_ok", "tail_too_few" or "tail_unsaturated", so a fallback floor cannot be mistaken for the rule's own. Where it matters: the 1.5 row plans 1.606 req/s, so it counts as saturated only below 1.526; if it is full but keeps up, the rule alone leaves the floor undefined.
  - **No floor:** any status other than "ok" or "tail_ok" means E1 gives no floor, and E0 reads "missing".
- **Prediction (BELIEF):** P(status "ok") ≈ 0.75; P("tail_ok") ≈ 0.2; floor 1.70–1.80 req/s. Model F's replay of E1's config at 1.681 over rates ≥ 2.0 gives 1.744 (fixed cost) or 1.771 (proportional) (`k2.closed_loop_floors`, DERIVED; model BELIEF); the closed-loop cold spans of REG-11 to REG-18 (1.72–1.81 req/s at λ = 2.0–2.4) already point above 1.681.
- **Reported, never judged:** the served-mix tilt against REG-8 (`e1.tilt`, over the rates both sweeps have from their common onset), with `e1.prediction` as its description. Round 1 showed it is the same for any saturated closed-loop server (first come first served, many slots, residence, superlinear cost and last come first served all give −0.36 to −0.39 per req/s against model F's −0.39, synthetic), so it cannot test model F. Also reported: the uncached-token work rate U of E1's saturated runs (`k3w.work_rate`, the statistic of REG-21), beside REG-8's.
- **Open question A17, answered since draft 2** (decisions.md 2026-11-13 [DECISION]): vLLM 0.32.0's scheduler does not skip a head-of-queue request that does not fit the KV pool, so an all-miss open-loop server admits in arrival order. It bore only on the tilt's open-loop arm, which is not judged.
- **Decision under each outcome (rule A1):** E1's floor is a required input of E0's gate, which decides 8–12 GPU h. A floor with status "ok" or "tail_ok": E2 runs. Any other status: E0 is "missing", **E2 does not run** (it could not be judged), and the delegate decides between a new grid under a new registration and reporting K2 as unmeasured. E1's value changes no decision by itself.
- **Confounds, named:** E1 opens a new connection per request and REG-8 did not; REG-8 ran on 2026-11-07 and under the code of that day, E1 runs under today's (the recorder fix and stricter `recorder` and `gpu_steady` checks of 2026-11-12; the load generator's session cap is off); both sweeps run their rates in ascending order, so drift within a sweep enters any slope. All three touch the reported tilt and the comparison of the floor with 1.681 only.
- **Stopping rule (REG-13's):** one harness invocation of the sweep; an invalid rate is rerun unchanged with a rerun config listing that rate only (same `name`, a new file), at most twice; a heat-invalid run once after cooling to ≤ 45 °C, a second heat failure stops the sweep; a `client_error`, a limit other than 350 W or an unexpected pre-launch check stops it. A rerun decision reads only `checks.json`. **No interim look** at any rate's throughput, KV or floor before the result is computed.
- **Withheld until the [RESULT] of E1:** the sweep's run folders (`*_sweep_l1pl350cl_pc_off_r*`; added to `analysis/withheld.py` with this registration).
- **Result, computed once** after every rate has a valid run or the stopping rule has ended: `AFTERSHOCK_UNSEAL=E1 uv run python -m analysis.e1 floor` (`e1.observed`: the floor, its status, the rows; the reported items).
- **Pre-launch (every invocation):** 350 W set by the agent (`sudo -n nvidia-smi -pl 350`) and read back as 350.00; GPU idle at ≤ 45 °C; no other compute process; the VM's tree clean at the commit that holds this registration's approval, pulled only when no run is in progress; reads kept in `docs/probe/<date>_e1/`.
- **Cost:** 6 runs × (900 + 300 + about 60 s) ≈ 2.1 GPU h; ≈ 4.2 h with one rerun per rate.
- **Code and tests:** `analysis/e1.py` (`floor`, `floor_tail`, `saturated`, `onset`; reported only: `tilt`, `fit`, `prediction`, `replay_rows`, `observed`); `tests/test_e1.py`, 7 tests.

---

## 2026-11-13 · [REG] E0 and E2: K2's gate. Does the window from the cold floor to the warm capacity widen from 8 to 16 turns per session, with the warm side gaining too? It decides whether the 16-turn shock matrix (8–12 GPU h) is registered (E0: 0 GPU h; E2: GPU, ≈ 4.2 h)

- **ID:** E0 (the prediction and the gate, rule G) and E2 (the two 16-turn sweeps it needs). Registered before E1 or E2 runs.
- **Owner's choice (2026-11-12, logged in decisions.md 2026-11-13 [CORR]):** "Add 2.2": E2's cache-on grid has 2.2, and "widens" requires the warm side to gain.
- **Claim tested:** K2's first half (`docs/claims.md`): the range between the cold floor and the warm capacity widens with the turns per session.
- **Statistic:** R = ratio₁₆ ÷ ratio₈, where ratio = closed-loop warm capacity ÷ closed-loop cold floor. R is reported with its two factors, warm₁₆/warm₈ and floor₁₆/floor₈ (`k2.decide`, `k2.observed`).
  - Warm capacities by the configs' rule (`tables.sweep_capacity`), seed 0. warm₈ is REG-13's `sweep_l1pl350cl_pc_on` (2.4, seen). warm₁₆ is E2's `sweep_l1t16pl350cl_pc_on` at rates [2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2].
  - Floors by `e1.floor`: floor₈ from E1; floor₁₆ from E2's `sweep_l1t16pl350cl_pc_off` at rates [1.0, 1.5, 2.0, 2.5, 3.0].
  - The E2 configs are REG-13's and E1's with `turns: 16` (committed, unused). The longest prompt is 6016 + 128 tokens, against the 40,960 limit.

### The rule (`k2.decide`)
- **g = 1 + (next REG-13 grid rate above warm₈ − warm₈) ÷ warm₈ = 1 + 0.2 / 2.4 = 1.083.** A measured R ≥ g still implies a true R ≥ 1 after the 8-turn rounding. g does not cover a lucky pass at one grid rate (REG-13's 2.4 passed at 0.9503 against 0.95) or noise in the floors.
- **Labels:**
  - **"widens":** R ≥ g and warm₁₆ > warm₈. Only this label lets the 16-turn shock matrix be registered.
  - **"floor_only":** R ≥ g but warm₁₆ ≤ warm₈: the window widened only because the cold floor fell. No matrix.
  - **"does_not_widen":** R ≤ 1. K2's first half is refuted for L1 at sweep cost. No matrix.
  - **"unresolved":** 1 < R < g. No matrix; the delegate decides, and says so to the owner.
  - **"missing":** a needed input is undefined for want of data (no valid run at E2-on's lowest rate, no valid E2-on run at all, or a floor that `e1.floor` leaves undefined). No matrix.
- **E2-on's lowest rate (2.0) measured and failed:** R is bounded above by its value at 2.0 (`R_upper`): "does_not_widen" if R_upper ≤ 1, otherwise "unresolved".
- **Surge sensitivity, stated:** the closed-loop warm capacity depends on where a 900 s schedule puts a surge (decisions.md 2026-11-10 [CORR]). Both setups use the same rule on seed 0, so R compares setups under one rule; it is not a ratio of sustained capacities.

### Prediction (DERIVED: `k2.predict`, `k2.closed_loop_floors`, `k2.predict_measured`; BELIEF as a forecast)
Cost per request a + b × (tokens to prefill) at the stationary mix. Cold tokens are 3072 at 8 turns and 4096 at 16; warm uncached tokens 496 and 376. Model F's closed-loop floors are replayed at onsets 2.0 (8 turns) and 1.5 (16 turns).

| cost model | warm₁₆/warm₈ (true) | warm₁₆, true → read on the grid | floor₁₆/floor₈ (closed loop) | R, true | **R as the gate reads it** | **label** |
|---|---|---|---|---|---|---|
| fixed (0.180 s + 0.135 ms per token; REG-8's two capacities) | 1.070 | 2.57 → 2.4 | 1.431 / 1.744 = 0.821 | 1.304 | **1.219** | **floor_only** |
| proportional | 1.319 | 3.17 → 3.0 | 1.367 / 1.771 = 0.772 | 1.709 | **1.619** | **widens** |

- **Primary model:** the fixed model predicts **"floor_only"**: the floor falls about 18 %, and the warm capacity rises 7 %, which the grid reads as no change.
- **Calibration caveat:** both models scale the warm side from the open-loop 4.047 req/s. The closed-loop warm capacity (2.4, 59 % of it) is limited by something other than per-request token cost, so the warm-side prediction is weak. At equal session counts the 16-turn live context is about a third larger, which could lower warm₁₆ further.
- **P (BELIEF):** "widens" ≈ 0.3, "floor_only" ≈ 0.3, "does_not_widen" ≈ 0.2, "unresolved" ≈ 0.1, "missing" ≈ 0.1.

### Not blind
REG-13's 2.4 and REG-8's 1.681 and 4.047 are seen, and they are inputs. E1 and E2 are unseen.

### Decision under each outcome (rule A1)
Only "widens" opens the registration of the 16-turn paired shock matrix (E3, 8–12 GPU h). Every other label stops K2 at about 6.3 GPU h (E1 + E2). "floor_only" and "does_not_widen" are written up as K2 results; the 4-turn point is considered only after "widens". The prediction table, the P values and the KV arithmetic change no decision.

### E2's runs
- **Order:** the cache-off sweep first (5 rates, ≈ 1.75 h), then the cache-on sweep (7 rates, ≈ 2.45 h).
- **One flag between them, nothing else:** after the cache-off sweep, `e1.floor` is computed on it and **only its `status`** is read. If it is neither "ok" nor "tail_ok", E0 is "missing" whatever the cache-on sweep would give, so the cache-on sweep does not run.
- **Stopping rule, pre-launch reads:** as E1's (REG-13's rule; 350 W; idle GPU at ≤ 45 °C; clean tree at the approved commit; reads in `docs/probe/<date>_e2/`).
- **Withheld until the [RESULT] of E0:** E2's run folders (`*_sweep_l1t16pl350cl_pc_o*_r*`; added to `analysis/withheld.py` with this registration).
- **Result, computed once** after both sweeps: `AFTERSHOCK_UNSEAL=E0 uv run python -m analysis.k2 observed` (`k2.observed`).
- **Cost:** 12 runs × about 1260 s ≈ 4.2 GPU h; ≈ 8.4 h with one rerun per rate.

### Code and tests
`analysis/k2.py` (`shape`, `cold_tokens`, `warm_tokens`, `token_gap`, `calibrate_fixed`, `predict`, `closed_loop_floors`, `predict_measured`, `gate_factor`, `decide`, `observed`; `gate`, R against g alone, is kept for the table); `tests/test_k2.py`, 9 tests. Configs `sweep_l1t16pl350cl_pc_{on,off}.yaml`.

---

## Changed from draft 2

1. The owner's two choices are cited from the [CORR] that now logs them; the approval is the delegate's (decisions.md 2026-11-13 [DECISION], delegation).
2. A17 is answered (source), and said so.
3. E1 has a registered stop for E2: without a floor from E1, E2 does not run. E2 has one registered flag between its two sweeps (the cache-off floor's status).
4. Stopping rule and pre-launch reads are written out (REG-13's), with the agent setting 350 W.
5. The sweeps' run folders are withheld until their results (`analysis/withheld.py`), and each result is computed once with a named command.
6. A named confound is added: E1 and E2 run under the code of 2026-11-12/13 (recorder fix, stricter checks), REG-8 and REG-13 under the code of their days.
7. E1 reports the uncached-token work rate of its saturated runs beside REG-8's (REG-21's statistic), never judged.
8. "unresolved" and "missing" go to the delegate, who records the choice for the owner.
