# rulef-reg21-draft24-r17 (rulef-reg21-r17), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T16:01:10.714Z). Item names as given by the reviewer (prefixes BE, BF, BG, BH were assigned in the round-2 review prompts).

---

Rule F round 17 on REG-21 draft 24: NOT READY. Six items are required, BE1–BE6. All six need an owner-proxy pass, and five concern batch 2's standing. In my reading none is a design change: each is wording, a tag, a stricter rule, a reporting duty or a disclosure.

What I read:
- The whole bundle reg21_r17.
- At HEAD (d76211b): analysis/k3w.py, withheld.py and recheck.py; load.py:1–45; gate.py (burst_end, reg19_step, reg19_inputs, `__main__`); k1.py:57 and :80; k3.py:60–118; modelf.py:38–40; harness/run.py:1–26; harness/config.py.
- analysis/recheck.py at 5ee6e38.
- decisions.md lines 3785, 4084, 4205, 4255, 4276, 4279 and 4308.
- git metadata. The bundle's final.sh, common.sh and launch.sh are byte-equal to HEAD's (PROBE: my `git show HEAD:… | diff`).

What I opened beyond that, inputs only (as the search script does):
- Three tool-call inputs in the transcripts: fdf13821 line 2209, its subagent aaebfa565af29d02f line 90, and bc2fcf6d line 10177.
- One pass over all transcripts that printed only counts of tool calls by tool name.

What I did not open: nothing under runs/ beyond folder names, nothing in state/, no queue or probe output except the bundle's search output, no backups, no RESUME.md. The classifier refused a listing of ops_r3/, so I did not read queue.sh.

I wrote nothing into the repository. My one experiment ran in a throwaway git repo in my scratchpad, with no project data.

D24:n means FILE(docs/drafts/review_bundles/reg21_r17/registration_draft24.md:n).

## Round 1's items (BA1–BA4, BB1–BB8)
- **BA1:** met. D24:55 sets the blind cut at S and states what the author had seen; D24:107 and D24:108 use BA1's words. S itself inherits BE1.
- **BA2:** met in the text: whole files are frozen, B is defined, and "a later commit that reverts it does not undo it". Not met in the command: see BE3.
- **BA3:** met. S is drawn from the working tree, all refs and decisions.md quotes; E must not be preceded by such a commit; the duties are reported breaches; D24:54 points to the facts. Two gaps remain, both in BE1: "file named `reg19_final_*`" also catches the review bundles' copies of final.sh, and "working tree" covers only the main checkout.
- **BA4:** met in form. D24:111 has the append duty, and D24:54 corrects the terminal clause with launch.sh:28 and :51, both right. But the statement the duty repeats is false: see BE4.
- **BA-O1:** taken, but the closure still misses three files (BE2). BA-O2 and BA-O5: taken.
- **BB1:** met (D24:49, :53, :111, :238).
- **BB2:** met in form (D24:111). I checked the two hits most likely to break it, both running draft 2's `k3` and naming batch-1 runs:
  - The hit at 2026-11-12T16:02:29Z computes `k3.kbar_obs`, `lam_w`, `d_obs` and `completed` over `k3.window`. It does so on `S.as_run(cfg, S.simulate(cfg, mu, …))`, model F replays built from the configs of four runs, not on their measured data.
  - The hit at 16:27:18Z reads configs only.
  - So D24:111's "the only such hit" holds for both. The PROBE file does not show this; see BE-O1.
- **BB3:** met (D24:107; D24:241).
- **BB4:** no object left under the whole-file freeze.
- **BB5:** not checked; it lives in the [DECISION], which is not in the bundle.
- **BB6:** met (D24:73, :75).
- **BB7:** met (D24:54 cites decisions.md:4279 and carries a BELIEF tag). The allowed-reads line it cites is stale; the fix is in BE4.
- **BB8:** met (D24:104, Limits).

