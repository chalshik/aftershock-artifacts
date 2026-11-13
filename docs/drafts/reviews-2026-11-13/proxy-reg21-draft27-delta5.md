Saved by the agent from the reviewer's own SendMessage call to team-lead (tool-call input, its session e1890469, line 1110, timestamp 2026-11-13T21:57:47.337Z), because the message was never delivered into the main session's transcript. Its ruling on the agent's message of 21:53 UTC (msg 7187d040), REG-22's CL14 and CL15 cross-applied and the queue-end sentence: APPROVE, CK9 before the entry, CK10 in the [DECISION] (delegate). Fifth message on draft 27; it governs on what it rules.

---

Owner-proxy, round 5, on `docs/drafts/reg21_draft27_ck.md` at fca9a09 (sha256 eb5d9cde74cb231a4c9542dd27b78db362f1939bf89cf35850d86d3f02abf65a; the working tree is the same file). Verdict: APPROVE, on CK9 (BEFORE) and CK10 (LATER, the [DECISION] (delegate)). Your items 1 to 4 are approved, with item 2's sentence amended by CK9.

# What I checked

**Earlier items, verbatim:** change 1, CK6 and CK7 each occur once in fca9a09, as I wrote them. They were applied in 05f48a3. CK1, CK2 and CK5 were checked at 5092376.

**Item 1, CL14 cross-applied:**
- The new list reads correctly with REG-21's own clause kept ("in parts, and once whole by Read at 12:23 UTC, at 2026-11-13 11:38–12:23 UTC").
- From tool-call inputs:
  - 4e055435 line 73: a Read of the whole note at 18:43:28.
  - 49020ad6 line 69: a Read of the whole note at 19:23:24.
  - 8c5f8396's Agent calls "Owner-proxy: REG-19 resume" at 18:43:06.526 (line 647) and 19:22:55.356 (line 1138).
  - Subagent reads: a6a8a3241c lines 158 and 164 (00:41:20, 00:41:28); ad7f6f660b line 111 (00:46:09); a5f4a6d2ba line 153 (01:24:35, `sed -n '12p;15p;20p' … | cut -c1-420`).

**Item 2, the nine reads.** I listed every read-like tool-call input that names the note, `s6.md`, `ctxpack` or the pack, across all transcripts, from 2026-11-12 17:59 to 2026-11-13 01:30 UTC (inputs only). Each of the nine matches its description:

| Time (UTC) | Where | What the input shows |
|---|---|---|
| 18:01:51 | fdf13821, ad7b5aba70 line 286 | `grep -n -i "350\|420\|reboot"` on the note, `cut -c1-250 \| head` |
| 18:07:30 | a625ca98 line 324 | three table rows, `head -3` and `tail -3` of `s6.md` |
| 18:07:47 | a625ca98 line 332 | `tail -8` of `s6.md` |
| 18:07:53 | a625ca98 line 336 | 16 lines from `### 6.20`, at 170 characters each |
| 18:12:45 | fdf13821 main line 4152 | lines naming `w3000_s1[5-7]`, filtered, `cut -c1-220 \| head -20` |
| 18:12:52 | fdf13821 main line 4156 | see CK9 |
| 18:24:32 | 8c5f8396 line 112 | `grep -o` of path strings only |
| 18:50:58 | 8c5f8396 line 800 | lines naming `sweep_l1pl350_pc_off_r` in the pack |
| 00:30:03 | 8c5f8396 line 2624 | `grep -n 'interim look\|last ~15 lines'` on the note, `cut -c1-80` |

I also checked the other hits in that window that the list does not name. Lines 340, 4169 and 4173 of fdf13821, line 192 of a2a5c2cef9 and line 298 of a6a8a3241c are edits, counts, a `git log` of the note's history, and a grep of a docs file for the string "RESUME.md:13". None prints the note or §6.20.

**CK6 still holds.** Of 8c5f8396's three new reads:
- 18:24:32 prints paths only, and it is earlier than 72fafb5.
- 18:50:58 and 00:30:03 fall inside CK6's windows.

So no commit of `analysis/k3w.py` changes side, and CK6's conclusion stands.

**Item 3, the queue end:**
- `reg19_step` returns `"continue": bool(remaining and reg18_continue(rows, remaining))`, with `remaining = len(order) - len(done)` (FILE(analysis/gate.py:2040), FILE(analysis/gate.py:2041)).
- The step line that 538f400's [OPS] quotes is "'done': [15, 16, 17, 18, 19] 'continue': False", so `remaining` is 0. The flag is False whatever the runs show, and the sentence is right.
- It is a disclosure that adds nothing. Approved.

