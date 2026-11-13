# rulef-reg21-draft26-r19 (rulef-reg21-r19), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T18:08:54.915Z; message 1 of 1 from this teammate). Round 4 (text written under the stop). Item names CE1–CE9, CE-O1–CE-O8 are this round's.

---

Rule F round 19 on REG-21 draft 26 (bundle reg21_r19, round 4 under the stop): NOT READY. Nine items are required (CE1–CE9), all of them text: no threshold, code or run set changes. ("main" was refused by the tool, so this comes to you.) D26:n = line n of registration_draft26.md.

Three items bear on what batch 2 still does:
- CE1: with batch 2 already retrospective, the freeze's only sanction has become a no-op.
- CE2: the owner's restoration window outlives S.
- CE3: the "two batches" rule is non-monotone.
The other six fix false or blind-sounding sentences.

WHAT I READ / RAN
- Read: BUNDLE_NOTE, MANIFEST, item_map, draft 26 (all of it), the word diff from draft 25, round18_rule_f with its addendum, the three proxy messages, the stop, review-stop, amendment, delegation and three [CORR] entries, inputs_s57_inv.txt, classify2 output headers and counts, the search2 source (classes), k3w.py:370–395, load.py:160–186, k1._state at 1cface7, harness/run.py (the Events class and the checks event), vm_state.py, and queue.sh:60.
- Ran (read-only): git log/diff/show; closure output (26 files); `git diff --stat 8164211 HEAD -- <26 frozen>` (empty); BJ4(a)'s shadow grep on 8164211..HEAD (empty); anchor and verbatim counts; `ls runs` (names only); a listing of the folder names under ~/.claude/projects; and an inputs-only grep of the transcripts (my scratch script).
- By design (rule F isolation) I did not read the session-start set.
- Disclosure: my grep printed ≤300-char excerpts of a few `SubagentHandback` records around "RESUME.md". These are stored as tool_use in subagent transcripts but are the parents' tool results. None held a run value (they mention validity, "outcome withheld" and line numbers). I then excluded that record type.

TASK 1 — ROUND 3'S ITEMS
- Verbatim check: all 29 texts I tested occur exactly once in D26: BJ1(amended), BJ2a/b, BJ3a/b, BJ4a/b, BJ5, BJ7, BJ8(P3), BJ9, BJ10, BJ11a/b, BJ14a–h, BI4b, BI5's trigger edit, BI6, BI7, BI8 and BI-O1. BI1's three edits are there. BI2's limits match the addendum.
- Applied, with sound departures: BI2, BI3, BI4 (as an attributed correction), BI4b, BI6, BI7, BI8, BI-O1, BI-O3, BI-O4 and BI-O5.
  - BI-O4 holds: one project folder under ~/.claude/projects; the two pin worktrees have none.
  - BI4 is right: the 14:09:43 input printed x['end'], and `n` is the mean of `num_requests_running` (k1._state at 1cface7; load.py:183).
  - BJ8's Timing holds: 72fafb5 (19:00:16 UTC) added the 0.05; 3f5c84a (20:07:42) added 0.99; d80b955 (16:19:45) added reuse ≤ 0.05. Both later commits were made by session 8c5f8396 (the inputs of its `git commit`, lines 990 and 2067), not fdf13821.
- Applied wrongly or on an unsound ground:
  - BI1's "rewrite 'The two batches'": departed on the ground that line 73 suffices. That ground is only partly true (CE3).
  - BJ14(i): lines 76, 84 and 113 still word batch 2 as able to govern, or as blind (CE3, CE4). The agent's grep covered "primary" and "unread", not "judged" (CE-O6).
  - BK4's departure rests on "the agent may not open the note under its delegation". That is not in the delegation, and the agent's own sessions opened the note under it (CE5).
  - BJ8 and BJ11(b) carry sentences that are or will become false (CE6, CE7). BJ3 keeps a false clause (CE-O1).
  - The item map is stale against D26:284 (CE-O3).
- Freeze: lines 105–110 are byte-identical to draft 25. Line 104 changed only by BJ14(d), BJ4(a), BJ5, BJ7 and BI-O1. The text holds; its sanction does not (CE1).

