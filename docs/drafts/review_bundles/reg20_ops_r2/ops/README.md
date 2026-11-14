# REG-20 arm A: operations scripts

**Status (2026-11-14).**
- The first version of these scripts (draft 1 of the operations decision) is committed in c8b482d. README:3 of that commit said "Nothing here is committed", which was false (rule F round 1, RA7).
- This folder now holds **draft 2's scripts**: c8b482d's files changed in the working tree after rule F round 1 (`docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft1-r1.md`, RA1–RA7, RA-O1–RA-O9) and owner-proxy round 1 (`docs/drafts/reviews-2026-11-13/proxy-reg20-ops-draft1.md`, RB1–RB15).
- Draft 2 adds two new files: `recheck_one.py` and `owner_rulings.txt`.
- A third new file, `gate.sh`, was written for RB5 (ii) and then withdrawn, because the gate had already been computed once: commit 3c8e5dc holds `docs/probe/reg20/gate_20261113T230307Z.txt` and its stderr file. The scripts now read that committed file. The decision draft, point 14, gives the details.
- **Draft 2 is not committed and not reviewed.**
- The decision text is `docs/drafts/reg20_ops_decision_draft2.md`. Where each review item went is in `docs/drafts/reg20_ops_draft2_itemmap.md`.
- 0 GPU h. The VM was not contacted. Nothing under `runs/` was opened beyond folder names, and no `state/` folder or queue output was opened.

REG-20's registration is FILE(docs/decisions.md:4045-4165). The owner's approval is FILE(docs/decisions.md:4166-4171).

`DESIGN_NOTES.md` and `PIN_DECISION_DRAFT.md` are an earlier worker's notes, superseded as their headers say.

**Tests (fakes only, never `runs/`):**
- `zsh docs/probe/20261113_reg20/ops/test_sandbox.sh`: 350 of 350 passed, `sandbox_20261113T231823Z.txt` in this folder.
- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider docs/probe/20261113_reg20/ops/test_control_due.py`: 46 of 46 passed, `test_control_due_20261113T231828Z.txt`.

## Scripts

**`common.sh`** holds the fixed settings and the shared functions.

Settings:
- the pin `1cface7`;
- `MAX_ATTEMPTS=2`, and `MAX_POWER_LOSSES=2` (ruling 8(b));
- the setup class `clean_git kv_capacity trigger` (RA3);
- the holding folder `STAGE` = `<repo's parent>/aftershock-reg20-holding`, outside every `runs/`;
- the commits of the checks in force (`5ee6e38`, `harness/checks.py`) and of `analysis/recheck.py` (`72fafb5`);
- the eleven configs and the plan;
- the heading patterns and the judged code.

Functions:
- `mac_checks`, unchanged from draft 1. It checks that:
  - the pin is an ancestor of HEAD;
  - the lock files and `tools/manifest.py` equal the pin's;
  - all eleven configs exist at the pin;
  - k1's import closure equals the pin's;
  - the two seal files are the recorded blobs;
  - the scripts are committed and named in `scripts_commit.txt`.
- `rulings_ok`: every point in `owner_rulings.txt` holds an answer it may take, and the file is tracked and equal to its commit (RA5).
- `gate_in_log`: four conditions.
  - REG-19's [RESULT] heading, the owner's rulings heading and, after both, `… REG-20 arm A starts: k1.reg20_a_may_start passed` (anchored, RA1).
  - No stop heading after the start (RA-O3).
  - Exactly one committed gate file in `docs/probe/reg20/` (`gate_<stamp>.txt`, from 3c8e5dc), whose one line reads `'may_start': True`, with its stderr file and no `withheld:` line (RB5).
  - `rulings_ok`.
- `vm_state`.
- `decide`, the rerun rule.
- `next_step`.
- `copy_verify`: copy to the holding folder, compare sha256s, recheck, apply ruling 2a, then move into `runs/` (or hold), compare again and update the manifest.
- `recheck_one`, `recheck_apply`, `recheck_guards`.

**The gate is not computed by these scripts.** It was computed once, after REG-19's [RESULT], in commit 3c8e5dc. No script runs `reg20_a_may_start`, and the sandbox fails if any script tries.

