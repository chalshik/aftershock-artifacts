# proxy-reg22-draft16-delta (proxy-reg22-d16), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T17:12:12.526Z; message 1 of 2 from this teammate). Item names BL1–BL4 are this round's.

---

Owner-proxy on REG-22 draft 16 (round 3 on the freeze, the last): APPROVE on BL1–BL4 (BL4 LATER, the rest BEFORE the entry is appended). Batch 2 is labelled retrospective (by design) from the entry.

**Decision: APPROVE**, on BL1–BL4.
- On batch 2's primary standing my answer is no (BL1). This gives the outcome the review-stop rule gives: batch 1 registered, batch 2 retrospective by design.
- This approval has no effect while rule F round 11 on draft 16 is outstanding. Its items are handled as "Which later changes need another proxy pass" says.

d16 = FILE(docs/drafts/review_bundles/reg22_r11/registration_draft16.md). It is byte-identical to docs/drafts/reg22_draft16.md (`cmp`). The bundle's commit is 90cd0a9. HEAD at my last check is 8a3e059 (2026-11-13 16:47:50 UTC). No commit from 90cd0a9 to HEAD touches `analysis/`, `harness/`, `pyproject.toml`, `uv.lock` or `.python-version` (`git diff --stat`, empty).

**Change of position (rule A4).** I came into this round reading the s57_inv.py look (read (iii) below) as a disclosure that leaves batch 2 primary. I changed that for a better argument, and new evidence agrees.
- **The argument.** d16 lists that read only as reading "names, configs, validity and sizes" (d16:80). d16's trigger fires on "a read of a line a REG-19 burst run wrote after its burst began, beyond what is listed here". The `no_errors` counts in seed 17's burst `checks.json` are such lines, and the listing said they were not read. A listing that misstates what a look read cannot cover that look.
- **The new evidence.** The agent's [CORR] (FILE(docs/decisions.md:4453), d960ef3) and its reading in `agent/STATE.md` (f3abd23) say the same.
- **The predecessor's rule.** It also asked for a pass for any hit classed other than synthetic, stubbed or excluded. This hit is none of those.

## 1. BH1–BH9 and the named departures
- **BH1–BH9: met as written.** I checked each condition's replacement text against d16 as a string.
- **BG3 and BG4, verbatim:** acceptable.
  - BG3 moves the validity cut to S.
  - BG4 counts a batch 2 not computed for a cause at or after S as meeting none of the lines.
  - Both are stricter than the texts they extend.
- **The cross-applied worktree `find` and `--full-history`:** acceptable. Fact (1) is now stricter: a commit hidden by history simplification, or a table file in another worktree, now counts.
- **The sentence equating the table-file set with REG-21's:** acceptable.
  - BH1 names `reg19_final_<stamp>.txt` and `reg19_final_err_<stamp>.txt`. BF1 uses the regex `^reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z`.
  - The two sets are the same for every file `final.sh` writes, because it writes only those two `.txt` names (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20)).
  - Optional, not a condition: fact (2)'s commands could list `reg19_final_*` and filter the names by BF1's regex, rather than glob `*.txt`.
- Under BL1 these facts now decide only which further reasons batch 2's label names.

## 2. BH8, search2.py and "What was known"
- **BH8 (a)–(d) is met in the letter by `search2.py` at 723a16b.**
  - It collects scripts written by redirect, `tee` or heredoc, and scripts changed by Edit, from every transcript before matching any run.
  - It has the `ran_unknown` class, and `names_reg19_run` over every tool's input.
  - It drops the `pytest` skip.
  - It flags globs and loops over `runs/`, `cd` into a run folder, and Grep, Glob and Read under `runs/`.
  - It reads scripts by their syntax tree, with `stubbed` flagged.
  - Its self-test has 16 cases (bundle: transcript_search2_selftest_20261113T162249Z.txt).
- **It has two defects; both are now in the [CORR] at :4453 and fixed in d960ef3.**
  - Any assignment to `RUNS`, `find_runs` or `load_run` earns the label `stubbed`, so `s57_inv.py`'s `RUNS = Path("runs")` was labelled a stub.
  - A string ending in `/runs` was not taken as a path into `runs/`. That missed `s134_runs.py` and `s57_md.py`.