## BE1. By its own words, fact (2) already fails: nine commits on main add files named `reg19_final_*` that are not REG-19 tables (D24:104, D24:55)
Trace:
1. D24:104 counts "any file named `reg19_final_*`" and requires that "no commit that adds such a file is E or an ancestor of E".
2. The review bundles hold copies of final.sh named `reg19_final_sh_for_reference.sh`. `git log --all --diff-filter=A --name-only -- ':(glob)**/reg19_final_*'` lists 15 such adds in nine commits, ab6988f through ba67e55. All nine are ancestors of HEAD, so every future E descends from them (PROBE: my run of that command and `git merge-base --is-ancestor` on each, 2026-11-13).
3. That gives two readings. On the literal one, fact (2) fails now and batch 2 is retrospective; D24:104's "the label follows from these facts alone" points that way. On the other, "such a file" means one whose name carries a stamp. The writer of the batch-2 [RESULT] holds REG-19's table and batch 2's output, and picks the reading. A later [CORR] can pick the other.
4. The same words make the owner's planned deletion of `_to_delete/` (six such copies, found with `find`) a breach of "No `reg19_final_*` file is deleted".
5. `find .` covers only the main working tree. `git worktree list` names two more worktrees of this repository, aftershock-reg19-pin and aftershock-linktest-pin. final.sh computes the table from inside the first (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:29)), so a hand run that saves its output there lies outside S's sources.

Replacement in D24:104. Replace "let S be the earliest UTC stamp in the name of any file named `reg19_final_*`, among the files of that name anywhere in the repository's working tree (`find . -name 'reg19_final_*' -not -path './.git/*'`), every name that any commit on any ref adds (`git log --all --diff-filter=A --name-only --format='%H %ct' -- ':(glob)**/reg19_final_*'`), and every such stamp a decisions.md entry quotes" with:

"A **REG-19 table file** is a file whose name is `reg19_final_` or `reg19_final_err_` followed at once by a UTC stamp of the form `YYYYMMDDTHHMMSSZ` (the names `final.sh` writes, FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20), FILE(docs/probe/20261113_reg19/ops_r3/common.sh:42)); a name that begins `reg19_final_` without such a stamp, such as the review bundles' copies `reg19_final_sh_for_reference.sh`, is not one. Let S be the earliest stamp of any REG-19 table file among the files in the working tree of every worktree that `git worktree list` prints (`find <worktree> -name 'reg19_final_*' -not -path '*/.git/*' | grep -E '/reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z'`), every name that any commit on any ref adds (`git log --all --diff-filter=A --name-only --format='%H %ct' -- ':(glob)**/reg19_final_*'`, filtered the same way), and every such name a decisions.md entry quotes"

Further edits in the same bullet:
- "no commit that adds such a file" becomes "no commit that adds a REG-19 table file".
- "every file named `reg19_final_*` is committed on `main`" becomes "every REG-19 table file is committed on `main`".
- "every such file in the working tree is committed" becomes "every REG-19 table file in any worktree is committed".
- "a `reg19_final_*` file moved out of the repository and never committed or quoted" becomes "a REG-19 table file moved out of the repository and never committed or quoted, a table saved under a name that is not a REG-19 table file".
- "No `reg19_final_*` file is deleted or moved out of the repository" becomes "No REG-19 table file is deleted or moved out of the repository, and from this entry on no other file is given a name that begins `reg19_final_` (copies of `final.sh` in review bundles are named `final_sh_for_reference.sh`)".

D24:55: replace "the UTC stamp in the name of the earliest file named `reg19_final_*`, wherever it now is" with "the earliest stamp of a REG-19 table file, wherever it now is".

- Owner-proxy pass: yes (the two git facts).
- Batch 2's standing: yes.
- Kind: wording, plus a stricter rule (every worktree, and no new names). It is wording because D24:104 ties S to "the UTC stamp in the name" and to final.sh's stamp, and a name with no stamp gives no S. If the owner-proxy reads the narrowing as a change of the facts' design, item 4 of the stop rule applies; that is for it to say.

## BE2. The frozen list leaves out three files of the import closure it defines (D24:104, D24:239)
Trace:
1. D24:104 defines the frozen files as "every file the command imports, by the import closure of `analysis/k3w.py` at this entry's commit (function-level imports included; computed with Python's `ast`)", then lists 22.
2. harness/run.py is on the list. It imports `env_snapshot`, `trigger`, `workload` and `loadgen` at module level (FILE(harness/run.py:23), FILE(harness/run.py:24)), and harness/env_snapshot.py, harness/loadgen.py and harness/trigger.py are not listed. An `ast` pass at HEAD that follows `from <package> import <submodule>` finds 23 .py files: the 20 listed plus these three (DERIVED: my pass, scratch only).
3. Now suppose a commit changes harness/loadgen.py after REG-19's table. That is plausible, because REG-20's open arm changes the client (FILE(analysis/k1.py:16)). By the list, fact (1) holds; by the definition, it fails. The writer of the [RESULT] chooses.

