# Owner-proxy delta pass on REG-22 draft 11 (agent a43b6d3c375ffd53e), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:54:43.054Z), no word changed. It replaces the proxy's draft-10 verdict for what it changes; the agent calls its two conditions "U1" and "U2".

---

**Decision: APPROVE**, as a delta pass on REG-22 draft 11 (FILE(docs/drafts/reg22_draft11.md), byte-identical to docs/drafts/review_bundles/reg22_r6/registration_draft11.md) at code `ffc76b3`.
- HEAD is `346ee6c`, and `git diff ffc76b3 HEAD -- analysis harness tests` is empty.
- This approval has no effect while rule F round 6 is outstanding or NOT READY.
- Round 1's conditions 8–16, D1–D8 and Q1–Q7 stay in force. Q7's consequence is now replaced by L1 (reason 1).
- The PROTOCOL re-reading is still not approved.

**T1–T6:**
- T1 is met in line 132: "a rule F review that passed its diff with no open required item"; the exemption limited to the five bodies, not `__main__`; "before batch 1" tested as order (b) tests it.
- T2 is met in line 135.
- T4 is met in line 133, in REG-21's P2 words. The effect is the same, so I accept the wording.
- T5 is met outside the entry: agent/RUNBOOK.md:45 now runs `final.sh`, agent/PLAN.md:56 says "never `analysis.gate reg19` by hand", and RESUME.md carries a superseded note at line 3.
- T6 is met in line 133.
- **T3 is withdrawn.** I accept L1 instead (reason 1).

**Reasons:**
1. **L1 over T3 and R1: accepted, and I change position.** The better argument is L1's (REG-21's rule F round 12).
   - The writer of the batch-2 [RESULT] holds batch 2's output. Under my T3, and under my draft-7 Q7 before it ("if any part is missing, batch 2 is labelled retrospective"), that writer could demote batch 2 by leaving out one citation.
   - That is the same post-data lever I argued against under G3, and I built it myself in Q7. Log it as my error.
   - T3's aim survives. A relied-on commit whose `%ct` is not before the cut gets its rule's consequence from the git facts, whether or not the time is quoted.
   - P2 also follows from git facts (the file name's stamp against the commit's `%ct`), so it is consistent with L1.
   - I do not reject L1. If REG-21's proxy rejects it, the passages diverge, and bringing them back into line needs a pass from me.
2. **The freeze (T1 plus L2): stricter.**
   - A pre-cut hunk now keeps batch 2's standing only if its commit and both reviews, saved and committed, all come before the cut.
   - This closes rule F's L2 route, where reviews were asked for after REG-19's table was public.
3. **The SEALS exemption: accepted.** It cannot change what the command reads.
   - The seal acts only on a folder's name: `sealed_by` uses `fnmatch.fnmatchcase(run_name, pattern)` (FILE(analysis/withheld.py:57–61)).
   - `find_runs` applies `withheld.keep` to the glob results before loading (FILE(analysis/load.py:42)), and `load_run` calls `guard` on the name (FILE(analysis/load.py:20)).
   - A tuple that matches none of the names the command globs therefore skips and refuses nothing.
   - Without the exemption, any new registration with runs would end batch 2 for nothing.
4. **The record (T6, R4, P1, P3, and the agent's lost-record sentence): stricter or neutral.**
   - P3 removes the lever I noted on draft 10: not committing a saved record no longer ends batch 2.
   - A lost record means no record and "not computed". That matches K1, and deleting a file is not delegated anyway.
   - R4 settles the sandbox reading.
   - The passage matches REG-21 draft 20's line 107 sentence by sentence, apart from the sections each one cross-references (I extracted both and diffed them).
5. **Rewrites judged by their new committer time (O-c): looser only for a commit rewritten before the stamp.** Such a rewrite leaks nothing of REG-19. A rewrite after the stamp fails the time test, and a hand-set date counts as after.
6. **Order (b) (R3): accepted.** "At once and alone" becomes a duty, and the other changes in a mixed commit count as after. This mirrors K3 and removes the one-extra-file lever over REG-21's labels.
7. **R2 (line 64), line 21 and line 148: consistent.** Line 64 is complete again.

**Conditions:**
1. **BEFORE the entry is appended (text; it applies L1 to the freeze):**
   - In line 132, the label must follow from the facts, not from what the [RESULT] shows. Whether a hunk lies outside what `reg22_table` and `reported_counts` reach is a fact about the code at the batch-2 commit, as are each hunk's commit, its `%ct` and its reviews' commits.
   - Wording: "an omission or an error in the [RESULT]'s diff, reach argument or hunk list is a [CORR] and never changes a label, as for the record's citations."
   - As written, "shows an empty `git diff` … or shows each hunk to lie outside …" with "Otherwise …" lets the writer demote batch 2 by not making the reach argument.
   - This case is likely, not rare: REG-20 will probably touch `gate.py` or `k1.py` after REG-19's table, and both are in the freeze.
   - The same change belongs in REG-21's freeze if it has the same "shows" wording (not checked by me).
2. **BEFORE the entry is appended (text; an order rule; this is K1 for batch outputs):**
   - In line 130, replace "a batch whose first run did not write its file this way is a deviation, reported, and changes no label" with: "… is a deviation, reported; it changes no label of REG-22, but for order (b) and (c) and for the freeze's 'before batch 1' that batch's table counts as existing from this entry's commit on, so every later change counts as after it."
   - As written, an unsaved first run of batch 1 followed by a saved second run moves the batch-1 time later. A change to REG-21 in between would then escape order (b)'s A5 test. That is K1's hole, reopened for the batch outputs.
   - Whether to redirect the output is decided before the output exists, so the rule gives no lever.

Both conditions, written as given, need no further pass.

**Which later changes need another proxy pass:**
- Everything on my earlier lists: the stopping rule, the not-computed cases (other than adding one), the record and its cut, the freeze and its interval, the order rules, the judged path and any threshold.
- New:
  - the SEALS exemption, if widened beyond "only adds a tuple matching no name";
  - L1's scope, if narrowed;
  - any change to the shared passage not made word for word in both registrations.
- Rule F round 6 corrections need no pass if they are wording, tags, a lower ceiling, a narrower exemption, or an added not-computed case. Anything that makes a citation's omission change a label again needs one, in either direction.

**Notes for the owner:**
- **My own errors to log:** Q7 and T3 created a post-data lever (reason 1). Rule F round 12 and the coordinator caught it, not me.
- **The rule's direction holds.** Each strict rule here is a way to lose batch 2 that is decided before the data; after L1, P3 and R3, none is a choice made after the data. The remaining loss routes are operational: an unsaved run of REG-19's table, a lost record, a post-cut change to a frozen file, or a mid-matrix look.
- **When REG-20 changes code, use new functions, or wait until after batch 2.** Any hunk in the freeze files after the cut makes batch 2 retrospective.
- **Commit the record at once, alone, on `main`.** Whoever runs `final.sh` must do this. P3 makes a late commit survivable, but it is still a breach.

**Not checked by me:**
- `runs/`, the backups, and the contents of any `state/` file (no `reg19_final_*` names exist as of my draft-10 check; I did not re-list them now).
- Rule F round 6.
- REG-21's freeze wording (condition 1's mirror).
- Commits or runs on the VM. Its clock is not the Mac's, and a run of the table there is not clearly covered by "the Mac's clock". I believe no script runs analysis there.
- Whether anyone has already run REG-19's table by hand.
- The full `uv run pytest` and `check_docs`.
