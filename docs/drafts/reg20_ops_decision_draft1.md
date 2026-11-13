# REG-20 arm A operations: decision draft 1

**Status.** Draft 1. It has not been reviewed and nothing is decided. It goes to a rule F review and to an owner-proxy, as the delegation requires (FILE(docs/decisions.md:4231-4237)).
- Written 2026-11-13 by a teammate agent. 0 GPU h.
- Nothing under `runs/`, no `state/` folder and no queue output was opened, and the VM was not contacted.
- The scripts it settles are in `docs/probe/20261113_reg20/ops/` (README there). They are not committed.

**Proposed heading:** `## 2026-11-1x · [DECISION] (delegate) REG-20 arm A operations: the scripts in docs/probe/20261113_reg20/ops/; the pin 1cface7 with the checks in force applied to every run as it is copied; the drift run after seed 17's control; the control decision by an ops wrapper of k1.cold_backlogged; the quiet hours withdrawn; three points left to the owner`

**Who decides.**
- The delegate decides what implements REG-20 as registered. The delegation covers "registrations and GPU runs; reruns under registered stopping rules" (FILE(docs/decisions.md:4233)).
- The owner decides what changes something the registration fixed. Each such point below says so in its last line. Until the owner rules, the scripts stop at that point and wait, as they already do.

## Summary

| # | Point | Recommendation | Who |
|---|---|---|---|
| 1 | Pin | `1cface7` | delegate |
| 2 | Checks in force | applied to every run right after its copy, and once more before the table; a changed run stops the queue for the owner | delegate (adds stops only) |
| 3 | Drift run's place | after seed 17's burst run and its control, when one is due | delegate (follows from the registration) |
| 4 | Drift run's open-file limit | recorded, not raised | delegate |
| 5 | Control decision | ops wrapper `control_due.py`; `unclear` runs no control | delegate |
| 6 | Client error in an open burst run | the queue stops; the answer is fixed now: one rerun; a second gives `lost_open` | **owner** |
| 7 | A burst that did not fill the pool, a wrong limit, a second heat failure | stop; the owner decides each time | delegate (unchanged from REG-17 to REG-19) |
| 8 | A lost attempt (no `checks.json`) | after a VM power-off: relaunch, not counted as the rerun; any other loss goes to the owner | delegate |
| 9 | A control with both attempts invalid | stop | **owner** |
| 10 | Invalid runs copied to the Mac | yes | delegate (k1 needs them) |
| 11 | Open-file limit in the launching shell | pre-launch read; the launch command raises the limit to 65536; the queue stops once on a low or missing log line | delegate |
| 12 | Where the analysis runs | the Mac's `main`, with k1's code checked against the pin | delegate |
| 13 | The table's command | `.venv/bin/python -m analysis.k1 reg20` | delegate |
| 14 | The gate | two headings, in order; `REG-190` excluded | delegate |
| 15 | Each control bit is visible in the queue output | accepted as inherent | delegate |
| 16 | Arm B | out of scope; its seal must exist before arm A's `[RESULT]` is written | **owner** |
| 17 | Quiet hours | withdrawn, applied | owner, already decided |

---

## 1. Pin

**Options**
- (a) `1cface7`.
- (b) HEAD, or any commit at or after `5ee6e38` (the A14 fix).
- (c) `1cface7`, plus the checks in force applied to every run (item 2).

**Evidence**
- FILE(docs/decisions.md:4052): each open config "extends its REG-19 partner and sets `workload.sessions.closed_loop: false`, the only change".
- DERIVED: `git diff a7bb77a 1cface7 -- harness/` is empty (run 2026-11-13). The harness at `1cface7` is byte for byte REG-19's harness, `a7bb77a`.
- `1cface7` adds REG-20's 17 configs and `analysis/k1.py`. FILE(docs/decisions.md:4169) requires only that these are committed before any run.
- DERIVED: `git diff --stat 1cface7 HEAD -- harness/` lists four files, `checks.py`, `loadgen.py`, `recorder.py` and `run.py`, with 163 lines added and 29 removed. `git log 1cface7..HEAD -- harness/` lists one commit, `5ee6e38` (A14). Both were run 2026-11-13.

