"""analysis/k1.py (REG-20 draft), stats.fisher_one_sided and k1.mcnemar_one_sided, on synthetic inputs and configs
only (no run folders)."""
import fnmatch
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import analysis.k1 as K
from analysis.stats import fisher_one_sided
from harness.run import load_config
from harness.workload import build_schedule

CONFIGS = Path(__file__).resolve().parents[1] / "configs"
VERDICT = {"baseline_s": 600, "watch_s": 3000, "end_s": 600, "stuck_hit_drop": 0.06, "recovered_hit_drop": 0.06,
           "recovered_q_excess": 1.0}


def make_run(reuse_after=0.0, q_after=120.0, kv_after=0.95, gap_at=None, name="synthetic", hit_after=None):
    """Sessions start every 4 s, 8 turns 5 s apart (2 req/s), prompts 2176 + 256 k. Before the burst's end (1080 s)
    every later turn reuses its whole previous prompt; after it, `reuse_after` of it. Server: hit 0.8, empty line,
    KV 0.5 before; after, hit `hit_after` (default: `reuse_after`), `q_after`, `kv_after`."""
    t = np.arange(0.0, 4081.0)
    after = t >= 1080
    h = reuse_after if hit_after is None else hit_after
    m = pd.DataFrame({"t": t, "vllm:prefix_cache_hits_total": np.cumsum(np.where(after, 100 * h, 80.0)),
                      "vllm:prefix_cache_queries_total": 100.0 * (t + 1),
                      "vllm:num_requests_waiting": np.where(after, q_after, 0.0), "vllm:num_requests_running": 30.0,
                      "vllm:kv_cache_usage_perc": np.where(after, kv_after, 0.5)})
    if gap_at is not None:
        m = m[(m.t < gap_at) | (m.t > gap_at + 30)]
    rows = []
    for sid, t0 in enumerate(np.arange(0.0, 4040.0, 4.0)):
        for k in range(8):
            ts = t0 + 5 * k
            prev = 2176 + 256 * (k - 1)
            share = 1.0 if ts + 0.3 < 1080 else reuse_after
            rows.append({"session_id": sid, "turn": k, "t_planned": ts, "t_sent": ts, "t_first_token": ts + 0.3,
                         "t_end": ts + 2.0, "status": "ok", "ttft": 0.3, "prompt_tokens": 2176 + 256 * k,
                         "prompt_tokens_planned": 2176 + 256 * k, "cached_tokens": 0 if k == 0 else int(share * prev)})
    cfg = {"trigger": {"kind": "burst", "at_s": 900, "duration_s": 180, "prompt_tokens": 2944}, "verdict": VERDICT,
           "slo": {"ttft_s": 1.0}, "checks": {"max_scrape_gap_s": 2.0}}
    return {"cfg": cfg, "metrics": m, "requests": pd.DataFrame(rows), "dir": Path(name)}


WARM = dict(reuse_after=1.0, q_after=0.0, kv_after=0.5)


# ---------------------------------------------------------------- tests

@pytest.mark.parametrize("k1, p", [(2, 0.222), (3, 0.083), (4, 0.024), (5, 0.004)])
def test_fisher_against_zero_of_five(k1, p):
    assert fisher_one_sided(k1, 5, 0, 5) == pytest.approx(p, abs=5e-4)


def test_fisher_edges():
    assert fisher_one_sided(0, 5, 0, 5) == 1.0
    assert fisher_one_sided(5, 5, 1, 5) == pytest.approx(6 / 252)
    assert fisher_one_sided(3, 3, 0, 3) == pytest.approx(0.05)
    with pytest.raises(ValueError):
        fisher_one_sided(6, 5, 0, 5)


def test_mcnemar():
    assert K.mcnemar_one_sided(5, 0) == pytest.approx(1 / 32)
    assert K.mcnemar_one_sided(4, 0) == pytest.approx(1 / 16)
    assert K.mcnemar_one_sided(5, 1) == pytest.approx(7 / 64)
    assert K.mcnemar_one_sided(0, 0) == 1.0


# ---------------------------------------------------------------- readout

def test_windows_follow_the_burst_config():
    assert K.windows(make_run()["cfg"]) == {"base": (300.0, 900.0), "end": (3480.0, 4080.0)}


