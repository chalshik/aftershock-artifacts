# proxy-reg22-draft15-delta (proxy-reg22-d15), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T16:01:10.714Z). Item names as given by the reviewer (prefixes BE, BF, BG, BH were assigned in the round-2 review prompts).

---

Owner-proxy on REG-22 draft 15 (round 2 on the freeze): APPROVE on BH1–BH10 (BH10 LATER, the rest BEFORE the entry is appended).

**Decision: APPROVE**, on BH1–BH10. This approval has no effect while rule F round 10 on draft 15 is outstanding or NOT READY.

d15 = FILE(docs/drafts/review_bundles/reg22_r10/registration_draft15.md). It is byte-identical to docs/drafts/reg22_draft15.md (`cmp`). HEAD is ba67e55.

**What I checked myself, in git and on disk:**
- `git log --all --diff-filter=A --name-only -- ':(glob)**/reg19_final_*'` lists 9 commits, ab6988f (2026-11-13 11:15:31 UTC, %ct 1794568531) to ba67e55. Every file they add is a review-bundle copy named `reg19_final_sh_for_reference.sh`.
- `find . -name 'reg19_final_*' -not -path './.git/*'` (runs/ excluded) lists 15 such copies and no table file.
- `final.sh` names its files `reg19_final_$ts.txt` and `reg19_final_err_$ts.txt` (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20)). `$ts` is `YYYYMMDDTHHMMSSZ_<pid>_<n>` (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:42)).
- The import closure of `analysis/c2.py` by `ast`, function-level imports included, has 24 code files. The draft's list has 21. It misses `harness/env_snapshot.py`, `harness/loadgen.py` and `harness/trigger.py`, which `harness/run.py:23–24` imports. `gate.py:751` and `k3.py:395` import `harness.run` inside functions. `.python-version` (3.12.13) is tracked and is not in the list. `analysis/__init__.py` and `harness/__init__.py` are 0 bytes.
- `CHECKS_COMMIT` is at common.sh:30 and `ALLOWED` at common.sh:36. The draft cites :28 and :34; the quiet-hours patch (ea4a25e) moved them. final.sh:20 and :29, load.py:11 and :20 are correct. The bundle's three REG-19 scripts are identical to `ops_r3/`.
- REG-21 draft 24 (the bundle copy) has the same `reg19_final_*` glob and the same six harness files.
- The review-stop entry is at docs/decisions.md:4406 and the [CORR] at :4420. The plan's stop rule is summarized at :4342.
- The transcripts: I wrote my own scripts, kept in the scratchpad. They print tool-call **inputs only** for every transcript since 2026-11-12. I opened no tool output, no run folder and no queue output. Findings are under question 5.

## 1. BD1–BD7

- **BD1: met.** Line 91 uses rule F's BC1 words, which mean the same and are stricter. The edits at lines 131 and 149 are made.
- **BD2: met.** Line 5 is verbatim. The d14:80 phrase is gone. Line 91 says "the looks", not "one look"; that is accurate, since two reads are now listed.
- **BD3: reworded, so it needs this pass. Accepted in design, with BH7 and BH8.** Draft 15 narrows the trigger: a run of `analysis/` code on any REG-19 folder, or a read of a line that a REG-19 burst run wrote after its burst began. BD3 had any read beyond ALLOWED of any REG-19 log. I accept the narrowing:
  - batch 2's labels come from burst runs only;
  - the thresholds are frozen from E;
  - control looks are still disclosed.
  The search behind the trigger, and the list of reads, are both incomplete (question 5).
- **BD4: met as asked. The list is still short** of its own definition (BH2).
- **BD5: reworded and broader, so it needs this pass. Accepted with BH1.** The earliest stamp over the working tree, all refs and decisions.md quotes is monotone. Each added name can only make fact (2) fail. The stash trick of BC2's trace 2 does not change S, because S is read from the name, not from the commit. As written, though, the glob catches the bundle copies.
- **BD6: reworded, so it needs this pass. Accepted with BH5.** "A new function or file" contradicts the whole-file freeze.
- **BD7: reworded** ("frozen files" in place of "judged path"). It is stricter, so it is accepted.

