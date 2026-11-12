"""analysis/k2.py: the E0 prediction and gate (draft)."""
import math
from pathlib import Path

import pytest

from analysis import k2
from harness.run import load_config
from tests.test_workload import CONFIGS

S = k2.shape(load_config(CONFIGS / "sweep_l1pl350cl_pc_on.yaml")["workload"]["sessions"])


def test_token_gap_matches_the_design_note():
    assert [round(k2.token_gap(S, T), 2) for T in (4, 8, 16)] == [3.48, 6.19, 10.89]   # the note rounds 10.89 to 10.9


def test_mean_tokens_of_l1():
    assert k2.cold_tokens(S, 8) == 3072 and k2.warm_tokens(S, 8) == 496
    assert k2.cold_tokens(S, 16) == 4096 and k2.warm_tokens(S, 16) == 376


def test_fixed_model_reproduces_reg8_and_the_m5_constants():
    a, b = k2.calibrate_fixed(S)
    assert 1 / (a + b * 3072) == pytest.approx(1.681) and 1 / (a + b * 496) == pytest.approx(4.047)
    assert a == pytest.approx(0.180, abs=0.001) and b == pytest.approx(0.000135, abs=1e-6)


def test_prediction_at_16_turns():
    p = k2.predict(S, 16)
    assert p["prop"]["floor_ratio"] == pytest.approx(0.75) and p["prop"]["R"] == pytest.approx(1.758, abs=0.001)
    assert p["fixed"]["R"] == pytest.approx(1.319, abs=0.002)
    assert k2.predict(S, 8)["fixed"]["R"] == pytest.approx(1.0)


def test_gate_factor_and_labels():
    assert k2.gate_factor() == pytest.approx(1 + 0.2 / 2.4)
    assert k2.gate_factor(3.0, (2.0, 3.0)) == math.inf
    assert k2.gate(1.2) == "widens" and k2.gate(1.05) == "unresolved" and k2.gate(0.98) == "does_not_widen"
    assert k2.gate(math.nan) == "nan"
    assert k2.measured_R(2.4, 1.7, 2.6, 1.3) == pytest.approx((2.6 / 1.3) / (2.4 / 1.7))


def test_e2_configs_have_16_turns_and_the_registered_grids():
    on = load_config(CONFIGS / "sweep_l1t16pl350cl_pc_on.yaml")
    off = load_config(CONFIGS / "sweep_l1t16pl350cl_pc_off.yaml")
    e1 = load_config(CONFIGS / "sweep_l1pl350cl_pc_off.yaml")
    assert on["workload"]["sessions"]["turns"] == off["workload"]["sessions"]["turns"] == 16
    assert tuple(on["sweep"]["rates"]) == k2.E0["warm_grid_16"]
    assert e1["workload"]["sessions"]["turns"] == 8 and e1["workload"]["sessions"]["closed_loop"]
    assert e1["server"]["args"]["--no-enable-prefix-caching"] and off["server"]["args"]["--no-enable-prefix-caching"]
    for c in (on, off, e1):
        assert c["workload"]["sessions"]["closed_loop"] and c["loadgen_force_close"] and c["seed"] == 0


def test_closed_loop_floors_lower_R_a_little():
    f = k2.closed_loop_floors(S)
    p = k2.predict(S, 16)
    for name in ("prop", "fixed"):
        assert f[name]["floor_cl_8"] > 1.681 and f[name]["floor_ratio_cl"] > p[name]["floor_ratio"]
        assert 1.0 < f[name]["R_cl"] < p[name]["R"]
    assert f["fixed"]["R_cl"] == pytest.approx(1.30, abs=0.01) and f["prop"]["R_cl"] == pytest.approx(1.71, abs=0.01)
