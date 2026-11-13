# proxy-reg22-draft14-delta (proxy-reg22-d14), verbatim

Saved by the agent from the teammate message received in the main session transcript, 2026-11-13 between 12:42 and 12:51 UTC (the senders' idle notifications). Item names as given by the reviewer (prefixes BA, BB, BC, BD, CA, CB were assigned in the review prompts).

---

Owner-proxy on REG-22 draft 14: APPROVE on BD1–BD9 (BD8 LATER, the rest BEFORE the entry is appended).

**Decision: APPROVE**, on BD1–BD9. d14 = FILE(docs/drafts/review_bundles/reg22_r9/registration_draft14.md), byte-identical to docs/drafts/reg22_draft14.md at HEAD e062504. What I checked in git and on disk:
- `git diff ffc76b3 HEAD -- analysis tests harness` is empty.
- No `reg19_final_*` file appears in `git log --all` or in `state/` (names only).
- The two git facts in d14:133 match REG-21 draft 23 word for word, apart from the file lists. I diffed them by sentence.

This approval has no effect while rule F on draft 14 is outstanding or NOT READY. Earlier conditions stay in force where BD9 maps them.

**1. Would the owner accept it? Yes.**
- On rule A5 it is stricter than every earlier regime: no judged-path change after the entry, with no exception.
- It removes the definition that four reviews could not close.
- Its cost is batch 2's standing, which is worth little: P(batch 2 changes a decision) ≤ 0.084 (DERIVED, d14:11).

What was dropped without being retired:
- **D7** ("does not call batch 2 'unread'") is contradicted at d14:5 ("outcomes nobody has read") and d14:80 ("read as unread data"). Fix: BD2.
- **T6's concern** (a hand run counts) has not gone away. It has moved to the time before the entry, and there it rests on a statement with no search behind it. Fix: BD3.
- **d14:91 and d14:131** cite text that was removed. Fix: BD1.

Round-1 condition 14's first half is covered by fact (2) plus `batch_runs(2)`'s raise (d14:63). D4 is now stricter, so it is met.

**2. Removing the readout exemption: acceptable.**
- The cost is known before any data, and it is bounded.
- The exemption was where the Y5 and AA3 double readings sat.
- One problem: an absolute freeze rewards leaving a known defect that does not raise unfixed. It also leaves open, after the data, which output to quote. Fix: BD6.

**3. "Disclosed, not a switch": acceptable after the entry.** A5 judges thresholds, and after the entry none can move without fact (1) failing. It is weakest in three places:
- **Before the entry.** `c2.py` was first committed 2026-11-12 19:36 UTC (d14:81). Seeds 15–17's burst runs already existed (d14:79). The seal on `main` dates from 72fafb5, 2026-11-12 19:00 UTC (git). Until then, `analysis.gate reg19` on `main` would have shown outcomes. The only guard is "known to the agent", with no search behind it, unlike Y1's. Fix: BD3.
- **"Registered before REG-19's table"** is now true by definition, because the table is whatever file `final.sh` saved, whatever else was seen. Fix: BD2.
- **Fact (2) sees only committed files.** `final.sh` tells the user to set a failed file aside by hand (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:31)). Fix: BD5.

**4. Order with REG-21: complete.** The parenthesis in (b) (d14:125) now stands on its own: first output by any entry point, the owning registration's statement, ancestry plus time, "at once and alone", and the fallback. One gap is exposed: under (a), a judged-path change made after the other registration's batch-1 table exists only demotes batch 2. Batch 1's labels have no stated consequence, unlike under (c). Fix: BD7.

**5. Stop rule: acceptable, with BD8.** It is used before REG-19's table exists (`final.sh` waits for both entries, FILE(agent/FOR_AUTHOR.md:7)), so it is not a lever. But no decisions.md entry records it (DERIVED: no match for "plan of 2026-11-13" in docs/decisions.md). And "retrospective by design" must not unfreeze the code.

**Conditions**
- **BD1 (BEFORE).**
  - d14:91: replace "only if the commit order of the stopping rule holds" with "only if both facts of the freeze hold (stopping rule, "Batch 2 is primary only if")".
  - d14:131: replace "for the order rules and the freeze's "before batch 1", see order (b)" with "for the order rules, see order (b)".
  - d14:149: delete "and the reviews it had".
- **BD2 (BEFORE).**
  - d14:5: replace "on runs whose outcomes nobody has read" with "on REG-19's runs, which no analysis is known to have read when this entry was committed (what was seen is under "What was known")".
  - d14:80: replace "For batch 2 to be read as unread data," with "For batch 2 to be primary,".
  - d14:91: after batch 2's standing, add "; run-time lines and one look disclosed in the [REG]".
