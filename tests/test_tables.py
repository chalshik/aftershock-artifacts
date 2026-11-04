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
    assert judgeable({"cfg": {"verdict": full}})
    assert not judgeable({"cfg": {"verdict": {**full, "pf_climb": None}}})
    assert not judgeable({"cfg": {}})


def test_published_check_flags_only_differences():
    bad = next(iter(PUBLISHED_NOT_RECOVERED))
    v = pd.DataFrame({"run": ["a", bad, "c"], "valid": [True, True, False], "verdict": ["recovered", "bad_baseline", "stuck"]})
    c = pd.DataFrame({"setup": ["s"], "mu_warm": [4.0], "mu_warm_published": [4], "mu_off": [2.0], "mu_off_published": [2]})
    assert published_check(v, c) == []
    v.loc[0, "verdict"] = "unclear"
    c.loc[0, "mu_off"] = 2.5
    assert len(published_check(v, c)) == 2
