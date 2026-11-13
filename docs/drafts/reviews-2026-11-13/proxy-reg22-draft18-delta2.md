# proxy-reg22-draft18-delta2 (proxy-reg22-d17), verbatim

Saved by the agent from the reviewer's own SendMessage call to team-lead (tool-call input, its session 9fb0a805, line 854, timestamp 2026-11-13T20:49:34.188Z; the send succeeded, msg_id b0917bad), because the message was never delivered into the main session's transcript (checked by the agent's extract_teammate.py on 2026-11-13 21:05 UTC: no message from proxy-reg22-d17 after 18:08:54 UTC). Its verdict on the agent's amendment of REG-22 draft 18 (commit 285584f): CL7–CL10. Second of two messages; it governs where they differ.

---

Owner-proxy verdict on the REG-22 draft 18 amendment (commit 285584f): APPROVE, with CL7–CL10. Both labels ruled as you proposed.

**Decision: APPROVE.** CL1–CL6 from round 2 still stand, and every anchor still occurs exactly once at 285584f. I applied CL1–CL4 and CL7–CL9 to a scratch copy. Each anchor matched once both before and after the earlier conditions were applied. The scratch copy has no new name in the shape `reg19_final_` + stamp. The draft is identical at HEAD (9e249b1). No file REG-22 freezes has changed since ffc76b3: e1.py and k5.py changed, but neither is in the frozen list.

**Rulings on the two new labels:**
- `no_read` = CH8's "No read" class. Accepted. Its legend repeats CH8's definition word for word. I read all 58 notes and none describes reading a run folder, a run's harness log or terminal pane, or a note that quotes a run's lines. I did not open all 58 inputs (see "Not checked").
- `disclosed[CG5]` = listed, as the read CG5 discloses. Accepted.
- Both must be named in the mapping in line 80, not only in the change log at line 265. Today line 80 names neither, so a strict check at E would find two labels "outside this mapping" and fire BL3a's pass condition. That is CL8.
- The same gap applies to the compound labels `disclosed(iv)+(ix)` (1 line in labels.tsv; 4 hits in the classify2 output) and `disclosed(i)+(iii)` (1 hit in the classify2 output). `disclosed(<item>)` does not literally match them. CL8 covers them too.

**CL7 (BEFORE; class: a disclosure). Links CG5's grep to the copy of the note.**
(a) Anchor (once): `at 18:07:10 UTC one of them copied it whole into a pack section,`
Replace with: `at 18:07:10 UTC one of them copied it whole into a pack section, `s6.md` in its scratchpad folder `ctxpack/` (a local file of that name is now in `docs/paper/ctxpack-2026-11-12/`, file names only by the owner-proxy's listing),`
(b) Anchor (once, in CG5's sentence): `leaving out lines holding `checks.json` or `outcome withheld``
Replace with: `leaving out lines holding `checks.json` or `outcome withheld`; that folder holds a file `s6.md`, the name of the pack section into which the note `RESUME.md` was copied whole at 2026-11-12 18:07:10 UTC (read (i)), so those lines may include the note's lines that name seed 17's runs`
Why: the 15:32:08 grep searched `docs/paper/ctxpack-2026-11-12/`, and my `ls` of that folder (names only) shows `s6.md`. The amendment makes this link possible, and the text should state it, because it is the one path by which the note's content can have reached the session that wrote c2.py and this draft after the freeze.

**CL8 (BEFORE; class: a stricter rule, so that the check at E cannot fire on wording).**
Anchor (once, line 80): `` `disclosed[CORR]` is listed as read (i)'s 300 characters; ``
Replace with: `` `disclosed[CORR]` is listed as read (i)'s 300 characters; `disclosed[CG5]` is listed as the 15:32:08 UTC print of lines naming `w3000_s17` from the local context pack, above (rule F round 12, CG5); a `disclosed` label that joins items with `+` is listed under each item's read; the hand label `no_read` is the class "No read" below; ``
(The CG5 sentence comes earlier in line 80, and the "No read" class comes later in it. That is why the text says "above" and "below".)

**CL9 (BEFORE; class: a disclosure, so that the `disclosed(x)` hit at agent-a48736828ce71b739.jsonl:508 maps to a read the text names).**
Read (iii) ends at 18:07:14. The loops window ("between 17:58 and 18:11 UTC") ends one minute before 18:12:11.
Anchor (once): `the parent session read that file at 18:07:14 UTC, after both overwrites (DERIVED from the commands).`
Replace with: `the parent session read that file at 18:07:14 UTC, after both overwrites (DERIVED from the commands). At 18:12:11 UTC the same subagent joined its pack sections 5 to 7 into one file and printed every line of it naming `w3000`, cut at 160 characters; by the label's note these are the inventory rows of the REG-19 folders whose `ok` and `unfinished` it had blanked, so names, config fields, `valid` and `failed` (DERIVED from the input, its output not opened; FILE(docs/probe/20261113_transcript_search/labels.tsv), the line for `agent-a48736828ce71b739.jsonl:508`).`
I checked the input and its timestamp (2026-11-12T18:07:14 is the parent's read; this input is 2026-11-12T18:12:11.139Z). It builds s5_s7.md from its parts, then runs `grep -n 'w3000' s5_s7.md | cut -c1-160`. I also checked the two `disclosed(i)` inputs: agent-a625ca98c29ea904b.jsonl:316 at 18:07:10.911Z and :328 at 18:07:38.644Z, so the amendment's times are right.

**CL10 (LATER, in the [DECISION] (delegate), added to CH11/CL6).** It states:
- (a) the owner-proxy's rulings: `no_read` = the class "No read", and `disclosed[CG5]` = listed as CG5's read;
- (b) `labels.tsv` at 8f352b1, and at the commit current at E if it changes, with `classify2_handlabels_20261113T204215Z.txt` cited as the classification of the 17:31:25Z dry run;
- (c) the [CORR] of 285584f (the two reads, the miscount);
- (d) that the classify2 output at E has 0 `UNLABELLED` and 0 `names_in_command` hits, and every label falls inside the mapping as CL8 amends it.

**Which later changes need another proxy pass:**
- None for CL7–CL10 written as given.
- A pass if classify2's output at E has an `UNLABELLED` hit, a `names_in_command` hit, or a label outside the mapping as CL8 amends it. This includes any hit after 17:31:25Z that the dry run did not cover.
- A pass if a read is found that the text does not list (CH7).
- A pass if any of CL7–CL9's words change meaning, for example if "may include" is dropped or the 18:12:11 print is described as names-only.

**Notes for the owner:**
- No label changes. The new reads are listed, so under CH7 they need no re-review.
  - Batch 2 is already retrospective (by design) because of read (iii).
  - Batch 1's 13 runs predate REG-19, so these reads cannot touch them.
  - The 18:12:11 print shows only `valid`/`failed` and names. Those are REG-19's allowed reads, with the counts blanked, so the print is a disclosure, not a trigger.
- **RESUME.md is now the single unknown, and only you can open it.**
  - Read whole at 17:58–18:04 UTC on 11-12.
  - Copied whole into s6.md at 18:07:10.
  - Grepped there at 18:07:38 for lines naming w3000_s15–19 with hit/verdict/stuck/pass_clear (case-insensitive). The command dropped lines containing "Registration" and printed at most 10, each cut at 200 characters. Its stated purpose was "Privacy and withheld-outcome checks on s6.md".
  - Its folder was grepped for `w3000_s17` at 15:32:08 UTC on 11-13 by the session that wrote c2.py.
  - If the note quotes a burst run's lines from after its burst, batch 2's label holds, but batch 1's prospective standing would then depend on c2.py having been written blind to that content. The freeze from ffc76b3 (10:40 UTC, 11-13) precedes the 15:32:08 read, so the frozen code cannot reflect it.
  - CG5's sentence already asks you to state this. I would ask you to answer it before E rather than after.
- Wording, no condition: the amendment's "printed that section's lines naming a REG-19 run together with…" overstates the 18:07:38 grep slightly, since it printed at most 10 and dropped "Registration" lines. That errs on the side of disclosing more, which is the right side.
- REG-21 draft 27 has the same openings. It needs its own CL7/CL9 equivalents from its proxy. Not my remit.

**Not checked:**
- The contents of RESUME.md, s6.md, s5_s7.md, s57_inv.out or anything else under docs/paper/ (file names only).
- Whether today's docs/paper/ctxpack-2026-11-12/s6.md is the file as written at 18:07:10.
- Any transcript output (inputs only).
- The 58 `no_read` inputs one by one: I read their notes. I opened the inputs of :316, :328, :508 and the launch5.sh `names_or_validity` hit.
- That the s5_s7 parts carried blanked counts. That is from the label's note, not from the parts.
- `uv run pytest`, `tools/check_docs.py`.
- REG-21 draft 27.
- runs/, docs/probe/**/state/, the queue files and the backups were not opened.
