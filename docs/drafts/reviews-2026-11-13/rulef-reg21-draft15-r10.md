# Rule F round 10 on REG-21 draft 15 (agent a0adfd0cddd98f5fb), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:20:22Z), no word changed. It saw the bundle `docs/drafts/review_bundles/reg21_r10/` and the code at `8164211`.

---

REG-21 draft 15, round-10 adversarial review (rule F): NOT READY

H1 is only partly fixed. Draft 15 rightly ties the cut to a committed record, made then, and treats a missing record as fail-safe. But the record is defined loosely enough that the operator can still shape the time, in three ways:
- A record committed late lets changes made after the table was read count as "before" it. In that one case draft 15 is looser than draft 14.
- When the first run of the table fails, it is unclear which file is the record, and the two readings give opposite answers.
- An accidental run with every REG-19 folder sealed would become "the record" and end batch 2 for no reason.

Everything else in the 14 → 15 diff is stricter or neutral. One text-only fix is needed, and no code has to change.

How I worked (same limits as before):
- I opened nothing under `runs/`, the backups, any `state/reg19_*` file, or any `docs/probe/` output. I checked that `docs/probe/20261113_reg19/ops_r3/final.sh` exists and is byte-identical to the bundle copy (`cmp` only), and I read only the bundle copy.
- HEAD is `ab6988f`. `git diff 8164211 HEAD` is empty for the nine named files, `k3.py`, `modelf.py`, `modelf_sim.py`, `harness/` and both power-limit base configs.
- The bundle diff equals a fresh `diff`. Draft 15 is byte-identical to `docs/drafts/reg21_draft15.md`, and the draft-14 copy is the one I reviewed.
- The two newly cited review files exist.
- New synthetic trace: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r7_scratch/runner/trace_sealed_reg19.py. It sets `find_runs` to return nothing and refuses `load_run`, so no run folder is read.
- Fresh diff: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r7_scratch/d1415.diff
- Line numbers below are draft 15's.

**1. Round 9's items**

1. **H1, the cut's time from a record made then: PARTLY fixed** (lines 107, 108, 54, 55). The record, the ancestry test and the no-record fallback are right. Three gaps are left (J1–J3 below).
2. **Optional items taken, all correct:**
   - line 55 defines "REG-19's table" (FILE(analysis/gate.py:2044) resolves to `reg19_table`);
   - line 108 (b) adds a third list, which catches a flag rewritten in `checks.json` with no entry;
   - line 104 makes a judged-path change committed after the record end batch 2's governing role, with no review route;
   - line 98 cites FILE(configs/stage2_l1pl350_base.yaml:6), which resolves;
   - line 3 has its comma.

**2. Findings**

**J1. A late record commit makes the ancestry test admit changes made after the table was read. Required. This is the one case looser than draft 14.**
- Inputs:
  - At 12:00Z, `final.sh` takes its stamp (`final.sh:20`), computes REG-19's table into `reg19_final_<12:00Z>.txt`, and prints it (`:32`).
  - At 12:20Z, a commit X lands. X is one of: REG-21's [REG] or its delegate [DECISION]; a [CORR] to REG-19's counting; or a REG-20 change to a judged function in `k1.py`.
  - At 12:30Z, the record is committed.
- What the text says (line 107): X's commit is an ancestor of the record's commit, so it "counts as made before that time". The consequences:
  - Line 54: batch 2 is read as unread data.
  - Line 104: the review route stays open instead of "retrospective".
  - Line 107: a change to the counted seeds does not end batch 2.
- What should happen: X came after the table was read. Draft 14's time-based cut would have put it after. The record's own file name holds the stamp that shows this, and the rule ignores it.
- "Commits that file at once, before any other commit" is the only guard, and its breach has no stated consequence. With other sessions committing every few minutes, "before any other commit" is also easy to break by accident.
- (b) is a backstop only for flags and counted seeds. Nothing backs up lines 54 and 104.

**J2. A failed first run leaves "the record" ambiguous. Required.**
- Inputs:
  - `final.sh` run 1: `analysis.gate reg19` raises. stdout goes to an empty `reg19_final_<t1>.txt`, because `gate`'s main prints once, at the end (`gate.py:2108–2122`).
  - `final.sh:31` then requires an [OPS] entry and the file set aside before a second try.
  - Run 2 succeeds into `reg19_final_<t2>.txt`.
- What the text says (line 107): "whoever first runs … saves its output … commits … at once; that commit is the record, and its output lists the counted seeds". The first commit is the empty file; only the second lists the seeds.
- What actually happens: the operator decides which commit is the record, with REG-19's table public. The answers are opposite:
  - Record = the empty file: (b)'s third list is empty, so "any two differ", and batch 2 is not computed.
  - Record = run 2: batch 2 is computed.
