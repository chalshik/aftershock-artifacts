Saved by the agent from the reviewer's own SendMessage call to team-lead (tool-call input, its session 9fb0a805, line 1224, timestamp 2026-11-13T21:58:09.025Z), because the message was never delivered into the main session's transcript. Its ruling (round 8) on the agent's message of 21:53 UTC (msg 33c97ce2): the CL15 disclosures and both factual updates of fca9a09 approved; CL16 before the entry, CL17 in the [DECISION] (delegate). Fifth message on draft 18; it governs on what it rules.

---

Owner-proxy on REG-22, round 8 (fca9a09): APPROVE the CL15 disclosures and both factual updates. One condition before the entry (CL16, on the `continue` sentence) and one for the E rerun (CL17).

**What I checked (tool-call inputs, record metadata, code; no output opened):**
- **Diff a5531f4→fca9a09 of `reg22_draft18_cl.md`:** only the CL14 text, the nine-read sentence, CL12's text, the two factual updates and the change log. Every other word is unchanged.
- **Code:** nothing frozen changed. Since ffc76b3 only `analysis/e1.py`, `analysis/k5.py` and `tests/test_k5.py` changed, and none is in REG-22's list; gate.py is unchanged since ffc76b3.
- **Table file:** no commit adds a file named `reg19_final_` + stamp outside the review bundles.
- **Count:** `noteread`'s first-class section has 24 hits before ffc76b3. 15 are in line 80 after CL12/CL14; the 9 added are exactly the rest.
- **The nine against their inputs:** I read the inputs of fdf13821:4152 and :4156, 8c5f8396:112, :800 and :2624, ad7b5ab:286, and a625ca9:324, :332 and :336. Each label in `noteread_labels.tsv` matches its command: the patterns, cuts, `head` limits, the `assemble.py` run before :4152, and the `-o` with `sort -u` at :112. I did not check :340 and :6730 (class 3) beyond their labels.
- **Order in line 80:** the nine-read sentence comes before CL12's text, and the 15:32:08 sentence comes after both, so each "below" is right. 18:24:32 is 3 m 46 s before 18:28:18, and the first c2.py commit is 19:36:02, so no window conclusion changes.
- **Gaps in the patterns (pre-freeze, inputs only):**
  - Inputs that reach the note or pack without naming them: directory or glob reads of `docs/paper` or `docs/probe/20261111_reg19[/ops]`, and `git show`/`log -p`/`diff` of the two commits that hold the note, 54a995d and da1f836. This found 49 inputs, and none reads the note or the pack. They are listings, other paper files (PDFs, paper-plan, related-work, quote-check) and the ops scripts.
  - Recursive greps (`grep -r`, `rg`, `git grep`, the Grep tool) over `docs`, `.` or those folders: 8 inputs. Six are in sessions 4e055435 and 49020ad6, the REG-19-resume proxies, which had already Read the note whole. The 19:25 and 19:28 git greps come after 49020ad6's 19:23:24 Read; the three 4e055435 ones after its 18:43:28 Read. Two are `-l`/`-rln`, file names only (49020ad6 at 20:06:27, and 8c5f8396's subagent at 01:25:05).
  - So I found no further pre-freeze read of the note or its copy. My listings: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/9fb0a805-9660-4a34-8cd0-40cdc274d7f6/scratchpad/rgrep.txt (the second check). The first check printed to the console only.

**Ruling on 3(a), my CL15 condition.** 8c5f8396:112 falls outside CL12's windows, which triggers my pass. It prints only path strings and their line numbers (`grep -n -o … | sort -u | head -40`). It enters context 4 minutes before the 18:28:18 Read and stays until the same summary, before any c2.py commit. The text says exactly that. Approved as written.

**Ruling on 3(b), CH7.** fdf13821:4152 at 18:12:45 is a possible read of the trigger's kind, in the pack-builder's session: lines naming `w3000_s1[5-7]` that hold none of withheld/config/valid/yaml, first 20, cut at 220. Treating it like the 15:32:08 print is right: disclosed, with the owner's statement invited. It changes no label, since batch 2 is retrospective by design. It is not in the c2 author's session, so CL12's windows are unaffected. With it listed and reviewed here, CH7's loop is closed for it.

