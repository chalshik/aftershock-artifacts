# rulef-e1-draft5-r1 (rulef-e1-r1), verbatim

Saved by the agent from the reviewer's own final text (its session a7b61c6b, line 558, timestamp 2026-11-13T21:19:16.276Z), which the reviewer ended its turn with and did not send by SendMessage, so it never reached the main session (checked by the agent on 2026-11-13 21:33 UTC: no SendMessage call in that session). The rule F round 1 on E1 draft 5 (bundle e1_r1).

---

Rule F review, round 1, of E1 draft 5 (bundle `docs/drafts/review_bundles/e1_r1/`)

**Verdict: NOT READY.** Twelve required items, DA1 to DA12. Three of them change code (DA1, DA2, DA6). The rest are text. Two script defects are confirmed in a scratch copy of the sandbox: a harness fault that fails one check on every run can spend 6.3 GPU h with no automatic stop (DA1), and the pause after an invalid run is lost if the queue stops for any other reason first (DA2). Both fixes were applied in the scratch copy and pass.

**Bundle and limits**
- MANIFEST: 28 of 28 sha256 lines OK.
- The bundle's scripts, `e1.py`, `test_e1.py` and draft 5 are byte-equal to the repo's files at e87884d (cmp).
- `harness_diff_a7bb77a_to_HEAD.diff` equals `git diff a7bb77a e87884d -- harness/`.
- Nothing under `runs/` was opened beyond folder names (`ls runs | grep`, `ls -d` of the two RUN-tagged folders).
- Nothing under `docs/probe/**/state/` was opened. File names under `docs/probe/20261113_reg19/ops_r3/state/` did appear in git-status output twice: once in the context injected at session start, and once from a `git status --short | head` I ran after the sandbox to confirm the repo was untouched. Only names, no content.
- I read `agent/RUNBOOK.md` lines 40–56 (§3 items 2–6 and the §4 heading). That file is not on the lead's list and not forbidden; I read it because DESIGN_NOTES cites FILE(agent/RUNBOOK.md:48,50).
- I did not read `docs/context-pack.md`, `status.md` (beyond the session-start digest a hook put into my context), `model.md`, `claims.md` or `open-questions.md`. That is on purpose: rule F's pass sees the registration and the code.
- No VM contact.

**What I ran**
- The sandbox, in a temp dir under my scratchpad: 170 of 170.
- A scratch copy of the sandbox with six trace cases: 176 of 176. Output: `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/a7b61c6b-f3e3-42e5-9c96-081c8a6cb2a9/scratchpad/e1r1/sandbox_reviewer.txt`.
- That copy with the DA1 and DA2 patches and the changed cases: 177 of 177. Output: `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/a7b61c6b-f3e3-42e5-9c96-081c8a6cb2a9/scratchpad/e1r1/sandbox_patched2.txt`.
- Patches as diffs: `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/a7b61c6b-f3e3-42e5-9c96-081c8a6cb2a9/scratchpad/e1r1/patch_common.sh.diff`, `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/a7b61c6b-f3e3-42e5-9c96-081c8a6cb2a9/scratchpad/e1r1/patch_queue.sh.diff`, `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/a7b61c6b-f3e3-42e5-9c96-081c8a6cb2a9/scratchpad/e1r1/patch_launch.sh.diff`, `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/a7b61c6b-f3e3-42e5-9c96-081c8a6cb2a9/scratchpad/e1r1/patch_test_sandbox.sh.diff`.
- `.venv/bin/python -m pytest tests/test_e1.py -q -p no:cacheprovider`: 12 passed.
- `python3 docs/probe/20261113_freeze/closure.py analysis/e1.py`: 24 .py files. `e1.py` is in neither REG-21's nor REG-22's closure.
- A schedule computation from the configs through `harness.workload.build_schedule`. It reads no runs.
- Python may have refreshed gitignored `__pycache__` files. Nothing else in the repo was written.

---

### Required items

**DA1. A harness fault that fails one check on every run spends 6.3 GPU h; the pause decides nothing**
- **Trace.**
  - The new harness fails `recorder` on every run without crashing (R2). For example, the last good scrape comes before `load_end` − 2 s.
  - The sweep returns six invalid runs (2.1 h) and the queue pauses.
  - For that stop, README says "Start the queue again; it reruns by E1's rule" (FILE(docs/probe/20261113_e1/ops/README.md:71)). No registered sentence says when not to restart.
  - Each restart launches one rerun, which fails and pauses again. After 12 restarts every rate has spent 3 attempts: 18 runs, 6.3 GPU h (DERIVED: 18 × 1260 s). The queue prints `QUEUE END` with six holes and there is no floor.
  - Reproduced in the scratch sandbox: `FAKE_FAIL` on all six rates, restarted at every pause, gives 13 launches (the sweep plus 12 single rates), then `QUEUE END rates without a valid run after 3 attempts: 1.5 2 2.5 3 3.5 4`.
  - Only `gpu_steady` is bounded (`MAX_HEAT`=2). So R2's sentence "a systematic failure is seen before the reruns spend about 4.2 h more" holds only if someone declines to restart, and that decision is not registered.
