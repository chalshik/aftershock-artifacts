# Rule F round 8 on REG-22 draft 13 (agent a7e69db175dbd3a1d), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T12:18:26.429Z), no word changed. It saw the bundle `docs/drafts/review_bundles/reg22_r8/` and the code at `ffc76b3`. Its items Z1–Z3 are called AC1–AC3 elsewhere (Y1 keeps its name), to keep them apart from the Z rows of `agent/PLAN.md` and the owner-proxies' items.

---

Rule F review of REG-22, draft 13 (round 8): NOT READY

Scope, as you asked: the diff from draft 12 to draft 13, whether Y1–Y5 are met, and any new double reading the diff creates.

- **Met:** Y3, Y4, Y5, O1, O2, X1 and N2 are in and hold.
- **Two items are still required, both text only:**
  - **Z1 (new, made by the diff).** Y2 replaced "a value that a row of `reg19_table` holds" with "a value computed from what the runs measured", and its list includes "whether a run ended cold, backlogged or stuck" and "re-warming". That now reaches the recorder's status lines (`t=… h=… N=… Q=… KV=…`, FILE(harness/recorder.py:159–162)). Every REG-19 run has printed these to its log since 2026-11-11. It also reaches the waiting line, running batch and KV in the same lines of seed 17's control that the agent read on 2026-11-12. The carve-out names only "the live hit rate … which is no row field", and "no row field" is not the criterion the passage now uses. On a hostile reading, REG-19's table was first produced unsaved, so there is no record and batch 2 is not computed.
  - **Y1 (only partly met).** The definition and the fallback are in line 124. That line also requires "the registration that owns the batch states in its entry that none was printed before its entry commit, or gives the time of the first". Draft 13 makes no such statement anywhere.
- **Optional:** Z2 (O2 meets the S1 statement test) and Z3 (a late statement that discloses a run). Neither can let batch 2 govern where it should not, except through a forged stamp.

Line numbers refer to `docs/drafts/review_bundles/reg22_r8/registration_draft13.md`.

**Bundle and code checks:**
- Draft 13 is byte-identical to `docs/drafts/reg22_draft13.md`.
- The draft-12 copy is the one I reviewed.
- The bundle diff equals a fresh diff.
- `round7_rule_f.md` equals `rulef-reg22-draft12-r7.md`.
- The scripts and `delegation.md` are unchanged.
- At HEAD `3e9c73f`, `git diff ffc76b3 HEAD -- analysis harness tests configs pyproject.toml uv.lock` is empty.

**Shared passage:** from "Here "REG-19's table"" to the citation sentences, it matches REG-21 draft 22's line 107 sentence by sentence, apart from cross-references.

## 1. Y1–Y5, one line each

- **Y1: PARTLY.**
  - In line 124: the first run is defined as printed output by any entry point, of the table or of `c2.levels`, `c2.links` or `c2.sustain`; the fallback takes "the earliest of the time of that first output where it is known, …".
  - The statement that line 124 requires of REG-22's entry is missing. I searched draft 13 for it, and the clause appears only as the duty itself. "What was known" (lines 66–79) lists other computations on the 13 runs but says nothing about `c2` output.
  - Without that statement, the fallback's premise (never later than the true time) is unattested again.
- **Y2: MET for what it targeted, but it creates Z1.**
  - Names, ids, seeds, validity, the `[run] start` line, the queue's lines, and `done` and `continue` are now excluded by name.
  - The saving duty ends once a record is saved (N1, second half).
- **Y3: MET** (line 133).
  - The full statement covers runs up to the stamp. It is committed after the record's commit and before batch 2's command.
  - The early statement covers runs only up to its own commit.
  - If no full statement passes the test (a strict ancestor of the commit that adds batch 2's saved output, with `%ct` before that file's stamp), batch 2 is retrospective, read from git alone.
  - My round-6 O3 slip is closed.
