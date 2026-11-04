cd /Users/chalshik/Projects/aftershock-artifacts; date -u; tail -c 300 /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/c075c1a8-132c-4000-a89a-88e64c9c2bfd/tasks/bihr786m0.output; echo; rsync -a -e "ssh -i $HOME/.ssh/id_ed25519_vllm -o IdentitiesOnly=yes -o BatchMode=yes" --include='*burst_kv72k*/***' --include='*wipe_kv72k*/***' --exclude='*' chalshik@192.168.3.249:aftershock-artifacts/runs/ runs/; echo rsync=$?; uv run python -c "
import glob
from analysis.load import load_run,verdict
for d in sorted(glob.glob('runs/*burst_kv72k_r3*'))+sorted(glob.glob('runs/*wipe_kv72k_r3*')):
    r=load_run(d);c=r['checks'];v=verdict(r);g=[x['detail'] for x in c['checks'] if x['name']=='gpu_steady'][0];tr=[x['detail'] for x in c['checks'] if x['name']=='trigger'][0]
    tr=tr.get('wipe',tr) if isinstance(tr,dict) else tr
    print(d.split('/')[1],'valid',c['valid'],c['failed'],'| hw',g['hw_throttle_samples'],'| VERDICT',v['verdict'],'| base pf %.3f hit %.3f | end pf %.3f hit %.3f q %.2f kv %.2f'%(v['baseline']['pf'],v['baseline']['hit'],v['end']['pf'],v['end']['hit'],v['end']['q'],v['end']['kv']))
"; ssh -i $HOME/.ssh/id_ed25519_vllm -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=8 chalshik@192.168.3.249 'tmux ls 2>&1 | cut -c1-40; nvidia-smi --query-gpu=temperature.gpu,memory.used --format=csv,noheader; df -h ~ | tail -1 | cut -c30-'