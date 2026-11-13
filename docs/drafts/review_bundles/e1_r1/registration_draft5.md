# Draft 5 (2026-11-13) of the E1 registration, split from E0/E2

**For review with its launch scripts** (`docs/probe/20261113_e1/ops/`: `common.sh`, `vm_state.py`, `session_probe.sh`, `launch.sh`, `queue.sh`, `vm_checkout.sh`, `README.md`, `DESIGN_NOTES.md`; sandbox 170 of 170, PROBE(docs/probe/20261113_e1/ops/sandbox_20261113T204859Z.txt)). The owner sent E1 to review so that it can run once REG-19's queue has ended (FILE(docs/decisions.md:4516)). Draft 3 (`docs/drafts/e0_e1_draft3.md`) registered E1 together with E0 and E2; its rule F review (`docs/drafts/reviews-2026-11-13/rulef-e0e1-r2.md`, NOT READY, 9 items) found the E0/E2 gate confounded by unpaired schedules, which needs a redesign and the owner's choice of a threshold. E1 does not depend on that, so it is registered alone. What changed is listed at the end.

---

## 2026-11-13 · [REG] E1: the closed-loop cache-off sweep of L1 at 350 W, which measures the 8-turn closed-loop cold floor (GPU, ≈ 2.1 h)

- **ID:** E1 (step E1 of `docs/experiment-plan.md`, "Stage 2, revised"). Runs after REG-19's queue has ended: the committed log holds an [OPS] entry headed `REG-19: the queue ended`, which quotes the queue's `QUEUE DONE` or `QUEUE END` line, or REG-19's [RESULT], and REG-19's queue lock does not exist (FILE(docs/probe/20261113_e1/ops/common.sh:96)). It needs no REG-19 result. A `QUEUE STOP` leaves no such entry: REG-19 then waits for the owner, and E1 waits with it. The owner's entry forbids only a run while REG-19's queue holds the GPU (FILE(docs/decisions.md:4520)); draft 4's wait for REG-19's [RESULT] is dropped, since that result waits for two registrations that have no bearing on E1, and the GPU would sit idle meanwhile. **The VM then leaves REG-19's pin** `a7bb77a` for this entry's commit (`vm_checkout.sh`). REG-19's launch refuses any other tree (FILE(docs/probe/20261113_reg19/ops_r3/launch.sh:45)), so a later REG-19 rerun, if the owner allows one, needs the VM moved back first; nothing of REG-19 is lost, since its runs are copied and verified and `runs/` is outside git.
- **Owner's choice (2026-11-12, logged in decisions.md 2026-11-13 [CORR]):** "Floor only": E1 carries no K3 test.
- **Question:** what does the saturated L1 server complete per second with caching off when turns are closed-loop?
- **Claim served:** K2 (`docs/claims.md`), as a measurement: the 8-turn closed-loop floor, so that 1.681 req/s (RUN(the 13 REG-8 runs, gate.reg8_zone)) is written as "the open-loop floor" only and closed-loop margins are stated against a closed-loop floor.
- **What E1 cannot do (rule A1), said first:** E1 changes no decision about a shock matrix. The rule F review showed that whether the 16-turn window "widens" is decided by the 16-turn cache-on sweep alone; E1 and the 16-turn cache-off sweep only word the ratio. E1 is proposed as K2's measurement and as the floor every closed-loop margin in the paper is quoted against, and for nothing else. If the owner holds that a measurement that changes no decision should not cost 2.1 GPU h, E1 should not run.
- **Config:** `configs/sweep_l1pl350cl_pc_off.yaml` (committed, unused). It is REG-8's cache-off sweep (seed 0, 900 s per rate, warm-up 240 s, drain 300 s) with REG-13's two changes, closed-loop turns and `loadgen_force_close: true`, at REG-8 part b's rates [1.5, 2, 2.5, 3, 3.5, 4]. At every rate the planned schedule equals REG-8's (FILE(tests/test_e1.py), `test_e1_schedules_equal_reg8_part_b_at_every_rate`). The longest prompt is 3968 tokens (DERIVED: 2176 + 7 × 256).
- **Single-rate configs** (`configs/sweep_l1pl350cl_pc_off_only_r<rate>.yaml`, six, committed, unused): each expands to the sweep's own run at that rate and nothing else (checked when they were written: equal to the sweep's expansion after the list of rates is removed). They exist so that every run E1 can ever need is in the commit that holds this registration.

