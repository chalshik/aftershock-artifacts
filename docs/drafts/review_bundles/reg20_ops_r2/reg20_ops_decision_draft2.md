# REG-20 arm A operations: decision draft 2

**Status.** Draft 2. It has not been reviewed and nothing is decided.
- **Written:** 2026-11-14 (Mac local time; 2026-11-13 ≈ 23:00–24:00 UTC) by a teammate agent, 0 GPU h.
- **Not touched:** the VM was not contacted. Nothing under `runs/` was opened beyond folder names. No `state/` folder, queue output, `reg19_final_*` file or transcript was opened.
- **Draft 1 and its scripts** are committed in c8b482d. Draft 1's line 6 ("They are not committed") was false (RA7).
- **Draft 2's scripts** are the working tree of `docs/probe/20261113_reg20/ops/` on 2026-11-14. They are **not committed**, because the brief for this draft said not to commit. The [DECISION] names the commit that holds them, with `scripts_commit.txt` and its sandbox count, after a rule F round 2 and an owner-proxy round 2 on the diff from c8b482d (RA7).
- **Round 1 of review** gave two verdicts:
  - rule F: NOT READY, with RA1–RA7 required and RA-O1–RA-O9 optional (`docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft1-r1.md`);
  - owner-proxy: APPROVE with conditions RB1–RB15 (`docs/drafts/reviews-2026-11-13/proxy-reg20-ops-draft1.md`).
- **The item map** says where each item went, every departure from its text and every merge of the two reviews: `docs/drafts/reg20_ops_draft2_itemmap.md`.
- **Tests** run on fakes only. The outputs are saved in the ops folder:
  - `test_sandbox.sh`: **350 of 350 passed**, `docs/probe/20261113_reg20/ops/sandbox_20261113T231823Z.txt`;
  - `test_control_due.py`: **46 of 46 passed**, `docs/probe/20261113_reg20/ops/test_control_due_20261113T231828Z.txt`.

**What changed around this draft while it was written (each from `git log` on the Mac, 2026-11-13 ≈ 23:10 UTC). Commit subjects are not evidence (rule B); the files they name are.**
- **REG-19's table was computed.** Commit 047b95e (2026-11-13T22:56Z) adds REG-19's table file, `ops_r3/state/reg19_final_<stamp>`, and its stderr file (`git show --stat`, names only, not opened).
- **REG-19's [RESULT] was committed.** Commit 6748c26 holds it, and its heading is FILE(docs/decisions.md:16517).
- **REG-20's gate was computed once.** Commit 3c8e5dc adds `docs/probe/reg20/gate_20261113T230307Z.txt` and `gate_err_20261113T230307Z.txt` (point 14).
- **So the brief's premise is out of date.** The brief said REG-19's table "is not yet computed".
- **RB11's first branch can no longer be met** (see "Timing" below).
- **The author saw REG-19's outcome after the scripts were written.** It saw it through the subject line of 6748c26 and the first words of the heading at 16517. This was after the scripts, `test_sandbox.sh`, `test_control_due.py`'s additions and the ops README were written, and before this text, the item map and the gate change in point 14. The author did not open REG-19's [RESULT] entry, the table files or the gate file's value.

**Proposed headings** (three entries, in this order in `docs/decisions.md`):
1. `## 2026-11-1x · [DECISION] (delegate) REG-20 arm A operations: the scripts in docs/probe/20261113_reg20/ops/ at <commit>; the pin 1cface7, each run rechecked by the checks in force before it enters runs/ or a control decision; the drift run after seed 17's control; the control decision by control_due.py between two code checks; the gate computed once (3c8e5dc); six points ruled by the owner before the first launch`
2. `## <date> · [DECISION] (owner) REG-20 arm A operations: the owner's rulings`. It quotes `docs/probe/20261113_reg20/ops/owner_rulings.txt`, and is committed with that file.
3. `## <date> · [DECISION] (owner|delegate) REG-20 arm A starts: k1.reg20_a_may_start passed`. Only if the gate file reads `'may_start': True`; it quotes the file verbatim.

The scripts start only with all three in HEAD, in this order, and with no stop heading after the third (point 14).

**Who decides.**
- The delegate decides what implements REG-20 as registered. The delegation covers "registrations and GPU runs; reruns under registered stopping rules" (FILE(docs/decisions.md:4233)).
- The owner decides what changes something the registration fixed, and every point whose answer would otherwise be chosen after control bits are visible.
  - These are points 2a, 6, 7, 8, 9 and 16, plus question G on the gate's command.
  - **All are ruled before the first launch** (RA5), in `owner_rulings.txt` and the owner's entry above.
  - The scripts refuse to start while any point reads `unset` or an answer it may not take (FILE(docs/probe/20261113_reg20/ops/common.sh:100), `rulings_ok`).
  - Draft 1's "until the owner rules, the scripts stop at that point and wait" (FILE(docs/drafts/reg20_ops_decision_draft1.md:12)) is withdrawn (RA5).

## Summary

