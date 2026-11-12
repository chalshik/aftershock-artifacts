"""REG-21 as registered (analysis/k3w.py): the stuck server's uncached-token work rate against the cache-off rate.
Synthetic servers only; no run folder is read. The `truth` server is adapted from the rule F round-2 review's
scripts (docs/drafts/scratchpad-2026-11-12/review2/truth.py): it breaks model F in one way at a time."""
import copy
import heapq
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import analysis.k3 as K3
import analysis.k3w as W
from analysis import modelf_sim as S
from harness.run import load_config

CONFIGS = Path(__file__).resolve().parent.parent / "configs"
MU = 1.681


def cfg(lam=2.0, seed=2, path="burst_l1pl350cl_r2.0_s2.yaml"):
    c = copy.deepcopy(load_config(CONFIGS / path))
    c["workload"]["rate"], c["seed"] = lam, seed
    return c


def truth(c, mu, servers=1, hit_frac=0.0, cost=(0.0, 1.0), gap_scale=1.0):
    """A closed-loop server on the config's own schedule: `servers` first-come-first-served slots, each at speed
    1/servers (a running batch: the total work rate is the same, a request stays `servers` times longer); warm until
    the burst starts, then every later turn finds `hit_frac` of its previous prompt cached."""
    sched = S.schedule(c)
    cold_from = float(c["trigger"]["at_s"])
    a, b = cost
    unit = (a + b * S.LBAR) * mu
    s = sched.sort_values(["session_id", "turn"]).reset_index(drop=True)
    burst = s["burst"].fillna(False).astype(bool).to_numpy()
    sid, turn = s.session_id.to_numpy(), s.turn.to_numpy()
    tp, L = s.t_planned.to_numpy(float), s.prompt_len.to_numpy(float)
    nxt = np.full(len(s), -1)
    same = (sid[1:] == sid[:-1]) & (turn[1:] == turn[:-1] + 1)
    nxt[:-1][same] = np.arange(1, len(s))[same]
    prev = np.zeros(len(s))
    prev[1:][same] = L[:-1][same]
    arr = [(tp[i], i) for i in range(len(s)) if turn[i] == 0 or burst[i]]
    heapq.heapify(arr)
    queue, busy, t, free, n = [], [], 0.0, servers, 0
    rel = np.full(len(s), np.nan)
    first, end, cached = rel.copy(), rel.copy(), np.zeros(len(s))
    while arr or queue or busy:
        if free > 0 and queue:
            r, _, i = heapq.heappop(queue)
            if burst[i] or turn[i] == 0:
                hit = 0.0
            else:
                hit = prev[i] if t < cold_from else hit_frac * prev[i]
            svc = (a + b * (L[i] - hit)) / unit * servers
            rel[i], first[i], end[i], cached[i] = r, t, t + svc, hit   # in service from t to t + svc
            heapq.heappush(busy, (end[i], i))
            free -= 1
            continue
        ta, tb = (arr[0][0] if arr else math.inf), (busy[0][0] if busy else math.inf)
        if ta <= tb:
            t, i = heapq.heappop(arr)
            n += 1
            heapq.heappush(queue, (t, n, i))
        else:
            t, i = heapq.heappop(busy)
            free += 1
            j = nxt[i]
            if j >= 0 and not burst[i]:
                heapq.heappush(arr, (t + gap_scale * (tp[j] - tp[i]), j))
    out = pd.DataFrame({"session_id": sid, "turn": turn, "t_planned": tp, "t_sent": rel, "t_first_token": first,
                        "t_end": end, "prompt_tokens": L.astype(int), "prompt_tokens_planned": L.astype(int),
                        "cached_tokens": cached.astype(int), "burst": burst})
    out["status"] = np.where(np.isnan(end), "unsent", "ok")
    return S.as_run(c, out, name=f"sim_r{c['workload']['rate']}_s{c['seed']}")


@pytest.fixture(scope="module")
def u_off():
    """The reference as REG-21 reads it, on model F's own cache-off server: a saturated open-loop cache-off run."""
    c = copy.deepcopy(load_config(CONFIGS / "sweep_l1pl350_pc_off.yaml"))
    c["workload"]["rate"] = 3.0
    run = S.as_run(c, S.simulate(c, MU))
    return W.work_rate(run, c["workload"]["warmup_s"], c["workload"]["duration_s"])


