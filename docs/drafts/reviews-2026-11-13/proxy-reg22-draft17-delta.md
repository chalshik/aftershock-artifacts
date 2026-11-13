# proxy-reg22-draft17-delta (proxy-reg22-d17), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T18:08:54.915Z; message 1 of 1 from this teammate). Round 4. Item names CH1–CH11 are this round's.

---

Owner-proxy on REG-22 draft 17 (the text written under the stop): APPROVE on CH1–CH11 (CH1–CH10 BEFORE the entry is appended, CH11 LATER, in the [DECISION] (delegate)). Batch 2 stays retrospective (by design); no condition changes a threshold, code, run set or label. (Sent to team-lead because "main" resolved to my own session.)

d17 = docs/drafts/review_bundles/reg22_r12/registration_draft17.md. It is byte-identical to docs/drafts/reg22_draft17.md (`cmp`), and its sha256 e4935793… matches MANIFEST.txt. HEAD at my check is 128fd88. From 0d86f02 to HEAD no commit touches analysis/, harness/, pyproject.toml, uv.lock, .python-version, docs/decisions.md or the draft (`git diff --stat`, empty).

## 1. Round 3's owner-proxy conditions, and the departures
- **BL1(a), (b), (c), BL2(a)+BL2a(a), BL2(b)+BL2a(b), BL2(c), BL3(a), (b), (c): verbatim.** I cut each replacement text from the saved verdict and addendum by line and matched it as a string. Each occurs exactly once in d17, and each old text occurs zero times. BL1(b)'s anchor is directly followed by its insertion (DERIVED, my script).
- **BL3a:** written out as the mapping, the `names_or_validity` limit, the floor ("may replace") and the pass condition. It matches the addendum in substance. BL4 is not in the draft, as it should not be.
- **Rule F round 11's BK items: applied as the item map says.** BK1's first sentence, BK1's addendum sentence (with "(read (iii) above)"), all five of BK2's replacements (the `git log` with `--reflog` added), BK3, BK4 up to "lists these calls", BK5's sentences, BK6(a), (b) and (d), and BK7 are verbatim. BK6(c) and BK8 are merged, and their facts are kept as separate tagged sentences. I checked these as strings.
- **BK4's departure: acceptable, with CH10 (a tag).**
  - The agent's limit is real. The delegation does not cover "reading outcome data a pending registration withholds" (FILE(docs/decisions.md:4235)).
  - RESUME.md is the source the [OPS] entry cites for what seed 17's control's harness log showed (FILE(docs/decisions.md:4276), citing RESUME.md:18).
  - The consequence BK4 guards against is already in force: batch 2 is retrospective by design. The departure only leaves one disclosure to the owner, and the text says so honestly.
- **The agent's label words at lines 133–134: acceptable.**
  - They take REG-21's BJ14(d) form, with (iii) for (x), and none of them makes batch 2 primary.
  - Two sentences beside them still read as if the facts decide the label. CH2 and CH3 fix those.
  - The plan's owner-overrule route is missing; CH4 adds it.
- **The other departures: acceptable.** BK-S4's opening ("This text, written under …") is followed by the freeze's own words. BK-O1 has `|| echo not_ancestor`. BK-O2: I reproduced the test in a scratch repository. With two stash entries, `--all` printed only the newer file and `--all --reflog` printed both (DERIVED, my run).
- **The item map's "Left for the review":**
  - BL3(c)'s pointer is wrong (CH5).
  - BL3(b) and BL3a's "no read" are inconsistent (CH8).
  - Line 79, line 125, line 155 and line 130's `python`: notes only, see below.

