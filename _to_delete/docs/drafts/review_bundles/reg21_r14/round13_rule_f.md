# Rule F round 13 on REG-21 draft 20 (agent a0adfd0cddd98f5fb), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:57:06.140Z), no word changed. It saw the bundle `docs/drafts/review_bundles/reg21_r13/` and the code at `8164211`.

---

REG-21 draft 20, round-13 adversarial review (rule F): NOT READY

L1 and L2 are fixed. L2's wording opens no route by which batch 2 governs where draft 19 would not have let it. P1–P3, T6, R4 and the agent's own sentence hold.

Two of the changes you asked about each open a route by which batch 2 governs where draft 19 would not:
- **M1, the SEALS exemption (line 104).** It tests the new seal against the folders the command finds. But a seal hides folders from the command, so the test is circular. A seal that hides a sixth valid reference run counts as "outside the path", and batch 2 governs. Under draft 19 the result was "retrospective" or "not computed". The hole is in my own O-b wording ("the run names … of the reference"); please log it as my error.
- **M2, the rewrite rule (line 107).** O-c's narrowing judges a rewritten commit "by its new committer time". Rewrite tools that keep or copy an old date (`--committer-date-is-author-date`, `git filter-repo`) then make a commit rewritten after the stamp count as before. "Set by hand" does not clearly cover them. Draft 19 counted every rewritten commit as after.

Both fixes are one passage each and text only. M2 touches the test for "before", so it needs an owner-proxy pass. M1 narrows an exemption on the freeze, so in doubt it needs one too. REG-22 draft 11 shares both passages.

How I worked:
- **Limits kept.** I opened nothing under `runs/`, the backups, any `state/reg19_*` file or any probe output. I ran no analysis.
- **Repo state.** HEAD is `346ee6c`. Since `8164211` only `c2.py`, `k5.py` and their tests have changed; the judged path, `harness/` and `configs/` have not.
- **Bundle copies.**
  - The bundle diff equals a fresh `diff`.
  - Draft 20 is byte-identical to `docs/drafts/reg21_draft20.md`, and the draft-19 copy is the one I reviewed.
  - `final.sh`, `common.sh` and `delegation.md` equal their sources.
- **Citations.** FILE(analysis/withheld.py:7) and FILE(docs/decisions.md:4256) resolve to what line 108 says.
- **Runbook.** `agent/RUNBOOK.md:45` and `agent/PLAN.md:56` now run the table only through `final.sh`.
- **Code read at `8164211`.** `load.find_runs` (load.py:41–44); `k3w.reference` (k3w.py:131–142); `REG21` (k3w.py:55–90); `batch1_runs` (k3w.py:360–367).
- Line numbers are draft 20's.

**1. Round 12's items**

1. **L1: fixed (line 107).** Citations are facts in git, an omission gets a [CORR], and the label follows from the facts alone. I agree with taking L1 over REG-22's T3 and R1. What they protect, that the time half of the test is checked, is a fact anyone can check. A label that depends on whether the [RESULT] quotes it would hand its writer, who already holds batch 2's output, a choice. One way to meet both concerns is optional item O-1.
2. **L2: fixed (lines 104, 106, 112).** On your question:
   - Draft 20 lets batch 2 keep its standing only when a change and both its approving reviews are committed before the cut.
   - Draft 19 allowed the same changes with reviews at any time before batch 2.
   - So draft 20's set of changes that keep batch 2 is a subset of draft 19's, and no new route opens.
   - Lines 106 and 112 say the same.
   - The cut's timing is still decided before the table exists, so whether a pending review lands in time is decided blind.
3. **Optional items.** O-a (as P2), O-d and O-e are correct. O-b and O-c open M1 and M2. The first half of O-f is correct. I accept your reason for not taking the second half: its only evidence is the [RESULT]'s own quote, written after the output. See O-4 for what the check then rests on.
4. **The rest of the diff holds:**
   - **P1:** `final.sh`'s stamp qualifies.
   - **P2:** a stamp later than the commit is a fact in git and makes batch 2 retrospective, so no one chooses it.
   - **P3:** a saved file is committed late and is still the record; "no record" no longer follows from leaving it uncommitted.
   - **The agent's sentence:** a lost record means batch 2 is not computed. That is the only reading, and loss is a forbidden act.
   - **T6:** it counts more outputs, so it is stricter.
   - **R4:** it removes only output on synthetic folders, which reveals nothing. `test_sandbox.sh:60` intercepts that command by a case pattern; I read only that line.

**2. Findings**

**M1. The SEALS exemption tests against the folders the command finds, which the seal itself decides. Required.**
- **Inputs:**
  - After the cut, a new registration reruns the open-loop cache-off sweep. A config named, say, `sweep_l1pl350_pc_off_rerun.yaml` gives a folder `…_sweep_l1pl350_pc_off_rerun_r2.5`, which matches `ref_pattern` `*_sweep_l1pl350_pc_off_r*` (k3w.py:77). It is valid, at a rate of 2.5.
  - The registration adds the usual tuple, `("REG-30", "*_sweep_l1pl350_pc_off_rerun*", "[RESULT] REG-30")`, as every registration with new runs does (withheld.py:26–32).
