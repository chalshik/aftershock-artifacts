# E1: operations scripts

**Read with the registration as entered** (docs/decisions.md, `[REG] E1`, and `[DECISION] (delegate) E1 approved`); it rules wherever this folder differs. Stale: the citations of `docs/drafts/e1_draft4.md` in DESIGN_NOTES.md (this file's stale lines were brought up to date for draft 7, rule F e1_r2, DC-O3); and, in DESIGN_NOTES.md, I7 (the pause is now kept in `state/pause_pending.txt` until a queue start has shown it, draft 6, DA2, and `settle` writes it there, draft 7, DC-O1), I3, I4 and R2 (a check other than `gpu_steady`, `no_errors` and `power_limit` in `failed` of two of E1's runs now stops E1, `MAX_SAME`, draft 6, DA1; the pause is no longer the only brake; and a second launch whose log names no run stops E1, draft 7, DC-O2) and I15 (a failed pre-launch check launches nothing and spends no attempt, and is not a stop that ends E1, draft 6, DA3). The code waits for REG-19's queue end as recorded (`END19_PAT`, `ready_to_run`), as the registration says. The scripts were changed for draft 6 (rule F e1_r1: DA1, DA2, DA12, DA-O1, DA-O2) and for draft 7 (rule F e1_r2: DC-O1, DC-O2, and DC-O3's comments) and are reviewed with it; what runs is their text at the registered commit (`mac_checks`). Step 5's move is approved by E1's approving decision.

Written 2026-11-13 by a teammate agent from REG-19's reviewed `docs/probe/20261113_reg19/ops_r3/`, which is unchanged. The registration is the `[REG] E1` entry in docs/decisions.md (drafts 4 to 7: `docs/drafts/e1_draft4.md` … `docs/drafts/e1_draft7.md`). Its "Stopping rule" and "Pre-launch and launch" are what these scripts implement. 0 GPU h.

- The VM was not contacted.
- No run folder, no `state/` file of another item and no queue output was opened.
- Reviewed with the registration's drafts 5 to 7 (rule F and the owner-proxy; the `[REG] E1` entry lists the rounds).
- `DESIGN_NOTES.md` lists every place the draft had to be read and every difference from ops_r3, plus one open point about the harness E1 would run on.

Test, offline, on fakes: `zsh docs/probe/20261113_e1/ops/test_sandbox.sh`. 192 of 192 passed on 2026-11-13 for draft 7 (PROBE(docs/drafts/e1_r3/sandbox_20261113T231637Z.txt)); 184 of 184 passed on 2026-11-13 for draft 6 (PROBE(docs/probe/20261113_e1/ops/sandbox_20261113T214307Z.txt)); 170 of 170 passed on 2026-11-13 after the queue-end gate (PROBE(docs/probe/20261113_e1/ops/sandbox_20261113T204859Z.txt)); 168 of 168 before it. It writes only to a temp folder; set `TMPDIR` to choose where.

## Files

