# Owner-proxy delta pass on REG-21 draft 20 (agent a4122f052f465a926), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:56:53.945Z), no word changed. A delta to the round-4 approval and to the passes on drafts 9 to 19; code at `8164211`.

---

**Decision: APPROVE**, with three wording conditions due before the entry is appended (V1–V3) and one later duty (V4). This approves REG-21 draft 20 (FILE(docs/drafts/reg21_draft20.md)), text only, with code at `8164211`. It is a delta to the round-4 approval and to my passes on drafts 9 to 19.

Integrity checks, at HEAD `346ee6c`:
- The bundle's drafts 19 and 20 are byte-identical to their sources, and the bundle diff equals a fresh diff.
- `git diff 8164211 HEAD` is empty for the eight judged-path files.
- My draft-19 verdict and `final.sh` equal their sources.
- `state/` holds no `reg19_final_*` file (names only).
- The shared record passage is the same in both registrations: line 107 here and REG-22 draft 11's line 133 differ, sentence by sentence, only in their references to their own sections.

**Reasons** (line numbers are draft 20's)

1. **L1 is accepted, for both registrations, over REG-22's T3 and R1. This corrects my own reason 9 on draft 19.**
   - **My error, rule A6.** I called draft 19's citation sentence harmless because it "lowers a ceiling". A ceiling is harmless only if no one can lower it after seeing the data. Here the writer of the batch-2 [RESULT] holds batch 2's output and could make batch 2 retrospective by leaving one citation out.
   - **Why I change position:** rule F round 12's L1 is the better argument, and it is the principle I applied myself in P2, where I would not tie a label to a quote written after the output.
   - **What T3 and R1 protect is kept.** They want the time half of the "before" test verified. That half is a fact in git (`%ct`, `merge-base --is-ancestor`, the `git log --all` listing), and under line 107 the label follows from those facts whether or not the [RESULT] quotes them.
   - Line 107's last sentences also remove the clash with the no-record rule.
   - V4 makes sure the facts are actually written down before anyone uses the label.

2. **L2 is accepted; it is stricter (lines 104, 106, 112).**
   - A change keeps batch 2 only if its commit and both reviews are committed before the cut. That closes the route of asking for reviews after the cut.
   - Line 106's "even when batch 1 needs it" costs batch 2 if batch 1 needs a fix after the cut. That cost is correct.
   - **One double reading is left: "approving" (V2).** A rule F review never "approves"; it says READY or NOT READY, and this study's own practice is that a NOT READY round's items get written in. Whether such a change "was approved" would be judged in the batch-2 [RESULT], after the data, and the two answers are "governs" and "retrospective".

3. **The definition of the record (line 107).**
   - **(a) T6, "any output … of `reg19_table()` … or of `reg19_pair`", is accepted in intent, but it has a double reading that must be closed (V1).**
     - `reg19_step` calls `reg19_pair` for every seed done (FILE(analysis/gate.py:2038)) and prints only `done` and `continue` (FILE(analysis/gate.py:2041)).
     - Read as "any output", every queue step since seed 15 already produced "output of `reg19_pair` for a REG-19 seed", and none was saved. So there is no record and batch 2 is already lost.
     - Read as printed output (the coordinator's own words, and T6's intent), batch 2 is untouched.
     - These are opposite outcomes that someone could choose after REG-19's table. The exclusion "`reg19_step`'s `done` and `continue` are not either" names the printed fields, not the internal call.
   - **(b) R4 is accepted.** It narrows the definition, but it was fixed before the data. The sandbox stubs the interpreter: its fake `python` prints `{'fake': 'table', …}` for `analysis.gate reg19` (test_sandbox.sh, the `fakepy` case), so nothing real ran there. Real data stays covered ("a copy of them" counts).
   - **(c) "A saved record lost against P3 … cut unknown … not computed" is accepted.**
     - It replaces two readings with one.
     - Under it, batch 2 can be lost only through a deletion that P3 forbids and CLAUDE.md §C reserves to the owner.
     - With the cut unknown, no "before" can be shown, so batch 2 can only be not computed.
   - **Removing draft 19's "not committed … before batch 2 is computed" is accepted.** P3 orders the commit first. A record committed after batch 2's start is still the record and a reported breach, and the order of the two commits is a fact in git. The file stays editable until it is committed (a renamed stamp, for example). That was true before too; no text can prevent it (see Not checked).

4. **O-c, "a rewritten commit is judged by its new committer time", is accepted.**
   - It is looser than draft 19 only for a commit rewritten before the stamp, and such a rewrite was made before the table existed, so it leaks nothing.
   - A rewrite after the stamp gets a later time, and a hand-set date counts as after.
   - The ban on rewriting stays as a duty.
   - Optional: name `GIT_COMMITTER_DATE` and `git rebase --committer-date-is-author-date` as setting a date by hand.

5. **The SEALS-only exemption (O-b) is accepted in principle, with V3.**
   - `sealed_by` returns the first tuple whose pattern matches (FILE(analysis/withheld.py:54–58)), so a tuple that matches none of the command's folders changes nothing for them.
   - **The set of folders is too narrow as written.** "The reference runs" can be read as the five `ref_runs`. But `reference` globs `ref_pattern` (k3w.py:137), and `find_runs` applies the seal before loading (load.py:42).
   - So a seal on a sixth folder matching `ref_pattern` would change what the command reads, for example by removing the "sixth valid reference run at a rate of 2.0 or more" case, which gives "not computed". The exemption's premise holds only if the set is every folder the command globs.

6. **The rest is accepted.**
   - `test -e`.
   - The source of the `checks.json` exception: FILE(analysis/withheld.py:7) and decisions.md:4256, both verified.
   - The batch stamps taken with `date -u` in the command line that redirects the output (line 113).
   - Both batch outputs committed at once, alone, before any reading.
   - Not taking O-f's second half: it would tie a label to a quote written after the output.
   - P1–P3 are in my words (lines 107 and 112).

7. **Nothing else moves a rule.** The new looser points are O-c, R4 and the SEALS exemption, each fixed before the data and justified above. Everything else is equal or stricter.

**Conditions**

BEFORE the entry is appended. Use the same words in REG-22's line 133 for V1, so the shared passage stays identical:
- **V1 (line 107).**
  - For "Here "REG-19's table" is any output, by any entry point" write: "Here "REG-19's table" is any printed or displayed output (to a terminal, a file, a notebook or a log), by any entry point".
  - After "and `reg19_step`'s `done` and `continue` are not either" add: "; a value that `reg19_pair` or `reg19_table` returns inside another function without being printed or displayed, as `reg19_pair`'s inside `reg19_step` (FILE(analysis/gate.py:2038)), is not output".
- **V2 (line 104).**
  - For "and the rule F review and owner-proxy pass approving it (saved verbatim and committed)" write: "a rule F review of its diff, and an owner-proxy pass that approves that commit and states that every required item of that rule F review is met in it (both saved verbatim and committed)".
  - Add: "Whether the reviews approve is read from those committed texts alone."
- **V3 (line 104).** For "none of the folder names the batch's command finds or names (batch 1's runs, the reference runs and every folder matching the batch-2 pattern, listed in the [RESULT])" write: "none of the folder names in `runs/` that match `REG21['ref_pattern']`, `REG21['batch2_pattern']` or a name in `REG21['batch1']`, taken before any validity check or selection and listed in the [RESULT]".

LATER:
- **V4 (before batch 2's label is cited in `docs/claims.md`, `docs/status.md` or any paper text).** Every fact the citation sentence lists is in the batch-2 [RESULT] or a [CORR], each as the verbatim output of its git command. Delaying this changes no label.

V1–V3, written as given, need no further proxy pass. The [DECISION] (delegate) names their sentences and carries E2, F1, G1, G2, proxy-H1, P1–P3 and V1–V4. The [DECISION] also records my reason-9 error.

**Which later changes need another proxy pass**
- **Needed:**
  - everything on the earlier lists;
  - what counts as output (V1);
  - which reviews keep a change made before the cut (V2);
  - the SEALS exemption and its folder set (V3);
  - any return to a label set by an omission (L1);
  - the rewritten-commit rule.
- **Corrections from rule F round 13:** wording, tags, line references, lower ceilings that the person holding the output cannot trigger, and reported-only duties need no pass. Anything on the needed list does, including other words for V1–V3. If in doubt, it needs one.
- **A further text-only round** needs me only if it touches that list.

**Notes for the owner**
- **V1 matters most.** Without it, a hostile reader can say batch 2 of both analyses was lost at seed 15 through the queue's own `reg19_step` calls.
- **REG-20's changes to the five named `k1` functions** now keep batch 2 only with both reviews committed before REG-19's table. New functions remain the safe route.
- **I changed position on reason 9** because of rule F round 12's L1; it is logged above as my error.
- **Run REG-19's table only through `final.sh`, once,** and commit its two files at once, alone. The stamp in the file name can be faked before that commit, and nothing written can detect it.

**Not checked by me**
- I opened nothing under `runs/`, `state/` file contents, the backups or probe outputs. I did not read rule F round 13, or REG-22 draft 11 beyond its record passage.
- I did not run pytest or any analysis; the code is unchanged since `8164211`.
- I cannot tell whether anyone has printed `reg19_table` or `reg19_pair` outside the queue, whether commits are ever made on the VM, or whether a record file was renamed before its commit.
