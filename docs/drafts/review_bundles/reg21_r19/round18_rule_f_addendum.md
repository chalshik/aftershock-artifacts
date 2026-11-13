# rulef-reg21-draft25-r18-addendum (rulef-reg21-r18), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T17:12:12.526Z; message 2 of 2 from this teammate). Addendum after the [CORR] at decisions.md:4453; adds BI6, BI7, BI4b, BI8.

---

Addendum to rule F round 18 on REG-21 draft 25, after the [CORR] at d960ef3 (FILE(docs/decisions.md:4453)) and the agent's reading that D25:54's trigger applies. It is saved after the review. **The verdict is unchanged: NOT READY. BI1 stands, it concerns batch 2's standing, and its class is a design change.**

What I read for it:
- the [CORR] (FILE(docs/decisions.md:4453) to its end);
- the diff of `search2.py` from 723a16b to d960ef3;
- `classify2.py`'s source;
- the tool-call inputs of the calls it names, read directly in the transcripts.

What I ran: the fixed `search2.py` and `classify2.py` on synthetic bodies and on a synthetic transcript in my scratch directory, and a pattern scan of every tool-call input since 2026-11-12 05:09 UTC that names `checks.json` together with a loop, a glob or a REG-19 name.

I did not open the new probe files (`inputs_s57_inv.txt`, `search2_20261113T163634Z.txt`, `search2_fix_added_…`, `classify2_…`, `labels.tsv`): they are probe files outside the bundle, and my limits are unchanged.

## The agent's reading: does the trigger apply?

Yes. I find no trace on which this reading is wrong.
- D25:54's trigger names "a read of a line a REG-19 burst run wrote after its burst began". `s57_inv.py` read seed 17's burst run's `checks.json` `no_errors` counts, and seeds 15 and 16's too. That file is written when the run ends (FILE(harness/checks.py:237)).
- The trigger names a read, not a print. So it applies even on the alternative that the 17:59:38 output held no counts.
- D25:111's last sentence applies the label to a reading known before the append, so listing Read 1 as (x) does not take it out of the trigger.
- Read 2 is of seed 17's control, not a burst run, so it does not fire REG-21's trigger. It is a disclosure here, and an interim look for REG-19.

The [CORR] confirms BI1's facts by the same derivation.

## Effect on my items

- **BI1:** stands as written. In the inserted (x), add "(decisions.md 2026-11-13 [CORR], FILE(docs/decisions.md:4453))" after "ran the script again." Then add BI7's sentence.
- **BI3:** met. The [CORR] records Read 1 and Read 2, and says REG-19's [RESULT] lists both as deviations (FILE(docs/decisions.md:4453)). Nothing more is required.
- **BI2:** partly met.
  - What is fixed: the `…/runs` path test (`search2.py:105`), and `stubbed` records now go to hand labels (`classify2.py`, its docstring).
  - Still open: on the fixed `search2.py`, these synthetic bodies all give `(None, [])`, so they are missed:
    - `R = "runs"; os.listdir(R)`;
    - a path built from a variable in an f-string;
    - `subprocess.run("cat runs/x/checks.json", shell=True)` inside python;
    - `pd.read_json(d + "/requests.jsonl")` with `d` a variable.
  - Also still open: base-name matching, untracked in-place edits, no batch-1 or reference class, and 140-character `ran` excerpts.
  - D25:54's and D25:111's "prints … the whole command" are still false. BI2's replacement text stands; in its first bullet, drop the line on the `stubbed` label and add "it misses a path into `runs/` that is built from a variable, an f-string or a shell command run from python".
  - Class unchanged: a reporting duty, and wording. Not batch 2's standing.
- **BI4:** extended (below, BI4b).
- **BI5:** unchanged. The [CORR]'s 17:56:24 listing goes into (viii), as planned.
- **BI-S1, BI-S2:** unchanged. The [CORR] does not touch the review-stop rule.

## New required items

### BI6. `classify2.py` labels any read of `checks.json` in a loop as "names and validity only", the error Read 2 made (classify2.py, rule `names_or_validity`)

**Trace.** The rule auto-labels a loop, glob or `cd` under `runs/` whose command names no run file other than `checks.json` and uses no size tool, without checking which fields it reads (FILE(docs/probe/20261113_transcript_search/classify2.py:27), its code at lines 110–113; `SIZETOOL` catches `cat`, `head` and `tail` only as shell tools).

I wrote a synthetic transcript of four calls at 2026-11-12 12:00–12:03 UTC, ran the fixed `search2.py` and then `classify2.py`. All four came out `names_or_validity | auto`:
- a loop printing every REG-19 run's whole `checks.json` through `python3 -c "…print(json.load(open('$d/checks.json')))"`;
- a loop printing `c['checks'][1]['detail']`, that is `no_errors`' `ok` and `unfinished`;
- `jq '.checks[1].detail'` on seed 17's burst run;
- a `valid`-only loop (the only correct one).

