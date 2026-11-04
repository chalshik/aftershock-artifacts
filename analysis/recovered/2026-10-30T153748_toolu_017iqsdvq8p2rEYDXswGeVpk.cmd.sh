uv run python - <<'EOF'
import sys
sys.path.insert(0, ".")
from pathlib import Path
import pandas as pd
from analysis.load import load_run, window, rates
for p in sorted(Path("runs").glob("*_sweep_pc_on_r*"), key=lambda p: float(p.name.split("_r")[-1])):
    r = load_run(p); wl = r["cfg"]["workload"]; q = r["requests"]
    lo, hi = wl["warmup_s"], wl["duration_s"]
    tp = ((q.status=="ok") & (q.t_end>=lo) & (q.t_end<hi)).sum()/(hi-lo)
    m = window(rates(r["metrics"]), r["cfg"]).reset_index(drop=True)
    g = (m.index * 3 // len(m))
    hr = m.groupby(g).hit_rate.mean().round(3).tolist(); kv = m.groupby(g).kv_cache_usage_perc.mean().round(3).tolist(); qq = m.groupby(g).num_requests_waiting.mean().round(1).tolist()
    w = window(q, r["cfg"], "t_planned").copy(); tg = ((w.t_planned-lo)*3//(hi-lo)).astype(int)
    tt = w.groupby(tg).ttft.median().round(3).tolist()
    print(f"rate {wl['rate']:>2} completions/s {tp:.3f} ({tp/wl['rate']:.3f} of rate) | thirds: hit {hr} kv {kv} Q {qq} ttft_p50 {tt}")
EOF