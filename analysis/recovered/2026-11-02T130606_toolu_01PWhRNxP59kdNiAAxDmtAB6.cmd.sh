cd /Users/chalshik/Projects/aftershock-artifacts; rsync -a -e "ssh -i $HOME/.ssh/id_ed25519_vllm -o IdentitiesOnly=yes -o BatchMode=yes" --include='*wipe_preempt_r3.5*/***' --exclude='*' chalshik@192.168.3.249:aftershock-artifacts/runs/ runs/; echo rsync=$?; uv run python - <<'E'
import glob
from analysis.load import load_run,verdict
c=load_run(sorted(glob.glob("runs/*stage2_control_cap_r3.5"))[0]);print("control",c["dir"].name,verdict(c)["verdict"])
for d in sorted(glob.glob("runs/*wipe_preempt_r3.5_s*")):
    r=load_run(d);ck=r["checks"];v=verdict(r);m=r["metrics"];p=m["vllm:num_preemptions_total"]
    print(d.split("/")[1],"valid",ck["valid"],ck["failed"],"| VERDICT",v["verdict"],"| base hit %.3f end hit %.3f prev %.3f | end pf %.3f q %.3f kv %.3f n %.1f | preempt %d"%(v["baseline"]["hit"],v["end"]["hit"],v["previous"]["hit"],v["end"]["pf"],v["end"]["q"],v["end"]["kv"],v["end"]["n"],int(p.iloc[-1]-p.iloc[0])))
E