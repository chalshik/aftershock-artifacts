cd /Users/chalshik/Projects/aftershock-artifacts; cat /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/f5298640-1574-4ceb-a3d1-13cbc96eea3b/tasks/blme3i931.output | cut -c1-300; rsync -a -e "ssh -i $HOME/.ssh/id_ed25519_vllm -o IdentitiesOnly=yes -o BatchMode=yes" --include='*_wipe_test_*/***' --exclude='*' chalshik@192.168.3.249:aftershock-artifacts/runs/ runs/; echo rsync=$?; ls -d runs/*wipe_test*; uv run python - <<'E'
import glob,json,numpy as np,pandas as pd,re
from analysis.load import load_run
for d in sorted(glob.glob("runs/*wipe_test*")):
    r=load_run(d); print("\n===",d)
    ck=json.load(open(d+"/checks.json")) if glob.glob(d+"/checks.json") else None
    print("valid",ck and ck["valid"],"failed",ck and ck["failed"])
    if ck:
        for c in ck["checks"]:
            if c["name"] in("trigger","accounting","recorder","no_errors","client_lag"): print(" ",c["name"],c["passed"],str(c["detail"])[:300])
    t=r["trigger"]; print("attempts",len(t), t.status.value_counts().to_dict() if len(t) else None)
    if not len(t): continue
    s=t[t.success]; print(t.tail(2).to_dict("records"))
    if not len(s): continue
    tw=float(s.t_end.iloc[0]); tst=float(s.t_start.iloc[0]); print("wipe t_start %.3f t_end %.3f dur %.3f"%(tst,tw,tw-tst))
    m=r["metrics"];q=r["requests"]
    cols=[c for c in m.columns if "preempt" in c]; print("preempt cols",cols)
    near=m[(m.t>=tw-3)&(m.t<=tw+4)]
    print(near[["t","vllm:num_requests_running","vllm:num_requests_waiting","vllm:kv_cache_usage_perc"]+cols].round(2).to_string(index=False))
    h,qq=m["vllm:prefix_cache_hits_total"],m["vllm:prefix_cache_queries_total"]
    for a,b in [(tw-120,tw),(tw,tw+15),(tw+15,tw+60),(tw+60,tw+120),(tw+120,tw+300)]:
        dq=np.interp(b,m.t,qq)-np.interp(a,m.t,qq); rq=q[(q.t_planned>=a)&(q.t_planned<b)]
        print(f" {a-tw:+5.0f}..{b-tw:+4.0f}s hit={(np.interp(b,m.t,h)-np.interp(a,m.t,h))/dq:.3f} n={len(rq)} p50={rq.ttft.median():.3f} p99={rq.ttft.quantile(.99):.3f} max={rq.ttft.max():.3f} cached_mean={rq.cached_tokens.mean():.0f}")
    print(" statuses",q.status.value_counts().to_dict(),"output_tokens",q.output_tokens.value_counts().to_dict())
    inflight=q[(q.t_sent<tst)&(q.t_end>tw)]; print(" in flight at wipe:",len(inflight),"output tokens",inflight.output_tokens.tolist()[:20],"e2e",inflight.e2e.round(2).tolist()[:20])
    other=q[(q.t_sent>=tst-30)&(q.t_sent<tst)&(q.t_end<tst)]; print(" normal e2e before p50 %.2f"%q[q.t_planned<tst].e2e.median())
    log=open(d+"/server.log",errors="ignore").read()
    print(" log: resets",len(re.findall("Successfully reset prefix cache",log)),"failed",len(re.findall("Failed to reset prefix cache",log)),"tracebacks",log.count("Traceback"))
E