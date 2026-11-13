"""analysis/e1.py: E1's floor rule and its reported tilt. The prediction is model F's replay of E1's and REG-8's
configs. No run folder is read."""
import math

import numpy as np
import pandas as pd
import pytest

from analysis import e1


def rows(rates, thr, kbar=None, kv=None):
    return pd.DataFrame({"rate": rates, "throughput": thr, "planned_rate": [r * 1.05 for r in rates],
                         "kv_mean": kv or [0.95] * len(rates), "kbar": kbar or [4.5] * len(rates)})


def test_fit_recovers_a_line_and_its_se():
    r = rows([2, 2.5, 3, 3.5, 4], [1.70, 1.73, 1.76, 1.79, 1.82])
    f = e1.fit(r, "throughput", 2.0)
    assert f["slope"] == pytest.approx(0.06) and f["se"] == pytest.approx(0.0, abs=1e-12) and f["n"] == 5
    assert e1.fit(r, "throughput", 2.5)["n"] == 4
    assert math.isnan(e1.fit(r, "throughput", 4.0)["slope"])


def test_tilt_over_the_rates_both_sweeps_have():
    cl = rows([2, 2.5, 3, 3.5, 4], [1.70] * 5, kbar=[4.3, 4.1, 3.9, 3.7, 3.5])
    ol = rows([2, 2.5, 3, 3.5, 4], [1.68] * 5, kbar=[4.5] * 5)
    assert e1.tilt(cl, ol, "kbar", 2.0)["d"] == pytest.approx(-0.4)
    t = e1.tilt(cl, ol.iloc[[0, 1, 2]], "kbar", 2.0)          # open loop lacks 3.5 and 4: both fits use 2-3
    assert t["cl"]["n"] == t["ol"]["n"] == 3
    assert not hasattr(e1, "judge")                          # owner 2026-11-12: the tilt is never judged


def test_floor_is_cold_floor_or_the_registered_tail_fallback():
    ok = rows([1.5, 2, 2.5, 3], [1.40, 1.70, 1.72, 1.74], kv=[0.5, 0.9, 0.9, 0.9])
    assert e1.floor(ok)["status"] == "ok" and e1.floor(ok)["lam_sat"] == 2.0
    # 1.5 is full (KV 0.9) but kept up (1.55 >= 0.95 x 1.575): cold_floor says not_monotone; the tail starts at 2.0
    nm = rows([1.5, 2, 2.5, 3], [1.55, 1.70, 1.72, 1.74], kv=[0.9, 0.9, 0.9, 0.9])
    assert e1.saturated(nm)["status"] == "not_monotone"
    f = e1.floor(nm)
    assert f["status"] == "tail_ok" and f["lam_sat"] == 2.0 and f["mu_sat_off"] == pytest.approx(1.72)
    short = rows([1.5, 2, 2.5, 3], [1.40, 1.70, 1.72, 3.1], kv=[0.9, 0.9, 0.9, 0.9])   # top row kept up
    assert e1.floor(short)["status"] == "tail_unsaturated"


def test_onset_is_the_later_of_the_two_sweeps():
    a = rows([1.5, 2, 2.5, 3], [1.4, 1.7, 1.7, 1.7], kv=[0.5, 0.9, 0.9, 0.9])
    b = rows([1.5, 2, 2.5, 3], [1.4, 1.6, 1.7, 1.7], kv=[0.5, 0.6, 0.9, 0.9])
    assert e1.onset(a, b) == 2.5
    assert math.isnan(e1.onset(a, rows([1.5, 2], [1.4, 1.5], kv=[0.5, 0.6])))


