# STATE

Any fresh session resumes from this file alone. Read it, then `agent/PLAN.md`, then the last block of `agent/LOG.md`.
Rules: `docs/FABLE_PROMPT.md` (the start prompt), `CLAUDE.md`, `PROTOCOL.md`, `docs/process.md`.

Last updated: 2026-11-13 (session 8c5f8396, block 2; stopped on the usage limit).

## Phase

**Phase 0/2: setup done; three registrations drafted and waiting for their reviews.** The session stopped on 2026-11-13 because the owner's usage limit was reached. No GPU. Nothing registered or approved by the delegate yet.

## Current task

Interrupted mid-review. Three subagent reviews were running and were **stopped unfinished** (no output kept):
- rule F and owner-proxy on the REG-19 resume decision (`docs/drafts/reg19_resume_decision_draft1.md`);
- rule F on REG-21 draft 3 (`docs/drafts/reg21_draft3.md`).
Their input bundles are saved in `docs/drafts/review_bundles/` (the briefs are in block 2 of `agent/LOG.md`). **Re-run them first.**

## Last completed

- S1–S3, S6/S7 (see LOG block 1). S8: `analysis/withheld.py` seals REG-19's and REG-20's runs (12 tests; commit `72fafb5`).
- A17 answered from the pinned source (no skip); [CORR] logging the owner's four choices of 2026-11-12.
- REG-19 resume: draft decision; `docs/probe/20261113_reg19/ops/launch7.sh`, `queue_reg19e.sh`; a git worktree at `a7bb77a` in `/Users/chalshik/Projects/aftershock-reg19-pin` with all 182 run folders linked into its `runs/` (tested with `reg19_inputs`, schedule only).
- REG-21 draft 3 (work rate) with `analysis/k3w.py`, `modelf_sim.simulate(decode_s=)` and 18 synthetic tests.
- E0/E1/E2 draft 3 (`docs/drafts/e0_e1_draft3.md`), not yet reviewed.
- KAIROS Fig. 10–11 check answered (`agent/LITERATURE.md`): the paper shows no frequency trace for that run.

## Next three

1. **Z6b:** re-run rule F and the owner-proxy on the REG-19 resume decision, revise, then write the [DECISION] (delegate). This is what blocks the GPU queue.
2. **Z1:** re-run rule F on REG-21 draft 3, revise, owner-proxy, [REG] + [DECISION] (delegate), then `uv run python -m analysis.k3w reg21` once and the [RESULT].
3. **Z2c:** rule F round 2 and owner-proxy on E0/E1/E2 draft 3; add the E1/E2 seals to `analysis/withheld.py`, an `e1` command-line entry (`python -m analysis.e1 floor`) and `k2 observed`; register and approve.
Then: `agent/RUNBOOK.md` and `agent/DECISION_TREE.md` (before any GPU run), Z6a stale docs (incl. the KAIROS wording in related work), Z9, Z3–Z5, Z7, Z8, Z10.

## Blockers

- `DRIVE_COPIES` path not given and not found on this Mac: the Drive copies' corrections cannot be merged (FOR_AUTHOR item 3).
- GPU: the VM is offline (Tailscale: "offline, last seen 2h ago" at 2026-11-13 00:25 local).

## GPU status

- VM `inference-vm` 100.83.53.50: **offline** at session start. Nothing running. Code on the VM: `a7bb77a` (status.md; not re-read, the VM is unreachable).
- REG-19: seeds 15, 16, 17 done and withheld; seed 18 control lost; seed 18 burst and seed 19 not run.
- Power limit after a reboot is 420 W; the queue needs `sudo -n nvidia-smi -pl 350` first.

## Withheld data (hard rule, start prompt §3)

Do not read outcome data of the six `runs/*_w3000_s15|s16|s17` folders until REG-19's `[RESULT]`. Only `checks.json` may be read, for a rerun decision.
Do not run: `tables.py verdicts|sweeps|published`, `analysis.recheck "*"`, `gate.surge_table`, `gate.reg19_table`, `reg19_step`,
`k3.reg21_table|fit|judge|observed`, `k2.observed`, `e1.observed`, `k1.reg20_a_may_start`, `k1.reg20_table`.

