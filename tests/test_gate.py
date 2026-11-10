"""analysis/gate.py (REG-7) on synthetic inputs only (no run folders). Includes the adversarial review's traces."""
import math
from pathlib import Path

import pandas as pd
import pytest

import analysis.gate as G
from analysis.load import capacity
from tests.test_margin import make_run

SPAN_ARGS = dict(baseline_s=600, cold_hit_drop=0.06, conf=0.95)


def sweep(rates, thr, kv, planned=None):
    return pd.DataFrame({"rate": rates, "throughput": thr, "kv_mean": kv, "planned_rate": planned or rates})


# ---------------------------------------------------------------- cold floor

def test_cold_floor_over_saturated_rows_only():
    f = G.cold_floor(sweep([1, 1.5, 2, 2.5], [1.0, 1.5, 1.7, 1.8], [0.3, 0.6, 0.9, 0.95]), 0.85, 2, 0.95)
    assert f["status"] == "ok" and f["lam_sat"] == 2 and f["n"] == 2 and f["mu_sat_off"] == pytest.approx(1.75)


def test_cold_floor_refuses_rows_that_still_keep_up():
    # Review trace: KV >= 0.85 from 1.5, but 1.5 and 2.0 still keep up; averaging them would pull the floor down.
    f = G.cold_floor(sweep([1.5, 2, 2.5, 3], [1.5, 2.0, 2.4, 2.4], [0.9, 0.9, 0.95, 0.97]), 0.85, 2, 0.95)
    assert f["status"] == "not_monotone" and math.isnan(f["mu_sat_off"])


def test_cold_floor_refuses_a_noisy_low_saturated_row():
    f = G.cold_floor(sweep([1, 1.5, 2, 2.5], [0.9, 1.5, 1.7, 1.8], [0.9, 0.6, 0.9, 0.95]), 0.85, 2, 0.95)
    assert f["status"] == "not_monotone"


def test_cold_floor_states_why_it_is_undefined():
    assert G.cold_floor(sweep([1, 2], [1.0, 1.9], [0.3, 0.5]), 0.85, 2, 0.95)["status"] == "unsaturated"
    assert G.cold_floor(sweep([1, 2], [1.0, 1.7], [0.3, 0.9]), 0.85, 2, 0.95)["status"] == "too_few"
    nan_row = sweep([1, 2, 2.5], [1.0, float("nan"), 1.8], [0.3, 0.9, 0.95])   # a NaN row is dropped, not counted
    assert G.cold_floor(nan_row, 0.85, 2, 0.95)["status"] == "too_few"
    with pytest.raises(ValueError):
        G.cold_floor(sweep([2, 2], [1.7, 1.7], [0.9, 0.9]), 0.85, 2, 0.95)


# ---------------------------------------------------------------- test load

def test_zone_check_rule():
    assert G.zone_check(5.0, 1.7, 0.8, 1.3, 0.5) == 4.0
    assert G.zone_check(4.5, 1.7, 0.8, 1.3, 0.5) == 3.5      # 3.6 rounds down to the grid
    assert G.zone_check(3.0, 2.0, 0.8, 1.3, 0.5) is None     # 2.4 -> 2.0 < 2.6
    assert G.zone_check(float("nan"), 1.7, 0.8, 1.3, 0.5) is None
    assert G.zone_check(5.0, float("nan"), 0.8, 1.3, 0.5) is None


def test_choose_lambda_steps_down_until_the_slo_holds():
    on = pd.DataFrame({"rate": [3, 3.5, 4, 4.5], "pf": [0.999, 0.99, 0.97, 0.9]})
    c = {"warm_frac": 0.8, "floor_mult": 1.3, "step": 0.5, "min_pf": 0.98}
    assert G.choose_lambda(5.0, 1.7, on, c) == 3.5           # 4.0 fails the SLO at its own sweep run
    assert G.choose_lambda(5.0, 2.8, on, c) is None          # 4.0 fails the SLO; 3.5 < 1.3 x 2.8 = 3.64


def test_monotone_capacity_ignores_a_rate_passing_above_a_failing_one():
    curve = pd.DataFrame({"rate": [3, 4, 5], "throughput": [3.0, 3.6, 5.0], "planned_rate": [3, 4, 5], "q_slope_per_s": [0, 0.05, 0]})
    assert capacity(curve, 0.95, 0.01, "planned_rate") == 5
    assert capacity(curve, 0.95, 0.01, "planned_rate", monotone=True) == 3


# ---------------------------------------------------------------- spans

def _with_planned(run, rate, lam=None):
    """Session requests planned at `rate` per second over the whole trace (so λp is known), the configured λ set to
    `lam`. The fixture's own completed requests get a planned time before the trace, so they don't count twice."""
    r = run["requests"].assign(t_planned=-1.0)
    n = int(rate * 1300)
    extra = pd.DataFrame({"t_planned": [i / rate for i in range(n)], "t_end": float("nan"), "status": "unfinished",
                          "turn": 1, "prompt_tokens_planned": 896, "prompt_tokens": 896, "t_first_token": float("nan"),
                          "cached_tokens": 0.0})
    run["requests"] = pd.concat([r, extra], ignore_index=True)
    run["cfg"]["workload"]["rate"] = lam if lam is not None else rate
    return run


def test_a_cold_backlog_completing_below_its_load_holds():
    run = _with_planned(make_run(q_after=50.0, share_after=0.2, done_per_s=2.0), rate=4.0)
    (row,) = G.burst_backlog(run, [(0, 60)], **SPAN_ARGS)
    assert row["qualifies"] and row["c_upper"] < row["lam_p"] and row["holds"]


def test_a_draining_backlog_does_not_hold():
    run = _with_planned(make_run(q_after=50.0, share_after=0.2, done_per_s=4.5), rate=3.0)
    (row,) = G.burst_backlog(run, [(0, 60)], **SPAN_ARGS)
    assert row["qualifies"] and not row["holds"]


def test_review_trace_a_a_local_schedule_rise_does_not_make_a_drain_hold():
    # λ = 3.0, c_b = 3.10: draining. The span's own planned rate is 3.39 (the schedule rises locally).
    run = _with_planned(make_run(q_after=500.0, share_after=0.2, done_per_s=3.10), rate=3.39, lam=3.0)
    (row,) = G.burst_backlog(run, [(0, 300)], **SPAN_ARGS)
    assert row["qualifies"] and row["c_upper"] < row["lam_p"] and not row["holds"]


def test_a_warm_backlog_does_not_hold():
    run = _with_planned(make_run(q_after=50.0, share_after=0.6, done_per_s=2.0), rate=4.0)
    (row,) = G.burst_backlog(run, [(0, 60)], **SPAN_ARGS)
    assert not row["cold"] and not row["holds"]


# ---------------------------------------------------------------- labels

def _fake(seed=1, duration=2580, valid=True, control_t=1080.0, trigger=True):
    cfg = {"seed": seed, "workload": {"duration_s": duration}, "verdict": {"control_t_s": control_t},
           "checks": {"max_scrape_gap_s": 2.0}}
    if trigger:
        cfg["trigger"] = {"at_s": 900, "duration_s": 180}
    return {"dir": Path("x"), "checks": {"valid": valid}, "cfg": cfg}


def _patch(monkeypatch, c, vc, vb, holds, control_backlogged=False, defined=True, control_defined=True):
    monkeypatch.setattr(G, "verdict", lambda run: {"verdict": vc if run is c else vb})
    monkeypatch.setattr(G, "burst_backlog", lambda run, *a: [{"holds": holds, "defined": defined}])
    monkeypatch.setattr(G, "control_backlog", lambda run, spans, gap: [{"backlogged": control_backlogged, "defined": control_defined}])


@pytest.mark.parametrize("vc, vb, holds, cb, want", [
    ("recovered", "recovered", True, False, "pass"),
    ("recovered", "stuck", True, False, "pass"),
    ("recovered", "stuck", False, False, "inconclusive"),  # stuck by the verdict, unconfirmed by a span: not a drain
    ("recovered", "recovered", True, True, "drains"),      # review trace B: the control is backlogged there too
    ("recovered", "slow_drain", False, False, "drains"),
    ("recovered", "unclear", True, False, "inconclusive"),        # review trace C
    ("recovered", "bad_baseline", False, False, "inconclusive"),
    ("unclear", "stuck", True, False, "inconclusive"),             # review trace D
    ("bad_baseline", "stuck", True, False, "control_not_healthy"),
    ("slow_drain", "recovered", True, False, "control_not_healthy"),
])
def test_gate_verdict_labels(monkeypatch, vc, vb, holds, cb, want):
    c, b = _fake(trigger=False), _fake()
    _patch(monkeypatch, c, vc, vb, holds, control_backlogged=cb)
    assert G.gate_verdict(c, b, [(600, 900)], 600, 0.06, 0.99)["label"] == want


def test_undefined_spans_are_inconclusive_not_drains(monkeypatch):
    c, b = _fake(trigger=False), _fake()
    _patch(monkeypatch, c, "recovered", "recovered", False, defined=False)
    assert G.gate_verdict(c, b, [(600, 900)], 600, 0.06, 0.99)["label"] == "inconclusive"
    _patch(monkeypatch, c, "recovered", "recovered", True, control_defined=False)
    assert G.gate_verdict(c, b, [(600, 900)], 600, 0.06, 0.99)["label"] == "inconclusive"