- **Class:** stricter rule, with a code fix.
- **Text.**
  - Anchor: `A second heat failure is counted over all of E1's runs, not per rate.`
  - Replace with: `A second heat failure is counted over all of E1's runs, not per rate. Likewise any other check (not `gpu_steady`, `no_errors` or `power_limit`) that is in `failed` of two of E1's runs, at any rates, stops E1: on the first GPU runs of a new harness a check that fails twice is a question about the harness, not a rerun.`
  - Anchor: `so a systematic failure is seen before the reruns spend about 4.2 h more.`
  - Replace with: `and a check in `failed` of two of E1's runs stops E1 (the stopping rule), so a systematic failure costs the sweep's 2.1 h and no rerun.`
- **Code, `common.sh`** (tested):
  - After the line `MAX_HEAT=2                                     # ... and the second among E1's runs stops the queue` add:
    `MAX_SAME=2                                     # E1 (rule F e1_r1): any other check in `failed` of this many of E1's runs stops the queue`
  - Replace `  local -A NAMED per` with `  local -A NAMED per nfail`.
  - After the line `      [[ ${NORERUN[(Ie)$f]} -gt 0 ]] && stopper="$f ($parts[1])"` add:
    `      [[ $f == - || $f == $HEAT || ${NORERUN[(Ie)$f]} -gt 0 ]] || nfail[$f]=$(( ${nfail[$f]:-0} + 1 ))`
  - After the line `    (( n_heat < MAX_HEAT )) || { MSG="second heat failure ($HEAT) among E1's runs: E1 stops; the owner decides"; return 2; }` add:
    ```
        for f in ${(k)nfail}; do
          (( nfail[$f] < MAX_SAME )) || { MSG="$f is in failed of ${nfail[$f]} of E1's runs: a check that fails twice is a question about the harness, not a rerun. E1 stops; the owner decides"; return 2; }
        done
    ```
- **Sandbox, `test_sandbox.sh`:**
  - In `case_ "the rerun is invalid again" ...` use `"INVALID failed=arrival_rate" 1 FAKE_FAIL="2:arrival_rate"`.
  - In `case_ "attempt 3 invalid too: ..."` use `FAKE_FAIL="2:release_chain"`.
  - In `run FAKE_SWEEP_RATES="1.5 2" FAKE_FAIL="2:recorder" zsh $Q; run FAKE_FAIL="2:recorder" zsh $Q; run FAKE_FAIL="2:recorder" zsh $Q` make the second and third `2:arrival_rate` and `2:release_chain`.
  - Add:
    ```
    reset
    run FAKE_FAIL="1.5:recorder 2:recorder 2.5:recorder 3:recorder 3.5:recorder 4:recorder" zsh $Q
    case_ "a check failing on two or more runs stops E1, no rerun" "recorder is in failed of 6 of E1's runs" 1 zsh $Q
    chk "one launch only" is "$(launches)" 1
    ```
- **README stop table:** add the row `| `<check> is in failed of 2 of E1's runs` | The registered systematic-fault stop | The owner |`.

**DA2. The pause is lost when any other stop comes between the settle and the next launch**
- **Trace.**
  - The sweep ends. `report_settled` prints `RUN …_r2 INVALID failed=recorder` and sets the shell variable `PAUSE`.
  - The next turn's copy of `…_r1.5` fails, giving `QUEUE STOP copy failed`. README says to find the cause and start again.
  - On restart the settle is already done, so `PAUSE` is empty. The queue copies the runs and launches rate 2's attempt 2 with no pause.
  - Reproduced: `FAKE_FAIL="2:recorder" FAKE_RSYNC_FAIL=1`, then a plain restart, gives `QUEUE DONE` with 2 launches.
  - The same happens after a checksum mismatch, a manifest failure, a VM read failure or the lost-run stop. `launch.sh` run by hand also launches with no pause.
  - So "After any invalid run the queue pauses" and R2's "(it copies what is pending and stops before the next launch …)" are false on this trace.
- **Class:** code fix.
- **Code, `queue.sh`** (tested):
  - Replace `      invalid) echo "RUN $id INVALID failed=$fl"; PAUSE+="${PAUSE:+; }$id failed=$fl";;`
    with `      invalid) echo "RUN $id INVALID failed=$fl"; print -r -- "$id failed=$fl" >> $ST/pause_pending.txt;;`
  - Replace `      [[ -z $PAUSE ]] || stop "after an invalid run ($PAUSE). Starting the queue again applies E1's rerun rule from checks.json (valid, failed) alone"` with:
    ```
          if [[ -e $ST/pause_pending.txt ]]; then
            stamp; mv $ST/pause_pending.txt $ST/pause_shown_$REPLY.txt || stop "the pause record could not be set aside"
            stop "after an invalid run ($(tr '\n' ';' < $ST/pause_shown_$REPLY.txt)). Starting the queue again applies E1's rerun rule from checks.json (valid, failed) alone"
          fi
    ```
  - `PAUSE=""` can stay; it is now unused.
