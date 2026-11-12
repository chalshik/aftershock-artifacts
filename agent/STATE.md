# STATE

Any fresh session resumes from this file alone. Read it, then `agent/PLAN.md`, then the last block of `agent/LOG.md`.
Rules: `docs/FABLE_PROMPT.md` (the start prompt), `CLAUDE.md`, `PROTOCOL.md`, `docs/process.md`.

Last updated: 2026-11-13 (session 8c5f8396, block 3).

## Phase

**Phase 2: zero-GPU work; four reviews running; nothing registered or approved by the delegate yet.** VM still off (read 2026-11-12 19:22 UTC).

## Current task

Waiting for four subagent reviews (started 2026-11-13 ≈ 01:25 local; inputs in `docs/drafts/review_bundles/`):
- `rulef-reg19-resume-2` and `proxy-reg19-resume-2` on the REG-19 resume decision (`docs/drafts/reg19_resume_decision_draft1.md`);
- `rulef-reg21-v3-2` on REG-21 draft 3 (`docs/drafts/reg21_draft3.md`);
- `rulef-e0e1-r2` on E0/E1/E2 draft 3 (`docs/drafts/e0_e1_draft3.md`).
If a session finds no result of these in `agent/LOG.md`, they did not finish: re-run them from the bundles (briefs in LOG block 2).

## Last completed

- Block 1–2: S1–S3, S6–S8, A17, [CORR] owner's choices, drafts (see LOG).
- Block 3: `agent/DECISION_TREE.md` and `agent/RUNBOOK.md` (both written before any GPU run); seals and command lines for E1/E2; `docs/status.md` updated; the three preprints read by this session (`agent/LITERATURE.md`: Huang and Liu end to end, Lu et al. §1–§6.2, §7.1–7.2, §9, Valse and Jannesari §1–§4); local paper files corrected (paper-plan, related-work; inner repo `docs/paper`).

## Next three

1. Process the four reviews: revise each draft, run the owner-proxy on REG-21 and on E0/E1/E2, write the [REG] and [DECISION] (delegate) entries. Add to REG-21 before registering: Valse and Jannesari's own trap rule as a reported per-run reading (uncached token rate within ±15 % of the all-miss rate; backlog slope above 0.5 × the excess), since its token half is REG-21's statistic (LITERATURE.md).
2. After REG-21 is approved: `uv run python -m analysis.k3w reg21` once, [RESULT].
3. Z3: register condition 4 with an executable trace-order test. Design note: the plan's order (hit rate first) is a wipe trigger's; for a burst the entry order is KV full, then reuse falls, then uncached prefill rises, and the test that matters is that all four links hold in every span after the last burst request has left. Then Z4 (K5), Z6a (PROTOCOL and claims.md notes need an owner-proxy pass), Z9, Z7, Z8, Z10.

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
- **Heartbeat:** a session cron job (`CronCreate`, id `3ca81824`, minutes 17 and 47 of every hour) enqueues a "continue the loop" prompt whenever the session is idle. Session-only; expires after 7 days (re-create before 2026-11-20).
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
