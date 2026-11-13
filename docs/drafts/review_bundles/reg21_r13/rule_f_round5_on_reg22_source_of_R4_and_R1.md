# Rule F round 5 on REG-22 draft 10 (agent a7e69db175dbd3a1d), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:40:47Z), no word changed. It was asked first for draft 9 and then, by addendum, for draft 10; it reviewed draft 10. Its items R1–R4 are REG-22's, not rule F round 7's R1–R5 on REG-21.

---

Rule F review of REG-22, draft 10 (round 5): NOT READY

G1 and G2 are fixed. On G3, I agree with taking K3: I withdraw the second clause of my round-4 G3 (see 3.1).

Draft 10 has four new defects, all text only. Each has two readings with opposite outcomes, or it loosens an approved condition:
- **R1:** the consequence for a missing citation (the owner-proxy's Q7) no longer covers committer times. That is looser than draft 9.
- **R2:** line 133 adds a "not computed" case that line 64's list, which says it is complete, does not hold.
- **R3:** line 124 still has the "committed at once and alone" test that K3 removed from the record. My round-4 optional 3 put it there.
- **R4:** "any output … from any checkout" also covers outputs on synthetic folders.

Line numbers below are those of `docs/drafts/review_bundles/reg22_r5/registration_draft10.md`.

**Copies checked.** The bundle copies of drafts 9 and 10 are byte-identical to `docs/drafts/reg22_draft9.md` and `reg22_draft10.md`. Both bundle diffs equal a fresh `diff`. The draft-7 copy is the one I reviewed in round 4.

**Code unchanged.** HEAD is now `2bf6a90`, one docs-only commit after `4ad587d`. `git diff ffc76b3 HEAD -- analysis harness tests configs pyproject.toml uv.lock` is empty.

## 1. Round-4 items and the owner-proxy's Q1–Q7

**G1–G3**
- **G1: FIXED** at line 36, in my F2 wording. Line 182 records it, so line 180 no longer needs changing.
- **G2: FIXED.**
  - Line 132 freezes from this entry's commit to the batch-2 commit.
  - A hunk not made before the cut, before or after batch 1, labels batch 2 retrospective.
  - Line 148 makes the batch-1 [RESULT] show the diff from this entry to batch 1, with each hunk's review.
  - My round-4 trace (a fix to `c2.links` after the cut, before batch 1) now labels batch 2 retrospective.
- **G3: superseded by K3.** I agree with the change (3.1).

**Q1–Q7**
- **Q1: holds** (line 36).
- **Q2: holds** (line 101). The fewer-than-3 case now gives batch 2's per-run labels, and the line states that it settles draft 6's contradiction before any batch-2 data.
- **Q3: holds** (line 101). Line e is not suspended when the batches disagree. That is right, because e only requires reading more.
- **Q4: partly.**
  - The fact about exposed seeds holds: `exposed` is fixed from the control's planned schedule before any run (FILE(analysis/gate.py:1811–1819), "Schedule only, fixed before any run"), and FILE(docs/decisions.md:3788) says no control reaches 3.2 (highest 3.092).
  - The `reported_counts` case is listed.
  - But line 64 is no longer "complete in one place": see R2.
- **Q5: holds** (line 124, last sentence).
- **Q6: holds** (line 11). 0.6 × 0.7 × 0.004 = 0.00168; 0.6 × 0.7 × 0.20 = 0.084; 1 − 0.05 − 0.084 = 0.866 ≈ 0.87. Line 84 states the factors without the product, so there is no inconsistency.
- **Q7: partly.** Draft 9's "if any part is missing" became a shorter list that leaves out the committer times: see R1.

**Round-4 optional items 1 and 3–6**
- **1** (lines 21, 120, 156): taken.
- **3** (line 124): taken, but it carries G3's flaw (R3).
- **4** (line 133, the stamp is no later than the start): verified. final.sh stamps at final.sh:20, before the recheck at :25 and the table at :29. `stamp` is `date -u +%Y%m%dT%H%M%SZ_<pid>_<n>` (common.sh:40).
- **5** (no rewritten history): taken.
- **6** (line 79, dated): taken.

## 2. The code

No code has changed since `ffc76b3`, so the round-3 traces t01–t06 still hold. The citations in the new record passage resolve:

| Claim | Where |
|---|---|
| `gate.py` is identical at the pin and at `ffc76b3`, so what final.sh runs is what line 133 cites | `git diff --stat a7bb77a ffc76b3 -- analysis/gate.py` is empty |
| `__main__` makes one `print` per branch, after the function returns, so a raise prints nothing | FILE(analysis/gate.py:2107) |
| `reg19_table` returns `seeds_run` and `excluded` (from `reg18_outcome`), and rows whose keys include `runs`, so line 133's seed check can be computed from the record | FILE(analysis/gate.py:1700), FILE(analysis/gate.py:2055–2056) |
| `ST` is the absolute path `$R/docs/probe/20261113_reg19/ops_r3/state`, so final.sh writes the record into this repo even though the table runs in the worktree. This settles the owner-proxy's open point. | common.sh:6–8; final.sh:20, :29 |
| final.sh's glob also matches the stderr file, so "set aside" must move both files | final.sh:18 |
| Commits on this Mac carry +0600 | `git log -3 --format=%ci` |

## 3. The text

### 3.1 K3 against my G3: I agree with K3, and withdraw G3's second clause

My G3 said "or its commit adds anything besides those two files, there is no record". That handed a lever to whoever commits the record, after REG-19's table is on screen.

**Trace under G3:**
- final.sh stamps 12:00Z.
- The record is committed at 12:40Z together with `agent/STATE.md` and `docs/status.md`. REG-21's round 11 reports this as the repo's habit for state files (b0ff529, 69f349b, c38388b); I did not re-check those commits.
- Under G3 there is then no record, and batch 2 is not computed. One innocent commit, or one deliberate extra file, decides whether batch 2 exists.

**Under K3:**
- The record stands, and the cut stays at 12:00Z.
- The other files in that commit count as after the cut.
- Nothing is loosened. The cut is the stamp, so the content or timing of the commit cannot move it.
- The strict-ancestor rule already counted "a change in the record's own commit" as after, so G3's purity condition did no work except to create the lever.

I missed this in round 4. Log it as my error, not the coordinator's.

**What K3 keeps:** an unsaved or uncommitted first run means no record, and no later run takes its place. Not committing the record is still a way to end batch 2, but it is a visible omission that is reported as the reason, not a habit.

**Other K3 checks found no new loosening:**
- a late commit;
- a merge as the record's commit, given honest committer times;
- a first pair holding the table that is set aside by mistake: it is still the record, and line 133 lists every `reg19_final_*` file;
- a later pair: it never becomes the record.

**The mid-matrix rule (K2) is stricter.** Any run of `analysis.gate reg19` on REG-19's folders before the matrix ends now ends batch 2. That is decided before REG-19's final data, so it is no lever. Using the mid-matrix stamp as the cut instead would also have been sound; I do not contest the choice.

### 3.2 R1: a missing committer time no longer labels batch 2 retrospective (looser than draft 9)

- **Draft 9** (line 133): the [RESULT] cites the record's commit, file name, ancestry check "and both committer times …; if any part is missing, batch 2 is labelled retrospective". That is the owner-proxy's Q7 as approved.
- **Draft 10** (line 133): it cites those, plus the list of `reg19_final_*` files and a statement. But the consequence names only "the record's file name, its commit or the ancestry check".
- **Trace:** a batch-2 [RESULT] gives the ancestry checks without `%ct`. The ancestry check alone does not establish "before the cut", which also needs the time. Under draft 10, batch 2 keeps "registered before REG-19's table"; under draft 9 it was retrospective.
- **The file list matters too.** Without it, an earlier pair that held the table and was set aside is invisible, and the record could be taken to be a later pair.

### 3.3 R2: the mid-matrix case is missing from line 64's list

- Line 133 says that if the record's seeds are not those REG-19's final [RESULT] counts, "the comparison under 'Runs' differs and batch 2 is not computed".
- Line 64's comparison is a different one: the valid batch-2 folders against the seeds in n "as REG-19's final [RESULT] reports it". Line 64 also says its list is "complete in one place" (Q4).
- **Trace:**
  - A record with `seeds_run` [15, 16, 17] is stamped at T0.
  - REG-19's final [RESULT] counts 15–19, and the folders match it.
  - Line 64's comparison passes, and nothing in its list applies.
  - Reading 1 (line 133): batch 2 is not computed.
  - Reading 2 (line 64 is complete): batch 2 is computed with cut T0.
- These are opposite outcomes, chosen after REG-19's table. Adding a "not computed" case needs no new proxy pass, by the owner-proxy's own list.

### 3.4 R3: line 124 keeps the construct K3 removed (my round-4 optional 3)

- Line 124's test: "a strict ancestor of the commit that adds that batch's saved output, committed at once and alone". Line 130 does not require the batch output to be committed alone.
- **Trace (order b used):**
  - The deferral [DECISION] fixes REG-21 at commit D.
  - X, a reviewed change to a REG-21 threshold, is committed at 10:00Z.
  - REG-22's batch 1 starts at 11:00Z.
  - Its output is committed at 11:30Z together with the [RESULT] entry.
  - Reading A ("alone" is a condition): no commit qualifies, so X cannot count as before. X is A5, and REG-21's batch 1 loses its labels.
  - Reading B ("alone" is a duty): X counts as before, and the labels stay.
- These are opposite outcomes. Whoever commits REG-22's batch-1 output, after seeing it, can void REG-21's labels with one extra file. This is the same lever K3 removed from the record.
- It touches an order rule, so by the owner-proxy's list it needs a proxy pass.

### 3.5 R4: "any output … from any checkout" also covers synthetic folders

- Line 133: "'REG-19's table' is any output of `analysis.gate reg19` whose `seeds_run` is not empty, from any checkout". The record is "the first run that gave REG-19's table", and an unsaved or uncommitted first run means no record. Nothing restricts this to REG-19's real folders or to runs after this entry.
- `docs/probe/20261113_reg19/ops_r3/test_sandbox.sh` exists. I saw its name only and did not read it. The status speaks of a sandbox (160 of 160).
- **Trace:**
  - If that sandbox, or any test, ran `analysis.gate reg19` on synthetic REG-19 folders, it printed a non-empty `seeds_run`.
  - Read literally, that was the first run that gave "REG-19's table". It was never committed, so there is no record and batch 2 is not computed.
  - The intended reading (REG-19's real runs only) computes batch 2. A reader picks one after REG-19's table.
- After this entry the same words also oblige a sandbox rerun to save into the real `state/`. That would make final.sh refuse (final.sh:18–19).
- It touches the record definition, so it needs a proxy pass.

### 3.6 Other checks, with no defect found

- **Q2 (anything looser?).** Against draft 9, R1 is the only loosening. Against draft 6, I found none: the cut is the stamp and comes before REG-19's heading in the normal order, and the freeze now starts at this entry.
- **Stricter or neutral:**
  - "compared as instants", with a commit in the same second counting as after;
  - the hand run's `date -u` in the same command line;
  - "set aside" defined as moving both files;
  - the full path;
  - the [RESULT] statement about earlier runs.
- **The stamp-after-commit breach** ("reported the same way") is a small hole; see optional O1.

## 4. Verdict: NOT READY

### REQUIRED (text only)

**R1 (line 133).** Replace "if the record's file name, its commit or the ancestry check is missing, batch 2 is labelled retrospective." with:

"if any of these is missing (the record's file name, its commit hash, an ancestry check, a committer time, the list of `reg19_final_*` files or the statement), batch 2 is labelled retrospective."

**R2 (lines 64 and 133).**
- In line 64, after "REG-19's table is computed or read and no record is made" insert:

  "; the record's output (`rows[].runs` and `excluded`) does not hold the seeds that REG-19's final [RESULT] counts (a record from the middle of the matrix, under "Stopping rule")"
- In line 133, replace "the comparison under "Runs" differs and batch 2 is not computed" with:

  "batch 2 is not computed (a case listed under "Runs")"

**R3 (lines 124 and 130).**
- In line 124, replace "a change counts as made before the table exists only if its commit is a strict ancestor of the commit that adds that batch's saved output, committed at once and alone, and its committer time is earlier than the UTC start time in that file's name, compared as instants." with:

  "a change counts as made before the table exists only if its commit is a strict ancestor of the first commit that adds that batch's saved output (line 130) and its committer time is earlier than the UTC start time in that file's name, compared as instants. That output is committed at once and alone; one committed late or with other changes still counts, the breach is reported, and every other change in that commit counts as after."
- In line 130, after "whose name carries the UTC time at which the command was started" add:

  ", committed at once and alone"

**R4 (line 133).** After "a run made in the middle of the matrix counts, and so does one from the pinned worktree, which has no seal." insert:

"Only output computed on REG-19's own run folders counts (this repo's `runs/`, or the pinned worktree's links to them); output on synthetic folders (tests, the scripts' sandbox) is not REG-19's table, and the saving duty below does not apply to it."

**Proxy passes.** By the owner-proxy's list, R3, R4 and K3 itself (a change to the record's definition) need an owner-proxy pass. R1 restores the owner-proxy's own Q7. R2 adds a "not computed" case.

### OPTIONAL

- **O1 (line 133), a stamp later than the record commit.** Replace "A stamp later than the record commit's committer time is a breach too, reported the same way." with: "A stamp later than the record commit's committer time is a breach too: the true start is then unknown, and batch 2 is labelled retrospective."
  - Trace: a hand run starts at 12:00Z; the stamp reads 12:30Z; the record is committed at 12:20Z; X is committed at 12:10Z as an ancestor.
  - X counts as before (12:10 < 12:30) although the table existed at 12:00. A cut clamped to the commit time (12:20) still lets X through, so only the label helps.
- **O2 (line 132), a pre-cut hunk without review.** Line 132 says such a hunk "needs" rule F and an owner-proxy pass but gives no consequence. Add "; without both it labels batch 2 retrospective". Also require the batch-2 [RESULT] to list each hunk with its commit, its `%ct` against the cut and its reviews, as line 148 does for batch 1.
- **O3 (line 21), repeated condition.** Line 21 states the 20-turn condition twice (fourth and last sentences); keep one.

### Can it change a decision?

Unchanged from round 4:
- Batch 2's line e (`not_sustained` in more than half, n ≥ 3) changes the confirmation run's registration, at P ≈ 0.0017 at the forecast and up to 0.084 at the pessimistic end (line 11, reproduced).
- Batch 1, at P ≈ 0.05 (BELIEF), changes no decision in its likeliest outcome.
- Both batches cost 0 GPU h.

## 5. What I could not check

- **Not opened, as instructed:** `runs/`, the backups, any `state/reg19_*` file, and any probe output.
- **`test_sandbox.sh`:** I did not read it, so I cannot say whether it ran `analysis.gate reg19`. R4 is required either way, because it is one clause.
- **REG-21 draft 19's record passage:** I did not read it (outside my bundle), so "the same as REG-21's" is unverified. REG-21 says "duty (b)'s lists" where REG-22 says "Runs", so the words must differ there. R2, R3 and R4 may need mirrors in REG-21.
- **Whether anyone has already run `analysis.gate reg19`** on REG-19's real folders (in the pinned worktree, or on main with `AFTERSHOCK_UNSEAL=REG-19`, which `withheld.py:51` honours). If so, batch 2 is already not computed under line 133.
- **The repo's habit of committing state files with other files** (b0ff529, 69f349b, c38388b): taken from REG-21's round 11, not re-checked.
- **Round 3's traces t01–t06** were not re-run; the code is unchanged. Scripts and outputs are in /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg22_r3_scratch/. Nothing was written into the repo.