My scan of the real inputs since 2026-11-12 05:09 UTC found no read of a REG-19 `checks.json` beyond `valid` and `failed` other than Reads 1 and 2. The 18:05:02 loop (fdf13821's `agent-a625ca98c29ea904b`, Input 308) prints `failed`, because `checks` is a list. So today's labels stand (BELIEF: a pattern scan). But the run at the append can mislabel a new read.

**Replacement text** (D25:111, after the sentence BI2 adds): "`classify2.py` labels a command `names_or_validity` only if every read of `checks.json` in it takes `valid` or `failed` by name, or tests that the file exists. Any other read of `checks.json` (a whole-file print, `jq`, `head`, the `checks` list, `detail`) is labelled by hand, with the fields it prints (rule F round 18, BI6)."

**Owner-proxy pass:** yes. **Batch 2's standing:** no (after BI1). It bears on REG-22's search and on REG-19's list of deviations. **Class:** a stricter rule.

### BI7. The [CORR]'s effect bullet states the opposite of the trigger: "Under the freeze, a look is disclosed, not a switch" (decisions.md:4453 entry; D25:54)

**Trace.** The [CORR]'s "Effect" bullet on REG-21 and REG-22 says a look "is disclosed, not a switch", and plans only to add Read 1 as item (x). D25:54's "None of this is a switch" speaks of looks after the entry. The trigger, and D25:111's last sentence, make Read 1 a switch to "retrospective by design". The agent's later reading (f3abd23) agrees with the trigger, but decisions.md is append-only. A later reader could cite the [CORR]'s sentence to keep batch 2 primary.

**Replacement text** (in D25:54, after (x)): "The [CORR] at FILE(docs/decisions.md:4453) says of this read: 'Under the freeze, a look is disclosed, not a switch.' For this entry that sentence does not hold. Read (x) is of the class the trigger below names, so batch 2 is labelled retrospective by design (rule F round 18, BI1, BI7)." The [DECISION] (delegate) repeats this.

**Owner-proxy pass:** yes. **Batch 2's standing:** yes; it states the label BI1 sets, and changes nothing beyond it. **Class:** wording, and a reporting duty.

### BI4b. The same script, and one earlier read, printed status counts of batch-1 and reference runs (D25:49)

**Trace.**
- At 17:59:48 (fdf/a487, Input 205) the `sed` blanked `ok` and `unfinished` for `w3000` folders only. The rerun printed `cut -c1-400` of the whole table.
- At 17:59:58 (Input 209) a compact section printed `ok` and `unfinished` in full for every other folder: the 13 batch-1 runs and the five reference runs. This is DERIVED from the two inputs; it is a BELIEF that the tool's output was not cut by length before those rows.
- At 17:56:29 (fdf/a487, Input 73) the subagent printed `cat … | head -80` of `20261110-063647_burst_l1pl350cl_r2.2_s2/checks.json`, a batch-1 run (FILE(analysis/k3w.py:61)). By the layout the [CORR] derives, those lines hold its `no_errors` counts.

This changes no batch-1 label. Batch 1 is retrospective (D25:1), its tolerances were fixed knowing its numbers (D25:49), and a whole-run count says less about W than the published completion rates over W (D25:50). But "What was known" lists what was printed on batch-1 runs, and these prints are not in it.

**Replacement text:** in D25:49, after BI4's inserted sentences, add: "On 2026-11-12 the same context-pack subagent also printed the `no_errors` counts `ok` and `unfinished` of every run other than REG-19's, batch-1 and reference runs included (17:59:48 and 17:59:58 UTC; the tool's output may have been cut by length). At 17:56:29 UTC it printed the first 80 lines of REG-14's burst run's `checks.json`, which hold the same counts (tool-call inputs; the agent has not read the output; rule F round 18, BI4b)."

**Owner-proxy pass:** yes (D25:111). **Batch 2's standing:** no. **Class:** a disclosure.

### BI8. "Batch 1 as the primary analysis" must not read as a blind reading (review-stop item 4; D25:1, D25:49)

**Trace.** With batch 2 retrospective, review-stop item 4 says "batch 1 as its only primary reading", and the agent's message says "batch 1 would be the primary analysis". Batch 1 is "a retrospective reading" (D25:1): "both tolerances were fixed knowing these numbers" (D25:49), and its labels are predicted before anything is computed (D25:52). REG-21 then has no reading whose thresholds were fixed blind. "Primary" can be read in a later claim as confirmatory. This is the trace on which batch 1's standing is hit: in wording, not in computation.

**Replacement text** (the first lines of draft 26's text, beside the title): "Neither batch was fixed blind. Batch 1, the reading this entry reports first, is retrospective: its tolerances were fixed knowing its runs' published numbers. Batch 2 is retrospective by design (read (x)). No label of REG-21 supports more than a description of these runs. In item 4 of the review-stop rule, 'primary' means the reading cited first, not a confirmatory one (rule F round 18, BI8)."

**Owner-proxy pass:** yes. **Batch 2's standing:** no. It concerns batch 1's label in words. **Class:** wording.

## Notes

- The owner-proxy's APPROVE on draft 25 (8a3e059) was written before the [CORR] reached it. Under item 4, the text with batch 2 retrospective gets its own rule F review and owner-proxy pass, so that approval does not carry over to draft 26.
- For REG-22's reviewers (outside this review): Read 2 is of seed 17's control. If REG-22's batch 2 reads controls, Read 2 may fire its counterpart of the trigger.
- **Not checked:** the new probe files listed above (not opened); the tool outputs of every call named here; whether the 17:59:58 output was cut by length.
