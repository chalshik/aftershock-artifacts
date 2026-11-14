# Draft 7 (2026-11-13, UTC) of the E1 registration, split from E0/E2

**For review round 3** (rule F; round 2 says that round can be limited to DC1's text and DC2's patch; this draft's departures from round 2's words, listed in the item map, are added to it), **with its launch scripts** (`docs/probe/20261113_e1/ops/` as committed in 97a6438, changed by draft 7's patch `docs/drafts/e1_r3/ops_draft7.patch` in `common.sh`, `queue.sh`, `vm_checkout.sh`, `test_sandbox.sh` and `README.md`; sandbox 192 of 192 on a scratch copy with that patch applied, PROBE(docs/drafts/e1_r3/sandbox_20261113T231637Z.txt)) **and its code:** `analysis/e1.py` and `tests/test_e1.py`, held as patches against HEAD (`docs/drafts/e1_r3/e1_py_draft7.patch` and `test_e1_draft7.patch`, each cumulative: draft 6's patch with round 2's DC2 and DC8; the patched files have sha256 `428771e04a7a740bc87b20bc7959d835c56e0eebbfb822086248a373c200d415` and `dd3f52c579288cbe9a9a0144b98d2b880f2606eacea153fc268d232e6f6a750d`, byte-equal to the reviewer's), not in the main checkout, by the rule of decisions.md 2026-11-13 [CORR] (a subagent writes code changes as patch files); with both applied to a scratch copy of HEAD, `tests/test_e1.py` gives 16 passed. Draft 7 applies rule F round 2 (`docs/drafts/reviews-2026-11-13/rulef-e1-draft6-r2.md`, NOT READY; DC1–DC9 applied, DC4 with its RUNBOOK order replaced; DC-O1 to DC-O5 applied) to draft 6, and carries the owner-proxy's round-2 conditions (`docs/drafts/reviews-2026-11-13/proxy-e1-draft6.md`, APPROVE on DD1–DD12; DD1, DD2, DD4 and DD6(a) applied, DD3 and DD6(b) merged into round 2's DC6 and DC5, DD5 not applied because DC2 removes the case it discloses, DD7 to be redone with draft 7's patches, DD8–DD12 for the approval commit). Where each item went, and every departure from the reviewers' words: `docs/drafts/e1_draft7_itemmap.md`. DC2, DC8, DC-O1 and DC-O2 change code, so the review-stop rule calls for a third rule F round; DC2 changes "holes", DC-O1 and DC-O2 the scripts, and DC-O2 the stopping rule, so the owner-proxy's §3 calls for another owner-proxy pass. Since round 2: REG-19's [RESULT] is in the log (FILE(docs/decisions.md:16517), commit 6748c26); REG-22's and REG-21's batch 1 [RESULT]s are in it (FILE(docs/decisions.md:16322), FILE(docs/decisions.md:16421)); REG-20's gate was computed once (commit 3c8e5dc). The owner sent E1 to review so that it can run once REG-19's queue has ended (FILE(docs/decisions.md:4516)). Draft 3 (`docs/drafts/e0_e1_draft3.md`) registered E1 together with E0 and E2; its rule F review (`docs/drafts/reviews-2026-11-13/rulef-e0e1-r2.md`, NOT READY, 9 items) found the E0/E2 gate confounded by unpaired schedules, which needs a redesign and the owner's choice of a threshold. E1's run does not depend on that, so it is registered alone; E0's gate does take E1's floor as an input, so E1's floor is not computed before E0's [REG] ("What E1 can and cannot do"). What changed is listed at the end.

---

## <date of append> · [REG] E1: the closed-loop cache-off sweep of L1 at 350 W, which measures the 8-turn closed-loop cold floor (GPU, ≈ 2.1 h)

