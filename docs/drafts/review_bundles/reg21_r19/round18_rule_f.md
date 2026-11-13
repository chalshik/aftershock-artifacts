# rulef-reg21-draft25-r18 (rulef-reg21-r18), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T17:12:12.526Z; message 1 of 2 from this teammate). Item names BI1–BI8, BI-S1–BI-S2, BI-O1–BI-O5 are this round's.

---

Rule F round 18 on REG-21 draft 25 (bundle reg21_r18), round 3 on the freeze, the last under the review-stop rule: **NOT READY.** Five items are required, BI1–BI5. **BI1 concerns batch 2's standing, and I class it as a design change.** With BI1, the draft's own rule labels batch 2 retrospective by design (D25:54, D25:111). Under the review-stop rule's item 4, batch 1 is then registered alone. BI2–BI5 are reporting duties, wording or disclosures. There are two items against the review-stop entries (BI-S1, BI-S2) and five optional items.

Abbreviations. D25:n is line n of `registration_draft25.md` in the bundle. "Input L" is the tool-call input (the input only) at line L of a transcript under `~/.claude/projects/-Users-chalshik-Projects-aftershock-artifacts/`. `fdf/a487` stands for `fdf13821-770b-43f6-866b-c82b3bbdc140/subagents/agent-a48736828ce71b739.jsonl`. "The dry run" is `transcript_search2_dryrun_20261113T162249Z.txt` in the bundle.

What I read:
- the whole draft and the diff from draft 24;
- round 17's rule F review and owner-proxy review, the review-stop entry and its amendment, both [CORR] entries, and the delegation;
- `analysis/k3w.py`, `load.py`, `withheld.py`, the readers in `tables.py`, `gate.py`, `e1.py`, `k2.py`, `k1.py` and `floor.py`;
- `harness/checks.py` (no_errors), `harness/config.py`, `tools/check_docs.py`, `tests/test_check_docs.py`;
- `closure.py` and `transcript_search2.py` in full;
- the dry run and the self-test output;
- REG-19's `common.sh`, `vm_state.py`, `launch.sh` and `final.sh`, and the configs of seed 17's burst run.

Under `runs/` I listed folder names only. In the transcripts I read tool-call inputs only, and opened no tool output.

What I ran:
- `transcript_search2.py`'s classifier on synthetic script bodies (a copy in my scratch directory);
- a synthetic package test of import shadowing;
- `closure.py`.

I did not run `uv run pytest`: it runs `tools/check_docs.py` on the real `runs/` (BI5).

## Task 1: BE1–BE6 and BF1–BF8

Every item is applied in the text as asked. BE2's "list governs" is replaced by BF2's union rule, and the change is disclosed (D25:246–260). The closure is 26 files at HEAD (PROBE(docs/drafts/review_bundles/reg21_r18/closure_k3w_20261113T162249Z.txt)), and the judged path reads only each run folder's `config.yaml`, not `configs/` (FILE(analysis/k3w.py), read in full). Two exceptions:
- **BE4 and BF5 (every read of a REG-19 folder listed):** not met. A read of seed 17's burst run's post-burst status counts is missing, and (ix) describes the call that made it as "validity only" (BI1).
- **BF6:** the draft carries BF6's text, but the tool does not do what the text says (BI2).

Checked and ruled out: the `analysis` calls of 2026-11-12 between 17:01 and 18:03 UTC that go through `tables.sweep_table`, `gate.sweep_rows`, `e1` and `k2` (Input 3201 and 3476 of fdf13821; `agent-a5a590d4c460ad9e1` 75 and 78; `agent-a27b7110cefc41d7d` 180; fdf/a487 221, 239 and 307) load no REG-19 folder:
- the `k2` and `e1` model functions read `configs/` and synthetic rows (FILE(analysis/k2.py:53), FILE(analysis/k2.py:132), FILE(analysis/e1.py:50));
- `s57_heavy.py` drops every `w3000` folder and replaces `load.find_runs` before it calls `tables.sweep_table` or `gate.sweep_rows`; the import inside `sweep_rows` reads the replaced attribute at call time (FILE(analysis/gate.py:193));
- the 18:03:12 call reads a pickle.

