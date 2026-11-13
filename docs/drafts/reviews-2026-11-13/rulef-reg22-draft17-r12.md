# rulef-reg22-draft17-r12 (rulef-reg22-r12), verbatim

Saved by the agent from the reviewer's own SendMessage call to team-lead (tool-call input, its session e6263307, line 576, timestamp 2026-11-13T20:22:05.115Z; the send succeeded, msg_id d0a4b76c), because the message had not yet been delivered into the main session's transcript when saved. An earlier send of the same review to "main" (17:50:07 UTC, 15,322 characters) was refused; this resend (16,930 characters) is the delivered one. Round 4 (text written under the stop). Item names CG1–CG6 are this round's.

---

Rule F round 12 on REG-22 draft 17 (the text written under the stop): NOT READY on six required items, CG1–CG6. CG1 and CG2 concern batch 2's standing.

Reviewer: rule F, isolated. Inputs:
- the bundle reg22_r12: all 33 MANIFEST hashes verify, and registration_draft17.md and item_map.md are cmp-equal to docs/drafts/reg22_draft17*.md;
- git at HEAD 128fd88, rechecked at 5f782d6;
- tool-call inputs only.

I wrote nothing to the repo. Scratch: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/e6263307-6f64-4fde-8309-47d36a63889e/scratchpad/r12/. D17 = registration_draft17.md.

I write the synthetic stamps below without their file-name prefix on purpose (see CG1). Do not add the prefix back when you record this review.

## 1. Round 11's items (BK1–BK8, BK-O, BL1–BL3, BL2a, BL3a) and the BK-S items

**Verbatim check** (string match, my script check_verbatim.py):
- Verbatim: BL1(a)–(c), BL2(c), BL3(a)–(c); BK2's find, grep, worktree and [OPS] texts; BK3; BK4 up to its departure; BK6(a), BK6(b), and BK6(d)'s second and third texts; BK7; BK1's first sentence.
- As composites: BL2(a) with BL2a(a) inside it, and BL2(b) with BL2a(b).
- With only the departures that item_map lists:
  - BK1's addendum sentence, with "(read (iii) above)";
  - BK2's git log, with --reflog;
  - BK5's sentences;
  - BK6(c), merged into BL3(a);
  - BK8, with its subject reworded;
  - BK-S4, adapted.

**The departures listed in item_map are sound.**
- BK4: what the note holds is stated as unknown, and the owner can open it.
- BK-S4 followed by "So from this entry…": the freeze keeps its words.
- BK-O1 and BK-O2: my scratch repo confirms that --all finds only the newest stash entry and --reflog finds all. --reflog also finds a commit that only another worktree's HEAD reflog reaches.
- The label words follow BJ14(d).

**BK-S1–S6 in the stop entry (decisions.md:4548–4555):** applied substantively. Two notes:
- (a) Item 2 adds BI-S1's definition ("its consequence is batch 2's label"). This is narrower than review-stop item 3's "what a retrospective batch 2 does", and BK-S4's own claim to concern batch 2's standing rests on item 3. It is harmless now that no further stop exists.
- (b) BK-S6's commands have no --reflog, so REG-22's fact (2) and the stop rule's check are not "these three commands" (CG8).

**The freeze (stop entry item 5, which is BK-S4).**
- The text keeps the freeze, both facts, the validity cut and the not-computed rules.
- `git log --all --full-history ffc76b3..HEAD` over the 27 files prints nothing, at 128fd88 and again at 5f782d6. `git status` on them prints nothing.
- closure.py at HEAD equals closure_c2_20261113T173125Z.txt.
- But see CG2: the facts now only add label words, which does not close BK-S4's own trace.

## 2. Required items

### CG1. Synthetic stamps will enter decisions.md and set S

Batch 2's standing: yes. Class: a change to fact (2), which by BK-S2 is none of the four classes. Owner-proxy pass: yes.

**Trace.**
1. Rule F round 11's BK2 trace, step 8, wrote two concrete table-file names with the stamps 20261114T010203Z and 20261114T020000Z (FILE(docs/drafts/reviews-2026-11-13/rulef-reg22-draft16-r11.md:74)). `git grep` finds these in committed text, and only these.
2. D17:4 says "The [REG] will hold every rule F review verbatim", and the stop entry (decisions.md:4556) says the same. So at E, decisions.md quotes both names.
3. Fact (2)'s third command (`grep -noE … docs/decisions.md`) then prints them, so S ≤ 2026-11-14 01:02:03 UTC. REG-19 is still running (now seed 18's burst run, then seed 19), so the real S is likely later.
4. The consequences:
   - (a) If E's committer time is at or after that instant, fact (2) "fails" and the label reads "retrospective (by design; fact (2))". That label is false.
   - (b) Every window "at or after S" opens early. Under "Runs", an entry on a seed-19 run's validity after 01:02:03 UTC ends batch 2. BK3's and BG4's withholding also start then.
   - (c) The [REG] itself breaches BG-O8's duty. By BG-O8's own words, round 11's saved review already "counts toward S", but no command searches saved reviews. So BK2's commands do not print everything the text counts.
