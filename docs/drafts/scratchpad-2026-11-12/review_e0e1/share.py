"""SYNTHETIC: first-turn share of ok completions in [240, 900) on the model-F replay, closed and open loop."""
import sys
sys.path.insert(0, "/Users/chalshik/Projects/aftershock-artifacts")
from analysis import e1, modelf_sim
for k in ("cl", "ol"):
    out = []
    for c in e1._cfgs(e1.E1["configs"][k], 0):
        q = modelf_sim.simulate(c, 1.681, (0.0, 1.0), all_miss_from=0.0)
        d = q[(q.status == "ok") & (q.t_end >= 240) & (q.t_end < 900)]
        out.append((c["workload"]["rate"], round(float((d.turn == 0).mean()), 3)))
    print(k, out)
