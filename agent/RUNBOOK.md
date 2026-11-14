# RUNBOOK: how a GPU item is run

Written 2026-11-13, before any GPU run of this session. Read with `agent/DECISION_TREE.md`. Nothing here overrides a registration: where they differ, the registration rules and this file is wrong (fix it and log a [CORR]).

## 0. Before anything

1. `git log -5`, `git status` on the Mac. If HEAD moved by a commit not in `agent/LOG.md`, read it first.
2. The item must be registered **and** approved (owner, or a `[DECISION] (delegate)` entry written after the rule F and owner-proxy reviews). An item that is only drafted does not run.
3. `agent/STOP` absent; `docs/decisions.md` has no entry ending the delegation.
4. The watcher says `up_idle` (`cat agent/run/gpu_watch.last`). `up_busy` (a compute process that is not ours) or `up_nogpu`: do nothing, log the state change, keep doing zero-GPU work.

## 1. Host

- VM `inference-vm`: `chalshik@100.83.53.50` (Tailscale), `chalshik@192.168.3.249` (home LAN); key `~/.ssh/id_ed25519_vllm`; always `-o BatchMode=yes -o ConnectTimeout=10`. An SSH timeout is not evidence that a run died: retry over the other address and re-check `checks.json` for about two minutes before concluding anything (the false "TMUX GONE" of 2026-11-12).
- Repo on the VM: `~/aftershock-artifacts`, whose `origin` is the bare repo `~/repos/aftershock-artifacts.git`. Over SSH `uv` is `~/.local/bin/uv`.
- The GPU is shared and the VM can be powered off from outside at any time. A reboot resets the power limit to 420 W.

## 2. Preflight (every launch; the launch script does it and writes the read to `docs/probe/<date>_<item>/`)

