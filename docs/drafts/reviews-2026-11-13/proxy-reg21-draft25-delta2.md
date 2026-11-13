# proxy-reg21-draft25-delta2 (proxy-reg21-d25), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T17:12:12.526Z; message 2 of 3 from this teammate). Second message; withdrawn in part by the third (its sections 2 and 4 items 1–2, BJ8, BJ12, BJ13, notes 1–2).

---

Owner-proxy, round 3, REG-21 draft 25, after the [CORR] at decisions.md:4453 (d960ef3): APPROVE kept, on BJ1–BJ7 as amended here plus BJ8–BJ13, all BEFORE. None is a design change, and none stops the review. I also reject the agent's reading in f3abd23 that the draft's own trigger fires on Read 1. My first verdict contained a false statement; its correction is section 1. Please save this message verbatim beside docs/drafts/reviews-2026-11-13/proxy-reg21-draft25-delta.md, as a second file. Do not edit the first.

## 1. Correction of my own verdict (rule A6)
The saved verdict, Q3 (proxy-reg21-draft25-delta.md, lines 83–85), says: "The listed reads (i)–(ix) are accurate, and none could have shown a REG-19 burst run's outcome", and "s57_inv.py masks the `no_errors` detail for w3000 folders."
- **What was wrong.** The masking is true only of the script's later version, the one I read. The run at 17:59:38 UTC used the unmasked version and printed `tail -3` of the table. That is most likely seed 17's control row and its burst row, with `ok` and `unfinished` (PROBE(docs/probe/20261113_transcript_search/inputs_s57_inv.txt)). The mask came 10 s later.
- **How it happened.** I checked the script's text but not which version ran at which time.
- **What still stands.** Q3's other findings: (a) the 14:09:43 command (BJ3), the listed reads (i)–(ix) as described, and s57_heavy.py skipping `w3000` folders.
- **What is struck.** Q3's sentence "none could have shown a REG-19 burst run's outcome."

## 2. Does the [CORR] change the decision? No, and here is why.
- **The owner's own rule covers this case.** The owner-approved plan says: "Looks before the entry are disclosed under 'What was known', not used as switches. A look cannot move the computation once that computation is frozen." (FILE(docs/drafts/plan_2026-11-13.md:41), approved in bbe5f1a.) The plan also records as not adopted an earlier REG-21 proxy position that a look beyond common.sh's allowed reads loses batch 2. Read 1 is exactly such a look.
- **Line 54's trigger does not fire on Read 1, on its own terms.**
  - The trigger reads: "The search is run again at this entry's commit. If it then finds … a read of a line a REG-19 burst run wrote after its burst began, beyond what is listed here …"
  - It is a completeness check at the append. Read 1 was found before the append and is listed as (x).
  - That is how (vi)–(ix) entered draft 25 after round 2's search. My first verdict applied the same reading to (vi), a run of `analysis/` code on REG-19 folders: listed before the append, so the trigger does not fire. Reversing that now for (x) would apply the rule unevenly.
- **The agent's reading (f3abd23) has a real argument.** Read 1 is the first listed read in the trigger's second category; every other burst-run read was argued to be start-up. And a list that can grow until the append makes the trigger bite only on reads the drafter failed to find. That is its design, as the plan intends. The cost is that batch 2's "primary" standing now carries a disclosed look at one of its runs, made before its J1 tolerance was set (BJ8). An honest disclosure plus a reporting duty (BJ12) is what the owner's rule asks for. Turning the look into a switch now would go against plan:41.
- **Optional, stricter choice.** If the agent nevertheless labels batch 2 retrospective by design, that is a stricter choice, not one my APPROVE requires. The [DECISION] must then say it was a choice, not the trigger (BJ13).
- **Does Read 1 bear on A5? Possibly, not shown.** Evidence:
  - J1/J2's 0.05 on r was first committed with `analysis/k3w.py` at 72fafb5, 2026-11-12 19:00:16 UTC, 61 min after Read 1 (FILE(analysis/k3w.py:83)). This commit also added agent/INGEST.md, so it is the autonomous agent's, not session fdf13821's.
  - busy ≥ 0.99 came at 3f5c84a (20:07 UTC), also after Read 1.
  - reuse ≤ 0.05 was committed before it, in k3.py at d80b955 (16:19:45 UTC).
  - The number 0.05 itself was in REG-21 draft 1, on another statistic (d_obs, Q2; FILE(docs/drafts/scratchpad-2026-11-12/reg21_draft.md:25); file time 15:55 UTC, BELIEF since that is a file mtime).
  - The agent read the 2026-11-12 context pack in part (FILE(agent/INGEST.md:14)). By a count-only check that printed no values, its four table rows for seed 17's burst run give the outcome as "withheld": 4 of 4 contain "withheld", none contains "ok=" or "unfinished". That is not proof that no other section holds the counts.
  - What the counts allow (DERIVED): `ok` ÷ run length is the whole-run mean completion rate, warm phase and burst included, not c over W. `unfinished` is the line at the stop. So at most a rough r for 1 of up to 5 batch-2 runs, beyond what the `continue` flags already bound (r < 1.24).
  - Whether anyone read the printed lines is unknown, BELIEF either way.
  - Conclusion: influence on 0.05 is neither shown nor excluded. Disclosure, not a switch.