TASK 2 — RULE F PROPER
- Trace (CE1):
  1. S happens: REG-19's table gives c over W per batch-2 run. By D26:55 that fixes r's first factor.
  2. Suppose batch 2 sits about 0.03 above batch 1's λ = 2.0 median with a different label. "At the tolerance" (D26:74) then bars "inside" at λ = 2.0.
  3. Someone commits a "fix" to k3w.py (busy threshold, coverage gap, or REG-20's work on k1.py), legitimately with reviews under line 106's fix clause.
  4. Batch 2 becomes undefined, or its contrast moves past 0.05. Line 75 or line 73 lifts the ceiling.
  5. The cost under D26: "labels batch 2 retrospective", already true, plus a reporting duty.
  6. Every batch-2 sanction is void this way: facts (1) and (2), the fix clause, line 110's heading rule, line 112's notice. Yet review-stop item 5 says "no code or threshold changes after the entry (rule A5 binds a retrospective batch too)", and stop entry rule 5 says the facts decide "with which words".
- Trace (CE3): batch 1's λ = 2.0 median is 1.03 (inside); retrospective batch 2's is 1.12 (outside high), a contrast of 0.09.
  - "Disagree" is disapplied (D26:73); "At the tolerance" needs ≤ 0.05.
  - So batch 1's "within 0.05" sentence for λ = 2.0 stands. At 1.07 it would be capped.
  - A larger same-load disagreement gives a stronger claim.
- Trace (CE2): BJ8 lets the owner restore primary standing "before batch 1 is computed". Batch 1 can follow S, and after S r is nearly known. P3's note 2 ("blind to J1") is false after S.
- Strongest alternative: J1 inside follows from preconditions (a) all-miss and (b) busy for any saturated all-miss engine with the same per-token prefill cost, and r restates c (D26:51). So "inside" cannot tell model F's trap from plain all-miss overload.
  - λ = 2.4's predicted "outside high" is confounded by open- versus closed-loop reference, dev mode, day/clock and redo. E1 and the redo proxy separate only the first and the last.
  - Seed 17's batch-2 r was roughly knowable from read (x).
- Can it change a decision? No GPU decision. It can change K3's wording only: J2 outside (P ≈ 0.13), and, after CE3, a retrospective batch 2 that differs at λ = 2.0. D26:63 already limits it to computing and reporting.

TASK 3 — NEW TEXT
- False sentences: CE5–CE9, and BJ3's clause (CE-O1).
- Batch 2 worded as primary or blind: lines 76, 84 (CE3) and 113 (CE4); BJ8's window (CE2).
- Batch 1 worded as confirmatory: none found.
- Freeze per rule 5: text kept; sanction lost (CE1).

REQUIRED ITEMS (every anchor occurs once in registration_draft26.md; checked)

CE1 — the freeze's sanction is void once batch 2 is retrospective
- Edit 1, D26:104. After `If either fact fails, batch 2 is labelled retrospective and never governs ("The two batches"); no review, statement, [CORR] or later commit restores primary standing.` add:
  " **Since batch 2 is already labelled retrospective by design (read (x)), that label is no longer a sanction, and the sanction falls on what REG-21 says about λ = 2.0:** if fact (1) or fact (2) fails, if a fix to a frozen file is made (the fix clause), if a line that begins as REG-19's result heading is written before REG-19's final result, or if batch 2 is not computed because of an entry that changes a validity flag, a breach of duty (a), or a result heading the seal does not accept, the ceiling of "At the tolerance" applies to every sentence on λ = 2.0 whatever batch 2's label or its absence, J2 is not read as a statement about load, and K3's status names the event; batch 2 is still computed and reported where these rules compute it, and the batch-2 [RESULT] states which event occurred (rule F round 19, CE1)."
- Edit 2, D26:112. Replace `REG-20's work included, labels batch 2 retrospective, and new code goes into new files` with:
  "REG-20's work included, caps what REG-21 says about λ = 2.0 at "at the tolerance" (batch 2 is already labelled retrospective by design; the stopping rule, rule F round 19, CE1), and new code goes into new files".
- Class: a stricter rule. Batch 2's standing under rule 2: no (the consequence is batch 1's wording). It does touch "the two facts", which item 3 names. Owner-proxy pass: yes.

