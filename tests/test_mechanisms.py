"""analysis/mechanisms.py on synthetic traces only (no run folders)."""
import numpy as np
import pandas as pd
import pytest

from analysis.mechanisms import REG2, classify_dips, episodes

ARGS = {k: REG2[k] for k in REG2 if k != "runs"}


def control(slow_bins=(), arrivals=None, preempt_bins=(), lam=4.0, dur=2400):
    """A 2400 s control at lambda; requests arrive at `arrivals(t)` req/s (default lambda), and are slow in
    `slow_bins` (60 s bins counted from 240 s). Preemptions happen once in each of `preempt_bins`."""
    arrivals = arrivals or (lambda t: lam)
    tp, t = [], 0.0
    while t < dur:
        tp.append(t)
        t += 1.0 / arrivals(t)
    tp = np.array(tp)
    slow = np.zeros(len(tp), bool)
    for b in slow_bins:
        slow |= (tp >= 240 + 60 * b) & (tp < 300 + 60 * b)
    r = pd.DataFrame({"t_planned": tp, "status": "ok", "ttft": np.where(slow, 5.0, 0.1)})
    ts = np.arange(0.0, dur + 1)
    pre = np.zeros(len(ts))
    for b in preempt_bins:
        pre[ts >= 270 + 60 * b] += 1
    m = pd.DataFrame({"t": ts, "vllm:prefix_cache_hits_total": 60.0 * ts, "vllm:prefix_cache_queries_total": 100.0 * ts,
                      "vllm:num_requests_waiting": 0.0, "vllm:num_requests_running": 10.0, "vllm:kv_cache_usage_perc": 0.4,
                      "vllm:num_preemptions_total": pre})
    return {"cfg": {"workload": {"rate": lam, "warmup_s": 240, "duration_s": dur}, "slo": {"ttft_s": 1.0}, "checks": {"max_scrape_gap_s": 2.0}}, "requests": r, "metrics": m, "gpu": pd.DataFrame()}


def test_episodes_merge_short_healthy_gaps():
    b = pd.DataFrame({"pf": [1, 0.5, 1, 0.5, 1, 1, 1, 0.9, 1, 0.1]})
    assert episodes(b, 0.98, merge_gap_bins=0) == [(1, 1), (3, 3), (7, 7), (9, 9)]
    assert episodes(b, 0.98, merge_gap_bins=2) == [(1, 3), (7, 9)]


def test_regular_preempting_dips_without_arrival_link_are_ao_like():
    bins = [3, 8, 13, 18, 23, 28]  # every 300 s, six episodes
    res = classify_dips(control(slow_bins=bins, preempt_bins=bins), **ARGS)
    assert res["n_episodes"] == 6 and res["interval_cv"] == 0 and res["cv_chance"] < 0.05
    assert res["label"] == "ao_like_cycle"


def test_review_trace_a_excess_inside_the_dip_bin_is_arrival_driven():
    """REG-2 review, trace A: the excess lands in the dip bin itself (percent fast is counted by arrival)."""
    hot = [(540, 600), (960, 1020), (1260, 1320), (1800, 1860)]
    arr = lambda t: 5.0 if any(a <= t < b for a, b in hot) else 4.0
    bins = [5, 12, 17, 26]
    res = classify_dips(control(slow_bins=bins, arrivals=arr, preempt_bins=bins), **ARGS)
    assert res["arrival_share"] == 1 and res["label"] == "arrival_driven"


def test_review_trace_b_a_flickering_slump_is_one_episode():
    """REG-2 review, trace B: one slump crossing the limit every other bin."""
    res = classify_dips(control(slow_bins=[10, 12, 14, 16], preempt_bins=[10, 12, 14, 16]), **ARGS)
    assert res["n_episodes"] == 1 and res["label"] == "too_few_episodes"


def test_three_randomish_dips_are_not_a_cycle():
    res = classify_dips(control(slow_bins=[4, 15, 21], preempt_bins=[4, 15, 21]), **ARGS)
    assert res["label"] != "ao_like_cycle"


def test_cv_chance_is_reproducible_and_sensible():
    from analysis.mechanisms import cv_chance
    assert cv_chance(4, 36, 0.0, 2000, 0) == cv_chance(4, 36, 0.0, 2000, 0) < 0.05
    assert cv_chance(4, 36, 10.0, 2000, 0) == 1.0
