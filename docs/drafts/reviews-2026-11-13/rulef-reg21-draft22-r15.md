# Rule F round 15 on REG-21 draft 22 (agent a0adfd0cddd98f5fb), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T12:27:11.417Z), no word changed. It saw the bundle `docs/drafts/review_bundles/reg21_r15/` and the code at `8164211`. Its items P1–P4 and O1–O5 are called AD1–AD4 and AD-O1 to AD-O5 elsewhere, to keep them apart from the owner-proxy's P1–P3 on draft 19.

---

REG-21 draft 22, round-15 adversarial review (rule F): NOT READY

Scope: the draft 21 → 22 diff (lines 3, 54, 104, 107, 108, 113, 219–223), my N1–N3, and new double readings the diff creates. Code at `8164211`. HEAD is `3e9c73f`; since `8164211` only c2.py, k5.py and their tests have changed, and harness/ is unchanged.

Integrity checks:
- The bundle's drafts 21 and 22 equal their sources, and the bundle diff equals a fresh diff.
- final.sh, common.sh, delegation.md and round14_rule_f.md equal their sources.
- FILE(docs/decisions.md:4276) resolves to the seed-17 control reading.
- RESUME.md and vm_state.py exist. I checked existence only.
- The shared record passage, split into sentences and diffed against REG-22 draft 13's line 133, differs only in cross-references and REG-22's own closing sentences. So P1 and P3 below apply to both registrations word for word.