### The harness E1 runs on: the first GPU run since `5ee6e38`
- **Facts.** REG-19 runs at `a7bb77a` (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:11)). E1 runs at this entry's commit, whose harness includes `5ee6e38`: a recorder that survives a half-written line and logs its death, stricter `recorder` and `gpu_steady` checks, and a session cap in the load generator that is off unless `workload.sessions.cap` is set (FILE(docs/decisions.md:4200)). E1's configs set no cap. `git diff --stat a7bb77a HEAD -- harness/` gives 4 files, 163 lines in and 29 out; `pyproject.toml` and `uv.lock` are the same at both. No GPU run has used this harness yet.
- **Risks, and how this entry bounds them** (DESIGN_NOTES.md, R1–R6):
  - R1, a fault that crashes a run: it leaves a folder without `checks.json`, and E1 stops there (the stopping rule). Cost: at most one run.
  - R2, a fault that fails `recorder` on every run without crashing: the six sweep rates come back invalid after about 2.1 h. **The queue pauses after any invalid run** (it copies what is pending and stops before the next launch; starting it again applies the rerun rule; FILE(docs/probe/20261113_e1/ops/queue.sh:41)), so a systematic failure is seen before the reruns spend about 4.2 h more.
  - R3, `gpu_steady` is no longer only heat: since `5ee6e38` it also fails when the GPU samples do not cover [warm-up, duration] with no gap above `max_scrape_gap_s` = 2.0 s, or when no sample is busy (FILE(harness/checks.py:127), FILE(configs/base.yaml:55)). E1 reads only the names in `failed`, so it cannot tell a coverage failure from heat; **either one gets the heat rule's single rerun and counts toward "a second heat failure stops E1"**. That is stricter than a rule for heat alone, never looser.
  - R4: the recheck of 182 folders under the new checks (FILE(docs/decisions.md:4205)) shows that the old recorder's output passes them, not that the new recorder produces such output on the GPU.
  - R5: E1's floor is compared with REG-8's 1.681 req/s, measured under the harness of 2026-11-07 ("Confounds, named").
  - R6: this is the first move of the VM off `a7bb77a` since REG-19 began (the ID line).
- **Not done:** a smoke run on the new harness before E1. It would be a GPU run with its own registration; the pause bounds R2 to the sweep's 2.1 h before a person looks, which this entry accepts.

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
E1 opens a new connection per request and REG-8 did not. REG-8 ran on 2026-11-07 under the code of that day; E1 runs under this entry's (the recorder fix, the stricter `recorder` and `gpu_steady` checks and the load generator's session cap, off here, of 2026-11-12; "The harness E1 runs on"). Both sweeps run their rates in ascending order, so drift within a sweep enters any slope. The 900 s per rate includes the transient. All of these touch the comparison of E1's floor with 1.681 and the reported tilt; none can be removed by E1.

