# STATE

Any fresh session resumes from this file alone. Read it, then `agent/PLAN.md`, then the last block of `agent/LOG.md`.
Rules: `docs/FABLE_PROMPT.md` (the start prompt), `CLAUDE.md`, `PROTOCOL.md`, `docs/process.md`. The plan in force: the owner-approved plan of 2026-11-13 (session 8c5f8396; copy at `/Users/chalshik/.claude/plans/lexical-petting-thunder.md`, summarised under "Next three").

Last updated: 2026-11-13 ≈ 17:00 UTC (session 8c5f8396). The update blocks of 05:15 to 12:10 UTC were moved to `_to_delete/agent/STATE_blocks_to_2026-11-13.md` (FOR_AUTHOR, "Things moved"); their content is in `agent/LOG.md` and `docs/decisions.md`.

## Phase

**Phase 3: REG-19's last runs are scheduled; registrations in review.** The VM came back at 15:20 UTC (boot `06d8b294`; [OPS] "The VM is back"). The owner approved attempt 3 and the quiet-hours patch and set 350 W (decisions.md 2026-11-13 [DECISION] (owner), attempt 3). No REG-19 verdict has been read; but on 2026-11-12 a context-pack script most likely printed seed 17's two runs' `ok`/`unfinished` request counts (decisions.md 2026-11-13 [CORR], :4453, found by the agent at ≈ 16:50 UTC; round 3's four reviewers were sent it). **The agent's reading, sent to all four:** the drafts' own trigger (REG-21 D25:54, REG-22 D16:80: "a read of a line a REG-19 burst run wrote after its burst began, beyond what is listed") applies to seed 17's burst `checks.json` counts, so both batch 2s are expected to be labelled retrospective by design and batch 1 to be the primary analysis; the proxies may reject that reading. No run registered by the delegate yet.

## State of each item

- **REG-19** (P0): seeds 15–17 done (6 valid, withheld). Seed 18's control: attempts 1 and 2 lost (`nochecks`); **attempt 3, the last, RUNNING since 16:55:12 UTC as `20261113-165516_stage2_control_l1pl350cl_r2.0_w3000_s18`, ends near 18:05** (the owner withdrew the quiet hours and the timer was cut short; queue pid 71631, launch.sh pid 65728), output `docs/probe/20261113_reg19/queue_agent_20261113T180030Z.txt` (read only its QUEUE/STOP: lines). The launch log appears only after launch.sh returns (queue.sh:44–45). Scripts: ops_r3 at `fb06088` (quiet windows emptied; sandbox's quiet-hour cases now fail, to be updated, test only); watcher `bwnigx6gj`; session probe renewed for boot `06d8b294` (SESSION OK, 350.00 W).
  - The watcher `bwnigx6gj` exits when the VM goes down or the queue prints `QUEUE STOP|DONE|END`. Then: read only the queue's allowed lines; RUNBOOK §3 step 3 for a stop.
  - If attempt 3 is lost: the queue stops, no table, the owner decides (attempt-3 entry, item 4).
  - **`final.sh` waits until REG-21's and REG-22's entries are committed** (or their review ends with batch 2 retrospective by design). End kit: `docs/drafts/reg19_end_kit.md`.
