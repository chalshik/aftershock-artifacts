# STATE

Any fresh session resumes from this file alone. Read it, then `agent/PLAN.md`, then the last block of `agent/LOG.md`.
Rules: `docs/FABLE_PROMPT.md` (the start prompt), `CLAUDE.md`, `PROTOCOL.md`, `docs/process.md`. The plan in force: the owner-approved plan of 2026-11-13 (session 8c5f8396; copy at `/Users/chalshik/.claude/plans/lexical-petting-thunder.md`, summarised under "Next three").

Last updated: 2026-11-13 ≈ 16:10 UTC (session 8c5f8396). The update blocks of 05:15 to 12:10 UTC were moved to `_to_delete/agent/STATE_blocks_to_2026-11-13.md` (FOR_AUTHOR, "Things moved"); their content is in `agent/LOG.md` and `docs/decisions.md`.

## Phase

**Phase 3: REG-19's last runs are scheduled; registrations in review.** The VM came back at 15:20 UTC (boot `06d8b294`; [OPS] "The VM is back"). The owner approved attempt 3 and the quiet-hours patch and set 350 W (decisions.md 2026-11-13 [DECISION] (owner), attempt 3). No REG-19 outcome has been read. No run registered by the delegate yet.

## State of each item

- **REG-19** (P0): seeds 15–17 done (6 valid, withheld). Seed 18's control: attempts 1 and 2 lost (`nochecks`); **attempt 3, the last, starts by a detached timer at 18:00:30 UTC** (`caffeinate` + `sleep`, pids 71631/71633 at scheduling), output `docs/probe/20261113_reg19/queue_agent_20261113T180030Z.txt`. Scripts: ops_r3 with the quiet-hours patch (no run overlaps 02:30–05:00 or 14:15–18:00 UTC; sandbox 167/167; `scripts_commit.txt` = `ea4a25e`); session probe renewed for boot `06d8b294` (SESSION OK, 350.00 W).
  - The watcher `bwnigx6gj` exits when the VM goes down or the queue prints `QUEUE STOP|DONE|END`. Then: read only the queue's allowed lines; RUNBOOK §3 step 3 for a stop.
  - If attempt 3 is lost: the queue stops, no table, the owner decides (attempt-3 entry, item 4).
  - **`final.sh` waits until REG-21's and REG-22's entries are committed** (or their review ends with batch 2 retrospective by design). End kit: `docs/drafts/reg19_end_kit.md`.
- **REG-21 / REG-22** (0 GPU h): drafts 24 / 15 (commit `ba67e55`), the one allowed fix of the freeze after round 1 (rule F r16 NOT READY BA1–BA4 + proxy REJECT BB1–BB9; rule F r9 NOT READY BC1–BC3 + proxy APPROVE BD1–BD9; all saved verbatim). Whole-file freeze of the import closure; fact (2) on the earliest `reg19_final_*` stamp anywhere; validity frozen from the entry. **Round 2 running:** `rulef-reg21-r17` (BE), `proxy-reg21-d24` (BF), `rulef-reg22-r10` (BG), `proxy-reg22-d15` (BH).
  - **Review-stop rule** (decisions.md 2026-11-13 [DECISION] (delegate), settled): at most three rounds on the freeze; after drafts 24/15 a change to the facts is allowed only if wording, a tag, stricter or a reporting duty; a round-2 NOT READY on batch 2's standing with a design item, or a round-3 NOT READY on it, means batch 1 alone and batch 2 retrospective by design (still computed once with the frozen code), with its own rule F and proxy.
  - **The freeze binds from the entry:** no commit to the 23 frozen files (k3w/c2 import closure, pyproject.toml, uv.lock) until both batch 2s are computed or declared not computed. REG-20 code, SEALS changes (arm B), everything new: new files only.
  - The transcript search (`docs/probe/20261113_transcript_search/search.py`) is rerun at the append; the [DECISION] (delegate) maps every proxy condition (BD9) and repeats the statement on REG-19 readings.
- **REG-23** (K5): draft 5 (`docs/drafts/reg23_k5_draft5.md`, commit `ea762b9`), code `63e8c65` (k5.py: Lr comparator and `leads_slo_only`, paired lead over A with the 120 s hurdle and ≥ 5 A onsets, `too_few_events` and `REASONS`, `alarm_share`, Poisson upper bounds per load, CP bounds, scan-start/recovery flags, peak A sent/planned; 15 tests). **Round 2 running:** `rulef-reg23-r2` (CC), `proxy-reg23-d5` (CD), bundle `reg23_r2`. Pending wording fix for draft 6 / the assembly: alternative 8 is already answered by S8 (FILE(docs/open-questions.md:33); source re-verified 2026-11-13, tarball sha256 matches), so it is a fact, not a BELIEF.
- **E1:** draft 4; launch scripts not written. **E0/E2:** draft 3, NOT READY, needs a redesign.
- **REG-20:** registered and approved by the owner; gate after REG-19's [RESULT] and before both batch 2s (arm A ≈ 0.2 by its own prediction; on a gate failure with ≥ 3 closed runs cold the tree says REG-20b, which reuses the same ops). **`reg20-ops-writer` running** (since ≈ 16:10 UTC): writes `common.sh`, `vm_state.py`, `session_probe.sh`, `launch.sh`, `queue.sh`, `final.sh`, `control_due.py`, `test_sandbox.sh`, README into `docs/probe/20261113_reg20/ops/`, new files only, nothing committed. The design points I fixed in its brief (pin `1cface7`; gate heading pattern; drift run after the third burst run and its control; `control_due.py` printing only `CONTROL_DUE yes|no|unclear`, unclear = no control; client error = stop; ulimit ≥ 4096 for the open arm; quiet hours with a two-run fit for open burst runs; arm B out of scope) are proposals: they need a [DECISION] (delegate) with rule F and an owner-proxy pass before any REG-20 run.

## Next three

1. When round 2 returns: save each verbatim (the teammate message, from the main transcript), commit, apply the review-stop rule. If cleared: dry-run the assembly through check_docs (the relative `FILE(delegation.md:…)`/`FILE(round1_rule_f.md:…)` refs in `proxy-reg21-draft4.md` need an annotated path), rerun the transcript search, then register REG-22 and REG-21 ([REG] + [DECISION] (delegate) mapping every proxy condition), with definitions, ledger rows, the status notice and FOR_AUTHOR in the same commit.
2. Batch 1 of each, once, stamped files under `docs/probe/reg21/` and `docs/probe/reg22/`, each committed alone; [RESULT]s. Then `final.sh` once the queue has ended (end kit C).
3. When REG-23's round 2 returns: save both verbatim, apply; register if READY and APPROVE (with S8 replacing alternative 8). When `reg20-ops-writer` returns: review its scripts and sandbox, write the REG-20 ops [DECISION] (delegate) draft (pin and the design points), send it to rule F and the owner-proxy. Then E1 scripts, the preprint.

## Blockers

- **GPU:** in use by REG-19 from 18:00:30 UTC. If the VM goes down again: record the partial matrix, never pool, and the owner decides (three attempts are spent).
- The owner: the host's power-key cause (A18; all eight ends are power-key presses), the sudoers rule for 350 W (FOR_AUTHOR −2), and FOR_AUTHOR −9 (auto-commit in `final.sh`, pushing `main`).
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