| # | Point | Recommendation | Who |
|---|---|---|---|
| 1 | Pin | `1cface7` | delegate |
| 2 | Checks in force | applied to each run in a holding folder outside `runs/`, after its copy and before it enters `runs/`, before any control decision; again over `runs/` before the table | delegate (the stop) |
| 2a | A run those checks change | ruling: `keep`, `setaside`, `stop` or `pin_head` | **owner** |
| 3 | Drift run's place | after seed 17's burst run and its control, when one is due | delegate (forced by the registration) |
| 4 | Drift run's open-file limit | recorded, not raised | delegate |
| 5 | Control decision | `control_due.py`; Mac-side checks just before and just after; `unclear` runs no control | delegate |
| 6 | Client error in an open burst run | ruling (a) or (b) | **owner** |
| 7 | Other stop-and-ask failures, and RA3's setup case | stop; per-stop answer only on rerun or not (RB7); the setup case by ruling 7 | delegate (stops); **owner** (ruling 7) |
| 8 | A lost attempt (no `checks.json`) | ruling (a) or (b) | **owner** (RA6) |
| 9 | A control with both attempts invalid | ruling (a) or (b) | **owner** |
| 10 | Invalid runs copied to the Mac | yes, through the holding folder | delegate |
| 11 | Open-file limit in the launching shell | as draft 1; a low or missing log line needs a `nofile_ok` record (RB15) | delegate |
| 12 | Where the analysis runs | the Mac's repo root; the code checked at every turn and just before and after each use | delegate |
| 13 | The table's command | `AFTERSHOCK_UNSEAL=REG-20 .venv/bin/python -m analysis.k1 reg20`, after a recheck | delegate |
| 14 | The gate | three ordered headings, no later stop heading, the one committed gate file | delegate; **owner** (question G) |
| 15 | Control bits and failed-check names visible in the queue output | accepted as inherent | delegate |
| 16 | Arm B and its seal | ruling (a), (b) or (c) | **owner** |
| 17 | Quiet hours | withdrawn, applied | owner, already decided |

---

## 1. Pin

**Options**
- (a) `1cface7`.
- (b) HEAD, or any commit at or after `5ee6e38` (the A14 fix).
- (c) `1cface7`, plus the checks in force applied to every run (point 2).

**Evidence** (as draft 1)
- FILE(docs/decisions.md:4052): each open config "extends its REG-19 partner and sets `workload.sessions.closed_loop: false`, the only change".
- The harness at `1cface7` is byte for byte REG-19's harness, `a7bb77a`. DERIVED: `git diff a7bb77a 1cface7 -- harness/` is empty (run 2026-11-13; owner-proxy round 1 repeated it).
- `1cface7` adds REG-20's 17 configs and `analysis/k1.py`. FILE(docs/decisions.md:4169) requires only that these are committed before any run.
- `git log 1cface7..HEAD -- harness/` lists one commit, `5ee6e38` (A14) (DERIVED, 2026-11-13).

**Recommendation: (c).**
- (b) puts a different `loadgen.py`, `recorder.py`, `run.py` and `checks.py` in the open arm, against "the only change" (4052).
- The owner made the same choice for REG-19 (FILE(docs/decisions.md:4284)).

**Correction of draft 1 (RA2).** Draft 1 said "(c) keeps one harness for both arms and still applies today's checks to every run" (FILE(docs/drafts/reg20_ops_decision_draft1.md:54)). That held for the stop only, never for a label: k1 reads validity only from the stored `checks.json` (FILE(analysis/k1.py:145)). Draft 2 gives the recheck a path to the label in point 2. Whether that path is used is ruling 2a, which also offers (b) as `pin_head`.

**Limit, stated with any result (BELIEF).** At `1cface7` the recorder can still die on a half-written line (FILE(docs/decisions.md:4202)), and an open-loop backlog writes the most lines.
- Under (c) such a death is detected, not prevented.
- A14's recheck covered 182 folders (FILE(docs/decisions.md:4205)). One death is on record.
- The open-loop rate is unknown.

**Deviation from PROTOCOL §5 (RB12), stated in the decision.**
- REG-20's stored checks are the pin's, which lack A14's coverage checks (FILE(PROTOCOL.md:78-79)).
- Today's checks are applied read-only (point 2), as REG-19's resume did (draft 5, point 4, first bullet).
- Under option (c), a recorder death is detected, not prevented.

**Who:** the delegate, because the registration names no commit (FILE(docs/decisions.md:4169)). Ruling 2a's `pin_head` would be the owner's.

## 2. The checks in force: when they are applied

**What the scripts do (draft 2, RA2 (b) and RB2 (ii), merged; item map M1).** Each finished run, valid or invalid, goes through five steps:
1. It is copied from the VM into a holding folder outside every `runs/`: `<repo's parent>/aftershock-reg20-holding` (FILE(docs/probe/20261113_reg20/ops/common.sh:12)).
2. Its sha256s are compared with the VM's.
3. `recheck_one.py` applies today's `harness.checks.run_checks` (the checks in force since `5ee6e38`) to it there (FILE(docs/probe/20261113_reg20/ops/recheck_one.py)). This is read-only.
   - Only `run`, `stored_valid`, `stored_failed`, `now_valid`, `now_failed`, `changed` and `error` are printed. The queue's filter keeps only these fields (FILE(docs/probe/20261113_reg20/ops/common.sh:486)).
   - ops_r3's two guards run first (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:206-207)): `harness/checks.py` equals `5ee6e38`'s, `analysis/recheck.py` equals `72fafb5`'s, and `analysis/`, `harness/` and `configs/defaults.yaml` equal HEAD in the working tree.
