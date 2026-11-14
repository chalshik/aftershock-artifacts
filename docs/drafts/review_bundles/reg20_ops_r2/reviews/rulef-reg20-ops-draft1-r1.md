Saved by the agent from the reviewer's own SendMessage calls to team-lead (tool-call inputs, its session c76f1b46, lines 532 and 542, timestamps 2026-11-13T22:15:53.358Z and 2026-11-13T22:16:18.959Z), because the messages were never delivered into the main session's transcript. The two parts are kept whole, in order, separated by a rule. Rule F round 1 on the REG-20 arm A operations decision, draft 1 (docs/drafts/reg20_ops_decision_draft1.md) and its scripts at c8b482d: NOT READY on RA1–RA7, optional RA-O1–RA-O9.

---

[Part 1 of 2] Rule F review of the REG-20 arm A operations decision (draft 1) and its scripts at c8b482d: NOT READY, with 7 required and 9 optional items.

**Reviewer:** a separate subagent, 2026-11-14. 0 GPU h. The VM was not contacted. I did not open anything under `runs/`, any `state/` folder, `docs/probe/20261111_reg19/ops/RESUME.md`, `docs/paper/`, the backups or any queue output file. I edited no repo file. My only scratch files are in my own scratchpad.

**Read:**
- the draft;
- `docs/probe/20261113_reg20/ops/` (README, DESIGN_NOTES, PIN_DECISION_DRAFT, common.sh, launch.sh, queue.sh, final.sh, session_probe.sh, vm_state.py, control_due.py, test_sandbox.sh's stubs, helpers and cases, and the test names in test_control_due.py);
- `docs/decisions.md`: 4040–4240 (REG-20's [REG], its approval, the delegation), the heading at 4383, and 4495–4610 (the quiet hours, the newest [OPS] and [CORR]);
- ops_r3's `common.sh:1-260` and `launch.sh:45-55`;
- `analysis/k1.py`, `withheld.py`, `load.py` (`load_run`, `find_runs`, `_level`) and `recheck.py`, plus the lazy imports in `gate.py`, `floor.py`, `margin.py` and `derived.py`;
- `harness/checks.py` at 1cface7 (recorder, no_errors, accounting, kv_capacity, trigger, manipulation) and its diff to HEAD; `LagTail` and the write calls in `recorder.py` and `loadgen.py` at 1cface7;
- `agent/RUNBOOK.md:20-95`; `docs/open-questions.md`, row A18; `_to_delete/docs/probe/20261113_reg19/ops/launch7.sh:41`.

**Tests, run on the Mac on 2026-11-14:**
- `zsh docs/probe/20261113_reg20/ops/test_sandbox.sh`: 214 passed, 0 failed.
- `uv run pytest docs/probe/20261113_reg20/ops/test_control_due.py -q`: 35 passed.
- Both counts match the draft (FILE(docs/drafts/reg20_ops_decision_draft1.md:310-311)).
- One extra sandbox case of mine is in RA4. It is a scratch copy of the sandbox and passes, which shows the defect.

## Verdict: NOT READY

- Three required items (RA1, RA3, RA4) give a trace that spends GPU hours on a wrong label or against the gate.
- One (RA2) leaves no path from a stop the draft adds to a table that can be computed.
- Points 2 and 8, which the draft gives the delegate, need the owner's ruling. So do 6 and 9, and that ruling must come before the first launch (RA2, RA5, RA6).
- The scripts at c8b482d are not the scripts the draft would approve (RA7).

---

## Required

### RA1. The start gate accepts a heading that says arm A does not start
**What is wrong.**
- `START_PAT` is a prefix with nothing anchored after "REG-20 arm A starts" (FILE(docs/probe/20261113_reg20/ops/common.sh:27)).
- `gate_in_log` takes the last heading that matches (FILE(docs/probe/20261113_reg20/ops/common.sh:83)).
- The design note anchored the pattern on `: k1\.reg20_a_may_start passed` (FILE(docs/probe/20261113_reg20/ops/DESIGN_NOTES.md:9)), and the scripts dropped that.
- Draft item 14 asks only for "these exact words" (FILE(docs/drafts/reg20_ops_decision_draft1.md:278)).

**Trace (PROBE: `grep -E "$START_PAT"` run by this review).** Both of these headings match:
- `## 2026-11-15 · [DECISION] (delegate) REG-20 arm A starts only after a new registration: k1.reg20_a_may_start failed (4 of 5 closed runs cold-backlogged)`
- `## 2026-11-15 · [DECISION] (owner) REG-20 arm A starts nothing: the gate is not passed`

With either heading committed after REG-19's [RESULT], `queue.sh` passes the gate (FILE(docs/probe/20261113_reg20/ops/queue.sh:17)) and runs arm A although the gate failed (FILE(docs/decisions.md:4051)).

**GPU h at risk.** Five burst runs, the drift run and up to five controls: 11 runs ≈ 11.8–13.5 GPU h (DERIVED: 11 × 1.07–1.23, the cost per run in FILE(docs/decisions.md:4097)).

**Fix.**
- Anchor the pattern on the full words `REG-20 arm A starts: k1\.reg20_a_may_start passed` followed by `([^0-9A-Za-z]|$)`.
- Fix that heading's text in the decision.
- Add sandbox cases for "starts only…", "starts nothing" and "starts: … failed".

**Required.**

### RA2. The checks in force (item 2) cannot reach the table, so the owner's ruling on a run they flag has no workable path
**What is wrong.**
- k1 judges validity only from the stored `checks.json`. `_runs` takes `r["checks"]["valid"]` (FILE(analysis/k1.py:145)) and raises when a pattern has two valid runs (FILE(analysis/k1.py:147)).
- At the pin, the `recorder` check measures gaps only between scrapes that exist (FILE(harness/checks.py:92-96 at 1cface7)). So a recorder that dies mid-run (A14) leaves the run VALID. This is the miss the A14 decision named (FILE(docs/decisions.md:4205)).
- A dead recorder leaves the end window uncovered, so `_level` gives NaN for the queue and KV (FILE(analysis/load.py:171-172)). The reading is then `None`, so control_due prints `unclear`; the test at FILE(docs/probe/20261113_reg20/ops/test_control_due.py:98) has a gap at 3700 s give `unclear`. k1 then drops the seed (FILE(analysis/k1.py:162-163), FILE(analysis/k1.py:215)).
- Item 2 says the delegate "marks, reruns and counts nothing", and the owner rules (FILE(docs/drafts/reg20_ops_decision_draft1.md:79-85)). It is not in the scripts (draft line 83).

**Trace.** Seed 16, attempt 1, at 1cface7: the recorder dies at about 2500 s, valid by the pin's checks. Whatever the owner rules at the recheck's stop:
- **(i) Keep it.** It reads `unclear`, the seed leaves n, and `supports` becomes unreachable. Four discordant pairs give p = 1/16 = 0.0625 > 0.05 (DERIVED).
- **(ii) Rerun.** `decide` returns the stored-valid run and launches nothing (FILE(docs/probe/20261113_reg20/ops/common.sh:144-145)). Forcing a rerun outside the scripts trips the attempt-count stop (FILE(docs/probe/20261113_reg20/ops/common.sh:140)). If the rerun is valid, k1 raises at k1.py:147, `final.sh` fails, and there is no table without changing frozen code (FILE(docs/decisions.md:4169)).
- **(iii) Keep it out of k1.** It is already in `runs/`, because the copy comes before any recheck. Removing it is a deletion in `runs/`, which the delegation does not allow (FILE(docs/decisions.md:4235)).

**GPU h and probability.**
- The rest of arm A, about 3.5–6 GPU h, can move the outcome only between `refutes` and `inconclusive`; at worst the whole matrix ends with no table.
- With A14's on-record rate of 1 in 182 folders (BELIEF, draft line 58), P(at least one death in 6–11 runs) ≈ 3–6 % (DERIVED: 1 − (181/182)^6 = 0.032; ^11 = 0.059). The open-loop rate is unknown.

**The draft's own words are wrong here.** "(c) keeps one harness for both arms and still applies today's checks to every run" (FILE(docs/drafts/reg20_ops_decision_draft1.md:54)) holds for the stop and never for a label.

**Fix (the owner's, before the first launch).** One of:
- **(a)** pin at or after 5ee6e38, so that the stored checks are the checks in force and the A14 death cannot happen. The drift run, at the same commit, is the registered check of that change (FILE(docs/decisions.md:4053)). This changes the harness against the closed arm, so it is the owner's.
- **(b)** keep 1cface7, and rule now what a recheck-flagged run becomes. If the answer is "invalid and rerun", the scripts must recheck in a staging folder outside `runs/` (`harness.checks.run_checks(path)` takes any path) before the copy. A flagged run then stays off the Mac until after `final.sh`, as RUNBOOK §7 already does for lost runs (FILE(agent/RUNBOOK.md:84)). The rerun goes through `decide` as attempt 2.

Either way, the recheck runs before `due`.

**Required.**

### RA3. Two setup failures become `lost_open`, which counts as cold, so a systematic failure unrelated to the outcome can produce `refutes`
**What is wrong.**
- `decide` gives LOST to any open burst run with two invalid attempts (FILE(docs/probe/20261113_reg20/ops/common.sh:151-152)). It stops first only for `no_errors/client_error`, `manipulation`, `power_limit` (FILE(docs/probe/20261113_reg20/ops/common.sh:130)) and a second `gpu_steady` (FILE(docs/probe/20261113_reg20/ops/common.sh:150)).
- k1 counts `lost_open` toward `refutes` (FILE(analysis/k1.py:224)). `refutes` takes three seeds (FILE(analysis/k1.py:33)) and moves K1 out of the paper's core claims (FILE(docs/decisions.md:4076)).
- The registration counts lost runs as cold because "a stuck open-loop run is the likeliest to fail its checks" (FILE(docs/decisions.md:4067)). That reason does not hold for checks whose inputs lie before the burst ends or outside the server's state:
  - `clean_git`;
  - `kv_capacity`, the KV size from the server log at start-up (FILE(harness/checks.py:152-156 at 1cface7));
  - `trigger`, whether every burst request was sent; the burst runs from 900 s (FILE(harness/checks.py:174-177 at 1cface7)).
- After an invalid run, the queue stops. Starting it again applies the rerun rule "from checks.json alone" (FILE(docs/probe/20261113_reg20/ops/queue.sh:69)). The delegate restarts it, as for REG-19 (FILE(docs/decisions.md:4589)).

**Trace.** A machine-level `kv_capacity` mismatch, say another tenant's memory at start-up, hits seeds 15–17. Each fails twice, and each restart is routine, so all three are `lost_open`. That gives `refutes` after 6 runs ≈ 6.4–7.4 GPU h (DERIVED: 6 × 1.07–1.23), with no stuck state shown.

**Fix.**
- In `decide`, do not give LOST when either attempt's `failed` list holds only checks from a pre-burst or setup class (`clean_git`, `kv_capacity`, `trigger`; the class is BELIEF and the list is for the decision to fix now). Stop for the owner instead.
- This adds a stop and narrows no label: whether such a seed counts as `lost_open` stays the owner's.
- Add sandbox cases.

**Required.**

### RA4. The control decision runs whatever analysis code is in the main working tree; nothing checks it at that moment
**What is wrong.**
- Draft item 12 says "every launch, copy and table first checks that k1's import closure equals the pin's" (FILE(docs/drafts/reg20_ops_decision_draft1.md:248)).
- In fact `mac_checks` runs only at the start of `queue.sh` (FILE(docs/probe/20261113_reg20/ops/queue.sh:16)), of `launch.sh` (FILE(docs/probe/20261113_reg20/ops/launch.sh:18)) and of `final.sh`.
- `copy_verify` does not call it (FILE(docs/probe/20261113_reg20/ops/common.sh:233-245)). Neither does the queue's `control_due` function (FILE(docs/probe/20261113_reg20/ops/queue.sh:33-44)).
- The last check before a control decision is the one at the start of the burst run's `launch.sh`, about 70–80 minutes earlier.
- REG-19 ran its mid-matrix analysis from a pinned worktree, and checked `git diff --quiet HEAD -- analysis harness …` just before it (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:207)). That guard caught the subagent's edit of 2026-11-13 (FILE(docs/decisions.md:4604-4609)).

**Trace (PROBE: `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/c76f1b46-4608-499c-babd-85fa7e8cd4fe/scratchpad/sb_edit.sh`, a copy of the sandbox with the real scripts; the fake launch appends a line to `analysis/k1.py` during seed 15's burst run).**
- `control_due.py` ran once on the edited tree, and `CONTROL_DUE yes` was recorded in `state/control_due.txt`.
- The queue stopped only at the next launch (the control).
- After `git checkout -- analysis/k1.py` and a restart, the queue ran to `QUEUE DONE`, with 5 calls to `control_due.py` in all. Seed 15's decision made on the edited code stood.
- A wrong `no` leaves a cold run without its control. That shows only in the one-time table as `pending_controls` (FILE(docs/decisions.md:4073)), so the control runs after the outcome is read and not "right after" (FILE(docs/decisions.md:4054)). A wrong `yes` spends ≈ 1.1 GPU h (FILE(docs/decisions.md:4097)).

**Fix.** Either of:
- run `control_due.py` and the table from a worktree at a fixed commit, as RUNBOOK §5 asks (FILE(agent/RUNBOOK.md:59)), with `runs/` linked and a clean-status check before each call. Note: in such a worktree, `withheld.lifted` reads the worktree's own `docs/decisions.md` (FILE(analysis/withheld.py:23)). Unless the commit holds REG-19's [RESULT], `find_runs` silently skips REG-19's closed runs (FILE(analysis/withheld.py:69-80)), and the table reads `too_few` with rc 0. So use `AFTERSHOCK_UNSEAL=REG-19,REG-20` for the table;
- or call `mac_checks` immediately before and immediately after the `control_due.py` call, and drop the decision if either fails.

Add a sandbox case like the one above, and correct item 12's sentence.

**Required.**

### RA5. The owner's points have to be ruled before the first launch, not when a stop reaches them
**What is wrong.**
- The draft lets the scripts "stop at that point and wait" until the owner rules on 6 and 9 (FILE(docs/drafts/reg20_ops_decision_draft1.md:12), FILE(docs/drafts/reg20_ops_decision_draft1.md:171)).
- By then the queue output will have shown each earlier seed's cold bit (item 15, FILE(docs/drafts/reg20_ops_decision_draft1.md:284)).
- The draft's own reason for fixing item 6 in advance is that an answer "fixed before any outcome exists cannot depend on one" (FILE(docs/drafts/reg20_ops_decision_draft1.md:167)). The same holds for 9, and for 2 and 8 (RA2, RA6).

**Trace.** Seeds 15–17 show `CONTROL_DUE yes, yes, no`. Seed 18's burst run then hits a client error, and the owner rules on rerun or `not_run` knowing that two cold seeds already make `refutes` one seed away (FILE(analysis/k1.py:233)). The owner may also be away (FILE(docs/decisions.md:4232)), so the GPU waits idle mid-matrix.

**Fix.**
- The `[DECISION] … REG-20 arm A starts` entry may be written only after the owner's rulings on items 2 (its resolution), 6, 8 and 9 are in the log.
- `gate_in_log` could also require those headings.

**Required.**

### RA6. Item 8 (a lost attempt is relaunched and not counted) is the owner's, by the draft's own test
**What is wrong.**
- Item 8(b) sets a standing answer: up to two relaunches per config after a power-off, outside the one registered rerun (FILE(docs/drafts/reg20_ops_decision_draft1.md:195), FILE(docs/decisions.md:4057)). One config could then be launched four times.
- Under REG-17 to REG-19, which the standing instructions point to, each lost relaunch had its own decision:
  - attempt 2 was named in the delegation itself (FILE(docs/decisions.md:4233));
  - attempt 3 was the owner's (FILE(docs/decisions.md:4383)).
- Item 6 calls exactly this kind of change, "fixing the answer now … changes how a registered instruction works", the owner's (FILE(docs/drafts/reg20_ops_decision_draft1.md:154)).
- 8(b)'s premise, "a power-off says nothing about the run", is a BELIEF. A18's reading (2) has losses come sooner under GPU load, and five of seven ends fell during a GPU run (FILE(docs/open-questions.md:61)).

**Trace.** If A18's reading (2) is true, a stuck open run holds the GPU busy for 3000 s. It is the likeliest to be lost and relaunched, up to four launches. The seed then goes to the owner as `not_run`, away from `refutes` (FILE(analysis/k1.py:215)). That is a selection the registration's `lost_open` rule was written to prevent (FILE(docs/decisions.md:4103)).

**Fix.** Mark item 8 as the owner's, and have the owner rule before the first launch (RA5). Record each lost attempt's elapsed time and its arm.

**Required.**

### RA7. The scripts under review are not the scripts the decision would approve, and the draft's status lines are false
**What is wrong.**
- The draft says the scripts "are not committed" (FILE(docs/drafts/reg20_ops_decision_draft1.md:6)), and README.md says "Nothing here is committed" (FILE(docs/probe/20261113_reg20/ops/README.md:3)). Both were committed in c8b482d (`git show c8b482d --stat`).
- Items 2, 8 and 13 are "not yet in the scripts" (FILE(docs/drafts/reg20_ops_decision_draft1.md:317-323)); `final.sh` still uses `uv run` (FILE(docs/probe/20261113_reg20/ops/final.sh:26)).
- RA1–RA4 add more changes.
- `scripts_commit.txt` does not exist yet (`ls` of `ops/`).

**Trace.** The [DECISION] approves c8b482d's behaviour. The commit that runs then holds a recheck, a lost-attempt counter and a table command that no rule F pass has seen, whereas rule F requires the diff to be reviewed (CLAUDE.md §F).

**Fix.** The [DECISION] names the commit that implements every approved change, with its sandbox count. The diff from c8b482d to that commit gets a rule F pass and an owner-proxy pass. Correct the status lines.

**Required.**

[End of part 1; part 2 follows: the optional items, alternative explanations, decisions and GPU hours at risk, and the 17-point table.]

---

[Part 2 of 2] Rule F review of the REG-20 arm A operations decision (draft 1): the optional items, alternative explanations, decisions and GPU hours at risk, and the 17 points.

## Optional

### RA-O1. The seal-file blob check will stop the queue on routine edits, possibly between a burst run and its control
- `mac_checks` requires `analysis/load.py` and `analysis/withheld.py` to be exact blobs (FILE(docs/probe/20261113_reg20/ops/common.sh:37), FILE(docs/probe/20261113_reg20/ops/common.sh:60-62)).
- Three commits since the pin touched them (DERIVED: `git log 1cface7..HEAD -- analysis/withheld.py analysis/load.py`: 72fafb5, ef4dc4e, 69ffedd). Each new registration adds a seal row (FILE(analysis/withheld.py:26-32)).
- A seal commit during seed n's burst run stops the queue at the control's launch until a reviewed commit updates `common.sh`. "Right after" (FILE(docs/decisions.md:4054)) is then lost.
- The worktree fix in RA4 removes this.
- Record, in `queue_done.txt` and the [RESULT], the gap from each burst run's end to its control's start, and whether the boot id changed between them.

### RA-O2. `final.sh` should enforce what item 8 only states
- **The folder set:** list the names of every folder on the Mac that matches k1's patterns (folder names are an allowed read), and require that set to equal the run ids in `queue_done.txt`. Otherwise a lost folder copied "for the record" (FILE(agent/RUNBOOK.md:84)) would raise `n_bad` (FILE(analysis/k1.py:148)).
- **stderr:** refuse a table whose stderr holds a `withheld:` line (FILE(analysis/withheld.py:79)). `final.sh` checks only rc (FILE(docs/probe/20261113_reg20/ops/final.sh:28)).

### RA-O3. The queue does not see the owner overrule the start
The owner may overrule a delegate decision with a [CORR] or a [DECISION] (FILE(docs/decisions.md:4236)). The queue reads only the positive heading (FILE(docs/probe/20261113_reg20/ops/common.sh:83)). Add a stop heading, such as `(owner) REG-20 arm A (stops|is stopped)`.

### RA-O4. One `rerun_ok_<rid>` lifts every stop of that run
When `failed` holds both `no_errors/client_error` and `manipulation`, one record lifts both stops (FILE(docs/probe/20261113_reg20/ops/common.sh:128-131)). The record should name the failure it lifts.

### RA-O5. Item 4's evidence is mis-cited
ops_r3 ran seeds 18 and 19 only (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:17)), so seed 15's closed run did not run "under ops_r3's launch command" (FILE(docs/drafts/reg20_ops_decision_draft1.md:109)). `launch7.sh` also sets no limit (FILE(_to_delete/docs/probe/20261113_reg19/ops/launch7.sh:41)); that it launched seed 15 is a BELIEF this review did not check. Cite seed 15's own launch record.

### RA-O6. Stale notes
- README "Not settled" item 4 calls the recheck the owner's (FILE(docs/probe/20261113_reg20/ops/README.md:96)), while draft item 2 calls it the delegate's.
- README item 9 keeps `uv run` (FILE(docs/probe/20261113_reg20/ops/README.md:87)).
- DESIGN_NOTES gives a different `GATE_PAT` (RA1).

### RA-O7. RUNBOOK conflicts with the pin
- RUNBOOK §3 step 6 and §4 deploy HEAD to the VM after REG-19's [RESULT] (FILE(agent/RUNBOOK.md:48), FILE(agent/RUNBOOK.md:50-56)).
- The scripts require 1cface7 and leave the checkout to hand (FILE(docs/probe/20261113_reg20/ops/README.md:72)).
- Put the order in the decision: deploy, then check out the pin, then the session probe.

### RA-O8. For the owner's information (rule A1), not an ops defect
- `supports` needs all five seeds `recovered_open`, since 4 of 4 gives 0.0625 (DERIVED).
- After the first open seed that is not `recovered_open`, the remaining runs, about 3.5–6 GPU h, can move the outcome only between `refutes` and `inconclusive`. That still changes a decision (FILE(docs/decisions.md:4076), FILE(docs/decisions.md:4079)).
- The registration has no futility stop for arm A.

### RA-O9. The queue prints the failed check names of invalid open runs
`RUN … INVALID failed=…` (FILE(docs/probe/20261113_reg20/ops/queue.sh:69)) shows names such as `no_errors/client_error` and `client_lag`. By T3 these are correlated with a stuck run (FILE(docs/decisions.md:4103)). They are allowed reads and the rerun rule needs them. State this in item 15 next to the control bits.

---

## Alternative explanations the operations would mislabel

1. **`lost_open`, counted as cold.**
   - Registered reading: a stuck run fails its checks (T3).
   - Alternatives:
     - (a) a client-side artifact of about 960 concurrent force-closed connections, which no closed run meets (FILE(docs/decisions.md:4057));
     - (b) A14's recorder death at the pin (RA2);
     - (c) a setup failure (RA3).
   - What separates them:
     - the error texts of the `client_error` records and when they occur, which ALLOWED forbids reading (FILE(docs/probe/20261113_reg20/ops/common.sh:38));
     - the recheck's `recorder` detail (`last_ok_scrape_t`), which ops_r3's filter drops (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:197-201));
     - the failed-check class (RA3).
2. **`unclear`, dropped.**
   - Alternatives: A14 at the pin against a true NaN.
   - What separates them: today's `recorder` coverage (RA2).
3. **`overload_open` against `stuck_open`.**
   - Alternative: a control run after a long gap or a reboot (RA-O1, RA6). The drift run checks only closed seed 15.
   - What separates them: the gap and the boot ids, which are not recorded now.
4. **`recovered_open`.** No ops-specific alternative found. `supports` needs five readings on valid runs with frozen code, provided RA4 is fixed. The registration's alternatives (working set, headroom) stand.

## Can these operations change a decision, and the GPU hours at risk

Yes. The operations decide:
- whether arm A runs at all (RA1);
- whether each control runs (RA4);
- whether a seed is `lost_open` (cold), `not_run` or `unclear` (dropped) (RA2, RA3, RA6);
- whether a table can be computed (RA2).

GPU hours:
- planned arm A ≈ 6.4–7.4 GPU h, plus ≈ 1.1 h per control (FILE(docs/decisions.md:4097));
- ceiling under the current caps: 22 launches (5 burst runs and 5 controls at 2 attempts, plus 2 drift attempts) ≈ 23.5–27.1 GPU h (DERIVED: 22 × 1.07–1.23); item 8(b) raises the ceiling further;
- at risk per trace:
  - RA1 ≈ 11.8–13.5 h;
  - RA3 ≈ 6.4–7.4 h;
  - RA2 ≈ 3.5–7.4 h;
  - RA4 ≈ 1.1 h per seed.

## The 17 points against the registration

| # | Draft says | This review |
|---|---|---|
| 1 | delegate, 1cface7 + recheck | The pin alone is the delegate's, since no commit is registered (FILE(docs/decisions.md:4169)). But "today's checks applied to every run" never reaches a label (RA2). Pin (b) would be the owner's. |
| 2 | delegate (adds stops) | The stop is the delegate's. Its resolution is "marking a run invalid beyond its automatic checks", which is the owner's (CLAUDE.md C), and has to come before the launch (RA2, RA5). |
| 3 | delegate | Agreed; FILE(docs/decisions.md:4053-4054) force it. |
| 4 | delegate | Agreed; the evidence is mis-cited (RA-O5). |
| 5 | delegate | Agreed in design. The claim that the code is the same is not enforced when the code is used (RA4). |
| 6 | owner | Agreed; rule before the launch (RA5). |
| 7 | delegate (unchanged) | Agreed. The setup-class lost case is missing (RA3). |
| 8 | delegate | **The owner's** (RA6). |
| 9 | owner | Agreed; rule before the launch (RA5). |
| 10 | delegate | Agreed; it implements FILE(analysis/k1.py:286). |
| 11 | delegate | Agreed. DERIVED from the `&&` chain (FILE(docs/probe/20261113_reg20/ops/launch.sh:58)): no harness starts below the raised limit. |
| 12 | delegate | It is the delegate's to choose, but the stated per-step check is false (RA4, RA-O1). |
| 13 | delegate | Agreed; not yet applied (RA7). |
| 14 | delegate | Agreed in kind; the pattern is too loose (RA1). |
| 15 | delegate, inherent | Agreed. Its consequence is RA5; add RA-O9. |
| 16 | owner | Agreed. |
| 17 | owner, already decided | Agreed: the delegate reads the owner's general words as covering REG-20, and nothing registered changes. |

[End of part 2 of 2. The full text is also in /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/c76f1b46-4608-499c-babd-85fa7e8cd4fe/scratchpad/review_reg20_ops_r1.md]
