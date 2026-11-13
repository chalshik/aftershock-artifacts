# Draft 4 (2026-11-13) of the E1 registration, split from E0/E2

**Not ready for review yet: its launch scripts are not written.** They will follow the design of REG-19's resume scripts (`docs/probe/20261113_reg19/ops_r3/`) once that design has passed its review, and go to rule F with this text. Draft 3 (`docs/drafts/e0_e1_draft3.md`) registered E1 together with E0 and E2; its rule F review (`docs/drafts/reviews-2026-11-13/rulef-e0e1-r2.md`, NOT READY, 9 items) found the E0/E2 gate confounded by unpaired schedules, which needs a redesign and the owner's choice of a threshold. E1 does not depend on that, so it is registered alone. What changed is listed at the end.

---

## 2026-11-13 · [REG] E1: the closed-loop cache-off sweep of L1 at 350 W, which measures the 8-turn closed-loop cold floor (GPU, ≈ 2.1 h)

- **ID:** E1 (step E1 of `docs/experiment-plan.md`, "Stage 2, revised"). Runs after REG-19's queue has ended and its [RESULT] is written; needs no REG-19 result.
- **Owner's choice (2026-11-12, logged in decisions.md 2026-11-13 [CORR]):** "Floor only": E1 carries no K3 test.
- **Question:** what does the saturated L1 server complete per second with caching off when turns are closed-loop?
- **Claim served:** K2 (`docs/claims.md`), as a measurement: the 8-turn closed-loop floor, so that 1.681 req/s (RUN(the 13 REG-8 runs, gate.reg8_zone)) is written as "the open-loop floor" only and closed-loop margins are stated against a closed-loop floor.
- **What E1 cannot do (rule A1), said first:** E1 changes no decision about a shock matrix. The rule F review showed that whether the 16-turn window "widens" is decided by the 16-turn cache-on sweep alone; E1 and the 16-turn cache-off sweep only word the ratio. E1 is proposed as K2's measurement and as the floor every closed-loop margin in the paper is quoted against, and for nothing else. If the owner holds that a measurement that changes no decision should not cost 2.1 GPU h, E1 should not run.
- **Config:** `configs/sweep_l1pl350cl_pc_off.yaml` (committed, unused). It is REG-8's cache-off sweep (seed 0, 900 s per rate, warm-up 240 s, drain 300 s) with REG-13's two changes, closed-loop turns and `loadgen_force_close: true`, at REG-8 part b's rates [1.5, 2, 2.5, 3, 3.5, 4]. At every rate the planned schedule equals REG-8's (FILE(tests/test_e1.py), `test_e1_schedules_equal_reg8_part_b_at_every_rate`). The longest prompt is 3968 tokens (DERIVED: 2176 + 7 × 256).
- **Single-rate configs** (`configs/sweep_l1pl350cl_pc_off_only_r<rate>.yaml`, six, committed, unused): each expands to the sweep's own run at that rate and nothing else (checked when they were written: equal to the sweep's expansion after the list of rates is removed). They exist so that every run E1 can ever need is in the commit that holds this registration.

### What is measured: the closed-loop cold floor (`e1.floor`)
- **Rule:** `gate.cold_floor` with REG-8's settings (mean KV ≥ 0.85, at least 2 runs, throughput < 0.95 × planned rate).
- **Registered fallback:** if and only if that rule returns "not_monotone", `e1.floor_tail`: λ_sat is the lowest rate from which every row is saturated, and the floor is the mean over those rows, from at least 2. Its status is "tail_ok", "tail_too_few" or "tail_unsaturated", so a fallback floor cannot be mistaken for the rule's own. Where it matters: the 1.5 row plans 1.606 req/s, so it counts as saturated only below 1.526 (DERIVED: 0.95 × 1.606).
- **Holes:** a swept rate at or above λ_sat with no valid run gives the status "holes" and no floor (the floor would average over a gap); the missing rates are listed.
- **Two valid runs at one rate** (a rate launched again by mistake): the earliest counts (`e1.first_valid`; run ids start with their launch time); the later ones are listed by name.
- **No rows at all** gives "no_rows", and the commands raise: a sweep that was not read is not a sweep that did not saturate.
- **A floor exists** only with status "ok" or "tail_ok". The result reports n and the rates used.

### Prediction (BELIEF)
P(status "ok") ≈ 0.75; P("tail_ok") ≈ 0.2; floor 1.70 to 1.80 req/s. Model F's replay of E1's config at 1.681 over rates ≥ 2.0 gives 1.744 (fixed cost) or 1.771 (proportional) (`k2.closed_loop_floors`, DERIVED; model BELIEF). The closed-loop cold spans on record point the same way: 1.73 to 1.81 req/s at λ = 2.0 and 2.2 (RUN(20261110-182920_burst_l1pl350cl_r2.0_s2, gate.reg17_gate), RUN(20261110-063647_burst_l1pl350cl_r2.2_s2, gate.reg14_gate)).

### Decision under each outcome (rule A1)
- **A floor ("ok" or "tail_ok"):** the paper and `docs/model.md` may quote it as the closed-loop cold floor at 8 turns, with its status, n and rates; closed-loop margins (λ ÷ floor) are restated against it. Each such edit is its own decision.
- **No floor:** K2's 8-turn closed-loop floor is reported as unmeasured on this grid; closed-loop margins keep the open-loop floor, named as such. A new grid is a new registration.
- **In neither case** does E1 start, stop or size another run. That is why the paragraph "What E1 cannot do" comes first.

