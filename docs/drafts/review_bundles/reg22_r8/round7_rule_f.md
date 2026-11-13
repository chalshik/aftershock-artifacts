# Rule F round 7 on REG-22 draft 12 (agent a7e69db175dbd3a1d), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T12:08:49.781Z), no word changed. It saw the bundle `docs/drafts/review_bundles/reg22_r7/` and the code at `ffc76b3`. Its required items W1–W5 are called Y1–Y5 in the drafts, to keep them apart from the owner-proxies' W and X items.

---

Rule F review of REG-22, draft 12 (round 7): NOT READY

S1–S3, U1, U2, M1, M2 and V1 are in, and most of draft 12 holds. Five items are still required, all text only. Each one leaves a reading that someone could choose after seeing data, and the two readings give opposite outcomes.

**Your two questions:**
- **S3 + U2 (W1): yes, two readings remain under (b) in which a later saved run sets the time.**
  - "That batch's first run" is not scoped. If it means the batch's command only, a table printed earlier from a REPL or `python -c` does not count, and the later saved command run sets the time.
  - The fallback is "never later than the true time" only if no such output came before the owning registration's entry commit. The entry does not state that.
  - Under (c), REG-22's functions are pinned to `727d1f2`, so the timing barely matters there.
- **O-3 after the record: you are right, it adds no "no record" trigger.** The record is the first run, so later prints are later runs.
- **O-3 before the record: it does add one (W2).** Read literally, "a value that a row of `reg19_table` holds" includes `seed`, `runs` (the run-folder names) and `exposed`. Run ids have been printed since 2026-11-11 (the harness's `start` event, the queue's allowed `run_id` lines). On that reading, the first "table" was never saved, so there is no record and batch 2 is already lost.

**The other three required items:**
- **W3 (my error):** my round-6 O3 lets a statement made before `final.sh` leave the window up to the record's stamp unattested.
- **W4:** for a lost record, REG-22's copy of the shared passage lacks REG-21's clause on whether the record's seed check is made. That is a difference in substance, not only in cross-references.
- **W5:** the freeze keeps T1's "a rule F review that passed its diff with no open required item" next to V2's owner-proxy clause. That gives two readings for a NOT READY review whose items were later written in.

Line numbers refer to `docs/drafts/review_bundles/reg22_r7/registration_draft12.md` (190 lines).

**Bundle and code checks:**
- Draft 12 is byte-identical to `docs/drafts/reg22_draft12.md`.
- The draft-11 copy is the one I reviewed in round 6.
- The bundle diff equals a fresh diff.
- `round6_rule_f.md` equals `rulef-reg22-draft11-r6.md`.
- `final.sh`, `common.sh` and `delegation.md` are unchanged.
- At HEAD `b8ea915`, `git diff ffc76b3 HEAD -- analysis harness tests configs pyproject.toml uv.lock` is empty.

## 1. Items, one line each

