# REG-20 arm A operations: decision draft 3

**Status.** Draft 3. It is not reviewed, nothing is decided, and nothing is committed or launched.
- **Written:** 2026-11-14, about 02:20 to 02:55 UTC, by a draft-writer subagent of session 8c5f8396, at 0 GPU h.
- **Not touched:**
  - The VM was not contacted, and no ssh was run.
  - Under `runs/`, only one reported REG-19 folder was measured, with `du -sk` and a file count (PROBE(docs/drafts/reg20_ops_r3/disk_probe_20261114.txt)).
  - No `state/` folder, queue output, sealed folder or E1 run was opened.
- **Draft 2's scripts** (RC8, verbatim): "are committed in 56820bd ("[OPS] Drafts for review, none approved"), with `owner_rulings.txt` all `unset`, so they refuse to start (FILE(docs/probe/20261113_reg20/ops/common.sh:116)). The [DECISION] names the commit that holds the scripts after round 2's items are applied, with `scripts_commit.txt` and its sandbox count, and the diff from 56820bd to it gets the review RA7 asks for."
  - HEAD's ops folder is still 56820bd's. DERIVED: `git diff --stat 56820bd HEAD -- docs/probe/20261113_reg20/ops` is empty (PROBE(docs/drafts/reg20_ops_r3/git_facts_20261114.txt)).
- **Draft 3's script changes** are patches against 40948ba. None is applied anywhere.
  - `docs/drafts/reg20_ops_r3/ops_draft3.patch`: the scripts, the sandbox, the tests, the README, and the comment of the rulings file.
  - `docs/drafts/reg20_ops_r3/owner_rulings_rd2.patch`: RD2's six values. It is for the rulings entry's commit only.
  - `docs/drafts/reg20_ops_r3/runbook_heading1.patch`: the RUNBOOK edits, for heading 1's commit.
  - The sha256 of every patched file: `docs/drafts/reg20_ops_r3/SHA256SUMS.txt`.
  - The commits from 40948ba to HEAD (5f9f442) touch no patched file (DERIVED, git_facts). Each patch applies cleanly to a fresh `git archive` of 40948ba and of 5f9f442, and the result is byte-equal to the tested scratch files (PROBE: the writer's build script with `cmp`; SHA256SUMS.txt).
- **Round 2 of review:**
  - rule F: NOT READY, with RC1–RC8 required and RC-O1–RC-O12 optional (`docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft2-r2.md`);
  - owner-proxy: APPROVE, with RD1–RD8 before the first launch and RD9–RD10 later, and with picks 2a `setaside`, 6 (b), 7 `lost_open`, 8 (b), 9 (a), 16 (a) and G (a) (`docs/drafts/reviews-2026-11-13/proxy-reg20-ops-draft2.md`).
  - A reject from either is binding (FILE(docs/decisions.md:4234)). Draft 3 therefore goes to rule F round 3 and to an owner-proxy delta.
- **RD1 versus this diff.** RD1 calls its own change "the only script change" and says "Anything else needs a new round". Draft 3's diff holds more:
  - RC2's and RC3's patches;
  - RC-O2, RC-O3, RC-O10, RC-O11 and RD-O1;
  - RC6 (ii);
  - point 18's check.

  The owner-proxy delta is that new round.
- **The item map:** `docs/drafts/reg20_ops_decision_draft3_itemmap.md`. It gives every RC, RC-O, RD and RD-O item, where it went, each departure from the reviewer's words, and the resolution wherever two items meet.
- **Tests** run on fakes only, in a scratch tree made of 40948ba with ops_draft3.patch applied:
  - `test_sandbox.sh`: 428 of 428 passed, exit 0 (PROBE(docs/drafts/reg20_ops_r3/sandbox_20261114T023449Z.txt));
  - `test_control_due.py`: 47 of 47 passed, exit 0 (PROBE(docs/drafts/reg20_ops_r3/test_control_due_20261114T024844Z.txt)).
- **Line numbers.** A citation marked † gives the line in the file as patched by ops_draft3.patch. An unmarked FILE citation gives the line at HEAD.

**What changed around this draft since draft 2.** Commit subjects are not evidence (rule B); where only a subject is known, the statement is tagged BELIEF.
- **REG-21's and REG-22's freezes have ended.**
  - Both batch 2s are computed (FILE(docs/decisions.md:16571), FILE(docs/decisions.md:16798)).
  - REG-21's entry says its freeze ends (FILE(docs/decisions.md:17012)).
  - REG-22's freeze has the same end (FILE(docs/decisions.md:4748)).
- **E1 was approved by the delegate** (FILE(docs/decisions.md:18286)).
  - That entry states that E1 is first (FILE(docs/decisions.md:18433)).
  - The VM was checked out at E1's commit ce5f842 (FILE(docs/decisions.md:19394)).
  - E1's queue started at 02:15:09 UTC (BELIEF: the subject of commit 40948ba; the queue's output was not opened).
- **Two seal rows for other items are drafted:**
  - REG-24's (FILE(docs/drafts/reg24_confirm_draft1.md:418-421));
  - D1's, a row `("D1", "*_burst_l1pl350cl_r2.0_w3000_s1[5-9]_cap", "[RESULT] D1")` (FILE(docs/drafts/d1_r1/withheld.patch:4), commit 5f9f442).

**Proposed headings.** Three entries, in this order in `docs/decisions.md`:
1. `## 2026-11-1x · [DECISION] (delegate) REG-20 arm A operations: the scripts in docs/probe/20261113_reg20/ops/ at <commit>; the pin 1cface7, each run rechecked by the checks in force before it enters runs/ or a control decision; the drift run after seed 17's control; the control decision by control_due.py between two code checks; the gate computed once (3c8e5dc); E1 first, arm A after E1's end entry, the VM moved back to the pin by vm_checkout.sh; the arm A hold; six points ruled before the first launch`
2. `## <date> · [DECISION] (delegate) REG-20 arm A operations: the rulings on the owner's points`.
   - It is written as (delegate), under the delegation (FILE(docs/decisions.md:4233)), with owner-proxy round 2 and its delta, and with rule F rounds 2 and 3.
   - It quotes `owner_rulings.txt` and is committed in the same commit as that file (RC2).
   - The owner may write `## <date> · [DECISION] (owner) REG-20 arm A operations: the owner's rulings` in its place.
   - Its text is under "Texts for headings 2 and 3".
3. `## <date> · [DECISION] (delegate) REG-20 arm A starts: k1.reg20_a_may_start passed`.
   - It is written only if the gate file reads `'may_start': True`.
   - It quotes the file verbatim (RD7).

**What the scripts check.** RD6's sentence, verbatim: "The scripts start only when HEAD holds REG-19's [RESULT], the rulings heading and, after both, the start heading, with no stop heading after the start (common.sh `gate_in_log`). They do not check heading 1."

Draft 3 adds three conditions:
- HEAD holds E1's end entry, and E1's queue lock is absent (`e1_ended`, point 18);
- a delegate's rulings heading counts only once, and only as the first rulings heading (RD2);
- the last commit that changed `owner_rulings.txt` adds a rulings heading (RC2).

**Who decides.**
- **The delegate** decides what implements REG-20 as registered. The delegation covers "registrations and GPU runs; reruns under registered stopping rules" (FILE(docs/decisions.md:4233)).
- **Points 2a, 6, 7, 8, 9, 16 and question G** are ruled before the first launch (RA5).
  - They are ruled by the delegate under the delegation (FILE(docs/decisions.md:4233)), with owner-proxy round 2 and its delta, and rule F rounds 2 and 3 (RD6, with round 3 added).
  - The owner may overrule any of them (FILE(docs/decisions.md:4236)). After the first rulings entry, a ruling changes only with an owner's entry (RD2). The scripts enforce this (`rulings_ok`, `gate_in_log`; points 14 and 18).
  - The scripts refuse to start while any point reads `unset` (FILE(docs/probe/20261113_reg20/ops/common.sh:116)).
- **Point D, the VM's disk,** is the owner's. Freeing space on the VM means deleting files, and "deleting anything" is not delegated (FILE(docs/decisions.md:4235)).

## Summary

