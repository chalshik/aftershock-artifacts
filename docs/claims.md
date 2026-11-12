# Claims

The study's claims, each with its test, what would support it, what would refute it, and its status. Created 2026-11-04; restructured 2026-11-12 (decisions.md 2026-11-12 [DECISION], Paper Plan v3). Changing a claim or its status needs the owner (CLAUDE.md C).

**Structure since 2026-11-12.** C1 and C2 are now the **premise P0**: they are cited from three preprints (Lu et al., arXiv 2611.02543; Valse and Jannesari, arXiv 2611.08902; Huang and Liu, arXiv 2611.13412) and replicated here; the paper claims no novelty for them. Their tests below are unchanged and still judge every run registered against them (REG-19 included). The paper's own claims are **K1–K5**, at the end of this file. What the three preprints show is BELIEF until checked against the papers (open-questions A16).

**Paper layer.** The paper plan is `docs/paper/paper-plan-v3.md`, kept on the Mac only and ignored by git; it replaces Paper Plan v2 and its claims C3–C9 (v2's C3 became K2, C5 became K3 and K4, C7 became K5; C4 is reduced to reporting cache reset as a weak trigger; C6, C8 and C9 are dropped). Nothing here may cite the paper plan as evidence, and it is not checked by `tools/check_docs.py`.

## C1. The symptom
**Claim:** at some load λ between μ_off and μ_warm, percent fast stays low after the trigger has ended, while the same load without a trigger stays healthy (plan, Stage 2 Purpose; PROTOCOL §2).

- **Test:** shock runs judged by `load.verdict` (PROTOCOL §3), and all six conditions of a metastable failure at one load; plus the up-then-down ramp at two dwells.
- **Supports:** at one load, `stuck` in most seeds, the control `recovered`, the confirmation run `stuck` over a 4500 s watch, and `recovered` after the drop to λ = 1 (condition 6). Or a ramp gap that stays at both dwells.
- **Refutes, for the conditions tested:** every valid trigger run at a setup's healthy loads `recovered` or `slow_drain`, none `stuck`, and that setup's ramp shows no gap (PROTOCOL §3; this rule was written after results, **[new 2026-11-04]**).
- **Metric:** percent fast is the plan's main number. **Decided 2026-11-12 (owner):** the paper states C1 in hit rate and SLO share (percent fast), not completions/s; the completion rate stays a secondary readout (decisions.md 2026-11-05 and 2026-11-12 [DECISION]).
- **Status (2026-11-04):** not supported. Per cell, all stuck 0 of 3, one-sided 95 % upper bound 0.63 each (`analysis/stats.py`, `cp_upper`):
  - default pool, 20 s gaps: wipe λ = 3, wipe λ = 3.5, burst λ = 3, burst λ = 3.5; ramp at 300 s and 600 s: no gap. Negative by the PROTOCOL rule.
  - 72,480-token pool, 20 s gaps: wipe λ = 3, burst λ = 3. **No ramp was run, so this setup is not negative by the PROTOCOL rule**; it is "no stuck run".
  - default pool, 5 s gaps: wipe and burst at λ = 3.5 and 4.5. **No ramp was run**; "no stuck run".
  - Single-seed controls in every cell. Whether the test loads were inside a real danger zone is in question (`docs/model.md` M2, M4); until the feasibility gate is run, a negative here may say only that these loads recover.

## C2. The cause
**Claim:** a sustaining loop. Cache lost → slow requests → big running batch → KV memory full → cached prefixes evicted before their session's next turn → cache stays lost (plan; PROTOCOL §2).

- **Test:** in stuck runs, the loop figure (helper metrics in the plan's order) and condition 4 (mean KV ≥ 0.80, mean N ≥ 2 × baseline, N below the 256 cap); then the controls that cut a link: prefix caching off, and a session-cap arm (a limit on the sessions in service, set at the load generator). **The session-cap arm replaces the protected-prefixes control (owner, decisions.md 2026-11-12 [DECISION]);** it is not yet defined in a config or registered.
- **Supports:** stuck runs that show the order and the memory limit, and stop getting stuck when a link is cut.
- **Refutes:** stuck runs without a memory limit (a backlog, not this loop), or stuck runs that stay stuck under the session cap.
- **Status (2026-11-04):** untestable so far: there is no stuck run. Related evidence, not a test of C2: during bursts KV reached 1.00, and in the first 60 s after each burst the counter hit rate was 0.11–0.35 (a counter that includes the burst requests, which never hit, so it overstates how cold the sessions' cache was; decisions.md 2026-11-05 [CORR]), and every run then recovered within about 5 minutes (decisions.md 2026-11-02, 2026-11-03). The caching-off control has no defined form yet, and the protected-prefixes control (S4) was not investigated; it is replaced by the session-cap arm (2026-11-12).

## Status of C1 and C2 after 2026-11-04
The two status lines above are dated 2026-11-04 and describe the open-loop setups. Later results are in `docs/status.md` and decisions.md: with closed-loop turns at setup L1 (350 W), single-seed pairs stuck with a recovered control at λ = 2.2 and 2.0 (decisions.md 2026-11-10 [RESULT] REG-14, REG-17), and the registered matrix at λ = 2.0 gave 1 of 4 (decisions.md 2026-11-11 [RESULT] REG-18). C1 is still not supported by its own test; REG-19 is under way.

# Paper claims K1–K5 (since 2026-11-12)

Each is stated for the cells tested only. None has a registered test yet; every test below needs its own `[REG]`, with thresholds fixed before the data (rule A5).

## K1. Turn semantics
**Claim:** whether a turn waits for the previous reply decides the outcome. With open-loop turns (each turn sent at its scheduled time) a slow server makes the next turn arrive while the previous one still runs, so its prefix is held and cannot be evicted. With closed-loop turns (the next turn sent a think time after the reply) every prefix has an idle, evictable interval, and the stuck state can hold.

- **Prior statement (BELIEF, open-questions A16):** Lu et al. name closed-loop sessions as a premise of the feedback (their §9), and Huang and Liu contrast agent sessions with "open-loop chat traffic" (their §2); neither tests an open-loop arm. K1 is the test of that stated premise, not a new idea. Valse and Jannesari's congestion bound assumes that each session "has at most one outstanding request" and that "sessions share no cached tokens" (their assumption A1, App. E.14); K1 relaxes the first clause and K2 the second.
- **Test:** one cell, the same seeds and the same burst, two arms that differ only in `workload.sessions.closed_loop`.
- **Supports:** the closed-loop arm passes C1's per-seed test in most seeds while the open-loop arm is `recovered`, and most open-loop session hits are served while the previous turn runs (`gate.overlap_share`).
- **Refutes:** the open-loop arm stuck at the matched cell.
- **Status (2026-11-12):** not tested at a clean load. Related evidence: with open-loop turns, stuck in 0 of 3 in each of 10 cells (FILE(PROTOCOL.md:105)). One matched pair at L1, λ = 2.4, one seed: the open-loop burst run drained with `overlap_share` 0.608 and the closed-loop one stuck (decisions.md 2026-11-09 [RESULT] REG-10 and REG-11); λ = 2.4 is at the closed-loop warm capacity, so overload explains the closed-loop arm as well (decisions.md 2026-11-10 [RESULT] REG-13).

## K2. Cost gap and reuse structure
**Claim:** the range of loads between the cold capacity and the warm capacity widens as per-session context grows; when all of the cache gain comes from a fixed set of prefixes shared across sessions, whose total size does not grow with load or backlog, the range is empty.

- **Definitions (2026-11-12, decisions.md [CORR]):** *cache gain* is the counter hit rate (`load._level` `"hit"`) of the no-trigger control in its warm state. A workload is *shared-only* when every reusable token lies in one of a fixed set of prefixes shared across sessions (tenants), the set's total size does not change with load or backlog, and no request reuses tokens of its own session's earlier turns. *Matched cache gain* means the two warm hit rates agree within a tolerance registered beforehand. A workload that mixes a shared prompt with growing per-session context does not test the shared-only prediction.
- **Prior result to cite (BELIEF, checked through a fetch agent's verbatim quotes, open-questions A16):** Huang and Liu's sessions carry a 2K system prompt shared by all sessions inside a 6K–37K context, and their stuck state held in 9 of 12 pairs. That workload is mixed, so it is not a counterexample; they report that the collapsed hit ratio of 0.10–0.12 is the shared prompt alone.

- **Test:** setups that differ only in the turns per session (8 at L1, then 16, then 4; decisions.md 2026-11-12 [DECISION], design choices), under closed-loop turns, each with its cold floor and warm capacity measured under closed-loop turns and a paired shock matrix; and one shared-only setup at matched cache gain: M tenant prefixes of 2576 tokens, every turn one tenant's prefix plus 496 fresh tokens, M set so that M × 2576 equals L1's warm working set at the test load (`derived.working_set` on the L1 control). **A single shared prefix is not used:** every request would hold it, so it could never be evicted and the arm could not fail (decisions.md 2026-11-12 [CORR], second review). Prompt length per turn, uncached tokens per turn, output tokens, M and the popularity law are registered with it.
- **Supports:** range width and stuck share rise with context; no stuck run in the shared-only setup at matched cache gain.
- **Refutes:** no trend with context, or a stuck state in the shared-only setup.
- **Status (2026-11-12):** untested. The 512-token setups were shocked with open-loop turns only, so they say nothing here. The system prompt is drawn per session (FILE(harness/workload.py:97)); a shared prompt needs a harness change (owner).

## K3. Model transfer
**Claim:** the published models place this setup's boundary and describe its stuck state within a tolerance fixed before the runs, or they do not. Quantities to predict: the drain threshold (a stuck server drains only below its all-miss capacity), the backlog slope, the mix of turns served while stuck, and the healthy-side condition.

- **Test:** the models' predictions and the tolerances registered before each run; the comparison computed once.
- **Supports / refutes:** per quantity, inside or outside its registered tolerance. Either outcome is reported.
- **Status (2026-11-12):** no registered test; the models' equations are known to the agent only through summaries (BELIEF, open-questions A16). Three readings of runs already seen agree with a drain threshold near the cold floor, none of them blind: the stuck completion rate is 1.03–1.08 times the cold floor (DERIVED: 1.73 / 1.681 and 1.81 / 1.681; `docs/model.md` M2, REG-8 and REG-14 rows); REG-18's seeds 3 and 6 failed the cold side only in spans planned at 1.62 and 1.76 (decisions.md 2026-11-11 [RESULT] REG-18); REG-15's 1800 s drop was short of the ≈ 3960 s a drain at the floor needs (DERIVED: 400 waiting / (1.681 − 1.58) req/s; `docs/model.md` M2, REG-15 row).
  - Expected under the published model for this workload (computed 2026-11-12 from the model's equations, fixed 8 turns, turn cost proportional to prompt length; BELIEF as to the model, the script is `docs/paper/modelf_l1.py` and moves to `analysis/` with tests when step B is registered): at λ = 2.0 (ρ = 1.19 against the open-loop floor) sessions complete at 0.89 of the all-miss capacity, the session backlog grows at 1.56 times the excess load, the served prompts are 1.6 % shorter than the schedule's mean, and requests complete at 1.016 times the all-miss request rate (1.71 req/s); at λ = 2.2, 0.83, 1.53, 2.5 % and 1.025 (1.72 req/s). The measured request rates (1.73–1.77 and 1.73–1.81) lie 1–5 % above these. So the request rate is a weak test, and it already leans above the model; the session completion rate and the session backlog slope are the discriminating readouts, and neither has been computed.
  - Alternatives for the first reading: the floor, measured with open-loop turns on seed 0, is off for closed-loop turns; or the spans were partly re-warming. The mean prompt length of the turns served in those spans separates them.

## K4. Lifetime of the warm state near the edge
**Claim:** close to the warm capacity the healthy state ends at an arrival surge, and the time to such a surge can be computed from the schedule alone.

- **Test:** a surge threshold fixed beforehand, then no-burst runs on new schedules chosen on both sides of it (`gate.surge_hazard` gives the schedule side).
- **Supports:** runs tip where the schedule crosses the threshold and stay warm where it does not.
- **Refutes:** tips without a surge, or surges above the threshold without a tip.
- **Status (2026-11-12):** exploratory. Every no-burst collapse so far followed a 120 s surge of 3.24–3.49 req/s (decisions.md 2026-11-10 [CORR]); that readout was found in the data and has not judged any new run.

## K5. Detection lead time (optional)
**Claim:** recomputed prefill tokens per second and the hit rate change before latency and queue length do; the contribution is the measured lead time.

- **Test:** a registered onset rule per signal, applied to stuck runs. 0 GPU h on existing runs, which makes it retrospective.
- **Status (2026-11-12):** not started; kept only if K1–K3 leave room.
