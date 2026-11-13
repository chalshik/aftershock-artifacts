"""K5 lead times (analysis/k5.py, draft for REG-23) on hand-made runs: no run folder is read."""
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import analysis.k5 as K

END = 1500.0


def fake_run(h=None, u=None, q=None, n=None, ttft=None, kv=None, surge=None, dip=None, name="fake", lam=2.0,
             ttft_ramp=None):
    """A warm server scraped every second for END seconds: 2 requests/s, hit rate 0.84, 1000 recomputed tokens/s,
    nobody waiting, 6 running, 0.2 s to the first token, KV 0.2. Each argument is the time from which that signal
    moves to its cold value (hit 0, 6000 tokens/s recomputed, 5 waiting, 30 running, 3 s, KV 0.95). `surge` is a
    (from, to) pair with 4 requests/s sent; `dip` a (from, to) pair with the hit rate at 0; `ttft_ramp` a (from,
    seconds) pair over which the time to first token rises linearly from 0.2 to 3 s. Every request is planned when
    it is sent."""
    t = np.arange(0.0, END, 1.0)
    inf = math.inf
    cold_h = (t >= (h if h is not None else inf)) | ((t >= dip[0]) & (t < dip[1]) if dip else False)
    cached = np.where(t >= (u if u is not None else inf), 0.0, 5000.0)
    per = np.where(t >= (ttft if ttft is not None else inf), 3.0, 0.2)
    if ttft_ramp:
        per = 0.2 + 2.8 * np.clip((t - ttft_ramp[0]) / ttft_ramp[1], 0.0, 1.0)
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
    reqs["t_planned"] = reqs.t_sent
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
    assert q0["in_alarm_s"]["H"] == 0.0 and q0["scanned_s"] == pytest.approx(END - 540.0)
    q1 = K.quiet(fake_run(dip=(800.0, 860.0)))                        # the hit rate falls for a minute and returns
    assert q1["alarms"]["H"] == 1 and q1["alarms"]["U"] == 0 and 45.0 <= q1["in_alarm_s"]["H"] <= 95.0
    assert K.quiet(fake_run(dip=(800.0, 802.0)))["alarms"]["H"] == 0  # two seconds move a 30 s mean by 0.056 < 0.06
    q2 = K.quiet(fake_run(h=600.0))                                   # the hit rate falls at 600 s and stays down
    assert q2["alarms"]["H"] == 1 and q2["in_alarm_s"]["H"] / q2["scanned_s"] > 0.9    # one onset, nearly all the time


def test_crossings_count_an_onset_once_and_rearm():
    s = pd.DataFrame({"t": np.arange(0.0, 100.0, 5.0), "X": [0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0]})
    assert K.crossings(s, "X", "at_least", 1.0, start=0.0) == [10.0, 55.0]      # the single 1 at 40 s does not hold
    assert K.crossings(s, "X", "at_least", 1.0, start=10.0) == [10.0, 55.0]     # already beyond when the scan starts
    assert K.crossings(s, "X", "at_least", 1.0, start=60.0) == [60.0]           # ... also when it began before the scan
    assert K.crossings(s, "X", "at_least", 1.0, start=0.0, stop=50.0) == [10.0]


def _e(leads, over_queue=None, rel=None, why=None):
    """An event from its leads over latency (L). The leads over Lr and over the queue default to the same. A has an
    onset iff "A" is in `leads`; the lead of X over A is then leads[X] - leads["A"], else +inf (A silent)."""
    oq, rl, has_a = (leads if over_queue is None else over_queue), (leads if rel is None else rel), "A" in leads
    lx = {k: leads.get(k, math.nan) for k in K.WARNERS}
    return {"why": why, "onsets": {"A": 0.0 if has_a else math.nan}, "leads": lx,
            "leads_rel": {k: rl.get(k, math.nan) for k in K.WARNERS},
            "leads_over_queue": {k: oq.get(k, math.nan) for k in K.WARNERS if k != "Q"},
            "lead_over_A": {k: (math.nan if math.isnan(lx[k]) else lx[k] - leads["A"] if has_a else math.inf)
                            for k in K.WARNERS if k != "A"}}


def _q(hours=6.0, lam=2.0, share=0.0, **alarms):
    scanned = hours * 3600.0
    return {"why": None, "lam": lam, "hours": hours, "alarms": {k: alarms.get(k, 0) for k in K.SIGNALS},
            "in_alarm_s": {k: share * scanned for k in K.SIGNALS}, "scanned_s": scanned}


LATE_A = -200.0          # arrivals cross 200 s after latency: H and U beat them by far more than A's 120 s window


