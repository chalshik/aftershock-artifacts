"""analysis/margin.py on synthetic traces only (no run folders)."""
import pandas as pd
import pytest

from analysis.margin import post_trigger_margin

SESS = {"system_tokens": 512, "user_tokens": 128}
ARGS = dict(baseline_s=600, cold_hit_drop=0.06, conf=0.95)


def make_run(kind="burst", q_after=50.0, share_after=0.2, done_per_s=4.5, burst_done_until=None, q_gap_at=None):
    """Healthy before t = 1020 (session cached share 0.6, Q 0, 3 completions/s); after it, `share_after`, `q_after`
    and `done_per_s`. Burst requests complete until `burst_done_until` (s after 1020), else none after 1020."""
    t = [float(x) for x in range(0, 1300)]
    qs = [0.0 if x < 1020 else q_after for x in t]
    if q_gap_at is not None:
        qs[int(1020 + q_gap_at)] = 0.0
    m = pd.DataFrame({"t": t, "vllm:prefix_cache_hits_total": [60.0 * x for x in t],
                      "vllm:prefix_cache_queries_total": [100.0 * x for x in t], "vllm:num_requests_waiting": qs,
                      "vllm:num_requests_running": 10.0, "vllm:kv_cache_usage_perc": 0.5,
                      "vllm:num_preemptions_total": [0.0 if x < 1020 else x - 1020 for x in t]})
    ends = [i / 3 for i in range(1, 3 * 1020)] + [1020 + i / done_per_s for i in range(int(done_per_s * 280))]
    r = pd.DataFrame({"t_end": ends, "status": "ok", "turn": 1, "prompt_tokens_planned": 896, "prompt_tokens": 896})
    r["t_first_token"] = r.t_end - 1.0
    r["t_planned"] = r.t_end - 1.5
    r["cached_tokens"] = [896 * (0.6 if e - 1.0 < 1020 else share_after) for e in r.t_end]
    if burst_done_until is not None:
        sel = (r.t_end >= 1020) & (r.t_end < 1020 + burst_done_until)
        r.loc[sel[sel].index[::4], ["turn", "prompt_tokens_planned"]] = [0, 1408]
    cfg = {"workload": {"rate": 3.0, "sessions": SESS}}
    if kind == "burst":
        cfg["trigger"] = {"kind": "burst", "at_s": 900, "duration_s": 120, "prompt_tokens": 1408}
        trig = pd.DataFrame()
    else:
        cfg["trigger"] = {"kind": "cache_wipe", "at_s": 1019}
        trig = pd.DataFrame({"success": [False, True], "t_start": [1019.0, 1019.5], "t_end": [1019.2, 1020.0]})
    return {"cfg": cfg, "metrics": m, "requests": r, "trigger": trig}


def test_a_backlogged_cold_burst_free_span_qualifies():
    (row,) = post_trigger_margin(make_run(), [(0, 60)], **ARGS)
    assert row["c"] == pytest.approx(4.5) and row["c_upper"] > row["c"]
    assert row["share"] == pytest.approx(0.2) and row["share_base"] == pytest.approx(0.6)
    assert row["qualifies"] and row["preemptions"] == pytest.approx(60)


def test_burst_completions_disqualify_a_span_and_do_not_make_it_cold():
    """The review's trace: the server counter would look cold, but the sessions' own share stays warm."""
    (row,) = post_trigger_margin(make_run(share_after=0.6, burst_done_until=60), [(0, 60)], **ARGS)
    assert row["burst_done"] > 0 and not row["burst_free"] and not row["cold"] and not row["qualifies"]


def test_one_empty_scrape_breaks_capacity_limited():
    (row,) = post_trigger_margin(make_run(q_gap_at=30), [(0, 60)], **ARGS)
    assert not row["capacity_limited"] and not row["qualifies"]


def test_wipe_uses_the_first_successful_call_end():
    (row,) = post_trigger_margin(make_run(kind="wipe"), [(0, 60)], **ARGS)
    assert row["c"] == pytest.approx(4.5)


def test_baseline_before_the_first_scrape_is_refused():
    run = make_run()
    run["metrics"] = run["metrics"][run["metrics"].t >= 400].reset_index(drop=True)
    with pytest.raises(ValueError):
        post_trigger_margin(run, [(0, 60)], **ARGS)


def test_indistinguishable_burst_prompt_is_refused():
    run = make_run()
    run["cfg"]["trigger"]["prompt_tokens"] = 640
    with pytest.raises(ValueError):
        post_trigger_margin(run, [(0, 60)], **ARGS)