def test_reuse_is_whole_prefix_when_warm_and_zero_when_cold():
    r = make_run()
    assert K.reuse(r, 300, 900) == pytest.approx(1.0) and K.reuse(r, 3480, 4080) == 0.0
    assert math.isnan(K.reuse(r, 5000, 6000))


def test_reuse_ignores_the_request_mix():
    """Review T1: extra first turns lower the server hit rate but not the reuse of later turns."""
    r = make_run(**{**WARM, "hit_after": 0.70})
    s = K.cold_backlogged(r)
    assert s["end"]["hit"] == pytest.approx(0.70, abs=0.01) and s["reuse"]["end"] == pytest.approx(1.0)
    assert s["cold_backlogged"] is False and s["recovered"] is True


def test_cold_full_backlogged_run_is_cold_backlogged():
    s = K.cold_backlogged(make_run())
    assert s["cold_backlogged"] is True and all(s["parts"].values()) and s["recovered"] is False


def test_each_part_is_needed():
    assert K.cold_backlogged(make_run(reuse_after=1.0))["parts"]["reuse_cold"] is False
    assert K.cold_backlogged(make_run(q_after=0.5))["parts"]["backlogged"] is False
    assert K.cold_backlogged(make_run(kv_after=0.85))["parts"]["kv_full"] is False


def test_partial_is_neither_cold_nor_recovered():
    """Review T2: a long line with a small reuse drop is not a recovery."""
    s = K.cold_backlogged(make_run(reuse_after=0.96, q_after=200.0, kv_after=0.95))
    assert s["cold_backlogged"] is False and s["recovered"] is False


def test_an_uncovered_window_is_none():
    s = K.cold_backlogged(make_run(gap_at=3600))
    assert s["cold_backlogged"] is None and s["recovered"] is None


def test_sessions_in_service():
    r = make_run()
    # a session lasts 37 s (7 gaps of 5 s plus a 2 s reply), one starts every 4 s
    assert K.sessions_in_service(r, 300, 900) == pytest.approx(37 / 4, abs=0.6)
    r["requests"].loc[r["requests"].session_id == 100, "t_end"] = np.nan   # an unfinished session stays in service
    assert K.sessions_in_service(r, 3000, 3100) == pytest.approx(37 / 4 + 1, abs=0.6)


def test_mechanism_contrast():
    r = make_run(**WARM)
    q = r["requests"]
    late = (q.turn > 0) & (q.t_first_token >= 1080) & (q.t_first_token < 1680)
    q.loc[late & (q.session_id % 2 == 0), "t_first_token"] -= 3.5        # sent before the previous turn's end
    q.loc[late & (q.session_id % 2 == 1), "cached_tokens"] = 0           # idle prefixes evicted
    r["cfg"]["workload"] = {"warmup_s": 0, "duration_s": 4080}
    m = K.mechanism(r)
    assert m["overlap"] == pytest.approx(1.0) and m["reuse_held"] == pytest.approx(1.0) and m["reuse_idle"] == 0.0
    assert m["shown"] and m["overlap_base"] == 0.0


# ---------------------------------------------------------------- one open seed

@pytest.fixture
def quiet(monkeypatch):
    monkeypatch.setattr(K, "readouts", lambda run: {})
    monkeypatch.setattr(K, "mechanism", lambda run: {"shown": True})


def test_open_seed_labels(quiet):
    warm, cold = make_run(**WARM), make_run()
    assert K.open_seed(warm, None)["label"] == "recovered_open"
    assert K.open_seed(make_run(reuse_after=0.96, q_after=200.0), None)["label"] == "partial_open"
    assert K.open_seed(cold, None)["label"] == "pending_control"
    assert K.open_seed(cold, warm)["label"] == "stuck_open"
    assert K.open_seed(cold, make_run(name="control"))["label"] == "overload_open"
    assert K.open_seed(cold, make_run(gap_at=3600))["label"] == "cold_control"
    assert K.open_seed(make_run(gap_at=3600), None)["label"] == "unclear"
    assert K.open_seed(None, None, lost=True)["label"] == "lost_open"
    assert K.open_seed(None, None)["label"] == "not_run"


# ---------------------------------------------------------------- decision rules

def rows(labels, shown=True):
    return [{"label": lab, "mechanism": {"shown": shown}} for lab in labels]


REC = "recovered_open"


