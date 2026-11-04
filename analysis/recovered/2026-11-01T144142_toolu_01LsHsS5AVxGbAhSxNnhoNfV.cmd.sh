cd /Users/chalshik/Projects/aftershock-artifacts; sed -n 253,278p docs/experiment-plan.md | cut -c1-330; sed -n 297,310p docs/experiment-plan.md | cut -c1-330; cat configs/long_run.yaml; ls runs | tail -5; uv run python - <<'E'
import numpy as np, pandas as pd
from analysis.load import load_run, percent_fast
for name,a,b,lam in [("20261030-181851_long_run",None,None,3),("20261101-131823_tau",300,900,2),("20261101-131823_tau",1200,2100,3)]:
    r=load_run("runs/"+name); wl=r["cfg"]["workload"]; q=r["requests"]; m=r["metrics"]
    a2=a if a is not None else wl["warmup_s"]; b2=b if b is not None else wl["duration_s"]
    print("\n",name,"lam",lam,"window",a2,b2,"dur",wl["duration_s"],"warm",wl["warmup_s"])
    for w in (60,300,500):
        pf=percent_fast(q[(q.t_planned>=a2)&(q.t_planned<b2)],1.0,w); pf=pf[pf.t+w<=b2]
        print(f" pfast bin={w}: n={len(pf)} min={pf.percent_fast.min():.4f} p5={pf.percent_fast.quantile(.05):.4f} med={pf.percent_fast.median():.4f}")
    h,qq=m["vllm:prefix_cache_hits_total"],m["vllm:prefix_cache_queries_total"]
    ts=np.arange(a2,b2,300); hr=[(np.interp(t+300,m.t,h)-np.interp(t,m.t,h))/(np.interp(t+300,m.t,qq)-np.interp(t,m.t,qq)) for t in ts[:-1] if t+300<=b2]
    print(" hit 300s:",np.round(hr,3).tolist()[:26])
    wq=m["vllm:num_requests_waiting"][(m.t>=a2)&(m.t<b2)]; print(" waiting: mean %.3f p99 %.1f max %d"%(wq.mean(),wq.quantile(.99),wq.max()))
    for wn in (300,):
        tt=[q[(q.t_planned>=t)&(q.t_planned<t+wn)].ttft.quantile(.5) for t in ts[:-1]]; print(" p50 300s range %.3f-%.3f"%(min(tt),max(tt)))
r=load_run("runs/20261030-181851_long_run");m=r["metrics"];q=r["requests"];h,qq=m["vllm:prefix_cache_hits_total"],m["vllm:prefix_cache_queries_total"]
print("\nlong run first 1800s hit per 120s:",[round((np.interp(t+120,m.t,h)-np.interp(t,m.t,h))/(np.interp(t+120,m.t,qq)-np.interp(t,m.t,qq)),3) for t in range(0,1800,120)])
print("sessions: t of last turn in first 1200s etc; N mean per 300s:",[round(m["vllm:num_requests_running"][(m.t>=t)&(m.t<t+300)].mean(),1) for t in range(0,2400,300)])
E