## 2. Does the review-stop entry meet BD8? Yes.
- Item 5 states all of these:
  - the same command, run once;
  - the path frozen at the entry, and the entry's decision lines;
  - no code or threshold change (A5 binds a retrospective batch too);
  - the entry committed before the first `reg19_final_*` commit.
- The owner gave no words on the stop rule beyond approving the plan. The entry cites the plan (decisions.md:4342).
- Its reading of "fixed once" is faithful and somewhat stricter than the plan's: a round-2 NOT READY with a non-wording item on batch 2 already stops.
- **One gap: process.** It is a [DECISION] (delegate) committed in ba67e55 with no rule F review and no owner-proxy pass of its own. The delegation requires both for each delegate decision. Fix: BH10.
- **Under it, BH1–BH9 do not trigger the stop.** They are wording, a tag, a stricter rule, a disclosure or a reporting duty. BH1 narrows a pattern; I count it as wording because it names the files the text already means. On the literal reading, fact (2) already fails today on files nobody intends (see BH1).

## 3. BC1–BC3 as written: acceptable, with BH1, BH3, BH4 and BH9

**BC1.**
- Line 133 gives REG-22 its own meaning of "retrospective", and that is right: the label can move only the standing words, never a decision line.
- I checked this against the lines: when the batches disagree, primary and retrospective act the same; when both meet line a, batch 1's sentence stands either way.
- Line 80 still says "never governs", which is REG-21's term and exactly what BC1 removed. Fix: BH3.

**BC2 (the new fact (2)).**
- The design is sound.
- The literal glob makes the ancestry clause fail at E. That happens because ab6988f…ba67e55 add files named `reg19_final_*`, and every one of them will be an ancestor of E.
- It also makes ab6988f "the first commit that adds a `reg19_final_*` file". That opens "Runs"'s not-computed window now (line 64) and empties the window of the validity freeze (line 133). Fix: BH1.

**BC3 (validity freeze).** Accepted, including the added exception for reruns of lost or invalid runs under REG-19's rules. A gap remains: an entry that marks a REG-19 *control* invalid beyond the checks can drop a seed from n. "Runs" then ends batch 2 instead of relabelling it. That act needs the owner (it is not delegated), so I ask only for a reporting duty (BH9).

## 4. Whole-file freeze of c2's import closure: acceptable, with BH2
- It is the mechanical rule the owner asked for: no hunk is ever argued.
- The cost is known before any data, and the owner should see it:
  - Until both batch 2s are computed or declared not computed, nothing on `main` may change `harness/run.py`, `recorder.py`, `checks.py`, `config.py`, `workload.py`, `loadgen.py`, `trigger.py`, `env_snapshot.py`, `.python-version`, `pyproject.toml`, `uv.lock` or the 15 analysis files.
  - REG-20 and every later code change go into new files, or wait.
- Every pending seal is already in `withheld.SEALS` (FILE(analysis/withheld.py:26)), REG-20's two included.

## 5. Is the disclosure honest and complete? Honest in intent, not complete. Fix: BH7 and BH8.

**Reads the draft omits** (tool-call inputs, my extraction):
- (i) The command of 2026-11-12 11:45:33 UTC (bc2fcf6d…jsonl:10177) also ran `cd …/runs/20261112-103423_stage2_control_l1pl350cl_r2.0_w3000_s17 && ls -la && tail -3 events.jsonl` on the VM. At 11:50:49 UTC (:10195) the same session printed `head -c 300` of that run's `checks.json`.
  - The [OPS] entry at decisions.md:4274–4280 records only the harness-log lines.
  - The events the harness writes last are `load_end`, `gpu_processes_end`, `stopped` and `checks` (FILE(harness/run.py:202), FILE(harness/run.py:219)). None carries a rate, hit share or queue length (DERIVED from the source; I did not see the printed lines).
