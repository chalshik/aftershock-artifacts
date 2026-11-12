# LOG (append-only)

One block per work block: what was done, what was found, the commit.

## 2026-11-13, block 1 (session 8c5f8396): start, first actions

**Done**
- Read `docs/FABLE_PROMPT.md`. `git log -5`, `git status`: HEAD `9958414`, dirty `.gitignore` (the owner's, left alone) and `docs/decisions.md` (the delegation entry, uncommitted).
- No other Claude process has this repo as its working folder (four other `claude` processes: `tam-sat` ×2, `cocobolo` ×2; OBSERVED via `lsof -d cwd`).
- Delegation entry: found uncommitted and without `## `; marker and line breaks added, words unchanged; committed with an [OPS] entry.
- S1: 31 draft files copied byte for byte into `docs/drafts/scratchpad-2026-11-12/`. Papers (5 PDFs + text), Schroeder 2006 and others from a second scratchpad, and the snapshot's 61 section files copied into `docs/paper/` (local).
- S2: `git init` in `docs/paper/`, `.gitignore` for `pdfs/`, `paper-text/`, `*.pdf`; first commit `3e41741`.
- S3 started: `rsync` of `runs/` to `/Users/chalshik/aftershock-backups/runs-2026-11-13`, then `tools/manifest.py verify` (background).
- Read in full: `PROTOCOL.md`, `docs/process.md`, `docs/claims.md`, `docs/status.md`, `docs/definitions.md`, `docs/model.md`, `docs/experiment-plan.md` (the "Stage 2, revised" section, lines 350–481), `docs/open-questions.md` (source questions and A1–A17), `docs/probe/20261111_reg19/ops/RESUME.md`; the pack's §0, §6.0, §6.20, §10.3–10.5, §12.1–12.5, §13, §14.

**Found**
- The pack is at `docs/paper/context-pack-2026-11-12.md`, not at the path the start prompt names.
- `PAPERS_DIR` and `DRIVE_COPIES` were left as placeholders. Papers found in scratchpads; Drive copies not found (searched the mounted Drive folder to depth 8 and the home folder to depth 6 for `context-alignment*`, `paper-plan*`, `related-work*`).
- No external volume is mounted (`/Volumes`: Macintosh HD, Recovery). 120 GiB free.
- The VM is offline on Tailscale.
- `docs/claims.md` K4 still says "0.41–0.51 of the warm peak" (line 77); the 2026-11-12 [CORR] fixed 0.43–0.52 against 3.15 only in the local paper files. Added to Z6a.
- `check_docs` failed at session start only on the stale context pack (the uncommitted delegation text); passes after regeneration.

**Commit:** `c94a77d` (main repo); `3e41741` (docs/paper inner repo).

## 2026-11-13, block 2 (session 8c5f8396): seal, A17, three drafts; stopped on the usage limit

**Done**
- S6/S7: `agent/bin/gpu_watch.sh` (7 faked states tested; real read `down`) and `agent/bin/resume.sh` (launchd → `claude -p` tested with a one-off job, `RESUME_TEST_OK`; dry-run decisions right). The install of the recurring launchd jobs was refused by Claude Code's permission classifier; not worked around. In-session GPU watcher loop started (background shell, 15 min).
- S8: `analysis/withheld.py` and its hooks; `tests/test_withheld.py` (12).
- A17 from `vllm-0.32.0/vllm/v1/core/sched/scheduler.py` (tarball at `~/.claude/jobs/c075c1a8/tmp/vllm_src/`, sha256 verified): no skip; decisions.md 2026-11-13 [DECISION].
- [CORR] for the owner's four unlogged choices (E1 "Floor only", E0 "Add 2.2", REG-21 "Register now, mix primary" and "Rebuild around per-run sim").
- Z6b draft: VM stays at `a7bb77a`; REG-19's Mac-side analysis from a worktree at `a7bb77a`; agent sets 350 W; the lost seed-18 folder copied only after the [RESULT].
- Z1 draft 3: judged J1 (|median r − 1| ≤ 0.05) and J2 (spread of load-group medians ≤ 0.05) on r = U_W / U_off, the uncached-token work rate; everything about the mix is reported only.
- Z2c draft 3 written.
- L2 answered; `agent/lit/verify_quotes.py`: 26 of 26 cited quotes found in the PDFs.
- Full suite: 443 passed (before `tests/test_k3w.py`, whose 18 pass).

**Found**
- `k3.reg21_table`'s batch-1 finder globbed `*_l1pl350cl_*`, which would have loaded REG-19's withheld runs; the seal now prevents that.
- KAIROS Fig. 11 has no frequency trace for the run without thrashing avoidance, and its text assigns panel (c) to that run while the panel's title says "With".

**Not finished (stopped by the usage limit)**
- The three reviews (briefs: rule F for the resume decision asked for traces where the procedure starts a wrong run, breaks REG-19's stopping rule or computes from other code, the strongest alternative for a seeds 15–17 vs 18–19 difference, and whether it changes REG-19; the owner-proxy asked scope, fidelity, the pin rule, the undeployed check changes; rule F for REG-21 asked for synthetic traces with a wrong J1/J2 label, code against text, alternatives, and whether any outcome changes a decision). Inputs in `docs/drafts/review_bundles/`.
- Not read by this session: decisions.md lines 1–3910 in full (the pack's indexes were used), the three preprints end to end, `docs/paper/paper-plan-v3.md`, `related-work-approach-v3.md`, `reading-notes.md`.

**Commit:** `72fafb5`, then this block's commit.

## 2026-11-13, block 3 (session 8c5f8396): resumed; VM check; reviews restarted; decision tree, runbook, literature

**Done**
- Owner asked whether the VM is back: no (Tailscale "offline, last seen 3h ago"; SSH timeout on both addresses; LAN ping 100 % loss; watcher `down` at 2026-11-12 19:22 UTC).
- Restarted the three reviews stopped in block 2, and started rule F round 2 on E0/E1/E2 draft 3. Heartbeat cron re-created (`3ca81824`).
- `analysis/withheld.py`: seals for E1 (`*_sweep_l1pl350cl_pc_off_r*`) and E2 (`*_sweep_l1t16pl350cl_pc_o*_r*`); `python -m analysis.e1 floor | status <parent>`, `python -m analysis.k2 observed`; tests.
- `agent/DECISION_TREE.md`, `agent/RUNBOOK.md`.
- `docs/status.md`: session paragraph; REG-20 approval line; the lost seed-18 folder.
- Local paper files (inner repo): K1 status and cost, K4's 0.43–0.52 against 3.15, KAIROS wording, "four things untested", P0 "close to the cold capacity", the 350 W sentence, 2.4 as a 900 s rule on one seed.
- Literature read by this session and recorded with anchors: Huang and Liu (whole text), Lu et al. (§1–§6.2, §7.1–7.2, §9), Valse and Jannesari (§1–§4).

**Found**
- Valse and Jannesari's registered trap rule has REG-21's statistic as its first half: "uncached prefill token rate within ±15% of the all-miss rate" (Table 1), and their measured token-rate ratios over 57 stuck runs were 0.95–1.12 (§4). Huang and Liu report the degraded regime's turn throughput equal to the cache-disabled engine's (§3). Lu et al. report uncached prefill "near the saturated" prefill throughput in their trapped run (§3). So REG-21's J1 tests, on this setup, a statement all three make.
- Lu et al. call the workload "partly-open" themselves (§2). Their hardware comparison's surge lasts 20 minutes (minutes 15–35), the §3 surges ten.
- Huang and Liu's abstract says the admission-only cap recovered "1 of 7 matched" runs, the text also "2 of 8" (unmatched): cite with the denominator named.
- Condition 4's "the traces follow the plan's order" was written for a wipe; a burst fills KV before the hit rate falls. The registration must define the order for a burst (STATE, next three).

**Commits:** `ef4dc4e`, `ea03d73`, the runbook commit, then this block's.

**Block 3, later (2026-11-12 19:52 UTC): the VM came back.** Watcher `down -> up_idle` at 19:51:46 UTC. Read-only state: idle GPU, 420 W, tree `a7bb77a` clean, the lost seed-18 folder present without `checks.json`. `sudo -n nvidia-smi -pl 350` and the same with `/usr/bin/nvidia-smi` both fail with "a password is required"; `/etc/sudoers.d/` holds only README. Per the start prompt §7: logged in FOR_AUTHOR, no 350 W run started. A 2-minute loop now waits for 350.00 W.
