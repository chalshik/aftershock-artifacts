**Decision: APPROVE** (conditional). The approval covers draft 4 as bundled and lapses if anything judged changes (see condition 1).

**Reasons**

1. **Scope: inside the delegation.** The delegation covers "analysis-only registrations" and "changes to paper claims or their status in docs/claims.md and docs/paper/" (FILE(delegation.md:3)).
   - It costs 0 GPU h, and the judged readout is one the owner's step B already lists: "uncached prefill tokens per second against the cache-off rate" (FILE(docs/experiment-plan.md:409)).
   - Batch 2 is not readable early: `batch2_runs` raises until a heading holds "[RESULT] REG-19" and ignores `AFTERSHOCK_UNSEAL` (FILE(analysis/k3w.py:286), FILE(analysis/withheld.py:38)).
   - Nothing in `runs/`, a used config or an old entry is touched.

2. **Rule A5, "Never choose or widen a threshold after seeing the data it judges": met for batch 2, and met for batch 1 only by the standard the owner set for step B.**
   - The thresholds sit in code committed in 3f5c84a, before any U or r exists. I could not verify that no run was read; the draft and a commit message say so, and neither is evidence (rule B).
   - Busy ≥ 0.99 and groups of three come from the blind round-1 review (FILE(round1_rule_f.md:19), FILE(round1_rule_f.md:44)). Reuse ≤ 0.05 dates from draft 2 (FILE(analysis/k3.py:57)); the draft does not say where it comes from.
   - **Batch 1's J1: I require that it keep its label, as a retrospective consistency reading, and not be reported without one.** The plan asks for exactly this: "Readouts, each with a tolerance fixed before it is computed" and "a consistency check, never a blind test" (FILE(docs/experiment-plan.md:405), FILE(docs/experiment-plan.md:413)).
   - The 0.05 is not chosen to pass: the draft's own estimate leaves about 0.2 for "outside high", where Valse and Jannesari's 0.15 would make "inside" certain. "Outside high" is the only informative outcome there.
   - The draft calls batch 1's J2 "live" without saying that its 0.05 was also fixed with the per-load completion rates known.

3. **Departure from the owner's choice: within the delegation and justified, but understated.** Rule A4: "Disagree with the owner when the evidence supports it … name which."
   - The argument is named: the two reviews showed the mix is moved by residence in the batch.
   - The draft says it departs from "mix primary". It also departs from "Rebuild around per-run sim" (FILE(docs/decisions.md:4267)) and from the plan's "each with a tolerance".
   - One of the plan's six readouts is judged. The two the owner marked as discriminating, the session completion rate and the session backlog slope, are reported without a tolerance.

4. **Template and rules: complete except for five gaps, all fixable in wording.**
   - Process §2 requires "Adversarial review (section 3): verbatim output". The draft only cites the draft-3 review by path, and holds no review of draft 4.
   - "every decisions.md heading … with exactly one tag": the draft heading contains both `[REG]` and `[RESULT]`, so `check_docs` will fail (FILE(tools/check_docs.py:124)).
   - Rule B: 1.67–1.84, 0.125–0.18, 3072 and the synthetic figures carry no tag. "A decisions.md entry is a record of a claim, not its evidence."
   - Rule H: "say so whenever cells are pooled". Seeds 2–6 run at both λ = 2.0 and 2.4, and seed 2 also at 2.2; the draft does not say so.
   - Rule J: `docs/definitions.md` has no entry for U, U_off, r or busy share.
   - Present and adequate: a numeric prediction, a decision per outcome, six alternatives with their readouts, the pooling assumption, a stopping rule, and named functions.

5. **Decision table: acceptable as a ceiling on wording, not as authority to edit claims.**
   - "Batch 2 governs what the paper says about λ = 2.0" is acceptable: it is a precedence rule fixed in advance in favour of the unread data.
   - It needs two caveats: the batches differ in window (900 s against 2400 s), and batch 2 has at most five runs.
   - "The paper uses model F for no prediction at another load" hangs on a contrast confounded with the day, which a single run can flip (FILE(round1_rule_f.md:40)). It only restricts claims, so I accept it as a ceiling.

