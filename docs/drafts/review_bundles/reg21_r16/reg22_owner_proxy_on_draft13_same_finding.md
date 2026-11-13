# Owner-proxy delta pass on REG-22 draft 13 (agent a43b6d3c375ffd53e), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T12:17:15.637Z), no word changed. It saw the bundle `docs/drafts/review_bundles/reg22_r8/`. Its conditions Z1–Z4 are called AA1–AA4 elsewhere, to keep them apart from the Z rows of `agent/PLAN.md`.

---

**Decision: APPROVE**, as a delta pass on REG-22 draft 13 (FILE(docs/drafts/reg22_draft13.md), byte-identical to docs/drafts/review_bundles/reg22_r8/registration_draft13.md) at code `ffc76b3`. HEAD is `3e9c73f`, and `git diff ffc76b3 HEAD -- analysis harness tests` is empty.
- As asked, I checked only items 1–7.
- This approval has no effect while rule F round 8 is outstanding or NOT READY. Every earlier condition in force stays in force.
- Z1 below is required before the entry is appended: without it, a hostile reading says batch 2 of both registrations is already lost.

**Items 1–7:**
1. **W1 merged (sentences 4–7 of line 133): accepted, with one new hole (Z1).**
   - My "in particular" sentences and the exclusions are in: names, seeds, `exposed`, `lam_p`, validity, failed checks, `vm_state` statuses, checksums, the `[run] start` line and the queue lines.
   - Sentence 11 (the saving duty ends once a record is saved; later tables are never the record) is right.
   - **The hole.** N1's lead clause, "a value computed from what the runs measured … whether a run ended cold, backlogged or stuck", is no longer tied to a row field. It now reads onto the recorder's own status line, which every run prints throughout and at its end: `t=… h=… N=… Q=… KV=…` (FILE(harness/recorder.py:141), FILE(harness/recorder.py:150–162)).
   - The last lines of a REG-19 burst run show h ≈ 0, a large Q and KV ≈ 95 %, that is, "ended cold, backlogged". They were printed to the harness's log and terminal from seed 15 on (2026-11-11), and never saved under a stamp in `state/`.
   - On that reading, the first "run that gave REG-19's table" has no record. K1 then applies, and batch 2 of both registrations is not computed today. That is the same class of defect as the queue's `RUN … VALID` lines that my W1 closed.
   - Sentence 7 excludes only the agent's 2026-11-12 look, and its reason ("which is no row field") no longer matches the lead clause.
2. **W2 merged (sentences 30–34): accepted.**
   - The full statement covers runs up to the stamp, committed after the record's commit and before batch 2's command.
   - The early statement covers runs up to its own commit.
   - "Governs" is read from git alone (a strict ancestor of batch 2's output commit, with a `%ct` earlier than that output's stamp).
   - A batch-2 run before the statement makes batch 2 retrospective. That is the only coherent consequence: a statement made after batch 2's output is not blind. It adds no new lever, because post-cut demotion routes already exist.
3. **Y1, order (b) (line 124): accepted.** "First run" now means the first printed output by any entry point. The fallback uses the earliest known time. The owning registration's statement is made at its entry, before the data.
   - But draft 13 does not carry REG-22's own statement (Z2).
   - I found no recorded output of `c2` on the 13 real runs. `analysis/c2.py` was first committed at `44ca82a` (2026-11-12 19:36 UTC), and no tracked file outside `docs/drafts/` names `c2` output. I checked file names only.
4. **Y4: accepted.** Sentence 28: "the check of the record's seeds under 'Runs' is then not made". It matches REG-21.
5. **Y5, the freeze's reviews: accepted in intent, with one double reading left (Z3).**
   - "READY or NOT READY" plus a proxy stating the required items are met is the study's own practice.
   - The double reading: when rule F's items are written in, the final commit's diff is not the diff rule F reviewed. "A rule F review of its diff" can then be read, after the data, as "no review of this diff", which makes batch 2 retrospective.
   - This case is likely: REG-20 is expected to touch `k1.py` and `gate.py`.
   - The readout exemption still requires READY: right.