**Recommendation: (c).**
- Under (b), the open arm would run a different `loadgen.py`, `recorder.py`, `run.py` and `checks.py` from the closed arm. That contradicts "the only change" (4052).
- (a) alone judges the open runs by weaker checks than the checks in force since A14 (FILE(docs/decisions.md:4200-4206): "checks only get stricter").
- (c) keeps one harness for both arms and still applies today's checks to every run.

**Limit, stated with any result (BELIEF).** At `1cface7` the recorder can still die on a half-written line (FILE(docs/decisions.md:4202)), and an open-loop backlog writes the most lines.
- Under (c) such a death is caught by the recheck, not prevented. Each one costs a run (≈ 1.07–1.23 GPU h, FILE(docs/decisions.md:4097)) and a stop for the owner.
- One death is on record: A14's run. A14's recheck covered 182 folders (FILE(docs/decisions.md:4205)). The agent did not check whether any other folder lost its recorder (BELIEF). The open-loop rate is unknown.

**Registration:** unchanged. It names no commit, and (c) is the only option that keeps its "only change". The VM's move from `a7bb77a` to `1cface7` waits until REG-19's queue has ended (FILE(agent/RUNBOOK.md:50): never during a run).

## 2. The checks in force: when they are applied

**Options**
- (a) Before the table only.
- (b) After each run's copy, before its control decision and before the next launch, and once more over every run before the table.
- (c) Never.

**Evidence**
- REG-19's resume decision, approved by the owner (FILE(docs/decisions.md:4287)), applies `analysis.recheck` before each step and before the table. A changed validity there is an operational stop, and only `valid` and `failed` are kept (FILE(docs/drafts/reg19_resume_decision_draft5.md:58-68)).
- That draft's reason for not waiting until the end: a ruling on validity made after the table is read is made knowing the outcome (line 66).
- Marking a run invalid beyond its automatic checks is the owner's (CLAUDE.md C; FILE(docs/decisions.md:4205)).

**Recommendation: (b).** Two reasons.
- A run that today's checks fail is found while its rerun is still possible, and before a control decision is spent on it.
- If a changed run is found only at the end, the owner must rule on validity after the open arm's bits have shown in the queue (item 15). Under (b) the owner rules on one run at a time, before the next launch.

How it would work:
- The recheck runs from `main` with `AFTERSHOCK_UNSEAL=REG-20` on two patterns: `*_l1pl350ol_r2.0_w3000_s1[5-9]` (open burst runs and controls) and `*_burst_l1pl350cl_r2.0_w3000_s15_drift`.
- Only `n_runs`, `n_changed` and each changed run's stored and recomputed `valid` and `failed` are written, as ops_r3's `RECHECK_FILTER` does (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:197-201)).
- Any change stops the queue for the owner. The delegate marks, reruns and counts nothing.

**Not yet in the scripts.** If this is approved, `recheck_ok` is ported from ops_r3, with sandbox cases, before the scripts are committed.

**Registration:** unchanged. It adds stops that hand the decision to the owner, and changes no `checks.json`, label or verdict code.

## 3. The drift run's place

**Options**
- (a) Right after seed 17's burst run, before its control.
- (b) After seed 17's burst run and its control, when one is due.

**Evidence**
- FILE(docs/decisions.md:4053): "run after arm A's third run". FILE(docs/decisions.md:4056): "the drift run after the third".
- FILE(docs/decisions.md:4054): a control runs "right after" its burst run.
- FILE(docs/decisions.md:4052) lists arm A's runs as the five burst configs; the controls are conditional.