Replacement in D24:104. Replace "`harness/__init__.py`, `harness/checks.py`, `harness/config.py`, `harness/recorder.py`, `harness/run.py`, `harness/workload.py`, `pyproject.toml`, `uv.lock` (22 files)" with:

"`harness/__init__.py`, `harness/checks.py`, `harness/config.py`, `harness/env_snapshot.py`, `harness/loadgen.py`, `harness/recorder.py`, `harness/run.py`, `harness/trigger.py`, `harness/workload.py`, `pyproject.toml`, `uv.lock` (25 files; `harness/run.py` imports `env_snapshot`, `loadgen` and `trigger` at module level, FILE(harness/run.py:23), FILE(harness/run.py:24)). The [DECISION] (delegate) prints the `ast` pass at E, which follows `from <package> import <name>` into submodules; a file it names that this list lacks is added before the append, and the list in the entry governs."

D24:239: replace "(22 files)" with "(25 files)".

- Owner-proxy pass: yes (the judged-path list).
- Batch 2's standing: yes.
- Kind: a stricter rule (more files frozen) and wording (which governs).

## BE3. Fact (1)'s command misses a change made and reverted on a merged branch (D24:104)
Trace (PROBE: a throwaway repo in my scratchpad):
1. Commit E. On a side branch, X edits k1.py and X′ reverts it. main gets one unrelated commit, then side is merged with `--no-ff`.
2. `git log E..HEAD -- k1.py` prints nothing; `git log --full-history E..HEAD -- k1.py` prints X and X′.
3. D24:104 says both "Any change counts … a later commit that reverts it does not undo it" and that fact (1) is this command printing nothing. After REG-19's table, one reading gives primary and the other retrospective. This is BA2's trace again, one layer down.

Replacement in D24:104. Replace "`git log --format='%H %ct %s' E..B -- <the frozen files>` prints nothing" with:

"`git log --full-history --format='%H %ct %s' E..B -- <the frozen files>` prints nothing (without `--full-history`, git hides a change made and reverted on a branch that was merged), and `git diff --quiet E B -- <the frozen files>` exits 0"

- Owner-proxy pass: yes.
- Batch 2's standing: yes.
- Kind: wording (the command now matches the sentence), and a stricter rule.

## BE4. "What was known" denies runs of `analysis/` code on REG-19's folders that the draft's own sources record, and two rules give such a run different consequences (D24:54, D24:55, D24:111)
Trace:
1. D24:54 says "no run of `analysis/` code on a REG-19 run folder from any checkout, is found by a search", and that "on `main` the seal has refused such runs since `72fafb5`".
2. Against that, four records:
   - (a) A14's recheck ran `analysis.recheck` "over all 182 folders" on 2026-11-12 (FILE(docs/decisions.md:4205)). The search lists it as a `ran` hit at 2026-11-12T16:46:27Z (PROBE(docs/probe/20261113_transcript_search/search_20261113T153519Z.txt)). Its default pattern was "*" and there was no seal yet (analysis/recheck.py:16 and :18 at 5ee6e38). REG-19's six folders were on the Mac, since their manifest was committed at 15:53:46 UTC in 54a995d (DERIVED). decisions.md itself says such a glob "would have read REG-19's six runs" (FILE(docs/decisions.md:4255)). The recheck printed only folders whose verdict changed, and none of the nine it names is a REG-19 run (FILE(docs/decisions.md:4205)). The search classes it as `ran`, not `ran_on_reg19`, because its command names no REG-19 run.
   - (b) The queue's `recheck_ok` runs `analysis.recheck` from `main` with `AFTERSHOCK_UNSEAL=REG-19` before each step, and final.sh does the same before the table (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:210), FILE(docs/probe/20261113_reg19/ops_r3/final.sh:25)). It keeps validity fields only (common.sh:197–201). The seal gives way to that variable (FILE(analysis/withheld.py:51), FILE(analysis/withheld.py:57)). The search cannot see these runs: its pattern needs a literal `python` (FILE(docs/drafts/review_bundles/reg21_r17/transcript_search.py:32)), and it does not parse `.sh` files.
   - (c) `analysis.gate reg19_step` runs after each seed. It computes each completed seed's pair outcome (`reg19_pair`) before it prints `done` and `continue` (FILE(analysis/gate.py:2022)), and those are the flags D24:54 cites.
   - (d) The read at 11:45 UTC on 2026-11-12 (D24:54 (i)) also printed `ls -la` of seed 17's control's run folder and the last three lines of its `events.jsonl` (that call's input, bc2fcf6d line 10177; the PROBE's `reg19_read` hits at 11:45:33Z show the start of it). D24:54 names only the log's last 15 lines.
