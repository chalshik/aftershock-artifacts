"""K5 lead times (analysis/k5.py, draft for REG-23) on hand-made runs: no run folder is read."""
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import analysis.k5 as K

END = 1500.0


def fake_run(h=None, u=None, q=None, n=None, ttft=None, kv=None, surge=None, dip=None, name="fake", lam=2.0):
    """A warm server scraped every second for END seconds: 2 requests/s, hit rate 0.84, 1000 recomputed tokens/s,
    nobody waiting, 6 running, 0.2 s to the first token, KV 0.2. Each argument is the time from which that signal
    moves to its cold value (hit 0, 6000 tokens/s recomputed, 5 waiting, 30 running, 3 s, KV 0.95). `surge` is a
    (from, to) pair with 4 requests/s sent; `dip` a (from, to) pair with the hit rate at 0."""
    t = np.arange(0.0, END, 1.0)
    inf = math.inf
    cold_h = (t >= (h if h is not None else inf)) | ((t >= dip[0]) & (t < dip[1]) if dip else False)
    cached = np.where(t >= (u if u is not None else inf), 0.0, 5000.0)
    per = np.where(t >= (ttft if ttft is not None else inf), 3.0, 0.2)
    m = pd.DataFrame({
        "t": t,
        K.COL["queries"]: np.cumsum(np.full(len(t), 2.0)),
        K.COL["hits"]: np.cumsum(np.where(cold_h, 0.0, 1.68)),
        K.COL["prompt"]: np.cumsum(np.full(len(t), 6000.0)),
        K.COL["cached"]: np.cumsum(cached),
        K.COL["waiting"]: np.where(t >= (q if q is not None else inf), 5.0, 0.0),
        K.COL["running"]: np.where(t >= (n if n is not None else inf), 30.0, 6.0),
        K.COL["ttft_count"]: np.cumsum(np.full(len(t), 2.0)),
        K.COL["ttft_sum"]: np.cumsum(2.0 * per),
        "vllm:kv_cache_usage_perc": np.where(t >= (kv if kv is not None else inf), 0.95, 0.2),
    })
    sent = list(np.arange(0.0, END, 0.5))
    if surge:
        sent += list(np.arange(surge[0], surge[1], 0.5) + 0.25)
    reqs = pd.DataFrame({"t_sent": sorted(sent), "turn": 1, "prompt_tokens_planned": 2432})
    return {"dir": Path(name), "cfg": {"workload": {"rate": lam, "duration_s": END}}, "metrics": m, "requests": reqs}


def test_signals_of_a_steady_warm_server():
    s = K.signals(fake_run())
    w = s[(s.t >= 300) & (s.t < 1200)]
    assert w.H.mean() == pytest.approx(0.84) and w.U.mean() == pytest.approx(1000.0) and w.L.mean() == pytest.approx(0.2)
    assert w.Q.max() == 0.0 and w.N.mean() == pytest.approx(6.0) and w.A.mean() == pytest.approx(2.0, abs=0.01)
    assert math.isnan(s[s.t < 120].A.iloc[0])                      # no arrival rate before its window is full


def test_an_event_gives_each_signals_onset_and_its_lead_over_latency():
    e = K.event(fake_run(h=900.0, u=905.0, n=920.0, q=930.0, ttft=960.0, kv=950.0))
    assert e["why"] is None and 980 <= e["kv_onset"] <= 1010          # a 60 s rolling mean crosses 0.9 after ~57 s
    assert e["ref"] == (240.0, e["kv_onset"] - 240.0)
    on, lead = e["onsets"], e["leads"]
    assert 900 <= on["H"] <= 910 and 905 <= on["U"] <= 925 and 930 <= on["Q"] <= 940 and 925 <= on["N"] <= 945
    assert 960 <= on["L"] <= 975 and math.isnan(on["A"])               # arrivals never surged
    assert lead["H"] > lead["U"] > lead["Q"] > 0 and math.isnan(lead["A"])
    assert e["leads_over_queue"]["H"] > e["leads_over_queue"]["U"] > 0 and "Q" not in e["leads_over_queue"]
    assert e["levels"]["H"] == pytest.approx(0.84 - 0.06) and e["levels"]["L"] == 1.0   # floors, the SDs being 0


def test_a_surge_in_arrivals_is_the_trivial_warning():
    e = K.event(fake_run(h=900.0, ttft=960.0, kv=950.0, surge=(700.0, 900.0)))
    assert 760 <= e["onsets"]["A"] <= 800 and e["leads"]["A"] > e["leads"]["H"] > 0     # 4 req/s over 120 s passes 3.2


def test_runs_that_are_not_events_say_why():
    assert K.event(fake_run())["why"] == "never tipped"
    assert K.event(fake_run(kv=300.0))["why"] == "no reference"       # the pool fills before a reference exists
    r = fake_run(h=900.0, kv=950.0)
    r["metrics"] = r["metrics"].drop(columns=[K.COL["cached"]])
    assert "metrics missing" in K.event(r)["why"]
    r = fake_run(h=900.0, kv=950.0)
    r["metrics"].loc[700:, K.COL["queries"]] -= 500.0                 # a restart: the counter goes down
    assert "goes down" in K.event(r)["why"]