def test_replay_tilts_the_closed_loop_mix_and_not_the_open_loop_one():
    cl = e1.replay_rows(e1.E1["configs"]["cl"], 1.681, (0.0, 1.0), 0)
    ol = e1.replay_rows(e1.E1["configs"]["ol"], 1.681, (0.0, 1.0), 0)
    assert list(cl.rate) == list(ol.rate) == [1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    t = e1.tilt(cl, ol, "kbar", 2.0)
    assert t["cl"]["slope"] < -0.3 and abs(t["ol"]["slope"]) < 0.05           # model F: the closed-loop mix shifts
    assert e1.tilt(cl, ol, "throughput", 2.0)["d"] > 0.04
    assert ol[ol.rate >= 2].throughput.mean() == pytest.approx(1.681, rel=0.01)   # open loop saturates at mu


def test_prediction_table():
    p = e1.prediction(seeds=(1, 2))
    assert sorted(p["by_onset"]) == [2.0, 2.5, 3.0]
    k = p["by_onset"][2.0]["kbar"]
    assert k["threshold"] == pytest.approx(min((m["d_F"] for m in k["models"].values()), key=abs) / 2)
    assert k["threshold"] < -0.15 and p["by_onset"][2.0]["throughput"]["threshold"] > 0.015


def test_e1_schedules_equal_reg8_part_b_at_every_rate():
    from harness.workload import build_schedule
    cl, ol = e1._cfgs(e1.E1["configs"]["cl"]), e1._cfgs(e1.E1["configs"]["ol"])
    assert [c["workload"]["rate"] for c in cl] == [c["workload"]["rate"] for c in ol]
    for x, y in zip(cl, ol):
        assert build_schedule(x["workload"], x["seed"], None)[0].equals(build_schedule(y["workload"], y["seed"], None)[0])


def test_floor_status_is_the_only_thing_the_flag_returns(monkeypatch):
    import pandas as pd
    import analysis.e1 as E
    rows = pd.DataFrame({"run": ["a", "b", "c"], "rate": [1.0, 1.5, 2.0], "throughput": [1.0, 1.3, 1.31],
                         "planned_rate": [1.05, 1.6, 2.1], "kv_mean": [0.3, 0.9, 0.95], "pf": [float("nan")] * 3})
    monkeypatch.setattr(E, "sweep_rows", lambda parent: rows)
    monkeypatch.setattr(E, "swept_rates", lambda parent: (1.0, 1.5, 2.0))
    assert E.floor_status("any") == "ok"
    monkeypatch.setattr(E, "sweep_rows", lambda parent: rows.assign(kv_mean=[0.3, 0.4, 0.5]))
    assert E.floor_status("any") == "unsaturated"
    monkeypatch.setattr(E, "sweep_rows", lambda parent: rows.iloc[:0])
    with pytest.raises(RuntimeError):
        E.floor_status("any")                               # nothing to read is an error, not a status


def test_floor_no_rows_and_holes():
    import analysis.e1 as E
    full = rows([1.5, 2.0, 2.5, 3.0, 3.5, 4.0], [1.45, 1.70, 1.72, 1.73, 1.74, 1.75], kv=[0.6, 0.9, 0.95, 0.95, 0.95, 0.95])
    grid = (1.5, 2.0, 2.5, 3.0, 3.5, 4.0)
    f = E.floor(full, grid)
    assert f["status"] == "ok" and f["lam_sat"] == 2.0 and f["n"] == 5
    assert E.floor(full.iloc[:0], grid)["status"] == "no_rows"
    gap = E.floor(full[full.rate != 3.0], grid)             # a swept rate above lam_sat has no valid run
    assert gap["status"] == "holes" and gap["missing_rates"] == [3.0] and math.isnan(gap["mu_sat_off"])
    low = E.floor(full[full.rate != 1.5], grid)             # a hole below lam_sat does not matter
    assert low["status"] == "ok" and low["n"] == 5
    assert E.floor(full[full.rate != 3.0])["status"] == "ok"   # without the swept rates the old behaviour


def test_swept_rates_are_read_from_the_sweeps_own_config():
    import analysis.e1 as E
    assert E.swept_rates("sweep_l1pl350cl_pc_off") == (1.5, 2.0, 2.5, 3.0, 3.5, 4.0)
    assert E.swept_rates("sweep_l1t16pl350cl_pc_off") == (1.0, 1.5, 2.0, 2.5, 3.0)


def test_the_earliest_of_two_valid_runs_at_a_rate_counts():
    import analysis.e1 as E
    r = pd.DataFrame({"run": ["20261114-10_x_r2", "20261114-09_x_r2", "20261114-08_x_r1.5"], "rate": [2.0, 2.0, 1.5],
                      "throughput": [1.7, 1.6, 1.4], "planned_rate": [2.1, 2.1, 1.6], "kv_mean": [0.9, 0.9, 0.5]})
    keep, dropped = E.first_valid(r)
    assert list(keep.run) == ["20261114-08_x_r1.5", "20261114-09_x_r2"] and dropped == ["20261114-10_x_r2"]


def test_the_report_waits_for_reg21s_result(monkeypatch, tmp_path):
    """`report` computes REG-21's statistic on REG-8's runs, which is REG-21's reference."""
    import analysis.e1 as E
    d = tmp_path / "decisions.md"
    d.write_text("## 2026-11-13 · [REG] REG-21 (K3, step B)\n")
    monkeypatch.setattr(E.withheld, "DECISIONS", d)
    with pytest.raises(RuntimeError, match="REG-21"):
        E.report()
