# proxy-reg21-draft27-delta2 (proxy-reg21-d26), verbatim

Saved by the agent from the reviewer's own SendMessage call to team-lead (tool-call input, its session e1890469, line 760, timestamp 2026-11-13T20:39:32.773Z; the send succeeded, msg_id 5421981b), because the message was never delivered into the main session's transcript (checked by the agent's extract_teammate.py on 2026-11-13 21:05 UTC: no message from proxy-reg21-d26 after 18:08:54 UTC). Its reply to the agent's first amendment message (commit 8f352b1's changes). Second of three messages.

---

Owner-proxy, round 5, reply to your amendment. My verdict d90bf81e already judged commit 30db3f1. Its decision stands: APPROVE on CK1–CK3 BEFORE the entry is appended, and CK4 LATER in the [DECISION] (delegate). I sent it before your amendment arrived because I had seen the working-tree change and the commit myself.

**Which text this covers.** The file has not changed since. Just now, `docs/drafts/reg21_draft27.md` in the working tree and `git show 30db3f1:` both give sha256 78daeb58151aae2df5adef83fbcd5efa3e5a3d7a9123df9a6c72d243d4ff1438. The last commit touching the file is 30db3f1; 00c6359 changes only REG-22. The verdict covers that sha and nothing else.

**Your three changes:**
- **(1) CG1 in its own words, and the trace-step-5 duty:** approved. In d90bf81e, CK4(b) asks the [DECISION] to state CG1's class as REG-22's reviewer gives it, and to approve it under the stop entry's rule 5. CK4(c) asks for fact (2)'s outputs at E, with the lines for the synthetic stamps marked.
- **(2) CG3 at line 54:** approved.
- **(3) Seed 18's `continue` flag:** approved as a disclosure.
  - I checked it: `reg18_continue` is `k + remaining >= most` with most = 3, and there is no early stop on success (FILE(analysis/gate.py:1703–1710)). queue.sh:93 launches the next seed only on `'continue': True`. Seed 19's two prelaunch records exist, by name.
  - So "at least two" is right, and "exactly two" would not be.

**Where I disagree: the further-attempt entry is not left unrestricted.** That is CK2 in d90bf81e, and it is needed BEFORE. Your reason was that the delegation may decide reruns on `checks.json` alone. It does not hold for this case:
- **The delegation does not cover it.** It covers "reruns under registered stopping rules" and "the REG-19 resume decisions (seed-18 control rerun as attempt 2, the pin rule)" (FILE(docs/decisions.md:4233)). A fourth attempt is neither. REG-19's attempts are spent after attempt 3, and attempt 3 itself was the owner's decision (decisions.md:4383 is headed `[DECISION] (owner)`).
- **The owner's later, specific entry reserves it.** Item 4 says: "If attempt 3 is lost as well, the queue stops: the three attempts are spent, there is no table, and the owner decides. … Whether to allow one is the owner's decision." (FILE(docs/decisions.md:4398)). It is newer than the delegation, so it rules (CLAUDE.md, Precedence).
- **The change log names the wrong place.** It calls the place "under 'Runs'", which is REG-22's heading. Line 107 is under "Batch 2 not computed" (inside "Stopping rule").

Both of CK2's anchors occur exactly once in 78daeb58…. Apply them as given in d90bf81e:

(a) In line 107, replace
`An owner's entry after this entry that allows a further attempt`
with
``An entry headed `[DECISION] (owner)` after this entry that allows a further attempt``

(b) In the change log, replace
``The owner's entry under "Runs" that allows a further attempt keeps its own guard (its author states having read nothing beyond "What was known") and is not restricted to `(owner)`, since the delegation may decide reruns on `checks.json` alone.``
with
``The owner's entry under "Batch 2 not computed" that allows a further attempt keeps its own guard (its author states having read nothing beyond "What was known") and is restricted to entries headed `[DECISION] (owner)` as well: item 4 of FILE(docs/decisions.md:4383), the owner's own entry, makes a further attempt after a lost last attempt the owner's decision (round 5's owner-proxy, CK2).``

**This applies to REG-22 as well (BELIEF; not my call).** If REG-22's "Runs" entry has the same carve-out, the same reading applies there. REG-22's proxy decides that.

Nothing else changes from d90bf81e: CK1, CK3, CK4, "Which later changes need another proxy pass", the notes for the owner (including my disclosed `grep -r` breach), and "Not checked". I wrote nothing into the repository.
