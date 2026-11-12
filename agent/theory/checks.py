"""Numeric checks of the derivations in agent/theory/*.md. Synthetic only; no run folder is read.

    uv run --offline python agent/theory/checks.py        # exits non-zero if a check fails

Each check has a case that should hold and a counterexample case in which the formula's premise is broken.
"""
import heapq
import math
import sys

import numpy as np

L1 = {"system": 2048, "user": 128, "reply": 128, "out": 128, "gap": 5.0, "pool": 96_656}
COST = (0.18, 0.000135)          # s + s/token: docs/model.md M5's fixed-cost model (REG-8's two capacities)


def cold_tokens(T, s=L1["system"], u=L1["user"], r=L1["reply"]):
    return s + u + (u + r) * (T - 1) / 2


def warm_tokens(T, s=L1["system"], u=L1["user"], r=L1["reply"]):
    return (s + u + (T - 1) * (u + r)) / T


# ---------------------------------------------------------------- K1: the held-prefix probability

def held_share_sim(lam, T, residence, gap_mean, servers, horizon=4000.0, seed=0, closed=False):
    """A queue with `servers` slots; every request stays `residence` seconds in service (a running batch whose
    throughput is servers / residence). Sessions start as a Poisson process at lam / T; with open-loop turns turn k is
    sent at its planned time (gaps exponential, counted from the previous planned time); with closed-loop turns it is
    sent a gap after the previous turn ended. Returns the share of later turns that are admitted while the previous
    turn of their session is still in service (its prefix is then held), over turns admitted after horizon / 2."""
    rng = np.random.default_rng(seed)
    t, arr, n = 0.0, [], 0
    while t < horizon:
        t += rng.exponential(T / lam)
        gaps = rng.exponential(gap_mean, T - 1)
        if closed:
            arr.append((t, n, 0, tuple(gaps)))
        else:
            for k, tk in enumerate(np.concatenate([[t], t + np.cumsum(gaps)])):
                arr.append((float(tk), n, k, ()))
        n += 1
    heapq.heapify(arr)
    busy, queue, free, now, c = [], [], servers, 0.0, 0
    end_of, held, later = {}, 0, 0
    while arr or queue or busy:
        if free > 0 and queue:
            _, _, sid, k, gaps = heapq.heappop(queue)
            if k > 0 and now > horizon / 2:
                later += 1
                held += end_of.get((sid, k - 1), -1.0) > now
            end_of[(sid, k)] = now + residence
            heapq.heappush(busy, (now + residence, sid, k, gaps))
            free -= 1
            continue
        ta, tb = (arr[0][0] if arr else math.inf), (busy[0][0] if busy else math.inf)
        if ta <= tb:
            now, sid, k, gaps = heapq.heappop(arr)
            c += 1
            heapq.heappush(queue, (now, c, sid, k, gaps))
        else:
            now, sid, k, gaps = heapq.heappop(busy)
            free += 1
            if closed and k < T - 1:
                heapq.heappush(arr, (now + gaps[k], sid, k + 1, gaps))
        if now > 2 * horizon:
            break
    return held / later if later else math.nan


def held_share_formula(residence, gap_mean, rho):
    """P(the next turn is admitted while the previous one is still in service) for open-loop turns behind a
    first-come-first-served line that is never empty: admissions leave the line at the service rate, so two requests
    that arrived g apart are admitted about rho * g apart (rho = arrival rate over service rate)."""
    return 1 - math.exp(-residence / (max(rho, 1.0) * gap_mean))


def check_k1():
    out = []
    # (a) overload, long residence: nearly every later turn finds its prefix held
    lam, T, S, B = 2.0, 8, 17.0, 30          # throughput B / S = 1.76 req/s < lam: a backlog
    rho = lam / (B / S)
    sim, f = held_share_sim(lam, T, S, 5.0, B), held_share_formula(S, 5.0, rho)
    out.append(("K1 open-loop, backlog, residence 17 s", sim, f, abs(sim - f) < 0.05 and sim > 0.9))
    # (b) no backlog, short residence: the share is the unloaded one, 1 - exp(-S / g)
    lam, S, B = 2.0, 2.0, 30                 # throughput 15 req/s: never queues
    sim, f = held_share_sim(lam, T, S, 5.0, B), 1 - math.exp(-S / 5.0)
    out.append(("K1 open-loop, no backlog, residence 2 s", sim, f, abs(sim - f) < 0.05))
    # (c) counterexample: closed-loop turns never find the prefix held, whatever the residence
    sim = held_share_sim(2.0, T, 17.0, 5.0, 30, closed=True)
    out.append(("K1 closed-loop: held share is 0 by construction", sim, 0.0, sim == 0.0))
    return out