- **Code, `launch.sh`:** after `next_step || die "$MSG"` add
  `[[ ! -e $ST/pause_pending.txt ]] || die "an invalid run has not been shown at a pause yet (state/pause_pending.txt): start the queue, which pauses first"`
- **Sandbox:**
  - Before `case_ "with lost_ok: the paused rerun of rate 2 goes first, in the sweep's order" "QUEUE DONE" 0 zsh $Q` insert
    `case_ "with lost_ok: the pause not yet shown comes first" "QUEUE STOP after an invalid run" 1 zsh $Q`
  - Add:
    ```
    reset
    case_ "an invalid run, then a failed copy" "copy failed" 1 FAKE_FAIL="2:recorder" FAKE_RSYNC_FAIL=1 zsh $Q
    chk "the invalid run was reported before the stop" is "$(print -r -- $out | grep -c 'INVALID failed=recorder')" 1
    case_ "the restart still pauses before the rerun" "QUEUE STOP after an invalid run" 1 zsh $Q
    chk "no rerun launched before the pause" is "$(launches)" 1
    ```
  - With DA1 and DA2 together the sandbox passes 177 of 177 (scratch run).
- **Text.**
  - Anchor: `(it copies what is pending and stops before the next launch; starting it again applies the rerun rule; FILE(docs/probe/20261113_e1/ops/queue.sh:41))`
  - Replace with: `(each invalid run is written to `state/pause_pending.txt` when its launch log is settled; no launch, by the queue or by hand, proceeds until a queue start has printed it and set it aside, so another stop in between does not consume the pause; starting the queue again then applies the rerun rule; `queue.sh`, `report_settled` and the `launch` branch; `launch.sh`)`

**DA3. The text says a pre-launch check ends E1; the scripts and README restart after it**
- **Trace.**
  - The VM reboots between two launches. This is likely: per the status file, open question A18 records that five of the seven recorded boot ends fell during a GPU run.
  - The next pre-launch read sees a new boot id and 420 W, so the launch stops with no attempt spent.
  - By the text, that is "an unexpected pre-launch check", which "stops E1: no further launch at any rate". E1 then ends with holes, and with no floor if the holes are at or above λ_sat.
  - By README (FILE(docs/probe/20261113_e1/ops/README.md:75-76)) and DESIGN_NOTES I15, the owner sets 350 W, a `RENEW=1` probe is recorded, and E1 goes on. The scripts allow this.
  - So whoever reads the stop decides after the fact which rule applies. The same holds for a GPU still hot after 30 min, low disk, or a stray tmux session.
- **Class:** wording.
- **Text.**
  - Anchor: `A client error (`no_errors`), a limit other than 350 W (`power_limit`) or an unexpected pre-launch check stops it.`
  - Replace with: `A client error (`no_errors`) or a limit other than 350 W (`power_limit`) in a run's `failed` stops it.`
  - Anchor: `**"Stops the sweep" stops E1:** no further launch at any rate.`
  - Replace with: `**"Stops the sweep" stops E1:** no further launch at any rate; E1's result is then computed from the runs made. A pre-launch check that fails (the limit read, the temperature after 30 min, a compute process, a tmux session, the tree, `uv.lock`, the boot id, free disk) is not such a stop: it launches nothing, spends no attempt, and the queue is started again once the cause is removed (after a reboot: 350 W set and a `RENEW=1` session probe recorded in a decisions entry).`

**DA4. The code that computes the floor is not frozen, so the result can move after the data exist**
- **Trace.**
  - E1's runs are on the Mac when the queue ends. The [RESULT] waits for REG-21's [RESULT], which may take days.
  - REG-21's and REG-22's freeze ends at their batch 2. REG-23 is "NOT READY on six items that need code changes" (status digest).
  - A commit in that window could change `analysis/load.py`'s `window` or `summarize` (the KV mean and the throughput window `gate.sweep_rows` uses, FILE(analysis/gate.py:198-205)), or `gate.cold_floor`.
  - The text asks only for "committed code … `uv run pytest` passing". The draft-3 review's B3/B4 shows the size of the stake: the 1.5 row's KV at 0.84 against 0.85 moves the floor from 1.725 ("ok") to 1.770 ("tail_ok"), 2.6 %.
  - `analysis/e1.py`'s import closure is 24 .py files plus `.python-version`, `pyproject.toml` and `uv.lock` (PROBE: `closure.py analysis/e1.py`, run by this review at e87884d).
- **Class:** stricter rule.
- **Text.**
  - Anchor: `From committed code, with `analysis/` and `tests/` clean and `uv run pytest` passing; the [RESULT] names the commit.`
  - Replace with: `From committed code, with `analysis/` and `tests/` clean and `uv run pytest` passing; the [RESULT] names the commit. **The code is the registered code:** the files printed by `python3 docs/probe/20261113_freeze/closure.py --at <registered commit> analysis/e1.py` (24 .py files and three environment files at e87884d; the output is quoted in the approval entry) are unchanged from the registered commit to the commit the [RESULT] names, except for rows added to `analysis/withheld.py`'s `SEALS`; the [RESULT] quotes `git diff --stat <registered commit> <its commit> -- <those files>`. Any other change is a [CORR] entry made before the result is computed, and the result then reports `e1.observed()["floor"]` from both codes, the registered code's first (run from a worktree at the registered commit whose `runs/` links to the Mac's).`