4. Ruling 2a is applied (`recheck_apply`, FILE(docs/probe/20261113_reg20/ops/common.sh:510)).
5. Only then is the run moved into `runs/` and verified again (FILE(docs/probe/20261113_reg20/ops/common.sh:543)). No control decision is made on a run without its recheck record (FILE(docs/probe/20261113_reg20/ops/queue.sh:44)).

Before the table, `final.sh` runs `analysis.recheck` over `runs/` on both patterns, `*_l1pl350ol_r2.0_w3000_s1[5-9]` and `*_burst_l1pl350cl_r2.0_w3000_s15_drift`, with `AFTERSHOCK_UNSEAL=REG-20` (FILE(docs/probe/20261113_reg20/ops/final.sh:58)).
- Its run count must equal the copied runs.
- The runs it finds changed must equal the queue's `recheck_changed … kept` lines.
- It must write no `withheld:` line.
- Otherwise there is no table (FILE(docs/probe/20261113_reg20/ops/final.sh:69-70)).

**RB2 (i), replacing draft 1's line 75 verbatim:** "A run that today's checks fail is found before a control decision is spent on it. It cannot be rerun: a second valid run of its config stops the queue (common.sh:139) and makes k1 raise (k1.py:146-147). The owner's answer is to keep it as its checks.json says, or to stop arm A."

Draft 2 adds the following to that text.
- **The cited line has moved.** In draft 2's scripts, "common.sh:139" is the two-valid-runs stop at FILE(docs/probe/20261113_reg20/ops/common.sh:273).
- **A third answer exists in draft 2's scripts.** The run is checked before it enters `runs/`, so the answer "set it aside" (RA2 (b)) is open. A run set aside stays in the holding folder, never enters `runs/`, and its config is rerun as its next attempt. k1 then never sees two valid runs of one config.
- **The text above is kept verbatim, as RB2 asks.** Its "It cannot be rerun" holds only for a run already in `runs/`. Ruling 2a chooses among the answers.

**Registration:** unchanged. It adds stops, and it changes no `checks.json`, label or verdict code. The answer to a stop is ruling 2a, the owner's.

## 2a. A run that today's checks change (new; the owner's, RB2 (iii), RA2)

The question and its options are under "For the owner, before the first launch".

How the scripts apply each answer:
- **`keep`:** they print the RECHECK line, keep the run as its `checks.json` says, and go on.
- **`setaside`:** this applies to a stored-valid run that is now invalid. The scripts write `state/setaside_<rid>.txt`, keep the run in the holding folder, and stop; a restart reruns its config. Any other change is kept.
- **`stop`:** they stop until the owner writes `state/recheck_ok_<rid>.txt` with `answer keep|setaside`.
- **`pin_head`:** they refuse to start until `common.sh`'s pin is changed by a reviewed commit (FILE(docs/probe/20261113_reg20/ops/common.sh:100)).

A folder that today's code cannot read stops the queue under every answer.

## 3. The drift run's place

As draft 1, unchanged: after seed 17's burst run and its control, when one is due (FILE(docs/decisions.md:4053-4054)). Both reviews agree.

## 4. The drift run's open-file limit

As draft 1 (b): recorded, not raised.

**RB13 replaces draft 1's line 109, second sentence, verbatim:** "It ran on 2026-11-12 under docs/probe/20261111_reg19/ops/, whose launch commands set no limit (FILE(docs/probe/20261111_reg19/ops/launch3.sh:27); launch4.sh:31, launch5.sh:32 and launch6.sh:36 carry the same command). ops_r3's command is the same in substance (FILE(docs/probe/20261113_reg19/ops_r3/launch.sh:51))."
- The agent checked the four citations: each line starts the harness with no `ulimit`.
- Which queue launched seed 15's closed run is not checked here. That would need `state/` or a queue output, which this draft may not open (RA-O5). The sentence's date and folder are RB13's (BELIEF until seed 15's launch record is cited).

## 5. The control decision

As draft 1: `control_due.py` prints one line from `k1.cold_backlogged(run)["cold_backlogged"]`, and `unclear` runs no control.

**Changed (RB1, RA4).**
- Every turn of the queue first runs the Mac-side checks. RB1's line is verbatim at FILE(docs/probe/20261113_reg20/ops/queue.sh:58).
- `mac_checks` also runs immediately before and immediately after the `control_due.py` call (FILE(docs/probe/20261113_reg20/ops/queue.sh:45), FILE(docs/probe/20261113_reg20/ops/queue.sh:49)). If either check fails, the decision is dropped: it is not recorded and not shown.
- The sandbox covers both RA4 cases:
  - `analysis/gate.py` edited during seed 15's burst run: QUEUE STOP before the decision, with no CONTROL line;
  - `analysis/k1.py` edited during the `control_due.py` call: the decision is dropped, then made again on clean code.
- One edge stays open: an edit made and undone within one `control_due.py` call is not seen.

## 6. A client error in an open burst run

As draft 1, with the options unchanged and the question for the owner (see "For the owner").

