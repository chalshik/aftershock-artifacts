# proxy-reg21-draft25-delta3 (proxy-reg21-d25), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T17:12:12.526Z; message 3 of 3 from this teammate). Third message: accepts the agent's reading; BJ8 and BJ13 replaced, BJ14 new, BJ12 withdrawn. Governs over the second.

---

Owner-proxy, round 3, REG-21 draft 25, on the agent's reading of D25:54 and D25:111: I accept it. Batch 2 is labelled retrospective by design under read (x). My previous message rejected that reading; this one replaces it, and it was wrong (section 1). Decision: APPROVE, on the conditions in section 3, all BEFORE. Please save this message verbatim as a third file beside the other two; edit neither earlier file.

## 1. Correction of my previous message (rule A6)
- **What I wrote.** "Line 54's trigger does not fire on Read 1, on its own terms … It is a completeness check at the append … That is how (vi)–(ix) entered draft 25 … Reversing that now for (x) would apply the rule unevenly."
- **Why it was wrong.**
  - I read only line 54's "If it then finds". I did not weigh the last sentence of line 111. That sentence repeats the statement on REG-19 readings "up to the append", against "the nine listed there, (i) to (ix)". It says: "If such a reading or run is known, it goes into 'What was known' … ; where the trigger in 'What was known' applies (…, or a read of a line a REG-19 burst run wrote after its burst began), batch 2 is also labelled retrospective by design (rule F round 17, BE4)."
  - That sentence covers a reading known before the append, beyond (i)–(ix). Read (x) is one.
- **My analogy to (vi) was also wrong.**
  - (vi)–(ix) entered under draft 24's line 111, which has no such sentence. I grepped draft 24 for "also labelled retrospective" and got no hit.
  - BE4's own text had already put the A14 recheck in its base list.
  - Draft 25's change log tested the four new reads against the trigger before listing them: "None prints a line a burst run wrote after its burst (DERIVED from the command texts)" (FILE(docs/drafts/reg21_draft25.md:253)).
- **The owner's plan does not override this rule.** The plan says looks are disclosed, not used as switches (FILE(docs/drafts/plan_2026-11-13.md:41)). But BE4 adopted a stricter rule through review, approved by both proxies, me included, before (x) was known. Applying it is mechanical. Reading it narrower now that the cost is known is what rule A5 forbids in spirit. The agent's refusal to do that is right.
- **"Known" holds.** From the inputs it is certain that the script read the `no_errors` counts out of every folder's `checks.json`, seed 15's to 17's burst runs included. Only the printing of seed 17's two rows is "most likely". The read of lines a burst run wrote after its burst began is enough.
- **What still stands from my previous message:** section 1 there (the correction of my Q3), BJ9, BJ10, and BJ11 (a) and (b).
- **What is withdrawn:**
  - its section 2;
  - BJ8 and BJ13, replaced below;
  - BJ12, a report meant to qualify a primary batch 2, which is now moot;
  - its section 4, items 1–2, and its owner notes 1–2.

## 2. Is round 3 now done on batch 2?
- Batch 2's standing is settled by the draft's own rule. Nothing about it is left for review.
- Line 54 and line 111 send the text "to rule F and an owner-proxy pass". This message is the owner-proxy pass on (x).
- Rule F round 18 was sent the [CORR] (FILE(docs/decisions.md:4453), "Round 3's four reviewers, running now, are sent this entry"). The [DECISION] (delegate) quotes round 18's reply on it, or says it gave none. That is the trade the review-stop rule made (decisions.md:4406 and :4437).
- REG-22 (D16:80) has the same text. My reading would be the same, but REG-22's proxy decides.

## 3. Conditions (all BEFORE). Every anchor occurs once in docs/drafts/reg21_draft25.md unless stated.

**BJ1 to BJ7** stand as in my first verdict, with BJ1 amended to "(i)–(x)". BJ4, BJ6 and BJ7 still apply: the freeze and its facts are still checked and reported for the retrospective batch 2.

**BJ8, replaced (disclosure, and the label it triggers).** In line 54, replace
`its committed run is the one at the append ("At the append of this entry").`
with
`its committed run is the one at the append ("At the append of this entry"). **(x) A read of REG-19's burst-run outcome counts, known before the append (decisions.md 2026-11-13 [CORR], FILE(docs/decisions.md:4453)).** On 2026-11-12 at 17:59:38 UTC a context-pack subagent of session fdf13821 (agent-a48736828ce71b739, line 201) ran `s57_inv.py`. For every folder under `runs/`, sorted by name, REG-19's included, the script read `config.yaml` fields, `checks.json`'s `valid` and `failed`, the `no_errors` counts `ok` (completed requests) and `unfinished` (not completed when the run stopped), and the number of files. It printed `tail -3` of that table. The last two folders are seed 17's control and its burst run, so the printed lines were most likely those two rows with both counts, plus a count line; the counts of seeds 15 and 16 were read but most likely not printed (DERIVED from the inputs, PROBE(docs/probe/20261113_transcript_search/inputs_s57_inv.txt)). Ten seconds later the subagent blanked both counts for every `w3000` folder and ran the script again. A run's `checks.json` is written at its end (FILE(harness/checks.py:237)), so this is a read of lines REG-19's burst runs wrote after their burst began. It goes beyond what `common.sh` allows (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:36)) and beyond (i) to (ix). The output was in the subagent's context. Its report to its parent was not opened, and whether anyone read the lines is not known (BELIEF either way). From the counts, a burst run's mean completion rate over the whole run (warm phase and burst included, not over W) and its line at the stop could be read, and so a rough r (DERIVED). **Timing:** the 0.05 on r of J1 and J2 was first committed with `analysis/k3w.py` at 72fafb5 (2026-11-12 19:00:16 UTC), and busy ≥ 0.99 at 3f5c84a (20:07 UTC). Both came after (x), in the autonomous agent's commits, not session fdf13821's. Reuse ≤ 0.05 was committed before (x), at d80b955 (16:19:45 UTC). **Consequence:** (x) is a reading known before the append, beyond (i) to (ix), of the kind this trigger names. So under the last sentence of "At the append of this entry", written in draft 25 from rule F round 17's BE4 before (x) was known, **batch 2 is labelled retrospective by design.** It is reported beside batch 1 as a second retrospective reading and never governs ("The two batches"). No review, statement, [CORR] or later commit restores primary standing; only the owner can, by an entry made before batch 1 is computed.`

