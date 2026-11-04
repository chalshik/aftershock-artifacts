cd /Users/chalshik/Projects/aftershock-artifacts; cat > configs/gap5_base.yaml <<'EOF'
# Shorter turn gaps: mean 5 s instead of 20 s, default KV pool, cap stated. Everything else as Stage 1. See docs/decisions.md.
extends: base.yaml
name: gap5_base
server:
  args:
    --max-num-seqs: 256
workload:
  sessions:
    turn_gap_s: {dist: exponential, mean: 5.0}
EOF
cat > configs/sweep_gap5_pc_on.yaml <<'EOF'
# Capacity with prefix caching on, 5 s turn gaps: mu_warm. Same run shape and rule as Stage 1.
extends: gap5_base.yaml
name: sweep_gap5_pc_on
sweep:
  rates: [2, 3, 3.5, 4, 4.5, 5, 6, 7]
EOF
cat > configs/sweep_gap5_pc_off.yaml <<'EOF'
# Capacity with prefix caching off, 5 s turn gaps: mu_off. Same run shape and rule as Stage 1.
extends: gap5_base.yaml
name: sweep_gap5_pc_off
server:
  args:
    --enable-prefix-caching: null
    --no-enable-prefix-caching: true
sweep:
  rates: [2, 2.5, 3, 3.5]
EOF
uv run python -c "
from harness.run import load_config,expand,server_cmd
from harness import workload
from pathlib import Path
import numpy as np
for n in ('sweep_gap5_pc_on','sweep_gap5_pc_off'):
    c=load_config(Path(f'configs/{n}.yaml'));rs=expand(c);r=rs[0]
    s,_=workload.build_schedule(r['workload'],r['seed']);sm=workload.summary(s)
    print(n,[x['workload']['rate'] for x in rs],r['workload']['duration_s'],r['workload']['warmup_s'],r['workload']['sessions']['turn_gap_s'],'| gap mean %.1f, turns/session %.2f, span p50 of session %.0f s'%(sm['turn_gap_s_mean'],sm['turns_per_session_mean'],(s.groupby('session_id').t_planned.max()-s.groupby('session_id').t_planned.min()).median()))
    print('  ',' '.join(server_cmd(r)))
# active-session working set W at lambda=3, 5 s vs 20 s gaps
for gap in (20.0,5.0):
    c=load_config(Path('configs/gap5_base.yaml'));wl=dict(c['workload']);wl['rate']=3.0;wl['duration_s']=2400;wl['sessions']=dict(wl['sessions'],turn_gap_s={'dist':'exponential','mean':gap})
    s,_=workload.build_schedule(wl,1);g=s.groupby('session_id');a=g.t_planned.min();b=g.t_planned.max();res=[]
    for t in np.arange(600,2400,10.):
        last=s[s.t_planned<=t].groupby('session_id').tail(1).set_index('session_id');live=last[(a.reindex(last.index)<=t)&(b.reindex(last.index)>=t)];res.append(live.prompt_len.sum())
    print('gap %.0f s: W at lambda 3 mean %.0f tokens (%.2f of 96,656)'%(gap,np.mean(res),np.mean(res)/96656))
"