# proxy-reg21-draft27-delta3 (proxy-reg21-d26), verbatim

Saved by the agent from the reviewer's own SendMessage call to team-lead (tool-call input, its session e1890469, line 878, timestamp 2026-11-13T20:47:25.809Z; the send succeeded, msg_id fe11bb7a), because the message was never delivered into the main session's transcript (checked by the agent's extract_teammate.py on 2026-11-13 21:05 UTC: no message from proxy-reg21-d26 after 18:08:54 UTC). Its reply to the agent's second amendment message: REG-21 draft 27 as of 285584f. Third of three messages; it governs.

---

Owner-proxy, round 5, second amendment: REG-21 draft 27 as of 285584f. APPROVE, on CK1, CK2, CK3 and a new CK5 BEFORE the entry is appended, and CK4 (now with (g)) LATER in the [DECISION] (delegate). This replaces my two earlier messages (d90bf81e and 5421981b) as to which text is approved and which items apply. Their reasons, notes and "Not checked" still stand.

**Which text this covers.** `docs/drafts/reg21_draft27.md` at 285584f, sha256 0911dfa75eaa6d0d8edc5afd60d0aeee563e817a1ed6f09fc6eea00ac5deb0d5. The working tree is the same file. 8f352b1 made the draft change; 285584f is the [CORR] and the context pack. Against 30db3f1, two lines change:
- line 54: the 18:07 parenthetical and the CG5 sentence;
- one new change-log bullet.

The quoted rule F review is untouched. Any other change needs another pass.

# What I checked (tool-call inputs only; no output opened)

| Read | What the inputs show |
|---|---|
| **18:07:10.911Z**, subagent agent-a625ca98c29ea904b of fdf13821, line 316 | It wrote the section-6 template with `#### 6.20.2 What is done, what remains, what is needed (RESUME.md, verbatim)` and the directive `@@F docs/probe/20261111_reg19/ops/RESUME.md 1-34`. In the same command it ran `python3 _gen6.py _s6_tmpl.md s6.md`, which expands that directive into the section, and printed only `grep -c 'FILE' s6.md`. So "copied it whole into a pack section" at 18:07:10 is right. At 18:07:30.706Z (line 324) it rebuilt s6.md the same way. |
| **18:07:38.644Z**, line 328 | `grep -n 'w3000_s1[5-9]' s6.md \| grep -iE 'hit\|verdict\|stuck\|pass_clear' \| grep -v '^.*Registration' \| cut -c1-200 \| head`. The draft's wording is broader than the command (it omits the exclusion of "Registration", the cap of 10 lines and the 200 characters). That is safe. |
| **15:32:08.571Z**, 8c5f8396, line 9857 | It matches CG5's sentence exactly: up to 12 lines, 400 characters each, lines holding `checks.json` or `outcome withheld` left out. |
| **The [CORR]** | 58 + 6 + 6 + 5 + 2 + 1 + 1 = 79. I did not count labels.tsv (see "Not checked"). |

**Both additions are approved.** Their class is disclosure, and they only add. Batch 2 is labelled retrospective by design already, so neither changes a label, a threshold or a rule.

# One gap: the note's copy in the pack was read again (CK5)

- **Where the copy is.** The section the subagent built is §6.20.2 of `docs/paper/context-pack-2026-11-12.md`. Its heading is at line 4060 and the next section's (§6.21) at line 4129, by `grep -n` of the pack's headings. The pack's file time is 2026-11-12 00:16 +0600, which is 18:16 UTC on 2026-11-12, before every read below.
- **The agent's own session read it.**
  - A Read of the pack at **2026-11-12 18:28:37.661Z** (offset 3891, limit 240, so lines 3891–4130). That is §6.20.2 whole, 19 s after the session's Read of the note itself. agent/INGEST.md:14 lists §6.20 as read "in full".
  - On 2026-11-13 the main session ran two greps of the pack that can print lines of that copy: CG5's at 15:32:08, and `grep -n "onset" docs/paper/context-pack-2026-11-12.md | cut -c1-300 | head -30` at **15:47:49.845Z**.
- **What this changes.** The draft lists the note's openings by its path only, so these reads of its verbatim copy are not listed. They add nothing to what the agent knew: the 18:28:18 whole Read came first. But the list is meant to be complete, so they belong in it.
- **"The agent does not open the note again"** should cover the copy too. That is a stricter rule.

# Conditions

**CK1, CK2 and CK3 (BEFORE): unchanged from d90bf81e and 5421981b.** Their anchors are still unique in 0911dfa7…:
- CK1's anchor `(rule F round 19, CE1). Apart from read (x)` occurs once.
- CK2(a)'s and CK2(b)'s anchors occur once each.
- CK3's anchor occurs twice, once in the text and once in the quoted review. Replace only the occurrence in line 54, as CK3 says.

**CK5 (BEFORE; a disclosure and a stricter rule; line 54, after CG5's sentence).** Replace:
`the owner can state whether those lines quote a line a REG-19 burst run wrote after its burst began, which would be a read under the trigger.`

with:
`the owner can state whether those lines quote a line a REG-19 burst run wrote after its burst began, which would be a read under the trigger. The note's copy made at 18:07:10 UTC (and made again at 18:07:30 UTC) is §6.20.2 of `docs/paper/context-pack-2026-11-12.md`, "What is done, what remains, what is needed (RESUME.md, verbatim)", lines 4060 to 4128 (DERIVED: `grep -n` of the pack's headings; the file's time, 2026-11-12 18:16 UTC, precedes the reads below), so a read of that section is a read of the note: the agent's session read lines 3891 to 4130 of the pack by Read at 2026-11-12 18:28:37 UTC, 19 s after its Read of the note, and its ingest record lists §6.20 as read in full (FILE(agent/INGEST.md:14)); the print above and a grep of the pack for "onset" at 2026-11-13 15:47:49 UTC may have printed lines of that copy (DERIVED from the tool-call inputs; what they printed is not stated). The agent does not read §6.20.2 of the pack either (round 5's owner-proxy, CK5).`

That anchor occurs once. CK5 adds a change-log entry: "CK5 (round 5's owner-proxy): the note's copy in the pack, and the reads of it, added to the note's openings."

**CK4 (LATER: the [DECISION] (delegate)):** (a) to (f) as in d90bf81e, with (e) now naming 285584f's text and sha 0911dfa7… (the appended entry differs from it only by CK1, CK2, CK3 and CK5). Add:
- **(g)** The [DECISION] lists the commands behind the two reads added in 8f352b1 and CK5, with times and transcript lines: fdf13821's subagent a625ca98, lines 316, 324 and 328; 8c5f8396, lines 300, 9857 and 10294. It also cites the [CORR] of 285584f.

# Which later changes need another proxy pass

- As in d90bf81e.
- CK5 written other than as given.
- Any edit after 285584f other than CK1, CK2, CK3 and CK5.

# Notes for the owner

- My earlier notes stand.
- **Add:** the context pack of 2026-11-12 holds RESUME.md's lines 1–34 verbatim (§6.20.2). Checking the note or the pack is one check. Anyone who stated having seen "the context pack of 2026-11-12" has seen the note.
- **REG-22 (BELIEF; its own proxy decides).** If REG-22 draft 18 carries the same 18:07 parenthetical, the same CK5 sentence fits it.

# My own reads this round (rule A6)

- **Inputs only.** I read tool-call inputs only, from fdf13821's subagent a625ca98 and from 8c5f8396.
- **Small quotes from the note.** To locate the include directive, I printed 120-character windows around "RESUME" in the subagent's template input. The windows showed the subagent's table rows citing the note's lines 4, 9–11 and 28, with two short quotes:
  - line 4's "manifest updated (not yet committed)";
  - line 28's pin rule as "(proposed)".

  Seed 18's burst run and seed 19 were "not run" as of 2026-11-12. None of this is a REG-19 run-time line or outcome.
- **The pack.** I printed its heading lines and one count: 49 lines carry a `RESUME.md:<n>` tag. I opened none of its content, and not the subagent's handback (line 343).

# Not checked

- labels.tsv's counts.
- classify2_handlabels_20261113T204215Z.txt, a probe output.
- What the 18:07:38, 15:32:08 and 15:47:49 commands printed.
- REG-22 draft 18.
- Everything listed as "Not checked" in d90bf81e.

I wrote nothing into the repository.
