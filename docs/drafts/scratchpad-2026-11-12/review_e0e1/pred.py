import json, sys
sys.path.insert(0, "/Users/chalshik/Projects/aftershock-artifacts")
from analysis import e1, k2
from harness.run import load_config
p = e1.prediction()
for lo, per in p["by_onset"].items():
    print(lo, {c: (round(v["threshold"],3), {n: (round(m["d_F"],3), round(m["d_sd"],3)) for n, m in v["models"].items()}) for c, v in per.items()})
for n, d in p["rows_seed0"].items():
    for k, rows in d.items():
        print(n, k, [(r["rate"], round(r["throughput"],3), round(r["kbar"],2), r["kv_mean"], round(r["planned_rate"],3)) for r in rows])
S = k2.shape(load_config("/Users/chalshik/Projects/aftershock-artifacts/configs/sweep_l1pl350cl_pc_on.yaml")["workload"]["sessions"])
print(k2.predict(S,16))
f = k2.closed_loop_floors(S)
for n, v in f.items():
    print(n, {k: v[k] for k in v if k!="by_onset"}); print(" by_onset", {k: {a: round(b,3) for a,b in x.items()} for k,x in v["by_onset"].items()})