def test_gate_verdict_refuses_invalid_or_unmatched_runs(monkeypatch):
    c = _fake(trigger=False)
    _patch(monkeypatch, c, "recovered", "recovered", False)
    for ctrl, burst in [(_fake(valid=False, trigger=False), _fake()), (_fake(seed=2, trigger=False), _fake()),
                        (_fake(duration=2400, trigger=False), _fake()), (_fake(control_t=900.0, trigger=False), _fake())]:
        with pytest.raises(ValueError):
            G.gate_verdict(ctrl, burst, [], 600, 0.06, 0.99)


# ---------------------------------------------------------------- overlap readout

def test_overlap_share_counts_hits_served_while_the_previous_turn_ran():
    reqs = pd.DataFrame([
        # session, turn, planned, first, end, status, cached, prompt
        (0, 0, 300.0, 300.5, 310.0, "ok", 0, 2176),
        (0, 1, 305.0, 306.0, 315.0, "ok", 2000, 2432),   # first token before turn 0 ended: overlap hit
        (1, 0, 300.0, 300.5, 302.0, "ok", 0, 2176),
        (1, 1, 305.0, 305.5, 312.0, "ok", 1000, 2432),   # previous turn had finished
    ], columns=["session_id", "turn", "t_planned", "t_first_token", "t_end", "status", "cached_tokens", "prompt_tokens"])
    run = {"requests": reqs, "cfg": {"workload": {"warmup_s": 0, "duration_s": 1000}}}
    assert G.overlap_share(run, 300, 400) == pytest.approx(2000 / 3000)
    assert math.isnan(G.overlap_share(run, 500, 600))


def test_reg8_is_reg7_with_the_350w_sweeps_only():
    diff = {k for k in G.REG7.keys() | G.REG8.keys() if G.REG7.get(k) != G.REG8.get(k)}
    assert diff == {"sweep_on", "sweep_off", "power_limit_w", "g1a_top"}   # the last two are new keys, not REG-7 values
    assert (G.REG8["sweep_on"], G.REG8["sweep_off"]) == ("sweep_l1pl350_pc_on", "sweep_l1pl350_pc_off")


def _part_a_run(tmp_path, valid, power_ok, gpu_ok, sw_frac, bits):
    import json
    (tmp_path / "gpu.jsonl").write_text("".join(json.dumps({"t": float(t), "throttle_reasons": bits}) + "\n"
                                                for t in range(0, 900, 10)))
    checks = [{"name": "power_limit", "passed": power_ok, "detail": {}},
              {"name": "gpu_steady", "passed": gpu_ok, "detail": {"sw_thermal_frac": sw_frac}}]
    return {"dir": tmp_path, "checks": {"valid": valid, "checks": checks},
            "cfg": {"checks": {"max_sw_thermal_frac": 0.05}, "workload": {"warmup_s": 240, "duration_s": 900}}}


def test_reg8_part_a_separates_heat_from_other_failures(tmp_path):
    assert G.reg8_part_a(_part_a_run(tmp_path, True, True, True, 0.0, 4)) == "valid"
    assert G.reg8_part_a(_part_a_run(tmp_path, False, True, False, 0.08, 4)) == "heat"       # SW thermal over limit
    assert G.reg8_part_a(_part_a_run(tmp_path, False, True, False, 0.0, 0x40)) == "heat"     # HW thermal bit
    assert G.reg8_part_a(_part_a_run(tmp_path, False, True, False, 0.0, 0x80)) == "rerun"    # HW power brake, or CV
    assert G.reg8_part_a(_part_a_run(tmp_path, False, False, False, 0.08, 4)) == "rerun"     # limit not held (T1)
    assert G.reg8_part_a(_part_a_run(tmp_path, False, False, True, 0.0, 4)) == "rerun"       # limit not held (T2)
    assert G.reg8_part_a({"checks": None}) == "rerun"                                        # stopped run


def test_reg8_gate_verdict_refuses_mismatched_or_420w_pairs(tmp_path):
    def run(rate, limit):
        return {"dir": tmp_path, "cfg": {"checks": {"expected_power_limit_w": limit}, "workload": {"rate": rate}}}
    with pytest.raises(ValueError, match="350 W"):
        G.reg8_gate_verdict(run(3.5, None), run(3.5, 350))
    with pytest.raises(ValueError, match="same λ"):
        G.reg8_gate_verdict(run(3.5, 350), run(3.0, 350))


def test_sweep_rows_of_an_empty_sweep_gives_an_unmeasured_floor():
    rows = G.sweep_rows("no_such_sweep")
    assert len(rows) == 0
    f = G.cold_floor(rows, 0.85, 2, 0.95)
    assert f["status"] != "ok" and math.isnan(f["mu_sat_off"])


def test_reg10_gate_takes_the_latest_valid_pair_and_splits_inconclusive(monkeypatch, tmp_path):
    import pytest
    import analysis.gate as g
    import analysis.load
    lam = g.REG10["lam"]
    mk = lambda name, rate=lam, fc=True: {"dir": tmp_path / name,
                                          "cfg": {"workload": {"rate": rate, "duration_s": 2580}, "loadgen_force_close": fc,
                                                  "checks": {"max_scrape_gap_s": 2.0}}}
    verdict = {"label": "drains", "burst_verdict": "slow_drain", "control_verdict": "recovered"}
    monkeypatch.setattr(g, "reg8_gate_verdict", lambda c, b: {**verdict, "pair": (c["dir"].name, b["dir"].name)})
    monkeypatch.setattr(g, "burst_end", lambda run: 1080.0)
    monkeypatch.setattr(g, "overlap_share", lambda run, a, b: (a, b))
    monkeypatch.setattr(g, "secondary_cb", lambda run, gap: {})
    monkeypatch.setattr(g, "queued_miss_share", lambda run, spans: [])
    monkeypatch.setattr(g, "span_clock", lambda run, spans, base: {})

    def runs(control, burst):
        monkeypatch.setattr(analysis.load, "find_runs", lambda p: control if "control" in p else burst)

    runs([mk("20261108-1_c")], [mk("20261108-2_b")])
    res = g.reg10_gate()
    assert res["outcome"] == "drains" and res["overlap_share"] == (1080.0, 2580)
    runs([mk("20261108-3_c"), mk("20261108-1_c")], [mk("20261108-2_b"), mk("20261108-4_b")])  # after a rerun
    assert g.reg10_gate()["pair"] == ("20261108-3_c", "20261108-4_b")
    for bv, cv, out in [("stuck", "recovered", "stuck_unconfirmed"), ("unclear", "recovered", "inconclusive"),
                        ("stuck", "unclear", "inconclusive")]:
        verdict.update(label="inconclusive", burst_verdict=bv, control_verdict=cv)
        assert g.reg10_gate()["outcome"] == out
    for control, burst in [([], [mk("b")]), ([mk("c")], [mk("b", 9.0)]), ([mk("c", fc=None)], [mk("b")])]:
        runs(control, burst)
        with pytest.raises(ValueError):
            g.reg10_gate()


def test_queued_miss_share_counts_cold_turns_whose_previous_turn_had_not_started(monkeypatch):
    import analysis.gate as g
    monkeypatch.setattr(g, "burst_end", lambda run: 0.0)
    q = pd.DataFrame({"status": "ok", "t_first_token": [10.0, 20.0, 30.0, 40.0], "cached_tokens": [0, 0, 0, 500],
                      "t_planned": [5.0, 15.0, 25.0, 35.0], "prev_first": [8.0, 12.0, None, 1.0]})
    monkeypatch.setattr(g, "_later_turns", lambda run: q)
    # cold turns: rows 0-2; previous not started at arrival: row 0 (8 > 5) and row 2 (none); row 3 is warm
    assert g.queued_miss_share({}, [(0, 100)]) == [2 / 3]
    assert math.isnan(g.queued_miss_share({}, [(100, 200)])[0])


def test_reg10_lambda_is_reg8s_warm_margin_and_above_its_floor_margin():
    import analysis.gate as g
    # DERIVED in REG-10 from REG-8's μ_warm 3.0 and μ_sat,off 1.681: λ = 0.8 μ_warm, ≥ 1.3 μ_sat,off; REG-8's 0.5 grid has none
    assert abs(g.REG10["lam"] - g.REG8["warm_frac"] * 3.0) < 1e-9 and g.REG10["lam"] >= g.REG8["floor_mult"] * 1.681
    assert g.zone_check(3.0, 1.681, g.REG8["warm_frac"], g.REG8["floor_mult"], g.REG8["step"]) is None
    assert g.REG10["control"].endswith("_r2.4") and g.REG10["burst"].endswith("_r2.4_s1")