| File | What it does |
|---|---|
| `e1_commit.txt` | The registered commit, the one that holds E1's approval. It says `UNSET` now, and every script refuses while it does. |
| `common.sh` | Every parameter, plus the shared functions: `mac_checks`, `ready_to_run`, `vm_tmux`, `vm_state`, `settle`, `next_step` (E1's stopping rule) and `copy_verify`. |
| `vm_state.py` | Runs read-only on the VM, sent over ssh. Reads only `valid` and `failed` of each E1 run's `checks.json`. |
| `session_probe.sh` | Once per boot. Requires boot id, driver 595.99.02, 350.00 W, and the VM's tree and `uv.lock` at the registered commit. `SET=1` and `RENEW=1` work as in ops_r3. |
| `launch.sh sweep \| <rate>` | Called by the queue. Runs the read-only pre-launch checks, writes the attempt record, starts the invocation in tmux session `run`, and waits until that session ends. |
| `queue.sh` | The one command. It settles, copies, launches and ends, as below. |
| `vm_checkout.sh` | The owner-approved step that moves the VM's tree from REG-19's pin to the registered commit. No other script changes the VM's tree. |
| `test_sandbox.sh` | Fake `ssh`, `rsync`, `sleep`, `uv`, `tmux` and `nvidia-smi`; a throwaway git repo for the Mac, and a bare repo plus clone for the VM. |

## Run order (owner = O, agent = A)

1. **Review (A).** Rule F and the owner-proxy see the registration text and this folder, `e1_commit.txt` still `UNSET`.
2. **Register (A, as delegate under FILE(docs/decisions.md:4516-4520)).** One commit holds three things:
   - the `[REG] E1` entry;
   - after it, a heading of exactly this form: `## <date> · [DECISION] (delegate) E1 approved …` (or `(owner)`);
   - this folder, with `e1_commit.txt` still `UNSET`.

   The scripts recognise the approval only by that heading (`APPROVE_PAT` in `common.sh`).
3. **Name the commit (A).** `git rev-parse HEAD > docs/probe/20261113_e1/ops/e1_commit.txt`, then commit that file alone. From here on, the scripts refuse if any of them differs from its text at that commit.
4. **Wait (A).** Both must hold:
   - REG-19's queue has ended: `test -e docs/probe/20261113_reg19/ops_r3/state/queue.lock` is false (existence only);
   - the committed `docs/decisions.md` holds an `[OPS]` entry headed `REG-19: the queue ended (QUEUE DONE)` or `REG-19: the queue ended (QUEUE END futility stop)` (it quotes the queue's `QUEUE DONE` or `QUEUE END` line), or REG-19's `[RESULT]` (both are in the log: FILE(docs/decisions.md:4611), FILE(docs/decisions.md:16517)).

   And, checked by hand (no script reads REG-20's entries): E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry (registration, "E1 holds the VM"). If REG-20 arm A runs first, step 5 waits for its end entry too.

   The scripts check both (`END19_PAT` in `common.sh`). The registration settles DESIGN_NOTES.md's I11 this way: the owner's entry forbids only a run while REG-19's queue holds the GPU (FILE(docs/decisions.md:4520)). A `QUEUE STOP` leaves no such entry, so E1 waits with REG-19 for the owner.
5. **Move the VM (O approves; A or O types).** Run `zsh docs/probe/20261113_e1/ops/vm_checkout.sh`. It pushes `main` to the VM's bare repository and checks out the registered commit, detached, on the VM. It writes `docs/probe/20261113_e1/vm_checkout_<stamp>.txt`. Commit that file with an `[OPS]` entry. The VM is left with a detached HEAD, so a later RUNBOOK §4 deploy (`git pull origin main`) needs `git checkout main` first.
6. **Power (O).** Set 350 W after any reboot: `ssh … 'sudo nvidia-smi -pl 350'`. `SET=1` on the probe works only if the owner allows it and a sudoers rule exists.
7. **Session probe (A).** Run `zsh docs/probe/20261113_e1/ops/session_probe.sh`. After a reboot, use `RENEW=1 …`, and only with a decisions.md entry. Commit the probe file.
8. **Queue (A), from the repo root, in the background:**
   `nohup caffeinate -i zsh docs/probe/20261113_e1/ops/queue.sh > docs/probe/20261113_e1/queue_<stamp>.txt 2>&1 &`
9. **At `QUEUE DONE` or `QUEUE END`:**
   - commit `state/`, `manifests/runs.sha256` and the probe files;
   - write the `[OPS]` entry, headed `[OPS] E1: the queue ended (QUEUE DONE)` or `(QUEUE END)` (registration, "E1 holds the VM");
   - compute nothing.

   E1's result is a later hand command, run once after REG-21's first `[RESULT]` and after E0's `[REG]` is committed or an entry records that E0's gate takes no input from E1's runs: `AFTERSHOCK_UNSEAL=E1 uv run python -m analysis.e1 floor` (registration, "Result, computed once").

## What the queue prints

| Line | Meaning |
|---|---|
| `LAUNCH sweep attempt 1` / `LAUNCH <rate> attempt <n>` | A launch is starting. |
| `LAUNCHED <run id>` | The first run id appeared in the launch log. |
| `ENDED …` | The tmux session ended. |
| `SETTLED attempt_….txt` | The launch log's `run_id` lines were read. |
| `RUN <run id> VALID` / `INVALID failed=<checks>` / `NO CHECKS.JSON` | Each run from that log. |
| `NOT STARTED rate <r> by the sweep` | That rate goes to its single-rate config as attempt 1. |
| `COPIED <run id> <n> files sha-of-sums <h>` | The copy was verified against the VM's checksums. |
| `QUEUE DONE` (exit 0) | Every rate has a valid run, copied and checksum-verified. |
| `QUEUE END` (exit 3) | Some rate spent its three attempts with no valid run. The other rates are done; the owner decides. |
| `QUEUE STOP …` (exit 1 or 2) | A stop. The allowed-reads line follows it. |

## Stops and what each needs

| Stop | Cause | Needs |
|---|---|---|
| `after an invalid run (…)` | The pause, as REG-19's queue does (I7) | Start the queue again only if no check name stands in `failed` of E1's runs at two or more different rates (registration, stopping rule); otherwise E1 stops for a new decision. Each restart gets an [OPS] entry quoting the `RUN … INVALID` lines |
| `has no checks.json …` | A run ended without `checks.json` (VM off, harness crash) | The owner's decision, then `state/lost_ok_<run id>.txt`, then start again |
| `E1 registers no rerun after no_errors / power_limit` | The registered stop | The owner |
| `<check> is in failed of 2 of E1's runs` | The registered systematic-fault stop | The owner |
| `<n> launches of E1 named no run` | Two launches whose logs hold no `run_id` line: the command failed, or the harness stopped before its first folder (draft 7, DC-O2) | The owner |
| `an invalid run has not been shown at a pause yet` | `launch.sh` by hand while a pause is pending (draft 6, DA2) | Start the queue, which pauses first |
| `the owner halted E1` | An entry headed `[DECISION] (owner) E1 halted` (draft 6, DA-O2) | The owner |
| `second heat failure (gpu_steady)` | The registered stop. See the open point: under the new checks `gpu_steady` is not only heat | The owner |
| `power limit '420.00'`, `rebooted since the session probe` | A reboot | Owner sets 350 W; `RENEW=1` probe with a decisions entry; start again |
| `GPU at '<t>' C`, `GPU compute process present`, `a tmux session exists`, `VM tree …`, `uv.lock …`, `kB free` | Other pre-launch checks; no attempt spent | Find the cause, then start again |
| `the tmux session 'run' is alive` / `STILL RUNNING` / `VM NOT REACHABLE` | An invocation is running, or the VM is unknown | Wait, then start again |
| `which no settled launch log … names`, `made at commit …`, `the Mac holds …`, `is not on the VM` | A run outside these scripts, or a moved folder | The owner |

While diagnosing a stop, read only what the allowed-reads line names: `tmux has-session -t run`; folder names; `valid` and `failed`; and, in a launch log, only the lines holding `run_id` or `[run] checks` (registration, stopping rule).

A stop that an entry decides ends E1 is recorded by an entry headed `[OPS] E1 ended by a stop: <the stop line>` (registration, "E1 holds the VM"). A pause, or a stop that waits for a decision, is not an end.