**Conditions**

1. The rule F review of draft 4 must not return NOT READY. Both reviews go verbatim into the `[REG]`. Any change to the statistic, thresholds, preconditions, windows, run lists, reference, pooling rule, stopping rule or the judged path of `k3w.py` returns to a proxy. The wording changes below do not.
2. Remove the bracketed "[RESULT]" from the `[REG]` heading. No heading written before REG-19 reports may contain the string "[RESULT] REG-19"; any such heading lifts REG-19's seal.
3. The `[REG]` and the delegate `[DECISION]` are committed before REG-19's registered computation is run or read by anyone, and the entry says so. If that is not true, batch 2 is labelled retrospective and does not govern. Batch 2 is computed once, after REG-19's final `[RESULT]`, not an interim one.
4. In the `[RESULT]`, K3's status and any paper sentence, batch 1's J1 is called a "retrospective consistency reading" and carries the draft's admission. The words "supports", "confirms", "passes" and "test" are not used for batch 1. If batch 2 is undefined, batch 1 does not become the paper's statement.
5. The "what is live" section adds three things:
   - J2's 0.05 was fixed with the per-load rates known, with the bound on the spread that the reported rates imply (DERIVED from reported numbers only);
   - the origin of reuse ≤ 0.05 and busy ≥ 0.99, and what has been seen of end-window reuse and quiet spans;
   - if REG-18's seeds 3 and 6 are left out, the λ = 2.0 group has exactly three runs.
6. The departure paragraph states plainly:
   - that it departs from both owner choices and from "each with a tolerance";
   - which of the six readouts is judged and which are only reported;
   - that the reported ones can never be judged later on these runs, REG-19's included;
   - that REG-11 is included although step B's list does not name it.
7. Wording of results:
   - "cold and backlogged (`k1.cold_backlogged`)", not "stuck". C1 is "still not supported by its own test" (FILE(docs/claims.md:31)).
   - State that λ = 2.4 sits at the closed-loop warm capacity (FILE(docs/claims.md:45)).
   - An "inside" sentence gives the median r, n, the range, and both factors of the request rate (r and the mean served prompt). It does not attribute the whole excess over 1.681 to the mix.
   - J2 outside reads "not shown (load or day)", never "refuted".
8. This approval covers computing and reporting only. Each edit to `docs/claims.md` or `docs/paper/`, the E0 label, "E1 runs in any case", the confirmation run's sizing and the C2 condition-4 item needs its own decision or registration, with its own rule F review and proxy approval.
9. Add to the entry:
   - model F's number (M5: r = 1.00, spread 0, a fixed cost within 0.02) beside the author's 1.02;
   - evidence tags on every number;
   - the run ids by FILE(analysis/k3.py:41) and FILE(analysis/k3w.py:54), and the code's commit hash;
   - the shared-seed sentence, and that U is a window mean reported without its minimum span;
   - a per-load k of n with its Clopper–Pearson bound for any count readout;
   - the four definitions in `docs/definitions.md`.
10. The command runs from committed code with `analysis/` and `tests/` clean. They are not clean now: `analysis/e1.py`, `tests/test_e1.py` and `tests/test_withheld.py` are modified. `uv run pytest` passes before the commit. The `[RESULT]` names the commit and lists the left-out runs with their reason and r.

**Notes for the owner**

- Look first at the departure. If you want the mix or the session rates judged on REG-19's runs, say so before REG-19's `[RESULT]`; after batch 2 they are spent.
- Expect little from batch 1: its J1 is nearly fixed in advance, and its J2 is confounded with the day. Batch 2's J1 is the only reading on unread runs.
- `withheld.lifted` accepts any heading that contains the text, whatever its tag. That is a weakness of the seal itself, beyond REG-21.
- `reference()` holds literal 2.0 and 2.5 (FILE(analysis/k3w.py:111), FILE(analysis/k3w.py:128)), and the reference runs are not held to the busy precondition. The second is disclosed in the draft.
- Not verified: that no run was read, the round-2 rule F result, and the tests. I ran nothing and opened nothing under `runs/`.
