# rulef-reg22-draft16-r11 (rulef-reg22-r11), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T17:12:12.526Z; message 1 of 2 from this teammate). Item names BK1–BK8, BK-S1–BK-S6, BK-O1–BK-O6 are this round's.

---

Rule F round 11 on REG-22 draft 16 (round 3 on the freeze, the last): NOT READY, on batch 2's standing (BK1, BK2). Under the review-stop rule, item 4, this is the stop.

# Rule F round 11 on REG-22 draft 16 (round 3 on the freeze, the last)

Reviewer: rule F, isolated. Inputs: the bundle `docs/drafts/review_bundles/reg22_r11/`; `analysis/c2.py` and its imports at HEAD; git; tool-call inputs of this project's transcripts (never tool outputs); `docs/decisions.md` at the lines cited. I did not do the session-start reading of CLAUDE.md (rule F isolation). Nothing was written to the repository. My scratch work is in /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/353762fb-0527-49f6-9a2c-1db84d1c97b0/scratchpad/r11/.

Notation:
- **D16:n** is line n of `registration_draft16.md`.
- **T(s:n)** is line n of a transcript under `~/.claude/projects/-Users-chalshik-Projects-aftershock-artifacts/`, where s is the session id prefix and, for a subagent, `/agent-<id>`. It cites the tool-call input only and lies outside the repository.

## Verdict: NOT READY, on batch 2's standing (BK1, BK2)

**The stop.** Under the review-stop rule's item 4 (FILE(docs/decisions.md:4406)), as amended (FILE(docs/decisions.md:4437)), this round being NOT READY on batch 2's standing is the stop. Batch 1 is registered as the only primary reading, and batch 2 is labelled retrospective by design.

**Two routes, independent of each other:**
- BK1: draft 16's own trigger (D16:80) has already fired. The read was found after the bundle was cut (decisions.md 2026-11-13 [CORR], FILE(docs/decisions.md:4453)).
- BK2: fact (2)'s commands cannot print the table files that its own text counts.

**The other items.** BK3–BK6 are not about batch 2's standing. They are applied as usual, in the text that the stop calls for, which gets its own rule F review and owner-proxy pass (item 4).

## 1. BG1–BG5 and BH1–BH9: met as asked?

Checked against D16 and `text_diff_draft15_to_draft16.diff`.
- **BH1 / BG1: met.** BH1's words are verbatim at D16:133. But the sentence added beside them (cross-applied from REG-21's BF1/BF3) widens the set beyond what BH1's commands can print. See BK2.
- **BH2 / BG2: met.**
  - The 27 files are listed. `closure.py` at HEAD prints 24 code files; with the 3 environment files that makes 27, the same list (DERIVED: I ran `docs/probe/20261113_freeze/closure.py`, and its output matches `closure_c2_20261113T162249Z.txt`).
  - `git log --full-history ffc76b3..HEAD` over the 27 files prints nothing, and HEAD is now beyond a8036fd (d960ef3, 81be812, f3abd23, 8a3e059). `git status` on them is clean. (DERIVED, my run.)
  - `uv run --offline pytest -q tests/test_c2.py` passes: 29 passed (DERIVED, my run).
  - Nit: "(rule F round 10, BG2).." has a double period (D16:133).
- **BG3: met.** Verbatim at D16:64 and D16:133.
- **BG4: met.** Verbatim at D16:93, D16:102 and the defect clause (D16:133).
- **BG5 / BH7 / BH8:**
  - (a) Met.
  - (b) Met in words, but what the text says about `search2.py`'s limits and about REG-19's own computations is incomplete, and in one place false (BK5, BK6).
  - (c) Met.
- **BH3, BH4, BH5, BH6, BH9: met verbatim** at the places they name.

## 2. Required items

### BK1. Draft 16's own trigger has fired: batch 2 is retrospective by design

