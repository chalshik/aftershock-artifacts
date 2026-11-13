# Owner-proxy delta pass on REG-22 draft 12 (agent a43b6d3c375ffd53e), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T12:06:35.899Z), no word changed. The agent calls its conditions "W1" to "W3".

---

**Decision: APPROVE**, as a delta pass on REG-22 draft 12 (FILE(docs/drafts/reg22_draft12.md), byte-identical to docs/drafts/review_bundles/reg22_r7/registration_draft12.md) at code `ffc76b3`. HEAD is `b8ea915`, and `git diff ffc76b3 HEAD -- analysis harness tests` is empty.
- This approval has no effect while rule F round 7 is outstanding or NOT READY.
- Round 1's conditions 8–16, D1–D8, Q1–Q7 (Q7 as replaced by L1), T1, T2, T4–T6 and U1–U2 stay in force. Condition W1 below is required before the entry is appended.
- The PROTOCOL re-reading is still not approved.

**U1, U2 and the process point:**
- **U1 is met in my words:**
  - in the freeze: "facts about the code at the batch-2 commit and about git … a [CORR] and never changes a label";
  - in the commit order: "(a fact in git: an omission in the [RESULT] is a [CORR] …)".
- **U2 is met in better words. My U2 was wrong for order (c); log it as my error.**
  - Order (c) is REG-21's batch 1 computed before REG-22's entries (FILE(docs/drafts/reg22_draft12.md:125)). "This entry's commit" can be later than that batch's true time, so my wording would have counted some changes as before when they were after.
  - The owning registration's entry commit is never later than its batch. Under (b), the named commit may be earlier still. Taking the earliest of the two is correct and stricter.
- **Rule F round 6's process point:** I passed L1 in place of T3 in my draft-11 verdict (reason 1). Line 188 records that.

**Reasons:**
1. **S1 is accepted in principle. It moves the one label-bearing fact that is not in git to before batch 2's output.**
   - Before S1, the writer chose after the data whether to disclose an earlier run.
   - The cost: an earlier run found only after batch 2's output no longer voids batch 2. It becomes a [CORR] with no label effect. That is the right trade. The owner keeps the power to overrule, and the [CORR] makes the fact public.
   - One reading is still open (W2).
2. **S2 is accepted, but rule F overstates what it closes. I change position on my draft-11 reason 4 for a different reason than rule F gives.**
   - Under draft 11 a lost record gave "not computed". Under draft 12 it gives "retrospective". Batch 2 governs nothing in either case.
   - So a `git clean` after REG-19's table still demotes batch 2 from governing to not governing. S2 does not remove that lever; it keeps batch 2's numbers reported.
   - I accept S2 because it is what the other rules give anyway (the cut is unknown, so the commit order fails) and it tells readers more. It does not close a lever.
   - The lever is narrowed by the commit duty, by P3 (no saved `reg19_final_*` file may be deleted or moved), and by the delegation (deleting anything is not delegated). See the note on `final.sh` below.
3. **The SEALS names from a directory listing (M1/O1) are correct and close the circularity.**
   - A seal acts on names (FILE(analysis/withheld.py:54–60)), and `find_runs` filters through `keep` before validity (FILE(analysis/load.py:42)), so the names must come from the directory.
   - `*_stage2_control_l1pl350cl_r*` is a superset of what `control_readout` globs. The derived name is `stage2_control_` + the burst name's tail (FILE(analysis/c2.py:299)), and the one explicit mapping is to `stage2_control_l1pl350cl_r2.4` (FILE(analysis/c2.py:384)). Both match.
   - Batch 1 looks up 13 exact names (FILE(analysis/c2.py:401)).
4. **M2 (rewrites) is stricter than draft 11 and accepted.** A rewrite after the stamp, or any date not taken from the clock, counts as after. The reflog and the first-parent `%ct` are quoted as facts, so their omission is a [CORR].
5. **V2 (the reviews read from their committed texts alone) is accepted.** It closes the "approved?" double reading, which would otherwise be judged after the data.
6. **V1 ("printed or displayed"; values inside `reg19_step` are not output) is accepted.** O-6 ("a copy" is any folder holding a file copied or derived from a REG-19 run) is accepted and stricter.
7. **O-3 opens a hostile reading that kills batch 2 today (W1).**
   - O-3 counts as REG-19's table "any other function that prints, for a REG-19 run, a value that a row of `reg19_table` holds". Rows hold `seed` and `runs`, the run ids (FILE(analysis/gate.py:2055–2056)).
   - REG-19's queue has printed run ids since seed 15: `echo "RUN $cfg $rid VALID"` and the `COPIED $rid …` line (FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:41, :54, :66)). The same holds for the earlier queues.
   - Read literally, the first "run that gave REG-19's table" was an unsaved queue line on 2026-11-11 or 2026-11-12. Then there is no record under K1, batch 2 of both registrations is not computed, and the S1 statement cannot be made truthfully.
   - The examples in parentheses (a verdict, an outcome, `c`) show the intent. The literal words still allow the other reading, and that choice would be made after the data. This is the same kind of defect REG-21's proxy closed with V1.