- **A minor third defect:** scripts are matched by basename, so a run of a `noise.py` or `t2.py` is attributed to another script of that name. labels.tsv notes both cases (lines 25–26). BL3 asks that every hit be classified by reading its input.
- **"What was known" in d16 is not honest and complete against the dry run.** The dry run is PROBE(docs/drafts/review_bundles/reg22_r11/transcript_search2_dryrun_20261113T162249Z.txt): 129 files, 7169 calls, 607 records.
  - The dry run holds the 17:59:38 record of s57_inv.py, labelled `stubbed`. d16 describes that read as "names, configs, validity and sizes".
  - d16 does not carry REG-21 draft 25's reads (vii)–(ix) in full.
  - d16 does not say what read (i)'s 300 characters hold.
  - BL2 fixes all three.
- **Could a read have shown a REG-19 burst run's outcome? One could.**
  - s57_inv.py's `tail -3` most likely showed seed 17's burst run's `ok` and `unfinished` (DERIVED from the inputs; output not opened).
  - That is an end-of-run backlog count. It is not REG-19's verdict and not a condition-4 value.
  - We already knew, from `continue` being True after seed 17, that at least one of seeds 15–17 ended stuck. This count could add whether seed 17's burst run ended backlogged.
- **I found no other read showing a burst run's rates, hit share, KV, queue or spans.** I read the inputs of these records:
  - the dry run's 58 Bash records that are `names_reg19_run` only;
  - the three scripts naming `…/aftershock-artifacts/runs`:
    - `s134_runs.py`: config fields, `valid` and failed checks only;
    - `s57_md.py`: only the runs in `s57_heavy.py`'s pickles, and `s57_heavy.py` skips every `w3000` folder;
    - a 2026-11-04 `check_docs` call, made before REG-19 existed;
  - s57_inv.py's three runs.

## 3. The frozen set
- **27 files is the right set.**
  - closure.py's output reproduces: 24 code files plus `.python-version`, `pyproject.toml` and `uv.lock`.
  - An independent `modulefinder` pass from `analysis/c2.py` gives the same 24 repository files.
  - I found no runtime read of a repository file on c2's call path other than run folders and the configs inside them.
  - closure.py flags `__import__("os")` at harness/env_snapshot.py:38. That is the standard library and adds no file.

## 4. The review-stop entries and the [CORR]
- **BH10 item 2: met** by the [CORR] at FILE(docs/decisions.md:4428). It lists the `ls -la`, the `tail -3 events.jsonl` and the `head -c 300 checks.json`.
  - That [CORR] says "`checks.json` is a read REG-19's rules allow". This overstates ALLOWED, which permits `valid` and `failed` only (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:36)).
  - The [CORR] at :4453 corrects this. Nothing more is needed.
- **BH10 item 1: not yet met.** It is LATER by its own terms (BL4).
- **BH10's classes:** items 1 and 3 are reporting duties; item 2 is a disclosure.
- **The order is disclosed honestly.** The order is: the stop entry (:4406), the [CORR]s, then the amendment (:4437). The amendment quotes BF10 and BF9(e) verbatim, quotes the predecessor, and says that rule F rounds 17 and 10 did not review the stop entry.
- **One inexactness, not a condition.** The amendment says BH1 gives "the same definition" as BF1. They differ in form and are the same set only because `final.sh` writes only `.txt` names. d16's bridging sentence states this.

## 5. Would the owner approve registering this?
- **Yes, with BL1–BL4.**
- **Why retrospective.** c2.py and its thresholds were written from 19:34 UTC on 2026-11-12, about 95 minutes after read (iii). The inputs suggest that the author did not see the counts, but that rests on inputs and a keyword count.
- **The cost is small.** Under BC1 the retrospective label moves only the standing words:
  - batch 2 still enters the disagreement test at λ = 2.0;
  - it can still withhold line a's permission and line d's wording;
  - no sentence rests on it alone.
- **Against a primary label.** It would rest on "nobody saw it", which cannot be shown.
- **Batch 1 is unchanged.**

## Conditions

