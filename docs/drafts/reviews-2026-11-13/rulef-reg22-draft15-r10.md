# rulef-reg22-draft15-r10 (rulef-reg22-r10), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T16:01:10.714Z). Item names as given by the reviewer (prefixes BE, BF, BG, BH were assigned in the round-2 review prompts).

---

Rule F round 10 on REG-22 draft 15: NOT READY. Five items are required (BG1–BG5). Four concern batch 2's standing (BG1–BG4); I classify each as wording or a stricter rule, so on my reading they do not trigger the review-stop rule's item 4. BG1 is the one whose classification the owner-proxy must decide. There are eight optional items.

Notation: D15:n = FILE(docs/drafts/review_bundles/reg22_r10/registration_draft15.md:n).

**What I read**
- The whole bundle reg22_r10: draft 15, draft 14, the diff, round 9, the owner-proxy on draft 14, the stop-rule entry, the [CORR], the delegation, the transcript search script and its output, the final.sh/common.sh/launch.sh copies, and REG-21 draft 24 with its round-16 reviews.
- At HEAD ba67e55: analysis/c2.py, k3w.py, withheld.py and load.py; the imports of gate.py and harness/run.py; ops_r3's queue.sh, common.sh, final.sh and launch.sh.
- `git show a7bb77a:analysis/gate.py`, for reg19_step's code only.
- Beyond the bundle: the tool-call inputs, never the outputs, of six transcript lines (named under BG5), and one inputs-only pass over all transcripts.
- Not opened: anything under runs/ beyond folder names, the backups, the contents of state/ (I looked at names only), any queue or probe output other than the bundle's search output, and RESUME.md.