- **Trace.**
  1. D16:80 says: "If it then finds a run of `analysis/` code on a REG-19 run folder, or a read of a line a REG-19 burst run wrote after its burst began, beyond what is listed here, this entry is not appended as written: batch 2 is labelled retrospective by design, and the text goes to rule F and an owner-proxy pass."
  2. On 2026-11-12 at 17:59:38 UTC, a context-pack subagent of session fdf13821 ran `s57_inv.py`. Its `tail -3` most likely printed the `ok` and `unfinished` request counts of seed 17's control and burst run (FILE(docs/decisions.md:4453), "Read 1"; DERIVED there from the inputs; the output was not opened).
  3. `unfinished` is written by the harness's checks into `checks.json` at the run's end (FILE(harness/checks.py:67), FILE(harness/checks.py:69), as cited by that [CORR]). So it is a line that a REG-19 burst run wrote after its burst began. In a burst run, a large `unfinished` goes with a waiting line that has not emptied, which is what REG-19's per-seed test asks about (FILE(docs/decisions.md:4453), "What the counts tell").
  4. Draft 16 does not list this read, and the widened search (`search2.py` as fixed in d960ef3) is what found it. This is exactly the case the trigger names.
  5. The [CORR]'s "Effect" proposes that the next drafts "add Read 1 as item (x) of 'What was known'" (FILE(docs/decisions.md:4494)) and reads the freeze as "a look is disclosed, not a switch". Written that way, the next draft would place the read inside "what is listed here", and the trigger would not fire.
  6. That is a trace on which batch 2's label is chosen after a look at batch-2 data: any read found before E can be listed, so the trigger becomes something the author can step around. Draft 16's "None of this is a switch" is about looks after the entry, not about this trigger.
  7. Commit f3abd23's message gives the agent's own reading: "the drafts' own trigger applies to seed 17's burst checks.json counts, so both batch 2s are expected to be retrospective by design". A commit message is not evidence (rule B). The text must say it.
- **Replacement.** In D16:80, after the sentence quoted in step 1, add:
  > Draft 16's list is the one this trigger compares against: a read of the kind it names that is found after draft 16, whether by the rerun at E or earlier, applies the trigger even if a later draft lists it. Read 1 of decisions.md 2026-11-13 [CORR] (FILE(docs/decisions.md:4453)) is such a read: at 2026-11-12 17:59:38 UTC `s57_inv.py` most likely printed the `ok` and `unfinished` counts of seed 17's burst run from its `checks.json` (DERIVED there from the inputs; the output was not opened). So batch 2 is labelled retrospective by design, and the standing words in line a and in "Batches that disagree at λ = 2.0" name this read beside any other cause.

  Also add Read 1 and the 17:56:24 UTC listing to "What was known", as the [CORR] asks.
- **Owner-proxy pass:** yes. It applies a stop to batch 2's standing, and the [CORR]'s "Effect" reads it the other way.
- **Batch 2's standing:** yes.
- **Class:** a stricter rule. It fixes what "listed here" means at the draft that set the trigger. REG-21 too: its draft 25 has the same trigger.

### BK2. Fact (2)'s commands cannot print the table files its own text counts

- **Trace.**
  1. D16:133 defines a table file to include "a name that matches `^reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z` without ending in `.txt`". The commands that are to be shown "as the verbatim output" glob only `*.txt`: `find . -name 'reg19_final_*.txt'` and `git log … -- ':(glob)**/reg19_final_*.txt'`. The decisions.md quotes have no command at all.
  2. After E, `final.sh` takes its stamp T1 (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20)) and computes. `analysis.gate reg19` fails after writing part of its stdout to `$out`, and `final.sh` says "the file $out must first be set aside by hand" (FILE(docs/drafts/review_bundles/reg22_r11/final_sh_for_reference.sh:31)).
  3. Its own guard refuses any `$ST/reg19_final_*.txt` (FILE(docs/drafts/review_bundles/reg22_r11/final_sh_for_reference.sh:18), FILE(docs/drafts/review_bundles/reg22_r11/final_sh_for_reference.sh:19)). So the obvious way to set the pair aside is to rename it to `…_T1_<pid>_1.txt.failed`. It is then committed "where it was set aside", as D16:133's duty asks.
  4. After seeing the partial `$out`, an entry changes the validity flag of a batch-2 run. Then `final.sh` succeeds with stamp T2.
  5. By the definition, S = T1. The change is at or after S, so batch 2 is not computed, and line a's permission and line d's wording are withheld (D16:64, D16:102).
  6. By the printed commands, S = T2. The change is "after E and before S", so batch 2 is retrospective and computed, and it enters the disagreement test.
  7. The two readings give different states of line a. The same commands also miss a set-aside pair from a `final.sh` run before E: that is fact (2) itself.
  8. Shown in a throwaway repository (DERIVED, /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/353762fb-0527-49f6-9a2c-1db84d1c97b0/scratchpad/r11/gitt). One commit adds `reg19_final_20261114T010203Z_11_1.txt.failed` and `reg19_final_20261114T020000Z_12_1.txt`. D16's `git log` prints only the 02:00:00 file; the replacement below prints both. Likewise for `find`.
  9. The backstop "a [CORR] corrects the quote" needs someone to notice what the printed commands hide. And D16's "so that the set is REG-21's" is false for the commands: REG-21's draft 25 uses the wide glob filtered by the expression (FILE(docs/drafts/review_bundles/reg22_r11/reg21_draft25_for_comparison.md:104)).
