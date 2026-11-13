<!-- docs/decisions.md lines 4453-4501 at HEAD 0d86f02 -->
## 2026-11-13 · [CORR] Two reads of REG-19's seed 17 on 2026-11-12 went beyond its allowed reads: a context-pack script most likely printed both runs' `ok` and `unfinished` request counts, and the first 300 bytes of the control's `checks.json` hold the same counts; the transcript search missed the scripts of that kind

- **Allowed reads.** While REG-19 runs, a run folder may be read for its name and for `checks.json`'s `valid` and `failed`, and for nothing else: "a run's checks.json (valid, failed) … Nothing else of a log or a run folder (REG-19: no interim look)" (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:36)).
- **What `checks.json` holds beyond those.**
  - The check `no_errors` stores as its detail the count of the run's requests by status (FILE(harness/checks.py:67), FILE(harness/checks.py:69)): `ok` (completed) and `unfinished` (not completed when the run stopped).
  - The file is written with `indent=2` (FILE(harness/checks.py:237)), in the order `valid`, `failed`, then the checks; `client_lag` is first and `no_errors` second (FILE(harness/checks.py:64), FILE(harness/checks.py:232)).
  - For a valid run, the `unfinished` line ends near byte 295 (DERIVED: `json.dumps` with indent 2 of that layout, with a 17-digit `p99_s`, `ok` = 12345 and `unfinished` = 123; other digit counts move this by a few bytes).
- **Read 1, 2026-11-12 17:59:38 UTC: a context-pack subagent of session fdf13821 ran `s57_inv.py`.**
  - For every folder under `runs/`, sorted by name, the script read `config.yaml` fields, `checks.json`'s `valid` and `failed`, the `no_errors` counts `ok` and `unfinished`, and the number of files. It printed `tail -3` of the table (PROBE(docs/probe/20261113_transcript_search/inputs_s57_inv.txt), lines 12, 24, 32, 37–38 and 40). The call's record in the search: PROBE(docs/probe/20261113_transcript_search/search2_20261113T163634Z.txt), line 4682.
  - The last two folder names in `runs/` are seed 17's control `20261112-103423_stage2_control_l1pl350cl_r2.0_w3000_s17` and its burst run `20261112-135538_burst_l1pl350cl_r2.0_w3000_s17` (folder names, read today; nothing is ever removed from `runs/`, rule 4).
  - With the script's display options, `pandas`' `to_string` prints one line per row (DERIVED: on synthetic data, 5 rows of 26 columns gave 6 lines; pandas 3.1.0 in `.venv`).
  - So the three printed lines were most likely those two rows, `ok` and `unfinished` included, and a count line. This is DERIVED from the inputs; the output was not opened.
  - Ten seconds later the subagent blanked `ok` and `unfinished` for every `w3000` folder and ran the script again (PROBE(docs/probe/20261113_transcript_search/inputs_s57_inv.txt), line 43).
- **Read 2, 2026-11-12 11:50:49 UTC: the `head -c 300` of seed 17's control `checks.json`,** which the [CORR] above records (FILE(docs/decisions.md:4431)).
  - That entry says "`checks.json` is a read REG-19's rules allow" (FILE(docs/decisions.md:4432)). This holds for `valid` and `failed` only.
  - If the control had ended by then, those 300 bytes hold its client-lag p99 and its `ok` and `unfinished` counts (DERIVED from the layout above). Whether it had ended is not known (BELIEF either way, as that entry says).
- **What the counts tell.**
  - `unfinished` counts the requests still waiting or running when the harness stopped the run. A large count in a burst run goes with a waiting line that has not emptied, and REG-19's per-seed test asks whether the line ever empties (decisions.md 2026-11-11 [REG] REG-19).
  - `ok`, divided by the run's length, is the run's mean completion rate (DERIVED).
  - Neither is REG-19's verdict.
  - Whether anyone read the printed lines is not known. They were in the subagent's own context, and its report to its parent was not opened (inputs only).
- **Why the search missed it.**
  - `search2.py` (723a16b) took a string as a path into `runs/` only if it held `runs/`. So `s134_runs.py` and `s57_md.py`, which name the folder as `…/aftershock-artifacts/runs`, were not flagged.
  - It marks as `stubbed` (a reviewer's guard) a script that assigns to `RUNS`. `s57_inv.py`'s `RUNS = Path("runs")` is not a guard.
  - The classification script dropped `stubbed` records.
  - Found by the agent while labelling the hits by hand. Round 2 (BH8, BE-O1, BE-O3) asks the [DECISION]s of REG-21 and REG-22 for that classification.
- **Fixes.**
  - `search2.py` now tests `(^|/)runs(/|$)` (FILE(docs/probe/20261113_transcript_search/search2.py:105)), with a 17th self-test case (FILE(docs/probe/20261113_transcript_search/search2.py:429), FILE(docs/probe/20261113_transcript_search/search2.py:467)).
  - Run beside 723a16b's version on the same transcripts, it adds seven records (PROBE(docs/probe/20261113_transcript_search/search2_fix_added_20261113T163634Z.txt)):
    - one of 2026-11-04;
    - three runs of `s134_runs.py` and a table built from its output, between 17:56 and 18:09 UTC on 2026-11-12 (`source_config`, `sweep_parent`, `valid` and `failed` of every folder: what draft 25's items (iv) and (ix) disclose);
    - two runs of `s57_md.py`, which read only the runs `s57_heavy.py` loaded; that script skips every `w3000` folder (PROBE(docs/probe/20261113_transcript_search/search2_20261113T163634Z.txt), line 4732).
  - `classify2.py` now keeps `stubbed` records, and each is labelled by hand.
  - Every hit at or after 2026-11-11 17:15:21 UTC has a label (PROBE(docs/probe/20261113_transcript_search/classify2_20261113T163634Z.txt)). The hand labels and their notes are in FILE(docs/probe/20261113_transcript_search/labels.tsv).
  - Labelling also found an `ls` of seed 17's burst folder at 2026-11-12 17:56:24 UTC (file names only), which draft 25's item (viii) does not list.
- **The agent's own reads beyond inputs, while checking:**
  - the lengths, not the text, of the results of four calls around Read 1 (1990, 697, 2242 and 26547 characters);
  - the first 60 characters of one result, to confirm that a call had been denied (a permission notice; session 8c5f8396, line 9853).
- **Effect.**
  - **REG-19.** Two looks beyond its allowed reads, in the middle of the matrix, at seed 17. Its rules and code are unchanged, and its table is still computed only by `final.sh`; its [RESULT] lists both looks as deviations. The decisions on REG-19 made since then give other grounds: the VM's power-offs and the attempt records for seed 18's control (decisions.md 2026-11-13 [DECISION] (owner), the resume and attempt 3).
  - **REG-21 and REG-22.** Their batch 2 is REG-19's burst runs, so Read 1 is a look at batch-2 data before their entries. Under the freeze, a look is disclosed, not a switch. Their next drafts:
    - add Read 1 as item (x) of "What was known";
    - correct what item (iii) says of `checks.json`;
    - add the 17:56:24 listing to item (viii).

    Round 3's four reviewers, running now, are sent this entry.
  - **status.md.** Its "No result has been read" holds for REG-19's verdict. It does not hold for the counts above, and status.md now says so.
- **Error:** mine. The search was built to find such reads and missed two kinds of script. And the earlier [CORR] of today called a `checks.json` read allowed without checking what its first bytes hold.