**BJ14 (wording: the label, made consistent).**
- (a) Replace
`- **What this is, in one line:** one judged item on unread data (batch 2's J1) and one retrospective consistency reading (batch 1).`
with
`- **What this is, in one line:** two retrospective consistency readings, batch 1 and batch 2; batch 2 is labelled retrospective by design under read (x) ("What was known"), so no item is judged on unread data.`
The sentence after it stays as it is.
- (b) Replace
`**The only item on unread data is batch 2's J1, with what is known about it.**`
with
`**Batch 2's J1, which would have been the only item on unread data (labelled retrospective by design under (x) below), with what is known about it.**`
- (c) Replace
`Batch 2 is primary only if the stopping rule's facts (1) and (2) hold; otherwise it is labelled retrospective and never governs ("The two batches").`
with
`Batch 2 is labelled retrospective by design under (x) above and never governs ("The two batches"); the stopping rule's facts (1) and (2) are still checked and reported.`
- (d) In line 104, replace
`**Batch 2 is primary only if two facts in git hold,**`
with
`**Batch 2 is labelled retrospective by design (read (x), "What was known"); it would have been primary only if two facts in git held,**`
and replace
`The label follows from these facts alone`
with
`Apart from read (x), the label follows from these facts alone`
- (e) In line 111, replace both occurrences of
`the nine listed there, (i) to (ix)`
with
`the ten listed there, (i) to (x)`
Line 111 has one occurrence. The second is in the change log at line 253 and stays, as history.
- (f) In the heading at line 1, replace
`batch 2 on REG-19's burst runs, once REG-19 has reported (0 GPU h)`
with
`batch 2 on REG-19's burst runs, once REG-19 has reported, labelled retrospective by design (0 GPU h)`
- (g) In line 127, replace
`and names batch 2's J1 as the only unread item.`
with
`and names batch 2's J1 as the item that would have been unread, now labelled retrospective by design (read (x)).`
- (h) The header (line 3, already under BJ2) adds:
`Draft 26: read (x) and its label (round 3's owner-proxy, BJ8 and BJ14).`
- (i) Any other sentence that calls batch 2 primary, judged, or a reading on unread runs gets only the label word changed. Each such edit is listed in the [DECISION] (delegate).

**BJ13, replaced (disclosure, in the [DECISION] (delegate)).** The [DECISION] states:
- (a) the label and its ground: D25:111's last sentence and D25:54, applied to read (x);
- (b) that the rule was written in draft 25 from BE4, before (x) was known, so the label follows mechanically;
- (c) that the agent read it this way first (f3abd23), and that this proxy first rejected and then accepted that reading, quoting section 1 above verbatim;
- (d) BJ8's timing;
- (e) that D25:75 now applies: "batch 1 does not become the paper's statement: the paper then has a retrospective reading and no reading on unread runs." So "batch 1 is the primary analysis" means only that it is the registration's first computation. It is never worded as a test, "supports", "confirms" or "passes";
- (f) round 18's reply on the [CORR], or that it gave none.

## 4. Later changes that need another proxy pass
- BJ8, BJ13 or BJ14 written other than as given.
- Any edit to batch-2 text beyond BJ14(i)'s label words.
- Any change to the trigger, to line 111's last sentence, or to "The two batches".
- Any entry that would restore batch 2's standing. That is the owner's alone, before batch 1.

## 5. Notes for the owner
1. **REG-21 no longer judges anything on unread data.** Its value is batch 1's readouts and a retrospective batch 2. If you want K3 read prospectively, it needs runs that no one has looked at, registered before they are read (BELIEF on which runs fit).
2. **Only you can overrule the label.** The plan allows it only by an entry before batch 1 (plan_2026-11-13.md, "Kept"). Such an entry would be blind to J1, but not to seed 17's counts, if anyone saw them. I would not recommend it. The rule that fired was adopted through review, blind, and it fired on the first case it was written for.
3. **A timing discrepancy.** status.md and STATE.md say the read was found "≈ 16:50 UTC", but the [CORR] was committed at 16:43:16 UTC (d960ef3, committer time). This is minor; the wording should be fixed.
4. **labels.tsv** is modified in the working tree after d960ef3. The entry should cite the version at its own commit.

## 6. Not checked
- Any output: s57_inv.out, the subagent's report, the transcripts' tool results.
- The context pack beyond count-only checks.
- Who made 3f5c84a.
- Whether 72fafb5's author saw the counts.
- Rule F round 18's reply.
- REG-22's draft 16.
- runs/ beyond names, which I did not open.