- **REG-21 / REG-22** (0 GPU h): **drafts 25 / 16 (commit `90cd0a9`), round 3 on the freeze running, the last** under the review-stop rule: `rulef-reg21-r18` (items BI), `proxy-reg21-d25` (BJ), `rulef-reg22-r11` (BK), `proxy-reg22-d16` (BL); bundles `reg21_r18`, `reg22_r11` (final.sh's copy renamed `final_sh_for_reference.sh`). Round 2 (r17 BE1–BE6 NOT READY + proxy APPROVE BF1–BF10; r10 BG1–BG5 NOT READY + proxy APPROVE BH1–BH10; saved verbatim, 8d0d126) did not stop the review: every item classed wording/tag/stricter/reporting duty/disclosure ([DECISION] (delegate) 2ea2722, which also amends the stop rule with BF10 verbatim: "table file" = `^reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z`; an item's class is its reviewer's). [CORR] on the interim-look entry (BH10 item 2) in the same commit.
  - **Round 3 outcomes:** READY + APPROVE (or only items of the allowed classes) → apply, register (`build_reg_entries.py`), [DECISION] (delegate) each with BF9 (a)–(f) / BH10 items 1, 3, the closure output at E, `search2.py`'s run at E with a saved classification of its hits after 2026-11-11 17:15 UTC. NOT READY on batch 2's standing → batch 1 alone, batch 2 retrospective by design, that text to its own rule F + proxy.
  - **The freeze binds from the entry:** 26 files for REG-21 (k3w closure + `.python-version`, `pyproject.toml`, `uv.lock`), 27 for REG-22 (c2 adds itself), printed by `docs/probe/20261113_freeze/closure.py`. Until both batch 2s are computed or declared not computed: new code in new files only; no run matching the batch-2 or reference pattern; no file named `reg19_final_*` other than final.sh's own.
  - **Disclosed reads of REG-19 folders** in draft 25 "What was known": (i)–(v) and (vi) A14 recheck, (vii) sizes during seed 16's copy, (viii) seed 17 burst folder listing + config lines, (ix) names-and-validity loops. Found by `search2.py` (723a16b; inputs only, heredoc bodies elided, status values masked). A dry run is in the bundles; the triage is `scratchpad/triage1.txt` (session 8c5f8396).
- **REG-23** (K5): draft 5 (`docs/drafts/reg23_k5_draft5.md`, commit `ea762b9`), code `63e8c65` (k5.py: Lr comparator and `leads_slo_only`, paired lead over A with the 120 s hurdle and ≥ 5 A onsets, `too_few_events` and `REASONS`, `alarm_share`, Poisson upper bounds per load, CP bounds, scan-start/recovery flags, peak A sent/planned; 15 tests). **Round 2 running:** `rulef-reg23-r2` (CC), `proxy-reg23-d5` (CD), bundle `reg23_r2`. Pending wording fix for draft 6 / the assembly: alternative 8 is already answered by S8 (FILE(docs/open-questions.md:33); source re-verified 2026-11-13, tarball sha256 matches), so it is a fact, not a BELIEF.
- **E1:** draft 4; launch scripts not written. **E0/E2:** draft 3, NOT READY, needs a redesign.
- **REG-20:** registered and approved by the owner; gate after REG-19's [RESULT] and before both batch 2s (arm A ≈ 0.2 by its own prediction; on a gate failure with ≥ 3 closed runs cold the tree says REG-20b, which reuses the same ops). **`reg20-ops-writer` running** (since ≈ 16:10 UTC): writes `common.sh`, `vm_state.py`, `session_probe.sh`, `launch.sh`, `queue.sh`, `final.sh`, `control_due.py`, `test_sandbox.sh`, README into `docs/probe/20261113_reg20/ops/`, new files only, nothing committed. The design points I fixed in its brief (pin `1cface7`; gate heading pattern; drift run after the third burst run and its control; `control_due.py` printing only `CONTROL_DUE yes|no|unclear`, unclear = no control; client error = stop; ulimit ≥ 4096 for the open arm; quiet hours with a two-run fit for open burst runs; arm B out of scope) are proposals: they need a [DECISION] (delegate) with rule F and an owner-proxy pass before any REG-20 run.

## Handoff (2026-11-13 ≈ 18:10 UTC, usage limit reached)

- REG-19: seed 18's control (attempt 3) ended and the queue went on to seed 18's burst run, attempt 1 (attempt record in state/, names only; GPU 100 % at 18:07). Its launch log of the control holds no `run_id`/`[run] checks` line to read. Watcher `bwnigx6gj` may have stopped with the session; restart it per the heartbeat.
- Running agents whose results arrive as messages to main (save verbatim with `scratchpad/save_review_n.py`): `rulef-reg21-r19`, `proxy-reg21-d26`, `rulef-reg22-r12`, `proxy-reg22-d17` (round 4); `e1-ops-writer`. If their messages were lost, extract them from their transcripts or ask them to resend.
- REG-20 ops committed (c8b482d) with decision draft 1; items 6 (client-error rerun rule), 9 (control invalid twice) and 16 (arm B seal) asked of the owner at ≈ 18:05 UTC, no answer; the scripts stop and wait in both cases. Next: send the draft to rule F + owner-proxy.

## Next three

1. **Round 3 ended in the stop for both** (decisions.md 2026-11-13 [DECISION] (delegate), round 3 ends in the stop, 743632e; reviews saved e3b2cc2): batch 1 first, batch 2 retrospective by design; BI-S/BK-S applied there. Drafts 26/17 committed (0d86f02), bundles `reg21_r19`/`reg22_r12` (53d5d99, classify2 0 unlabelled). **Round 4 running (≈ 17:35 UTC):** `rulef-reg21-r19` (items CE), `proxy-reg21-d26` (CF), `rulef-reg22-r12` (CG), `proxy-reg22-d17` (CH); each sends one message to main. Save verbatim with `scratchpad/save_review_n.py NAME IDX STEM NOTE`. Round 4 ends the review: rule F items applied, the proxy's APPROVE/REJECT decides. Then the [DECISION]s (delegate) (REG-21: BJ13 (a)–(f); REG-22: BL4 1–4 with BL3a's mapping), register REG-22 then REG-21, with search2 + classify2 (0 UNLABELLED) + closure at E.
2. Batch 1 of each, once, stamped outputs committed alone; [RESULT]s (k of n with bounds; "primary" = cited first, never "confirms"). Then `final.sh` once REG-19's queue has ended (end kit C).
3. **E1:** `e1-ops-writer` writes `docs/probe/20261113_e1/ops/`; review it, write E1 draft 5 (drop "not ready", name the harness pin 5ee6e38 vs a7bb77a), send with the scripts to rule F + owner-proxy (owner approved). **REG-23:** full texts of rulef-reg23-r2 and proxy-reg23-d5 requested (17:20 UTC); save, apply, register. **REG-20:** review `reg20-ops-writer`'s scripts; ops [DECISION] draft to review.

## Blockers

- **GPU:** in use by REG-19 since 16:55:12 UTC (seed 18's control ends near 18:05, its burst near 19:20; seed 19 to ≈ 21:40 if the step says continue). E1 is the next GPU work once its [REG] is committed and the queue has ended. If the VM goes down again: record the partial matrix, never pool, and the owner decides (three attempts are spent).
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
