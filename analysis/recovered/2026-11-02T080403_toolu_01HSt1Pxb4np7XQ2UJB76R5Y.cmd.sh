cd /Users/chalshik/Projects/aftershock-artifacts; rsync -a -e "ssh -i $HOME/.ssh/id_ed25519_vllm -o IdentitiesOnly=yes -o BatchMode=yes" chalshik@192.168.3.249:aftershock-artifacts/runs/20261102-072216_wipe_preempt_r3_s1 runs/ && uv run python -c "
from analysis.load import load_run,verdict
r=load_run('runs/20261102-072216_wipe_preempt_r3_s1');v=verdict(r)
print(v['verdict']);[print(k,{a:round(b,3) for a,b in v[k].items()}) for k in ('baseline','previous','end')]
m=r['metrics'];p=m['vllm:num_preemptions_total'];print('preempt',int(p.iloc[-1]-p.iloc[0]))
import numpy as np;T=v['t_wipe'];h=m['vllm:prefix_cache_hits_total'];q=m['vllm:prefix_cache_queries_total']
print('hit 0-15s %.3f'%((np.interp(T+15,m.t,h)-np.interp(T,m.t,h))/(np.interp(T+15,m.t,q)-np.interp(T,m.t,q))))"