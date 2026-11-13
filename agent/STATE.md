# STATE

Any fresh session resumes from this file alone. Read it, then `agent/PLAN.md`, then the last block of `agent/LOG.md`.
Rules: `docs/FABLE_PROMPT.md` (the start prompt), `CLAUDE.md`, `PROTOCOL.md`, `docs/process.md`.

Last updated: 2026-11-13 (session 8c5f8396, block 3).

## ⚠⚠ UPDATE 2026-11-13 05:15 UTC: the VM went off again (≈ 04:40 UTC), ~61 min into seed 18's control attempt 2

- Logged: decisions.md 2026-11-13 [OPS] "the VM went off again…"; probe `docs/probe/20261113_reg19/vm_down_*.txt`. Cause unknown (journal unread). Outside the quiet hours.
- **Attempt 2 is spent; one remains. No `lost_ok` record exists for this run, so no rerun is allowed** (draft 5 item 1). The queue was left to stop by itself (exit 7 at ≈ 05:39 UTC, or TMUX GONE if the VM returns). Save its output file and stop line, then commit the state files (`attempt_…_2.txt`, `session_boot_id.txt`, the prelaunch probe, the queue output).
- **When the VM is back:** read-only first: is there a `checks.json` in the new seed-18 folder (allowed read), the journal for the boot's end (as `poweroff_*.txt` on 2026-11-12), the limit (likely 420 W). **Then stop for the owner:** attempt 3 needs the owner's decision, 350 W, and a `RENEW=1` session probe. Do not launch.
- The block below is the earlier handoff; its "queue is RUNNING" no longer holds.

## ⚠ READ FIRST: what happened while you were stopped (2026-11-13 ≈ 03:30–03:40 UTC, an owner-attended Opus session, not you)

