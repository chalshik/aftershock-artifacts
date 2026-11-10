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
