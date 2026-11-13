# REG-20 ops scripts: design notes (the scripts themselves are NOT yet written)

Written 2026-11-13 by a teammate agent. 0 GPU h. The VM was not contacted, and no run folder or probe output was opened. The work stopped at the usage limit, before any script was written. This file records the registered rules found, each with its citation, and the points the scripts must settle, so that the next session can write `common.sh`, `vm_state.py`, `session_probe.sh`, `launch.sh`, `queue.sh` and `test_sandbox.sh` from REG-19's `ops_r3`.

## Registered rules to implement

| Rule | Source | Design |
|---|---|---|
| The gate is computed once, after REG-19's [RESULT]; arm A starts only if it passes | FILE(docs/decisions.md:4051), FILE(docs/decisions.md:4168) | The scripts never compute it. Use `GATE_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[DECISION\] \((owner|delegate)\) REG-20 arm A starts: k1\.reg20_a_may_start passed'`, matched by `git grep` on HEAD's `docs/decisions.md`, and also require a `^## … · \[RESULT\] REG-19` heading on an earlier line |
| Arm A: `burst_l1pl350ol_r2.0_w3000_s{15..19}`, in order 15–19 | FILE(docs/decisions.md:4052), FILE(docs/decisions.md:4056) | `ARM_A` array |
| Drift run `burst_l1pl350cl_r2.0_w3000_s15_drift`, "after arm A's third run" | FILE(docs/decisions.md:4053) | Ambiguous, see below. Proposed: after seed 17's burst run and its control, if one is due |
| Controls `stage2_control_l1pl350ol_r{2.0,2.5}_w3000_s{n}`, only for an open run that ends cold-backlogged, right after it | FILE(docs/decisions.md:4054) | Needs a per-run reading in the middle of the matrix, see below |
| Arm B `burst_l1pl350ol_r2.5_w3000_s{15,16,17}`, only after `supports`/`supports_no_mechanism` | FILE(docs/decisions.md:4055), FILE(docs/decisions.md:4081) | A second queue mode, `ARM=B`, gated by its own heading pattern `… REG-20 arm B starts: k1.b_may_start` |
| 350 W read, idle ≤ 45 °C, clean tree at the registered commit; one rerun of a run the automatic checks invalidate; stop and ask on a client error, on a burst that does not fill the pool, or on an unexpected pre-launch check | FILE(docs/decisions.md:4057) | `MAX_ATTEMPTS=2` (REG-19 used 3). No rerun after `no_errors/client_error` or `manipulation`; the owner allows one with `state/rerun_ok_<run id>.txt`. `power_limit` and the second `gpu_steady` stop are carried over from REG-19 ("as for REG-17 to REG-19") |
| `ulimit -n` ≥ 4096 in the shell that starts the harness, for the open arm | FILE(docs/decisions.md:4057); FILE(agent/RUNBOOK.md:28) (soft limit 1024, hard limit 1,048,576, read 2026-11-12) | The pre-launch read records `ulimit -Hn` and `(ulimit -n 65536 && ulimit -n)` and stops below 4096. The tmux command is `ulimit -n 65536 && echo "nofile $(ulimit -n)" && exec ~/.local/bin/uv run python -m harness.run …`, and the `nofile` line from the launch log goes into the attempt record |

## Points the registration leaves open, or that conflict with the code (for the coordinating agent and the owner)

1. **"After arm A's third run"** (FILE(docs/decisions.md:4053)) does not say whether a conditional control counts as a run. The proposal counts burst runs only, so the drift run comes after seed 17's burst run and its control.
2. **No CLI exists for the per-run control decision.** `k1.py`'s `__main__` offers only `reg20` (the whole table, which would be an interim look) and `reg20_a_may_start` (FILE(analysis/k1.py:303-305)). A control needs `k1.cold_backlogged` on the open burst run just made. Two options:
   - a wrapper in `ops/` that prints only `cold_backlogged True|False|None`, run from the pin worktree;
   - a CLI entry added to `k1.py`, which is an edit and is the coordinator's or owner's call.

   For a `None` reading (`unclear`), the proposal is: no control.
3. **`lost_open` needs two invalid runs** (`_open_row`: `lost = ob is None and n_bad >= 2`, FILE(analysis/k1.py:283-286)), yet the standing instructions stop without a rerun after a client error. A stuck open run is the likeliest to fail on client errors (review T3, FILE(docs/decisions.md:4103)). If the owner does not allow the rerun, that seed reads `not_run`, not `lost_open`, and is dropped instead of counting as cold.
4. **Arm B's seal.** `analysis/withheld.py` lifts the REG-20 seal on every `*_l1pl350ol_r2.[05]_*` folder at "[RESULT] REG-20". If arm A's outcome is logged under that heading before arm B runs, arm B is unsealed before it runs.
5. **Quiet hours.** `ops_r3` uses 14:15–18:00 UTC (a control from 11:45, a burst run from 13:00; FILE(docs/probe/20261113_reg19/ops_r3/common.sh:25)). The 02:30–05:00 window is only a patch that has not been applied (`docs/drafts/reg19_ops_r3_patch/`). An open burst run may need a control right after it, so it should start only when a pair still fits, as REG-19's control does. The drift run and a control need room for one run only.
6. **The drift run's `ulimit`.** The registration asks for the read "for the open arm". REG-19's closed run of seed 15 ran at 1024, so the proposal does not raise the limit for the drift run and only records it.
7. **Pin.** See `PIN_DECISION_DRAFT.md`.
