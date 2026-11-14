# Soundness of e1.floor's holes rule: a floor reported on a subset S of the grid must equal the floor the full grid
# would give, whatever values the missing rows take (three row types). Also: "less data never gives a cleaner status".
import itertools, math, sys
import pandas as pd
from analysis import e1
grid = (1.5, 2.0, 2.5, 3.0, 3.5, 4.0)
planned = {1.5: 1.606, 2.0: 2.097, 2.5: 2.6, 3.0: 3.1, 3.5: 3.6, 4.0: 4.1}
def row(r, t):
    p = planned[r]
    if t == "low":   return dict(run=f"r{r}", rate=r, throughput=p, planned_rate=p, kv_mean=0.5)    # kept up, not full
    if t == "full":  return dict(run=f"r{r}", rate=r, throughput=p, planned_rate=p, kv_mean=0.95)   # full, kept up
    if t == "sat":   return dict(run=f"r{r}", rate=r, throughput=1.70 + 0.02 * r, planned_rate=p, kv_mean=0.95)
types = ("low", "full", "sat")
bad_value = bad_mono = n_floor = 0
for full in itertools.product(types, repeat=len(grid)):
    for k in range(len(grid) + 1):
        for miss in itertools.combinations(range(len(grid)), k):
            S = [i for i in range(len(grid)) if i not in miss]
            rs = pd.DataFrame([row(grid[i], full[i]) for i in S], columns=["run", "rate", "throughput", "planned_rate", "kv_mean"])
            f = e1.floor(rs, grid)
            if f["status"] not in ("ok", "tail_ok"):
                continue
            n_floor += bool(miss)
            # every completion of the missing rows
            for fill in itertools.product(types, repeat=len(miss)):
                t = list(full); [t.__setitem__(i, v) for i, v in zip(miss, fill)]
                g = e1.floor(pd.DataFrame([row(grid[i], t[i]) for i in range(len(grid))]), grid)
                if g["status"] not in ("ok", "tail_ok") or abs(g["mu_sat_off"] - f["mu_sat_off"]) > 1e-12 or g["lam_sat"] != f["lam_sat"]:
                    bad_value += 1
                    if bad_value <= 5: print("VALUE", full, miss, fill, f["status"], f["lam_sat"], g["status"], g["lam_sat"])
print("floors on partial data:", n_floor, "| completions that change the floor:", bad_value)