def test_work_rate_counts_uncached_tokens_of_ok_requests_by_first_token():
    q = pd.DataFrame({"status": ["ok", "ok", "ok", "error", "ok"], "t_first_token": [10.0, 19.9, 20.0, 12.0, 5.0],
                      "t_end": [30.0, 40.0, 50.0, 13.0, 9.0], "prompt_tokens": [3000, 2000, 9999, 7777, 5555],
                      "cached_tokens": [1000, np.nan, 0, 0, 0]})
    run = {"requests": q}
    assert W.work_rate(run, 10.0, 20.0) == pytest.approx((2000 + 2000) / 10.0)
    assert W.work_rate(run, 30.0, 50.0, by="t_end") == pytest.approx((2000 + 2000) / 20.0)
    assert math.isnan(W.work_rate(run, 100.0, 110.0))


def test_the_reference_is_the_all_miss_token_rate(u_off):
    assert u_off == pytest.approx(MU * S.LBAR, rel=0.01)       # 1.681 req/s x 3072 tokens: a saturated server's rate


@pytest.mark.parametrize("lam", [2.0, 2.4])
def test_an_all_miss_fifo_trap_reads_r_one(u_off, lam):
    r = W.row(truth(cfg(lam), MU), u_off, with_readouts=False)
    assert r["allmiss"] and r["r"] == pytest.approx(1.0, abs=0.02)


@pytest.mark.parametrize("servers", [16, 64])
def test_a_running_batch_does_not_move_r(u_off, servers):
    """Round 2's confound: a request that stays in a running batch delays its session's next turn, which moves the
    served-turn mix (and the capacities draft 2 fitted to it). The work rate does not move."""
    assert W.row(truth(cfg(2.0), MU, servers=servers), u_off, with_readouts=False)["r"] == pytest.approx(1.0, abs=0.02)


def test_a_running_batch_of_64_does_move_the_mix():
    c = cfg(2.0)
    one, many = truth(c, MU), truth(c, MU, servers=64)
    a, b = W.window(one)
    stay = many["requests"]
    stay = stay[(stay.t_first_token >= a) & (stay.t_first_token < b)]
    assert float((stay.t_end - stay.t_first_token).median()) > 30.0          # about 64 / 1.681 s in the batch
    assert abs(K3.kbar_obs(many, a, b) - K3.kbar_obs(one, a, b)) > 0.03


def test_longer_think_times_do_not_move_r(u_off):
    assert W.row(truth(cfg(2.0), MU, gap_scale=6.0), u_off, with_readouts=False)["r"] == pytest.approx(1.0, abs=0.02)


def test_a_fixed_cost_per_turn_moves_r_by_under_two_percent(u_off):
    """With 0.18 s + 0.135 ms per token the token rate depends a little on the mean served prompt."""
    r = W.row(truth(cfg(2.0), MU, cost=(0.18, 0.000135)), u_off, with_readouts=False)["r"]
    assert abs(r - 1.0) < 0.02


@pytest.mark.parametrize("mu, side", [(1.85, "high"), (1.55, "low")])
def test_a_trap_faster_or_slower_than_the_cache_off_server_is_outside(u_off, mu, side):
    rows = [W.row(truth(cfg(2.0, sd), mu), u_off, with_readouts=False) for sd in (2, 3, 4)]
    j = W.judge(rows, loads=False)
    assert j["J1"] == "outside" and j["J1_side"] == side
    assert j["median_r"] == pytest.approx(mu / MU, abs=0.02)


def test_a_work_rate_that_depends_on_load_fails_J2_alone(u_off):
    rows = [W.row(truth(cfg(2.0, sd), 1.64), u_off, with_readouts=False) for sd in (2, 3)]
    rows += [W.row(truth(cfg(2.4, sd), 1.75), u_off, with_readouts=False) for sd in (2, 3)]
    j = W.judge(rows)
    assert j["J1"] == "inside" and j["J2"] == "outside"
    assert j["spread"] == pytest.approx((1.75 - 1.64) / MU, abs=0.02)


def test_partial_hits_fail_the_all_miss_precondition(u_off):
    r = W.row(truth(cfg(2.0), MU, hit_frac=0.3), u_off, with_readouts=False)
    assert r["reuse_W"] == pytest.approx(0.3, abs=0.02) and not r["allmiss"]
    j = W.judge([r] * 3, loads=False)
    assert j["n"] == 0 and j["J1"] == "undefined" and len(j["left_out"]) == 3


def _r(lam, r, allmiss=True, name=None):
    return {"run": name or f"x_r{lam}_{r}", "lam": lam, "reuse_W": 0.0, "allmiss": allmiss, "U": 1.0, "r": r}


