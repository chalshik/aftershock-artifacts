"""Exact binomial bounds for "stuck in k of n" (docs/process.md §5). Stdlib only."""
from math import comb


def _binom_cdf(k: int, n: int, p: float) -> float:
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def cp_upper(k: int, n: int, conf: float = 0.95, one_sided: bool = True) -> float:
    """Clopper–Pearson upper bound on the probability behind k successes in n trials.
    One-sided by default: P(X <= k | p_upper) = 1 - conf. Two-sided uses (1 - conf) / 2."""
    if not 0 <= k <= n or n < 1:
        raise ValueError(f"need 0 <= k <= n and n >= 1, got k={k}, n={n}")
    if k == n:
        return 1.0
    alpha = (1 - conf) if one_sided else (1 - conf) / 2
    lo, hi = k / n, 1.0
    for _ in range(100):  # bisection: the CDF falls as p rises
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _binom_cdf(k, n, mid) > alpha else (lo, mid)
    return hi


def cell(k: int, n: int) -> str:
    """The reporting form: 'k of n (≤ upper, one-sided 95 %)'."""
    return f"{k} of {n} (≤ {cp_upper(k, n):.2f}, one-sided 95 %)"


def _poisson_cdf(k: int, mu: float) -> float:
    """P(X <= k) for X ~ Poisson(mu), summed in log space so that exp(-mu) cannot underflow for large mu."""
    from math import exp, lgamma, log
    if mu <= 0:
        return 1.0
    logs = [-mu + i * log(mu) - lgamma(i + 1) for i in range(k + 1)]
    top = max(logs)
    return min(1.0, exp(top) * sum(exp(x - top) for x in logs))


def poisson_rate_upper(n: int, t: float, conf: float = 0.95) -> float:
    """One-sided exact upper bound on a rate from n events in time t: the mu with P(X <= n | mu) = 1 - conf, over t.
    Completions come in batches, so this is optimistic about precision; use it as a floor on doubt, not a ceiling."""
    if n < 0 or t <= 0:
        raise ValueError("need n >= 0 and t > 0")
    lo, hi = float(n), float(n) + 50.0 + 10.0 * n ** 0.5
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _poisson_cdf(n, mid) > 1 - conf else (lo, mid)
    return hi / t
