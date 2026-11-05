"""analysis/tables.py helpers on synthetic inputs (no run folders)."""
import pandas as pd

from analysis.tables import PUBLISHED_NOT_RECOVERED, VERDICT_KEYS, arrival_profile, judgeable, published_check


def test_arrival_profile_shares_of_lambda():
    sched = pd.DataFrame({"t_planned": [250.0] * 150 + [800.0] * 450})  # 1/s in 240-390, 3/s in 750-900
    p = arrival_profile(sched, rate=2.0)
    assert p["240-390"] == 0.5 and p["750-900"] == 1.5 and p["390-540"] == 0.0
    assert p["window"] == 600 / 660 / 2.0


def test_judgeable_needs_the_full_verdict_block():
    full = {k: 1 for k in VERDICT_KEYS}
    wl = {"workload": {}}
    assert judgeable({"cfg": {"verdict": full, **wl}})
    assert not judgeable({"cfg": {"verdict": {**full, "pf_climb": None}, **wl}})
    assert not judgeable({"cfg": {**wl}})
    assert not judgeable({"cfg": {"verdict": full, "workload": {"steps": [{"at_s": 300, "rate": 3}]}}})  # a ramp


def test_published_check_flags_only_differences():
    bad = next(iter(PUBLISHED_NOT_RECOVERED))
    v = pd.DataFrame({"run": ["a", bad, "c"], "valid": [True, True, False], "verdict": ["recovered", "bad_baseline", "stuck"]})
    c = pd.DataFrame({"setup": ["s"], "mu_warm": [4.0], "mu_warm_published": [4], "mu_off": [2.0], "mu_off_published": [2]})
    assert published_check(v, c) == []
    v.loc[0, "verdict"] = "unclear"
    c.loc[0, "mu_off"] = 2.5
    assert len(published_check(v, c)) == 2


def test_capacity_rule_is_read_from_the_config_and_defaults_to_the_old_rule():
    from analysis.tables import CAPACITY_RULE, capacity_rule
    assert capacity_rule({}) == {**CAPACITY_RULE, "against": "rate", "monotone": False}
    new = {"capacity": {"min_throughput_frac": 0.95, "max_q_slope": 0.01, "against": "planned_rate"}}
    assert capacity_rule(new)["against"] == "planned_rate"


def test_sweep_capacity_uses_the_registered_rule_and_refuses_a_mix():
    import json
    import pytest
    from analysis.tables import sweep_capacity
    rule = lambda a: json.dumps({"against": a, "max_q_slope": 0.01, "min_throughput_frac": 0.95}, sort_keys=True)
    sw = pd.DataFrame({"parent": ["p", "p"], "valid": [True, True], "rate": [2, 3], "throughput": [2.0, 3.0],
                       "planned_rate": [2.0, 3.3], "q_slope_per_s": [0.0, 0.0], "capacity_rule": [rule("planned_rate")] * 2})
    assert sweep_capacity("p", sw) == 2
    with pytest.raises(ValueError):
        sweep_capacity("p", sw.assign(capacity_rule=[rule("rate"), rule("planned_rate")]))


def _mono_sweep(valid, throughput, rates=(2, 3, 4, 5), swept=None):
    import json
    rule = json.dumps({"against": "planned_rate", "max_q_slope": 0.01, "min_throughput_frac": 0.95, "monotone": True},
                      sort_keys=True)
    n = len(rates)
    swept = json.dumps([float(x) for x in (swept or rates)])
    return pd.DataFrame({"parent": ["p"] * n, "valid": list(valid), "rate": list(rates), "throughput": list(throughput),
                         "planned_rate": [float(r) for r in rates], "q_slope_per_s": [0.0] * n,
                         "capacity_rule": [rule] * n, "swept_rates": [swept] * n})


def test_monotone_capacity_stops_at_a_rate_with_no_valid_run():
    """decisions.md 2026-11-05 [CORR]: an invalid rate ends the chain, so a valid pass above it cannot set mu."""
    from analysis.tables import sweep_capacity
    all_pass = [2.0, 3.0, 4.0, 5.0]
    assert sweep_capacity("p", _mono_sweep([True, True, True, True], all_pass)) == 5
    assert sweep_capacity("p", _mono_sweep([True, True, False, True], all_pass)) == 3  # was 5 before the fix
    import math
    assert math.isnan(sweep_capacity("p", _mono_sweep([False, True, True, True], all_pass)))  # lowest rate unmeasured


def test_monotone_capacity_counts_a_valid_rerun_and_sees_rates_from_every_run():
    import json
    from analysis.tables import sweep_capacity
    sw = _mono_sweep([True, True, False, True], [2.0, 3.0, 4.0, 5.0])
    rerun = sw.iloc[[2]].assign(valid=True, swept_rates=json.dumps([4.0]))  # a rerun config listing only rate 4
    assert sweep_capacity("p", pd.concat([sw, rerun], ignore_index=True)) == 5
    # a rate that is swept but has no row at all (e.g. a run without metrics) also ends the chain
    sw2 = _mono_sweep([True, True, True], [2.0, 3.0, 5.0], rates=(2, 3, 5), swept=(2, 3, 4, 5))
    assert sweep_capacity("p", sw2) == 3


def test_monotone_capacity_refuses_two_valid_runs_at_one_rate():
    import pytest
    from analysis.tables import sweep_capacity
    sw = _mono_sweep([True, True, True, True], [2.0, 3.0, 4.0, 5.0])
    with pytest.raises(ValueError):
        sweep_capacity("p", pd.concat([sw, sw.iloc[[1]]], ignore_index=True))


def test_swept_rates_is_refused_outside_the_monotone_rule():
    import pytest
    from analysis.load import capacity
    c = pd.DataFrame({"rate": [2], "throughput": [2.0], "planned_rate": [2.0], "q_slope_per_s": [0.0]})
    with pytest.raises(ValueError):
        capacity(c, 0.95, 0.01, against="planned_rate", monotone=False, swept_rates=[2])
