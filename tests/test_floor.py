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


def test_reg9_is_reg6_with_the_350w_runs_only():
    from fnmatch import fnmatch
    from analysis.floor import REG6, REG9
    assert {k for k in REG9 if REG9.get(k) != REG6.get(k)} == {"runs_pattern", "power_limit_w", "force_close"}
    names = ["20261104-134159_long_pc_off_r3_s0", "20261108-000000_long_pl350_pc_off_r3_s1",
             "20261109-000000_long_pl350fc_pc_off_r3_s1", "20261109-000000_long_pl350fc_pc_off_r3_s10"]
    assert [fnmatch(n, REG6["runs_pattern"]) for n in names] == [True, False, False, False]
    # amended 2026-11-09: only the runs with a new connection per request
    assert [fnmatch(n, REG9["runs_pattern"]) for n in names] == [False, False, True, False]


def test_reg9_table_refuses_a_run_without_a_passed_350w_check(monkeypatch, tmp_path):
    import pytest
    import analysis.load
    from analysis.floor import reg9_table
    base = run(lambda t: 0.0, lambda t: 3.0)

    def fake(checks, expected, force_close=True):
        r = {**base, "dir": tmp_path / "x_long_pl350_pc_off_r3_s0", "checks": {"valid": True, "checks": checks},
             "cfg": {"seed": 0, "loadgen_force_close": force_close,
                     "checks": {"max_scrape_gap_s": 2.0, "expected_power_limit_w": expected}}}
        monkeypatch.setattr(analysis.load, "find_runs", lambda pattern: [r])

    fake([{"name": "power_limit", "passed": True}], 350)
    assert reg9_table().label.tolist() == ["sustainable_no_backlog"]
    r = analysis.load.find_runs("")[0]  # two valid runs for one seed: the registration counts one, so refuse
    monkeypatch.setattr(analysis.load, "find_runs", lambda pattern: [r, {**r, "dir": tmp_path / "y"}])
    with pytest.raises(ValueError, match="more than one"):
        reg9_table()
    for checks, expected in [([], 350), ([{"name": "power_limit", "passed": None}], 350),
                             ([{"name": "power_limit", "passed": True}], 420)]:
        fake(checks, expected)
        with pytest.raises(ValueError):
            reg9_table()
    fake([{"name": "power_limit", "passed": True}], 350, force_close=None)  # amendment: pooled-connection run refused
    with pytest.raises(ValueError, match="new connection"):
        reg9_table()


def test_reg9_seed1_starts_only_after_a_sustainable_seed0(monkeypatch):
    import analysis.floor as f
    for rows, expected in [([], False), ([(0, "sustainable")], True), ([(0, "sustainable_no_backlog")], True),
                           ([(0, "unclear")], False), ([(0, "not_sustainable")], False), ([(0, "unclear_data")], False),
                           ([(1, "sustainable")], False)]:
        monkeypatch.setattr(f, "reg9_table", lambda rows=rows: pd.DataFrame(rows, columns=["seed", "label"]))
        assert f.reg9_seed1_may_start() is expected


def test_reg9_outcome_precedence():
    from analysis.floor import reg9_outcome
    t = lambda *labels: pd.DataFrame({"seed": list(range(len(labels))), "label": list(labels)})
    assert reg9_outcome(t("sustainable", "sustainable_no_backlog")) == "first_edge"
    assert reg9_outcome(t("sustainable_no_backlog", "sustainable")) == "first_edge"
    assert reg9_outcome(t("sustainable", "not_sustainable")) == "not_decided_at_420W"  # a split with not_sustainable
    assert reg9_outcome(t("not_sustainable")) == "not_decided_at_420W"  # seed 1 not started
    assert reg9_outcome(t("sustainable")) == "no_change"  # seed 1 missing: first_edge needs both
    assert reg9_outcome(t("sustainable", "unclear")) == "no_change"
    assert reg9_outcome(t("unclear_data", "sustainable")) == "no_change"
    assert reg9_outcome(pd.DataFrame(columns=["seed", "label"])) == "no_change"


def test_window_heat_reads_only_the_verdict_window(monkeypatch):
    import analysis.load
    from analysis.floor import window_heat
    monkeypatch.setattr(analysis.load, "verdict", lambda run: {"t_start": 900.0, "t_wipe": 900.0})  # a control at 900 s
    g = pd.DataFrame({"t": np.arange(0.0, 3000), "power_limit_w": 420.0,
                      "throttle_reasons": [0x20 if t < 200 or 2500 <= t < 2560 else (0x40 if t == 2900 else 0)
                                           for t in range(3000)]})
    cfg = {"verdict": {"baseline_s": 600, "watch_s": 1500, "control_t_s": 900}}
    h = window_heat({"cfg": cfg, "gpu": g, "trigger": pd.DataFrame(), "metrics": None, "requests": None})
    # control at 900 s: window [300, 2400]; SW thermal before 300 and the HW sample at 2900 lie outside it
    assert (h["a"], h["b"]) == (300, 2400) and h["sw_thermal_frac"] == 0 and h["hw_samples"] == 0
    g.loc[g.t == 1000, "throttle_reasons"] = 0x8
    assert window_heat({"cfg": cfg, "gpu": g, "trigger": pd.DataFrame(), "metrics": None, "requests": None})["hw_samples"] == 1


def test_connect_overhead_counts_only_requests_with_a_new_connection():
    import math
    from pathlib import Path
    import pandas as pd
    from analysis.floor import connect_overhead
    q = pd.DataFrame({"t_sent": [1.0, 2.0, 3.0], "t_connected": [1.001, None, 3.003]})
    r = connect_overhead({"dir": Path("x"), "requests": q})
    assert r["n"] == 3 and r["n_connected"] == 2
    assert abs(r["median_ms"] - 2.0) < 1e-6 and abs(r["max_ms"] - 3.0) < 1e-6
    old = connect_overhead({"dir": Path("y"), "requests": pd.DataFrame({"t_sent": [1.0]})})
    assert old["n_connected"] == 0 and math.isnan(old["median_ms"])