## Required items

### BI1. An unlisted read of seed 17's burst run, after its burst, of the class D25:54's trigger names: its `no_errors` status counts (`ok`, `unfinished`) (D25:54, D25:111)

**Trace.**
1. On 2026-11-12 at 17:59:38 UTC, before the seal (written 18:45:42, committed 19:00:16), a context-pack subagent of session fdf13821 wrote `s57_inv.py` and ran it (fdf/a487, Input 201). Its text is in that input:
   - it loops over every folder in `runs/` (`for d in sorted(RUNS.iterdir())`);
   - it reads `checks.json`, and for the `no_errors` check it takes `ok = c["detail"].get("ok"); unf = c["detail"].get("unfinished")`;
   - it puts both into each row with `valid` and `failed`, prints the whole table to a scratch file, and then runs `tail -3` on that file.

   `no_errors`' detail is the dict of request status counts (FILE(harness/checks.py:67), FILE(harness/checks.py:69), FILE(harness/checks.py:44)), and `checks.json` is written after the run (FILE(harness/checks.py:237)).
2. The folders are taken in name order, and the last two are seed 17's control and burst run (DERIVED: `ls runs | tail -3` today, names only; no folder is ever removed, CLAUDE.md research rule 4; the lost seed-18 control went to a holding folder). The last printed line is `len(df)`. So the three lines `tail -3` printed were seed 17's control row and burst row, each with `ok` and `unfinished`, and the row count (BELIEF: from the script's text; the output was not opened).
3. Ten seconds later (17:59:48, Input 205) the same subagent ran `sed -i 's/ok=ok, unf=unf,/ok=(None if "w3000" in d.name else ok), unf=(None if "w3000" in d.name else unf),/'` and ran the script again. At 17:59:58 (Input 209) it added a compact print. Only the first run printed REG-19's counts. The first run also read the counts of seeds 15, 16 and 17 into a scratch file, which the second run overwrote.
4. These counts are exactly what REG-19's rule withholds:
   - its allowed reads are a run's `checks.json` "(valid, failed)" and "Nothing else … (REG-19: no interim look)" (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:36));
   - `vm_state.py` reads "the names of the statuses, never their counts" (FILE(docs/probe/20261113_reg19/ops_r3/vm_state.py:3)).
5. What the counts tell (DERIVED from FILE(configs/burst_l1pl350cl_r2.0_w3000_s17.yaml) and its parent):
   - The burst runs over [900, 1080) s, arrivals stop at 4080 s, and the drain lasts 300 s. So `ok` counts completions up to 4380 s, and `unfinished` counts what was left at 4380 s.
   - Completions before 900 s follow the published warm schedule. The main unknown is the 180 s of the burst, between the cold rate (about 1.7 req/s, D25:50) and 2.4 req/s: ±63 requests.
   - So `ok` fixes the mean completion rate over [1080, 4380) to about ±63 ÷ 3300 = ±0.02 req/s. That is r's first factor (÷ 1.681) to about ±0.01, well inside J1's 0.05. This holds if the rate over W equals the rate over [1080, 4380), as it does for a steady stuck state (BELIEF).
   - `unfinished` > 0 says the line had not emptied by 4380 s. That is one part of REG-19's per-seed test for seed 17.
6. D25:54 does not list this read. (ix) says "names and validity only … `valid` and the names of failed checks in loops by the context-pack subagents between 17:58 and 18:11 UTC", which covers 17:59:38 by its time and misdescribes it. The dry run shows the hit (PROBE(docs/drafts/review_bundles/reg21_r18/transcript_search2_dryrun_20261113T162249Z.txt:4641)), labelled `stubbed`, with its 32-line body elided (BI2).
7. The draft's own rule fires. D25:111: "If such a reading or run is known, it goes into 'What was known' … where the trigger in 'What was known' applies (… a read of a line a REG-19 burst run wrote after its burst began), batch 2 is also labelled retrospective by design." This applies to a read known before the append, not only to one found by the append-time search. Listing (x) without the label would keep batch 2 primary after a read that D25:54 calls disqualifying when it is found one step later.
8. The trace for task 2(a) follows. Every rule on batch 2 written after 17:59:38 on 2026-11-12 could have been chosen by sessions that had one batch-2 run's r to about ±0.01. Those rules include:
   - the fixed-load contrast's 0.05 (draft 5 on);
   - "busy ≥ 0.99" in its present use;
   - the BE and BF rules on batch 2's label.

   Whether the subagent's report carried the counts to session fdf13821, and from there to the agent, is not checkable from inputs. Under rule A, the look stands until it is ruled out.

**Replacement text** (D25:54, four edits; D25:111, one edit):
- In D25:54, replace "`valid` and the names of failed checks in loops by the context-pack subagents between 17:58 and 18:11 UTC," with "`valid` and the names of failed checks in loops by the context-pack subagents between 17:58 and 18:11 UTC (other than (x)),".
- In D25:54, insert before "That pass prints each of these": "(x) On 2026-11-12 at 17:59:38 UTC, before the seal, a context-pack subagent of session fdf13821 ran a script, `s57_inv.py`, that read from every run folder's `checks.json` the counts of the `no_errors` check's statuses, `ok` and `unfinished` (FILE(harness/checks.py:69)), REG-19's runs of seeds 15 to 17 included. It wrote them to a scratch file and printed the file's last three lines. The folders are read in name order, so those lines were seed 17's control and burst rows, with their `ok` and `unfinished`, and the row count (BELIEF: from the script's text in the tool-call input; the agent has not read the output). Ten seconds later the same subagent blanked those two columns for REG-19's folders and ran the script again. REG-19's own scripts never read these counts (FILE(docs/probe/20261113_reg19/ops_r3/vm_state.py:3), FILE(docs/probe/20261113_reg19/ops_r3/common.sh:36)). With the published schedule, the `ok` of seed 17's burst run fixes its mean completion rate after the burst to about ±0.02 req/s, and so r's first factor to about ±0.01 (DERIVED: rule F round 18, BI1). `unfinished` says whether its line had emptied by the drain's end. This is a read of a line a REG-19 burst run wrote after its burst began, the class the trigger below names. The agent's pass found it as a `stubbed` hit with its body elided and filed it under (ix) (rule F round 18, BI1, BI2)."
- In D25:54, replace "No other read of a REG-19 run's files or logs, and no other run of `analysis/` code on a REG-19 run folder from any checkout, is found by a search" with "No other read of a REG-19 run's files or logs, and no other run of `analysis/` code on a REG-19 run folder from any checkout, is known to the agent from a search". Then, after that sentence's PROBE citation, add: "(x) shows that the search's hits must be read in the scripts' full text (rule F round 18, BI2)".
- In D25:54, replace "Batch 2 is primary only if the stopping rule's facts (1) and (2) hold; otherwise it is labelled retrospective and never governs ("The two batches")." with "**Batch 2 is labelled retrospective by design** because of read (x), by this paragraph's trigger as the last sentence of "At the append of this entry" applies it to a read known before the append. It never governs ("The two batches"). Facts (1) and (2) are still checked and reported in the batch-2 [RESULT]."
- In D25:111, replace "the nine listed there, (i) to (ix)" with "the ten listed there, (i) to (x)".
- Every sentence that makes batch 2 primary is rewritten to the retrospective label, as the review-stop rule's item 4 asks: D25:104's "Batch 2 is primary only if two facts in git hold" and "The two batches" rules. D25:1's title also says that batch 2 is retrospective by design. That text gets its own rule F review and owner-proxy pass (item 4).

**Owner-proxy pass:** yes. **Batch 2's standing:** yes. **Class: a design change** (batch 2's label). It is also a disclosure; I class it as a design change because its consequence, under D25:54's and D25:111's own rule, is batch 2's label.

