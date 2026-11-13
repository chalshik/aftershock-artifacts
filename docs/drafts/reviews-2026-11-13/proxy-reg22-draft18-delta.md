# proxy-reg22-draft18-delta (proxy-reg22-d17), verbatim

Saved by the agent from the reviewer's own SendMessage call to team-lead (tool-call input, its session 9fb0a805, line 612, timestamp 2026-11-13T20:41:12.830Z; the send succeeded, msg_id 5e3f0d49), because the message was never delivered into the main session's transcript (checked by the agent's extract_teammate.py on 2026-11-13 21:05 UTC: no message from proxy-reg22-d17 after 18:08:54 UTC). Its verdict on REG-22 draft 18 (round 4: rule F round 12's items) as of 00c6359. Item names CL1–CL6 are this pass's. First of two messages.

---

Owner-proxy on REG-22 draft 18 (round 4: rule F round 12's items, CG1–CG12): APPROVE on CL1–CL6. CL1–CL4 apply BEFORE the entry. CL5 is BEFORE E, as a further entry on the review-stop rule. CL6 is LATER, in the [DECISION] (delegate). CH11 stands as given. Batch 2 stays retrospective (by design); no threshold, code, run set or label changes.

d18 = docs/drafts/reg22_draft18.md at 00c6359 (HEAD at my check). The freeze holds:
- `git log --all --full-history ffc76b3..HEAD` over the 27 frozen files prints nothing.
- `git status --porcelain` on them prints nothing.
- The last commit on the set is ffc76b3, 2026-11-13 10:40:28 UTC (DERIVED, my run).

## 1. Is draft 18 as approved, and are round 12's items applied?
- **CH1–CH10: verbatim.** Each replacement text occurs exactly once in d18, and each old text zero times (string match, my script; CH7's old text is a prefix of its new one).
- **CG1(a), CG1(b), CG2, CG3(a)–(c), CG4, CG5(a), CG6: verbatim.** I cut each from rulef-reg22-draft17-r12.md by line and matched it once.
- **Optional items:**
  - CG7 is in as `git log -m --all --reflog …`;
  - CG9, CG10 and CG12 are verbatim;
  - CG8 = CH9, and CG11 = CH5.
- **CG5's second replacement, not applied: approved.** CH8 is stricter (every `names_in_command` hit labelled by hand), and both list `disclosed[CORR]`.
- **The agent's additions: approved.**
  - (a) "That entry is headed `[DECISION] (owner)`; a delegate entry restores nothing" adds to CH4 without changing its words. It is consistent with CG3 and with the plan (FILE(docs/drafts/plan_2026-11-13.md:54)).
  - (b) Seed 18's `continue`: the arithmetic is right. `reg18_continue` is True only if k + remaining ≥ most (FILE(analysis/gate.py:1710)); with remaining = 1 and most = 3, k ≥ 2. queue.sh:93 is the arm that goes on to the next seed. The premise that the queue, not a hand launch, started seed 19 rests on the prelaunch names. It is honest disclosure of what REG-19 allows to be read (`continue`).
- **My rulings on the items rule F sent to the proxy:**
  - **CG1:** approved. Only the two synthetic names exist in committed text (`git grep -E 'reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z' HEAD`: rulef-reg22-draft16-r11.md:74 and two bundle copies). A real file with either stamp still counts.
    - Its duty sentence was left inconsistent: the [REG] itself will breach "no … committed text writes a table-file name …" by quoting round 11 verbatim. CL2 fixes that.
    - Its effect on the review-stop rule's check is not yet applied; CL5 applies it.
  - **CG2:** approved. It closes BK-S4's own trace (a post-S code change steering line a through batch 2).
  - **CG3:** approved, and CL4 extends it to the one release left open. Line 102 still lets "a [DECISION] that cites both batches", which can be a delegate's, release line a and line d when the batches disagree. That is the main disagreement case and the same after-the-data trace CG3 names.
  - **CG5(a):** approved. CL1 adds two facts:
    - the session that ran the grep is the one that wrote c2.py and built this draft;
    - no frozen file has changed since before the grep.
  - **CG4 and CG6** (rule F: no pass) and **CG7, CG9, CG10, CG12:** approved.

## 2. False, or readable as a blind or confirmatory test?
- No sentence makes either batch primary or calls it a test; the label words are as approved.
- **Line 4's "CG1–CG6, all in the text" is inexact:** CG5's second replacement is not in it. CL3.
- **The duty sentence (line 133):** besides being self-breached, it joins two clauses with a comma. CL2 rewrites it.

## 3. Conditions

**CL1 (BEFORE; a disclosure; batch 2's standing: no).** Line 80, CG5(a)'s text. Replace:
`(DERIVED from the command text, tool-call inputs only; what it printed is not stated; those files are local and not committed);`
with:
`(DERIVED from the command text, tool-call inputs only; what it printed is not stated; those files are local and not committed; session 8c5f8396 is the session that wrote `analysis/c2.py`, above, and built this draft; no frozen file has changed since `ffc76b3`, 2026-11-13 10:40 UTC, before this read: `git log --all --full-history ffc76b3..HEAD` over the frozen files printed nothing at `00c6359`, owner-proxy on draft 18, CL1);`

**CL2 (BEFORE; a reporting duty made consistent with CG1; standing: no).** Line 133. Replace:
`no decisions.md entry, saved review or other committed text writes a table-file name with a stamp that `final.sh` did not write, a decisions.md entry that does so`
with:
`no decisions.md entry, saved review or other committed text writes a table-file name with a stamp that `final.sh` did not write, apart from the two synthetic names that rule F round 11's saved review holds (FILE(docs/drafts/reviews-2026-11-13/rulef-reg22-draft16-r11.md:74)), its review-bundle copies and this [REG]'s verbatim quote of it; a decisions.md entry that does so`

**CL3 (BEFORE; wording).** Line 4. Replace:
`NOT READY, CG1–CG6, all in the text)`
with:
`NOT READY, CG1–CG6, all in the text but CG5's second replacement, which CH8 meets)`

**CL4 (BEFORE; a stricter rule, CG3 cross-applied; standing: no).** Line 102. Replace:
`any wording that relies on either waits for a [DECISION] that cites both batches.`
with:
`any wording that relies on either waits for an entry headed `[DECISION] (owner)` that cites both batches; a delegate entry does not release either line (rule F round 12, CG3, cross-applied by the owner-proxy on draft 18, CL4).`

I applied CL1–CL4 in order to a scratch copy. Each anchor occurs exactly once in d18 and once at the moment it is applied. No CL text contains a string that fact (2)'s grep matches.

**CL5 (BEFORE E: a further entry, as BK-S1 times items against the review-stop rule; a stricter rule).** Anchor in d18, line 133: `whose check uses these three commands without `--reflog`, so that this fact's `git log` can only find more, FILE(docs/decisions.md:4555)`. No text change in d18. A further [DECISION] (delegate) entry, committed before E of either registration, applies to the review-stop rule's item-5 check, verbatim:
"In item 5's check (FILE(docs/decisions.md:4555)), the two synthetic stamps 20261114T010203Z and 20261114T020000Z that the decisions.md grep prints (rule F round 11's BK2 trace, step 8, FILE(docs/drafts/reviews-2026-11-13/rulef-reg22-draft16-r11.md:74), which REG-22's [REG] quotes verbatim) do not count toward S; a file with either stamp in a working tree, or added by a commit, still counts (rule F round 12, CG1, cross-applied as its verdict asks; owner-proxy on REG-22 draft 18, CL5)."
Written as given, this needs no further pass. Write the stamps without their file-name prefix, as above.

**CL6 (LATER: in the [DECISION] (delegate); a reporting duty).** Anchor, line 4: `the [DECISION] (delegate) holds both owner-proxy verdicts verbatim and names, for each owner-proxy condition in force, the sentence that meets it.` No text change. The [DECISION]:
- (a) carries CH11 in full, with its mapping extended to CL1–CL6;
- (b) lists each of CG1–CG12 with rule F's class, where it sits in the text, and this pass's ruling (section 1);
- (c) names the agent's two additions as approved here;
- (d) quotes the CL5 entry by its line;
- (e) shows that classify2's output at E has no `UNLABELLED` hit and no `names_in_command` rule label (each hand-labelled under CH8), and names the hit at session 8c5f8396 line 9857 (15:32:08 UTC) with its class "listed" (the CG5(a) read);
- (f) says the agent's own session ran that grep, and that neither the agent nor any reviewer has opened its output.

## Which later changes need another proxy pass
- CL1–CL6 written other than as given.
- Any change to CH1–CH10, CG1–CG3, CG5(a), the agent's additions, BL1–BL3, BK1, the trigger or CH7.
- Any text that makes batch 2 primary or splits it.
- Any change to the freeze, facts (1) and (2), the validity cut, the frozen list or the release clauses beyond wording or a stricter rule.
- **At E, a pass if:**
  - classify2 has an `UNLABELLED` hit, a `names_in_command` rule label, or a label outside CH8's mapping;
  - the rerun finds a read of the trigger's kind that this text does not list;
  - a `c2` output exists on a batch-1 run;
  - `search2.py` at E narrows what d960ef3 finds.
- **No pass** for:
  - a [CORR] after E recording what the 15:32 grep or RESUME.md held;
  - change-log lines describing CL1–CL6.

## Notes for the owner
1. **CG3 and CL4: in every disputed case at λ = 2.0, the D1/D2 wording now waits for you** (batch 2 pending after S, not computed after S, a defect, a post-S code change, or the batches disagreeing). A delegate entry cannot release it. This goes against "it should never depend on me", but only in cases where the choice is made after seeing the data, which the delegation does not cover. P(any such case) is small (BELIEF; ≤ 0.084 for batch 2 changing a decision, DERIVED in the draft).
2. **The registration now records partial REG-19 outcome: at least two of seeds 15–18 passed.** REG-19 allows reading its `continue` flag.
3. **The 15:32:08 UTC grep of `docs/paper/` (the local, uncommitted context pack) was run by the agent's own session.** Only you can check whether those lines quote a burst run's post-burst line. Either way the label does not change.
4. **Timing:** if REG-21's or REG-22's E falls after 2026-11-14 01:02:03 UTC, CG1's exemption (and CL5 for the stop rule) is what keeps fact (2) from failing on the synthetic stamps.
5. **RESUME.md** is still unchecked (CH11 d).

## Not checked
- CG4's two `find` commands: not run, because the second one lists `runs/`'s entries.
- CG7's merge-commit case: rule F's scratch test, not reproduced.
- The 79 `names_in_command` hand labels, which do not exist yet.
- REG-21 draft 27; docs/drafts/reg22_decision_draft2.md (untracked, not opened); the build script.
- Not opened: `runs/` beyond folder names, `state/`, queue and probe outputs, RESUME.md, docs/paper, any transcript.
- `pytest` and `check_docs`: not run.
- I wrote nothing into the repository. My scratch copy with CL1–CL4 applied: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/9fb0a805-9660-4a34-8cd0-40cdc274d7f6/scratchpad/d18_with_CL.md (script: cl.py).
