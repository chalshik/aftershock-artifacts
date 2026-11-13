# Rule F round 4 on REG-22 draft 7 (agent a7e69db175dbd3a1d), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:29:16Z), no word changed. It saw the bundle `docs/drafts/review_bundles/reg22_r4/` and the code at `ffc76b3`. Its items G1–G3 are REG-22's; they are not the owner-proxy's G1–G2 on REG-21.

---

Rule F review of REG-22, draft 7 (round 4): NOT READY

F1, F3, F4, F5, F6 and F7 are fixed. Three items remain, all text:
- **G1 (the rest of F2).** Line 36 still says "So `loop` means 'no span re-warmed for most of its length'". Line 8 now calls that same sentence false.
- **G2 (looser than draft 6).** The freeze checks only the diff from the batch-1 commit to the batch-2 commit. A judged-path change made after REG-19's table is public, but before batch 1, now passes. Draft 6's freeze would have caught it once REG-19's result heading existed.
- **G3 (the record).** "The record is the first such pair … with its commit, which adds those two files and nothing else" has two readings. Under one of them the cut can move later.

The record rule is otherwise sound. The code is unchanged: `git diff ffc76b3 HEAD -- analysis harness tests` is empty at HEAD `72d4884`.

"Line N" means a line of `registration_draft7.md` in `docs/drafts/review_bundles/reg22_r4/`. Code citations are at `ffc76b3` unless stated otherwise.

## 1. Round 3's F1–F7

- **F1: FIXED** (lines 21, 85, 100, 120, 156).
  - The run-level reading is no longer said to answer A19. Line 21 says why `plan_order_beyond_lags` cannot occur.
  - Line 100 lists, per run, the readings of the pairs (reuse, N) and (reuse, KV) with their `dt_s` (c2.py:357 prints them), with no tally. `not_distinguishable_from_simultaneous` is quoted as "no pair reversed".
  - Alternative 7 adds the reuse's own lateness when session turns get no first token. That is right: in round 3's t03 C and C2, the reuse's onset was 1090 s in both runs.
  - Remaining issue: line 120 says the condition under which the pairs bear on A19 is not computed, so REG-22 in effect leaves A19 open. Lines 21 and 156 do not say so (optional 1).