**Changed.**
- **The record names what it lifts (RA-O4).** `rerun_ok_<rid>.txt` must hold `lifts no_errors/client_error`, and one line per other failure it lifts. Each needs `under …` and `by owner|delegate` (FILE(docs/probe/20261113_reg20/ops/common.sh:191)).
- **A refusal has a path (RB3).** The record `settle_<rid>.txt` with `label not_run` settles the seed. Its run is in `runs/`, k1 reads `not_run`, and the queue goes on.
- **Under (b), the delegate's record is accepted only in one case:** for a client error, when the run's launch log read nofile ≥ 4096 and the session's boot id equals the run's launch boot.

**RB10's sentence, added to option (b) verbatim:** "Residual risk: a client error in open runs that are not stuck, from a cause the allowed reads cannot see, would make each such seed `lost_open` without a stop, and could reach `refutes`. BELIEF that this is unlikely: REG-10's open-loop run at λ = 2.4 was valid and recovered (FILE(docs/decisions.md:4085)), and the 65536 limit removes the descriptor cause named in review T3 (FILE(docs/decisions.md:4103))."

## 7. A burst that did not fill the pool, a wrong limit, a second heat failure, and setup failures

**Stops (as draft 1).** These each stop the queue:
- `manipulation`;
- `power_limit`;
- a second `gpu_steady` among REG-20's runs.

A rerun needs the owner's `rerun_ok` record that names the failure (RA-O4).

