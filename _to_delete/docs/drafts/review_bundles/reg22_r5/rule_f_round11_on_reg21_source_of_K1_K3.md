# Rule F round 11 on REG-21 draft 17 (agent a0adfd0cddd98f5fb), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:31:51Z), no word changed. It saw the bundle `docs/drafts/review_bundles/reg21_r11/` and the code at `8164211`.

---

REG-21 draft 17, round-11 adversarial review (rule F): NOT READY

Draft 17 fixes J1, J2 and J3 as I worded them, and G1's two rules are in. But the new wording of the record sentence in line 107 can be read two ways in three places. Each pair of readings gives opposite outcomes for batch 2, and the reader would choose after REG-19's table is public:
- **K1:** an earlier run that nobody saved.
- **K2:** a run made in the middle of the matrix.
- **K3:** whether "alone, nothing else" defines the record or is only a duty.

K1 and K2 each admit a reading looser than draft 15. One text-only replacement of line 107's record sentences fixes all three. It changes G1's definition of the record, so it needs an owner-proxy pass.

How I worked (same limits as before):
- **Nothing sealed opened.** I opened nothing under `runs/`, the backups, any `state/reg19_*` file or any probe output. I listed tracked file names only (`git ls-files`, `git log --stat`).
- **Repo state.** HEAD is `ac5100d`. It is two commits after `72d4884`, which touch only `agent/LOG.md`, `agent/STATE.md`, `docs/context-pack.md` and `docs/decisions.md`. Since `8164211`, only `c2.py`, `k5.py` and their tests have changed. The judged path, `gate.py`, `harness/` and `configs/` are unchanged, and `gate.py` is also identical at the pin `a7bb77a`.
- **Bundle copies.** The bundle diff equals a fresh `diff`. Draft 17 is byte-identical to `docs/drafts/reg21_draft17.md`. The draft-15 copy is the one I reviewed. `final.sh` and `delegation.md` are identical to their sources. `round10_rule_f.md` is my report.
- **The record's path.** `git check-ignore` does not ignore `docs/probe/20261113_reg19/ops_r3/state/reg19_final_X.txt` or `reg19_final_err_X.txt`.
- **The pin has no seal.** `a7bb77a` has no `analysis/withheld.py`, and `final.sh` computes the table from the worktree at that pin (`final.sh:2`, `:29`).
- Line numbers below are draft 17's.

**1. Round 10's items**

1. **J1, a late record commit: fixed.** Line 107 now says "before" = a strict ancestor of the record's commit and a committer time earlier than the stamp. In my round-10 trace (stamp 12:00Z, X committed at 12:20Z, record committed at 12:30Z), X now counts as after. The same test is used in lines 54, 55, 104 and 108 (a).
2. **J2, a failed first run: fixed.** A run that raised prints nothing (FILE(analysis/gate.py:2107–2122)). Its files go in with the [OPS] entry, and it is not the record. The same sentence opens K1.
3. **J3, a sealed run: fixed.** A run whose `seeds_run` is empty is not REG-19's table. The new qualifier "with REG-19's runs readable" opens K2.
4. **Optional items: both taken, both correct.**
   - Line 54 names the commits of the [REG] and of the [DECISION].
   - Line 55 adds batch 1's stamp as a further condition an overrule must meet; it does not replace "before the first of".
5. **Do G1 and J1–J3 agree? Yes, except in one place.**
   - They agree on: the strict-ancestor test with the time test; no record means batch 2 is not computed; failed and sealed runs neither count as the record nor set off G1's "computed with no record".
   - They pull apart on whether "alone, nothing else" defines the record or is a duty (K3).

**2. Findings**

**K1. An earlier run that nobody saved: the later saved run may become "the record". Required. Looser than draft 15.**
- Inputs:
  - At 11:00Z someone runs `python -m analysis.gate reg19` to the terminal (in the pinned worktree, for example). `seeds_run` is not empty. Nothing is saved.
  - At 11:30Z a commit X lands: a [CORR] to REG-19's counting, a REG-20 change to `k1.cold_backlogged`, or REG-21's [REG].
  - At 12:00Z `final.sh` runs. It refuses only if a `reg19_final_*` file exists (`final.sh:18–19`). It stamps 12:00Z and saves the output, and the record is committed alone at 12:05Z.