- **What the code does:** `find_runs` drops sealed folders before anything else (load.py:42). So `reference` finds exactly the five pinned runs and does not raise (k3w.py:137–142).
- **What the text says (line 104):** the tuple's pattern matches none of "batch 1's runs, the reference runs and every folder matching the batch-2 pattern". "The reference runs" are the five, so the hunk "lies outside the path", and batch 2 governs.
- **What should happen:** without the seal, the sixth valid run at a rate of 2.0 or more makes `reference` raise, and batch 2 is not computed (line 107 lists that case). Under draft 19 the SEALS hunk after the cut made batch 2 retrospective. So "such a seal changes nothing the command reads" is false here.
- **A timing lever too:** computing batch 2 before REG-30's [RESULT] lifts the seal means it governs; computing it after means it is not computed. That choice is made with REG-19's table public.

**M2. "Judged by its new committer time" trusts a date that some rewrite tools keep or copy. Required.**
- **Inputs:**
  - Entry E is at 10:00Z. Two alternative fixes to `k1.windows`, F_a at 11:00Z and F_b at 11:10Z, sit on side branches; each has its reviews committed. The stamp is 12:00Z, and record R is committed at 12:05Z.
  - After the table is read, `main` is rebased to E–F_a–reviews–R with `git rebase --committer-date-is-author-date`.
- **What the text says (line 107):** "a rewritten commit is judged by its new committer time".
  - The new time is the old author time, 11:00Z, and F_a′ is a strict ancestor of R′, which is now "the first commit that adds that file".
  - So F_a counts as before, line 104's exception holds, and batch 2 governs.
  - The fix was chosen after the data. `git filter-repo`, editing a pre-cut commit's content and keeping its dates, does the same.
- **Draft 19's text** ("a rewritten commit counts as after the cut") gave "retrospective".
- **"Set by hand"** might cover the flag, but it plainly does not cover a tool's defaults. Two readings, opposite outcomes.
- Both drafts depend on the rewrite being reported. Optional O-2 makes it a fact.

**3. Verdict: NOT READY.**

**Required 1 (line 104, M1).** For "A hunk that only adds a tuple to `withheld.SEALS` whose pattern matches … such a seal changes nothing the command reads." write:
"A hunk that only adds a tuple to `withheld.SEALS` lies outside the path if its pattern matches (by `fnmatch.fnmatchcase`) none of these names, listed in the [RESULT] of each batch computed after the hunk, from the directory itself (a listing of the `runs/` that `load.RUNS` names in the checkout the command runs from, sealed folders included, not `find_runs`): the 13 names of batch 1, every folder matching `ref_pattern` (`*_sweep_l1pl350_pc_off_r*`, valid or not) and every folder matching the batch-2 pattern. A seal that hides a folder the command would otherwise find changes what it reads (a sixth valid reference run at a rate of 2.0 or more makes `reference` raise, FILE(analysis/k3w.py:137–142)), so it is on the path."

**Required 2 (line 107, M2).** For "A rewritten commit is judged by its new committer time, like any other, so one rewritten after the stamp counts as after the cut; a commit whose committer date was set by hand counts as after the cut." write:
"A commit rewritten before the stamp is judged by its new committer time, like any other. A commit rewritten after the stamp counts as after the cut, whatever its committer date says, and so does any commit whose committer date was not taken from the clock when the commit object was written (`GIT_COMMITTER_DATE`, `--committer-date-is-author-date` in `git rebase` or `git am`, `git filter-repo` and other tools that keep or copy a date)."

Optional:
- **O-1, reconciling L1 with T3 and R1.** Until a [CORR] supplies a missing citation, the [RESULT] gives the label as "pending that check". The label that stands is the one the facts give, so no one gets a choice.
- **O-2, rewrites as a fact.** The batch-2 [RESULT] quotes `git reflog show <branch>` from this entry's commit to the batch-2 commit, showing no `rebase`, `amend`, `reset` or `filter` entry. Add that committer times along the first-parent chain from the entry's commit to the record's commit never decrease. Both are local facts; they shrink the part that rests on honesty.
- **O-3, T6's list.** It names `reg19_table()` and `reg19_pair`. `reg19_cold_side` (gate.py:1834) prints the same `c` per run. Define the table by content: any printed value that a row of `reg19_table` holds (`c`, outcome, verdicts) for a REG-19 run.
- **O-4, a batch with no saved file (line 113).** The `batch1_median` check then uses a recomputation at the batch's named commit (a check, not a second computation), never the [RESULT]'s quote. That is what "the computation reads only committed code and the run folders" relies on; say so.
- **O-5, "approving" (line 104).** Define it: rule F READY with no open required item, and owner-proxy APPROVE, on the change as committed (REG-22 proxy's condition 1 wording).
- **O-6, R4's "a copy".** A folder holding any file copied or derived from a REG-19 run counts as a copy.

**Can it change a decision?** Yes, unchanged. Batch 2's J1 sets what may be said about λ = 2.0 and K3's status, at 0 GPU h.

**4. What I could not check**
- **REG-22 draft 11's copy.** Not in this bundle. M1 and M2 apply to its shared passage and to its freeze.
- **Rerun plans.** Whether any planned registration reruns `configs/sweep_l1pl350_pc_off.yaml`, or uses a config whose folder names match `ref_pattern`. That is M1's practical likelihood. The owner-proxy's standing note says no rerun before batch 2, but that is a note, not a rule.
- **Remote history.** Whether `main` is pushed to a remote, which would make a rewrite visible from outside.
- **Earlier runs, VM commits, REG-20's gate.** Whether `analysis.gate reg19`, `reg19_pair` or `reg19_cold_side` has already printed on REG-19's real folders. Whether commits are made on the VM. What REG-20's gate prints.
- **`test_sandbox.sh`.** Beyond its line 60, not read.
- **Tests.** I did not rerun pytest; the judged path is unchanged.