CE2 — BJ8's restoration window outlives S
- D26:54. Replace `No review, statement, [CORR] or later commit restores primary standing; only the owner can, by an entry made before batch 1 is computed.` with:
  "No review, statement, [CORR] or later commit restores primary standing; only the owner can, by an entry whose commit's committer time is earlier than each of batch 1's time, the time of any computation that prints U, an uncached-token rate or r on a batch-1 or reference run, and S (the earliest table-file stamp, the stopping rule's fact (2)), compared as instants as "The rule on the two batches was fixed knowing batch 1's side of it" compares them. That entry states what its author had seen of REG-19's runs, read (x)'s counts, the note `RESUME.md` and the context pack of 2026-11-12 included; if that includes any output of `analysis.gate reg19` or anything of a REG-19 burst run after its burst beyond `common.sh`'s allowed reads, it restores nothing. A later entry restores nothing: REG-19's table gives each batch-2 run's completion rate over W, which fixes r's first factor (rule F round 19, CE2)."
- Class: a stricter rule. Batch 2's standing: yes (its label). Owner-proxy pass: yes.

CE3 — non-monotone "two batches"; lines 76 and 84 still say the contrast decides whether batch 2 governs
- (a) D26:73. After `A batch 2 labelled retrospective is reported beside batch 1 as a second retrospective reading; it never governs, and "disagree" and "Batch 2's J1 inside" do not apply to it.` add:
  " When batch 2 so labelled and batch 1's λ = 2.0 group are both defined and differ in label or side, the ceiling of "At the tolerance" applies whatever the size of the fixed-load contrast: both medians, both labels with their sides, both n, both windows and the contrast are given together, no sentence says "within 0.05" or "r times" for λ = 2.0 on one batch alone, and K3's status says "at the tolerance at λ = 2.0", names batch 2's label and its retrospective standing, and is not worded as inside (rule F round 19, CE3)."
- (b) D26:76. Replace `(not judged as a statement; its size against 0.05 decides whether batch 2 governs;` with:
  "(not judged as a statement; its size against 0.05 would have decided whether a batch 2 not labelled retrospective governs, and decides J2's reading below;"
- (c) D26:76. Replace `it changes neither J2's reading nor which batch governs, which rests on `fixed_load_contrast.difference` and the check of `batch1_median` ("Reported", the fixed-load contrast) alone.` with:
  "it changes neither J2's reading nor which batch governs; for a batch 2 not labelled retrospective, which batch governs rests on `fixed_load_contrast.difference` and the check of `batch1_median` ("Reported", the fixed-load contrast) alone, and a batch 2 labelled retrospective never governs ("The two batches")."
- (d) D26:84. Replace `It carries no label of its own, but its size against 0.05 decides whether batch 2 governs;` with:
  "It carries no label of its own; its size against 0.05 would have decided whether a batch 2 not labelled retrospective governs, and it decides J2's reading ("The fixed-load contrast", above);"
- Class: a stricter rule, and wording. Batch 2's standing under rule 2: no; it is "what a retrospective batch 2 does" (item 3). Owner-proxy pass: yes (P3 §4).

CE4 — D26:113 obliges a blind-sounding wording
- Replace `and keeps the wording "whose r had not been computed" exactly.` with:
  "and, since batch 2 is labelled retrospective by design (read (x)), does not use the words "whose r had not been computed" or the wording of "Batch 2's J1 inside"; it gives batch 2's J1 with its label, side, median, n, range and window, names read (x), and calls it a second retrospective reading (rule F round 19, CE4)."
- Why: it contradicts BI8 and D26:73, and leaves the wording to whoever holds the output.
- Class: wording, and a reporting duty. Batch 2's standing: no. Owner-proxy pass: yes.