- **Replacement, in D16:133:**
  - Replace "(`find . -name 'reg19_final_*.txt' -not -path './.git/*'`, table-file names only)" with:
    > (`find . -name 'reg19_final_*' -not -path './.git/*' | grep -E '/reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z[^/]*$'`; the same `find` piped to `grep -vE` with that expression lists the other names)
  - Replace "(`git log --all --diff-filter=A --name-only --format='%H %ct' -- ':(glob)**/reg19_final_*.txt'`, table-file names only)" with:
    > (`git log --all --full-history --no-renames --diff-filter=A --name-only --format='%H %ct' -- ':(glob)**/reg19_final_*' | awk '/^[0-9a-f]+ [0-9]+$/ {c=$0; next} NF {print c, $0}' | grep -E ' (.*/)?reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z[^/]*$'`, one line per added table file with its commit and committer time; `--no-renames` so that a file renamed to a table-file name counts as added)
  - Replace "and every such time a decisions.md entry quotes for a table file." with:
    > and every such time a decisions.md entry quotes for a table file (`grep -noE 'reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z' docs/decisions.md`).
  - Replace "The `find` is run in every working tree that `git worktree list` names, and the `git log` with `--full-history` as well;" with:
    > The `find` is run in every working tree that `git worktree list` names, and the whole output of the three commands goes into the batch-2 [RESULT];
  - After "a pair set aside after a failed run is committed where it was set aside", add:
    > , and the [OPS] entry that `final.sh` requires for a second try quotes the set-aside files' names
- **Owner-proxy pass:** yes. It is other wording of BH1 and a change to fact (2) beyond BH1 (FILE(docs/drafts/reviews-2026-11-13/proxy-reg22-draft15-delta.md:160)).
- **Batch 2's standing:** yes (fact (2) and the validity cut at S).
- **Class:** a stricter rule. The commands print a superset, and the definition is unchanged.

### BK3. "Batch 2 pending" after S leaves batch 1's line a and line d free

- **Trace.**
  1. Batch 1 is computed after E and meets line a at λ = 2.0 (P ≈ 0.8, BELIEF, D16:11).
  2. REG-19's table is written (S). It shows which burst runs are `stuck`: a pass needs the burst run `stuck` with its control `recovered` (FILE(analysis/gate.py:1948)). That is batch 2's n for the n ≥ 3 tests.
  3. Batch 2 runs only once REG-19's final [RESULT] exists (D16:64), and the agent chooses when to write it.
  4. Until then D16:93 reads "batch 2 pending", and nothing withholds line a's permission to propose D1 and D2, or line d's wording. So a D1/D2 proposal that cites batch 1 alone can be made after seeing REG-19's table, at a time chosen after it.
  5. If batch 2 then disagrees, D16:102 withholds the permission "by itself" from then on, but says nothing of a proposal already made.
  6. BG4 closed this for a batch 2 not computed after S. Pending after S is the same state of knowledge.