5. The same names reach:
   - REG-21's S and its duty that no text gives a table file's name;
   - the review-stop rule's item-5 check.

   Cross-apply there, or both E's must precede 2026-11-14 01:02:03 UTC.

**Replacements in D17.**
- After "every such time a decisions.md entry quotes for a table file (`grep -noE 'reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z' docs/decisions.md`)", keeping the period, insert:
  > Two stamps that this grep prints are synthetic and do not count toward S: 20261114T010203Z and 20261114T020000Z. Rule F round 11's BK2 trace (step 8) wrote them for files in a throwaway repository (FILE(docs/drafts/reviews-2026-11-13/rulef-reg22-draft16-r11.md:74)), and this [REG] quotes that review verbatim. They are fixed here, before any table file exists. The [RESULT] lists the grep's lines for them as synthetic. A file with either stamp in a working tree, or added by a commit, still counts (rule F round 12, CG1).
- Replace "and one that does still counts toward S as it stands (rule F round 10, BG-O8)." with:
  > a decisions.md entry that does so still counts toward S as it stands, except the two synthetic stamps named above; a saved review or other committed text is not searched and does not count toward S (rule F round 10, BG-O8; rule F round 12, CG1).

### CG2. A fact-(1) failure still lets a changed-code batch 2 decide batch 1's line a

Batch 2's standing: yes, as "what a retrospective batch 2 does" (item 3); it changes no label word. Class: a stricter rule. Owner-proxy pass: yes.

**Trace.**
1. Batch 2 is already retrospective by design, so a fact-(1) failure costs it nothing but one word.
2. D17:133 says such a batch "enters that line's disagreement test as a computed batch".
3. D17:136 allows "a fix to a frozen file" (with rule F and an owner-proxy pass) if batch 2's command raises after S. The fix is written by people who have seen REG-19's table and [RESULT].
4. The fixed code's labels then go straight into "Batches that disagree at λ = 2.0". They can turn a disagreement into agreement and release line a's D1/D2 permission.
5. The defect clause already sends differing labels to "met none". The raise path and a plain breach do not.
6. So BK-S4's stated reason (decisions.md:4553: "a change to its code after REG-19's table could steer batch 1's line a") is not met by keeping the facts as label words.

**Replacement in D17:133.** Replace "it enters that line's disagreement test as a computed batch, so it can withhold line a's permission and line d's wording, and no sentence rests on it alone;" with:
> it enters that line's disagreement test as a computed batch, so it can withhold line a's permission and line d's wording, and no sentence rests on it alone; but if fact (1) fails through a commit whose committer time is at or after S, or through a line of `git status`, a fix under the fix clause included, batch 2 is reported per run with its labels and counts in 'Batches that disagree at λ = 2.0' as a batch that met none of the lines, until an entry headed `[DECISION] (owner)` names that change (rule F round 12, CG2);

### CG3. "An owner's [DECISION]" can be read as including a delegate entry

Batch 2's standing: no. Class: wording (a stricter reading). Owner-proxy pass: yes.

**Trace.**
1. The delegation lets "[DECISION] (delegate)" entries give "the approvals that CLAUDE.md rule C reserves for the owner".
2. So the agent that has seen REG-19's table can write a delegate entry "that names the pending batch" and propose D1/D2 on batch 1 alone. That empties BK3's window, BG4's withholding and the defect clause.
3. D17:22 already uses "an entry headed `[DECISION] (owner)`".

**Replacements.**
- "waits for batch 2 or for an owner's [DECISION] that names the pending batch" becomes:
  > waits for batch 2 or for an entry headed `[DECISION] (owner)` that names the pending batch
- "waits for an owner's [DECISION] that names the cause" becomes:
  > waits for an entry headed `[DECISION] (owner)` that names the cause
- "as a batch that met none of the lines until an owner's [DECISION]." becomes:
  > as a batch that met none of the lines until an entry headed `[DECISION] (owner)`; a delegate entry does not release any of these lines (rule F round 12, CG3).