**Checks I ran** (git and pytest in the reviewer's terminal; output not saved)
- `git diff ffc76b3 HEAD -- analysis harness tests pyproject.toml uv.lock` touches only analysis/e1.py (a docstring, e404c74). From 727d1f2 to HEAD, analysis/c2.py is the only frozen file that changed (ffc76b3).
- `uv run pytest -q tests/test_c2.py`: 29 passed.
- No file whose name carries a final.sh stamp exists in the working tree or under any ref. The files that do match `reg19_final_*` are the review bundles' copies of final.sh (BG1).
- state/ is not ignored by git (`git check-ignore` exits 1).

**BC1–BC3 and BD1–BD7, as asked**
- **BC1:** met verbatim (D15:133, D15:91). It also creates BG4: a retrospective batch 2 can now withhold batch 1's permission, while a batch 2 that is not computed cannot, so ending batch 2 now matters for decisions.
- **BC2:** met in substance (the earliest stamp over the working tree, every ref and decisions.md, D15:133). Its sentence "A file `final.sh` saved never makes REG-19 'end without the table …'" was not taken; it is in BG4. The pattern itself fails (BG1).
- **BC3:** met at D15:133 and D15:80, but the cut is still "the first commit that adds a `reg19_final_*` file", not S (BG3).
- **BD1, BD2, BD5, BD7:** met. **BD4:** met in kind, but the list it extends is wrong (BG2).
- **BD6:** met, but "adds nothing to C2's status" can release batch 1's lines (BG4).
- **BD3:** the trigger at D15:80 is narrower than BD3's wording, so it needs the owner-proxy's pass (BG5 c).

## Required

### BG1. Fact (2) already fails on its own words: the review bundles hold committed files named `reg19_final_*`

**Trace**
- `find . -name 'reg19_final_*' -not -path './.git/*'` prints 15 paths today. All are copies of final.sh named `reg19_final_sh_for_reference.sh`, under docs/drafts/review_bundles/ and _to_delete/, this bundle's copy included.
- `git log --all --diff-filter=A --name-only --format='%H %ct' -- ':(glob)**/reg19_final_*'` lists commits 3e9c73f, e062504 and ba67e55 (HEAD) as adding such files, and `git merge-base --is-ancestor 3e9c73f HEAD` succeeds.
- So every future commit, E included, has "a commit that adds such a file" as an ancestor, and D15:133's second condition fails.
- Read literally, batch 2 is already retrospective, and "no review, statement, [CORR] or later commit restores primary standing". Read by intent ("such a file" = a file final.sh wrote), it is primary. The writer of the batch-2 [RESULT] chooses between the two readings with batch 2's output in hand.
- The first condition has the same gap: "the earliest UTC stamp in the name of any file named `reg19_final_*`" is undefined for a name with no stamp.
- REG-21 draft 24 (its line 104) has the same words and the same defect.

**Replacement.** At D15:133, replace "let S be the earliest UTC stamp in the name of any file named `reg19_final_*`, among the files of that name anywhere in the repository's working tree (`find . -name 'reg19_final_*' -not -path './.git/*'`), every name that any commit on any ref adds (`git log --all --diff-filter=A --name-only --format='%H %ct' -- ':(glob)**/reg19_final_*'`), and every such stamp a decisions.md entry quotes" with:
> "call a *table file* any file whose name begins `reg19_final_` or `reg19_final_err_` followed by a UTC stamp `YYYYMMDDTHHMMSSZ` (the names `final.sh` writes, FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20), with the stamp of FILE(docs/probe/20261113_reg19/ops_r3/common.sh:42), which `_<pid>_<n>` follows); a name that begins `reg19_final_` with no such stamp (the review bundles' copies of `final.sh`) is not a table file. Let S be the earliest such stamp among the table files anywhere in the repository's working tree (`find . -not -path './.git/*' \( -name 'reg19_final_[0-9]*' -o -name 'reg19_final_err_[0-9]*' \)`), every table file that any commit on any ref adds (`git log --all --diff-filter=A --name-only --format='%H %ct' -- ':(glob)**/reg19_final_[0-9]*' ':(glob)**/reg19_final_err_[0-9]*'`), and every such stamp a decisions.md entry quotes"

In the same bullet:
- "no commit that adds such a file is E or an ancestor of E" → "no commit that adds a table file is E or an ancestor of E".
- In the duties, "every file named `reg19_final_*`" → "every table file".
- In the limits, "a `reg19_final_*` file moved out" → "a table file moved out", and "No `reg19_final_*` file is deleted" → "No table file is deleted".
- The three places in D15:64 and D15:133 that cite "the first commit that adds a `reg19_final_*` file" are replaced under BG3.

I tested the replacement commands in a throwaway repository holding one bundle-copy name and one name with a synthetic stamp (no project data). The draft's pathspec lists both names; the replacement lists only the stamped one.

- **Owner-proxy pass:** yes (a change to fact (2)).
- **Batch 2's standing:** yes.
- **Type:** wording. The second condition now reads the same files as the first: the only files that carry a stamp, and so the only ones that can witness REG-19's table. The set is narrower, though. If the proxy calls this a design change, the stop rule's item 4 applies.
- **Why that is tolerable:** under BC1, a retrospective batch 2 moves only the standing words, never a decision line (DERIVED from D15:102 and D15:133).
- **Why no stricter fix exists:** 3e9c73f is already in E's history, so no stricter wording leaves primary standing possible. The fix must land before E.

### BG2. The list of 23 files is not the import closure it claims to be: three files are missing

**Trace**
- D15:133 defines the frozen files as "every file the batch command imports, by the import closure of `analysis/c2.py` … (function-level imports included; computed with Python's `ast`)", then lists 23 files.
- The closure reaches `harness/run.py` through c2 → k1 → gate: FILE(analysis/c2.py:24), FILE(analysis/k1.py:24), and gate's function-level import FILE(analysis/gate.py:751); also FILE(analysis/k3.py:395).
- `harness/run.py` imports at top level `from harness import checks, env_snapshot, trigger, workload` and `from harness import loadgen` (FILE(harness/run.py:23), FILE(harness/run.py:24)).
- So `harness/env_snapshot.py`, `harness/loadgen.py` and `harness/trigger.py` are in the closure but not in the list. My ast walk gives 24 Python files, not 21 (DERIVED: a scratch script over HEAD ba67e55 that treats `from <package> import <name>` as an import of `<package>/<name>.py` when that file exists). The draft's walk appears to have missed that form.
- Now let a commit after E touch `harness/loadgen.py`. That is plausible: C2's session-cap control is "set at the load generator" (D15:17), and REG-20 works on the load generator.
  - Fact (1)'s command names "<the frozen files>". Run with the list, it prints nothing, and batch 2 is primary.
  - Read by the definition, the file is frozen, and batch 2 is retrospective.
  - The choice is made after the data.
- REG-21 draft 24's list of 22 files misses the same three: k3w's closure is 23 Python files by the same walk.

**Replacement**
- At D15:133, replace "`harness/config.py`, `harness/recorder.py`, `harness/run.py`, `harness/workload.py`, `pyproject.toml`, `uv.lock` (23 files)" with "`harness/config.py`, `harness/env_snapshot.py`, `harness/loadgen.py`, `harness/recorder.py`, `harness/run.py`, `harness/trigger.py`, `harness/workload.py`, `pyproject.toml`, `uv.lock` (26 files)".
- After that list, add: "The list is the output of a committed script, run at E and saved with the [DECISION] (delegate); it counts `from <package> import <name>` as an import of `<package>/<name>.py` where that file exists. If the list and the import closure at E ever differ, the frozen files are their union, and fact (1)'s commands name the union."
- At D15:210, change "23 files" to "26 files".

- **Owner-proxy pass:** yes (fact (1)'s list, the same kind of change as BD4).
- **Batch 2's standing:** yes.
- **Type:** a stricter rule (more files frozen).

### BG3. The validity cut is still at "the first commit that adds a `reg19_final_*` file" while fact (2) is at S, so one event has two outcomes

**Trace**
- `final.sh` takes its stamp (S), computes the table and `cat`s it (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20), FILE(docs/probe/20261113_reg19/ops_r3/final.sh:29), FILE(docs/probe/20261113_reg19/ops_r3/final.sh:32)).
- The pair is committed later; a late commit is only a breach of the duties (D15:133).
- Between S and that commit, an entry marks a REG-19 burst run invalid, or a valid burst run is rerun. Two readings follow:
  - **Reading A (D15:133):** the change is "before the first commit that adds a `reg19_final_*` file", so batch 2 is retrospective and computed.
  - **Reading B (D15:64):** "a flag set before that commit is part of what that table counts". That is false here, because the table was computed at S. The valid folders then differ from the burst runs whose seeds are in n, so batch 2 is not computed.
- The writer chooses after the table. Under BC1 the two readings differ in a decision (BG4).
- REG-21's round 16 found the same trace in REG-21 draft 23 (BA1, trace 2). D15 moved fact (2) to S but left the validity cut where it was.

**Replacement**
- At D15:64, replace "after the first commit that adds a `reg19_final_*` file and before batch 2, an entry changes the seeds that table counts or the validity flag of a matching run (a flag set before that commit is part of what that table counts)" with:
> "at or after S (the stopping rule's fact (2)) and before batch 2, an entry changes the seeds that table counts or the validity flag of a matching run (a flag set before S is part of what that table counts; an entry is placed by its commit's committer time, compared with S as instants, the same second counting as after)"
- At D15:133, replace "after E and before the first commit that adds a `reg19_final_*` file, the validity flag" with "after E and before S, the validity flag".
- At D15:133, replace "A change after that commit ends batch 2 ("Runs", not computed), which takes precedence." with "A change at or after S ends batch 2 ("Runs", not computed), which takes precedence, with the consequence that 'Batches that disagree at λ = 2.0' gives it."

- **Owner-proxy pass:** yes.
- **Batch 2's standing:** yes (the validity cut).
- **Type:** wording. The cut moves to the instant the two facts already use, and nothing becomes looser.

### BG4. After REG-19's table, "not computed" frees batch 1's lines a and d, which a computed retrospective batch 2 would have withheld; BC1 turned this into a lever

**Trace**
- Under BC1, a retrospective batch 2 "enters that line's disagreement test as a computed batch, so it can withhold line a's permission and line d's wording" (D15:133).
- A batch 2 that is not computed cannot: "batch 1's sentence stands, with 'batch 2 not computed: <reason>'" (D15:102). Line a's sentence carries the D1/D2 permission (D15:94).
- REG-19's [RESULT] publishes each run's verdict, end-window values and emptyings, "so the labels were partly implied" (D15:134).
- A reader who foresees batch 2 disagreeing at λ = 2.0 keeps batch 1's permission by ending batch 2 after S. Four routes break no rule:
  - (a) An entry after S changes a validity flag or the seeds counted. That ends batch 2 (D15:64; D15:133, "which takes precedence"). An invalidation after the fact can be made in good faith, for example a power limit later found at 420 W.
  - (b) `batch_runs(2)` raises "for any reason" (D15:64). For example, REG-19's [RESULT] heading is worded so that `withheld.lifted` does not match it; "(delegate)" placed before "REG-19" is enough (FILE(analysis/withheld.py:46)).
  - (c) A defect that does not raise is fixed beside the frozen code, and a label differs. Batch 2 then "adds nothing to C2's status" (D15:133), and nothing says whether it still enters the disagreement test.
  - (d) The `final.sh` pair is set aside as a failure, and REG-19 "ends without the table that `final.sh` saves" (D15:64). Round 9's BC2 sentence would have closed this.
- Before BC1, none of this mattered: retrospective and not computed both meant "does not govern". Now the same event makes batch 2 retrospective and able to withhold if it happens before S, but not computed and unable to withhold if it happens after S. The rule is looser after the data than before it.

**Replacement**
- At D15:102, replace "When batch 2 is not computed or has fewer than 3 stuck runs at λ = 2.0, batch 1's sentence stands," with:
> "When batch 2 is not computed for a cause that arose at or after S (the stopping rule's fact (2)), whatever the cause (an entry on validity or on the seeds counted, a raise of `batch_runs(2)` or of `reported_counts`, the run comparison under 'Runs', or REG-19 said to end without a table), it counts here as a batch that met none of the lines: neither line a's permission to propose D1 and D2 nor line d's 'D1 and D2 not proposed as planned' applies by itself, and wording that relies on either waits for an owner's [DECISION] that names the cause. A file `final.sh` saved never makes REG-19 'end without the table that `final.sh` saves'. When batch 2 is not computed for a cause that arose before S, or has fewer than 3 stuck runs at λ = 2.0, batch 1's sentence stands,"
- At D15:133, replace "if any label differs between the two, batch 2 is reported per run with both labels and adds nothing to C2's status until an owner's [DECISION]." with:
> "if any label differs between the two, batch 2 is reported per run with both labels and counts in 'Batches that disagree at λ = 2.0' as a batch that met none of the lines until an owner's [DECISION]. A defect found after batch 2 is computed is handled the same way, and the frozen labels are the ones quoted."
- At D15:93, after "once it is reported not computed, "batch 2 not computed: <reason>", with batch 1's standing unchanged", add: "(and, for a cause at or after S, with line a's permission withheld as under 'Batches that disagree at λ = 2.0')".

- **Owner-proxy pass:** yes. It changes what a decision line does.
- **Batch 2's standing:** yes (what a retrospective or not-computed batch 2 does).
- **Type:** a stricter rule. Every event it covers can only withhold, never release, and it withholds line a and line d alike, so it favours neither direction. The cost is an owner's [DECISION] in the rare innocent case.

### BG5. "What was known" is incomplete, and the search it cites cannot see the read forms that were in fact used

**(a) Read (i) is under-reported.**
- D15:80 describes read (i) as "about the last 15 lines of seed 17's control's harness log".
- The same command (2026-11-12 11:45:33 UTC, session bc2fcf6d, transcript line 10177; tool-call input only, FILE(~/.claude/projects/-Users-chalshik-Projects-aftershock-artifacts/bc2fcf6d-b7b6-45b7-9398-2cecb62afb9a.jsonl:10177)) went on, on the VM, with `echo ---RUN; cd ~/aftershock-artifacts/runs/20261112-103423_stage2_control_l1pl350cl_r2.0_w3000_s17 && ls -la && tail -3 events.jsonl`.
- The bundle's own search output shows the start of that command, cut off at the `cd` (FILE(docs/drafts/review_bundles/reg22_r10/transcript_search_output_20261113T153519Z.txt:254)).
- At a run's end, the last three events the harness writes are `gpu_processes_end`, `stopped` and `checks` (with `valid` and `failed`) (FILE(harness/run.py:214), FILE(harness/run.py:216), FILE(harness/run.py:219)). So the read was probably validity-level (BELIEF: whether the run had ended at 11:45 is not known, and the output was not opened). It concerns a control, not a burst run.

**(b) The search misses read forms that were used.**
- Its classifier needs a REG-19 folder name followed by `/` and a file name (FILE(docs/drafts/review_bundles/reg22_r10/transcript_search.py:37)).
- It missed the `cd` read above.
- It also missed the subagent's two loop reads in `agent-ad7b5aba70bdf01d4.jsonl`: `cat $r/env.json` at 17:57:42 (transcript line 131) and `grep … $r/server.log` at 17:57:48 (line 135). The output lists only that subagent's line 139 (at its :281–282). D15 discloses lines 131 and 135 from another source.
- It does not see:
  - globs that leave out `w3000`;
  - Python written by a Bash heredoc and run later;
  - any Bash command that contains the word `pytest` (such commands are skipped whole, :124);
  - tool calls other than Bash, Read and Write (Monitor among them);
  - commands run inside scripts.
- The last gap matters for the draft's own statement:
  - REG-19's queue ran `analysis.gate reg19_step` on REG-19 folders from the pinned worktree after each seed, and saved its whole stdout to `state/reg19_step_out_s<seed>_<stamp>.txt` (FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:75), FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:77)). Its docstring at a7bb77a says it prints only `done` and `continue`.
  - The queue also ran `analysis.recheck` with `AFTERSHOCK_UNSEAL=REG-19` (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:210)).
  - D15:80's "no run of `analysis/` code on a REG-19 run folder from any checkout, is found by a search" is therefore true of the search and false of the project.