- **Replacement, D16:93.** After "  - at λ = 2.0 only, "batch 2 pending" until batch 2 is computed or reported as not computed", insert:
  > ; from S (the stopping rule's fact (2)) until then, neither line a's permission to propose D1 and D2 nor line d's 'D1 and D2 not proposed as planned' applies at λ = 2.0 by itself, and wording that relies on either waits for batch 2 or for an owner's [DECISION] that names the pending batch; a proposal made before S stands, and the batch-2 [RESULT] names it with its commit
- **Owner-proxy pass:** yes. It changes what a decision line does, as BG4 did.
- **Batch 2's standing:** no. It governs batch 1's lines while batch 2 is pending, and it changes neither fact, nor the validity cut, nor what a retrospective batch 2 does.
- **Class:** a stricter rule.

### BK4. "RESUME.md was not opened" is false for this project's sessions

- **Trace.**
  1. D16:80 tags "the rest of each status line … was on the same lines" as "(BELIEF: the note that records it, RESUME.md, was not opened)". REG-21's draft 25 has the same sentence (FILE(docs/drafts/review_bundles/reg22_r11/reg21_draft25_for_comparison.md:54)).
  2. Tool-call inputs show the note written at T(bc2fcf6d:10376) (2026-11-12 15:53:29 UTC; committed in 54a995d) and opened many times:
     - Whole, by session fdf13821's context-pack subagents: T(fdf13821/agent-a625ca98c29ea904b:130) `cat -n` at 17:58:06 UTC and :273 (awk over every line) at 18:03:33 UTC; T(fdf13821/agent-a2058e8f5d4c1fd10:177) `cat -n` at 17:58:38 UTC.
     - By session 8c5f8396, whose subagents ran this registration's reviews (PROBE(docs/drafts/review_bundles/reg22_r11/transcript_search2_dryrun_20261113T162249Z.txt:466)):
       - Read at T(8c5f8396:265), 2026-11-12 18:28:18 UTC;
       - `cut -c1-1800` at :2302, 20:28:32 UTC;
       - `head -3` at :6720, 2026-11-13 11:38:25 UTC;
       - an Edit at :6730;
       - `sed -n 18,22p` at :7544, 12:07:26 UTC.
     - By 8c5f8396's subagents:
       - T(8c5f8396/agent-a2a5c2cef92be27bd:131), `cat -n` of the whole note with REG-19's queue outputs `queue_run*_output.txt`, 2026-11-13 00:39:56 UTC;
       - parts at a6a8a3241c8c5e416:158 and :164, a5f4a6d2ba3957cd7:153, ad7f6f660bfdeb54d:111, a43b6d3c375ffd53e:553, :612, :644 and :649 (12:04:57 UTC), and a4122f052f465a926:533 (12:16:30 UTC);
       - a Read at afe7a850230fb13ab:135, 12:23:22 UTC.
     - Read at T(4e055435:73), 2026-11-12 18:43:28 UTC, and at T(49020ad6:55).
  3. The note records what (i) saw of seed 17's control, so these are second-hand reads of those lines. Whether it quotes any burst run's lines after its burst, I cannot tell: I may not open it.
  4. `search2.py` does not see such reads: a note's path names no run id. A synthetic Read of RESUME.md gave no record (DERIVED, /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/353762fb-0527-49f6-9a2c-1db84d1c97b0/scratchpad/r11/synth_out.txt).
- **Replacement, D16:80.** Replace "(BELIEF: the note that records it, RESUME.md, was not opened)" with:
  > (BELIEF: what the note `docs/probe/20261111_reg19/ops/RESUME.md` holds of these lines is not quoted here. The note was written in session bc2fcf6d at 2026-11-12 15:53 UTC (committed in `54a995d`) and was opened, whole or in part, in this project's sessions: whole at 2026-11-12 17:58–18:04 UTC (session fdf13821's context-pack subagents) and at 2026-11-13 00:39 UTC (with REG-19's queue outputs); by Read at 18:28 and 18:43 UTC; its first 1800 characters per line at 20:28 UTC; in parts at 2026-11-13 11:38–12:23 UTC; and edited at 2026-11-13 ≈ 11:38 UTC. All are found in tool-call inputs only. The [DECISION] (delegate) lists these calls and states, from the note's committed text and without quoting a value, which REG-19 runs' run-time lines the note quotes. A line of a REG-19 burst run written after its burst began and quoted in the note is a read under this paragraph's trigger.)

  The same change applies to REG-21's line 54.
- **Owner-proxy pass:** yes. It is a false sentence in "What was known", as BB1 was.
- **Batch 2's standing:** no (a disclosure, item 3), unless the note quotes a burst run's line after its burst; then BK1's trigger applies.
- **Class:** a disclosure.

### BK5. Line 81's claim about reviewer scripts does not rest on what `search2.py` can show

- **Trace.**
  1. D16:81 rests the sentence "every reviewer script that called `c2` functions replaced `find_runs` … first" on `search2.py`'s `script_reads_runs` hits, "labelled `stubbed`".
  2. `script_reads_runs` fires only on code that calls `find_runs`, `load_run`, `batch1_runs`, `batch2_runs`, `reg19_inputs` or `references`, or that names a `runs/` path (FILE(docs/drafts/review_bundles/reg22_r11/transcript_search2.py:93)). A script that calls `c2.reg22_table` or `c2.batch_runs` has no record, whether or not it replaced `find_runs`.
  3. The dry run lists such scripts as bare `ran` lines with no record (PROBE(docs/drafts/review_bundles/reg22_r11/transcript_search2_dryrun_20261113T162249Z.txt:466) `t04_table.py`, :471 `t07_batch2_json.py`, :491 `r2_t04_reported_code.py`, :493 `r2_t06_judged_path.py`, and :464 `k_rules.py` for `k3w.reg21_table`).
  4. I read the inputs of the four c2 scripts. Each replaces `C.find_runs` (and `W.find_runs`) before calling (T(8c5f8396/agent-a1a83befb82fcfd8a:189), :219; T(8c5f8396/agent-a0fd29b2b40338bb5:178), :200). So no read was found. The point is that the cited support cannot show it.
  5. `stubbed` marks any assignment to those names anywhere in the code, including one made after the read, or `RUNS = Path('runs')` (DERIVED, synthetic run at 723a16b, /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/353762fb-0527-49f6-9a2c-1db84d1c97b0/scratchpad/r11/synth_out.txt; the [CORR] at FILE(docs/decisions.md:4453) found the second case in real data).
  6. An inline heredoc calling `c2.reg22_table(1)` gives only a `ran` line. `from analysis.c2 import *` is not resolved (same synthetic run).
- **Replacement, D16:81.** Replace "rests on `search2.py`'s output at E (its `script_reads_runs` hits, labelled `stubbed` where the code assigns to `find_runs`, `load_run` or `RUNS`, each classified in the [DECISION] (delegate)), and on round 2's owner-proxy's own reading" with:
  > rests on `search2.py`'s output at E, read as follows. Every `ran` line whose script or inline code imports `analysis.c2`, `analysis.k3w` or `analysis.gate`'s `reg19*` functions, with or without a `script_reads_runs` record, is listed in the [DECISION] (delegate). Each is classified there from the script's text in the tool-call inputs, never from the `stubbed` label: synthetic runs or a stub assigned to `find_runs`, `load_run` or `RUNS` before the first call that can read runs; a guard; or a read of real runs. The `stubbed` label marks any such assignment anywhere in the code, and `script_reads_runs` gives no record to code that calls `c2.reg22_table` or `c2.batch_runs` alone (FILE(docs/probe/20261113_transcript_search/search2.py:93)). A heredoc body that the output elides is read in the transcript's input. The sentence also rests on round 2's owner-proxy's own reading
- **Owner-proxy pass:** yes. It changes what batch 1's "What was known" rests on.
- **Batch 2's standing:** no.
- **Class:** a disclosure and a reporting duty.

### BK6. Line 80's statements on REG-19's own computations and on the search's limits

**(a) "From the pinned worktree" is false for seeds 15–17.** Their `reg19_step` ran from the queues of 2026-11-11/12:
- with `cd $R` in the main checkout (FILE(docs/probe/20261111_reg19/ops/queue_reg19.sh:9));
- as `uv run python -m analysis.gate reg19_step 2>$S/reg19_step_err_s$sd.txt | tail -1`, so stdout was reduced to its last line and the rest discarded (FILE(docs/probe/20261111_reg19/ops/queue_reg19.sh:30), the same line in `queue_reg19b.sh`, :34 in `queue_reg19c.sh` and `queue_reg19d.sh`);
- with stderr in session bc2fcf6d's scratchpad (FILE(docs/probe/20261111_reg19/ops/queue_reg19.sh:6));
- before the seal (72fafb5, 2026-11-12 19:00 UTC; DERIVED from `git log`).

Replace "(`analysis.gate reg19_step` from the pinned worktree after each seed, its stdout saved whole in `state/reg19_step_out_s<seed>_<stamp>.txt` and reduced to `done` and `continue`, FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:75);" with:
> (`analysis.gate reg19_step` after each seed: for seeds 15 to 17 by the queues of 2026-11-11/12 (`docs/probe/20261111_reg19/ops/queue_reg19*.sh`) from the main checkout, before the seal existed, with stdout reduced by `tail -1` and stderr saved in session bc2fcf6d's scratchpad (FILE(docs/probe/20261111_reg19/ops/queue_reg19.sh:9), FILE(docs/probe/20261111_reg19/ops/queue_reg19.sh:30)); from seed 18 on by `ops_r3/queue.sh` from the pinned worktree, its stdout saved whole in `state/reg19_step_out_s<seed>_<stamp>.txt` and reduced to `done` and `continue`, FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:75), FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:77);

**(b) The stated limits omit blind spots shown on synthetic inputs.** These were run with `search2.py` at 723a16b (DERIVED, /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/353762fb-0527-49f6-9a2c-1db84d1c97b0/scratchpad/r11/synth_out.txt):
- `$PY -m analysis.gate reg19`, the way `final.sh` runs REG-19's table, gives no line at all;
- `uv run /path/x.py` without `python` gives none;
- an ssh read of a harness log by a glob or by `ls -t | head -1` that names no run id or config gives no record;
- so does `tmux capture-pane` on the VM;
- so does a Read of a note that quotes run lines.

Replace "Its stated limits: commands run by hand outside these sessions, the commands inside shell scripts (listed only as runs of those scripts), and reads by code a script imports from another file." with:
> Its stated limits: commands run by hand outside these sessions; the commands inside shell scripts (listed only as runs of those scripts); reads by code a script imports from another file; `.py` files whose writing no transcript shows (`ran_unknown`); spellings its expressions miss, among them a module run through a shell variable (`$PY -m …`, the way `final.sh` runs REG-19's table), `uv run <file>.py` without `python`, a star import, a harness-log read on the VM by a glob or `ls -t` that names no run id or config, and `tmux capture-pane`; and reads of notes or files that quote a run's lines (DERIVED by rule F round 11 on synthetic inputs).

**(c) Which `search2.py` runs at E.** D16 says "committed in `723a16b`", but the version the [CORR] relies on is d960ef3's (FILE(docs/decisions.md:4453), "Fixes"). Replace "(committed in `723a16b`; BH8, BG5(b))" with:
> (committed in `723a16b` and fixed in `d960ef3`; the rerun at E uses the version at E, whose commit and `shasum -a 256` head its output; BH8, BG5(b))

**(d) Reads that REG-21's draft 25 discloses and draft 16 lacks.** REG-21's items (vii) to (ix) (FILE(docs/drafts/review_bundles/reg22_r11/reg21_draft25_for_comparison.md:54)) are missing, among them `ls -la | head -30` and the hidden files of seed 16's control, file counts, checksums at 19:56–19:57 UTC and 00:28 UTC, and fdf13821's 17:53:11 listing. So D16:80's "no other read … beyond names, validity and the names of failed checks" is false. The 17:56:24 UTC listing of the [CORR] at FILE(docs/decisions.md:4453) is missing too.
- Insert REG-21's items (vii)–(ix) verbatim, with the 17:56:24 listing.
- Replace "no other read of a REG-19 run's files or logs beyond names, validity and the names of failed checks" with:
  > no other read of a REG-19 run's files or logs beyond names, validity, the names of failed checks and the sizes, file counts, checksums and configuration lines listed above
- After "on `main` the seal has refused such runs since `72fafb5` (FILE(analysis/load.py:20))", add:
  > unless `AFTERSHOCK_UNSEAL` names REG-19 (FILE(analysis/withheld.py:51)), as REG-19's queue and `final.sh` do

**For BK6 as a whole:**
- **Owner-proxy pass:** (a) and (c) no, as wording and a tag; (b) and (d) yes, because they change what "What was known" and the trigger's search cover.
- **Batch 2's standing:** no.
- **Class:** (a) wording (a false statement corrected); (b) and (d) a disclosure; (c) a tag.

## 3. `closure.py` and `search2.py`: what each can miss, and whether the draft's statements about them are true

**`closure.py`.**
- D16:133's description is true: `from <package> import <name>` is tried as `<package>/<name>.py`, relative imports are resolved, and dynamic imports are printed (FILE(docs/probe/20261113_freeze/closure.py:12), FILE(docs/probe/20261113_freeze/closure.py:77), FILE(docs/probe/20261113_freeze/closure.py:88)). The one dynamic import it flags is `__import__("os")` in `harness/env_snapshot.py`, which is harmless.
- It cannot see:
  - non-Python files read at run time, for example `docs/decisions.md`, read by `withheld.lifted` (FILE(analysis/withheld.py:47)). That file is append-only and cannot be frozen; it gates only.
  - installed packages, which are fixed only if the venv is synced to the frozen `uv.lock`;
  - `.pth` files, `PYTHONPATH` and `sitecustomize`.
- None of these is a trace on which the frozen code computes differently without a git trace, except an unsynced venv (BK-O4).

**`search2.py`.** See BK5 and BK6(b)–(c). The draft's statements of what it adds are true. Its statements of what it can miss are incomplete (BK6(b)). D16:81's use of it is not supported (BK5).

**The dry-run's class counts as I read them:** 7 `ran_on_reg19`, 2 `reg19_read`, 1 `ran_unknown` (PROBE(docs/drafts/review_bundles/reg22_r11/transcript_search2_dryrun_20261113T162249Z.txt:3), :4).
- The three `ran_on_reg19` hits beyond rule F round 10's four (T(8c5f8396/agent-af3cd85f0f63adbb0:157), :200; T(8c5f8396/agent-aea70a41daaffaecd:119)) must be classified in the [DECISION] (delegate) as BG-O3 asks. I did not classify them.
- The `-m analysis.c2` at T(8c5f8396/agent-a43b6d3c375ffd53e:737) is a grep pattern, not a run.
- The two `analysis.gate reg19_inputs` runs (T(41a5ee70:200), T(f6210500:124)) read configs only (FILE(analysis/gate.py), `reg19_inputs` at a7bb77a).

## 4. Strongest alternative explanation, and whether the analysis can change a decision

**For any `loop` count:** a queue that the load alone sustains gives the same four links. The pool holds about 30 requests, and a full pool evicts prefixes (D16:9). Only PROTOCOL §3's conditions 2, 5 and 6 and the loop-cut controls separate the two. The draft says so.

**For a disagreement between batches:** batch 1 runs have up to 4 judged spans each (D16:84, 54 spans over 11 runs), and batch 2 runs up to 9 (D16:85). `not_sustained` needs one failing span, so at the same per-span rate a batch-2 run is less often `loop`. At the pessimistic 3.7 % per span, a run is `loop` with probability 0.86 at 4 spans and 0.71 at 9 (DERIVED: 0.963⁴, 0.963⁹). So a disagreement can come from span count alone (BK-O6).

**Can it change a decision?** Yes, at λ = 2.0, through line a (D1/D2 permission), line d, line e's duty and the disagreement test: P ≈ 0.05 for batch 1 (BELIEF) and ≈ 0.002–0.084 for batch 2 (DERIVED, D16:11).
- Under the stop, batch 2 still enters the disagreement test as a computed batch (BC1), so that probability is unchanged. What the stop removes is any sentence resting on batch 2 alone, and with it the only reading of condition 4 registered before its data. That cost is to the paper's claim C2, not only to its words. I disagree here with "that would cost little" (FILE(docs/drafts/reviews-2026-11-13/proxy-reg22-draft15-delta.md), notes for the owner).
- BK3 adds a window, from S to batch 2, in which neither line a nor line d applies by itself.

## 5. The two review-stop entries (delegate decisions)

**BK-S1. When the further entry is committed.** The amendment applies items against either entry "by a further entry before any batch is computed" (FILE(docs/decisions.md:4437), its "order" item). The rule decides what REG-22's text becomes, so it must be settled before E.
- Replacement: "before E of either registration, and REG-21's and REG-22's entries cite it".
- Class: a stricter rule. Owner-proxy pass: yes.

**BK-S2. Part (2) and REG-22's owner-proxy disagree, and neither entry says which holds.**
- REG-22's owner-proxy classed a whole kind of change in advance: "A pass for any change to fact (1), fact (2) or the validity freeze beyond BH1, BH2 and BH9. Under the review-stop entry such a change is not wording, so it brings the stop" (FILE(docs/drafts/reviews-2026-11-13/proxy-reg22-draft15-delta.md:160)).
- Draft 16 makes such changes, and its change log says so: the BF1/BF3 sentence and BG3 (D16:218, D16:221).
- Part (2) makes "the class its reviewer states" govern. These changes' reviewers (REG-21's proxy; rule F round 10) classed them as stricter or wording. The amendment applied its rule to round 2 without naming line 160.
- If line 160 governs, round 2 already stopped. The outcome is the same as this round's, but the record must say which reading was used.
- Add to part (2): "Where two reviewers of the same registration class one change differently, or one classes a kind of change in advance, the class that is none of wording, a tag, a stricter rule or a reporting duty holds; applied to round 2, REG-22's owner-proxy's line 160 makes draft 16's changes to fact (2) and the validity freeze beyond BH1, BH2 and BH9 a stop from round 2, with the same effect as round 3's."
- Class: a stricter rule and a disclosure. Owner-proxy pass: yes.

**BK-S3. Who states whether an item is "about batch 2's standing"?** Item 3 lists the scope, and part (2) settles the class, not the standing.
- Add: "Whether an item is about batch 2's standing is stated by its reviewer; where none states it, the owner-proxy of the same round states it; an item no one has stated counts as about batch 2's standing."
- Class: a stricter rule.

**BK-S4. What the text after the stop keeps.** Item 4 gives that text "its own rule F review and owner-proxy pass" but does not say what it keeps.
- Under BC1 a retrospective batch 2 is still computed and still withholds lines, so the freeze, facts (1) and (2) (with BK2's commands), the validity cut at S and BG4 still decide whether it is computed and under which cause words.
- Add: "The text written under item 4 keeps the freeze, the two facts, the validity cut and the not-computed rules, which decide whether batch 2 is computed and with which words; items of its review are applied as usual, and no further stop exists."
- Class: a stricter rule.

**BK-S5. "Selects on no data" needs a qualifier.** The entry is free of run data. But part (2) was adopted after round 2's items were known and was then used to class them (FILE(docs/decisions.md:4437)): a rule chosen after seeing what it judges (rule A5, in kind).
- Add to the amendment: "Part (2) was adopted after round 2's items and their reviewers' classes were known, and applied to them."
- Class: a disclosure.

**BK-S6. Item 5's check has no command.** "The entry is committed before the first commit that adds a `reg19_final_*` file", read by part (1), names no command.
- Name BK2's three commands there, with `--no-renames`.
- Class: a stricter rule.

## 6. Optional items

- **BK-O1.** In fact (1), also print `git merge-base --is-ancestor E B && echo ancestor` (B descends from E) and `git diff --stat E B -- <frozen files>` (the net change, as a check on the log).
- **BK-O2.** In fact (2), add `--reflog` to the `git log`, so that an older stash entry or an unreachable commit adding a table file counts. `--all` sees only `refs/stash`'s top entry (BELIEF from git's documentation; not tested).
- **BK-O3.** "Lines a, e and h quote the frozen output" (D16:133) should also name line d, "Batches that disagree at λ = 2.0" and batch 1.
- **BK-O4.** Print `uv --version`, and print `python -c 'import analysis, numpy; print(analysis.__file__, numpy.__version__)'` into the batch file, so that a shadowed `analysis` or an unsynced venv shows. `uv run --locked` stays declined, as D16 says.
- **BK-O5.** "BG2).." at D16:133 should be "BG2).".
- **BK-O6.** Beside any disagreement, give each batch's judged-span count and its count of failed spans (the span-count alternative in §4).

## 7. Not checked

- The contents of `RESUME.md`, of the queue and probe outputs, and of `docs/probe/**/state/`: forbidden.
- Nothing under `runs/` beyond folder names.
- No tool output inside any transcript.
- The VM's shell history and any Claude session on the VM.
- Commands run by hand outside these sessions.
- The context pack's contents.
- The full `uv run pytest` suite and `tools/check_docs.py`.
- REG-21's draft 25 beyond lines 54 and 104.
- `docs/decisions.md` beyond the lines cited (4205, 4276, 4279, 4406–4500).
- PROTOCOL, claims and status (rule F isolation).
- Whether vLLM writes the patterns of read (ii) only at start-up.
- Whether `gate.reg19` prints per-run labels.
- The classification of the 3 new `ran_on_reg19` hits and of every `names_reg19_run` hit.
- `search2.py` at d960ef3 on my synthetic inputs (I ran 723a16b's).

Nothing was written to the repository.