- What the text says (line 107): "The record is the first such pair whose stdout holds the table."
  - Reading 1: the 12:00Z pair is the first saved pair, so it is the record and the cut is 12:00Z. X then counts as before:
    - line 54: batch 2 is read as unread data;
    - line 104: the review route stays open;
    - line 107: the flag rule does not end batch 2.
  - Reading 2: the first computation left no record, so G1 applies and batch 2 is not computed.
- What should happen: the table was public at 11:00Z.
  - Draft 15 ("whoever first runs … that commit is the record") allowed only reading 2.
  - Draft 17's "first such pair" adds reading 1.

**K2. A run in the middle of the matrix. Required (wording). Looser than draft 15.**
- Inputs, all true today:
  - Seeds 15–17 have valid pairs, and seed 18's control is lost.
  - `reg19_step` then gives done = [15, 16, 17] (FILE(analysis/gate.py:2026–2035)).
  - `reg19_table` builds rows for those seeds (FILE(analysis/gate.py:2051–2052)), each carrying `c`, the completion rate over W (FILE(analysis/gate.py:2064)). That `c` fixes r's first factor (line 55).
  - The pin has no seal, so a run in `$W` prints all of this now.
- What the text says (line 107): the record rule covers a run "with REG-19's runs readable", and only a run whose `seeds_run` is empty is excluded.
  - Reading 1: the run is REG-19's table. Saved, it is the record, its seeds differ from the final [RESULT]'s, and (b) ends batch 2. Unsaved, there is no record, so G1 ends batch 2.
  - Reading 2: "REG-19's runs" means all of them, as in "the table … as REG-19's final [RESULT] reports it" (line 108) and "ends without the table" (line 107). Then the final run is the record, its cut is later, and changes made after the partial run was read count as before.
- Draft 15 had no qualifier. Any run of `analysis.gate reg19` counted, so reading 2 is new.

**K3. "At once, alone … and nothing else", and "pair": do they define the record, or are they duties? Required. This is an open choice, not a loosening.**
- Inputs:
  - `final.sh` stamps 12:00Z.
  - The output is committed at 12:40Z in an ordinary [OPS] commit together with `agent/STATE.md` and `docs/status.md`.
  - That is this repo's habit: every commit that has added files under `ops_r3/state/` also carried 6 or 7 other files (`b0ff529` 8 files, `69f349b` 7, `c38388b` 8).
- What the text says (line 107):
  - Reading A: "The record is the first such pair …, with its commit, which adds those two files and nothing else." No commit fits, so there is no record and G1 says batch 2 is not computed.
  - Reading B: the same sentence says "a change in the record's own commit included" counts as after. That clause only has work to do if the record's commit can hold other changes; G1's own words say the same. So the record stands, the extra files count as after, and batch 2 is computed.
- What actually happens:
  - Opposite outcomes, and the delegate picks one with every batch-2 run's `c` public.
  - Reading A also gives whoever commits the record a lever: one extra file, or a missing stderr file ("pair"), ends batch 2.
  - Since the cut is now the stamp, a late commit or extra content no longer moves the cut, so voiding the record buys nothing.

**Stricter or neutral, checked:**
- Line 54, line 104's exception and line 108 (a): "before" is now a subset of draft 15's "before".
- Line 55: the time condition is added on top of "before the first of"; nothing is removed.
- Line 108 (b): "rows less `excluded`" is the same as "the counted seeds". `excluded` is always empty here, because no REG-19 seed is exposed.
- Line 113: file names carry the start time.
- G1's "not computed" is stricter than draft 15's "retrospective".
- Dropping "before any other commit" loosens nothing: the time test now does that work.
- Excluding failed and sealed runs is correct, because neither prints anything about REG-19. Round 10's synthetic sealed run printed outcome `too_few`, n 0, `seeds_run` [] and no rows.

**3. Verdict: NOT READY.** One change is required. It changes G1's definition of the record, so under the proxy's own list it needs an owner-proxy pass.