**DA5. The ID line's REG-19 sentence is false, and the gate contradicts RUNBOOK §3 item 6 and §4**
- **Trace (a).**
  - The text says "nothing of REG-19 is lost, since its runs are copied and verified".
  - ops_r3 copies valid runs only: only `valid` ids enter `rids`, which the copy loop walks (FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:54-60)).
  - The lost seed-18 folder is still to be copied "After the [RESULT]" (FILE(agent/RUNBOOK.md:48)). Those folders exist only on the VM.
  - `vm_checkout.sh` leaves them alone: `runs/` is gitignored and untracked, and `git checkout` keeps untracked files. So nothing is lost, but for that reason, not the stated one.
- **Trace (b).**
  - RUNBOOK §4's heading allows a deploy "never before REG-19's [RESULT]" (FILE(agent/RUNBOOK.md:50)). E1 moves the VM before that.
  - After REG-19's [RESULT], §3 item 6 has the agent "deploy HEAD (§4)" with `git pull origin main`. On E1's detached HEAD that either fails, or, after `git checkout main`, moves the VM off E1.
  - If E1 is then paused or waiting for a `lost_ok` decision, its next pre-launch read stops on the tree. `vm_checkout.sh` then refuses to move forward again (the VM's commit is not an ancestor of E1's), so the owner must decide.
  - Two files give contradicting orders (CLAUDE.md D).
- **Class:** wording and disclosure; RUNBOOK is amended in the registration commit.
- **Text.**
  - Anchor: `nothing of REG-19 is lost, since its runs are copied and verified and `runs/` is outside git.`
  - Replace with: `nothing of REG-19 is lost: `vm_checkout.sh` changes no file under `runs/` (gitignored and untracked), so REG-19's folders on the VM stay as they are, including those only the VM holds (ops_r3 copies valid runs only, FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:54-60); the lost seed-18 folder is copied after REG-19's [RESULT], FILE(agent/RUNBOOK.md:48)). This entry supersedes RUNBOOK §4's "never before REG-19's [RESULT]" for E1's move only, and its commit amends `agent/RUNBOOK.md` to match.`
- **RUNBOOK.**
  - Anchor: `## 4. Deploying `main` to the VM (only between items, never during a run, never before REG-19's [RESULT])`
  - Replace with: `## 4. Deploying `main` to the VM (only between items, never during a run; never before REG-19's queue has ended (E1's gate); never while E1 has not ended: E1 moves the VM only with its own `docs/probe/20261113_e1/ops/vm_checkout.sh`)`
  - Anchor: `then deploy HEAD (§4);`
  - Replace with: `then, once E1 has ended (its queue printed QUEUE DONE or QUEUE END, or a stop that ends E1 is recorded), deploy HEAD (§4, after `git checkout main` on the VM, whose HEAD E1 leaves detached);`

**DA6. The floor is a mean over a rate range, and closed-loop throughput is predicted to rise with the rate**
- **Trace.**
  - Model F's replay of E1's config puts the closed-loop throughput slope on rate more than 0.04 req/s per req/s above the open-loop one (FILE(tests/test_e1.py:59), passing; BELIEF as to the model). The draft-3 review found the same tilt for FIFO, LIFO, many slots and superlinear cost.
  - With rows 2.0–4.0 on a line of slope 0.04–0.06, the floor (their mean) sits 0.04–0.06 req/s, 2.4–3.5 %, above the 2.0 row (DERIVED, synthetic rows in this review: 1.74 or 1.76 against 1.70).
  - If λ_sat is 2.5, it is 0.01–0.015 higher still. That can happen if the 2.0 row's KV mean stays below 0.85, because a closed loop fills slowly from an empty start just above its floor.
  - "Closed-loop margins (λ ÷ floor) are restated against it" at λ = 2.0 and 2.2, the operating points, would understate those margins by that much, under the label "the closed-loop cold floor", and nothing in the result would show it.
- **Class:** reporting duty, with a small code change.
- **Text (decision).**
  - Anchor: `closed-loop margins (λ ÷ floor) are restated against it. Each such edit is its own decision.`
  - Replace with: `closed-loop margins (λ ÷ floor) are restated against it, each with the floor's rates and the slope of throughput on rate over them (`floor_slope_reported`, with its SE; reported, never judged), and, at λ = 2.0, also against E1's own 2.0 row (one run, labelled as such). Closed-loop throughput is predicted to rise with the rate (the served mix tilts toward early, shorter turns; FILE(tests/test_e1.py:59), BELIEF as to the model), so the floor is a mean over a rate range, not a constant of the server. Each such edit is its own decision.`
- **Text (result).**
  - Anchor: `the floor with its status, n, rates and any later valid run not counted;`
  - Replace with: `the floor with its status, n, rates, the slope of throughput on rate over those rates with its SE (`floor_slope_reported`) and any later valid run not counted;`