**BL1 (BEFORE; class: a stricter rule. Batch 2 gets the label that the entry's own trigger gives; no code, threshold, run set or fact changes.)**
(a) Line 5. Replace
`batch 2 is the same table once on REG-19's runs, which no analysis is known to have read when this entry was committed (what was seen is under "What was known").`
with
`batch 2 is the same table once on REG-19's runs, which no analysis is known to have read when this entry was committed; a script run before this entry most likely printed two end-of-run request counts of seed 17's burst run, so batch 2 is labelled retrospective (by design) from this entry (what was seen is under "What was known", read (iii)).`
(b) Line 80. Directly after
`Batch 2 is primary only if the stopping rule's facts (1) and (2) and its validity freeze hold; otherwise it is labelled retrospective, with the effects the stopping rule gives (it enters the disagreement test at λ = 2.0 as a computed batch, and no sentence rests on it alone).`
insert
` **Batch 2 is labelled retrospective (by design) from this entry.** Read (iii), made before this entry, read lines that seed 17's burst run wrote after its burst began, beyond the validity that drafts up to 16 said it read; that meets this paragraph's trigger before E (owner-proxy round 3 on the freeze, BL1; FILE(docs/decisions.md:4453)). So batch 2 is never primary. Facts (1) and (2) and the validity freeze are still checked and shown in the batch-2 [RESULT], and its label names each of them that fails besides "by design"; the effects are the stopping rule's.`
(c) Line 91. Replace
`batch 2 "registered before REG-19's table", only if both facts of "Batch 2 is primary only if" hold (stopping rule); otherwise "retrospective (<fact (1) | fact (2) | the validity freeze | by design>)", naming each that applies;`
with
`batch 2 "retrospective (by design<; fact (1) | fact (2) | the validity freeze>)", naming "by design" always and each fact that also fails (stopping rule; read (iii) of "What was known"), with decisions.md 2026-11-13 [CORR] "Two reads of REG-19's seed 17" cited;`

**BL2 (BEFORE; class: a disclosure.)**
(a) Line 80. Replace
`between 17:56 and 17:59 UTC the context-pack subagents also printed the `source_config` line of every run folder's `config.yaml` and ran an inventory of every folder's `config.yaml` and `checks.json`; and on 2026-11-12 at 10:13 and 10:14 UTC the session that ran the queue printed the sizes of seed 16's folders and the byte size of seed 16's partial metrics file while it was being copied. These read names, configs, validity and sizes (DERIVED from the command texts; the agent has not read their output, BELIEF: the agent's own report).`
with
`between 17:56 and 18:09 UTC the context-pack subagents also printed, for every run folder, its `config.yaml`'s `source_config`, `sweep_parent` and `name` and its `checks.json`'s `valid` and failed checks (`s134_runs.py`, three runs, and a table built from its output; REG-21 draft 25's reads (iv) and (ix); FILE(docs/decisions.md:4453)), and ran `s57_inv.py`, read (iii) below; and on 2026-11-12 the session that ran the queue read sizes and listings while seed 16's runs were being copied to the Mac: at 10:13:22 UTC the size (`du -sk`) of both seed-16 folders on the Mac and on the VM, at 10:13:27 the control folder's growth over 30 s, at 10:14:02 `ls -la | head -30` of the control folder and a listing of its hidden files, and at 10:25:28 an `ls -la` of the burst run's metrics files on the Mac (REG-21 draft 25's read (vii)). Further, names and validity only (REG-21 draft 25's reads (viii) and (ix)): at 17:53:11 UTC session fdf13821 listed the file names in the last run folder by name; at 17:56:16 one of its subagents listed the same folder and printed the lines of its `config.yaml` that match `config_path`, `source`, `extends` or `^name`, and at 17:56:24 a subagent listed it again (file names only); that folder is seed 17's burst run (DERIVED: it is still the last folder name in `runs/`); the number of files and `checks.json`'s `valid` of each REG-19 folder then on the Mac (session d4d16c2c at 10:30 UTC and session fdf13821 at 13:58 UTC); `valid` and the names of failed checks in loops by the context-pack subagents between 17:58 and 18:11 UTC; the agent's links into the pin worktree with the six runs' `valid` at 18:41 UTC; the copy of seed 18's lost first control to a holding folder with a checksum of every file at 19:56–19:57 UTC; and the agent's read-only VM read of 2026-11-13 at 00:28 UTC (folder names, `valid` and `failed`, checksums). Apart from read (iii), these read names, configs, validity, the names of failed checks and sizes (DERIVED from the command texts; the agent has not read their output, BELIEF: the agent's own report). (iii) **One read printed more than validity, from a file that a burst run wrote after its burst** (FILE(docs/decisions.md:4453), Read 1). At 17:59:38 UTC the context-pack subagent `agent-a48736828ce71b739` of session fdf13821 ran `s57_inv.py`. The script assigns `RUNS = Path("runs")`, reads every folder's `config.yaml` and `checks.json`, and takes from the `no_errors` check its request counts `ok` and `unfinished` (FILE(harness/checks.py:67), FILE(harness/checks.py:69)). It printed `tail -3` of a table sorted by folder name: most likely seed 17's control row and burst row, counts included, and a count line (DERIVED from the inputs, PROBE(docs/probe/20261113_transcript_search/inputs_s57_inv.txt); the output was not opened). `unfinished` counts the requests still waiting or running when the run stopped, so for a burst run it bears on whether its waiting line emptied; `ok` over the run's length is its mean completion rate (DERIVED). Neither is REG-19's verdict, and neither is a span value, a hit share, KV or a link that this table judges. At 17:59:48 UTC the subagent blanked both counts for every `w3000` folder and ran the script again into the same file, and again at 17:59:58 UTC; the parent session read that file at 18:07:14 UTC, after both overwrites (DERIVED from the commands). No assistant text, Write input or Edit input of that subagent, its final report included, has a line that names a REG-19 folder together with `ok` or `unfinished` (DERIVED: a keyword count by REG-22's owner-proxy in round 3 on the freeze, values not printed; a value written without those words would escape it). Session 8c5f8396, which wrote `analysis/c2.py` from 19:34 UTC that day, names `s57_inv` in no tool-call input before 2026-11-13 16:38 UTC (DERIVED from the inputs). REG-19's rules allow reading `checks.json` for `valid` and `failed` only (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:36)). `search2.py` as committed in `723a16b` labelled this script `stubbed` because it assigns to `RUNS`; that label is wrong here, since the assignment names the real folder (FILE(docs/decisions.md:4453)). Read (iii) is why batch 2 is labelled retrospective (by design) (below, "Batch 2 is labelled retrospective (by design) from this entry").`
(b) Line 80, read (i). Replace
`at 11:50:49 UTC it printed the first 300 characters of that run's `checks.json`)`
with
`at 11:50:49 UTC it printed the first 300 characters of that run's `checks.json`, which, if the run had ended, hold its client-lag p99 and its `no_errors` counts `ok` and `unfinished` (DERIVED from the layout `harness/checks.py` writes, FILE(harness/checks.py:237), for a valid run; with a failed check listed, the second count can fall past character 300; output not opened; FILE(docs/decisions.md:4453), Read 2): a control's counts, not a burst run's)`
(c) Line 80. Replace `**Two reads are known.**` with `**Three reads are known, (i) to (iii), besides reads of names, configs, validity and sizes.**`

**BL3 (BEFORE; class: a reporting duty and a stricter rule.)**
(a) Line 80. Replace
`(committed in `723a16b`; BH8, BG5(b))`
with
`(committed in `723a16b` and widened in `d960ef3` to strings that end in `/runs`, FILE(docs/decisions.md:4453); BH8, BG5(b); the run at E uses the file as committed at E, and if that differs from `d960ef3` the [DECISION] (delegate) names the commit and quotes the diff, which may only widen what is found)`
(b) Line 80. Replace
`and the [DECISION] (delegate) cites both outputs and classifies every `ran_unknown`, `names_reg19_run` and `reg19_read` hit.`
with
`and the [DECISION] (delegate) cites both outputs and classifies, by reading each tool-call input, every `ran_unknown`, `names_reg19_run` and `reg19_read` hit, and every `script_reads_runs`, `runs_glob_loop` and `cd_run` hit from 2026-11-11 00:00 UTC on, as one of: synthetic (no real run folder is read); stubbed (before any read, the reader is replaced by synthetic runs, a scratch folder or a raise; an assignment that names the real `runs/` folder, such as `RUNS = Path("runs")`, is a read, not a stub); excluded (the code skips every REG-19 folder by its name, quoted); not REG-19 (the runs it reads are named); or listed (the read of this section that covers it is named). A hit in none of these classes is a read beyond what is listed here.`
(c) Line 81. Replace
`(its `script_reads_runs` hits, labelled `stubbed` where the code assigns to `find_runs`, `load_run` or `RUNS`, each classified in the [DECISION] (delegate))`
with
`(its `script_reads_runs` hits, each classified in the [DECISION] (delegate) as "About batch 2" says; search2's `stubbed` label alone, given to any assignment to `find_runs`, `load_run` or `RUNS`, is not a stub)`

**BL4 (LATER: in the [DECISION] (delegate) that approves this entry, before the entry is appended; class: a reporting duty.)**
1. **BH10 item 1, for both delegate entries on the review stop** (decisions.md:4406 and its amendment at :4437). For each, the [DECISION] states that it was committed as a delegate decision without its own rule F review and owner-proxy pass. It records that this pass approves the content of both for REG-22, with the note on "the same definition" under question 4. It quotes rule F round 11 on them, or says that rule F has not reviewed them.
2. **BH10 item 3:** the BD9 mapping is extended to BH1–BH10 and BL1–BL4.
3. **Batch 2's label:** it states "retrospective (by design)" and its cause, read (iii), and cites FILE(docs/decisions.md:4453).
4. **The classification:** it lists BL3's classification of every hit, one line each, with its transcript file and line.

**No new [CORR] is needed.** The [CORR] at :4453 (d960ef3) already records read (iii), read (i)'s 300 characters, the overstatement of ALLOWED, and both search2 defects with their fix.

## Which later changes need another proxy pass
- **None** for BL1–BL4 written as given. BL2 in other words needs none, as long as it keeps every fact of read (iii) with its tag.
- **A pass for:**
  - any wording of BL1 other than as given;
  - any text that makes batch 2 primary, or that splits batch 2 (for example, seed 17's burst run retrospective and the other seeds primary). Such a split is a design change made after a look, and it is the owner's decision alone;
  - any other wording of BL3(b)'s classes or its definition of a stub;
  - a rerun at E that classes a hit in none of BL3's classes, or that finds a `c2` output on a batch-1 run. d16's own rule sends that text to rule F and a proxy anyway;
  - any change to fact (1), fact (2), the validity freeze or the frozen list beyond wording, as the predecessor ruled.
- **Rule F round 11's items:** no pass if they are wording, a tag, a stricter rule, a reporting duty or a disclosure; a pass otherwise. This is the last round, and batch 2 is already retrospective (by design), so an item about batch 2's standing changes no label.

## Notes for the owner
- **This is the call that matters.** Under BL1, REG-22 is retrospective throughout (batch 1 already was). It is still worth registering, to fix the code and thresholds before REG-19's table. If you read (iii) as a disclosure that leaves batch 2 primary, you can overrule BL1. I would not, for the reasons under question 5.
- **REG-21 draft 25 has the same read under the same trigger** (its line 54). The agent expects both batch 2s to be retrospective (`agent/STATE.md` at f3abd23). By its commit message, REG-21's owner-proxy verdict (8a3e059) was written before the [CORR] at :4453 reached it. I have not read that verdict.
- **Four sessions reached s57_inv.py from the inputs within about eight minutes** (tool-call input timestamps):
  - this session at 16:30:21 UTC;
  - REG-21's owner-proxy (session 0ec2e539) at 16:30:24;
  - another review session (9aa8df0a) at 16:32:49;
  - the agent at 16:38:03.

  The [CORR] credits the agent; STATE.md gives ≈ 16:50 UTC. Neither affects a label.
- **Read (i)'s 300 characters** likely held seed 17's control's counts: a control's, not a burst run's.
- **The case that the c2 author did not see the counts** rests on tool-call inputs and a keyword count. I did not open what the subagent's parent received, because that is a tool output.
- **Pushing `main`** is still the only outside witness against rewritten history. That is your choice.
- **The working tree at my last check:**
  - `.gitignore` adds `docs/potential_gaps.md`, uncommitted;
  - untracked: `docs/FABLE_PROMPT.md`, the two [DECISION] drafts, the REG-19 queue output, and `docs/probe/20261113_reg20/`.

  I opened none of them.

## Not checked
- Rule F round 11 on d16, and REG-21's round 3.
- Any tool output in a transcript.
  - I read tool-call inputs only.
  - In one subagent's assistant text and Write/Edit inputs I counted keywords without printing anything.
  - What s57_inv.py's `tail -3` and read (i) printed is DERIVED only.
- A rerun of `search2.py` at 723a16b or at d960ef3.
- The outputs search2_20261113T163634Z.txt and classify2_20261113T163634Z.txt. They are not in the bundle, so I did not open them. labels.tsv and classify2.py I checked by grep only.
- `uv run pytest` and `tools/check_docs.py`.
- The VM's state, and the vLLM source behind d16's KV-size phrase.
- REG-21 draft 25 beyond its read list; the plan file beyond its stop-rule section; the session-start docs.
- None opened: `runs/` beyond folder names, the backups, the contents of `state/`, queue outputs, RESUME.md.
- I wrote nothing into the repository. My scripts are in my scratchpad.