- **Required (line 107).** Replace the text from "**The time of that cut comes from a record made then, not from memory.**" through "The batch-2 [RESULT] cites the record's file and commit." with:
  "**The time of that cut comes from a record made then, not from memory.** Here "REG-19's table" is any output of `analysis.gate reg19` whose `seeds_run` is not empty, from any checkout and however many of REG-19's seeds it holds: a run made in the middle of the matrix counts, and so does one from the pinned worktree, which has no seal. A run that raised printed nothing (`gate`'s `__main__` prints once, at the end), and a run whose `seeds_run` is empty (the seal, or no `runs/`) printed nothing of REG-19; neither is REG-19's table, and `reg19_step`'s flag is not either. From this entry on, whoever runs `analysis.gate reg19` saves its stdout verbatim to a file whose name carries the UTC time at which the command was started, and its stderr beside it (REG-19's script already does: `state/reg19_final_<UTC stamp>.txt` and `state/reg19_final_err_<UTC stamp>.txt`, FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20)), and commits those two files at once, alone, on the branch that holds this entry; the files of a run that raised go in with the [OPS] entry that `final.sh` requires before a second try (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:31)). **The record** is the saved stdout of the first run that gave REG-19's table; **the record's commit** is the first commit that adds that file to the branch that holds this entry. A record committed late, without its stderr file, or together with other changes is still the record: that is a breach of the duty above, which the batch-2 [RESULT] reports, and every other change in the record's commit counts as after the cut. The record's output lists the seeds run with their runs (`rows[].runs`) and the seeds left out of n (`excluded`); if they are not the seeds REG-19's final [RESULT] counts (a record from the middle of the matrix), duty (b)'s lists differ and batch 2 is not computed. **The cut is the UTC time in the record's file name.** For this bullet, for duty (a), for the stopping rule's bullet "Between batch 1 and batch 2" and for "What was known", a change or an entry counts as made before the cut only if the commit that makes it is a strict ancestor of the record's commit (an ancestor other than the record's commit itself) and its committer time is earlier than the cut; anything else counts as after it. The stamp and the commit times both come from the Mac's clock (`final.sh` runs there). **If REG-19's table was computed or read and there is no record, batch 2 is not computed, with that reason** (the third list of duty (b) does not exist). There is no record if the first run that gave REG-19's table was not saved under its start time, or if its file was not committed to the branch that holds this entry before batch 2 is computed; a later saved run does not take its place. The batch-2 [RESULT] cites the record's file and commit, lists every `reg19_final_*` file with its stamp (those set aside included), and states that no run of `analysis.gate reg19` that gave REG-19's table is known to have started before the record's stamp."

Optional:
- **O1, the stamp on a hand run.** A stamp later than the true start would move the cut later, which is J1 again, by hand. Say that a hand run takes its stamp with `date -u` in the same command line that runs the table, as `final.sh` does, and that the record's commit message quotes that line. A stamp later than the record commit's committer time is a breach.
- **O2, comparing times.** Compare times as UTC instants, `git log -1 --format=%ct` against the stamp. Commits here show +0600; misread as UTC, that is only ever stricter, but it can wrongly end batch 2.
- **O3, timing of G2's notice.** Make G2's `docs/status.md` notice due at the append of this entry, not before batch 1. REG-19's final run may come first, and `final.sh` prints nothing about committing (`final.sh:29–32`).
- **O4, set-aside files.** "Set aside" means moved out of `state/`. `final.sh`'s glob `reg19_final_*.txt` (`:18`) also matches the stderr file, so both files must leave `state/` before a second try.
- **O5, the full path.** Give the record's full path: `docs/probe/20261113_reg19/ops_r3/state/`.

**4. What I could not check**
- **An earlier run already made.** Whether anyone has already run `analysis.gate reg19`, in the pinned worktree or to a terminal. If so, K1 applies today. The coordinator's listing was of file names only.
- **REG-22's copy of the record rule.** REG-22 draft 7's "shared record rule" (not read). It must change in step with this one, or the two registrations could treat the same commit differently.
- **The stamp function.** `common.sh`'s stamp function was not read; I used the coordinator's account. I also cannot say whether commits are ever made on the VM, which has its own clock.
- **The [DECISION] (delegate).** It must carry E2, F1, G1 and G2, and it does not exist yet.
- **Tests.** I did not rerun pytest (the judged path is unchanged; 35 tests passed in round 7). I did not run `analysis.k3w reg21` or `analysis.gate reg19`.
