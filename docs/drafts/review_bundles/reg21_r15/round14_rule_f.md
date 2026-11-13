# Rule F round 14 on REG-21 draft 21 (agent a0adfd0cddd98f5fb), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T12:11:03.123Z), no word changed. It saw the bundle `docs/drafts/review_bundles/reg21_r14/` and the code at `8164211`.

---

REG-21 draft 21, round-14 adversarial review (rule F): NOT READY

M1 and M2 are fixed, and V1–V3, U1, U2 and the shared passage hold. On your two questions:
- **S2's mirror holds.** No case now governs that draft 20 would not let govern. But deleting the record after the table still moves batch 2 from governing to not governing; S2 only turns "not computed" into "retrospective".
- **O-3 does catch things it should not, in two places:**
  - **Before the record:** a row of `reg19_table` also holds folder names, seed numbers, `exposed` and `lam_p`. The harness printed REG-19 folder names at every run's start. Under the literal reading, that print was "the first run that gave REG-19's table", it was never saved, and so there is no record and batch 2 is not computed. Draft 21's own folder listings (lines 104 and 108) would do the same.
  - **After the record:** REG-20's `reg20` table, REG-22's batch 2 and REG-21's own batch 2 all become "REG-19's table", so the saving duty applies to them. That has no effect on any label.

Three items are required, all text only:
- **N1:** close O-3's list.
- **N2:** give O-2's facts a fixed consequence. As written, the reader decides what a reflog entry or a decreasing time means, after the data. This is my own O-2's loose end.
- **N3:** S1's ancestry test does not show that the statement came before batch 2 ran.

All three touch the proxy's list (what counts as output, the rewritten-commit rule, the record's statement), so all three need an owner-proxy pass and the same words in REG-22.

How I worked:
- **Limits kept.** I opened nothing under `runs/`, the backups, any `state/` file or any probe output. I read harness and analysis code at `8164211` only.
- **Repo state.** HEAD is `b8ea915`. Since `8164211` only `c2.py`, `k5.py` and their tests have changed. The judged path, `harness/` and `configs/` are unchanged.
- **Bundle copies.**
  - Draft 21 is byte-identical to `docs/drafts/reg21_draft21.md`, and the draft-20 copy is the one I reviewed.
  - The bundle diff equals a fresh `diff`.
  - `final.sh`, `common.sh` and `delegation.md` equal their sources.
- **Shared passage.** I cut both passages from "Here "REG-19's table"" to "These compute nothing" and diffed them sentence by sentence. They differ only in cross-references.
- Line numbers are draft 21's.

**1. Round 13's items and what was mirrored**

1. **M1: fixed (line 104), with V3.** Names come from the directory listing, sealed and invalid folders included, and the list covers `ref_pattern`. My REG-30 trace now puts the seal on the judged path.
2. **M2: fixed (line 107).** A rewrite after the stamp counts as after, whatever date it carries.
3. **O-2: taken, but no consequence is attached** (N2).
4. **O-3: over-catches** (N1).
5. **O-4, O-5 (as V2) and O-6: fine.** V2 reads approval from the committed texts alone, so nothing is left to judgement after the data.
6. **V1: fixed.** FILE(analysis/gate.py:2038) is `reg19_step`'s internal `reg19_pair` call.
7. **U1 and U2: hold.** One consistency note on U2 is in O-c.
8. **S1: one hole** (N3).
9. **S2: holds** (Q-A below).

**2. Findings**

**N1. O-3: "a value that a row of `reg19_table` holds" includes names and config values. Required.**
- **Inputs:**
  - A row holds `seed`, `runs` (folder names), `exposed` and `lam_p` (FILE(analysis/gate.py:2055–2056)). The last two come from the schedule alone (gate.py:1811–1819, 1852).
  - The harness prints `[run] start {'run_id': …}` at every run's start (FILE(harness/run.py:80), FILE(harness/run.py:143)), and so at seed 15's first REG-19 run on 2026-11-11. That run's folder name is "a value that a row holds", printed for a REG-19 run on its own folder, so R4 does not exclude it.
  - Draft 21 itself requires folder names of REG-19 runs to be printed: duty (a)'s `test -e` list (line 108) and M1's directory listing (line 104), both before the record.