def test_judge_labels_reasons_and_bounds():
    five = [_e({"H": 40.0 + i, "U": 35.0, "Q": -5.0, "A": LATE_A}) for i in range(5)]
    j = K.judge(five, [_q()])
    h = j["signals"]["H"]
    assert h["over_latency"]["label"] == "leads" and h["over_queue"]["label"] == "leads" and h["usable"]
    assert h["over_latency"]["above_window"]["k"] == 5 and h["over_latency"]["above_window"]["n"] == 5
    assert h["over_latency"]["above_window"]["cp_lower"] == pytest.approx(0.05 ** 0.2, abs=1e-6)   # 5 of 5: >= 0.55
    assert j["signals"]["Q"]["over_latency"]["label"] == "no_lead" and "over_queue" not in j["signals"]["Q"]
    assert j["signals"]["A"]["over_latency"]["label"] == "no_lead" and "over_arrivals" not in j["signals"]["A"]
    assert j["k5"] == "cache_signal_leads" and j["cache_signals_that_lead"] == ["H", "U"] and h["reasons"] == []
    four = K.judge(five[:4], [_q()])                                                  # four events are not five
    assert four["signals"]["H"]["over_latency"]["label"] == "too_few" and four["k5"] == "too_few_events"
    assert four["first_reason"] == {"H": "too_few_events", "U": "too_few_events"}
    few = K.judge([_e({"H": -50.0, "U": -50.0, "A": LATE_A})] * 3, [_q()])            # too few is checked first
    assert few["signals"]["H"]["over_latency"]["label"] == "too_few" and few["k5"] == "too_few_events"
    mixed = K.judge(five[:4] + [_e({"H": 12.0, "U": 35.0, "A": LATE_A})], [_q()])     # one lead inside the window
    assert mixed["signals"]["H"]["over_latency"]["label"] == "mixed" and mixed["first_reason"]["H"] == "latency:mixed"
    inside = K.judge([_e({"H": 12.0 + i, "U": 8.0, "A": LATE_A}) for i in range(5)], [_q()])
    assert inside["signals"]["H"]["over_latency"]["label"] == "within_window" and inside["k5"] == "no_usable_cache_lead"
    assert inside["signals"]["H"]["over_latency"]["k_positive"] == 5 and inside["signals"]["H"]["over_latency"]["k_above_window"] == 0
    assert inside["first_reason"] == {"H": "latency:within_window", "U": "latency:within_window"}
    queue_first = K.judge([_e({"H": 40.0, "U": 35.0, "A": LATE_A}, over_queue={"H": -8.0, "U": -20.0})] * 5, [_q()])
    assert queue_first["signals"]["H"]["reasons"] == ["queue:no_lead"] and queue_first["k5"] == "no_usable_cache_lead"
    assert K.judge(five + [_e({}, why="no reference")], [_q()])["n_events"] == 5


def test_false_alarms_are_judged_on_their_upper_bound_and_their_share_of_time():
    five = [_e({"H": 40.0, "U": 35.0, "A": LATE_A})] * 5
    one = K.judge(five, [_q(hours=6.0, H=1)])                     # 1 in 6 h: upper bound 0.79 per hour
    assert one["signals"]["H"]["false_alarms"]["per_hour_upper"] == pytest.approx(4.744 / 6.0, abs=0.01)
    assert one["signals"]["H"]["usable"] and one["k5"] == "cache_signal_leads"
    two = K.judge(five, [_q(hours=6.0, H=2, U=2)])                # 0.33 per hour, but the bound is 1.05
    assert two["signals"]["H"]["false_alarms"]["per_hour"] < 1.0 and two["signals"]["H"]["reasons"] == ["false_alarms"]
    assert two["k5"] == "no_usable_cache_lead"
    held = K.judge(five, [_q(share=0.06)])                        # no new onset, but an alarm that lasts
    assert held["signals"]["H"]["reasons"] == ["alarm_share"] and not held["signals"]["H"]["usable"]
    for qs in ([], [_q(hours=2.0)]):                              # 0 alarms in 2 h still allow 1.5 per hour
        assert K.judge(five, qs)["first_reason"]["H"] == "too_few_quiet_hours"
        assert K.judge(five, qs)["k5"] == "no_usable_cache_lead"
    by = K.judge(five, [_q(hours=1.0, lam=2.0, H=1), _q(hours=5.0, lam=2.4)])["false_alarms_by_load"]
    assert by["2.0"]["runs"] == 1 and by["2.0"]["H"]["alarms"] == 1 and by["2.4"]["H"]["alarms"] == 0
    assert by["2.4"]["H"]["per_hour_upper"] == pytest.approx(2.996 / 5.0, abs=0.01)