| # | Point | Draft 3 | Who |
|---|---|---|---|
| 1 | Pin | `1cface7`, with the checks in force applied to every run | delegate |
| 2 | Checks in force | applied to each run in the holding folder, before it enters `runs/` and before any control decision; again over `runs/` before the table; all of `harness/` held to `5ee6e38` (RD-O1) | delegate |
| 2a | A run those checks change | a ruling; the pick is `setaside` | delegate (RD2); the owner may overrule |
| 3 | The drift run's place | after seed 17's burst run and its control | delegate |
| 4 | The drift run's open-file limit | recorded, not raised | delegate |
| 5 | Control decision | `control_due.py`, between two code checks | delegate |
| 6 | Client error in an open-loop run of arm A (a burst run or its control) | a ruling; the pick is (b) | delegate (RD2) |
| 7 | Other stop-and-ask failures, and RA3's setup case | stops; ruling 7, pick `lost_open`; the mixed case is `lost_open` (RC3); the systematic-fault stop (RD3 (ii)) | delegate |
| 8 | A lost attempt | a ruling; the pick is (b) | delegate (RD2) |
| 9 | A control with both attempts invalid | a ruling; the pick is (a) | delegate (RD2) |
| 10 | Invalid runs copied; held and set-aside folders | through the holding folder; custody as RC6 and RD8 | delegate |
| 11 | Open-file limit in the launching shell | as draft 2 | delegate |
| 12 | Where the analysis runs | as draft 2; the arm A hold replaces the freeze | delegate |
| 13 | The table's command | as draft 2 | delegate |
| 14 | The gate and the headings | RD1's regex, RC2, RD2; the stop heading (RC-O3, "ended by a stop"); the one gate file; question G, pick (a) | delegate |
| 15 | Bits visible in the queue output | accepted; the per-stop answers are listed (RC4) | delegate |
| 16 | Arm B and its seal | a ruling; the pick is (a) | delegate (RD2) |
| 17 | Quiet hours | withdrawn, applied | owner, already decided |
| 18 | Order with E1 | E1 first; arm A after E1's end entry and with E1's lock gone; `vm_checkout.sh` back to the pin; arm A's end entry defined | delegate |
| D | The VM's disk | arm A's planned runs do not fit (DERIVED) | **owner** |

---

## 1. Pin

**Options** (as draft 2):
- (a) `1cface7`;
- (b) HEAD, or any commit at or after `5ee6e38` (the A14 fix);
- (c) `1cface7`, plus the checks in force applied to every run (point 2).

