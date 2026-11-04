cd /Users/chalshik/Projects/aftershock-artifacts; date -u; cut -c1-200 /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/c075c1a8-132c-4000-a89a-88e64c9c2bfd/tasks/b59yybocr.output | tail -3; rsync -a -e "ssh -i $HOME/.ssh/id_ed25519_vllm -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=10" --include='*wipe_preempt_r3*/***' --exclude='*' chalshik@192.168.3.249:aftershock-artifacts/runs/ runs/; echo rsync=$?; ls -d runs/*wipe_preempt_r3*; ssh -i $HOME/.ssh/id_ed25519_vllm -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=10 chalshik@192.168.3.249 'tail -n 4 ~/wipes_r3.console.log | cut -c1-110; uptime -p; tmux ls 2>&1 | cut -c1-50; cd ~/aftershock-artifacts; echo "git $(git rev-parse --short HEAD) dirty=$(git status --porcelain | wc -l)"'; uv run python - <<'E'
import glob,numpy as np
from analysis.load import load_run,verdict
ctrl=load_run(sorted(glob.glob("runs/*r3_rerun"))[0]);print("control",verdict(ctrl)["verdict"])
for d in sorted(glob.glob("runs/*wipe_preempt_r3*")):
    r=load_run(d);c=r["checks"]
    print("\n==",d.split("/")[1])
    if not c: print(" no checks");continue
    print(" valid",c["valid"],c["failed"],"| gpu",[x["detail"] for x in c["checks"] if x["name"]=="gpu_steady"][0])
    print(" trigger",[x["detail"]["wipe"] for x in c["checks"] if x["name"]=="trigger"][0])
    v=verdict(r);print(" VERDICT",v["verdict"],"t_wipe %.2f"%v["t_wipe"])
    for k in("baseline","previous","end"): print("  ",k,{a:round(b,3) for a,b in v[k].items()})
    q=r["requests"];m=r["metrics"];p=m["vllm:num_preemptions_total"];T=v["t_wipe"];h=m["vllm:prefix_cache_hits_total"];qq=m["vllm:prefix_cache_queries_total"]
    print(" status",q.status.value_counts().to_dict(),"output",q.output_tokens.value_counts().to_dict(),"preempt total",int(p.iloc[-1]-p.iloc[0]),"after +5s",int(p.iloc[-1]-np.interp(T+5,m.t,p)))
    for a,b in [(0,15),(15,60),(60,120),(120,300),(300,600),(600,1500)]:
        z=q[(q.t_planned>=T+a)&(q.t_planned<T+b)];w=m[(m.t>=T+a)&(m.t<T+b)]
        print("   +%4d..%4d n %4d fast %.3f p50 %.3f p99 %.2f max %.2f hit %.3f N %.1f maxN %d Q %.1f maxQ %d KV %.2f maxKV %.2f"%(a,b,len(z),((z.status=="ok")&(z.ttft<=1)).mean(),z.ttft.median(),z.ttft.quantile(.99),z.ttft.max(),(np.interp(T+b,m.t,h)-np.interp(T+a,m.t,h))/(np.interp(T+b,m.t,qq)-np.interp(T+a,m.t,qq)),w["vllm:num_requests_running"].mean(),w["vllm:num_requests_running"].max(),w["vllm:num_requests_waiting"].mean(),w["vllm:num_requests_waiting"].max(),w["vllm:kv_cache_usage_perc"].mean(),w["vllm:kv_cache_usage_perc"].max()))
E