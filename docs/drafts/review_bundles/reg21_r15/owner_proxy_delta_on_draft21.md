# Owner-proxy delta pass on REG-21 draft 21 (agent a4122f052f465a926), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T12:07:26.641Z), no word changed. Its conditions W1–W3 are called X1–X3 in the drafts, to keep them apart from REG-22's owner-proxy W1–W3 on REG-22 draft 12.

---

**Decision: APPROVE**, with three wording conditions due before the entry is appended (W1–W3) and one later duty (V5, which widens V4). This approves REG-21 draft 21 (FILE(docs/drafts/reg21_draft21.md)), text only, with code at `8164211`. It is a delta to the round-4 approval and to my passes on drafts 9 to 20.

Integrity checks:
- HEAD is `6d4fc6b`, one commit after `b8ea915`, which touches only `agent/STATE.md`.
- The bundle's drafts 20 and 21 are byte-identical to their sources, and the bundle diff equals a fresh diff.
- `git diff 8164211 HEAD` is empty for the eight judged-path files.
- `state/` holds no `reg19_final_*` file (names only).
- The shared record passage (line 107 here, REG-22 draft 12's line 133) differs only in references to each registration's own sections.

**Reasons** (line numbers are draft 21's)

1. **V1 and V2 are met, in my words (lines 104 and 107).**

2. **V3 in rule F's M1 wording is accepted (line 104).**
   - It is stricter than my words. Mine ("folder names in `runs/` that match …") could still be read as what `find_runs` returns, and that is exactly what a seal decides (load.py:42), so the test was circular.
   - The names now come from a listing of the directory, sealed folders included, before any validity check or selection.
   - The list is complete for the command. `reported_spans` globs only batch 1's or batch 2's runs and `ref_runs` (k3w.py:419, :428), and `REG21['batch1']` has 13 names (k3w.py:58–64).

3. **M2 is accepted (line 107).** It is stricter than draft 20 and keeps one exception: a rewrite before the stamp, which leaks nothing.

4. **A route M2 does not close: a commit that joins the branch after the stamp without any rewrite (W1).**
   - **Trace:**
     - REG-20's change to `k1.windows` and both of its reviews are committed at 11:00Z on a side branch. Agents' worktrees make side branches; this repo has the branch `reg11-closed-loop` and one merge on `main`.
     - The stamp is 12:00Z. After REG-19's table has been read, the delegate decides whether to fast-forward or merge that branch before the record's commit at 12:05Z.
     - If merged, the change's commit is a strict ancestor of the record's commit and its `%ct` is before the cut, so line 104's exception holds and batch 2 governs on the changed path. If not merged, batch 2 governs on the old path.
   - Either way batch 2 governs, and the path is chosen after the table. That is rule A5 again, done with ordinary commands that the text does not forbid.
   - The reflog that draft 21 already quotes (O-2) shows merges and fast-forwards with their times, so the test can stay a fact in git.

5. **O-3 (output defined by content) is accepted in intent, but it has a double reading that must be closed (W2).**
   - A row of `reg19_table` also holds `runs` (the folder names), `seed`, `exposed` (gate.py:2055–2056) and `lam_p` (gate.py:2064).
   - So "a value that a row … holds", printed for a REG-19 run, covers any print of a REG-19 folder name. The queue's committed outputs print those names, and so does duty (a)'s list.
   - On that reading, REG-19's table was printed long ago and never saved, so there is no record and batch 2 is already lost. On the intended reading, batch 2 is untouched. These are opposite outcomes that could be chosen after the data.

6. **S1 is accepted: the statement is committed before batch 2's command (line 107).** One gap remains (W3): nothing follows if the statement is not committed first. Then the statement is written with batch 2's output in hand, which is the very choice S1 removes. The order is a fact in git, and the runner decides it before batch 2's output exists, so tying a label to it gives no one a lever after the data.

7. **S2 is accepted (line 107). It corrects my reason 3(c) on draft 20.**
   - **My error, rule A6.** I accepted "the cut is unknown, so batch 2 is not computed" and argued that nothing else was possible. That was wrong: with the cut unknown, the other rules already give "retrospective".
   - "Not computed" added only a switch that a `git clean` could throw after REG-19's table (REG-22's rule F round 6, S2).
   - Batch 2 governs nothing in either case. Under S2, though, its numbers are reported rather than suppressed.

8. **U1, U2, O-4 and O-6 are accepted.**
   - **U1** applies L1 to the freeze (line 104).
   - **U2:** an unsaved first run of a batch counts as existing from the entry commit (line 113). This is K1 for the batch outputs, stricter, and decided before the output.
   - **O-4:** acceptable. Optional: name the commit by a fact in git, the parent of the commit that adds batch 1's [RESULT], rather than by the [RESULT]'s own statement.
   - **O-6:** stricter.
   - **O-1 not taken:** agreed, because V4 covers it.

9. **Nothing else moves a rule.** Every change in this draft is equal or stricter, apart from what W1–W3 address.

**Conditions**

BEFORE the entry is appended. Use the same words in REG-22's line 133 so the shared passage stays identical; for W3 the line-113 counterpart is REG-22's line 130.

- **W1 (line 107).**
  - After "…and other tools that keep or copy a date)." insert: "A commit that joins the branch that holds this entry after the stamp, by a merge, a fast-forward, a cherry-pick or a rebase, counts as after the cut whatever its committer date says, and a merge commit counts as the commit that makes every change it brings in."
  - In the reflog sentence, replace "(whether any `rebase`, `amend`, `reset` or `filter` entry appears)" with "(whether any `rebase`, `amend`, `reset`, `filter`, `merge`, `cherry-pick` or fast-forward entry appears, each with its time beside the stamp)".
- **W2 (line 107).** Replace the parenthesis "(a verdict, an outcome or the completion rate `c`; `reg19_cold_side`, FILE(analysis/gate.py:1834), for one)", and the words "a value that a row of `reg19_table` holds" before it, with: "a value that a row of `reg19_table` derives from the run's recorded requests, metrics or logs (a verdict, an outcome, the completion rate `c` or any other such value; `reg19_cold_side`, FILE(analysis/gate.py:1834), prints one; folder names, seeds, `exposed`, planned rates and a run's `checks.json` fields are not such values)".
- **W3 (lines 107 and 113).**
  - In line 107, after "…which makes it blind to REG-19's table too." add: "If that statement's commit is not a strict ancestor of the commit that adds batch 2's saved output (with no saved output, it is not), batch 2 is labelled retrospective; this is read from git alone."
  - In line 113, after "it changes no label of REG-21" add: "(except under the statement rule of "Batch 2 not computed")".

LATER:
- **V5 (widens V4; due before batch 2's label is cited in `docs/claims.md`, `docs/status.md` or paper text).**
  - V4's verbatim git facts also include the freeze's hunk list (each hunk's commit, `%ct` and reviews' commits), the reflog and first-parent times, and the S1 statement's commit.
  - Any hunk in the freeze's files that the [RESULT] calls outside the path has a rule F review of that claim, committed before the label is cited.
  - This delays citing the label; it changes no label.

W1–W3, written as given, need no further proxy pass. The [DECISION] (delegate) names their sentences, carries V1–V5 with the earlier conditions, and records my reason-3(c) error.

**Which later changes need another proxy pass**
- **Needed:**
  - everything on the earlier lists;
  - when a commit counts as joining the branch (W1, M2);
  - what counts as REG-19's table (V1, W2);
  - the S1 statement's timing and consequence (W3);
  - the source of the SEALS listing (M1);
  - what U2 and S2 give.
- **Corrections from the parallel rule F round:** same terms as before. Other words for W1–W3 need a pass. If in doubt, it needs one.
- **A further text-only round** needs me only if it touches that list.

**Notes for the owner**
- **Push `main` to `origin` after the entry is appended and after the record's commit.** `main` is 115 commits ahead of `origin/main`, whose last push was `a7bb77a` on 2026-11-11. A remote copy is the only witness of history that a local rewrite or a reflog edit cannot change. Pushing is your call.
- **Side branches:** a judged-path change made on a side branch and merged after REG-19's table now counts as after the cut (W1). REG-20's work should go into new functions, or land on `main` before `final.sh` runs.
- **Optional:** put a first no-earlier-run statement into the [DECISION] (delegate) at the append. That is always possible for any batch 2 that can govern, and it is blind to everything.
- **I logged one more error of mine (reason 3(c), above).**

**Not checked by me**
- I opened nothing under `runs/`, `state/` file contents or the backups. I did not read rule F's parallel round, or REG-22 draft 12 beyond its record passage.
- I did not run pytest or any analysis; the code is unchanged since `8164211`.
- The reflog is local and can be expired or edited. The no-earlier-run statement and the record's file name both rest on honesty before their commits.
- I cannot tell whether commits are made on the VM. Its remote `vm/main` is 117 commits behind.