## 2. False, or readable as a confirmatory or blind test?
- **Batch 1 is never called a test.** Line 3 calls it "the reading reported first", line 5 says "Neither is called a test below", line 67 calls it retrospective, and line a gives its standing.
- **What I found:**
  1. **Line 5 (BL1(a)): "which no analysis is known to have read" is false on the draft's own line 80.** REG-19's `analysis.gate reg19_step` read those runs after each seed. CH1.
  2. **A disclosure is dropped.** BL2(a)'s replacement removed draft 16's "the byte size of seed 16's partial metrics file while it was being copied" (REG-21's read (v); 10:14:09 UTC, classify2_20261113T163634Z.txt line 19). So line 80's "no other read … beyond … the sizes … listed above" is now incomplete. CH6.
  3. **BL3(c)'s pointer "as "About batch 2" says" names line 79.** The classes are in line 80's "Run-time lines and looks". CH5.
  4. **"whose check uses these three commands" (line 133) is inexact.** The stop entry's BK-S6 check (decisions.md:4555) has no `--reflog`. CH9.
  5. **BL3a maps `reg19_scripts` to "no read".** REG-19's own scripts read the runs by design (classify2's own docstring says "reads by design, disclosed"), and line 80 lists them. CH8.
  6. **The 17:31 UTC dry run has labels outside BL3a's mapping:** `names_in_command` on 79 hits and `disclosed[CORR]` on 1 (classify2_dryrun_20261113T173125Z.txt, line 2). Also:
     - its `disclosed(<item>)` keys carry REG-21's numbers, which REG-22's text does not use;
     - BL3a gives `names_or_validity` no class.
     As written, BL3a's own rule would force another proxy pass at E. CH8 completes the mapping and sends `names_in_command` to hand labels: a command naming a run can read its lines through a tmux pane or an ssh log read, which search2 does not parse (BK6(b)).
  7. **Present-tense "Batch 2 is primary only if …" (line 80) and "If either fact fails, batch 2 is labelled retrospective" (line 133)** can be read as "primary when the facts hold". CH2, CH3.
  8. **The trigger loops on the letter.** BK1 fixes the comparison list at draft 16, so the rerun at E will find read (iii) again. Then "this entry is not appended as written … goes to rule F and an owner-proxy pass" fires again, with no end. CH7 breaks the loop without moving the label.

## 3. The stop entry (decisions.md:4541) for REG-22: content approved
- **BK-S1, S3, S4, S5:** applied. BK-S4 is verbatim.
- **BK-S2:** applied, but its paraphrase of proxy-reg22-draft15-delta.md:160 says "fact (2) or the validity freeze". Line 160 reads "fact (1), fact (2) or the validity freeze", and draft 16 also changed fact (1) (`--full-history`). The outcome is the same: round 2 stopped.
- **BK-S6:** the commands are described rather than given, with no `--reflog`. REG-22's fact (2) is stricter, which CH9 states.
- **BK-S3's added definition** ("concerns batch 2's standing when … its consequence is batch 2's label") is narrower than item 3's scope. It has no remaining effect on REG-22, because BK-S4 says no further stop exists.
- **The entry was itself committed before its own rule F review and owner-proxy pass**, as the amendment at :4437 allows ("applied by a further entry").
- The [DECISION] discloses all of these (CH11 b).

## 4. Would the owner approve registering this? Yes, with CH1–CH11.
- It is exactly the plan's stop: "register batch 1 alone, label batch 2 retrospective by design, and stop iterating" (FILE(docs/drafts/plan_2026-11-13.md:64)). It keeps the plan's freeze, BC1 and BK-S4.
- **"Batch 1 now"** means after all of the following:
  - both entries and their [DECISION]s are committed (order (a)), or REG-21's deferral under order (b);
  - E precedes the first REG-19 table file;
  - "Before batch 1 is computed" holds.
- **Batch 2** waits for REG-19's final [RESULT] and the run comparison, not only for its table, with REG-20's gate first or the order stated.

## 5. Conditions