- (ii) At 17:58:13 and 17:58:25 UTC, the context-pack subagent (agent-ad7b5aba…jsonl:154, :157) ran two loops over every folder in `runs/`. REG-19's six runs were present then. The loops printed each run's `env.json` `nvidia_smi` field and the first `GPU KV cache size` line of its `server.log`. These are start-up data, consistent with the draft's account of (ii), but not listed.

**The search does not cover what it is cited for.**
- `search.py` registers a script only when a Write call wrote it. A `.py` file written by a shell heredoc (`cat > x.py <<'EOF' … EOF; python x.py`) is never seen as run.
- By my count, 35 such scripts were run since 2026-11-12, and none appears in the saved output. 21 of them name `find_runs`, among them the c2 reviewer scripts `t01`–`t10`, `guarded_pytest.py` and `trace_main.py`.
- So line 81's "every reviewer script that called `c2` functions replaced `find_runs` … first" is not shown by the PROBE it cites.
- Its REG-19 file regex also missed the `cd <folder> && tail events.jsonl` above.
- My own reading, for the record: the substance holds.
  - 19 of the 21 replace `find_runs` with synthetic runs or a stub.
  - `s57_heavy.py` (context pack, 2026-11-12 18:00:40 UTC, before the seal) skips every folder whose name holds `w3000`.
  - `f_pooled_between.py` stubs `find_runs` to raise.
  - I found no run of `analysis/` code on a REG-19 folder and no read of a burst run's post-burst lines.
  - The 2026-11-12 server.log greps of seed 17's burst run used start-up patterns: line 14 only, or `| head` (10) and `| head -14`.

## 6. Would the owner approve registering this?
Yes, once BH1–BH9 are written in and rule F round 10 is not NOT READY on batch 2's standing.
- The design is right: the entry commit is the cut, the code is frozen whole, and looks are disclosed, not switches.
- The defects are mechanical. BH1 matters most: as drafted, fact (2) fails on the review bundles before any data exists.

## Conditions

**BH1 (BEFORE; REG-21 too). What "a `reg19_final_*` file" is.**
In line 133, replace:
> let S be the earliest UTC stamp in the name of any file named `reg19_final_*`, among the files of that name anywhere in the repository's working tree (`find . -name 'reg19_final_*' -not -path './.git/*'`), every name that any commit on any ref adds (`git log --all --diff-filter=A --name-only --format='%H %ct' -- ':(glob)**/reg19_final_*'`), and every such stamp a decisions.md entry quotes.

with:
> a REG-19 table file is a file named `reg19_final_<stamp>.txt` or `reg19_final_err_<stamp>.txt` whose `<stamp>` begins with a UTC time `YYYYMMDDTHHMMSSZ` (the names `final.sh` writes, FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20), FILE(docs/probe/20261113_reg19/ops_r3/common.sh:42)); other names matching `reg19_final_*`, such as the review bundles' `reg19_final_sh_for_reference.sh` (committed since `ab6988f`), are not table files and are listed as such. Let S be the earliest such UTC time among the table files anywhere in the repository's working tree (`find . -name 'reg19_final_*.txt' -not -path './.git/*'`, table-file names only), every table file that any commit on any ref adds (`git log --all --diff-filter=A --name-only --format='%H %ct' -- ':(glob)**/reg19_final_*.txt'`, table-file names only), and every such time a decisions.md entry quotes for a table file.

In the same sentence, replace "no commit that adds such a file is E or an ancestor of E" with "no commit that adds a table file is E or an ancestor of E". After it, add:
> Everywhere else in this entry ("Runs", the duties, the limits, the validity freeze), "a `reg19_final_*` file" and "every file named `reg19_final_*`" read "a REG-19 table file" and "every REG-19 table file".

**BH2 (BEFORE; REG-21 too, with its own closure). The frozen list equals its definition.**
In line 133, replace "and the two files that fix the environment:" with "and the three files that fix the environment:". Then replace:
> `harness/__init__.py`, `harness/checks.py`, `harness/config.py`, `harness/recorder.py`, `harness/run.py`, `harness/workload.py`, `pyproject.toml`, `uv.lock` (23 files)

