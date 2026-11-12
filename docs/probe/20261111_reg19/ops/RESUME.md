# REG-19: how to resume (written 2026-11-12 ~16:00 UTC, after the VM went off)

## State
- Done, valid, copied to the Mac with matching checksums, manifest updated (not yet committed):
  - seed 15: `20261112-050920_stage2_control_l1pl350cl_r2.0_w3000_s15`, `20261112-061951_burst_l1pl350cl_r2.0_w3000_s15`
  - seed 16: `20261112-073516_stage2_control_l1pl350cl_r2.0_w3000_s16`, `20261112-084533_burst_l1pl350cl_r2.0_w3000_s16`
  - seed 17: `20261112-103423_stage2_control_l1pl350cl_r2.0_w3000_s17`, `20261112-135538_burst_l1pl350cl_r2.0_w3000_s17`
- `reg19_step` after seed 17: `'done': [15, 16, 17] 'continue': True` (queue_run4_output.txt). No result has been read.
- Lost: seed 18's control `20261112-151030_stage2_control_l1pl350cl_r2.0_w3000_s18`, started 15:10 UTC, the VM went off
  during it (last seen running at 15:25 UTC). Expect no checks.json. Keep its VM folder; copy it to the Mac for the record.
- Not run: seed 18's burst, seed 19's pair.
- The VM must stay at `a7bb77a` (owner, 2026-11-12). The queue is stopped (killed on the Mac at ~15:55 UTC).

## Queue stops so far (for the [OPS] entry)
1. ~10:20 UTC: Mac HEAD moved (other session, docs-only commits) -> launch3's VM == Mac check. Owner: pin VM at a7bb77a -> launch4.
2. ~11:44 UTC: false "TMUX GONE, no checks.json" for seed 17's control (ssh timeouts over a slow link; the run was valid).
   Fix: launch5 re-checks checks.json for ~2 min; queue_reg19c adopts a finished valid control.
   While diagnosing, the agent read the last ~15 lines of that run's harness log (live hit rate after arrivals ended):
   an interim look beyond the `continue` flag; not used.
3. ~11:50 UTC: CLAUDE.md changed (other session) -> owner allowed CLAUDE.md (launch5 edited in place).
4. ~15:25-15:50 UTC: VM off during seed 18's control.

## To resume (all needs the owner)
1. VM on and reachable over Tailscale; on the VM: `sudo nvidia-smi -pl 350` (a reboot resets it to 420 W).
2. Owner decides:
   a. the rerun of seed 18's control (lost run, no checks.json), as attempt 2;
   b. the pin rule: since a7bb77a the other session committed REG-20 code and configs (1cface7: analysis/k1.py,
      analysis/stats.py additions, tests, 17 new configs), so launch5 would stop. `launch6.sh` (proposed) allows only
      additions outside docs (new files, appended lines; nothing under harness/, pyproject.toml, uv.lock). It passed on
      HEAD a126635. harness/, analysis/gate.py, tools/manifest.py and every config REG-19 reads are unchanged since a7bb77a.
3. Command (from the repo root on the Mac, in the background):
   `SEEDS="18 19" ATTEMPT_SEED=18 ATTEMPT=2 zsh docs/probe/20261111_reg19/ops/queue_reg19d.sh`
4. After the queue ends: `uv run python -m analysis.gate reg19` once; [OPS] (stops above) and [RESULT]; model.md row;
   status.md; context_pack; check_docs; commit the manifest, the probes and this folder.