## 1. Round 14's items
- **N1 (narrow O-3 to measured values; the saving duty lasts only until a record): met.** It is in line 107, from "Here "REG-19's table" is any printed or displayed output…" to "…are not REG-19's table", plus "The saving duty holds until a record has been saved". My own wording of N1 opened P1 (see section 5).
- **N2 (O-2's git facts decide with no reading): met.** It is in line 107, "These facts decide, with no reading of them: …", extended with X1. It decides by reflog label, which leaves P3 open (also my wording).
- **N3 (the S1 statement gets a time test against batch 2's output stamp): met.** Line 107 says: "If no statement that covers runs up to the record's stamp has a commit that is a strict ancestor of the commit that adds batch 2's saved output and a committer time earlier than the UTC start time in that output's file name (…; with no saved output, none has) … batch 2 is labelled retrospective". The breach sentence "A run of batch 2's command made before the statement's commit, saved or not…" is also there.

## 2. Findings

### P1. The live status lines of every REG-19 run already fit the new definition of REG-19's table (line 107). Required.
- **Inputs:**
  - Seed 15's, 16's or 17's burst run, 2026-11-11/12, with the recorder on.
  - All through W, `harness.recorder` prints one status line per scrape to stdout: `t=… h=<hit rate since the last scrape> N=… Q=<waiting> KV=…%` (harness/recorder.py:141, :150–161). That stdout "stays on the console" (harness/run.py:177).
  - decisions.md:4276 confirms such a log, with a live hit rate, for seed 17's control. The burst runs share its config family (BELIEF, not checked).
  - At the end of a stuck burst run's watch, these lines show h=0.00 with Q high or rising.
- **What the text says:**
  - The first sentence of line 107 counts "any printed or displayed output (to a terminal, a file, a notebook or a log), by any entry point … of any other function that prints, for one REG-19 run …, a value computed from what the runs measured (their requests, metrics or GPU samples): … whether a run ended cold, backlogged or stuck; the completion rate `c` or another rate over W; …".
  - The exclusions that follow name folder names, seeds, `exposed`, `lam_p`, validity flags, check names, the `[run] start` line, the queue lines, `done` and `continue`. They do not name gauge lines.
  - The new sentence "Nor is the live hit rate the agent read in seed 17's control's harness log … which is no row field" excludes one reading of one control run. It gives a reason, "no row field", that the new first sentence no longer uses: draft 22 dropped the row-field test (draft 21's "a value that a row of `reg19_table` holds") for "a value computed from what the runs measured".
- **Reading A (literal first sentence):**
  - The recorder's console output for seed 15's burst, on 2026-11-11, is the first run of REG-19's table. Nobody needs to have read it, because "printed … to a terminal … or a log" is enough. Its h is a rate in W, and its last lines show whether the run ended cold and backlogged.
  - It was not saved by final.sh, so K1 applies: there is no record, and batch 2 is not computed, for REG-21 and REG-22 alike, today.
  - The S1 statement ("no run that gave REG-19's table is known to have started before the record's stamp") cannot be made truthfully.
- **Reading B (the reason in the seed-17 sentence, and the owner-proxy's W1 aim that "no identifier, validity line or gauge reading already printed can be read as the first run of the table"):** a gauge line is not the table, and batch 2 can govern.
- **Who chooses:** whoever writes or challenges the batch-2 [RESULT], after REG-19's table and batch 2's output are seen. The outcomes are opposite.
- **The same split for a future reading:** someone tails seed 18's or 19's burst-run log during its watch and sees h=0.00 with Q rising.
- **A smaller case of the same kind:**
  - The text excludes "the checks that set it (`checks.json`; …)" in one sentence, but only "the names of failed checks" in the sentence before it.
  - `checks.json`'s `accounting` detail holds `scheduled`, `ok` and `vllm_success_delta` (harness/checks.py:80–82). Their difference shows the backlog at the run's stop.
  - Whether a hand print of those fields is "the checks" (excluded) or "a value computed from what the runs measured … backlogged" (the table) is the same open choice.
  - The automatic flows do not print them: `harness.run` prints only VALID or failed names (harness/run.py:219, :246), and `recheck_ok` keeps validity fields only (common.sh, RECHECK_FILTER and :200–213).

### P2. Y5's "a rule F review of its diff, READY or NOT READY" (line 104). Required.
- **Inputs:**
  - REG-20 changes a function on REG-21's judged path; the owner-proxy's X1 trace uses `k1.windows`.
  - Rule F returns NOT READY on version v1 with item Z.
  - Commit C (v1 plus Z's fix) at 11:00Z. An owner-proxy pass at 11:30Z states that Z is met in C. Stamp at 12:00Z.
- **What the text says:** the exception keeps batch 2 if "its commit, a rule F review of its diff, READY or NOT READY, and an owner-proxy pass … states that every required item of that rule F review is met in it" are all made before the cut.
- **Reading A:** the review of v1 is a review of "its diff", meaning the change in an earlier version. The exception holds, and batch 2 governs on the changed path.
- **Reading B:** C's diff is v2. No rule F review of C's diff exists, so the exception fails and batch 2 is retrospective.
- Reading B leaves "NOT READY" almost without effect, so A is the intended reading. The words still allow B, and the choice falls after batch 2's output.

### P3. The reflog rule decides by label, so a `reset` (or `checkout -B`, `update-ref`, `push`) that moves the branch forward escapes it (line 107). Required.
- **Inputs:**
  - REG-20's judged-path change and both its reviews are committed at 11:00Z on branch `reg20`, cut from `main` after this entry.
  - `main` has no commit of its own since the branch point, which is plausible in a quiet window.
  - Stamp at 12:00Z.
  - At 12:03Z, after reading REG-19's table, the delegate runs `git reset --hard reg20` on `main`. The reflog shows "reset: moving to reg20".
  - The record is committed at 12:05Z.
- **What the text says:**
  - X1's sentence counts a join "by a merge, a fast-forward, a cherry-pick or a rebase" as after.
  - The quoted facts list `reset`.
  - The deciding sentence covers only `rebase`, `amend` and `filter` ("rewrote") and `merge`, `cherry-pick` and fast-forward ("brought onto").
  - Then: "with no such entry and no such decrease, no rewrite or late join is assumed".
- **Reading A (mechanical, as the text says it must be):**
  - A reset is not a listed entry, and first-parent times rise (11:00, 12:05).
  - So no late join is assumed. The change's commit is a strict ancestor with `%ct` before the cut, so line 104's exception holds and batch 2 governs on the changed path.
  - Without the reset, batch 2 governs on the old path. The path is chosen after the table, which is rule A5.
- **Reading B:** the reset moved `main` forward, a fast-forward in effect, so X1 makes it after and batch 2 is retrospective.
- Other labels outside the list behave the same way: "branch: Reset to" (`checkout -B`), an `update-ref` entry with no message, "update by push".
- Draft 21 left this consequence open (my N2). Draft 22 now positively assumes "no late join" for unlisted labels, which is looser for this one route.

### P4. Y1 relies on an append-time check that does not cover what Y1 says it covers (lines 111 and 113). Required (small).
- Line 113 says "the append-time check ('At the append of this entry') states that none was printed for batch 1 before the entry commit". "None" means an output of `k3w.reg21_table` or a judged value (U, r, a label).
- Line 111's check names U, uncached-token rates, mean served prompt, reuse and busy share. It does not name r, a label, or `k3w.reg21_table` output.
- An r printed for batch-1 runs gives J1's answer directly, yet passes line 111 as worded. The check is made before data, so the fix is stricter and needs no pass.

## 3. Verdict: NOT READY. Required changes, as replacement text

**P1 (line 107; needs an owner-proxy pass because it is on "what counts as REG-19's table"; same words in REG-22's line 133).**
Replace "Nor is the live hit rate the agent read in seed 17's control's harness log on 2026-11-12 (FILE(docs/decisions.md:4276), FILE(docs/probe/20261111_reg19/ops/RESUME.md:20–21)), which is no row field; it is listed under "What was known"." with:

"Nor is any field of a run's `checks.json`, nor a line printed while a run is in progress or as it stops by the harness recorder's status line (`t= h= N= Q= KV= lag= sm=`, one scrape each, FILE(harness/recorder.py:141, :150–161)) or by vLLM's own periodic stats log, whoever prints or reads it and whatever it shows. Each such value or line of a REG-19 run that anyone read before the record is listed under "What was known", with its run, its time and what it showed, and changes no label; the live hit rate the agent read in seed 17's control's harness log on 2026-11-12 (FILE(docs/decisions.md:4276), FILE(docs/probe/20261111_reg19/ops/RESUME.md:20–21)) is one."

Also, before the entry is appended, the agent lists every other program that ran during REG-19's runs or queue and prints a value computed from a run's measured data (`vm_state.py`, `session_probe.sh`, the queue scripts). Each is either named in that sentence, with the same pass, or judged now under the general rule, before batch 2's output, and stated in the [DECISION]. I could not read them.

**P2 (line 104; needs a pass because it is on "which reviews keep a hunk"; same words in REG-22's freeze).**
Replace "its commit, a rule F review of its diff, READY or NOT READY, and an owner-proxy pass that approves that commit and states that every required item of that rule F review is met in it" with:

"its commit, a rule F review, READY or NOT READY, of that commit's diff or of an earlier version of it, and an owner-proxy pass that approves that commit and states that every required item of that rule F review is met in it and that the commit differs from the reviewed version only by changes that review asked for"

**P3 (line 107; needs a pass because it is on "when a commit counts as joining the branch"; same words in REG-22's line 133).**
- In X1's sentence, replace "by a merge, a fast-forward, a cherry-pick or a rebase" with "by any update of the branch other than a commit made on it (a merge, a fast-forward, a cherry-pick, a rebase, a reset or any other)".
- In the reflog sentence, replace "(whether any `rebase`, `amend`, `reset`, `filter`, `merge`, `cherry-pick` or fast-forward entry appears, each with its time beside the stamp)" with "(every entry dated after the stamp, with its label, its old and new values and its time beside the stamp)".
- Replace "every commit that a `rebase`, `amend` or `filter` reflog entry dated after the stamp rewrote, and every commit that a `merge`, `cherry-pick` or fast-forward entry dated after the stamp brought onto the branch, counts as after the cut" with "every commit that a reflog entry for the branch dated after the stamp brought onto it (each commit `git rev-list <old>..<new>` lists for that entry), whatever the entry's label (`commit`, `merge`, `cherry-pick`, `rebase`, `amend`, `reset`, `pull`, `fetch`, `branch`, `update by push` or none), counts as after the cut".

**P4 (line 111; no pass needed, because it is stricter and checked before data; REG-22's own append check should be compared, which I did not do).**
Replace "no computation has yet printed U or any uncached-token rate," with "no computation has yet printed U or any uncached-token rate, r, a label of either test or any output of `k3w.reg21_table`,".

**Optional:**
- **O1.** "saved or not" in the breach sentence rests on a report made after the output. That is the class of report rejected in O-f's other half, though it errs only toward "after". Add "(this rests on the report, within the honesty limit S1 states)", as line 113 does for batches.
- **O2.** decisions.md:4276 cites RESUME.md:18 for the seed-17 reading, while lines 54 and 107 cite RESUME.md:20–21. One may be stale. I could not read RESUME.md.
- **O3.** Reflog entry times follow the committer date a command is given (BELIEF), so a reset or merge run with a set date shows before the stamp. Name this beside "an expired or cleared reflog" as a limit. Only a push to a remote before the stamp closes it (the owner-proxy's note).
- **O4.** P1 leaves a disclosed leak: a person can learn from live lines whether seed 18 or 19 ended stuck before the record, and still make a reviewed pre-cut path change. A stricter owner's option is "a judged-path change committed after anyone read such a line of a REG-19 burst run after its burst counts as after the cut". It is a self-report that errs toward "after", and it needs a pass.
- **O5.** "the earliest of the time of its first output where that is known and REG-21's entry commit" (line 113) is always the entry commit for REG-21's own batches. It is harmless, and it matters only for REG-22's order rules.

## 4. Looser than draft 21?
- **Y5 (line 104):** this settles draft 21's "passed its diff with no open required item" on its looser side. Under a strict reading, a NOT READY review never "passed". This is deliberate (REG-22 rule F round 7's W5), and the owner-proxy's statement is committed before the cut. The [DECISION] should say so.
- **The reflog rule:** it now positively assumes "no late join" for unlisted labels (P3), looser than draft 21 for the reset route.
- **The seed-17 exclusion:** not looser. No row held a live hit rate under draft 21's test.
- **The N1 narrowing and the end of the saving duty:** deliberate.
- **Stricter:** X1, N3, Y1 and the late-stamped batch file. O-d is consistent with S2.

## 5. My errors (rule A6)
- **N1's words were mine** (round 14: "a value computed from what the runs measured (their requests, metrics or GPU samples): …"). In round 14 I wrote under "could not check" that the VM probes "would count" under N1, and I did not make it a required item, although the recorder's status line was in my code snapshot. That opened P1.
- **N2's words were mine and decided by reflog label** ("a `rebase`, `amend` or `filter` reflog entry"), not by what an entry brought onto the branch. Draft 22 extended my list with X1's labels, and the label approach left P3.

## 6. Can it change a decision?
Yes, unchanged from round 14. Batch 1 (13 named runs) and, if the record rules let it govern, batch 2 (REG-19's burst runs) decide whether K3 step B is read as a work rate. Cost: 0 GPU h. P1 bears on this directly: under reading A, batch 2 is already not computed for both registrations, so the decision would rest on batch 1 alone.

## 7. Not checked
- Whether the recorder was on for REG-19's burst runs, and where their console output is kept (VM log, tmux, a committed queue output). I opened nothing under runs/, state/, the backups or the probe outputs. decisions.md:4276 confirms the recorder output for seed 17's control only.
- vLLM 0.32.0's periodic stats log line: the pinned source is not on the Mac. BELIEF: it prints prompt throughput, running and waiting counts, KV use and prefix-cache hit rate every few seconds. If its prompt throughput counts only uncached tokens, it is close to U itself. This belongs in docs/open-questions.md.
- What `vm_state.py` and `session_probe.sh` print. I checked existence only, and did not resolve the vm_state.py:6 citation.
- Whether r or a label was ever printed for batch-1 runs before now (P4).
- Commits or reflog on the VM, and pushed history.
- pytest and check_docs were not rerun. The REG-21 path and harness/ are unchanged since `8164211`.