**On 4(i): one condition.**
gate.py:2041 is `return {"done": done, "continue": bool(remaining and reg18_continue(rows, remaining))}`, with `remaining = len(order) - len(done)`. `done` holds the seeds whose pair is valid, up to the first gap. "With no seed left" is not the code's condition, and "QUEUE DONE (all five seeds run)" does not establish it: a run can end and still not count as a valid pair.
- If `done` held fewer than five seeds, `remaining` > 0 and `False` would carry the futility rule's reading (FILE(analysis/gate.py:1703)). With k ≥ 2 already known, that reading would be `surge_reading_wrong` or `controls_not_healthy`, not "nothing".
- The sentence is true only if the step's printed `done` lists seeds 15 to 19. I cannot open the queue output, so the agent must check it.

**CL16 (BEFORE; class: wording that states its basis).** Only if the printed `done` in PROBE(docs/probe/20261113_reg19/queue_agent_20261113T214838Z.txt) lists 15, 16, 17, 18 and 19:
Anchor (occurs once, line 79): `with no seed left the flag is False whatever the runs show (DERIVED: `remaining` is 0 in `reg19_step`, FILE(analysis/gate.py:2041)), so it adds nothing to what was known.`
Replace with: `the step's `done` listed seeds 15 to 19 (the same PROBE; `done` is the seeds whose pair is valid), so `remaining` is 0 and the flag is False whatever the runs show (DERIVED from FILE(analysis/gate.py:2041)), so it adds nothing to what was known.`
If `done` lists fewer seeds, do not register this sentence: the flag then carries information, and the text needs another owner-proxy pass.

**On 4(ii): approved as written.** I cannot check the COPIED line or the 21:46 time, because queue outputs are outside my limits. Note that the PROBE cited is the first queue file (180030Z), not the 214838Z one. That is correct if the first queue copied seed 19's burst run before stopping before seed 19's step, as your message describes.

**CL17 (LATER: the E rerun of `noteread.py`; a stricter rule).** The rerun at E adds these as hits, each classified by hand where it can print the note's or the copy's lines:
- recursive or folder-level reads whose path covers the note or the pack without naming them: `grep -r`/`-R`, `rg`, `git grep`, the Grep tool, and `cat`/`head`/`sed` on a glob, over `.`, `docs`, `docs/probe`, `docs/probe/20261111_reg19[/ops]` or `docs/paper`;
- `git show`, `git log -p`/`--patch` or `git diff` that covers 54a995d or da1f836, the commits that hold the note.
The [DECISION] states the rule change and how many hits it added before and after ffc76b3. A new pre-freeze first-class hit in 8c5f8396 or its subagents outside CL12's windows needs another pass. My inputs-only check above found none.

**Which later changes need another proxy pass:**
- CL16's condition fails (`done` lists fewer than five seeds).
- CL17 finds a pre-freeze first-class hit in 8c5f8396 or its subagents outside CL12's windows.
- Any search finds an unlisted read of the trigger's kind (CH7).
- Any of the nine-read sentence's clauses is dropped or softened: "may include", "not known", or the owner's statement.
- None for CL16 and CL17 written as given.

**Notes for the owner:**
- Two prints, the builder's at 18:12:45 on 11-12 and the c2 author's at 15:32:08 on 11-13, may have shown note lines that name seeds 15–17's runs. Both are disclosed, and both ask for your statement on what such a line quotes. Neither changes a label.
- Batch 1's code was written with the whole note in its author's context (CL12). Whether the note quotes any REG-19 outcome is still the one open fact, and only you can check it. I would check it before E.
- REG-19's queue is done (by the text). `final.sh` must still wait until both entries are committed. No table file is in git.

**Not checked:**
- The queue outputs (the printed `done`, the COPIED line, 21:46).
- The pack, the note and `s6.md` (contents).
- That pack lines 3891–4128 are §6.20, and that the pack's numbering at 18:24–18:50 on 11-12 equals today's.
- The class-2/3 labels beyond :340 and :6730.
- `noteread.py`'s shlex/`cd`/`$VAR` logic line by line (read for structure only).
- Post-freeze hits beyond the first-class list.
- `pytest`, `check_docs`.
- No runs/, state/, RESUME.md or docs/paper contents opened. I wrote nothing into the repository.
