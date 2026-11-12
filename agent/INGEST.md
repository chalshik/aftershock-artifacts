# INGEST (2026-11-13, first pass)

Tags: **OBSERVED** `RUN(id, function)` · **SUPPORTED** (source and anchor) · **DERIVED** (math or code in the repo) · **BELIEF** · **CONJECTURED**.
Numbers below are quoted from the repo's own documents with their place; none was recomputed in this pass. "decisions" = `docs/decisions.md`.

## 0. What was read, and how

| Source | How |
|---|---|
| `docs/FABLE_PROMPT.md`, `CLAUDE.md`, `PROTOCOL.md`, `docs/process.md`, `docs/claims.md`, `docs/status.md`, `docs/definitions.md`, `docs/model.md` | in full, by this session |
| `docs/experiment-plan.md` | lines 350–481 ("Stage 2, revised") in full; the older part through the pack |
| `docs/open-questions.md` | source questions S8–S11 and A1–A17 in full |
| `docs/decisions.md` | lines 3911–4233 (all 2026-11-12 and 2026-11-13 entries) in full, except REG-20's review text (4099–4145); the rest through the pack's indexes (§2, §6) and targeted reads. **Not read in full: lines 1–3910.** |
| The pack `docs/paper/context-pack-2026-11-12.md` | §0, §6.0, §6.20, §10.3–10.5, §12, §12.C, §13, §14 in full; the rest as a map |
| `docs/probe/20261111_reg19/ops/RESUME.md`, `launch6.sh`, `queue_reg19d.sh` | in full |
| vLLM 0.32.0 `v1/core/sched/scheduler.py` (tarball, sha256 verified) | the waiting loop, lines 884–963, 1236–1300, and the skip sites |
| Paper layer (`docs/paper/*.md`), the saved drafts, the PDFs | **not yet read** (tasks L1, Z1, Z2) |

## 1. Claims ledger

| Claim | Statement (short) | Evidence on record | Status | Registration that addresses it |
|---|---|---|---|---|
| **P0 = C1 + C2** (premise, cited from Lu et al. 2611.02543, Valse and Jannesari 2611.08902, Huang and Liu 2611.13412; replicated here; no novelty claimed) | After a burst, at a load its no-burst twin sustains, the server stays cold and backlogged (C1), through an eviction loop (C2) | REG-17 `pass_clear`, 1 seed, λ = 2.0 (decisions 2026-11-10 [RESULT]); REG-18 `some`, 1 of 4, futility stop, no bound (2026-11-11 [RESULT]); REG-14 `pass_clear` at 2.2, 1 seed; REG-15 `drop_inconclusive`; REG-16 `control_cold_persistent` (no burst). Older open-loop setups: stuck 0 of 3 in each of 10 cells | C1 **not supported by its own test**. C2 **untested** (condition 4 not computed, no loop figure, no loop-cut control). Conditions 5–6 not shown after a burst | REG-19 (running, paused; seeds 18–19 left). Not registered: condition 4 (Z3), confirmation run at λ = 2.0, D1 session cap, D2 caching off |
| **K1** turn semantics | Open-loop turns hold the prefix and prevent the stuck state; closed-loop turns expose it | One matched pair at λ = 2.4, one seed: REG-10 open `drains` (`overlap_share` 0.608), REG-11 closed `pass`; λ = 2.4 is at the closed-loop warm capacity, so overload also explains the closed arm (REG-13). The older 0-of-30 is **not** evidence ([CORR] 2026-11-12) | not tested at a clean load | REG-20, approved by the owner 2026-11-12; gate `k1.reg20_a_may_start` once after REG-19's [RESULT]; predicted P(arm A starts) ≈ 0.2 (BELIEF, model.md row 23) |
| **K2** range widens with turns per session (the shared-prefix half was dropped 2026-11-12) | Warm capacity over cold floor grows with turns per session (8 → 16, then 4) | none | untested | E0 (prediction and gate, draft 2), E1 (closed-loop cache-off sweep at L1, draft 2), E2 (16-turn sweeps, configs exist), E3 (matrix, only if the gate passes): none registered |
| **K3** model transfer | Published models place this setup's boundary and stuck state within tolerances fixed beforehand, or not | Three unblinded readings near the cold floor (claims.md K3). Model F for L1: sessions 0.89 of all-miss capacity at λ = 2.0, backlog growth 1.56 × excess, served prompt 0.984, requests 1.016 (1.71 req/s) (`analysis/modelf.py`, DERIVED; model itself BELIEF). Measured span rates lie 1–5 % above the model | no registered test | REG-21 draft 2 (needs v3: "J4 cannot change a decision; batching residence confounds J1/J2") |
| **K4** warm-state lifetime | Near the warm capacity the healthy state ends at an arrival surge computable from the schedule | Every no-burst collapse so far followed a 120 s surge of 3.24–3.49 req/s (decisions 2026-11-10 [CORR]); found in the data, has judged no new run | exploratory | none (Z5e exploratory analysis; K4 runs Z9) |
| **K5** detection lead time (optional) | Uncached prefill tokens/s and hit rate move before latency and queue | none | not started | none (Z4) |