- **ID:** E1 (step E1 of `docs/experiment-plan.md`, "Stage 2, revised"). Runs after REG-19's queue has ended: the committed log holds an [OPS] entry headed `REG-19: the queue ended (QUEUE DONE)` or `(QUEUE END futility stop)`, which quotes the queue's `QUEUE DONE` or `QUEUE END` line, or REG-19's [RESULT], and REG-19's queue lock does not exist (FILE(docs/probe/20261113_e1/ops/common.sh:98-108)). It needs no REG-19 result. That entry exists: FILE(docs/decisions.md:4611) (commit 302d431, headed `[OPS] REG-19: the queue ended (QUEUE DONE)`, quoting `QUEUE DONE (all five seeds run). Next: final.sh, once`), which restates FILE(docs/decisions.md:4571) and records no new event. REG-19's [RESULT] has since been written as well (FILE(docs/decisions.md:16517), commit 6748c26), and its heading also matches the gate (DERIVED: `END19_PAT`, FILE(docs/probe/20261113_e1/ops/common.sh:38), against that line). A `QUEUE STOP` leaves no such entry: REG-19 then waits for the owner, and E1 waits with it. The owner's entry on E1 forbids only a run while REG-19's queue holds the GPU (FILE(docs/decisions.md:4520)). REG-19's pin rule says more: "The VM stays at `a7bb77a` with a clean tree until REG-19's [RESULT] is written" (FILE(docs/drafts/reg19_resume_decision_draft5.md:41), approved by the owner as part of that plan, FILE(docs/decisions.md:4287), and kept unchanged by FILE(docs/decisions.md:4400)). **That clause is now met:** REG-19's [RESULT] is written (FILE(docs/decisions.md:16517)), from the table that `final.sh` computed on the Mac from the worktree at `a7bb77a` (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:2); its output committed in 047b95e), which needed nothing of the VM's tree. So the VM may leave `a7bb77a` under the pin rule as written. Draft 6's amendment of that clause (under the delegation's "the pin rule", FILE(docs/decisions.md:4233)), which let the VM leave before REG-19's [RESULT] so that the GPU would not sit idle (the owner: "whenever its available use it", FILE(docs/decisions.md:4506)), is dropped: nothing is left for it to amend. An owner's entry that stops E1 is seen by the scripts only when it is headed as the owner's halt (the stopping rule, FILE(docs/probe/20261113_e1/ops/common.sh:104)); an entry of any other form is applied by hand: no queue start and no launch after its commit. **The VM then leaves REG-19's pin** `a7bb77a` for this entry's commit (`vm_checkout.sh`), or, if REG-20 arm A runs first ("E1 holds the VM"), the commit REG-20 left it at; `vm_checkout.sh` moves it only forward, from a commit that is an ancestor of E1's, and otherwise refuses for the owner (FILE(docs/probe/20261113_e1/ops/vm_checkout.sh:33), after draft 7's script patch). REG-19's launch refuses any other tree (FILE(docs/probe/20261113_reg19/ops_r3/launch.sh:45)), so a later REG-19 rerun, if the owner allows one, needs the VM moved back first: only while no tmux session `run` exists, by RUNBOOK §4's steps with `git checkout --detach a7bb77abc863adcaad9d4516815a5ddddf2908e9`, recorded in an [OPS] entry; E1's next pre-launch read then stops on the tree (no attempt spent), and `vm_checkout.sh` later moves it forward again (a7bb77a is an ancestor of E1's commit); nothing of REG-19 is lost: `vm_checkout.sh` changes no file under `runs/` (gitignored and untracked), so REG-19's folders on the VM stay as they are, including those only the VM holds (ops_r3 copies valid runs only, FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:54-60); the lost seed-18 folder is copied after REG-19's [RESULT], FILE(agent/RUNBOOK.md:48), which is now written). RUNBOOK §4's "never before REG-19's [RESULT]" is met now that the [RESULT] is written; this entry's commit amends `agent/RUNBOOK.md` for E1 as the section "RUNBOOK, for the approval commit" below says. The move back is not covered by this entry's approval: it needs its own entry, as the REG-19 rerun it serves does.
- **Owner's choice (2026-11-12, logged in decisions.md 2026-11-13 [CORR]):** "Floor only": E1 carries no K3 test.
- **Question:** what does the saturated L1 server complete per second with caching off when turns are closed-loop?
- **Claim served:** K2 (`docs/claims.md`), as a measurement: the 8-turn closed-loop floor, so that 1.681 req/s (RUN(REG-8's 7 cache-off runs, `sweep_l1pl350_pc_off`, gate.reg8_zone)) is written as "the open-loop floor" only and closed-loop margins are stated against a closed-loop floor.
- **What E1 can and cannot do (rule A1), said first:** E1's floor is K2's 8-turn reference: the denominator of the 8-turn window ratio that E0's gate compares the 16-turn ratio against (FILE(docs/experiment-plan.md:427-428); FILE(docs/decisions.md:4040); FILE(docs/claims.md:56)). As committed, `k2.decide` takes it as `f8` in R = (warm16/f16)/(warm8/f8) and returns "missing" (no matrix) when it is undefined (FILE(analysis/k2.py:102-109)), and `k2.observed` computes it from E1's runs (FILE(analysis/k2.py:179)). The draft-3 rule F review argued that the label is set by the 16-turn cache-on sweep alone; that is an argument about a gate that is not registered (BELIEF until E0's [REG] shows it), and it does not hold for E1's outcomes without a floor, which make the committed label "missing". So E1 can change the 16-turn matrix decision and K2's "does not widen" reading, through E0. E1 runs before E0 is registered, which departs from "E0 … registers … the gate factor before any sweep (rule G)" (FILE(docs/decisions.md:4040)). To keep rule A5 for E0's gate, no part of E1's floor (status, value, n, rates, slope) is computed, quoted or used before E0's [REG] is committed, or before an entry records that E0's gate takes no input from E1's runs. E0's registration discloses the one bit per rate that the allowed reads show (stopping rule, first bullet), and takes E1's floor as E1's [RESULT] reports it (the registered code, "holes" included), not recomputed by another rule (`k2.observed` calls `e1.floor` without `first_valid` or the swept rates, FILE(analysis/k2.py:179)). Apart from E0's gate, E1 is proposed as K2's measurement and as the floor every closed-loop margin in the paper is quoted against, and for nothing else. Rule A1 and `docs/process.md` §3 say a run whose outcomes change no decision is not proposed. The owner has decided otherwise for this run: the L1 closed-loop cache-off sweep "is run in any case" (FILE(docs/decisions.md:4037)), "run whatever step B finds" (FILE(docs/decisions.md:4040)), and the owner sent E1 to review with this paragraph's content stated (FILE(docs/decisions.md:4520)). The decisions E1's outcomes do change are E0's gate input (above) and the wording ones under "Decision under each outcome". E1's validity record changes one more, about other runs on this harness (the same section, "In neither case").
- **Config:** `configs/sweep_l1pl350cl_pc_off.yaml` (committed, unused). It is REG-8's cache-off sweep (seed 0, 900 s per rate, warm-up 240 s, drain 300 s) with REG-13's two changes, closed-loop turns and `loadgen_force_close: true`, at REG-8 part b's rates [1.5, 2, 2.5, 3, 3.5, 4]. At every rate the planned schedule equals REG-8's (FILE(tests/test_e1.py), `test_e1_schedules_equal_reg8_part_b_at_every_rate`). The longest prompt is 3968 tokens (DERIVED: 2176 + 7 × 256).
- **Single-rate configs** (`configs/sweep_l1pl350cl_pc_off_only_r<rate>.yaml`, six, committed, unused): each expands to the sweep's own run at that rate and nothing else (FILE(tests/test_e1.py), `test_each_single_rate_config_is_the_sweeps_own_run_at_that_rate`: one run each, equal to the sweep's own run at that rate in every key but `sweep`). They exist so that every run E1 can ever need is in the commit that holds this registration.

### The harness E1 runs on: the first GPU run since `5ee6e38`
- **Facts.** REG-19 runs at `a7bb77a` (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:11)). E1 runs at this entry's commit, whose harness includes `5ee6e38`: a recorder that survives a half-written line and logs its death, stricter `recorder` and `gpu_steady` checks, and a session cap in the load generator that is off unless `workload.sessions.cap` is set (FILE(docs/decisions.md:4200) for the recorder and checks; FILE(docs/decisions.md:4209) for the session cap). E1's configs set no cap (DERIVED: `workload.sessions.cap` is absent from the expanded config of every rate of the sweep and of the six single-rate configs). `git diff --stat a7bb77a 9e249b1 -- harness/` gives 4 files, 163 lines in and 29 out; `pyproject.toml` and `uv.lock` are the same at both. The reviewed harness is the one that runs: `git diff --quiet 9e249b1 <registered commit> -- harness/ pyproject.toml uv.lock .python-version configs/defaults.yaml configs/base.yaml configs/gap5_base.yaml configs/l1_base.yaml configs/l1_pl350_base.yaml configs/sweep_l1pl350_pc_off.yaml configs/sweep_l1pl350cl_pc_off.yaml 'configs/sweep_l1pl350cl_pc_off_only_r*.yaml'` exits 0, and the approval entry quotes it; otherwise the registration goes back to rule F. No GPU run has used this harness yet (FILE(docs/decisions.md:4201): "Nothing is deployed to the VM"; REG-19's launches require `a7bb77a`, FILE(docs/probe/20261113_reg19/ops_r3/launch.sh:45)).
- **Risks, and how this entry bounds them** (DESIGN_NOTES.md, R1–R6):
  - R1, a fault that crashes a run: it leaves a folder without `checks.json`, and E1 stops there (the stopping rule). Cost: at most one run.
  - R2, a fault that fails `recorder` on every run without crashing: the six sweep rates come back invalid after about 2.1 h. **The queue pauses after any invalid run** (each invalid run is written to `state/pause_pending.txt` when its launch log is settled; no launch, by the queue or by hand, proceeds until a queue start has printed it and set it aside, so another stop in between does not consume the pause; starting the queue again then applies the rerun rule; `common.sh`'s `settle` writes it before its settle record, so a queue that dies after settling still pauses (round 2, DC-O1); `queue.sh`'s `launch` branch; `launch.sh`), and a check in `failed` of two of E1's runs stops E1 (the stopping rule), so a systematic failure costs the sweep's 2.1 h and no rerun.
  - R3, `gpu_steady` is no longer only heat: since `5ee6e38` it also fails when the GPU samples do not cover [warm-up, duration] with no gap above `max_scrape_gap_s` = 2.0 s, or when no sample is busy (FILE(harness/checks.py:127), FILE(configs/base.yaml:55)). E1 reads only the names in `failed`, so it cannot tell a coverage failure from heat; **either one gets the heat rule's single rerun and counts toward "a second heat failure stops E1"**. That is stricter than a rule for heat alone, never looser. The [RESULT] names each `gpu_steady` failure "heat, SM-clock steadiness or sample coverage" until its detail is read (the fields listed under "In neither case"), then says which.
  - R4: the recheck of 182 folders under the new checks (FILE(docs/decisions.md:4205)) shows that the old recorder's output passes them, not that the new recorder produces such output on the GPU.
  - R5: E1's floor is compared with REG-8's 1.681 req/s, measured under the harness of 2026-11-07 ("Confounds, named").
  - R6: this is the first move of the VM off `a7bb77a` since REG-19 began (the ID line), unless REG-20 arm A runs first ("E1 holds the VM").
- **Not done:** a smoke run on the new harness before E1. It would be a GPU run with its own registration; the pause bounds R2 to the sweep's 2.1 h before a person looks, which this entry accepts.
- **The harness is frozen meanwhile** (disclosed; rule F round 2, "Bundle and limits"): `harness/checks.py`, `run.py`, `recorder.py`, `loadgen.py` and the other harness modules E1 runs on are among REG-21's and REG-22's frozen files (FILE(docs/decisions.md:9834), FILE(docs/decisions.md:4748)) until both batch 2s are computed or declared not computed (expected on 2026-11-13/14). A harness fault that E1's validity record finds ("In neither case") cannot be fixed before then. That freeze has since ended: both batch 2s are computed and their [RESULT]s committed (FILE(docs/decisions.md:16571), FILE(docs/decisions.md:16798), commit 7230ae8), so this disclosure is moot and is kept as a record.

### What is measured: the closed-loop cold floor (`e1.floor`)
- **Rule:** `gate.cold_floor` with REG-8's settings (mean KV ≥ 0.85, at least 2 runs, throughput < 0.95 × planned rate).
- **Registered fallback:** if and only if that rule returns "not_monotone", `e1.floor_tail`: λ_sat is the lowest rate from which every row is saturated, and the floor is the mean over those rows, from at least 2. Its status is "tail_ok", "tail_too_few" or "tail_unsaturated", so a fallback floor cannot be mistaken for the rule's own. Where it matters: the 1.5 row plans 1.606 req/s, so it counts as saturated only below 1.526 (DERIVED: 0.95 × 1.606).
- **Holes:** a swept rate with no valid run gives the status "holes" and no floor when it lies at or above λ_sat, or below λ_sat with no valid row between it and λ_sat (λ_sat could lie there; with no valid row below λ_sat, every swept rate below it without a valid run is such a hole). A row with a non-finite rate, throughput, planned rate or KV mean, which `gate.cold_floor` drops, counts as no valid run. The missing rates are listed.
- **Two valid runs at one rate** (a rate launched again by mistake): the earliest counts (`e1.first_valid`; run ids start with their launch time); the later ones are listed by name.
- **No rows at all** gives "no_rows", and the commands raise: a sweep that was not read is not a sweep that did not saturate.
- **A floor exists** only with status "ok" or "tail_ok". The result reports n and the rates used, and labels the floor "single seed (seed 0), one run per rate": no seed-to-seed spread is measured, and the SE of `floor_slope_reported` is across rates, not seeds (rule H). The floor pools its rows under REG-8's assumption that a saturated cache-off server completes requests at one rate whatever the offered load. E1's own prediction says closed-loop rows break that assumption by a slope of about 0.04 req/s per req/s (FILE(tests/test_e1.py:59), BELIEF as to the model), so the result states the assumption beside the floor, with the slope as the evidence on it.

### Prediction (BELIEF)
P(status "ok") ≈ 0.75; P("tail_ok") ≈ 0.2; floor 1.70 to 1.80 req/s. Model F's replay of E1's config at 1.681 over rates ≥ 2.0 gives 1.744 (fixed cost) or 1.771 (proportional) (`k2.closed_loop_floors`, DERIVED; model BELIEF). The closed-loop cold spans on record point the same way: 1.73 to 1.81 req/s at λ = 2.0 and 2.2 (RUN(20261110-182920_burst_l1pl350cl_r2.0_s2, gate.reg17_gate), RUN(20261110-063647_burst_l1pl350cl_r2.2_s2, gate.reg14_gate)). The status figures assume a valid run at every rate. **E1's validity record** (the decision under "In neither case"; rule A1 asks for a number): P(clean: every launched run ends with a `checks.json`, and neither `recorder` nor `gpu_steady` is in any run's `failed`) ≈ 0.7; P(not clean) ≈ 0.3, of which a run lost to a power-off ≈ 0.2 and a `recorder` or `gpu_steady` failure ≈ 0.1. BELIEF: the VM went off twice during REG-19's runs, at 15:51 UTC on 2026-11-12 and at 04:39 UTC on 2026-11-13, and every boot end the journal keeps was a power-key press (FILE(docs/decisions.md:4383); open question A18); no run of REG-8's cache-off sweep failed a check (FILE(docs/decisions.md:1744)), and the recheck of 182 folders under the new checks changed no valid verdict (FILE(docs/decisions.md:4205)), but no GPU run has used the new recorder.

### Decision under each outcome (rule A1)
- **A floor ("ok" or "tail_ok"):** the paper and `docs/model.md` may quote it as the closed-loop cold floor at 8 turns, with its status, n and rates; closed-loop margins (λ ÷ floor) are restated against it, each with the floor's rates and the slope of throughput on rate over them (`floor_slope_reported`, with its SE; reported, never judged), and, at λ = 2.0, also against E1's own 2.0 row (one run, labelled as such). Closed-loop throughput is predicted to rise with the rate (the served mix tilts toward early, shorter turns; FILE(tests/test_e1.py:59), BELIEF as to the model), so the floor is a mean over a rate range, not a constant of the server. Each such edit is its own decision.
- **No floor:** K2's 8-turn closed-loop floor is reported as unmeasured on this grid; closed-loop margins keep the open-loop floor, named as such. A new grid is a new registration. Under E0's gate as committed, the label is then "missing": no 16-turn matrix, the owner decides (FILE(analysis/k2.py:94-95,102-103)).
- **In neither case** does E1's floor start, stop or size a run other than through E0's gate ("What E1 can and cannot do", which is why that paragraph comes first). **E1's validity record is another matter:** it is the first GPU evidence on `5ee6e38`'s harness (with the session cap off, so the cap's path is not exercised). If `recorder` or `gpu_steady` is in `failed` of any E1 run, or a run ends without `checks.json` on an unchanged boot id, no registration runs on this harness until the cause is found and recorded in an [OPS] or [CORR] entry. After E1's queue has ended (it printed `QUEUE DONE` or `QUEUE END`, or stopped on a rule that ends E1: `no_errors` or `power_limit` in a run's `failed`, a second `gpu_steady`, one check in `failed` of two runs, or the owner's halt), and only for the runs that have that check in `failed`, only these fields of a failed check may be read for that: `recorder`'s `first_ok_scrape_t`, `last_ok_scrape_t`, `end_ref_t`, `end_ref`, `recorder_died`, `max_gap_s`, `failed_scrapes`, `counter_decreases`; `gpu_steady`'s `window_max_gap_s`, `window_samples`, `busy_samples`, `busy_sm_clock_cv`, `hw_throttle_samples`, `sw_thermal_frac`, `max_temp_c`, or its detail text when the detail is not a dict ("no gpu.jsonl data"). These are every input of the two checks' pass conditions (FILE(harness/checks.py:106-110,134-138)). None of them holds a request count, throughput or KV. Disclosed: `end_ref_t` is the time of `load_end`, which comes early for a run whose sessions all ended before the drain deadline, and `busy_samples` counts the samples with the GPU at least 50 % busy. For a failed run, both show the same one bit per rate as the stopping rule's first bullet, and no more. `end_ref_t` and `last_ok_scrape_t` show when that run's load ended, so they carry the same one bit per rate as the run ids (the stopping rule, "Disclosed"). The read is one command that prints these fields and nothing else; the command and its output are quoted in the [OPS] or [CORR] entry that records the cause, and the [RESULT] lists every such read. If every run is valid, the next registration on this harness cites E1's run ids for R4.

### Reported, never judged
- The served-mix tilt against REG-8 (`e1.tilt`, over the rates both sweeps have from their common onset), with `e1.prediction` as its description. Round 1 showed it is the same for any saturated closed-loop server, so it cannot test model F.
- The uncached-token work rate U of both sweeps' saturated runs (`e1.work_rates`, REG-21's statistic). On REG-8's runs that is REG-21's reference, so **`e1.report` raises until REG-21's first [RESULT] is in `docs/decisions.md`**, and E1's result is computed after it. If an entry withdraws REG-21, E1's result is the worktree floor and `e1.observed()` without the work rates, by a [DECISION] entry made before it is computed. REG-21's first [RESULT] (batch 1) is now in the log (FILE(docs/decisions.md:16421)), under a heading that `withheld.lifted("[RESULT] REG-21")` accepts (DERIVED: its pattern, FILE(analysis/withheld.py:46), against that line), so this wait is met; the wait for E0's [REG] ("Result, computed once") remains.
- Preemptions per second and the mean running batch of E1's saturated runs beside REG-8's (the review's alternative to the mix: a different running batch in closed loop).

### Confounds, named
E1 opens a new connection per request and REG-8 did not. REG-8 ran on 2026-11-07 under the code of that day; E1 runs under this entry's (the recorder fix, the stricter `recorder` and `gpu_steady` checks and the load generator's session cap, off here, of 2026-11-12; "The harness E1 runs on"). Both sweeps run their rates in ascending order, so drift within a sweep enters any slope. The 900 s per rate includes the transient. All of these touch the comparison of E1's floor with 1.681 and the reported tilt; none can be removed by E1.

### Stopping rule (REG-13's, completed)
- **One harness invocation of the sweep** (`configs/sweep_l1pl350cl_pc_off.yaml`), launched at most once ever; if it fails before its first rate starts, every rate counts as never started. No interim look at any rate's throughput, KV or floor before the result is computed. Disclosed: the allowed reads still show one bit per rate. Run ids carry their launch time, and a run whose sessions all ended before the drain deadline ends early, so the gaps between consecutive run ids of the sweep, and a single-rate run's `LAUNCHED`/`ENDED` times, show whether the server kept up with that rate. No step of the stopping rule uses this, and the [RESULT] says so.
- **Attempts.** A rate's attempts are 1 if the sweep started it (the sweep's launch log has a `run_id` line for it) plus each single-rate launch of it; every launch is one attempt, whatever it left behind.
- **A rate the invocation never started** (the VM went off, the harness stopped): it is run from its single-rate config. That is its first attempt, not a rerun.
- **An invalid rate** is rerun unchanged from its single-rate config, at most twice. A heat-invalid run (`gpu_steady`) once, after cooling to ≤ 45 °C; a second heat failure stops the sweep. A client error (`no_errors`) or a limit other than 350 W (`power_limit`) in a run's `failed` stops it. Every launch of a rate is one attempt, at most three; a run that ends without `checks.json` stops the sweep until a new decision. **"Stops the sweep" stops E1:** no further launch at any rate; E1's result is then computed from the runs made. A pre-launch check that fails (the limit read, the temperature after 30 min, a compute process, a tmux session, the tree, `uv.lock`, the boot id, free disk) is not such a stop: it launches nothing, spends no attempt, and the queue is started again once the cause is removed (after a reboot: 350 W set and a `RENEW=1` session probe recorded in a decisions entry). A second heat failure is counted over all of E1's runs, not per rate. Likewise any other check (not `gpu_steady`, `no_errors` or `power_limit`) that is in `failed` of two of E1's runs, at any rates, stops E1: on the first GPU runs of a new harness a check that fails twice is a question about the harness, not a rerun. Any `no_errors` in `failed` stops E1 (the details that would separate a client error from another are not read). A launch whose log names no run (no `run_id` line: its command failed, or the harness stopped before its first folder) spends its attempt; a second such launch, at any rate, stops E1 for a new decision. A rate whose three attempts are spent is not launched again; the other rates still run, and the queue ends with `QUEUE END`, naming the rates without a valid run ("holes"). **After any invalid run the queue pauses** ("The harness E1 runs on", R2). **The queue is started again only if no check name stands in `failed` of E1's runs at two or more different rates;** otherwise E1 stops for a new decision, since one failure at several rates points to the harness's first GPU use (R2) or to the cell, and an unchanged rerun would repeat it. The check is made from the queue's `RUN … INVALID failed=…` lines alone, and each restart is recorded in an [OPS] entry that quotes those lines. The scripts enforce this restart rule and are stricter than it in one case: a check other than `gpu_steady`, `no_errors` and `power_limit` in `failed` of two runs at one rate stops E1 (`MAX_SAME`, FILE(docs/probe/20261113_e1/ops/common.sh:24,267-269), lines after draft 7's script patch), where this restart rule would allow a restart; `gpu_steady` in two runs stops by the heat rule, at one rate or two, and one `no_errors` or `power_limit` stops at once. So every case this restart rule stops, the scripts stop too, before any launch. Two valid runs at one rate: nothing is launched and both are listed, the earliest counting. A folder that no launch log of these scripts names, a named run missing from the VM, or a run made at another commit (read from the harness's start line, which holds `run_id` and `git_commit`, FILE(harness/run.py:143), printed by FILE(harness/run.py:80)) stops E1 for the owner. Every run with a `checks.json`, valid or invalid, is copied and checksum-verified; a run without one is copied by a separate step. No E1 run is removed from the VM before E1's end entry (the queue stops when the Mac holds an E1 folder that the VM does not list, FILE(docs/probe/20261113_e1/ops/common.sh:224-226)).
- **A rerun decision reads only the fields `valid` and `failed` of `checks.json`.** The details in that file (counts of ok and unfinished requests) are outcome data and are not read.
- **Reads allowed while diagnosing a stop:** `tmux has-session`, folder names, `valid` and `failed`, and in a launch log only the lines holding `run_id` or `[run] checks`.
- The owner halts E1 by an entry headed `## <date> · [DECISION] (owner) E1 halted`; no launch follows its commit.
- **E1 holds the VM** from `vm_checkout.sh` until its end is recorded by an entry headed `## <date> · [OPS] E1: the queue ended (QUEUE DONE)`, `## <date> · [OPS] E1: the queue ended (QUEUE END)`, or `## <date> · [OPS] E1 ended by a stop: <the stop line>` (a stop that an entry has decided ends E1). A pause, or a stop that waits for a decision, is not an end. Until the end entry, no other registration's run is launched, and the VM's tree is moved only by E1's scripts or under an owner's entry. The approval commit amends RUNBOOK §5's order to match: E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry ([OPS] … the queue ended …, or … ended by a stop …). If REG-20 arm A runs first, E1's `vm_checkout.sh` is not run, and E1's queue is not started, before REG-20's end entry; E1's scripts do not read REG-20's entries, so this is kept by hand (E1's pre-launch checks still refuse a launch while a compute process is on the GPU or the VM's tree is not E1's commit, "Pre-launch and launch").
- **The VM's tree** is clean at the commit that holds this registration's approval. That commit already holds the single-rate configs, so no later commit is needed for a rerun. The scripts recognise the approval only by a heading of the form `## <date> · [DECISION] (owner|delegate) E1 approved` after this entry, at the commit named in `docs/probe/20261113_e1/ops/e1_commit.txt` (FILE(docs/probe/20261113_e1/ops/common.sh:40)); from then on they refuse if any of them differs from its text at that commit.

### Withheld until the [RESULT] of E1
The sweep's run folders (`*_sweep_l1pl350cl_pc_off_r*`; `analysis/withheld.py`, seal "E1").

### Result, computed once
After every rate has a valid run or the stopping rule has ended, after REG-21's first [RESULT], and after E0's [REG] is committed or an entry records that E0's gate takes no input from E1's runs ("What E1 can and cannot do"; no computation in this section, and no `e1.observed`, `e1.floor_status` or `k2.observed` on E1's runs, runs before then): `AFTERSHOCK_UNSEAL=E1 uv run python -m analysis.e1 floor`. It prints `e1.report`: the floor with its status, n, rates, the slope of throughput on rate over those rates with its SE (`floor_slope_reported`) and any later valid run not counted; the open-loop floor recomputed by `gate.cold_floor` with REG-8's settings (`e1.saturated`, as REG-8 computed it: no tail fallback and no holes check); the common onset; the tilt (`tilt_reported`); the work rates of both sweeps. The tilt's model-F description, `e1.prediction()`, reads no run. `e1.report` does not print it; it is quoted beside the tilt from `python -c 'import json; from analysis import e1; print(json.dumps(e1.prediction(), default=str))'`, run from the same code. The tilt is present only when `gate.cold_floor` gives "ok" on both sweeps, since otherwise there is no common onset; the prediction is computed once, beside the result, with `uv run` before that command, and reported as the tilt's description. From committed code, with `analysis/` and `tests/` clean and `uv run pytest` passing; the [RESULT] names the commit. **The code is the registered code:** the files printed by `python3 docs/probe/20261113_freeze/closure.py --at <registered commit> analysis/e1.py` (24 .py files and three environment files at e87884d; the output is quoted in the approval entry) are unchanged from the registered commit to the commit the [RESULT] names, except for rows added to `analysis/withheld.py`'s `SEALS`; the [RESULT] quotes `git diff --stat <registered commit> <its commit> -- <those files>`. Any other change is a [CORR] entry made before the result is computed, and the result then reports `e1.observed()["floor"]` from both codes, the registered code's first (the worktree computation below, whose `runs/` is a real directory holding links to E1's and REG-8's cache-off sweep folders only, as REG-19's `links_ok` builds its own, FILE(docs/probe/20261113_reg19/ops_r3/common.sh:88-102); never a link to the whole of the Mac's `runs/`: the registered code's `analysis/withheld.py` does not know seals added after the registered commit, and `gate.sweep_rows` loads every run folder it can see, FILE(analysis/load.py:41-44)). **The floor is also computed from the registered code** (`agent/RUNBOOK.md` §5): from a worktree at the commit that holds this entry's approval (`git worktree add --detach ../aftershock-e1-pin <commit>`), with the run folders `*_sweep_l1pl350cl_pc_off_r*` and `*_sweep_l1pl350_pc_off_r*` of the Mac's `runs/` linked into its `runs/`, run from its root with the repo's interpreter: `AFTERSHOCK_UNSEAL=E1 /Users/chalshik/Projects/aftershock-artifacts/.venv/bin/python -c 'import json; from analysis import e1; print(e1.__file__); print(json.dumps(e1.observed()["floor"], default=str))'` (the floor needs no REG-21 statistic). The printed path must lie in the worktree. The worktree's floor (status, n, rates, value) is E1's floor; if the result commit's differs in any of these, the [RESULT] reports both and names the commits between the two that touch `analysis/`. The two rules give one order: with the frozen files unchanged both computations run the same code, and after a [CORR] that changed them the registered code's floor is E1's floor and is reported first.

### Pre-launch and launch (`docs/probe/20261113_e1/ops/`, reviewed with this text)
As REG-19's resume, with the differences DESIGN_NOTES.md lists: a session probe once per boot (boot id, driver 595.99.02, the VM's tree and `uv.lock` at the registered commit, 350.00 W read, not set by the launch; a renewal needs a decisions entry); before every launch a read-only check of the limit, temperature ≤ 45 °C (waiting up to 30 min, which spends no attempt), an idle GPU, no tmux session, the tree, `uv.lock`'s blob, free disk and the boot id; an attempt record written immediately before the launch command; validity read from `checks.json`'s `valid` and `failed` only (`vm_state.py`); a valid run found on the VM is used, not relaunched; copies checksum-verified, one run at a time. The VM moves from `a7bb77a` (or from REG-20 arm A's commit, if that runs first: "E1 holds the VM") to the registered commit by `vm_checkout.sh` (detached HEAD, its output saved and committed with an [OPS] entry). **The owner must set 350 W** unless a sudoers rule for `nvidia-smi -pl 350` exists by then. Run order: `README.md`, "Run order".

### Cost
6 runs × (900 + 300 + about 60 s) ≈ 2.1 GPU h (DERIVED: every rate's planned schedule ends at 900 s, so a saturated closed-loop run lasts to its 1200 s deadline; REG-8 part b's saturated runs started 21 min apart, FILE(docs/decisions.md:1745-1751)); ≈ 4.2 h with one rerun per rate; at most 18 runs, 6.3 h (DERIVED: 6 × 3 × 1260 s), and with the systematic-fault stop at most the sweep and a few runs when one check fails throughout. Waits for ≤ 45 °C before a launch (up to 30 min each) keep the GPU idle and are not counted. Every other stop only lowers that ceiling.

### Code and tests
`analysis/e1.py` (`floor`, `floor_tail`, `first_valid`, `swept_rates`, `floor_status`, `saturated`, `onset`, `observed`, `report`; reported only: `tilt`, `fit`, `prediction`, `replay_rows`, `work_rates`, and `observed`'s `floor_slope_reported`); `tests/test_e1.py`, 16 tests; the seal test in `tests/test_withheld.py`. `work_rates` gives, beside U, the running batch, waiting line, KV, preemptions per second and the redo proxy of each saturated run.

### Adversarial review (rule F, `docs/process.md` §3), verbatim

> # rulef-e1-draft5-r1 (rulef-e1-r1), verbatim
> 
> Saved by the agent from the reviewer's own final text (its session a7b61c6b, line 558, timestamp 2026-11-13T21:19:16.276Z), which the reviewer ended its turn with and did not send by SendMessage, so it never reached the main session (checked by the agent on 2026-11-13 21:33 UTC: no SendMessage call in that session). The rule F round 1 on E1 draft 5 (bundle e1_r1).
> 
> ---
> 
> Rule F review, round 1, of E1 draft 5 (bundle `docs/drafts/review_bundles/e1_r1/`)
> 
> **Verdict: NOT READY.** Twelve required items, DA1 to DA12. Three of them change code (DA1, DA2, DA6). The rest are text. Two script defects are confirmed in a scratch copy of the sandbox: a harness fault that fails one check on every run can spend 6.3 GPU h with no automatic stop (DA1), and the pause after an invalid run is lost if the queue stops for any other reason first (DA2). Both fixes were applied in the scratch copy and pass.
> 
> **Bundle and limits**
> - MANIFEST: 28 of 28 sha256 lines OK.
> - The bundle's scripts, `e1.py`, `test_e1.py` and draft 5 are byte-equal to the repo's files at e87884d (cmp).
> - `harness_diff_a7bb77a_to_HEAD.diff` equals `git diff a7bb77a e87884d -- harness/`.
> - Nothing under `runs/` was opened beyond folder names (`ls runs | grep`, `ls -d` of the two RUN-tagged folders).
> - Nothing under `docs/probe/**/state/` was opened. File names under `docs/probe/20261113_reg19/ops_r3/state/` did appear in git-status output twice: once in the context injected at session start, and once from a `git status --short | head` I ran after the sandbox to confirm the repo was untouched. Only names, no content.
> - I read `agent/RUNBOOK.md` lines 40–56 (§3 items 2–6 and the §4 heading). That file is not on the lead's list and not forbidden; I read it because DESIGN_NOTES cites FILE(agent/RUNBOOK.md:48,50).
> - I did not read `docs/context-pack.md`, `status.md` (beyond the session-start digest a hook put into my context), `model.md`, `claims.md` or `open-questions.md`. That is on purpose: rule F's pass sees the registration and the code.
> - No VM contact.
> 
> **What I ran**
> - The sandbox, in a temp dir under my scratchpad: 170 of 170.
> - A scratch copy of the sandbox with six trace cases: 176 of 176. Output: `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/a7b61c6b-f3e3-42e5-9c96-081c8a6cb2a9/scratchpad/e1r1/sandbox_reviewer.txt`.
> - That copy with the DA1 and DA2 patches and the changed cases: 177 of 177. Output: `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/a7b61c6b-f3e3-42e5-9c96-081c8a6cb2a9/scratchpad/e1r1/sandbox_patched2.txt`.
> - Patches as diffs: `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/a7b61c6b-f3e3-42e5-9c96-081c8a6cb2a9/scratchpad/e1r1/patch_common.sh.diff`, `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/a7b61c6b-f3e3-42e5-9c96-081c8a6cb2a9/scratchpad/e1r1/patch_queue.sh.diff`, `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/a7b61c6b-f3e3-42e5-9c96-081c8a6cb2a9/scratchpad/e1r1/patch_launch.sh.diff`, `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/a7b61c6b-f3e3-42e5-9c96-081c8a6cb2a9/scratchpad/e1r1/patch_test_sandbox.sh.diff`.
> - `.venv/bin/python -m pytest tests/test_e1.py -q -p no:cacheprovider`: 12 passed.
> - `python3 docs/probe/20261113_freeze/closure.py analysis/e1.py`: 24 .py files. `e1.py` is in neither REG-21's nor REG-22's closure.
> - A schedule computation from the configs through `harness.workload.build_schedule`. It reads no runs.
> - Python may have refreshed gitignored `__pycache__` files. Nothing else in the repo was written.
> 
> ---
> 
> ### Required items
> 
> **DA1. A harness fault that fails one check on every run spends 6.3 GPU h; the pause decides nothing**
> - **Trace.**
>   - The new harness fails `recorder` on every run without crashing (R2). For example, the last good scrape comes before `load_end` − 2 s.
>   - The sweep returns six invalid runs (2.1 h) and the queue pauses.
>   - For that stop, README says "Start the queue again; it reruns by E1's rule" (FILE(docs/probe/20261113_e1/ops/README.md:71)). No registered sentence says when not to restart.
>   - Each restart launches one rerun, which fails and pauses again. After 12 restarts every rate has spent 3 attempts: 18 runs, 6.3 GPU h (DERIVED: 18 × 1260 s). The queue prints `QUEUE END` with six holes and there is no floor.
>   - Reproduced in the scratch sandbox: `FAKE_FAIL` on all six rates, restarted at every pause, gives 13 launches (the sweep plus 12 single rates), then `QUEUE END rates without a valid run after 3 attempts: 1.5 2 2.5 3 3.5 4`.
>   - Only `gpu_steady` is bounded (`MAX_HEAT`=2). So R2's sentence "a systematic failure is seen before the reruns spend about 4.2 h more" holds only if someone declines to restart, and that decision is not registered.
> - **Class:** stricter rule, with a code fix.
> - **Text.**
>   - Anchor: `A second heat failure is counted over all of E1's runs, not per rate.`
>   - Replace with: `A second heat failure is counted over all of E1's runs, not per rate. Likewise any other check (not `gpu_steady`, `no_errors` or `power_limit`) that is in `failed` of two of E1's runs, at any rates, stops E1: on the first GPU runs of a new harness a check that fails twice is a question about the harness, not a rerun.`
>   - Anchor: `so a systematic failure is seen before the reruns spend about 4.2 h more.`
>   - Replace with: `and a check in `failed` of two of E1's runs stops E1 (the stopping rule), so a systematic failure costs the sweep's 2.1 h and no rerun.`
> - **Code, `common.sh`** (tested):
>   - After the line `MAX_HEAT=2                                     # ... and the second among E1's runs stops the queue` add:
>     `MAX_SAME=2                                     # E1 (rule F e1_r1): any other check in `failed` of this many of E1's runs stops the queue`
>   - Replace `  local -A NAMED per` with `  local -A NAMED per nfail`.
>   - After the line `      [[ ${NORERUN[(Ie)$f]} -gt 0 ]] && stopper="$f ($parts[1])"` add:
>     `      [[ $f == - || $f == $HEAT || ${NORERUN[(Ie)$f]} -gt 0 ]] || nfail[$f]=$(( ${nfail[$f]:-0} + 1 ))`
>   - After the line `    (( n_heat < MAX_HEAT )) || { MSG="second heat failure ($HEAT) among E1's runs: E1 stops; the owner decides"; return 2; }` add:
>     ```
>         for f in ${(k)nfail}; do
>           (( nfail[$f] < MAX_SAME )) || { MSG="$f is in failed of ${nfail[$f]} of E1's runs: a check that fails twice is a question about the harness, not a rerun. E1 stops; the owner decides"; return 2; }
>         done
>     ```
> - **Sandbox, `test_sandbox.sh`:**
>   - In `case_ "the rerun is invalid again" ...` use `"INVALID failed=arrival_rate" 1 FAKE_FAIL="2:arrival_rate"`.
>   - In `case_ "attempt 3 invalid too: ..."` use `FAKE_FAIL="2:release_chain"`.
>   - In `run FAKE_SWEEP_RATES="1.5 2" FAKE_FAIL="2:recorder" zsh $Q; run FAKE_FAIL="2:recorder" zsh $Q; run FAKE_FAIL="2:recorder" zsh $Q` make the second and third `2:arrival_rate` and `2:release_chain`.
>   - Add:
>     ```
>     reset
>     run FAKE_FAIL="1.5:recorder 2:recorder 2.5:recorder 3:recorder 3.5:recorder 4:recorder" zsh $Q
>     case_ "a check failing on two or more runs stops E1, no rerun" "recorder is in failed of 6 of E1's runs" 1 zsh $Q
>     chk "one launch only" is "$(launches)" 1
>     ```
> - **README stop table:** add the row `| `<check> is in failed of 2 of E1's runs` | The registered systematic-fault stop | The owner |`.
> 
> **DA2. The pause is lost when any other stop comes between the settle and the next launch**
> - **Trace.**
>   - The sweep ends. `report_settled` prints `RUN …_r2 INVALID failed=recorder` and sets the shell variable `PAUSE`.
>   - The next turn's copy of `…_r1.5` fails, giving `QUEUE STOP copy failed`. README says to find the cause and start again.
>   - On restart the settle is already done, so `PAUSE` is empty. The queue copies the runs and launches rate 2's attempt 2 with no pause.
>   - Reproduced: `FAKE_FAIL="2:recorder" FAKE_RSYNC_FAIL=1`, then a plain restart, gives `QUEUE DONE` with 2 launches.
>   - The same happens after a checksum mismatch, a manifest failure, a VM read failure or the lost-run stop. `launch.sh` run by hand also launches with no pause.
>   - So "After any invalid run the queue pauses" and R2's "(it copies what is pending and stops before the next launch …)" are false on this trace.
> - **Class:** code fix.
> - **Code, `queue.sh`** (tested):
>   - Replace `      invalid) echo "RUN $id INVALID failed=$fl"; PAUSE+="${PAUSE:+; }$id failed=$fl";;`
>     with `      invalid) echo "RUN $id INVALID failed=$fl"; print -r -- "$id failed=$fl" >> $ST/pause_pending.txt;;`
>   - Replace `      [[ -z $PAUSE ]] || stop "after an invalid run ($PAUSE). Starting the queue again applies E1's rerun rule from checks.json (valid, failed) alone"` with:
>     ```
>           if [[ -e $ST/pause_pending.txt ]]; then
>             stamp; mv $ST/pause_pending.txt $ST/pause_shown_$REPLY.txt || stop "the pause record could not be set aside"
>             stop "after an invalid run ($(tr '\n' ';' < $ST/pause_shown_$REPLY.txt)). Starting the queue again applies E1's rerun rule from checks.json (valid, failed) alone"
>           fi
>     ```
>   - `PAUSE=""` can stay; it is now unused.
> - **Code, `launch.sh`:** after `next_step || die "$MSG"` add
>   `[[ ! -e $ST/pause_pending.txt ]] || die "an invalid run has not been shown at a pause yet (state/pause_pending.txt): start the queue, which pauses first"`
> - **Sandbox:**
>   - Before `case_ "with lost_ok: the paused rerun of rate 2 goes first, in the sweep's order" "QUEUE DONE" 0 zsh $Q` insert
>     `case_ "with lost_ok: the pause not yet shown comes first" "QUEUE STOP after an invalid run" 1 zsh $Q`
>   - Add:
>     ```
>     reset
>     case_ "an invalid run, then a failed copy" "copy failed" 1 FAKE_FAIL="2:recorder" FAKE_RSYNC_FAIL=1 zsh $Q
>     chk "the invalid run was reported before the stop" is "$(print -r -- $out | grep -c 'INVALID failed=recorder')" 1
>     case_ "the restart still pauses before the rerun" "QUEUE STOP after an invalid run" 1 zsh $Q
>     chk "no rerun launched before the pause" is "$(launches)" 1
>     ```
>   - With DA1 and DA2 together the sandbox passes 177 of 177 (scratch run).
> - **Text.**
>   - Anchor: `(it copies what is pending and stops before the next launch; starting it again applies the rerun rule; FILE(docs/probe/20261113_e1/ops/queue.sh:41))`
>   - Replace with: `(each invalid run is written to `state/pause_pending.txt` when its launch log is settled; no launch, by the queue or by hand, proceeds until a queue start has printed it and set it aside, so another stop in between does not consume the pause; starting the queue again then applies the rerun rule; `queue.sh`, `report_settled` and the `launch` branch; `launch.sh`)`
> 
> **DA3. The text says a pre-launch check ends E1; the scripts and README restart after it**
> - **Trace.**
>   - The VM reboots between two launches. This is likely: per the status file, open question A18 records that five of the seven recorded boot ends fell during a GPU run.
>   - The next pre-launch read sees a new boot id and 420 W, so the launch stops with no attempt spent.
>   - By the text, that is "an unexpected pre-launch check", which "stops E1: no further launch at any rate". E1 then ends with holes, and with no floor if the holes are at or above λ_sat.
>   - By README (FILE(docs/probe/20261113_e1/ops/README.md:75-76)) and DESIGN_NOTES I15, the owner sets 350 W, a `RENEW=1` probe is recorded, and E1 goes on. The scripts allow this.
>   - So whoever reads the stop decides after the fact which rule applies. The same holds for a GPU still hot after 30 min, low disk, or a stray tmux session.
> - **Class:** wording.
> - **Text.**
>   - Anchor: `A client error (`no_errors`), a limit other than 350 W (`power_limit`) or an unexpected pre-launch check stops it.`
>   - Replace with: `A client error (`no_errors`) or a limit other than 350 W (`power_limit`) in a run's `failed` stops it.`
>   - Anchor: `**"Stops the sweep" stops E1:** no further launch at any rate.`
>   - Replace with: `**"Stops the sweep" stops E1:** no further launch at any rate; E1's result is then computed from the runs made. A pre-launch check that fails (the limit read, the temperature after 30 min, a compute process, a tmux session, the tree, `uv.lock`, the boot id, free disk) is not such a stop: it launches nothing, spends no attempt, and the queue is started again once the cause is removed (after a reboot: 350 W set and a `RENEW=1` session probe recorded in a decisions entry).`
> 
> **DA4. The code that computes the floor is not frozen, so the result can move after the data exist**
> - **Trace.**
>   - E1's runs are on the Mac when the queue ends. The [RESULT] waits for REG-21's [RESULT], which may take days.
>   - REG-21's and REG-22's freeze ends at their batch 2. REG-23 is "NOT READY on six items that need code changes" (status digest).
>   - A commit in that window could change `analysis/load.py`'s `window` or `summarize` (the KV mean and the throughput window `gate.sweep_rows` uses, FILE(analysis/gate.py:198-205)), or `gate.cold_floor`.
>   - The text asks only for "committed code … `uv run pytest` passing". The draft-3 review's B3/B4 shows the size of the stake: the 1.5 row's KV at 0.84 against 0.85 moves the floor from 1.725 ("ok") to 1.770 ("tail_ok"), 2.6 %.
>   - `analysis/e1.py`'s import closure is 24 .py files plus `.python-version`, `pyproject.toml` and `uv.lock` (PROBE: `closure.py analysis/e1.py`, run by this review at e87884d).
> - **Class:** stricter rule.
> - **Text.**
>   - Anchor: `From committed code, with `analysis/` and `tests/` clean and `uv run pytest` passing; the [RESULT] names the commit.`
>   - Replace with: `From committed code, with `analysis/` and `tests/` clean and `uv run pytest` passing; the [RESULT] names the commit. **The code is the registered code:** the files printed by `python3 docs/probe/20261113_freeze/closure.py --at <registered commit> analysis/e1.py` (24 .py files and three environment files at e87884d; the output is quoted in the approval entry) are unchanged from the registered commit to the commit the [RESULT] names, except for rows added to `analysis/withheld.py`'s `SEALS`; the [RESULT] quotes `git diff --stat <registered commit> <its commit> -- <those files>`. Any other change is a [CORR] entry made before the result is computed, and the result then reports `e1.observed()["floor"]` from both codes, the registered code's first (run from a worktree at the registered commit whose `runs/` links to the Mac's).`
> 
> **DA5. The ID line's REG-19 sentence is false, and the gate contradicts RUNBOOK §3 item 6 and §4**
> - **Trace (a).**
>   - The text says "nothing of REG-19 is lost, since its runs are copied and verified".
>   - ops_r3 copies valid runs only: only `valid` ids enter `rids`, which the copy loop walks (FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:54-60)).
>   - The lost seed-18 folder is still to be copied "After the [RESULT]" (FILE(agent/RUNBOOK.md:48)). Those folders exist only on the VM.
>   - `vm_checkout.sh` leaves them alone: `runs/` is gitignored and untracked, and `git checkout` keeps untracked files. So nothing is lost, but for that reason, not the stated one.
> - **Trace (b).**
>   - RUNBOOK §4's heading allows a deploy "never before REG-19's [RESULT]" (FILE(agent/RUNBOOK.md:50)). E1 moves the VM before that.
>   - After REG-19's [RESULT], §3 item 6 has the agent "deploy HEAD (§4)" with `git pull origin main`. On E1's detached HEAD that either fails, or, after `git checkout main`, moves the VM off E1.
>   - If E1 is then paused or waiting for a `lost_ok` decision, its next pre-launch read stops on the tree. `vm_checkout.sh` then refuses to move forward again (the VM's commit is not an ancestor of E1's), so the owner must decide.
>   - Two files give contradicting orders (CLAUDE.md D).
> - **Class:** wording and disclosure; RUNBOOK is amended in the registration commit.
> - **Text.**
>   - Anchor: `nothing of REG-19 is lost, since its runs are copied and verified and `runs/` is outside git.`
>   - Replace with: `nothing of REG-19 is lost: `vm_checkout.sh` changes no file under `runs/` (gitignored and untracked), so REG-19's folders on the VM stay as they are, including those only the VM holds (ops_r3 copies valid runs only, FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:54-60); the lost seed-18 folder is copied after REG-19's [RESULT], FILE(agent/RUNBOOK.md:48)). This entry supersedes RUNBOOK §4's "never before REG-19's [RESULT]" for E1's move only, and its commit amends `agent/RUNBOOK.md` to match.`
> - **RUNBOOK.**
>   - Anchor: `## 4. Deploying `main` to the VM (only between items, never during a run, never before REG-19's [RESULT])`
>   - Replace with: `## 4. Deploying `main` to the VM (only between items, never during a run; never before REG-19's queue has ended (E1's gate); never while E1 has not ended: E1 moves the VM only with its own `docs/probe/20261113_e1/ops/vm_checkout.sh`)`
>   - Anchor: `then deploy HEAD (§4);`
>   - Replace with: `then, once E1 has ended (its queue printed QUEUE DONE or QUEUE END, or a stop that ends E1 is recorded), deploy HEAD (§4, after `git checkout main` on the VM, whose HEAD E1 leaves detached);`
> 
> **DA6. The floor is a mean over a rate range, and closed-loop throughput is predicted to rise with the rate**
> - **Trace.**
>   - Model F's replay of E1's config puts the closed-loop throughput slope on rate more than 0.04 req/s per req/s above the open-loop one (FILE(tests/test_e1.py:59), passing; BELIEF as to the model). The draft-3 review found the same tilt for FIFO, LIFO, many slots and superlinear cost.
>   - With rows 2.0–4.0 on a line of slope 0.04–0.06, the floor (their mean) sits 0.04–0.06 req/s, 2.4–3.5 %, above the 2.0 row (DERIVED, synthetic rows in this review: 1.74 or 1.76 against 1.70).
>   - If λ_sat is 2.5, it is 0.01–0.015 higher still. That can happen if the 2.0 row's KV mean stays below 0.85, because a closed loop fills slowly from an empty start just above its floor.
>   - "Closed-loop margins (λ ÷ floor) are restated against it" at λ = 2.0 and 2.2, the operating points, would understate those margins by that much, under the label "the closed-loop cold floor", and nothing in the result would show it.
> - **Class:** reporting duty, with a small code change.
> - **Text (decision).**
>   - Anchor: `closed-loop margins (λ ÷ floor) are restated against it. Each such edit is its own decision.`
>   - Replace with: `closed-loop margins (λ ÷ floor) are restated against it, each with the floor's rates and the slope of throughput on rate over them (`floor_slope_reported`, with its SE; reported, never judged), and, at λ = 2.0, also against E1's own 2.0 row (one run, labelled as such). Closed-loop throughput is predicted to rise with the rate (the served mix tilts toward early, shorter turns; FILE(tests/test_e1.py:59), BELIEF as to the model), so the floor is a mean over a rate range, not a constant of the server. Each such edit is its own decision.`
> - **Text (result).**
>   - Anchor: `the floor with its status, n, rates and any later valid run not counted;`
>   - Replace with: `the floor with its status, n, rates, the slope of throughput on rate over those rates with its SE (`floor_slope_reported`) and any later valid run not counted;`
> - **Code, `analysis/e1.py`, `observed`:** after `           "rows_cl": cl.to_dict("records"), "later_valid_runs_not_counted": dropped}` add:
>   ```
>       lam = res["floor"]["lam_sat"]
>       res["floor_slope_reported"] = fit(cl, "throughput", lam) if np.isfinite(lam) else None   # reported, never judged
>   ```
>   Checked on synthetic rows through the real `observed`: status "ok", λ_sat 2.0, slope 0.04, n 4.
> 
> **DA7. "In neither case does E1 start, stop or size another run" leaves out the one decision E1 can change**
> - **Trace.**
>   - E1 is the first GPU run on 5ee6e38's harness (R1–R4). The session-cap arm (step D) will run on that harness.
>   - If E1's runs have `recorder` or `gpu_steady` in `failed` (both now include coverage), a later registration would be proposed on a recorder known to fail on the GPU.
>   - If every E1 run is valid, R4's gap closes for the cap-off path.
>   - Either way this is a decision about other runs, read from allowed fields.
> - **Class:** wording.
> - **Text.**
>   - Anchor: `- **In neither case** does E1 start, stop or size another run. That is why the paragraph "What E1 cannot do" comes first.`
>   - Replace with: `- **In neither case** does E1's floor start, stop or size another run. That is why the paragraph "What E1 cannot do" comes first. **E1's validity record is another matter:** it is the first GPU evidence on `5ee6e38`'s harness (with the session cap off, so the cap's path is not exercised). If `recorder` or `gpu_steady` is in `failed` of any E1 run, or a run ends without `checks.json` on an unchanged boot id, no registration runs on this harness until the cause is found and recorded in an [OPS] or [CORR] entry. After E1's queue has ended, only these fields of a failed check may be read for that: `recorder`'s `first_ok_scrape_t`, `last_ok_scrape_t`, `end_ref_t`, `recorder_died`, `max_gap_s`, `failed_scrapes`; `gpu_steady`'s `window_max_gap_s`, `hw_throttle_samples`, `sw_thermal_frac`, `max_temp_c`. None of them holds a request count, throughput or KV. If every run is valid, the next registration on this harness cites E1's run ids for R4.`
> 
> **DA8. The allowed reads show, for each rate, whether the server kept up**
> - **Trace.**
>   - Run ids begin with their launch time (FILE(harness/run.py:136)).
>   - In the sweep each run starts when the previous one ends.
>   - The load generator exits as soon as every session chain is done (FILE(harness/loadgen.py:237-239)). So a rate the server keeps up with (1.5 plans 1.606 req/s, below the predicted 1.70–1.80 floor) ends early, while a saturated rate runs to its 1200 s deadline.
>   - REG-8's open-loop 1.5 run lasted 16 min 55 s against about 21 min for the saturated ones (DERIVED from the start times at FILE(docs/decisions.md:1746-1751)).
>   - So consecutive run ids, and a single-rate run's `LAUNCHED`/`ENDED` lines, show one bit of each rate's throughput. At 1.5 that is the bit that separates "ok" from "tail_ok".
> - **Class:** disclosure.
> - **Text.**
>   - Anchor: `No interim look at any rate's throughput, KV or floor before the result is computed.`
>   - Replace with: `No interim look at any rate's throughput, KV or floor before the result is computed. Disclosed: the allowed reads still show one bit per rate. Run ids carry their launch time, and a run whose sessions all ended before the drain deadline ends early, so the gaps between consecutive run ids of the sweep, and a single-rate run's `LAUNCHED`/`ENDED` times, show whether the server kept up with that rate. No step of the stopping rule uses this, and the [RESULT] says so.`
> 
> **DA9. The cost gives no ceiling**
> - **Class:** wording (cost).
> - **Text.**
>   - Anchor: `6 runs × (900 + 300 + about 60 s) ≈ 2.1 GPU h (DERIVED); ≈ 4.2 h with one rerun per rate.`
>   - Replace with: `6 runs × (900 + 300 + about 60 s) ≈ 2.1 GPU h (DERIVED: every rate's planned schedule ends at 900 s, so a saturated closed-loop run lasts to its 1200 s deadline; REG-8 part b's saturated runs started 21 min apart, FILE(docs/decisions.md:1745-1751)); ≈ 4.2 h with one rerun per rate; at most 18 launches, 6.3 h (DERIVED: 6 × 3 × 1260 s), and with the systematic-fault stop at most the sweep and a few runs when one check fails throughout. Waits for ≤ 45 °C before a launch (up to 30 min each) keep the GPU idle and are not counted.`
> - Checked: maximum planned time 899.2–900.0 s at every rate, from `build_schedule` on the configs. 2.1 h and 4.2 h are correct.
> 
> **DA10. Tags**
> - **Class:** tag.
> - `(FILE(docs/decisions.md:4200))` → `(FILE(docs/decisions.md:4200) for the recorder and checks; FILE(docs/decisions.md:4209) for the session cap)`.
> - `E1's configs set no cap.` → `E1's configs set no cap (DERIVED: `workload.sessions.cap` is absent from the expanded config of every rate of the sweep and of the six single-rate configs).`
> - `No GPU run has used this harness yet.` → `No GPU run has used this harness yet (FILE(docs/decisions.md:4201): "Nothing is deployed to the VM"; REG-19's launches require `a7bb77a`, FILE(docs/probe/20261113_reg19/ops_r3/launch.sh:45)).`
> - `FILE(docs/probe/20261113_e1/ops/common.sh:96)` → `FILE(docs/probe/20261113_e1/ops/common.sh:96-104)`.
> - `FILE(harness/run.py:143))` → `FILE(harness/run.py:143), printed by FILE(harness/run.py:80))`.
> - `RUN(the 13 REG-8 runs, gate.reg8_zone)` → `RUN(REG-8's 7 cache-off runs, `sweep_l1pl350_pc_off`, gate.reg8_zone)`. 1.681 comes from those 7 runs (FILE(docs/decisions.md:1744-1752)).
> - All other FILE tags checked and correct: decisions.md:4205, 4516, 4520; ops_r3/common.sh:11; ops_r3/launch.sh:45; checks.py:127; base.yaml:55; common.sh:38. Also DESIGN_NOTES' run.py:136-143, 218, 243, RUNBOOK:48/50, and ops_r3 common.sh:136, vm_state.py:21/32-35, queue.sh:55, launch.sh:76.
> 
> **DA11. The harness that runs is not tied to the harness reviewed**
> - **Trace.**
>   - This review saw the harness at 9e249b1, whose `harness/` tree is e8a3e1e7425da486327884d093055e0846229d38 (the same at e87884d).
>   - The registered commit comes later. The text says only "`git diff --stat a7bb77a HEAD …`", with HEAD unnamed.
>   - A harness commit before registration (for step D, or a REG-23 fix) would run on the GPU unreviewed, as "the first GPU run on 5ee6e38".
> - **Class:** stricter rule.
> - **Text.**
>   - Anchor: `` `git diff --stat a7bb77a HEAD -- harness/` gives 4 files, 163 lines in and 29 out; `pyproject.toml` and `uv.lock` are the same at both. ``
>   - Replace with: `` `git diff --stat a7bb77a 9e249b1 -- harness/` gives 4 files, 163 lines in and 29 out; `pyproject.toml` and `uv.lock` are the same at both. The reviewed harness is the one that runs: `git diff --quiet 9e249b1 <registered commit> -- harness/ pyproject.toml uv.lock .python-version configs/defaults.yaml configs/base.yaml configs/gap5_base.yaml configs/l1_base.yaml configs/l1_pl350_base.yaml configs/sweep_l1pl350_pc_off.yaml configs/sweep_l1pl350cl_pc_off.yaml 'configs/sweep_l1pl350cl_pc_off_only_r*.yaml'` exits 0, and the approval entry quotes it; otherwise the registration goes back to rule F. ``
> - This holds now: exit 0 against e87884d. The config chain is also unchanged since a7bb77a.
> 
> **DA12. Stale comments in the scripts that the registration will freeze**
> - **Class:** wording.
> - `queue.sh:2`: `# E1's queue (registration: docs/drafts/e1_draft4.md until it is registered; README.md).` → `# E1's queue (registration: the [REG] E1 entry in docs/decisions.md; README.md).`
> - `queue.sh:4`: `REG-19's [RESULT] is in the committed log` → `the committed log records REG-19's queue end ('[OPS] REG-19: the queue ended') or its [RESULT],`
> - `vm_checkout.sh:6`: `# before REG-19's [RESULT] is in the committed log, or while REG-19's queue lock exists` → `# before the committed log records REG-19's queue end ('[OPS] REG-19: the queue ended') or its [RESULT], or while REG-19's queue lock exists`
> - `common.sh:3`: `the registration (docs/drafts/e1_draft4.md,` → `the registration (read from draft 4, docs/drafts/e1_draft4.md; registered as the [REG] E1 entry;`
> - `DESIGN_NOTES.md:67`: `- The scripts implement the stricter rule, `RESULT19_PAT`.` (no such variable exists) → `- Draft 5 drops that wait: the scripts wait for an `[OPS] REG-19: the queue ended` or `[RESULT] REG-19` heading (`END19_PAT`) and for REG-19's lock to be absent.`
> - DESIGN_NOTES §2 item 12: `or before REG-19's `[RESULT]` (I11)` → `or before an `[OPS] REG-19: the queue ended` or `[RESULT] REG-19` heading is committed (I11)`.
> - DESIGN_NOTES R6: `RUNBOOK §4 allows a deploy only after REG-19's `[RESULT]` (I11).` → `RUNBOOK §4 allowed a deploy only after REG-19's `[RESULT]`; the registration supersedes that for E1's move and amends RUNBOOK (DA5).`
> 
> ---
> 
> ### Optional items
> 
> **DA-O1. The gate trusts a heading that a QUEUE STOP could carry**
> - **Trace:** an `[OPS] REG-19: the queue ended` entry written by mistake after a `QUEUE STOP` passes `END19_PAT`. The VM then leaves the pin while REG-19 waits for the owner.
> - **Class:** code fix plus heading form.
> - **Code, `common.sh`:**
>   - Anchor: `END19_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · (\[RESULT\] REG-19([^0-9]|$)|\[OPS\] REG-19: the queue ended)'`
>   - Replace with: `END19_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · (\[RESULT\] REG-19([^0-9]|$)|\[OPS\] REG-19: the queue ended \(QUEUE (DONE|END futility stop)\))'`
>   - Tested with grep -E: it matches `(QUEUE DONE)` and `(QUEUE END futility stop)`; it rejects `(QUEUE STOP …)`, a bare heading and `REG-190`. These are ops_r3's two end lines (FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:91)).
> - **Sandbox:** the heading becomes `## 2026-11-15 · [OPS] REG-19: the queue ended (QUEUE DONE)`.
> - **Text (ID line):** `an [OPS] entry headed `REG-19: the queue ended`` → `an [OPS] entry headed `REG-19: the queue ended (QUEUE DONE)` or `(QUEUE END futility stop)``.
> 
> **DA-O2. An owner's overrule cannot be seen by the scripts**
> - **Trace:** the delegation says the owner may overrule a delegate decision by an entry (FILE(docs/decisions.md:4231-4238)). The scripts check the approval only at E1's commit.
> - **Class:** code fix.
> - **Code, `ready_to_run`, first line after `MSG=""`:**
>   `git -C $R grep -q -E '^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[(DECISION|CORR)\] \(owner\) E1 halted' HEAD -- docs/decisions.md && { MSG="the owner halted E1 (a '[DECISION] (owner) E1 halted' heading)"; return 2; }`
> - **Text (stopping rule):** add `The owner halts E1 by an entry headed `## <date> · [DECISION] (owner) E1 halted`; no launch follows its commit.`
> 
> **DA-O3. Register the default for a run lost to a power-off (A18) instead of a new decision each time**
> - **Class:** stricter rule.
> - **Text.**
>   - Anchor: `a run that ends without `checks.json` stops the sweep until a new decision.`
>   - Replace with: `a run that ends without `checks.json` stops the sweep until a new decision; if the VM's boot id changed during it (a power-off), the decision is fixed in advance: the run counts as one attempt, its rate is launched again under the attempt limit once 350 W is set and a `RENEW=1` probe is recorded, and an [OPS] entry and `state/lost_ok_<run id>.txt` record it; on an unchanged boot id (a harness fault, R1) the owner decides.`
> 
> **DA-O4. A hole just below λ_sat goes unreported**
> - **Trace:** 2.0 has no valid run (three attempts spent), 1.5 is valid and kept up, 2.5–4.0 are saturated. `floor()` returns "ok" with λ_sat 2.5 and n 4, although λ_sat lies somewhere in (1.5, 2.5]. Scratch check on synthetic rows: registered code gives `ok`, 1.735; the patch gives `holes`, missing [2.0].
> - **Class:** code fix.
> - **Code, `e1.floor`:**
>   - Anchor: `        missing = [float(x) for x in swept if x >= f["lam_sat"] - 1e-9 and round(float(x), 6) not in have]`
>   - Replace with:
>     ```
>             below = [r for r in have if r < f["lam_sat"] - 1e-9]
>             lo = max(below) if below else f["lam_sat"]
>             missing = [float(x) for x in swept if x > lo + 1e-9 and round(float(x), 6) not in have]
>     ```
>   - The existing holes tests pass unchanged (1.5 missing: ok; 3.0 missing: holes [3.0]).
> - **Text ("Holes"):** add `, or a swept rate between the highest valid row below λ_sat and λ_sat`.
> 
> **DA-O5. Say what a `gpu_steady` failure was**
> - **Class:** reporting duty.
> - **Text, append to R3:** `The [RESULT] names each `gpu_steady` failure "heat or sample coverage" until its detail is read (DA7's fields), then says which.`
> 
> **DA-O6. `report()` counts runs that `first_valid` excludes**
> - **Class:** code fix.
> - **Code:**
>   - Anchor: `    cl, ol = sweep_rows(E1["sweeps"]["cl"]), sweep_rows(E1["sweeps"]["ol"])` in `report`.
>   - Replace with: `    cl, ol = first_valid(sweep_rows(E1["sweeps"]["cl"]))[0], sweep_rows(E1["sweeps"]["ol"])`.
> 
> **DA-O7. Name the move back to the pin for a REG-19 rerun**
> - **Class:** wording.
> - **Text.**
>   - Anchor: `needs the VM moved back first;`
>   - Replace with: `needs the VM moved back first: only while no tmux session `run` exists, by RUNBOOK §4's steps with `git checkout --detach a7bb77abc863adcaad9d4516815a5ddddf2908e9`, recorded in an [OPS] entry; E1's next pre-launch read then stops on the tree (no attempt spent), and `vm_checkout.sh` later moves it forward again (a7bb77a is an ancestor of E1's commit);`
> 
> ---
> 
> ### 3. Strongest alternative explanation for the floor E1 would report
> 
> The floor is the mean, over the saturated rows from λ_sat to 4.0, of ok completions per second in [240, 900). The registration reads it as the closed-loop server's cold capacity. The strongest alternative is that it differs from 1.681, and from the cold throughput at λ = 2.0–2.2, mostly because of what is counted, not because of what the server can do:
> 
> - **The served mix tilts toward early turns.**
>   - Closed loop serves a session's early turns first, and cold prompts grow with the turn (2176 + 256·k tokens). So completions per second rise with the load at a fixed token rate.
>   - Model F puts the closed-loop throughput slope more than 0.04 req/s per req/s above the open-loop one (FILE(tests/test_e1.py:59)). The draft-3 review found the same tilt for any work-conserving server with within-session precedence.
>   - The floor therefore depends on the grid and on λ_sat. Averaged over 2.0–4.0 it sits about 0.04–0.06 req/s above the 2.0 row (DERIVED, synthetic rows), and 0.01–0.015 higher if the 2.0 row's KV keeps λ_sat at 2.5.
>   - Separating evidence: per-row throughput and its slope (DA6), k̄ per row, and U per row against REG-8's (both reported). A flat U equal to REG-8's, with rising req/s, means mix. A different U means the server: running batch, preemptions, a new connection per request, code, or day.
> - **Drift between 2026-11-07 and E1's day at 350 W** (SM clock, thermal state after back-to-back runs) would move the absolute level against 1.681. Separating evidence: each saturated run's busy SM-clock mean against REG-8's, from `gpu.jsonl`. This is not registered; it could join the reported gauges.
> - **The fill transient at the lowest saturated rate** inside the 660 s window. Separating evidence: throughput in each half of the window per row. Not registered.
> 
> ### 4. Can E1 change any decision?
> 
> - **The floor: no run decision.** I agree with the text, and the draft-3 review's label map has the 16-turn question resting on the cache-on sweep alone.
> - **It changes a claim decision:** K2's wording and the paper's closed-loop margins, which the text names.
> - **The text does not name one more:** E1's validity record is the first GPU evidence on 5ee6e38's harness, and the step-D registrations will run on that harness (DA7). With DA7, the answer is yes, one decision. Without it, the sentence "In neither case does E1 start, stop or size another run" is incomplete.
> - **Is it worth 2.1 GPU h?**
>   - On the text's own terms (K2 wording only), weakly. The closed-loop cold throughput at the operating points is already bounded by the two cold spans the text cites (1.73–1.81 at λ = 2.0 and 2.2) and by model F's replay (1.744 or 1.771). E1 would add a sweep mean with a predicted rate dependence and the same named confounds.
>   - With DA7 (the first GPU exercise of the A14 recorder and the stricter checks before step D relies on them), and with the GPU otherwise idle until REG-21's and REG-22's entries are committed, it is worth 2.1 h. DA1 keeps a broken harness from turning that into 6.3 h.
>   - The text's own sentence, "If the owner holds that a measurement that changes no decision should not cost 2.1 GPU h, E1 should not run", stays the owner's call; the owner's 2026-11-13 entry chose to prepare it.
> 
> ### Checked and correct
> - The attempt count from the sweep's `run_id` lines; the sweep launched at most once ever.
> - The global stops (`no_errors`/`power_limit` anywhere, the second `gpu_steady` over all runs).
> - A spent rate does not block the other rates.
> - Two valid runs at one rate: both listed, earliest counted.
> - Unnamed folders, missing named runs and Mac-only folders stop E1.
> - The commit check, from the start line `[run] start {'run_id': …, 'git_commit': …}`. `git_commit` is `git rev-parse HEAD`; a missing value fails safe.
> - Every run with `checks.json` is copied and checksum-verified, one at a time.
> - `vm_state.py` prints only `valid` and `failed`. The launch log is read only through `'run_id': '` lines (no other harness print carries that pattern). `copy_verify` reads bytes, not content. `tools/context_pack.py` reads no runs; `check_docs.py` reads `valid`.
> - The six single-rate configs expand to exactly the sweep's run at their rate (the configs' `sweep` key is the only difference). E1 folders exist on neither the Mac nor the VM side named in the repo (0 matching folder names on the Mac).
> - Moving off a7bb77a does not touch REG-19's data or `final.sh`, which is Mac-only. The harm is limited to DA5(b) and the need for a move back (DA-O7).
> - Treating `gpu_steady`'s coverage failures as heat is sound: it allows one rerun instead of two and adds to the global stop, so it is never looser. The [RESULT] should not call them heat (DA-O5).
> - R5's BELIEF holds on reading the diff: with the cap off, the load generator changes only in bookkeeping and flushing.
> 
> ### Could not check
> - The cold spans 1.73–1.81 and the RUN tags of runs (they need reads beyond folder names).
> - The replay floors 1.744/1.771 (verified by the draft-3 review; not recomputed here, because analysis-module commands are outside my limits).
> - `docs/claims.md` K2 and `experiment-plan.md` step E1.
> - Whether a sudoers rule for `nvidia-smi -pl 350` exists.
> 
> ### 5. Verdict
> **NOT READY.** Apply first: DA1, DA2, DA3, DA4, DA5, DA6, DA7, DA8, DA9, DA10, DA11, DA12.
> - DA1 and DA2 change `common.sh`, `queue.sh`, `launch.sh` and `test_sandbox.sh`. The patches and changed cases were tested at 177 of 177 in scratch; rerun the sandbox in the repo after applying them.
> - DA6 changes `analysis/e1.py`. `e1.py` is outside REG-21's and REG-22's frozen closures. Rerun `tests/test_e1.py`.
> - The other items are text and tags.
> - Because DA1, DA2 and DA6 are code changes, the review-stop rule calls for a second round on the new bundle.

#### What was changed because of it
- **DA1** (a check failing on two runs): the stopping rule's sentence "Likewise any other check …" and R2's last clause, verbatim. Code: `MAX_SAME` (FILE(docs/probe/20261113_e1/ops/common.sh:24,193,242,267-269), lines after draft 7's script patch), as the review gives it. Sandbox: the three-attempt cases use three different checks; the new case "a check failing on two or more runs stops E1, no rerun". README: the stop-table row. Kept beside the owner-proxy's restart rule (DB4); the sentence after DB4 says where the code is stricter (two runs at one rate).
- **DA2** (the pause lost to another stop): R2's parenthesis, verbatim. Code: `queue.sh`'s `report_settled` wrote `state/pause_pending.txt` (draft 7 moves that write into `common.sh`'s `settle`, FILE(docs/probe/20261113_e1/ops/common.sh:164-167), round 2's DC-O1) and the `launch` branch shows it and sets it aside (FILE(docs/probe/20261113_e1/ops/queue.sh:68-71); lines after draft 7's script patch); `launch.sh` refuses while it exists (FILE(docs/probe/20261113_e1/ops/launch.sh:27)). Sandbox: the case "with lost_ok: the pause not yet shown comes first" and the four checks of "an invalid run, then a failed copy". `PAUSE=""` stays, unused, as the review allows.
- **DA3** (pre-launch checks do not end E1): both sentences of the stopping rule, verbatim.
- **DA4** (the floor's code frozen): "Result, computed once", verbatim, followed by the owner-proxy's DB6 and one sentence on how the two agree.
- **DA5** (REG-19's runs, RUNBOOK): the ID line, verbatim. The two RUNBOOK edits are not made in this draft; with the owner-proxy's DB11 they form one proposal for the approval commit (`docs/drafts/e1_draft6_itemmap.md`, "RUNBOOK").
- **DA6** (the floor is a mean over a rate range): "Decision under each outcome" and "Result, computed once", verbatim. Code: `observed` gives `floor_slope_reported`, as the review gives it; a test (`test_observed_reports_the_floors_slope_on_rate`).
- **DA7** (the validity record changes one decision): the bullet "In neither case", verbatim; "What E1 cannot do" ends with a sentence pointing to it.
- **DA8** (one bit per rate): the stopping rule's first bullet, verbatim.
- **DA9** (the cost's ceiling): "Cost", verbatim but for one word: "at most 18 runs" for "at most 18 launches" (the sweep is one launch for six runs, so 18 runs take 13 launches, or 19 when the sweep's launch fails before any rate starts). The owner-proxy's DB7 is merged into it.
- **DA10** (tags): all six, verbatim, except that `common.sh:96-104` is now `common.sh:98-108`, the same lines after this draft's edits.
- **DA11** (the reviewed harness is the one that runs): "The harness E1 runs on", **Facts**, verbatim. Rechecked on 2026-11-13: `harness/` has tree `e8a3e1e7425da486327884d093055e0846229d38` at 9e249b1, e87884d and the working HEAD, and the `git diff --quiet` of the text exits 0 against HEAD.
- **DA12** (stale comments): `queue.sh` lines 2 and 4, `vm_checkout.sh` line 6, `common.sh` line 3, and DESIGN_NOTES.md (I11, part 2 item 12, R6), verbatim; comment lines rewrapped. Comments that this draft's own code changes made stale were also brought up to date (`common.sh`'s `ready_to_run` and `next_step` comments, `queue.sh`'s header and `report_settled` comment, `launch.sh`'s header).
- **DA-O1** (the gate's heading names the end line): the ID line and `END19_PAT`, verbatim; the sandbox's heading `(QUEUE DONE)`, and three cases added by this draft's writer (the futility-stop end passes; a `QUEUE STOP` heading and a bare heading are refused). The gate's refusal message also names the two forms.
- **DA-O2** (the owner's halt): the stopping rule's sentence and `ready_to_run`'s first line, verbatim; four sandbox cases added by this draft's writer (the queue, `launch.sh` and `vm_checkout.sh` refuse; nothing moved). The code also accepts a `[CORR] (owner) E1 halted` heading, as the review's line does.
- **DA-O3** (a pre-registered rerun after a power-off): **not taken.** It changes the stopping rule for lost runs, which the owner-proxy's note N3 leaves to the owner. A run that ends without `checks.json` still stops E1 until a new decision.
- **DA-O4** (a hole just below λ_sat): "Holes", verbatim; `e1.floor`, as the review gives it; a test (`test_a_hole_just_below_lam_sat_is_a_hole`).
- **DA-O5** (what a `gpu_steady` failure was): appended to R3, verbatim.
- **DA-O6** (`report` and `first_valid`): `e1.report`, as the review gives it; a test (`test_report_counts_only_the_runs_first_valid_keeps`).
- **DA-O7** (the move back to the pin): the ID line, verbatim, followed by the owner-proxy's DB10(iii): the move back needs its own entry.

### Adversarial review, round 2 (rule F, `docs/process.md` §3), verbatim

> <!-- Saved verbatim 2026-11-13 ≈ 23:20 UTC from the reviewer's own file /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/d3f64482-d0cf-4bf8-9ad1-c1dc026c562c/scratchpad/rulef-e1-draft6-r2.md (sha256 8dc8a1463b8db0850d3e97b8a357f336fcf39996e4ff69aa4117075f933b6408, 354 lines); the reviewer (rulef-e1-r2) sent the same text to the agent in five SendMessage parts. Body below this line is byte-identical to that file. -->
> Rule F review, round 2, of E1 draft 6 (bundle `docs/drafts/review_bundles/e1_r2/`, commit 97a6438), with the start-gate entry of 302d431
> 
> **Verdict: NOT READY.** Two blocking items: DC1 (E1's floor is an input of E0's gate in the plan, in claims.md and in committed code, so "E1 changes no decision about a shock matrix" is false, and running E1 before E0 is registered needs a rule-A5 guard) and DC2 (the "holes" rule in `e1.floor` gives a cleaner status on less data; a code fix, tested). DC3–DC9 are required but do not block: they are text, tags or reporting duties and can be applied verbatim. DC-O1 to DC-O5 are optional; DC-O1 and DC-O2 are code, tested in a scratch sandbox. The start gate with the 4611 entry is sound (section "The start gate").
> 
> **Bundle and limits**
> - MANIFEST: 41 of 41 sha256 lines OK. Every file in the bundle is in the manifest, and the manifest lists nothing else.
> - `ops/` in the bundle is byte-equal to `docs/probe/20261113_e1/ops/` at HEAD (cmp, 10 files).
> - `e1_draft6.patch` and `test_e1_draft6.patch`, applied to HEAD's `analysis/e1.py` and `tests/test_e1.py`, give the bundle's `e1.py` and `test_e1.py` byte for byte (patch in scratch, then cmp).
> - HEAD moved to 08817af during this review: 7e1a9fd, de80007, d9b324d (REG-22 and REG-21 registered), 62c9d96, 1dc008d and 08817af. `git diff --stat 97a6438 HEAD` over `docs/probe/20261113_e1`, `analysis`, `tests`, `harness`, `configs`, `agent/RUNBOOK.md`, `docs/experiment-plan.md`, `docs/claims.md` and the bundle is empty, so every anchor and FILE line below holds at HEAD. `docs/decisions.md` is append-only and now has 16320 lines; lines 1–4614 are unchanged, and every decisions.md line cited below is in that range unless named otherwise.
> - **REG-21's and REG-22's freezes (since d9b324d, after the bundle).**
>   - E1's draft-6 patch and DC2's patch change only `analysis/e1.py` and `tests/test_e1.py`. Neither is in REG-22's 27 frozen files (FILE(docs/decisions.md:4748)) or REG-21's 26 (FILE(docs/decisions.md:9834)), and neither adds a `.py` file. So the approval commit does not break either freeze. `analysis/k2.py` is not frozen either, so DC1's guard still matters.
>   - E1's seal is already at HEAD (FILE(analysis/withheld.py:30)), and `withheld.py` is frozen, so no seal change is needed or allowed.
>   - E1's folders match neither REG-21's reference pattern `*_sweep_l1pl350_pc_off_r*` (FILE(analysis/k3w.py:77); E1's names carry `l1pl350cl`) nor REG-21's or REG-22's batch-2 patterns, which name REG-19's burst configs. So E1's runs enter no batch.
>   - Disclosure E1 should carry (in DC5's spirit, not a separate item): the harness E1 runs on (`harness/checks.py`, `run.py`, `recorder.py`, `loadgen.py`, …) is frozen until both batch 2s are computed or declared not computed. A harness fault that DA7's block finds cannot be fixed before then.
> - Read: the bundle; the ops scripts; `analysis/e1.py`, `gate.py` (cold_floor, sweep_rows), `load.py` (find_runs), `withheld.py`, `k2.py` (decide, observed), `k3.py` (e1_prediction, legacy); `harness/run.py`, `checks.py`, `config.py`, `loadgen.py` (the drain deadline); the E1 config chain; `tools/manifest.py` (reads bytes only); `docs/decisions.md` (the cited lines, 1744–1752, 4037–4045, 4260–4275, 4516–4521, 4571–4614); `docs/claims.md` K2; `docs/experiment-plan.md` lines 427–428 (a grep for E0/E1); `agent/RUNBOOK.md` lines 46–75; `docs/drafts/reg19_resume_decision_draft5.md` line 41; REG-19's `ops_r3/` scripts (`common.sh`, `queue.sh`, `launch.sh`, `final.sh`); `docs/probe/20261113_reg20/ops/common.sh` (a grep for E1 and the gate); `docs/probe/20261113_freeze/closure.py` (source); `git diff .gitignore`.
> - Not opened: anything under `runs/` beyond folder names (`ls runs | grep -E '_sweep_l1pl350(cl)?_pc_off'`: seven REG-8 folders, no E1 folder; 186 folders in all); `docs/probe/**/state/`; `/Users/chalshik/aftershock-backups/`; RESUME.md; `docs/paper/`; any `queue_*.txt` or `launch_*.out`; any transcript; `docs/context-pack.md`; `docs/status.md` beyond the session-start digest a hook put into my context; the draft-3 rule F review (`rulef-e0e1-r2.md`), whose argument DC1 contradicts but which I did not read. Names under `ops_r3/state/` appeared in the git-status snapshot of my context (names only). No VM contact.
> - Ran: the sandbox in a temp dir under my scratchpad (`passed 184, failed 0`); `tests/test_e1.py` on the patched files in a scratch copy (`git archive HEAD analysis harness configs tests pyproject.toml`, with no `runs/`), run with the repo's interpreter: 16 passed; `python3 docs/probe/20261113_freeze/closure.py --at HEAD analysis/e1.py` (24 .py files, the same 27 in all as draft 6 says; it reads source only); schedule and config expansion through `e1._cfgs` and `harness.workload.build_schedule` in the scratch copy (no run read); `git diff --quiet 9e249b1 HEAD -- <DA11's list>` (exit 0); `git merge-base --is-ancestor a7bb77a HEAD` (exit 0). No analysis module command, no `tables.py`, `recheck`, `gate`, `check_docs.py` or full pytest. Python may have refreshed gitignored `__pycache__` in the repo when the sandbox ran `vm_state.py`; nothing else in the repo was written. The working tree's other modifications (`docs/decisions.md`, `agent/STATE.md` and others, shown by `git status` during this review) are not mine.
> - Scratch files, under `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/d3f64482-d0cf-4bf8-9ad1-c1dc026c562c/scratchpad/`:
>   - `DC2_DC8_e1_vs_bundle.patch`, `DC2_test_e1_vs_bundle.patch`: against the bundle's `e1.py` and `test_e1.py`. Patched files: `out/b/analysis/e1.py` (sha256 428771e0…) and `out/b/tests/test_e1.py` (dd3f52c5…); 16 passed.
>   - `DCO1_common.patch`, `DCO1_queue.patch`, `DCO1_test_sandbox.patch`: sandbox 188 of 188 (`sandbox_patched_newcase.txt`). Without the fix, the new case fails (`sandbox_unpatched_newcase.txt`, 186 passed, 2 failed).
>   - `DCO2_common.patch`, `DCO2_test_sandbox.patch`: sandbox 188 of 188 (`sandbox_dco2.txt`).
> - Every replacement anchor below was counted in the entry (lines 1–75 of `registration_draft6.md`): each occurs exactly once. The RUNBOOK and README anchors also occur once each.
> 
> ---
> 
> ### Required items
> 
> **DC1 (BLOCKING). E1's floor is an input of E0's gate. "E1 changes no decision about a shock matrix" is false, and E1 is run ahead of the gate that will judge it.**
> - **Trace.**
>   - The owner's plan makes E1's floor K2's 8-turn reference: "E0 … register[s], before any sweep, a numeric prediction of each setup's window ratio (closed-loop warm capacity over closed-loop cold floor) and the gate: the 16-turn shock matrix runs only if the 16-turn ratio exceeds the 8-turn ratio by a factor fixed here (rule G)" (FILE(docs/experiment-plan.md:427)). E1 "gives K2 its 8-turn reference" (FILE(docs/experiment-plan.md:428)). The same is said in FILE(docs/decisions.md:4040) ("E0 (0 GPU h) registers … the gate factor before any sweep (rule G)") and FILE(docs/claims.md:56).
>   - In the committed code, `k2.observed` computes `f8 = e1.floor(sweep_rows("sweep_l1pl350cl_pc_off"))`, which is E1's runs (FILE(analysis/k2.py:179)). `k2.decide` puts f8 into R = (warm16/f16)/(warm8/f8) (FILE(analysis/k2.py:109)) and returns "missing", meaning no matrix, when f8 is NaN (FILE(analysis/k2.py:102-103)). The owner's choice 2 of 2026-11-12 is "kept as it is in the E0 … registration" (FILE(docs/decisions.md:4264-4269)).
>   - So on E1's no-floor outcomes ("holes", "too_few", "unsaturated", "tail_*" but "tail_ok"), E0's committed gate gives "missing": no 16-turn matrix. Within E1's predicted range, f8 still moves R in proportion. Whether that flips a label depends on g and on E2's grid, which E0 has not fixed.
>   - The draft rests its claim on the draft-3 review's argument ("decided by the 16-turn cache-on sweep alone"). That argument is about a gate that is not registered, and it fails on the no-floor branch above. The owner's 4516 entry repeats the claim from the draft ("as its own draft says first", FILE(docs/decisions.md:4520)), so the owner's acceptance rests on it.
>   - Rule A5 hazard. E1 runs before E0 is registered. E0's redesign "needs … the owner's choice of a threshold" (draft 6, header). E1's result waits only for REG-21's first [RESULT]. If E1's floor is reported first, E0's threshold is chosen with one of its inputs known. The delegation does not cover choosing a threshold after seeing the data it judges (FILE(docs/decisions.md:4235)).
>   - Second inconsistency: `k2.observed` reads E1's runs with `e1.floor` but without `first_valid` and without the swept rates. It skips E1's holes check, and `gate.cold_floor` raises on two valid runs at one rate (FILE(analysis/gate.py:35-36)). E0 could therefore get a floor from runs on which E1's own rule reports "holes".
> - **Class:** disclosure and stricter rule (text).
> - **Text.** All anchors are in the entry, above the quoted review.
>   - (a) Anchor: `- **What E1 cannot do (rule A1), said first:** E1 changes no decision about a shock matrix. The rule F review showed that whether the 16-turn window "widens" is decided by the 16-turn cache-on sweep alone; E1 and the 16-turn cache-off sweep only word the ratio. E1 is proposed as K2's measurement and as the floor every closed-loop margin in the paper is quoted against, and for nothing else.`
>     Replace with: `- **What E1 can and cannot do (rule A1), said first:** E1's floor is K2's 8-turn reference: the denominator of the 8-turn window ratio that E0's gate compares the 16-turn ratio against (FILE(docs/experiment-plan.md:427-428); FILE(docs/decisions.md:4040); FILE(docs/claims.md:56)). As committed, `k2.decide` takes it as `f8` in R = (warm16/f16)/(warm8/f8) and returns "missing" (no matrix) when it is undefined (FILE(analysis/k2.py:102-109)), and `k2.observed` computes it from E1's runs (FILE(analysis/k2.py:179)). The draft-3 rule F review argued that the label is set by the 16-turn cache-on sweep alone; that is an argument about a gate that is not registered (BELIEF until E0's [REG] shows it), and it does not hold for E1's outcomes without a floor, which make the committed label "missing". So E1 can change the 16-turn matrix decision and K2's "does not widen" reading, through E0. E1 runs before E0 is registered, which departs from "E0 … registers … the gate factor before any sweep (rule G)" (FILE(docs/decisions.md:4040)). To keep rule A5 for E0's gate, no part of E1's floor (status, value, n, rates, slope) is computed, quoted or used before E0's [REG] is committed, or before an entry records that E0's gate takes no input from E1's runs. E0's registration discloses the one bit per rate that the allowed reads show (stopping rule, first bullet), and takes E1's floor as E1's [RESULT] reports it (the registered code, "holes" included), not recomputed by another rule (`k2.observed` calls `e1.floor` without `first_valid` or the swept rates, FILE(analysis/k2.py:179)). Apart from E0's gate, E1 is proposed as K2's measurement and as the floor every closed-loop margin in the paper is quoted against, and for nothing else.`
>   - (b) Anchor: `The decisions E1's outcomes do change are the wording ones under "Decision under each outcome".`
>     Replace with: `The decisions E1's outcomes do change are E0's gate input (above) and the wording ones under "Decision under each outcome".`
>   - (c) Anchor: `- **No floor:** K2's 8-turn closed-loop floor is reported as unmeasured on this grid; closed-loop margins keep the open-loop floor, named as such. A new grid is a new registration.`
>     Replace with the same text followed by: ` Under E0's gate as committed, the label is then "missing": no 16-turn matrix, the owner decides (FILE(analysis/k2.py:94-95,102-103)).`
>   - (d) Anchor: `- **In neither case** does E1's floor start, stop or size another run. That is why the paragraph "What E1 cannot do" comes first.`
>     Replace with: `- **In neither case** does E1's floor start, stop or size a run other than through E0's gate ("What E1 can and cannot do", which is why that paragraph comes first).`
>   - (e) Anchor: `After every rate has a valid run or the stopping rule has ended, and after REG-21's first [RESULT]:`
>     Replace with: `After every rate has a valid run or the stopping rule has ended, after REG-21's first [RESULT], and after E0's [REG] is committed or an entry records that E0's gate takes no input from E1's runs ("What E1 can and cannot do"; no computation in this section, and no `e1.observed`, `e1.floor_status` or `k2.observed` on E1's runs, runs before then):`
> - **Why blocking.** The first paragraph is the entry's rule-A1 statement, and a delegate approval may not rest on a false one. Without (e), the order of E1's result and E0's registration is left to chance, and with it rule A5 for E0.
> 
> **DC2 (BLOCKING). The holes rule gives "ok" when two rates are missing and "holes" when one is; a row `cold_floor` drops is not counted as a hole.**
> - **Trace (a), the main one.**
>   - The sweep returns 1.5 INVALID `recorder` and 2.0 INVALID `recorder`; 2.5–4.0 are valid. `MAX_SAME` stops E1 after the sweep (common.sh:260-262), and "E1's result is then computed from the runs made".
>   - `floor` sees rows 2.5–4.0 only. `cold_floor` returns "ok" with λ_sat 2.5. Draft 6's hole check finds no valid row below λ_sat, sets `lo = lam_sat`, and so reports **"ok", 1.735** (scratch check on synthetic rows).
>   - With 1.5 valid and kept up, and only 2.0 missing, the same code reports "holes" [2.0] (DA-O4's own case). Less data gives the cleaner status.
>   - 2.0 plans 2.097 req/s and counts as saturated below 1.992, against a predicted floor of 1.70–1.80 (DERIVED from `build_schedule`: 1374 planned arrivals in [240, 900) over 660 s). So the "ok" floor leaves out a row predicted to belong to it, and sits about 0.01–0.015 req/s high (DA6's figures).
>   - A fault that hits only the first two runs of the sweep (the coolest and shortest) is the kind DA1's stop is built for, so this trace is reachable.
>   - Under the DA4 merge, after a later [CORR] "the registered code's floor is E1's floor". A fix after registration cannot correct this outcome, so it must be in the registered code.
> - **Trace (b).** `have` is built from every row's rate, including rows that `cold_floor` drops for a non-finite value (FILE(analysis/gate.py:33)). A valid run with a NaN `kv_mean` or throughput at 3.0 therefore makes no hole, and the floor silently leaves out 3.0. This is unlikely under the new coverage checks, and costs one line.
> - **Class:** code fix, plus text.
> - **Code** (against the bundle's `e1.py`; full patch `DC2_DC8_e1_vs_bundle.patch`).
>   - Replace `        have = set(np.round(rows.rate.to_numpy(float), 6))` with:
>     ```
>             fin = rows[np.isfinite(rows[["rate", "throughput", "planned_rate", "kv_mean"]]).all(axis=1)]   # as cold_floor reads them
>             have = set(np.round(fin.rate.to_numpy(float), 6))
>     ```
>   - Replace `        lo = max(below) if below else f["lam_sat"]` with `        lo = max(below) if below else -math.inf          # no valid row below lam_sat: lam_sat is not bracketed (DC2)`.
>   - In `floor`'s docstring, replace `    lam_sat, or between the highest valid row below lam_sat and lam_sat (rule F e1_r1, DA-O4: lam_sat could lie` / `    there), has no valid run (the floor would average over a gap)."""` with `    lam_sat, or below lam_sat with no valid row between it and lam_sat (rule F e1_r1, DA-O4; e1_r2, DC2: lam_sat` / `    could lie there), has no valid run (the floor would average over a gap); a row with a non-finite rate, throughput,` / `    planned rate or KV mean, which cold_floor drops, counts as no valid run."""`.
> - **Tests** (`DC2_test_e1_vs_bundle.patch`; still 16 tests, 16 passed).
>   - In `test_floor_no_rows_and_holes`, replace
>     ```
>         low = E.floor(full[full.rate != 1.5], grid)             # a hole below lam_sat does not matter
>         assert low["status"] == "ok" and low["n"] == 5
>     ```
>     with
>     ```
>         low = E.floor(full[full.rate != 1.5], grid)             # no valid row below lam_sat: lam_sat could be 1.5
>         assert low["status"] == "holes" and low["missing_rates"] == [1.5]
>         assert E.floor(full, (1.0,) + grid)["status"] == "ok"   # a hole below a valid unsaturated row does not matter
>     ```
>   - In `test_a_hole_just_below_lam_sat_is_a_hole`, replace
>     ```
>         g = e1.floor(no_low, grid)
>         assert g["status"] == "ok" and g["lam_sat"] == 2.5                               # 1.5 and 2.0: below, not holes
>     ```
>     with
>     ```
>         g = e1.floor(no_low, grid)                                                       # no valid row below lam_sat:
>         assert g["status"] == "holes" and g["missing_rates"] == [1.5, 2.0]               # lam_sat could be 1.5 or 2.0
>         nan_row = rows([1.5, 2.0, 2.5, 3.0], [1.45, 1.70, 1.72, float("nan")], kv=[0.6, 0.95, 0.95, 0.95])
>         assert e1.floor(nan_row, (1.5, 2.0, 2.5, 3.0))["missing_rates"] == [3.0]     # a row cold_floor drops is a hole
>     ```
> - **Text.**
>   - Anchor: `- **Holes:** a swept rate at or above λ_sat, or a swept rate between the highest valid row below λ_sat and λ_sat, with no valid run gives the status "holes" and no floor (the floor would average over a gap); the missing rates are listed.`
>   - Replace with: `- **Holes:** a swept rate with no valid run gives the status "holes" and no floor when it lies at or above λ_sat, or below λ_sat with no valid row between it and λ_sat (λ_sat could lie there; with no valid row below λ_sat, every swept rate below it without a valid run is such a hole). A row with a non-finite rate, throughput, planned rate or KV mean, which `gate.cold_floor` drops, counts as no valid run. The missing rates are listed.`
> - **Cost and side effect.**
>   - The stricter rule costs a floor only when 1.5 has no valid run. Outside a stop, that means three failures at 1.5.
>   - It also changes `floor_status`, which E2 reads (E2's lowest rate is 1.0). E2 is not registered; its registration must say so.
>   - "holes" is on the owner-proxy's §3 list, so this needs its pass.
> 
> **DC3. Two descriptions of the registered-code computation disagree, and one of them would read sealed folders.**
> - **Trace.**
>   - DA4's sentence runs the registered code "from a worktree at the registered commit whose `runs/` links to the Mac's". DB6's sentence links only the two sweeps' folders.
>   - Read as a link to the whole `runs/`, the worktree's `e1.observed` → `gate.sweep_rows` → `load.find_runs("*")` would load every run folder that the registered commit's `withheld.SEALS` does not list (FILE(analysis/load.py:41-44)).
>   - E1's result waits for REG-21's first [RESULT] (and, with DC1, for E0's [REG]). Seal rows added after the registered commit, for REG-20 arm A's operations or D1/D2, are unknown to that code, so their sealed runs' requests and metrics would be loaded.
>   - That is "reading outcome data a pending registration withholds", which the delegation does not cover.
> - **Class:** stricter rule (text; resolves a DA4/DB6 merge conflict).
> - **Text.**
>   - Anchor, in the entry: ``(run from a worktree at the registered commit whose `runs/` links to the Mac's)``
>   - Replace with: ``(the worktree computation below, whose `runs/` is a real directory holding links to E1's and REG-8's cache-off sweep folders only, as REG-19's `links_ok` builds its own, FILE(docs/probe/20261113_reg19/ops_r3/common.sh:88-102); never a link to the whole of the Mac's `runs/`: the registered code's `analysis/withheld.py` does not know seals added after the registered commit, and `gate.sweep_rows` loads every run folder it can see, FILE(analysis/load.py:41-44))``
> 
> **DC4. Nothing holds the VM for E1 between its queue runs, and RUNBOOK §5 puts REG-20 first.**
> - **Trace.**
>   - E1 pauses after an invalid run, or stops for a `lost_ok` decision (likely, given A18). While it waits, E1's queue lock does not exist.
>   - REG-19's [RESULT] may land then. REG-21's and REG-22's entries are now committed (d9b324d), so only `final.sh` stands before it.
>   - RUNBOOK §5 orders "2 REG-20 gate, 2a REG-20 arm A" before "4 E1" (FILE(agent/RUNBOOK.md:63-66)). REG-20's ops scripts (in review) gate on `[RESULT] REG-19` and know nothing of E1 (a grep of `docs/probe/20261113_reg20/ops/common.sh` for E1 has no hit).
>   - REG-20's move puts the VM on a commit that descends from E1's. E1's next pre-launch then stops on the tree, and `vm_checkout.sh` refuses to move backward (FILE(docs/probe/20261113_e1/ops/vm_checkout.sh:32)).
>   - E1 is stranded with holes. The 2.1 h already spent may then give no floor.
>   - The draft's RUNBOOK proposal amends §4 and §3 item 6 only, and E1's end has no fixed record that another registration's gate could read. This is the mirror of the REG-19 gate E1 itself needed.
> - **Class:** stricter rule (text, with RUNBOOK and README edits in the approval commit).
> - **Text.**
>   - Anchor: `- The owner halts E1 by an entry headed `## <date> · [DECISION] (owner) E1 halted`; no launch follows its commit.`
>   - Replace with the same line followed by a new bullet: ``- **E1 holds the VM** from `vm_checkout.sh` until its end is recorded by an entry headed `## <date> · [OPS] E1: the queue ended (QUEUE DONE)`, `## <date> · [OPS] E1: the queue ended (QUEUE END)`, or `## <date> · [OPS] E1 ended by a stop: <the stop line>` (a stop that an entry has decided ends E1). A pause, or a stop that waits for a decision, is not an end. Until the end entry, no other registration's run is launched, and the VM's tree is moved only by E1's scripts or under an owner's entry. The approval commit amends RUNBOOK §5's order to match: E1 runs from REG-19's recorded queue end, and REG-20's gate and arm A wait for E1's end entry.``
> - **RUNBOOK, (c), merged with the item map's (a) and (b).**
>   - Anchor: `| 4 | E1 |`
>   - Replace with: `| 1a (before 2) | E1 (runs from REG-19's recorded queue end; items 2 and 2a wait for E1's end entry, "[OPS] E1: the queue ended …" or "[OPS] E1 ended by a stop: …") |`
> - **README.**
>   - Anchor: ``   - write the `[OPS]` entry;``
>   - Replace with: ``   - write the `[OPS]` entry, headed `[OPS] E1: the queue ended (QUEUE DONE)` or `(QUEUE END)` (registration, "E1 holds the VM");``
> 
> **DC5. DA7's readable fields cannot name every cause of a `recorder` or `gpu_steady` failure, and two of them carry DA8's bit without saying so.**
> - **Trace.**
>   - `gpu_steady` fails on `busy_sm_clock_cv` > 0.05 or on no busy sample, as well as on throttling, SW thermal or coverage (FILE(harness/checks.py:134-138)).
>   - Suppose a run fails on the clock CV alone. Every allowed field then reads as passing: `hw_throttle_samples` 0, `sw_thermal_frac` ≤ 0.05, `window_max_gap_s` ≤ 2.
>   - Three sentences then pull against each other. DA-O5's "then says which" cannot be met. DA7's block ("no registration runs on this harness until the cause is found") cannot be lifted within the allowed reads. The only way out is a read outside the list.
>   - `recorder`'s `counter_decreases` is missing the same way (FILE(harness/checks.py:106-110)).
>   - The item map's finding 2: `end_ref_t` (the time of `load_end`) shows whether the run ended early. `busy_samples`, once added, shows how loaded the GPU was. For a failed run, both show DA8's bit per rate.
> - **Class:** reporting duty and disclosure (text). It widens what may be read before E1's [RESULT], so the owner-proxy must rule on it (its §3, fourth bullet; item map finding 3).
> - **Text.**
>   - Anchor: `` `recorder`'s `first_ok_scrape_t`, `last_ok_scrape_t`, `end_ref_t`, `recorder_died`, `max_gap_s`, `failed_scrapes`; `gpu_steady`'s `window_max_gap_s`, `hw_throttle_samples`, `sw_thermal_frac`, `max_temp_c`. None of them holds a request count, throughput or KV. ``
>   - Replace with: `` `recorder`'s `first_ok_scrape_t`, `last_ok_scrape_t`, `end_ref_t`, `end_ref`, `recorder_died`, `max_gap_s`, `failed_scrapes`, `counter_decreases`; `gpu_steady`'s `window_max_gap_s`, `window_samples`, `busy_samples`, `busy_sm_clock_cv`, `hw_throttle_samples`, `sw_thermal_frac`, `max_temp_c`, or its detail text when the detail is not a dict ("no gpu.jsonl data"). These are every input of the two checks' pass conditions (FILE(harness/checks.py:106-110,134-138)). None of them holds a request count, throughput or KV. Disclosed: `end_ref_t` is the time of `load_end`, which comes early for a run whose sessions all ended before the drain deadline, and `busy_samples` counts the samples with the GPU at least 50 % busy. For a failed run, both show the same one bit per rate as the stopping rule's first bullet, and no more. ``
>   - Anchor (in R3, in the entry): `The [RESULT] names each `gpu_steady` failure "heat or sample coverage" until its detail is read (DA7's fields), then says which.`
>   - Replace with: `The [RESULT] names each `gpu_steady` failure "heat, SM-clock steadiness or sample coverage" until its detail is read (the fields listed under "In neither case"), then says which.`
> 
> **DC6. Two sentences of "Result, computed once" describe a `report()` that does not exist (item map finding 4).**
> - **Trace.**
>   - `report()` returns `observed()` plus the work rates. `observed()` gives `tilt_reported` and never calls `prediction()` (bundle `e1.py`:184-199, 242-252).
>   - `floor_ol` is `saturated(ol)`: `cold_floor` with no tail fallback and no holes check, which is not "the same way" as E1's floor.
>   - For REG-8's seven rows the value is 1.681 either way, since `cold_floor` gives "ok" and every swept rate has a row. So the fix is wording, which keeps REG-8's own definition.
> - **Class:** wording.
> - **Text.**
>   - Anchor: `the open-loop floor recomputed the same way; the common onset; the tilt with its prediction; the work rates of both sweeps.`
>   - Replace with: `the open-loop floor recomputed by `gate.cold_floor` with REG-8's settings (`e1.saturated`, as REG-8 computed it: no tail fallback and no holes check); the common onset; the tilt (`tilt_reported`); the work rates of both sweeps. The tilt's model-F description, `e1.prediction()`, reads no run. `e1.report` does not print it; it is quoted beside the tilt from `python -c 'import json; from analysis import e1; print(json.dumps(e1.prediction(), default=str))'`, run from the same code.`
> 
> **DC7. Rule H: the floor is a single-seed, pooled quantity, and the entry does not label it so.**
> - **Class:** reporting duty.
> - **Text.**
>   - Anchor: `- **A floor exists** only with status "ok" or "tail_ok". The result reports n and the rates used.`
>   - Replace with: `- **A floor exists** only with status "ok" or "tail_ok". The result reports n and the rates used, and labels the floor "single seed (seed 0), one run per rate": no seed-to-seed spread is measured, and the SE of `floor_slope_reported` is across rates, not seeds (rule H). The floor pools its rows under REG-8's assumption that a saturated cache-off server completes requests at one rate whatever the offered load. E1's own prediction says closed-loop rows break that assumption by a slope of about 0.04 req/s per req/s (FILE(tests/test_e1.py:59), BELIEF as to the model), so the result states the assumption beside the floor, with the slope as the evidence on it.`
> 
> **DC8. `analysis/e1.py`'s module docstring still says "not yet registered: draft docs/drafts/e1_draft4.md" (item map finding 7; owner-proxy N7).**
> - **Why now.** Draft 6 changes `e1.py` anyway, and from the registered commit the file is frozen (DA4). After registration this sentence would be false in judged code, with no way to fix it short of a [CORR].
> - **Class:** wording, in code; included in `DC2_DC8_e1_vs_bundle.patch`.
> - **Code.**
>   - Replace `"""E1 (not yet registered: draft docs/drafts/e1_draft4.md; its [REG] E1 entry does not exist yet): the closed-loop cache-off sweep of setup L1`
>   - with `"""E1 (registered: the [REG] E1 entry in docs/decisions.md; frozen from its registered commit): the closed-loop cache-off sweep of setup L1`.
> - **Note.** `observed`'s docstring "feeds E0" is true (DC1) and stays.
> 
> **DC9. The gate's entry now exists; cite it.**
> - **Class:** tag.
> - **Text.**
>   - Anchor: `It needs no REG-19 result.`
>   - Replace with: `It needs no REG-19 result. That entry exists: FILE(docs/decisions.md:4611) (commit 302d431, headed `[OPS] REG-19: the queue ended (QUEUE DONE)`, quoting `QUEUE DONE (all five seeds run). Next: final.sh, once`), which restates FILE(docs/decisions.md:4571) and records no new event.`
> 
> ---
> 
> ### Optional items
> 
> Every code anchor below occurs exactly once in the ops scripts at HEAD (grep -c -F).
> 
> **DC-O1. The DA2 residual gap (item map finding 5), closed by writing the pause in `settle`.**
> - **Trace** (reproduced in the scratch sandbox).
>   - The sweep is launched by `launch.sh` with 2.0 INVALID, then settled by hand without `report_settled`. This is the state a queue leaves when it dies between the two statements.
>   - Restart: the queue launches rate 2's rerun with no pause, rc 0 (`sandbox_unpatched_newcase.txt`: "FAIL the restart still pauses before the rerun").
>   - DA1's stop still bounds a systematic fault, so this is optional.
> - **Code.**
>   - `common.sh`, in `settle`:
>     - Replace `  local rec=$1 f log out line id c lines recs=()` with `  local rec=$1 f log out line id c lines recs=() l2 p`.
>     - Immediately before the line `  print -r -l -- $recs "time $(date -u +%Y-%m-%dT%H:%M:%SZ)" "scripts $SC" > $f.tmp && mv $f.tmp $f || { MSG="${f:t} could not be written"; return 2; }`, insert:
>       ```
>         for line in $recs; do                          # the pause (draft 6, DA2), written before the settle record (e1_r2, DC-O1)
>           id=${${=line}[2]}
>           for l2 in $VMS; do p=(${=l2}); [[ $p[1] == $id && $p[2] == invalid ]] && print -r -- "$id failed=$p[3]" >> $ST/pause_pending.txt; done
>         done
>       ```
>   - `queue.sh`: replace `      invalid) echo "RUN $id INVALID failed=$fl"; print -r -- "$id failed=$fl" >> $ST/pause_pending.txt;;` with ``      invalid) echo "RUN $id INVALID failed=$fl";;   # its pause line was written by `settle` (e1_r2, DC-O1)``. In its comment, replace `# The runs an attempt's launch log names, as the VM's checks.json says them; an invalid one is written to` / `# state/pause_pending.txt (draft 6, rule F e1_r1 DA2), which the next launch turn shows and sets aside.` with `# The runs an attempt's launch log names, as the VM's checks.json says them; `settle` has written each invalid one to` / `# state/pause_pending.txt (draft 6, DA2; e1_r2, DC-O1), which the next launch turn shows and sets aside.`
> - **Sandbox.** Before `echo "--- every stop"`, add:
>   ```
>   echo "--- review e1_r2: the queue dies between settle and report_settled"
>   reset
>   case_ "the sweep launched by hand" "ENDED sweep attempt 1" 0 FAKE_FAIL="2:recorder" zsh $L sweep
>   case_ "settled by hand, as if the queue died before report_settled" "SETTLED-BY-HAND" 0 zsh -c "source $S/common.sh; mac_checks && next_step && [[ \$ACT == settle ]] && settle \$ARG && echo SETTLED-BY-HAND"
>   case_ "the restart still pauses before the rerun" "QUEUE STOP after an invalid run" 1 zsh $Q
>   chk "no rerun launched before the pause" is "$(launches)" 1
>   ```
>   188 of 188 with the fix. A death after the append but before the settle record leaves a duplicate pause line, which is harmless.
> 
> **DC-O2. Launches that leave no run spend attempts with no stop.**
> - **Trace.**
>   - A fault that stops the harness before its first folder (a failed `uv run`, a held `.run.lock`, an ssh failure on the launch command) leaves a launch log with no `run_id` line. Each such launch is an attempt.
>   - The queue stops after each one (rc 2 or 4), but README has no row for that stop. A habitual restart spends all 13–19 launches, and E1 ends with six holes and no GPU time spent.
> - **Code** (`common.sh`, `next_step`; tested with three new sandbox checks, 188 of 188).
>   - Replace `  local rec f stem line l2 parts id c r rate name s att n a ids valid inval lost=() stopper="" n_heat=0` with the same line plus ` n_norun=0`.
>   - After the inner `done` of the settled-records loop, that is, after `      per[$r]=$id; NAMED[$id]=$stem` / `    done`, insert `    grep -q '^rid ' $f || n_norun=$((n_norun + 1))   # a launch whose log names no run (e1_r2, DC-O2)`.
>   - After the `MAX_SAME` loop's `    done`, insert `    (( n_norun < MAX_SAME )) || { MSG="$n_norun launches of E1 named no run (no run_id line in their logs): a question about the harness or the VM, not a rerun. E1 stops; the owner decides"; return 2; }`.
>   - Sandbox case: `DCO2_test_sandbox.patch`.
> - **Text.**
>   - Anchor: `Any `no_errors` in `failed` stops E1 (the details that would separate a client error from another are not read).`
>   - Append: ` A launch whose log names no run (no `run_id` line: its command failed, or the harness stopped before its first folder) spends its attempt; a second such launch, at any rate, stops E1 for a new decision.`
> 
> **DC-O3. README is not frozen by `mac_checks` (only the six scripts and `e1_commit.txt` are), so its stale lines can be fixed instead of listed.**
> - The stale lines are 5, 9, 39, 41, 52 and 85: the citations of draft 4, "Nothing here is committed or reviewed", and the step-4 heading without "(QUEUE DONE)".
> - If DC-O1 or DC-O2 changes the scripts, also bring `queue.sh` lines 4–5 and `vm_checkout.sh` lines 6–7 up to the heading form `END19_PAT` requires.
> 
> **DC-O4. No E1 run's VM copy may be removed before E1's end entry.**
> - **Why.** The queue stops when the Mac holds an E1 folder that the VM does not list (FILE(docs/probe/20261113_e1/ops/common.sh:217-219)). Rule 4's exception (2026-11-04) would otherwise allow the removal.
> - **Text.**
>   - Anchor: `Every run with a `checks.json`, valid or invalid, is copied and checksum-verified; a run without one is copied by a separate step.`
>   - Append: ` No E1 run is removed from the VM before E1's end entry (the queue stops when the Mac holds an E1 folder that the VM does not list, FILE(docs/probe/20261113_e1/ops/common.sh:217-219)).`
> 
> **DC-O5. If REG-21 is withdrawn, E1's result can never be computed (owner-proxy N4).**
> - **Text.**
>   - Anchor: `and E1's result is computed after it.`
>   - Append: ` If an entry withdraws REG-21, E1's result is the worktree floor and `e1.observed()` without the work rates, by a [DECISION] entry made before it is computed.`
> 
> ---
> 
> ### The start gate, with the 4611 entry (asked by the lead)
> 
> **Sound.**
> - `git grep -n -E "$END19_PAT" HEAD -- docs/decisions.md` has exactly one hit, at 302d431 and again at 08817af (after REG-21's and REG-22's 11 700 appended lines): line 4611, `## 2026-11-13 · [OPS] REG-19: the queue ended (QUEUE DONE)`. The UTC date matches the commit time (22:18 UTC).
> - The entry quotes `QUEUE DONE (all five seeds run). Next: final.sh, once`, as the ID line requires. That line is one of ops_r3's two end lines (FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:91)). The same queue lines are quoted in FILE(docs/decisions.md:4571); I did not open the queue output file it cites.
> - After QUEUE DONE, REG-19 has no run left by its own rules (seed 19's `'continue': False`).
> - What remains of REG-19 does not need the VM's tree:
>   - `final.sh` runs on the Mac, from the worktree at the pin.
>   - Its `links_ok` links only REG-19's folders into a real `runs/` and refuses anything else (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:88-102)), so E1's copied folders are never seen by REG-19's unsealed a7bb77a code.
>   - Its recheck uses REG-19's pattern only.
>   - Applying E1's code at the approval commit keeps the working tree equal to HEAD, which `recheck_ok` requires (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:207)), as long as it is committed and not left in the working tree.
> - The gate is a heading pattern and is now permanently open. Three independent guards keep REG-19 and E1 apart afterwards:
>   - REG-19's lock is tested at every queue start and before every launch (`launch.sh` calls `ready_to_run`).
>   - The tmux check.
>   - The tree check: REG-19 launches only at `a7bb77a`, and E1 only at its own commit.
> - The restated heading was written to fit the gate (it says so). That is honest, and the event it points to is recorded with its quote in 4571.
> 
> **Residual.** The gate only answers "has REG-19 let go of the GPU". The converse, other registrations waiting for E1, is DC4.
> 
> ---
> 
> ### Were DA1–DA12 and DB1–DB12 applied, and do the merges keep both?
> 
> - **Verbatim.** DA1, DA2, DA3, DA4, DA5 (text), DA6, DA7, DA8, DA10, DA11 and DA12 are verbatim (checked against the round-1 text quoted in the draft).
> - **DA9.** "18 launches" → "18 runs" is a correct departure. 18 runs take 13 launches when the sweep starts every rate, and 19 when it starts none (DERIVED: 1 + (6 − k) × 3 + k × 2 launches for k rates started).
> - **Optional DA items.** DA-O1, O2, O4, O5, O6 and O7 are applied as given. DA-O3 is not taken, with its reason stated.
> - **DB items.** DB1–DB9 are applied. DB9(a) is rewritten, as listed. DB10–DB12 are deferred to the approval commit.
> - **Merges.**
>   - DA1+DB4: both kept. The claim "every case DB4 stops, the scripts stop too" holds: a check at two rates means two runs, so `MAX_SAME` or the heat rule fires, and `no_errors`/`power_limit` stop at once.
>   - DA4+DB6: both kept, but their link specifications conflict (DC3).
>   - DA7+DB3: kept, but both understate what E1 changes (DC1).
>   - DA-O7+DB10(iii), DB2+DA-O2, DA9+DB7: fine.
> - **Item map, "Found while applying".** Items 1 and 6 are correct and benign. Item 2 is DC5. Item 3 is for the owner-proxy. Item 4 is DC6. Item 5 is DC-O1. Item 7 is DC8.
> 
> ### Do the scripts do what the stopping rule says?
> 
> - **Attempt counting.** The sweep counts as attempt 1 for each rate whose `run_id` line it has, and every single-rate launch is one attempt. Records are numbered and checked (common.sh:240-254).
> - **The sweep is launched at most once.** `attempt_sweep_1.txt` gates it, and folders or records before it stop the queue.
> - **Global stop.** `no_errors`/`power_limit` in any run, a second `gpu_steady` over all runs, and `MAX_SAME` for any other check over all runs all stop E1. When every rate still without a valid run is already spent, the queue prints QUEUE END instead (item map finding 6). Nothing is launched either way.
> - **Spent rates** do not hold back the others.
> - **The pause.** It survives other stops, and `launch.sh` by hand refuses while it is pending. The one residual gap is DC-O1.
> - **Two valid runs:** both are listed, nothing is launched, and the earliest is marked.
> - **The commit check** is taken from the start line. `git_commit` comes from FILE(harness/run.py:143), printed by FILE(harness/run.py:80); a missing value fails safe.
> - **Copying.** Every run with `checks.json` is copied, the sha256 lists are compared, and the copy record is written after the manifest. `tools/manifest.py` reads bytes only.
> - **Sandbox:** 184 of 184 in my scratch run.
> 
> ### Reads beyond `valid`/`failed` and the allowed log lines
> 
> None by the scripts:
> - `vm_state.py` prints only `valid` and `failed`.
> - `'run_id': '` appears on one harness print only, `ev("start", run_id=…, git_commit=…)`. All 16 `ev(` calls in `harness/run.py` were checked. The `[run] checks` line prints `valid` and `failed` only (FILE(harness/run.py:219)).
> - `copy_verify` prints a file count and a hash of hashes.
> - The pre-launch read is GPU state before the launch.
> 
> What the allowed reads still show:
> - The `LAUNCHED`/`ENDED` times and the run-id gaps (DA8's bit, disclosed).
> - With DC5, the same bit in two failure fields.
> - With DC1, that bit is information about E0's input before E0's gate is fixed, which E0 must disclose.
> 
> ### Cost arithmetic
> 
> - **2.1 h:** 6 × 1260 s = 7560 s. Every rate's schedule ends at 899.2–900.0 s, the drain deadline is t_planned max + 300 s (FILE(harness/loadgen.py:209)), and REG-8's saturated runs started 1262–1264 s apart (FILE(docs/decisions.md:1748-1751)).
> - **4.2 h** with one rerun per rate. **At most 18 runs, 6.3 h (22680 s).**
> - **Launches:** 13 to 19 for 18 runs; the extra launch is a sweep start that failed before its first rate, which costs at most the server start.
> - **What the stops do to the ceiling.** With `MAX_SAME` and the heat rule, the 4.2 h case already needs six invalid runs with six different check names. The practical ceiling is well below 6.3 h, so "every other stop only lowers that ceiling" holds.
> 
> ### FILE tags
> 
> All checked and correct:
> - decisions.md: 4037, 4040, 4200, 4201, 4205, 4209, 4233, 4287, 4400, 4506, 4516, 4520, 1745-1751.
> - reg19_resume_decision_draft5.md:41.
> - ops_r3: final.sh:2, launch.sh:45, common.sh:11, queue.sh:54-60.
> - agent/RUNBOOK.md:48.
> - harness: checks.py:127, run.py:80 and :143.
> - configs/base.yaml:55.
> - tests/test_e1.py:59.
> - E1's scripts: common.sh:24, :40, :98-108, :104, :187, :235, :260-262; queue.sh:44, :67-70; launch.sh:27.
> 
> Not checked: the RUN tags and the cold spans of 1.73–1.81, which need run reads; the replay floors 1.744/1.771, which need an analysis call.
> 
> ---
> 
> ### Strongest alternative explanation for the floor E1 would report
> 
> The floor will be read as the 8-turn closed-loop server's cold capacity, and through E0 as the denominator of the 8-turn window ratio. The strongest alternative is that it differs from 1.681, and from what a 16-turn sweep reports, mostly because of what is counted.
> 
> - **The mix.**
>   - Closed loop serves early, short turns first, so completions per second rise with the load at a fixed token rate (FILE(tests/test_e1.py:59); BELIEF as to the model). The 16-turn closed loop tilts by a different amount.
>   - E0's ratio of two req/s floors therefore mixes capacity with counting. A "widens" or "does not widen" label could come from the served mix, not from the cost gap K2 is about.
>   - **Separating evidence:** the token work rate U per saturated row at 8 turns (reported, `e1.work_rates`) against its 16-turn counterpart. Equal U with different req/s floors means counting. E0's registration should state R also on U-based floors, or say why not.
> - **Drift within an ascending sweep.**
>   - At 350 W the GPU warms over two hours of back-to-back runs, and the SM clock can fall with it. That lowers the high-rate rows and the slope.
>   - REG-8 ran in the same order but on another day.
>   - **Separating evidence:** the busy SM-clock mean per run from `gpu.jsonl`, which is not registered.
> - **For the margin use.**
>   - A cache-off floor is not the capacity of a cold cache-on server, which still hits on whatever prefix survives. So λ ÷ floor at λ = 2.0–2.2 overstates how far the cold state sits below its own capacity.
>   - **Separating evidence:** the hit rate of the cold spans on record, already measured.
> 
> ### Can E1 change any decision, and is it worth its GPU hours?
> 
> - **Yes, three.**
>   - (1) E0's gate, through f8 (DC1). Under the committed code, an E1 without a floor makes the 16-turn label "missing".
>   - (2) Whether the next registration may run on 5ee6e38's harness (DA7).
>   - (3) K2's wording and the closed-loop margins.
> - **Worth 2.1 GPU h:** yes. It is K2's 8-turn reference, which the owner's plan requires. It is the first GPU exercise of the A14 recorder and the stricter checks. And the GPU is otherwise idle until REG-19's [RESULT].
> - **But only on DC1's terms.** Run before E0's gate is registered, its floor must stay unseen until that gate exists. Otherwise the run's main decision value turns into a rule-A5 problem for E0.
> 
> ### Verdict
> 
> **NOT READY.**
> - **Blocking, apply first:**
>   - DC1 (text; E0 dependency and its A5 guard).
>   - DC2 (code and tests in `analysis/e1.py` and `tests/test_e1.py`, patches in scratch, 16 passed; "holes" changes, so the owner-proxy must pass it).
> - **Required, not blocking (verbatim):** DC3, DC4 (with its RUNBOOK and README edits in the approval commit), DC5 (the owner-proxy rules on the wider reads), DC6, DC7, DC8 (inside DC2's patch) and DC9.
> - **Optional:** DC-O1 to DC-O5. If DC-O1 or DC-O2 is taken, the scripts change and need the sandbox rerun and the owner-proxy's pass.
> - **Next round.** DC2 is a code change, so the review-stop rule calls for one more rule F round on the new bundle. That round can be limited to DC1's text and DC2's patch.
> 
> Review file: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/d3f64482-d0cf-4bf8-9ad1-c1dc026c562c/scratchpad/rulef-e1-draft6-r2.md

#### What was changed because of it (round 2)
- **DC1** (E0's gate takes E1's floor): (a) to (e), verbatim: "What E1 can and cannot do", the sentence after it, "No floor", "In neither case" and "Result, computed once". The guard is text only: no code refuses `e1.observed`, `e1.floor_status` or `k2.observed` before E0's [REG] (E1's seal is lifted by `AFTERSHOCK_UNSEAL=E1` alone), so it is kept by hand; the README's result line names the wait.
- **DC2** (the holes rule): "Holes", verbatim. Code: `e1.floor` and its docstring, the reviewer's patch byte for byte (`docs/drafts/e1_r3/DC2_DC8_e1_vs_bundle.patch`), now inside the cumulative `docs/drafts/e1_r3/e1_py_draft7.patch`. Tests: the reviewer's `DC2_test_e1_vs_bundle.patch`, inside `test_e1_draft7.patch`; 16 tests, 16 passed. With draft 6's `e1.py` the two changed tests fail (2 failed, 14 passed), so they test the change. The owner-proxy's DD5 is not applied (below).
- **DC3** (the worktree's `runs/`): verbatim.
- **DC4** (E1 holds the VM): the bullet "E1 holds the VM", verbatim except its last sentence; README's step 9 edit, verbatim (in `ops_draft7.patch`). **Departure:** the RUNBOOK row that puts E1 before REG-20 (`| 1a (before 2) | E1 (runs from REG-19's recorded queue end; items 2 and 2a wait for E1's end entry, …) |`) is not applied, and the bullet's last sentence, which says the same ("E1 runs from REG-19's recorded queue end, and REG-20's gate and arm A wait for E1's end entry"), is replaced by the lead's rule: "E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry ([OPS] … the queue ended …, or … ended by a stop …)". Reason (the lead's instruction for draft 7): the facts changed after the review. REG-19's [RESULT] is written (FILE(docs/decisions.md:16517)); REG-20's gate was computed (commit 3c8e5dc), so it cannot wait for E1's end entry; REG-20's arm A is owner-approved since 2026-11-12 (FILE(docs/decisions.md:4166), REG-20 approved by the owner as registered), and only its ops decision is in review. So the order between E1 and arm A follows from which ops decision is approved first. Added by this draft's writer, for round 3 to check: if REG-20 arm A runs first, E1's `vm_checkout.sh` and queue wait for REG-20's end entry, by hand, since E1's scripts do not read REG-20's entries (the same bullet, README step 4); the ID line, R6 and "Pre-launch and launch" name the commit the VM may then be at; README names the third end form (`[OPS] E1 ended by a stop: …`) under its stops table. The RUNBOOK text for the approval commit is the section "RUNBOOK, for the approval commit" below.
- **DC5** (the failure fields): both anchors, verbatim. The owner-proxy's DD6(b) is merged after it (below).
- **DC6** (what the result prints): verbatim. The owner-proxy's DD3 is merged after it as one sentence (below).
- **DC7** (rule H): verbatim. FILE(tests/test_e1.py:59) is the same line in the draft-7 patched file as at HEAD.
- **DC8** (the docstring): in the code patch, byte for byte.
- **DC9** (the gate's entry): verbatim, followed by one sentence: REG-19's [RESULT] has since been written (FILE(docs/decisions.md:16517)) and matches the gate too.
- **DC-O1** (the pause written in `settle`): code: the reviewer's `DCO1_common.patch`, `DCO1_queue.patch` and `DCO1_test_sandbox.patch`, byte for byte, and `queue.sh`'s comment, replaced as the review's text gives it (that change is not in the reviewer's queue patch). Added by this draft's writer: `settle`'s header comment says it writes the pause. Text: R2's parenthesis now names `settle`, and the round-1 list below (DA2) says the write moved.
- **DC-O2** (launches that name no run): code: the reviewer's `DCO2_common.patch` and `DCO2_test_sandbox.patch`, byte for byte; text: appended verbatim. Added by this draft's writer: a row for the new stop in README's stops table.
- **DC-O3** (README and comments): README's stale lines 5, 9, 39, 41, 52 and 85 brought up to date, and its line 3 "Stale" list cut to what is still stale (DESIGN_NOTES.md); line 52 also names DC1's wait for E0's [REG]; line 12 names draft 7's sandbox. `queue.sh` lines 4–5 and `vm_checkout.sh` lines 6–7 now name `(QUEUE DONE)` or `(QUEUE END futility stop)`; the two comment paragraphs are rewrapped. DESIGN_NOTES.md is unchanged; README's line 3 lists what in it is stale.
- **DC-O4** (no VM copy removed before E1's end entry): appended verbatim but for one citation, renumbered: `common.sh:217-219` is `common.sh:224-226` after draft 7's script patch (the same three lines).
- **DC-O5** (REG-21 withdrawn): appended verbatim, followed by one sentence: REG-21's first [RESULT] is now in the log (FILE(docs/decisions.md:16421)), so `e1.report`'s wait for it is met and the wait for E0's [REG] remains.
- **Facts since round 2** (the lead's instruction for draft 7): every sentence that had E1 or the GPU wait for REG-19's [RESULT], or that had REG-19 not yet reported, now cites FILE(docs/decisions.md:16517): the ID line (the pin clause is met, so draft 6's amendment of it is dropped as having nothing left to amend; REG-19's table was computed in 047b95e; the lost seed-18 folder's copy may follow; RUNBOOK §4's clause is met). The quoted reviews keep their words.
- **The harness freeze** (round 2, "Bundle and limits", a disclosure in DC5's spirit): a bullet under "The harness E1 runs on", worded as the lead gave it: "until both batch 2s are computed or declared not computed (expected on 2026-11-13/14)". Both batch 2s were then committed (7230ae8); one sentence added to the bullet says the disclosure is moot.
- **Sandbox:** 192 of 192 on a scratch copy of HEAD's scripts with `ops_draft7.patch` applied (184 of draft 6, plus DC-O1's 4 checks and DC-O2's 4; the reviewer had 188 for each alone), PROBE(docs/drafts/e1_r3/sandbox_20261113T231637Z.txt).

#### Owner-proxy pass
Owner-proxy on draft 5 (`docs/drafts/reviews-2026-11-13/proxy-e1-draft5.md`): **APPROVE on DB1–DB12**; DB1 (the heading's date, `<date of append>` until the entry is appended), DB2 (the ID line), DB3 ("What E1 cannot do"), DB4 (the stopping rule, with DA1), DB5 (the single-rate configs, the test, 16 tests), DB6 ("Result, computed once", with DA4), DB7 ("Cost", merged into DA9), DB8 (this section) and DB9 (`README.md`, written with the facts still true after draft 6) are applied in this draft; DB10 (the approving decision), DB11 (`agent/RUNBOOK.md`, merged with DA5's two edits) and DB12 (the `docs/model.md` ledger row) belong to the approval commit; draft 6's script, holes and stopping-rule changes need another owner-proxy pass (its §3). Owner-proxy on draft 6 (round 2; `docs/drafts/reviews-2026-11-13/proxy-e1-draft6.md`): **APPROVE on DD1–DD12**; DD1 (rule F round 2, verbatim, above), DD2 (this line), DD3 ("Result, computed once", merged into round 2's DC6 there), DD4 ("Prediction"), DD6 ("In neither case"; its (b) merged into round 2's DC5 there) and DD7 (the two patches, applied in this commit; draft 7's patches and sha256s take the place of draft 6's, so DD7's steps are run with them) are applied in this entry; DD5 ("Holes") is not, because round 2's DC2 changes the code so that the case it discloses no longer occurs; DD8–DD12 belong to the approval commit and the steps after it. Draft 7's DC2 ("holes"), DC-O1 and DC-O2 (the scripts; DC-O2 also the stopping rule) need another owner-proxy pass (its §3).

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

### Changed from draft 5 (rule F round 1 and the owner-proxy pass)
- Every rule F item is listed above ("What was changed because of it"), every owner-proxy item in the line after it, and both item by item, with each departure from the reviewers' words, in `docs/drafts/e1_draft6_itemmap.md`.
- Code, as patches against HEAD (bundle e1_r2): `analysis/e1.py` (DA6, DA-O4, DA-O6); `tests/test_e1.py` (DB5's test, and one test each for DA6, DA-O4 and DA-O6; 16 passed with both applied). They are applied in the commit that registers E1, at the latest. Scripts: `common.sh`, `queue.sh`, `launch.sh`, `vm_checkout.sh`, `test_sandbox.sh` (184 of 184), `README.md`, `DESIGN_NOTES.md`; `vm_state.py`, `session_probe.sh` and `e1_commit.txt` (still `UNSET`) are unchanged.

### Changed from draft 6 (rule F round 2 and the owner-proxy's round-2 conditions)
- Every rule F round-2 item is listed above ("What was changed because of it (round 2)"), every owner-proxy round-2 item in the line after it, and both item by item, with each departure from the reviewers' words, in `docs/drafts/e1_draft7_itemmap.md`.
- Code, as cumulative patches against HEAD: `docs/drafts/e1_r3/e1_py_draft7.patch` (draft 6's DA6, DA-O4 and DA-O6; round 2's DC2 and DC8) and `test_e1_draft7.patch` (draft 6's four added tests; round 2's DC2 changes to two tests); 16 passed with both applied. They are applied in the commit that registers E1, and DD7's sha256 check uses the hashes in this draft's header.
- Scripts, as one patch against HEAD: `docs/drafts/e1_r3/ops_draft7.patch` (`common.sh`, `queue.sh`, `vm_checkout.sh`, `test_sandbox.sh`, `README.md`; DC-O1, DC-O2, DC-O3 and DC4's README edit); 192 of 192. `vm_state.py`, `session_probe.sh`, `launch.sh`, `DESIGN_NOTES.md` and `e1_commit.txt` (still `UNSET`) are unchanged. The patch is applied in the commit that registers E1, before `e1_commit.txt` is set, and the sandbox is run again there.
- E1's order with REG-20 arm A follows the lead's rule, not round 2's RUNBOOK row (DC4, above).
- Facts since round 2: REG-19's [RESULT], REG-21's first [RESULT], REG-20's gate (the header, the ID line, "Reported, never judged").

### RUNBOOK, for the approval commit (text; `agent/RUNBOOK.md` is not edited by this draft)
The owner-proxy's DD10 applies draft 6's merged proposal, (a) and (b), verbatim (`docs/drafts/e1_draft6_itemmap.md`, "RUNBOOK: one proposal for the approval commit"; anchors FILE(agent/RUNBOOK.md:50) and FILE(agent/RUNBOOK.md:48), unchanged since 97a6438). Since REG-19's [RESULT] is written, (a)'s clauses on REG-19 are met; they are kept as DD10 asks. Round 2's DC4 adds a §5 row, (c), which this draft replaces by the lead's rule:

(c) In `agent/RUNBOOK.md` §5's table, replace
```text
| 4 | E1 |
```
with
```text
| 2b (with 2a) | E1 (E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry ([OPS] … the queue ended …, or … ended by a stop …)) |
```
(The row's other cells stay. Row 2a, REG-20 arm A, is not edited here: the same rule belongs in REG-20's ops decision, which is in review.)
