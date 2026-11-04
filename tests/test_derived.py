import numpy as np
import pandas as pd

from analysis.derived import cached_share_split, hit_between, overlap_fraction, working_set


def test_working_set_sums_latest_prompt_of_active_sessions():
    sched = pd.DataFrame({"session_id": [0, 0, 1], "t_planned": [0.0, 10.0, 5.0],
                          "prompt_len": [100, 300, 50], "burst": [False, False, False]})
    w = working_set(sched, np.array([0.0, 5.0, 10.0, 11.0]))
    # t=0: session 0 at 100; t=5: + session 1 (its only turn, active at that instant); t=10: session 0 at 300; t=11: none
    assert list(w) == [100, 150, 300, 0]


def test_working_set_ignores_burst_rows():
    sched = pd.DataFrame({"session_id": [0, 1], "t_planned": [0.0, 0.0], "prompt_len": [100, 999], "burst": [False, True]})
    assert list(working_set(sched, np.array([0.0]))) == [100]


def test_hit_between_uses_counter_differences():
    m = pd.DataFrame({"t": [0.0, 10.0, 20.0], "vllm:prefix_cache_hits_total": [0.0, 10.0, 90.0],
                      "vllm:prefix_cache_queries_total": [0.0, 100.0, 200.0]})
    assert hit_between(m, 0, 20) == 0.45
    assert hit_between(m, 10, 20) == 0.8


def _run(rows):
    reqs = pd.DataFrame(rows, columns=["session_id", "turn", "t_planned", "t_sent", "t_first_token", "t_end",
                                       "status", "cached_tokens", "prompt_tokens"])
    return {"requests": reqs, "cfg": {"workload": {"warmup_s": 0, "duration_s": 100}}}


def test_cached_share_split_keys_on_first_token_after_previous_end():
    run = _run([
        (0, 0, 1.0, 1.0, 1.1, 2.0, "ok", 0, 100),
        (0, 1, 1.5, 1.5, 2.5, 3.0, "ok", 50, 100),   # sent before turn 0 ended, served after it: counts as "after"
        (1, 0, 1.0, 1.0, 1.1, 9.0, "ok", 0, 100),
        (1, 1, 2.0, 2.0, 3.0, 4.0, "ok", 10, 100),   # first token before turn 0 ended: not "after"
    ])
    s = cached_share_split(run)
    assert s["all_later"] == 0.3 and s["after_prev_finished"] == 0.5 and s["n_after"] == 1


def test_overlap_fraction_counts_sends_before_previous_first_token():
    run = _run([
        (0, 0, 1.0, 1.0, 2.0, 3.0, "ok", 0, 100),
        (0, 1, 1.5, 1.5, 2.5, 3.5, "ok", 0, 100),    # sent before 2.0: overlaps
        (1, 0, 1.0, 1.0, 1.1, 2.0, "ok", 0, 100),
        (1, 1, 5.0, 5.0, 5.1, 6.0, "ok", 0, 100),
    ])
    assert overlap_fraction(run) == 0.5


def test_hit_between_is_nan_on_a_counter_reset_or_no_queries():
    m = pd.DataFrame({"t": [0.0, 10.0, 20.0], "vllm:prefix_cache_hits_total": [50.0, 10.0, 30.0],
                      "vllm:prefix_cache_queries_total": [100.0, 20.0, 60.0]})
    assert np.isnan(hit_between(m, 0, 20))       # both counters went down at t = 10: a restart
    assert hit_between(m, 10, 20) == 0.5         # after the reset the window is clean
    flat = m.assign(**{"vllm:prefix_cache_queries_total": [5.0, 5.0, 5.0], "vllm:prefix_cache_hits_total": [1.0, 1.0, 1.0]})
    assert np.isnan(hit_between(flat, 0, 20))    # no queries
