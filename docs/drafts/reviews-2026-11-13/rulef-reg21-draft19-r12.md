# Rule F round 12 on REG-21 draft 19 (agent a0adfd0cddd98f5fb), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:41:00Z), no word changed. It saw the bundle `docs/drafts/review_bundles/reg21_r12/` and the code at `8164211`.

---

REG-21 draft 19, round-12 adversarial review (rule F): NOT READY

K1, K2 and K3 are fixed, and nothing in draft 19 lets a batch govern that draft 17 would not. G2, the replacement of G3 by K3, and the folder-list change all hold. Two items are still required, both text only. Each gives someone a choice, made after seeing data, that moves batch 2 between governing and not:
- **L1 (line 107).** The new citation sentence makes batch 2 retrospective if the [RESULT] leaves a citation out. The [RESULT] is written with batch 2's own output in hand, so its writer could demote batch 2 by leaving one out. The same sentence also contradicts the bullet's own rule for "no record".
- **L2 (line 104, reach widened by G2).** A judged-path change made before the cut keeps batch 2 only if rule F and the owner-proxy review it "before batch 2". The delegate can decide whether to ask for those reviews after REG-19's table is public. This route has existed since draft 15, and I missed it in rounds 9–11; please log it as my error. Draft 19's freeze from the entry now applies it to every change between the entry and batch 1.

Both items touch line 104's route or a label rule, so they need an owner-proxy pass.

How I worked (same limits as before):
- **Nothing withheld opened.** I opened nothing under `runs/`, the backups, any `state/reg19_*` file or any probe output.
- **Repo state.** HEAD is `2bf6a90`. Since `8164211` only `c2.py`, `k5.py` and their tests have changed. The judged path, `gate.py`, `harness/` and `configs/` are unchanged.
- **Bundle copies.**
  - The bundle diff equals a fresh `diff`.
  - Draft 19 is byte-identical to `docs/drafts/reg21_draft19.md`, and the draft-17 copy is the one I reviewed.
  - `final.sh`, `common.sh` and `delegation.md` equal their sources.
  - The round-11 copy equals `rulef-reg21-draft17-r11.md`, and the three newly cited review files exist.
- **Code read.** I read `withheld.py` and `batch2_runs` at `8164211`.
- Line numbers below are draft 19's.

**1. Round 11's items**

1. **K1, an unsaved earlier run: fixed.** Line 107 now says: "There is no record if the first run that gave REG-19's table was not saved …; a later saved run does not take its place."
2. **K2, a run from the middle of the matrix: fixed.** Any output with a non-empty `seeds_run` counts, "from any checkout and however many of REG-19's seeds it holds" (line 107). The line-112 notice says "at any point of the matrix". I checked:
   - the pin `a7bb77a` has no `withheld.py`;
   - `AFTERSHOCK_UNSEAL=REG-19` also lifts the seal on `main` (FILE(analysis/withheld.py:51), FILE(analysis/withheld.py:57)), and "any checkout" covers that;
   - `batch2_runs` checks the heading alone (FILE(analysis/k3w.py:345)), so that variable cannot start batch 2 early.
3. **K3, "alone, nothing else": fixed.** A record committed late, without its stderr file or with other changes is still the record. Every other change in its commit counts as after the cut. Nothing in the rule text still voids a record.
4. **Optional items, all taken:**
   - O1 (hand stamp);
   - O2, through proxy-H1's `%ct` instants;
   - O3 (the notice in the append commit);
   - O4 ("set aside" moves both files; FILE(docs/probe/20261113_reg19/ops_r3/final.sh:18) is the glob);
   - O5 (the full path).

   One check for O3 and O4: the record's own commit is always after the cut by the time test alone, because its file exists only after the stamp, and a commit in the same second counts as after. So `git merge-base --is-ancestor`, which also returns true when the two commits are the same, does no harm here.

**2. Findings**

**L1. Line 107: "if the record's file name, its commit or the ancestry check is missing, batch 2 is labelled retrospective". Required.**
- **Inputs.** Batch 2 is computed, and its output is saved and committed before any reading is written (line 113). The writer of the batch-2 [RESULT] then knows batch 2's r and its J1 label.
- **What the text says.** "Missing" most naturally means missing from the [RESULT]: an ancestry check is always possible in git, so it can only be missing from the text.
  - The writer cites everything, and batch 2 governs.
  - The writer leaves out the ancestry check, and batch 2 is retrospective.
  - If a later [CORR] can add the check, whether to write it is again the writer's choice.
