# Owner-proxy delta pass on REG-21 draft 22 (agent a4122f052f465a926), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T12:17:25.511Z), no word changed. It saw the bundle `docs/drafts/review_bundles/reg21_r15/`. Its conditions Z1–Z2 are called AB1–AB2 elsewhere, to keep them apart from the Z rows of `agent/PLAN.md`.

---

**Decision: APPROVE**, with two wording conditions due before the entry is appended (Z1, Z2). V5 is still due later. This approves REG-21 draft 22 (FILE(docs/drafts/reg21_draft22.md)), text only, with code at `8164211`, as a delta limited to the seven items you listed.

Integrity checks:
- HEAD is `3e9c73f`.
- The bundle's drafts 21 and 22 are byte-identical to their sources, and the bundle diff equals a fresh diff.
- `git diff 8164211 HEAD` is empty for the eight judged-path files.
- `state/` holds no `reg19_final_*` file (names only).
- The shared passage, line 107 here and REG-22 draft 13's line 133, differs only in cross-references. I compared it in memory and wrote nothing.

**Reasons** (line numbers are draft 22's)

1. **X1 is met in my words (line 107).** The joining sentence is there, and the reflog list names `merge`, `cherry-pick` and fast-forward entries, each with its time.

2. **X2 as merged with N1, Y2 and W1 is accepted, but one double reading is left (Z1).**
   - **Right:** the exclusions (names, seeds, `exposed`, `lam_p`, validity flags, failed checks, checksums, "whoever prints them"). So are the end of the saving duty once a record is saved and the line-54 disclosure.
   - **Still open:** whether the list after "a value computed from what the runs measured (…):" is closed or only gives examples.
     - **Read as examples:** vLLM writes its prefix-cache hit rate into every run's harness log while the run is made. The 2026-11-12 look saw exactly such a line (RESUME.md:20). That is "printed output … to a log" of a measured value, so the first such line, during seed 15's first run on 2026-11-11, was REG-19's table and was never saved. Then there is no record and batch 2 is already lost. The text exempts only the one look at seed 17's control.
     - **Read as a closed list:** a hit rate or uncached-token rate over W that an analysis prints for a burst run before the record is not on the list. Yet it nearly fixes r, since U is the uncached part of the prompt tokens. Changes made after such a print would then count as before.
     - The two readings give opposite outcomes, and either can be chosen after the data.
   - **The fix:** keep the definition open, and say explicitly that a run's own raw data is not "output". A look at a burst run's raw data beyond `common.sh`'s allowed reads then counts as the table being read.

3. **X3 as merged with N3, W2 and Y3 is accepted (lines 107 and 113).**
   - The full statement covers runs up to the stamp and is committed after the record.
   - The early statement covers runs up to its own commit.
   - Ancestry and `%ct` against batch 2's output stamp are read from git, and with no saved output batch 2 is retrospective.
   - Line 113 names the exception to "changes no label".
   - The sentence "a run of batch 2's command made before the statement's commit … labels batch 2 retrospective" rests on a self-report. It errs only toward not governing; a false confession is inside S1's stated honesty limit.

4. **N2 is accepted (line 107).** The reflog entries dated after the stamp and a first-parent committer time earlier than its parent's now decide, with no reading.
   - On one branch with one clock, honest commits, merges, fast-forwards and plain rebases never make that chain decrease. False positives are rare, and the rule is fixed before the data.
   - A `reset` that drops a later change leaves a net diff equal to the registered path, so it offers no choice of computation.

5. **Y5 is accepted (line 104).** V2's words stand. "READY or NOT READY" and the parenthesis exempt only the statement, not the approval.

6. **Y1 is accepted (line 113).** It is stricter: the earliest known first output, else the entry commit.
   - Optional: "a value it judges" could be read to make REG-22's batch 1, which prints an uncached-token rate on the same runs, REG-21's batch-1 first run. Writing "a value that `k3w`'s functions compute" removes that reading. It errs strict and line 55 already covers REG-22's batch 1, so I leave it optional.

7. **O-4 is met.** I agree with not taking O-a: the loss it covers needs a deletion only the owner may make, and it would add a rule that reads REG-19's run folders.

**Conditions**

BEFORE the entry is appended. Use the same words in REG-22's line 133:

- **Z1 (line 107).**
  - For "(their requests, metrics or GPU samples): a verdict" write "(their requests, metrics or GPU samples), for example: a verdict".
  - After "…and `reg19_step`'s `done` and `continue`, are not REG-19's table." add: "What vLLM, the harness and the run's own recorders write while a run is made (their logs, vLLM's periodic prefix-cache hit rate among them, metric scrapes and event files, in the run folder or on the VM) is the run's raw data, not output under this bullet. A reading of a REG-19 burst run's raw data beyond the reads `common.sh` allows (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:34)), made before the record exists, counts as REG-19's table being read: the statement names it, and the rule for no record applies."
  - In "its validity flag and the checks that set it (`checks.json`", add after `checks.json`: ", with every value it or a `[run] checks` line holds".
- **Z2 (line 107; a factual correction under rule B, which needs no pass).** For "the live hit rate the agent read" write "the live hit rate the session that ran REG-19's queue read". FILE(docs/decisions.md:4279) says it was not the autonomous agent, and line 54 already says it correctly.

LATER:
- **V5** stands as stated in my draft-21 verdict.

Z1 and Z2, written as given, need no further proxy pass. The [DECISION] (delegate) names their sentences.

**Which later changes need another proxy pass**
- **Needed:**
  - everything on the earlier lists;
  - what counts as raw data and as a look (Z1);
  - what a batch's first run is (Y1);
  - the statements' coverage and timing (X3);
  - the reflog rules (N2).
- **Corrections from the parallel rule F round:** same terms as before. If in doubt, it needs one.
- **A further text-only round** needs me only if it touches that list.

**Notes for the owner**
- **Under Z1, the allowed reads during REG-19's operation now matter for REG-21:** reading a burst run's log beyond `common.sh`'s allowed reads before the record ends batch 2. Reading a control's log is a REG-19 deviation, disclosed as at line 54.
- **Pushing `main` to `origin`:** `main` is 115 commits ahead of `origin/main`. A pushed copy is the only witness to history that a local rewrite cannot alter. This is your call.
- **Line 54's "that reading is no row field of REG-19's table" is true but narrow.** A control's late hit rate bears on its `control_verdict`, which is a row field, though on no burst run. Optional rewording: "it bears on the control's verdict, not on any burst run".

**Not checked by me**
- I opened nothing under `runs/`, `state/` contents or the backups. I did not read rule F's parallel round, or REG-22 draft 13 beyond its record passage.
- I did not read vLLM's logging source. That its log carries a periodic prefix-cache hit rate is inferred from RESUME.md:20 ("live hit rate" in the harness log), not checked against the pinned vLLM.
- I did not run pytest or any analysis; the code is unchanged since `8164211`.
- The reflog is local and can be expired. The statements, an unsaved run's time and the record's file name rest on honesty before their commits.