import sys
from pathlib import Path
sys.path.insert(0, "/Users/chalshik/Projects/aftershock-artifacts")
from analysis import e1, k2
from harness.run import load_config
S = k2.shape(load_config(Path("/Users/chalshik/Projects/aftershock-artifacts/configs/sweep_l1pl350cl_pc_on.yaml"))["workload"]["sessions"])
print(k2.predict(S,16))
f = k2.closed_loop_floors(S)
for n, v in f.items():
    print(n, {k: v[k] for k in v if k!="by_onset"}); print(" by_onset", {k: {a: round(b,3) for a,b in x.items()} for k,x in v["by_onset"].items()})
r16 = e1.replay_rows(k2.E0_SWEEPS["off_16"], 1.681, e1.E1["costs"]["fixed"], 0)
print(r16)
print("g", k2.gate_factor())
