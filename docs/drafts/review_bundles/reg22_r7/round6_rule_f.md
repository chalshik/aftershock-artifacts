# Rule F round 6 on REG-22 draft 11 (agent a7e69db175dbd3a1d), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:58:47.594Z), no word changed. It saw the bundle `docs/drafts/review_bundles/reg22_r6/` and the code at `ffc76b3`. Its items S1–S3 are REG-22's.

---

Rule F review of REG-22, draft 11 (round 6): NOT READY

Most of draft 11 holds:
- R2, R3 and R4 are fixed.
- O1, O2 and O3 are in.
- The owner-proxy's T1, T2, T4 and T6, REG-21's P1–P3, and L2 all hold.
- The record passage is the same as REG-21 draft 20's line 107 apart from cross-references.

**I accept L1 and withdraw my R1.** For every fact git holds, a missing or wrong citation now changes no label (3.1).

Three items are still required. Each is text only, and each gives someone a choice, made after seeing data, that decides whether batch 2 or REG-21's labels govern:
- **S1, the "no earlier run" statement.** It is the one fact with a label consequence that git does not hold, and it is still written after batch 2's output exists.
- **S2, a lost record.** "A saved record lost … batch 2 is not computed" reopens the kill switch that P3 closed. An innocent `git clean` is enough.
- **S3, order (b).** Order (b) has no K1: a first batch-1 run that was not saved lets a later saved run set the time.

**The two routes you asked about:**
- **T1/L2 freeze:** opens nothing that draft 10 closed; it is stricter.
- **SEALS exemption:** opens one narrow route, readouts only (optional O1).
- **O-c's new wording:** opens one reading for a rebase that keeps old dates (optional O2).

**Process:** the owner-proxy's T3 was a "before the entry is appended" condition of its APPROVE. Draft 11 does not meet it, so the proxy has to accept L1 in its place in a new pass. The [DECISION] (delegate) cannot otherwise name, as draft 11's line 4 promises, a sentence for every condition in force.

Line numbers are those of `docs/drafts/review_bundles/reg22_r6/registration_draft11.md` (187 lines).

**Bundle and code checks**
- `registration_draft11.md` is byte-identical to `docs/drafts/reg22_draft11.md`.
- The draft-10 copy is the one I reviewed in round 5.
- The bundle diff equals a fresh `diff`.
- `final.sh` and `common.sh` equal their committed text at HEAD `346ee6c`.
- `round5_rule_f.md` equals `rulef-reg22-draft10-r5.md`.
- `git diff ffc76b3 HEAD -- analysis harness tests configs pyproject.toml uv.lock` is empty.

## 1. Items, one line each