| Check | Rule | On failure |
|---|---|---|
| Power limit | `ssh … sudo -n nvidia-smi -pl 350`, then `nvidia-smi --query-gpu=power.limit --format=csv` reads `350.00 W` | If `sudo -n` fails: no 350 W run starts; write it at the top of `agent/FOR_AUTHOR.md`; keep doing zero-GPU work |
| Temperature | ≤ 45 °C (wait up to 30 min) | stop the launch |
| Other processes | `nvidia-smi --query-compute-apps` empty; no tmux session `run` | stop; never kill another process |
| VM tree | `git log -1 --format=%h` equals the item's pinned commit; `git status --short` empty | stop |
| Disk | free space ≥ 4 × the item's expected size (≈ 240 MB per 4080 s run) | stop |
| The registration's own start rule | as written in its [REG] | stop |
| Open-loop arms only (REG-20) | `ulimit -n` ≥ 4096 in the shell that starts the harness. Read 2026-11-12: soft limit 1024, hard limit 1,048,576, so the launch command sets `ulimit -n 65536` first and the read must show it | stop (REG-20's rule) |

No root command other than `sudo -n nvidia-smi -pl 350`. No `git pull` on the VM while a run is in progress.

## 3. REG-19, seeds 18 and 19 (rewritten 2026-11-13 ≈ 12:45 UTC; blocked on the owner's attempt-3 decision)

REG-19 runs only by the owner's [DECISION] of 2026-11-13 (resume, attempts 1–2) and the scripts in `docs/probe/20261113_reg19/ops_r3/` (`common.sh`, `vm_state.py`, `session_probe.sh`, `launch.sh`, `queue.sh`, `final.sh`; sandbox `test_sandbox.sh`, 160 of 160). Attempt 2 of seed 18's control was lost at ≈ 04:40 UTC; one attempt is left and needs a new `[DECISION] (owner)` (draft: `docs/drafts/reg19_attempt3_decision_draft1.md`). The earlier scripts (`ops/launch7.sh`, `queue_reg19e.sh`, resume drafts 1–4) were moved to `_to_delete/` on 2026-11-13 (listed in FOR_AUTHOR). Worktree at `a7bb77a`: `/Users/chalshik/Projects/aftershock-reg19-pin` (run folders linked into its `runs/`).

**REG-19's table is computed only by `zsh docs/probe/20261113_reg19/ops_r3/final.sh`**, once, never by hand, never mid-matrix, and its two files (`ops_r3/state/reg19_final_<stamp>.txt` and `…_err_<stamp>.txt`) are committed at once, alone (`git add <the two files> && git commit -m "[OPS] REG-19 table <stamp>"`). This is REG-19's own rule. Under the plan of 2026-11-13 (Step 1), REG-21 and REG-22 no longer rest on that commit as a "record": their batch 2 needs only that their entries are committed before the first `reg19_final_*` file and that their judged code is unchanged since the entry. So **`final.sh` waits until both entries are committed**, or until their review has ended with batch 2 labelled retrospective by design.

0. When the VM answers: `zsh agent/bin/vm_back_probe.zsh` (read-only); an [OPS] entry with what it printed; stop. The owner sets 350 W, decides attempt 3 (with its `lost_ok` record and the allowance of `RENEW=1`), and may change the quiet hours.
1. VM stays at `a7bb77a`; do **not** push or pull.
2. `RENEW=1 zsh docs/probe/20261113_reg19/ops_r3/session_probe.sh`, commit its files; then from the repo root on the Mac, in the background:
   `nohup caffeinate -i zsh docs/probe/20261113_reg19/ops_r3/queue.sh > docs/probe/20261113_reg19/queue_<stamp>.txt 2>&1 &`
3. The queue prints only `RUN … VALID/INVALID`, `COPIED …`, `STEP after seed N: 'done': […] 'continue': …`. Read nothing else of a run (`ALLOWED` in `common.sh:34`). A stop (`QUEUE STOP …`) is handled by its cause:
   - invalid run: read its `checks.json` only; rerun unchanged if the registration's stopping rule allows (at most twice per run; heat once after cooling); `client_error`, a burst that did not fill the pool, a wrong limit: the queue stays stopped;
   - VM off: record a partial matrix, never pool it, wait for the watcher;
   - `sudo -n` failed: FOR_AUTHOR, no run.
4. After `QUEUE DONE` or `QUEUE END futility stop`: once, `zsh docs/probe/20261113_reg19/ops_r3/final.sh` from the repo root (it checks the step records, rechecks validity, stamps, and saves stdout and stderr in `ops_r3/state/`); then **at once, before any other commit**, commit those two files alone (the box above). ~~Old step: `python -m analysis.gate reg19 > docs/probe/20261113_reg19/reg19_table.txt` from the worktree~~ (struck: no stamp, outside `state/`; it would leave REG-21 and REG-22 without a record).
5. Then, in this order: the [OPS] entry (the four queue stops of 2026-11-12 from RESUME.md, the interim look it records, this session's stops, per-run launch reads); the [RESULT] (k of n, bound, `k_18`, the registered wording; alternatives; the decision taken from `agent/DECISION_TREE.md`); `docs/model.md`'s next free ledger row (rows are numbered when appended, in the order entries land); `docs/status.md`; `docs/claims.md` status lines; `python3 tools/context_pack.py`; `python3 tools/check_docs.py`; commit (manifest, probes, entries).
6. After the [RESULT]: copy the lost seed-18 folder from the VM (`rsync`, checksum, `tools/manifest.py update`, status.md "No checks" list); then deploy HEAD (§4); then `uv run python -m analysis.recheck '*_w3000_s1[5-9]'` and report it beside the result.

## 4. Deploying `main` to the VM (only between items, never during a run, never before REG-19's [RESULT]; never while E1 holds the VM, that is from E1's `docs/probe/20261113_e1/ops/vm_checkout.sh` until E1's end entry (decisions.md [REG] E1, "E1 holds the VM"), nor while E1's queue lock `docs/probe/20261113_e1/ops/state/queue.lock` exists; E1 moves the VM only with its own `vm_checkout.sh`, to E1's commit, detached: decisions.md, [DECISION] (delegate) E1 approved; if the VM is at E1's commit, detached, `git checkout main` comes first)

1. `git push chalshik@100.83.53.50:repos/aftershock-artifacts.git main` (the `vm` remote points at the LAN address; use it at home).
2. `ssh … 'cd ~/aftershock-artifacts && git pull origin main && git log -1 --format=%h && git status --short | wc -l'`: the hash equals the Mac's, 0 dirty files.
3. `ssh … 'cd ~/aftershock-artifacts && ~/.local/bin/uv sync --frozen --extra server --dry-run'` makes no change (`uv.lock` is never touched).
4. Record the hash as the item's pin in its probe folder. A run from a dirty tree is invalid (rule 6).

## 5. Items after REG-19

For each item: a worktree at the commit that holds its approval (`git worktree add --detach ../aftershock-<item>-pin <commit>`, run folders linked into its `runs/`), so that the registered computation runs from the registered code whatever `main` has become. Launch and queue scripts are written per item as new files under `docs/probe/<date>_<item>/ops/`, derived from `docs/probe/20261113_reg19/ops_r3/launch.sh` and `queue.sh` (single runs) or from the sweep form below; each is reviewed with its registration.

| Order | Item | Command(s) on the VM | Registered computation (once) | Seal lifted by |
|---|---|---|---|---|
| 2 | REG-20 gate | none | `AFTERSHOCK_UNSEAL=REG-20 uv run python -m analysis.k1 reg20_a_may_start` after REG-19's [RESULT] | — |
| 2a | REG-20 arm A | `configs/burst_l1pl350ol_r2.0_w3000_s{15..19}.yaml`, drift rerun after the third; a control only for an open run that ends cold | `AFTERSHOCK_UNSEAL=REG-20 … analysis.k1 reg20` | [RESULT] REG-20 |
| 3 | REG-21 batch 2 | none | `uv run python -m analysis.k3w reg21 2` | — |
| 2b (with 2a) | E1 (E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry; decisions.md [REG] E1, "E1 holds the VM") | `docs/probe/20261113_e1/ops/queue.sh` (its README, "Run order"): the sweep `configs/sweep_l1pl350cl_pc_off.yaml` once; a rate never started, or a rerun, from its single-rate config (same `name`) | `AFTERSHOCK_UNSEAL=E1 uv run python -m analysis.e1 floor`, once, only after REG-21's first [RESULT] (met) and after E0's [REG] is committed or an entry records that E0's gate takes no input from E1's runs; before then no part of E1's floor is computed, quoted or used (no `e1.observed`, `e1.floor_status` or `k2.observed` on E1's runs; decisions.md [REG] E1, "Result, computed once") | [RESULT] E1 |
| 4a | E2 | cache-off sweep, then **only** `AFTERSHOCK_UNSEAL=E0 … analysis.e1 status sweep_l1t16pl350cl_pc_off`; if "ok" or "tail_ok", the cache-on sweep | `AFTERSHOCK_UNSEAL=E0 uv run python -m analysis.k2 observed` | [RESULT] E0 |
| 5 | D1, D2 | not registered | — | — |
| 6 | Confirmation run | not registered | — | — |
| 7 | K4 | not registered | — | — |

Sweep form: a sweep is one `harness.run` invocation that writes one run folder per rate; the launch script waits for the tmux session to end, lists the run ids from the log, and requires a `checks.json` for each before anything is copied.

## 6. After every run (the queue script does 1–3)

1. `rsync` the run folder to the Mac's `runs/`; compare the sha256 of every file with the VM's; a mismatch stops the queue.
2. `python3 tools/manifest.py update` (append-only).
3. Link the folder into the item's worktree.
4. The verdict or table is computed only if the registration allows it at that point (REG-19: only `reg19_step`'s flag between pairs).
5. Update the results entry, the paper's pending block, `agent/REPORT.md`'s GPU-hour ledger; commit.

## 7. If the VM goes off mid-queue

Kill nothing on the Mac that is not the queue script. Record what ran (`RUN …` lines), which run was in progress (it will have no `checks.json`; it is kept on the VM and copied later "for the record", after the item's result if its folder matches the item's glob). Never pool a partial cell. Resume through the watcher with the same pinned commit; a lost run is rerun unchanged as the next attempt under the registration's stopping rule.
