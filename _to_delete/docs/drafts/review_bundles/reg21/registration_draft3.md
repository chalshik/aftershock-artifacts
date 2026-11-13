## 2026-11-13 · [REG] REG-21 (K3, step B): is the stuck server the all-miss server? Its uncached-token work rate against the saturated cache-off sweep's, at each load; batch 1 on the 13 closed-loop burst runs made before REG-19, batch 2 on REG-19's burst runs after its [RESULT] (0 GPU h)

- **ID:** REG-21. An analysis of existing runs, 0 GPU h. Draft 3; it replaces drafts 1 and 2 (`docs/drafts/scratchpad-2026-11-12/reg21_draft.md`, `reg21_draft2.md`), which were never registered.
- **How this draft came about.** Draft 1 judged model F's long-run mix values on 900 s windows; its review showed that such a window is not in the long run and that the burst and the turn gaps move it. Draft 2 replayed model F on each run's own schedule and judged the capacities μ_k and μ_X at which the replay reproduces the run's served-turn mix and its throughput. Its round-2 review (text lost; scripts in `docs/drafts/scratchpad-2026-11-12/review2/`; summary in `docs/status.md`) found that the time a request stays in the running batch delays its session's next turn and so moves the mix, which confounds both fitted capacities, and that the E1 item could change no decision. The owner then made E1 "Floor only" (decisions.md 2026-11-13 [CORR], owner's choices). The owner's choices for this registration were "Register now, mix primary", then "Rebuild around per-run sim" (same [CORR]). **This draft departs from "mix primary":** two review rounds showed that the mix is set by queue kinematics and by the residence in the batch, not by what K3 asks. The mix and the replay are kept as reported readouts. The departure is the delegate's and is listed for the owner.
- **Question:** in the cold, backlogged state after a burst, does the server prefill uncached prompt tokens at the rate of the saturated cache-off server (J1), and is that rate the same at λ = 2.0, 2.2 and 2.4 (J2)?
- **Claim tested:** K3 (`docs/claims.md`), the quantity "a stuck server drains only below its all-miss capacity". Model F (Valse and Jannesari, arXiv 2611.08902 §3; BELIEF as to the model, open-questions A16) gives the trapped server one capacity, the all-miss capacity, at every load. Stated in tokens it needs no model of the queue: a server on which every turn misses does cache-off work.

### Statistic (`analysis/k3w.py`)
- **U** (`work_rate`): uncached prompt tokens per second, Σ (prompt_tokens − cached_tokens) over ok requests, session and burst, whose first token falls in the window (the first token ends a request's prefill).
- **U_off** (`reference`): the mean of U over REG-8's saturated cache-off runs, the five runs of `sweep_l1pl350_pc_off` at rates ≥ λ_sat = 2.0 that give the floor 1.681 req/s (decisions.md 2026-11-07 [RESULT] REG-8), each over its measured window (warm-up to the end of arrivals).
- **r** = U over W ÷ U_off, per run. W = [burst end + 600 s, burst end + watch): [1680, 2580) s; [1680, 5580) s for REG-15; [1680, 4080) s for REG-19's runs.
- **Why r:** it contains no turn mix, no residence, no queue discipline and no think time. On synthetic servers (`tests/test_k3w.py`, no run read): an all-miss first-come-first-served server reads r = 1.00 ± 0.02 at λ = 2.0 and 2.4; so does a running batch of 16 or 64 slots (which moves the mean served turn index by more than 0.03, draft 2's confound), and a six-fold think time; a fixed cost per turn (0.18 s + 0.135 ms per token) moves r by under 0.02; a trap at 1.85 or 1.55 req/s reads r = 1.10 or 0.92; a server with partial hits fails the precondition below.

### Runs
- **Batch 1** (`k3w.REG21["batch1"]`): the 13 valid closed-loop L1 burst runs at 350 W made before REG-19: REG-11 (λ = 2.4, seed 1), REG-12 (2.4, seeds 2–6), REG-14 (2.2, seed 2), REG-15 (2.2, seed 12), REG-17 (2.0, seed 2), REG-18 (2.0, seeds 3–6).
- **Batch 2:** REG-19's burst runs (`*_burst_l1pl350cl_r2.0_w3000_s1[5-9]`), computed once, only after REG-19's [RESULT] is in this file (until then `analysis/withheld.py` refuses them). One load, so J1 only.
- **A run enters** when `k1.cold_backlogged` holds in its own end window. **It is judged** only if it is all-miss in W: the prefix reuse of later turns in W (`k1.reuse`) ≤ 0.05. Runs left out are listed with the reason.

### Judged (`k3w.judge`; thresholds fixed here, before U or r is computed on any run)
| # | Statement | inside if | undefined if |
|---|---|---|---|
| J1, level | the stuck server works at the cache-off token rate | \|median of r over the judged runs − 1\| ≤ 0.05 | fewer than 3 judged runs |
| J2, load | one work rate at every load | max − min of the load groups' medians of r ≤ 0.05; groups λ = 2.0, 2.2, 2.4, each used only with at least 2 judged runs | fewer than 2 such groups |

A value exactly at 0.05 is inside. "Undefined" is never rounded to inside or outside. Batch 1 and batch 2 are judged apart and never pooled.

**Where 0.05 comes from (DERIVED and BELIEF, before any r):** the five reference runs' completion rates are within about ±1 % of their mean (1.656 and 1.688 req/s at λ = 2.0 and 2.5; RUN(20261107-083730_sweep_l1pl350_pc_off_r2, load.summarize), RUN(20261107-085650_sweep_l1pl350_pc_off_r2.5, load.summarize)), so run-to-run noise of a median is about 0.01–0.02; a fixed cost per turn moves r by under 0.02 (synthetic); 0.01 is left for drift between days (BELIEF). The same components bound a difference of two medians.

### Not blind, said plainly
Every batch-1 run has been reported. Seen: span completion rates of 1.70–1.84 req/s (decisions.md, the [RESULT] entries of REG-11 to REG-18) and first-turn shares of completions of 0.125–0.18. From these r can be guessed: r ≈ (completion rate ÷ 1.681) × (mean served prompt ÷ 3072). U, the mean served prompt and r itself have not been computed by anyone. The tolerance was chosen knowing those completion rates. So batch 1 is a consistency check. Batch 2 is on runs nobody has read.

### Prediction (BELIEF)
12–13 runs enter; each is all-miss in W with probability ≈ 0.9. Median r ≈ 1.02 (DERIVED from a completion rate of 1.75 req/s and model F's mean served prompt of 0.984 × 3072 at λ = 2.0: 1.75 / 1.681 × 0.984); per run 0.99–1.07. P(J1 inside) ≈ 0.7, outside high ≈ 0.25, outside low ≈ 0.05. Group medians within 0.03 of each other; P(J2 inside) ≈ 0.65 (the λ = 2.4 runs reported the highest rates, up to 1.84). Batch 2: P(J1 inside) ≈ 0.7.

### Decision under each outcome (rule A1)
- **J1 inside and J2 inside:** K3's status says that the stuck server works at the cache-off token rate at the three loads (retrospective for batch 1). The paper replaces "completes near the cache-off floor" by the token statement and gives the request rate's excess over 1.681 as a matter of the served mix. The confirmation run's drop (conditions 5–6) is sized from U_off and the reported mean served prompt.
- **J1 outside, high:** the closed-loop cold state does more token work than the open-loop cache-off sweep, so 1.681 understates the closed-loop all-miss capacity. K3 reports the miss; the paper states every closed-loop margin against E1's closed-loop floor only (E1 runs in any case); the confirmation run's drop is sized from the measured cold completion rate, not from 1.681.
- **J1 outside, low:** the trap does less work than a miss explains (BELIEF: prefill recomputed after preemptions). K3 reports it; the comparison of preemptions with matched controls becomes a judged item of C2's condition-4 registration, not a readout.
- **J2 outside:** no single work rate fits the loads, so model F's one-capacity premise does not hold here; the paper reports the work rate per load and uses model F for no prediction at another load.
- **Undefined:** reported; nothing follows.

### Reported, never judged (`k3w.readouts`)
U by end time; request rates (all requests, session turns); the mean served prompt; the mean turn index and the first-turn share; sessions completed over sessions started in W; the median time from first token to end (the residence in the running batch); mean running batch, waiting line and KV in W; preemptions per second in W; Huang and Liu's rule (arXiv 2611.13412 §3); the burst's size (`gate.shock_size`); model F's long-run values (`analysis/modelf.py`); and model F's replay of the run's own schedule at 1.681, without and with that residence (`modelf_sim.simulate(decode_s=…)`), for the mean turn index, the session-turn rate and sessions completed over started. Each reference run's U, with their SD and spread.

### Alternatives to state with any result
1. **Dev mode.** The burst runs ran with dev mode, the reference sweeps without (PROTOCOL §4; open-questions A6 is open). An r off 1 could be dev mode. Not separable here; E1 (cache off, closed loop, no dev mode) and the caching-off control of step D (dev mode) each give a cache-off U in another condition, to be reported when they exist.
2. **A different saturated state.** The reference is an open-loop sweep whose line grows without bound; its batch and preemptions may differ from the trap's. The running batch, KV and preemptions per second are reported for both.
3. **Hits below the precondition.** Cached tokens are subtracted in U, so hits enter r only through what they save in time; the reuse in W is reported per run.
4. **The burst's tail.** Burst requests whose first token falls in W count in U (they are work); their number is reported.
5. **Window edges.** U by first token and by end time are both reported.
6. **Heat and clock.** The runs are days apart from the reference; `gpu_steady` passed on each (SM-clock CV ≤ 5 %), which bounds within-run drift only.

### Stopping rule
Each batch is computed once: `uv run python -m analysis.k3w reg21` (batch 1) after this registration is approved, and `uv run python -m analysis.k3w reg21 2` after REG-19's [RESULT]. No second window, statistic or threshold. If the command raises, the cause is fixed and logged as a [CORR] before the table is read; an exception prints no r.

### Cost
0 GPU h; a few minutes of CPU (it loads every closed-loop L1 run except the withheld ones, and REG-8's cache-off sweep).

### Code and tests
`analysis/k3w.py` (`work_rate`, `reference`, `readouts`, `row`, `judge`, `select`, `reg21_table`); `analysis/modelf_sim.py` (`simulate` gains `decode_s`, default 0 = model F's trajectory unchanged); `tests/test_k3w.py`, 18 tests on synthetic servers and hand-made rows (listed under "Why r", plus the judge's labels, groups, what it leaves out, the boundary, the table on fake runs, and the readouts on a run without metrics). `analysis/k3.py` keeps draft 2's code; its fitted capacities and its `judge` are not registered and are not run. No run folder was read while writing this draft or its code.
