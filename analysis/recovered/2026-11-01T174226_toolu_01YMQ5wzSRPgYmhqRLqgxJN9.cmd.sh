cd /Users/chalshik/Projects/aftershock-artifacts; uv run python - <<'E'
import glob,numpy as np,pandas as pd
from analysis.load import load_run,verdict
one=lambda p:sorted(glob.glob("runs/"+p))[-1]
print("=== noise in healthy long run, λ=3")
r=load_run(one("*long_run"));m=r["metrics"];q=r["requests"]
h,qq=m["vllm:prefix_cache_hits_total"],m["vllm:prefix_cache_queries_total"]
def hit(a,b):return (np.interp(b,m.t,h)-np.interp(a,m.t,h))/(np.interp(b,m.t,qq)-np.interp(a,m.t,qq))
for w in (300,450,600,750):
    ts=np.arange(600,7200-2*w,60.); d=np.array([hit(t+w,t+2*w)-hit(t,t+w) for t in ts])
    print(f" adjacent {w}s windows hit diff: sd {d.std():.3f} p95|d| {np.quantile(abs(d),.95):.3f} max {abs(d).max():.3f}; rises>=.02 share {(d>=.02).mean():.2f}")
# false slow-drain style: slope of 60s-bin hit over 900s
sl=[]
for t in np.arange(600,7200-900,60.):
    x=np.arange(t,t+900,60.);y=[hit(a,a+60) for a in x];sl.append(np.polyfit(x,y,1)[0]*300)
sl=np.array(sl);print(" hit slope per 300s over 900s: sd %.3f p95|s| %.3f max %.3f"%(sl.std(),np.quantile(abs(sl),.95),abs(sl).max()))
W=m["vllm:num_requests_waiting"]
print("=== backlog vs session turns: was the previous turn unfinished when the next was sent?")
for p in ["*sweep_pc_on_r3","*sweep_pc_on_r4","*sweep_pc_on_r5","*sweep_pc_on_r6","*sweep_pc_on_r10","*sweep_pc_off_r3","*sweep_pc_off_r4"]:
    r=load_run(one(p));q=r["requests"].sort_values(["session_id","turn"]).copy();wl=r["cfg"]["workload"]
    q["prev_first"]=q.groupby("session_id").t_first_token.shift(1);q["prev_end"]=q.groupby("session_id").t_end.shift(1);later=q[(q.turn>0)&(q.t_planned>=wl["warmup_s"])&(q.t_planned<wl["duration_s"])]
    # prefix available only if previous request had been prefilled before this one started being served
    nf=(later.t_sent<later.prev_first)|later.prev_first.isna(); ne=(later.t_sent<later.prev_end)|later.prev_end.isna()
    done=later[later.t_first_token.notna()]
    rate=(done.cached_tokens/done.prompt_tokens)
    bl=(done.t_first_token<done.prev_first)|done.prev_first.isna()
    print(p[1:],"later turns %d | sent before prev first token %.3f, before prev end %.3f | gap p50 %.0fs | cached share: all %.3f, prev already done at own start %.3f"%(len(later),nf.mean(),ne.mean(),(later.t_sent-later.groupby("session_id").t_sent.shift(1)).median() if False else 0,rate.mean(),rate[(done.t_first_token>done.prev_end)].mean() if len(done) else 0))
print("=== sessions in a stage 2 run")
sc=pd.read_parquet(one("*long_run")+"/schedule.parquet");print(" long run sessions",sc.session_id.nunique(),"max turn",sc.turn.max(),"req",len(sc),"session span p50 %.0f"%(sc.groupby("session_id").t_planned.max()-sc.groupby("session_id").t_planned.min()).median())
print("=== current verdict rule on existing runs, judged at t=450 (mechanics runs excluded)")
import copy
V={"control_t_s":900,"baseline_s":600,"watch_s":1500,"end_s":300,"min_baseline_pf":.98,"recovered_pf_drop":.02,"recovered_hit_drop":.06,"recovered_q_excess":1.0,"stuck_pf_drop":.10,"stuck_hit_drop":.06,"q_slope":.01,"climb":.02}
r=load_run(one("*long_run"));r["cfg"]["verdict"]=V;r["cfg"]["slo"]={"ttft_s":1.0}
for t in (900,2400,3900,5400):
    V2=dict(V,control_t_s=t);r["cfg"]["verdict"]=V2;v=verdict(r);print(" healthy λ=3 at",t,v["verdict"],{k:round(v["end"][k],3) for k in v["end"]},"base hit %.3f"%v["baseline"]["hit"])
E