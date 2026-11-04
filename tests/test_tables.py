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
