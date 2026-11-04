"""analysis/floor.py (REG-6) on synthetic inputs only."""
import numpy as np
import pandas as pd

from analysis.floor import backlogged_stretches, sustained_capacity

ARGS = dict(min_waiting=1.0, min_stretch_s=30, min_backlog_s=300, margin=0.05, max_gap_s=2.0)


def run(q_fn, done_fn, rate=3.0, dur=3600):
    """Scrapes every 1 s with waiting q_fn(t). Planned arrivals at `rate` (rows with no completion), and completions
    at done_fn(t) per second (rows with no planned time), so the two rates are set independently."""
    t = np.arange(0.0, dur + 1)
    m = pd.DataFrame({"t": t, "vllm:num_requests_waiting": [q_fn(x) for x in t]})
    ends, x = [], 0.0
    while x < dur:
        ends.append(x)
        x += 1.0 / done_fn(x)
    planned = pd.DataFrame({"t_planned": np.arange(0, dur, 1 / rate), "t_end": np.nan, "status": "planned"})
    done = pd.DataFrame({"t_planned": np.nan, "t_end": ends, "status": "ok"})
    return {"metrics": m, "requests": pd.concat([planned, done], ignore_index=True)}


def test_stretches_keep_only_long_runs():
    m = pd.DataFrame({"t": np.arange(0.0, 200), "vllm:num_requests_waiting": [5.0 if 50 <= x < 120 or 150 <= x < 160 else 0.0 for x in range(200)]})
    assert backlogged_stretches(m, 0, 200, 1.0, 30) == [(50.0, 119.0)]


def test_no_backlog_means_it_kept_up():
    res = sustained_capacity(run(lambda t: 0.0, lambda t: 3.0), 600, 3600, **ARGS)
    assert res["label"] == "sustainable_no_backlog" and abs(res["planned_rate"] - 3.0) < 0.01


def test_a_burst_that_drains_measures_capacity():
    """REG-6 review: a late schedule burst raised the queue, which then drained. Capacity 3.5 in the stretch."""
    q = lambda t: 50.0 if 3000 <= t < 3400 else 0.0
    res = sustained_capacity(run(q, lambda t: 3.5 if 3000 <= t < 3400 else 3.0), 600, 3600, **ARGS)
    assert res["label"] == "sustainable" and abs(res["c_b"] - 3.5) < 0.02


def test_a_saturated_server_below_its_load_is_not_sustainable():
    res = sustained_capacity(run(lambda t: 10.0 + t / 100, lambda t: 2.8), 600, 3600, **ARGS)
    assert res["label"] == "not_sustainable" and res["c_b"] < 3.0


def test_capacity_just_above_the_load_is_unclear():
    res = sustained_capacity(run(lambda t: 20.0, lambda t: 3.06), 600, 3600, **ARGS)
    assert res["label"] == "unclear"


def test_nan_or_gap_gives_unclear_data():
    """REG-6 review: one NaN scrape must not produce a label."""
    assert sustained_capacity(run(lambda t: np.nan if t == 2000 else 0.0, lambda t: 3.0), 600, 3600, **ARGS)["label"] == "unclear_data"
    r = run(lambda t: 0.0, lambda t: 3.0)
    r["metrics"] = r["metrics"][(r["metrics"].t < 2000) | (r["metrics"].t > 2010)]
    assert sustained_capacity(r, 600, 3600, **ARGS)["label"] == "unclear_data"
