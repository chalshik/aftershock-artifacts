# proxy-reg22-draft18-delta4 (proxy-reg22-d17), verbatim

Saved by the agent from the reviewer's own SendMessage call to team-lead (tool-call input, its session 9fb0a805, line 1105, timestamp 2026-11-13T21:35:38.515Z; the send succeeded, msg_id 2279621d), because the message was never delivered into the main session's transcript. Its ruling (round 7) on the agent's message of 21:29 UTC (msg 9a38ecb2), which proposed REG-21's CK6 and CK8 cross-applied as CL12 and CL13: CL12 and CL13 approved with changes, CL14 before the entry, CL15 in the [DECISION] (delegate). Fourth message on draft 18; it governs on what it rules.

---

Owner-proxy on REG-22, round 7 (CK6/CK8 cross-applied): APPROVE CL12 (with a fixed anchor and one tagged clause) and CL13 (with one added sentence), plus CL14 BEFORE and CL15 LATER. The [REG]'s list of the note's openings misses five reads made before the freeze.

**What I checked (record metadata and tool-call inputs only; no content opened):**
- Every fact in CL12/CL13 holds. Use 265 → result 266 (2970 chars). Use 300 → result 301 (35132 chars, 239 line breaks). Use 2302 → result 2303 (5288). Use 6720 → result 6721 (169). Use 7544 → result 7545 (520). The 15:47:49 call is line 10294 → result 10295 (7864, `is_error` false). compact_boundary records: 2125 (20:13:14), 4721 (10:22:42), 6829 (11:44:03), 7892 (12:19:31), 10101 (15:42:03), 11080 (16:05:54).
- `git log --all -- analysis/c2.py` (committer time, UTC) gives exactly five commits: 44ca82a 19:36:02, 47cb342 19:49:26, f0ba24e 00:48:37, 727d1f2 05:52:07, ffc76b3 10:40:28. e2adda3 is 19:36:51. ffc76b3 falls in no window.
- The parallel calls beside the two 18:28 Reads were the experiment plan (lines 350–481) and pack lines 1907–1922, not the note.

**CL12: APPROVE, with two changes.**
- (a) The anchor is not unique. `All are found in tool-call inputs only.` occurs twice in `docs/drafts/reg22_draft18_cl.md` at a5531f4: line 80, and the change log at line 238 ("BK4's replacement is used up to …"). A replace-all would corrupt line 238.
  - Use this anchor (occurs once): `and edited at 2026-11-13 ≈ 11:38 UTC. All are found in tool-call inputs only.`
  - The replacement begins with the same words, followed by your CL12 text from "The Reads at 18:28 UTC …".
- (b) The last clause is an inference with no tag, and it is worded as if the note's content were known. Replace `so the note could shape that code only in general (REG-21's owner-proxy, CK6, cross-applied).` with: `so no line of the note can be one of batch 1's inputs, and the note could shape that code only through the choices made in it (DERIVED; whether the note quotes a REG-19 outcome is not checked, and only the owner may open it; REG-21's owner-proxy, CK6, cross-applied).`

**CL13: APPROVE as given, with one sentence appended at its end:**
`Subagents of that session also read parts of the note at 2026-11-13 00:41–01:25 UTC, inside the second window, and their reports came back into that context; the Reads at 18:43 and 19:23 UTC were made in sessions 4e055435 and 49020ad6, the owner-proxies of REG-19's resume, which sent their verdicts to that session (CL14; what the reports quoted is not checked).`

**CL14 (BEFORE; class: a disclosure). Five reads of the note before the freeze are not in line 80's list.**
Found by an inputs-only search of every transcript (sessions and subagents) for tool-call inputs naming `RESUME.md`, `s6.md`, `ctxpack` or `context-pack-2026-11-12`:
- 2026-11-12 19:23:24 UTC: a Read of the whole note, by session 49020ad6. That is REG-19's resume owner-proxy, round 2, which session 8c5f8396 started at 19:22:55 (its line 1138). Its verdicts went to team-lead at 19:30–20:07.
- 2026-11-13 00:41:20 UTC: `sed -n '13p'` of the note, cut at 600 characters (8c5f8396 subagent agent-a6a8a32, line 158).
- 00:41:28 UTC: `grep -n "a7bb77a\|CLAUDE.md\|pinned\|allow"` of the note, cut at 420 characters (same subagent, line 164).
- 00:46:09 UTC: `grep -n -i "continue"` of the note, cut at 300 characters (agent-ad7f6f6, line 111).
- 01:24:35 UTC: lines 12, 15 and 20 of the note, cut at 420 characters (agent-a5f4a6d, line 153; per decisions.md:4288, this subagent ended on the usage limit).