3. The two rules disagree on (a)–(c). If the append-time search finds an unlisted run of `analysis/` code on a REG-19 folder, D24:54 says "batch 2 is labelled retrospective by design". D24:111 says such a run "goes into 'What was known' … and the draft returns to rule F and an owner-proxy pass", with no label. (a)–(c) fall under both, so the delegate picks one at the append. (b) and (c) will run again before then if REG-19 resumes first (BELIEF).
4. D24:54 and D24:55 cite the allowed reads as common.sh:34. At HEAD that line is `CONTROL_PAT`; `ALLOWED` is line 36, moved by the quiet-hours patch.

Replacements:
- In D24:54, replace "No other read of a REG-19 run's files or logs beyond names, validity and the names of failed checks, and no run of `analysis/` code on a REG-19 run folder from any checkout, is found by a search" with:

  "The read in (i) also printed `ls -la` of that control's run folder and the last three lines of its `events.jsonl` (the same command). **Code in `analysis/` has read REG-19's run folders in three ways, each printing validity or the queue's flags only:** (iii) the A14 recheck, `analysis.recheck` over all 182 folders on 2026-11-12 at 16:46 UTC, before the seal existed (FILE(docs/decisions.md:4205); the search's `ran` hit of that time), which printed only folders whose verdict or failed checks changed, none of them a REG-19 run; (iv) the queue's `recheck_ok` before each step and `final.sh` before the table, which run `analysis.recheck` from `main` with `AFTERSHOCK_UNSEAL=REG-19` and keep only validity fields (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:197), FILE(docs/probe/20261113_reg19/ops_r3/common.sh:210)); (v) `analysis.gate reg19_step` after each seed, which computes each completed seed's pair outcome and prints only `done` and `continue` (FILE(analysis/gate.py:2022)), the flags quoted above. (iv) and (v) run again with every step and are listed here as classes. No other read of a REG-19 run's files or logs beyond names, validity and the names of failed checks, and no other run of `analysis/` code on a REG-19 run folder from any checkout, is found by a search"

- In D24:54, replace "on `main` the seal has refused such runs since `72fafb5` (FILE(analysis/load.py:20))" with:

  "on `main` the seal has refused such runs since `72fafb5` (FILE(analysis/load.py:20)) unless `AFTERSHOCK_UNSEAL` names REG-19 (FILE(analysis/withheld.py:51)), as (iv) does; the search does not see commands run from a `.sh` file or through `$PY`"

- In D24:54 and D24:55, replace "FILE(docs/probe/20261113_reg19/ops_r3/common.sh:34)" with "FILE(docs/probe/20261113_reg19/ops_r3/common.sh:36)".

- In D24:111, replace "no reading of a REG-19 run beyond `common.sh`'s allowed reads and the two listed there, and no run of `analysis.gate reg19` or any other analysis on a REG-19 run folder from any checkout, is known. If one is, it goes into "What was known" with its run, time, reader and content, and the draft returns to rule F and an owner-proxy pass." with:

  "no reading of a REG-19 run beyond `common.sh`'s allowed reads and the two listed there, and no run of `analysis.gate reg19`, or of other `analysis/` code on a REG-19 run folder beyond (iii)–(v), is known; it gives the `done` and `continue` of every step record written since draft 23 and the bound they imply, derived as 'What was known' derives it for seed 17. If such a reading or run is known, it goes into 'What was known' with its run, time, reader and content, and the draft returns to rule F and an owner-proxy pass; where the trigger in 'What was known' applies (a run of `analysis/` code on a REG-19 run folder, or a read of a line a REG-19 burst run wrote after its burst began), batch 2 is also labelled retrospective by design."

