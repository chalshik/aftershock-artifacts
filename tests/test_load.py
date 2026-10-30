from pathlib import Path

import pandas as pd

from analysis.load import summarize


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
