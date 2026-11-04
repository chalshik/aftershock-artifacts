cd /Users/chalshik/Projects/aftershock-artifacts; date -u; tail -c 300 /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/c075c1a8-132c-4000-a89a-88e64c9c2bfd/tasks/bx5brdd38.output; echo; rsync -a -e "ssh -i $HOME/.ssh/id_ed25519_vllm -o IdentitiesOnly=yes -o BatchMode=yes" chalshik@192.168.3.249:aftershock-artifacts/runs/20261102-100744_wipe_preempt_r3_s3 runs/; echo rsync=$?; uv run python - <<'E'
import numpy as np
from analysis.load import load_run,verdict
r=load_run("runs/20261102-100744_wipe_preempt_r3_s3");c=r["checks"]
print("valid",c["valid"],c["failed"])
for x in c["checks"]: print(" ",x["name"],x["passed"],str(x["detail"])[:200])
v=verdict(r);print("VERDICT",v["verdict"])
for k in("baseline","previous","end"): print("  ",k,{a:round(b,3) for a,b in v[k].items()})
q=r["requests"];m=r["metrics"];T=v["t_wipe"];h=m["vllm:prefix_cache_hits_total"];qq=m["vllm:prefix_cache_queries_total"];p=m["vllm:num_preemptions_total"]
print("status",q.status.value_counts().to_dict(),"output",q.output_tokens.value_counts().to_dict(),"preempt",int(p.iloc[-1]-p.iloc[0]))
for a,b in [(0,15),(15,60),(60,120),(120,300)]:
    z=q[(q.t_planned>=T+a)&(q.t_planned<T+b)];w=m[(m.t>=T+a)&(m.t<T+b)]
    print("  +%d..%d fast %.3f hit %.3f maxQ %d maxKV %.2f"%(a,b,((z.status=="ok")&(z.ttft<=1)).mean(),(np.interp(T+b,m.t,h)-np.interp(T+a,m.t,h))/(np.interp(T+b,m.t,qq)-np.interp(T+a,m.t,qq)),w["vllm:num_requests_waiting"].max(),w["vllm:kv_cache_usage_perc"].max()))
g=r["gpu"];w=g[(g.t>=240)&(g.t<=2400)];b=w[w.util_pct>=50]
print("gpu mean busy T %.1f p90 %d max %d"%(b.temp_c.mean(),b.temp_c.quantile(.9),w.temp_c.max()))
E