def test_reg11_is_reg10_with_closed_loop_and_refuses_an_open_loop_pair(monkeypatch, tmp_path):
    import fnmatch
    import pytest
    import analysis.gate as g
    import analysis.load
    assert {k: v for k, v in g.REG11.items() if k not in ("control", "burst", "closed_loop", "comparable_frac", "reference_run")} == \
        {k: v for k, v in g.REG10.items() if k not in ("control", "burst")}
    assert g.REG11["closed_loop"] is True
    # neither registration's patterns match the other's run names
    for a, b in [("REG10", "REG11"), ("REG11", "REG10")]:
        for key, name in [("control", "stage2_control_l1pl350{}_r2.4"), ("burst", "burst_l1pl350{}_r2.4_s1")]:
            own = name.format("cl" if b == "REG11" else "")
            assert not fnmatch.fnmatch("20261110-000000_" + own, getattr(g, a)[key])
    mk = lambda name, cl: {"dir": tmp_path / name, "cfg": {"workload": {"rate": 2.4, "duration_s": 2580,
                           "sessions": {"closed_loop": cl}}, "loadgen_force_close": True, "checks": {"max_scrape_gap_s": 2.0}}}
    monkeypatch.setattr(g, "reg8_gate_verdict", lambda c, b: {"label": "drains", "burst_verdict": "recovered",
                                                               "control_verdict": "recovered"})
    for f in ("overlap_share", "secondary_cb", "queued_miss_share", "span_clock", "release_delay",
              "release_delay_baseline", "shock_size", "turn0_share", "unreleased"):
        monkeypatch.setattr(g, f, lambda *a: "x")
    monkeypatch.setattr(g, "burst_end", lambda run: 1080.0)
    pairs = {"ok": ([mk("c", True)], [mk("b", True)]), "open": ([mk("c", None)], [mk("b", True)])}
    for case, (c, b) in pairs.items():
        monkeypatch.setattr(analysis.load, "find_runs", lambda p, c=c, b=b: c if "control" in p else b)
        if case == "ok":
            monkeypatch.setattr(g, "reg11_reference", lambda: {"outstanding": 10, "backlog_s": 100.0})
            monkeypatch.setattr(g, "shock_size", lambda run: {"outstanding": 5, "backlog_s": 49.0})
            res = g.reg11_gate()
            assert res["release_delay"] == "x" and res["shock_comparable"] is False   # 49 < 0.5 x 100
            monkeypatch.setattr(g, "shock_size", lambda run: {"outstanding": 5, "backlog_s": 50.0})
            assert g.reg11_gate()["shock_comparable"] is True
            monkeypatch.setattr(g, "shock_size", lambda run: "x")
        else:
            with pytest.raises(ValueError):
                g.reg11_gate()
    monkeypatch.setattr(analysis.load, "find_runs", lambda p: [mk("c", True)] if "control" in p else [mk("b", True)])
    with pytest.raises(ValueError):  # REG-10 refuses a closed-loop pair
        g.reg10_gate()


def test_release_delay_is_the_median_lag_of_later_turns_per_span(monkeypatch):
    import analysis.gate as g
    monkeypatch.setattr(g, "burst_end", lambda run: 0.0)
    q = pd.DataFrame({"turn": [0, 1, 1, 2, 1], "t_planned": [0.0, 10.0, 20.0, 30.0, 150.0],
                      "t_released": [0.0, 12.0, 26.0, 40.0, None]})
    assert g.release_delay({"requests": q}, [(0, 100), (100, 200)])[0] == 6.0
    assert math.isnan(g.release_delay({"requests": q}, [(0, 100), (100, 200)])[1])
    assert all(math.isnan(x) for x in g.release_delay({"requests": q.drop(columns="t_released")}, [(0, 1)]))


def test_reg11_readouts_shock_size_turn0_share_unreleased_and_queued_miss_against_release(monkeypatch):
    import analysis.gate as g
    monkeypatch.setattr(g, "burst_end", lambda run: 100.0)
    monkeypatch.setattr(g, "secondary_cb", lambda run, gap: {"backlog_s": 42.0})
    nan = float("nan")
    q = pd.DataFrame({
        "turn":                 [0,    1,     1,     2,    0,     1],
        "prompt_tokens_planned": [10,   20,    20,    30,   99,    20],   # row 4 is a burst request (99 tokens)
        "t_planned":            [50.0, 90.0,  95.0,  700., 95.0,  800.],
        "t_released":           [50.0, 98.0,  101.0, nan,  nan,   850.],
        "t_sent":               [50.0, 98.0,  101.0, nan,  95.0,  850.],
        "t_end":                [60.0, 150.0, 160.0, nan,  120.0, 900.],
        "status":               ["ok", "ok",  "ok",  "unfinished", "ok", "ok"]})
    run = {"requests": q, "cfg": {"trigger": {"kind": "burst", "prompt_tokens": 99, "at_s": 0},
                                  "checks": {"max_scrape_gap_s": 2.0}}}
    # due by 100 and not ended by 100: row 1 only (row 2 released at 101, row 4 is the burst)
    assert g.shock_size(run) == {"outstanding": 1, "backlog_s": 42.0}
    assert g.unreleased(run, [(500, 700), (0, 100)]) == [1, 0]   # row 3, planned at 700 = 100 + 600
    assert g.turn0_share(run, [(-100, 0), (0, 100)]) == [1.0, 0.0]
    w = pd.DataFrame({"status": "ok", "t_first_token": [150.0], "cached_tokens": [0], "t_planned": [90.0],
                      "t_released": [140.0], "prev_first": [120.0]})
    monkeypatch.setattr(g, "_later_turns", lambda run: w)
    assert g.queued_miss_share({}, [(0, 100)]) == [0.0]          # previous started before release: not queued
    assert g.queued_miss_share({}, [(0, 100)]) != [1.0]


def test_reg12_counts_stuck_only_with_a_recovered_control_and_checks_seeds(monkeypatch, tmp_path):
    import fnmatch
    import pytest
    import analysis.gate as g
    import analysis.load
    from analysis.stats import cp_upper
    assert g.REG12["closed_loop"] is True and g.REG12["lam"] == g.REG11["lam"] and g.REG12["seeds"] == (2, 3, 4, 5, 6)
    for s in g.REG12["seeds"]:  # REG-11's seed-1 pair is never picked up, and seeds do not cross
        spec = g.reg12_spec(s)
        assert not fnmatch.fnmatch("20261109-042828_burst_l1pl350cl_r2.4_s1", spec["burst"])
        assert not fnmatch.fnmatch("20261109-034255_stage2_control_l1pl350cl_r2.4", spec["control"])
        assert not fnmatch.fnmatch(f"20261110-000000_burst_l1pl350cl_r2.4_s{s}6", spec["burst"])
        assert fnmatch.fnmatch(f"20261110-000000_stage2_control_l1pl350cl_r2.4_s{s}", spec["control"])
    verdicts = {2: ("recovered", "stuck", "pass"), 3: ("recovered", "stuck", "inconclusive"),
                4: ("unclear", "stuck", "pass"), 5: ("recovered", "recovered", "drains"), 6: ("recovered", "stuck", "pass")}
    seed_of = lambda p: int(p.rsplit("_s", 1)[1])
    mk = lambda seed: [{"dir": tmp_path / f"x_s{seed}", "cfg": {"seed": seed}}]
    monkeypatch.setattr(analysis.load, "find_runs", lambda p: mk(seed_of(p)))
    monkeypatch.setattr(g, "end_window", lambda run: {})
    monkeypatch.setattr(g, "reg10_gate", lambda spec: dict(zip(("control_verdict", "burst_verdict", "label"),
                                                               verdicts[seed_of(spec["burst"])]), runs=[]))
    t = g.reg12_table()
    assert (t["k"], t["n"], t["k_pass"], t["n_control_recovered"]) == (3, 5, 2, 4)   # seed 4: in n, not in k
    assert t["outcome"] == "supports" and t["cp_upper"] == cp_upper(3, 5, 0.95)
    assert [r["stuck"] for r in t["rows"]] == [True, True, False, False, True]
    assert g.reg12_table((2, 5))["outcome"] == "some"
    assert g.reg12_table((5,))["outcome"] == "none"
    assert g.reg12_table((4, 5))["outcome"] == "none"            # one control not recovered: not yet the first branch
    verdicts[5] = ("unclear", "recovered", "drains")
    assert g.reg12_table()["outcome"] == "controls_not_healthy"  # two controls not recovered: first, even with k = 3
    assert g.reg12_outcome(5, 3, 0) == "controls_not_healthy" and g.reg12_outcome(5, 4, 0) == "none"
    monkeypatch.setattr(analysis.load, "find_runs", lambda p: mk(9))
    with pytest.raises(ValueError):                              # wrong seed
        g.reg12_table((2,))
    monkeypatch.setattr(analysis.load, "find_runs", lambda p: mk(seed_of(p)) * 2)
    with pytest.raises(ValueError):                              # two valid runs for one pattern: refused
        g.reg12_table((2,))


def test_reg12_pair_runs_the_real_checks(monkeypatch, tmp_path):
    """Review recommendation 8: reg12_pair through the real reg10_gate and reg8_gate_verdict checks (λ, force_close,
    closed loop, 350 W, equal λ); only the verdict and the readouts are stubbed."""
    import pytest
    import analysis.gate as g
    import analysis.load

    def mk(name, seed=2, rate=2.4, fc=True, cl=True, w=350):
        return {"dir": tmp_path / name, "cfg": {"seed": seed, "loadgen_force_close": fc,
                "workload": {"rate": rate, "duration_s": 2580, "sessions": {"closed_loop": cl}},
                "checks": {"expected_power_limit_w": w, "max_scrape_gap_s": 2.0}}}

    monkeypatch.setattr(g, "gate_verdict", lambda c, b, *a: {"label": "pass", "control_verdict": "recovered",
                                                             "burst_verdict": "stuck"})
    for f in ("overlap_share", "secondary_cb", "queued_miss_share", "span_clock", "release_delay",
              "release_delay_baseline", "shock_size", "turn0_share", "unreleased", "end_window"):
        monkeypatch.setattr(g, f, lambda *a: "x")
    monkeypatch.setattr(g, "burst_end", lambda run: 1080.0)

    def runs(control, burst):
        monkeypatch.setattr(analysis.load, "find_runs", lambda p: [control] if "control" in p else [burst])

    runs(mk("c"), mk("b"))
    r = g.reg12_pair(2)
    assert r["stuck"] and r["stuck_pass"] and r["end_window"] == "x"
    for c, b in [(mk("c", cl=None), mk("b")), (mk("c"), mk("b", fc=None)), (mk("c", w=420), mk("b")),
                 (mk("c"), mk("b", rate=2.5)), (mk("c", seed=3), mk("b"))]:
        runs(c, b)
        with pytest.raises(ValueError):
            g.reg12_pair(2)