Key numbers the claims rest on (all quoted, with place):
- L1 at 350 W, open-loop: μ_warm 3.0, μ_off (keep-up rule) 1.0, cold floor μ_sat,off 1.681 req/s (model.md M2, REG-8 row; `gate.reg8_zone`). The floor was measured with **open-loop** turns on seed 0.
- Closed-loop warm capacity ≈ 2.4 by the configs' rule on seed 0 (REG-13), **not shown to be a sustained capacity** ([CORR] 2026-11-10: the tips at 2.6–3 followed 120 s surges).
- Margin at λ = 2.0: 2.0 / 1.681 = 1.19 (DERIVED). The cell is 0.83 of the closed-loop warm capacity (a fact about the cell, not a comparison; [DECISION] 2026-11-12 "P0 option B").
- Stuck completion rates: 1.73–1.77 req/s at λ = 2.0 (REG-17), 1.73–1.81 at 2.2 (REG-14).
- Burst: 2.4 req/s of one-off 2944-token prompts for 180 s from t = 900 s. L1: 2048-token system prompt per session, 8 turns, 5 s mean gaps, 128 output tokens, prompts 2176 + 256 (k − 1).

## 2. Conflicts (start: pack §12.2 and §12.C)

Status after this pass. "Z6a" = to be fixed with a [CORR]; "kept" = a known difference that needs no fix.

| # | Conflict | Resolution |
|---|---|---|
| 12.2 #1 | status.md says REG-20 both "awaits the owner's approval" and "approved" | stale clause; Z6a |
| 12.2 #2 | `analysis/k3.py` cites a REG-21 entry in decisions.md that does not exist | fixed when REG-21 v3 is registered (Z1); the docstring is corrected then |
| 12.2 #3 | Owner's choices for E0/E1 ("Floor only", 2.2 on E2's grid) and REG-21 ("Register now, mix primary", "Rebuild around per-run sim") are not in decisions.md | [CORR] (Z2b); the only records are status.md:15, a config comment and the saved drafts |
| 12.2 #4 | RESUME.md's pin premise no longer holds: `5ee6e38` changed four harness files, so `launch6.sh` would stop | delegate [DECISION] in review (Z6b): VM stays at `a7bb77a`; Mac-side REG-19 analysis runs from a worktree at `a7bb77a` |
| 12.2 #5 | "Every run is on the Mac" vs the lost seed-18 folder still on the VM | Z6a; the folder is copied after REG-19's [RESULT] (Z6b item 5) |
| 12.2 #6 | PROTOCOL condition 6 says an 1800 s drop; the revised plan sizes the drop from the backlog with a factor of two | PROTOCOL note (Z6a); the confirmation registration fixes the length (Z9) |
| 12.2 #7 | PROTOCOL SLO "from the planned arrival" vs closed-loop latency from release | PROTOCOL note (Z6a) |
| 12.2 #8 | PROTOCOL §4/§5 tables describe the old setups | already annotated; tables are the owner's; kept |
| 12.2 #9 | REG-19 cost heading vs body | old entry, append-only; kept (body rules) |
| 12.2 #10–#12 | paper-plan: K1 cost 11–12 h vs REG-20's 6.4–7.4; K1 status "drafted"; K4 line still "0.41 to 0.51" | Z6a (local paper files); also `docs/claims.md:77` "0.41–0.51" → 0.43–0.52 against 3.15 |
| 12.2 #13 | E1/E2 cost: plan 2.3 / 4.5 h vs draft 2.1 / 4.2 h | fixed at registration (Z2c) |
| 12.2 #14 | related-work "every run reported here uses this limit" (350 W) vs 30 open-loop runs at 420 W | Z6a |
| 12.2 #15 | related-work lists four questions, paper-plan K1–K5; "Three things are untested" then four items | Z6a |
| 12.2 #16–#18 | superseded plan entries; RESUME vs status on the manifest commit; stale remote refs | kept (time-ordered); remote refs re-read when the VM is back |
| 12.C s1 #1–#13 | condition wording, stale line refs in definitions.md, `analysis/CLAUDE.md` "two computations" of percent fast, `harness/CLAUDE.md` "never waits", PROTOCOL check list lacks `release_chain`, `kv_capacity`, `power_limit`, `manipulation`; judged window "1500 s" | Z6a for the ones in documents the agent may fix (status, claims, definitions line refs as a dated note); PROTOCOL and the two code-folder CLAUDE.md files get dated notes under the delegation ("corrections of stale docs") |
| 12.C s2C #1 | REG-16's text says 20 s turn gaps; L1 uses 5 s | [CORR] (Z6a); bears on nothing used |
| 12.C s2C #4, s5/7 #1 | "closed-loop warm capacity ≈ 2.4" used as a capacity after the [CORR] that it is not sustained | wording rule for the paper: "2.4 by the 900 s rule on seed 0"; E0 states it as a known weakness |
| 12.C s5/7 #2 | μ_off 1.0 (keep-up rule) vs cold floor 1.681 | two definitions; D2's registration must name which (start prompt §6.9) |
| 12.C s8/9/13 #4 | claims.md K3 calls session rate and session backlog slope two "discriminating readouts"; decisions 4197: they are one quantity and discriminate only with a closed-loop floor | Z6a (claims.md K3) and REG-21 v3 |
| new | `docs/claims.md:77` and decisions 3978 give Valse and Jannesari's loads as 0.41–0.51 of a 3.26 warm peak; the [CORR] of 2026-11-12 fixed 0.43–0.52 against 3.15 only in the local paper files | Z6a |
| new | The start prompt's snapshot path, `PAPERS_DIR`, `DRIVE_COPIES` | logged (decisions 2026-11-13 [OPS]); Drive copies missing |
| new | The delegation entry was uncommitted and unmarked | committed with the marker (decisions 2026-11-13 [OPS]) |