with:
> `harness/__init__.py`, `harness/checks.py`, `harness/config.py`, `harness/env_snapshot.py`, `harness/loadgen.py`, `harness/recorder.py`, `harness/run.py`, `harness/trigger.py`, `harness/workload.py`, `pyproject.toml`, `uv.lock`, `.python-version` (27 files; `harness/run.py` imports `env_snapshot`, `trigger` and `loadgen` at its top, FILE(harness/run.py:23), and `gate.py` and `k3.py` import `harness.run` inside functions). If the closure computed at E differs from this list, the union is frozen and the [DECISION] (delegate) prints both.

In line 210, replace "(23 files, the two `__init__.py` included)" with "(27 files, the two `__init__.py` and `.python-version` included)".

**BH3 (BEFORE). Line 80 keeps BC1's meaning.**
Replace:
> Batch 2 is primary only if the stopping rule's facts (1) and (2) hold; otherwise it is labelled retrospective and never governs: wherever a batch's standing is given it reads "retrospective" (the stopping rule).

with:
> Batch 2 is primary only if the stopping rule's facts (1) and (2) and its validity freeze hold; otherwise it is labelled retrospective, with the effects the stopping rule gives (it enters the disagreement test at λ = 2.0 as a computed batch, and no sentence rests on it alone).

**BH4 (BEFORE). The standing words name the cause.**
- In line 91, replace `otherwise "retrospective (fact (1)/(2) failed)"` with `otherwise "retrospective (<fact (1) | fact (2) | the validity freeze | by design>)", naming each that applies`.
- In line 133, replace `it reads "retrospective (fact (1)/(2) failed)"` with `it reads "retrospective (<fact (1) | fact (2) | the validity freeze | by design>)", naming each that applies`.

**BH5 (BEFORE). BD6 under a whole-file freeze.**
In line 133, replace "a fix goes into a new function or file, run by its own saved command" with:
> a fix goes into a new file outside the frozen list (a new function in a frozen file is a change to it and fails fact (1)), run by its own saved command

**BH6 (BEFORE). Tags.**
- Replace "FILE(docs/probe/20261113_reg19/ops_r3/common.sh:28)" with "FILE(docs/probe/20261113_reg19/ops_r3/common.sh:30)".
- Replace "FILE(docs/probe/20261113_reg19/ops_r3/common.sh:34)" with "FILE(docs/probe/20261113_reg19/ops_r3/common.sh:36)".

