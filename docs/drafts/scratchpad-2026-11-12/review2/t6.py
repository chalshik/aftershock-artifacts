import sys; sys.path.insert(0, "/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/fdf13821-770b-43f6-866b-c82b3bbdc140/scratchpad/review2")
from truth import *
def sw(rates, closed=True, seed=None):
    out = []
    for r in rates:
        c = copy.deepcopy(load_config(C / "sweep_l1pl350_pc_off.yaml")); c["workload"]["rate"] = r
        c["workload"]["sessions"]["closed_loop"] = closed
        if seed is not None: c["seed"] = seed
        out.append(c)
    return out
for mu in (1.681, 1.70, 1.75, 1.80):
    st = K3.e1_statistic(sw((1.5, 1.8, 2.0, 2.5, 3.0, 4.0)), mu, (0.0, 1.0))
    print(mu, "lam_sat", st["lam_sat"], "stat %.3f" % st["statistic"], [(r["rate"], round(r["throughput"], 3), round(r["planned_rate"], 3)) for r in st["rows"]])
st = K3.e1_statistic(sw((1.5, 1.8, 2.0, 2.5, 3.0, 4.0)), 1.681, (0.18, 0.000135)); print("fixed 1.681", round(st["statistic"],3), [(r["rate"], round(r["throughput"], 3)) for r in st["rows"]])
# seeds spread for one rate set
v=[K3.e1_statistic(sw((2.0, 2.5, 3.0), seed=s), 1.681, (0.0,1.0))["statistic"] for s in range(1,9)]
print("seed spread at 1.681 rates 2.0/2.5/3.0:", np.round(v,3), "sd %.3f"%np.std(v))