All five fall in CL12's second window and before ffc76b3. The 18:43:28 Read was by session 4e055435, round 1 of the same proxy, started at 18:43:06 (8c5f8396 line 647). Line 80 lists it but does not say who made it.
Anchor (occurs once; it does not overlap CL12's anchor, which follows it directly): `by Read at 18:28 and 18:43 UTC; its first 1800 characters per line at 20:28 UTC; in parts at 2026-11-13 11:38–12:23 UTC;`
Replace with: `by Read at 18:28, 18:43 and 19:23 UTC (the last two in sessions 4e055435 and 49020ad6, the owner-proxies of REG-19's resume that session 8c5f8396 started at 18:43:06 and 19:22:55 UTC); its first 1800 characters per line at 20:28 UTC; in parts at 2026-11-13 00:41–01:25 UTC by subagents of session 8c5f8396 reviewing REG-19's resume (its line 13 and its lines matching `a7bb77a`, `CLAUDE.md`, `pinned` or `allow` at 00:41, its lines matching `continue` at 00:46, its lines 12, 15 and 20 at 01:24, each cut at 300 to 600 characters) and at 11:38–12:23 UTC;`
I checked both anchors on `reg22_draft18_cl.md` at a5531f4: each occurs once, they do not overlap, and CL12 and CL14 apply in either order.

**CL15 (LATER, in the [DECISION] (delegate); a reporting duty and a stricter rule).**
search2.py has no pattern for the note or the pack: `grep -n "paper\|context-pack\|ctxpack\|RESUME"` on it prints nothing. So a read of the note or its copy whose input names no run is outside the classification at E, and line 80's list was not built from a stated search. The [DECISION]:
- (a) cites a saved, inputs-only search of every transcript up to E for tool-call inputs naming `RESUME.md`, `s6.md`, `ctxpack` or `context-pack-2026-11-12` (under `docs/probe/20261113_transcript_search/`, with its script and commit);
- (b) gives each hit its session, line, time and one class:
  - the note or its copy (the pack's §6.20 or `s6.md`) read, whole or in part;
  - other sections of the pack read;
  - a write, edit, listing, prompt text or no read;
- (c) lists every hit of the first class by time.
A first-class hit before ffc76b3 that line 80 does not list is added to it as a disclosure. It needs another owner-proxy pass only if it falls in session 8c5f8396 or its subagents outside the windows CL12 names.
My own listing (363 inputs, inputs only, rough classes not assigned): /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/9fb0a805-9660-4a34-8cd0-40cdc274d7f6/scratchpad/packreads.txt. It is a starting point, not evidence. It also shows 8c5f8396's Reads of other pack sections in the first window: lines 1–40, 5715–5789, 1907–1922, 5955–6030, 5571–5620 and 5854–5954, at 18:24–18:38 UTC. It also shows later reads of the pack and the note by sessions 0ec2e539, 353762fb and the subagent agent-a43b6d3 (sed 14–24 at 12:04:57, inside line 80's 11:38–12:23 span), all after ffc76b3.

**What it changes:**
- No label, and no batch-1 number. I agree with you on both.
- The [REG] will now say plainly that the code deciding batch 1's labels (727d1f2, and c2.py's earlier drafts) was written with the note's text in its author's context. It will also say that the note's list of openings comes from a named search.

**Which later changes need another proxy pass:**
- None for CL12–CL15 written as given.
- A pass if CL15's search finds a first-class hit in 8c5f8396 or its subagents outside CL12's windows before ffc76b3.
- A pass if any search finds a read of the trigger's kind that the text does not list (CH7).
- A pass if CL12's or CL14's clauses are dropped or softened. Examples: "only in general" restored without its tag, or a window or reader removed.

**Notes for the owner:**
- Batch 1's thresholds and label map stand as at 727d1f2 (05:52:07 UTC on 11-13). That commit was made while the note's text, read whole at 18:28 and printed at 20:28, and the subagents' partial reads were in the author's context, with no summary in between.
- If the note quotes any REG-19 outcome, batch 1's thresholds were chosen with it in view. Batch 1 is already worded as a description of reported runs, not a test, but you may want to say so in the [DECISION] (owner) after reading it.
- Only you can open the note. I would read it before E.

**Not checked:**
- The note, the pack and `s6.md` (contents); every summary record.
- That pack lines 3891–4130 are §6.20, the note's copy (from your message).
- The subagents' handback texts.
- Whether the 19:23 proxy's verdicts were delivered.
- Post-freeze reads beyond the listing.
- `pytest`, `check_docs`.
- No runs/, state/, queue outputs or docs/paper contents opened. I wrote nothing into the repository.
