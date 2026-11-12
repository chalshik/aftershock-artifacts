# BELIEF inputs -> outcome probabilities under analysis/k1.k1_outcome's rules (mechanism and controls aside).
from math import comb
from analysis.stats import fisher_one_sided
pc, po, alpha = 0.85, 0.10, 0.05
for n in (5, 4, 3):
    P = {"supports": 0, "refutes": 0, "inconclusive": 0, "closed_not_cold": 0}
    for kc in range(n + 1):
        for ko in range(n + 1):
            w = comb(n, kc) * pc**kc * (1-pc)**(n-kc) * comb(n, ko) * po**ko * (1-po)**(n-ko)
            if kc == 0: P["closed_not_cold"] += w
            elif ko >= 3 or ko >= kc: P["refutes"] += w
            elif fisher_one_sided(kc, n, ko, n) <= alpha: P["supports"] += w
            else: P["inconclusive"] += w
    print(n, {k: round(v, 3) for k, v in P.items()}, "P(k_open=0)", round((1-po)**n, 3))