## Delegation (quoted from docs/decisions.md, 2026-11-13 [DECISION])

> Owner, verbatim: "it should never depend on me ... it should run end to end, GPU can return at any time ... I allow it run sudo to set power limit".
> From this entry on, the autonomous agent (Fable, run in this repo) may give the approvals that CLAUDE.md rule C reserves for the owner, for: registrations and GPU runs; reruns under registered stopping rules; the REG-19 resume decisions (seed-18 control rerun as attempt 2, the pin rule); new configs (as new files); analysis-only registrations; corrections of stale docs; and changes to paper claims or their status in docs/claims.md and docs/paper/.
> Each such approval is its own [DECISION] entry tagged "(delegate)", written only after (a) the rule F review by a separate subagent, recorded verbatim in the [REG], and (b) an independent owner-proxy subagent's approval; a reject from either is binding.
> Not delegated: editing runs/, a used config or an old decisions.md entry; choosing or widening a threshold after seeing the data it judges (rule A5); reading outcome data a pending registration withholds; deleting anything; vLLM or uv.lock changes; any root action other than sudo -n nvidia-smi -pl 350 on the VM; posting or uploading anything outside this machine and the VM.
> The owner may overrule any delegate decision later with a [CORR] or [DECISION] entry.
> Ends when the owner writes an entry ending it.

OBSERVED: the entry was in the working copy, uncommitted and without its `## ` marker, at session start. The agent committed it with the marker and line breaks added and no word changed (decisions.md 2026-11-13 [OPS]). Mode: **delegated, not restricted.**

## Self-resume mechanism (tested 2026-11-13)

What works now, while the interactive session `8c5f8396` is alive:
- **Heartbeat:** none now. The session cron job was cancelled on 2026-11-13 when the usage limit was reached; re-create it (`CronCreate`, e.g. `17,47 * * * *`, prompt: continue the loop from STATE.md) when work resumes.
- **GPU watcher:** a background loop in the session runs `agent/bin/gpu_watch.sh` every 15 min and exits, which notifies the session, when `agent/GPU_AVAILABLE` appears. States and the last read: `agent/run/gpu_watch.state`, `agent/run/gpu_watch.last`; changes only in `agent/run/gpu_watch.log`. If the loop is gone, restart it:
  `while true; do zsh agent/bin/gpu_watch.sh; [[ -f agent/GPU_AVAILABLE ]] && break; sleep 900; done` (in the background).

What does **not** work: restart after a crash or a reboot. The launchd jobs that would do it are written and tested (`agent/launchd/`, README there) but **not installed**: Claude Code's permission classifier refused the install (`cp` to `~/Library/LaunchAgents` + `launchctl bootstrap`) on 2026-11-13, and the agent does not work around a refusal. The owner can install them with the three commands in `agent/launchd/README.md`. Tested: a one-off launchd job started `claude -p` and returned `RESUME_TEST_OK`; `RESUME_DRY=1` showed the start/no-start decision is right in both cases.

A fresh session (started by the owner with `claude` in this repo, or by the launchd job once installed) resumes with `agent/RESUME_PROMPT.md`.

## Where things are

| Thing | Path |
|---|---|
| Full snapshot ("the pack") | `docs/paper/context-pack-2026-11-12.md` (local; the start prompt's `docs/context-pack-2026-11-12-full.md` does not exist) |
| Snapshot section files | `docs/paper/ctxpack-2026-11-12/` (local) |
| Papers (PDF + text) | `docs/paper/pdfs/` (local, never committed) |
| Saved drafts | `docs/drafts/scratchpad-2026-11-12/` |
| runs backup | `/Users/chalshik/aftershock-backups/runs-2026-11-13` (same disk) |
| REG-19 resume note | `docs/probe/20261111_reg19/ops/RESUME.md` |