- **What the text says (line 107):** the parenthetical "(a verdict, an outcome or the completion rate `c` …)" reads as examples. The governing phrase is "a value that a row … holds".
  - Under that reading, the first "REG-19's table" was the harness print. It was not "saved under a stamp taken as this bullet requires", so "there is no record", and batch 2 is not computed.
  - The intended reading makes `final.sh`'s output the record.
  - These are opposite outcomes, open to anyone after REG-19's table.
- **Q-B, your question, after the record exists:**
  - REG-20's `python -m analysis.k1 reg20` prints a row per REG-19 run with its folder name, `cold_backlogged` and readouts (FILE(analysis/k1.py:269–276), FILE(analysis/k1.py:305)). REG-22's and REG-21's batch 2 print per-run rows too. Under O-3 each is "REG-19's table", so the saving duty applies: `state/`, a stamp, stderr, committed at once and alone.
  - None of them can be the record, which stays the first output. So there is no label effect, only a duty that conflicts with line 113's place for batch 2's file, and that gets breached.
  - `reg20_a_may_start` prints only counts (`k_closed`, `n`, `best_p`, `may_start`; FILE(analysis/k1.py:186–192), FILE(analysis/k1.py:279–280)). It is outside O-3 as worded. Before REG-19's [RESULT] it sees REG-19's runs only under `AFTERSHOCK_UNSEAL=REG-19`, which is not REG-20's to set. If it is run that way, it leaks `k` with no cut. N1's count clause catches that case.

**N2. O-2's facts are quoted but decide nothing (line 107, the reflog sentence). Required.**
- **Inputs:** the [RESULT] quotes the reflog and finds that one committer time on the first-parent chain decreases.
- **What the text says:** they are given "as facts for the sentence on rewritten commits". Whether a decrease shows "a date not taken from the clock" (after the cut, so retrospective) or clock skew (nothing) is left to the writer, who holds batch 2's output.
- **What it should be:** a fixed rule. On one branch with one clock, honest work (commits, `--no-ff` merges, fast-forwards, rebases and cherry-picks without date options) never makes the first-parent chain decrease. A mechanical rule is therefore almost free of false positives and leaves no lever.

**N3. S1's statement can come after batch 2 has run and still pass (line 107).**
- **Inputs:**
  - At 14:00 batch 2 runs, and its output is saved and seen.
  - At 14:10 the statement "no earlier run known" is committed.
  - At 14:20 the output file is committed.
- **What the text says:** "its commit a strict ancestor of the commit that adds batch 2's output". 14:10 is a strict ancestor of 14:20, so it passes, and "what it states governs", although it was written with batch 2's labels known. This is J1 again, for S1.
- **No consequence is stated for a statement that is missing or late.**

**Q-A, S2's mirror: holds, with one residual lever.**
- **Consistent with the rest of the passage:**
  - "Lost" is not "no record": sentence 20 defines no record as never saved, and P3 says leaving a file uncommitted never makes it so.
  - (b) then compares its first two lists, and sentence 23 says so explicitly.
  - Line 54 makes batch 2 retrospective, because the [DECISION] lands after the entry's commit.
  - Any flag entry on a batch-2-pattern run since the entry now counts as after, so line 107's flag rule and duty (a) give "not computed". The sentence covers this with "if the other rules let it be computed". Either way batch 2 does not govern.
  - Nothing governs that draft 20 would not let govern.
- **Residual:** a record deleted after the table still moves batch 2 from governing to retrospective. S2 removed only the "not computed" label.
  - Deleting is not delegated and needs the owner (CLAUDE.md C; delegation), and the owner may overrule anyway. So this is optional.
  - The fix is a floor taken from facts (O-a).

**3. Verdict: NOT READY.**

