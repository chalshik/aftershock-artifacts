# rulef-reg21-draft23-r16 (rulef-reg21-r16), verbatim

Saved by the agent from the teammate message received in the main session transcript, 2026-11-13 between 12:42 and 12:51 UTC (the senders' idle notifications). Item names as given by the reviewer (prefixes BA, BB, BC, BD, CA, CB were assigned in the review prompts).

---

Rule F round 16 on REG-21 draft 23: NOT READY (4 required items, BA1–BA4; 3 need an owner-proxy pass).

Read: bundle reg21_r16 (draft 23, draft 22, diff, round 15, proxy delta on draft 22, delegation, final.sh and common.sh copies); analysis/{k3w,k1,load,gate,withheld,floor,k3,modelf_sim}.py at 8164211; ops_r3/launch.sh; decisions.md:4274–4279. I opened nothing under runs/, the backups, any queue or probe output, or RESUME.md. In state/ I counted names only: none matches reg19_final_*. D23:n = FILE(docs/drafts/review_bundles/reg21_r16/registration_draft23.md:n).

Is the new rule sound? For code and thresholds after the entry, yes. With the path frozen, a look cannot change what batch 2 computes (DERIVED from D23:104). But three things can still move after a look, and both git facts have readings that whoever holds REG-19's table can choose between.

## BA1. The cut moved from "the table first seen" to "the first commit that adds a reg19_final_* file" (D23:55, :107, :108). Required; needs a proxy pass.
final.sh takes its stamp (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20)), computes the table (:29) and prints it to the terminal (:32, `cat $out`). The commit that adds the file comes later, at a time its committer picks: D23 no longer requires "at once". Draft 22 closed these windows at "REG-19's table being computed or read by anyone" (draft 22 :55, :107, :108).
- Trace 1 (overrule): final.sh prints the table at 10:00Z. At 10:20Z the owner commits "batch 2 always governs" (or the reverse), knowing each run's c over W, which fixes r's first factor (D23:55). The file is committed at 10:30Z.
  - On the commit reading, the overrule is blind and governs.
  - D23:55's "%ct against the UTC stamp" supports a stamp reading. So there are two readings, and the choice is made after the table.
  - A hand run of `analysis.gate reg19` in the unsealed pin worktree (D23:54) never closes the window; the overrule only "states what its author had seen".
- Trace 2 (validity): in the same gap, an entry marks a burst run invalid.
  - D23:107: a flag set before that commit "is part of what that table counts and does not end batch 2". That is false in this gap.
  - (b)'s third list (D23:108) catches the difference and gives "not computed". So one event has two readings.
Replacement:
- D23:55, for "the first commit that adds … had seen of REG-19's runs)", write: "the start of the first final.sh run, i.e. the UTC stamp in the name of the earliest file named `reg19_final_*`, wherever it now is (final.sh takes it before computing the table, FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20, :29)). The overrule's entry states what its author had seen of REG-19's runs; if that includes any output of `analysis.gate reg19`, or anything of a REG-19 burst run after its burst beyond the reads common.sh allows (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:34)), the overrule is not blind."
- D23:107, for "if, after the first commit … does not end batch 2)", write: "if, after this entry's commit and before batch 2, an entry changes the validity flag of a run matching the batch-2 pattern, or the seeds REG-19's table counts, other than through the checks.json the harness wrote when the run ended and REG-19's registered rerun rules".
- D23:108 (a), for "changes after the first commit that adds a `reg19_final_*` file", write: "changes other than as the harness wrote it when the run ended". For "a flag set before that commit is part of what REG-19's table counts, and a flag changed after it", write: "a flag rewritten without an entry".
With these, validity is frozen from the entry like the code, and no time test is needed.

## BA2. Fact (1) is a net diff, but the notice and "no later commit restores it" work per commit (D23:104, :112). Required; needs a proxy pass.
Trace:
1. REG-20 edits `k1.windows` in place in commit X, after the entry.
2. The notice (D23:112) says X "labels batch 2 retrospective", and D23:104 says no "later commit restores it".
3. After REG-19's table, someone either moves the change into a new function, which reverts X and is D23:104's own remedy, or leaves it.
4. If moved, the net diff is empty, so batch 2 is "primary" by "facts alone". The notice says retrospective.
Also, "the commit batch 2 runs from" is unconstrained: a branch without X gives an empty diff. And D23:104 asks for "each hunk with its commit", which a net diff does not have.
Replacement for (1): "(1) no commit in `git rev-list <entry>..<B>` has, against its first parent, a hunk in [the eight files] that lies on the judged path as this bullet defines it, where B, the commit batch 2 runs from, is the tip of `main` when its command starts; a later revert undoes no such commit."

## BA3. Fact (2) depends on where and how a reg19_final_* file is first committed (D23:104; D23:54). Required; needs a proxy pass.
- (a) Rerun after setting the file aside:
  1. REG-19 finishes while REG-21 is still in review, which the plan allows (D23:233). final.sh prints the table at T1. The honest label is retrospective.
  2. The T1 pair is "set aside". final.sh itself says to do this after a failure (final.sh:31), and D23:104 forbids only deletion or a move "out of the repository".
  3. The entry is committed. final.sh runs again at T3; its guard looks only in state/ (final.sh:18–19).
  4. The first commit that adds a `state/reg19_final_*` file now carries stamp T3, so the label is primary.
  The same happens without intent after a failed first run that wrote partial output.
