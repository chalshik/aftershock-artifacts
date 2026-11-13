# reg20-ops-worker-report (reg20-ops), verbatim

Saved by the agent from the teammate message received in the main session transcript, 2026-11-13 between 12:42 and 12:51 UTC (the senders' idle notifications). Item names as given by the reviewer (prefixes BA, BB, BC, BD, CA, CB were assigned in the review prompts).

---

REG-20 ops is only partly done: no scripts written, no sandbox run. I hit the usage limit. I wrote 2 docs (new files only, no commits, no existing file edited, VM not contacted, no run, probe or state file opened).

Files, all in docs/probe/20261113_reg20/ops/:
1. PIN_DECISION_DRAFT.md — the pin facts and three options. None is recommended.
2. DESIGN_NOTES.md — each registered rule with its decisions.md line, the proposed script design, and 7 open points. The next session can write common.sh, vm_state.py, session_probe.sh, launch.sh, queue.sh and test_sandbox.sh from ops_r3 using it.

Sandbox: not written, not run (0 of 0).

PIN FACTS (git on the Mac):
- a7bb77a is an ancestor of 1cface7, and 1cface7 is an ancestor of HEAD (e404c74).
- `git diff --stat a7bb77a 1cface7 -- harness/` is empty: the harness is byte-identical. Only the 17 REG-20 configs are added; uv.lock, pyproject and manifest.py are unchanged.
- `git diff --stat 1cface7 HEAD -- harness/`: 4 files, +163/−29 (checks 42, loadgen 83, recorder 50, run 17). All of it is commit 5ee6e38: the A14 fix plus the session cap.
- From 1cface7 to HEAD, no REG-20 config changes, and k1.py, gate.py and stats.py are unchanged. load.py changes by 6 lines; withheld.py is new.
- The approval names no commit (decisions.md:4169), so the default pin is 1cface7.

REGISTERED RULES FOUND:
- Gate is computed once, after REG-19's [RESULT] (decisions.md:4051, 4168). Proposed check: a GATE_PAT heading "[DECISION] (owner|delegate) REG-20 arm A starts: k1.reg20_a_may_start passed", placed after a "[RESULT] REG-19" heading.
- Arm A: s15–19 in order (4052, 4056).
- Drift run after "arm A's third run" (4053).
- Controls only after a cold-backlogged open run, right after it (4054).
- Arm B: s15–17 at 2.5, only after supports or supports_no_mechanism (4055).
- Standing instructions (4057): 350 W read; ≤45 °C; clean tree; ONE rerun, so MAX_ATTEMPTS=2 (REG-19 used 3); stop and ask on client_error, manipulation, or an unexpected pre-launch read; `ulimit -n` ≥ 4096 for the open arm. RUNBOOK.md:28 gives soft 1024, hard 1,048,576. Plan: `ulimit -n 65536 && echo nofile …` inside the tmux command, plus a pre-launch read that stops below 4096.

AMBIGUITIES AND CONFLICTS (details in DESIGN_NOTES):
1. "Third run": does a conditional control count as a run? I propose counting burst runs only.
2. k1.py's CLI has only `reg20` and `reg20_a_may_start` (k1.py:303-305). Nothing gives the per-run cold_backlogged reading the control decision needs mid-matrix. Options: a wrapper that prints only the boolean, or a CLI edit.
3. k1 `_open_row` marks lost_open only after 2 invalid runs. But a client error means stop and ask, so if the owner allows no rerun, the seed becomes not_run and is dropped instead of counting as cold. This is the T3 bias again.
4. withheld.py lifts the seal on the arm B runs at "[RESULT] REG-20". If arm A's result is logged under that heading, arm B is unsealed before it runs.
5. Quiet hours: ops_r3 uses 14:15–18:00; the 02:30–05:00 window is an unapplied patch. An open burst run should need room for a following control too.
6. Drift run's ulimit: I propose leaving it unraised, since REG-19's s15 ran at 1024.

LEFT TO DO: the six scripts, the sandbox and its pass count.