- **Code, `analysis/e1.py`, `observed`:** after `           "rows_cl": cl.to_dict("records"), "later_valid_runs_not_counted": dropped}` add:
  ```
      lam = res["floor"]["lam_sat"]
      res["floor_slope_reported"] = fit(cl, "throughput", lam) if np.isfinite(lam) else None   # reported, never judged
  ```
  Checked on synthetic rows through the real `observed`: status "ok", λ_sat 2.0, slope 0.04, n 4.

**DA7. "In neither case does E1 start, stop or size another run" leaves out the one decision E1 can change**
- **Trace.**
  - E1 is the first GPU run on 5ee6e38's harness (R1–R4). The session-cap arm (step D) will run on that harness.
  - If E1's runs have `recorder` or `gpu_steady` in `failed` (both now include coverage), a later registration would be proposed on a recorder known to fail on the GPU.
  - If every E1 run is valid, R4's gap closes for the cap-off path.
  - Either way this is a decision about other runs, read from allowed fields.
- **Class:** wording.
- **Text.**
  - Anchor: `- **In neither case** does E1 start, stop or size another run. That is why the paragraph "What E1 cannot do" comes first.`
  - Replace with: `- **In neither case** does E1's floor start, stop or size another run. That is why the paragraph "What E1 cannot do" comes first. **E1's validity record is another matter:** it is the first GPU evidence on `5ee6e38`'s harness (with the session cap off, so the cap's path is not exercised). If `recorder` or `gpu_steady` is in `failed` of any E1 run, or a run ends without `checks.json` on an unchanged boot id, no registration runs on this harness until the cause is found and recorded in an [OPS] or [CORR] entry. After E1's queue has ended, only these fields of a failed check may be read for that: `recorder`'s `first_ok_scrape_t`, `last_ok_scrape_t`, `end_ref_t`, `recorder_died`, `max_gap_s`, `failed_scrapes`; `gpu_steady`'s `window_max_gap_s`, `hw_throttle_samples`, `sw_thermal_frac`, `max_temp_c`. None of them holds a request count, throughput or KV. If every run is valid, the next registration on this harness cites E1's run ids for R4.`

**DA8. The allowed reads show, for each rate, whether the server kept up**
- **Trace.**
  - Run ids begin with their launch time (FILE(harness/run.py:136)).
  - In the sweep each run starts when the previous one ends.
  - The load generator exits as soon as every session chain is done (FILE(harness/loadgen.py:237-239)). So a rate the server keeps up with (1.5 plans 1.606 req/s, below the predicted 1.70–1.80 floor) ends early, while a saturated rate runs to its 1200 s deadline.
  - REG-8's open-loop 1.5 run lasted 16 min 55 s against about 21 min for the saturated ones (DERIVED from the start times at FILE(docs/decisions.md:1746-1751)).
  - So consecutive run ids, and a single-rate run's `LAUNCHED`/`ENDED` lines, show one bit of each rate's throughput. At 1.5 that is the bit that separates "ok" from "tail_ok".
- **Class:** disclosure.
- **Text.**
  - Anchor: `No interim look at any rate's throughput, KV or floor before the result is computed.`
  - Replace with: `No interim look at any rate's throughput, KV or floor before the result is computed. Disclosed: the allowed reads still show one bit per rate. Run ids carry their launch time, and a run whose sessions all ended before the drain deadline ends early, so the gaps between consecutive run ids of the sweep, and a single-rate run's `LAUNCHED`/`ENDED` times, show whether the server kept up with that rate. No step of the stopping rule uses this, and the [RESULT] says so.`

**DA9. The cost gives no ceiling**
- **Class:** wording (cost).
- **Text.**
  - Anchor: `6 runs × (900 + 300 + about 60 s) ≈ 2.1 GPU h (DERIVED); ≈ 4.2 h with one rerun per rate.`
  - Replace with: `6 runs × (900 + 300 + about 60 s) ≈ 2.1 GPU h (DERIVED: every rate's planned schedule ends at 900 s, so a saturated closed-loop run lasts to its 1200 s deadline; REG-8 part b's saturated runs started 21 min apart, FILE(docs/decisions.md:1745-1751)); ≈ 4.2 h with one rerun per rate; at most 18 launches, 6.3 h (DERIVED: 6 × 3 × 1260 s), and with the systematic-fault stop at most the sweep and a few runs when one check fails throughout. Waits for ≤ 45 °C before a launch (up to 30 min each) keep the GPU idle and are not counted.`
- Checked: maximum planned time 899.2–900.0 s at every rate, from `build_schedule` on the configs. 2.1 h and 4.2 h are correct.