- **BD3 (BEFORE).**
  - In d14:80, after "(a statement, within the honesty limit of any registration)", add: "It rests on a search of the transcripts named in the next bullet, made at this entry's commit and covering up to it, for commands that run `analysis.gate reg19`, `reg19_table`, `reg19_pair`, `reg19_cold_side` or any `analysis` module on a folder matching `*_l1pl350cl_r2.0_w3000_s1[5-9]`, or that read a REG-19 run's harness or launch log beyond the lines `common.sh`'s ALLOWED names (PROBE, quoted in the [DECISION] (delegate)). If anything beyond the 2026-11-12 look is found, this entry registers batch 2 as retrospective by design. A look before this entry that becomes known after it goes into a [CORR] that every later quote of batch 2's standing cites; it changes no label."
  - Y1's search (d14:81) is likewise rerun at the entry commit.
- **BD4 (BEFORE; REG-21 too).** Add `analysis/__init__.py` and `harness/__init__.py` to fact (1)'s list and to d14:145. Both run at import and are empty today (0 bytes, wc). Diffing the whole of `analysis/` and `harness/` is also acceptable.
- **BD5 (BEFORE; REG-21 too).** After "(… the same second counts as after)" add: "Before batch 2's command runs, every file in the working tree whose name matches `reg19_final_*` is committed (late: a breach, reported); the stamp compared is the earliest among those names and every name `git log --all` shows for that pattern. A pair moved out of the repository or never committed cannot be detected: a limit."
- **BD6 (BEFORE).** Replace "A fix to a frozen readout goes into a new function, reported beside the frozen one." with: "A defect that does not raise, found in the judged path or a frozen readout before batch 2, is logged in a [CORR] when found. Batch 2 still runs the frozen code; a fix goes into a new function or file, run by its own saved command, and is printed beside the frozen output as retrospective. Lines a, e and h quote the frozen output with the [CORR] named; if any label differs between the two, batch 2 is reported per run with both labels and adds nothing to C2's status until an owner's [DECISION]."
- **BD7 (BEFORE).** In order (a), add: "A change to REG-22's judged path after this entry and before its batch 1 is reported, and batch 1 is then values without labels, or waits for the owner (as under (c))."
- **BD8 (LATER, before the stop rule is used and before `final.sh` runs).** Log the stop rule as a [DECISION], quoting the owner's words if the owner gave them. If it is used, that entry states:
  - batch 2, retrospective by design, is computed by the same command, with the judged path frozen at the entry and these decision lines, and no code or threshold changed after the entry (A5 binds retrospective batches too);
  - the entry is committed before the first `reg19_final_*` commit.
- **BD9 (BEFORE).** The [DECISION] (delegate) lists every owner-proxy condition: round 1's 1–16, D1–D8, Q1–Q7, T1–T6, U1–U2, W1–W3, AA1–AA4 and BD1–BD9. For each it gives the sentence that meets it, or "no object since draft 14: <reason>". The mapping includes T6 → BD3, D7 → BD2, Q7 and condition 14 → fact (2). The phrase "where they still have an object" in d14:3 is not such a list.

**Which later changes need another pass:**
- None for BD1, BD2, BD4, BD5 and BD7 if written as given.
- A pass for any other wording of BD3, BD5 or BD6.
- A pass for any change to the two facts beyond BD4 and BD5. Such a change counts as the stop rule's one allowed fix.
- No pass for rule F's corrections if they are wording, tags, something stricter, or a reporting duty.

**Notes for the owner:**
- I think the redesign is right. Fourteen drafts tried to put a cut at "the first print of REG-19's table"; freezing the code at the entry makes the entry commit the cut.
- The case for batch 2 now rests on nobody having computed anything on seeds 15–17 before 72fafb5, and `c2`'s thresholds were written while those runs existed. BD3 turns that into a search.
- Until both batch 2s are computed, REG-20's code goes into new files whenever it would touch k1, load, gate, margin, stats, k3w, withheld or derived.
- Pushing `main` is still the only outside witness against rewritten history, and it is your choice.

**Not checked:**
- Rule F on draft 14.
- REG-21 draft 23 beyond the two-facts passage.
- The transcripts themselves.
- Static reach beyond the import lines I grepped.
- `pytest` and `check_docs`.
- Commits on the VM.
- That you approved the plan of 2026-11-13 (FOR_AUTHOR.md says so; decisions.md does not).
- `runs/`, backups, `state/` contents and probe outputs (not opened).

Nothing was written into the repository.
