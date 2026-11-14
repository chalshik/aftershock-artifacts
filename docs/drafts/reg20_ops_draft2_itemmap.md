# REG-20 arm A operations, draft 2: where each review item went

Written 2026-11-14 (Mac local; 2026-11-13 UTC) by a teammate agent, 0 GPU h, with `docs/drafts/reg20_ops_decision_draft2.md`.

**Sources:**
- rule F round 1, `docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft1-r1.md` (RA…);
- owner-proxy round 1, `docs/drafts/reviews-2026-11-13/proxy-reg20-ops-draft1.md` (RB…).

**Scripts:** `docs/probe/20261113_reg20/ops/`, working tree, not committed. Line numbers are those of the working tree when the sandbox output was saved.

**Rule for every item:**
- Required items are applied verbatim where they give exact text or code.
- Optional items are applied unless a reason is given.
- The owner's items become questions in the draft's section "For the owner, before the first launch".
- Where the two reviews conflict, both texts are kept and the stricter rule wins (merges M1–M10, below).

**The freeze.** No item touched a frozen file. The list is REG-21's and REG-22's: `analysis/{__init__,c2,derived,floor,gate,k1,k3,k3w,load,margin,modelf,modelf_sim,stats,tables,withheld}.py`, `harness/{__init__,checks,config,env_snapshot,loadgen,recorder,run,trigger,workload}.py`, `pyproject.toml`, `uv.lock`, `.python-version`. Each fix went to one of these destinations:
- **ops** (a new or edited file in `docs/probe/20261113_reg20/ops/`);
- **text** (the decision draft);
- **proposal** (a later decision; the file is outside what this draft may edit).

## Rule F, required

| Item | Where it went | Verbatim? Departures |
|---|---|---|
| RA1 start heading too loose | **ops:** `START_PAT` (common.sh:41) is anchored on `REG-20 arm A starts: k1\.reg20_a_may_start passed` + `([^0-9A-Za-z]\|$)`. **text:** proposed heading 3 and point 14. **Sandbox:** "starts only after a new registration … failed", "starts nothing", "starts: … failed", "passedover" | Pattern verbatim. |
| RA2 the checks in force never reach a label | **ops:** new `recheck_one.py`. `copy_verify` copies each run to the holding folder `STAGE` outside every `runs/` (common.sh:12), rechecks it there and applies ruling 2a before the run enters `runs/` (common.sh:543). No control decision without a recheck record (queue.sh:44). **text:** point 1's correction, point 2, 2a; owner question 2a offers (a) as `pin_head` and (b) as `setaside`. | Merged with RB2 (M1). RA2 (b) says a flagged run "stays off the Mac until after `final.sh`". Here it stays on the Mac but outside `runs/` (the holding folder), until REG-20's [RESULT]. `pin_head` refuses to start until `common.sh`'s pin is changed by a reviewed commit; the scripts do not re-pin themselves. |
| RA3 setup failures become `lost_open` | **ops:** `SETUP_CLASS=(clean_git kv_capacity trigger)` (common.sh:24). `decide` stops when both attempts are invalid and either failed only setup checks (common.sh:304, 341). **text:** point 7, owner question 7. **Sandbox:** kv_capacity twice, client_lag then trigger. | List verbatim. Merged with RB7 (M2). The stop is kept. The label is fixed before the launch by ruling 7, so under `lost_open` or `not_run` the delegate may write the settle record the ruling names. RA3's "stays the owner's" is met by the owner's advance ruling. |
| RA4 control decision on unchecked code | **ops:** `mac_checks` just before and just after `control_due.py` (queue.sh:45, :49). The decision is dropped if either fails. `final.sh` also runs it after the table (final.sh:73-75). **text:** point 5 and point 12's sentence. **Sandbox:** k1.py edited during the call. | RA4's second option, as worded. The worktree option was not taken. Remaining edge: an edit made and undone within one call (text, "Not settled"). |
| RA5 owner's points ruled before the first launch | **ops:** new `owner_rulings.txt` (every point `unset`). `rulings_ok` (common.sh:100) is called by `gate_in_log`. `RULINGS_PAT` (common.sh:40): the owner's rulings heading must come before the start heading. **text:** "Who decides", "For the owner". | Stricter than RA5's "could also require": required, and the file must be tracked and equal to its commit. |
| RA6 point 8 is the owner's | **text:** point 8, owner question 8. **ops:** `lost_count` (common.sh:206). Attempt records gain `arm` and `end <time> <how>` (launch.sh:58-59). `queue_done.txt` gains `lost <rid> arm … elapsed_s … end … counted …` (common.sh:467). | Merged with RB4 (iii) (M3). |
| RA7 scripts not the ones approved; false status lines | **text:** draft 2's Status. Draft 1's line 6 and README:3 are corrected. The [DECISION] is to name the implementing commit, `scripts_commit.txt` and the sandbox count after a rule F and an owner-proxy pass on the diff from c8b482d. **ops:** README rewritten. | Not applied: the commit and `scripts_commit.txt`, because the brief forbids committing. The review bundle carries the diff from c8b482d for round 2. |

