# DECISION TREE

Written 2026-11-13, before any GPU run of this session and before any REG-19 outcome is read. For each outcome: the next action, and the sentence the paper gets. `k`, `n`, `u` (the one-sided 95 % Clopper–Pearson upper bound) and measured values are filled from the [RESULT] entry, never from memory. Where a registration already fixes a branch, it is quoted; where it left the choice to the owner, the delegate's choice is fixed **here, now**, so that it is not made after the data.

Standing rule: a refuted claim is a result. The thesis is a boundary map; a negative cell is a point on it.

## P0 (C1's matrix condition at λ = 2.0): REG-19

Registered outcomes (`gate.reg19_outcome`): `supports`, `supports_edge`, `some`, `none`, `controls_not_healthy`, `surge_reading_wrong`, `too_few`; or a futility stop.

| Outcome | Next action | Paper text |
|---|---|---|
| `supports` (k_clear ≥ 3 of 5) | Register the confirmation run at λ = 2.0 (conditions 5–6; task Z9) and run it after REG-20's gate. The cell for D1/D2 is L1, λ = 2.0. | The registered wording: "At λ = 2.0, after the burst the server stayed stuck, cold and below its load through a 3000 s watch without the line emptying, while the same schedule without the burst stayed healthy, in k of n new seeds (15–19), under REG-19's whole-window test, written after REG-18's matrix (1 of 4 under the per-span test). Under REG-18's per-span test on the same runs: k_18 of n." Bound: "(one-sided 95 % upper bound on the pass probability u; lower bound from the registration's table)". If k_18 < 3: "The result rests on the whole-window test." |
| `supports_edge` (k ≥ 3, k_clear < 3) | **Delegate's choice, fixed now:** as `supports`, and the confirmation run's registration must show the control's waiting share per span; the cell is described as "at the warm edge". | The same sentence, followed by: "In (k − k_clear) of these seeds the no-burst control itself queued in more than half of a span's scrapes, so the load is at the edge of what the warm state carries." |
| `some` or `none` (or a futility stop) with `drains` in ≥ 2 of the seeds run | The registration's branch: report the zone as too narrow. No λ = 2.1 matrix. D1/D2 run only if REG-20b or E3 provides a cell. | "At λ = 2.0 (1.19 times the cold floor) the burst left the server cold for [range] s, after which the line drained in d of n seeds: at this margin the cold states are long drains, not a stuck state. The window between the cold floor and the warm capacity is too narrow at this scale to hold the state." (Fallback framing: a point on the K2 map.) |
| `some` or `none` (or a stop), failures mostly `emptied_*`, `stuck_not_cold`, `bad_baseline`, `inconclusive`, `unclear` | **Delegate's choice, fixed now: the report, not a λ = 2.1 matrix.** Reasons fixed now: 2.1 is nearer the warm edge, where REG-16 and REG-12 showed controls tipping by themselves, so a matrix there risks `controls_not_healthy` at ≈ 11 GPU h; the same hours buy E1, E2 and REG-20b, which bear on K1 and K2. The confirmation run is **not** registered for λ = 2.0. | "At λ = 2.0 the registered matrix passed in k of n seeds (REG-19; with REG-18's 1 of 4 under the earlier test). Every burst run that did not pass [was still cold and backlogged at the end / emptied and re-tipped / …, as counted]. We therefore report this cell as one where the stuck state is entered but not held reliably, and make no claim of a metastable failure by our six conditions." |
| `controls_not_healthy` | No further P0 run at λ = 2.0. Report; K4 gains these controls as data (exploratory). | "At λ = 2.0, c of n no-burst controls left the warm state within 4080 s, so the load is not reliably warm on these schedules and the matrix says nothing about the burst." |
| `surge_reading_wrong` | Stop P0 and K4's surge reading. Write a [CORR] on the surge readout before anything else is drafted (the registration's branch). | "A control went cold with no 120 s surge above 3.2 req/s in its schedule; the surge reading of the earlier collapses does not hold." |
| The queue stops for an operational reason | No table. Runs reported from `checks.json`. Resume through the watcher; a partial matrix is recorded and never pooled. | none |