### Stopping rule (REG-13's, completed)
- **One harness invocation of the sweep** (`configs/sweep_l1pl350cl_pc_off.yaml`), launched at most once ever; if it fails before its first rate starts, every rate counts as never started. No interim look at any rate's throughput, KV or floor before the result is computed.
- **Attempts.** A rate's attempts are 1 if the sweep started it (the sweep's launch log has a `run_id` line for it) plus each single-rate launch of it; every launch is one attempt, whatever it left behind.
- **A rate the invocation never started** (the VM went off, the harness stopped): it is run from its single-rate config. That is its first attempt, not a rerun.
- **An invalid rate** is rerun unchanged from its single-rate config, at most twice. A heat-invalid run (`gpu_steady`) once, after cooling to ≤ 45 °C; a second heat failure stops the sweep. A client error (`no_errors`), a limit other than 350 W (`power_limit`) or an unexpected pre-launch check stops it. Every launch of a rate is one attempt, at most three; a run that ends without `checks.json` stops the sweep until a new decision. **"Stops the sweep" stops E1:** no further launch at any rate. A second heat failure is counted over all of E1's runs, not per rate. Any `no_errors` in `failed` stops E1 (the details that would separate a client error from another are not read). A rate whose three attempts are spent is not launched again; the other rates still run, and the queue ends with `QUEUE END`, naming the rates without a valid run ("holes"). **After any invalid run the queue pauses** ("The harness E1 runs on", R2). Two valid runs at one rate: nothing is launched and both are listed, the earliest counting. A folder that no launch log of these scripts names, a named run missing from the VM, or a run made at another commit (read from the harness's start line, which holds `run_id` and `git_commit`, FILE(harness/run.py:143)) stops E1 for the owner. Every run with a `checks.json`, valid or invalid, is copied and checksum-verified; a run without one is copied by a separate step.
- **A rerun decision reads only the fields `valid` and `failed` of `checks.json`.** The details in that file (counts of ok and unfinished requests) are outcome data and are not read.
- **Reads allowed while diagnosing a stop:** `tmux has-session`, folder names, `valid` and `failed`, and in a launch log only the lines holding `run_id` or `[run] checks`.
- **The VM's tree** is clean at the commit that holds this registration's approval. That commit already holds the single-rate configs, so no later commit is needed for a rerun. The scripts recognise the approval only by a heading of the form `## <date> · [DECISION] (owner|delegate) E1 approved` after this entry, at the commit named in `docs/probe/20261113_e1/ops/e1_commit.txt` (FILE(docs/probe/20261113_e1/ops/common.sh:38)); from then on they refuse if any of them differs from its text at that commit.

### Withheld until the [RESULT] of E1
The sweep's run folders (`*_sweep_l1pl350cl_pc_off_r*`; `analysis/withheld.py`, seal "E1").

### Result, computed once
After every rate has a valid run or the stopping rule has ended, and after REG-21's first [RESULT]: `AFTERSHOCK_UNSEAL=E1 uv run python -m analysis.e1 floor`. It prints `e1.report`: the floor with its status, n, rates and any later valid run not counted; the open-loop floor recomputed the same way; the common onset; the tilt with its prediction; the work rates of both sweeps. From committed code, with `analysis/` and `tests/` clean and `uv run pytest` passing; the [RESULT] names the commit.

### Pre-launch and launch (`docs/probe/20261113_e1/ops/`, reviewed with this text)
As REG-19's resume, with the differences DESIGN_NOTES.md lists: a session probe once per boot (boot id, driver 595.99.02, the VM's tree and `uv.lock` at the registered commit, 350.00 W read, not set by the launch; a renewal needs a decisions entry); before every launch a read-only check of the limit, temperature ≤ 45 °C (waiting up to 30 min, which spends no attempt), an idle GPU, no tmux session, the tree, `uv.lock`'s blob, free disk and the boot id; an attempt record written immediately before the launch command; validity read from `checks.json`'s `valid` and `failed` only (`vm_state.py`); a valid run found on the VM is used, not relaunched; copies checksum-verified, one run at a time. The VM moves from `a7bb77a` to the registered commit by `vm_checkout.sh` (detached HEAD, its output saved and committed with an [OPS] entry). **The owner must set 350 W** unless a sudoers rule for `nvidia-smi -pl 350` exists by then. Run order: `README.md`, "Run order".

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

### Changed from draft 4 (the launch scripts written; no review yet)
- "Not ready for review" is dropped: the scripts exist and go to rule F and the owner-proxy with this text.
- E1 waits for REG-19's queue to end, recorded by an [OPS] entry, not for REG-19's [RESULT] (the ID line; DESIGN_NOTES.md I11). The VM's move off `a7bb77a` is stated.
- New section "The harness E1 runs on": E1 is the first GPU run on `5ee6e38`'s harness; risks R1–R6 and how they are bounded; `gpu_steady`'s coverage failures are treated as heat (R3); the pause after an invalid run is part of the rule (R2).
- The stopping rule states the scripts' readings of draft 4 (DESIGN_NOTES.md I1–I9, I12, I13): attempts, a global stop, the heat count over all runs, any `no_errors`, spent rates, two valid runs, unnamed folders, the commit check and what is copied.
- The approval heading the scripts recognise, and `e1_commit.txt`.