- **What should happen.** These are facts in git that anyone can check. This sentence was added in draft 18 from REG-22's proxy (Q7), and it is the same kind of choice K3 removed: one made after seeing the data. Line 84 already treats a misquote this way: a [CORR] corrects it, and it is never read as a mismatch.
- **It also contradicts the bullet.** Read as facts, "its commit is missing" means no commit adds the record's file. The same bullet calls that "no record", so batch 2 is not computed, while this sentence says retrospective.
- **Small wording issue in the same bullet.** "Not saved under its start time" fits `final.sh` only loosely: its stamp is taken before the recheck (`final.sh:20`, `:25`), not when `analysis.gate reg19` starts. The passage itself approves that stamp, so the reading that voids `final.sh`'s file is weak. It costs one phrase to close.

**L2. Line 104's exception: the reviews of a change made before the cut may be asked for after the cut. Required.**
- **Inputs.**
  - At T0, before the cut, REG-20's work changes `k1.windows`, with no review for REG-21. G2's notice expects such changes (line 112).
  - At T1, `final.sh` runs and makes the record. Every batch-2 run's `c` is now public, and with it r's first factor (lines 51 and 55).
- **What the text says (line 104).** "Rule F and an owner-proxy pass on it then come before batch 2, or batch 2 is labelled retrospective."
- **What actually happens.** The delegate decides after T1 whether to ask for the two reviews:
  - asked for and approved, batch 2 governs;
  - not asked for, batch 2 is retrospective.
  - The reviewers also work with REG-19's table public.
- **Why it matters.** "What was known" sets the principle that whether batch 2 governs is not settled with REG-19's table public, and this route breaks it.
- **What draft 19 changed.**
  - In draft 17, the freeze ran only from batch 1 to batch 2, so a change between the entry and batch 1 governed with no review.
  - Draft 19 is stricter: such a change now needs a review.
  - But the review can be asked for after the cut, so this route now covers every change from the entry on.

**Is anything looser than draft 17?** No rule lets a batch govern that draft 17 would not. Checked:
- **Line 107:**
  - "a UTC time taken no later than the command's start" can only move the cut earlier, which is stricter for lines 54, 55 and 104 and for the flag rule;
  - the instants and the rule that a commit in the same second counts as after;
  - the ban on rewriting history.
- **Line 104:** the freeze now starts at the entry.
- **Line 112:** the notice is due at the append.
- **Line 113:** the batch-1 [RESULT] shows the diff from the entry to batch 1.
- **Line 55:** times are compared as instants.

The only new options are L1 and the wider reach of L2. Both are choices made after the data.

**Do the G2/G3 changes and the folder list hold?**
- **G2 (freeze from the entry): holds.** REG-22's round-4 trace (a judged-path change after the cut, before batch 1) now makes batch 2 retrospective. Two side effects:
  - it carries L2 into the longer window;
  - `withheld.SEALS` is on the path, and any new registration with new runs adds a tuple to it (see O-b).
- **G3 replaced by K3: holds, and both reviews agree.** G3's own trace: P1 is committed together with an [OPS] entry, then set aside; P2 is committed alone.
  - Under draft 19, P1 is the record because it is "the first run that gave REG-19's table", and P2 "does not take its place". So the cut stays T1, which was G3's concern, and nothing is voided.
  - Voiding would hand whoever commits the record a way to end batch 2 after seeing the table. The coordinator's reasoning (line 207) is right.
- **The folder list (line 108): holds.** No rule read the append-time `valid`. I checked each of its uses:
  - the breach of (a) is tested by name, and the list still records whether a `checks.json` exists;
  - a flag set before the cut is part of what REG-19's table counts;
  - a flag changed after the cut is caught by (b)'s third list and by line 107's flag rule.
  - One wording point is in O-e.

**3. Verdict: NOT READY.** Two required items. Both touch line 104's route or a label rule, so they need an owner-proxy pass. REG-22 draft 10 shares the passage and needs the same change.

