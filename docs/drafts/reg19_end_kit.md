# REG-19 end kit (drafted 2026-11-13, before any outcome exists)

These are skeletons for the entries that REG-19's last steps need, written in advance so that they are not composed after the data. Every `<…>` is filled from a probe file or a saved output, never from memory. No outcome value appears here. The steps are those of `agent/RUNBOOK.md` §3. The branch, the next action and the paper sentence for each outcome are in `agent/DECISION_TREE.md`, "P0".

## A. When the VM answers (agent): one [OPS], then stop for the owner

```
## <date> · [OPS] The VM is back after the power-off of 2026-11-13 ≈ 04:40 UTC: what it shows, read-only; REG-19 waits for the owner's attempt-3 decision

- **Probe:** PROBE(docs/probe/20261113_reg19/vm_back_<stamp>.txt), by `agent/bin/vm_back_probe.zsh` (read-only; no run folder and no harness log opened), via <Tailscale | LAN>.
- **Boot:** new boot id <id>, up since <time>; the previous boot's last lines and any power-key, thermal or Xid line: <quoted from the probe>.
- **GPU:** limit <W> (350 needs the owner), <n> compute processes, tmux <state>; tree <hash>, <n> dirty files; free <kB>.
- **REG-19's folders on the VM** (`vm_state.py`: names, valid/invalid, failed check names only): <quoted>. Attempt 2's folder `20261113-033842_…s18`: <checks.json present or not>.
- **What `gate` and `decide` say for the four configs left:** <quoted>; `decide` refuses attempt 3 until the `lost_ok` record exists (expected).
- **Open question A18:** the row for this end is filled in (`docs/open-questions.md`), and the attempt-3 draft's journal line is filled in (`docs/drafts/reg19_attempt3_decision_draft2.md`).
- **Not done:** no launch, no 350 W (the owner's), no `RENEW=1` probe (needs the owner's entry). FOR_AUTHOR's top item is updated.
```

## B. The owner's attempt-3 decision

This is `docs/drafts/reg19_attempt3_decision_draft2.md`. With it come:
- the `lost_ok` record, whose text is in the draft;
- the quiet-hours patch, `docs/drafts/reg19_ops_r3_patch/`, if the owner takes item 3;
- `scripts_commit.txt` and the `RENEW=1` session probe, each committed.

## C. At `final.sh` (agent; only after REG-21's and REG-22's entries are committed, RUNBOOK §3)

1. Check, by file names only, that `docs/probe/20261113_reg19/ops_r3/state/` holds no `reg19_final_*` file.
2. Run `zsh docs/probe/20261113_reg19/ops_r3/final.sh` once.
3. Commit its two files at once, alone:

```
git add docs/probe/20261113_reg19/ops_r3/state/reg19_final_<stamp>.txt docs/probe/20261113_reg19/ops_r3/state/reg19_final_err_<stamp>.txt
git commit -m "[OPS] REG-19 table <stamp> (final.sh, once; nothing else in this commit)"
```

If `final.sh` raises, its two files go in with the [OPS] entry that `final.sh` requires before a second try (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:31)).

## D. The [OPS] for the queue (before the [RESULT])

```
## <date> · [OPS] REG-19's queue for seeds 18 and 19: every launch, stop and copy, and the boots it ran in

- Launches, with attempt, boot id, launch read (limit, temp, driver) and run id: <from state/attempt_* and the queue output, names and reads only>.
- Stops and their causes (2026-11-12: four, from RESUME.md; 2026-11-13: attempt 2 lost at ≈ 04:40 UTC, stop line FILE(docs/decisions.md:4306); later: <…>).
- The interim look of 2026-11-12 (seed 17's control's harness log, FILE(docs/decisions.md:4276)), restated; any other read beyond `common.sh`'s ALLOWED: <none known | listed>.
- Copies and checksums: <COPIED lines>; manifest <command, output>.
- The recheck before the table (`final.sh`): <its lines>.
```

## E. The [RESULT] skeleton

```
## <date> · [RESULT] REG-19 (P0 at λ = 2.0, seeds 15–19, whole-window test): <outcome>, <k> of <n> (k_clear <…>), one-sided 95 % upper bound <u>

- **Computation:** `final.sh` at <stamp>, FILE(docs/probe/20261113_reg19/ops_r3/state/reg19_final_<stamp>.txt:1), commit <hash>; code at the pin `a7bb77a` (worktree), checks in force (A14) applied before the table.
- **Per seed:** label, outcome, `outcome_18`, c1, drain time, cold side; copied from the saved output, never retyped by hand.
- **k_18 under REG-18's per-span test:** <k_18> of <n>.
- **Order flag and the controls' waiting share:** <…>.
- **Wording:** the registered sentence for this outcome, from `agent/DECISION_TREE.md` P0 and nothing stronger.
- **Alternatives (rule A2), at least two, each with what would separate them:** <…>.
- **Deviations:** the two lost runs of seed 18's control (attempts 1 and 2), the boots, and the interim look; none of them selects on outcomes, because a lost run is never opened.
- **Decision taken:** the P0 row of `agent/DECISION_TREE.md` for this outcome, quoted.
- **Then:** `docs/model.md`'s next free ledger row; `docs/status.md`; `docs/claims.md` status lines; `python3 tools/context_pack.py`; `python3 tools/check_docs.py`; commit. After that, the lost seed-18 folders are copied (`pending_copy`), HEAD is deployed to the VM (RUNBOOK §4) and `analysis.recheck` is reported beside the result.
```

## F. After REG-19's [RESULT]: what unlocks

- **REG-21 batch 2** (`uv run python -m analysis.k3w reg21 2`) and **REG-22 batch 2** (`uv run python -m analysis.c2 reg22 2`). Each needs its registration's two git facts and its hand duties.
- **REG-20's gate** (`AFTERSHOCK_UNSEAL=REG-20 uv run python -m analysis.k1 reg20_a_may_start`). It must run before both batch 2s, or every result must state the order.
- **The DECISION_TREE row** for the outcome.
