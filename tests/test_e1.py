"""analysis/e1.py: E1's blind K3 test (draft). The prediction is model F's replay of E1's and REG-8's configs."""
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


def test_tilt_judge_and_unresolved():
    cl = rows([2, 2.5, 3, 3.5, 4], [1.70] * 5, kbar=[4.3, 4.1, 3.9, 3.7, 3.5])
    ol = rows([2, 2.5, 3, 3.5, 4], [1.68] * 5, kbar=[4.5] * 5)
    t = e1.tilt(cl, ol, "kbar", 2.0)
    assert t["d"] == pytest.approx(-0.4)
    assert e1.judge(t, -0.2) == "tilted"
    assert e1.judge({"d": -0.05, "se": 0.0}, -0.2) == "flat"
    assert e1.judge({"d": -0.18, "se": 0.02}, -0.2) == "unresolved"
    assert e1.judge({"d": 0.05, "se": 0.0}, 0.02) == "tilted" and e1.judge({"d": 0.0, "se": 0.0}, 0.02) == "flat"
    assert e1.judge({"d": math.nan, "se": 0.0}, 0.02) == "nan"


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