**`recheck_one.py`** (new, RB2 and RA2 (b)) applies `harness.checks.run_checks` to one folder in the holding folder:
- it is read-only, and it refuses a folder inside `runs/`;
- it prints only `run`, `stored_valid`, `stored_failed`, `now_valid`, `now_failed`, `changed`, and `error` when the folder cannot be read;
- it imports no analysis module.

**`owner_rulings.txt`** (new, RA5) holds one line per owner's point: `2a`, `6`, `7`, `8`, `9`, `16`.
- Every point reads `unset`. The scripts refuse to start until the owner's entry sets every point and commits the file.

**`vm_state.py`** and **`session_probe.sh`** are unchanged from draft 1.

**`launch.sh <config>`** is draft 1's, plus three lines in the attempt record:
- `arm open|closed`;
- `log <path>`;
- `end <time> <how>`, written when the wait ends. `<how>` is one of `done`, `tmux_gone`, `unreachable` (with the time of the first unanswered read), `still_running`, `no_run_id`, `launch_command_failed`.

These feed the lost runs' elapsed time (RA6) and each control's gap (RA-O1).

**`queue.sh`** runs `mac_checks` first in every turn (RB1). Each turn does one of these:
- **copy:** see `copy_verify`. Under ruling 2a `setaside`, a stored-valid run that today's checks fail stays in the holding folder and the queue stops. A restart reruns its config.
- **hold:** copy and verify into the holding folder only, for the second invalid run of a seed settled `not_run`.
- **due:** `control_due.py` once, on a copied and rechecked valid open burst run. `mac_checks` runs just before and just after it, and if either fails the decision is dropped (RA4).
- **launch:** as in draft 1. A valid open run whose log shows no nofile line of at least 4096 needs `state/nofile_ok_<rid>.txt` (RB15).
- **done:** writes `state/queue_done.txt`. It holds:
  - six slot lines; a control slot carries `gap_s` and `boot same|changed`;
  - `copied`, `held` and `lost …` lines (arm, elapsed time, how it ended, counted or not);
  - `recheck_changed … kept|set_aside|held` lines;
  - the rulings.

**`control_due.py`** is unchanged from draft 1.

**`final.sh`** computes the table once. Before it runs, it checks:
- the gate;
- that the queue has ended;
- the six slot lines;
- each copied run's copy record, recheck record and `checks.json`.

The folders of the eleven configs in `runs/` must equal the copied runs (RB4 (i), RA-O2). The steps, in order:
1. It runs `analysis.recheck` on both patterns (RB2). The changed runs it finds must equal the queue's `recheck_changed … kept` lines.
2. It runs `AFTERSHOCK_UNSEAL=REG-20 .venv/bin/python -m analysis.k1 reg20` (RB5 (i), point 13), with no `uv run`.
3. It runs `mac_checks` again (RA4).
4. It refuses a stderr that holds a `withheld:` line (RA-O2).

## Records

Hand-written records are text files in `state/`, one "key value" per line. Each needs `under <the decision, ruling or [OPS] entry>` and `by owner|delegate`. The scripts check that the writer is one the rulings allow.

| Record | Lines | Who may write it |
|---|---|---|
| `rerun_ok_<rid>.txt` | `lifts <failure>`, one line per failure lifted (RA-O4) | the owner; under 6(b), the delegate for `no_errors/client_error` when the run's log read nofile ≥ 4096 and the boot is unchanged |
| `lost_ok_<rid>.txt` | `count yes\|no` (ruling 8) | after a power-off: 8(a) `count yes` by either; 8(b) `count no` by either, or `count yes` by the owner; without a reboot: the owner |
| `settle_<rid>.txt` | `label not_run\|lost_open\|control_not_run\|drift_not_run` (RB3) | the owner. The delegate may write it: in RA3's case for the label ruling 7 names; for `control_not_run` after the spent attempts under 9(b) |
| `attempt_ok_<cfg>_<n>.txt` | none beyond `under` and `by` | the owner; the delegate for a control's third attempt under 9(a) |
| `nofile_ok_<rid>.txt` | none beyond `under` and `by` (RB15) | either, logged in an [OPS] entry |
| `recheck_ok_<rid>.txt` | `answer keep\|setaside` (ruling 2a `stop`) | the owner |