- My own inputs-only pass over the same transcripts flagged every tool's input that names a REG-19 run id or `w3000_s1[5-9]` near a read verb (63 hits).
  - It found no other read of a REG-19 folder's contents.
  - The other two VM reads of seed 17's control read only `checks.json` (lines 10195 and 10213 of the same transcript).
  - The remaining hits are names, sizes, checksums or configs.
  - This pass is not saved and not exhaustive.

**(c) The append switch is narrower than BD3.**
- D15:80 stops the append only for "a read of a line a REG-19 burst run wrote after its burst began".
- BD3 asked for any read of "a REG-19 run's harness or launch log beyond the lines `common.sh`'s ALLOWED names", controls included.
- The proxy required "a pass for any other wording of BD3".

**Replacement**
- (a) At D15:80, after "(BELIEF: the note that records it, RESUME.md, was not opened);", insert:
> "the same command also listed that control's run folder on the VM (`ls -la`) and printed the last three lines of its `events.jsonl` (FILE(~/.claude/projects/-Users-chalshik-Projects-aftershock-artifacts/bc2fcf6d-b7b6-45b7-9398-2cecb62afb9a.jsonl:10177), its input only; at a run's end these are the `gpu_processes_end`, `stopped` and `checks` events, FILE(harness/run.py:214) to FILE(harness/run.py:219); whether the run had ended then is not known);"
- (b) At D15:80, replace "No other read of a REG-19 run's files or logs beyond names, validity and the names of failed checks, and no run of `analysis/` code on a REG-19 run folder from any checkout, is found by a search" with:
> "Besides REG-19's own computations, which its queue scripts run where no transcript shows them (`analysis.gate reg19_step` from the pinned worktree after each seed, its stdout saved whole in `state/reg19_step_out_s<seed>_<stamp>.txt` and reduced to `done` and `continue`, FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:75); `analysis.recheck` with `AFTERSHOCK_UNSEAL=REG-19`, validity fields only, FILE(docs/probe/20261113_reg19/ops_r3/common.sh:210)), no other read of a REG-19 run's files or logs beyond names, validity and the names of failed checks, and no other run of `analysis/` code on a REG-19 run folder from any checkout, is found by a search"
- (b) Also, before the rerun at E, widen `search.py`:
  - list every tool-call input, of any tool, whose text names a REG-19 run id, a REG-19 config name or `w3000_s1[5-9]`;
  - drop the `pytest` skip;
  - have the [DECISION] (delegate) classify each hit and state, as limits, the forms still unseen (commands inside scripts, commands run by hand).
