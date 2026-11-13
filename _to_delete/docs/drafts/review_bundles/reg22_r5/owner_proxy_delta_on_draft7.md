# Owner-proxy delta pass on REG-22 draft 7 (agent a43b6d3c375ffd53e), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:27:12Z), no word changed. A delta to round 1 (conditions 1–16) and to the delta on draft 5 (D1–D8); code at `ffc76b3`. The agent calls its conditions 1–7 "Q1–Q7" to keep them apart from round 1's.

---

**Decision: APPROVE**, as a delta pass on REG-22 draft 7 (FILE(docs/drafts/reg22_draft7.md), byte-identical to docs/drafts/review_bundles/reg22_r4/registration_draft7.md) at code `ffc76b3`. HEAD is now `ac5100d`: two commits since 72d4884, both docs or agent state. `git diff ffc76b3 -- analysis/ tests/` is empty.

This approval has no effect while rule F round 4 on draft 7 is outstanding or NOT READY. Conditions 8–16 from round 1 and D1–D8 from round 2 stay in force. I find D1–D8 met in draft 7: lines 56, 110, 75, 58/60, 53, 17, 78, 4/165–176, 132, 92, 142, 133 and 134. The PROTOCOL re-reading is still not approved; it needs the owner (rule C, decisions.md 2026-11-13 delegation).

**Reasons:**
1. **The code is unchanged.** There is no diff in analysis/ or tests/ since ffc76b3. Round 3 of rule F found the judged path AST-identical to 727d1f2, so the round-2 code findings stand.
2. **F4, the order with REG-21 (line 124), is acceptable.**
   - Batch 1 waits, or a [DECISION] fixes REG-21's thresholds, label map and judged functions at a named commit.
   - A later change to them is A5 and outside the delegation.
   - REG-22's table goes into REG-21's "What was known".
   - Line 128 makes batch 1 wait for (a) or (b).
   - This is stricter than draft 6, not looser.
3. **F5, the freeze (line 132), is stricter.**
   - It now covers `onsets`, `onset_reading`, `planned_rates`, `control_readout`, `reported_counts` and `__main__`, as well as the judged path.
   - The diff list adds gate.py, derived.py, floor.py, k3.py, modelf.py, modelf_sim.py and harness/workload.py.
   - Before the cut, a change needs rule F plus a proxy pass. After the cut, batch 2 is retrospective and no review restores it.
4. **The record and its cut (line 133) are acceptable, and identical to REG-21's.**
   - The cut is the UTC stamp in the file name, which final.sh writes when the command starts (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20), `stamp` at FILE(docs/probe/20261113_reg19/ops_r3/common.sh:40), `date -u`). A delay before the commit therefore does not move the cut.
   - The record lands in `docs/probe/20261113_reg19/ops_r3/state/` (common.sh:7–8), which git does not ignore (`git check-ignore` rc=1), so it can be committed.
   - What remains is a suppression risk: a table computed and never recorded. Line 64 now covers it as a not-computed case ("computed or read and no record is made"), so the risk is visible rather than silent.
5. **The new not-computed cases at line 64 only remove batch 2.**
   - They cover a seed or validity change after the cut, and a missing record.
   - They never add a reading, and none of them depends on batch 2's outcome. This is consistent with my round-2 approval of change (a).
6. **F3 is not uniformly a lower ceiling; the coordinator's reading is partly wrong.** Case by case:
   - **Batch 2 not computed:** the same as draft 6.
   - **Batch 2 with fewer than 3 stuck runs at λ = 2.0:** draft 6 contradicted itself (line 101 against line 102). Draft 7 adopts line 102's reading, that batch 1's sentence stands with batch 2 reported per run. That is not strictly lower than every reading of draft 6. It is acceptable because the choice was made blind to batch 2, but it needs disclosure (condition 2).
   - **Mixed batches:** stricter than rule F proposed. A batch that meets none of the lines disagrees with one that meets a line, and neither is claimed.
   - **Both batches with at least 3 stuck runs that meet the same line:** unchanged.
   - Net: lower or equal everywhere except the fewer-than-3 case, which is a resolved contradiction rather than a raised ceiling.
7. **F1, the onset reading, is honest.** Line h (line 100) is now lower: pair readings per run with no tally. Onsets remain reported only and judge nothing.
8. **F6, the prediction arithmetic (lines 11 and 84), checks.**
   - DERIVED: 0.6 × 0.7 × 0.20 = 0.084, and 0.6 × 0.7 × 0.004 ≈ 0.0017.
   - The text rounds 0.084 up to "≈ 0.09" (condition 6).