**Round 6:**
- **S1:** FIXED in line 133 (committed before batch 2's command, and "what it states governs"). My O3 add-on opens W3.
- **S2:** FIXED in lines 133 and 64. W4 is the missing mirror clause. S2 also removes a "not computed" case that both owner-proxies had accepted (REG-22's on draft 11, its reason 4; REG-21's on draft 20, its reason 3c), so it needs both owner-proxies (Section 4).
- **S3:** PARTLY, in lines 124 and 130 (W1).
- **Round-6 O1:** FIXED with M1's method (line 132). The names come from a listing of the directory. Every control that `control_readout` can glob matches `*_stage2_control_l1pl350cl_r*`: REG-11's override `stage2_control_l1pl350cl_r2.4` (FILE(analysis/c2.py:384)), the names derived from `burst_…` (c2.py:299), and REG-19's controls. The `confirm_` run has no control.
- **Round-6 O2:** FIXED, stricter, as M2.
- **Round-6 O3:** see W3.

**Owner-proxy on draft 11:**
- **U1:** holds in lines 132 and 133. Reach, hunks, `%ct` and reviews are facts; an omission is a [CORR]. See optional O1 on the word "reach".
- **U2:** taken, with the change to "the entry commit of the registration that owns the batch". That change is correct for (c), but see W1.
- **T3:** withdrawn, accepted.

**REG-21's rounds:**
- **V1:** holds. A value returned inside `reg19_step` is not output (FILE(analysis/gate.py:2038)).
- **V2:** see W5.
- **V3/M1:** holds.
- **M2:** holds.
- **O-2:** holds; these are facts in git.
- **O-3:** see W2.
- **O-6:** holds; it is stricter.

## 2. The code

There is no code change, so round 3's traces t01–t06 stand. Checked this round:
- **The SEALS exemption.** `sealed_by` looks only at a folder's name (FILE(analysis/withheld.py:54–60)). `find_runs` applies the seal before it loads anything (FILE(analysis/load.py:42)). So a tuple that matches none of the folders the command can glob has no effect on that command, provided the names come from the directory and not from `find_runs`. Draft 12 does take them from the directory.
- **The fields of a `reg19_table` row:** `seed`, `runs` and `exposed`, alongside the outcome values (FILE(analysis/gate.py:2055–2056)). `exposed` is fixed from the schedule alone (FILE(analysis/gate.py:1811–1819)). `reg19_cold_side` is at FILE(analysis/gate.py:1834).
- **What the harness prints.** It prints `[run] start {run_id: …}` (FILE(harness/run.py:143), printed at :80). Among the lines of a launch log, the queue scripts may read only those holding `run_id` or `[run] checks` (common.sh:34).
- **The shared passage, compared sentence by sentence with REG-21 draft 21's line 107.** It is identical except for the cross-references and REG-21's clause on the lost record: "(duty (b) then compares its first two lists; the record's list does not exist)". REG-22 has no counterpart to that clause (W4).

## 3. The text

### 3.1 W1: S3 + U2 under (b) and (c), your first question

Line 124's fallback uses "that batch's first run", which is never defined. The record passage defines REG-19's table by printed output from any entry point (T6/V1); nothing here does the same for a batch-1 table.

**Trace under (b):**
- At 09:00 the agent, debugging a readout, runs `python -c "from analysis import c2; print(c2.reg22_table())"` on the real runs.
- At 09:30, X lands: a reviewed change to a REG-21 threshold, after D, the commit the deferral [DECISION] names.
- At 10:00 the command `uv run python -m analysis.c2 reg22` runs, saved and committed alone.
- **Reading 1 (first run = the command):** the first run did write its file, so no fallback applies. X is an ancestor and earlier than 10:00, so it counts as before. A5 is not triggered, and REG-21 keeps its labels.
- **Reading 2 (first run = any printed output):** the fallback applies. X comes after min(E22, D), so it counts as after, A5 applies, and REG-21 loses its labels.
- These are opposite outcomes, read after REG-22's batch 1.

**The premise behind your choice of fallback** ("the owning registration's entry is never later than the true time") holds only if no such output came before the entry commit. Line 66 ("Computed by registered functions on these runs, besides the tables above") lists other computations. It does not say that `c2` was never run on the 13 real runs.

**Under (c)** the batch is REG-21's batch 1. REG-22's constants and functions "must be those of `727d1f2`" whatever the time, so the fallback's timing hardly matters there. Its mirror in REG-21's own order text was not checked.

### 3.2 W2: O-3's breadth, your second question

- **After the record: agreed.** "No record" depends only on the first run. Later prints (REG-20's gate, REG-21's batch 2, a `reg19_cold_side` call while writing the [RESULT]) are later runs. A lost record is now S2, which makes batch 2 retrospective, not "no record".
- **Before the record: there is a reading on which batch 2 is already lost.**
  - Line 133 counts "any other function that prints, for a REG-19 run, a value that a row of `reg19_table` holds", from "output computed on REG-19's own run folders", printed "to a terminal, a file, a notebook or a log".
  - The parenthesis "(a verdict, an outcome or the completion rate `c` …)" gives examples; it is not a closed list.
  - A row also holds `seed`, `runs` and `exposed`.
  - Run ids of REG-19's runs have been printed since 2026-11-11: the harness's `start` event, the queue's allowed `run_id` lines, `vm_state` and the recheck's `run` field.
  - Read literally, the first "REG-19's table" was printed then and was not saved. So there is no record, and batch 2 is not computed.
- The intended reading is plain, but a reader can choose the literal one after REG-19's table. Its outcome is the opposite. The same words are in REG-21's line 107.

### 3.3 W3: the S1 statement before `final.sh` (my error, from my round-6 O3)

- Line 133 requires a statement "that no run that gave REG-19's table is known to have started before the record's stamp". It then adds: "it is committed before `final.sh` runs where it can be".
- A statement committed at time T_s, before `final.sh`, cannot speak about the record's stamp, which does not exist yet.
- **Reading 1:** that one statement meets the duty. Then the window [T_s, stamp) is attested by no one, and K1's protection lapses for an unsaved run inside it.
- **Reading 2:** a statement up to the stamp is still due before batch 2's command.
- My O3 text caused this. Log it as my error.

### 3.4 W4: lost record and the mid-matrix check

- With S2, a lost record makes batch 2 "retrospective, if the other rules let it be computed".
- Line 64 also lists "the record's output … does not hold the seeds that REG-19's final [RESULT] counts".
- With the record lost, that output does not exist:
  - **Reading 1:** the condition cannot fail, so batch 2 is computed and labelled retrospective.
  - **Reading 2:** it cannot be checked, so batch 2 is not computed.
- REG-21's copy settles the matching case: "duty (b) then compares its first two lists; the record's list does not exist". REG-22's copy does not, so the two passages differ in substance.

### 3.5 W5: "passed … with no open required item" next to V2

- Line 132 keeps a pre-cut hunk only with "a rule F review that passed its diff with no open required item, and an owner-proxy pass that approves that commit and states that every required item of that rule F review is met in it".
- Take the study's usual case: rule F returns NOT READY on a draft diff, its items are written into the commit, and the owner-proxy states they are met.
  - **Reading 1:** the review did not "pass", so batch 2 is retrospective.
  - **Reading 2:** no required item is left open, so the hunk keeps batch 2's standing.
- The [RESULT] writer settles this "from those committed texts alone", after the data.
- REG-21's V2 has only the second half, so the two freezes also differ.
- The case is likely: the owner-proxy expects REG-20 to touch `k1.py` or `gate.py`, and REG-20's rule F rounds may well end NOT READY.

### 3.6 Is anything looser than draft 11? No.

- M1's list is a superset of what the command can glob.
- M2 counts as after every commit that was rewritten after the stamp or whose date was not set from the clock.
- O-6 widens what counts as a copy.
- S1 moves a choice to before the data.
- S2 swaps a way to lose batch 2 after the data for a retrospective label.
- U1 removes the option of losing standing by leaving something out.
- W1–W5 are double readings, not loosenings of the rules.

## 4. Verdict: NOT READY

### REQUIRED (text only)

W2, W3 and W4 are in the shared passage, so mirror them in REG-21's line 107. W1 has a mirror in REG-21's order text if it has the same test.

**W1 (line 124).**
- After "is tested as the record's cut is:" insert:

  "a batch's first run is the first printed or displayed output, by any entry point (the batch's command, `python -c`, a REPL, another module), of that batch's table (`c2.reg22_table`, or under (c) `k3w.reg21_table`) on real run folders, or of a label or judged value it gives for one of that batch's runs (for REG-22, a result of `c2.levels`, `c2.links` or `c2.sustain`); the registration that owns the batch states in its entry that none was printed before its entry commit, or gives the time of the first;"
- Replace "the batch's table counts as existing from the earliest of the entry commit of the registration that owns the batch and" with:

  "the batch's table counts as existing from the earliest of the time of that first output where it is known, the entry commit of the registration that owns the batch and"

**W2 (line 133).** Replace "or of any other function that prints, for a REG-19 run, a value that a row of `reg19_table` holds (a verdict, an outcome or the completion rate `c`; `reg19_cold_side`, FILE(analysis/gate.py:1834), for one)" with:

"or of any other function that prints, for a REG-19 run, a value that a row of `reg19_table` holds and that the run's recorded data decide (a verdict, a label, an outcome, `c1`, `c`, `q_ratio`, an emptying, `rewarmed`; `reg19_cold_side`, FILE(analysis/gate.py:1834), for one); the seed, the folder names (`runs`), `exposed` and any value the config alone fixes are not REG-19's table"

**W3 (line 133).** Replace "it is committed before `final.sh` runs where it can be, which makes it blind to REG-19's table too." with:

"it covers every run up to the record's stamp; where it can be, a first statement, covering runs up to its own commit, is also committed before `final.sh` runs, which makes that part blind to REG-19's table too."

**W4 (line 133).** After "and batch 2, if the other rules let it be computed, is labelled retrospective" add:

"(the check of the record's seeds under "Runs" is then not made; the record's output does not exist)"

**W5 (line 132).** Replace "a rule F review that passed its diff with no open required item, and an owner-proxy pass that approves that commit and states that every required item of that rule F review is met in it" with:

"a rule F review of its diff, READY or NOT READY, and an owner-proxy pass that approves that commit and states that every required item of that rule F review is met in it (a rule F review with no required item needs no such statement)"

### OPTIONAL

- **O1 (line 132, "reach").** After "(a hunk in a function body that is not reached is outside)" add:

  "(reach is static: a function that `reg22_table` or `reported_counts` calls, directly or transitively, on any branch, and the module constants those read, as line 131 defines the judged path)"

  This settles whether a branch not taken on batch 2's data counts as outside, and it agrees with U1's "facts about the code".
- **O2 (lines 124 and 130), a P2 for batch stamps.** A batch file whose stamp is later than its commit's committer time is treated as a first run that did not write its file this way, so the fallback applies.

### Process

The owner-proxies must pass:
- S2: it removes a "not computed" case that both owner-proxies accepted.
- W1: an order rule.
- W2 and W4: the record passage, in both registrations, word for word.
- W5: which reviews keep a hunk.

### Can it change a decision?

Unchanged from round 6: line e at P ≈ 0.0017 to 0.084, batch 1 at about 0.05 (BELIEF), 0 GPU h.

## 5. What I could not check

- **Not opened, as instructed:** `runs/`, the backups, `state/` file contents and probe outputs.
- **Whether `c2` has ever printed `reg22_table` or a label for the 13 real runs before now.** This is W1's premise. No text I read says either way.
- **Whether any REG-19 outcome value has been printed before the record** other than the run ids and seeds named in W2.
- **REG-21 draft 21 beyond line 107:** its order text (W1's mirror) and its freeze (W5).
- **Unchanged limits:** commits on the VM, pushed history, and `pytest` not rerun. Nothing was written into the repo.
