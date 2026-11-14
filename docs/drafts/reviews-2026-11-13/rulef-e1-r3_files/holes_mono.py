# Monotonicity of e1.floor's status in the data: for one underlying sweep (a type per rate) and present sets S < S',
# a floor on S must not be "holes" on S' (less data never gives a cleaner status), and the floor values agree.
import itertools
import pandas as pd
from analysis import e1
grid = (1.5, 2.0, 2.5, 3.0, 3.5, 4.0)
planned = {1.5: 1.606, 2.0: 2.097, 2.5: 2.6, 3.0: 3.1, 3.5: 3.6, 4.0: 4.1}
def row(r, t):
    p = planned[r]
    return dict(run=f"r{r}", rate=r, planned_rate=p,
                throughput={"low": p, "full": p, "sat": 1.70 + 0.02 * r}[t], kv_mean={"low": 0.5, "full": 0.95, "sat": 0.95}[t])
FL = ("ok", "tail_ok")
bad = pairs = 0
for full in itertools.product(("low", "full", "sat"), repeat=6):
    memo = {}
    for k in range(7):
        for S in itertools.combinations(range(6), k):
            memo[S] = e1.floor(pd.DataFrame([row(grid[i], full[i]) for i in S], columns=["run","rate","throughput","planned_rate","kv_mean"]), grid)
    for S, f in memo.items():
        if f["status"] not in FL: continue
        for S2, g in memo.items():
            if set(S) < set(S2):
                pairs += 1
                if g["status"] == "holes" or (g["status"] in FL and abs(g["mu_sat_off"] - f["mu_sat_off"]) > 1e-12):
                    bad += 1
                    if bad <= 3: print("BAD", full, S, f["status"], S2, g["status"])
print("pairs (floor on S, S < S'):", pairs, "| S' gives holes or another floor:", bad)