### BI2. `search2.py` does not do what D25:54 and D25:111 say it does, and its labels misled the classification (D25:54, D25:111)

**Trace.** The `s57_inv.py` hit went into (ix) because the tool hid what decides its class:
- **(a)** A script body written to a file is elided ("<<body: 32 lines …, not printed>>"). For the script, only the lines that call a reader or list `runs/` are printed: the dry run, line 4641 and the lines after it.
- **(b)** A script that assigns `RUNS` is labelled `stubbed`, the label of a reviewer's guard, even when `RUNS = Path("runs")` is the real folder. On a synthetic body the classifier returns `('stubbed', ['RUNS = Path("runs")', 'for d in sorted(RUNS.iterdir()):'])` (my run; FILE(docs/drafts/review_bundles/reg21_r18/transcript_search2.py:108)).
- **(c)** A script that lists `runs/` through any other variable is missed. `R = "runs"; os.listdir(R)` returns `(None, [])` on a synthetic body (my run).
- **(d)** Scripts are matched by base name across all transcripts (FILE(docs/drafts/review_bundles/reg21_r18/transcript_search2.py:263), FILE(docs/drafts/review_bundles/reg21_r18/transcript_search2.py:302)). The 16:20:26 `t2.py` and 17:11:18 `noise.py` hits show other files' bodies (`/Users/chalshik/.claude/jobs/c075c1a8/tmp/scripts/t2.py`, `…/f5298640-…/scratchpad/noise.py`). Their own bodies, which are in the same inputs, are synthetic (fdf13821's `agent-aaebfa565af29d02f` Input 74 and `agent-a023b34dba3dfefb8` Input 94). The same mechanism can show a harmless body for a run of a different file.
- **(e)** `sed -i` and other in-place edits are not tracked. The three runs of `s57_inv.py` are shown with one text, and the first, the only one that printed counts, cannot be told from the others.
- **(f)** There is no class for batch-1 or reference run ids: `RUN_ID` matches only `w3000_s1[5-9]` names (FILE(docs/drafts/review_bundles/reg21_r18/transcript_search2.py:73)). A `ran` hit is printed as a 140-character excerpt (FILE(docs/drafts/review_bundles/reg21_r18/transcript_search2.py:63)).