## Rule F, optional

| Item | Where it went | Verbatim? Departures |
|---|---|---|
| RA-O1 seal-blob stop between a burst run and its control | **ops:** each control's `gap_s` and `boot same\|changed` in `queue_done.txt` (`gap_of`, common.sh:398). **text:** point 12, [RESULT] duty (vi). | The blob check is kept, as the stricter rule. Not taken: the worktree that would remove the stop (RA4's second option was chosen). REG-21's and REG-22's freeze bars commits to both seal files until both batch 2s. |
| RA-O2 `final.sh` enforces the folder set and stderr | **ops:** `final.sh:40-47` (the folder set of the eleven configs equals the copied set; nothing held or set aside); `final.sh:77` (`withheld:` refused). | Merged with RB4 (i) (M6). |
| RA-O3 owner overrules the start | **ops:** `STOP_PAT` (common.sh:42), checked in `gate_in_log`. | Wider than RA-O3's example: it also stops on `(delegate)` and on `[CORR]` or `[OPS]` headings with no author. More headings stop. |
| RA-O4 one record lifts every stop | **ops:** `lift_ok` (common.sh:191). It needs `lifts <failure>` per failure, plus `under` and `by`. **Sandbox:** client error plus manipulation. | — |
| RA-O5 item 4 mis-cited | **text:** point 4 takes RB13's verbatim sentence. | Departure: seed 15's own launch record is not cited, because it is in `state/`, which the brief forbids opening. Written as BELIEF until cited. |
| RA-O6 stale notes | **ops:** README rewritten. `DESIGN_NOTES.md` and `PIN_DECISION_DRAFT.md` get a "Superseded (2026-11-14)" paragraph at the top; the rest is kept as written. | — |
| RA-O7 RUNBOOK conflicts with the pin | **text:** "Proposals" 1–2 (RB6's text). **ops:** README's launch order, step 4. | RUNBOOK is outside the files this draft may edit, so it is a **proposal**. Merged with RB6 (M8). |
| RA-O8 for the owner's information | **text:** [RESULT] duty (vii). | No futility stop added: that would be the owner's change to the registration. |
| RA-O9 failed-check names visible | **text:** point 15. Draft 2 adds that the RECHECK and SET ASIDE lines show recomputed names too. | — |

## Owner-proxy

| Item | Where it went | Verbatim? Departures |
|---|---|---|
| RB1 code check before a control decision | **ops:** queue.sh:58, `mc=$(mac_checks) \|\| stop "Mac-side check failed before turn $turn: ${mc##*$'\n'}"`, as the loop's first line. **Sandbox:** gate.py edited during seed 15's run, QUEUE STOP, no CONTROL line. **text:** point 12, line 248's replacement. | Line and sentence verbatim. The sentence gains RA4's after-check as an added clause (M4). |
| RB2 (i) line 75's text | **text:** point 2, quoted verbatim. | Verbatim, followed by a note (M1): "It cannot be rerun" holds only for a run already in `runs/`; draft 2 rechecks before that. The cited "common.sh:139" is now common.sh:273. |
| RB2 (ii) port `recheck_ok` with both guards; count from `copied_*`; call after each copy, before `control_due`, and in final.sh | **ops:** `recheck_guards` (common.sh:492, ops_r3's two guards); `recheck_one` and `recheck_apply` (common.sh:498, :510); `final.sh:52-70` (`analysis.recheck` on both patterns, n equal to the copied count, changed set equal to the queue's `kept` lines). **Sandbox:** keep, setaside, stop, error, failing script, three guard cases, the final mismatch. | Departure: at each copy the recheck uses the new `recheck_one.py`, which applies `harness.checks.run_checks` to a holding-folder path. `analysis.recheck` reads only `runs/`, and RA2 (b) needs the check before `runs/`. `analysis.recheck` itself runs before the table. Review error: RB2 cites ops_r3 common.sh:204-205; the guards are at 206-207. |
| RB2 (iii) new owner point 2a | **text:** point 2a, owner question 2a. **ops:** ruling `2a`. | Options widened by RA2 (M1). |
| RB3 a path for "no rerun" | **ops:** `settle_<rid>.txt` with `label not_run\|control_not_run` (common.sh:306-334). Slot lines `s<n> not_run <rid>` and `s<n> <rid> CONTROL_DUE yes control_not_run <rid>`, accepted by final.sh:32. **Sandbox:** owner refuses a rerun, control_not_run, drift_not_run. | Extended: `drift_not_run`, and `lost_open` for RA3's case (M2). Who may write each label follows the rulings. |
| RB4 (i) final.sh refuses folders without a copy record or checks.json | **ops:** final.sh:37-47. | Stricter (M6): the folder set must equal the copied set. |
| RB4 (ii) decision text on lost folders | **text:** point 8, verbatim. | — |
| RB4 (iii) implement 8(b) | **ops:** `lost_count`, `MAX_POWER_LOSSES=2`. **Sandbox:** 8(a), 8(b), a third uncounted loss. | Departure (M3): RA6 makes point 8 the owner's, so 8(b) is active only under the owner's ruling. |
| RB5 (i) `$PY` in final.sh | **ops:** final.sh:8 (comment) and :72. **Sandbox:** no `uv run` call. | Verbatim. |
| RB5 (ii) gate computed once, text for point 14 | **text:** point 14 quotes it verbatim as the text asked for, then states what happened. | **Overtaken by events.** Commit 3c8e5dc had already computed the gate, with RUNBOOK:63's command (`AFTERSHOCK_UNSEAL=REG-20 uv run …`), into `docs/probe/reg20/`. `gate.sh` was written for RB5 (ii), then withdrawn before any use (a copy is in the review bundle, `withdrawn/gate.sh`). `gate_in_log` now reads the committed file in `docs/probe/reg20/` (common.sh:43-44, :126). New owner question G. |
| RB6 the VM step, RUNBOOK:48 and :64, README and draft status lines | **text:** "Proposals" 1–2 (VM step verbatim). **ops:** README's status and launch order. | RUNBOOK edits are **proposals**: RUNBOOK is outside the files this draft may edit. README:3, :93 and :96 and draft line 6 are rewritten. |
| RB7 replace line 180 | **text:** point 7, verbatim. | Merged with RA3 (M2). |
| RB8 point 9's options | **text:** point 9 and owner question 9, verbatim. **ops:** ruling 9; `attempt_ok` and `control_not_run` paths. | — |
| RB9 point 16's options | **text:** point 16 and owner question 16, verbatim. | — |
| RB10 residual risk under 6(b) | **text:** point 6, verbatim. | — |
| RB11 commit before REG-19's table | **text:** "Timing". | Cannot be met: the first `reg19_final_*` file is in 047b95e, before draft 2. The section says so and names the points written after. |
| RB12 deviation from PROTOCOL §5 | **text:** point 1. | Verbatim in substance (three sentences). |
| RB13 point 4's citation | **text:** point 4, verbatim. | The four citations were checked (launch3.sh:27, launch4.sh:31, launch5.sh:32, launch6.sh:36): no `ulimit`. Which queue launched seed 15 is not checked (state/ is forbidden). |
| RB14 [RESULT] duties (i)–(iv) | **text:** "Duties for the [RESULT]". | (ii)'s open question is a **proposal**. |
| RB15 `nofile_ok` record | **ops:** common.sh:286 (a restart uses the run only with the record); queue.sh:84 (the stop names it). **Sandbox:** low log line; no-run-id restart. | — |

## Merges of the two reviews

- **M1, RA2 against RB2.** RA2 (b) wants the run checked outside `runs/` before it enters, so it can be set aside. RB2 (i) says the run cannot be rerun, and the answer is keep or stop. RB2 (ii) says recheck after each copy, before `control_due`.
  - **Merge:** recheck in the holding folder after the VM copy and before `runs/`. That is "after each copy" and "before the run is on the Mac's `runs/`" at once.
  - Ruling 2a carries every answer: `keep` (RB), `setaside` (RA2 b), `stop` (RB2 i), `pin_head` (RA2 a).
  - RB2 (i)'s text is kept verbatim, with a note.
- **M2, RA3 against RB7.** RA3 says two invalid attempts with a setup-only failure should stop, not give `lost_open`. RB7 says the registered label is `lost_open` for any check, and the owner decides only rerun or not.
  - **Merge:** RA3's stop is kept (stricter). The answer is fixed before the launch by ruling 7: `lost_open` (RB7), `not_run` (RA3) or `per_stop`.
  - RB7's sentence is verbatim. Both reviews' A5 concern weighs against `per_stop`.
- **M3, RA6 against RB4 (iii).** RA6 says point 8 is the owner's. RB4 (iii) says it is inside the delegation and approves 8(b).
  - **Merge:** the owner's (stricter). 8(b) is implemented and used only under the owner's ruling.
- **M4, RA4 and RB1.** Both are applied: the per-turn check (RB1) and the before-and-after check around the call (RA4).
- **M5, RA5 and RB's "quick" points 6, 9, 16.** RA5's timing (before the first launch) applies to every owner point.
- **M6, RA-O2 and RB4 (i).** Both are applied: set equality (RA-O2) plus a copy record and `checks.json` for each run (RB4 i).
- **M7, RA-O5 and RB13.** RB13's verbatim sentence. RA-O5's own launch record is not cited (state/ forbidden).
- **M8, RA-O7 and RB6.** RB6's text as the decision text; RUNBOOK as a proposal.
- **M9, RA1 and RB5 (ii).** RB5 (ii) says "the heading '… REG-20 arm A starts'". RA1 fixes the full words. Both are applied.
- **M10, RA-O1's worktree against RA4's two options.** RA4's second option was chosen, so RA-O1's stop remains. It is mitigated by the freeze and recorded by `gap_s`.

## Found wrong in the reviews

1. **RB2 (ii)** cites ops_r3 common.sh:204-205 for the two guards. They are at FILE(docs/probe/20261113_reg19/ops_r3/common.sh:206-207).
2. **RB2 (i)**'s "It cannot be rerun" assumes draft 1's order (copy into `runs/` before any recheck). RA2 (b) shows the other order, which draft 2 uses.
3. **RB5 (ii)** asked for a different gate command but left RUNBOOK:63's command in place (FILE(agent/RUNBOOK.md:63)), and that command is the one used at 3c8e5dc. Neither review asked for RUNBOOK:63 to change.
4. **RB13**'s four citations are correct. That seed 15's closed run was launched by `docs/probe/20261111_reg19/ops/` is unchecked here (RA-O5 had the same gap).
5. **Not wrong but incomplete, RA2 (b)'s set-aside path:** two set-aside attempts of one burst config leave no invalid folder in `runs/`, so k1 reads `not_run`, not `lost_open`. This is a selection risk the reviews do not mention. Draft 2 states it under 2a; the queue stops after the second set-aside.
6. **RA-O1**'s three commits (72fafb5, ef4dc4e, 69ffedd) are confirmed (`git log 1cface7..HEAD -- analysis/withheld.py analysis/load.py`).

## Found wrong in draft 1

1. Line 6, "They are not committed": false, c8b482d (RA7).
2. Line 12, "Until the owner rules, the scripts stop at that point and wait": withdrawn (RA5).
3. Line 54, "(c) … still applies today's checks to every run": true for the stop only, not a label (RA2).
4. Line 75, "found while its rerun is still possible": false under draft 1's order (RB2).
5. Line 109, seed 15's run "under ops_r3's launch command": mis-cited (RA-O5, RB13).
6. Line 180, the label left open: already registered (RB7).
7. Line 248, "Every launch, copy and table first checks": false for the copy and the control decision (RA4, RB1).
8. Line 278, "the heading … must carry these exact words", while the pattern was a prefix (RA1).
9. Summary row 8, "delegate": the owner's (RA6).
10. Point 13: not applied in draft 1's scripts (`uv run`), now applied (RB5 i).
11. **Found by draft 2:** k1 can give `not_run` only with at most one invalid folder of the config in `runs/`. Draft 1's refusal paths (6(a), 7) would have copied both runs and read `lost_open`. Draft 2 holds the second run in the holding folder (point 7).

## The agent's own errors in this draft's work, fixed before any saved output

- Four sandbox checks piped the case output through `print` inside `sh -c`. `print` is a zsh builtin. Two of the checks failed, and two passed without testing anything: "no CONTROL line" in RB1's case, and "not shown" in RA4's case.
- All four were rewritten as zsh functions (`has`, `lacks`). All pass on the saved run, `sandbox_20261113T231823Z.txt`.
- The first full run (357 passed, 2 failed) is not saved in the repo.

## Sandbox and tests

- `test_sandbox.sh`: 350 of 350, `docs/probe/20261113_reg20/ops/sandbox_20261113T231823Z.txt`.
- `test_control_due.py`: 46 of 46, `docs/probe/20261113_reg20/ops/test_control_due_20261113T231828Z.txt` (35 from draft 1, 11 new for `recheck_one.py`).