**Item 4, the change log:** approved.

**538f400's [CORR]** (a subagent edited `analysis/e1.py` in the main checkout at 21:38):
- `analysis/e1.py` is not one of REG-21's 26 frozen files.
- An edit left in the working tree is already caught when batch 2 is computed: `_dirty` refuses a dirty tree, and fact (1) requires `git status --porcelain -- <the frozen files>` to print nothing.
- This is no condition, but see note 2.

# CK9 (BEFORE; wording; in the sentence item 2 added)

The 18:12:52 print is not "two line ranges". Its first part is filtered to lines naming `w3000`, REG-19's runs: `awk 'NR>=4573 && NR<=4860' $P | grep -n "w3000" | cut -c1-260 | head -8; sed -n 6000,6028p $P | cut -c1-200`. That filter is the part that matters, and the caveat should cover it as well as the 18:12:45 print.

Anchor (occurs once in fca9a09):
`and two line ranges of that assembly, which an earlier `assemble.py` built, so whether they held §6.20 is not known (the first of these may include the note's lines that name those seeds' runs;`

Replace with:
`and, from that assembly, which an earlier `assemble.py` built, so whether these lines held §6.20 is not known, its lines naming `w3000` among lines 4573 to 4860 (the first 8, cut at 260 characters) and its lines 6000 to 6028 (cut at 200 characters) (the first two of these prints may include the note's lines that name REG-19's runs;`

The rest of that parenthetical stays as it is ("the owner can state whether …"). The change log records CK9 in one line. The same sentence is in REG-22. Whether it needs the same change is for REG-22's proxy (BELIEF that it does).

# CK10 (LATER, the [DECISION] (delegate); a reporting duty and a stricter rule; CL15 cross-applied)

- (a) The [DECISION] cites `docs/probe/20261113_transcript_search/noteread.py`, its output `noteread_20261113T214908Z.txt` and `noteread_labels.tsv`, each with its commit.
- (b) It lists every first-class hit by time, with its session, line and whether REG-21's [REG] names it. This covers every hit up to E, not only those before REG-22's freeze.
- (c) `search2.py` has no pattern for the note or the pack (REG-22's CL15), so the search run at this entry's commit does not cover them. At E, `noteread.py` is run again, inputs only. The [DECISION] reports its new first-class hits since 21:49:08 UTC, or that there are none.
  - A new hit is added to the [REG] as a disclosure before the append.
  - If it reads a line a REG-19 burst run wrote after its burst began, the [REG]'s trigger applies as written.
- (d) It carries CK8 as given, which you said goes into the [DECISION].

# Which later changes need another proxy pass

- CK9 or CK10 written other than as given.
- Any other edit of the [REG] text after fca9a09.
- At E, a new note or pack read in session 8c5f8396 or its subagents before 8164211 that changes which `k3w.py` commits CK6 names. I expect none: every one of them is already inside a window.
- Everything listed in my earlier messages still stands.

# Notes for the owner

1. The note was read whole by two further sessions, REG-19's resume proxies, at 18:43 and 19:23 UTC on 2026-11-12. In parts it was read by four of the agent's subagents overnight. None of this changes a label: both batches are retrospective.
2. 538f400's [CORR] limits code-editing subagents to their own worktree only while a queue runs. Until both batch 2s are computed or declared not computed, the same limit protects REG-21's freeze (BELIEF; the `_dirty` gate catches a dirty tree, not a committed change).
3. REG-19's step after seed 19 printed only `done` and `continue: False`, which carries no information here. REG-19's table waits for both entries.

# My reads this round

- **Committed files:** fca9a09 (the draft), a5531f4 and fca9a09's proxy files, 538f400's decisions entries, and `analysis/gate.py`.
- **Tool-call inputs** in every transcript for 17:59 to 01:30 UTC that name the note or the pack, first 200 characters each; three of them were subagents' handback messages, of which I saw no outcome. I also printed short contexts of nine commands, and the Agent-call heads at 18:43:06 and 19:22:55.
- **No tool output opened:** not noteread's, and nothing under runs/, state/, docs/paper or RESUME.md.

# Not checked

- noteread's output and labels (a probe output), and so the count of 46 first-class hits.
- Whether every first-class hit after 01:30 UTC on 2026-11-13 is named in REG-21's [REG].
- REG-22's texts.
- pytest and check_docs.

I wrote nothing into the repository.
