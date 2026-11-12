"""analysis/modelf_sim.py and analysis/k3.py (REG-21 draft, second version) on synthetic runs and on replays of the
study's configs only (no run folders)."""
import copy
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import analysis.k3 as K3
from analysis import modelf_sim as S
from harness.run import load_config
from tests.test_k1 import WARM, make_run

CONFIGS = Path(__file__).resolve().parents[1] / "configs"
BURST20 = CONFIGS / "burst_l1pl350cl_r2.0_s2.yaml"
BURST24 = CONFIGS / "burst_l1pl350cl_r2.4_s1.yaml"


def cfg_of(path, **wl):
    c = copy.deepcopy(load_config(path))
    c["workload"].update(wl)
    return c


def sim_run(cfg, mu, cost=(0.0, 1.0), hit_after=0.0, name="sim"):
    """A run-like dict from model F's replay; `hit_after` > 0 makes later turns after the burst keep that share of
    their previous prompt cached (a server that is not all-miss)."""
    reqs = S.simulate(cfg, mu, cost).sort_values(["session_id", "turn"]).reset_index(drop=True)
    if hit_after:
        prev = reqs.groupby("session_id").prompt_tokens.shift().fillna(0)
        late = (reqs.turn > 0) & (reqs.t_first_token >= cfg["trigger"]["at_s"]) & ~reqs.burst
        reqs.loc[late, "cached_tokens"] = (hit_after * prev[late]).astype(int)
    return S.as_run(cfg, reqs, name)


# ---------------------------------------------------------------- the replay

def test_replay_serves_every_request_once_one_at_a_time_in_release_order():
    cfg = load_config(BURST20)
    sch = S.schedule(cfg)
    out = S.simulate(cfg, 1.681, sched=sch)
    assert len(out) == len(sch) and (out.status == "ok").all()
    o = out.sort_values("t_first_token")
    assert (o.t_first_token.to_numpy()[1:] >= o.t_end.to_numpy()[:-1] - 1e-9).all()     # one at a time
    assert (np.diff(o.t_sent.to_numpy()) >= -1e-9).all()                                 # FIFO by release time


def test_closed_loop_release_is_previous_end_plus_the_schedule_gap():
    cfg = load_config(BURST20)
    out = S.simulate(cfg, 1.681).sort_values(["session_id", "turn"])
    s = out[~out.burst]
    g = s.groupby("session_id")
    prev_end, prev_tp = g.t_end.shift(), g.t_planned.shift()
    later = s.turn > 0
    assert np.allclose(s.t_sent[later], (prev_end + s.t_planned - prev_tp)[later])
    assert np.allclose(s.t_sent[s.turn == 0], s.t_planned[s.turn == 0])


def test_costs_warm_then_all_miss():
    cfg = load_config(BURST20)
    out = S.simulate(cfg, 1.681)
    svc = out.t_end - out.t_first_token
    unit = 3072 * 1.681
    pre = out[(out.t_first_token < 900) & (out.turn > 0) & ~out.burst]
    post = out[out.t_first_token >= 900]
    assert np.allclose(svc[pre.index], (pre.prompt_tokens - pre.cached_tokens) / unit)
    assert (pre.cached_tokens > 0).all() and (post.cached_tokens == 0).all()
    assert np.allclose(svc[post.index], post.prompt_tokens / unit)


def test_caching_off_config_misses_from_the_start():
    out = S.simulate(cfg_of(CONFIGS / "sweep_l1pl350_pc_off.yaml", rate=2.0), 1.681)
    assert (out.cached_tokens == 0).all()


# ---------------------------------------------------------------- fitted floors

@pytest.mark.parametrize("path, mu", [(BURST20, 1.681), (BURST20, 1.78), (BURST24, 1.70)])
def test_fit_reads_a_replay_back_to_its_floor(path, mu):
    run = sim_run(load_config(path), mu)
    f = K3.fit(run)["prop"]
    # One trajectory's kbar departs from its smooth trend by about 0.01-0.02, so mu_k reads back to about +-0.02
    # (errors -0.025 to +0.021 on the four cases here); mu_X, a smooth curve, to +-0.006.
    assert f["mu_k_status"] == "ok" and f["mu_k"] == pytest.approx(mu, abs=0.03)
    assert f["mu_X_status"] == "ok" and f["mu_X"] == pytest.approx(mu, abs=0.006)
    assert f["at_mu_k"]["d"] == pytest.approx(K3.observed(run)["d"], abs=0.03)   # d jitters as kbar does


def test_fit_with_a_larger_burst_still_reads_back():
    cfg = load_config(BURST20)
    cfg["trigger"]["rate"] = 6.0
    f = K3.fit(sim_run(cfg, 1.70))["prop"]
    assert f["mu_k"] == pytest.approx(1.70, abs=0.03) and f["mu_X"] == pytest.approx(1.70, abs=0.015)