**Recommendation: (b).** (a) would break "right after" (4054), so (b) is the only reading that keeps both sentences. "Third run" counts arm A's burst runs, which are its runs (4052). If seed 17 is `lost_open`, the drift run follows its second attempt.

**Registration:** unchanged. This is the coordinator's proposal, and the registration forces it.

## 4. The drift run's open-file limit

**Options**
- (a) Raise it to 65536, as for the open runs.
- (b) Record it only, and launch with ops_r3's command.

**Evidence**
- FILE(docs/decisions.md:4053): the drift config is REG-19's seed-15 closed run "under a new name". It ran under ops_r3's launch command, which sets no limit (FILE(docs/probe/20261113_reg19/ops_r3/launch.sh:51)).
- The soft limit on the VM read 1024 on 2026-11-12 (FILE(agent/RUNBOOK.md:28)).
- FILE(docs/decisions.md:4057) asks for the read "for the open arm".

**Recommendation: (b).** A drift check should repeat its original's conditions. REG-17/18's closed burst runs ended with 149–226 sessions in service (FILE(docs/decisions.md:4089)), well below 1024.
- That a closed-loop run holds about one socket per session in service is a BELIEF.
- That the limit did not bind seed 15's original run is a BELIEF too: its numbers are withheld.

**Registration:** unchanged.

## 5. The control decision

**Options**
- (a) An ops wrapper, `docs/probe/20261113_reg20/ops/control_due.py`, that prints one line.
- (b) A command-line entry added to `analysis/k1.py`.
- (c) The whole `analysis.k1 reg20` table mid-matrix, with one field read from it.

**Evidence**
- FILE(analysis/k1.py:303-305): k1's `__main__` offers only `reg20` and `reg20_a_may_start`.
- FILE(docs/decisions.md:4169): `k1.py` had to be committed before any run.
- FILE(analysis/k1.py:160): `open_seed` reads `cold_backlogged(burst)` with the run's own windows and rules. The wrapper makes the same call (FILE(docs/probe/20261113_reg20/ops/control_due.py)).
- FILE(analysis/k1.py:162-163): a `None` reading becomes `unclear` before any control is looked at.
- Tests: `test_control_due.py`, 35 of 35 passed.

**Recommendation: (a).**
- The control decision is the table's own reading of that run, by construction (DERIVED from the same call with the same arguments).
- (b) edits code that the approval fixed.
- (c) is an interim look at every arm A run.
- `CONTROL_DUE unclear` runs no control, because the table would never read it.

**Registration:** unchanged.

## 6. A client error in an open burst run (the coordinator's `lost_open` reading tested)

**The coordinator's claim:** `lost_open` needs two invalid attempts, so one rerun after a client error is part of REG-20's own definition, not a new rule.

**Evidence**
- FILE(docs/decisions.md:4057), standing instructions "as for REG-17 to REG-19": "one rerun of a run invalid by the automatic checks; stop and ask on a client error, a burst that does not fill the pool, or an unexpected pre-launch check".
- FILE(docs/decisions.md:4067): `lost_open` is "burst run invalid after its rerun", and it counts as cold.
- FILE(analysis/k1.py:286): `lost = ob is None and n_bad >= 2`.
- FILE(docs/decisions.md:4103), review T3: a stuck open run is expected to end in client errors, and "Invalid → one rerun → invalid → `reg20_table` drops the seed silently". FILE(docs/decisions.md:4137) answers T3 by counting `lost_open` as cold.
- FILE(docs/drafts/reg19_resume_decision_draft5.md:34): under REG-17 to REG-19, "stop and ask on a client error" was applied as no rerun without the owner.

**What the agent finds.**
- **Agreed:** the rerun is REG-20's. Its `lost_open` exists for exactly this path (T3, 4103 and 4137), and k1 cannot give it without a second invalid run. If the rerun is refused, the seed reads `not_run`, leaves n (FILE(analysis/k1.py:158), FILE(analysis/k1.py:215)), and the bias T3 named returns.
- **Not agreed:** that it is "not a new rule". The registered instruction is still "stop and ask". Under REG-17 to REG-19 it meant the owner answers each time. Fixing the answer now, before any run, changes how a registered instruction works.