CE5 — BK4's departure rests on a false ground; the session that fixed the tolerances read the note whole
Trace (inputs only):
- 8c5f8396 main line 265, Read of RESUME.md, 2026-11-12 18:28:18 UTC. That is 37 s after the delegation's commit (c94a77d, 18:27:41) and 32 min before 72fafb5.
- Same session, 20:28:32: `cut -c1-1800`.
- Its subagents: `cat -n` at 2026-11-13 00:39:56; a whole Read at 12:23:22.
- The main session: `sed -n 18,22p` at 12:07:26.
- The no-open rule first appears at about 12:35 UTC on 11-13.
Edits:
- (a) Replace `what the note quotes of REG-19 runs' run-time lines is not stated: the agent may not open the note under its delegation; the owner can.` with:
  "what the note quotes of REG-19 runs' run-time lines is not stated here. The autonomous agent's own sessions opened it under the delegation: session 8c5f8396, which committed the 0.05 on r (72fafb5) and busy ≥ 0.99 (3f5c84a), read it by Read at 2026-11-12 18:28:18 UTC, 37 s after the delegation entry was committed (c94a77d) and 32 min before 72fafb5, and its first 1800 characters per line at 20:28:32 UTC; its subagents printed it whole at 2026-11-13 00:39:56 UTC and read it whole at 12:23:22 UTC; its main session printed lines 18–22 at 12:07:26 UTC (tool-call inputs only). Since about 12:35 UTC on 2026-11-13 the agent keeps the note closed to its subagents, and it does not state the note's content (BELIEF: its own report). The owner checks what the note quotes of REG-19 burst runs' run-time lines, and the batch-2 [RESULT] states what the owner found or that it was not checked (rule F round 19, CE5)."
- (b) Replace `by Read at 18:28 and 18:43 UTC;` with "by Read at 2026-11-12 18:28 and 18:43 UTC;".
- (c) Replace `in parts at 2026-11-13 11:38–12:23 UTC;` with "in parts, and once whole by Read at 12:23 UTC, at 2026-11-13 11:38–12:23 UTC;".
- Class: a disclosure, and a reporting duty. Batch 2's standing: no. Owner-proxy pass: yes.

CE6 — two present-tense sentences will be false at the append
- Why: queue.sh:60 rsyncs each finished run into `runs/`. Seed 18's attempt-3 control, `20261113-165516_…_s18`, sorts after seed 17's burst run. At 17:46 UTC the last name in `runs/` was still seed 17's burst run.
- (a) Replace `The last two folders are seed 17's control and its burst run, so the printed lines were most likely those two rows with both counts, plus a count line;` with:
  "At 17:59:38 UTC on 2026-11-12 the last two folders were seed 17's control and its burst run (DERIVED: they were the last two folder names in `runs/` on 2026-11-13 at 17:46 UTC, and no folder is ever removed), so the printed lines were most likely those two rows with both counts, plus a count line;"
- (b) Replace `(DERIVED: it is still the last folder name in `runs/`, and no run folder is ever removed)` with:
  "(DERIVED: it was still the last folder name in `runs/` on 2026-11-13 at 17:46 UTC, and no run folder is ever removed)".
- Class: wording. Batch 2's standing: no. Owner-proxy pass: yes (BJ8 text).

CE7 — BJ11(b): "labelled by hand" is false, and the cited output predates BI6's rule
- 120 lines of classify2_20261113T163634Z.txt carry the note `auto`. That file was last committed in d960ef3, before ba93d3b saved classify2_bi6_20261113T163634Z.txt.
- Replace `with every hit at or after 2026-11-11 17:15:21 UTC labelled by hand (PROBE(docs/probe/20261113_transcript_search/classify2_20261113T163634Z.txt), FILE(docs/probe/20261113_transcript_search/labels.tsv) at its entry-commit version);` with:
  "with every hit at or after 2026-11-11 17:15:21 UTC labelled, by hand or by `classify2.py`'s rules as BI6 restricts them (120 lines carry the note `auto`; PROBE(docs/probe/20261113_transcript_search/classify2_bi6_20261113T163634Z.txt), FILE(docs/probe/20261113_transcript_search/labels.tsv) at its entry-commit version);"
