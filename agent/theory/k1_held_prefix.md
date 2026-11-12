# K1: when a session's prefix is idle and evictable, with open-loop and with closed-loop turns

Status: **DERIVED** from stated assumptions and checked numerically (`agent/theory/checks.py`, `check_k1`, `check_turnover`); **not evidence about the engine**. Every engine number quoted is from the repo with its source. Written 2026-11-13, before REG-20's runs exist.

## Setting and assumptions

- (A1) The engine admits waiting requests in arrival order and the head of the line blocks it (SUPPORTED: vLLM 0.32.0 `Scheduler.schedule`, open-questions A17).
- (A2) A request holds the KV blocks of its prompt from admission to its end; held blocks cannot be evicted; a later request whose prompt starts with those blocks reuses them, whether they are held or idle (SUPPORTED: open-questions S9, S11).
- (A3) Idle cached blocks are evicted in the order of their release, as new blocks are allocated (SUPPORTED: S9).
- (A4) A session's turn k + 1 has the whole prompt of turn k as its prefix; the gap between turns is exponential with mean g = 5 s.
- (A5) While it is in the running batch a request stays S seconds (its residence); S is treated as a constant of the state. In the stuck state on record about 30 requests run and 1.75 complete per second, so S ≈ 30 / 1.75 ≈ 17 s (DERIVED from RUN(20261110-182920_burst_l1pl350cl_r2.0_s2, gate.reg17_gate): 30.0 running, c 1.733–1.773).

## 1. Closed-loop turns: every prefix has an idle interval

Turn k + 1 is released at the end of turn k plus the gap. From the end of turn k until turn k + 1 is admitted, the prefix is held by nobody. Its idle time is I = gap + the wait of turn k + 1 in the line. It survives only if it is not evicted in that time. By (A3) an idle prefix released now is evicted after the blocks ahead of it in the free queue have been taken, that is after about

  R_M = C (1 − κ) / A,

where C is the pool in tokens, κ the share of the pool held by running requests (the KV-usage gauge) and A the rate at which new blocks are allocated (uncached prefill tokens plus output tokens, per second). This is the turnover time of Valse and Jannesari ("R_M = M / churn", their §4), with the held share taken out.

- Warm, λ = 2.0: κ = 0.171 (RUN(20261110-174432_stage2_control_l1pl350cl_r2.0_s2, gate.reg17_gate)), A ≈ 2.0 × (496 + 128) tokens/s, so R_M ≈ 64 s, far above I ≈ 5 s: every later turn hits. (`check_turnover`)
- Cold: κ = 0.949 (the burst run, same function), A ≈ 1.75 × (3072 + 128), so R_M ≈ 0.9 s, far below I (5 s plus a wait of the order of a minute): every later turn misses. The cold state is self-consistent.

So with closed-loop turns both states are self-consistent at one load, and the boundary between them is I = R_M. Whatever makes requests slower raises κ (more requests running) and, once misses start, A; both shorten R_M. That is the loop.

## 2. Open-loop turns: a slow engine holds the prefix

Turn k + 1 is sent at its planned time, a gap after turn k's planned time, whether or not turn k has finished. Behind a line that is never empty, admissions leave the line at the service rate μ while requests arrive at λ, so two requests that arrived g apart are admitted about ρ g apart, ρ = λ / μ ≥ 1. Turn k + 1 finds its prefix **held** if turn k is still in the batch when turn k + 1 is admitted:

  P(held) = P(ρ · gap < S) = 1 − exp(−S / (ρ g)).

With no backlog the same event has probability 1 − exp(−S / g).

- In a cold backlog with S ≈ 17 s and ρ = 2.0 / 1.76: P(held) ≈ 0.95 (simulated 0.93, `check_k1`). So an all-miss state is **not self-consistent** with open-loop turns: nineteen of twenty later turns would be admitted while their prefix is held, would hit, and would cost a warm turn's work. The slower the engine, the longer S and the nearer P(held) is to 1: slowdown protects the cache.
- Unloaded and warm with S ≈ 2 s: P(held) ≈ 0.33 (simulated 0.35). On record: the open-loop pair at λ = 2.4 had an overlap share of 0.502 before the burst and 0.835 after it (decisions.md 2026-11-12 [REG] REG-20, prediction; RUN(20261108-220248_burst_l1pl350_r2.4_s1, k1.mechanism)), the direction this formula gives.
- With closed-loop turns P(held) = 0 by construction (`check_k1`, the counterexample case).

## 3. What this predicts for REG-20 (registered there as BELIEF; restated, not changed)

- Open-loop arm at λ = 2.0: the burst fills the pool and evicts idle prefixes, but as soon as the batch is slow, later turns are admitted while their predecessors run and hit. The run should not end cold and backlogged. An overlap share above 0.5 in the 600 s after the burst, and higher reuse for the turns that overlapped than for those that did not, is the mechanism REG-20 asks for.
- Where it can fail (a falsifying observation): an open-loop run that ends cold and backlogged with an overlap share below 0.5. Two ways the engine could produce it, both outside the assumptions: preemption (a preempted turn k frees its blocks, so the hold is lost; (A2) fails), and a residence shorter than the admission spacing (S < ρ g: a batch that is small because the pool is full of long burst prompts).
- A different load under slowdown: open-loop turns keep offering λ while closed-loop turns throttle themselves, so an open arm that recovers does so under more load. That works against K1, not for it (REG-20, alternative 4).

## 4. Relation to the published models

- Model F (Valse and Jannesari §3) assumes every turn misses (F1) and that a completed turn rejoins the tail of the queue (F4). §2 above says (F1) cannot hold with open-loop turns once S exceeds a few gaps; model F is a model of closed-loop sessions, as its authors state ("each has at most one outstanding request", their assumption A1).
- Lu et al.'s drain condition (arrivals below D_low) and Huang and Liu's (λ < 1/S_session) both describe leaving the trap by lowering arrivals. §2 gives a second way out that needs no change of load: holding the prefix. Huang and Liu's parking controller and Valse and Jannesari's session cap restore reuse by shrinking the active set; open-loop turns restore it by overlapping a session's own turns.
- Metronome's stall, which "never recovers, because audio keeps arriving open-loop", has no reusable prefix: (A2)'s reuse does not exist there, so open-loop arrivals only add work.

## 5. Not covered

Chunked prefill and the 2048-token step budget (a request's prefix blocks are committed as they are prefilled, S11, so a turn admitted while its predecessor is still prefilling hits only the part already computed); the reply tokens (the recorded reply in the next prompt is not the generated one, so the last 128 tokens of the previous turn never match); preemption. Each lowers the reuse of an overlapping turn below 1 and none changes the sign.