**Correction (2026-11-13): D1 and D2 do not need `supports`.** What a loop-cut control needs is a cell where the burst run ends with the verdict `stuck` while its control recovers, in most seeds. REG-18 already showed that at λ = 2.0: all four burst runs ended cold, full and backlogged and all four controls recovered (decisions.md 2026-11-11 [RESULT]); the matrix label was `some` because of the per-span cold side. So after `some` or `none` with the backlog persisting (not `drains`), D1 and D2 can still be registered at λ = 2.0, with their comparison stated on the verdict and on the line never emptying, not on the matrix label. Only `drains` in most seeds, or controls that do not recover, takes the cell away. The rows above that tie D1/D2 to `supports` are superseded by this note.


**Fallback framing if P0 fails** (any row but the first two): the paper's title claim is the boundary map, with this cell as "entered, not held" at margin 1.19; P0 stays a cited premise, replicated only in single seeds (REG-14, REG-17) and in the cold, backlogged end state of every burst run.

## K1 (turn semantics): REG-20

Gate (`k1.reg20_a_may_start`, once, after REG-19's [RESULT]): arm A starts only if REG-19 ran all five seeds and all five closed burst runs are cold-backlogged.

| Outcome | Next action | Paper text |
|---|---|---|
| Gate passes | Arm A (five open-loop burst runs, drift rerun after the third); controls only for an open run that ends cold; then `k1.reg20_table`. | below |
| Gate fails, ≥ 3 closed runs cold-backlogged | **Delegate's choice, fixed now: add paired seeds (REG-20b), not drop K1.** New registration, reviewed and approved before any run: seeds 20, 21, … (the first unused), enough that 5 cold closed runs are expected at the observed cold share; for each new seed the closed burst run, then for every seed with a cold closed run the open burst run; the same readout and the same exact McNemar test at 0.05, computed once at a fixed n. REG-19's seeds that its futility stop left unrun may be run as K1 closed-arm runs under REG-20b; they never enter REG-19's k of n. | none yet |
| Gate fails, < 3 closed runs cold-backlogged | K1 is not testable at this cell. Report. K1 leaves the core claims unless E3 gives a 16-turn cell. | "With closed-loop turns the burst left the server cold and backlogged at the end of the watch in only c of n seeds, so this cell cannot carry a paired test of turn semantics." |
| `supports` | Arm B (λ = 2.5, seeds 15–17). | "On the same seeds and the same burst, the server ended cold and backlogged in all n runs with closed-loop turns and in none with open-loop turns (exact one-sided McNemar p = …). In every open-loop run most cache hits of later turns were served while the session's previous turn was still running (overlap share …), and those turns reused more of their prefix than the others." |
| `supports_no_mechanism` | Arm B. | The first sentence only, then: "The held-prefix mechanism was not shown in every run (overlap share … in m of n), so we state the outcome without it." |
| `inconclusive` | **Delegate's choice, fixed now:** REG-20b if at most one open run was cold or partial; otherwise report. | "The paired test did not reach 0.05 (p = …): c_o of n open-loop runs ended cold [and p_o partial]." |
| `refutes` (≥ 3 open runs cold, lost or with a cold control) | K1 is reported as refuted at this cell and leaves the core claims. No arm B. | "With open-loop turns the server also ended cold and backlogged in c_o of n runs: at this cell the stuck state does not need turns that wait for the reply." |
| `open_arm_overload` | The open-loop cell is not warm-healthy; K1 not testable there. Report. | "An open-loop run and its no-burst control both ended cold: λ = 2.0 is not healthy with open-loop turns on that seed." |
| Arm B `headroom_weakened` | K1 stated with the headroom check. | "At λ = 2.5, the same share of the open-loop warm capacity as 2.0 is of the closed-loop one, all three open-loop runs recovered." |
| Arm B `headroom_open` | K1's sentence carries the confound. | "At λ = 2.5 c of 3 open-loop runs ended cold, so the difference at λ = 2.0 may be headroom, not turn semantics." |

## K2 (the window and turns per session): E1, E0/E2, E3

| Outcome | Next action | Paper text |
|---|---|---|
| E1 floor "ok" or "tail_ok" | E2. The closed-loop floor replaces 1.681 for closed-loop margins. | "With closed-loop turns the saturated cache-off server completes f₈ req/s (open-loop: 1.681)." |
| E1 no floor | E2 does not run. **Delegate's choice, fixed now:** one new registration with a grid shifted by what the status says (lower rates if "unsaturated" never fired, higher if too few rows), else K2 is reported as unmeasured. | "The closed-loop cache-off sweep did not define a floor (status …)." |
| E0 "widens" | Register E3 (16-turn paired shock matrix, 8–12 GPU h) with its own review. | "From 8 to 16 turns per session the window ratio grew by R = … (gate 1.083), with the warm capacity rising from 2.4 to …" |
| E0 "floor_only" | No matrix. K2's first half reported as: the window widens only through the cold floor. | "The window ratio grew by R = …, entirely because the cold floor fell (floor ratio …); the warm capacity did not rise (… against 2.4)." |
| E0 "does_not_widen" | No matrix. K2's first half is refuted for L1. | "The window did not widen with the turns per session (R = …)." |
| E0 "unresolved" | **Delegate's choice, fixed now:** no matrix; report R with both factors. | "R = … lies between 1 and the gate's 1.083: the sweeps cannot tell a widening from grid rounding." |
| E0 "missing" | No matrix; report which input is missing. | "K2's ratio could not be formed (… undefined)." |

## K3 (model transfer): REG-21 and the registered predictions

| Outcome | Next action | Paper text |
|---|---|---|
| J1 inside, J2 inside | The confirmation run's drop is sized from U_off and the mean served prompt. | "In the stuck state the server prefilled uncached tokens at r = … of the saturated cache-off rate (n runs, three loads; retrospective), so the stuck server is the all-miss server; its request rate exceeds the cache-off floor because it serves shorter prompts (mean … against 3072 tokens)." |
| J1 outside, high | Margins against E1's floor only; the drop is sized from the measured cold completion rate. | "The stuck server did r = … times the token work of the open-loop cache-off sweep: the open-loop floor understates the closed-loop all-miss capacity." |
| J1 outside, low | The preemption comparison becomes a judged item of C2's condition-4 registration. | "The stuck server did only r = … of the cache-off token work: it loses more than a miss costs." |
| J2 outside | Work rate reported per load; model F used for no prediction at another load. | "The stuck work rate differed by load (… at 2.0, … at 2.4), against model F's single capacity." |
| undefined | Report. | "Too few all-miss runs (n = …) to judge." |
| Each registered blind prediction (E0's R, the confirmation run's drain time, REG-20's arm labels, batch 2 of REG-21) | Compared once; listed in the model-against-measurement figure. | "Predicted …, measured …: inside / outside the registered tolerance." |

## K4 and K5

Neither has a registration yet. Fixed now: K4 stays exploratory in the paper unless new no-burst runs on both sides of a threshold registered beforehand are made (GPU item 7, only if hours remain); its text then is "tips where the schedule crosses …" or "tipped without a surge / stayed warm above it in …". K5 is retrospective: "the hit rate fell … s and uncached prefill rose … s before TTFT p50 doubled (median over n runs; onset rules registered before the computation)", or "no lead (… s)". A critical-slowing-down signal is reported only with its false-alarm rate on the controls.

## GPU order (start prompt §7), with the stops above

1. REG-19 seeds 18–19 → [RESULT]. 2. REG-20's gate → arm A or REG-20b's registration. 3. REG-21 batch 2 (0 GPU h). 4. E1 → E2 (→ E3 only on "widens"). 5. D1, D2 at the cell P0 leaves (λ = 2.0 after `supports`/`supports_edge`; otherwise only if E3 or REG-20b gives a cell that holds). 6. The confirmation run (only after `supports`/`supports_edge`). 7. K4 if hours remain.