# ---------------------------------------------------------------- K2: how the two capacities scale with the turns

def cost(tokens, ab=COST):
    return ab[0] + ab[1] * tokens


def window_ratio_cost_limited(T, ab=COST):
    """warm capacity / cold floor when both are set by the cost per request at the stationary mix."""
    return cost(cold_tokens(T), ab) / cost(warm_tokens(T), ab)


def window_ratio_memory_limited(T, ab=COST, pool=L1["pool"], cycle_s=6.5):
    """warm capacity / cold floor when the warm side ends where the sessions' latest contexts fill the pool:
    lam_fit * cycle_s * cold_tokens(T) = pool (cycle_s: think time plus response time of a warm turn)."""
    lam_fit = pool / (cycle_s * cold_tokens(T))
    return lam_fit * cost(cold_tokens(T), ab)


def check_k2():
    out = []
    r8, r16, r4 = (window_ratio_cost_limited(T) for T in (8, 16, 4))
    out.append(("K2 cost-limited: ratio grows with T (4 < 8 < 16)", (r4, r8, r16), None, r4 < r8 < r16))
    out.append(("K2 cost-limited R = ratio16/ratio8 (fixed cost)", r16 / r8, 1.319, abs(r16 / r8 - 1.319) < 0.005))
    p8, p16 = (window_ratio_cost_limited(T, (0.0, 1.0)) for T in (8, 16))
    out.append(("K2 cost-limited R (proportional cost) = token-gap ratio", p16 / p8, 10.89 / 6.19, abs(p16 / p8 - 10.89 / 6.19) < 0.01))
    m8, m16 = window_ratio_memory_limited(8), window_ratio_memory_limited(16)
    exact = (COST[0] / cold_tokens(16) + COST[1]) / (COST[0] / cold_tokens(8) + COST[1])
    out.append(("K2 memory-limited R = (a/L16 + b)/(a/L8 + b) < 1", m16 / m8, exact, abs(m16 / m8 - exact) < 1e-9 and m16 < m8))
    # counterexample: with no fixed cost per request the memory-limited ratio does not depend on T at all
    z8, z16 = window_ratio_memory_limited(8, (0.0, 1.0)), window_ratio_memory_limited(16, (0.0, 1.0))
    out.append(("K2 memory-limited, proportional cost: R = 1 exactly", z16 / z8, 1.0, abs(z16 / z8 - 1.0) < 1e-12))
    out.append(("K2 tokens: cold 3072/4096/2560, warm 496/376/736",
                (cold_tokens(8), cold_tokens(16), cold_tokens(4), warm_tokens(8), warm_tokens(16), warm_tokens(4)), None,
                (cold_tokens(8), cold_tokens(16), cold_tokens(4), warm_tokens(8), warm_tokens(16), warm_tokens(4))
                == (3072.0, 4096.0, 2560.0, 496.0, 376.0, 736.0)))
    return out


# ---------------------------------------------------------------- the turnover time of an idle prefix

def turnover_s(pool, kv_running, alloc_tok_s):
    """Time until an idle prefix released now is evicted: the blocks not held by running requests, divided by the
    rate at which new blocks are allocated (uncached prefill plus output tokens)."""
    return pool * (1 - kv_running) / alloc_tok_s


def check_turnover():
    warm = turnover_s(L1["pool"], 0.171, 2.0 * (warm_tokens(8) + L1["out"]))        # REG-17's control: KV 0.171
    cold = turnover_s(L1["pool"], 0.949, 1.75 * (cold_tokens(8) + L1["out"]))       # REG-17's burst run: KV 0.949
    return [("turnover, warm at 2.0 req/s: far longer than a 5 s gap", warm, None, warm > 10 * L1["gap"]),
            ("turnover, cold: far shorter than a 5 s gap", cold, None, cold < L1["gap"] / 2)]


if __name__ == "__main__":
    rows = check_k1() + check_k2() + check_turnover()
    for name, got, want, ok in rows:
        print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}" + ("" if want is None else f" (expected {want})"))
    sys.exit(0 if all(r[3] for r in rows) else 1)