**CH1 (BEFORE; wording, a false statement corrected; batch 2's standing: no change).** Line 5. Anchor, replace:
`batch 2 is the same table once on REG-19's runs, which no analysis is known to have read when this entry was committed;`
with:
`batch 2 is the same table once on REG-19's runs, on which no run of `c2` is known when this entry was committed (REG-19's own per-seed computations read them: "Run-time lines and looks");`

**CH2 (BEFORE; wording, label words; standing: no change).** Line 80. Replace:
`Batch 2 is primary only if the stopping rule's facts (1) and (2) and its validity freeze hold; otherwise it is labelled retrospective, with the effects the stopping rule gives`
with:
`Batch 2 would have been primary only if the stopping rule's facts (1) and (2) and its validity freeze held; a retrospective batch 2 has the effects the stopping rule gives`
(BL1(b) stays directly after this sentence.)

**CH3 (BEFORE; wording, label words; standing: no change).** Line 133. Replace:
`If either fact fails, batch 2 is labelled retrospective: wherever`
with:
`Batch 2 is labelled retrospective whether or not the facts hold, and each fact that fails is named: wherever`

**CH4 (BEFORE; a stricter rule, the owner's own rule restated as in REG-21's BJ8; standing: no change).** Line 133. Replace:
`no review, statement, [CORR] or later commit restores primary standing.`
with:
`no review, statement, [CORR] or later commit restores primary standing; only the owner can, by an entry made before batch 1 is computed (the plan the owner approved, FILE(docs/drafts/plan_2026-11-13.md:54), FILE(docs/decisions.md:4337)).`

**CH5 (BEFORE; wording, a false pointer).** Line 81. Replace:
`each classified in the [DECISION] (delegate) as "About batch 2" says;`
with:
`each classified in the [DECISION] (delegate) as "Run-time lines and looks" says;`

**CH6 (BEFORE; a disclosure restored).** Line 80. Replace:
`at 10:14:02 `ls -la | head -30` of the control folder and a listing of its hidden files, and at 10:25:28`
with:
`at 10:14:02 `ls -la | head -30` of the control folder and a listing of its hidden files, at 10:14:09 the byte size of seed 16's partial metrics file while it was being copied (REG-21's read (v), which draft 16 listed; PROBE(docs/probe/20261113_transcript_search/classify2_20261113T163634Z.txt), line 19), and at 10:25:28`

**CH7 (BEFORE; a stricter rule, it closes a loop; standing: no change).** Line 80. Replace:
`(rule F round 11, BK1 and its addendum).`
with:
`(rule F round 11, BK1 and its addendum). Read (iii) has applied this trigger: batch 2 is labelled retrospective by design, and this text is the one the trigger sent to rule F and an owner-proxy pass (this text's own rule F review, round 12, and owner-proxy pass, quoted in the [REG] and the [DECISION] (delegate)). A read that this text lists has had that review; at E, "this entry is not appended as written" applies to a read of the trigger's kind that this text does not list, found by the rerun at E or earlier, and batch 2's label is "retrospective (by design)" either way.`
(If this text's rule F round is not numbered 12, correcting the number is wording and needs no pass.)

**CH8 (BEFORE; a stricter rule, BL3a's mapping completed and corrected).** Line 80. Replace:
`` `false_positive` and `denied_never_ran` are no read, with a note that says why; the rule labels `names_in_text`, `code_text`, `own_tools`, `reg19_scripts` and `no_run_read` are no read.``
with:
`` `false_positive` and `denied_never_ran` are no read, with a note that says why; the rule labels `names_in_text`, `code_text`, `own_tools` and `no_run_read` are no read; `reg19_scripts` is listed (REG-19's own computations, `analysis.recheck` and `vm_state.py`'s reads, named above); `names_or_validity` is listed (names and validity, named above); `disclosed[CORR]` is listed as read (i)'s 300 characters; a `disclosed(<item>)` label carries REG-21's item number and is listed under this section's read for it: REG-21's (i) and (iii) under read (i); its (ii), (iv), (v), (vii), (viii) and (ix) under read (ii) and the reads listed with it; its (vi) under A14's `analysis.recheck`; its (x) under read (iii). The rule label `names_in_command` is not in this mapping: each such hit is labelled by hand in `labels.tsv` by reading its input, because a command that names a REG-19 run can read its lines in ways `search2.py` does not parse (a terminal pane or a log read over `ssh`; rule F round 11, BK6(b)). "No read" (the input reads no run folder, no harness log or terminal pane of a run, and no note that quotes a run's lines; its note says what the input does) is a class beside the five above, and a hit in none of the six is a read beyond what is listed here (owner-proxy on draft 17, CH8).``

**CH9 (BEFORE; wording, an inexact statement).** Line 133. Replace:
`whose check uses these three commands, FILE(docs/decisions.md:4555)`
with:
`whose check uses these three commands without `--reflog`, so that this fact's `git log` can only find more, FILE(docs/decisions.md:4555)`

**CH10 (BEFORE; a tag, for BK4's departure).** Line 80. Replace:
`What the note quotes of REG-19 runs' run-time lines is not stated: the agent may not open the note under its delegation; the owner can.`
with:
`What the note quotes of REG-19 runs' run-time lines is not stated: the agent may not open the note under its delegation, which does not cover reading outcome data a pending registration withholds (FILE(docs/decisions.md:4235)), and the note is the source the [OPS] entry cites for what a REG-19 control's harness log showed (FILE(docs/decisions.md:4276)); the owner can open it.`

I applied CH1–CH10 in order to a scratch copy. Each anchor occurs exactly once in d17 and once at the moment it is applied.

**CH11 (LATER: in the [DECISION] (delegate), before the entry is appended; a reporting duty).** Anchor, line 4: `the [DECISION] (delegate) holds both owner-proxy verdicts verbatim and names, for each owner-proxy condition in force, the sentence that meets it.` The draft text is unchanged. The [DECISION] states:
- (a) **Round 3's BL4 items 1–4**, with these extensions:
  - item 2's mapping (BD9 to BH, BL) also covers BL2a, BL3a and CH1–CH11;
  - item 4's classification is done under BL3a as CH8 amends it, one line per hit with transcript file, line, label and class;
  - `labels.tsv` and classify2's output are cited at E's commit, not the working tree;
  - zero `UNLABELLED` hits and zero `names_in_command` rule labels are left.
- (b) **The stop entry (FILE(docs/decisions.md:4541)):**
  - it was committed as a delegate decision before its own rule F review and owner-proxy pass;
  - this pass approves its content for REG-22;
  - this text's rule F review on it is quoted, or the [DECISION] says it gave none;
  - BK-S2's application omits fact (1), which proxy-reg22-draft15-delta.md:160 names, and draft 16 changed fact (1) too, with the same outcome;
  - BK-S6's check has no `--reflog`, which REG-22's fact (2) adds.
- (c) **The departures from round 11's items, with this pass's ruling:**
  - BK4: accepted with CH10;
  - the label words: accepted with CH2–CH4;
  - BK-S4's opening: accepted;
  - BK-O1 and BK-O2: accepted; this pass reproduced the stash test.
- (d) **BK4's list of the calls that opened RESUME.md** (transcript and line, from rule F round 11's BK4 trace), and that what the note quotes is left to the owner. An `agent/FOR_AUTHOR.md` item asks the owner to check whether the note quotes any line a REG-19 burst run wrote after its burst began. Such a line goes into a [CORR] and changes no label.
- (e) **"Batch 1 is the reading reported first"** means only that it is computed and reported first. No REG-22 label of either batch is worded as a test, "supports", "confirms" or "passes" (FILE(docs/decisions.md:4547)).
- (f) **The order:**
  - REG-21 is registered with REG-22 (order (a)), or deferred (order (b), naming its commit);
  - no batch-1 command runs before both entries and their [DECISION]s are committed;
  - fact (2)'s three commands are run at E, and their output (expected empty) is quoted.
- (g) **BK5's list and BG-O3's list:**
  - BK5: every `ran` line importing `analysis.c2`, `analysis.k3w` or `gate`'s `reg19*` functions, each classified from its script text;
  - BG-O3: the first search's four `ran_on_reg19` hits, plus the three that rule F round 11 found (T(8c5f8396/agent-af3cd85f0f63adbb0:157), :200; T(8c5f8396/agent-aea70a41daaffaecd:119)), each classified.

## Which later changes need another proxy pass
- CH1–CH11 written other than as given, except the round number in CH7.
- Any text that makes batch 2 primary or splits it (for example seed 17 retrospective and the other seeds primary).
- Any change to BL1's texts, the trigger, BK1's sentences or CH7.
- Any change to the freeze, facts (1) and (2), the validity cut, the frozen list or the not-computed rules beyond wording or a stricter rule.
- **At E, a pass if:**
  - classify2's output has an `UNLABELLED` hit, a `names_in_command` rule label, or a label outside CH8's mapping;
  - the rerun finds a read of the trigger's kind that this text does not list;
  - a `c2` output is found on a batch-1 run;
  - `search2.py` at E differs from d960ef3 in a way that narrows what it finds.
- **Rule F round 12's items:** no pass if they are wording, a tag, a stricter rule, a reporting duty, or a disclosure that only adds. A pass if an item removes or narrows a disclosure, rewords BL1–BL3 or a CH, or is none of these.

## Notes for the owner
1. **REG-22 now has no reading on unread data.**
   - Batch 1 was always retrospective, and batch 2 is retrospective by design (read (iii)).
   - Its value is fixing the code and thresholds before REG-19's table.
   - Rule F round 11 rightly notes that this costs C2's claim its only reading of condition 4 registered before the data.
   - You can overrule BL1 only by an entry before batch 1 (your plan, :54; CH4). I would not.
2. **RESUME.md is unchecked by anyone allowed to check it** (CH11 d). Only you can open it.
3. **CH8 adds hand labels for 79 `names_in_command` hits.** That costs some agent time and buys a classification "by reading each input", as BL3(b) asks.
4. **Line 79's "Three REG-19 burst runs exist at this draft"** was true at 17:24 UTC (folder names: seeds 15–17). Seed 18's burst may exist by E; the [DECISION] names the folders at E (BG-O4).
5. **Line 125's deferral clause ("REG-21's batch 2 is no longer read blind")** is now true under REG-21's BJ8. A deferral [DECISION] could therefore let REG-22's batch 2 run before REG-21 is registered. That is harmless while both batch 2s are retrospective; left as written.
6. **Line 130 prints `python -V` and `python -c …` without `uv run`.** In this shell `python` is `.venv/bin/python`, so the check works. `uv run python …` would be stricter; optional, not a condition.
7. **Line 155's "blind order test"** is still blind to onsets: read (iii) reached end-of-run counts, not onsets (BELIEF from the [CORR]'s description).
8. **Pushing `main`** is still the only outside witness against rewritten history.

## Not checked
- Anything under runs/ beyond folder names. Nothing opened: docs/probe/**/state/, any queue_*.txt, RESUME.md, the backups, any transcript (inputs or outputs). From the classify2 outputs I read only label counts and a few records (the dry run's lines 2–30; line 19 of classify2_20261113T163634Z.txt).
- Rule F round 12 on draft 17, which I have not seen.
- The 79 `names_in_command` hits themselves. Round 3's proxy read 58 such records and found no read.
- `uv run pytest`, tools/check_docs.py, closure.py, search2.py; none was run.
- That the judged path is unchanged from 727d1f2 to ffc76b3; vLLM source; REG-21 draft 26 beyond greps.
- FILE tags beyond those I opened: decisions.md 4235, 4276, 4337, 4342, 4406, 4437, 4453, 4541–4556; plan :41–64; proxy-reg22-draft15-delta.md:160.
- I wrote nothing into the repository. My scripts and the scratch copy with CH1–CH10 applied are in /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/9fb0a805-9660-4a34-8cd0-40cdc274d7f6/scratchpad/ (ch.py, d17_with_CH.md).
