cd /Users/chalshik/Projects/aftershock-artifacts; D=$(mktemp -d); gh api -H "Accept: application/vnd.github.raw" "repos/vllm-project/vllm/contents/vllm/v1/core/block_pool.py?ref=v0.32.0" > $D/bp.py; sed -n 774,806p $D/bp.py | cut -c1-100; grep -n "ref_cnt\|def _maybe_evict\|def get_new_blocks\|popleft" $D/bp.py | cut -c1-100 | head -14; sed -n 288,294p docs/experiment-plan.md | cut -c1-260; sed -n 330,335p docs/experiment-plan.md | cut -c1-200; uv run python - <<'E'
import glob,copy,numpy as np,pandas as pd
from analysis.load import load_run
from harness.workload import build_schedule
from harness.run import load_config
from pathlib import Path
C=96656
one=lambda p:sorted(glob.glob("runs/"+p))[-1]
base=load_config(Path("configs/stage2_base.yaml"))
def W(lam,seed):
    wl=copy.deepcopy(base["workload"]);wl["rate"]=lam
    s,_=build_schedule(wl,seed);s=s.sort_values("t_planned")
    g=s.groupby("session_id");a=g.t_planned.min();b=g.t_planned.max();res=[];act=[]
    for t in np.arange(600,2400,5.):
        last=s[s.t_planned<=t].groupby("session_id").tail(1).set_index("session_id")
        live=last[(a.reindex(last.index)<=t)&(b.reindex(last.index)>=t)]
        res.append(live.prompt_len.sum());act.append(len(live))
    # upper bound on hit rate with unlimited cache: all prior prompt reused
    s["prev"]=s.groupby("session_id").prompt_len.shift(1).fillna(0)
    return np.array(res),np.array(act),(s.prev.sum()/s.prompt_len.sum())
for lam in (2,2.5,3,3.5,4,5):
    rs=[W(lam,x) for x in (1,2)]
    w=np.concatenate([r[0] for r in rs]);a=np.concatenate([r[1] for r in rs])
    print(f"λ={lam}: active {a.mean():.1f} W mean {w.mean():.0f} = {w.mean()/C:.2f}C p10 {np.quantile(w,.1)/C:.2f} p90 {np.quantile(w,.9)/C:.2f}; hit ceiling {rs[0][2]:.3f}")
print("--- F: mean, and last third of the measured window")
for lam,p in [(2,"*sweep_pc_on_r2"),(3,"*sweep_pc_on_r3"),(4,"*sweep_pc_on_r4"),(5,"*sweep_pc_on_r5"),(2,"*sweep_pc_off_r2"),(3,"*sweep_pc_off_r3"),(4,"*sweep_pc_off_r4")]:
    r=load_run(one(p));m=r["metrics"];wl=r["cfg"]["workload"];K=m[(m.t>=wl["warmup_s"])&(m.t<wl["duration_s"])]
    t3=wl["warmup_s"]+2*(wl["duration_s"]-wl["warmup_s"])/3;L=K[K.t>=t3];h=m["vllm:prefix_cache_hits_total"];q=m["vllm:prefix_cache_queries_total"]
    print(p[1:],"dur",wl["duration_s"],"KV mean %.3f last third %.3f"%(K["vllm:kv_cache_usage_perc"].mean(),L["vllm:kv_cache_usage_perc"].mean()),"hit %.3f"%((h.iloc[-1]-h.iloc[0])/max(q.iloc[-1]-q.iloc[0],1)),"Q last third %.1f"%L["vllm:num_requests_waiting"].mean())
for p in ["*sweep_pc_off_r3"]:
    r=load_run(one(p));q=r["requests"];print("pc_off r3 pf by 150s:",[round(((x.status=="ok")&(x.ttft<=1)).mean(),2) for _,x in q.groupby((q.t_planned//150)*150)])
E