def test_false_alarms_on_a_run_that_never_tipped():
    q0 = K.quiet(fake_run())
    assert q0["why"] is None and q0["hours"] == pytest.approx((END - 540.0) / 3600.0) and sum(q0["alarms"].values()) == 0
    q1 = K.quiet(fake_run(dip=(800.0, 860.0)))                        # the hit rate falls for a minute and returns
    assert q1["alarms"]["H"] == 1 and q1["alarms"]["U"] == 0
    assert K.quiet(fake_run(dip=(800.0, 802.0)))["alarms"]["H"] == 0  # two seconds move a 30 s mean by 0.056 < 0.06


def test_crossings_count_an_onset_once_and_rearm():
    s = pd.DataFrame({"t": np.arange(0.0, 100.0, 5.0), "X": [0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0]})
    assert K.crossings(s, "X", "at_least", 1.0, start=0.0) == [10.0, 55.0]      # the single 1 at 40 s does not hold
    assert K.crossings(s, "X", "at_least", 1.0, start=10.0) == [10.0, 55.0]     # already beyond when the scan starts
    assert K.crossings(s, "X", "at_least", 1.0, start=60.0) == [60.0]           # ... also when it began before the scan
    assert K.crossings(s, "X", "at_least", 1.0, start=0.0, stop=50.0) == [10.0]


def _e(leads, over_queue=None, why=None):
    oq = leads if over_queue is None else over_queue
    return {"why": why, "leads": {k: leads.get(k, math.nan) for k in K.WARNERS},
            "leads_over_queue": {k: oq.get(k, math.nan) for k in K.WARNERS if k != "Q"}}


def _q(hours=1.0, **alarms):
    return {"why": None, "hours": hours, "alarms": {k: alarms.get(k, 0) for k in K.SIGNALS}}


def test_judge_labels_and_the_comparison_with_arrivals():
    five = [_e({"H": 40.0 + i, "U": 20.0, "Q": -5.0}) for i in range(5)]
    j = K.judge(five, [_q()])
    h = j["signals"]["H"]
    assert h["over_latency"]["label"] == "leads" and h["over_queue"]["label"] == "leads" and h["usable"]
    assert j["signals"]["Q"]["over_latency"]["label"] == "no_lead" and "over_queue" not in j["signals"]["Q"]
    assert j["signals"]["A"]["over_latency"]["label"] == "too_few"
    assert j["k5"] == "cache_signal_leads" and j["cache_signals_that_lead"] == ["H", "U"]
    assert K.judge(five[:4], [_q()])["signals"]["H"]["over_latency"]["label"] == "too_few"   # four events are not five
    mixed = five[:4] + [_e({"H": -10.0, "U": 20.0})]
    assert K.judge(mixed, [_q()])["signals"]["H"]["over_latency"]["label"] == "mixed"
    noisy = K.judge(five, [_q(H=2, U=2)])                                             # two false alarms an hour
    assert not noisy["signals"]["H"]["usable"] and noisy["k5"] == "no_usable_cache_lead"
    assert K.judge(five, [])["k5"] == "no_usable_cache_lead"                          # no quiet hours: not usable
    arrivals_first = [_e({"H": 40.0, "U": 20.0, "A": 90.0}) for _ in range(5)]
    assert K.judge(arrivals_first, [_q()])["k5"] == "no_usable_cache_lead"            # watching arrivals warns earlier
    queue_first = [_e({"H": 40.0, "U": 20.0}, over_queue={"H": -8.0, "U": -20.0}) for _ in range(5)]
    jq = K.judge(queue_first, [_q()])                                                 # the queue moved before the cache
    assert jq["signals"]["H"]["over_queue"]["label"] == "no_lead" and jq["k5"] == "no_usable_cache_lead"
    assert K.judge(five + [_e({}, why="no reference")], [_q()])["n_events"] == 5


def test_candidates_need_every_registered_folder_and_drop_invalid_runs(monkeypatch):
    runs = {"a": {**fake_run(name="a"), "checks": {"valid": True}}, "b": {**fake_run(name="b"), "checks": {"valid": False}}}
    monkeypatch.setitem(K.K5, "runs", ("a", "b", "c"))
    monkeypatch.setattr(K, "find_runs", lambda pattern, valid_only=True: [runs[pattern]] if pattern in runs else [])
    with pytest.raises(ValueError, match="c gives 0"):
        K.candidates()
    monkeypatch.setitem(K.K5, "runs", ("a", "b"))
    assert [r["dir"].name for r in K.candidates()] == ["a"]


def test_table_splits_events_from_quiet_runs(monkeypatch):
    runs = [{**fake_run(h=900.0, u=905.0, ttft=960.0, kv=950.0, name="tipped"), "checks": {"valid": True}},
            {**fake_run(name="quiet"), "checks": {"valid": True}}]
    monkeypatch.setattr(K, "candidates", lambda: runs)
    t = K.k5_table()
    assert [e["run"] for e in t["events"]] == ["tipped"] and [x["run"] for x in t["quiet"]] == ["quiet"]
    assert t["judged"]["n_events"] == 1 and t["judged"]["signals"]["H"]["over_latency"]["label"] == "too_few"
    assert t["judged"]["k5"] == "no_usable_cache_lead"