- (c) Either take BD3's trigger wording ("a run of `analysis.gate reg19`, `reg19_table`, `reg19_pair`, `reg19_cold_side` or any `analysis` module on a REG-19 run folder, or a read of a REG-19 run's harness or launch log beyond the lines `common.sh`'s ALLOWED names, beyond what is listed here"), or get the proxy's pass on D15's narrower wording.

- **Owner-proxy pass:** yes, for (c); (a) and (b) are disclosures.
- **Batch 2's standing:** no (a disclosure item; stop rule item 3).
- **Type:** a reporting duty.

## Optional
- **BG-O1. Fact (1)'s commands.**
  - Run fact (1)'s two commands and `git rev-parse HEAD` (this is B) in the same command line as batch 2's command, before it, with their output written into the batch file.
  - Add `--full-history` to fact (1)'s `git log`. By default, history simplification drops a side branch whose change a merge discards, which "a later commit that reverts it does not undo it" means to count.
  - `git merge-base --is-ancestor` prints nothing, so append `&& echo ancestor || echo not_ancestor` to make it show "verbatim".
- **BG-O2. The environment is fixed by more than the two files.**
  - `.python-version` (3.12.13) picks the interpreter: freeze it, or show `python -V`.
  - `uv run` syncs `.venv` unless told not to: run batch 2 with `uv run --locked`.
  - `python -m` puts the repository root first on `sys.path`, where an untracked module would shadow a library. Fact (1)'s `git status` names only the frozen files, so also show an unrestricted `git status --porcelain`.