9. **F2 is incomplete.**
   - Line 8 was rewritten.
   - Line 36 still ends "So `loop` means 'no span re-warmed for most of its length', at 300 s resolution". That contradicts line 8 and line 36's own first sentence (a full recovery of up to 65–70 s fails no link).
   - Only the text overstates; the judged code is unaffected.
10. **Optional item 5 is moot.**
    - No REG-19 seed is exposed: FILE(docs/decisions.md:3788), "No control reaches `surge_tip` 3.2 within 4080 s (highest 3.092), so no seed is exposed".
    - `excluded` requires `exposed` (FILE(analysis/gate.py:1684)).
    - So line 64's excluded-seed branch cannot arise. It is harmless, but it should say so.

**Conditions:**
1. **BEFORE the entry is appended:** replace line 36's last sentence with rule F's F2 text: "So `loop` excludes a span with the cache back for more than about 240 of its 300 s, or with a full recovery of more than about 70 s, at 300 s resolution." Text only; no new pass.
2. **BEFORE the entry is appended:**
   - Line 101's fewer-than-3 clause must give batch 2's per-run labels beside batch 1's sentence, not only "k of n".
   - The entry states, under "What was known" or under the change list, that this resolves draft 6's contradiction between lines 101 and 102 in favour of line 102, before any batch-2 data exist.
3. **BEFORE the entry is appended:** line 101 states that when the batches disagree, neither line a's D1/D2 permission nor line d's prohibition applies automatically. Any wording that relies on either waits for a [DECISION] that cites both batches.
4. **BEFORE the entry is appended:** line 64 adds two things:
   - the tagged fact that no REG-19 seed is exposed (FILE(docs/decisions.md:3788), FILE(analysis/gate.py:1684)), so the excluded-seed case cannot arise;
   - a raise of `reported_counts` during batch 2 (line 136), listed explicitly among the not-computed cases so that the list is complete in one place.
5. **BEFORE batch 1 is computed:** if order (b) is used, the deferral [DECISION] states which of the two batch-2 options it takes:
   - REG-22's batch 2 waits for REG-21's registration; or
   - REG-21's batch 2 is declared no longer read blind, with that consequence for REG-21 stated in the same entry.
6. **BEFORE the entry is appended:** at line 11, write "≈ 0.08" for the pessimistic end, or show 0.6 × 0.7 × 0.20 = 0.084. Line 11's "≈ 0.86 or more" then becomes 1 − 0.05 − 0.084 ≈ 0.87.
7. **LATER, at the batch-2 [RESULT]:** cite the record's commit hash, its file name (the cut), the ancestry check (`git merge-base --is-ancestor`) and both committer times. If any part is missing, batch 2 is labelled retrospective.

**Which later changes need another proxy pass:**
- Everything on my earlier list.
- The record and the definition of its cut.
- The before/after split of the freeze.
- F3's disagreement rule, including the fewer-than-3 clause.
- Order (b)'s batch-2 clause.

**How to treat corrections from rule F round 4:**
- **No new proxy pass:** wording, evidence tags, arithmetic, and any change that lowers a ceiling or adds a not-computed case.
- **New proxy pass required:** anything that touches the stopping rule, the not-computed cases (other than adding one), the record or cut, the freeze, the order rules, the judged path or a threshold.
- If round 4 changes code, the whole of my round-2 code reasoning must be re-checked.

**Notes for the owner:**
- **If you run REG-19's table yourself (final.sh), commit the record at once and alone.** That means `state/reg19_final_<stamp>.txt` and `state/reg19_final_err_<stamp>.txt`. final.sh saves them but does not commit them (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:29–31)). Without that commit, both REG-21's and REG-22's batch 2 are lost.
- REG-22's onset output cannot settle the order of reuse, U, N and KV. It is reported only and has no tally.
- BELIEF: P(batch 2 is computed) ≈ 0.6, so batch 2 is likely but not assured.
- Taking the "no longer blind" option under order (b) downgrades REG-21's batch 2. That is your trade-off, not the agent's.
- My own error from round 1 (reason 3, REG-12's seeds 2 and 3) stays corrected, as noted in round 2.

**Not checked by me:**
- Anything under `runs/` or the backups.
- Rule F round 4.
- Rule F's traces t01–t06 (not re-run).
- The full `uv run pytest` and `check_docs` (only tests/test_c2.py, in round 2).
- That both times in the record come from the Mac's clock in practice.
- Whether the worktree `/Users/chalshik/Projects/aftershock-reg19-pin` writes the state files into this repo's tree. common.sh sets S and ST under `R` = this repo (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:6–8)), but I did not trace final.sh's `cd $W` on a real run.