- (b) With `--all`, a commit on any other ref can be "the first" (a branch, or a detached HEAD in the two pin worktrees, `git worktree list`). Then the entry is not its ancestor, and batch 2 becomes retrospective by choice. A stash is not a lever: in a throwaway repo, `git log --all --diff-filter=A -- <path>` did not list a stash's untracked commit (PROBE: my scratchpad test, no project data).
- (c) A file that final.sh saved but nobody committed leaves (2) undefined.
- (d) D23:54 asks for the [REG] and its [DECISION] before the file, with no time test. D23:104 asks for the entry only, with a time test.
Replacement for (2): "(2) the commit that appends this entry and its [DECISION] (delegate) (the later, if two) has a committer time earlier than the UTC stamp in the name of every file named `reg19_final_*` that is in the checkout, wherever it was moved, or that any commit added (`git log --all --diff-filter=A --name-only -- ':(glob)**/reg19_final_*'`), compared as instants (as now); and no commit that adds such a file precedes it on B's first-parent chain. Each such file is committed on main, alone, in the first commit after it is written; a pair set aside is committed where it was set aside." In D23:54, replace "this [REG] and its delegate [DECISION] are committed … (the stopping rule's freeze)" with "the stopping rule's facts (1) and (2) hold".

## BA4. Looks at batch 2's runs before the entry are checked only at draft time (D23:54, :111). Required; no pass needed (stricter, before data).
- D23:111 re-checks batch-1 and reference prints at the append (AD4), but D23:54's statement on REG-19 readings is dated at draft 23. REG-19 can resume before the append (attempt 3 is pending).
- Under ops_r3, the live lines go to `~/<config>_<stamp>.log` on the VM from a detached tmux (FILE(docs/probe/20261113_reg19/ops_r3/launch.sh:28, :51)). They do not go "to the terminal of whoever started it", and anyone with ssh can read them.
- Trace: seed 18's burst run happens; someone reads the end of its log; a round-17 item then changes a precondition. Facts (1) and (2) hold, the look is disclosed nowhere, and batch 2 is primary.
Replacement, appended to D23:111: "The [DECISION] (delegate) also names every REG-19 run folder made since draft 23 and repeats, up to the append, D23:54's statement: no reading of a REG-19 run beyond common.sh's allowed reads, and no run of `analysis.gate reg19` or any other analysis on a REG-19 run folder from any checkout, is known. If one is, it goes into 'What was known' with its run, time, reader and content, and the draft returns to rule F and an owner-proxy pass." In D23:54, correct the terminal clause, citing launch.sh.

## Optional
- BA-O1. Fact (1)'s eight files omit modules whose top level runs at import: analysis/__init__.py; floor.py (via gate); k3.py, modelf.py and modelf_sim.py (via k3w); harness/__init__.py and harness/workload.py (via modelf_sim). It also omits uv.lock. D23:104's definition covers their import-time statements, but the test does not look at them; add them. The named functions' static reach stays within the eight files (DERIVED: an AST pass at 8164211).
- BA-O2. AD4's evidence searched only `analysis.k3w` and `analysis.c2`. Two other places compute an uncached-token rate: `analysis/k5.py` (U, FILE(analysis/k5.py:8)) and `load.rates` (`recomputed_prefill_tok_s`, FILE(analysis/load.py:75); used by analysis.ipynb). Widen the search, or state its scope as a limit.
- BA-O3. A lost_ok or rerun decision for a REG-19 burst config is a selection that survives the freeze. If its maker had read that run beyond common.sh's reads, label batch 2 retrospective (a self-report, so it errs that way).
- BA-O4. `git branch -a` shows a `vm` remote, and pushing there is within the delegation. Pushing the entry commit there at the append would witness rewrites; D23:104 leaves this to the owner's `origin`.
- BA-O5. Typo at D23:3: "in the text)., rule F on draft 22".

## AD4 and AB2
AD4 is met verbatim (D23:111). AB2 is met (D23:54, matching FILE(docs/decisions.md:4279)), and the optional rewording was taken.

## Dangling text
- The first-commit cut at D23:55, :107 and :108 (BA1).
- D23:107's parenthesis (BA1).
- D23:54 against D23:104 (BA3d).
- "each hunk with its commit" against a net diff (BA2).
Nothing else cites the record, cut, statements or reflog. docs/status.md still describes draft 19's record regime; D23:112's notice must replace it.

## Can it change a decision?
Yes. Batch 2 is the only judged item on unread data, and its label decides λ = 2.0 and K3's status (D23:71–75). BA1–BA3 let that label be chosen after REG-19's table, which nearly fixes batch 2's r (D23:55). 0 GPU h.

## Not checked
- REG-22 draft 14's mirror passage (the same items likely apply; BELIEF).
- Where the launch scripts for seeds 15–17 (now in _to_delete/) sent the harness's stdout.
- Pushed or VM history.
- pytest, and any analysis.
