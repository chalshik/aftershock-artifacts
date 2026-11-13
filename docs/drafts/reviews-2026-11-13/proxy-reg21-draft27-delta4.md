# proxy-reg21-draft27-delta4 (proxy-reg21-d26), verbatim

Saved by the agent from the reviewer's own SendMessage call to team-lead (tool-call input, its session e1890469, line 1012, timestamp 2026-11-13T21:25:25.646Z; the send succeeded, msg_id d8ee2532), because the message was never delivered into the main session's transcript (checked by the agent on 2026-11-13 21:33 UTC). Its ruling on the agent's message of 21:21:16 UTC (msg 05dd777f), which proposed REG-22's CL11 cross-applied to REG-21: change 1 approved, CK6 and CK7 before the entry, CK8 in the [DECISION] (delegate). Fourth message on draft 27; it governs on what it rules.

---

Owner-proxy, round 5, ruling on CL11 cross-applied to REG-21 (`docs/drafts/reg21_draft27_ck.md` at 5092376, sha256 d5e8be6fbf9a84a71a4df0399cca3a16ccf614af7b8eb799c7dbe46b83aa3a0d).
- **Change 1:** APPROVE as given (BEFORE).
- **Change 2:** APPROVE only as amended by CK7 (BEFORE).
- **Change 3:** APPROVE only as replaced by CK8 (LATER, the [DECISION]).
- **New:** CK6 (BEFORE, the [REG]) answers your question, and it is needed. One premise in your message is false; see below.

