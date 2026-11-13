# rulef-reg22-draft14-r9 (rulef-reg22-r9), verbatim

Saved by the agent from the teammate message received in the main session transcript, 2026-11-13 between 12:42 and 12:51 UTC (the senders' idle notifications). Item names as given by the reviewer (prefixes BA, BB, BC, BD, CA, CB were assigned in the review prompts).

---

Rule F round 9 on REG-22 draft 14: NOT READY. Three items are required (BC1–BC3, text only, all three need an owner-proxy pass) and five are optional.

Notation: d14:N = FILE(docs/drafts/review_bundles/reg22_r9/registration_draft14.md:N).

**Checks I ran**
- HEAD is e062504.
- `git diff ffc76b3 HEAD -- analysis harness tests configs pyproject.toml uv.lock` is empty.
- No commit adds a `reg19_final_*` file under any ref yet.
- main is 123 commits ahead of origin/main, so nothing outside this Mac witnesses the history.
- Two worktrees sit detached at a7bb77a (aftershock-reg19-pin, aftershock-linktest-pin).
- `final.sh` saves into main's `state/` and `cat`s the table; it never commits (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20,29,32)).
- The harness writes its stdout to `$LOG` on the VM inside a detached tmux, not to a terminal (FILE(docs/probe/20261113_reg19/ops_r3/launch.sh:51)).
- With git 2.55, `--all` includes every worktree's HEAD unless `--single-worktree` is given (`git help rev-list`).

**The new rule, in short.** Freezing the path from E (the entry commit) with no exception and testing E against the first `final.sh` stamp is sound in principle. The stamp is taken before the table is computed (final.sh:20), so fact (2) is enough to place E before `final.sh`'s display. Order (b) is mechanical now on its own words. What remains is a label that is undefined or can be chosen in three places.

## Required

**BC1. "does not govern" has no meaning in REG-22, so what a retrospective batch 2 does is chosen after its output.**
- d14:133 says that if either fact fails, batch 2 "is labelled retrospective and does not govern". REG-22 defines no "govern"; the word comes from REG-21, where "The two batches" defines it.
- d14:93 puts every computed batch 2 under "Batches that disagree".
- d14:102 then gives "each batch's standing" and, when the batches disagree, withholds line a's permission to propose D1/D2 and line d's wording.
- d14:91 grants the standing "only if the commit order of the stopping rule holds". That bullet is gone (diff:44). Read as fact (2) alone, a batch whose fact (1) failed still carries "registered before REG-19's table".
- **Trace:** a `k1.later_turns` bug fix lands after E, so fact (1) fails. Batch 2 at λ = 2.0 is then `not_sustained` in 2 of 3.
  - Reading A: the batches disagree, D1/D2 wording is withheld, and C2's status claims neither.
  - Reading B: batch 2 "does not govern", so batch 1's line-a sentence stands and D1/D2 are proposed.
  - The writer of the [RESULT] picks between them with batch 2's output in hand. Without exceptions, retrospective is now the main way the freeze fails, so this is the decision-relevant case.
- **Replacement.** In d14:133, replace "is labelled retrospective and does not govern" with:
  > "is labelled retrospective: wherever a batch's standing is given (line a, 'Batches that disagree at λ = 2.0') it reads 'retrospective (fact (1)/(2) failed)'; it enters that line's disagreement test as a computed batch, so it can withhold line a's permission and line d's wording, and no sentence rests on it alone"
- In d14:91, replace "only if the commit order of the stopping rule holds" with:
  > "only if both facts of 'Batch 2 is primary only if' hold; otherwise 'retrospective'"
- Why this text: with it, the labels that BC2 and BC3 can still move change only the standing words, never a decision line. The other unambiguous option, retrospective treated as not computed, makes every git lever below decision-relevant.

**BC2. Fact (2) has no value when no commit adds the file, and with `--all` its value depends on whatever refs exist when it is checked.**
- d14:133 tests "the first commit that adds" a `reg19_final_*` file, using `git log --all … the earliest`.
- Removed with the record (diff:43–44): P3 ("a saved record not yet committed is committed first … 'No record' never follows from leaving a saved file uncommitted").
- **Trace 1:** `final.sh` saves and shows the table, and the pair stays untracked. Three readings follow, each chosen after REG-19's table, whose [RESULT] already implies batch 2's labels in part (d14:134):
  - fact (2) is false, so batch 2 is retrospective;
  - "REG-19 ends without the table that `final.sh` saves", so batch 2 is not computed (d14:64);
  - the pair is committed late, so batch 2 is primary.
- **Trace 2:** `git stash -u` sweeps the untracked pair into a parentless commit; refs/stash is in `--all`. A commit made in a pin worktree would also be in `--all`, and E is not an ancestor of it. That commit is then "the earliest", so fact (2) fails. Dropping the stash before the check makes it pass again: either way, chosen after the data.
- **Replacement for fact (2):**
  > "(2) on the first-parent chain of the commit batch 2 runs from, the first commit that adds a file matching `…/state/reg19_final_*` (`git log --first-parent --diff-filter=A --format='%H %ct' --name-only <batch-2 commit> -- '<pattern>'`, the last listed) has this entry's commit as a strict ancestor (`git merge-base --is-ancestor`, and not equal), and this entry's `%ct` is earlier than the UTC stamp in that file's name … A file `final.sh` saved that no commit on that chain adds when batch 2 is to be computed or declared not computed is committed first, alone (late: a breach, reported), and (2) is read with it. If it can no longer be committed, (2) is read against the stamp that REG-19's final [RESULT] or an [OPS] entry quotes for it; with no such stamp, (2) fails. A file `final.sh` saved never makes REG-19 'end without the table that `final.sh` saves'."

**BC3. "A later look moves nothing that batch 2 computes" (d14:80) is false: the run set can still change between E and the first `final.sh` commit.**
- "Runs" ends batch 2 only for an entry that changes validity after that commit; "a flag set before that commit is part of what that table counts" (d14:64).
- Seeds 18 and 19 run after E.
- **Trace:** after E, someone reads a burst run's status lines in its VM log (the 2026-11-12 look is precedent, d14:80). An entry then marks that run invalid beyond the automatic checks, and the seed is rerun. The new run enters batch 2 under a primary label. REG-21 draft 23 (a) has the same gap.
- **Replacement, added to d14:133:**
  > "Batch 2 is also retrospective if, after this entry's commit and before the first commit that adds a `reg19_final_*` file, the validity flag of a run matching the batch-2 pattern is set or changed other than by the harness's checks at the run's end or the queue's recheck under the checks pinned at this entry (`CHECKS_COMMIT`, FILE(docs/probe/20261113_reg19/ops_r3/common.sh:28)), or a valid burst run of a REG-19 seed is rerun; the batch-2 [RESULT] lists every such flag with its entry."
- At d14:80, replace "so a later look moves nothing that batch 2 computes" with:
  > "so a later look moves no threshold; it could move which runs batch 2 reads only through a validity change, which the freeze treats"

## Optional
- **BC-O1 (Y1 is dated at the draft, not at E).** The search was made "on 2026-11-13" (d14:81). Add REG-21's clause: at the append, the search is run again and the [DECISION] quotes the re-run; if it finds a run, the entry is not appended as written.
- **BC-O2 (text that still points at removed or contradicted rules):**
  - d14:131: "the freeze's 'before batch 1'" refers to a test the freeze no longer has.
  - d14:149: "and the reviews it had" refers to reviews that no longer keep a hunk.
  - d14:5 ("runs whose outcomes nobody has read") and d14:80 ("read as unread data") contradict d14:134 ("does not call batch 2 'unread'").
  - d14:80: "the terminal of whoever started it" is wrong under launch.sh:51, which writes to `$LOG` only.
- **BC-O3 (the fact (2) command does not show what it is cited for).** Its `--format='%H %ct'` prints no file name, so the stamp is not in the "verbatim output". Name `--name-only`, the `--is-ancestor` call and `git log -1 --format=%ct <E>`.
  - Fact (1) compares commits only, while `_dirty` covers only `analysis/` and `tests/` (FILE(analysis/k3w.py:453)). An uncommitted `harness/workload.py` would run at import unseen. Have the [RESULT] show `git status --porcelain` for every file of the freeze.
  - `load.RUNS` is the checkout's `runs/` (FILE(analysis/load.py:11)). Name the main working tree as the checkout.
- **BC-O4.** The batch-1 file has no fixed directory or name pattern. Order (b)'s "first commit that adds the saved output" needs one; REG-21 uses `docs/probe/`.
- **BC-O5.** REG-21's third list (the `reg19_final` rows less `excluded`, which catches a `checks.json` rewritten with no entry) has no counterpart here.

## Y1 and AA2
- **Y1:** met in substance, with a hedged statement, a search and its limit (d14:81). The search's date is BC-O1.
- **AA2:** met. `c2.condition4` is named at d14:81 and d14:125, and the statement is in "What was known".

## Can it change a decision?
- BC1 is the only route by which REG-22's label choice reaches a decision: line e, or the block on D1/D2.
- P(line e changes a decision for batch 2) ≈ 0.0017 to 0.084 (BELIEF, the draft's own figure, d14:11).
- The share of computed batch 2s that end retrospective rises with the no-exception freeze (BELIEF).
- Batch 1 is unchanged at ≈ 0.05 (BELIEF). Cost: 0 GPU h.

## Not checked
- I did not open the contents of `queue_run*_output.txt`, so I don't know whether recorder lines of burst runs 15–17 are committed in the repo. The VM logs, `runs/`, `state/` contents and RESUME.md were not opened either.
- `gate.py`'s and `harness/workload.py`'s import-time code; pytest; any analysis.
- REG-21 draft 23 beyond its stopping rule.
- Whether the transcript search exists as quoted (the [DECISION] is not written yet).

Nothing was written to the repository.