# ---------------------------------------------------------------- REG-13

def test_reg13_outcome_order_and_classes():
    o = lambda complete=True, col=False, mu=3.0, carried=3.1: G.reg13_outcome(complete, col, mu, carried, 2.4, 2.711)
    assert o(complete=False, col=True) == "incomplete"
    assert o(col=True, mu=2.0, carried=2.1) == "collapsed"      # before overload: carried, then went cold (review T1)
    assert o(col=True, mu=2.6, carried=2.758) == "below"        # a rate carrying >= 2.711 first, then a collapse above it
    assert o(col=True, mu=2.4, carried=2.529) == "collapsed"
    assert o(mu=math.nan, carried=math.nan) == "overload" and o(mu=2.0, carried=2.1) == "overload"
    assert o(mu=2.6, carried=2.758) == "below"                  # realized planned rate, not the grid value (review T2)
    assert o(mu=2.4, carried=2.529) == "partial"
    assert G.REG13["post_lam_p_max"] == G.REG13["cold_runs"]["20261109-111316_burst_l1pl350cl_r2.4_s4"]


def test_reg13_post_trigger_rate_from_the_burst_end_or_the_first_backlog(monkeypatch, tmp_path):
    import analysis.floor
    monkeypatch.setattr(G, "burst_end", lambda run: 1080.0)
    monkeypatch.setattr(G, "planned_session_rate", lambda run, a, b: (a, b))
    wl = {"warmup_s": 240, "duration_s": 2580}
    burst = {"dir": tmp_path / "b", "cfg": {"workload": wl, "trigger": {"kind": "burst"}}, "metrics": None}
    ctrl = {"dir": tmp_path / "c", "cfg": {"workload": wl}, "metrics": None}
    assert G.post_trigger_rate(burst)["lam_p"] == (1080.0, 2580.0)
    monkeypatch.setattr(analysis.floor, "backlogged_stretches", lambda m, a, b, w, s: [(1330.0, 2579.0), (2580.0, 2600.0)])
    assert G.post_trigger_rate(ctrl)["lam_p"] == (1330.0, 2580.0)
    monkeypatch.setattr(analysis.floor, "backlogged_stretches", lambda m, a, b, w, s: [])
    assert math.isnan(G.post_trigger_rate(ctrl)["lam_p"])


def test_reg13_due_unreleased_slope_grows_only_when_turns_fall_behind(tmp_path):
    wl = {"warmup_s": 0, "duration_s": 100}
    t = [float(x) for x in range(100)]
    on_time = pd.DataFrame({"turn": 1, "t_planned": t, "t_released": [x + 5.0 for x in t]})
    behind = pd.DataFrame({"turn": 1, "t_planned": t, "t_released": [x * 1.5 for x in t]})
    mk = lambda q: {"cfg": {"workload": wl}, "requests": q}
    assert abs(G.due_unreleased_slope(mk(on_time))) < 0.01
    assert G.due_unreleased_slope(mk(behind)) > 0.3
    assert G.due_unreleased_slope(mk(on_time.drop(columns="t_released"))) == 0.0   # open loop


def test_reg13_collapsed_needs_a_warm_stretch_that_carried_its_load_then_a_hit_drop(monkeypatch, tmp_path):
    import analysis.floor
    wl = {"warmup_s": 240, "duration_s": 900}
    req = pd.DataFrame({"status": "ok", "t_end": [300.0 + i for i in range(300)]})   # 300 done in [240, 600)
    run = {"cfg": {"workload": wl, "capacity": {"min_throughput_frac": 0.95}}, "requests": req, "metrics": None}
    monkeypatch.setattr(G, "planned_session_rate", lambda r, a, b: 300 / (b - a))
    monkeypatch.setattr(G, "_level", lambda r, a, b: {"hit": 0.8 if a == 240 else 0.1})
    monkeypatch.setattr(analysis.floor, "backlogged_stretches", lambda m, a, b, w, s: [(600.0, 899.0)])
    assert G.collapsed(run)["collapsed"] is True
    monkeypatch.setattr(analysis.floor, "backlogged_stretches", lambda m, a, b, w, s: [(500.0, 899.0)])   # < 300 s warm
    assert G.collapsed(run)["collapsed"] is False
    monkeypatch.setattr(analysis.floor, "backlogged_stretches", lambda m, a, b, w, s: [(600.0, 899.0)])
    monkeypatch.setattr(G, "_level", lambda r, a, b: {"hit": 0.8 if a == 240 else 0.78})                 # no hit drop
    assert G.collapsed(run)["collapsed"] is False
    monkeypatch.setattr(G, "_level", lambda r, a, b: {"hit": 0.8 if a == 240 else 0.1})
    monkeypatch.setattr(G, "planned_session_rate", lambda r, a, b: 400 / (b - a))                        # did not carry
    assert G.collapsed(run)["collapsed"] is False


def test_reg13_check_refuses_runs_outside_the_sweep(tmp_path):
    ok = {"sweep_parent": "sweep_l1pl350cl_pc_on", "loadgen_force_close": True,
          "workload": {"sessions": {"closed_loop": True}}, "checks": {"expected_power_limit_w": 350}}
    G.reg13_check({"dir": tmp_path / "x", "cfg": ok})
    bad = [{**ok, "sweep_parent": "sweep_l1pl350_pc_on"}, {**ok, "loadgen_force_close": False},
           {**ok, "workload": {"sessions": {}}}, {**ok, "checks": {"expected_power_limit_w": None}}]
    for cfg in bad:
        with pytest.raises(ValueError):
            G.reg13_check({"dir": tmp_path / "x", "cfg": cfg})


def test_reg13_config_is_reg8s_sweep_with_closed_loop_and_the_same_schedules():
    from harness.config import load_config, with_defaults
    from harness.run import expand
    from harness.workload import build_schedule
    new = {r["workload"]["rate"]: r for r in expand(with_defaults(load_config(Path("configs/sweep_l1pl350cl_pc_on.yaml"))))}
    old = {r["workload"]["rate"]: r for r in expand(with_defaults(load_config(Path("configs/sweep_l1pl350_pc_on.yaml"))))}
    assert tuple(sorted(new)) == G.REG13["rates"]
    for rate, r in new.items():
        assert r["workload"]["sessions"]["closed_loop"] and r["loadgen_force_close"] and r["seed"] == 0
        assert r["sweep_parent"] == G.REG13["sweep_on"] and r["checks"]["expected_power_limit_w"] == 350
        assert r["capacity"] == old[3]["capacity"] and r["workload"]["duration_s"] == 900
    for rate in G.REG13["paired"]:
        a, _ = build_schedule(new[rate]["workload"], new[rate]["seed"], None)
        b, _ = build_schedule(old[rate]["workload"], old[rate]["seed"], None)
        assert a.equals(b)


def _reg13_env(monkeypatch, tmp_path, rates, thr, due=0.0, col=False, cold=None):
    import analysis.load
    import analysis.tables
    cfg = lambda rate: {"sweep_parent": "sweep_l1pl350cl_pc_on", "loadgen_force_close": True,
                        "workload": {"rate": rate, "warmup_s": 240, "duration_s": 900, "sessions": {"closed_loop": True}},
                        "checks": {"expected_power_limit_w": 350},
                        "capacity": {"min_throughput_frac": 0.95, "max_q_slope": 0.01}}
    runs = [{"dir": tmp_path / f"r{x}", "cfg": cfg(x), "checks": {"valid": True}, "metrics": [1]} for x in rates]
    planned = {x: x * 1.05 for x in rates}
    monkeypatch.setattr(analysis.load, "find_runs", lambda p: runs)
    monkeypatch.setattr(analysis.load, "summarize", lambda r: {"throughput": thr(r["cfg"]["workload"]["rate"]),
                        "planned_rate": planned[r["cfg"]["workload"]["rate"]], "q_slope_per_s": 0.0, "unfinished": 0})
    monkeypatch.setattr(G, "sweep_rows", lambda parent, slo: pd.DataFrame(
        {"run": [f"r{x}" for x in rates], "rate": rates, "throughput": 0.0, "planned_rate": [planned[x] for x in rates],
         "kv_mean": 0.3, "pf": 1.0}))
    monkeypatch.setattr(G, "due_unreleased_slope", lambda r: due)
    monkeypatch.setattr(G, "collapsed", lambda r: {"collapsed": col})
    monkeypatch.setattr(G, "release_delay", lambda r, spans, end=None: [10.0])
    monkeypatch.setattr(G, "surge_max", lambda r, w: 3.0)
    monkeypatch.setattr(analysis.tables, "sweep_capacity", lambda p: math.nan)
    monkeypatch.setattr(analysis.load, "load_run", lambda p: {"dir": Path(p)})
    regd = dict(G.REG13["cold_runs"])
    monkeypatch.setattr(G, "post_trigger_rate", lambda run: {"lam_p": (cold or regd)[run["dir"].name]})
    monkeypatch.setattr(G, "reg8_g1_may_start", lambda: {"mu_sat_off": 1.681})
    monkeypatch.setattr(G, "choose_lambda", lambda *a: None)


