Saved by the agent from the reviewer's own SendMessage call to team-lead (tool-call input, its session 3168253b, line 386, timestamp 2026-11-13T22:14:43.532Z), because the message was never delivered into the main session's transcript. Owner-proxy round 1 on the REG-20 arm A operations decision, draft 1, and its scripts at c8b482d: APPROVE with conditions RB1–RB11 before any REG-20 run and RB12–RB15 in the [DECISION] or the [RESULT]; points 6, 9, 16 and a new 2a stay the owner's.

---

Owner-proxy verdict on REG-20 arm A operations (decision draft 1 and the scripts in c8b482d): APPROVE with conditions. RB1–RB11 must change before any REG-20 run; RB12–RB15 go into the [DECISION] or the [RESULT]. Points 6, 9 and 16, and a new point 2a, stay the owner's; my recommendations on them are marked.

**Files read, in order:** CLAUDE.md; decisions.md lines 4200–4260 (the delegation is at 4231–4237); docs/drafts/reg20_ops_decision_draft1.md; decisions.md 4030–4200 (REG-20's [REG] at 4045, its approval at 4166); decisions.md 4284–4340 and 4502–4609; in ops/: README, PIN_DECISION_DRAFT, DESIGN_NOTES, common.sh, queue.sh, launch.sh, final.sh, control_due.py, session_probe.sh, vm_state.py, and the heads of test_sandbox.sh and test_control_due.py; analysis/k1.py; analysis/load.py (load_run, find_runs); analysis/withheld.py; reg19_resume_decision_draft5.md lines 1–80; agent/RUNBOOK.md lines 1–84; ops_r3/common.sh lines 190–215; PROTOCOL.md lines 60–118; status.md lines 1–60.

**Read only by grep:** the context pack, definitions (cold-backlogged), model.md row 23, open-questions A14 and A18, tools/check_docs.py, and docs/probe/20261113_freeze/closure.py, which I ran.

**Disclosures:** I listed the file names in docs/probe/20261111_reg19/ops/; RESUME.md and the queue_run*_output.txt files appear there by name, and I opened neither. The starting git status showed state/ file names, none opened. Nothing under runs/ was opened, the VM was not contacted, and nothing in the repo was edited.

**Tests reproduced, on fakes only, in my scratchpad:** sandbox 214 of 214, test_control_due 35 of 35. `git status` of the ops folder is identical before and after (PROBE: my runs).

## Answers

**Q1. Do the delegate points stay inside the delegation?**
- **Inside it:** points 1, 3, 4, 5, 10, 11, 12, 13, 14 and 15.
- **Point 2:** adding the stop is inside. What happens after the stop is the owner's (new point 2a, RB2).
- **Point 7:** inside, except draft line 180, which leaves a registered label open (RB7).
- **Point 8(b):** inside, as an operational rule fixed before any REG-20 run exists.
  - It changes no label and no threshold, and not the one registered rerun of an invalid run.
  - Lost runs are not among REG-20's standing instructions (FILE(docs/decisions.md:4057)).
  - I prefer (b) to (a). Under open question A18's reading (2), a power-off is likelier under sustained GPU load, that is, in a stuck run, so (a) would drop stuck seeds (BELIEF).
- **Point 17:** the owner's words are general (FILE(docs/decisions.md:4502-4510)), and REG-20 registers no quiet hours.

**Q2. Can the owner decide points 6, 9 and 16 quickly?** Point 6, yes. Points 9 and 16, no: one has no options and the other misses the freeze (RB8, RB9). Point 2a is missing (RB2). My recommendations are at the end.

**Q3. Would the owner accept the pin, the drift placement and the control rule?**
- **Pin 1cface7: yes.**
  - The harness is byte for byte REG-19's (DERIVED: `git diff --stat a7bb77a 1cface7 -- harness/` is empty, my run).
  - It is the commit that holds what the approval required (FILE(docs/decisions.md:4169)).
  - REG-20's configs, base.yaml and defaults.yaml are unchanged since then (DERIVED: `git diff --quiet 1cface7 HEAD` over them passes, my run).
  - HEAD would put 5ee6e38's changes to loadgen, recorder, run and checks next to the loop flag, against "the only change" (FILE(docs/decisions.md:4052)).
  - It is the same choice the owner made for REG-19 (FILE(docs/decisions.md:4284)).
- **Drift run after seed 17's burst run and its control: yes.** It is the only reading that keeps both FILE(docs/decisions.md:4053) and FILE(docs/decisions.md:4054).
- **control_due.py: yes, after RB1.**
  - It makes the same call with the same arguments as the table (FILE(analysis/k1.py:160), FILE(docs/probe/20261113_reg20/ops/control_due.py:64)).
  - Running no control on `unclear` matches 4054 and FILE(analysis/k1.py:162-163).

**Q4. What must change, and when?** RB1–RB11 before any run; RB12–RB15 later.

**Q5. Rules A5 and H.**
- **A5: no point chooses or widens a threshold after its data could be seen.**
  - 4096, 45 °C, 350 W and the single rerun are registered (4057).
  - 65536 is a setting, not a number that judges data.
  - Point 8(b)'s cap of two relaunches is fixed before any REG-20 run exists.
  - The A5 risk lies elsewhere: stops left without a fixed answer would be ruled while the control bits are visible (points 2, 7, 9). RB2, RB7 and RB8 fix that.
- **H: unchanged.** No point touches the test, the pairing or `k1_outcome`. The Clopper–Pearson duty belongs in the [RESULT] (RB14).

## Items

**RB1 BEFORE. The code check does not run before a control decision.**
- **Evidence:**
  - `mac_checks` runs once, when the queue starts (FILE(docs/probe/20261113_reg20/ops/queue.sh:16)).
  - The loop calls `copy_verify` and `control_due` without it (FILE(docs/probe/20261113_reg20/ops/queue.sh:46-52)).
  - Only launch.sh (FILE(docs/probe/20261113_reg20/ops/launch.sh:18)) and final.sh (FILE(docs/probe/20261113_reg20/ops/final.sh:10)) run it again.
  - A run lasts about 70 min after its launch's check. An edit to k1's import closure in that time reaches control_due.py unseen. That is the path of the 2026-11-13 incident (FILE(docs/decisions.md:4604)).
  - So the draft's "Every launch, copy and table first checks…" (FILE(docs/drafts/reg20_ops_decision_draft1.md:248)) is false for the copy and the control decision.
- **Change:**
  - In queue.sh, make this the first line inside `for turn in {1..80}; do`: `mc=$(mac_checks) || stop "Mac-side check failed before turn $turn: ${mc##*$'\n'}"`
  - Add a sandbox case: analysis/gate.py edited between a launch and its control decision gives QUEUE STOP and no CONTROL line.
  - Draft line 248 becomes: "Every turn of the queue (before each copy, control decision and launch), every launch and the table first check that…".

**RB2 BEFORE. Point 2 gives a false reason, is not implemented, and leaves its stop unanswered.**
- **Evidence:**
  - Draft line 75 says a run that today's checks fail is found "while its rerun is still possible". It is not. Its stored checks.json still says valid, so a rerun gives two valid runs of one config.
  - Two valid runs stop the queue (FILE(docs/probe/20261113_reg20/ops/common.sh:139)) and make k1 raise (FILE(analysis/k1.py:146-147)).
  - No run folder may be edited or removed (CLAUDE.md, "Never").
  - So the owner's only answers are to keep the run or to stop arm A, and until the owner answers, the GPU sits idle.
- **Change:**
  - (i) Replace line 75 with: "A run that today's checks fail is found before a control decision is spent on it. It cannot be rerun: a second valid run of its config stops the queue (common.sh:139) and makes k1 raise (k1.py:146-147). The owner's answer is to keep it as its checks.json says, or to stop arm A."
  - (ii) Port `recheck_ok` with both of ops_r3's guards (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:204-205)), take the expected run count from the `copied_*` records, and add sandbox cases. Call it after each copy, before `control_due`, and in final.sh.
  - (iii) Add owner point 2a (see the recommendations).

**RB3 BEFORE. There is no path for "no rerun", so any refusal ends arm A without a table.**
- **Evidence:**
  - `decide` returns 2 in three cases: an unrecorded stop-and-ask failure, a lost run, and spent attempts (FILE(docs/probe/20261113_reg20/ops/common.sh:148-153)).
  - `next_step` passes that up (common.sh:205), and the queue stops (queue.sh:47).
  - No record settles a slot otherwise, so queue_done.txt is never written and final.sh refuses (FILE(docs/probe/20261113_reg20/ops/final.sh:17)).
  - Every refusal the draft relies on is therefore unexecutable: point 6(a)'s "A refusal leaves the seed `not_run`" (draft line 157), point 7's per-case answers, point 8's harness death, and point 9.
- **Change:**
  - Add a record `state/settle_<run id>.txt`, written only under a recorded owner decision or a rule of this decision, which it names.
  - For an open burst config, `decide` then treats the slot as settled `not_run`: the run is copied, nothing more is launched, no control runs, and the slot line reads `s<n> not_run <rid>`.
  - For a control, the slot reads `control_not_run`. k1 then gives `pending_control`, and the outcome is the registered `pending_controls`.
  - final.sh accepts both slot lines. Add sandbox cases for each.

**RB4 BEFORE. Lost folders can change the table's inputs.**
- **Evidence:**
  - `find_runs(…, valid_only=False)` loads every matching folder that has a config, including one without checks.json (FILE(analysis/load.py:31), FILE(analysis/load.py:42-44)), and `_runs` counts it as bad (FILE(analysis/k1.py:144-148)).
  - So one lost folder plus one invalid run reads `lost_open` (FILE(analysis/k1.py:286)) where the queue's own count reads `not_run`.
  - The order constraint (draft line 203) is not enforced: final.sh checks only the runs that queue_done names (final.sh:18-22).
- **Change:**
  - (i) final.sh, after line 22: refuse if any `runs/*_<cfg>` folder of the eleven configs lacks `state/copied_<rid>.txt` or a checks.json.
  - (ii) Decision text: "A REG-20 folder without checks.json is copied only to a holding folder outside every runs/ (as REG-19's resume, draft 5 item 5) until REG-20's [RESULT]. If it is ever placed in runs/, `analysis.k1 reg20` is run again, and an [OPS] or [CORR] entry says whether its output changed."
  - (iii) Implement 8(b), which I approve, with sandbox cases.

**RB5 BEFORE. The table's interpreter, and the gate computed once.**
- **Change:**
  - (i) In final.sh line 26 and its comment at line 5, replace `uv run python` with `$PY`. This is point 13, which I accept.
  - (ii) Add to point 14: "The gate is computed once, after REG-19's [RESULT] is committed, as `.venv/bin/python -m analysis.k1 reg20_a_may_start` from the repo root with mac_checks passing. No AFTERSHOCK_UNSEAL: it reads only REG-19's runs. Its stdout and stderr are saved under a stamp in docs/probe/20261113_reg20/ and committed at once, alone. The heading '… REG-20 arm A starts' is written only if that file reads 'may_start': True, and the entry quotes it verbatim."
- **Evidence:**
  - "Computed once" (FILE(docs/decisions.md:4051), FILE(docs/decisions.md:4168)).
  - `gate_in_log` checks only the headings (FILE(docs/probe/20261113_reg20/ops/common.sh:77-87)).
  - RUNBOOK's command is a by-hand line (FILE(agent/RUNBOOK.md:63)).

**RB6 BEFORE. Nothing written moves the VM to the pin, and four texts contradict the draft.**
- **Evidence:**
  - RUNBOOK says "then deploy HEAD (§4)" after REG-19's [RESULT] (FILE(agent/RUNBOOK.md:48)), and §4 pulls main (FILE(agent/RUNBOOK.md:52-53)).
  - The scripts do not check out the pin (FILE(docs/probe/20261113_reg20/ops/README.md:72)). It fails safe, since launch.sh stops on any other tree (launch.sh:47), but no written step reaches 1cface7.
  - README:3 and draft line 6 say the files are not committed; they are, in c8b482d.
  - README:93 (the pin needs the owner) and README:96 (the recheck is the owner's call and not implemented) contradict draft points 1 and 2.
- **Change:**
  - Decision text: "VM: push main to the VM's bare repo (RUNBOOK §4 step 1). On the VM, `git fetch origin && git checkout --detach 1cface77ca001cdf5d90de9313ddd4a3af4569a1`. Then `git rev-parse HEAD` equals the pin and `git status --short` is empty. Never while a run is in progress."
  - RUNBOOK:48 "then deploy HEAD (§4)" becomes "then, if REG-20's gate passed, check the VM out at 1cface7 (REG-20 ops decision); otherwise deploy HEAD (§4)".
  - RUNBOOK:64, row 2a, gains "pin 1cface7; no worktree (ops decision point 12)".
  - README:3, :93 and :96 and draft line 6 are brought in line with the decision.

**RB7 BEFORE. Point 7 leaves a registered label open.**
- **Evidence:**
  - Draft line 180 says "Whether a seed lost to two such failures should count as `lost_open` (cold, by k1) is for the owner, if it ever happens."
  - The registration already fixed this: `lost_open` is a "burst run invalid after its rerun", for any failed check (FILE(docs/decisions.md:4067)), and k1 has no branch on the failure type (FILE(analysis/k1.py:286)).
  - Ruling on it later, with the control bits visible, is what rule A5 forbids.
- **Replace that sentence with:** "By REG-20's label, a burst run invalid after its rerun is `lost_open` and counts as cold, whatever check it failed (decisions.md:4067; k1.py:286). At each of these stops the owner decides only whether the rerun is made (a second failure is then `lost_open`) or not (the seed is then settled `not_run` by RB3's record and leaves n). If the open arm's burst fails to fill the pool systematically, allowing reruns would make each such seed `lost_open` and could reach `refutes` on a shock that was never delivered. That weighs against a rerun after `manipulation`."

**RB8 BEFORE. Point 9 has no options and no recommendation (draft lines 209–219).**
- **Write these options into it:**
  - (a) One further attempt of the control, under the registered outcome row "run the control, then compute again" (FILE(docs/decisions.md:4073)). A further failure stops arm A.
  - (b) No further attempt. The slot is settled (RB3), k1 gives `pending_control`, the outcome is `pending_controls`, and K1 gets no statement.
  - (c) Count it as `cold_control`. Not possible without changing k1 (FILE(analysis/k1.py:166-167)), which the approval fixed.

**RB9 BEFORE (the text). Point 16 misses the freeze.**
- **Evidence:**
  - analysis/withheld.py and analysis/load.py are in REG-21's and REG-22's freeze. PROBE: my runs of `python3 -I docs/probe/20261113_freeze/closure.py` on analysis/k3w.py and on analysis/c2.py both list both files.
  - status.md bars any commit to frozen files until both batch 2s are computed or declared not computed. So "after final.sh" (draft line 299) is not enough.
  - The seal lifts only when "· [RESULT] REG-20" comes right after the date (FILE(analysis/withheld.py:46)).
  - check_docs requires only one tag and a RUN( citation (FILE(tools/check_docs.py:124-129)).
- **Write these options into it:**
  - (a) If arm A gives `supports` or `supports_no_mechanism`, its outcome is reported in an entry whose heading does not lift the seal, for example "## <date> · [RESULT] K1 arm A, from REG-20's table (seal kept until arm B)". "[RESULT] REG-20" follows arm B. For any other arm A outcome, arm B never runs, and "[RESULT] REG-20" is written at once.
  - (b) A seal on `*_l1pl350ol_r2.5_*`, lifted by "[RESULT] REG-20 arm B", added after final.sh and after both batch 2s.
  - (c) Accept arm B unsealed.

**RB10 BEFORE. Point 6 needs its residual risk stated.**
- **Add to option (b):** "Residual risk: a client error in open runs that are not stuck, from a cause the allowed reads cannot see, would make each such seed `lost_open` without a stop, and could reach `refutes`. BELIEF that this is unlikely: REG-10's open-loop run at λ = 2.4 was valid and recovered (FILE(docs/decisions.md:4085)), and the 65536 limit removes the descriptor cause named in review T3 (FILE(docs/decisions.md:4103))."

**RB11 BEFORE. Commit this decision before REG-19's table.**
- Commit the [DECISION] before the first `reg19_final_*` file exists. If that is not possible, the entry says so and names any of its points written after REG-19's table was seen.
- **Why:** rule A5. Today none of the 17 points depends on REG-19's outcome, and committing first keeps that checkable. Arm A cannot start before this entry anyway, so the order costs no GPU time (DERIVED).

**RB12 LATER ([DECISION]).** State the deviation from PROTOCOL §5 (FILE(PROTOCOL.md:78-79)):
- REG-20's stored checks are the pin's, which lack A14's coverage checks. Today's checks are applied read-only (point 2), as REG-19's resume did (draft 5, point 4, first bullet).
- Under option (c), a recorder death is detected, not prevented.

**RB13 LATER ([DECISION]). Point 4 cites the wrong script.**
- Seed 15's closed run was made on 2026-11-12, before ops_r3 existed, by docs/probe/20261111_reg19/ops/ (queue_reg19.sh calls launch3.sh, FILE(docs/probe/20261111_reg19/ops/queue_reg19.sh:14)).
- **Replace draft line 109's second sentence with:** "It ran on 2026-11-12 under docs/probe/20261111_reg19/ops/, whose launch commands set no limit (FILE(docs/probe/20261111_reg19/ops/launch3.sh:27); launch4.sh:31, launch5.sh:32 and launch6.sh:36 carry the same command). ops_r3's command is the same in substance (FILE(docs/probe/20261113_reg19/ops_r3/launch.sh:51))."
- The recommendation, option (b), stays.

**RB14 LATER ([RESULT]).**
- (i) **Rule H.** Give k of n per arm with the one-sided 95 % Clopper–Pearson upper bound from `stats.cp_upper`. McNemar's p comes first, with Fisher's beside it (FILE(analysis/k1.py:220)). The drift check is labelled a single seed, and each control a single run.
- (ii) **Arm differences.** The open arm's harness shell runs at 65536 open files, the closed arm's at the default 1024 (FILE(agent/RUNBOOK.md:28)). BELIEF that this does not matter: the closed arm held 149–226 sessions in service (FILE(docs/decisions.md:4089)). What vLLM 0.32.0 does with its own limit is unchecked; add that to open-questions.
- (iii) **Where `supports` went out of reach.**
  - With all five closed runs cold, as the gate requires, one open seed that is cold, unclear or partial gives McNemar p ≥ 1/16 > 0.05 (DERIVED from `k1.mcnemar_one_sided`: (5,0) gives 1/32 and (4,0) gives 1/16).
  - So the first `CONTROL_DUE yes` or `unclear` line in the queue output shows that `supports` is out of reach.
  - The [RESULT] names that line, and states that no discretionary ruling was made after it.
- (iv) **The judged code.** State that it is k1's module-level closure, and that the functions on reg20's path reach no import made inside a function. DERIVED: my AST trace of gate.burst_end, overlap_share, shock_size and turn0_share, margin.is_burst_request, load._level, find_runs and load_run, and all of derived.

**RB15 LATER (minor).**
- queue.sh:68 lets a restart go on with the run after a nofile WARN, with no record.
- Require `state/nofile_ok_<rid>.txt`, logged in an [OPS] entry.
- It costs nothing: by the `&&` chain (launch.sh:58), a run with a low or missing nofile line should be impossible (DERIVED).

## Recommendations on the owner's points (recommendations, not decisions)

- **2a (new): keep the run as its checks.json says, and go on.**
  - The [RESULT] names the run and its recomputed `failed`. As a second line that changes no label, it also gives the outcome with that seed counted `lost_open`.
  - **Why:** a rerun is impossible (RB2), and a stop would idle the GPU for a question with one usable answer.
- **6: option (b), with RB10's sentence.**
  - A stuck open run is the likeliest to end in client errors (review T3). Under (a), a refusal drops the seed (`not_run`), which is the bias T3 named. Under (b) the seed counts as cold, against K1, which is what a skeptic wants.
  - Fixed now, the answer cannot depend on the control bits.
- **9: option (a).**
  - The seed is already cold for the test (`pending_control` is in OPEN_COLD, FILE(analysis/k1.py:176)), so a third control run cannot move McNemar's p. It decides only between `stuck_open` and `overload_open`, and the registration's own row orders it (4073).
  - Keep the stop for a drift run that fails twice. Two failures point at the machine, and the open runs' failures would then count as cold.
- **16: option (a).** No frozen file changes. The cost is that arm A's folders stay sealed until arm B ends, which happens only after `supports` or `supports_no_mechanism`.
