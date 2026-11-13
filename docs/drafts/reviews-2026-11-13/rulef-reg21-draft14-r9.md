# Rule F round 9 on REG-21 draft 14 (agent a0adfd0cddd98f5fb), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input, 2026-11-13T11:13:14Z), no word changed. It saw the bundle `docs/drafts/review_bundles/reg21_r9/` and the code at `8164211`.

---

REG-21 draft 14, round-9 adversarial review (rule F): NOT READY

Both of round 8's required items are fixed as worded, and the optional items taken are correct. E1 moves the cut to the right point, so it is stricter, not looser. But draft 14 does not say where the time of that cut comes from. In one concrete case, the person running batch 2 supplies that time from memory, with REG-19's outcomes public, and the time decides whether batch 2 exists. That needs one text-only fix; no code has to change.

How I worked (same limits as before):
- I opened and listed nothing under `runs/` or the backups. Under `docs/` I read only the bundle and checked that the two newly cited review files exist.
- Besides the bundle I read `harness/checks.py:188`, `configs/l1_pl350_base.yaml:7` and the burst configs' `extends:` chain.
- HEAD is `929a507`. `git diff 8164211 HEAD` is empty for the nine named files and also for `analysis/k3.py`, `modelf.py`, `modelf_sim.py`, `harness/` and the two power-limit base configs.
- The bundle diff equals a fresh `diff`. Draft 14 is byte-identical to `docs/drafts/reg21_draft14.md`, and the draft-12 copy is the one I reviewed.
- I did not rerun the tests: the code is unchanged, and `tests/test_k3w.py` passed 35 in round 7.
- Fresh diff: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r7_scratch/d1214.diff
- Line numbers below are draft 14's.

**1. Round 8's items**

1. **Required 1 (the `batch1_median` check): FIXED, verbatim.**
   - Line 84 compares within `EPS` against the median batch 1's command printed, quoted in full. A NaN for a λ = 2.0 group of fewer than three judged runs is not a mismatch, and line 75 then applies.
   - Line 76 says governance rests on the contrast "and the check of `batch1_median`".
   - Line 113 says the batch-1 [RESULT] quotes each group's median in full.
   - The one remaining sub-case is coherent: a group of fewer than three judged runs in batch 1 but three or more on recomputation prints a number, so it is a mismatch, and batch 2 does not govern.
2. **Required 2 (the clock mechanism in alternative 10): FIXED, verbatim** (line 98). The power-limit sentence is added; its citation is incomplete (Optional).
3. **Optional items taken, all correct:**
   - line 73 (precedence of the check);
   - line 107 (`MemoryError` and `KeyboardInterrupt` count as interruptions; a code-caused `MemoryError` can only repeat, and nothing is printed before the end, so the operator chooses nothing);
   - line 110 (a table printed under a stray heading ends batch 2 for good);
   - line 86 (`reported_spans`' own run list, `k3w.py:419`);
   - line 108 (a) (the same `runs/` as (b));
   - line 103 ("committed" in both sentences);
   - line 99 (BELIEF tag);
   - line 59 (a REG-22 that is never registered as a route).
   - The comma fix in line 3 moved the missing comma: it now reads "D1 to D3 rule F round 7's".

**2. Findings on E1 and the rest of the 12 → 14 diff**

**H1. E1 (lines 107, 108 (a)): the cut is right, but the time it rests on has no stated source. Required.**
- Direction: the cut is now when REG-19's table is first computed or read, at the latest its final [RESULT]. That is no later than draft 12's cut, so every change that ended batch 2 under draft 12 still does. Line 55's window uses the same event. No ceiling is raised.
- Trace:
  - Inputs:
    - The agent runs `analysis.gate reg19` in the worktree and reads the table (T1). Nothing is saved.
    - Later the same day, an entry marks seed 18's burst run invalid.
    - The table is recomputed and counts seeds 15–17. REG-19's [RESULT] reports that recomputed table.
  - What the text gives:
    - Line 107: batch 2 is not computed if the entry came after T1.
    - (b) compares valid folders 15–17 with the counted seeds 15–17. They are equal, so (b) does not catch it.
    - Line 107: "the batch-2 [RESULT] gives the time REG-19's table was first computed".
  - What actually happens:
    - decisions.md headings carry a date, not a time. The only record of T1 is the agent's memory.
    - The batch-2 operator states T1 with REG-19's c on screen. Placing T1 before the entry ends batch 2; placing T1 at the recomputation keeps it.
    - The window E1 was written to close is exactly where the text leaves the choice open.
- Two smaller points:
  - The duty sentence sits inside the list of "not computed" conditions ("if …; if …; the batch-2 [RESULT] gives the time …; or if …").
  - A validity flag rewritten in `checks.json` with no entry (`runs/` is gitignored) breaches (a) but leaves no record (Optional).

**H2. The rest of the diff: no other defect.**
- Line 59's new route is consistent with lines 102–103.
- Line 98's two new citations resolve (`harness/checks.py:188`; `configs/l1_pl350_base.yaml:7`). That parent covers the reference sweep. The burst runs inherit the check through `stage2_l1pl350_base.yaml:6` instead: `burst_l1pl350_r2.4_s1` → `stage2_l1pl350_base` → … → `base`.
- Line 110's added clause closes round 8's G5.
- E2 lives in the [DECISION] (delegate), not in the entry. That is acceptable, because the [DECISION] is on record too.

**3. Verdict: NOT READY.** One change is required. It touches E1's cut, so under the proxy's own list it needs an owner-proxy pass, though it is stricter.

- **Required (line 107).** Delete "; the batch-2 [RESULT] gives the time REG-19's table was first computed" from the list of conditions. After the sentence that ends "or if duty (a) below is breached.", add:
  "For this bullet and for duty (a), the time REG-19's table was first computed or read comes from a record made then (REG-19's entry, or the commit that holds the table's output), not from memory, and the batch-2 [RESULT] cites it; a change that record does not place before that time counts as after it."
  - An accepted alternative: if the entry already requires REG-19's [RESULT] to record when its table was first computed (the proxy says round-4 condition 10 does, which I cannot see), cite that requirement in this sentence and keep the last clause ("a change … counts as after it").

Optional:
- **Line 98:** add FILE(configs/stage2_l1pl350_base.yaml:6) for the burst runs.
- **Lines 55 and 107:** say once that "REG-19's table" is the output of `analysis.gate reg19`, not of `reg19_step`. The step computes each seed's outcome internally between seeds but prints only the flag (`gate.py:2022–2041`).
- **Line 108 (a):** to make its first clause checkable for flags rewritten with no entry, have REG-19's record at T1 list the counted seeds and burst run names, and have (b) also compare against that list.
- **Line 104:** its route "rule F and an owner-proxy pass come before batch 2" is always taken after REG-19's table is public, because batch 2 follows REG-19's [RESULT]. To match E2's principle (no stopping-rule change once REG-19's table is computed or read), the alternative "batch 2 is labelled retrospective" could be the only one.
- **Line 3:** comma after "D1 to D3".

**4. What I could not check**
- **docs/ outside the bundle:**
  - whether round-4 condition 10, or REG-19's own entries, require a record of when REG-19's table was first computed (this decides whether the alternative to the required item suffices);
  - REG-19's resume rules on rulings made after its table is read;
  - draft 13;
  - the proxy's round-8 file beyond the bundle copy.
- **Real runs:**
  - whether any validity flag of a REG-19 burst run has been changed, or would be, without an entry;
  - the folder list the [DECISION] must hold.
- **Not rerun:** pytest (the code is unchanged; 35 passed in round 7). Not run: `python -m analysis.k3w reg21`.