def test_arrivals_are_compared_per_event_and_against_their_own_window():
    """Rule F round 1, CA2: H leads latency by 100 s, 100, 100, 40, 40; A only in the last two, by 90 s. Unpaired
    medians (100 against 90) would pass H; paired, A came first wherever it moved, and A moved in two events only."""
    two_a = [_e({"H": 100.0, "U": 100.0})] * 3 + [_e({"H": 40.0, "U": 40.0, "A": 90.0})] * 2
    j = K.judge(two_a, [_q()])
    assert j["n_events_with_A_onset"] == 2 and not j["arrivals_compared"]
    assert j["signals"]["H"]["reasons"][-1:] == ["arrivals_not_compared"] and j["k5"] == "no_usable_cache_lead"
    seven = [_e({"H": 100.0, "U": 100.0, "A": 90.0})] * 5 + [_e({"H": 100.0, "U": 100.0})] * 2
    j = K.judge(seven, [_q()])
    assert j["arrivals_compared"] and j["signals"]["H"]["over_arrivals"]["k_a_silent"] == 2
    assert j["signals"]["H"]["over_arrivals"]["median_lead_s"] == pytest.approx(10.0)
    assert j["signals"]["H"]["reasons"] == ["arrivals_first"]       # 10 s is inside A's 120 s window
    early = K.judge([_e({"H": 100.0, "U": 100.0, "A": -30.0})] * 5, [_q()])
    assert early["signals"]["H"]["over_arrivals"]["median_lead_s"] == pytest.approx(130.0) and early["k5"] == "cache_signal_leads"


def test_a_lead_over_the_slo_alone_is_labelled_as_such():
    slo = K.judge([_e({"H": 40.0, "U": 35.0, "A": LATE_A}, rel={"H": 5.0, "U": 3.0})] * 5, [_q()])
    assert slo["signals"]["H"]["reasons"] == ["slo_only"] and slo["k5"] == "leads_slo_only"
    assert slo["cache_signals_that_lead"] == []


def test_latency_that_ramps_from_the_cache_step_is_caught_by_the_relative_level():
    """Rule F round 1, CA1: H and U step at 900 s; latency starts to rise at the same instant and reaches 3 s 300 s
    later; the queue steps at 1000 s. Against the 1.0 s SLO, H leads by about 100 s; against latency's own first
    move it does not lead."""
    e = K.event(fake_run(h=900.0, u=900.0, q=1000.0, ttft_ramp=(900.0, 300.0), kv=950.0))
    assert e["why"] is None and 900 <= e["onsets"]["H"] <= 910 and 990 <= e["onsets"]["L"] <= 1010
    assert 905 <= e["onsets"]["Lr"] <= 930 and e["levels"]["Lr"] == pytest.approx(0.3)
    assert e["leads"]["H"] > 80 and e["leads_rel"]["H"] < K.K5["min_lead_s"] and e["leads_over_queue"]["H"] > 80
    j = K.judge([e] * 5, [_q()])
    assert j["signals"]["H"]["over_latency"]["label"] == "leads" and "slo_only" in j["signals"]["H"]["reasons"]
    assert j["k5"] == "no_usable_cache_lead"


def test_reported_flags_scan_start_recovery_and_planned_arrivals():
    e = K.event(fake_run(h=900.0, q=700.0, ttft=960.0, kv=950.0))
    assert e["at_scan_start"]["Q"] and e["onsets"]["Q"] == min(t for t in np.arange(30.0, END, 5.0) if t >= e["ref"][1])
    assert not e["at_scan_start"]["H"] and e["beyond_at_kv"]["H"] and e["beyond_at_kv"]["Q"]
    d = K.event(fake_run(dip=(800.0, 860.0), ttft=960.0, kv=950.0))  # H falls for a minute and returns before the pool fills
    assert 800 <= d["onsets"]["H"] <= 810 and not d["beyond_at_kv"]["H"]
    r = fake_run(h=900.0, ttft=960.0, kv=950.0, surge=(700.0, 900.0))
    extra = (r["requests"].t_sent % 0.5 == 0.25) & (r["requests"].t_sent >= 700.0)
    r["requests"].loc[extra, "t_planned"] = 700.0 + (r["requests"].t_sent[extra] - 700.0) / 2.0   # planned in 100 s
    s = K.event(r)
    assert s["a_peak_sent"] == pytest.approx(4.0, abs=0.01) and s["a_peak_planned"] > 5.0
    r["requests"] = r["requests"].drop(columns=["t_planned"])
    assert math.isnan(K.event(r)["a_peak_planned"])


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
    assert t["judged"]["k5"] == "too_few_events"


def test_signals_that_step_together_do_not_lead():
    """Hit rate, recomputed work, queue and latency all step at 900 s. Their trailing means cross their levels a few
    seconds apart (a level near the reference mean is crossed sooner): those gaps stay inside the window and are not
    leads."""
    e = K.event(fake_run(h=900.0, u=900.0, q=900.0, n=900.0, ttft=900.0, kv=940.0))
    assert e["why"] is None and all(900 <= e["onsets"][k] <= 925 for k in ("H", "U", "Q", "N", "L"))
    assert all(abs(e["leads"][k]) < K.K5["min_lead_s"] for k in ("H", "U", "Q", "N"))
    j = K.judge([e] * 5, [_q()])
    assert j["signals"]["H"]["over_latency"]["label"] in ("within_window", "no_lead") and j["k5"] == "no_usable_cache_lead"