def test_reg13_table_outcomes(monkeypatch, tmp_path):
    all_rates = list(G.REG13["rates"])
    _reg13_env(monkeypatch, tmp_path, all_rates, lambda x: x * 1.05)
    t = G.reg13_table()
    assert t["mu_warm_cl"] == 3.0 and t["outcome"] == "below" and t["n_cold_below"] == 7 and t["chain_end"] is None
    _reg13_env(monkeypatch, tmp_path, all_rates, lambda x: x * 1.05 if x < 2.8 else 1.0)
    t = G.reg13_table()                            # μ = 2.6 carried 2.73 >= 2.711: below, on the realized rate
    assert t["mu_warm_cl"] == 2.6 and t["carried"] == pytest.approx(2.73) and t["outcome"] == "below"
    _reg13_env(monkeypatch, tmp_path, all_rates, lambda x: x * 1.05 if x < 2.8 else 1.0, col=True)
    assert G.reg13_table()["outcome"] == "below"     # 2.6 carried 2.73 before 2.8 collapsed
    _reg13_env(monkeypatch, tmp_path, all_rates, lambda x: x * 1.05 if x < 2.6 else 1.0, col=True)
    assert G.reg13_table()["outcome"] == "collapsed"
    _reg13_env(monkeypatch, tmp_path, all_rates, lambda x: x * 1.05 if x < 2.6 else 1.0)
    t = G.reg13_table()
    assert t["outcome"] == "partial" and t["n_cold_below"] == 6     # carried 2.52: all but seed 4's burst
    _reg13_env(monkeypatch, tmp_path, all_rates, lambda x: x * 1.05, due=0.02)   # client backlog grows: fails (T3)
    assert G.reg13_table()["outcome"] == "overload"
    _reg13_env(monkeypatch, tmp_path, [2.0, 2.6], lambda x: x * 1.05)
    t = G.reg13_table()
    assert t["chain_end"] == 2.4 and t["outcome"] == "incomplete"
    bad = {**G.REG13["cold_runs"], "20261109-111316_burst_l1pl350cl_r2.4_s4": 2.5}
    _reg13_env(monkeypatch, tmp_path, all_rates, lambda x: x * 1.05, cold=bad)
    with pytest.raises(ValueError):                # the registered threshold no longer matches its run (T4)
        G.reg13_table()


# ---------------------------------------------------------------- REG-14

def test_reg14_configs_are_reg12_seed2_at_lambda_2_2_and_share_the_session_schedule():
    from harness.config import load_config, with_defaults
    from harness.run import expand

    def flat(d, p=""):
        out = {}
        for k, v in d.items():
            out.update(flat(v, p + k + ".") if isinstance(v, dict) else {p + k: v})
        return out
    res = lambda n: flat(expand(with_defaults(load_config(Path(f"configs/{n}.yaml"))))[0])
    for new, old in [("stage2_control_l1pl350cl_r2.2_s2", "stage2_control_l1pl350cl_r2.4_s2"),
                     ("burst_l1pl350cl_r2.2_s2", "burst_l1pl350cl_r2.4_s2")]:
        a, b = res(new), res(old)
        assert {k for k in set(a) | set(b) if a.get(k) != b.get(k)} == {"name", "workload.rate"}
        assert a["workload.rate"] == 2.2 and a["seed"] == 2
    assert G.reg14_schedule_inputs()["control_schedule_same"] is True


def test_reg14_patterns_match_only_its_own_runs_and_spec_is_reg11_at_2_2():
    import fnmatch
    extra = ("lam", "seed", "control", "burst", "reference_run", "cold_c_max", "seed_candidates", "warm_runs",
             "max_control_waiting")
    assert {k: v for k, v in G.REG14.items() if k not in extra} == \
        {k: v for k, v in G.REG11.items() if k not in ("lam", "control", "burst", "reference_run")}
    assert G.REG14["lam"] == 2.2 and G.REG14["seed"] == 2 and G.REG14["closed_loop"] is True
    own = {"control": "20261110-000000_stage2_control_l1pl350cl_r2.2_s2", "burst": "20261110-000000_burst_l1pl350cl_r2.2_s2"}
    others = ["20261109-034255_stage2_control_l1pl350cl_r2.4", "20261109-042828_burst_l1pl350cl_r2.4_s1",
              "20261109-055910_stage2_control_l1pl350cl_r2.4_s2", "20261109-080203_burst_l1pl350cl_r2.4_s2",
              "20261109-190221_sweep_l1pl350cl_pc_on_r2", "20261110-000000_burst_l1pl350cl_r2.2_s20"]
    for key, pat in (("control", G.REG14["control"]), ("burst", G.REG14["burst"])):
        assert fnmatch.fnmatch(own[key], pat)
        assert not any(fnmatch.fnmatch(o, pat) for o in others + [own["burst" if key == "control" else "control"]])


def test_max_holding_c_is_the_highest_rate_whose_upper_bound_is_below_the_cap():
    from analysis.stats import poisson_rate_upper
    for lam, lam_p in [(2.0, 2.103), (2.2, 2.1), (2.0, 1.717)]:
        c = G.max_holding_c(lam, lam_p, 300, 0.99)
        n = round(c * 300)
        assert poisson_rate_upper(n, 300, 0.99) < min(lam, lam_p) <= poisson_rate_upper(n + 1, 300, 0.99)
    assert math.isnan(G.max_holding_c(0.001, 0.001, 300, 0.99))


def test_reg14_seed_rule_picks_the_lowest_seed_with_every_span_above_the_cold_rate(monkeypatch):
    rows = {1: [2.0, 1.7, 2.0], 2: [2.0, 1.9, 2.0], 3: [2.0, 2.0, 2.0]}
    monkeypatch.setattr(G, "span_sensitivity", lambda lam, sd: {"spans": [{"max_c": c} for c in rows[sd]]})
    assert G.reg14_seed_rule(2.2, seeds=(1, 2, 3), cold_c_max=1.84) == 2
    assert G.reg14_seed_rule(2.2, seeds=(1, 2, 3), cold_c_max=1.95) == 3
    assert G.reg14_seed_rule(2.2, seeds=(1,), cold_c_max=1.84) is None


def test_reg14_gate_reads_the_shock_against_reg12_seed2_and_checks_lambda_and_seed(monkeypatch, tmp_path):
    import analysis.load
    mk = lambda name, rate=2.2, seed=2: {"dir": tmp_path / name, "cfg": {"seed": seed, "workload": {"rate": rate,
                                         "duration_s": 2580, "sessions": {"closed_loop": True}},
                                         "loadgen_force_close": True, "checks": {"max_scrape_gap_s": 2.0}}}
    pair = {"c": mk("c"), "b": mk("b")}
    monkeypatch.setattr(analysis.load, "find_runs", lambda p: [pair["c"]] if "control" in p else [pair["b"]])
    monkeypatch.setattr(analysis.load, "load_run", lambda p: pair.get(Path(p).name, {"dir": Path(p)}))
    monkeypatch.setattr(G, "reg8_gate_verdict", lambda c, b: {"label": "drains", "burst_verdict": "recovered",
                        "control_verdict": "recovered", "spans": [{"span": (1680, 1980), "lam_p": 2.1}]})
    for f in ("overlap_share", "secondary_cb", "queued_miss_share", "span_clock", "release_delay",
              "release_delay_baseline", "turn0_share", "unreleased", "release_rate", "control_waiting"):
        monkeypatch.setattr(G, f, lambda *a: "x")
    monkeypatch.setattr(G, "burst_end", lambda run: 1080.0)
    monkeypatch.setattr(G, "post_trigger_rate", lambda run: {"lam_p": 2.178})
    ref = {"outstanding": 46, "backlog_s": 1499.0}
    sizes = {"b": {"outstanding": 22, "backlog_s": 1499.0}}
    monkeypatch.setattr(G, "shock_size", lambda run: ref if run["dir"].name == G.REG14["reference_run"] else sizes["b"])
    res = G.reg14_gate()
    assert res["reference"] == ref and res["shock_comparable"] is False and res["post_trigger"]["lam_p"] == 2.178
    assert res["max_holding_c"][0] == pytest.approx(G.max_holding_c(2.2, 2.1, 300, 0.99))
    sizes["b"] = {"outstanding": 23, "backlog_s": 750.0}
    assert G.reg14_gate()["shock_comparable"] is True                                  # 23 >= 23, 750 >= 749.5
    for bad in (mk("c", rate=2.4), mk("c", seed=1)):
        pair["c"] = bad
        with pytest.raises(ValueError):
            G.reg14_gate()