- **BG-O3. Unclassified search hits.** The current search output has four `ran_on_reg19` hits (:239, :290, :302, :315) that the draft does not classify. They are a config read made before any REG-19 run existed, two edits that only name the seal and batch-2 patterns, and a listing of `configs/`. Classify them in the [REG] now, so that the rerun at E is compared against a written list.
- **BG-O4. Stale run count.** D15:79's "Three REG-19 burst runs exist at this draft" will be stale at E: the queue is running, and state/ holds a launch record for seed 18's control. Have the [DECISION] (delegate) name the REG-19 folders present at E, by name only, as REG-21's BA4 asked.
- **BG-O5. REG-20's seal.** D15:133 says "every pending registration's seal is already in `withheld.SEALS`" and, in the same sentence, that "REG-20's arm-B seal … waits". A seal can only go into `withheld.SEALS`, which is frozen. Say whether REG-20's arm B runs before both batch 2s; if it does, its folders stay unsealed until then, and that is disclosed.
- **BG-O6. Line e.** Say whether a retrospective batch 2 triggers line e's duty ("the confirmation run's registration must read every span"). The stricter answer is yes.
- **BG-O7. Worktrees.** `final.sh` runs `analysis.gate reg19` after `cd $W`, the pinned worktree (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:29)), but fact (2)'s `find .` covers only the main working tree. Run the same `find` in each path that `git worktree list` gives.
- **BG-O8. Invented stamps.** Fact (2) counts "every such stamp a decisions.md entry quotes", and the [REG] will hold the reviews verbatim. Add a duty that no entry or saved review writes a table-file name with an invented stamp: an early one would set S. This review writes none.

