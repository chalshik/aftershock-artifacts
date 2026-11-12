"""Model F (analysis/modelf.py): the paper's identities, and the L1 values in docs/model.md M5."""
import math

import pytest

from analysis import modelf as mf


def test_survival_and_fixed_turns():
    assert mf.survival([0.5, 0.25, 0.25]) == [1.0, 0.5, 0.25]
    assert mf.fixed_turns(3) == [0.0, 0.0, 1.0]
    assert mf.survival(mf.fixed_turns(3)) == [1.0, 1.0, 1.0]
    with pytest.raises(ValueError):
        mf.survival([0.5, 0.4])
    with pytest.raises(ValueError):
        mf.fixed_turns(0)


def test_l1_prompts():
    assert mf.l1_prompts(8) == [2176 + 256 * k for k in range(8)]
    assert mf.l1_prompts(8)[-1] == 3968


def test_perron_root_solves_its_equation():
    p, c, rho = mf.fixed_turns(8), mf.l1_prompts(8), 1.19
    z = mf.perron_root(p, c, rho)
    s = sum(c)
    assert rho * sum(ck / s * z ** -(k + 1) for k, ck in enumerate(c)) == pytest.approx(1.0, abs=1e-10)
    assert z > 1


def test_below_threshold_is_rejected():
    with pytest.raises(ValueError):
        mf.perron_root(mf.fixed_turns(8), mf.l1_prompts(8), 1.0)


def test_theorem2_decomposition_equals_sessions():
    for p in (mf.fixed_turns(8), [0.1, 0.2, 0.3, 0.4], [0.25] * 4):
        c = [1.0 + 0.5 * k for k in range(len(p))]
        for rho in (1.05, 1.3, 2.0):
            t = mf.trap(p, c, rho)
            assert t.H * t.Gamma == pytest.approx(t.sessions, rel=1e-9)


def test_geometric_turn_count_has_h_one():
    # Theorem 2: H = 1 for a geometric T on {1, 2, ...}; truncated at a large K, H -> 1.
    q, K = 0.2, 400
    p = [q * (1 - q) ** k for k in range(K - 1)] + [(1 - q) ** (K - 1)]   # tail mass P(T >= K) in the last turn
    t = mf.trap(p, [1.0] * K, 1.5)
    assert t.H == pytest.approx(1.0, abs=1e-6)


def test_equal_costs_give_no_cost_factor():
    t = mf.trap(mf.fixed_turns(5), [1.0] * 5, 1.4)
    assert t.Gamma == pytest.approx(1.0)
    assert t.served_prompt == pytest.approx(1.0)


def test_first_order_expansion_near_threshold():
    p, c = mf.fixed_turns(8), mf.l1_prompts(8)
    for eps in (1e-3, 1e-4):
        exact = mf.trap(p, c, 1 + eps).sessions
        assert (exact - mf.first_order(p, c, 1 + eps)) / eps == pytest.approx(0.0, abs=20 * eps)


def test_fixed_turns_give_a_deficit_not_a_premium():
    # The MIRROR case (docs/model.md M5): a fixed turn count puts sessions below the all-miss capacity.
    assert mf.trap(mf.fixed_turns(8), mf.l1_prompts(8), 1.19).sessions < 1.0


def test_corollary3():
    assert mf.drains(1.6, 1.681) and not mf.drains(1.7, 1.681) and not mf.drains(1.681, 1.681)


@pytest.mark.parametrize("rate, sessions, growth, served, req", [
    (2.0, 0.89, 1.56, 0.984, 1.016),
    (2.2, 0.83, 1.53, 0.975, 1.025),
    (2.4, 0.78, 1.51, 0.967, 1.034),
])
def test_l1_values_match_model_md_m5(rate, sessions, growth, served, req):
    # M5's table was computed at rho rounded to two decimals (1.19, 1.31, 1.43); at the exact rho = rate / 1.681 the
    # values agree with M5 to within one unit of its last digit (at 2.2: sessions 0.8353, M5 0.83; served prompt 0.9755,
    # M5 0.975; decisions.md 2026-11-12 [CORR]).
    t = mf.l1(rate, 1.681)
    assert t.sessions == pytest.approx(sessions, abs=0.006)
    assert t.backlog_growth == pytest.approx(growth, abs=0.006)
    assert t.served_prompt == pytest.approx(served, abs=0.001)
    assert t.requests == pytest.approx(req, abs=0.001)


def test_fixed_cost_part_sensitivity():
    # A fixed part per turn (0.18 s + 0.135 ms/token, the alternative in docs/paper/modelf_l1.py) moves sessions, the
    # served prompt and the request rate by under 0.02 but the session backlog growth by about 0.04 (1.563 -> 1.602).
    # docs/model.md M5 first said "less than 0.02" for all four (decisions.md 2026-11-12 [CORR]).
    a = mf.l1(2.0, 1.681)
    b = mf.l1(2.0, 1.681, fixed_cost_s=0.18, per_token_s=0.000135)
    for f in ("sessions", "served_prompt", "requests"):
        assert abs(getattr(a, f) - getattr(b, f)) < 0.02
    assert 0.03 < b.backlog_growth - a.backlog_growth < 0.05
    assert math.isclose(a.rho, 2.0 / 1.681)