### CG4. BI-O1's status check already fails today

Batch 2's standing: no. Class: a reporting duty. Owner-proxy pass: no.

**Trace.**
1. At HEAD, `git status --porcelain --ignored --untracked-files=all -- ':(glob)*.py' ':(glob)*.pth'` prints "!! docs/paper/". docs/paper is a nested git repository: it holds docs/paper/.git and is excluded via .git/info/exclude. So the [RESULT] will always report a breach that is not one.
2. The check also misses a root-level package directory (yaml/__init__.py) and .so modules.
3. My run of the two `find` commands below prints nothing at HEAD.

**Replacement.** Replace "and that `git status --porcelain --ignored --untracked-files=all -- ':(glob)*.py' ':(glob)*.pth'` prints nothing: `python -m analysis.c2` puts" with:
> and that `find . -maxdepth 1 \( -name '*.py' -o -name '*.pth' -o -name '*.so' \) -print` and `find . -mindepth 2 -maxdepth 2 -name '__init__.py' -not -path './analysis/*' -not -path './harness/*' -print` print nothing (the earlier `git status` form prints the nested repository `docs/paper/`; rule F round 12, CG4): `python -m analysis.c2` puts

### CG5. A read missing from "What was known", and a classify2 label outside BL3a's map

Batch 2's standing: no, unless the owner finds trigger lines. Class: a disclosure, and a stricter rule on BL3a. Owner-proxy pass: yes.

**Trace.**
1. The bundle's classify2 output has 80 hits whose labels lie outside BL3a's mapping: 79 `names_in_command` (classify2.py:111) and 1 `disclosed[CORR]`. By D17:80's own rule, that already requires another owner-proxy pass at E.
2. `names_in_command` auto-labels any command whose only class is `names_reg19_run` as no read. One such hit is a read:
   - Where: session 8c5f8396, line 9857, 2026-11-13 15:32:08 UTC.
   - Command: `grep -rn "w3000_s17" docs/paper/context-pack-2026-11-12.md docs/paper/ctxpack-2026-11-12/ | grep -iv "checks.json\|outcome withheld" | cut -c1-400 | head -12`
   - It printed up to 12 lines about seed 17 from local files that quote run data. These are exactly the "files that quote a run's lines" that search2 is said not to see.
   - D17 does not list it.

**Replacements.**
- Before "On 2026-11-12 A14's `analysis.recheck` read every run folder", insert:
  > On 2026-11-13 at 15:32:08 UTC session 8c5f8396 printed up to 12 lines naming `w3000_s17` from `docs/paper/context-pack-2026-11-12.md` and `docs/paper/ctxpack-2026-11-12/`, leaving out lines holding `checks.json` or `outcome withheld` (DERIVED from the command text, tool-call inputs only; what it printed is not stated; those files are local and not committed); the owner can state whether those lines quote a line a REG-19 burst run wrote after its burst began, which would be a read under the trigger (rule F round 12, CG5).
- Replace "are no read. The rule label `names_or_validity`" with:
  > are no read. `names_in_command` stands only where the command prints no file's lines; a command that prints lines of a file other than a config, a script or a prelaunch record (`cat`, `grep`, `head`, `tail`, `sed -n`) is labelled by hand by reading its input, and `disclosed[CORR]` is listed (read (i)) (rule F round 12, CG5). The rule label `names_or_validity`

### CG6. A sentence that will be false at E

Batch 2's standing: no. Class: wording. Owner-proxy pass: no (it is not one of read (iii)'s facts).