- **Y4: MET** (line 133: "the check of the record's seeds under "Runs" is then not made").
- **Y5: MET** (line 132).
  - For pre-cut hunks: a rule F review that is READY or NOT READY, plus an owner-proxy pass stating that every required item is met.
  - The readout exemption still requires "READY with no open required item", stated explicitly.

**The rest of the diff:**
- **O1: MET** (line 132: reach is static, on any branch, as line 131 defines it).
- **O2: MET** (line 130). See Z2 for how it meets Y3.
- **X1: MET, stricter.** A commit that joins the branch after the stamp counts as after, and a merge counts as the commit that makes every change it brings in.
- **N2: MET.** The reflog entries and a decreasing first-parent `%ct` decide mechanically. Honest work on one Mac clock does not trigger them, so they give no lever.
- **Line 130's "(except under the statement rule of the commit-order bullet)":** consistent with Y3.

## 2. The code

Unchanged since `ffc76b3`. Read this round for Z1:
- **FILE(harness/recorder.py:141):** the recorder prints `status_line(...)` to stdout during the run.
- **FILE(harness/recorder.py:155–162):** that line holds the hit share `h`, `N` running, `Q` waiting, `KV%`, the lag and the SM clock, all computed from the run's live metric scrapes.
- **FILE(harness/run.py:80):** the harness prints its `[run]` events.
- **FILE(docs/decisions.md:4276):** on 2026-11-12 "the session that ran the queue read about the last 15 lines of that run's harness log on the VM, which showed a live hit rate after the arrivals had ended". Those last lines are status lines, so they also showed N, Q and KV.

## 3. The text

### 3.1 Z1: the new criterion reaches the run's own status lines and the rest of the interim look (required)

**What line 133 now counts as REG-19's table:**
- any "printed or displayed output (to a terminal, a file, a notebook or a log)", by any module, of "a value computed from what the runs measured (their requests, metrics or GPU samples)";
- for one REG-19 run, values such as "whether a run ended cold, backlogged or stuck" and "re-warming".

**What it excludes:**
- names, ids, seeds, `exposed`, `lam_p`, validity and checks, by name;
- "the live hit rate the agent read … which is no row field".

**Trace A, run-time printing:**
- Every REG-19 run's recorder printed status lines to its log from 2026-11-11 on. Near the end those lines show `h=0.00 Q=… KV=95%`, that is, whether the run ended cold and backlogged.
- These are measured values, "printed … to a log", "for one REG-19 run", and on the list. No exclusion names them.
- The only defence is "Only output computed on REG-19's own run folders counts". That clause was written to keep out synthetic folders. It does not say whether a run's own live output counts.
- **Hostile reading:** the first table was printed on 2026-11-11 and never saved, so there is no record and batch 2 is not computed.
- Under draft 12's criterion (row fields) these values were not the table, so the diff created this reading.

**Trace B, the interim look:**
- The roughly 15 lines read on 2026-11-12 showed h, N, Q and KV for seed 17's control after its arrivals ended.
- The carve-out covers only "the live hit rate". Its reason, "no row field", is not the passage's criterion.
- Q and KV after the arrivals ended show "whether a run ended … backlogged", which is on the list.
- **Hostile reading:** that display was the first table, unsaved, so there is no record.

Both readings come out opposite to the intended one, and either can be chosen after REG-19's table.

### 3.2 Y1's missing statement (required)

- Line 124 makes the owning registration responsible for this fact. If REG-22's entry says nothing, "the time of that first output where it is known" is empty, and the fallback is min(E22, D).
- That is later than the truth if anyone printed a `c2` result on the 13 real runs before E22.
- The agent wrote `c2.py`, so it is the only one who can state this.

### 3.3 Z2: O2 meets the Y3 statement test (optional)