## 3. Conditions (all BEFORE). Anchors are verified to occur exactly once in registration_draft25.md (= docs/drafts/reg21_draft25.md, byte-identical).

**BJ1, amended (wording).** In BJ1's replacement text, "(i)–(ix)" becomes "(i)–(x)". Wherever the drafts count the listed reads (for example "nine"), the count becomes ten, (i) to (x).

**BJ8 (disclosure).** In line 54, replace
`its committed run is the one at the append ("At the append of this entry").`
with
`its committed run is the one at the append ("At the append of this entry"). **(x) A read of seed 17's outcome counts, found after draft 25 (decisions.md 2026-11-13 [CORR], FILE(docs/decisions.md:4453)).** On 2026-11-12 at 17:59:38 UTC a context-pack subagent of session fdf13821 (agent-a48736828ce71b739, line 201) ran `s57_inv.py`. For every folder under `runs/`, sorted by name, the script read `config.yaml` fields, `checks.json`'s `valid` and `failed`, the `no_errors` counts `ok` (completed requests) and `unfinished` (not completed when the run stopped), and the number of files. It printed `tail -3` of that table. The last two folders are seed 17's control and its burst run, so the printed lines were most likely those two rows with both counts, plus a count line (DERIVED from the inputs, PROBE(docs/probe/20261113_transcript_search/inputs_s57_inv.txt)). Ten seconds later the subagent blanked both counts for every `w3000` folder and ran the script again. `unfinished` is counted when the run stops, so this is a read of lines a REG-19 burst run wrote after its burst began: the only one known, and listed here, not found at the append. The output was in the subagent's context. Its report to its parent was not opened, and whether anyone read the lines is not known (BELIEF either way). From the counts, that run's mean completion rate over the whole run (warm phase and burst included, not over W) and its line at the stop could be read, and so a rough r for one of batch 2's runs (DERIVED). **Timing:** the 0.05 on r of J1 and J2 was first committed with `analysis/k3w.py` at 72fafb5 (2026-11-12 19:00:16 UTC), and busy ≥ 0.99 at 3f5c84a (20:07 UTC). Both came after (x), in the autonomous agent's commits, not session fdf13821's. Reuse ≤ 0.05 was committed before (x), at d80b955 (16:19:45 UTC). The agent read the context pack of 2026-11-12 in part (FILE(agent/INGEST.md:14)); its rows for seed 17's burst run give the outcome as withheld (an owner-proxy check that printed no values). That the agent never saw the counts is BELIEF (its own report). Under the owner's plan a look before the entry is disclosed, not used as a switch (FILE(docs/drafts/plan_2026-11-13.md:41)); (x) changes no label, and BJ12's report stands beside J1.`

**BJ9 (wording: a correction).** Replace
`are also recorded by a [CORR] (FILE(docs/decisions.md:4428)).`
with
`are also recorded by a [CORR] (FILE(docs/decisions.md:4428)). That [CORR] called the `checks.json` read allowed. It is allowed for `valid` and `failed` only: if the control had ended by then, the first 300 bytes hold its client-lag p99 and its `ok` and `unfinished` counts, and whether it had ended is not known (decisions.md 2026-11-13 [CORR], FILE(docs/decisions.md:4453)). It is a control, not a burst run.`