**Replacement.** Replace "(DERIVED: it is still the last folder name in `runs/`)" with:
> (DERIVED: it was the last folder name in `runs/` from 2026-11-12 13:55 UTC until seed 18's runs were copied, folder names only)

## 3. Optional items (CG7–CG12)

**CG7.** Class: a stricter rule on fact (2). Owner-proxy pass: yes.
- Add `-m` to fact (2)'s git log.
- Reason (my scratch repo): a table file added only in a merge commit is not printed without -m, and is printed with it.

**CG8.** Class: wording.
- Replace "whose check uses these three commands" with "whose check uses these commands without `--reflog`".

**CG9.** Class: wording.
- Replace "`python -V`, `uv --version`, `python -c 'import analysis" with "`uv run python -V`, `uv --version`, `uv run python -c 'import analysis".
- Reason: the bare form reaches the venv's interpreter only because this shell's PATH has .venv/bin first.

**CG10.** Class: wording, BL3(b). Owner-proxy pass: yes.
- After "A hit in none of these classes is a read beyond what is listed here." add "A hit that BL3a's mapping calls no read is not such a read."

**CG11.** Class: wording, BL3(c). Owner-proxy pass: yes.
- Replace `as "About batch 2" says` with `as "Run-time lines and looks" says`.
- Reason: the classes are in line 80, not line 79.

**CG12.** Class: a reporting duty.
- After "a proposal made before S stands, and the batch-2 [RESULT] names it with its commit" add ", with the `done` and `continue` lines REG-19's queue had printed by that commit".
- Reason: `continue: False` after seed 18 is REG-19's futility stop (final.sh:15), which is outcome information known before S.

## 4. Rule F proper

**Traces on which the labels or verdict are wrong:**
- CG1: a false "fact (2)" label word, and every after-S window opening early;
- CG2: a steered line a;
- CG3: a release by a delegate entry.

**Does BK3 close the "batch 2 pending" trace?**
- From S, yes, apart from CG3.
- Before S, the queue's `continue`/`done` lines leak partial outcome (CG12).
- If REG-19 ends with no table, S never exists and the window never opens; that path is REG-19's owner decision.

**Do BK2's commands print every table file the text counts?** Not quite. They miss files added only in a merge commit (CG7), and the saved-review quotes that BG-O8 counts (CG1).

**Strongest alternative explanation.**
- For `loop`: an overload that the load alone sustains. The control readout separates the two only in part.
- For a disagreement between batches: the span count (9 judged spans against 4; 0.963⁹ = 0.71 against 0.963⁴ = 0.86, DERIVED), and schedule lulls in the longer watch.

**Can the analysis change a decision?** Yes, at λ = 2.0, through lines a, d and e and the disagreement test: P ≈ 0.05 for batch 1 (BELIEF) and ≤ 0.084 for batch 2 (DERIVED in D17). The stop does not change this, because batch 2 still withholds.

**Other checks that pass:** the line citations decisions.md:4541, 4546, 4548, 4552, 4553, 4555 and 4556; BK-O6's arithmetic; BK6(d)'s UNSEAL sentence.

## Not checked (at the time of the original text)
- A full classification of the 79 `names_in_command` hits. I read about a dozen inputs; apart from the 15:32 grep, they print configs, prelaunch records, manifests or folder names.
- The crosswalk from the `disclosed(<item>)` labels, which use REG-21's numbers, to REG-22's reads (i)–(iii).
- The tags search2.py:93, queue.sh:75 and 77, withheld.py:51 and load.py:20.
- BL1(b)'s "read lines" without "most likely".
- BL1(a)'s "which no analysis is known to have read". It is ambiguous, because reg19_step did read REG-19's runs.
- Not opened, by rule: RESUME.md, `state/`, queue outputs, `runs/` beyond names, the context pack's content, any transcript output.
- Not run, by rule: pytest and check_docs.

Verdict: NOT READY.
- Apply CG1–CG6 verbatim.
- CG1, CG2, CG3 and CG5 need the owner-proxy pass.
- Cross-apply CG1 (and CG3) to REG-21 and to the review-stop rule's item-5 check.

## ADDENDUM (checked after the original text, 2026-11-13 ≈ 20:21 UTC)
- **FILE tags confirmed at HEAD 5f782d6:**
  - search2.py:93 is the READERS set (`find_runs`, `load_run`, `batch1_runs`, `batch2_runs`, `reg19_inputs`, `references`), which supports BK5's sentence.
  - queue.sh:75 takes the stamp and names `state/reg19_step_out_s<seed>_<stamp>.txt`; queue.sh:77 runs `(cd $W && $PY -m analysis.gate reg19_step > $outf …)`, from the pinned worktree.
  - withheld.py:51 reads AFTERSHOCK_UNSEAL.
  - load.py:20 is `withheld.guard(d.name)`.

  All are as D17 cites them.
- **The freeze, rechecked at 5f782d6** (after c8b482d, REG-20 arm A ops scripts, and 5f782d6, STATE.md): `git log --all --full-history ffc76b3..HEAD` over the 27 files still prints nothing.
- **CG1 is unchanged.** decisions.md holds no concrete table-file stamp yet. Committed text holds the two synthetic names in three files only: the saved round-11 review and its two bundle copies. It is 20:21 UTC now, so E can still precede 2026-11-14 01:02:03 UTC. CG1's other effects (the early S windows, the BG-O8 breach, REG-21) hold whatever E's time.
- **Still not done:** the full 79-hit classification, the `disclosed(<item>)` crosswalk, and BL1(a)/(b) wording.