**BH7 (BEFORE). The omitted reads.** In line 80:
- After "read about the last 15 lines of seed 17's control's harness log", insert:
  > (in the same command, at 11:45:33 UTC, it listed that run's folder with sizes, `ls -la`, and printed the last three lines of its `events.jsonl`, whose last events by the harness's code are `load_end`, `gpu_processes_end`, `stopped` and `checks`, none carrying a rate, hit share or queue length, FILE(harness/run.py:202), FILE(harness/run.py:219); at 11:50:49 UTC it printed the first 300 characters of that run's `checks.json`)
- After "printing its line 14, the engine's configuration line.", insert:
  > At 17:58:13 and 17:58:25 UTC the same subagent ran two loops over every folder in `runs/`, REG-19's six then present included, printing each run's `nvidia_smi` field of `env.json` and the first `GPU KV cache size` line of its `server.log`.

**BH8 (BEFORE the rerun quoted at the append; disclosure). The search covers what it is cited for.**
The rerun at this entry's commit is made with a new file, `docs/probe/20261113_transcript_search/search2.py`. It is `search.py` plus:
- (a) a `.py` file written by a shell redirection (`cat`, `tee` or `printf` … `> f.py`, heredoc bodies included) registers as a script, as a Write call does;
- (b) scripts are collected from every transcript before any run is matched;
- (c) a python run of a `.py` file outside `analysis/` and `tests/` whose writing it did not see is listed as `ran_unknown`;
- (d) every tool call whose input names a REG-19 run id (regex `[0-9]{8}-[0-9]{6}_[A-Za-z0-9_.]+_w3000_s1[5-9]`) is listed as `names_reg19_run`.

Its output is saved and committed beside the first. The [DECISION] (delegate) classifies every `ran_unknown` and `names_reg19_run` hit. Lines 80 and 81 cite both outputs. Line 81's sentence on reviewer scripts cites `search2.py`'s output.

**BH9 (BEFORE; a reporting duty). Control flags.** After "The batch-2 [RESULT] lists every such flag with its entry.", add:
> It also lists every change after E to the validity flag of a REG-19 control run (`*_stage2_control_l1pl350cl_r2.0_w3000_s1[5-9]`) other than by the harness's checks or the recheck, with its entry, beside batch 2's standing; such a change marks a run invalid beyond the automatic checks and needs the owner.

**BH10 (LATER: in the [DECISION] (delegate) that approves this entry, and before it is appended).**
1. The [DECISION] (delegate) states that the review-stop entry (decisions.md 2026-11-13, ba67e55) was committed as a delegate decision without its own rule F review and owner-proxy pass, which the delegation requires. It records that this pass approves its content for REG-22 (BD8 met), and quotes rule F round 10 on it, or says rule F has not reviewed it.
2. A [CORR] to decisions.md 2026-11-13 [OPS] (the interim look of 2026-11-12) adds the `ls -la`, `tail -3 events.jsonl` and `head -c 300 checks.json` reads of BH7.
3. The BD9 mapping is extended to BH1–BH10.

## Which later changes need another proxy pass
- **None** for BH1–BH10 if written as given. A longer frozen list under BH2 needs none either.
- **A pass** for any other wording of BH1, BH3 or BH5.
- **A pass** for any change to fact (1), fact (2) or the validity freeze beyond BH1, BH2 and BH9. Under the review-stop entry such a change is not wording, so it brings the stop: batch 2 becomes retrospective by design.
- **A pass** if `search2.py`'s rerun classifies any hit as other than synthetic, stubbed or excluded. The draft's own rule then sends the text to rule F and a proxy anyway.
- **Rule F round 10's items:** no pass if they are wording, a tag, something stricter or a reporting duty; a pass otherwise.

## Notes for the owner
- **Fact (2) as drafted fails on the review bundles,** before any data exists. BH1 fixes it. I count BH1 as wording, so it does not trigger the stop. If you count it as a change of design, the review-stop entry makes batch 2 "retrospective by design". That would cost little: under BC1 the label moves only the standing words.
- **REG-21 draft 24 has the same glob and the same short harness list.** Its proxy should get BH1 and BH2.
- **The freeze now holds the run harness on `main`** (`run.py`, `loadgen.py`, `trigger.py`, `recorder.py`, `checks.py`, …) and the interpreter pin until both batch 2s exist. Any harness change for REG-20 or later runs goes into new files or waits.
- **The transcript search's blind spot is real; nothing I found contradicts the disclosure.** I re-checked, inputs only, the 35 scripts it cannot see. None ran on a REG-19 folder.
- **The thresholds were set while seeds 15–17 existed** (c2.py first committed 44ca82a, 2026-11-12 19:36 UTC; the seal on `main` from 72fafb5, 19:00 UTC). Batch 2's case still rests on no one having looked at them before. With BH7 and BH8 that rests on a search that covers what it claims, with its limit (hand commands) stated.
- **Pushing `main`** is still the only outside witness against rewritten history. That is your choice.

## Not checked
- Rule F round 10 on draft 15.
- REG-21 draft 24 beyond its harness list and its glob (grep only).
- Any tool output in the transcripts. I read tool-call inputs only, so I have not seen what (i) and (ii) printed.
- Whether `search.py` reproduces its saved output (not rerun).
- `pytest` and `check_docs`.
- VM commits and VM logs.
- The full plan text `docs/drafts/plan_2026-11-13.md`. I read the decisions.md summary at :4342 only.
- `runs/`, the backups, `state/` contents, queue and probe outputs, and RESUME.md (none opened).

Nothing was written into the repository. My scripts are in the session scratchpad only.