**RB7 replaces draft 1's line 180 verbatim:** "By REG-20's label, a burst run invalid after its rerun is `lost_open` and counts as cold, whatever check it failed (decisions.md:4067; k1.py:286). At each of these stops the owner decides only whether the rerun is made (a second failure is then `lost_open`) or not (the seed is then settled `not_run` by RB3's record and leaves n). If the open arm's burst fails to fill the pool systematically, allowing reruns would make each such seed `lost_open` and could reach `refutes` on a shock that was never delivered. That weighs against a rerun after `manipulation`."

**Added (RA3).** When both attempts of an open burst run are invalid and either attempt failed only checks of the setup class, the queue does not give `lost_open`. It stops instead (FILE(docs/probe/20261113_reg20/ops/common.sh:304)).
- The setup class is `clean_git`, `kv_capacity` and `trigger` (FILE(docs/probe/20261113_reg20/ops/common.sh:24)). The class is a BELIEF, fixed here before any run.
- A settle record then decides, with `label lost_open` (RB7's registered label) or `label not_run`.
- Ruling 7 says which label the delegate may write, or that each case goes to the owner.
- **`not_run` and k1.** For k1 to read `not_run`, at most one invalid folder of the config may be in `runs/` (FILE(analysis/k1.py:286)). The record must name the run already copied. The second run is held in the holding folder (`state/held_<rid>.txt`) until REG-20's [RESULT].

**Registration:** unchanged under `lost_open`. Under `not_run` the seed leaves n, which is the registered meaning of `not_run` (FILE(analysis/k1.py:215)).

## 8. A lost attempt (no `checks.json`)

**Who: the owner (RA6).** Draft 1's "delegate" is withdrawn.
- RB4 (iii) approved 8(b) as inside the delegation. RA6 calls it the owner's.
- The stricter reading wins (item map M3). It is implemented, and it is active only under the owner's ruling.

**Implemented** (FILE(docs/probe/20261113_reg20/ops/common.sh:206), `lost_count`).
- A run without `checks.json` stops the queue until `state/lost_ok_<rid>.txt` says `count yes` or `count no`.
- **After a power-off** (the run's launch boot ≠ the session's boot):
  - 8(a): `count yes`, by owner or delegate.
  - 8(b): `count no` by owner or delegate, or `count yes` by the owner. At most `MAX_POWER_LOSSES` = 2 uncounted losses per config (FILE(docs/probe/20261113_reg20/ops/common.sh:21)).
- **Without a reboot,** or with an unknown launch boot: the owner's record only, under either ruling.
- **What is recorded (RA6).**
  - Each attempt record holds `arm` and `end <time> <how>` (FILE(docs/probe/20261113_reg20/ops/launch.sh:58-59)).
  - `queue_done.txt` lists each lost run as `lost <rid> arm … elapsed_s … end … counted …` (FILE(docs/probe/20261113_reg20/ops/common.sh:467)).

**RB4 (ii), verbatim:** "A REG-20 folder without checks.json is copied only to a holding folder outside every runs/ (as REG-19's resume, draft 5 item 5) until REG-20's [RESULT]. If it is ever placed in runs/, `analysis.k1 reg20` is run again, and an [OPS] or [CORR] entry says whether its output changed."
- The scripts never copy such a folder.
- The holding folder of point 2 is the place for a copy made by hand.
- `final.sh` refuses the table when `runs/` holds any folder of the eleven configs that the queue did not copy (RB4 (i), RA-O2; FILE(docs/probe/20261113_reg20/ops/final.sh:40-47)).

## 9. A control with both attempts invalid

**Who: the owner.** RB8's options, written in verbatim:
- "(a) One further attempt of the control, under the registered outcome row "run the control, then compute again" (FILE(docs/decisions.md:4073)). A further failure stops arm A."
- "(b) No further attempt. The slot is settled (RB3), k1 gives `pending_control`, the outcome is `pending_controls`, and K1 gets no statement."
- "(c) Count it as `cold_control`. Not possible without changing k1 (FILE(analysis/k1.py:166-167)), which the approval fixed."

**Implemented:**
- under 9(a), a delegate's `attempt_ok_<cfg>_3.txt` gives one third attempt;
- under 9(b), a delegate's `settle_<rid>.txt` with `label control_not_run` settles the slot.

The owner's records are always accepted.

The drift run with its attempts spent still stops for an owner's `label drift_not_run` (as draft 1, and RB's recommendation).

## 10. Invalid runs are copied to the Mac

As draft 1. Each run now goes through the holding folder first (point 2).

## 11. The open-file limit in the launching shell

As draft 1. One change (RB15): an open run whose launch log shows no nofile line of at least 4096 is used only with `state/nofile_ok_<rid>.txt`, logged in an [OPS] entry (FILE(docs/probe/20261113_reg20/ops/common.sh:286)). Before, a restart went on without a record.

## 12. Where the control decision and the table run

As draft 1 (b): the Mac's repo root, with k1's closure checked against the pin and the seal files against their blobs.

**RB1's sentence replaces draft 1's line 248:** "Every turn of the queue (before each copy, control decision and launch), every launch and the table first check that…". Draft 2 adds: "…and the control decision and the table are each followed by the same check, whose failure drops the decision or refuses the table (RA4)."

**The seal blobs (RA-O1).** A commit to `analysis/load.py` or `analysis/withheld.py` during arm A stops the queue, possibly between a burst run and its control.
- The check is kept, because it is the stricter one.
- The files are frozen by REG-21 and REG-22 until both batch 2s are computed or declared not computed (FILE(docs/decisions.md:9834); `docs/status.md`, freeze notice).
- Each control's gap after its burst run (`gap_s`) and whether the boot changed are now recorded (RA-O1; FILE(docs/probe/20261113_reg20/ops/common.sh:398)).

This departs from RUNBOOK §5 (FILE(agent/RUNBOOK.md:59)). See "Proposals".

## 13. The table's command

`AFTERSHOCK_UNSEAL=REG-20 .venv/bin/python -m analysis.k1 reg20`, from the repo root (RB5 (i); FILE(docs/probe/20261113_reg20/ops/final.sh:72)). Applied: the comment and the command no longer say `uv run`.

Around the command:
- **Before:** the folder set, the recheck and the slot lines (point 2, point 8).
- **After:** `mac_checks` again (RA4), the rc, and no `withheld:` line on stderr (RA-O2; FILE(docs/probe/20261113_reg20/ops/final.sh:73-77)).

## 14. The gate

**Headings.** All three of these headings must be in HEAD's `docs/decisions.md`:
- REG-19's [RESULT] (`([^0-9]|$)` keeps `REG-190` out);
- the owner's rulings, `^## <date> · [DECISION] (owner) REG-20 arm A operations: the owner's rulings` (RA5);
- after both, the start, `^## <date> · [DECISION] \((owner|delegate)\) REG-20 arm A starts: k1\.reg20_a_may_start passed([^0-9A-Za-z]|$)` (RA1; FILE(docs/probe/20261113_reg20/ops/common.sh:41)).

Draft 1's start pattern was a prefix. The sandbox now refuses three headings that matched it:
- "starts only after a new registration … failed";
- "starts nothing";
- "starts: … failed".

**Stop heading (RA-O3).** A heading `[DECISION|CORR|OPS] (owner|delegate)? REG-20 arm A (stops|is stopped)` after the start heading refuses every start (FILE(docs/probe/20261113_reg20/ops/common.sh:42)).

**The gate's one computation (RB5 (ii)).** RB5 (ii) asked for this text: "The gate is computed once, after REG-19's [RESULT] is committed, as `.venv/bin/python -m analysis.k1 reg20_a_may_start` from the repo root with mac_checks passing. No AFTERSHOCK_UNSEAL: it reads only REG-19's runs. Its stdout and stderr are saved under a stamp in docs/probe/20261113_reg20/ and committed at once, alone. The heading '… REG-20 arm A starts' is written only if that file reads 'may_start': True, and the entry quotes it verbatim."

**What happened instead, before this draft.**
- **The commit.** 3c8e5dc (2026-11-13T23:03Z) adds `docs/probe/reg20/gate_20261113T230307Z.txt`, one line, and `gate_err_20261113T230307Z.txt`, 0 bytes. The facts: `git show --stat`; `git cat-file -s`; a shape check `^{'k_closed': …, 'n': …, 'best_p': …, 'may_start': (True|False)}$` gave 1 of 1 lines. The value was not read by this author.
- **The command it used.** Its subject names `AFTERSHOCK_UNSEAL=REG-20 uv run python -m analysis.k1 reg20_a_may_start`, which is RUNBOOK's command (FILE(agent/RUNBOOK.md:63)). The subject is not evidence; the file has no record of its command.
- **How this differs from RB5 (ii):**
  - **The seal variable.** It was set to `REG-20` where RB5 (ii) says none. DERIVED: `ls runs | grep -cE '_l1pl350ol_|_s15_drift$'` gave 0 at 2026-11-13T23:12Z, so no REG-20 folder existed for that variable to unseal. A folder present at 23:03Z and gone at 23:12Z would need a deletion, which no rule allows (BELIEF).
  - **The interpreter.** It was `uv run`, not `.venv/bin/python`. BELIEF that the packages were the same: `uv.lock` is pinned, and `mac_checks` compares it with the pin's.
  - **The Mac-side checks.** Whether they passed before it, and whether the working tree's `docs/decisions.md` equalled HEAD's, is not recorded.
  - **The folder.** It is `docs/probe/reg20/`, not `docs/probe/20261113_reg20/`.
- **What still matches:** after REG-19's [RESULT]; once; committed alone, at once.

**Decision (delegate, draft).**
- The gate is not computed again, because the registration says "computed once" (FILE(docs/decisions.md:4051), FILE(docs/decisions.md:4168)).
- The scripts accept only the one committed file in `docs/probe/reg20/`.
  - It must read `'may_start': True` on its one line.
  - Its stderr file must be committed and hold no `withheld:` line.
  - Any second gate file there refuses the start (FILE(docs/probe/20261113_reg20/ops/common.sh:126)).
  - The scripts never call `reg20_a_may_start`. The sandbox fails if one tries.
- `gate.sh`, written for RB5 (ii), is withdrawn (a copy is in the review bundle).
- Whether the computation at 3c8e5dc is accepted is **question G** for the owner.

## 15. The control bits and failed checks in the queue output

As draft 1: accepted as inherent. Three things show in the queue output.
- **Control bits.** A control runs only after a cold-backlogged burst run, so a launched control shows that seed's bit.
- **Failed-check names (RA-O9).** `RUN … INVALID failed=…` shows names such as `no_errors/client_error` and `client_lag`. By T3 these correlate with a stuck run (FILE(docs/decisions.md:4103)). They are allowed reads, and the rerun rule needs them.
- **RECHECK and SET ASIDE lines.** They show the recomputed failed names (for example `recorder`), which can correlate with a backlog (BELIEF).

The answers that follow any stop are fixed before the first launch (RA5), so no later choice depends on these lines.

## 16. Arm B and its seal

**Who: the owner.** RB9's options, written in verbatim:
- "(a) If arm A gives `supports` or `supports_no_mechanism`, its outcome is reported in an entry whose heading does not lift the seal, for example "## <date> · [RESULT] K1 arm A, from REG-20's table (seal kept until arm B)". "[RESULT] REG-20" follows arm B. For any other arm A outcome, arm B never runs, and "[RESULT] REG-20" is written at once."
- "(b) A seal on `*_l1pl350ol_r2.5_*`, lifted by "[RESULT] REG-20 arm B", added after final.sh and after both batch 2s."
- "(c) Accept arm B unsealed."

**The freeze (RB9).** `analysis/withheld.py` and `analysis/load.py` are frozen by REG-21 and REG-22. So "after final.sh" (draft 1, line 299) is not enough: (b) also waits for both batch 2s.

## 17. Quiet hours

As draft 1: withdrawn, applied. No script reads the hour. The sandbox runs the whole queue with the clock at seven hours and at one value that is not an hour.

---

## For the owner, before the first launch

Each point is answered in `owner_rulings.txt`, one line `<point> <answer>`, committed with the owner's entry. The file now holds `unset` for every point, and the scripts refuse to start (RA5).

**2a. A run that today's checks change at its copy** (RB2 (iii), RA2)
- Options:
  - `keep`: keep it as its `checks.json` says and go on. The [RESULT] names the run and its recomputed `failed`.
  - `setaside`: a stored-valid run that is now invalid stays in the holding folder, out of `runs/`, and its config is rerun if an attempt remains (RA2 (b)).
  - `stop`: the queue stops and the owner answers keep or setaside each time.
  - `pin_head`: re-pin at or after `5ee6e38` (RA2 (a)). Arm A then cannot start until the pin changes by a reviewed commit, and the closed arm's harness differs from the open arm's.
- **Owner-proxy recommends `keep`.** As a second line that changes no label, the [RESULT] would also give the outcome with that seed counted `lost_open`. The proxy's reason: a rerun is impossible and a stop idles the GPU (RB2's recommendation). Draft 2 makes `setaside` possible, so that reason now holds only for runs already in `runs/`.
- **Rule F offers (a) or (b)**, and recommends neither one.
- **Risk of `setaside`, found in this draft:** two set-aside attempts of one burst config leave no invalid folder in `runs/`, so k1 reads `not_run` and the seed leaves n. That is a selection if A14 deaths correlate with a stuck run (BELIEF). In that case the queue stops after the second set-aside, and the owner settles it.

