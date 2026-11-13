# REG-20 arm A: operations scripts

Written 2026-11-13 by a teammate agent from REG-19's reviewed `docs/probe/20261113_reg19/ops_r3/`, which is unchanged. 0 GPU h. The VM was not contacted, and no run folder or queue output was opened. **Nothing here is committed, and nothing has been reviewed yet.** REG-20's registration is FILE(docs/decisions.md:4045-4165) and the owner's approval is FILE(docs/decisions.md:4166-4171). `DESIGN_NOTES.md` and `PIN_DECISION_DRAFT.md` are an earlier worker's notes.

Tests:
- `zsh docs/probe/20261113_reg20/ops/test_sandbox.sh`: 214 of 214 passed on 2026-11-13, after the quiet hours were removed.
- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider docs/probe/20261113_reg20/ops/test_control_due.py`: 35 of 35 passed.

## Scripts

**`common.sh`** holds the fixed settings and the shared functions:
- the pin `1cface7`, `MAX_ATTEMPTS=2`, the eleven configs and the plan;
- the two gate patterns and the judged code;
- `mac_checks`, which checks on the Mac that:
  - the pin is an ancestor of HEAD;
  - the lock files and `tools/manifest.py` equal the pin's;
  - all eleven configs exist at the pin;
  - k1's import closure (`__init__`, `k1`, `gate`, `margin`, `derived`, `floor`, `stats`) equals the pin's;
  - `analysis/load.py` and `analysis/withheld.py` are the blobs of 2026-11-13;
  - the scripts are committed and named in `scripts_commit.txt`;
- `gate_in_log`;
- `vm_state`;
- `decide`, the rerun rule;
- `next_step`, which reads the plan and the state and returns one action;
- `copy_verify`.

**`vm_state.py`** runs read-only on the VM, sent over ssh. It is ops_r3's file byte for byte, with a two-line header added to the docstring.

**`session_probe.sh`** runs once before the queue and is ops_r3's in substance. It requires 350.00 W, driver 595.99.02, the VM tree clean at the pin, and the pin's `uv.lock` on the VM. It writes the boot id that every launch compares against. `SET=1` runs `sudo -n nvidia-smi -pl 350` on an idle GPU. `RENEW=1` replaces an existing probe, and needs a decisions.md entry.

**`launch.sh <config>`** is called by the queue. It launches only the config that `next_step` names, at the attempt number `next_step` gives.
- Pre-launch checks, as in ops_r3:
  - the two gate headings in the log;
  - the GPU at or below 45 °C, waiting up to 30 min;
  - the limit at 350.00 W;
  - no compute process and no tmux session;
  - the VM tree at the pin and clean;
  - the same boot id as the session probe;
  - at least 2 GB free.
- Added for REG-20: the read records `ulimit -Hn` and `(ulimit -n 65536 && ulimit -n)`. An open-loop config stops if the second value is below 4096. For the closed drift run the values are only recorded.
- The open-loop tmux command is `ulimit -n 65536 && echo "nofile $(ulimit -n)" > LOG && exec ~/.local/bin/uv run python -m harness.run configs/<cfg>.yaml >> LOG 2>&1`.
- The drift run uses ops_r3's command unchanged.
- The attempt record holds `nofile_hard`, `nofile_raised` and, for open-loop runs, `nofile_log`, the line from the log.

**`queue.sh`** is the one command. Each turn it asks `next_step` for one of these actions:
- **copy**: copy a finished run, valid or invalid, check its sha256s against the VM's as ops_r3 does, update the manifest, then write `state/copied_<rid>.txt`.
- **due**: run `control_due.py` once on a copied valid open burst run and append its line to `state/control_due.txt`.
- **launch**: launch the next config. After an invalid run it stops. It also stops once after an open-loop run whose log shows `nofile` below 4096, or no `nofile` line.
- **done**: write `state/queue_done.txt`, one line per slot.

The order is 15, 16, 17, the drift run, 18, 19. A control runs right after its burst run, and only when the decision is `yes`.

**`control_due.py <run folder>`** accepts only `^\d{8}-\d{6}_burst_l1pl350ol_r2\.0_w3000_s1[5-9]$`.
- It sets `AFTERSHOCK_UNSEAL=REG-20` inside its own process, replacing any inherited value.
- It loads `analysis.load.RUNS/<name>` with `load_run` and requires `checks.json` valid and the config name to match.
- It prints `CONTROL_DUE yes|no|unclear` from `k1.cold_backlogged(run)["cold_backlogged"]`: True gives `yes`, False gives `no`, None or NaN gives `unclear`.
- Any other outcome prints nothing on stdout and exits non-zero.

**`final.sh`** computes the table once. It requires:
- `state/queue_done.txt`;
- no live queue lock;
- a verified copy of every run the record names;
- no earlier `reg20_final_*` file.

It runs `AFTERSHOCK_UNSEAL=REG-20 uv run python -m analysis.k1 reg20` from the repo root and writes `state/reg20_final_<stamp>.txt` and `state/reg20_final_err_<stamp>.txt`. It was never run.

**`test_sandbox.sh`** and **`test_control_due.py`** run on fakes only and never read `runs/`.

## Launch command (only after review, commit, the owner's pin decision and both gate headings)

1. Commit this folder. Write `git log -1 --format=%H -- docs/probe/20261113_reg20/ops/{common.sh,vm_state.py,session_probe.sh,launch.sh,queue.sh,final.sh,control_due.py}` into `ops/scripts_commit.txt` and commit that file.
2. Check the VM out clean at `1cface77ca001cdf5d90de9313ddd4a3af4569a1`. These scripts do not do it.
3. Run `zsh docs/probe/20261113_reg20/ops/session_probe.sh`, with `SET=1` if allowed.
4. Run `nohup caffeinate -i zsh docs/probe/20261113_reg20/ops/queue.sh > docs/probe/20261113_reg20/queue_<stamp>.txt 2>&1 &`
5. After `QUEUE DONE`, run `zsh docs/probe/20261113_reg20/ops/final.sh` once, then commit its two files at once, alone.

## Deviations from ops_r3, and why

1. **No pinned worktree and no links.** Analysis runs from the repo root, and the judged code is checked instead. The design's `AFTERSHOCK_UNSEAL` needs `analysis/withheld.py`, which the pin predates. Between the pin and HEAD, k1's closure has an empty `git diff`, and `load.py` differs only by the 6-line seal guard. This also departs from `agent/RUNBOOK.md` §5, which asks for a worktree per item.
2. **The gate is two ordered headings**, and `([^0-9]|$)` is added after `REG-19` so that `[RESULT] REG-190` does not match. The addition only refuses more.
3. **Invalid runs are copied too.** `k1._open_row` counts invalid runs on the Mac to decide `lost_open`, and ops_r3 copied only valid ones. Copying is now per run, and the copy record is written after the manifest update.
4. **One record type, `rerun_ok_<rid>.txt`.** It replaces ops_r3's `lost_ok`, and it also lifts the stop-and-ask for that run: client error, `manipulation`, `power_limit` or the second `gpu_steady`.
5. **`lost_open` keeps the queue going.** When both attempts of an open burst run are invalid, the seed takes REG-20's label `lost_open` (counted as cold), gets no control, and the queue goes on. The design was silent on this. A control or the drift run with both attempts spent stops the queue, as ops_r3 does.
6. **No time-of-day limit.** ops_r3 had quiet hours; the owner withdrew them on 2026-11-13 ("there is no such thing as quiet hours, whenever its available use it, power off happens randomly"; FILE(docs/decisions.md:4502)). An earlier version of these scripts copied ops_r3's windows and read run lengths from the configs; both are removed, because nothing else used the lengths. The sandbox now runs the whole queue with the clock at eleven different hours.
7. **The `nofile` redirect.** The `echo` writes `> LOG` and the harness writes `>> LOG`, so the line lands in the log. The remote tmux argument is single-quoted, so tmux's own shell evaluates `$(ulimit -n)`.
8. **No step records, futility flag or `analysis.recheck`.** These are REG-19's rules.
9. **`final.sh` uses `uv run`**, the design's command, not `$PY`.

## Not settled

Each point below is settled, or sent to the owner, in `docs/drafts/reg20_ops_decision_draft1.md` (draft 1, not reviewed).

1. **The pin.** `1cface7` is the coordinator's proposal. The registration names no commit (FILE(docs/decisions.md:4169)). It needs the owner's entry before the VM moves (`PIN_DECISION_DRAFT.md`).
2. **The drift run's place.** It runs after seed 17's burst run and its control, following the design. The registration says only "after arm A's third run" (FILE(docs/decisions.md:4053)).
3. **A lost attempt (no `checks.json`) plus one invalid attempt.** Lost runs are not copied before the result (RUNBOOK §7), so k1 reads the seed as `not_run` and the queue stops. The owner decides.
4. **Recheck before the table.** Whether to recheck validity under HEAD's stricter checks (A14), as REG-19 does, is the owner's call. It is not implemented.
5. **The pre-launch `ulimit` read is a proxy.** It comes from an ssh shell. The launching shell's real value is known only after launch, from the log line, and the queue's stop after the run covers that.
6. **Future changes to the judged code.** Any change on `main` to k1's closure or to the seal files stops the queue until `common.sh` is updated by a reviewed commit.
7. **The queue output shows each control decision.** That reveals one bit per open run, which is inherent to the conditional control.

**Arm B is out of scope.** REG-20's seal lifts both arms at `[RESULT] REG-20` (`analysis/withheld.py`), so arm B needs a new seal in a frozen file. Nothing is written for it.