- **The owner set the VM to 350 W by hand** (read 350.00 W at 03:34:45 UTC) and **approved the REG-19 resume directly**: decisions.md 2026-11-13 `[DECISION] (owner) REG-19 resumes for seeds 18 and 19` (commit `7bbb134`). It adopts your draft 5 as written. It is an owner decision, so rule F/owner-proxy no longer gate it. **Do not re-run the round-4 reviews of the REG-19 resume.** (All four round-4 subagents had died on the usage limit with no verdict.)
- **One script change:** `DECISION_PAT` in `ops_r3/common.sh` now also accepts `(owner)` (commit `a4d46ce`; `scripts_commit.txt` updated in `7bbb134`). Sandbox: 159/160; the failure is `final.sh`'s "all five seeds run" case comparing `T//` with `T/` (a TMPDIR double slash). Please confirm it is only that before running `final.sh`.
- **Session probe passed** at 03:38:25 UTC (`docs/probe/20261113_reg19/session_*.txt`; boot id `7d11a297…`; `state/session_boot_id.txt` written).
- **The queue is RUNNING**, started 03:38:39 UTC, detached (`nohup caffeinate -i zsh docs/probe/20261113_reg19/ops_r3/queue.sh`). Output: `docs/probe/20261113_reg19/queue_owner_20261113T033838Z.txt`. Seed 18's control attempt 2 launched on the VM at 03:38:42 UTC. The queue continues by itself: seed 18 burst, step, and seed 19 only if `'continue': True`. Quiet hours (no control after 11:45, no burst after 13:00 UTC) may stop it; then start it again after 18:00 UTC with the same command.
- **Your next steps:** do not start a second queue (it holds a lock; check `pgrep -f ops_r3/queue.sh`). Watch the output file. When it prints `QUEUE DONE` or `QUEUE END futility stop`: run `final.sh` once, write the [OPS] record of item 7 (include this session's facts above) and the [RESULT]. On any `QUEUE STOP`: follow draft 5's rules (allowed reads only). Still in review and yours: REG-21 round 4 (relaunch from `review_bundles/reg21_r4/`).
- Stale lines below (Phase, "VM still off", "four reviews running", 420 W) predate this block.

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

- **VM up since 2026-11-12 ≈ 19:48 UTC**, read 19:52 UTC: RTX 3090 idle, 39 °C, no compute process, no tmux session, tree `a7bb77a` clean, 5.4 GB free, **power limit 420 W**.
- **Blocker: `sudo -n nvidia-smi -pl 350` fails ("a password is required"; no rule in `/etc/sudoers.d/`).** No 350 W run starts until the owner sets 350 W. A background loop in the session reads the limit every 2 minutes and exits when it is 350.00 W or when the VM's state changes.
- REG-19: seeds 15, 16, 17 done and withheld; seed 18's lost control folder is on the VM (no `checks.json`, as expected); seed 18 burst and seed 19 not run. The resume decision is in review.
- `ulimit -n` on the VM is 1024 (REG-20's open arm needs ≥ 4096).

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

## Update 2026-11-13, after review round 2 (session stopped on the usage limit)
- **Nothing registered or approved yet; no run made; no REG-19 outcome read.** VM up, idle, still at 420 W (the owner must set 350 W; `sudo -n` needs a password).
- Round-2 reviews, verbatim in `docs/drafts/reviews-2026-11-13/`: rule F on the REG-19 resume NOT READY (12 changes, `rulef-reg19-resume-r2.md`); rule F on REG-21 draft 4 NOT READY (7 changes, `rulef-reg21-draft4-r2.md`); owner-proxy on REG-21 draft 4 approve on 10 conditions, lapsed by the rule F verdict (`proxy-reg21-draft4.md`).
- **In hand, REG-19 resume, third version:** `docs/probe/20261113_reg19/ops_r3/` (common.sh, vm_state.py, session_probe.sh, launch.sh, queue.sh, final.sh, state/ with the lost run's attempt record). Syntax-checked only. **Not tested, not reviewed, no scripts_commit.txt.** Design: no typed seed, attempt or run id; attempts counted from records written just before the launch command; `valid` read from checks.json; a valid run on the VM is used, not relaunched; step record per seed gates seed 19 and final.sh.
- **Next, in order:** (1) write `ops_r3/test_sandbox.sh` (fake VM tree, real git checks; reuse the reviewer's cases 14–19) and run it; (2) commit, write scripts_commit.txt; (3) decision draft 3 answering the 12 items (registered rerun exceptions stand; allowed reads named; the eight statements corrected; probes saved for untagged facts); (4) rule F round 3 and owner-proxy, unnamed agents; (5) REG-21 draft 5 (leave the λ = 2.2 pair out of the pooled median, minimum scrapes and a "no waiting gauge" reason, the fixed-load contrast, the proxy's ten conditions), then rule F round 3 and a new proxy pass; (6) E1-only draft 4 (code committed in 3349552).

## Update 2026-11-13 00:50 UTC: round 3 of both reviews is running
- **Nothing registered or approved; no run made; no REG-19 outcome read.** VM idle at 420 W (owner must set 350 W).
- **REG-19 resume:** scripts `docs/probe/20261113_reg19/ops_r3/` at `69f349b` (sandbox 116 of 116; real `mac_checks`, `links_ok`, `vm_state` and `decide` run read-only: seed 18's control would be attempt 2). Draft 3 `docs/drafts/reg19_resume_decision_draft3.md`; bundle `docs/drafts/review_bundles/reg19resume_r3/`. Probes saved (VM read, lost-folder checksums, stored validity, link-path test). The interim look of 2026-11-12 is logged ([OPS]). **Waiting for:** rule F round 3 and owner-proxy round 3 (unnamed background agents).
- **REG-21:** code at `69ffedd` (31 tests), draft 5 `docs/drafts/reg21_draft5.md`, bundle `docs/drafts/review_bundles/reg21_r3/`. **Waiting for:** rule F round 3 and a new owner-proxy pass.
- **When a review returns:** save it verbatim in `docs/drafts/reviews-2026-11-13/`. READY plus APPROVE: write the entry with both reviews verbatim, meet the proxy's "before" conditions, context pack, check_docs, commit. NOT READY: fix only the required items, re-review. REG-21's [REG] and [DECISION] must be committed before REG-19's table is computed.
- **After REG-19's decision is in and the owner has set 350 W:** `zsh docs/probe/20261113_reg19/ops_r3/session_probe.sh`, then `zsh docs/probe/20261113_reg19/ops_r3/queue.sh` in the background, then `final.sh` once.
- **Next zero-GPU work:** E1-only registration draft 4 (code committed in `3349552`); REG-22 review; stale docs.

## Update 2026-11-13 01:03 UTC
- **REG-19 resume:** owner-proxy round 3 APPROVE on D1 to D8 (`docs/drafts/reviews-2026-11-13/proxy-reg19-resume-r3.md`). Draft 4 (`docs/drafts/reg19_resume_decision_draft4.md`) has D2 (second heat failure counted over all REG-19 runs, applied by hand at each restart), D3 (power-off cause: a power-key event at 15:51:32 UTC, probe saved), D5 (corrections), D6 (first session probe with `SET=1`). **Still needed:** rule F round 3 not NOT READY (D1). Then: append the entry with rule F round 3 and proxy round 3 verbatim, every quoted line prefixed `> ` (no line may start a `## ` heading), commit, and only then the first launch (D4). A script change or a rule change after rule F needs a new proxy pass first; wording does not.
- **REG-21:** rule F round 3 and the owner-proxy still running on draft 5.
- **Drafted, not sent to review:** REG-22 draft 2 (`analysis/c2.py`, 14 tests); REG-23 draft 1 for K5 (`analysis/k5.py`, 9 tests); E1 draft 4 (launch scripts not written; six single-rate configs committed). Send REG-22 after REG-21's round 3, REG-23 after REG-22.
- **Full test suite:** 491 passed at `69ffedd`; run it again before any registration's commit (c2, e1, k5 changed since).

## Update 2026-11-13 01:25 UTC (session stopped on the usage limit; round 4 launched, results unknown)
- **Nothing registered or approved; no run made; no REG-19 outcome read.** VM idle at 420 W.
- **Round 3 results (all verbatim in `docs/drafts/reviews-2026-11-13/`):** REG-19 resume: owner-proxy approve on D1 to D8, rule F NOT READY (T1, T2, statements a to i, item 8). REG-21 draft 5: owner-proxy approve on 12 conditions, rule F NOT READY (six changes in the text).
- **Done since:** REG-19 scripts revised (`docs/probe/20261113_reg19/ops_r3/`, commit `106f3ed`, sandbox 160 of 160, real read-only check passed) and decision draft 5 (`docs/drafts/reg19_resume_decision_draft5.md`, bundle `review_bundles/reg19resume_r4/`). REG-21 draft 6 (`docs/drafts/reg21_draft6.md`, code `8164211`, 35 tests, bundle `review_bundles/reg21_r4/`).
- **Round 4 was launched for both (rule F on the diff, owner-proxy on the delta), as four unnamed background agents, and was stopped with the session.** On resume: look for a hand-back in `~/.claude/projects/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/subagents/agent-{ab7bb0a5b38b0ae99,a5f4a6d2ba3957cd7,af3cd85f0f63adbb0,a4ca1db0b695fabcf}.jsonl` (REG-19 rule F, REG-19 proxy, REG-21 rule F, REG-21 proxy); relaunch from the bundles any that has none (the prompts are in this session's transcript).
- **When both of a pair clear:** write the entry (body from the draft; every review quoted verbatim with each line prefixed `> `; decisions.md already uses `### ` sub-headings and `> ` quotes), meet the proxy's "before" conditions, run the full test suite and check_docs, commit. REG-19: then D6 (first session probe with `SET=1`) and the queue, outside 11:45 to 18:00 UTC. REG-21: definitions (`docs/drafts/definitions_reg21_reg22.md`), a ledger row in `docs/model.md` (next number 24), then batch 1 once.
- **Drafted, not sent to review:** REG-22 draft 2, REG-23 (K5) draft 1, E1 draft 4.

## Update 2026-11-13 05:30 UTC (the agent, resumed after the usage limit)
- Read the two handoff blocks at the top. Followed: no second queue; no rerun; the REG-19 round-4 reviews are not relaunched (the resume is the owner's decision now).
- **REG-21 round 4:** both agents resumed by message (`af3cd85f0f63adbb0` rule F, `a4ca1db0b695fabcf` owner-proxy). Waiting.
- **Watcher:** a new background loop exits when the VM answers again. Then, read-only: `vm_state` and `decide` for the four configs (expect two folders of seed 18's control without `checks.json`, one of them without a `lost_ok` record, so `decide` stops), the journal of the boot that ended ≈ 04:40 UTC, the limit. Then stop for the owner.
- **When the queue process ends** (it is still in `launch.sh`'s wait): save its stop line, then commit `ops_r3/state/attempt_…_2.txt`, `session_boot_id.txt`, the lock folder's renamed copy, the prelaunch probe and the queue output.
- **Open question A18** (what sends the power-key events; five of seven fell during a run) added; FOR_AUTHOR items -7 and -6.
- **Sandbox note from the owner's session** (159 of 160 with a TMPDIR that ends in a slash): test-only; fix `test_sandbox.sh` by normalising the sandbox path, after the queue has stopped.

## Update 2026-11-13 06:00 UTC
- **REG-19:** the queue stopped by itself at 05:49:28 UTC (VM NOT REACHABLE); its records are committed and logged ([OPS], then a [CORR] for a commit made while check_docs failed: run check_docs as its own command, never through a pipe). VM still down. Attempt 3 of seed 18's control is the owner's (draft `docs/drafts/reg19_attempt3_decision_draft1.md`). When the VM answers: run `zsh <scratchpad>/vm_back_probe.zsh` (read-only; writes `docs/probe/20261113_reg19/vm_back_*.txt`), fill the two open lines of the draft and A18's table, then stop for the owner.
- **REG-21:** owner-proxy round 4 APPROVE on 12 conditions (`proxy-reg21-draft6-r4.md`); rule F round 4 NOT READY, three text items (`rulef-reg21-draft6-r4.md`); draft 8 (`docs/drafts/reg21_draft8.md`) has both; **rule F round 5 on the text diff is running** (`aea70a41daaffaecd`). If READY: compose the [REG] (draft 8's body; every review verbatim, prefixed `> `, each followed by what changed) and the [DECISION] (delegate) (proxy r4 condition 7: list the sentence meeting each of conditions 2 to 6; a bullet on the departure with its deadline); re-resolve every FILE(path:line); definitions and ledger row; full tests; commit. **Do not compute batch 1 before REG-22 is registered.**
- **REG-22:** rule F round 1 NOT READY, ten items (`rulef-reg22-draft3-r1.md`); code revised (`727d1f2`, 22 tests), draft 4; **rule F round 2 (`a0fd29b2b40338bb5`) and the first owner-proxy pass (`a43b6d3c375ffd53e`) are running.** Open point for the proxy: the registration re-reads a PROTOCOL clause (order → `sustain`).
- **Waiting, not sent:** REG-23 (K5) draft 1; E1 draft 4 (needs launch scripts).
- **Full test suite:** 508 passed at `9b3cddf`; c2.py changed since (22 tests pass); run the suite again before a registration's commit.

## Update 2026-11-13 06:11 UTC (session stopped on the usage limit)
- **Nothing registered; no run made or read since the queue's stop.** VM still down; REG-19 waits for the owner (VM on, 350 W, attempt 3).
- **Four reviews were running and will have been cut by the limit; resume each with SendMessage to its id (its work so far is saved), do not start new ones:**
  - `a1bce48befd9127b9` rule F round 6 on REG-21 draft 9 (bundle `docs/drafts/review_bundles/reg21_r6/`);
  - `a4122f052f465a926` owner-proxy delta pass on REG-21 draft 9 (the stopping-rule changes);
  - `a0fd29b2b40338bb5` rule F round 2 on REG-22 draft 4 (bundle `reg22_r2/`);
  - `a43b6d3c375ffd53e` owner-proxy first pass on REG-22 draft 4.
- **REG-21 so far:** rule F round 5 NOT READY, six text items (`rulef-reg21-draft8-r5.md`), all in draft 9 (`docs/drafts/reg21_draft9.md`); code unchanged at `8164211`. Owner-proxy round 4 approved draft 6 on 12 conditions. When rule F says READY and the proxy's delta pass approves: compose the [REG] and [DECISION] (delegate) as the 06:00 block says; do not compute batch 1 before REG-22 is registered.
- **REG-23 (K5):** draft 2 with a 30 s floor on a lead (`docs/drafts/reg23_k5_draft2.md`, `analysis/k5.py`, 10 tests); not sent to review.
- **Full test suite:** the run at `642e850` ended with exit 0 (its count is in the scratchpad file `full_tests_642e850.txt`); `analysis/k5.py` changed after it (10 tests pass).
- **Always run `tools/check_docs.py` as its own command before a commit** ([CORR] of today).

## Update 2026-11-13 10:50 UTC (resumed after the usage limit)
- **Nothing registered; no run made or read.** VM still down (watcher loop `b2n4cwfii` reads `down` every 3 min). REG-19 waits for the owner (VM on, 350 W, attempt 3: `docs/drafts/reg19_attempt3_decision_draft1.md`).
- **Reviews returned and saved verbatim** (`docs/drafts/reviews-2026-11-13/`): REG-22 owner-proxy r1 APPROVE on 16 conditions, PROTOCOL re-reading NOT delegated (`proxy-reg22-draft4-r1.md`); REG-22 rule F r2 NOT READY, N1–N8 text (`rulef-reg22-draft4-r2.md`); REG-21 rule F r6 NOT READY, three text items (`rulef-reg21-draft9-r6.md`); REG-21 owner-proxy delta APPROVE on C1–C6 (`proxy-reg21-draft9-delta.md`).
- **Done:** REG-22 draft 5 (`docs/drafts/reg22_draft5.md`; code `ffc76b3`: reported-only readouts `planned_rates`, `onset_reading`, `reported_counts`, histogram restart at any scrape, control vs burst baseline; 29 tests; judged path as `727d1f2`). REG-21 draft 10 (`docs/drafts/reg21_draft10.md`, text only, code `8164211`). Definitions/ledger draft updated (`docs/drafts/definitions_reg21_reg22.md`). Full suite 522 passed (before the second c2 edit; c2's 29 pass after).
- **Running (resume by SendMessage to the id if cut, do not start new ones):** rule F r7 on REG-21 draft 10 (`a0adfd0cddd98f5fb`, bundle `reg21_r7`); rule F r3 on REG-22 draft 5 (`a7e69db175dbd3a1d`, bundle `reg22_r3`); owner-proxy delta on REG-21 draft 10 (`a4122f052f465a926`); owner-proxy delta on REG-22 draft 5 (`a43b6d3c375ffd53e`).
- **When both of a pair clear:** compose the [REG] (draft body; every rule F review verbatim, prefixed `> `, each followed by what changed) and the [DECISION] (delegate) (proxy verdicts verbatim; the sentence meeting each condition; REG-22: the bullet "For the owner: condition 4's order clause"; REG-21: the append-time check C4). Same commit: definitions blocks, ledger rows 24/25, status line, FOR_AUTHOR top item on the order clause, open question A19. **Neither batch 1 before both entries are committed.** Then batch 1 of each once, output saved verbatim with sha256.
- **Next zero-GPU work if idle:** REG-23 (K5) must list REG-22's control readout as known or be registered first; E1 launch scripts.