def test_release_rate_counts_every_released_session_request_per_span(monkeypatch):
    monkeypatch.setattr(G, "burst_end", lambda run: 0.0)
    monkeypatch.setattr(G, "is_burst_request", lambda run: pd.Series([False, False, False, True, False]))
    q = pd.DataFrame({"turn": [0, 1, 2, 0, 3], "t_released": [None, 5.0, 150.0, 6.0, None],
                      "t_planned": [1.0, 4.0, 9.0, 6.0, 20.0], "t_sent": [1.0, 5.0, 150.0, 6.0, None]})
    # first turn (t_planned 1) and turn 1 in span 1; turn 2 in span 2; burst row and the never-sent turn 3 left out
    assert G.release_rate({"requests": q}, [(0, 100), (100, 200)]) == [0.02, 0.01]
    assert math.isnan(G.release_rate({"requests": q.drop(columns="t_released")}, [(0, 1)])[0])


def test_reg14_outcome_splits_pass_by_the_controls_waiting_share():
    spans = [{"counts": True}, {"counts": False}, {"counts": True}]
    w = lambda *xs: [{"share_waiting": x} for x in xs]
    assert G.reg14_outcome({"outcome": "pass", "spans": spans, "control_waiting": w(0.9, 0.1, 0.5)}) == "pass_clear"
    assert G.reg14_outcome({"outcome": "pass", "spans": spans, "control_waiting": w(0.9, 0.1, 0.51)}) == "pass_warm_edge"
    for o in ("drains", "control_not_healthy", "stuck_unconfirmed", "inconclusive"):
        assert G.reg14_outcome({"outcome": o}) == o


def test_due_unreleased_profile_reports_the_slope_rates_and_lag(tmp_path):
    q = pd.DataFrame({"turn": [1, 1, 1, 1], "t_planned": [250.0, 300.0, 800.0, 850.0],
                      "t_released": [260.0, 310.0, 820.0, 870.0]})
    run = {"cfg": {"workload": {"warmup_s": 240, "duration_s": 900}}, "requests": q}
    p = G.due_unreleased_profile(run)
    assert p["later_rate_first"] == pytest.approx(2 / 120) and p["later_rate_last"] == pytest.approx(2 / 120)
    assert p["lag_by_minute"][0] == 10.0 and p["lag_by_minute"][-2] == 20.0 and len(p["lag_by_minute"]) == 11


# ---------------------------------------------------------------- REG-15

def _reg15_cfg(**over):
    cfg = {"seed": 12, "loadgen_force_close": True, "checks": {"expected_power_limit_w": 350},
           "trigger": {"kind": "burst", "at_s": 900, "duration_s": 180},
           "verdict": {"watch_s": 4500, "baseline_s": 600, "recovered_pf_drop": 0.02, "recovered_hit_drop": 0.06,
                       "recovered_q_excess": 1.0},
           "workload": {"rate": 2.2, "duration_s": 8880, "sessions": {"closed_loop": True},
                        "steps": [{"at_s": 5580, "rate": 1}, {"at_s": 7380, "rate": 2.2}]}}
    for k, v in over.items():
        cfg["workload"][k] = v
    return cfg


def test_reg15_config_is_reg14s_burst_run_with_the_watch_drop_and_return():
    from harness.config import load_config, with_defaults
    from harness.run import expand
    from harness.workload import build_schedule
    res = lambda n: expand(with_defaults(load_config(Path(f"configs/{n}.yaml"))))[0]
    new, old = res("confirm_l1pl350cl_r2.2_s12"), res("burst_l1pl350cl_r2.2_s2")
    diff = {k for k in set(new) | set(old) if new.get(k) != old.get(k)}
    assert diff == {"name", "seed", "workload", "verdict"} and new["seed"] == 12
    assert {k for k in new["workload"] if new["workload"].get(k) != old["workload"].get(k)} == {"duration_s", "steps"}
    assert {k for k in new["verdict"] if new["verdict"][k] != old["verdict"][k]} == {"watch_s"}
    ph = G.reg15_phases({"dir": Path("x"), "cfg": new})
    assert ph["watch_end"] == 5580 and ph["drop"] == (5580, 7380) and ph["return_end"] == (8280, 8880)
    w = G.reg15_judged_windows(12)["windows"]   # the verdict's own windows (end_s from the config: review rec. 6)
    assert w["end"] == (5580 - new["verdict"]["end_s"], 5580) == (4980, 5580) and w["previous"] == (4380, 4980)
    assert w["baseline"] == (300, 900) and w["return_end"] == (8280, 8880)


def test_reg15_phases_refuse_another_design():
    run = lambda cfg: {"dir": Path("x"), "cfg": cfg}
    assert G.reg15_phases(run(_reg15_cfg()))["baseline"] == (300, 900)
    for bad in (_reg15_cfg(steps=[{"at_s": 5580, "rate": 1}]), _reg15_cfg(duration_s=8000),
                _reg15_cfg(steps=[{"at_s": 5580, "rate": 0.5}, {"at_s": 7380, "rate": 2.2}]),
                _reg15_cfg(steps=[{"at_s": 5580, "rate": 1}, {"at_s": 7380, "rate": 2.4}])):
        with pytest.raises(ValueError):
            G.reg15_phases(run(bad))


def test_reg15_outcome_classes():
    o = G.reg15_outcome
    assert o("stuck", True, True) == "confirms" and o("stuck", True, False) == "no_return"
    assert o("stuck", False, True) == "drop_inconclusive"
    assert o("recovered", None, None) == "not_persistent" and o("slow_drain", True, True) == "not_persistent"
    assert o("bad_baseline", True, True) == "bad_baseline"
    assert o("unclear", True, True) == "inconclusive" and o("stuck", None, True) == "inconclusive"
    assert o("stuck", True, None) == "inconclusive"
    assert o("stuck", True, True, broken=True) == "reformed" and o("stuck", None, None, broken=True) == "reformed"
    assert o("recovered", True, True, broken=True) == "not_persistent"


def test_line_reached_zero_and_recovered_against(monkeypatch):
    m = pd.DataFrame({"t": [0.0, 10.0, 20.0, 30.0], "vllm:num_requests_waiting": [5.0, 0.0, 3.0, float("nan")]})
    run = {"metrics": m, "cfg": _reg15_cfg()}
    assert G.line_reached_zero(run, 0, 20) is True and G.line_reached_zero(run, 20, 40) is False
    assert G.line_reached_zero(run, 30, 40) is None
    import analysis.load
    base = {"pf": 1.0, "hit": 0.83, "q": 0.0}
    for lv, want in [({"pf": 0.99, "hit": 0.80, "q": 0.5}, True), ({"pf": 0.97, "hit": 0.80, "q": 0.5}, False),
                     ({"pf": 0.99, "hit": 0.76, "q": 0.5}, False), ({"pf": 0.99, "hit": 0.80, "q": 1.5}, False),
                     ({"pf": float("nan"), "hit": 0.80, "q": 0.5}, None)]:
        monkeypatch.setattr(analysis.load, "_level", lambda r, a, b, lv=lv: lv)
        assert G.recovered_against(run, base, 0, 1) is want


def test_reg15_check_refuses_runs_outside_the_design():
    ok = {"dir": Path("x"), "checks": {"valid": True}, "cfg": _reg15_cfg()}
    G.reg15_check(ok)
    for change in ({"seed": 2}, {"loadgen_force_close": None}, {"checks": {"expected_power_limit_w": 420}}):
        with pytest.raises(ValueError):
            G.reg15_check({**ok, "cfg": {**ok["cfg"], **change}})
    with pytest.raises(ValueError):
        G.reg15_check({**ok, "checks": {"valid": False}})
    with pytest.raises(ValueError):
        G.reg15_check({**ok, "cfg": _reg15_cfg(rate=2.4)})


def test_reg15_seed_rule_picks_the_lowest_seed_with_every_judged_window_near_lambda(monkeypatch):
    lam = {1: [2.2, 2.2, 2.44, 2.2], 2: [2.2, 2.1, 2.3, 2.25], 3: [2.2] * 4}
    monkeypatch.setattr(G, "reg15_judged_windows", lambda sd: {"seed": sd, "lam_p": dict(zip("abcd", lam[sd]))})
    assert G.reg15_seed_rule(seeds=(1, 2, 3))["picked"] == 2                       # 2.31 is the edge at 5 %
    assert G.reg15_seed_rule(seeds=(1, 2, 3), tol=0.04)["picked"] == 3
    assert G.reg15_seed_rule(seeds=(1,))["picked"] is None


def test_watch_broken_flags_any_recovered_window(monkeypatch):
    seq = iter([False, None, True, False])
    monkeypatch.setattr(G, "recovered_against", lambda run, base, a, b: next(seq))
    r = G.watch_broken({}, {}, 1080.0, 2280.0)
    assert r["windows"][0] == (1080.0, 1380.0) and len(r["windows"]) == 4 and r["broken"] is True
    seq = iter([False, None, False, False])
    assert G.watch_broken({}, {}, 1080.0, 2280.0)["broken"] is False


def test_load_verdict_judges_reg15s_windows_from_the_config(monkeypatch):
    """Review round 2, point 6: `load.verdict` itself, on a run with REG-15's config, judges 4980-5580 against
    4380-4980 and the baseline 300-900: the same windows as `reg15_judged_windows`."""
    import analysis.load as L
    from harness.config import load_config, with_defaults
    from harness.run import expand
    cfg = expand(with_defaults(load_config(Path("configs/confirm_l1pl350cl_r2.2_s12.yaml"))))[0]
    seen = []
    monkeypatch.setattr(L, "_level", lambda run, a, b: seen.append((a, b)) or
                        {"pf": 1.0, "hit": 0.8, "q": 0.0, "q_slope": 0.0, "n": 5.0, "kv": 0.2})
    L.verdict({"cfg": cfg, "metrics": pd.DataFrame(), "requests": pd.DataFrame(), "trigger": pd.DataFrame()})
    w = G.reg15_judged_windows(12)["windows"]
    assert seen == [w["baseline"], w["previous"], w["end"]]