@pytest.mark.parametrize("test, p", [("fisher", 1 / 252), ("mcnemar", 1 / 32)])
def test_supports_five_of_five_against_none(test, p):
    a = K.k1_outcome([True] * 5, rows([REC] * 5), test)
    assert a["outcome"] == "supports" and a["p"] == pytest.approx(p)


def test_four_of_five_passes_fisher_not_mcnemar():
    c = [True, True, True, True, False]
    assert K.k1_outcome(c, rows([REC] * 5), "fisher")["outcome"] == "supports"
    assert K.k1_outcome(c, rows([REC] * 5), "mcnemar")["outcome"] == "inconclusive"


def test_supports_needs_every_warm_open_run_recovered():
    assert K.k1_outcome([True] * 5, rows([REC] * 4 + ["partial_open"]), "fisher")["outcome"] == "inconclusive"


def test_mechanism_must_show_in_every_warm_open_run():
    r = rows([REC] * 5)
    r[2]["mechanism"] = {"shown": False}
    assert K.k1_outcome([True] * 5, r, "fisher")["outcome"] == "supports_no_mechanism"


def test_lost_and_unreadable_controls_count_as_cold():
    a = K.k1_outcome([True] * 5, rows([REC] * 3 + ["lost_open", "cold_control"]), "fisher")
    assert a["k_open"] == 2 and a["outcome"] == "inconclusive"


def test_refutation_needs_three_open_stuck():
    assert K.k1_outcome([True] * 5, rows(["stuck_open"] * 3 + [REC] * 2))["outcome"] == "refutes"
    assert K.k1_outcome([True] * 5, rows(["stuck_open", "lost_open", "cold_control", REC, REC]))["outcome"] == "refutes"
    # one event per arm is not a refutation (review T4)
    assert K.k1_outcome([True, False, False, False, False], rows(["stuck_open"] + [REC] * 4))["outcome"] == "inconclusive"


def test_states_that_cannot_decide():
    assert K.k1_outcome([False] * 5, rows([REC] * 5))["outcome"] == "closed_not_cold"
    assert K.k1_outcome([True], rows([REC]))["outcome"] == "too_few"
    assert K.k1_outcome([True] * 5, rows([REC] * 4 + ["pending_control"]))["outcome"] == "pending_controls"
    assert K.k1_outcome([True] * 5, rows([REC] * 4 + ["overload_open"]))["outcome"] == "open_arm_overload"


def test_unclear_and_missing_seeds_leave_n_and_are_listed():
    a = K.k1_outcome([True, True, None, True, True], rows([REC, REC, REC, "unclear", "not_run"]), "fisher")
    assert a["n"] == 2 and a["dropped"] == [2, 3, 4]


def test_arm_a_gate_on_the_closed_count():
    assert K.a_may_start([True] * 5, "mcnemar")["may_start"]
    assert not K.a_may_start([True] * 4 + [False], "mcnemar")["may_start"]
    assert K.a_may_start([True] * 4 + [False], "fisher")["may_start"]
    assert not K.a_may_start([True, True, True, False, False], "fisher")["may_start"]
    assert not K.a_may_start([True, None, None, None, None], "fisher")["may_start"]


def test_arm_b_rules():
    assert K.b_may_start(K.k1_outcome([True] * 5, rows([REC] * 5)))
    assert not K.b_may_start(K.k1_outcome([False] * 5, rows([REC] * 5)))
    assert K.b_outcome(rows([REC] * 3)) == "headroom_weakened"
    assert K.b_outcome(rows([REC, REC, "stuck_open"])) == "headroom_open"
    assert K.b_outcome(rows([REC, REC, "partial_open"])) == "headroom_open"
    assert K.b_outcome(rows([REC, REC])) == "incomplete"
    assert K.b_outcome(rows([REC, REC, "pending_control"])) == "incomplete"


def test_drift():
    assert K.drift({"cold_backlogged": True}, make_run())["agrees"] is True
    assert K.drift({"cold_backlogged": True}, make_run(**WARM))["agrees"] is False
    assert K.drift({"cold_backlogged": True}, None)["agrees"] is None


# ---------------------------------------------------------------- run lookup (review: the λ = 2.0 pattern bug)

