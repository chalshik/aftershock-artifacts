# REG-21 draft 26: where each round-3 item went

Built from `docs/drafts/reg21_draft25.md` by `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/fa346d1a-a9c4-4607-bad4-9b34c206c996/scratchpad/make_reg21_draft26.py`. The script uses anchored replacements, each asserted to occur the stated number of times. It takes the reviewers' texts from their saved files by line number; nothing is retyped. Line numbers below are draft 26's. No line is inserted before the change log, so lines 1–260 match draft 25's numbering. The lines that changed are 1, 3, 4, 49, 54, 71, 104, 111, 112, 113 and 127, and the change log is lines 262–282.

Sources:
- r18: `docs/drafts/reviews-2026-11-13/rulef-reg21-draft25-r18.md`.
- add.: its addendum.
- P1, P2 and P3: the owner-proxy's three messages. P3 governs.
- K11: `rulef-reg22-draft16-r11.md`.

| Item | Where applied in draft 26 | How | Why / note |
|---|---|---|---|
| BI1 (r18; add. changes) | Line 54: (ix) "(other than (x))"; item (x) at BJ8's anchor; BI1's further facts after BJ8's text; search sentence "is known to the agent from a search" + "(x) shows that…" after BJ11(b)'s clause. Line 111: "ten listed there, (i) to (x)" (= BJ14(e)). Label edits: lines 1, 4, 54, 104, 127, 71 (via BJ14). | merged | Rule 2: BJ8's (x) is used verbatim. BI1's further facts are added as separate, attributed sentences: counts from the `no_errors` detail (checks.py:69), before the seal, into a scratch file; how the agent's pass showed the hit; `vm_state.py`'s rule; BI1's ±0.02 req/s and ±0.01 on r's first factor, next to BJ8's "rough r" (both attributed, with BI1's BELIEF on a steady state); what `unfinished` says. The addendum's added [CORR] citation is carried by BJ8's heading. BI1's "facts reported in the batch-2 [RESULT]" is not added beside BJ14(c), because line 104 already requires it. BI1's "'The two batches' rules" are not edited: line 73 already makes a retrospective batch 2 never govern, and P3 §4 sends any change there to another proxy pass. |
| BI2 (r18; add. changes the first list) | Line 54 (the limits of `search2.py`); line 111 ("For each hit it prints the command…", and the classification duty after "(rule F round 17, BE-O1, BE-O3).") | verbatim, form departed | The addendum drops the `stubbed` line and adds "it misses a path into `runs/` that is built from a variable, an f-string or a shell command run from python". The bullet lists are written inline with semicolons, because the draft's lines are paragraphs. No words changed. |
| BI3 | — (cited) | met | Met by decisions.md 2026-11-13 [CORR], FILE(docs/decisions.md:4453) (per the addendum). BJ8's (x) and line 3 cite it. No text added. |
| BI4 | Line 49, after BJ3's text | merged | BJ3 and BI4 describe the same 14:09:43 UTC command, so BJ3's verbatim text is used and BI4's sentence on it is not repeated. **They disagree on one field:** BJ3 says "the request count in the end window", BI4 says "mean running batch". The code agrees with BI4: `n` is the mean of `vllm:num_requests_running` (FILE(analysis/load.py:183); the same code at `1cface7`, its line 179). Draft 26 states this in a separate sentence attributed to BI4, and BJ3's text is left verbatim. BI4's 18:02:32 UTC `load.verdict` sentence is verbatim. |
| BI4b (add.) | Line 49, after BI4's sentence | verbatim | — |
| BI5 | Line 54: trigger "other than `checks.json`'s `valid` and `failed`"; (ix) addition (pytest, check_docs, the 19:52:14 UTC listing) | verbatim | Changes the trigger's wording. P3 §4 lists "any change to the trigger" as needing another proxy pass; draft 26 gets one in any case (the stop entry). Line 111's last sentence restates the trigger in brief and is **not** changed (P3 §4). The added "(ix) … at 19:52:14 UTC" carries no date in BI5's text, and the date is 2026-11-12 (BI5's trace); left verbatim. |
| BI6 (add.) | Line 111, after BI2's added sentence | verbatim | The draft states the rule; the code is changed apart from this draft. |
| BI7 (add.) | Line 54, after (x) and BI1's further facts | verbatim | "The [DECISION] (delegate) repeats this" is for the [DECISION]. |
| BI8 (add.) | Line 4, at the end of the "What this is" bullet, after the sentence BJ14(a) keeps | verbatim, placement departed | "Beside the title" is read as the first bullet. A new line was not inserted because it would shift every later line, and the text cites its own lines (for example "line 51" in line 54). The stop entry is cited after it (rule 5). |
| BI-O1 | Line 104, at the end (the batch-2 [RESULT] shows root-level `*.py`/`*.pth` diff and status) | verbatim commands | Reporting duty, with r18's two commands. |
| BI-O2 | — | not taken | It concerns the bundle note (team lead's instruction). |
| BI-O3 | Line 54, after BI7 | written by the agent | Reporting duty as the team lead framed it: the agent did not check whether the 2026-11-12 context pack or the subagent's report carries seed 17's counts; the owner can, and the batch-2 [RESULT] states the result or that it was not checked. |
| BI-O4 | Line 54, after "Commands run by hand … a limit (…)." | written by the agent | "Both searches cover only the Mac's transcript folder for this project." Tagged BELIEF on a listing of folder names under `~/.claude/projects` (one folder for this project, checked 2026-11-13, saved in no file). |
| BI-O5 | Line 113, after "It quotes each load group's median…" | written by the agent | A reporting duty in the batch-1 [RESULT]: r per run beside (c ÷ 1.681) × (mean served prompt ÷ 3072), with published c. The reviewer's "< 0.01" reading was not added, so no new threshold is introduced. |
| BI-S1, BI-S2 | Lines 3 and 4 (citations) | cited | Applied by the stop entry, FILE(docs/decisions.md:4541), items 2–3. The draft cites it where it names the review-stop rule. |
| BJ1 (P1, amended in P2/P3) | Line 111 | verbatim | "(i)–(ix)" → "(i)–(x)" inside BJ1's text, as amended. "(vi) to (ix) were found" stays as history. |
| BJ2 (P1) | Line 3: replacement and end-of-line addition | verbatim | BJ14(h) and the agent's draft-26 sentences come before BJ2's "Draft 25. …". The round-3 file citations come after BJ2's end text. |
| BJ3 (P1) | Line 49 (end); line 111 ("the known such hits are…") | verbatim | See BI4 for the field on which BJ3 and the code disagree. |
| BJ4 (P1) | (a) line 104, fact (1); (b) line 112; (c) → [DECISION] | verbatim | (c) is not draft text. |
| BJ5 (P1) | Line 104 | verbatim | — |
| BJ6 (P1) | → [DECISION] (delegate) | not in draft | — |
| BJ7 (P1) | Line 104 | verbatim | — |
| BJ8 (P3, replaced) | Line 54, after "its committed run is the one at the append (…)." | verbatim | P2's BJ8 is withdrawn. |
| BJ9 (P2) | Line 54, after (iii)'s [CORR] sentence | verbatim | Stands under P3. |
| BJ10 (P2) | Line 54, (viii) | verbatim | Stands under P3. |
| BJ11 (P2) | (a) line 54, the bound; (b) line 54, the search sentence | verbatim | Stands under P3. BI1's "(x) shows…" follows (b)'s clause. |
| BJ12 (P2) | — | withdrawn by P3 | — |
| BJ13 (P3, replaced) | → [DECISION] (delegate) | not in draft | — |
| BJ14 (P3) | (a) line 4; (b) line 54; (c) line 54; (d) line 104 (two); (e) line 111 only; (f) line 1; (g) line 127; (h) line 3; (i) line 71 | verbatim; (i) label words | (e): the anchor occurs twice in draft 25 (lines 111 and 253). Only line 111 is replaced and line 253 stays as history, as BJ14(e) says. (i): line 71 "the one item not yet read" → "the one item that would have been unread"; no other sentence called batch 2 primary or a reading on unread runs (grep below). |
| BK4 (K11, for REG-21's line 54) | Line 54, (i): replaces "(BELIEF: the note that records it, RESUME.md, was not opened)" | departed | The team lead's change is applied. BK4's text is kept up to "lists these calls". Its last two sentences, which would have the [DECISION] say what the note quotes, become: "; what the note quotes of REG-19 runs' run-time lines is not stated: the agent may not open the note under its delegation; the owner can. If it quotes a line a REG-19 burst run wrote after its burst began, that is a read under the trigger, and batch 2 is labelled retrospective by design in any case.)" |

## Checks

**Anchors.** There are 36 replacements, and each anchor occurred exactly once in the text, with one exception. BJ14(e)'s anchor occurs twice, as BJ14(e) says, and was replaced on line 111 only. The script's per-anchor log is in `make_reg21_draft26_anchors.txt`, next to the script.

**Verbatim.** Each of the 36 reviewer texts taken word for word (BJ1–BJ5, BJ7–BJ11, BJ14(a)–(h), and BI1's, BI2's, BI4's, BI4b's, BI5's, BI6's, BI7's and BI8's sentences) occurs once in draft 26. The list is in `make_reg21_draft26_verbatim.txt`, next to the script.

**Diff from draft 25.**
- `git diff --no-index --stat`: 1 file changed, 33 insertions(+), 11 deletions(−).
- Lines changed: 1, 3, 4, 49, 54, 71, 104, 111, 112, 113 and 127, plus lines 261–282 appended (282 lines, against 260).
- About 0.7 k characters removed and 24.5 k added (word diff).

**Grep for "primary" and "unread" in the body (lines 1–123).** No sentence calls batch 2 primary or a reading on unread data:
- L4: BI8's definition of "primary".
- L9: the owner's "mix primary", unrelated.
- L54 and L104: "restores primary standing", "would have been primary only if".
- L4, L54 and L71: "no item is judged on unread data", "would have been … unread".
- L75: "no reading on unread runs".

The other hits (L127, L198, L231, L239, L265) are in the change log. The output is saved as `grep_primary_unread.txt` next to the script.

**FILE tags.** Every FILE tag new in draft 26 was checked against `git show HEAD:<path>` at 8271d71:
- the cited line holds the cited content for checks.py:69 and :237, load.py:183, check_docs.py:41 and :196, test_check_docs.py:57, and decisions.md:4406, :4437, :4453 and :4541;
- `vm_state.py:3` is where the `no_errors` clause starts; its words "never their counts" are on line 4. Line 3 is kept, as r18 gave it.

No item text cited a line that has moved. Every PROBE path that is new in draft 26 exists.

## Not applied, or left for the next review
1. **BJ3's "the request count in the end window" is wrong by the code.** BJ3 is kept verbatim, as rule 1 requires, and the correction stands beside it, attributed to BI4. Rewriting BJ3 would need another proxy pass.
2. **Line 111's last sentence restates the trigger without BI5's exception.** It is unchanged, because P3 §4 sends any change there to another proxy pass.
3. **Two passages are untouched although they read oddly now.** Line 54's "**None of this is a switch.**" now follows (x), which is a switch; its subject is looks after the entry (BI7's trace). Line 104's "If either fact fails, batch 2 is labelled retrospective" is now redundant. Neither calls batch 2 primary.
4. **Pre-existing tags and facts, not in any item, not changed:**
   - D25/D26:9 cites FILE(docs/status.md:21) for "a one-line summary" of the review of draft 2. At HEAD, and at a8036fd, that line is "Next action: run REG-19". The tag was stale before this draft.
   - Line 3 says "3 to 22 in `docs/drafts/`"; drafts 23–25 are there too.
5. **BI-O2 is not taken.** It concerns the bundle note.