**DA10. Tags**
- **Class:** tag.
- `(FILE(docs/decisions.md:4200))` → `(FILE(docs/decisions.md:4200) for the recorder and checks; FILE(docs/decisions.md:4209) for the session cap)`.
- `E1's configs set no cap.` → `E1's configs set no cap (DERIVED: `workload.sessions.cap` is absent from the expanded config of every rate of the sweep and of the six single-rate configs).`
- `No GPU run has used this harness yet.` → `No GPU run has used this harness yet (FILE(docs/decisions.md:4201): "Nothing is deployed to the VM"; REG-19's launches require `a7bb77a`, FILE(docs/probe/20261113_reg19/ops_r3/launch.sh:45)).`
- `FILE(docs/probe/20261113_e1/ops/common.sh:96)` → `FILE(docs/probe/20261113_e1/ops/common.sh:96-104)`.
- `FILE(harness/run.py:143))` → `FILE(harness/run.py:143), printed by FILE(harness/run.py:80))`.
- `RUN(the 13 REG-8 runs, gate.reg8_zone)` → `RUN(REG-8's 7 cache-off runs, `sweep_l1pl350_pc_off`, gate.reg8_zone)`. 1.681 comes from those 7 runs (FILE(docs/decisions.md:1744-1752)).
- All other FILE tags checked and correct: decisions.md:4205, 4516, 4520; ops_r3/common.sh:11; ops_r3/launch.sh:45; checks.py:127; base.yaml:55; common.sh:38. Also DESIGN_NOTES' run.py:136-143, 218, 243, RUNBOOK:48/50, and ops_r3 common.sh:136, vm_state.py:21/32-35, queue.sh:55, launch.sh:76.

**DA11. The harness that runs is not tied to the harness reviewed**
- **Trace.**
  - This review saw the harness at 9e249b1, whose `harness/` tree is e8a3e1e7425da486327884d093055e0846229d38 (the same at e87884d).
  - The registered commit comes later. The text says only "`git diff --stat a7bb77a HEAD …`", with HEAD unnamed.
  - A harness commit before registration (for step D, or a REG-23 fix) would run on the GPU unreviewed, as "the first GPU run on 5ee6e38".
- **Class:** stricter rule.
- **Text.**
  - Anchor: `` `git diff --stat a7bb77a HEAD -- harness/` gives 4 files, 163 lines in and 29 out; `pyproject.toml` and `uv.lock` are the same at both. ``
  - Replace with: `` `git diff --stat a7bb77a 9e249b1 -- harness/` gives 4 files, 163 lines in and 29 out; `pyproject.toml` and `uv.lock` are the same at both. The reviewed harness is the one that runs: `git diff --quiet 9e249b1 <registered commit> -- harness/ pyproject.toml uv.lock .python-version configs/defaults.yaml configs/base.yaml configs/gap5_base.yaml configs/l1_base.yaml configs/l1_pl350_base.yaml configs/sweep_l1pl350_pc_off.yaml configs/sweep_l1pl350cl_pc_off.yaml 'configs/sweep_l1pl350cl_pc_off_only_r*.yaml'` exits 0, and the approval entry quotes it; otherwise the registration goes back to rule F. ``
- This holds now: exit 0 against e87884d. The config chain is also unchanged since a7bb77a.

**DA12. Stale comments in the scripts that the registration will freeze**
- **Class:** wording.
- `queue.sh:2`: `# E1's queue (registration: docs/drafts/e1_draft4.md until it is registered; README.md).` → `# E1's queue (registration: the [REG] E1 entry in docs/decisions.md; README.md).`
- `queue.sh:4`: `REG-19's [RESULT] is in the committed log` → `the committed log records REG-19's queue end ('[OPS] REG-19: the queue ended') or its [RESULT],`
- `vm_checkout.sh:6`: `# before REG-19's [RESULT] is in the committed log, or while REG-19's queue lock exists` → `# before the committed log records REG-19's queue end ('[OPS] REG-19: the queue ended') or its [RESULT], or while REG-19's queue lock exists`
- `common.sh:3`: `the registration (docs/drafts/e1_draft4.md,` → `the registration (read from draft 4, docs/drafts/e1_draft4.md; registered as the [REG] E1 entry;`
- `DESIGN_NOTES.md:67`: `- The scripts implement the stricter rule, `RESULT19_PAT`.` (no such variable exists) → `- Draft 5 drops that wait: the scripts wait for an `[OPS] REG-19: the queue ended` or `[RESULT] REG-19` heading (`END19_PAT`) and for REG-19's lock to be absent.`
- DESIGN_NOTES §2 item 12: `or before REG-19's `[RESULT]` (I11)` → `or before an `[OPS] REG-19: the queue ended` or `[RESULT] REG-19` heading is committed (I11)`.
- DESIGN_NOTES R6: `RUNBOOK §4 allows a deploy only after REG-19's `[RESULT]` (I11).` → `RUNBOOK §4 allowed a deploy only after REG-19's `[RESULT]`; the registration supersedes that for E1's move and amends RUNBOOK (DA5).`

---

### Optional items

**DA-O1. The gate trusts a heading that a QUEUE STOP could carry**
- **Trace:** an `[OPS] REG-19: the queue ended` entry written by mistake after a `QUEUE STOP` passes `END19_PAT`. The VM then leaves the pin while REG-19 waits for the owner.
- **Class:** code fix plus heading form.
- **Code, `common.sh`:**
  - Anchor: `END19_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · (\[RESULT\] REG-19([^0-9]|$)|\[OPS\] REG-19: the queue ended)'`
  - Replace with: `END19_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · (\[RESULT\] REG-19([^0-9]|$)|\[OPS\] REG-19: the queue ended \(QUEUE (DONE|END futility stop)\))'`
  - Tested with grep -E: it matches `(QUEUE DONE)` and `(QUEUE END futility stop)`; it rejects `(QUEUE STOP …)`, a bare heading and `REG-190`. These are ops_r3's two end lines (FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:91)).