So D25:111's "For each hit on a REG-19 run, a batch-1 run or a reference run it prints the whole command" (BF6's words) and D25:54's "That pass prints each of these with its whole command" are false.

**Replacement text:**
- In D25:54, replace "That pass prints each of these with its whole command (inputs only);" with "That pass prints each of these with its command (inputs only), with these limits:
  - it does not print the body of a script written to a file;
  - for a script run from a file, it prints only the lines that call a run reader or list a path under `runs/`, taken from every script of the same base name;
  - it labels a script that assigns `RUNS` as `stubbed` even when `RUNS` is the real `runs/`;
  - it misses a script that lists `runs/` through any other variable;
  - it does not track in-place edits;

  (rule F round 18, BI2);".
- In D25:111, replace "For each hit on a REG-19 run, a batch-1 run or a reference run it prints the whole command (tool-call inputs only)." with "For each hit it prints the command (tool-call inputs only), with the limits stated in "What was known"; it has no class for batch-1 or reference run ids, and it prints a `ran` hit as a 140-character excerpt (rule F round 18, BI2)."
- At the end of D25:111's sentence ending "(rule F round 17, BE-O1, BE-O3).", add: "For every `script_reads_runs`, `ran_unknown` and `ran` hit after 2026-11-11 17:15 UTC, the classification:
  - opens, in the tool-call inputs, the full text of the script as it ran: the heredoc, Write or Edit that made it, and every later `sed`, `cat >>` or Edit before that run;
  - states what the script reads from which folders and what it prints;
  - treats the label `stubbed` as no evidence of a guard;
  - names every run of a script whose text no transcript shows (rule F round 18, BI2)."

