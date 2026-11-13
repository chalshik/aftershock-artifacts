# proxy-reg21-draft23-delta (proxy-reg21-d23), verbatim

Saved by the agent from the teammate message received in the main session transcript, 2026-11-13 between 12:42 and 12:51 UTC (the senders' idle notifications). Item names as given by the reviewer (prefixes BA, BB, BC, BD, CA, CB were assigned in the review prompts).

---

Owner-proxy on REG-21 draft 23 (bundle reg21_r16): REJECT, binding for draft 23 as written. The redesign itself is accepted. A draft 24 that makes BB1–BB8 (BB1 through rule F) gets a delta pass limited to them.

Integrity checks: HEAD is e062504. The bundle's draft 23 is byte-identical to docs/drafts/reg21_draft23.md and committed. The bundle's draft 22 equals its source. `git diff 8164211 HEAD` is empty for the eight judged-path files; only c2.py, k5.py and their tests changed. No `reg19_final_*` name is in state/ (I listed names only).

WHY REJECT: the draft's own append check fails against a committed file.
- Line 49 says "U, the mean served prompt, `k1.reuse`, the busy share and r have not been computed on any run by anyone".
- Line 111 says no computation has printed "the reuse of later turns (by any function)" on a batch-1 run.
- FILE(docs/decisions.md:4084), REG-20's [REG] of 2026-11-12, contradicts both. It reports RUN(20261110-182920_burst_l1pl350cl_r2.0_s2, k1.cold_backlogged) and REG-18's four burst runs: "reuse 0.000 at the end against ≈ 1.0 before; checked as a code smoke test on reported runs".
- `cold_backlogged` calls `k1.reuse` (FILE(analysis/k1.py:80)). Its end window ends at burst end + watch (FILE(analysis/k1.py:57)), which is the end of W (DERIVED).
- Line 111's own rule then applies: "this entry is not appended as written: 'What was known' is rewritten, and the draft goes to rule F and an owner-proxy pass". An APPROVE from me would override that rule after the fact.
- What it changes is small: 0.000 against a 0.05 threshold fixed in draft 2, and line 53 already says the reuse precondition "is expected to pass". So the fix is a disclosure.
- Line 49 has stood since draft 6 at least (DERIVED: grep of drafts 6, 15 and 22). Every review missed it, my predecessors included.
- This REJECT concerns batch 1's "What was known", not the two git facts. I would not count it as a round that is NOT READY on batch 2 under the stop rule.

Q1. Would the owner accept the redesign? Yes (BELIEF, from rule A5 and the owner's preference for mechanical rules). It replaces a definition that 15 rounds could not close with two git facts that need no reading, and lines 104 and 112 state its costs. Three items are narrowed without a reason rather than retired with one:
- E1 (the cut for a validity flag or the counted seeds is "first computed or read by anyone", and the batch-2 [RESULT] gives that time). Lines 107–108 now use "the first commit that adds a reg19_final_* file", while line 186 still describes E1 as in force. The narrowing itself is right:
  - Moving the cut to the entry could end batch 2 if the owner's pending attempt-3 decision is logged after the entry.
  - A flag change after the table is caught by duty (b)'s third list.
  - final.sh stops on any changed validity (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:25–26)).
  It must still be stated (BB3).
- V5's second bullet ("any hunk called outside the path has a rule F review of that claim before the label is cited"). Line 231 keeps only V5's git facts, yet line 104 still allows hunks outside the path (BB4).
- E2's third clause ("once REG-19's table has been computed or read") rests on the term the redesign dropped (BB5).
The round-4 conditions, C1–C6, D1–D3, F1, G2 (as the new notice) and proxy-H1 (line 104, fact 2) are kept. G1, P1–P3, V1–V3, X1–X3 and AB1 correctly lose their object.

Q2. Is "disclosed, not a switch" acceptable? Yes for code and thresholds: after the entry nothing on the path moves without making batch 2 retrospective, and a retrospective batch 2 only removes a claim. It is weakest where the freeze does not reach:
- (i) Which runs batch 2 reads (validity flags, counted seeds) between a look and the first reg19_final commit. Such changes need the owner, final.sh and duty (b) limit them, and BB3 adds disclosure.
- (ii) The "outside the path" judgment, which is made by whoever already holds batch 2's output (BB4).
- (iii) A hand run of REG-19's table before the entry, or a reg19_final file deleted before it was committed. Neither can be detected; they should be stated as limits (BB8).

Q3. Is the stop rule acceptable? In direction, yes: it errs toward less claim and is fixed before the data. A retrospective batch 2 cannot promote batch 1, but only once BB6 says so. Today line 73's "batch 2 governs" and line 75's "undefined or not computed" leave that case open. The rule itself needs BB9.

Q4. AB2 and the transcript search.
- AB2 is right in substance: FILE(docs/decisions.md:4279) says "the session that ran the queue on 2026-11-12, not the autonomous agent". But line 54 cites only :4276, which does not say who.
- :4276 says only "a live hit rate". The words "with it the running batch, the waiting line and KV" rest on nothing the agent read this round: RESUME.md was not opened, and :4276 cites RESUME.md:18 where the draft cites :20–21 (BB7).
- The transcript-search statement (line 111) is not correct as offered:
  - It searched only `analysis.c2` and `analysis.k3w`, so it cannot see the :4084 print, which came from `analysis.k1`.
  - It also misses `analysis.k3` (draft 2's code, which computes an uncached-token rate, FILE(analysis/k3.py:116)) and `load.rates`' `recomputed_prefill_tok_s` (FILE(analysis/load.py:75)).
  - "PROBE: … quoted in the [DECISION]" names no file path.
  - It is dated at this draft, not at the append (BB2).

CONDITIONS, all BEFORE the entry is appended:
- BB1 (needs rule F and a proxy delta, by line 111's own rule).
  - Line 49: delete "`k1.reuse`, " and add: "`k1.reuse` has been printed: REG-20's registration reports `k1.cold_backlogged` on REG-17's burst run and REG-18's four, run on 2026-11-12 as a code smoke test, with reuse 0.000 in each run's end window against about 1.0 before (FILE(docs/decisions.md:4084)). That window ends at the end of W (DERIVED, FILE(analysis/k1.py:57)), so precondition (a) was seen to hold over part of W on five of the 13 runs."
  - Line 53: after "so it is expected to pass" add "(and was seen to pass at the end of W on five runs, above)".
  - Line 111: after "(by any function)" add "(other than the print disclosed under "What was known")".
  - Change log: name this as the agent's error (rule A6).
- BB2. Line 111: replace the search sentence with: "Before the append, a search of every Claude session transcript of this project, with no date floor, for commands, `python -c` lines and imports that run `analysis.c2`, `analysis.k3w`, `analysis.k3`, `analysis.k1` or `load.rates` on real run folders outside `pytest`; the script and its output are saved under `docs/probe/` and cited as PROBE(path) in the [DECISION] (delegate); every hit on a batch-1 or reference run is listed under "What was known". Commands run by hand outside these sessions are not covered: a limit."
- BB3.
  - Line 107: after "(a flag set before that commit is part of what that table counts and does not end batch 2)" add "; an entry after this entry's commit that changes such a flag or the counted seeds states what its author had seen of REG-19's runs".
  - Line 231: add "E1's cut becomes the first commit adding a `reg19_final_*` file, since no definition of a reading is kept; a later flag change is caught by duty (b)'s third list, and final.sh stops on any changed validity."
- BB4. Line 231 and the [DECISION]: V5 also keeps "every hunk the batch-2 [RESULT] calls outside the judged path has a rule F review of that claim, committed before batch 2's label is cited; this delays the citation and changes no label".
- BB5. The [DECISION] restates E2's third clause as "the delegate makes no change to the stopping rule after this entry is appended".
- BB6.
  - Line 75: replace "If batch 2 is undefined or not computed" with "If batch 2 is undefined, not computed or labelled retrospective".
  - Line 73: add "A batch 2 labelled retrospective is reported beside batch 1 as a second retrospective reading; it never governs, and 'disagree' and 'Batch 2's J1 inside' do not apply to it."
- BB7. Line 54: add FILE(docs/decisions.md:4279) for who read the lines. Either verify "the running batch, the waiting line and KV" together with the RESUME.md line numbers, or tag that clause BELIEF.
- BB8. Line 104: after "only a copy pushed elsewhere would witness it" add "; a hand run of REG-19's table before this entry, and a `reg19_final_*` file removed before it was committed, cannot be detected either".

LATER (before rule F round 17 is launched):
- BB9. Write the stop rule into a [DECISION] (delegate) that settles three things:
  - which rounds count: the plan says both "fixes it once" and "a third round", so pick one;
  - that only required items on batch 2's standing trigger it;
  - that a batch-1-only text gets its own rule F review and proxy pass, binding as always.

WHICH LATER CHANGES NEED ANOTHER PROXY PASS: BB1's text (a delta pass). Also any change to the two git facts, the judged-path list, the outside-the-path rule, the flag and seed cut, line 111's check, "The two batches" or the stop rule. BB2–BB8 written as given need no further pass.

NOTES FOR THE OWNER:
- The redesign trades batch 2's tolerance of bug fixes for an end to the definition churn. I believe you would take that trade.
- A REG-20 edit to a function on the path now costs batch 2, and the status.md notice is the only guard.
- Under BB9, consider dropping batch 2 from REG-21 rather than labelling it "retrospective by design". That keeps a later blind registration possible under the same two git facts.
- Pushing main stays your call. It now bears only on the entry's ancestry and time.

NOT CHECKED:
- Rule F round 16, and REG-22 draft 14 and its reviews beyond what the bundle quotes.
- RESUME.md, runs/, the contents of state/, the backups, and transcript contents. I only counted files: 66 transcript files modified since 2026-11-12, against the draft's 62; later sessions, this one included, would explain the rise.
- Whether `analysis.k3` was ever run on batch-1 runs.
- The end_s of the REG-17/18 configs.
- The reflog.
- pytest.
I wrote nothing into the repository.