# ---------------------------------------------------------------- REG-16

def _res(name):
    from harness.config import load_config, with_defaults
    from harness.run import expand
    return expand(with_defaults(load_config(Path(f"configs/{name}.yaml"))))[0]


def test_reg16_control_is_reg14s_control_with_reg17s_schedule():
    from harness.workload import build_schedule
    new, old = _res("stage2_control_l1pl350cl_r2.2_long_s14"), _res("stage2_control_l1pl350cl_r2.2_s2")
    assert {k for k in set(new) | set(old) if new.get(k) != old.get(k)} == {"name", "seed", "workload", "verdict"}
    assert {k for k in new["workload"] if new["workload"].get(k) != old["workload"].get(k)} == {"duration_s", "steps"}
    assert {k for k in new["verdict"] if new["verdict"][k] != old["verdict"][k]} == {"watch_s"}
    burst = _res("confirm_l1pl350cl_r2.2_long_s14")
    assert burst["workload"] == new["workload"] and burst["seed"] == new["seed"] == 14
    assert burst == {**G.reg16_burst_cfg(14, G.REG16["drop_s"]), "name": burst["name"]} and G.REG16["drop_s"] == 9000
    sc, _ = build_schedule(new["workload"], new["seed"], new.get("trigger"))
    sb, _ = build_schedule(burst["workload"], burst["seed"], burst["trigger"])
    cols = ["t_planned", "session_id", "turn", "prompt_len"]
    assert sc[cols].equals(sb[~sb.burst][cols].reset_index(drop=True))
    ph = G.reg16_phases({"dir": Path("x"), "cfg": new})
    assert ph["watch"] == (1080, 5580) and ph["drop"] == (5580, 14580) and ph["return_end"] == (15480, 16080)
    with pytest.raises(ValueError):
        G.reg16_phases({"dir": Path("x"), "cfg": burst})                     # a burst run is not the control
    with pytest.raises(ValueError):
        G.reg16_phases({"dir": Path("x"), "cfg": {**new, "workload": {**new["workload"], "duration_s": 16000}}})


def test_reg16_spec_keeps_the_matrix_seeds_and_the_baseline_window():
    assert not set(G.REG16["seeds"]) & {3, 4, 5, 6, 7} and 14 in G.REG16["seeds"]
    b = _res("confirm_l1pl350cl_r2.2_long_s14")
    t = float(b["trigger"]["at_s"])
    assert G.REG16["baseline"] == (t - b["verdict"]["baseline_s"], t)


def test_completion_rate_and_owed_backlog():
    q = pd.DataFrame({"t_planned": [0.0, 1.0, 2.0, 3.0], "t_end": [0.5, 5.0, float("nan"), 3.5]})
    run = {"requests": q}
    assert G.completion_rate(run, 0, 4) == 2 / 4
    assert G.owed_backlog(run, 2.5) == 2          # planned before 2.5: ids 0-2; id 0 done
    assert G.owed_backlog(run, 6.0) == 1          # only the never-completed one


def test_reg16_empty_time_bounds():
    cfg = G.reg16_burst_cfg(14, 7200)
    fast = {"owed_at_trigger": 0, "c_watch": 100.0, "c_drop": 100.0, "c_watch_min": 100.0, "c_drop_min": 100.0}
    assert G.reg16_empty_time(cfg, fast) == 0.0
    zero = {"owed_at_trigger": 0, "c_watch": 0.0, "c_drop": 0.0, "c_watch_min": 0.0, "c_drop_min": 0.0}
    assert math.isnan(G.reg16_empty_time(cfg, zero))
    cal = {"owed_at_trigger": 28, "c_watch": 1.758, "c_drop": 1.672, "c_watch_min": 1.728, "c_drop_min": 1.637}
    assert G.reg16_empty_time(cfg, cal) < G.reg16_empty_time(cfg, cal, pessimistic=True)
    # the pessimistic rates are the lowest 600 s rates minus c_pessimism, not the means minus it
    alt = {**cal, "c_watch_min": cal["c_watch"], "c_drop_min": cal["c_drop"]}
    assert G.reg16_empty_time(cfg, alt, pessimistic=True) < G.reg16_empty_time(cfg, cal, pessimistic=True)


def test_pf_by_sent_uses_send_time():
    q = pd.DataFrame({"t_planned": [0.0, 0.0, 500.0], "t_sent": [900.0, 950.0, 510.0], "status": ["ok"] * 3,
                      "ttft": [5.0, 0.2, 0.2]})
    run = {"requests": q, "cfg": {"slo": {"ttft_s": 1.0}}}
    assert G.pf_by_sent(run, 900, 1000) == 0.5 and G.pf_by_sent(run, 500, 600) == 1.0
    assert math.isnan(G.pf_by_sent(run, 0, 100))


def test_cold_windows_need_both_stuck_levels_and_flag_low_hit_with_a_queue(monkeypatch):
    lv = iter([{"hit": 0.0, "q": 50.0}, {"hit": 0.0, "q": 50.0}, {"hit": float("nan"), "q": 0.0},
               {"hit": 0.78, "q": 0.0}])
    pf = iter([0.0, 0.95, 0.0, 0.0])
    monkeypatch.setattr(G, "_level", lambda run, a, b: next(lv))
    monkeypatch.setattr(G, "pf_by_sent", lambda run, a, b: next(pf))
    run = {"cfg": {"verdict": {"stuck_hit_drop": 0.06, "stuck_pf_drop": 0.10, "recovered_q_excess": 1.0}}}
    r = G.cold_windows(run, {"hit": 0.84, "pf": 1.0, "q": 0.0}, 1080.0, 2280.0)
    assert r["windows"][0] == (1080.0, 1380.0)
    assert r["cold"] == [True, False, None, True]
    assert r["hit_low_queued"] == [True, True, None, False]


def test_cold_persistent_at_a_phase_end_or_a_long_stretch():
    cw = {"windows": [(0, 300), (300, 600), (600, 900)], "cold": [True, False, False]}
    assert G.cold_persistent(cw, [900]) is False
    assert G.cold_persistent({**cw, "cold": [False, False, True]}, [900]) is True
    assert G.cold_persistent(cw, [300]) is True
    assert G.cold_persistent({**cw, "cold": [True, None, False]}, [600]) is None        # gap at a phase end after cold
    assert G.cold_persistent({**cw, "cold": [False, None, False]}, [600]) is False
    wins = [(x, x + 300) for x in range(0, 3000, 300)]
    long = {"windows": wins, "cold": [False] + [True] * 5 + [False] * 4}                 # 1500 s cold, then warm
    assert G.longest_cold_s(long) == 1500 and G.cold_persistent(long, [3000]) is True
    short = {"windows": wins, "cold": [False] + [True] * 4 + [None, True] + [False] * 3}  # None breaks a stretch
    assert G.longest_cold_s(short) == 1200 and G.cold_persistent(short, [3000]) is False


def test_window_mix_counts_unsent_and_first_turns():
    q = pd.DataFrame({"t_planned": [0.0, 10.0, 20.0, 30.0], "t_sent": [5.0, float("nan"), 25.0, 35.0],
                      "turn": [0, 1, 0, 2], "prompt_tokens_planned": [10, 20, 10, 30]})
    run = {"requests": q, "cfg": {}}
    assert G.window_mix(run, 0, 40) == {"unsent": 1, "turn0_share": 2 / 3}


def _cw(cold, low=None):
    return {"cold": cold, "hit_low_queued": low if low is not None else [False] * len(cold)}


@pytest.mark.parametrize("base_ok,v,cw,pers,back,want", [
    (False, "recovered", _cw([False]), False, True, "bad_baseline"),
    (True, "bad_baseline", _cw([False]), False, True, "bad_baseline"),          # review N3: to the owner, not a rerun
    (None, "recovered", _cw([False]), False, True, "inconclusive"),
    (True, "unclear", _cw([False, True]), True, None, "control_cold_persistent"),
    (True, "stuck", _cw([False]), False, True, "control_cold_persistent"),
    (True, "recovered", _cw([True, False]), False, True, "control_cold_transient"),
    (True, "recovered", _cw([True, None]), None, True, "inconclusive"),
    (True, "unclear", _cw([False]), False, True, "inconclusive"),
    (True, "recovered", _cw([False, None]), False, True, "inconclusive"),
    (True, "recovered", _cw([False], [None]), False, True, "inconclusive"),
    (True, "recovered", _cw([False]), False, None, "inconclusive"),
    (True, "recovered", _cw([False, False], [False, True]), False, True, "control_unclear"),
    (True, "slow_drain", _cw([False]), False, True, "control_not_recovered"),
    (True, "recovered", _cw([False]), False, False, "control_not_recovered"),
    (True, "recovered", _cw([False, False]), False, True, "control_warm"),
])
def test_reg16_control_outcome_order(base_ok, v, cw, pers, back, want):
    assert G.reg16_control_outcome(base_ok, v, cw, pers, back) == want


