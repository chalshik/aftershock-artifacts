# REPORT (one page; rewritten at each milestone)

Milestone: **session start, 2026-11-13.** Nothing new is measured yet. All values below are the repo's own, with their sources.

## Claims

| Claim | Status today | Evidence on record | Registration that addresses it |
|---|---|---|---|
| P0 (C1 + C2, cited premise, replicated here) | not supported by its own test | REG-17 `pass_clear` (1 seed, λ = 2.0); REG-18 `some`, 1 of 4; REG-14 `pass_clear` (λ = 2.2, 1 seed); conditions 4–6 not shown | REG-19 (paused, seeds 18–19 left); confirmation run not registered |
| K1 turn semantics | not tested at a clean load | one matched pair at λ = 2.4 (REG-10 drains, REG-11 stuck; overload confound) | REG-20 (approved, gated on REG-19) |
| K2 range widens with turns per session | untested | none | E0/E1 drafts (not registered); E2, E3 |
| K3 model transfer | no registered test | three unblinded readings near the cold floor | REG-21 draft 2 (needs v3) |
| K4 warm-state lifetime | exploratory | every no-burst collapse followed a 120 s surge of 3.24–3.49 req/s (found in the data) | none |
| K5 detection lead time | not started | none | none |

## What changed in this block

Setup only: drafts saved into the repo, `docs/paper/` under its own git history, `runs/` backed up on the same disk and verified, state files, GPU watcher, heartbeat.

## Next

Finish the ingest, read the papers, then the zero-GPU registrations in the order of `agent/PLAN.md` (REG-21 v3, A17 and E0/E1, condition 4, K5, the REG-19 pin decision).

## GPU readiness

VM offline (2026-11-13 00:33 local, watcher state `down`). REG-19's resume needs the pin decision (PLAN Z6b) before it can launch.

## GPU-hour ledger (remaining; registrations' own figures, else planning estimates)

| Item | GPU h | Registered and approved? |
|---|---|---|
| REG-19 seeds 18–19 | 4.7–4.9 | yes (owner); resume decision pending |
| REG-20 arm A + drift | 6.4–7.4, only if its gate passes (predicted P ≈ 0.2) | yes (owner) |
| REG-20 arm B | 3.2–3.7, only after `supports` | yes (owner) |
| E1 | ≈ 2.1 | no |
| E2 | ≈ 4.2 | no |
| E3 | 8–12, only if E0's gate passes | no |
| D1 + D2 | 4–6 | no |
| Confirmation (conditions 5–6) | ≈ 4.5 (REG-16's scale) | no |
| K4 | long runs, not sized | no |