def test_wrong_cost_model_moves_the_fit_little():
    f = K3.fit(sim_run(load_config(BURST20), 1.70, cost=K3.REG21["costs"]["fixed"]))
    assert f["fixed"]["mu_k"] == pytest.approx(1.70, abs=0.03)
    assert abs(f["prop"]["mu_k"] - 1.70) < 0.05


def test_partial_hits_are_kept_out_by_the_all_miss_precondition():
    cfg = load_config(BURST20)
    assert K3.observed(sim_run(cfg, 1.681, hit_after=0.5))["reuse_W"] > K3.REG21["allmiss_reuse_max"]
    assert K3.observed(sim_run(cfg, 1.681))["reuse_W"] == 0.0


def test_long_run_values_are_not_the_window_values():
    # Review T1: the replay of a 900 s window differs from model F's long-run value; the judged items use the replay.
    o = K3.observed(sim_run(load_config(BURST20), 1.681))
    assert abs(o["d"] - K3.long_run(o["lam_W"])["d"]) > 0.03


# ---------------------------------------------------------------- J3's premise and E1

def _sweep(closed: bool):
    out = []
    for r in (2.0, 3.0):
        c = cfg_of(CONFIGS / "sweep_l1pl350_pc_off.yaml", rate=r)
        c["workload"]["sessions"]["closed_loop"] = closed
        out.append(c)
    return out


def test_open_loop_cache_off_replay_saturates_at_mu_and_closed_loop_above_it():
    st = K3.e1_statistic(_sweep(False), 1.681, (0.0, 1.0))
    assert st["status"] == "ok" and st["statistic"] == pytest.approx(1.681, rel=0.02)
    assert K3.e1_statistic(_sweep(True), 1.681, (0.0, 1.0))["statistic"] > st["statistic"]


def test_e1_prediction_and_hit():
    judged = {n: {"J3": {"pooled_mu_k": 1.90}} for n in K3.REG21["costs"]}
    p = K3.e1_prediction(_sweep(True), judged)
    assert p["prop"]["predicted"] > p["prop"]["at_open_loop_floor"] + 0.08 and p["prop"]["separates"]
    assert K3.e1_hit(p, p["prop"]["predicted"] + 0.05) and not K3.e1_hit(p, p["prop"]["at_open_loop_floor"])


# ---------------------------------------------------------------- judging

def _row(name, lam, mk, mx, allmiss=True):
    f = {"mu_k": mk, "mu_k_status": "ok", "mu_X": mx, "mu_X_status": "ok"}
    return {"run": name, "lam": lam, "allmiss": allmiss, "fit": {"prop": dict(f), "fixed": dict(f)}}


def test_judge_inside_when_one_floor_fits_all():
    j = K3.judge([_row(f"r{i}", lam, 1.70, 1.71) for i, lam in enumerate((2.0, 2.0, 2.2, 2.4, 2.4))])
    assert j["J1"]["label"] == j["J2"]["label"] == j["J3"]["label"] == "inside"


def test_judge_flags_loads_that_disagree_and_a_floor_off_the_open_loop_one():
    j = K3.judge([_row("a", 2.0, 1.68, 1.68), _row("b", 2.0, 1.69, 1.69), _row("c", 2.4, 1.85, 1.86),
                  _row("d", 2.4, 1.86, 1.86)])
    assert j["J1"]["label"] == "outside" and j["J2"]["label"] == "inside"
    j = K3.judge([_row("a", 2.0, 1.82, 1.70), _row("b", 2.4, 1.83, 1.71)])
    assert j["J2"]["label"] == "outside" and j["J3"]["label"] == "outside"


def test_judge_lists_rows_left_out_and_unfitted():
    rows = [_row("a", 2.0, 1.70, 1.70), _row("b", 2.0, 1.70, 1.70, allmiss=False), _row("c", 2.4, math.nan, 1.7)]
    rows[2]["fit"]["prop"]["mu_k_status"] = "multiple"
    j = K3.judge(rows)
    assert j["not_allmiss"] == ["b"] and j["unfitted"] == {"c": ("multiple", "ok")} and j["n_allmiss"] == 2


def test_reg15_is_its_own_group():
    assert K3.group(_row(K3.REG21["apart"][0], 2.2, 1.7, 1.7)).startswith("apart:")
    assert K3.group(_row("x", 2.2, 1.7, 1.7)) == "2.2"


@pytest.mark.parametrize("vals, target, status", [
    ([1.0, 2.0, 3.0], 2.5, "ok"), ([1.0, 2.0, 3.0], 3.5, "target_above_grid_values"),
    ([1.0, 2.0, 3.0], 0.5, "target_below_grid_values"), ([1.0, 3.0, 1.0], 2.0, "multiple"),
    ([1.0, 2.0, 3.0], math.nan, "nan")])