def test_reg16_check_pins_the_registered_config():
    cfg = G._burst_cfg(G.REG16_CONTROL)
    run = lambda c: {"dir": Path("x"), "checks": {"valid": True}, "cfg": c}
    G.reg16_check(run({**cfg, "run_id": "x", "source_config": "y"}))           # run-time extras are fine
    for bad in ({**cfg, "seed": 12}, {**cfg, "trigger": {"kind": "wipe"}},
                {**cfg, "workload": {**cfg["workload"], "rate": 2.4}}):
        with pytest.raises(ValueError):
            G.reg16_check(run(bad))
    with pytest.raises(ValueError):
        G.reg16_check({"dir": Path("x"), "checks": {"valid": False}, "cfg": cfg})


def test_reg16_seed_rule_picks_the_shortest_drop_then_the_lowest_seed(monkeypatch):
    cal = {"run": "x", "owed_at_trigger": 28, "owed_at_watch_end": 2149, "owed_at_drop_end": 1215,
           "c_watch": 1.758119658119658, "c_drop": 1.6716666666666666, "c_watch_min": 1.7283333333333333,
           "c_drop_min": 1.6366666666666667, "released_drop": 1.58}
    monkeypatch.setattr(G, "reg16_calibration", lambda: cal)
    monkeypatch.setattr(G, "REG16", {**G.REG16, "seeds": (13, 14, 24)})
    r = G.reg16_seed_rule()
    assert r["picked"] == {"drop_s": 7200, "seed": 14}
    row = next(x for x in r["rows"] if x["drop_s"] == 5400 and x["seed"] == 14)
    assert row["windows_ok"] and not row["drop_ok"]


# ---------------------------------------------------------------- surge statistic

def _surge_run(t_planned, kv, burst_at=None, duration=3000.0, burst_rows=()):
    """A synthetic closed-loop run: session requests at `t_planned` (turn 1), KV usage per 1 s scrape from `kv(t)`,
    optional burst requests (turn 0, prompt 2944) at `burst_rows`."""
    t = [float(x) for x in range(int(duration))]
    m = pd.DataFrame({"t": t, "vllm:kv_cache_usage_perc": [kv(x) for x in t]})
    rows = [{"t_planned": float(x), "turn": 1, "prompt_tokens_planned": 896} for x in t_planned]
    rows += [{"t_planned": float(x), "turn": 0, "prompt_tokens_planned": 2944} for x in burst_rows]
    cfg = {"workload": {"rate": 2.0, "duration_s": duration}}
    if burst_at is not None:
        cfg["trigger"] = {"kind": "burst", "at_s": burst_at, "duration_s": 180, "prompt_tokens": 2944}
    return {"dir": Path("x_run"), "cfg": cfg, "metrics": m, "requests": pd.DataFrame(rows)}


def test_rolling_rate_counts_the_trailing_window():
    import numpy as np
    x = G.rolling_rate([10.0, 50.0, 119.0, 130.0], np.array([120.0, 200.0]), 120.0)
    assert x[0] == pytest.approx(3 / 120) and x[1] == pytest.approx(2 / 120)   # [0,120) holds 3; [80,200) holds 2


def test_kv_onset_needs_a_sustained_mean():
    spike = _surge_run([], lambda t: 1.0 if 1000 <= t < 1010 else 0.2)       # a 10 s spike: mean stays below 0.9
    assert math.isnan(G.kv_onset(spike))
    full = _surge_run([], lambda t: 0.95 if t >= 1000 else 0.2)
    assert 1000 < G.kv_onset(full) < 1060                                      # trailing 60 s mean crosses 0.9 inside


def test_surge_run_splits_the_tipping_peak_from_warm_time():
    import numpy as np
    base = list(np.arange(0, 3000, 0.5))                                       # 2 req/s throughout
    surge = list(np.arange(1860, 1980, 0.8))                                    # +1.25 req/s for 120 s
    run = _surge_run(base + surge, lambda t: 0.95 if t >= 2000 else 0.2)
    r = G.surge_run(run)
    assert r["tipped"] and r["onset"] == pytest.approx(2053, abs=2)
    assert r["peak_tip"] == pytest.approx(3.25, abs=0.02)                      # inside the last 180 s before onset - 60
    assert r["peak_before"] == pytest.approx(2.0, abs=0.02)


def test_surge_run_burst_run_stops_at_the_burst_and_ignores_burst_requests():
    import numpy as np
    run = _surge_run(list(np.arange(0, 3000, 0.5)), lambda t: 0.95 if t >= 960 else 0.2, burst_at=900.0,
                     burst_rows=list(np.arange(880, 899, 0.1)))                 # burst-sized rows before 900 left out
    r = G.surge_run(run)
    assert not r["tipped"] and r["warm_s"] == pytest.approx(900 - G.SURGE["start_s"])
    assert math.isnan(r["peak_tip"]) and r["peak_before"] == pytest.approx(2.0, abs=0.02)


def test_pair_schedule_reproduces_reg14s_burst_run_at_its_own_rate():
    """At λ 2.2 and seed 2 the pair schedule is REG-14's burst config itself; its baseline λp matches the REG-14 rule's
    readout (`reg14_schedule_inputs`), so a pair at another λ changes only the rate."""
    p = G.pair_schedule(2.2, 2)
    assert p["lam_p_baseline"] == pytest.approx(G.reg14_schedule_inputs()["lam_p_baseline"])
    assert len(p["lam_p_watch_thirds"]) == 3 and p["peak_run"] >= p["peak_pre_burst"]


# ---------------------------------------------------------------- REG-17

def test_reg17_configs_change_only_the_rate():
    flat = lambda d, p="": {k2: v2 for k, v in d.items()
                            for k2, v2 in (flat(v, p + k + ".") if isinstance(v, dict) else {p + k: v}).items()}
    for new, old in (("stage2_control_l1pl350cl_r2.0_s2", "stage2_control_l1pl350cl_r2.2_s2"),
                     ("burst_l1pl350cl_r2.0_s2", "burst_l1pl350cl_r2.2_s2")):
        a, b = flat(G._burst_cfg(new)), flat(G._burst_cfg(old))
        assert sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k)) == ["name", "workload.rate"]
        assert a["workload.rate"] == 2.0


def test_reg17_outcome_order():
    calm = [{"share_waiting": 0.0}] * 3
    tip = {"tipped": True, "peak_tip": 3.3}
    flat = {"tipped": False, "peak_tip": math.nan}
    assert G.reg17_outcome("bad_baseline", "stuck", {}, calm) == "bad_baseline"
    assert G.reg17_outcome("recovered", "bad_baseline", {}, calm) == "bad_baseline"
    assert G.reg17_outcome("stuck", "stuck", tip, calm) == "control_cold_surge"
    assert G.reg17_outcome("stuck", "stuck", {"tipped": True, "peak_tip": 3.1}, calm) == "control_cold_no_surge"
    assert G.reg17_outcome("unclear", "stuck", {"tipped": True, "peak_tip": 3.1}, calm) == "control_cold_no_surge"
    # review T1: an unclear control that never tipped is an instrument question, not a refutation
    assert G.reg17_outcome("unclear", "stuck", flat, calm) == "control_unclear"
    assert G.reg17_outcome("slow_drain", "stuck", flat, calm) == "control_warm_queue"
    assert G.reg17_outcome("recovered", "stuck", {}, calm) == "pass_clear"
    assert G.reg17_outcome("recovered", "stuck", {}, calm, cold_side=False) == "stuck_draining"   # review T2
    assert G.reg17_outcome("recovered", "stuck", {}, calm, cold_side=None) == "inconclusive"
    assert G.reg17_outcome("recovered", "stuck", {}, calm[:2] + [{"share_waiting": 0.6}]) == "pass_warm_edge"
    assert G.reg17_outcome("recovered", "stuck", {}, calm[:2] + [{"share_waiting": math.nan}]) == "pass_warm_edge"
    assert G.reg17_outcome("recovered", "slow_drain", {}, calm) == "drains"
    assert G.reg17_outcome("recovered", "recovered", {}, calm) == "drains"
    assert G.reg17_outcome("recovered", "unclear", {}, calm) == "unclear"


def test_reg17_cold_side_and_drain_time_on_reg14s_burst_run():
    """On REG-14's stuck burst run at 2.2 (judged at λ 2.0 here only to exercise the code): its spans completed
    1.73-1.81, below 2.0 and below each span's λp, and its queue grew to the end, so the cold side holds; its line
    never emptied."""
    from analysis.load import RUNS, load_run
    d = RUNS / "20261110-063647_burst_l1pl350cl_r2.2_s2"
    if not d.exists():
        pytest.skip("run folder not on this machine")
    r = load_run(d)
    cs = G.reg17_cold_side(r)
    assert cs["holds"] is True and all(1.6 < x["c"] < 1.9 for x in cs["spans"]) and cs["end_q_slope"] > 0
    assert math.isnan(G.drain_time(r))


def test_reg17_span_test_cannot_confirm_the_known_cold_rates():
    """Why REG-17 is decided by the verdict pair: every span's highest confirmable cold rate is below REG-14's
    cold_c_max (1.84), so REG-14's seed rule finds no seed at 2.0."""
    assert all(r["max_c"] < G.REG14["cold_c_max"] for r in G.span_sensitivity(2.0, 2)["spans"])
    assert G.reg14_seed_rule(2.0) is None