- Line 130 says a batch file stamped later than its commit's committer time "counts as a first run that did not write its file this way".
- Line 133's test compares against "batch 2's saved output" and its stamp.
- For such a file there are two readings:
  - **Reading A:** it is still the saved output. A statement committed after batch 2's true start but before the late stamp passes, so batch 2 governs.
  - **Reading B:** there is "no saved output", so batch 2 is retrospective.
- Only a forged or mistyped stamp produces this, because line 130 requires `date -u` in the same command line. That is why it is optional.

### 3.4 Z3: a disclosure in a statement that fails the test (optional)

- "A run made known before batch 2's command runs is stated in such an entry, and the rule for no record applies" can conflict with "what any statement says does not govern" when that entry fails the ancestry-and-time test.
- The two readings give "not computed" and "retrospective". Batch 2 governs nothing under either, so this is optional.

## 4. Verdict: NOT READY

### REQUIRED

**Z1 (line 133; mirror in REG-21's line 107).** Replace "Nor is the live hit rate the agent read in seed 17's control's harness log on 2026-11-12 (FILE(docs/decisions.md:4276), FILE(docs/probe/20261111_reg19/ops/RESUME.md:20–21)), which is no row field; it is listed under "What was known"." with:

"Lines that a run writes about itself while it runs (its harness or launch log: the harness's `[run]` events, FILE(harness/run.py:80), and the recorder's status lines `t=… h=… N=… Q=… KV=…`, FILE(harness/recorder.py:159–162)) are not REG-19's table when written. Displaying such lines of a run that REG-19's table counts, showing a time after its burst ends (for a control, after its control time), is producing REG-19's table, with one exception: the about 15 lines of seed 17's control's harness log that the agent read on 2026-11-12 (FILE(docs/decisions.md:4276)), whatever values they show (the hit rate, the running batch, the waiting line, KV), which are listed under "What was known" and are not REG-19's table."

This changes what counts as REG-19's table, so it needs owner-proxy passes for both registrations. Deciding to display such lines is made before the data, so the display sentence gives no lever after it. REG-19's own rule forbids that display anyway (common.sh:34).

**Y1 (add to "What was known", lines 66–79, as a new bullet).**

"**No earlier output of batch 1's table.** No output of `c2.reg22_table` on real run folders, and no result of `c2.levels`, `c2.links` or `c2.sustain` for one of batch 1's runs, was printed or displayed before this entry's commit."

If that is not true, write instead "the first was printed at <UTC time>". If the agent cannot state either, write: "not known; the committer time of the first commit that added `c2.sustain` to `analysis/c2.py` stands in for it (a limit: code run before its commit is not covered)".

### OPTIONAL

- **Z2 (line 133, the statement test).** After "that output's file name" add: "(a file that line 130 counts as not written that way, a stamp later than its commit included, is no saved output here)".
- **Z3 (line 133).** After "the rule for no record applies to it" add: "(if that entry fails the test below, batch 2 is labelled retrospective and the disclosed run is reported beside it)".

### Process

- Z1 needs both owner-proxies; it touches "what counts as REG-19's table".
- Y1's statement is a fact of the entry, not a rule change.

### Can it change a decision?

Unchanged: line e at P ≈ 0.0017 to 0.084, batch 1 at about 0.05 (BELIEF), 0 GPU h.

## 5. What I could not check

- **Not opened, as instructed:** `runs/`, the backups, `state/` contents including the `launch_*.out` files, and probe outputs. RESUME.md:20–21 was not read either.
- **What the 15 lines showed:** whether they include values beyond h, N, Q and KV. I infer their form from recorder.py, not from the log.
- **Other displays:** whether any other launch-log lines of a counted REG-19 run, showing times after the burst or control time, were ever displayed.
- **Earlier `c2` output:** whether `c2` was ever run on the 13 real runs. Only the agent can state this (Y1).
- **REG-21 draft 22 beyond line 107:** in particular whether REG-21's entry states its own batch-1 fact for order (c).
- **Not run:** `pytest` and every analysis. Nothing was written into the repo.