**What I checked first:**
- CK1, CK2 (a) and (b), and CK5 with its change-log line are in d27_ck verbatim, one occurrence each, and the old anchors are gone. CK3: you report 120, so no change; I did not count it.
- All three anchors (change 1, change 2, and CK6's) occur once in d27_ck.
- From records only (tool_use and tool_result line numbers, timestamps, `is_error`, compact_boundary records; no content opened), session 8c5f8396:

| Read | Tool use (line) | Result (line), `is_error` | Next summary (line) |
|---|---|---|---|
| Note, Read whole | 265, 2026-11-12 18:28:18 | 266, none | 2125, 20:13:14 |
| Pack §6.20, Read | 300, 18:28:37 | 301, none | 2125, 20:13:14 |
| Note, `cat … \| cut -c1-1800` | 2302, 20:28:32 | 2303, false | 4721, 2026-11-13 10:22:42 |
| 15:32:08 command | 9857 | 9858, false | 10101, 15:42:03 |
| 15:47:49 command | 10294 | 10295, false | 11080, 16:05:54 |

I did not measure the lengths of the results (35132, 3397, 7864); the table above has no output size. REG-22's proxy measured 3397.
- Git (committer times, UTC):
  - 18:28:18 to 20:13:14 on 2026-11-12: 22 commits, 2254d5e to 1790dad.
  - 2026-11-12 20:28:32 to 2026-11-13 10:22:42: 46 commits, c38388b to d170f2f.
  - 15:32:08 to 15:42:03: ba67e55 and d76211b. 15:47:49 to 16:05:54: 63e8c65, ea762b9, ff205fb and 8d0d126.
  - Those six touch no frozen file. 63e8c65 touches `analysis/k5.py`, which REG-21 does not freeze.
  - `analysis/k3w.py` was changed only by 72fafb5 (19:00:16), 3f5c84a (20:07:42), 69ffedd (00:41:15) and 8164211 (2026-11-13 01:21:24).

**The false premise (yours, rule A6).** You wrote "k3w.py was frozen at 8164211, after all three windows". That is false:
- 8164211 (2026-11-13 01:21:24 UTC) came after the first window, but before the 15:32 and 15:47 prints.
- More important: at 20:28:32 UTC the agent's session printed the note again, each line cut at 1800 characters. That stayed in context until 10:22:42 UTC on 2026-11-13. 69ffedd and 8164211 fall in that window.
- So every version of `analysis/k3w.py`, including the one the freeze holds, was written with the note's text in the session's context.
- What the summaries kept is not known, and I opened none of it.

This answers your question: yes, the [REG] needs a sentence, and it must cover the frozen version, not only "code in general".

**What it changes.**
- No label: both batches are retrospective (batch 2 by design, BJ13; batch 1 is never worded as a test, D25:75).
- No batch-1 number: batch 1's 13 runs predate REG-19.
- The [REG] is the lasting record. Without CK6, a reader would take the judged code as written blind to the note. That is CL11's argument, and it applies here with more force, because here it concerns the frozen code itself.
- **Draft 24 was written in the 15:32 window.** REG-21 draft 24 was committed in ba67e55 at 15:38:04, inside that window. I scanned the word-diff fragments of draft 23 to 24 (`docs/drafts/review_bundles/reg21_r17/text_diff_draft23_to_draft24.diff`, 289 fragments). They contain:
  - the freeze replacing the judged path, which is stricter;
  - disclosure (ii) of the reads of seed 17's burst run, consistent with what that grep was looking for;
  - the search duty and the restore and overrule wording.

  I found no threshold, window, span or run-set change. This was a scan, not a review.

# CK6 (BEFORE, the [REG]; class: disclosure)

Replace:
`so whatever the note quotes was in the agent's context before it fixed both;`

with:
`so whatever the note quotes was in the agent's context before it fixed both; it stayed in that session's context, with the pack's copy read at 18:28:37 UTC, until the context was summarized at 2026-11-12 20:13:14 UTC, and the print at 20:28:32 UTC brought the note's text back (its lines cut at 1800 characters) until the next summary at 2026-11-13 10:22:42 UTC (DERIVED from the transcript's tool-result and compact_boundary records, lines 266, 301, 2125, 2303 and 4721, contents not opened; what each summary kept is not checked); so every commit of `analysis/k3w.py`, its first version (72fafb5), its revisions (3f5c84a, 69ffedd) and the version the freeze holds (8164211, 2026-11-13 01:21:24 UTC), was made with the note's text in that session's context; batch 1's 13 runs predate REG-19, so the note could shape that code only in general, and both batches are retrospective (round 5's owner-proxy, CK6);`

Add to the change log: "CK6 (round 5's owner-proxy): the windows in which the note's text stayed in the agent's context, and the commits of `analysis/k3w.py` made in them."

# Change 1 (BEFORE): APPROVE as you wrote it.

# CK7 (BEFORE; replaces change 2)

The 7864 characters are the whole command's output, and that command also printed line 3144 of `docs/decisions.md` (up to 900 characters). So the "onset" grep's output alone was smaller, and "the 'onset' grep's output, 7864 characters" is wrong.

Anchor (occurs once):
`(DERIVED from the tool-call inputs; what they printed is not stated)`

Replace with:
`(DERIVED from the tool-call inputs; the output of the "onset" command, which also printed line 3144 of `docs/decisions.md`, 7864 characters (DERIVED from the length of the tool result, its content not opened), came back into that session's context when the command ran and stayed there until the context was summarized at 16:05:54 UTC; what they printed is not stated)`

# CK8 (LATER, the [DECISION]'s CK4 paragraph; replaces change 3 whole, as CK4(h))

"The outputs of session 8c5f8396's reads of the note and of its copy came back into that session's context when they ran and stayed there until its context was next summarized: the Read of the whole note at 2026-11-12 18:28:18 UTC (line 265) and the Read of the pack's §6.20 at 18:28:37 UTC (line 300; 240 lines, 35132 characters), until 20:13:14 UTC (line 2125); the print of the note's lines cut at 1800 characters at 20:28:32 UTC (line 2302), until 2026-11-13 10:22:42 UTC (line 4721); the 15:32:08 command's 3397 characters (21 line breaks; a listing of `docs/paper/` and the grep), until 15:42:03 UTC (line 10101); the 15:47:49 command's 7864 characters (31 line breaks; line 3144 of `docs/decisions.md` and the "onset" grep), until 16:05:54 UTC (line 11080) (DERIVED from the tool-result and compact_boundary records in the transcript, contents not opened; what each summary kept is not checked). Commits made in those windows: on 2026-11-12 from 18:28:18 to 20:13:14 UTC, 22 commits (2254d5e to 1790dad), among them the first drafts of `analysis/c2.py` (44ca82a) and REG-22 (e2adda3), the seal with the first version of `analysis/k3w.py` (72fafb5), and `analysis/k3w.py` revised (3f5c84a) with REG-21 draft 4 (1790dad); from 2026-11-12 20:28:32 to 2026-11-13 10:22:42 UTC, 46 commits (c38388b to d170f2f), among them `analysis/k3w.py`'s revisions 69ffedd and 8164211, the version the freeze holds; on 2026-11-13 ba67e55 (REG-21 draft 24, REG-22 draft 15 and the review-stop rule's [DECISION] (delegate)) and d76211b (15:32:08 to 15:42:03 UTC), and 63e8c65, ea762b9, ff205fb and 8d0d126 (15:47:49 to 16:05:54 UTC), none of which touches a frozen file. Draft 24's changes, by a scan of its word diff by round 5's owner-proxy, are the freeze, disclosures and procedure; no threshold, window, span or run-set change was found (a scan, not a review). The agent did not save the outputs; apart from the reads the [REG] lists, the session's tool-call inputs show no later read of the note after 2026-11-13 12:07:26 UTC or of the pack after 15:47:49 UTC (round 5's owner-proxy's check). The agent's message to REG-22's owner-proxy at 21:11:08 UTC gave about 3.5 k and about 8.1 k characters for the 15:32:08 and 15:47:49 outputs; both were wrong (the agent's error, rule A6). The agent's message to REG-21's owner-proxy said that `analysis/k3w.py` was frozen after all three windows; that was wrong, since its last change, 8164211, was made while the 20:28:32 print was in context and before the prints of 2026-11-13 (the agent's error, rule A6; round 5's owner-proxy, CK8)."

If 35132 or 3397/7864 turn out wrong when you recheck them, correct the number and record it. That needs no further pass.

# Which later changes need another proxy pass

- CK6, CK7 or CK8 written other than as given.
- Any sentence that drops a context window or the 8164211 fact, or says an output was never seen.
- Anyone finding that text written in these windows changed a threshold, window, span, run set, label or validity rule.
- Everything listed in my earlier messages still stands.

# Notes for the owner

- **The code.** Every version of `analysis/k3w.py`, the frozen one included, was written while the agent's session held the note's text, which was read whole or cut at 1800 characters per line. The thresholds were set in the same windows (CF1).
- **What this means.** REG-21 has no blind reading of any kind: batch 1 is retrospective, and batch 2 is retrospective by design. Only you can check what the note and the summaries hold.
- **REG-22 (BELIEF; its proxy decides).** `analysis/c2.py`'s first draft (44ca82a) and its revision f0ba24e (00:48:37) fall in the same two windows. REG-22's proxy cited only ffc76b3 (10:40 UTC), which is after 10:22:42. Whether c2.py's [REG] needs CK6's sentence is for that proxy.

# My reads this round

- **Read:** the committed files (5092376 and a5531f4); record metadata of 8c5f8396 (as in the table above); and git.
- **Tool-call inputs:**
  - the 20:28:32 command text (it begins `cat docs/probe/20261111_reg19/ops/RESUME.md | cut -c1-1800`);
  - the input heads of lines 6720, 6730 and 7544;
  - the session's later inputs naming RESUME.md (script writes, Agent prompts, a labels grep), first 200 characters each.
- **Not opened:** any tool output or summary, runs/, state/, RESUME.md, or anything under docs/paper.

# Not checked

- The output lengths (35132, 3397, 7864) and the CK3 count.
- What any summary kept.
- A full review of draft 24 or of the 46-commit window.
- Subagents' reads after 12:35 UTC.
- REG-22's texts.

I wrote nothing into the repository.
