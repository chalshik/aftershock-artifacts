# PLAN: task board

Status: todo / doing / done / blocked / dropped. GPU h are the registrations' own figures where one exists, else planning estimates (BELIEF).
Value rule: information for the paper per hour. Re-plan GPU order only through `agent/DECISION_TREE.md`.

## Phase 0: setup

| ID | Goal | Inputs | Output | Done-test | Status | Depends | GPU h |
|---|---|---|---|---|---|---|---|
| S1 | Save out-of-repo drafts | scratchpad `fdf13821…` | `docs/drafts/scratchpad-2026-11-12/` | `cmp` clean, committed | done (`c94a77d`) | — | 0 |
| S2 | History for `docs/paper/` | — | inner git repo | `git -C docs/paper log` shows a commit | done | — | 0 |
| S3 | Back up `runs/` | `runs/` 19 GB | `/Users/chalshik/aftershock-backups/runs-2026-11-13` | `tools/manifest.py verify` prints OK | done (1831 listed, 0 missing, 0 different) | — | 0 |
| S4 | State files | — | `agent/*.md` | committed | doing | — | 0 |
| S5 | Ingest | pack, rules, decisions.md, paper layer | `agent/INGEST.md` | claims ledger, conflicts, missing, plan | doing | — | 0 |
| S6 | Self-resume | harness features, launchd | documented in STATE.md | a test shows a re-invocation | done in part: launchd → `claude -p` tested OK; recurring install refused by the permission classifier; in-session heartbeat cron `933698ad` runs | S4 | 0 |
| S7 | GPU watcher | ssh key, VM addresses | `agent/bin/gpu_watch.sh` + schedule | writes `agent/GPU_AVAILABLE` on a faked success; logs changes only | done: 7 faked states tested; real read = `down`; runs as an in-session loop every 15 min | S4 | 0 |
| S8 | Withheld-run exclusion in glob tools | `analysis/tables.py`, `recheck.py`, `gate.py` | code + tests | tests pass; tools skip `*_w3000_s1[5-9]*` until REG-19's [RESULT] | done (`72fafb5`) | — | 0 |

## Phase 1: literature

| ID | Goal | Inputs | Output | Done-test | Status | Depends | GPU h |
|---|---|---|---|---|---|---|---|
| L1 | Read the PDFs myself; check against reading-notes and quote-check | `docs/paper/pdfs/` | `agent/LITERATURE.md` | every statement the paper will cite has an anchor (section, page, quote) | todo | — | 0 |
| L2 | KAIROS Fig. 10–11 check (did the controller restore full frequency during thrashing without thrashing avoidance?) | 2604.16682v2 | entry in LITERATURE.md; Related Work fixed if yes | answered with a quote and figure anchor | done: not shown in the paper (LITERATURE.md) | L1 | 0 |
| L3 | Merge Drive-copy corrections the repo lacks | `DRIVE_COPIES` | `docs/paper/` commits, log | — | blocked (path missing) | owner | 0 |
| L4 | Novelty checks | papers | `agent/NOVELTY_CHECKS.md` | no "first"/"new" in the draft without an entry | todo | L1 | 0 |

## Phase 2: zero-GPU work (start prompt §6)

