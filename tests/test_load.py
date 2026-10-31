from pathlib import Path

import pandas as pd

from analysis.load import client_backlog_slope, summarize, whole_run_hit_rate


def test_throughput_counts_completions_inside_the_window():
    reqs = pd.DataFrame({
        "t_planned": [50.0, 150.0, 150.0, 190.0, 190.0],
        "t_end": [110.0, 160.0, 170.0, 250.0, None],  # warm-up arrival counts; drain completion and unfinished do not
        "status": ["ok", "ok", "ok", "ok", "unfinished"],
    })
    reqs["ttft"] = reqs["e2e"] = 1.0
    cfg = {"workload": {"rate": 1, "warmup_s": 100, "duration_s": 200}, "server": {"args": {}}}
    run = {"dir": Path("x"), "cfg": cfg, "requests": reqs, "metrics": pd.DataFrame(), "checks": None}
    assert summarize(run)["throughput"] == 3 / 100


def test_client_backlog_slope_sees_a_growing_backlog():
    cfg = {"workload": {"warmup_s": 0, "duration_s": 100}}
    sent = [float(i) for i in range(100)]
    steady = pd.DataFrame({"t_sent": sent, "t_first_token": [t + 0.1 for t in sent]})
    growing = pd.DataFrame({"t_sent": sent, "t_first_token": [t * 2 for t in sent]})
    assert abs(client_backlog_slope({"cfg": cfg, "requests": steady})) < 0.01
    assert client_backlog_slope({"cfg": cfg, "requests": growing}) > 0.4


def test_whole_run_hit_rate_uses_first_and_last_scrape():
    m = pd.DataFrame({"vllm:prefix_cache_hits_total": [10.0, 99.0, 40.0], "vllm:prefix_cache_queries_total": [20.0, 21.0, 80.0]})
    assert whole_run_hit_rate({"metrics": m}) == 0.5
