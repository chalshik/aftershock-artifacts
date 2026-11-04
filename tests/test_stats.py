import pytest

from analysis.stats import cell, cp_upper


@pytest.mark.parametrize("n, one, two", [(3, 0.6316, 0.7076), (6, 0.3930, 0.4593), (30, 0.0950, 0.1157)])
def test_zero_successes_has_the_closed_form(n, one, two):
    assert cp_upper(0, n) == pytest.approx(1 - 0.05 ** (1 / n), abs=1e-6) == pytest.approx(one, abs=1e-4)
    assert cp_upper(0, n, one_sided=False) == pytest.approx(two, abs=1e-4)


def test_known_value_with_successes():
    # Clopper–Pearson two-sided 95 % for 1 of 10: upper 0.4450 (standard tables)
    assert cp_upper(1, 10, one_sided=False) == pytest.approx(0.4450, abs=1e-3)


def test_all_successes_and_bad_input():
    assert cp_upper(3, 3) == 1.0
    with pytest.raises(ValueError):
        cp_upper(4, 3)


def test_cell_text():
    assert cell(0, 3) == "0 of 3 (≤ 0.63, one-sided 95 %)"


def test_poisson_rate_upper():
    from analysis.stats import poisson_rate_upper
    assert poisson_rate_upper(0, 1.0) == pytest.approx(2.9957, abs=1e-3)   # -ln(0.05)
    assert poisson_rate_upper(10, 1.0) == pytest.approx(17.0, abs=0.05)    # standard table, one-sided 95 %
    assert poisson_rate_upper(270, 60.0) > 4.5


def test_poisson_rate_upper_large_counts():
    """exp(-mu) underflows near mu = 745; the bound must keep rising with n (REG-1 [CORR], 2026-11-04)."""
    from analysis.stats import poisson_rate_upper
    vals = [poisson_rate_upper(n, 120.0, 0.99) for n in (600, 714, 861, 2000)]
    assert all(b > a for a, b in zip(vals, vals[1:])) and all(v > n / 120 for v, n in zip(vals, (600, 714, 861, 2000)))
    # normal approximation as a check: n + 2.326 sqrt(n) + ~2
    assert poisson_rate_upper(861, 120.0, 0.99) * 120 == __import__("pytest").approx(861 + 2.326 * 861 ** 0.5 + 2.2, abs=2)