## Can it change a decision?
Yes, rarely.
- Batch 1: P ≈ 0.05 (the draft's BELIEF). Batch 2: P ≈ 0.0017 to 0.084 (DERIVED at D15:11 from BELIEF inputs).
- Of the items above, only BG4 reaches a decision line. It closes the one remaining path by which, once REG-19's table is out, someone can end batch 2 and so restore batch 1's D1/D2 permission or line d's wording.
- BG1–BG3 otherwise move only the standing words (BC1), or move a batch 2 between computed and not computed, which BG4 makes harmless. Without BG1, batch 2's standing is open to choice from the moment E is committed.
- Cost: 0 GPU h.

## Not checked
- docs/decisions.md beyond the format of past [RESULT] headings and its mentions of `reg19_final_`.
- docs/status.md, PROTOCOL.md and docs/claims.md (rule F sees the registration and its code).
- How the stop rule will classify BG1.
- REG-21 draft 24 beyond its freeze passage. BG1 and BG2 apply to it as well; my walk gives k3w's closure as 23 Python files.
- The VM's own history, and any pushed copy.
- tools/check_docs.py and the full pytest suite (only tests/test_c2.py was run).
- The transcripts beyond the six inputs named and my unsaved inputs-only pass.
- Whether vLLM 0.32.0 writes a periodic log line that matches read (ii)'s patterns (the draft's BELIEF).

Nothing was written to the repository.