- **F2: PARTLY.** Line 8 is fixed. Line 36's last sentence is unchanged (the draft 6 → 7 diff has no hunk at line 36), and line 180 reports F2 as met in line 8 only. See G1.
- **F3: FIXED** (lines 92, 101, 102). It is stricter than round 3's text. Checked cases:
  - Batch 1 meets line a and batch 2 is mixed (it meets none of a, d's KV clause or e): they disagree, and the status claims neither. Line 102 now defers to line 101, so the two lines agree.
  - Batch 2 is not computed, or has fewer than 3 stuck runs: batch 1's sentence stands, with the reason beside it (lines 92, 101).
  - Both batches meet line a: both counts are given side by side, and nothing is summed across them.
- **F4: FIXED** (line 124 as given; line 128 "after order (a) or (b) above holds").
- **F5: FIXED as asked** (line 132 freezes `onsets`, `onset_reading`, `planned_rates`, `control_readout`, `reported_counts` and `__main__`). The interval it freezes is too short: G2.
- **F6: FIXED** (lines 11, 83, 84). The arithmetic reproduces:
  - 1 − 0.9959⁹ = 0.036;
  - 3 × 0.036² × 0.964 + 0.036³ = 0.0038;
  - 3 × 0.29² × 0.71 + 0.29³ = 0.204;
  - 0.42 × 0.0038 = 0.0016 and 0.42 × 0.204 = 0.086;
  - 1 − 0.05 − 0.09 = 0.86.
- **F7: FIXED** (line 56: c2.py:387 is the `"runs"` tuple).

**Optional items taken: all verified.**
- 1: line 91, against c2.py:376.
- 2: line 52.
- 3: line 12.
- 4: line 75, against margin.py:61.
- 7: lines 132 and 144.
- 8: line 78, against k3w.py:96, 169 and 198. `_gauges` gives running, waiting, KV and preemptions inside `readouts`, over W.
- 9: decisions.md:2316–2318, 2840–2842 and 3546–3548 hold exactly the ranges stated:
  - KV 0.950–0.951, N 29.8–31.0 and waiting 169.4–247.7, with "yes" in all three rows;
  - KV 0.948–0.952 and waiting 116–177;
  - KV 0.948–0.951.
- 10: line 151, against k1.py:69.
- 11: line 100.
- 12: lines 97 and 117, against load.py:25.
- 13: line 92.
- 6 and 14 are stated as limits (lines 109 and 136).
- 5 not taken: its consequence is stated in line 64. That is acceptable.

## 2. The code

- **No code changed.** `git diff ffc76b3 HEAD -- analysis harness tests` is empty. Round 3's traces t01–t06 stand: the judged path equals 727d1f2's, and no readout touches a label.
- **The draft's new claims about code hold:**
  - c2.py:376 uses the own-baseline flag;
  - c2.py:443 calls `reported_counts` outside any `try`;
  - per-span burst-baseline flags are printed (c2.py:311–317).
- **"A run that raised printed no table" (line 133) holds at REG-19's pin.** In `git show a7bb77a:analysis/gate.py`, `__main__` is `print({…"reg19": reg19_table…}[sys.argv[1]]())`. No other print to stdout sits on that path; the others are in `__main__` blocks.
- **The bundle's `final.sh` copy is the committed file.** Its blob hash equals `git rev-parse HEAD:docs/probe/20261113_reg19/ops_r3/final.sh` (4555b3f). The citations final.sh:20 (the stamp and the two file names) and final.sh:31 (a second try needs the file set aside by hand) resolve.
- **agent/theory/k1_held_prefix.md:21–22** give R_M ≈ 64 s warm and ≈ 0.9 s cold, as line 110 says. Line 110 tags them "not reviewed".

## 3. The text

**Q2: is anything looser than draft 5 or 6?** One thing is (G2). Everything else is equal or stricter:
- the cut (the record's stamp, before REG-19's heading) replaces "after REG-19's result heading";
- line 64 now treats "no record" as "not computed", and a validity flag set before the cut counts as part of REG-19's table;
- lines 101 and 102 are stricter;
- line 100 has no tally;
- line 136 adds "not computed" if `reported_counts` raises;
- the claims in lines 21 and 85 are weaker.

**Q3: is the record rule sound for REG-22?** Mostly.
- **What holds:**
  - The cut is final.sh's stamp, taken (final.sh:20) before the recheck (:25) and the table command (:29), so it errs early. A change counts as before the cut only if it is a strict ancestor of the record's commit with an earlier committer time. A change made after the stamp, or off the record's branch, therefore counts as after.
  - final.sh refuses a second try while a table file exists (final.sh:18–19).
- **What fails:**
  - G3: which saved pair is the record.
  - G2: the cut is not applied between this entry and batch 1.
  - Optional 4 and 5: the stamp's wording, and rewritten history.

**Q4: is anything else wrong?** These checks found nothing:
- the checks of line 11, lines 83–85 and lines 91–102;
- line 124 against line 128;
- line 136 against lines 64 and 134 (only optional 2 there);
- line 142, lines 151 and 156, and the review list (lines 165–181).

**G1 trace.** In round 3's t04, the cache back for 240 of 300 s gives `loop`. Line 8 (fixed) says that span is let through. Line 36 still concludes "no span re-warmed for most of its length".

**G2 trace.**
- R: this entry is committed, before the cut.
- Rec: REG-19's record is committed, cut T.
- X: after T, batch 1's command raises, and a fix to `c2.links` is made with rule F and an owner-proxy pass (line 135 allows this).
- B1: batch 1 runs at X. B2: batch 2.
- The checks then pass:
  - Line 144 checks 727d1f2 → R: empty.
  - Line 132 checks B1 → B2: empty.
  - Line 133: R is before the cut.
- Batch 2 keeps "registered before REG-19's table", though its labels come from a judged path changed with REG-19's table public.
- Draft 6's sentence ("A change to anything `reg22_table` reaches … made after REG-19's result heading exists also labels batch 2 retrospective") was not limited to the batch-1 → batch-2 diff. It would have caught X once the heading existed.
- **Plausibility:** batch 1 waits for REG-21's registration (order a), which is in its eleventh review round, while REG-19 lacks only seeds 18 and 19. So batch 1 after the cut is plausible.

**G3 trace.**
- Pair P1 (stamp T1) holds the table and is committed in one commit with an [OPS] entry.
- P1 is set aside by hand, and final.sh runs again (allowed once no `reg19_final_*` file is present), giving P2 (stamp T2 > T1), which is committed alone.
- Line 133 can be read two ways:
  - as describing the first pair's commit: then there is no record, and batch 2 is not computed;
  - as filtering pairs: then P2 is the record and the cut moves to T2.
- Under the second reading, a change committed in (T1, T2), with the table known, counts as before the cut.

## 4. Verdict: NOT READY

### REQUIRED

- **G1 (line 36; also line 180).**
  - In line 36, for "So `loop` means "no span re-warmed for most of its length", at 300 s resolution." write: "So `loop` excludes a span with the cache back for more than about 240 of its 300 s, or with a full recovery of more than about 70 s, at 300 s resolution."
  - In line 180, write "F2 in the first bullet of 'What it can and cannot show' and in the last sentence of 'What a link's threshold lets through'".
- **G2 (lines 132, 144, 148).**
  - In line 132, replace "Between the batches" with "From this entry to batch 2", and "between the batch-1 and batch-2 commits" with "between this entry's commit and the batch-2 commit".
  - Replace "Otherwise: a change made before the record's cut (below) needs rule F and an owner-proxy pass first, and the batch-2 [RESULT] says the change was made knowing batch 1; any other change labels batch 2 retrospective" with: "Otherwise: a hunk whose commit is before the record's cut (below) needs rule F and an owner-proxy pass first (before batch 1, a reported-only readout whose diff rule F has seen needs no proxy pass), and the batch-2 [RESULT] says whether it was made knowing batch 1; any other hunk, before or after batch 1, labels batch 2 retrospective".
  - In line 148, add: "shows `git diff` from this entry's commit to the batch-1 commit for the files of line 132, and the review each hunk had".
- **G3 (line 133).** For "The record is the first such pair whose stdout holds the table, with its commit, which adds those two files and nothing else;" write: "The record is the first saved pair whose stdout holds the table. If that pair is not committed, or its commit adds anything besides those two files, there is no record: no later pair becomes the record, and batch 2 is not computed ('Runs');".

### OPTIONAL

1. **Lines 21 and 156.** Add: "REG-22 does not compute where this holds (line 120), so it leaves A19 open." Line 120's condition (at least 20 later turns in every trailing 60 s window through the burst) is narrower than "kept getting first tokens".
2. **Lines 64 and 134.** Line 136 makes batch 2 "not computed" if `reported_counts` raises. Add that case to line 64's list, so that line 134 can name it.
3. **Order (b) and (c) (lines 124–125).**
   - Define "after REG-22's batch-1 table exists" and "after that table exists" by the record's test: strict ancestor of the batch-1 output's commit, and a committer time earlier than the start time in its file name (line 130).
   - Require that output to be committed alone, as the record is.
4. **Line 133.** Say "the stamp final.sh takes before its recheck (final.sh:20)" instead of "the UTC time at which the command was started". It is a little earlier, which errs on the safe side.
5. **Line 133.** Add: "no commit from this entry to batch 2 is amended or rebased, and no committer date is set by hand; a rewritten commit counts as after the cut". The test trusts committer times and an unrewritten history.
6. **Line 79.** Date "Three REG-19 burst runs exist today", for example "at draft 7, 2026-11-13".

### Can it change a decision?

Yes, as in round 3, with draft 7's numbers. Batch 2's line e (`not_sustained` in more than half, n ≥ 3) changes the confirmation run's registration. The probability is about 0.002 at the forecast and up to about 0.09 at the pessimistic end (line 11, reproduced). Batch 1 changes no decision in its likeliest outcome. It should run after G1–G3, at 0 GPU h.

## 5. What I could not check

- **Not opened, as instructed:**
  - `runs/` and the backups;
  - any `state/reg19_*` file and any probe output;
  - `docs/probe/20261113_reg19/ops_r3/common.sh`.
  So I could not check that `stamp` writes UTC, or that `$ST` is inside the repo and committed. The file names visible in `git diff --stat` end in "Z", which is consistent with UTC, but that is BELIEF.
- **REG-21 draft 17** was not read, so I could not check that its record rule uses the same words ("the same as REG-21's", line 133), nor the mirror of order (b).
- **Line 79** ("three REG-19 burst runs exist today") is still unverified.
- **Round 3's traces were not re-run.** The code is unchanged, so they stand as recorded in `docs/drafts/reviews-2026-11-13/rulef-reg22-draft5-r3.md` (scripts in /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r3_scratch/).