- The failed run printed no table and revealed no outcome. So the successful run's file should be the record.

**J3. A run from `main` with every REG-19 folder sealed becomes "the record". Required, folded into the same fix; this is a fail-safe that misfires, not a loosening.**
- Inputs: someone runs `python -m analysis.gate reg19` on `main` before REG-19's [RESULT]. `withheld.keep` skips every REG-19 folder (seal pattern `*_l1pl350cl_r2.0_w3000_s1[5-9]`, `withheld.py:27`).
- Synthetic trace: it prints `{'outcome': 'too_few', 'n': 0, 'seeds_run': [], 'excluded': []}` with no rows and no raise.
- What the text says: that run is the first run of `analysis.gate reg19`.
  - If it is saved, it is the record. (b) then compares against no runs, the lists differ, and batch 2 is not computed.
  - If it is not saved, "every change counts as after it", REG-21's own entry included. Line 54 then makes batch 2 retrospective.
- Nothing about REG-19 was seen.
- Small inexactness in the same sentence: "its output lists the counted seeds with their runs (`rows[].runs`)". The rows hold the seeds run; counted = rows minus `excluded`. `excluded` is always empty here because no REG-19 seed is exposed.

**Stricter or neutral, checked:**
- **Line 54:** "committed before" is now "an ancestor of the record's commit". It is mechanical, and stricter except for J1.
- **Line 104:** strictly stricter.
- **Line 108 (b):** the third list is stricter. Compared against the record's runs, it catches any validity flip after the record of a run the record names, or of a run that was invalid at the record and is now valid.
- **F1 (lines 84, 113):**
  - The check and the contrast comparison are made on committed files of verbatim stdout.
  - `json.dumps` prints floats in full and NaN as `NaN`, so the `EPS` and NaN rules work on the file.
  - A quote that differs is corrected by a [CORR]. That resolves draft 14's ambiguity and loosens nothing.
  - Batch 2's file is committed before any reading is written. After the output exists, no route to "not computed" remains: duty (a) and the flag rule apply only "before batch 2".
- **Line 107's cited `final.sh:20`** is the stamp-and-file line.

**3. Verdict: NOT READY.** One change is required. It touches E1's cut, so under the proxy's own list it needs an owner-proxy pass.

- **Required (line 107).** Replace the text from "From this entry on, whoever first runs" through "…with no record made." with:
  "From this entry on, whoever first runs `analysis.gate reg19` with REG-19's runs readable ("REG-19's table"; not `reg19_step`'s flag, and not a run on which the seal skipped every REG-19 folder, whose `seeds_run` is empty) saves its stdout verbatim to a file whose name carries the UTC time at which the command was started (REG-19's script already does: `reg19_final_<UTC stamp>.txt`, FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20)), and commits that file at once on the branch that holds this entry. The record is the first such file that holds the table, with its commit; a run that raised printed no table, and its files go in with the [OPS] entry `final.sh` requires before a second try. The record's output lists the seeds run with their runs (`rows[].runs`) and those left out of n (`excluded`). The cut is the UTC time in the record's file name. For this bullet, for duty (a) and for "What was known", a change or an entry counts as made before the cut only if the commit that makes it is an ancestor of the record's commit and its committer time is earlier than the cut; any other counts as after it, and so does every change if the table was computed or read with no record made."
  - In line 108 (b), write "the burst runs of the seeds the record counts (its rows less `excluded`)".
  - Both the stamp and the commit times come from the Mac's clock (`final.sh` runs there), so they can be compared.

Optional:
- **Line 54:** write "the commits of this [REG] and of its delegate [DECISION]" in place of "the entry's commit", in case they are two commits.
- **Line 55:** the window's first event, "REG-21's batch 1", still has no recorded time. Name batch 1's saved output file (F1, line 113) with the UTC time the command was started, and count an overrule as blind only if its commit time is earlier. This matters little, because after the window only the owner can change the rule and the change governs nothing.

**4. What I could not check**
- **Under docs/probe/ (not opened):** `common.sh` (where `$ST` lies, the format of the stamp, and whether `state/` is tracked or gitignored), and whether `final.sh` commits anything itself.
- **Real runs and state files:** whether `analysis.gate reg19` has already been run anywhere, which would make line 54 fail today.
- **docs/ outside the bundle:** REG-19's resume rules; the proxy's files beyond the bundle copy.
- **Not rerun:** pytest (the code is unchanged; 35 passed in round 7). Not run: `python -m analysis.k3w reg21`.