**Round 5:**
- **R1: withdrawn.** L1 is the better argument (3.1). This is my error, logged here: R1 tied a label to what the writer of the [RESULT] cites, after batch 2's output exists.
- **R2: FIXED.** Line 64 lists the mid-matrix record. Line 133 says "batch 2 is not computed (a case listed under "Runs")".
- **R3: FIXED** (line 124: "first commit that adds"; "at once and alone" is a duty; line 130: "committed at once and alone"). See S3, which goes further.
- **R4: FIXED** (line 133; "or a copy of them" is stricter).
- **O1: FIXED** (line 133, in P2's words).
- **O2: FIXED** (line 132: reviews committed before the cut; the [RESULT] lists each hunk with its commit, `%ct` and reviews).
- **O3: FIXED** (line 21).

**Owner-proxy on draft 10:**
- **T1: holds** (line 132). The exemption covers only the bodies of the five readouts. It needs a rule F review that passed with no open required item, and the hunk and its review must both be committed before batch 1 (order (b)'s test) and before the cut.
- **T2: holds** (line 135).
- **T3: not met.** By design it is replaced by L1, which needs the proxy's acceptance (Section 4).
- **T4: holds** (P2's words).
- **T5: met outside the entry.** agent/RUNBOOK.md:34 and :45 strike the old unsaved step and run `final.sh`. agent/PLAN.md:56 says "never `analysis.gate reg19` by hand".
- **T6: holds** (line 133).

**REG-21's rounds, as carried into REG-22:**
- **P1: holds.**
- **P2: holds.** A stamp later than the record's commit is a fact in git, and it labels batch 2 retrospective.
- **P3: holds.** Its last sentence is altered by the agent's added sentence (S2).
- **L1: accepted.**
- **L2: holds** (lines 132 and 135).
- **O-b: holds, but too narrow** (optional O1).
- **O-c: one reading is looser than draft 10** (optional O2).
- **O-f, first half: holds** (line 130).

## 2. The code

There is still no code change, so round 3's traces t01–t06 stand. Checked this round:

| What | Where | What it shows |
|---|---|---|
| `withheld.SEALS` entries | FILE(analysis/withheld.py:26) | Each is (registration, one pattern over the folder name, lifting heading) |
| `sealed_by` | FILE(analysis/withheld.py:54–60) | It returns the first still-sealed tuple whose pattern matches by `fnmatch.fnmatchcase`, and evaluates `lifted` only after a match. So a tuple whose pattern matches none of the folder names the command globs has no effect on that command. |
| `find_runs` | FILE(analysis/load.py:41–44) | It loads every matching folder that `keep` lets through and has `config.yaml`, before it filters on validity |
| Batch 2's selection | FILE(analysis/k3w.py:347) | It globs only the burst pattern |
| Batch 1 | FILE(analysis/c2.py:401) | It looks up exact folder names |
| `control_readout` | FILE(analysis/c2.py:302) | It globs `*_<control config>`, every attempt of that control included. This matters for optional O1. |
| `reg19_step` | FILE(analysis/gate.py:2036–2041) | It computes `reg19_pair` internally and prints only `done` and `continue`, consistent with line 133's exclusion |
| `reg19_pair` / `reg19_table` callers | grep of `analysis/` and `tools/` | Called only inside gate.py (:2038, :2052) |

**The shared passage.** I cut both texts from "Here "REG-19's table"" to the end of the citation sentences and diffed them sentence by sentence. They differ only in four cross-references:
- the mid-matrix consequence;
- the cut's scope list;
- the "no record" reference;
- the list of consequences.

## 3. The text

### 3.1 Testing L1, and S1

L1 says the citations are facts in git and the label follows from the facts alone. I tested each kind of commit the passage relies on. Each has its consequence in its own rule, whether or not the [RESULT] quotes it:

| Commit relied on | Its consequence, if it is not before the cut |
|---|---|
| This entry's commit | The commit-order bullet: retrospective |
| A hunk under the freeze | Line 132: retrospective |
| The reviews of that hunk | Line 132 (L2): retrospective |
| A seed or validity-flag entry | Line 64: not computed |
| The record's own commit | It counts as after |
| A stamp later than the record's commit | P2: retrospective |

My R1 trace (ancestry checks given without `%ct`) is covered: each `%ct` is a fact, and the freeze, "Runs" and the commit order use it directly. Under draft 9, the writer could demote batch 2 by leaving a citation out. Under draft 11 the writer cannot.

**S1. One fact with a label consequence is not in git.** It is whether a run that gave REG-19's table started before the record's stamp (K1: no record, so batch 2 is not computed). Line 133 has the batch-2 [RESULT] "state" that none is known, and that [RESULT] is written with batch 2's output in hand.

Trace:
- Last week, a hand call of `reg19_pair(15)` was made at the pin while debugging, and not saved. Under T6, that counts as REG-19's table.
- Later `final.sh` makes the record, batch 2 is computed, and its labels are known.
- The writer now chooses:
  - disclose the earlier call: no record, so batch 2 is not computed;
  - write "none known": batch 2 governs.
- This is a choice after batch 2's data, and L1's reasoning ("facts in git") does not reach it.
- Committing the statement before batch 2's command makes the choice blind to batch 2's output. It is still made with REG-19's table public; that is a limit (optional O3 shrinks it).

### 3.2 S2: "lost" reopens the lever that P3 closed

The agent's added sentence (line 133, and line 64 "or the saved record is lost"):

"A saved record lost against that rule is a breach, reported; the cut is then unknown, and batch 2 is not computed".

Trace:
- `final.sh` saves the pair at 12:00Z, and the table is on screen.
- Before anyone commits it, `git clean -fdx` or `git stash -u` removes the untracked files. This could be innocent or chosen.
- Under draft 11, batch 2 is not computed.

That is the same switch P3 removed for "not committed", and the same one K3 removed for "committed with other files": a void that can be triggered after REG-19's table.

The other rules already give the right answer without a void:
- With the cut unknown, no hunk and no entry can be shown to be before it.
- The commit order fails, so batch 2 is retrospective.
- Line 64's seed/validity rule ends batch 2 only if such an entry exists.

So "not computed" adds nothing except the switch.

### 3.3 S3: order (b) has no K1

Line 124 tests "after a batch-1 table exists" against "the first commit that adds that batch's saved output". Line 130 calls a first run that did not write its file "a deviation, reported, and changes no label".

Trace (REG-21 deferred under (b)):
- At 10:00, `analysis.c2 reg22` is run to the terminal. That is a deviation.
- At 10:30, X is committed: a reviewed change to a REG-21 threshold.
- At 11:00, batch 1 is run again, saved and committed alone.

Two readings follow:
- **Literal:** X is a strict ancestor and earlier than 11:00, so it counts as before. A5 is not triggered, and REG-21 keeps its labels.
- **"Tested as the record's cut is" (line 124):** this imports K1, so there is no valid time and X counts as after. REG-21's batch 1 is reported without labels.

These are opposite outcomes for REG-21's labels, read after REG-22's batch 1 is known. Line 130's "changes no label" leans toward the literal reading. Whether the first run is saved is decided before its output exists, so closing this costs no lever.

### 3.4 The T1/L2 freeze and the SEALS exemption (your question)

**The freeze opens nothing that draft 10 closed.**
- Draft 10 required "rule F and an owner-proxy pass first". The time of the reviews was open, which is L2.
- Draft 11 requires the hunk and both reviews to be committed before the cut. A pre-cut hunk whose reviews came later is retrospective.
- The readout exemption is narrower than draft 10's "a reported-only readout whose diff rule F has seen": five bodies only, no `__main__`, nothing the judged path reaches, a rule F pass with no open required item, and commits before batch 1 and before the cut.
- A hunk in the body of `reported_counts` can decide whether batch 2 is computed (line 136). It is made before the cut and before batch 1, so it is blind.

**The SEALS exemption opens one route that draft 10 closed (draft 10 labelled any `withheld.py` hunk on the path retrospective).**
- The exemption's list is "its runs, their same-seed controls and every folder matching the batch-2 pattern".
- `control_readout` globs every attempt of the control config, and `find_runs` loads each one before checking validity.

Trace:
- A new tuple's pattern matches only seed 18's lost control attempt, not the valid one.
- Read as "the controls used", the list does not contain that folder, so the hunk is exempt.
- `keep` now skips the lost folder, which may have made `load_run` raise. That changes `control_readout` and the control count that line a quotes.
- A tuple sealing an old attempt is unlikely, and the effect stays in the readouts: no label, and the selection is covered by the batch-2 pattern. So this is optional, but it is a real route.

**O-c, a loosening against draft 10.**
- Draft 10 said "a rewritten commit counts as after the cut". Draft 11 says "judged by its new committer time", and only a date "set by hand" counts as after.
- A rebase after the cut with `--committer-date-is-author-date` writes old committer dates. On the reading "a flag is not by hand", a judged-path change folded into an old commit counts as before.
- This needs a deliberate rewrite that is already forbidden, so it is optional, but the words should not leave that reading open.

### 3.5 Other checks: no defect found

- Line 64 is again complete in one place, with S2 still to be applied.
- Line 101 is consistent with line 102.
- Line 135 is consistent with line 132.
- In line 130, the `date -u` duty and "changes no label" for REG-22's own labels are fine, because batch outputs are deterministic from committed code (the dirty-tree refusal).

**Is anything looser than draft 10 or draft 6?** Only three things:
- the SEALS route (O1);
- O-c's reading (O2);
- S2's void. That one is not looser in what it lets govern; it adds a way to lose batch 2 after REG-19's table is public.

## 4. Verdict: NOT READY

### REQUIRED (text only)

S1 and S2 change the shared passage, so mirror them in REG-21's line 107.

**S1 (line 133).** Replace "and states that no run that gave REG-19's table is known to have started before the record's stamp (a pair set aside and never committed, against the rule above, cannot be detected: a limit)." with:

"and quotes the statement that no run that gave REG-19's table is known to have started before the record's stamp. That statement is committed in its own entry before batch 2's command runs (its commit a strict ancestor of the commit that adds batch 2's output), and batch 2's command is not run before it exists; what it states governs, and a run made known only after batch 2's output exists is reported in a [CORR] beside batch 2 and changes no label (a pair set aside and never committed, against the rule above, and a run not disclosed by then cannot be detected: a limit)."

**S2 (lines 133 and 64).**
- In line 133, replace "A saved record lost against that rule is a breach, reported; the cut is then unknown, and batch 2 is not computed, with that reason." with:

  "A saved record lost against that rule is a breach, reported; the cut is then unknown, so every change and entry since this entry's commit counts as after it (for "Runs", the freeze and the commit order), and batch 2, if the other rules let it be computed, is labelled retrospective."
- In line 64, replace "REG-19's table is computed or read and there is no record, or the saved record is lost (both under "Stopping rule")" with:

  "REG-19's table is computed or read and there is no record (under "Stopping rule"; a saved record that is lost is not this case)"

**S3 (lines 124 and 130).**
- In line 124, replace "the first commit that adds that batch's saved output (the stopping rule's third bullet)" with:

  "the first commit that adds the saved output of that batch's first run (the stopping rule's third bullet)"
- After "…and every other change in that commit counts as after." add:

  "If that first run did not write its file as the third bullet says, no change made after the commit the deferral [DECISION] names counts as made before the table exists; a later saved run does not take its place."
- In line 130, replace "and changes no label" with:

  "and changes none of REG-22's labels (for REG-21's labels under order (b), see there)"

### OPTIONAL

- **O1 (line 132, SEALS).** Replace "(its runs, their same-seed controls and every folder matching the batch-2 pattern, listed in the [RESULT])" with:

  "(every folder in `runs/` that a pattern the command passes to `find_runs` matches, lost and invalid ones included: batch 1's names, `*_<control config>` of each judged run, FILE(analysis/c2.py:302), and the batch-2 pattern; listed in the [RESULT])"
- **O2 (line 133, rewrites; mirror in REG-21).** Replace "a commit whose committer date was set by hand counts as after the cut" with:

  "a commit whose committer date was not taken from the clock when that commit or its rewrite was made (set by hand, by `GIT_COMMITTER_DATE`, or kept by a rebase option such as `--committer-date-is-author-date`) counts as after the cut"
- **O3 (S1, stronger).** Where possible, commit the S1 statement before `final.sh` runs. It is then blind to REG-19's table as well.

### Process

The owner-proxy has to pass:
- L1 in place of its T3;
- S1–S3 (all on its list: the record, the not-computed cases other than adding one, and the order rules);
- the adoption into REG-22 of REG-21's P1–P3, which REG-21's proxy left to REG-22's proxy.

Until then, line 4's promise cannot be kept for T3.

### Can it change a decision?

Unchanged: batch 2's line e has P ≈ 0.0017 to 0.084, batch 1 ≈ 0.05 (BELIEF), both at 0 GPU h.

## 5. What I could not check

- **Not opened, as instructed:** `runs/`, the backups, `state/` file contents and probe outputs. I also did not read `test_sandbox.sh`.
- **Lost control folders:** whether the Mac's `runs/` holds lost control attempts of REG-19 seeds, which is what makes O1 more than theoretical. Checking would need a listing of `runs/`.
- **REG-21 draft 20:** I saw only line 107, so S3's mirror in REG-21's own order text is unchecked.
- **Earlier runs:** whether anyone has already computed REG-19's table or `reg19_pair` for a REG-19 seed. If so, K1 applies today, and S1's statement cannot be made.
- **Other unknowns:** commits made on the VM, and whether `main` is pushed anywhere (the only outside evidence of no rewrite).
- **Not run:** `pytest` and every analysis. Nothing was written into the repo.
