import json
import numpy as np
from analysis.load import load_run, summarize, window, rates, RUNS
run = load_run(RUNS / "20261030-181851_long_run")
print("valid", run["checks"]["valid"], "failed", run["checks"]["failed"])
for c in run["checks"]["checks"]:
    print(c["name"], c["passed"], json.dumps(c["detail"], default=str)[:300])
s = summarize(run)
print(json.dumps(s, indent=1, default=str))
rate = run["cfg"]["workload"]["rate"]
print("throughput/lambda", s["throughput"]/rate)
wl = run["cfg"]["workload"]; lo, hi = wl["warmup_s"], wl["duration_s"]; third = (hi-lo)/3
reqs = window(run["requests"], run["cfg"], "t_planned")
m = window(rates(run["metrics"]), run["cfg"])
rows = []
for i in range(3):
    a, b = lo+i*third, lo+(i+1)*third
    r = reqs[(reqs.t_planned>=a)&(reqs.t_planned<b)]
    mm = run["metrics"]; mm = mm[(mm.t>=a)&(mm.t<b)]
    h = (mm["vllm:prefix_cache_hits_total"].iloc[-1]-mm["vllm:prefix_cache_hits_total"].iloc[0])/(mm["vllm:prefix_cache_queries_total"].iloc[-1]-mm["vllm:prefix_cache_queries_total"].iloc[0])
    mw = m[(m.t>=a)&(m.t<b)]
    rows.append((r.ttft.quantile(.5), r.ttft.quantile(.99), mw.hit_rate.mean(), h, mw.num_requests_waiting.max(), mw.kv_cache_usage_perc.max()))
    print(f"third {i+1}: ttft p50 {rows[-1][0]:.4f} p99 {rows[-1][1]:.4f} hit(mean of intervals) {rows[-1][2]:.4f} hit(counter ratio) {rows[-1][3]:.4f} Qmax {rows[-1][4]} KVmax {rows[-1][5]:.3f}")
print("p50 last/middle", rows[2][0]/rows[1][0], "hit drop", rows[1][2]-rows[2][2], "counter hit drop", rows[1][3]-rows[2][3])
tot = run["metrics"]
print({k: tot[k].iloc[-1]-tot[k].iloc[0] for k in tot if "preempt" in k or "request_success" in k})
g = run["gpu"]; w = g[(g.t>=lo)&(g.t<=hi)]; print("temp max", w.temp_c.max(), "unfinished total", (run["requests"].status=="unfinished").sum())