**6. A client error in an open burst run**
- Options:
  - (a) As REG-19: stop, and the owner answers each time. A refusal is a settle record, `not_run`.
  - (b) Stop, and answer by a rule fixed now. The delegate writes `rerun_ok` when the log's nofile is ≥ 4096 and the boot is unchanged; a second client error makes the seed `lost_open`. RB10's residual risk applies.
  - (c) Rerun automatically, without the stop. Not offered: it drops a registered stop.
- Recommendations: owner-proxy (b), with RB10's sentence; draft 1 (b). Rule F: rule before the launch (RA5), with no option preferred.

**7. An open burst run invalid twice, with an attempt that failed only setup checks** (RA3, RB7)
- Options:
  - `lost_open`: the delegate may settle it as REG-20's registered label (RB7).
  - `not_run`: the delegate may settle it as `not_run`, and the second run is held out of `runs/` (RA3's concern: a machine fault is not a stuck state).
  - `per_stop`: the owner rules each time.
- RB7 says the label is already registered, so `lost_open` is the reading that changes nothing. RA3 says a systematic setup failure could produce `refutes`.
- Both reviews say not to rule after the control bits are visible. That weighs against `per_stop` (rule A5).
- Draft 2 recommends **`not_run`** for this narrow class only. Its reason: `clean_git`, `kv_capacity` and `trigger` are decided before the burst ends or outside the server (RA3), so T3's reason for counting a loss as cold does not reach them (BELIEF).

**8. A lost attempt** (RA6, RB4 (iii))
- Options:
  - (a) A loss counts as one of the two attempts.
  - (b) A loss after a power-off is relaunched and not counted, at most twice per config; a loss without a reboot goes to the owner.
- Owner-proxy recommends (b), because under A18's reading (2) (a) would drop stuck seeds (BELIEF). Rule F says it is the owner's, and that each lost attempt's elapsed time and arm must be recorded (done).
- Draft 1 recommended (b).

**9. A control with both attempts invalid**
- Options: RB8's (a), (b) and (c), as in point 9. (c) is not possible without changing k1.
- Owner-proxy recommends (a). The seed is already cold for the test, and a third run decides only between `stuck_open` and `overload_open`.
- Rule F: rule before the launch, with no option preferred.

**16. Arm B and how arm A's result is headed**
- Options: RB9's (a), (b) and (c), as in point 16.
- Owner-proxy recommends (a), since no frozen file changes.

**G. The gate computed at 3c8e5dc** (new in draft 2; no line in `owner_rulings.txt`; answered in the owner's entry)
- Options:
  - (a) Accept it as the one computation, with its differences from RB5 (ii) stated in the start entry.
  - (b) Do not accept it. A new computation then needs its own decision, because the registration says "computed once".
- Draft 2 recommends (a). The unseal had no REG-20 folder to act on (DERIVED, point 14), and the other differences change no input (BELIEF).

---

## The freeze

REG-21 and REG-22 freeze these files from d9b324d until each batch 2 is computed or declared not computed (FILE(docs/decisions.md:9834); `docs/status.md`):
- `analysis/{__init__,c2,derived,floor,gate,k1,k3,k3w,load,margin,modelf,modelf_sim,stats,tables,withheld}.py`;
- `harness/{__init__,checks,config,env_snapshot,loadgen,recorder,run,trigger,workload}.py`;
- `pyproject.toml`, `uv.lock`, `.python-version`.

**Draft 2 changes none of them.** Every fix went into one of two places:
- **New files in `docs/probe/20261113_reg20/ops/`:** `recheck_one.py` (RA2, RB2), `owner_rulings.txt` (RA5), and the edited `common.sh`, `queue.sh`, `launch.sh`, `final.sh`, `test_sandbox.sh` and `test_control_due.py`. None is a `.py` file at the repository root, or in a folder named after a frozen module. `recheck_one.py` imports `harness.checks` and does not change it.
- **Proposals for a later decision:**
  - the RUNBOOK lines (RB6, RA-O7, RB5 (ii));
  - two open questions (RB14 (ii); draft 1's harness-death question);
  - an arm-B seal, if ruling 16 is (b).

## Timing (RB11)

RB11 asked to commit this decision "before the first `reg19_final_*` file exists". That is no longer possible: the file was committed in 047b95e (2026-11-13T22:56Z), before draft 2 was written.

As RB11 requires, the entry says so and names its points written after REG-19's table existed.
- **Written before:** every point of draft 1. Its text is at c8b482d, and both reviews of it are timed 2026-11-13T22:14Z–22:16Z.
- **Written after the table existed but before this author saw REG-19's outcome:** all of draft 2's script changes, the sandbox, the README and the rulings file.
- **Written after this author saw the subject line of REG-19's [RESULT]:**
  - this text;
  - the item map;
  - point 14's gate change: `GATE_DIR` and `GATE_FILE_RE` in `common.sh`, the withdrawal of `gate.sh`, and the sandbox's gate cases.

  Point 14's change follows from where the gate file is, not from its value.
- **Who else saw the outcome.** Whether the team lead or the owner saw REG-19's outcome before any of the rulings above is for their entries to state.

## Duties for the [RESULT] (RB14, and draft 2's additions)

- **(i) Rule H.**
  - Give k of n per arm, with the one-sided 95 % Clopper–Pearson upper bound from `stats.cp_upper`.
  - McNemar's p comes first, with Fisher's beside it (FILE(analysis/k1.py:220)).
  - Label the drift check a single seed, and each control a single run.
- **(ii) Arm differences.** The open arm's harness shell runs at 65536 open files, the closed arm's at the default 1024 (FILE(agent/RUNBOOK.md:28)). BELIEF that this does not matter: the closed arm held 149–226 sessions in service (FILE(docs/decisions.md:4089)). What vLLM 0.32.0 does with its own limit is unchecked (open question proposed below).
- **(iii) Where `supports` went out of reach.**
  - With all five closed runs cold, one open seed that is cold, unclear or partial gives McNemar p ≥ 1/16 > 0.05 (DERIVED from `k1.mcnemar_one_sided`: (5,0) gives 1/32 and (4,0) gives 1/16).
  - The [RESULT] names the first `CONTROL_DUE yes` or `unclear` line in the queue output, and states that no discretionary ruling was made after it.
  - All rulings are made before the first launch (RA5).
- **(iv) The judged code.** k1's module-level closure. The functions on reg20's path reach no import made inside a function (RB14 (iv), the proxy's AST trace).
- **(v) Ruling 2a.** Every `recheck_changed` line of `queue_done.txt`, with the recomputed `failed`. Under `keep`, add the second outcome line with that seed counted `lost_open`.
- **(vi) RA-O1 and RA6.** Each control's `gap_s` and boot line, and each `lost` line (arm, elapsed time, how it ended, counted or not).
- **(vii) RA-O8, for the owner's information.**
  - `supports` needs all five seeds `recovered_open`, since 4 of 4 gives 0.0625 (DERIVED).
  - After the first open seed that is not `recovered_open`, the remaining runs, about 3.5–6 GPU h, can move the outcome only between `refutes` and `inconclusive`.
  - The registration has no futility stop for arm A. Draft 2 adds none, because adding one would be the owner's change to the registration.
- **(viii) Question G's answer**, and the gate file quoted verbatim.

## Proposals for later decisions (not applied; outside the files this draft may edit)

1. **RUNBOOK (RB6, RA-O7, RB5 (ii)).**
   - RUNBOOK:48's "then deploy HEAD (§4)" becomes "then, if REG-20's gate passed, check the VM out at 1cface7 (REG-20 ops decision); otherwise deploy HEAD (§4)" (RB6, verbatim).
   - RUNBOOK:64, row 2a, gains "pin 1cface7; no worktree (ops decision point 12)" (RB6, verbatim).
   - RUNBOOK:63's gate command is now history (3c8e5dc). Mark the row done, citing 3c8e5dc and question G.
2. **The VM step (RB6, verbatim, into the decision):** "VM: push main to the VM's bare repo (RUNBOOK §4 step 1). On the VM, `git fetch origin && git checkout --detach 1cface77ca001cdf5d90de9313ddd4a3af4569a1`. Then `git rev-parse HEAD` equals the pin and `git status --short` is empty. Never while a run is in progress."
   - RUNBOOK:48 tells the agent to deploy HEAD after REG-19's [RESULT]. So the VM may now be at HEAD, which this draft cannot check.
   - The session probe and every launch stop on any other tree (FILE(docs/probe/20261113_reg20/ops/launch.sh:50)).
3. **Open questions** (`docs/open-questions.md`, by a later docs commit):
   - what vLLM 0.32.0 does with its own open-file limit (RB14 (ii));
   - whether a harness death correlates with a stuck open run (draft 1, "Not settled").
4. **Arm B's seal**, only if ruling 16 is (b), after `final.sh` and both batch 2s.

## Tests

- `zsh docs/probe/20261113_reg20/ops/test_sandbox.sh`, on a throwaway git repo and a fake VM: 350 of 350 passed (2026-11-13T23:18:23Z–23:31:21Z UTC), saved as `docs/probe/20261113_reg20/ops/sandbox_20261113T231823Z.txt`. It covers:
  - every RA and RB item that changes behaviour, except RB6;
  - the gate cases;
  - the three RA1 headings;
  - RB1's edit during a run, and RA4's edit during the call;
  - ruling 2a (`keep`, `setaside`, `stop`), 6 (a) and (b), 7 (`per_stop`, `not_run`, `lost_open`), 8 (a) and (b) with the cap, 9 (a) and (b);
  - RB3's settle paths, RA-O4, RB15;
  - `final.sh`'s folder set, the recheck before the table, the `withheld:` refusal and `mac_checks` after the table.
- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider docs/probe/20261113_reg20/ops/test_control_due.py`, 46 of 46 passed, saved as `test_control_due_20261113T231828Z.txt`. It holds draft 1's 35 tests and 11 new tests of `recheck_one.py`:
  - validity fields only;
  - `changed` computed as `analysis.recheck` computes it;
  - an error row;
  - refusal of a folder in `runs/` (a temporary stand-in);
  - one folder only;
  - no analysis module imported in its own process.

## Not settled by this draft

- **Points 2a, 6, 7, 8, 9, 16 and question G:** the owner's, before the first launch.
- **The pin's A14 risk (point 1).** A limit, not settled.
- **Which queue launched seed 15's closed run (point 4).** Not checked here (RA-O5, RB13).
- **The setup class (point 7).** A BELIEF fixed in advance. A failure outside it with a setup cause would still give `lost_open`.
- **Under 2a `setaside`, two set-asides of one burst config** read `not_run` in k1 (see 2a).
- **An edit made and undone within one `control_due.py` call** is not seen (point 5).
