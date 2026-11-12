import math, json, numpy as np, pandas as pd
from analysis import e1, k2
from analysis.load import capacity
from harness.workload import build_schedule
# 1. planned mix in the window, open-loop schedule (closed loop only delays later turns further)
for path in ["configs/sweep_l1pl350cl_pc_on.yaml","configs/sweep_l1t16pl350cl_pc_on.yaml","configs/sweep_l1t16pl350cl_pc_off.yaml"]:
    for c in e1._cfgs(path)[:3]:
        wl=c["workload"]; T=wl["sessions"]["turns"]; df,_=build_schedule(wl,c["seed"],None)
        w=df[(df.t_planned>=wl["warmup_s"])&(df.t_planned<wl["duration_s"])]
        s=k2.shape(wl["sessions"])
        print(path.split('/')[-1], wl["rate"], "T",T,"kbar",round((w.turn+1).mean(),3),"stat",(T+1)/2,
              "cold mean",round(w.prompt_len.mean(),0),"stat",k2.cold_tokens(s),
              "first-turn share",round((w.turn==0).mean(),4),"stat",round(1/T,4),"planned/rate",round(len(w)/(wl['duration_s']-wl['warmup_s'])/wl['rate'],3))
# 2. tail fallback traces (synthetic)
def rows(r,t,kv,pl=None): return pd.DataFrame({"rate":r,"throughput":t,"planned_rate":pl or [x*1.05 for x in r],"kv_mean":kv})
R=[1.5,2,2.5,3,3.5,4]
print("A mid row kept up:", e1.floor(rows(R,[1.45,1.72,2.6,1.76,1.78,1.80],[.9]*6)))
print("B only top 2 sat, lower kept up at 3.0:", e1.floor(rows(R,[1.55,2.05,2.6,3.1,3.4,3.5],[.9]*6)))
print("C 2.0 sat, 2.5 kv low:", e1.floor(rows(R,[1.45,1.72,1.74,1.76,1.78,1.80],[.5,.9,.6,.9,.9,.9])))
# 3. decide traces
print("D true widen read floor_only", k2.decide(2.4,1.744,2.4,1.431))
print("E refute w/o margin", k2.decide(2.4,1.744,2.0,1.744*0.85))
print("F R_upper unresolved though warm lost", k2.decide(2.4,1.744,math.nan,1.744*0.76))
print("G g with warm8=2.0", k2.gate_factor(2.0), "warm8=3.0", k2.gate_factor(3.0))
# 4. chain ends at invalid 2.2
c=pd.DataFrame({"rate":[2.0,2.4,2.6,2.8],"throughput":[2.0,2.4,2.6,2.8],"planned_rate":[2.0,2.4,2.6,2.8],"q_slope_per_s":[0]*4})
print("H 2.2 invalid ->", capacity(c,0.95,0.01,"planned_rate",True,list(k2.E0["warm_grid_16"])))
# 5. closed-loop floors by onset
S=k2.shape(e1._cfgs("configs/sweep_l1pl350cl_pc_on.yaml")[0]["workload"]["sessions"])
f=k2.closed_loop_floors(S)
for n in f: print(n, json.dumps({k:{a:round(b,3) for a,b in v.items()} for k,v in f[n]["by_onset"].items()}))
print(k2.predict_measured(S))
