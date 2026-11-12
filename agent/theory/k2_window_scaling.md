# K2: how the cold floor and the warm capacity scale with the turns per session

Status: **DERIVED** from stated assumptions and checked numerically (`agent/theory/checks.py`, `check_k2`); the second bound is **CONJECTURED** as a description of this engine. Written 2026-11-13, before E1 and E2 exist. It adds one prediction to E0's two; it changes no threshold.

## Tokens per request (DERIVED from the L1 workload: 2048 system + 128 user tokens on turn 0, + 256 per later turn)

| Turns T | Mean prompt with every turn missing | Mean uncached tokens with every later turn hitting | Ratio |
|---|---|---|---|
| 4 | 2560 | 736 | 3.48 |
| 8 | 3072 | 496 | 6.19 |
| 16 | 4096 | 376 | 10.89 |

## Bound 1: both capacities limited by the cost per request (E0's model)

With a cost of a + b × (tokens to prefill) per request at the stationary mix, cold floor ∝ 1 / (a + b L_cold(T)) and warm capacity ∝ 1 / (a + b L_warm(T)). The window ratio is (a + b L_cold) / (a + b L_warm): 1.88, 2.41, 3.18 for T = 4, 8, 16 with (a, b) = (0.18 s, 0.135 ms), REG-8's two capacities rewritten (`analysis/k2.py`). R = ratio₁₆ / ratio₈ = 1.319; with a = 0 it is the token-gap ratio, 1.76.

- Assumption that can fail: the warm capacity is where the cost per request saturates the engine. For open-loop turns the measured warm capacity is 3.0 and the best completion rate 4.047; for closed-loop turns the warm edge is 2.4 (REG-13), 59 % of 4.047. Something other than cost ends the warm state there.

## Bound 2: the warm side limited by memory (CONJECTURED)

Suppose the warm state ends where the latest contexts of the sessions in service no longer fit beside each other: λ × (think time + warm response time) × L_cold(T) ≈ C. (Sessions in service = λ/T × T × cycle; each needs its latest prompt resident.) Then the warm capacity scales as 1 / L_cold(T): it **falls** with the turn count, by 3072 / 4096 = 0.75 from 8 to 16 turns. The cold floor falls too, as 1 / (a + b L_cold). Their ratio is C (a / L_cold + b) / cycle, so

  R = (a / L₁₆ + b) / (a / L₈ + b) = 0.924 with the fixed-cost values, and exactly 1 with a = 0.

Under this bound the window does **not** widen with the turns per session; it narrows a little.

- For it: the closed-loop warm capacity is far below the cost limit; every no-burst departure from the warm state on record followed an arrival surge (decisions.md 2026-11-10 [CORR]), which is what a memory limit predicts and a cost limit does not; open-question A15 records a larger live working set with closed-loop turns (KV mean 0.659 against 0.336 at λ = 3).
- Against it, and why it is only conjectured: the study's memory-fit model (M1) is 0 for 3 on tested predictions (`docs/model.md`); the simple count λ × cycle × L_cold reaches the pool only near 4.8 req/s at 8 turns (DERIVED: 96,656 / (6.5 s × 3072)), twice the measured edge, so the limit, if it is one, binds through surges and through what running requests hold, not through the mean.

## What E0 and E2 will separate (predictions, registered with E0 before the sweeps)

| Model | warm₁₆ / warm₈ | floor₁₆ / floor₈ | R (true) | E0's label as the gate reads it |
|---|---|---|---|---|
| Cost-limited, fixed cost | 1.07 | 0.82 | 1.30 | "floor_only" (the grid reads the warm side as unchanged) |
| Cost-limited, proportional | 1.32 | 0.77 | 1.71 | "widens" |
| Memory-limited warm side | 0.75 | 0.82 | 0.92 | "does_not_widen" (warm₁₆ ≈ 1.8, below the grid's lowest rate 2.0, so the `R_upper` branch decides) |

The two factors of R are reported separately by `k2.decide`, so the sweeps identify the regime whatever the label: a warm factor near 0.75 is the memory limit; near 1.07 to 1.32 the cost limit.

- Falsifying observations: a 16-turn warm capacity above 2.4 refutes bound 2; a 16-turn warm capacity at or below 2.0 refutes bound 1.
- Consequence if bound 2 holds: K2's first half is refuted for this engine and pool, and the lever that widens the window is the pool size per session, not the turn count. Valse and Jannesari report the same direction from the other side: a larger all-miss capacity with an unchanged pool narrowed their window to (1, 1.3) (their §2, the H200 at a 300k pool), and doubling the pool reopened it.

## Relation to the published models

Model F gives the trapped state at a given ρ, not where the two capacities lie (`docs/model.md` M5: 16-turn sessions have nearly the same trapped state as 8-turn ones at equal ρ). Lu et al.'s fluid model has a departure curve whose peak N* is set by the cache cliff, "near N_c ≈ 1.9 C / c̄" (their §5): a memory limit on the warm side, of the kind bound 2 assumes, with c̄ the mean context. Huang and Liu state the healthy side the same way: "The healthy regime exists as long as the cache-warm population fits, λT(Z + R₀)L̄ ≲ C, and the cache-warm engine keeps up" (their §4). Both published healthy-side conditions are bound 2's form; E0's cost model is not in either paper.