def test_judge_labels_and_what_it_leaves_out():
    j = W.judge([_r(2.0, 1.03), _r(2.0, 1.05), _r(2.4, 1.01), _r(2.4, 1.02), _r(2.2, 1.30)])
    assert j["J1"] == "inside" and j["median_r"] == pytest.approx(1.03)
    assert j["group_medians"] == {"2.0": pytest.approx(1.04), "2.4": pytest.approx(1.015)}   # 2.2 has one run: unused
    assert j["J2"] == "inside" and j["spread"] == pytest.approx(0.025)
    assert W.judge([_r(2.0, 1.0), _r(2.0, 1.2)])["J1"] == "undefined"                        # fewer than 3 runs
    assert W.judge([_r(2.0, 1.0), _r(2.0, 1.0), _r(2.0, 1.0)])["J2"] == "undefined"          # one load group
    j = W.judge([_r(2.0, 1.06), _r(2.0, 1.07), _r(2.4, 1.08), _r(2.4, math.nan), _r(2.4, 0.5, allmiss=False)])
    assert j["J1"] == "outside" and j["J1_side"] == "high" and j["n"] == 3 and len(j["left_out"]) == 2
    assert "J2" not in W.judge([_r(2.0, 1.0)] * 3, loads=False)


def test_exactly_at_the_tolerance_is_inside():
    assert W.judge([_r(2.0, 1.05)] * 3, loads=False)["J1"] == "inside"
    assert W.judge([_r(2.0, 0.9499)] * 3, loads=False)["J1"] == "outside"


def test_decode_residence_in_the_replay_keeps_the_work_and_shifts_the_mix():
    c = cfg(2.0)
    plain, dec = S.simulate(c, MU), S.simulate(c, MU, decode_s=40.0)
    assert S.simulate(c, MU, decode_s=0.0).equals(plain)                    # 0 is model F's trajectory, unchanged
    a, b = W.window(S.as_run(c, plain))
    rp, rd = S.as_run(c, plain), S.as_run(c, dec)
    assert W.work_rate(rd, a, b) == pytest.approx(W.work_rate(rp, a, b), rel=0.02)
    assert np.allclose((dec.t_end - dec.t_first_token).dropna().to_numpy(), 40.0)
    assert K3.kbar_obs(rd, a, b) != pytest.approx(K3.kbar_obs(rp, a, b), abs=0.02)


def test_table_on_fake_runs(monkeypatch, u_off):
    runs = {f"2026-fake_burst_l1pl350cl_r{lam}_s{sd}": truth(cfg(lam, sd), MU) for lam in (2.0, 2.4) for sd in (2, 3)}
    for n, r in runs.items():
        r["dir"] = Path(n)
    monkeypatch.setitem(W.REG21, "batch1", tuple(runs) + ("2026-fake_missing",))
    monkeypatch.setattr(W, "find_runs", lambda pattern: list(runs.values()))
    monkeypatch.setattr(W, "reference", lambda: {"mean": u_off, "n": 5})
    monkeypatch.setattr(W, "select", lambda rs: (rs[:-1], [{"run": rs[-1]["dir"].name, "cold_backlogged": False}]))
    monkeypatch.setattr(W, "readouts", lambda run: {"stub": True})
    t = W.reg21_table(1)
    assert t["missing_or_invalid"] == ["2026-fake_missing"] and len(t["rows"]) == 3
    assert t["not_cold_backlogged"][0]["cold_backlogged"] is False
    assert t["judged"]["J1"] == "inside" and t["judged"]["J2"] == "undefined"     # 2.4 is left with one run
    assert "J2" not in W.reg21_table(2)["judged"]


def test_readouts_on_a_run_without_metrics(u_off):
    """Every reported readout is computed, or NaN / None where the run has no scrapes; nothing raises."""
    r = W.row(truth(cfg(2.0), MU, servers=64), u_off)
    ro = r["readouts"]
    assert ro["residence_s"] > 30 and math.isnan(ro["running"]) and ro["shock"] is None
    assert ro["X_all"] == pytest.approx(ro["X_session"], abs=0.2) and 3.5 < ro["kbar"] < 4.6
    assert set(ro["replay_at_floor"]) == {"prop_plain", "prop_residence", "fixed_plain", "fixed_residence"}
    assert ro["replay_at_floor"]["prop_residence"]["U"] == pytest.approx(MU * S.LBAR, rel=0.02)