- Owner-proxy pass: yes (line 111's check).
- Batch 2's standing: only through D24:54's trigger. With (iii)–(v) unlisted, the stricter reading labels batch 2 retrospective by design at the append.
- Kind: a disclosure and a tag. The harsher consequence where both rules apply is a stricter rule, and the step flags are a reporting duty.

## BE5. Four actions can end or demote batch 2 after REG-19's table, and none carries the duty to say what its author had seen (D24:104, D24:108, D24:112)
A validity change carries that duty (D24:107). These four do not:
- **(a) A commit to a frozen file after E.** It labels batch 2 retrospective (D24:104), and the list now holds harness modules that REG-20 and E1 may need. Once REG-19's table gives each burst run's c over W, which nearly fixes r (D24:55), such a commit removes a batch-2 reading that could make K3 "mixed" (D24:73).
- **(b) A new valid run whose folder matches the batch-2 pattern,** for example a later registration's run of a REG-19 burst config. Duty (a) bars only folders without a valid checks.json (D24:108). Two valid runs of one seed give "not computed" (D24:107).
- **(c) A new valid run matching `*_sweep_l1pl350_pc_off_r*` at a rate of 2.0 or more** (FILE(analysis/k3w.py:77), FILE(analysis/k3w.py:139)). `reference` then raises, for batch 1 too, and batch 2 is not computed. Alternatives 2, 4 and 10 (D24:69, D24:92, D24:98) invite exactly this re-measurement of the cache-off sweep.
- **(d) A REG-19 table name with a stamp earlier than E,** whether as a file or as a quote in decisions.md. It sets S before E for good ("no review, statement, [CORR] or later commit restores primary standing", D24:104). A typo in an [OPS] entry's quote is enough. So is an example name in a review saved verbatim into an entry; this review writes none.

Replacement in D24:104: after "…given a committer date by hand." add:

"From this entry until batch 2 is computed or declared not computed: no run is made, or copied into the `runs/` that `load.RUNS` names, whose folder name matches the batch-2 pattern (other than REG-19's own registered runs and reruns) or `REG21["ref_pattern"]`; and no text, file name or commit message gives a REG-19 table file's name with its stamp, other than `final.sh`'s own files and the entry that reports and commits them (all others write `reg19_final_<stamp>`). Any commit after E that touches a frozen file, any such run, and any such name or quote states in its commit message or entry what its author had seen of REG-19's runs, as an entry that changes a validity flag does ('Batch 2 not computed'). The batch-2 [RESULT] lists each such event with that statement and, for the stamp that sets S, its source (the path and the commit that adds it, or the decisions.md line). These duties change neither fact; a breach is reported and its consequence stands."

In D24:112's notice, after "and new code goes into new files" add: "; no run whose folder matches REG-21's batch-2 pattern or `*_sweep_l1pl350_pc_off_r*` is made before then".

- Owner-proxy pass: yes.
- Batch 2's standing: yes.
- Kind: a stricter rule and a reporting duty. A deliberate breach after the table remains possible, as under every breach rule; I do not ask for a design change for that.

## BE6. If REG-22's entry is not committed before S, batch 2 can end up in a state the draft says it never reaches (D24:102, D24:107)
Trace:
1. final.sh checks for neither entry (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:8–32)). "not run until both entries are committed" is a process rule only (BELIEF: docs/status.md's wording, not code).
2. Suppose S falls after REG-21's entry but before REG-22's. After the table, the delegate can either commit a [DECISION] withdrawing REG-22, which lets batch 1 and then batch 2 run, or leave REG-22 pending, which blocks both (D24:102; D24:59 counts this route).
3. D24:107 promises that "once REG-19's final [RESULT] exists, batch 2 is computed or declared not computed by these rules, and a [RESULT] says which". In this case that promise fails silently, and which way it goes is chosen after the table.

Replacement in D24:102: after "…will list REG-21's tables as known." add:

"If REG-22's [REG] and its [DECISION] (delegate) are not both committed before S (the stopping rule), this bullet no longer waits for them: from S on, REG-22 counts as listing REG-21's tables as known, and REG-21's batches proceed by these rules; no later [DECISION] on REG-22 changes that."

- Owner-proxy pass: yes (the stopping rule).
- Batch 2's standing: whether batch 2 is computed at all; it does not touch the two facts or the validity cut.
- Kind: a stricter rule, a default fixed before the data in place of a choice after it.

## Optional
- **BE-O1.** Save the classification of every `ran` hit (runs, real or simulated, functions) beside the search output, and cite it. I could confirm D24:111's "the only such hit" for the 16:02:29Z hit only by reading its input. On real data that hit would have mattered: `k3.window` is W (FILE(analysis/k3.py:70)), `kbar_obs` is the mean of turn + 1 over the turns completed in W (FILE(analysis/k3.py:91)), and the prompt of turn k is 2176 + 256k (FILE(analysis/modelf.py:38)). So the mean served prompt by end time equals 1920 + 256 × kbar_obs (DERIVED). For the same reason, add "the mean turn index of the turns served (`k3.kbar_obs`)" to D24:111's list.
- **BE-O2.** The search reads only Bash, Read and Write inputs (transcript_search.py:111–121). My count-only pass found the transcripts also hold Edit (209), Monitor (7), Agent (92) and SendMessage (69) calls; none of the Monitor inputs names a REG-19 run. Its run pattern misses `$PY -m`, `env VAR=… python -m`, `python3.12 -m`, `python -X …`/`-W … -m`, and `.sh` files a session runs. Either state these as limits in the [DECISION] or widen the pattern before the append.
- **BE-O3.** The PROBE has four `ran_on_reg19` hits, and D24:54 does not say why none is a run on a REG-19 folder. They are config parsing on 2026-11-11, code text for `SEALS` and `batch2_pattern`, and an `ls configs`. Say so in the [DECISION].
- **BE-O4.** D24:54's bound is too tight. The second factor of r can reach 3200 ÷ 3072 ≈ 1.04 if no first turns are served (D24:51), so c < 2.0 bounds r below about 1.24 (DERIVED: 2.0 ÷ 1.681 × 1.042), not 1.19.
- **BE-O5.** `.python-version` (3.12.13) picks the interpreter for `uv run` and is not frozen; add it. Also, `git status --porcelain -- <frozen files>` cannot see an untracked `harness/<name>/` package or an ignored extension module beside a frozen `.py`, and Python imports either one first. A check that `git status --porcelain --ignored --untracked-files=all -- analysis harness` lists nothing but `__pycache__` would close that.
- **BE-O6.** Write "from E (included)" in the rule against hand-set committer dates, and quote E's reflog line in the [DECISION] and in the batch-2 [RESULT]: it is the one witness to a backdated E that needs no push. Also require `git stash list` to be empty at batch 2; round 16's PROBE showed that `--all` does not list a stash's untracked commit.
- **BE-O7.** D24:186 still describes E1's cut as if it were in force. Add "(replaced in draft 24 by the validity freeze from E, 'Batch 2 not computed')".
- **BE-O8.** Cost for the owner: withheld.py is frozen, so no new seal can be added before both batch 2s. Runs of any registration made in the meantime stay unsealed, and their protection rests on discipline alone.

## Strongest alternative explanation
- **Batch 2's J1 "inside".** REG-19's pass test keeps runs that complete less than min(2.0, λp) over the same W, and the precondition keeps them all-miss. With r ≈ (c ÷ 1.681) × (mean served prompt ÷ 3072) (D24:51), "inside" mostly restates that REG-19's already published c over W lies within about 5 % of the cache-off floor, plus the prompt factor. It is not an independent measurement of token rate. To separate the two, compare per run r with (c ÷ 1.681) × (prompt ÷ 3072) × (1.681 × 3072 ÷ U_off), and compare r over spans with c over spans. If r tracks c this closely, J1 adds nothing beyond REG-19's table.
- **Batch 2 outside high while batch 1's λ = 2.0 group is inside, with a contrast above 0.05.** Either the day or GPU clock differs (alternative 10; the gpu.jsonl clock means over W would separate it, but they are not computed here), or batch 2's stricter selection (busy over 2400 s) does it (the left-out lists per load).
- **Batch 1's J2.** Load and day coincide (D24:67); nothing on these runs separates them.

## Can it change a decision?
Yes, and only through batch 2. It is the one judged item on unread data, and its label sets what may be said about λ = 2.0 and K3's status (D24:71–75). As written, BE1's literal reading already makes batch 2 retrospective, so it can change no decision until BE1 is fixed. Batch 1's labels are nearly fixed by published rates (D24:52) and change none. Cost: 0 GPU h.

## Not checked
- REG-22 draft 15's mirror passage. Its line 133 has the same `find .`, the same `git log` without `--full-history` and a "(23 files)" list, so BE1–BE3 likely apply there too (BELIEF).
- The [DECISION] (delegate) text (BB5, AD4's statement).
- Whether any step record after seed 17 exists, and what it holds (state/ unopened).
- queue.sh (the listing was refused); I relied on the bundle's common.sh, final.sh and launch.sh, which equal HEAD's.
- The other `ran` hits outside 2026-11-12 05:00–19:00 UTC, and every input beyond the three I opened.
- Whether `git log --all` lists commits made on the pin worktrees' detached HEADs.
- Pushed or VM history, and the reflog.
- pytest beyond tests/test_k3w.py (35 passed; synthetic).