| ID | Goal | Inputs | Output | Done-test | Status | Depends | GPU h |
|---|---|---|---|---|---|---|---|
| Z1 | REG-21 (K3 step B) v3: fix round 2 (J4 cannot change a decision; batching residence confounds J1/J2), rule F, owner-proxy, register, approve, compute batch 1 | `docs/drafts/…/reg21_draft2.md`, `round1.md`, `review2/`, `analysis/k3.py`, `modelf.py`, `modelf_sim.py` | [REG] + [DECISION](delegate) + [RESULT] batch 1 | registered before any `k3` judging call; batch 1 computed once | doing: draft 3 + code + tests written; rule F to re-run | S8 | 0 |
| Z2a | A17 from the pinned vLLM source | vLLM 0.32.0 tarball (sha256 in open-questions) | open-questions A17 answered with SOURCE | SOURCE tag with path:symbol | done | — | 0 |
| Z2b | [CORR] logging the owner's E0/E1/REG-21 choices missing from decisions.md (pack §12.2 #3) | status.md:15, configs, drafts | [CORR] | committed | done | — | 0 |
| Z2c | E0 and E1 registered and approved | `e0_e1_draft2.md`, reviews, `analysis/k2.py`, `e1.py` | [REG] ×2, [DECISION](delegate) | rule F + proxy done; configs unchanged or new files | doing: draft 3 written, not reviewed | Z2a, Z2b | 0 (E1 2.1, E2 4.2 on GPU) |
| Z3 | C2 condition 4 with an executable trace-order test on the stuck runs on record (not REG-19) | REG-11/12/14/15/17/18 burst runs | [REG], code + tests, [RESULT] | registered before computing | todo | S8 | 0 |
| Z4 | K5 lead times + critical-slowing-down test | stuck runs, no-trigger tips (REG-12 s4/s5 controls, REG-13 r2.6–3, REG-16) | [REG], code, [RESULT] | onset rules fixed in text first | todo | S8 | 0 |
| Z5a | A5 client vs server TTFT | valid non-REG-19 runs | [REG], [RESULT] | — | todo | S8 | 0 |
| Z5b | R and reuse-gap histograms vs the 5 s turn gap | raw `metrics.jsonl` buckets | [REG], code, [RESULT] | — | todo | S8 | 0 |
| Z5c | Preemptions vs matched controls | pairs REG-14 s2, REG-17 s2, REG-18 s3–s6 | [REG], [RESULT] | — | todo | S8 | 0 |
| Z5d | Session-cap values from the REG-17/18 controls | 5 controls | values for D1's registration | not from REG-19 controls | todo | — | 0 |
| Z5e | K4's two readings (request surge vs session-start surge) | schedules; closed-loop L1 runs excl. `*_w3000_*` | [REG] (exploratory), [RESULT] | — | todo | S8 | 0 |
| Z5f | A11: c_b of the older open-loop bursts | default, 72k, 5 s-gap bursts | [REG], [RESULT] | — | todo | — | 0 |
| Z6a | Stale docs (pack §12.2 #1, #4–#7, #10–#15; claims.md K4 "0.41–0.51") | listed files | [CORR] entries | check_docs passes | todo | — | 0 |
| Z6b | REG-19 resume: pin decision (#4) as delegate [DECISION]. Default: finish at `a7bb77a`, exempt that pin explicitly; deploy HEAD only after REG-19 | RESUME.md, launch6.sh | [DECISION](delegate), launch script as a new file | rule F + proxy | doing: draft + scripts + worktree; both reviews to re-run | — | 0 |
| Z7 | Theory: K1 idle/evictable prefix; K2 scaling with turns; partial-reuse trap or bounds | modelf, papers | `agent/theory/*.md` + code checks | each derivation tested with a counterexample case | todo | L1 | 0 |
| Z8 | Design simulator, calibrated on REG-8 sweeps; never evidence | REG-8 cache-on/off sweeps | `analysis/` or `agent/sim/`, calibration error reported | every planned test shown able to fail | todo | — | 0 |
| Z9 | GPU-queue registrations: confirmation at λ = 2.0; D1 session cap; D2 caching off; E3 (if E0 passes); K4 | — | [REG] + [DECISION](delegate) each, configs as new files | reviewed and approved before the GPU returns | todo | Z2c, Z5d, Z7 | see ledger |
| Z10 | Preprint full draft with [PENDING] blocks | all | `docs/paper/preprint/` | every claim scoped; each section adversarially reviewed | todo | L1, Z1–Z9 | 0 |
| Z11 | `agent/DECISION_TREE.md`, `agent/RUNBOOK.md` | registrations | files | written before any GPU run | todo | Z9 | 0 |

## Phase 3: GPU queue (start prompt §7; order fixed there)

| ID | Goal | Registered? | GPU h | Status |
|---|---|---|---|---|
| G1 | REG-19: seed 18 control (attempt 2), seed 18 burst, seed 19 pair; then `ops_r3/final.sh` once (never `analysis.gate reg19` by hand), its two `state/reg19_final_*` files committed at once and alone (the record of REG-21/REG-22), [OPS], [RESULT] | yes, owner-approved 2026-11-11; resume needs Z6b | 4.7–4.9 | blocked (VM off, Z6b) |
| G2 | REG-20 gate once; arm A if it passes; arm B only after `supports` | yes, owner-approved 2026-11-12 | 6.4–7.4 (A), 3.2–3.7 (B), conditional | blocked (G1) |
| G3 | REG-21 batch 2 | no (Z1) | 0 | blocked (G1, Z1) |
| G4 | E1, then E2; E3 only if E0's gate passes | no (Z2c) | 2.1, 4.2; E3 8–12 | blocked (Z2c) |
| G5 | Loop-cut controls D1, D2 | no (Z9) | 4–6 | blocked (Z9) |
| G6 | Confirmation run, conditions 5–6 | no (Z9) | ≈ 4.5 (REG-16's scale) | blocked (Z9) |
| G7 | K4, if hours remain | no (Z9) | long runs, few | blocked (Z9) |