**Required 1 (line 107).**
- (a) For "There is no record if the first run that gave REG-19's table was not saved under its start time," write: "There is no record if the first run that gave REG-19's table was not saved under a stamp as above (a UTC time taken no later than its start; `final.sh`'s stamp, taken before its recheck, is one),"
- (b) For "; if the record's file name, its commit or the ancestry check is missing, batch 2 is labelled retrospective." write: ". These are facts in git that anyone can check: if the [RESULT] leaves one out or quotes one wrongly, a [CORR] adds or corrects it, and the omission never changes a label. The label follows from the facts alone: with no record, batch 2 is not computed (above); a commit this bullet relies on that is not before the cut has the consequence its own rule gives ("What was known", duty (a), the stopping rule's bullet "From this entry to batch 2")."

**Required 2 (line 104; line 112's notice).**
- In line 104, replace from "The one exception is a change committed before REG-19's table was first computed or read" through "governs nothing)." with: "The one exception is a change made and reviewed before REG-19's table was first computed or read: its commit, and the rule F review and owner-proxy pass approving it (saved verbatim and committed), are all made before the record's cut, as "Batch 2 not computed" defines it. Any other change on the path labels batch 2 retrospective, including a change made before the cut whose reviews were not committed before it; no review made after the cut restores batch 2 (the principle of "What was known": whether batch 2 governs is not settled with REG-19's table public)."
- In line 112, after "makes batch 2 retrospective if it lands after the record's cut", add: ", or if its rule F review and owner-proxy pass are not committed before that cut".

Optional:
- **O-a, a stamp later than the record's commit.** Line 107 calls this "a breach too, reported the same way", so the record stands. But such a cut lies after the record's commit, so the time test does nothing, and changes made between the true start and the commit count as before; that is J1 again. Only a wrong clock or a forged name can cause it. Say batch 2 is then retrospective.
- **O-b, SEALS in the freeze.** `withheld.SEALS` is on the path (line 104), and from the entry to batch 2 a registration with new runs would add a tuple to it, ending batch 2 for nothing. Say that a hunk that only adds a `SEALS` tuple whose pattern matches none of the run names of batch 1, batch 2 or the reference lies outside the path, checked with `fnmatch` on the names listed in the [RESULT].
- **O-c, history rewrites before the stamp.** "A rewritten commit counts as after the cut" also catches a rewrite made before the stamp, such as an amend of the [REG] commit minutes after appending it. That rewrite leaks nothing, and the time test already catches rewrites after the stamp. Limit it to commits rewritten after the stamp or with a committer date set by hand.
- **O-d, the folder-list command.** Name the exact command (`test -e <folder>/checks.json` per folder). An `ls` of a folder would print its file names, which is more than existence.
- **O-e, line 108's source.** Line 108 says "the delegation names `checks.json` as the one file a rerun decision may read". The committed delegation entry does not say this. FILE(analysis/withheld.py:7) does, and so does the untracked `docs/FABLE_PROMPT.md`, which is not evidence under rule B. Cite `withheld.py:7`.
- **O-f, batch outputs (line 113).**
  - Batch 1's stamp should be taken with `date -u` in the same command line, as the record's is.
  - If batch 2's command line did not redirect its stdout to the file, batch 2 should be retrospective. That fact is fixed before the output exists; today no consequence is stated.

**Can it change a decision?** Yes, as in earlier rounds. Batch 2's J1 sets what may be said about λ = 2.0 and K3's status, at 0 GPU h.

**4. What I could not check**
- **REG-22 draft 10.** Not in this bundle. L1 and L2 apply to the shared passage and to REG-22's freeze, whose replacement text says "needs rule F and an owner-proxy pass first". I also did not read REG-22's proxy Q7, which is where L1's sentence came from.
- **Earlier runs of `analysis.gate reg19`.** Whether anyone has already run it, in the pinned worktree or on `main` with `AFTERSHOCK_UNSEAL=REG-19`. If so, K1 applies today.
- **REG-20's gate.** Whether `analysis.k1 reg20_a_may_start` (line 103), which reads REG-19's runs, prints anything per run before REG-19's table. That output would sit outside the record rule. Not read.
- **Commits on the VM.** Whether commits are ever made on the VM, which has its own clock.
- **Pushed history.** Whether `main` is pushed anywhere, which is the only outside evidence that history was not rewritten.
- **Tests.** I did not rerun pytest; the judged path is unchanged, and 35 tests passed in round 7.