**Owner-proxy pass:** yes. **Batch 2's standing:** not as the review-stop rule's item 3 defines it (it bears on the trigger's search; after BI1, batch 2 is retrospective in any case). It governs batch 1's "What was known" and REG-22's. **Class:** a reporting duty, and wording.

### BI3. Read (x) is an interim look at REG-19 that its records do not hold (D25:54)

**Trace.** REG-19's rule is "no interim look" (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:36)). Neither the interim-look [CORR] (FILE(docs/decisions.md:4428), cited in D25:54; the bundle's `corr_interim_look_entry.md`) nor any line of the draft records the 17:59:38 read. REG-19's [RESULT] would then report no interim look, while seed 17's counts were printed before seeds 18 and 19 were run.

**Replacement text:** at the end of (x) in D25:54 (BI1), add: "This read is recorded for REG-19 by a [CORR] appended before this entry (decisions.md 2026-11-13 [CORR], REG-19's interim look, 17:59:38 UTC). That [CORR] states the run, time, reader, fields and what was printed, and REG-19's [RESULT] cites it."

**Owner-proxy pass:** no for the [CORR] itself (it records the session's own error, rule A6). Whether it bears on REG-19's standing is the owner's call. **Batch 2's standing:** no, beyond BI1. **Class:** a reporting duty.

### BI4. "What was known" leaves out two prints on batch-1 runs (D25:49)

**Trace.**
- On 2026-11-12 at 14:09:43 UTC (fdf13821, Input 443), 13 minutes before the command D25:49 calls "The same command", session fdf13821 ran `k1.cold_backlogged` on the five λ = 2.0 runs. It printed each run's flag, its end window's `hit`, `q`, `kv` and `n`, and its baseline's `hit`, `q`, `kv` and `pf` (FILE(analysis/k1.py:91)).
- On 2026-11-12 at 18:02:32 UTC (fdf/a487, Input 297), a context-pack subagent ran `load.verdict` on REG-15's run `20261110-085730_confirm_l1pl350cl_r2.2_s12`, a batch-1 run (FILE(analysis/k3w.py:61)), and on REG-16's control. It printed the verdict, `t_start`, `t_wipe`, the baseline's and end window's `pf`, `hit`, `q`, `q_slope`, `n` (the mean running batch) and `kv` (FILE(analysis/load.py:168), FILE(analysis/load.py:183)), and the KV maximum.

Neither printed U, r, the busy share or the served prompt, so D25:49's first sentence stands. But the list of what was printed is incomplete, and the end window's hit share on REG-15's run is the same kind of value D25:49 discloses for five runs.

**Replacement text:** in D25:49, after "…was printed for the end window of those five runs.", insert: "An earlier command of the same session, at 14:09:43 UTC, printed `k1.cold_backlogged` on the same five runs: each run's flag, its end window's hit, waiting line, KV and mean running batch, and its baseline's hit, waiting line, KV and percent fast. At 18:02:32 UTC a context-pack subagent of that session printed `load.verdict` on REG-15's run (batch 1) and REG-16's control: the verdict and each window's percent fast, hit share, waiting line and its slope, mean running batch and KV, and the KV maximum (tool-call inputs; the agent has not read the output; rule F round 18, BI4)."

**Owner-proxy pass:** yes (D25:111 sends a new "What was known" item to one). **Batch 2's standing:** no. **Class:** a disclosure.

### BI5. The trigger's words cover the listed validity reads, and reads of the same class by `pytest` and `check_docs` are not listed (D25:54)

**Trace.**
- "a read of a line a REG-19 burst run wrote after its burst began" literally includes `checks.json`'s `valid` and `failed`, which (ix) and REG-19's scripts read by design. An append-time search that finds one more `valid` loop would fire the trigger as worded.
- Every `uv run pytest` runs `tools/check_docs.py` on the real `runs/` (FILE(tests/test_check_docs.py:57)), as does every `python3 tools/check_docs.py`, which is required at each session's end (CLAUDE.md D). Each such run reads every folder's `checks.json` `valid` (FILE(tools/check_docs.py:41)), and its `env.json` `git_commit` and `config.yaml` `source_config` (FILE(tools/check_docs.py:196)). Every such run since 2026-11-12 05:09 UTC read REG-19's folders this way, and D25:105 requires a `pytest` run before each batch.
- On 2026-11-12 at 19:52:14 UTC (session 8c5f8396, Input 1779), `ls runs/*_w3000_s18 | head -20` on the VM listed the file names of seed 18's lost first control.

**Replacement text:**
- In D25:54, replace "a read of a line a REG-19 burst run wrote after its burst began, beyond what is listed here," with "a read of a line a REG-19 burst run wrote after its burst began, other than `checks.json`'s `valid` and `failed`, beyond what is listed here,".
- In (ix), after "(folder names, `valid` and `failed`, checksums)", add "; every `uv run pytest` and `python3 tools/check_docs.py` on the Mac since 2026-11-12 05:09 UTC (`checks.json` `valid`, `env.json` `git_commit` and `config.yaml` `source_config` of every folder; FILE(tools/check_docs.py:41), FILE(tools/check_docs.py:196), FILE(tests/test_check_docs.py:57)); and, at 19:52:14 UTC, the file names of seed 18's lost first control on the VM".

**Owner-proxy pass:** yes (the trigger's wording). **Batch 2's standing:** only if BI1 is not taken. **Class:** wording, and a disclosure.

## Items against the two review-stop entries

**The amendment carries BF10's text verbatim:** yes. The 719 characters between the quotes at line 179 of `owner_proxy_on_draft24.md` occur unchanged in `review_stop_amendment_entry.md` (my check, byte for byte).

### BI-S1. Item 3, item 4 and part (2) disagree on a disclosure item that bears on batch 2's label, and round 2's application settled that in the delegate's favour

**Trace.**
- Item 3 says items "on disclosures ("What was known")" do not count.
- Item 4's round-2 clause, and part (2) of the amendment, allow only "wording, a tag, a stricter rule or a reporting duty". Part (2) adds "or none of these" and has no "disclosure".
- Round 17's reviewer said five items concern batch 2's standing. It classed BE4 "a disclosure and a tag" (plus a stricter rule and a reporting duty), and wrote "Batch 2's standing: only through D24:54's trigger" (round17_rule_f.md, BE4).
- The amendment resolved this with its own sentence, "A disclosure is not about batch 2's standing (item 3)", over the reviewer's statement on standing. Part (2) gives the class to the reviewer, but no text says who decides whether an item concerns batch 2's standing.
- In round 3 the same conflict arises for BI1. It is a disclosure whose consequence, under D25's own text, is batch 2's label.

The outcome does not depend on this: I class BI1 as a design change, and D25:111 labels batch 2 retrospective for such a read in any case. But a rule that lets a read of the trigger's class pass as "a disclosure" leaves batch 2 primary whenever the read is found before the append, the opposite of the draft's intent.

**Replacement text** (a further entry, as the amendment provides): "(3) The reviewer who raises an item also states whether it concerns batch 2's standing; the class rule of part (2) applies to that statement. An item concerns batch 2's standing when, under the registration's own text, its consequence is batch 2's label (the trigger in REG-21's "What was known", and REG-22's counterpart). (4) "A disclosure" is a class under part (2); it does not count under item 3 unless (3) makes it concern batch 2's standing. (5) Round 2's reading of BE4 ("A disclosure is not about batch 2's standing") was the delegate's, not the reviewer's; under (3) it stands only because BE4's consequence was applied in full in draft 25."

**Owner-proxy pass:** yes. **Class:** wording, with a stricter rule.

### BI-S2. BH10 was applied before anyone classed it, and the delegate judged its standing

**Trace.** The amendment says REG-22's owner-proxy "stated no class for BH10" and decides itself that BH10 is "not about batch 2's standing". Part (2) asks for a class from "the owner-proxy of the same or the next round … before the item is applied", and the amendment also says "Drafts 25 and 16 apply every item". So BH10 was applied unclassed, and by part (2) it "counts as none of these". It fires no stop only through the delegate's own judgment of its standing.

**Replacement text** (same further entry): "(6) REG-22's round-3 owner-proxy states BH10's class and whether it concerns batch 2's standing; this entry records both. Until then BH10 counts as none of the classes."

**Owner-proxy pass:** yes (REG-22's). **Class:** a reporting duty.

## Optional items

- **BI-O1 (stricter rule).** Facts (1) and (2) and the status check cover only the frozen files and `analysis`/`harness`, but `python -m analysis.k3w` puts the repository root first on `sys.path`. A root-level `json.py`, `yaml.py` or `numpy.py` added after E, committed or not, replaces what the judged path imports, while both facts hold. In a synthetic package, `python3 -m analysis.k` imported a root-level `json.py` in place of the standard library's (my run). Add to D25:104's list of what the batch-2 [RESULT] shows: `git diff --quiet E B -- ':(glob)*.py' ':(glob)*.pth'` exits 0, and `git status --porcelain --ignored --untracked-files=all -- ':(glob)*.py' ':(glob)*.pth'` prints nothing; any other line is a breach it reports.
- **BI-O2 (wording).** The bundle's `closure.py` sets `REPO = Path(__file__).resolve().parents[3]` (FILE(docs/drafts/review_bundles/reg21_r18/closure.py:26)). That is right only at its committed path, `docs/probe/20261113_freeze/closure.py`; run from the bundle it points at `docs/`. Say so in the bundle note.
- **BI-O3 (reporting duty).** The context pack `docs/paper/context-pack-2026-11-12.md` (local) and the subagent's final report are where seed 17's counts would have travelled. The owner, not the agent, can check whether either carries them. The [CORR] (BI3) should state the result, or that it was not checked.
- **BI-O4 (wording).** Say that the searches cover only the Mac's transcript folder for this project. It is the only one: `~/.claude/projects` has one folder named for this project. Claude sessions on the VM, if any, are not covered.
- **BI-O5 (reporting duty, from round 17, still open).** In the batch-1 [RESULT], report r against (c ÷ 1.681) × (served prompt ÷ 3072), per run, from the published completion rates c (see the alternative below).

## Strongest alternative explanation

- **For BI1's read:** the 17:59:38 output was not seed 17's two rows (for example, it ended in a traceback or a warning line), and the 17:59:48 patch was a precaution. The separating evidence is the tool result that follows fdf/a487 Input 201, which only the owner may open. Even then the script read the counts of seeds 15–17's burst runs into a file, and the trigger names a read. Only "who saw what" changes, which matters for BI3 and BI-O3, not for BI1's label.
- **For REG-21's result** (round 17's, still standing): r restates REG-19's completion rate over W and the first-turn share, r ≈ (c ÷ 1.681) × (prompt ÷ 3072) (D25:51). The separating check is BI-O5. If |r − that| < 0.01 on every run, the token reading adds nothing beyond c.

## Can it change a decision?

With BI1, batch 2 never governs. Batch 1's labels are predicted from published numbers before anything is computed (D25:52: λ = 2.0 inside the tolerance, λ = 2.4 at or above it, J2's spread 0.02–0.05). Batch 2's r for seed 17 is already bounded closely (BI1). I see no outcome of REG-21 that changes a decision on K3 that the published numbers do not already set. Its value is the reported readouts. Rule A1 asks the registration to say so plainly. It costs 0 GPU h.

BI3 can change REG-19's record: an interim look before seeds 18 and 19. The owner decides whether it bears on REG-19's standing; REG-19's per-seed verdicts are computed by fixed code.

## Not checked

- Any tool output in a transcript, including the 17:59:38 result.
- `uv run pytest`: it reads every run folder's `checks.json`, `env.json` and `config.yaml` through `check_docs` (BI5), beyond my folder-names limit.
- The bodies of post-seal reviewer scripts (2026-11-12 19:33 onward: `r3_traces.py`, `b_judge_ref_batch2_vj.py`, `c_batches_seal.py`, `a_path.py`, `r6_check.py`, the `snap` run) beyond the reader lines `search2` prints. So D25:111's "every reviewer script … replaced `find_runs` … before any call" is unverified by me.
- The context pack of 2026-11-12, the subagent's report to fdf13821, VM-side sessions, and commands run by hand.
- REG-22 draft 16 (read only for comparison).
- Whether the closed-loop details change BI1's ±0.02 req/s; BELIEF, stated as such.
