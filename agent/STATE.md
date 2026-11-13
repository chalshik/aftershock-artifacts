# STATE

Any fresh session resumes from this file alone. Read it, then `agent/PLAN.md`, then the last block of `agent/LOG.md`.
Rules: `docs/FABLE_PROMPT.md` (the start prompt), `CLAUDE.md`, `PROTOCOL.md`, `docs/process.md`. The plan in force: the owner-approved plan of 2026-11-13 (session 8c5f8396; copy at `/Users/chalshik/.claude/plans/lexical-petting-thunder.md`, summarised under "Next three").

Last updated: 2026-11-13 ≈ 13:10 UTC (session 8c5f8396). The update blocks of 05:15 to 12:10 UTC were moved to `_to_delete/agent/STATE_blocks_to_2026-11-13.md` (FOR_AUTHOR, "Things moved"); their content is in `agent/LOG.md` and `docs/decisions.md`.

## Phase

**Phase 2: zero-GPU work while the VM is off.** No run is registered by the delegate yet. No run has been made by this agent. No REG-19 outcome has been read.

## State of each item

- **REG-19** (P0, the owner's): seeds 15–17 are done (6 valid runs, withheld). Both attempts of seed 18's control were lost to the VM going off (2026-11-12 15:51 and 2026-11-13 ≈ 04:40 UTC). The queue stopped by itself at 05:49:28 UTC.
  - Attempt 3 is the last and needs the owner's `[DECISION] (owner)`. It is ready to sign: `docs/drafts/reg19_attempt3_decision_draft2.md` (the stop line, the `lost_ok` text, `RENEW=1`).
  - The quiet-hours patch is prepared, not applied: `docs/drafts/reg19_ops_r3_patch/` (sandbox 167/167; unpatched 160/160).
  - The end kit: `docs/drafts/reg19_end_kit.md`. Steps: `agent/RUNBOOK.md` §3.
  - **`final.sh` waits until REG-21's and REG-22's entries are committed.**
- **REG-21 / REG-22** (K3 step B / C2 condition 4, 0 GPU h): drafts 23 / 14 (commit `e062504`). The record machinery is replaced by a freeze with no exception from the entry commit (plan Step 1; FOR_AUTHOR −10). Four fresh reviews are running: rule F r16 on REG-21, rule F r9 on REG-22, and an owner-proxy on each, named `rulef-reg21-r16`, `rulef-reg22-r9`, `proxy-reg21-d23`, `proxy-reg22-d14`. Their items are named BA (r16), BC (r9), BB and BD (the proxies).
  - **Stop rule, fixed:** wording-only items are applied and the drafts registered. A hole in the two git facts is fixed once. A third round still NOT READY on batch 2 means batch 1 is registered alone and batch 2 is retrospective by design.
- **REG-23** (K5): draft 3 with `analysis/k5.py` exists; never reviewed. Next after REG-21/22.
- **E1:** draft 4; its launch scripts are not written. **E0/E2:** draft 3, NOT READY, needs a redesign.
- **REG-20:** registered and approved by the owner. Its gate needs REG-19's [RESULT]. No ops scripts yet. `ulimit -n 65536` in the launch command is enough (hard limit 1,048,576).

## Next three

1. When the four reviews return: save each verbatim (`scratchpad/extract_handback.py` pattern: the SubagentHandback input) and apply the stop rule. Then register: `[REG]` with every review quoted (`assemble_entry.py`), and the `[DECISION] (delegate)` from `docs/drafts/reg21_decision_draft1.md` / `reg22_decision_draft1.md`, trimmed to the conditions in force. In the same commit: definitions (`docs/drafts/definitions_reg21_reg22.md`), ledger rows, the status notice, FOR_AUTHOR. REG-22 goes first or together with REG-21, both before any batch 1.
2. Batch 1 of each, once (`uv run python -m analysis.k3w reg21`, `uv run python -m analysis.c2 reg22`). Each output is stamped with `date -u` in the command line and committed at once and alone; then its [RESULT]. Then Step 5b: move the superseded `reg21_draft*`/`reg22_draft*` to `_to_delete/`, except drafts 4, 10, 19 / 4, 12, which are line-cited by reviews.
3. REG-23 to rule F and the owner-proxy. In parallel: the vLLM-source answers (A6, the histogram semantics, the TTFT reference point), E1 launch scripts, REG-20 ops scripts, then the preprint (plan Step 4).

## Blockers

- **GPU:** the VM has been off since ≈ 04:40 UTC. The watcher loop (`b2n4cwfii`) runs `agent/bin/gpu_watch.sh` every 3 min and exits when the state changes. When the VM is back: run `zsh agent/bin/vm_back_probe.zsh`, write the [OPS] (end kit A), and stop for the owner.
- The owner: 350 W, the attempt-3 decision, `RENEW=1`, the host's power log (A18), and the choices in FOR_AUTHOR −9 (auto-commit in `final.sh`, pushing `main`).
- `DRIVE_COPIES` path not given (FOR_AUTHOR item 3).

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
- **GPU watcher:** a background loop in the session runs `agent/bin/gpu_watch.sh` every 3 min (since 2026-11-13; earlier every 15 min) and exits, which notifies the session, when the VM's state changes. States and the last read: `agent/run/gpu_watch.state`, `agent/run/gpu_watch.last`; changes only in `agent/run/gpu_watch.log`. If the loop is gone, restart it:
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
| REG-19 resume note (superseded) | `docs/probe/20261111_reg19/ops/RESUME.md` |
| REG-19 scripts in force | `docs/probe/20261113_reg19/ops_r3/` |
| VM-back probe | `agent/bin/vm_back_probe.zsh` |
| Archived (moved, not deleted) | `_to_delete/` (list in FOR_AUTHOR) |