**Options**
- (a) As REG-19: stop, and the owner answers each time. A refusal leaves the seed `not_run`.
- (b) Stop, and answer by a rule fixed now:
  - the delegate reads only `checks.json` and the allowed reads (the attempt record's `nofile` lines, the pre-launch probe, the boot id);
  - if those show no cause outside the run (the launching shell's limit at least 4096, the same boot), it writes `state/rerun_ok_<run id>.txt` and the run is rerun once;
  - a second client error gets a second record, the seed is `lost_open`, and the queue goes on;
  - a cause outside the run goes to the owner.
- (c) Rerun automatically, without the stop.

**Recommendation: (b).**
- It keeps the registered stop, and it gives the answer that the registration's own labels need.
- Fixed before any outcome exists, it cannot depend on one (rule A5).
- That matters here: by the time a client error comes, the queue output has shown earlier seeds' control bits (item 15).
- (c) drops a registered stop.

**Registration: (b) changes a registered instruction ("stop and ask") into an answer fixed in advance. It needs the owner, not the delegate.** Until the owner rules, the scripts stop and wait on a client error. They already do this (FILE(docs/probe/20261113_reg20/ops/common.sh:130), FILE(docs/probe/20261113_reg20/ops/common.sh:148)). The `rerun_ok` record is the mechanism under either answer.

## 7. A burst that did not fill the pool, a wrong limit, a second heat failure

**Evidence**
- `manipulation` (the burst's KV maximum below its minimum) and "a burst that does not fill the pool" are registered stops (FILE(docs/decisions.md:4057)).
- `power_limit` and a second `gpu_steady` failure are REG-19's stops, carried over by "as for REG-17 to REG-19".

**Recommendation:** stop, and the owner decides each time. This is what the scripts do (FILE(docs/probe/20261113_reg20/ops/common.sh:120), FILE(docs/probe/20261113_reg20/ops/common.sh:130), FILE(docs/probe/20261113_reg20/ops/common.sh:148-150)).
- A burst that did not fill the pool means the shock was not delivered. Whether a seed lost to two such failures should count as `lost_open` (cold, by k1) is for the owner, if it ever happens.

**Registration:** unchanged.

## 8. A lost attempt (no `checks.json`)

**Evidence**
- The registered rerun is "of a run invalid by the automatic checks" (FILE(docs/decisions.md:4057)). A run with no `checks.json` was never judged by them.
- k1 counts every folder on the Mac that is not valid, including one without `checks.json` (FILE(analysis/k1.py:142-148)).
- A lost folder is kept on the VM and copied later, for the record (FILE(agent/RUNBOOK.md:84)). For REG-19 that copy comes after the [RESULT] (FILE(agent/RUNBOOK.md:48)). The scripts never copy a folder without `checks.json` (FILE(docs/probe/20261113_reg20/ops/common.sh:162-169)).
- The owner says power-offs happen at random (FILE(docs/decisions.md:4504-4506)).
- A harness that dies under a stuck open load would make a loss depend on the outcome. That is a BELIEF, untested.

**Options**
- (a) As now: a lost attempt counts as one of the two. One lost plus one invalid leaves the seed `not_run`, and the queue stops for the owner.
- (b) A loss with a changed boot id (the VM went off) does not count as the registered rerun. It is relaunched under a record, at most twice per config, as REG-19 allowed after its losses. A loss with an unchanged boot id (the harness died while the VM stayed up) goes to the owner.
- (c) Count a lost run as invalid.

**Recommendation: (b).**
- A power-off says nothing about the run, so it should not spend the registered rerun.
- A harness death might, so the owner rules on that one.
- (c) changes the meaning of `lost_open`.

**Order constraint:** no lost folder of a REG-20 config may reach the Mac's `runs/` before `final.sh` has run. Otherwise k1 would count it in `n_bad`.

**Not yet in the scripts.** (b) needs the attempt count to read the boot id from each attempt record, which holds it, and a second cap. It comes with sandbox cases, after approval.

**Registration:** unchanged under (b), which is outside the registered rerun rule. (c) would need the owner.

## 9. A control with both attempts invalid

**Evidence**
- k1 reads a cold open run with no valid control as `pending_control` (FILE(analysis/k1.py:166-167)). The registered outcome is then `pending_controls`, "run the control, then compute again" (FILE(docs/decisions.md:4073)).
- The rerun rule allows one rerun (4057).

**Recommendation:** the queue stops, as now. The registration asks for both a valid control and at most one rerun, so a third attempt or a table with `pending_controls` is a choice between two registered sentences.

**Registration: either way out needs the owner.**

The drift run with both attempts invalid also stops. This is the delegate's choice: the drift reading changes no label (4053), but two failed drift runs say something about the machine that matters before more open runs.

## 10. Invalid runs are copied to the Mac

**Evidence:** `lost_open` needs `n_bad >= 2` on the Mac (FILE(analysis/k1.py:142-148, 283-286)). ops_r3 copied only valid runs.

**Recommendation:** copy every run that has a `checks.json` and verify its checksums, as the scripts do. Without this, two invalid attempts would read `not_run`, not `lost_open`.

**Registration:** unchanged. This implements it.

## 11. The open-file limit in the launching shell

**Evidence**
- FILE(docs/decisions.md:4057): the read is "in the shell that starts the harness"; below 4096, stop and ask.
- DERIVED: a grep of `harness/` at `1cface7` for `rlimit`, `ulimit` and `nofile` finds nothing. The pinned harness cannot set the limit itself.
- The launch command is `ulimit -n 65536 && echo "nofile $(ulimit -n)" > LOG && exec … harness.run … >> LOG 2>&1` (FILE(docs/probe/20261113_reg20/ops/launch.sh:58)).

**Recommendation: keep it as written.**
- The pre-launch read tests the raise in an ssh shell and stops below 4096.
- DERIVED from the `&&` chain: if the harness starts at all, its shell holds 65536.
- The log line records this. A low or missing line stops the queue once after the run (FILE(docs/probe/20261113_reg20/ops/queue.sh:62-68)).
- The value is set in `common.sh` (`NOFILE_SET`) and written to every attempt record. A config field would need a harness change.

**Registration:** unchanged. It asks for at least 4096 in the launching shell, and this provides it and records it.

## 12. Where the control decision and the table run

**Options**
- (a) A worktree at `1cface7` with links, as REG-19 does.
- (b) The Mac's `main` from the repo root. Every launch, copy and table first checks that k1's import closure equals the pin's and that the seal files match their recorded blobs (FILE(docs/probe/20261113_reg20/ops/common.sh:35-37), FILE(docs/probe/20261113_reg20/ops/common.sh:56-62)).

**Evidence**
- DERIVED: `git diff 1cface7 HEAD` over k1's closure (`__init__`, `k1`, `gate`, `margin`, `derived`, `floor`, `stats`) is empty. `load.py` differs only by the 6-line seal guard.
- `withheld.py` does not exist at `1cface7` (DERIVED: `git cat-file` at the pin).

**Recommendation: (b).** The seal stays in force for every other process. The code identity is checked on every turn, not assumed. No links are needed.
- Any commit to those files stops the queue until `common.sh` is updated by a reviewed commit.
- This departs from RUNBOOK §5, which asks for a worktree per item (FILE(agent/RUNBOOK.md:59)).

**Registration:** unchanged.

## 13. The table's command

**Evidence:** `final.sh` now runs `uv run python -m analysis.k1 reg20` (FILE(docs/probe/20261113_reg20/ops/final.sh:26)). `control_due.py` runs under `.venv/bin/python`, and the session probe checks that `.venv` holds the locked packages.

**Recommendation:** `AFTERSHOCK_UNSEAL=REG-20 .venv/bin/python -m analysis.k1 reg20`.
- It is the same interpreter as the control decision and as REG-19's table.
- `uv run` may sync the environment first.

**Registration:** unchanged. The registered computation is `analysis.k1 reg20`. A one-line script change after approval.

## 14. The gate

**Evidence:** the scripts require both headings in HEAD's `docs/decisions.md`, in order:
- `^## <date> · \[RESULT\] REG-19([^0-9]|$)`;
- on a later line, `^## <date> · \[DECISION\] \((owner|delegate)\) REG-20 arm A starts`.

They never compute `k1.reg20_a_may_start` (FILE(docs/decisions.md:4051)).

**Recommendation:** keep it. `([^0-9]|$)` only refuses more. The heading of the start decision must carry these exact words.

**Registration:** unchanged.

## 15. The control bits in the queue output

**Evidence:** a control runs only after a cold-backlogged burst run (FILE(docs/decisions.md:4054)). Whoever sees a control launched knows that seed's bit.

**Recommendation:** accept it. It cannot be hidden without breaking 4054. The answers that follow a stop are fixed in advance wherever this draft can fix them (items 6 and 8), so no later choice depends on those bits.

**Registration:** unchanged.

## 16. Arm B and its seal

**Evidence**
- FILE(analysis/withheld.py:28): REG-20's seal covers `*_l1pl350ol_r2.[05]_w3000_s1[5-9]`, both arms, and lifts at `[RESULT] REG-20`.
- FILE(analysis/withheld.py:46): the seal lifts on any heading `[RESULT] REG-20` followed by a non-digit, so "REG-20 arm A" and "REG-20A" both lift it.
- Arm B runs only after arm A gives `supports` or `supports_no_mechanism` (FILE(docs/decisions.md:4055)). That is known only from arm A's table, which a `[RESULT]` reports.

**Recommendation:** arm B is out of scope for these scripts and this decision. But arm A's `[RESULT]` heading would unseal arm B's folders before they exist.
- An arm-B seal must be in place before that heading is committed.
- That means an edit to `analysis/withheld.py`, a frozen file. It changes the blob these scripts check, so it must come after `final.sh` has run.

**Registration: how arm A's result is written and when the seal changes needs the owner, before arm A's `[RESULT]`.**

## 17. Quiet hours: withdrawn, applied

**Evidence:** FILE(docs/decisions.md:4502-4510): the owner, verbatim, "there is no such thing as quiet hours, whenever its available use it, power off happens randomly".

**Applied:**
- `common.sh` and `launch.sh` no longer hold a time-of-day limit, nor the config-derived run lengths that only that limit used.
- The sandbox runs the whole queue with the clock at eleven hours and checks that no script reads the hour.
- `zsh docs/probe/20261113_reg20/ops/test_sandbox.sh`: 214 of 214 passed (2026-11-13).
- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider docs/probe/20261113_reg20/ops/test_control_due.py`: 35 of 35 passed.

**The reading:** the entry's heading names REG-19, but the owner's words are general. The delegate applies them to REG-20. REG-20's registration has no quiet hours, so nothing it fixed changes.

---

## Script changes this decision implies (none made yet)

1. Item 2: `recheck_ok` after each copy and before the table.
2. Item 8: lost attempts counted by boot id, with their own cap.
3. Item 13: `final.sh` under `.venv/bin/python`.

Each comes with sandbox cases, and `scripts_commit.txt` is written after the commit.

## Not settled by this draft

- **For the owner:** items 6, 9 and 16.
- **The pin's A14 risk** (item 1) is a limit, not settled: the open-loop recorder death rate is unknown.
- **Whether a harness death correlates with a stuck open run** (item 8) is a BELIEF. It could be checked only by an open-loop run that is not part of REG-20. It belongs in `docs/open-questions.md`.