**BJ10 (disclosure).** Replace
``extends` or `^name`; that folder was seed 17's burst run`
with
``extends` or `^name`, and at 17:56:24 UTC listed its file names again (decisions.md 2026-11-13 [CORR], FILE(docs/decisions.md:4453)); that folder was seed 17's burst run`

**BJ11 (wording, and a tag).** Two replacements in line 54.
- (a) Replace
` and no closer, so the tolerance was not fitted to it.`
with
` and no closer from the `continue` flags. Read (x) below most likely printed seed 17's burst run's `ok` and `unfinished` counts before the 0.05 on r was fixed, and a rough r for that run could have been estimated from them; whether anyone did is not known (BELIEF either way).`
- (b) Replace
`by `docs/probe/20261113_transcript_search/search.py`);`
with
`by `docs/probe/20261113_transcript_search/search.py`), nor, apart from (x) and the 17:56:24 listing in (viii), by `search2.py` as fixed after it missed scripts that name the folder as `…/runs` (decisions.md 2026-11-13 [CORR], FILE(docs/decisions.md:4453)), with every hit at or after 2026-11-11 17:15:21 UTC labelled by hand (PROBE(docs/probe/20261113_transcript_search/classify2_20261113T163634Z.txt), FILE(docs/probe/20261113_transcript_search/labels.tsv) at its entry-commit version);`

**BJ12 (reporting duty).** In "The two batches" (or the batch-2 output duties), add:
`**Seed 17 (read (x)).** The batch-2 [RESULT], and every later quote of batch 2's J1 or of its standing, names read (x). From the saved output's `per_run` r, it reports by hand the median of batch 2's judged runs with seed 17's burst run left out, its distance from 1, and whether J1's label would differ. If fewer than 3 judged runs remain, it says "undefined without seed 17". This is reported only: it changes no label and no standing (a look is not a switch, FILE(docs/drafts/plan_2026-11-13.md:41)).`

**BJ13 (disclosure, in the [DECISION] (delegate), beside BJ6).** The [DECISION] states:
- (a) the agent's reading in f3abd23 that the trigger fires on read (x);
- (b) this proxy's rejection of it, with the reason (the trigger is a completeness check at the append; (x) was listed before it, as (vi)–(ix) were; plan:41);
- (c) the timing in BJ8;
- (d) which standing batch 2 has, and, if the agent chooses "retrospective by design" anyway, that it is a choice, stricter than the rule, not the trigger;
- (e) this proxy's correction in section 1, quoted verbatim.

## 4. What later changes need another proxy pass
- BJ1 (amended) or BJ8–BJ13 written other than as given.
- Any change to line 54's trigger or to "beyond what is listed here".
- A search2 hit at the append beyond (i)–(x), BJ3's 14:09:43 command and REG-19's scripts. Line 54's rule then applies as written.
- Any use of read (x), or of BJ12's leave-out median, as a switch.

## 5. Notes for the owner
1. The real question is whether a look at seed 17's burst counts before the 0.05 was fixed should cost batch 2 its standing. Your plan says no (disclose, don't switch). The agent's own reading says yes. I followed your plan. If you think otherwise, the only cut that is blind to batch 2's J1 is an owner entry before batch 2 is computed.
2. The influence is bounded but not excluded. It concerns one rough r out of up to five. 0.05 was derived from the reference runs' spread (draft 25 line 46), and the number was already in use on another statistic before Read 1. Whether its author saw the counts is BELIEF only.
3. labels.tsv is modified in the working tree (git status) after d960ef3. The entry should cite the version at its own commit.
4. Read 2 (the control's head -c 300) bears on REG-19's verdict for seed 17's control, not on REG-21: batch 2 is burst runs only.

## 6. Not checked
- Any output: s57_inv.out, the subagent's report, the transcripts' tool results.
- The context pack beyond masked, count-only checks on its seed-17 rows.
- Which session made 3f5c84a.
- Whether the 72fafb5 author ever read fdf13821's transcripts. agent/INGEST.md names no transcript, a grep with no hit, which is not proof.
- The mtime-based dates of drafts 1–2.
- REG-22's draft 16.
- runs/ beyond names, which I did not open.
