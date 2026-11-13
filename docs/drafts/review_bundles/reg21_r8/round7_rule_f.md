# Rule F, round 7, on REG-21 draft 10 (agent a0adfd0cddd98f5fb), verbatim

Saved by the agent from the subagent's hand-back (its transcript, SubagentHandback input), no word changed. Bundle: `docs/drafts/review_bundles/reg21_r7/`; code at `8164211`.

---

REG-21 draft 10, round-7 adversarial review (rule F): NOT READY

Draft 10 fixes round 6's items 2 and 3 as worded and item 1 only in part. I found five defects in the changed sentences, all fixable in the text alone; no code has to change:
- The new overrule wording opens a way to change the governing rule after the data are public, and that way contradicts the delegation.
- The order with REG-22 can be bypassed by running batch 2 first.
- Two of the new "not computed" cases leave a reading that someone would choose after REG-19's outcomes are public.
- The new readouts sentence names too few modules to keep its promise.

How I worked:
- I opened and listed nothing under `runs/` or the backups. Under `docs/` I read only the bundle, plus two cited lines of `docs/decisions.md` (4308, cited by draft 10:59; 4236, cited by the proxy's C2), and I checked that the cited review files exist.
- I read the code from a `git archive` snapshot of `8164211` (with `harness/` and `configs/`). `tests/test_k3w.py` passes, 35 tests. It ran under a wrapper that pointed `load.RUNS` and `withheld.DECISIONS` at scratch files and refused any `find_runs` or `load_run` outside scratch.
- `git diff 8164211 HEAD` is empty for the nine named files, and also for `analysis/k3.py`, `modelf_sim.py`, `modelf.py` and `harness/workload.py`. The bundle diff equals a fresh `diff` of the two drafts, and draft 10 is byte-identical to `docs/drafts/reg21_draft10.md`.
- HEAD moved from `358418e` to `c0d4d70` during the review. The bundle did not change. Other sessions have committed a REG-21 draft 11 (`5a2c7b1`), which I did not read. Everything below is on draft 10; the agent has to map it onto draft 11.
- Scratch files: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r7_scratch/runner/guarded_pytest.py, /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r7_scratch/runner/trace_main.py, /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r7_scratch/d910.diff

**1. Round 6's three required items**

1. **Overrule window (line 55): PARTLY fixed.**
   - The window now closes at the right events: batch 1, any print of U, an uncached-token rate or r on a batch-1 run, and REG-19's table computed or read.
   - But round 6 said "can overrule *only while*". Line 55 now says "counts as made blind only before" and adds: "A change made after that point is labelled …; if the delegate makes it, it needs rule F and an owner-proxy pass."
   - That allows a change after the data are public, which draft 9 did not, and the label carries no consequence. See F1.
2. **One answer for every failure of the batch-2 command (line 105): FIXED.** The first sentence is as worded, with "for example" added. The batch-1 sentence is deleted, and the heading sentence is added verbatim.
3. **The readouts claim (lines 157, 166): FIXED as worded.** Round 6's own list was incomplete, though. See F5.

**2. Findings on the changed sentences**

**F1. Line 55: a route to change the governing rule after the data are public, open to the delegate.**
- Inputs:
  - REG-22's batch 1 prints an uncached-token rate on the λ = 2.0 runs, which closes the window.
  - REG-21's batch 1 gives a λ = 2.0 median of 1.03.
  - REG-19's [RESULT] publishes c over [1680, 4080) at about 1.79 to 1.82 req/s. By line 51 (DERIVED), that puts batch 2's median at about 1.05 to 1.08.
  - The registered rule (lines 73–74) then gives "at the tolerance, neither batch governs", or "batch 2 governs" if the contrast is above 0.05.
- What the text says: the delegate may now adopt "batch 2 always governs" after rule F and a proxy pass. The batch-2 [RESULT] applies it, with a label.
- What should happen:
  - delegation.md line 5 says "Not delegated: choosing or widening a threshold after seeing the data it judges (rule A5)". Dropping the 0.05 on the contrast is exactly that.
  - Line 54 gives a late commit a consequence ("labelled retrospective and does not govern"). Line 55's label has none, so a rule chosen after the data are public could set K3's status ("mixed").
  - This raises a ceiling relative to draft 9.

**F2. Batch 2 can run before batch 1 and bypass the order with REG-22 (line 100 / C3).**
- Inputs: REG-22 is not registered, so batch 1 is blocked by line 100. Then REG-19 reports, and REG-20's gate has run (line 101).
- What the text says: nothing stops batch 2. Line 101 asks only for REG-19's final [RESULT] and REG-20's gate. Line 84's check against "batch 1's [RESULT]" cannot be made, and a mismatch "changes nothing else".
- What actually happens:
  - `reg21_table(2)` recomputes batch 1 (`k3w.py:387`).
  - It prints `fixed_load_contrast.batch1_median` (`:390`) and `reference` with each reference run's U (`:385`, `:148`). `reported_spans` adds the reference runs' span U (`:428–433`).
  - So batch 1's λ = 2.0 median of r, and U_off, are printed before REG-22's [REG]. That is what C3 was meant to prevent.
  - Batch 1 is then "computed once" in name only. The proxy's "batch 2 cannot run before batch 1's [RESULT]" is an inference from line 84; no sentence states it as a rule.

**F3. Line 105, "a later entry changes … the validity flag": later than what?**
- Inputs:
  - Before REG-19's final [RESULT], an entry marks a seed-18 burst run invalid, and REG-19 reruns it. This could happen, for example, under REG-19's resume rules (delegation.md line 3 names "the pin rule") or because a run failed its checks.
  - REG-19 then counts seeds 15–18, and (b)'s lists agree.
- What the text says:
  - If "later" means later than REG-21's entry, batch 2 is not computed.
  - If it means later than REG-19's final [RESULT], batch 2 is computed. That second reading matches duty (a), "changes after REG-19's final [RESULT]".
- The two readings give opposite answers, and the reading would be chosen at batch-2 time, with REG-19's c public.

**F4. Line 106 (a), "the [RESULT] lists any such folder already present": nothing records which folders were present.**
- Inputs: at batch-2 time, (b)'s listing shows a folder matching the batch-2 pattern with `valid: false` that loads cleanly, so `find_runs` drops it (`load.py:42–44`).
- What the text says:
  - If it was copied after this entry, that breaches (a), and batch 2 is not computed (line 105).
  - If it was "already present", it is listed, and batch 2 is computed.
- What actually happens: no list is made at append time. So the batch-2 operator decides which case applies, after REG-19's outcomes are public. Copies made with mtime preserved hide the copy date.
- This is round 6's optional item as adopted. As written, it creates a choice.

**F5. Line 157, the readouts: two modules are missing, and `harness/` is unchecked.**
- The readouts also reach:
  - `analysis/modelf.py`, through `k3.long_run` → `modelf.l1` (`k3.py:254–259`, called at `k3w.py:198`);
  - `harness/workload.py`, through `modelf_sim.simulate`/`schedule` → `build_schedule` (`modelf_sim.py:28, 33–35`, called at `k3w.py:204`).
- `_dirty` checks only `analysis/` and `tests/` (`k3w.py:453`). So a committed or uncommitted change to `harness/workload.py` or `modelf.py` changes model F's replay readouts without showing in any diff the [RESULT] gives.
- "Marks any readout computed with changed code" cannot be done with the means stated. This affects reported-only readouts; no label depends on it.

**Smaller findings (Optional below):**
- **F6. "Before the judged table exists" (line 105) is not "before it is printed".**
  - `reported_spans` calls `batch2_runs()` again outside its `try` (`k3w.py:419`). That happens after `reg21_table` returns (`:465`) and before the print (`:468`).
  - My synthetic trace (`trace_main.py`): a raise there prints nothing. Line 105 does not cover it, so line 104 applies (fix and rerun), and that choice is made with REG-19 public.
  - This can happen only if the folder set changes between two calls seconds apart.
- **F7. The order with REG-22 is set for batch 1 only.**
  - REG-22's batch 2 takes `k3w.batch2_runs` (`c2.py:397–408` at `c0d4d70`) and judges `session_uncached_rate` (`c2.py:68`) on those runs. So the conflict where each prints what the other judges also exists for batch 2.
  - Line 100's escape names only "REG-21's batch-1 table".
  - Line 111 has no batch-2 version of C6.
- **F8. Line 109's list is narrower than line 49's.**
  - Line 109 omits "the mean served prompt".
  - It names `k1.reuse` by function, while `c2.reuse_in(later_turns(run), a, b)` (`c2.py:62`) computes the same quantity.
- **F9. Line 55 says "on a batch-1 run"; line 109 says "batch-1 or reference run".**
  - Low impact: U_off scales both batches alike, and E1 waits for REG-21's [RESULT] (`e1.py:241`).
- **F10. The example "a sixth valid reference run" raises only at a rate of 2.0 or more** (`k3w.py:139–142`).
- **F11. A breach of line 108 is not covered.**
  - With "the seal's raise" now narrowed, an interim heading (a breach of line 108) followed by an early run has no stated answer, whether the run raises or succeeds.

**Checked and could not break:**
- **"Counts" (line 106).** n is the seeds done, less the exposed seeds whose control went cold with a surge (`gate.py:1684–1686`, `reg19_table` at `:2044`). `gate.py` is identical at `a7bb77a` and `8164211`, and `gate reg19` exists at both (`:2113`, `:2122`). With no seed exposed, n's seeds are `seeds_run`.
- **Line 59.** The citation decisions.md:4308 resolves ("attempts 1 and 2 … spent; one is left … six valid runs"). 0.4 is a BELIEF, inside the proxy's 0.25 to 0.68.
- **Lines 100, 110 and 111** carry C3, C5 and C6. **Line 109** carries C4.
- **Line 108's recommendation** works: `lifted` reads the working copy of decisions.md (`withheld.py:43–47`).
- **Line 120:** `_dirty` is called a gate. **Line 102:** "(none is planned …)". **Line 3:** both new review files exist.
- **The judged path** does not reach `harness/`.

**3. Verdict: NOT READY.** These changes are required. Under the proxy's own list, R1–R4 touch the overrule window, the stopping rule, the hand duties or the order with REG-22, so they need an owner-proxy pass. R5 is reported-only and needs none.

- **R1, line 55.** Replace the last sentence with:
  "A change made after that point is not blind and does not replace the registered rule: the batch-2 [RESULT] gives the reading under the rule registered here, and only that reading sets what may be said about λ = 2.0 and K3's status; a reading under a changed rule may be given beside it, labelled with what was public when the change was made, and governs nothing. The delegate makes no such change after that point (rule A5 is not delegated: delegation, 2026-11-13); only the owner can, by an entry that says it overrides this sentence."
- **R2, line 101.** Add:
  "Batch 2 is not computed before batch 1's [RESULT] is committed: its command recomputes batch 1 and prints batch 1's λ = 2.0 median and every reference run's U (`k3w.reg21_table`, `reported_spans`), so the order with REG-22 in the bullet above binds it too."
- **R3, line 105.** Replace "if, before batch 2, a later entry changes the seeds that table counts or the validity flag of a run matching the batch-2 pattern" with:
  "if, after REG-19's final [RESULT] and before batch 2, an entry changes the seeds that table counts or the validity flag of a run matching the batch-2 pattern (a flag set before REG-19's final [RESULT] is part of what that result counts and does not end batch 2)".
- **R4, line 106 (a).** Replace "; the [RESULT] lists any such folder already present." with:
  "; the [DECISION] (delegate) that approves this entry lists every folder then in `runs/` whose name matches the batch-2 pattern, with its `valid` (true, false, or no `checks.json`; names and `checks.json` only), and "already present" means on that list. A folder without a valid `checks.json` that (b) finds and that list does not name is a breach of (a)."
- **R5, line 157.** Replace its last sentence with:
  "The readouts also call `analysis/k3.py`, `analysis/modelf_sim.py` and `gate.shock_size`, and through them `analysis/modelf.py` (`k3.long_run`) and `harness/workload.py` (`modelf_sim.schedule`, `build_schedule`), which the stopping rule's diff check does not hold fixed and `_dirty` does not check; the batch-2 [RESULT] shows the `git diff` of `analysis/k3.py`, `analysis/modelf.py`, `analysis/modelf_sim.py` and `harness/workload.py` between the two commits and that `git status --porcelain -- harness` was empty when the command ran, and marks any readout computed with changed code."

Optional:
- **F6, line 105:** write "before the table is printed" in place of "before the judged table exists".
- **F7:**
  - Line 100: write "REG-21's tables" in place of "REG-21's batch-1 table".
  - Line 111: add "The batch-2 [RESULT] states whether any computation printed an uncached-token rate on its runs before it (REG-22's batch 2 included), naming the commit."
- **F8, line 109:** list quantities, not functions: "U or any uncached-token rate, the mean served prompt, the reuse of later turns (by any function), the busy share".
- **F9, line 55:** write "a batch-1 or reference run".
- **F10:** write "a sixth valid reference run at a rate of 2.0 or more".
- **F11:** state what an early output means after a breach of line 108. For example: "batch 2 is then labelled retrospective and does not govern".
- **Alternatives (Q3).** Add as alternative 10, with a reported-only readout outside `k3w.py`: the GPU clock under the software power cap.
  - The power limit itself is enforced by the run checks (`harness/checks.py:188–196`), and hardware throttling fails a run (`:16`). But the software power cap is ignored (`:15`), so the SM clock can vary with temperature and day inside a valid run.
  - Prefill is compute-bound, so r would move about one-for-one with the clock ratio (BELIEF). A few percent between the reference's day (2026-11-07) and REG-19's days is the size of the tolerance. It is also the likeliest cause of a non-zero fixed-load contrast.
  - The data to separate it exist: `gpu.jsonl` records `sm_clock_mhz`, `temp_c` and `power_w` per sample (`harness/recorder.py:64–71`). Report their means over W for every run and over the measured window for every reference run.
  - A second alternative missing from the list: selection on the outcome within one load. The preconditions keep the runs that stayed backlogged and busy, and a run whose engine ran slower is likelier to stay so. That biases J1's median low by a fraction of the run-to-run SD. Alternative 8 names selection only for J2.

**Can the analysis change any decision (Q4)?** It makes no decision itself (line 63). It sets the ceiling on K3's λ = 2.0 sentence and K3's status word, which a later claims.md decision uses.
- Batch 1's labels are nearly fixed by published rates (line 52). Its J2 "outside" (P ≈ 0.13) would change K3's claim, but it is confounded with the day.
- The decisive item is batch 2's J1. It exists with P ≈ 0.6 × (0.56 to 0.76) ≈ 0.34 to 0.46 (DERIVED from line 59: P(computed) ≈ 0.6; P(undefined) ≈ 0.44 with four seeds and 0.24 with five).
- J1 "outside low" would propose a judged item for C2's condition 4.
- Without R1, a rule change after the data are public could also change which batch governs.

**4. What I could not check**
- **Real runs:**
  - whether a folder matching the batch-2 or reference pattern is invalid or cannot be loaded today;
  - whether any such folder is already in `runs/` (relevant to R4);
  - whether the `a7bb77a` worktree's `runs/` is the main repo's.
- **docs/ outside the bundle:**
  - REG-22's drafts (its "order with REG-21 both ways", and which windows its uncached rate uses on REG-19's runs);
  - REG-19's resume rules (whether the pin rule changes a validity flag by an entry, which sets how likely F3 is);
  - draft 11 and the proxy's D1–D3 on draft 10 (commits `802bb99`, `5a2c7b1`).
- **Whether any computation has already printed** U, an uncached-token rate, reuse or the busy share on batch-1 or reference runs (line 109's check rests on the agent's report). The code for it exists at HEAD (`c2.py`); whether it was run, I cannot tell.
- **How much the SM clock differs between the runs' days** (BELIEF).
- **Not run:** the full `uv run pytest`, `tests/test_withheld.py`, and `python -m analysis.k3w reg21`.
