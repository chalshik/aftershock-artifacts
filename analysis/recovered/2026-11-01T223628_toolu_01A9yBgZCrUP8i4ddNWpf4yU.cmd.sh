cd /Users/chalshik/Projects/aftershock-artifacts; date -u; cut -c1-160 /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/c075c1a8-132c-4000-a89a-88e64c9c2bfd/tasks/bh9191w73.output | tail -3; rsync -a -e "ssh -i $HOME/.ssh/id_ed25519_vllm -o IdentitiesOnly=yes -o BatchMode=yes" --include='*r3_rerun*/***' --exclude='*' chalshik@192.168.3.249:aftershock-artifacts/runs/ runs/; echo rsync=$?; ls -d runs/*r3_rerun*; uv run python - <<'E'
import glob,json
from analysis.load import load_run,verdict
for d in sorted(glob.glob("runs/*r3_rerun*")):
    r=load_run(d);c=r["checks"]
    print(d,"has checks",bool(c))
    if not c: continue
    print("valid",c["valid"],c["failed"])
    for x in c["checks"]: print(" ",x["name"],x["passed"],str(x["detail"])[:170])
    v=verdict(r);print("verdict",v["verdict"])
    for k in("baseline","previous","end"): print("  ",k,{a:round(b,3) for a,b in v[k].items()})
    q=r["requests"];m=r["metrics"];p=m["vllm:num_preemptions_total"];print("status",q.status.value_counts().to_dict(),"preempt",int(p.iloc[-1]-p.iloc[0]))
    print("p50 %.3f p99 %.3f"%(q.ttft.quantile(.5),q.ttft.quantile(.99)))
E
ssh -i $HOME/.ssh/id_ed25519_vllm -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=8 chalshik@192.168.3.249 'tail -n 2 ~/control_r3_rerun.console.log | cut -c1-120; tmux ls 2>&1 | cut -c1-50; nvidia-smi --query-gpu=temperature.gpu,memory.used --format=csv,noheader'