8. **The shared passage matches REG-21 draft 21's line 107 sentence by sentence, apart from cross-references.** I extracted both passages and diffed them.

**Conditions:**
1. **W1, BEFORE the entry is appended (both registrations, same words; it changes what counts as REG-19's table, so it is on my list; written as given it needs no further pass).**
   - After "(a verdict, an outcome or the completion rate `c`; `reg19_cold_side`, FILE(analysis/gate.py:1834), for one)", add: "that is, a field computed from a REG-19 run's measured data (its requests, metrics or logs): every row field except `seed`, `runs`, `exposed` and the planned rates, which come from names, configs or schedules. A run's name, id or seed, its validity flag and the checks that set it (`checks.json`; the queue's `RUN … VALID/INVALID`, `COPIED` and `RECHECK` lines), and `reg19_step`'s `done` and `continue`, are not REG-19's table. Nor is the live hit rate the agent read in seed 17's control's harness log on 2026-11-12 (FILE(docs/probe/20261111_reg19/ops/RESUME.md:20–21)), which is no row field; it is listed under 'What was known'."
   - If the agent prefers other words, they need a pass. The result must be the same: no identifier, validity line or gauge reading already printed can be read as the first run of the table.
2. **W2, BEFORE the entry is appended (both registrations; text):**
   - The S1 statement covers every run up to the record's stamp.
   - If it is committed before `final.sh` runs, a second statement covers the time from its own commit to the stamp. That second statement is committed in its own entry after the record's commit and before batch 2's command. It is still blind to batch 2's output.
   - A run made known before batch 2's command runs is stated in such an entry, and K1 applies to it. Only a run made known after batch 2's output exists is a [CORR] that changes no label.
   - Why: as written, a run between an early statement and the stamp, or one disclosed between the statement and batch 2, has two readings: "what it states governs" (batch 2 governs) or K1 (no record).
3. **W3, LATER (before batch 2's label is cited in `docs/claims.md`, `docs/status.md` or any paper text; mirrors REG-21's V4):** every fact the citation sentences list is in the batch-2 [RESULT] or a [CORR], each as the verbatim output of its git command. Delaying this changes no label.

**Which later changes need another proxy pass:**
- Everything on my earlier lists: the stopping rule, the not-computed cases (other than adding one), the record and its cut, the freeze and its interval, the order rules, the judged path and any threshold.
- New:
  - what counts as REG-19's table (W1 and V1);
  - the S1 statement's timing and reach;
  - the SEALS name set;
  - the rewrite rule.
- Rule F round 7 corrections need no pass if they are wording, tags, a lower ceiling that the holder of the output cannot trigger, or a reporting duty. Anything that lets a post-data act change a label, in either direction, needs one.

**Notes for the owner:**
- **W1 matters most.** Without it, a hostile reader can argue that batch 2 of both analyses was already lost on 2026-11-11 or 2026-11-12, through the queue's own `RUN … VALID` lines.
- **One governing lever remains:** losing the record after REG-19's table is computed and before its commit (reason 2). An auto-commit of the two `state/reg19_final_*` files at the end of `final.sh` would close the window. That changes REG-19's ops script, so it is your decision, with an [OPS] entry.
- **My errors to log:**
  - my U2 wording for order (c);
  - my draft-11 reason 4, which accepted "not computed" for a lost record (it was no worse in governing terms than "retrospective", but less informative).
- **What I check per draft.** Every draft since 9 has tightened the record passage, and each round finds the next double reading. From here on I would check only W1, W2 and whatever rule F round 7 adds.

**Not checked by me:**
- `runs/`, the backups, and the contents of any `state/` file.
- Rule F round 7.
- Whether any earlier output printed a measured row value for a REG-19 run. I saw the queue's print lines and RESUME.md's disclosure only, not the queue output files.
- Commits or runs on the VM.
- The full `uv run pytest` and `check_docs`.