The queue writes these records itself:
- `copied_<rid>.txt`;
- `held_<rid>.txt` and `setaside_<rid>.txt`, for runs kept in the holding folder;
- `recheck_<rid>.json`, which holds validity fields only;
- `control_due.txt`;
- `queue_done.txt`.

## Launch order (only after: review rounds 2, the owner's rulings, the commit, REG-19's [RESULT] and the gate)

1. Commit this folder. Write `git log -1 --format=%H -- docs/probe/20261113_reg20/ops/{common.sh,vm_state.py,session_probe.sh,launch.sh,queue.sh,final.sh,control_due.py,recheck_one.py}` into `ops/scripts_commit.txt` and commit that file.
2. The owner's entry `## <date> · [DECISION] (owner) REG-20 arm A operations: the owner's rulings`. It quotes `owner_rulings.txt`, and is committed with it.
3. The gate is already computed (3c8e5dc). Only if `docs/probe/reg20/gate_20261113T230307Z.txt` reads `'may_start': True`: write the entry `## <date> · [DECISION] (owner|delegate) REG-20 arm A starts: k1.reg20_a_may_start passed`. The entry quotes the file verbatim, and states how the gate's command differed from RB5 (ii) (decision draft, point 14).
4. The VM, never while a run is in progress (RB6, RA-O7):
   1. Push main to the VM's bare repo (RUNBOOK §4, step 1).
   2. On the VM, run `git fetch origin && git checkout --detach 1cface77ca001cdf5d90de9313ddd4a3af4569a1`.
   3. Check that `git rev-parse HEAD` equals the pin and that `git status --short` is empty.
5. Run `zsh docs/probe/20261113_reg20/ops/session_probe.sh`, with `SET=1` if allowed.
6. Run `nohup caffeinate -i zsh docs/probe/20261113_reg20/ops/queue.sh > docs/probe/20261113_reg20/queue_<stamp>.txt 2>&1 &`
7. After `QUEUE DONE`: run `zsh docs/probe/20261113_reg20/ops/final.sh` once, then commit its files at once, alone.

While arm A runs, no commit may change k1's closure, `analysis/load.py` or `analysis/withheld.py` (RA-O1). Any such commit stops the queue until `common.sh` is updated by a reviewed commit. REG-21's and REG-22's freeze already bars these files until both batch 2s are computed or declared not computed.

## Deviations from ops_r3, and why

1. **No pinned worktree and no links.** Analysis runs from the repo root, and the judged code is checked instead.
   - It is checked at every turn, and just before and just after each `control_due.py` call and the table (RB1, RA4).
   - This departs from `agent/RUNBOOK.md` §5. Draft 2 proposes a RUNBOOK change (see the decision draft).
2. **The gate is three ordered headings plus the committed gate file.**
   - The start heading is anchored on `: k1.reg20_a_may_start passed` (RA1).
   - `([^0-9]|$)` keeps `[RESULT] REG-190` out.
3. **Invalid runs are copied too**, because k1 counts them towards `lost_open`. Every run goes through the holding folder first.
4. **The records** in the table above replace ops_r3's `lost_ok` and `recheck_ok`. ops_r3's recheck guard is kept: `analysis/`, `harness/` and `configs/defaults.yaml` must equal HEAD.
5. **`lost_open` keeps the queue going**, except in RA3's setup case, which stops for a settle record under ruling 7.
6. **No time-of-day limit.** The owner withdrew the quiet hours (FILE(docs/decisions.md:4502)).
7. **The `nofile` redirect** is as in draft 1.
8. **No step records and no futility flag.** These are REG-19's rules.
9. **`final.sh` uses `$PY`**, `.venv/bin/python`.

## Not settled

See the decision draft, "For the owner, before the first launch" (points 2a, 6, 7, 8, 9, 16), and "Not settled".

**Arm B is out of scope** (point 16).