- Class: wording, and a tag. Batch 2's standing: no. Owner-proxy pass: yes.

CE8 — D26:264's "none of them changes here" is false (BJ4(a) adds a condition to fact (1))
- Replace `That entry keeps the freeze, the two git facts, the validity cut and the not-computed rules (its item 5, BK-S4); none of them changes here.` with:
  "That entry keeps the freeze, the two git facts, the validity cut and the not-computed rules (its item 5, BK-S4); none of them is loosened here: fact (1) gains BJ4(a)'s shadow-path condition, line 104's duties gain BJ5's, BJ7's and BI-O1's words, and line 112's notice gains BJ4(b) (stricter rules and reporting duties); lines 105–110 are unchanged."
- Class: wording. Batch 2's standing: no. Owner-proxy pass: no.

CE9 — D26:3's "No code changed since `8164211`." is false (pre-existing)
- c2.py, k5.py and e1.py changed (`git diff --stat 8164211 HEAD -- analysis`).
- Replace it with: "No frozen file and no line of `tests/test_k3w.py` changed since `8164211` (`git diff --stat 8164211 HEAD` on them is empty on 2026-11-13; `analysis/c2.py`, `analysis/k5.py` and `analysis/e1.py`, none of them frozen, changed)."
- Class: wording. Batch 2's standing: no. Owner-proxy pass: no.

OPTIONAL
- CE-O1: In BJ3's text, `the request count in the end window and percent fast in the baseline;` → "the mean running batch in the end window and percent fast in the baseline;". Proxy pass yes.
- CE-O2: D26:111's last sentence lacks BI5's exception. After `a read of a line a REG-19 burst run wrote after its burst began)` insert ", other than `checks.json`'s `valid` and `failed`". Proxy pass yes.
- CE-O3: The item map is stale against D26:284: it omits line 9 and calls the "switch", "3 to 22" and line-9 edits untouched. Replace `- **BI5:** verbatim.` with "- **BI5:** verbatim, except the date (2026-11-12) added to its 19:52:14 listing (the last bullet)." The "switch" edit sits in the trigger paragraph (P3 §4), so the proxy should see it named.
- CE-O4: `r, a label of either test or any output` → "r, a label of J1 or J2 or any output".
- CE-O5: `and one attempt is left;` → "and one attempt was left at draft 26 (BELIEF as of 2026-11-13 17:30 UTC);".
- CE-O6: "judged" (lines 35, 42 and 59) is the technical sense; no change, but the [DECISION]'s BJ14(i) list should say so.
- CE-O7: After BI8's sentence (`In item 4 of the review-stop rule, 'primary' means the reading cited first, not a confirmatory one (rule F round 18, BI8).`) add: "Elsewhere in this entry 'primary standing' means the standing of a reading on unread data that governs; batch 2 does not have it."
- CE-O8: Replace `` `grep_runs` and `read_run`, and every `ran` hit `` with "`grep_runs`, `glob_runs`, `write_runs` and `read_run`, and every `ran` hit".

VERDICT: NOT READY until CE1–CE9 are applied, all as text. Under the stop entry they are applied and recorded verbatim, and the owner-proxy decides. CE2 alone has batch 2's label as its consequence.

NOT CHECKED
- RESUME.md, queue_*.txt (including queue_run4_output.txt:5), state/, the backups, and runs/ beyond names.
- Any tool output, including the s57_inv output, the subagent's report and the context pack.
- The [DECISION] (delegate): BJ6, BJ13, BF9, BJ4(c) and BI7's repeat.
- REG-22 draft 17.
- I did not run pytest, check_docs, any analysis on runs, or search2/classify2.
- Who made the 18:43 Read (4e055435).
- The ±0.02 BELIEF and the predictions.
- The VM.
- That both of seed 17's folders were in runs/ at 17:59:38 (taken from the [CORR]).
- Scratch: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/81c4f760-bf64-44f0-97bf-91de7a8730ee/scratchpad/inputs_grep.py. Nothing was written into the repository.