**Required N1 (line 107).**
- For "or of any other function that prints, for a REG-19 run, a value that a row of `reg19_table` holds (a verdict, an outcome or the completion rate `c`; `reg19_cold_side`, FILE(analysis/gate.py:1834), for one)," write:
  "or of any other function that prints, for one REG-19 run or as a count over them, a value computed from what the runs measured (their requests, metrics or GPU samples): a verdict, label or outcome under any registration's rule; whether a run ended cold, backlogged or stuck; the completion rate `c` or another rate over W; the cold side; `c1`; a drain or emptying time; `q_ratio`; the end-window slope or unreleased turns; re-warming; `order_flag` or the baseline difference (`reg19_cold_side`, FILE(analysis/gate.py:1834), for one). Folder names, seed numbers, `exposed`, `lam_p` and other values taken from names or configs alone, validity flags and the names of failed checks, and checksums or sizes are not REG-19's table, whoever prints them, although a row of `reg19_table` holds some of them,"
- After "the record's commit message quotes that line." add:
  "The saving duty holds until a record has been saved; REG-19's table produced after that (REG-19's own [RESULT], REG-20's tables, REG-22's and this registration's batch 2) needs no saving under this bullet and is never the record."

**Required N2 (line 107).** After "…as facts for the sentence on rewritten commits." add:
"These facts decide, with no reading of them: every commit that a `rebase`, `amend` or `filter` reflog entry dated after the stamp rewrote counts as after the cut, and so does a commit on that chain whose committer time is earlier than its first parent's; with no such entry and no such decrease, no rewrite is assumed (an expired or cleared reflog cannot be detected: a limit)."

**Required N3 (line 107).**
- For "(its commit a strict ancestor of the commit that adds batch 2's output)" write:
  "(its commit a strict ancestor of the commit that adds batch 2's output, and its committer time earlier than the UTC start time in that output's file name, compared as instants; where batch 2's first run wrote no file, only the ancestry half can be checked: a limit)"
- After "and batch 2's command is not run before it exists;" add:
  "if no statement meets this, what any statement says does not govern and batch 2 is labelled retrospective;"

Optional:
- **O-a, a floor for a lost record (S2).** When the record is lost, take as the cut the latest `stopped` wall time (UTC) in `events.jsonl` among the runs REG-19's final [RESULT] counts (FILE(harness/run.py:77), FILE(harness/run.py:216)). No table can predate that time, given S1's statement. A change before it, and an ancestor of the commit that adds REG-19's heading, then counts as before. Losing the record would then decide nothing. These folders can be read only after REG-19's [RESULT], which is when batch 2 runs.
- **O-b, S1's two moments.** A statement committed "before `final.sh` runs" covers runs only up to its own commit. Say that a second statement, covering up to the record's stamp, is committed before batch 2's command when the first was made before `final.sh`.
- **O-c, U2's evidence.** U2 ties order-rule consequences to a self-report of an unsaved first run, the same kind of evidence refused for O-f's second half. It errs only toward "after", so it is acceptable. Saying "consistent with S1's honesty limit" would keep the reasoning uniform.
- **O-d, line 108 (b).** Add a pointer: "(with a lost record, the first two lists only; 'Batch 2 not computed')".

**Can it change a decision?** Yes, unchanged. Batch 2's J1 sets what may be said about λ = 2.0 and K3's status, at 0 GPU h.

**4. What I could not check**
- **The launch logs.** The committed `state/launch_*.out` files: from harness/run.py:143 and their names, I believe they hold `[run] start` lines with REG-19 folder names, but I did not open them. N1 does not depend on it.
- **The VM probes.** Whether `vm_state.py` or `session_probe.sh` print measured values from REG-19 run folders during runs. Not read (docs/probe, outside the bundle). Under N1 they would count.
- **Earlier hand runs.** Whether anyone has already printed a measured REG-19 value by hand. If so, K1 applies today.
- **Reflog settings.** Reflog retention on this Mac (`gc.reflogExpire`), which bounds O-2's facts.
- **VM commits and pushed history.** Whether commits are made on the VM, and whether `main` is pushed anywhere.
- **REG-22 draft 12.** Read only at its line 133.
- **Tests.** I did not rerun pytest; the judged path is unchanged.