def test_crossing(vals, target, status):
    c = K3.crossing(np.array([0.0, 1.0, 2.0]), np.array(vals), target)
    assert c["status"] == status
    if status == "ok":
        assert c["mu"] == pytest.approx(1.5)


# ---------------------------------------------------------------- reported readouts

def test_hl_rule_on_cold_and_warm_runs():
    h = K3.hl_rule(make_run(reuse_after=0.0))
    assert h["first_degraded"] == 0 and h["persistently_degraded"]
    assert not K3.hl_rule(make_run(**WARM))["persistently_degraded"]


def test_counter_rate_and_restart_flag():
    m = pd.DataFrame({"t": np.arange(0.0, 100.0), "vllm:num_preemptions_total": np.arange(0.0, 100.0) * 2})
    assert K3.counter_rate({"metrics": m}, "vllm:num_preemptions_total", 10, 50) == pytest.approx(2.0)
    m2 = m.copy()
    m2.loc[30, "vllm:num_preemptions_total"] = 0.0
    assert math.isnan(K3.counter_rate({"metrics": m2}, "vllm:num_preemptions_total", 10, 50))
    assert math.isnan(K3.counter_rate({"metrics": pd.DataFrame()}, "x", 0, 1))


def test_d_obs_counts_last_turns_over_starts():
    reqs = pd.DataFrame([
        {"session_id": 0, "turn": 0, "t_planned": 10.0, "t_end": 20.0, "status": "ok", "prompt_tokens_planned": 2176},
        {"session_id": 1, "turn": 0, "t_planned": 15.0, "t_end": np.nan, "status": "ok",
         "prompt_tokens_planned": 2176},
        {"session_id": 2, "turn": 7, "t_planned": 5.0, "t_end": 30.0, "status": "ok", "prompt_tokens_planned": 3968},
        {"session_id": 3, "turn": 7, "t_planned": 5.0, "t_end": 30.0, "status": "error",
         "prompt_tokens_planned": 3968},
    ])
    run = {"requests": reqs, "cfg": {"trigger": {"kind": "burst", "prompt_tokens": 2944}}}
    assert K3.d_obs(run, 0, 40) == pytest.approx(0.5)
    assert K3.kbar_obs(run, 0, 40) == pytest.approx(4.5)
    assert K3.lam_w(run, 0, 40) == pytest.approx(0.4)


def test_select_keeps_cold_backlogged_runs_only():
    keep, out = K3.select([make_run(name="cold"), make_run(name="warm", **WARM)])
    assert [r["dir"].name for r in keep] == ["cold"] and out[0]["run"] == "warm"


def test_cacheoff_reference_uses_the_floor_runs(monkeypatch):
    r1 = sim_run(load_config(BURST20), 1.681)
    runs = [{"dir": Path(f"sweep_r{rate}"), "requests": r1["requests"],
             "cfg": {"workload": {"rate": rate, "warmup_s": 1680.0, "duration_s": 2580.0}}} for rate in (1.5, 2.0, 3.0)]
    monkeypatch.setattr(K3, "find_runs", lambda pattern: runs)
    assert sorted(K3.cacheoff_uncached()["runs"]) == ["sweep_r2.0", "sweep_r3.0"]


def test_batch1_ids_are_closed_loop_l1_burst_runs():
    ids = K3.REG21["batch1"]
    assert len(ids) == len(set(ids)) == 13
    assert all("_l1pl350cl_" in i and ("_burst_" in i or "_confirm_" in i) for i in ids)
    assert set(K3.REG21["apart"]) <= set(ids)


def test_local_fit_on_a_jittered_curve():
    g = np.round(np.arange(1.3, 2.401, 0.01), 6)
    rng = np.random.default_rng(0)
    v = 4.0 + 1.1 * (g - 1.3) + rng.normal(0, 0.008, len(g))
    f = K3.local_fit(g, v, 4.0 + 1.1 * 0.4)
    assert f["status"] == "ok" and f["mu"] == pytest.approx(1.70, abs=0.015) and 0.004 < f["jitter"] < 0.012
    assert K3.crossing(g, v, 4.0 + 1.1 * 0.4)["status"] == "multiple"         # why the sign-change search is not used
    assert K3.local_fit(g, 5.0 - g, 3.3)["status"] == "no_slope"
    assert K3.local_fit(g, v, 9.0)["status"] == "edge"


def test_overall_label_is_inside_under_either_cost_model():
    j = {"prop": {"J1": {"label": "outside"}, "J2": {"label": "inside"}, "J3": {"label": "nan"}},
         "fixed": {"J1": {"label": "inside"}, "J2": {"label": "outside"}, "J3": {"label": "nan"}}}
    assert K3.overall(j) == {"J1": "inside", "J2": "inside", "J3": "nan"}
    j["fixed"]["J1"]["label"] = "outside"
    j["prop"]["J3"]["label"] = "outside"
    assert K3.overall(j) == {"J1": "outside", "J2": "inside", "J3": "outside"}