**Evidence** (as draft 2, with draft 3's checks):
- Each open config "extends its REG-19 partner and sets `workload.sessions.closed_loop: false`, the only change" (FILE(docs/decisions.md:4052)).
- The harness at `1cface7` is byte for byte REG-19's harness at `a7bb77a`. DERIVED: `git diff a7bb77a 1cface7 -- harness/` is empty (draft 2; owner-proxy round 1).
- `1cface7` is an ancestor of HEAD and of E1's ce5f842 (DERIVED, git_facts).
- `uv.lock` has the same blob, `8b1c04b4…`, at the pin, at ce5f842 and at HEAD (DERIVED, git_facts).
- `configs/defaults.yaml`, `.python-version`, `tools/manifest.py`, `pyproject.toml` and `uv.lock` equal the pin's at HEAD (DERIVED, git_facts).
- The harness at ce5f842 differs from the pin's in four files (DERIVED, git_facts: `git diff --stat 1cface7 ce5f842 -- harness/`). This is A14's change (FILE(docs/decisions.md:4204)): `harness/` at ce5f842 equals `5ee6e38`'s (DERIVED, git_facts).
  - So E1's runs are on `5ee6e38`'s harness and arm A's are on the pin's.
  - The move back (point 18) restores REG-19's harness on the VM.

**Recommendation: (c),** for draft 2's reasons:
- (b) puts a different harness in the open arm, against "the only change" (FILE(docs/decisions.md:4052));
- the owner made the same choice for REG-19 (FILE(docs/decisions.md:4284)).

**Correction of draft 1 (RA2), the limit (BELIEF), and the deviation from PROTOCOL §5 (RB12):** as draft 2, unchanged (FILE(docs/drafts/reg20_ops_decision_draft2.md:81-91)).
- At `1cface7` a recorder death is detected, not prevented (FILE(docs/decisions.md:4202)).
- REG-20's stored checks lack A14's coverage checks (FILE(PROTOCOL.md:78-79)).

**Who:** the delegate. The registration names no commit (FILE(docs/decisions.md:4169)).

## 2. The checks in force: when they are applied

As draft 2 (FILE(docs/drafts/reg20_ops_decision_draft2.md:97-119)). Each finished run, valid or invalid, goes through five steps:
1. It is copied into the holding folder `<repo's parent>/aftershock-reg20-holding`, outside every `runs/` (FILE(docs/probe/20261113_reg20/ops/common.sh:12)).
2. Its sha256s are compared with the VM's.
3. `recheck_one.py` applies `harness.checks.run_checks`, as in force since `5ee6e38`, read-only.
4. Ruling 2a is applied.
5. The run is moved into `runs/` and verified again. No control decision is made on a run without its recheck record (FILE(docs/probe/20261113_reg20/ops/queue.sh:44)).

Before the table, `final.sh` runs `analysis.recheck` over `runs/` and must find the queue's changed set (FILE(docs/probe/20261113_reg20/ops/final.sh:58-70)). RB2 (i)'s text and draft 2's additions to it are kept verbatim (draft 2, point 2).

**Changed in draft 3 (RD-O1).**
- `recheck_guards` also holds all of `harness/` in the working tree to `5ee6e38`, the commit whose `harness/checks.py` the recheck runs (FILE(docs/probe/20261113_reg20/ops/common.sh:526-527)†).
- The reason: the recheck's import closure holds `harness/{__init__,checks,config,workload}.py` (PROBE(docs/drafts/reg20_ops_r3/closure_20261114.txt)). Draft 2 held only `checks.py` to that commit, and the other three only to HEAD (proxy round 2, judged item 1 (i)).
- So a commit to `harness/config.py`, which passed silently in draft 2, now stops the copy before the recheck. The sandbox case is "RD-O1: a commit to harness/config.py (in the recheck's closure, not in mac_checks) stops the recheck".
- Today's whole `harness/` equals `5ee6e38`'s (DERIVED, git_facts: `git diff --stat 5ee6e38 HEAD -- harness/` is empty).

**Changed in draft 3 (RC6 (ii)).** When a run is held or set aside, `copy_verify` writes its per-file sha256 list beside it as `<holding folder>/<run id>.sha256`. It then prints `SHA256 LIST <path> sha256 <sha256 of the list>` for the [OPS] entry that names the record (FILE(docs/probe/20261113_reg20/ops/common.sh:592-599)†). See point 10.

**Registration:** unchanged. The checks add stops, and they change no `checks.json`, label or verdict code.

## 2a. A run that today's checks change

How the scripts apply each answer is as draft 2 (FILE(docs/drafts/reg20_ops_decision_draft2.md:125-131)), with RC5's change to the `setaside` bullet:
- **`keep`:** they print the RECHECK line, keep the run as its `checks.json` says, and go on.
- **`setaside`:** this applies to a stored-valid run that is now invalid. The scripts write `state/setaside_<rid>.txt` and `<holding folder>/<rid>.sha256`, keep the run in the holding folder, and stop. Then (RC5, verbatim): "and stop; a restart reruns its config. A later stop with the attempts spent can be settled only `not_run` (or by a third attempt); see owner question 2a." Any other change is kept.
- **`stop`:** they stop until the owner writes `state/recheck_ok_<rid>.txt` with `answer keep|setaside`.
- **`pin_head`:** they refuse to start until `common.sh`'s pin changes by a reviewed commit.

A folder that today's code cannot read stops the queue under every answer.

**The ruling, RD2:** `setaside`. The reasons are owner-proxy round 2's (its section "2a: `setaside`"):
- PROTOCOL §5 says invalid runs are "kept, never counted, and rerun unchanged" (FILE(PROTOCOL.md:74-84));
- `keep` would count a run that PROTOCOL calls invalid;
- `stop` idles the GPU while the owner is away.

## 3. The drift run's place

As draft 1 and draft 2: after seed 17's burst run and its control, when one is due (FILE(docs/decisions.md:4053-4054)).

## 4. The drift run's open-file limit

As draft 2 (b): recorded, not raised. RB13's sentence is kept verbatim (FILE(docs/drafts/reg20_ops_decision_draft2.md:141)).

**RC-O5 replaces draft 2's open question (its line 143), verbatim:** "Every REG-19 launch script on file starts the harness with the same command and no `ulimit`: launch3.sh:27, launch4.sh:31, launch5.sh:32, launch6.sh:36 (all in `docs/probe/20261111_reg19/ops/`), `_to_delete/docs/probe/20261113_reg19/ops/launch7.sh:41` and `launch8.sh:35`, `docs/probe/20261113_reg19/ops_r3/launch.sh:51` (PROBE: `grep -l ulimit` over the three folders finds none, rule F round 2). Whichever of them launched seed 15's closed run, it set no limit; only a launch by hand outside these scripts would differ (BELIEF that there was none)."

## 5. The control decision

As draft 2 (FILE(docs/drafts/reg20_ops_decision_draft2.md:145-155)).
- `control_due.py` prints one line from `k1.cold_backlogged(run)["cold_backlogged"]`.
- `mac_checks` runs immediately before and immediately after the call. If either fails, the decision is dropped.
- `unclear` runs no control.
- One edge stays open: an edit made and undone within one call is not seen. The arm A hold (item 2) forbids the edit itself.

## 6. A client error in an open-loop run of arm A (a burst run or its control)

The wording is RD6's: "an open-loop run of arm A (a burst run or its control)". The scripts already apply point 6 to both (FILE(docs/probe/20261113_reg20/ops/common.sh:195-197), FILE(docs/probe/20261113_reg20/ops/launch.sh:29)). Draft 2's "an open burst run" was narrower than the code.

As draft 2 otherwise (FILE(docs/drafts/reg20_ops_decision_draft2.md:161-166)):
- RA-O4's `lifts` line;
- RB3's refusal path;
- under (b), the delegate's record only with the launch log's nofile ≥ 4096 and the same boot;
- RB10's residual-risk sentence, verbatim.

**The ruling, RD2:** (b). The delegate's answers at these stops are RD3 (iii) (see "Texts for headings 2 and 3").

## 7. A burst that did not fill the pool, a wrong limit, a second heat failure, and setup failures

**Stops** (as draft 2):
- `manipulation`;
- `power_limit`;
- a second `gpu_steady` among REG-20's runs.

A rerun needs the owner's `rerun_ok` record that names the failure (RA-O4). RB7's text is kept verbatim (FILE(docs/drafts/reg20_ops_decision_draft2.md:177)).

**RA3, as draft 2.**
- When both attempts of an open burst run are invalid and either attempt failed only checks of the setup class, the queue stops. It does not give `lost_open` (FILE(docs/probe/20261113_reg20/ops/common.sh:304)).
- The class is `clean_git`, `kv_capacity` and `trigger` (FILE(docs/probe/20261113_reg20/ops/common.sh:24)). It is a BELIEF, fixed before any run.
- A settle record then decides.

**RC3 replaces "Ruling 7 says which label the delegate may write, or that each case goes to the owner.", verbatim:** "Ruling 7 says which label the delegate may write, or that each case goes to the owner. Under `not_run` the delegate may write `not_run` only when every invalid attempt failed only setup checks; when one attempt failed a check outside the class (for example `client_lag`, which T3 ties to a stuck run, FILE(docs/decisions.md:4103)), the delegate writes `lost_open`, REG-20's registered label (RB7)."
- The code is rule F's patch, unchanged: `setup_all` (FILE(docs/probe/20261113_reg20/ops/common.sh:335)†), and the `not_run` and `lost_open` branches (FILE(docs/probe/20261113_reg20/ops/common.sh:345)†, FILE(docs/probe/20261113_reg20/ops/common.sh:352)†).
- **`not_run` and k1** (as draft 2): for k1 to read `not_run`, the record names the run already copied, and the second run is held in the holding folder (`state/held_<rid>.txt`, now with its `.sha256` list) until REG-20's [RESULT] (FILE(analysis/k1.py:286)).

**The ruling, RD2:** `lost_open`. The reasons are owner-proxy round 2's:
- it is the registered label (FILE(docs/decisions.md:4067));
- the mixed case is the T3 kind;
- RD3 (ii)'s stop meets RA3's systematic case.

Under `lost_open`, RC3's narrowing of `not_run` has no effect. It stays in the code for an owner who rules `not_run`.

**RD3 (ii), the systematic-fault stop.** It is kept by hand and is written into the rulings entry verbatim (see "Texts for headings 2 and 3"). RD-O2, which would make it mechanical, is not taken. Draft 3's only mechanical changes are the ones the two reviews tested or asked for (item map).

**RC4's stricter rule, added here and to the README's "Records", verbatim:** "Each hand-written record is named in an [OPS] entry committed when it is written; that commit's time is the record's time."

**Registration:** unchanged under `lost_open`.

## 8. A lost attempt (no `checks.json`)

As draft 2 (FILE(docs/drafts/reg20_ops_decision_draft2.md:189-206)):
- `lost_count`;
- at most `MAX_POWER_LOSSES` = 2 uncounted losses per config;
- a loss without a reboot, or with an unknown launch boot, needs the owner's record only;
- each lost run's arm, elapsed time and end are recorded;
- RB4 (ii), verbatim.

**The ruling, RD2:** (b). The delegate's answer is RD3 (iv).

## 9. A control with both attempts invalid

As draft 2 (FILE(docs/drafts/reg20_ops_decision_draft2.md:208-221)), with RB8's options (a), (b) and (c) verbatim.

**The ruling, RD2:** (a). The delegate's answer is RD3 (v), a delegate's `attempt_ok_<cfg>_3.txt`. A third failure stops arm A for the owner.

## 10. Invalid runs are copied to the Mac; held and set-aside folders

As draft 2: each run goes through the holding folder first (point 2).

**RC6, added as point 10a.** The text is verbatim, with two changes, each marked [·]:

> **Held and set-aside folders.** A folder kept in the holding folder is raw data outside `runs/`, the manifest and the second copy of `runs/`. Until a decision names its permanent place: (i) its VM copy is not removed, and no VM copy of any folder of the eleven configs is removed before [· REG-20's [RESULT] (RD8, the stricter end) ·] (`decide` stops on a Mac folder the VM does not list, FILE(docs/probe/20261113_reg20/ops/common.sh:275-276)); (ii) when it is held or set aside, its per-file sha256 list is written beside it as `<holding folder>/<run id>.sha256`, and that list's own sha256 is quoted in the [OPS] entry that names the record [· (written by `copy_verify` and printed as its `SHA256 LIST` line, FILE(docs/probe/20261113_reg20/ops/common.sh:592-599)†) ·]; (iii) its run id is listed in `manifests/pending_copy.txt` before any doc names it, with the holding path in the [OPS] entry; (iv) the [RESULT] lists each such folder with its record. A set-aside folder whose config has a valid rerun can never enter `runs/` while REG-20's table must stay computable (two valid runs make k1 raise, FILE(analysis/k1.py:146-147)); a held folder entering `runs/` turns `not_run` into `lost_open` (FILE(analysis/k1.py:286)). Either move is RB4 (ii)'s case: `analysis.k1 reg20` is run again and an [OPS] or [CORR] entry reports whether its output changed. Rule 4's custody of these folders after REG-20's [RESULT] is the owner's.

**RD8, verbatim:** "No VM folder of arm A's eleven configs is removed from the VM before REG-20's [RESULT]; the 2026-11-04 exception does not apply to a folder held or set aside outside runs/. Nothing in `/Users/chalshik/Projects/aftershock-reg20-holding` is opened, moved or deleted before REG-20's [RESULT] except by the scripts. `docs/status.md`'s Watch list names that folder."

## 11. The open-file limit in the launching shell

As draft 2. An open run whose launch log shows no nofile line of at least 4096 is used only with `state/nofile_ok_<rid>.txt`, logged in an [OPS] entry (FILE(docs/probe/20261113_reg20/ops/common.sh:286)).

## 12. Where the control decision and the table run

As draft 2 (b): from the Mac's repo root. k1's closure is checked against the pin, the seal files against their blobs, and the code again just before and just after each use (RB1, RA4).

**RC1 (a) replaces the bullets under "The seal blobs (RA-O1)", verbatim:** "**The seal blobs and the judged code (RA-O1).** A change to any file of the arm A hold (below) stops the queue at its next turn (queue.sh:58), possibly between a burst run and its control. REG-21's and REG-22's freeze no longer prevents such a change: both batch 2s are computed (FILE(docs/decisions.md:16571), FILE(docs/decisions.md:16798)), which ends both freezes (FILE(docs/decisions.md:9834) and FILE(docs/decisions.md:17012) for REG-21; FILE(docs/decisions.md:4748) for REG-22). At least one such commit is planned: REG-24's seal row in `analysis/withheld.py` (FILE(docs/drafts/reg24_confirm_draft1.md:418-421)). The check is kept, as the stricter one; the arm A hold replaces the freeze; each control's gap after its burst run (`gap_s`) and whether the boot changed are recorded (FILE(docs/probe/20261113_reg20/ops/common.sh:398))."

**RD6's sentence, added after it** (the name "freeze" becomes "hold", as RC1 names it): "REG-21's and REG-22's freezes ended when both batch 2s were computed (FILE(docs/decisions.md:16571), FILE(docs/decisions.md:16798)). The seal files and k1's closure are now protected only by this decision's arm A hold (RD4)."

**Draft 3 adds a second planned commit:** D1's seal row (FILE(docs/drafts/d1_r1/withheld.patch:4)).

This departs from RUNBOOK §5's worktree rule (FILE(agent/RUNBOOK.md:59)). RUNBOOK row 2a gains RB6's "pin 1cface7; no worktree (ops decision point 12)" in heading 1's commit (`runbook_heading1.patch`).

## 13. The table's command

As draft 2: `AFTERSHOCK_UNSEAL=REG-20 .venv/bin/python -m analysis.k1 reg20` from the repo root, after the folder set and the recheck, followed by `mac_checks`, the rc and the `withheld:` test (FILE(docs/probe/20261113_reg20/ops/final.sh:72-77)).

**Draft 3 states** (unchanged code, new consequence): `final.sh` also calls `gate_in_log` (FILE(docs/probe/20261113_reg20/ops/final.sh:15)), so it refuses after any `STOP_PAT` heading that follows the start. That includes arm A's own "… ended by a stop: …" end entry (point 18).
- So a table after a stop-ended arm A needs its own decision (and a new start heading, or a script change).
- After the `QUEUE DONE` end entry, `final.sh` runs. The sandbox case is "and final.sh runs after it".

## 14. The gate and the headings

**Headings.** All of these must be in HEAD's `docs/decisions.md`:
- REG-19's [RESULT] (as draft 2);
- **a rulings heading** (RD1, the regex verbatim, FILE(docs/probe/20261113_reg20/ops/common.sh:43)†):
  ```
  RULINGS_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[DECISION\] (\(owner\) REG-20 arm A operations: the owner.s rulings|\(delegate\) REG-20 arm A operations: the rulings on the owner.s points)([^0-9A-Za-z]|$)'
  ```
- after both, the start heading, as draft 2 (FILE(docs/probe/20261113_reg20/ops/common.sh:45)†).

**RD2, made mechanical (draft 3).** RD2 says "`owner_rulings.txt` is not changed again before REG-20 arm A's end entry, except by an `(owner)` [DECISION]". Two checks enforce it:
- **In `gate_in_log`:** a heading matching
  ```
  RULINGS_DLG_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[DECISION\] \(delegate\) REG-20 arm A operations: the rulings on the owner.s points([^0-9A-Za-z]|$)'
  ```
  may occur at most once, and only as the first rulings heading (FILE(docs/probe/20261113_reg20/ops/common.sh:44)†, FILE(docs/probe/20261113_reg20/ops/common.sh:159-161)†).
- **In `rulings_ok`** (RC2, rule F's patch with RD1's wording in its message): the last commit that changed `owner_rulings.txt` must add a `RULINGS_PAT` heading to `docs/decisions.md` (FILE(docs/probe/20261113_reg20/ops/common.sh:131-133)†).

Together, after the delegate's first rulings commit, a changed ruling needs an owner's heading in the same commit. The start heading must then follow it (`sl > gl`, FILE(docs/probe/20261113_reg20/ops/common.sh:165)†).

**RC2's text, added to the headings list.** It is adapted to RD1: "the owner's rulings heading" becomes "a rulings heading", and the parenthesis is new:
> The last commit that changed `owner_rulings.txt` must add a rulings heading (`rulings_ok`): the owner's, or once and first the delegate's (RD1, RD2). A ruling therefore changes only with a new owner's entry, after which the start heading must be written again (RA5).

**The sandbox cases** (draft 3, section "the rulings heading is the owner's, or once and first the delegate's"):
- RD1's two cases:
  - the delegate's heading in its own words: the queue starts;
  - a delegate heading in the owner's words: refused.
- RD2's cases, each refused:
  - a delegate's heading after the owner's;
  - a second delegate heading;
  - a ruling changed alone after the delegate's commit (the queue and `final.sh`);
  - a delegate heading after the start.
- An owner's entry that overrules the delegate (with a new start heading after it): runs.

**The stop heading (RA-O3; RC-O3; point 18).** It is now (FILE(docs/probe/20261113_reg20/ops/common.sh:46)†):
```
STOP_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[(DECISION|CORR|OPS)\]( \((owner|delegate)\))? REG-20 arm A (stops|is stopped|halted|is halted|ended by a stop)([^0-9A-Za-z]|$)'
```
- After the start heading, such a heading refuses every start, the queue's, `launch.sh`'s, `final.sh`'s and `vm_checkout.sh`'s.
- Arm A's `QUEUE DONE` end entry, `[OPS] REG-20 arm A: the queue ended (QUEUE DONE)`, does not match (sandbox).

**The gate's one computation:** as draft 2 (FILE(docs/drafts/reg20_ops_decision_draft2.md:266-286)).
- The scripts accept only the one committed file in `docs/probe/reg20/`. Any second gate file there refuses the start (the count check is at FILE(docs/probe/20261113_reg20/ops/common.sh:170)†; RC-O12 corrects draft 2's "common.sh:126").
- `gate.sh` stays withdrawn.
- **Question G, the ruling (RD2): (a).** The start entry carries RD7's text (see "Texts for headings 2 and 3").

## 15. The control bits and failed checks in the queue output

As draft 2: accepted as inherent. Three things show:
- control bits;
- failed-check names (RA-O9);
- RECHECK and SET ASIDE lines.

**RC4 replaces draft 2's last sentence, verbatim:** "The answers to the stops of points 2a, 6, 7, 8 and 9 are fixed before the first launch (RA5). These are still given per stop, after control bits and failed-check names may be visible: a rerun after `manipulation`, `power_limit` or a second `gpu_steady` (RB7); a loss without a reboot, or with an unknown launch boot (point 8); every answer under ruling 2a `stop` or 7 `per_stop`; a further attempt by `attempt_ok` other than 9(a)'s; `nofile_ok`; and every "the owner decides" stop of `decide`. Each such answer is a discretionary ruling made after outcome bits may be visible."

**Draft 3 adds two to that list:**
- the owner's answer after RD3 (ii)'s systematic-fault stop;
- the owner's settle record after RD3 (vi)'s stop under `setaside` (two set-asides, or a set-aside and an invalid run).

## 16. Arm B and its seal

RB9's options (a), (b) and (c), verbatim as draft 2 (FILE(docs/drafts/reg20_ops_decision_draft2.md:299-302)).

**The freeze paragraph** is RC1 (c) and RD6, merged:
> **The freeze (RB9) has ended:** both batch 2s are computed (FILE(docs/decisions.md:16571), FILE(docs/decisions.md:16798); FILE(docs/decisions.md:17012)). Under (b) the seal row is added after `final.sh`'s files are committed, which is also the end of the arm A hold. Ruling 16 is (a), which changes no file.

## 17. Quiet hours

As draft 1 and draft 2: withdrawn, applied. No script reads the hour.

## 18. Order with E1 (new; RC7, RD5, RC-O2, RC-O10)

**The rule.** It is RD5's first sentence, which is also the rule in E1's [REG] (FILE(docs/decisions.md:17076)): "E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry."

**E1 is first.**
- E1's approving entry says so (FILE(docs/decisions.md:18433)).
- It is also first under each of the three definitions in play:
  - E1's [REG] (the item whose last required heading has the earlier line, FILE(docs/decisions.md:17076));
  - RD5's (the earlier line of E1's approval heading and of arm A's start heading);
  - RC7's (the operations [DECISION] committed first).
- DERIVED: HEAD's `docs/decisions.md` holds E1's approval at line 18286, and no REG-20 rulings, start or operations heading (PROBE: `git show HEAD:docs/decisions.md | grep -n -E '^## .*(REG-20 arm A (starts|operations)|E1 approved|E1: the queue ended|E1 ended by a stop)'` gives the one line 18286, 2026-11-14 ≈ 02:40 UTC).

**E1's end entry** is one of the three headings E1 registered (FILE(docs/decisions.md:17076)):
- `## <date> · [OPS] E1: the queue ended (QUEUE DONE)`;
- `## <date> · [OPS] E1: the queue ended (QUEUE END)`;
- `## <date> · [OPS] E1 ended by a stop: <the stop line>`.

"A pause, or a stop that waits for a decision, is not an end" (ibid.).

**Arm A's end entry** is RD5's two forms, with RC7's `STOP_PAT` branch:
- `## <date> · [OPS] REG-20 arm A: the queue ended (QUEUE DONE)`, quoting the queue's `QUEUE DONE` line. It is written after `QUEUE DONE` and before `final.sh`.
- `## <date> · [OPS] REG-20 arm A ended by a stop: <the stop line>`, for a stop that an entry has decided ends arm A.
- A pause, or a stop that waits for a decision, is not an end.
- An entry matching `STOP_PAT` (point 14) stops every script. Of those, only "… ended by a stop: …" is an end for this rule.

**What arm A waits for, by script** (draft 3; RC-O2 widened). This replaces RD5's "The scripts do not read E1's entries, so this rule is kept by hand".
- `e1_ended` (FILE(docs/probe/20261113_reg20/ops/common.sh:138-143)†) returns 2 unless both hold:
  - (i) HEAD's committed `docs/decisions.md` holds a heading matching
    ```
    E1_END_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[OPS\] E1(: the queue ended \(QUEUE (DONE|END)\)| ended by a stop: [^ ].*)'
    ```
    (FILE(docs/probe/20261113_reg20/ops/common.sh:51)†);
  - (ii) E1's queue lock `docs/probe/20261113_e1/ops/state/queue.lock` does not exist. Only its existence is tested; nothing in E1's `state/` is opened (RC-O2).
- `gate_in_log` calls `e1_ended`, so the queue, `launch.sh`, `final.sh` and `vm_checkout.sh` refuse before E1's end (FILE(docs/probe/20261113_reg20/ops/common.sh:177)†).
- `session_probe.sh` calls it after `mac_checks`, so no REG-20 session probe is written while E1 holds the VM (FILE(docs/probe/20261113_reg20/ops/session_probe.sh:14)†).
- The sandbox cases (section "point 18"):
  - With no end entry, the queue, `launch.sh`, `final.sh`, `vm_checkout.sh` and `session_probe.sh` are refused.
  - Six headings that are not ends are refused: E1's `(QUEUE STOP …)`, `E10`, `(QUEUE END futility stop)`, `E1 halted`, an empty stop line, and a heading in the working tree only.
  - `QUEUE END` and "ended by a stop" are accepted.
  - The lock refuses the queue, `launch.sh`, `vm_checkout.sh` and the probe. The queue runs once the lock is removed.
  - With the VM at ce5f842, there is no launch and no session.
- **Not judged by the script:**
  - whether an entry "decided" that a stop ends E1 (that is the entry's content);
  - where the end entry sits in the log.

**The VM's move back, from E1's ce5f842 to the pin 1cface7.**
- E1's approval does not cover it: "A move of the VM back to `a7bb77a`, or to any commit other than forward to E1's, is not covered by this approval and needs its own entry" (DB10 (iii), FILE(docs/decisions.md:18294)). **Heading 1 is that entry.** It covers the move only by `vm_checkout.sh` and only from a commit that the pin is an ancestor of.
- **The two ends of the move.**
  - The pin is an ancestor of ce5f842 (DERIVED, git_facts).
  - `uv.lock` is the same blob at both ends (DERIVED, git_facts), so no package changes. `vm_checkout.sh` still runs the dry-run sync and stops on any change.
  - `harness/` changes back to the pin's, as point 1 intends.
  - `runs/` is gitignored and untracked (FILE(.gitignore:7)), so a checkout changes no run folder. E1's [REG] says the same of E1's move (FILE(docs/decisions.md:17022)).
- **`vm_checkout.sh`** (new; RC-O10; FILE(docs/probe/20261113_reg20/ops/vm_checkout.sh)†) refuses, and changes nothing on the VM, in each of these cases:
  - `mac_checks` fails;
  - `gate_in_log` fails, that is before every heading the queue needs and E1's end entry, or while E1's lock exists;
  - REG-20's own queue lock exists;
  - a compute process is on the GPU, or any tmux session exists;
  - the VM's tree is dirty;
  - the VM's commit is not one that the pin is an ancestor of on the Mac (the sandbox includes an orphan commit).
- **What it does when none of these applies.**
  - It runs `git checkout -q --detach <pin>` on the VM only, with no push and no fetch. The pin is already in the VM's clone as an ancestor of ce5f842 (BELIEF that the clone is not shallow; the checkout fails otherwise and the script stops).
  - It then reads back the commit, the dirty count and `uv.lock`'s blob, and runs `uv sync --frozen --extra server --dry-run`.
  - It writes everything to `docs/probe/20261113_reg20/vm_checkout_<stamp>.txt`, to be committed with an [OPS] entry.
  - If the VM is already at the pin, it records `already_at_pin` and changes nothing.
- **RB6's hand steps** ("push main …; `git fetch origin && git checkout --detach 1cface77ca001cdf5d90de9313ddd4a3af4569a1`; … Never while a run is in progress") are kept as the record of the move. The script drops the push and the fetch, because the backward move needs neither (item map, departure).
- **Launch refuses any other tree.**
  - `launch.sh` stops unless the VM is at the pin, clean (FILE(docs/probe/20261113_reg20/ops/launch.sh:50)).
  - `session_probe.sh` stops the same way (FILE(docs/probe/20261113_reg20/ops/session_probe.sh:46)†).
  - The sandbox cases: with the VM at ce5f842, no launch and no session.

**Also kept by hand** (RC7 (a), adapted to E1 first). These are not mechanical, because E1's scripts do not read REG-20's entries (FILE(docs/decisions.md:17076)):
- While arm A has started (heading 3) and not ended:
  - no E1 `vm_checkout.sh`, session probe or queue;
  - no change of the VM's checkout other than README step 4;
  - no deploy of HEAD (RUNBOOK §3 step 6, §4).
- After E1's end entry, this applies to any later E1 run, such as a rerun the owner allows.
- `launch.sh` refuses while a compute process or a tmux session exists (FILE(docs/probe/20261113_reg20/ops/launch.sh:49-56)), so two runs cannot overlap (RD5's last sentence).
- RUNBOOK's row order and §4 are amended in heading 1's commit (see "RUNBOOK, in heading 1's commit").

**README step 4** begins with RC7 (c)'s words, verbatim: "Only if E1 has not started, or E1's end entry is committed and E1's queue lock is absent (point 18):". The step is now `vm_checkout.sh`.

---

## For the owner, before the first launch

Each point is answered in `owner_rulings.txt` (G in the rulings entry). The picks below are owner-proxy round 2's (RD2). The rulings entry commits them under the delegation. The owner may overrule any of them by an (owner) entry, and the scripts then require a new start heading (point 14).

**2a. A run that today's checks change at its copy.** The pick is **`setaside`**.
- The options are as draft 2: `keep`, `setaside`, `stop`, `pin_head`.
- **RC5 replaces draft 2's "Risk of `setaside`" bullet, verbatim:** "**Risk of `setaside`:** k1 reads `lost_open` only from two stored-invalid folders in `runs/` (FILE(analysis/k1.py:286)); a set-aside folder is stored valid and stays out of `runs/`. A seed with a set-aside attempt therefore ends with its valid rerun's label or as `not_run`: after a set-aside and an invalid rerun, or two set-asides, the queue stops (FILE(docs/probe/20261113_reg20/ops/common.sh:347)), a `lost_open` settle is refused (FILE(docs/probe/20261113_reg20/ops/common.sh:320)), and the only answers are the owner's `not_run` or a third attempt. Both attempts are then invalid by the checks in force, which REG-20 labels `lost_open`, cold (FILE(docs/decisions.md:4067)); the seed leaves n instead, which can turn `refutes` into `inconclusive` (DERIVED: k_stuck falls by one, FILE(analysis/k1.py:224), FILE(analysis/k1.py:233)), T3's direction (FILE(docs/decisions.md:4103))."
- The cost the proxy gives (DERIVED, proxy round 2): `stats.cp_upper(0, 182)` = 0.0163 per run, so P(at least one set-aside over 11 runs) ≤ about 0.17.
- RD3 (vi)'s recommendation, the owner's `not_run` with a counterfactual line, is in the rulings entry.

**6. A client error in an open-loop run of arm A (a burst run or its control).** The pick is **(b)**.
- The options are as draft 2: (a), (b) and (c), where (c) is not offered.
- RB10's residual-risk sentence stays.
- The delegate's answers are RD3 (iii).

**7. An open burst run invalid twice, with an attempt that failed only setup checks** (RA3, RB7). The pick is **`lost_open`**.
- The options, with RC3's `not_run` text, verbatim:
  - `lost_open`: the delegate may settle it as REG-20's registered label (RB7).
  - `not_run`: "when every invalid attempt failed only setup checks, the delegate may settle it as `not_run` and the second run is held out of `runs/`; in the mixed case the delegate settles `lost_open` (RB7)."
  - `per_stop`: the owner rules each time.
- Draft 2's own recommendation ("Draft 2 recommends **`not_run`** for this narrow class only, where both attempts are setup-only", with RC3's words added) is replaced by the proxy's pick and its reasons (point 7).
- RD3 (ii)'s systematic-fault stop goes with it.

**8. A lost attempt.** The pick is **(b)**. The options are as draft 2. The delegate's answer is RD3 (iv).

**9. A control with both attempts invalid.** The pick is **(a)**.
- The options are RB8's.
- **RC-O4, added:** "Under (b) one settled control slot makes the whole outcome `pending_controls`, whatever the other seeds give, `refutes` included (FILE(analysis/k1.py:227-234))."

**16. Arm B and how arm A's result is headed.** The pick is **(a)**.
- The options are RB9's.
- After draft 2's "Owner-proxy recommends (a), since no frozen file changes.", RC1 (d) adds, verbatim: "(Written while the freeze was in force. It has ended, so this reason no longer separates (a) from (b): (a) keeps arm A's folders sealed until arm B ends; (b) adds one seal row after `final.sh`, under the hold's end.)"
- REG-20's seal row already covers arm B (FILE(analysis/withheld.py:28)).

**G. The gate computed at 3c8e5dc.** The pick is **(a)**.
- The options are as draft 2.
- **RC-O7's evidence, added verbatim:** "Evidence for (a): (1) `reg20_a_may_start` reads only `*_burst_l1pl350cl_r2.0_w3000_s<seed>` (FILE(analysis/k1.py:43-44), FILE(analysis/k1.py:269-280)); `fnmatch` matches whole names, so the unseal could not change its input even had a REG-20 folder existed. (2) No commit touched k1's import closure from d9b324d to 3c8e5dc, and REG-22 batch 2's prechecks found those files clean in the working tree at about 23:17 UTC (FILE(docs/decisions.md:16586-16598)); an uncommitted edit at 23:03 UTC that was undone by then is not excluded (BELIEF that there was none). (3) HEAD holds exactly one gate pair in `docs/probe/reg20/` (PROBE: `git ls-tree -r --name-only HEAD -- docs/probe/reg20/`, rule F round 2)."
- (3) holds at 5f9f442 too (PROBE(docs/drafts/reg20_ops_r3/git_facts_20261114.txt)).

**D. The VM's disk (new in draft 3; the owner's, because it means deleting files: FILE(docs/decisions.md:4235)).**

*Inputs.*
- Free space on the VM at E1's session probe, before E1's runs: F0 = 4,171,272 kB (PROBE(docs/probe/20261113_e1/session_20261114T021434Z_30853_1.txt), read with `git show HEAD:`, quoted in disk_probe_20261114.txt).
- One reported 4080 s run of REG-19, seed 15's closed burst run: r = 242,736 kB on the Mac's disk (PROBE(docs/drafts/reg20_ops_r3/disk_probe_20261114.txt)). This matches RUNBOOK's "≈ 240 MB per 4080 s run" (FILE(agent/RUNBOOK.md:26)).
- An open-loop run is taken to be the same size (BELIEF). An open-loop backlog writes the most lines (draft 2, point 1), so an open run may be larger.
- An E1 run lasts 1200 s, so it is taken to be r × 1200/4080 = 71,393 kB (DERIVED; E1's own estimate is "about 70 MB", FILE(docs/probe/20261113_e1/ops/common.sh:34)).
  - E1 has six rates.
  - At most 3 attempts per rate gives 18 launches at most (BELIEF from E1's at most 6.3 GPU h, FILE(docs/decisions.md:18286)).
- The pre-launch rule: launch k (1-based) proceeds only if the free space read before it is ≥ MIN_FREE_KB = 2,097,152 (FILE(docs/probe/20261113_reg20/ops/common.sh:19), FILE(docs/probe/20261113_reg20/ops/launch.sh:52)).
- No VM folder of arm A is removed before REG-20's [RESULT] (RD8). No E1 folder is removed before E1's end entry (DC-O4, FILE(docs/decisions.md:17072)).

*DERIVED.* Free space when arm A starts, F1 = F0 − (E1's runs):
- F1 = 3,742,914 kB with E1's six runs;
- F1 = 2,886,198 kB with 18 runs.

Launch k needs F1 − (k − 1) × r ≥ 2,097,152, so the number of launches that fit is ⌊(F1 − 2,097,152) / r⌋ + 1:

| Free space when arm A starts | Launches that fit |
|---|---|
| F0, no E1 run | 9 |
| E1's six runs (expected) | 7 |
| E1's worst case, 18 runs | 4 |

What arm A needs, against those launches:

| Arm A needs | Launches | Free space needed at the first launch | Short by, from expected F1 |
|---|---|---|---|
| no control due (5 burst runs and the drift run) | 6 | 3,310,832 kB | fits (432,082 kB to spare) |
| all 11 planned (5 burst runs, 5 controls, the drift run) | 11 | 4,524,512 kB | 781,598 kB (353,240 from F0; 1,638,314 in E1's worst case) |
| ceiling under the picks, without losses (11 × 2, plus 5 third control attempts under 9(a)) | 27 | 8,408,288 kB | 4,665,374 kB |
| with 8(b)'s up to 2 uncounted losses per config (BELIEF: a lost folder can be as large as a run) | 49 | 13,748,480 kB | 10,005,566 kB |

**So arm A's worst case does not fit, and neither do its 11 planned runs.** Even with no E1 run on the VM, the eleventh launch is refused. With E1's expected six runs, only seven launches fit, so arm A stops for disk once two controls are due.

*What the pre-launch check does when space runs out.*
- `launch.sh` prints `STOP: only '<free>' kB free on the VM` and exits 2 (FILE(docs/probe/20261113_reg20/ops/launch.sh:52)).
- This happens before the attempt record is written (FILE(docs/probe/20261113_reg20/ops/launch.sh:58)), so no attempt is spent.
- The queue prints `QUEUE STOP <cfg> launch rc=2 …` with that line (FILE(docs/probe/20261113_reg20/ops/queue.sh:76)). It can be started again once space is freed.
- No label is written wrongly. But the stop can fall between a cold burst run and its due control, which then runs late. That loses "right after it" (FILE(docs/decisions.md:4054)), and `gap_s` records the gap. This is Trace 1's cost class.

*RUNBOOK:26's rule* is "free space ≥ 4 × the item's expected size (≈ 240 MB per 4080 s run)" (FILE(agent/RUNBOOK.md:26)). It has two readings:
- per launch: 4 × r = 970,944 kB, which MIN_FREE_KB (2,097,152) meets;
- per item: 4 × 11 × r = 10,680,384 kB, which F0 does not meet.

Draft 3 takes the per-launch reading (BELIEF: the row is in "Preflight (every launch)"). That reading is the owner's to confirm.

*Options.*
- **(a), recommended.** Before arm A's first launch, the owner frees VM space so that the session probe reads free ≥ 4,524,512 kB (all 11 planned runs), and preferably ≥ 8,408,288 kB (the 27-launch ceiling without losses).
  - The space comes only from folders whose Mac copy is checksum-verified (the 2026-11-04 rule, FILE(docs/decisions.md:530)).
  - Never from arm A's folders (RD8).
  - From E1's only after E1's end entry (DC-O4).
  - The agent deletes nothing on the VM. The owner's removal is recorded in an [OPS] entry.
- **(b)** Accept a disk stop mid-arm, with its late control. The owner frees space at that stop.
- **(c)** A later script check, not applied here: before a burst launch, require free ≥ MIN_FREE_KB + r, so that a disk stop never falls between a burst run and its control. It would need its own review round, and r would be a new parameter in `common.sh` (rule 5).

---

## The freeze (ended)

RD6 asks that this section keep draft 2's first sentence and its list, marked "ended". Both are kept below.

**Ended:** "REG-21 and REG-22 freeze these files from d9b324d until each batch 2 is computed or declared not computed (FILE(docs/decisions.md:9834); `docs/status.md`)". The files:
- `analysis/{__init__,c2,derived,floor,gate,k1,k3,k3w,load,margin,modelf,modelf_sim,stats,tables,withheld}.py`;
- `harness/{__init__,checks,config,env_snapshot,loadgen,recorder,run,trigger,workload}.py`;
- `pyproject.toml`, `uv.lock`, `.python-version`.

This is FILE(docs/drafts/reg20_ops_decision_draft2.md:368-371). Both batch 2s are computed (FILE(docs/decisions.md:16571), FILE(docs/decisions.md:16798)), so the freeze is over. RD4's text follows, merged with RC1 (b), as the arm A hold.

## The arm A hold (replaces REG-21's and REG-22's freeze, which ended with both batch 2s)

This merges RC1 (b) and RD4. The name is RC1's (RD4 calls it "the arm A freeze"). The list is the union of the two. Where the two differ, the stricter text is kept, and the item map gives each such case.

**When it applies.** From the commit of the start entry (heading 3) until `final.sh`'s two output files are committed, or until an entry matching `STOP_PAT` stops arm A, whichever comes first (RC1 (b); RD4: "or an entry ends arm A").
- A later start heading starts the hold again.
- If heading 3 is committed while E1 is still running, the hold starts then. To keep it short, heading 3 may wait for E1's end entry (BELIEF that this costs nothing: the scripts refuse before E1's end entry either way, point 18).

**1. No commit, in any session, changes any of these:**
- the 19 `.py` files of k1's import closure: `analysis/{__init__,derived,floor,gate,k1,load,margin,stats,tables,withheld}.py` and `harness/{__init__,checks,config,env_snapshot,loadgen,recorder,run,trigger,workload}.py` (PROBE(docs/drafts/reg20_ops_r3/closure_20261114.txt); RD4 asks for `closure.py`'s output at heading 1's commit to be quoted in the entry);
- `analysis/recheck.py`;
- any file under `harness/` (RD4);
- `configs/defaults.yaml`;
- `tools/manifest.py`, `pyproject.toml`, `uv.lock` and `.python-version`;
- in `docs/probe/20261113_reg20/ops/`: the nine scripts `common.sh`, `vm_state.py`, `session_probe.sh`, `launch.sh`, `queue.sh`, `final.sh`, `control_due.py`, `recheck_one.py` and `vm_checkout.sh`, plus `owner_rulings.txt` and `scripts_commit.txt`.
  - A script changes only by a reviewed commit with its new `scripts_commit.txt`.
  - `owner_rulings.txt` changes only by an (owner) rulings entry (RD2).

Also, no file named `gate_*.txt` is added under `docs/probe/reg20/` (RC1).

**2. No hand edits under `analysis/` or `harness/`.** RC1's words, with RD4's exception:
- RC1: "No tracked file under `analysis/` or `harness/` is edited in the main checkout's working tree, committed or not" (`recheck_guards` stops the copy, FILE(docs/probe/20261113_reg20/ops/common.sh:495); the stop of 2026-11-13, FILE(docs/decisions.md:4604)).
- Work for other items is written and tested in a separate git worktree or a scratch copy (RD4). Examples are E1's `analysis/e1.py`, REG-24's `analysis/confirm.py`, D1's `analysis/d1.py` and any subagent's work.
- RD4's exception: a file *outside* item 1's list reaches main only by one command that applies and commits it (`git apply … && git commit …`, or a fast-forward). A commit to such a file under `analysis/` or `tests/` is allowed, because none is in k1's or the recheck's import closure (PROBE(docs/drafts/reg20_ops_r3/closure_20261114.txt)).
- The sub-second gap between the apply and the commit can at worst stop the queue at a copy (`recheck_guards` compares the working tree with HEAD). It cannot change a label (DERIVED from FILE(docs/probe/20261113_reg20/ops/common.sh:523-528)†).
- The Mac's `.venv` is not changed: no `uv add`, `uv remove`, `uv sync` or `uv pip` (RD4).

**3. No new SEALS row.**
- RD4: "in particular no row is added to `analysis/withheld.py`'s SEALS: REG-24's row waits until final.sh's files are committed, and lands before REG-24's first run". D1's row (FILE(docs/drafts/d1_r1/withheld.patch:4)) waits the same way.
- RC1 item 3's path is kept for a row that cannot wait: "an entry first stops arm A (`STOP_PAT`); `common.sh`'s `SEAL_BLOBS` is then changed by a reviewed commit, with a new `scripts_commit.txt`, before the queue starts again, and that entry and the [RESULT] name both scripts commits."
- RC-O1 (tolerating added rows) is not taken, because RD4 forbids the row itself (item map).

**4. A notice.** `docs/status.md` and `agent/STATE.md` carry a notice of the hold, naming this list, from the start entry's commit to its end (RC1). `docs/status.md`'s Watch list names the holding folder (RD8). The proposed text is under "Docs, for the commits named".

**5. A breach is a [CORR] entry** (RC1).

**The duty in the [RESULT]** (RC1, verbatim): "the output of `git log --full-history --format='%H %ct %s' <start entry's commit>..<the commit of final.sh's files> -- <the files of item 1>` and of `git status --porcelain -- <the same files>` run just before `final.sh`, verbatim, as REG-22's batch 2 quoted its freeze facts (FILE(docs/decisions.md:16586-16598))."

**Draft 3 changes none of item 1's files outside its ops folder.** DERIVED: the patch's file list (ops_draft3.patch) holds only paths under `docs/probe/20261113_reg20/ops/`. `runbook_heading1.patch` touches `agent/RUNBOOK.md` only.

## Timing (RB11)

- **Draft 2's Timing section stands** (FILE(docs/drafts/reg20_ops_decision_draft2.md:380-393)). RB11's first branch could not be met: the first `reg19_final_*` file is in 047b95e, before draft 2.
- **This author saw REG-19's outcome before writing any part of draft 3.** It saw it in three places:
  - owner-proxy round 2's file, which quotes the gate's value (`k_closed` 5 of 5) and the heading at FILE(docs/decisions.md:16517) ("`supports`, 5 of 5");
  - rule F round 2's file;
  - the session digest's status headline.

  Every draft-3 change was written after that.
- **Draft 3's changes come from the reviewers' items, which name no REG-20 outcome.** The picks are the proxy's. The proxy disclosed the same knowledge before making them (proxy round 2, "Disclosure (A5)").
- **No REG-20 open run exists.** DERIVED by the reviewers: `ls runs | grep -cE '_l1pl350ol_|_s15_drift$'` gives 0 (proxy round 2; rule F round 2). This author did not list `runs/`, so as not to see E1's run ids.
- **What k_c = 5 implies for the rulings** is stated in the rulings entry (RC-O8).

## Duties for the [RESULT]

- **(i) Rule H.** As draft 2:
  - k of n per arm, with the one-sided 95 % Clopper–Pearson bound;
  - McNemar's p first, with Fisher's beside it;
  - the drift check labelled a single seed, and each control a single run.
- **(ii) Arm differences.** RC-O6 replaces the first sentence, verbatim: "The open arm's launch shell raises the soft open-file limit to 65536, and the harness starts vLLM as its child (FILE(harness/run.py:159)), so the server under test inherits it; the closed arm's server ran at the shell's default (BELIEF 1024, FILE(agent/RUNBOOK.md:28))." The rest is as draft 2.
- **(iii) Where `supports` went out of reach.**
  - As draft 2's first bullet: (5,0) gives 1/32 and (4,0) gives 1/16 (DERIVED from `k1.mcnemar_one_sided`).
  - RC4 replaces the second bullet, verbatim: "The [RESULT] names the first `CONTROL_DUE yes` or `unclear` line in the queue output and lists every hand-written record in `state/` (`rerun_ok`, `lost_ok`, `settle`, `attempt_ok`, `nofile_ok`, `recheck_ok`): its name, `by`, `under`, the commit of the [OPS] entry that names it, whether it came after that line, and the label it led to."
  - RD9 adds: each RD3 record written, with its stop line.
- **(iv) The judged code.** As draft 2.
- **(v) Ruling 2a.**
  - RD9: "every `recheck_changed` line of `queue_done.txt` with its recomputed `failed`; for each set-aside run, the attempt that replaced it".
  - RC5: "Under `keep`, and under `setaside` for every seed settled `not_run` with a set-aside attempt, add a second outcome line, which changes no label, with that seed counted `lost_open`." This is also RD3 (vi)'s line.
- **(vi) RA-O1, RA6 and RC6 (iv).**
  - Each control's `gap_s` and boot line.
  - Each `lost` line: arm, elapsed time, how it ended, counted or not.
  - Each held or set-aside folder, with its record and the sha256 of its `.sha256` list.
- **(vii) RA-O8.** As draft 2:
  - `supports` needs all five seeds `recovered_open`;
  - after the first that is not, the remaining runs can move the outcome only between `refutes` and `inconclusive`;
  - no futility stop is added.
- **(viii) Question G's answer**, with the gate file quoted verbatim.
- **(ix) RD9's statements.**
  - The rulings were made by the delegate after REG-19's outcome was visible (the gate value and REG-19's [RESULT] heading), and before any REG-20 run existed.
  - Whether arm A or E1 ran first (E1, point 18), and every gap the ordering caused between a burst run and its control.
- **(x) The arm A hold:** RC1's `git log` and `git status` output, verbatim (above), and every [CORR] for a breach.
- **(xi) RD3 (ii):** each systematic-fault stop, with both `RUN … INVALID failed=…` lines.
- **(xii) Point D:** each disk stop, with the free space it read, and any VM removal the owner recorded.

## RUNBOOK, in heading 1's commit (RC7 (b), RD10)

The patch is `docs/drafts/reg20_ops_r3/runbook_heading1.patch`, against HEAD's `agent/RUNBOOK.md`, which is unchanged since 40948ba (DERIVED, git_facts).
- **:48 (§3 step 6).** RB6's text, verbatim: "then, if REG-20's gate passed, check the VM out at 1cface7 (REG-20 ops decision); otherwise deploy HEAD (§4)".
  - RC7 (b)'s addition follows, verbatim: "; while REG-20 arm A or E1 has started and not ended, no deploy".
  - A parenthesis is added that names `vm_checkout.sh` and point 18. This is a departure: the parenthesis is new.
- **:50 (§4 heading).** It gains "nor while REG-20 arm A holds the VM, that is from REG-20's `vm_checkout.sh` until arm A's end entry (…), nor while REG-20's queue lock … exists; if the VM is at the pin 1cface7, detached, `git checkout main` comes first".
  - **This is new, by this author, and flagged for round 3.** It mirrors the E1 clause already in that heading.
- **:63 (§5 row 2).** Marked done, citing 3c8e5dc, question G and "never computed again" (RD10; draft 2's Proposal 1).
- **:64 (§5 row 2a).** It gains:
  - RB6's "pin 1cface7; no worktree (ops decision point 12)", verbatim;
  - RD5's sentence, verbatim ("E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry");
  - "E1 is first";
  - the wait by `e1_ended`;
  - the queue and `vm_checkout.sh`.
- Row 2b (E1) is already in place (FILE(agent/RUNBOOK.md:66)).

## Texts for headings 2 and 3

**Heading 2, the rulings entry** (RD2; RD3 verbatim; RC-O8; RD6):
- It quotes `owner_rulings.txt` as committed: draft 3's file with `owner_rulings_rd2.patch` applied, `2a setaside`, `6 b`, `7 lost_open`, `8 b`, `9 a`, `16 a`. It is committed in the same commit (RC2: the scripts refuse otherwise).
- It quotes question G's answer: (a).
- It quotes, verbatim:
  - owner-proxy round 2 and its delta on draft 3;
  - rule F round 2 and rule F round 3 (the delegation's (a) and (b), FILE(docs/decisions.md:4234)).
  - Departure: RD2 names rule F round 2 only. Round 2 was NOT READY, and a reject is binding, so round 3 must be quoted too.
- **RD3, verbatim:**
  > At each stop below the delegate writes the record named here, as soon as the queue stops for it, and no other. It reads nothing beyond the stop line and the reads that common.sh's ALLOWED lists, and makes no choice. Each record carries `under <this entry's heading> (ruling <n>)` and `by delegate`, and is logged in the next [OPS] entry.
  > (i) Ruling 7 (RA3's case): `state/settle_<run id of the second attempt>.txt` with `label lost_open`, unless (ii) applies.
  > (ii) Systematic-fault stop: when a run of any of arm A's eleven configs is invalid with `clean_git`, `kv_capacity` or `trigger` in its `failed`, and a run of another of the eleven configs already had one of these, the delegate does not start the queue again and writes no settle record. Arm A waits for the owner, and an [OPS] entry quotes both `RUN … INVALID failed=…` lines.
  > (iii) Ruling 6(b), for every open-loop config of arm A: after a client error, `state/rerun_ok_<run id>.txt` with `lifts no_errors/client_error`, when the scripts would accept it (launch log nofile ≥ 4096, same boot). After a second client error in the same config, the same record, which makes the seed `lost_open`. A client error with `manipulation` or `power_limit` in the same `failed` waits for the owner.
  > (iv) Ruling 8(b): after a power-off, once the VM is back, 350.00 W is read and the session probe is renewed with its [OPS] entry: `state/lost_ok_<run id>.txt` with `count no`, for a run launched in an earlier boot, at most two per config. The lost folder is not opened or copied. A loss without a reboot, or a third, waits for the owner.
  > (v) Ruling 9(a): when both attempts of a control are invalid, `state/attempt_ok_<config>_3.txt`. If the third is invalid or lost, arm A waits for the owner.
  > (vi) Ruling 2a `setaside`: no record. If a burst config's attempts end as two set-asides, or a set-aside and an invalid run, arm A waits for the owner. The recommendation fixed now is a settle record with `label not_run`, naming the invalid run if there is one, and a [RESULT] line with that seed counted `lost_open`.
- **RC4's rule applies to each record:** it is named in an [OPS] entry committed when it is written.
- **RC-O8, verbatim:** "The entry states that the rulings are made with REG-19's outcome and the gate public (k_c = 5), and, beside each ruling: a ruling that takes a seed out of n makes `supports` unreachable (DERIVED: (4,0) gives 1/16) and can lower k_stuck by one; a ruling that labels a seed `lost_open` adds one to k_stuck."
- Beside each pick, under that rule (DERIVED from k1's labels, FILE(analysis/k1.py:286), FILE(analysis/k1.py:176)):
  - 2a `setaside`: can take a seed out of n (RD3 (vi));
  - 7 `lost_open`: adds one to k_stuck in RA3's case;
  - 6 (b): a second client error adds one to k_stuck;
  - 8 (b): takes no seed out by itself;
  - 9 (a): keeps a `pending_control` seed in play;
  - 16 (a): changes no label.

**Heading 3, the start entry** (RD7, with RC-O7 as its evidence for G):
- It quotes the gate file verbatim: `{'k_closed': 5, 'n': 5, 'best_p': 0.03125, 'may_start': True}` (FILE(docs/probe/reg20/gate_20261113T230307Z.txt:1)). Its stderr file is 0 bytes (PROBE: `git cat-file -s HEAD:docs/probe/reg20/gate_err_20261113T230307Z.txt` gives 0).
- It names commit 3c8e5dc.
- It gives the command as the commit subject gives it, labelled BELIEF: the file has no record of its command, and a subject is not evidence.
- It gives the four differences from RB5 (ii): the seal variable, `uv run`, the unrecorded Mac-side checks, and the folder.
- It gives these DERIVED facts:
  - 0 REG-20-named folders on the Mac;
  - at `3c8e5dc^`, the judged code, the seal blobs and the lock equal what `mac_checks` requires;
  - 6748c26 is an ancestor of 3c8e5dc;
  - stderr is 0 bytes;
  - k1's closed pattern cannot match the drift name.
- It states that the working tree's state at the computation is not recorded, and that the gate is not computed again.
- It names the commit of heading 1, with `scripts_commit.txt` and the sandbox count, and `git diff --stat 56820bd <that commit> -- docs/probe/20261113_reg20/ops` (RD1).
- It states that the arm A hold begins with its commit, and quotes the hold's list.

## Docs, for the commits named

- **Heading 1's commit:**
  - `runbook_heading1.patch`;
  - the README as patched;
  - `scripts_commit.txt` (README step 1).
- **The start entry's commit, the hold notice** (RC1 item 4; RD8). For `docs/status.md`, under "Watch", and for `agent/STATE.md`: "**REG-20 arm A hold** (decisions.md [DECISION] REG-20 arm A starts, from its commit until `final.sh`'s two files are committed or an entry stops arm A): no commit to k1's 19-file import closure, `analysis/recheck.py`, `harness/`, `configs/defaults.yaml`, `tools/manifest.py`, `pyproject.toml`, `uv.lock`, `.python-version`, or `docs/probe/20261113_reg20/ops/` (nine scripts, `owner_rulings.txt`, `scripts_commit.txt`); no new `docs/probe/reg20/gate_*.txt`; no new SEALS row (REG-24's and D1's wait); no hand edit under `analysis/` or `harness/` in the main checkout; no change to the Mac's `.venv`. No VM folder of arm A's eleven configs is removed before REG-20's [RESULT]; nothing in `/Users/chalshik/Projects/aftershock-reg20-holding` is opened, moved or deleted before then except by the scripts."
- **The approval commit or the next docs commit** (RD10):
  - The two open questions, for `docs/open-questions.md`: "What does vLLM 0.32.0 do with its own open-file limit when the harness raises it to 65536 (RB14 (ii))?" and "Does a harness death (recorder or loadgen) correlate with a stuck open-loop run (draft 1, 'Not settled')?".
  - Any held or set-aside run id named in a canonical doc goes into `manifests/pending_copy.txt` first (FILE(tools/check_docs.py:69-76); RC6 (iii)).

## Tests

- **`zsh docs/probe/20261113_reg20/ops/test_sandbox.sh`,** on a throwaway git repo and a fake VM, in a scratch tree (40948ba with ops_draft3.patch applied): 428 of 428 passed, exit 0 (PROBE(docs/drafts/reg20_ops_r3/sandbox_20261114T023449Z.txt)). Draft 2's cases run unchanged except:
  - the messages RD1 renames;
  - RC3's move of the two not_run blocks to both-setup attempts (rule F's patch).

  New sections:
  - RD1, RC2 and RD2: the rulings heading;
  - point 18: E1's end entry and lock, and the VM at ce5f842;
  - `STOP_PAT`: `halted`, `is halted` and `ended by a stop`, and the `QUEUE DONE` end entry that is not a stop;
  - RC3's mixed case (rule F's cases);
  - RD-O1;
  - RC6 (ii)'s `.sha256` lists, held and set aside;
  - `vm_checkout.sh` (20 checks): its refusals, an orphan commit, a commit unknown on the Mac, `already_at_pin`, a failed checkout, a tree that is not the pin after the checkout, another `uv.lock` after it, and a dry-run change.
- **`test_control_due.py`:** 47 of 47 passed, exit 0 (PROBE(docs/drafts/reg20_ops_r3/test_control_due_20261114T024844Z.txt)). Draft 2's 46 tests, with RC-O11's change to the error test (`error` is `KeyError`) and one new test: the exception text stays out of the record and goes to stderr.
- `zsh -n` passes on every zsh script, and `ast.parse` on the three Python scripts (PROBE(docs/drafts/reg20_ops_r3/syntax_20261114.txt)).

## Not settled by this draft

- **Point D:** the owner's. Arm A's planned runs do not fit on the VM's disk as last read.
  - Open-loop runs may be larger than r (BELIEF).
  - RUNBOOK:26 has two readings.
- **The pin's A14 risk (point 1):** a limit, not settled.
- **The setup class (point 7):** a BELIEF fixed in advance.
- **Under 2a `setaside`** (RC5's text): "any seed with a set-aside attempt and no valid rerun reads `not_run` in k1, never `lost_open` (owner question 2a; duty (v))."
- **An edit made and undone within one `control_due.py` call** is not seen (point 5).
- **RD3 (ii) and RD3 (vi) are kept by hand** (RD-O2 not taken).
- **Point 18's limits.**
  - The scripts do not judge whether an entry "decided" an end, or where the end entry sits.
  - E1's scripts do not read REG-20's entries, so any later E1 run waits by hand.
- **`vm_checkout.sh` refuses a dirty VM tree.** Untracked files that E1 might leave outside `runs/` would make the move the owner's (fail-safe; BELIEF that there are none, since E1's `vm_checkout.sh` found the tree clean, FILE(docs/decisions.md:19394)).
- **After an "ended by a stop" entry, `final.sh` refuses** (point 13). The table of a partial arm A needs its own decision ("never pool a partial cell", FILE(agent/RUNBOOK.md:84)).
- **RD1's "anything else needs a new round":** met by the owner-proxy delta on this draft.
- **The new §4 clause in RUNBOOK** is this author's addition (flagged).
