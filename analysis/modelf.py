"""Model F of Valse and Jannesari (arXiv 2611.08902v1, §3), the published trapped-state model, for K3 (docs/claims.md).

BELIEF as to the model: the equations are read from the paper's §3 (Lemma 1, Theorems 1-2, Corollary 3), not derived
here. Model F: a fluid FIFO server on which every turn misses; a session of T turns rejoins the queue tail after each
turn; turn k costs c_k. With G_k = P(T >= k) and the cost-weighted turn mix w_k = c_k G_k / sum_j c_j G_j, the trapped
state's growth factor z > 1 solves rho * sum_k w_k z^-k = 1, where rho = lambda / lambda_miss and lambda_miss =
1 / sum_k c_k G_k is the all-miss session capacity. Long-run values (Theorem 1(a)):
  sessions completed / lambda_miss        D / lambda_miss = rho * E[z^-T]
  session backlog growth / excess load    rho * (1 - E[z^-T]) / (rho - 1)
  served-turn mix                         nu_k proportional to G_k z^-k
Theorem 2: D / lambda_miss = H(z) * Gamma(z), H = E[T] E[z^-T] / sum_k G_k z^-k, Gamma = E_nu[c] / E_nu_z[c]; near the
threshold D / lambda_miss - 1 = (rho - 1)(1 - E[T] / kbar_c) + O((rho - 1)^2), kbar_c = sum_k k c_k G_k / sum_k c_k G_k.
Corollary 3: after a change of arrivals to lambda' the trapped queue empties iff lambda' < lambda_miss.

Units in this study: `workload.rate` is requests/s and sessions start at rate / turns (harness/workload.py:95), and the
cache-off capacity mu_off (req/s) is measured at the schedule's stationary turn mix, so rho = rate / mu_off.
Moved from docs/paper/modelf_l1.py (local) on 2026-11-12, with the same numbers (tests/test_modelf.py).
"""
from __future__ import annotations

from dataclasses import dataclass


def survival(p_t: list[float]) -> list[float]:
    """G_k = P(T >= k), k = 1..K, from P(T = k) for k = 1..K."""
    if any(p < 0 for p in p_t) or abs(sum(p_t) - 1.0) > 1e-9:
        raise ValueError("p_t must be a probability vector over T = 1..K")
    return [sum(p_t[k:]) for k in range(len(p_t))]


def fixed_turns(turns: int) -> list[float]:
    """P(T = k) for a session that always has `turns` turns (this study's workloads)."""
    if turns < 1:
        raise ValueError("turns >= 1")
    return [0.0] * (turns - 1) + [1.0]


def l1_prompts(turns: int, first: int = 2176, step: int = 256) -> list[int]:
    """Prompt length of turn k at L1: 2176 + 256 (k - 1) tokens (configs/l1_base.yaml, PROTOCOL.md; docs/model.md M5)."""
    return [first + step * k for k in range(turns)]


@dataclass(frozen=True)
class Trap:
    rho: float
    z: float
    sessions: float          # D / lambda_miss
    backlog_growth: float    # session backlog growth / excess load (lambda - lambda_miss)
    served_prompt: float     # mean prompt of served turns / mean prompt of the stationary turn mix
    requests: float          # turns completed / all-miss turn rate at the stationary mix (mu_off)
    H: float
    Gamma: float


def _ez(p_t, z):
    return sum(p * z ** -(k + 1) for k, p in enumerate(p_t))


def perron_root(p_t: list[float], c: list[float], rho: float, tol: float = 1e-13) -> float:
    """z > 1 with rho * sum_k w_k z^-k = 1. Requires rho > 1 (above the all-miss capacity)."""
    if rho <= 1:
        raise ValueError("model F's trapped regime needs rho > 1; below it the trap drains (Corollary 3)")
    G = survival(p_t)
    if len(c) != len(G) or any(x <= 0 for x in c):
        raise ValueError("one positive cost per turn")
    s = sum(ci * gi for ci, gi in zip(c, G))
    w = [ci * gi / s for ci, gi in zip(c, G)]
    f = lambda z: rho * sum(wk * z ** -(k + 1) for k, wk in enumerate(w)) - 1.0
    lo, hi = 1.0, 2.0
    while f(hi) > 0:
        hi *= 2.0
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
    return 0.5 * (lo + hi)


def trap(p_t: list[float], c: list[float], rho: float, prompts: list[float] | None = None) -> Trap:
    """Model F's long-run trapped values for turn-count law p_t, turn costs c, load rho = lambda / lambda_miss."""
    G = survival(p_t)
    z = perron_root(p_t, c, rho)
    ez = _ez(p_t, z)
    nu = [g * z ** -(k + 1) for k, g in enumerate(G)]
    sn = sum(nu)
    nu = [x / sn for x in nu]
    sg = sum(G)
    stat = [g / sg for g in G]
    mean = lambda mix, v: sum(a * b for a, b in zip(mix, v))
    L = prompts if prompts is not None else c
    H = sg * ez / sum(g * z ** -(k + 1) for k, g in enumerate(G))
    Gamma = mean(stat, c) / mean(nu, c)
    return Trap(rho=rho, z=z, sessions=rho * ez, backlog_growth=rho * (1 - ez) / (rho - 1),
                served_prompt=mean(nu, L) / mean(stat, L), requests=Gamma, H=H, Gamma=Gamma)


def first_order(p_t: list[float], c: list[float], rho: float) -> float:
    """Theorem 2's expansion of D / lambda_miss near the threshold: 1 + (rho - 1)(1 - E[T] / kbar_c)."""
    G = survival(p_t)
    s = sum(ci * gi for ci, gi in zip(c, G))
    kbar = sum((k + 1) * ci * gi for k, (ci, gi) in enumerate(zip(c, G))) / s
    return 1.0 + (rho - 1.0) * (1.0 - sum(G) / kbar)


def drains(lam_after: float, lam_miss: float) -> bool:
    """Corollary 3: a trapped model-F queue empties iff the new arrival rate is below the all-miss capacity."""
    return lam_after < lam_miss


def l1(rate: float, mu_off: float, turns: int = 8, fixed_cost_s: float = 0.0, per_token_s: float = 1.0) -> Trap:
    """Model F at L1 with a fixed turn count, turn cost fixed_cost_s + per_token_s * prompt (default: proportional)."""
    L = l1_prompts(turns)
    return trap(fixed_turns(turns), [fixed_cost_s + per_token_s * x for x in L], rate / mu_off, prompts=L)
