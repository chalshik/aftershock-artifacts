from pathlib import Path

import pandas as pd

import pytest

from analysis.load import client_backlog_slope, settling_time, summarize, verdict, whole_run_hit_rate


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


def tau_run(never_settles=False):
    """Hit rate 0.8 up to t = 100 and from then on 0.2 for 60 s, then 0.5; or stays at 0.2 until the settled span."""
    t = list(range(0, 401, 10))
    rate = lambda x: 0.8 if x < 100 else (0.2 if x < (300 if never_settles else 160) else 0.5)
    q, hits = [0.0], [0.0]
    for a in t[1:]:
        q.append(q[-1] + 100.0); hits.append(hits[-1] + 100.0 * rate(a - 10))
    m = pd.DataFrame({"t": [float(x) for x in t], "vllm:prefix_cache_hits_total": hits, "vllm:prefix_cache_queries_total": q})
    r = pd.DataFrame({"t_planned": [float(x) for x in range(400)], "ttft": [0.1] * 400})
    cfg = {"tau": {"bin_s": 20, "n_bins": 2, "settled_s": 100, "hit_band": 0.03, "ttft_p50_band_s": 0.02}}
    return {"cfg": cfg, "metrics": m, "requests": r}


def test_settling_time_finds_when_the_level_returns():
    assert settling_time(tau_run(), 100, 400) == 60


def test_settling_time_none_when_it_never_settles_before_the_settled_span():
    assert settling_time(tau_run(never_settles=True), 100, 400) is None


VERDICT = {"control_t_s": 900, "baseline_s": 600, "watch_s": 1500, "end_s": 600, "min_baseline_pf": 0.98,
           "recovered_pf_drop": 0.02, "recovered_hit_drop": 0.06, "recovered_q_excess": 1.0,
           "stuck_pf_drop": 0.10, "stuck_hit_drop": 0.06, "hit_climb": 0.06, "pf_climb": 0.05, "drain_horizon_s": 3600}


def wipe_run(after, base_pf=1.0, wiped=True):
    """Healthy (hit 0.6, Q 0) up to t = 900, then after(x) = (percent fast, hit rate, Q) with x = seconds since 900."""
    level = lambda t: (base_pf, 0.6, 0.0) if t < 900 else after(t - 900)
    t = [float(x) for x in range(0, 2401)]
    hits, q = [0.0], [0.0]
    for a in t[1:]:
        q.append(q[-1] + 100.0); hits.append(hits[-1] + 100.0 * level(a - 1)[1])
    m = pd.DataFrame({"t": t, "vllm:prefix_cache_hits_total": hits, "vllm:prefix_cache_queries_total": q,
                      "vllm:num_requests_waiting": [level(a)[2] for a in t],
                      "vllm:num_requests_running": 8.0, "vllm:kv_cache_usage_perc": 0.2})
    r = pd.DataFrame({"t_planned": t, "status": "ok", "ttft": [0.1 if (i % 100) < level(a)[0] * 100 else 5.0 for i, a in enumerate(t)]})
    trig = pd.DataFrame({"success": [True], "t_end": [900.0]}) if wiped else pd.DataFrame()
    return {"cfg": {"verdict": VERDICT, "slo": {"ttft_s": 1.0}}, "metrics": m, "requests": r, "trigger": trig}


@pytest.mark.parametrize("after, expected", [
    (lambda x: (1.0, 0.6, 0.0), "recovered"),                                   # back to baseline
    (lambda x: (0.99, 0.56, 0.5), "recovered"),                                 # small differences stay inside the limits
    (lambda x: (0.3, 0.1, 50.0), "stuck"),                                      # low and flat
    (lambda x: (0.3, 0.1, 50.0 + x / 10), "stuck"),                             # low with a growing line
    (lambda x: (0.3, 0.2, 500.0 - x / 5), "slow_drain"),                        # the line is shrinking
    (lambda x: (0.2 + x / 3000, 0.1 + x / 5000, 50.0), "slow_drain"),           # percent fast and hit rate both climbing
    (lambda x: (0.3, 0.1 + x / 5000, 50.0), "slow_drain"),                      # only the hit rate is climbing
    (lambda x: (0.3, 0.1 + x / 5000, 50.0 + x / 10), "slow_drain"),             # hit rate climbing while the line still grows
    (lambda x: (0.3 + x / 5000, 0.1, 50.0), "slow_drain"),                      # only percent fast is climbing
    (lambda x: (0.3, 0.1, 500.0 - x / 100), "stuck"),                           # the line shrinks, but would take hours to empty
    (lambda x: (0.3, 0.1 + x / 50000, 50.0), "stuck"),                          # a hit-rate rise inside healthy noise is not a climb
    (lambda x: (0.3, 0.1, 0.0), "stuck"),                                       # low with no line: not a backlog
    (lambda x: (1.0, 0.4, 0.0), "unclear"),                                     # fast, but the hit rate stayed low
    (lambda x: (0.85, 0.6, 0.0), "unclear"),                                    # slower, but the hit rate came back
])
def test_verdict(after, expected):
    assert verdict(wipe_run(after))["verdict"] == expected


def test_verdict_needs_a_healthy_baseline():
    assert verdict(wipe_run(lambda x: (1.0, 0.6, 0.0), base_pf=0.9))["verdict"] == "bad_baseline"


def test_verdict_judges_a_control_at_the_configured_time():
    v = verdict(wipe_run(lambda x: (1.0, 0.6, 0.0), wiped=False))
    assert v["verdict"] == "recovered" and v["t_wipe"] == 900