- **Sandbox:** the heading becomes `## 2026-11-15 · [OPS] REG-19: the queue ended (QUEUE DONE)`.
- **Text (ID line):** `an [OPS] entry headed `REG-19: the queue ended`` → `an [OPS] entry headed `REG-19: the queue ended (QUEUE DONE)` or `(QUEUE END futility stop)``.

**DA-O2. An owner's overrule cannot be seen by the scripts**
- **Trace:** the delegation says the owner may overrule a delegate decision by an entry (FILE(docs/decisions.md:4231-4238)). The scripts check the approval only at E1's commit.
- **Class:** code fix.
- **Code, `ready_to_run`, first line after `MSG=""`:**
  `git -C $R grep -q -E '^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[(DECISION|CORR)\] \(owner\) E1 halted' HEAD -- docs/decisions.md && { MSG="the owner halted E1 (a '[DECISION] (owner) E1 halted' heading)"; return 2; }`
- **Text (stopping rule):** add `The owner halts E1 by an entry headed `## <date> · [DECISION] (owner) E1 halted`; no launch follows its commit.`

**DA-O3. Register the default for a run lost to a power-off (A18) instead of a new decision each time**
- **Class:** stricter rule.
- **Text.**
  - Anchor: `a run that ends without `checks.json` stops the sweep until a new decision.`
  - Replace with: `a run that ends without `checks.json` stops the sweep until a new decision; if the VM's boot id changed during it (a power-off), the decision is fixed in advance: the run counts as one attempt, its rate is launched again under the attempt limit once 350 W is set and a `RENEW=1` probe is recorded, and an [OPS] entry and `state/lost_ok_<run id>.txt` record it; on an unchanged boot id (a harness fault, R1) the owner decides.`

**DA-O4. A hole just below λ_sat goes unreported**
- **Trace:** 2.0 has no valid run (three attempts spent), 1.5 is valid and kept up, 2.5–4.0 are saturated. `floor()` returns "ok" with λ_sat 2.5 and n 4, although λ_sat lies somewhere in (1.5, 2.5]. Scratch check on synthetic rows: registered code gives `ok`, 1.735; the patch gives `holes`, missing [2.0].
- **Class:** code fix.
- **Code, `e1.floor`:**
  - Anchor: `        missing = [float(x) for x in swept if x >= f["lam_sat"] - 1e-9 and round(float(x), 6) not in have]`
  - Replace with:
    ```
            below = [r for r in have if r < f["lam_sat"] - 1e-9]
            lo = max(below) if below else f["lam_sat"]
            missing = [float(x) for x in swept if x > lo + 1e-9 and round(float(x), 6) not in have]
    ```
  - The existing holes tests pass unchanged (1.5 missing: ok; 3.0 missing: holes [3.0]).
- **Text ("Holes"):** add `, or a swept rate between the highest valid row below λ_sat and λ_sat`.

**DA-O5. Say what a `gpu_steady` failure was**
- **Class:** reporting duty.
- **Text, append to R3:** `The [RESULT] names each `gpu_steady` failure "heat or sample coverage" until its detail is read (DA7's fields), then says which.`

**DA-O6. `report()` counts runs that `first_valid` excludes**
- **Class:** code fix.
- **Code:**
  - Anchor: `    cl, ol = sweep_rows(E1["sweeps"]["cl"]), sweep_rows(E1["sweeps"]["ol"])` in `report`.
  - Replace with: `    cl, ol = first_valid(sweep_rows(E1["sweeps"]["cl"]))[0], sweep_rows(E1["sweeps"]["ol"])`.

**DA-O7. Name the move back to the pin for a REG-19 rerun**
- **Class:** wording.
- **Text.**
  - Anchor: `needs the VM moved back first;`
  - Replace with: `needs the VM moved back first: only while no tmux session `run` exists, by RUNBOOK §4's steps with `git checkout --detach a7bb77abc863adcaad9d4516815a5ddddf2908e9`, recorded in an [OPS] entry; E1's next pre-launch read then stops on the tree (no attempt spent), and `vm_checkout.sh` later moves it forward again (a7bb77a is an ancestor of E1's commit);`

---

### 3. Strongest alternative explanation for the floor E1 would report

The floor is the mean, over the saturated rows from λ_sat to 4.0, of ok completions per second in [240, 900). The registration reads it as the closed-loop server's cold capacity. The strongest alternative is that it differs from 1.681, and from the cold throughput at λ = 2.0–2.2, mostly because of what is counted, not because of what the server can do:

- **The served mix tilts toward early turns.**
  - Closed loop serves a session's early turns first, and cold prompts grow with the turn (2176 + 256·k tokens). So completions per second rise with the load at a fixed token rate.
  - Model F puts the closed-loop throughput slope more than 0.04 req/s per req/s above the open-loop one (FILE(tests/test_e1.py:59)). The draft-3 review found the same tilt for any work-conserving server with within-session precedence.
  - The floor therefore depends on the grid and on λ_sat. Averaged over 2.0–4.0 it sits about 0.04–0.06 req/s above the 2.0 row (DERIVED, synthetic rows), and 0.01–0.015 higher if the 2.0 row's KV keeps λ_sat at 2.5.
  - Separating evidence: per-row throughput and its slope (DA6), k̄ per row, and U per row against REG-8's (both reported). A flat U equal to REG-8's, with rising req/s, means mix. A different U means the server: running batch, preemptions, a new connection per request, code, or day.
- **Drift between 2026-11-07 and E1's day at 350 W** (SM clock, thermal state after back-to-back runs) would move the absolute level against 1.681. Separating evidence: each saturated run's busy SM-clock mean against REG-8's, from `gpu.jsonl`. This is not registered; it could join the reported gauges.
- **The fill transient at the lowest saturated rate** inside the 660 s window. Separating evidence: throughput in each half of the window per row. Not registered.

### 4. Can E1 change any decision?

- **The floor: no run decision.** I agree with the text, and the draft-3 review's label map has the 16-turn question resting on the cache-on sweep alone.
- **It changes a claim decision:** K2's wording and the paper's closed-loop margins, which the text names.
- **The text does not name one more:** E1's validity record is the first GPU evidence on 5ee6e38's harness, and the step-D registrations will run on that harness (DA7). With DA7, the answer is yes, one decision. Without it, the sentence "In neither case does E1 start, stop or size another run" is incomplete.
- **Is it worth 2.1 GPU h?**
  - On the text's own terms (K2 wording only), weakly. The closed-loop cold throughput at the operating points is already bounded by the two cold spans the text cites (1.73–1.81 at λ = 2.0 and 2.2) and by model F's replay (1.744 or 1.771). E1 would add a sweep mean with a predicted rate dependence and the same named confounds.
  - With DA7 (the first GPU exercise of the A14 recorder and the stricter checks before step D relies on them), and with the GPU otherwise idle until REG-21's and REG-22's entries are committed, it is worth 2.1 h. DA1 keeps a broken harness from turning that into 6.3 h.
  - The text's own sentence, "If the owner holds that a measurement that changes no decision should not cost 2.1 GPU h, E1 should not run", stays the owner's call; the owner's 2026-11-13 entry chose to prepare it.

### Checked and correct
- The attempt count from the sweep's `run_id` lines; the sweep launched at most once ever.
- The global stops (`no_errors`/`power_limit` anywhere, the second `gpu_steady` over all runs).
- A spent rate does not block the other rates.
- Two valid runs at one rate: both listed, earliest counted.
- Unnamed folders, missing named runs and Mac-only folders stop E1.
- The commit check, from the start line `[run] start {'run_id': …, 'git_commit': …}`. `git_commit` is `git rev-parse HEAD`; a missing value fails safe.
- Every run with `checks.json` is copied and checksum-verified, one at a time.
- `vm_state.py` prints only `valid` and `failed`. The launch log is read only through `'run_id': '` lines (no other harness print carries that pattern). `copy_verify` reads bytes, not content. `tools/context_pack.py` reads no runs; `check_docs.py` reads `valid`.
- The six single-rate configs expand to exactly the sweep's run at their rate (the configs' `sweep` key is the only difference). E1 folders exist on neither the Mac nor the VM side named in the repo (0 matching folder names on the Mac).
- Moving off a7bb77a does not touch REG-19's data or `final.sh`, which is Mac-only. The harm is limited to DA5(b) and the need for a move back (DA-O7).
- Treating `gpu_steady`'s coverage failures as heat is sound: it allows one rerun instead of two and adds to the global stop, so it is never looser. The [RESULT] should not call them heat (DA-O5).
- R5's BELIEF holds on reading the diff: with the cap off, the load generator changes only in bookkeeping and flushing.

### Could not check
- The cold spans 1.73–1.81 and the RUN tags of runs (they need reads beyond folder names).
- The replay floors 1.744/1.771 (verified by the draft-3 review; not recomputed here, because analysis-module commands are outside my limits).
- `docs/claims.md` K2 and `experiment-plan.md` step E1.
- Whether a sudoers rule for `nvidia-smi -pl 350` exists.

### 5. Verdict
**NOT READY.** Apply first: DA1, DA2, DA3, DA4, DA5, DA6, DA7, DA8, DA9, DA10, DA11, DA12.
- DA1 and DA2 change `common.sh`, `queue.sh`, `launch.sh` and `test_sandbox.sh`. The patches and changed cases were tested at 177 of 177 in scratch; rerun the sandbox in the repo after applying them.
- DA6 changes `analysis/e1.py`. `e1.py` is outside REG-21's and REG-22's frozen closures. Rerun `tests/test_e1.py`.
- The other items are text and tags.
- Because DA1, DA2 and DA6 are code changes, the review-stop rule calls for a second round on the new bundle.
