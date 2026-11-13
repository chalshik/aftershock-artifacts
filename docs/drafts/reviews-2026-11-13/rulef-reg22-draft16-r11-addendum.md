# rulef-reg22-draft16-r11-addendum (rulef-reg22-r11), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T17:12:12.526Z; message 2 of 2 from this teammate). Addendum after the [CORR] at decisions.md:4453; adds BK7, BK8, makes BK-S4 required.

---

Addendum to rule F round 11 on REG-22 draft 16, on the [CORR] at decisions.md:4453 and the agent's reading. Save it with the review. The verdict is unchanged: NOT READY on batch 2's standing.

## Addendum: the [CORR] at decisions.md:4453 and the agent's reading of D16:80

I had already found the [CORR] at HEAD and built BK1 on it. Below I answer the two questions in your messages. All of it is from tool-call inputs and the cited files; no output was opened.

### 1. Is the agent's reading of D16:80 wrong on any trace?

On substance, no.
- `unfinished` and `ok` sit in `checks.json`, which the harness writes at the run's end (FILE(harness/checks.py:237), as cited by FILE(docs/decisions.md:4453)). So for seed 17's burst run they are lines written after its burst began.
- D16:80 does not list them.

On the letter, there are two traces on which the trigger does not fire. BK1's replacement closes both; the second needs one more sentence.
- **(a) "If it then finds."** In D16:80, "then" refers to the rerun at E. Read 1 was found before E, by hand labelling. If the next draft lists it as item (x), the rerun at E finds nothing "beyond what is listed here", and batch 2 stays primary. This is why BK1 fixes the list at draft 16.
- **(b) "Most likely printed."** The [CORR] derives the print from the inputs. A reader could say the trigger needs a read that is shown to have happened. Showing it would mean opening the output, which is itself a look at batch-2 data.

Add to BK1's replacement, after its first sentence:
> A read counts when the tool-call inputs make it likely, as the [CORR] judges Read 1; no output is opened to settle it.

- **Class:** a stricter rule.
- **Batch 2's standing:** yes. It is part of BK1.

### 2. Is batch 1's standing also hit?

Batch 1's standing words ("thresholds fixed after these runs were reported") cannot fall further. Its trigger in D16:81 fires only on an output of `c2`. No new trace hits either. But three things touch batch 1.

**BK7 (new). A batch-1 look not in D16:81.** On 2026-11-12, a context-pack subagent of session fdf13821 ran `s57_heavy.py` at 18:00:40 UTC (T(fdf13821/agent-a48736828ce71b739:221)) and printed from it at 18:04:51 UTC (:343).
- It loaded every run folder whose name lacks `w3000`, so batch 1's runs were included.
- It printed, per run:
  - `load.verdict`'s baseline and end-window percent fast, hit share, waiting line and KV;
  - the whole-run KV maximum;
  - `checks.json`'s `ok` and `unfinished`.
- These are close to the values REG-22 judges at the end of the watch.
- It is not `c2`, so the batch-1 trigger does not fire. D16:81 names this script only as the one that skips `w3000` folders, and it names REG-20's smoke test as the one batch-1 hit outside `c2`.

In D16:81, after "(found by round 2's owner-proxy on REG-21, BF5(a), FILE(docs/drafts/reviews-2026-11-13/proxy-reg21-draft24-delta.md:144)).", insert:
> On 2026-11-12 at 18:00:40 and 18:04:51 UTC a context-pack subagent of session fdf13821 ran `s57_heavy.py`, which loads every run folder whose name lacks `w3000`, batch 1's runs included, and printed per run `load.verdict`'s baseline and end-window percent fast, hit share, waiting line and KV, the whole-run KV maximum, and `checks.json`'s `ok` and `unfinished` counts (DERIVED from the command texts, tool-call inputs only; the output was not opened); these are close to values REG-22 judges at the end of the watch; they are not an output of `c2`.

- **Owner-proxy pass:** yes. It adds to batch 1's "What was known", as BB1 did.
- **Batch 2's standing:** no.
- **Class:** a disclosure.

**BK8 (new). Seed 17's control.** Read 2 (`head -c 300` at 11:50:49 UTC) and Read 1's control row reach the control's `ok` and `unfinished` counts (FILE(docs/decisions.md:4453)). D16:80 says only that the first 300 characters were printed.
- The trigger covers burst runs only.
- A control's counts bear on its `recovered` flag. That flag feeds the count reported beside line a ("how many of the k runs have a same-seed control that is `recovered` …", D16:91 and the bullet under line a). This is a reported number, not a decision line.

In D16:80, after "at 11:50:49 UTC it printed the first 300 characters of that run's `checks.json`", insert:
> , which by the file's layout reach the control's `ok` and `unfinished` counts if the run had ended (FILE(docs/decisions.md:4453), Read 2); those counts are not an allowed read under REG-19 (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:36)) and bear on that control's `recovered` flag, which batch 2's control readout reports beside line a

Also add Read 1's control row to the same sentence.
- **Owner-proxy pass:** no. It is a disclosure of a read the [CORR] already records.
- **Batch 2's standing:** no. The trigger is about burst runs, and batch 2 is retrospective by BK1 anyway.
- **Class:** a disclosure.

**BK-S4, now required, with a trace on batch 1's line a.**
1. After the stop, batch 2 is already retrospective by design.
2. A text written under item 4 could then drop facts (1) and (2) and the validity cut, because they no longer move batch 2's standing.
3. But a retrospective batch 2 still enters the disagreement test (BC1). There it can withhold line a's permission and line d's wording, and those are batch 1's decision lines.
4. Without the freeze, a change to `c2` or its imports made after REG-19's table would change batch 2's labels. Through that disagreement, it would decide whether batch 1's line a applies.

The replacement for item 4 of the stop entry is as given in BK-S4:
> The text written under item 4 keeps the freeze, the two facts, the validity cut and the not-computed rules, which decide whether batch 2 is computed and with which words; items of its review are applied as usual, and no further stop exists.

Apply the same in the text written under the stop, in place of D16:133's opening "From this entry to batch 2 the frozen files do not change, with no exception".
- **Owner-proxy pass:** yes.
- **Batch 2's standing:** yes. It is "what a retrospective batch 2 does" (item 3), and it is the trace on which batch 1's line a could be steered.
- **Class:** a stricter rule.

BK3 (the "batch 2 pending" window after S) is the other trace that reaches batch 1's line a. It stands as written.

### 3. The agent's planned handling

- Read 1 as item (x), the corrected wording of item (iii) on `checks.json`, and the 17:56:24 UTC listing under (viii): agreed, as disclosures. They match BK6(d).
- Listing Read 1 does not take it out of the trigger. Batch 2 is retrospective by design (BK1).

### Not checked in this addendum

- The [CORR]'s evidence files (`inputs_s57_inv.txt`, `search2_20261113T163634Z.txt`, `search2_fix_added_…`, `classify2_…`, `labels.tsv`). They are probe outputs outside my bundle, so my limits forbid them. I read the fdf13821 subagent's inputs directly instead.
- `search2.py` at d960ef3.

Nothing was written to the repository.