## 3. What is missing

- **Drive copies** (`context-alignment.md` and the edited paper files): not on this Mac. Their corrections cannot be merged; from the start prompt they are: P0 cut to the cold side only (the repo has this: [DECISION] "P0 option B"); corrections about Lu, Huang and Liu, Valse and Jannesari, KAIROS (the repo has three [CORR]s of 2026-11-12 on these); references pinned to v1 (the repo's [CORR] says "arXiv versions and dates in the references" were added). BELIEF: most of it is already in the repo; unverifiable without the files.
- **Round-2 review texts** of REG-21 and of E0/E1: only the reviewers' scripts survive (`review2/`, `review_e0e1_r2/traces.py`); the findings survive as two sentences in status.md:15.
- No executable trace-order test for condition 4; no onset-rule code for K5; no code reads the `kv_block_*` histograms; no preemption comparison code; no Stage 2 figure.
- No config for: the confirmation run at λ = 2.0, D1 (session cap), D2 (caching off), E3, E4, K4.
- No off-machine backup of `runs/`.
- Self-resume after a crash or reboot (launchd install refused by the permission classifier).

## 4. Answered in this pass

- **A17 (SUPPORTED, source):** vLLM 0.32.0's FCFS scheduler does **not** skip a head-of-queue request that does not fit the KV pool; the waiting loop breaks (scheduler.py lines 1256–1282). Skips exist only for blocked statuses, stale output after a preemption, the LoRA limit, an undetermined connector match and pending encoder transfers. Preempted requests re-enter at the head. So an open-loop all-miss server admits in arrival order. In `docs/open-questions.md`.

## 5. First-pass plan (order by information per hour; GPU can return at any time)

1. **Unblock the GPU queue first:** Z6b (REG-19 resume decision; in review). Then RUNBOOK and DECISION_TREE for REG-19 and REG-20, which are already owner-approved.
2. S8: exclusion of withheld runs in glob tools, so that the zero-GPU analyses can run.
3. Z2a done → Z2b [CORR] → Z2c E0/E1 registration (E1 and E2 are the next GPU items after REG-19/20 and cost 6.3 h; they need approval before the GPU returns).
4. Z1 REG-21 v3 and batch 1 (0 GPU h; K3 is the claim with the most data on record).
5. Z9: confirmation run at λ = 2.0, D1, D2 registrations (need Z5d cap values and the D2 capacity choice).
6. L1/L2 literature pass with anchors; Z6a stale docs.
7. Z3, Z4, Z5 analyses, each registered first.
8. Z7 theory, Z8 simulator, Z10 preprint, Z11 trees.
