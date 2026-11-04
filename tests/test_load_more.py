"""analysis/load.py functions that had no tests (audit item N15). Synthetic data only."""
import numpy as np
import pandas as pd
import pytest

from analysis.load import _level, capacity, metrics_wide, percent_fast, rates, verdict
from tests.test_load import VERDICT, wipe_run


def test_metrics_wide_sums_label_sets_drops_buckets_and_skips_failed_scrapes():
    scrapes = [{"t": 0.0, "values": {'vllm:x_total{a="1"}': 2.0, 'vllm:x_total{a="2"}': 3.0, 'vllm:h_bucket{le="1"}': 9.0,
                                     'vllm:h_sum{}': 4.0}},
               {"t": 1.0, "error": "timeout"},
               {"t": 2.0, "values": {'vllm:x_total{a="1"}': 4.0, 'vllm:x_total{a="2"}': 3.0, 'vllm:h_sum{}': 6.0}}]
    m = metrics_wide(scrapes)
    assert list(m.t) == [0.0, 2.0] and list(m["vllm:x_total"]) == [5.0, 7.0]
    assert "vllm:h_bucket" not in m and list(m["vllm:h_sum"]) == [4.0, 6.0]


def test_rates_make_a_counter_decrease_nan_not_zero():
    m = pd.DataFrame({"t": [0.0, 1.0, 2.0, 3.0], "vllm:x_total": [0.0, 10.0, 5.0, 7.0],
                      "vllm:prefix_cache_hits_total": [0.0, 5.0, 5.0, 8.0], "vllm:prefix_cache_queries_total": [0.0, 10.0, 10.0, 14.0],
                      "vllm:prompt_tokens_total": [0.0, 10.0, 10.0, 14.0], "vllm:prompt_tokens_cached_total": [0.0, 5.0, 5.0, 8.0]})
    r = rates(m)
    assert r["vllm:x_rate"].iloc[1] == 10.0 and np.isnan(r["vllm:x_rate"].iloc[2]) and r["vllm:x_rate"].iloc[3] == 2.0
    assert r.hit_rate.iloc[1] == 0.5 and np.isnan(r.hit_rate.iloc[2]) and r.hit_rate.iloc[3] == 0.75  # no queries: NaN
    assert list(r.recomputed_prefill_tok_s.iloc[1:]) == [5.0, 0.0, 1.0]


def test_percent_fast_bins_by_planned_arrival_and_counts_unfinished_as_misses():
    reqs = pd.DataFrame({"t_planned": [0.1, 0.5, 1.2, 1.9], "ttft": [0.2, 2.0, 0.3, np.nan],
                         "status": ["ok", "ok", "ok", "unfinished"]})
    pf = percent_fast(reqs, slo_ttft_s=1.0)
    assert list(pf.t) == [0.0, 1.0] and list(pf.percent_fast) == [0.5, 0.5]


def test_capacity_is_the_highest_rate_passing_both_tests():
    curve = pd.DataFrame({"rate": [1, 2, 3, 4], "throughput": [1.0, 2.0, 2.96, 3.5], "q_slope_per_s": [0, 0, 0.005, 0.5]})
    assert capacity(curve, 0.95, 0.01) == 3
    assert capacity(curve.assign(q_slope_per_s=[0, 0, 0.02, 0.5]), 0.95, 0.01) == 2  # slope fails at 3
    assert np.isnan(capacity(curve.assign(throughput=0.0), 0.95, 0.01))


def test_level_pools_requests_in_a_window():
    run = wipe_run(lambda x: (1.0, 0.6, 0.0))
    lv = _level(run, 300, 900)
    assert lv["pf"] == 1.0 and lv["hit"] == pytest.approx(0.6) and lv["q"] == 0.0 and lv["n"] == 8.0


def test_level_with_no_requests_gives_nan_percent_fast():
    run = wipe_run(lambda x: (1.0, 0.6, 0.0))
    run["requests"] = run["requests"][run["requests"].t_planned < 100]
    assert np.isnan(_level(run, 300, 900)["pf"])


@pytest.mark.xfail(strict=True, reason="approved registered verdict-code change (items 9-10) not yet made: "
                                       "a window with no cache queries gives hit 0.0, not NaN")
def test_level_with_no_queries_gives_nan_hit():
    run = wipe_run(lambda x: (1.0, 0.6, 0.0))
    m = run["metrics"]
    m.loc[(m.t >= 300) & (m.t <= 900), "vllm:prefix_cache_queries_total"] = m.loc[m.t == 300, "vllm:prefix_cache_queries_total"].iloc[0]
    assert np.isnan(_level(run, 300.5, 899.5)["hit"])


@pytest.mark.xfail(strict=True, reason="approved registered verdict-code change (items 9-10) not yet made: "
                                       "an empty window raises instead of giving `unclear`")
def test_verdict_on_an_empty_window_is_unclear():
    run = wipe_run(lambda x: (1.0, 0.6, 0.0))
    run["metrics"] = run["metrics"][run["metrics"].t < 1500]   # stopped early: the end window has no scrapes
    run["requests"] = run["requests"][run["requests"].t_planned < 1500]
    assert verdict(run)["verdict"] == "unclear"


def test_verdict_settings_used_by_the_tests_are_the_registered_ones():
    """Guards the fixture: the thresholds in tests/test_load.py match configs/stage2_cap_base.yaml."""
    from pathlib import Path
    from harness.run import load_config
    v = load_config(Path(__file__).resolve().parent.parent / "configs/stage2_cap_base.yaml")["verdict"]
    assert {k: v[k] for k in VERDICT} == VERDICT