### Reported, never judged
- The served-mix tilt against REG-8 (`e1.tilt`, over the rates both sweeps have from their common onset), with `e1.prediction` as its description. Round 1 showed it is the same for any saturated closed-loop server, so it cannot test model F.
- The uncached-token work rate U of both sweeps' saturated runs (`e1.work_rates`, REG-21's statistic). On REG-8's runs that is REG-21's reference, so **`e1.report` raises until REG-21's first [RESULT] is in `docs/decisions.md`**, and E1's result is computed after it.
- Preemptions per second and the mean running batch of E1's saturated runs beside REG-8's (the review's alternative to the mix: a different running batch in closed loop).

### Confounds, named
E1 opens a new connection per request and REG-8 did not. REG-8 ran on 2026-11-07 under the code of that day; E1 runs under today's (the recorder fix and stricter `recorder` and `gpu_steady` checks of 2026-11-12). Both sweeps run their rates in ascending order, so drift within a sweep enters any slope. The 900 s per rate includes the transient. All of these touch the comparison of E1's floor with 1.681 and the reported tilt; none can be removed by E1.

### Stopping rule (REG-13's, completed)
- **One harness invocation of the sweep** (`configs/sweep_l1pl350cl_pc_off.yaml`). No interim look at any rate's throughput, KV or floor before the result is computed.
- **A rate the invocation never started** (the VM went off, the harness stopped): it is run from its single-rate config. That is its first attempt, not a rerun.
- **An invalid rate** is rerun unchanged from its single-rate config, at most twice. A heat-invalid run (`gpu_steady`) once, after cooling to ≤ 45 °C; a second heat failure stops the sweep. A client error (`no_errors`), a limit other than 350 W (`power_limit`) or an unexpected pre-launch check stops it. Every launch of a rate is one attempt, at most three; a run that ends without `checks.json` stops the sweep until a new decision.
- **A rerun decision reads only the fields `valid` and `failed` of `checks.json`.** The details in that file (counts of ok and unfinished requests) are outcome data and are not read.
- **Reads allowed while diagnosing a stop:** `tmux has-session`, folder names, `valid` and `failed`, and in a launch log only the lines holding `run_id` or `[run] checks`.
- **The VM's tree** is clean at the commit that holds this registration's approval. That commit already holds the single-rate configs, so no later commit is needed for a rerun.

### Withheld until the [RESULT] of E1
The sweep's run folders (`*_sweep_l1pl350cl_pc_off_r*`; `analysis/withheld.py`, seal "E1").

### Result, computed once
After every rate has a valid run or the stopping rule has ended, and after REG-21's first [RESULT]: `AFTERSHOCK_UNSEAL=E1 uv run python -m analysis.e1 floor`. It prints `e1.report`: the floor with its status, n, rates and any later valid run not counted; the open-loop floor recomputed the same way; the common onset; the tilt with its prediction; the work rates of both sweeps. From committed code, with `analysis/` and `tests/` clean and `uv run pytest` passing; the [RESULT] names the commit.

### Pre-launch and launch (scripts to be written and reviewed with this text)
As REG-19's resume: a session probe once (boot id, driver 595.99.02, the VM's tree and `uv.lock` at the registered commit, 350.00 W read, not set by the launch); before every launch a read-only check of the limit, temperature ≤ 45 °C, an idle GPU, no tmux session, the tree, free disk and the boot id; an attempt record written immediately before the launch command, per rate; validity read from `checks.json`; a valid run found on the VM is used, not relaunched; copies checksum-verified. **The owner must set 350 W** unless a sudoers rule for `nvidia-smi -pl 350` exists by then.

### Cost
6 runs × (900 + 300 + about 60 s) ≈ 2.1 GPU h (DERIVED); ≈ 4.2 h with one rerun per rate.

### Code and tests
`analysis/e1.py` (`floor`, `floor_tail`, `first_valid`, `swept_rates`, `floor_status`, `saturated`, `onset`, `observed`, `report`; reported only: `tilt`, `fit`, `prediction`, `replay_rows`, `work_rates`); `tests/test_e1.py`, 12 tests; the seal test in `tests/test_withheld.py`. `work_rates` gives, beside U, the running batch, waiting line, KV, preemptions per second and the redo proxy of each saturated run.

### Changed from draft 3 (the E1 items of its rule F review)
- E1 is registered alone and says first that it changes no decision (item 9).
- `floor`, `floor_status` and `observed` fail loudly on a sweep with no readable run; "holes" for a swept rate without a valid run; n and the rates are reported (items 4, 5).
- The result command names `AFTERSHOCK_UNSEAL=E1`; the seal test is keyed on the config's `name`, so single-rate configs do not break it (item 5).
- Rerun decisions read only `valid` and `failed` (item 6).
- The stopping rule covers a rate never started, says which of two valid runs counts, and needs no later commit, because the single-rate configs are registered with it (item 7).
- The text lists the functions and what the command prints (item 8).
- New: the report waits for REG-21's result, because it computes REG-21's statistic on REG-8's runs.
- Left for the E0/E2 registration: its items 1 to 3 (the planned-rate and surge table, floors over common rates, the rounding guard).