6. **X1 (sentence 23) and N2 (sentence 36): accepted.** A commit joining after the stamp counts as after whatever its date says, a merge counts as making what it brings in, and the reflog and first-parent facts decide with no reading. Both are stricter.
7. **Rule F's optional items:**
   - **The stamp item: accepted.** A batch file stamped later than its commit counts as unsaved (line 130).
   - **Static reach (line 132): accepted, with one gap (Z4).** It names functions called and the constants they read. A module-level statement that runs at import, in a module the freeze lists for that reason, is neither of those. So it could be argued to lie "outside" even when it rebinds something on the path. The previous wording did not invite that reading, because only function-body hunks were declared outside.
   - **The shared passage:** it matches REG-21 draft 22's line 107 sentence by sentence, apart from cross-references (I extracted both and diffed them).

**Conditions, all BEFORE the entry is appended. Written as given, they need no further pass.**
- **Z1 (both registrations, same words).**
  - In sentence 5's exclusion list, add: "the harness's and recorder's own output while a run is in progress or ending (the `[run] …` events, FILE(harness/run.py:80), and the status lines `t=… h=… N=… Q=… KV=…`, FILE(harness/recorder.py:141, 150–162)), wherever it is shown or kept".
  - Add: "Reading those lines for a REG-19 run is an interim look, not REG-19's table: it is disclosed in the statement and under 'What was known', and moves no cut."
  - In sentence 7, replace "which is no row field" with "which is such output".
  - Other words that keep every run-time line of the harness and recorder out of "REG-19's table" are acceptable only with a pass.
- **Z2.** REG-22's entry itself states, under "What was known", whether any output of `c2.reg22_table`, `levels`, `links`, `sustain` or `condition4` on the 13 real run folders was printed before the entry commit, and gives the time of the first if so.
  - Line 124 requires the statement but draft 13 does not make it.
  - In line 124's parenthesis, "a result of `c2.levels`, `c2.links` or `c2.sustain`" should also name `c2.condition4` (the label).
- **Z3 (line 132; REG-21's freeze too, if it has the same words).** Write "a rule F review of its diff, or of an earlier version of it whose required items were then written in, READY or NOT READY", and "an owner-proxy pass that approves the final commit and states …".
- **Z4 (line 132).** In the static reach definition, after "the module constants those read", add "and every statement that runs at import of a module the command imports, other than a definition that nothing reached uses". Low stakes, but it keeps the new definition from being looser than the old one.

**Which later changes need another proxy pass:** as in my draft-12 verdict, plus Z1's exclusion set and the reviews that keep a hunk (Z3). Corrections from rule F round 8 need no pass if they are wording, tags, a lower ceiling that the holder of the output cannot trigger, or a reporting duty.

**Notes for the owner:**
- **Z1 matters most.** It is the second time a broadened "what counts as REG-19's table" has reached the harness's own unavoidable output. My W1 caught the queue's lines; N1's broadened lead clause reached the recorder's lines. Any future widening of that clause should be tested against every line the harness, recorder and queue print.
- **The auto-commit at the end of `final.sh`** is your decision, as the coordinator said.
- **The remaining loss routes are all operational, and none lets batch 2 be won after the data:**
  - an unsaved table run;
  - a lost record;
  - a batch-2 run before the statement;
  - a post-cut change to a frozen file;
  - a mid-matrix look.

**Not checked by me:**
- Items outside 1–7.
- `runs/`, the backups, any `state/` file contents and probe outputs.
- Rule F round 8.
- Whether anyone read the recorder's status lines of REG-19 burst runs, beyond the 2026-11-12 look RESUME.md discloses.
- REG-21's order text and freeze beyond line 107.
- Commits on the VM.
- The full `uv run pytest` and `check_docs`.