@pytest.mark.parametrize("lam, seed", [(2.0, 15), (2.5, 17)])
@pytest.mark.parametrize("control", [False, True])
def test_patterns_match_the_config_names(lam, seed, control):
    kind = "stage2_control" if control else "burst"
    name = f"20261113-000000_{kind}_l1pl350ol_r{lam:.1f}_w3000_s{seed}"
    assert load_config(CONFIGS / f"{name.split('_', 1)[1]}.yaml")["name"] == name.split("_", 1)[1]
    assert fnmatch.fnmatch(name, K.open_pattern(lam, seed, control))
    assert fnmatch.fnmatch(f"20261112-050920_burst_l1pl350cl_r2.0_w3000_s{seed}", K.closed_pattern(seed))


def test_reg20_table_on_fake_runs(monkeypatch, quiet):
    """The table end to end on fake folders: valid closed and open runs, an invalid one, a drift rerun."""
    cold, warm = make_run(), make_run(**WARM)
    folders = {}
    for sd in (15, 16, 17, 18, 19):
        folders[f"20261112-0000{sd}_burst_l1pl350cl_r2.0_w3000_s{sd}"] = (cold, True)
        folders[f"20261113-0000{sd}_burst_l1pl350ol_r2.0_w3000_s{sd}"] = (warm, True)
    folders["20261113-1000_burst_l1pl350ol_r2.0_w3000_s19"] = (warm, False)          # an invalid attempt as well
    folders["20261113-2000_burst_l1pl350cl_r2.0_w3000_s15_drift"] = (cold, True)

    def find_runs(pattern="*", valid_only=True):
        out = [{**run, "dir": Path(n), "checks": {"valid": ok}} for n, (run, ok) in sorted(folders.items())
               if fnmatch.fnmatch(n, pattern)]
        return [r for r in out if not valid_only or r["checks"]["valid"]]
    monkeypatch.setattr(K, "find_runs", find_runs)
    t = K.reg20_table()
    assert [r["cold_backlogged"] for r in t["closed"]] == [True] * 5
    assert [r["label"] for r in t["open_a"]] == [REC] * 5
    assert t["start"]["may_start"] and t["a"]["outcome"] == "supports" and t["b_may_start"]
    assert t["b"] == "not_run" and t["drift"]["agrees"] is True


# ---------------------------------------------------------------- configs

def _sched(name):
    c = load_config(CONFIGS / f"{name}.yaml")
    return c, build_schedule(c["workload"], seed=c["seed"], trigger=c.get("trigger"))[0]


@pytest.mark.parametrize("seed", [15, 16, 17, 18, 19])
@pytest.mark.parametrize("kind", ["burst", "stage2_control"])
def test_open_arm_a_has_its_closed_partners_schedule(kind, seed):
    co, so = _sched(f"{kind}_l1pl350ol_r2.0_w3000_s{seed}")
    cc, sc = _sched(f"{kind}_l1pl350cl_r2.0_w3000_s{seed}")
    assert co["workload"]["sessions"]["closed_loop"] is False and cc["workload"]["sessions"]["closed_loop"] is True
    cols = ["t_planned", "session_id", "turn", "prompt_len"]
    pd.testing.assert_frame_equal(so[cols].reset_index(drop=True), sc[cols].reset_index(drop=True))
    strip = lambda c: {**c, "name": None, "workload": {**c["workload"], "sessions": {**c["workload"]["sessions"],
                                                                                    "closed_loop": None}}}
    assert strip(co) == strip(cc)


@pytest.mark.parametrize("seed", [15, 16, 17])
@pytest.mark.parametrize("kind", ["burst", "stage2_control"])
def test_open_arm_b_differs_from_arm_a_only_in_rate(kind, seed):
    b = load_config(CONFIGS / f"{kind}_l1pl350ol_r2.5_w3000_s{seed}.yaml")
    a = load_config(CONFIGS / f"{kind}_l1pl350ol_r2.0_w3000_s{seed}.yaml")
    assert b["workload"]["rate"] == 2.5 and a["workload"]["rate"] == 2.0
    assert {**b, "name": None, "workload": {**b["workload"], "rate": None}} == \
           {**a, "name": None, "workload": {**a["workload"], "rate": None}}


def test_drift_config_is_its_partner_renamed():
    d = load_config(CONFIGS / f"{K.REG20['drift_cfg']}.yaml")
    p = load_config(CONFIGS / "burst_l1pl350cl_r2.0_w3000_s15.yaml")
    assert {**d, "name": None} == {**p, "name": None}
