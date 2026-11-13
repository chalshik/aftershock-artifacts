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


def cfg(lam=2.0, seed=2, path="burst_l1pl350cl_r2.0_s2.yaml", steps=None):
    c = copy.deepcopy(load_config(CONFIGS / path))
    c["workload"]["rate"], c["seed"] = lam, seed
    if steps:
        c["workload"]["steps"] = steps
    return c


def with_metrics(run):
    """A scrape per second with the number of requests waiting (sent and not yet in service), so that the busy
    precondition reads the synthetic run as it reads a real one."""
    q = run["requests"]
    q = q[q.status == "ok"]
    t = np.arange(0.0, float(q.t_end.max()) + 1.0, 1.0)
    sent, first = np.sort(q.t_sent.to_numpy(float)), np.sort(q.t_first_token.to_numpy(float))
    wait = np.searchsorted(sent, t, side="right") - np.searchsorted(first, t, side="right")
    run["metrics"] = pd.DataFrame({"t": t, "vllm:num_requests_waiting": wait.astype(float)})
    return run


def truth(c, mu, servers=1, hit_frac=0.0, cost=(0.0, 1.0), gap_scale=1.0, name=None):
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
    return with_metrics(S.as_run(c, out, name=name or f"20261110-000000_sim_r{c['workload']['rate']}_s{c['seed']}"))


def ref_run(rate=3.0, mu=MU, name=None):
    c = copy.deepcopy(load_config(CONFIGS / "sweep_l1pl350_pc_off.yaml"))
    c["workload"]["rate"] = rate
    return with_metrics(S.as_run(c, S.simulate(c, mu), name=name or f"20261107-000000_sweep_l1pl350_pc_off_r{rate:g}"))


@pytest.fixture(scope="module")
def ref():
    """The reference as REG-21 reads it, on model F's own cache-off server: saturated open-loop cache-off runs."""
    return W.reference([ref_run(r) for r in (2.0, 2.5, 3.0, 3.5, 4.0)])


def R(run, ref):
    return W.row(run, ref, with_readouts=False)


# ---------------------------------------------------------------- the statistic

def test_work_rate_counts_uncached_tokens_of_ok_requests_by_first_token():
    q = pd.DataFrame({"status": ["ok", "ok", "ok", "error", "ok"], "t_first_token": [10.0, 19.9, 20.0, 12.0, 5.0],
                      "t_end": [30.0, 40.0, 50.0, 13.0, 9.0], "prompt_tokens": [3000, 2000, 9999, 7777, 5555],
                      "cached_tokens": [1000, np.nan, 0, 0, 0]})
    run = {"requests": q}
    assert W.work_rate(run, 10.0, 20.0) == pytest.approx((2000 + 2000) / 10.0)
    assert W.work_rate(run, 30.0, 50.0, by="t_end") == pytest.approx((2000 + 2000) / 20.0)
    assert math.isnan(W.work_rate(run, 100.0, 110.0))


def test_work_rate_raises_on_an_ok_request_it_cannot_place():
    q = pd.DataFrame({"status": ["ok", "ok"], "t_first_token": [10.0, np.nan], "t_end": [30.0, 40.0],
                      "prompt_tokens": [3000, 2000], "cached_tokens": [0, 0]})
    with pytest.raises(ValueError):
        W.work_rate({"requests": q}, 0.0, 50.0)
    q2 = q.assign(t_first_token=[10.0, 11.0], prompt_tokens=[3000, np.nan])
    with pytest.raises(ValueError):
        W.work_rate({"requests": q2}, 0.0, 50.0)
    q3 = q.assign(status=["ok", "unfinished"])                 # an unfinished request may lack a first token
    assert W.work_rate({"requests": q3}, 0.0, 50.0) == pytest.approx(3000 / 50.0)


def test_the_reference_is_the_all_miss_token_rate(ref):
    assert ref["n"] == 5 and ref["mean"] == pytest.approx(MU * S.LBAR, rel=0.01)   # 1.681 req/s x 3072 tokens
    assert ref["spread"] < 0.01 and ref["mean_without_2.0"] == pytest.approx(ref["mean"], rel=0.005)
    one = next(iter(ref["runs"].values()))
    assert {"rate", "U", "U_by_end", "busy", "running", "waiting", "kv", "preempt_per_s", "redo_share"} <= set(one)
    assert one["busy"] > 0.99


def test_reference_from_run_folders_needs_exactly_the_five_pinned_runs(monkeypatch):
    five = [ref_run(r, name=n) for r, n in zip((2.0, 2.5, 3.0, 3.5, 4.0), W.REG21["ref_runs"])]
    low = ref_run(1.5, name="20261107-082035_sweep_l1pl350_pc_off_r1.5")
    monkeypatch.setattr(W, "find_runs", lambda pattern: five + [low])
    assert W.reference()["n"] == 5                                          # a lower rate is not part of it
    monkeypatch.setattr(W, "find_runs", lambda pattern: five[:4] + [low])
    with pytest.raises(ValueError):
        W.reference()                                                       # one of the five is missing
    again = ref_run(3.0, name="20261108-000000_sweep_l1pl350_pc_off_r3")
    monkeypatch.setattr(W, "find_runs", lambda pattern: five + [again])
    with pytest.raises(ValueError):
        W.reference()                                                       # a second valid run at a rate


@pytest.mark.parametrize("lam", [2.0, 2.4])
def test_an_all_miss_fifo_trap_reads_r_one(ref, lam):
    r = R(truth(cfg(lam), MU), ref)
    assert r["allmiss"] and r["busy"] and r["why_not"] is None and r["r"] == pytest.approx(1.0, abs=0.02)


@pytest.mark.parametrize("servers", [16, 64])
def test_a_running_batch_does_not_move_r(ref, servers):
    """Round 2's confound: a request that stays in a running batch delays its session's next turn, which moves the
    served-turn mix (and the capacities draft 2 fitted to it). The work rate does not move."""
    assert R(truth(cfg(2.0), MU, servers=servers), ref)["r"] == pytest.approx(1.0, abs=0.02)


def test_a_running_batch_of_64_does_move_the_mix():
    c = cfg(2.0)
    one, many = truth(c, MU), truth(c, MU, servers=64)
    a, b = W.window(one)
    stay = many["requests"]
    stay = stay[(stay.t_first_token >= a) & (stay.t_first_token < b)]
    assert float((stay.t_end - stay.t_first_token).median()) > 30.0          # about 64 / 1.681 s in the batch
    assert abs(K3.kbar_obs(many, a, b) - K3.kbar_obs(one, a, b)) > 0.03


def test_longer_think_times_do_not_move_r(ref):
    assert R(truth(cfg(2.0), MU, gap_scale=6.0), ref)["r"] == pytest.approx(1.0, abs=0.02)


def test_a_fixed_cost_per_turn_moves_r_by_under_two_percent(ref):
    assert abs(R(truth(cfg(2.0), MU, cost=(0.18, 0.000135)), ref)["r"] - 1.0) < 0.02


@pytest.mark.parametrize("mu, side", [(1.85, "high"), (1.55, "low")])
def test_a_trap_faster_or_slower_than_the_cache_off_server_is_outside(ref, mu, side):
    rows = [R(truth(cfg(2.0, sd), mu), ref) for sd in (2, 3, 4)]
    j = W.judge(rows, loads=False)
    assert j["J1"] == "outside" and j["J1_side"] == side and j["median_r"] == pytest.approx(mu / MU, abs=0.02)


def test_partial_hits_fail_the_all_miss_precondition(ref):
    r = R(truth(cfg(2.0), MU, hit_frac=0.3), ref)
    assert r["reuse_W"] == pytest.approx(0.3, abs=0.02) and r["why_not"] == "not all-miss in W"
    j = W.judge([r] * 3, loads=False)
    assert j["n"] == 0 and j["J1"] == "undefined" and len(j["left_out"]) == 3


def test_a_server_that_idles_in_W_is_not_judged(ref):
    """The review's trace: an all-miss server at exactly the cache-off rate whose load falls for a while empties its
    line, does less work, and would read as a slower server. The busy precondition leaves it out."""
    lull = [{"at_s": 1200, "rate": 0.5}, {"at_s": 2050, "rate": 2.0}]
    r = R(truth(cfg(2.0, steps=lull), MU), ref)
    assert r["allmiss"] and r["busy_W"] < 0.99 and r["why_not"] == "idle in W" and r["r"] < 0.9


# ---------------------------------------------------------------- the judge

def _r(lam, r, why=None, name=None, date="20261109", why95="same"):
    return {"run": name or f"x_r{lam}_{r}", "date": date, "lam": lam, "r": r, "why_not": why,
            "why_not_reported": why if why95 == "same" else why95}


def test_J2_uses_only_groups_of_three_and_J1_pools_only_when_J2_is_inside():
    rows = [_r(2.0, 1.03), _r(2.0, 1.05), _r(2.0, 1.04), _r(2.4, 1.01), _r(2.4, 1.02), _r(2.4, 1.02),
            _r(2.2, 1.30), _r(2.2, 0.70)]
    j = W.judge(rows)
    assert j["judged_groups"] == ["2.0", "2.4"] and j["J2"] == "inside" and j["spread"] == pytest.approx(0.02)
    assert j["J1"] == "inside" and j["median_r"] == pytest.approx(1.025)      # pooled over the six runs J2 judged
    assert j["pooled_n"] == 6 and j["reported_not_pooled"] == ["x_r2.2_1.3", "x_r2.2_0.7"]
    assert j["groups"]["2.2"]["n"] == 2 and j["groups"]["2.2"]["min"] == 0.70 and "slope_r_per_reqs" in j
    far = [_r(2.0, 1.00), _r(2.0, 1.00), _r(2.0, 1.01), _r(2.4, 1.07), _r(2.4, 1.08), _r(2.4, 1.09)]
    j = W.judge(far)
    assert j["J2"] == "outside" and j["J1"] == "not_pooled" and math.isnan(j["median_r"])
    assert j["groups"]["2.0"]["J1"] == "inside" and j["groups"]["2.4"]["J1"] == "outside"
    assert j["groups"]["2.4"]["J1_side"] == "high" and j["all_judged_groups_inside"] is False
    one = W.judge([_r(2.0, 1.0)] * 4)
    assert one["J2"] == "undefined" and one["J1"] == "not_pooled"            # one load group: nothing to pool over


def test_a_pair_at_a_third_load_cannot_decide_the_pooled_level():
    """The round-2 review's trace D2: with the pair pooled, its two runs moved the label either way."""
    base = [_r(2.0, x) for x in (1.03, 1.04, 1.04, 1.05, 1.05)] + [_r(2.4, 1.05)] + [_r(2.4, 1.06)] * 5
    for pair in ([], [_r(2.2, 1.07), _r(2.2, 1.08)], [_r(2.2, 0.90), _r(2.2, 0.95)]):
        j = W.judge(base + pair)
        assert j["J2"] == "inside" and j["J1"] == "inside" and j["median_r"] == pytest.approx(1.05) and j["pooled_n"] == 11


def test_J2_outside_with_every_group_inside_is_told_apart():
    j = W.judge([_r(2.0, 0.96)] * 3 + [_r(2.4, 1.02)] * 3)
    assert j["J2"] == "outside" and j["spread"] == pytest.approx(0.06) and j["J1"] == "not_pooled"
    assert j["all_judged_groups_inside"] is True
    assert W._level(math.nan, 5) == ("undefined", None)


def test_the_reported_second_table_uses_its_own_reasons():
    rows = [_r(2.0, 1.0)] * 2 + [_r(2.0, 1.0, why="idle in W", why95=None)] + [_r(2.4, 1.0)] * 3
    assert W.judge(rows)["J2"] == "undefined"                                 # the 2.0 group has two judged runs
    assert W.judge(rows, why="why_not_reported")["J2"] == "inside"            # reported only


def test_a_gauge_that_does_not_cover_W_is_not_idleness(ref):
    run = truth(cfg(2.0), MU)
    a, b = W.window(run)
    full = run["metrics"]
    run["metrics"] = full[(full.t < a + 100) | (full.t > a + 130)]            # a 30 s hole in the gauge
    assert math.isnan(W.busy_share(run, a, b)) and W.row(run, ref, with_readouts=False)["why_not"] == "no waiting gauge in W"
    run["metrics"] = full.drop(columns=["vllm:num_requests_waiting"])
    assert W.row(run, ref, with_readouts=False)["why_not"] == "no waiting gauge in W"
    run["metrics"] = full.iloc[::5]                                           # a scrape every 5 s still covers W
    assert W.row(run, ref, with_readouts=False)["why_not"] is None
    both = truth(cfg(2.0), MU, hit_frac=0.3)
    both["metrics"] = both["metrics"].drop(columns=["vllm:num_requests_waiting"])
    assert W.row(both, ref, with_readouts=False)["why_not"] == "not all-miss in W; no waiting gauge in W"


def test_a_load_dependent_work_rate_fails_J2(ref):
    rows = [R(truth(cfg(2.0, sd), 1.62), ref) for sd in (2, 3, 4)] + [R(truth(cfg(2.4, sd), 1.75), ref) for sd in (2, 3, 4)]
    j = W.judge(rows)
    assert j["J2"] == "outside" and j["spread"] == pytest.approx((1.75 - 1.62) / MU, abs=0.02)


def test_judge_without_loads_and_what_it_leaves_out():
    j = W.judge([_r(2.0, 1.06), _r(2.0, 1.07), _r(2.0, 1.08), _r(2.0, math.nan, why="no work rate"),
                 _r(2.0, 0.5, why="idle in W")], loads=False)
    assert j["J1"] == "outside" and j["J1_side"] == "high" and j["n"] == 3
    assert [x["why"] for x in j["left_out"]] == ["no work rate", "idle in W"] and "J2" not in j
    assert W.judge([_r(2.0, 1.0), _r(2.0, 1.2)], loads=False)["J1"] == "undefined"


def test_exactly_at_the_tolerance_is_inside():
    assert W.judge([_r(2.0, 1.05)] * 3, loads=False)["J1"] == "inside"
    assert W.judge([_r(2.0, 0.9499)] * 3, loads=False)["J1"] == "outside"


# ---------------------------------------------------------------- batches, readouts

def test_batch2_waits_for_reg19s_result_and_needs_one_run_per_seed(monkeypatch, tmp_path):
    d = tmp_path / "decisions.md"
    d.write_text("## 2026-11-11 · [REG] REG-19\n")
    monkeypatch.setattr(W.withheld, "DECISIONS", d)
    with pytest.raises(RuntimeError):
        W.batch2_runs()
    d.write_text("## 2026-11-14 · [RESULT] REG-19: some\n")
    mk = lambda sd, n: {"cfg": {"seed": sd}, "dir": Path(f"2026111{n}-000000_burst_l1pl350cl_r2.0_w3000_s{sd}")}
    monkeypatch.setattr(W, "find_runs", lambda pattern: [mk(15, 2), mk(16, 2), mk(17, 2)])
    assert [r["cfg"]["seed"] for r in W.batch2_runs()] == [15, 16, 17]
    monkeypatch.setattr(W, "find_runs", lambda pattern: [mk(15, 2), mk(17, 2)])
    with pytest.raises(ValueError):
        W.batch2_runs()                                                     # a gap in the seeds
    monkeypatch.setattr(W, "find_runs", lambda pattern: [mk(15, 2), mk(15, 3), mk(16, 2)])
    with pytest.raises(ValueError):
        W.batch2_runs()                                                     # two valid runs of one seed
    monkeypatch.setattr(W, "find_runs", lambda pattern: [])
    with pytest.raises(ValueError):
        W.batch2_runs()
    monkeypatch.setattr(W, "find_runs", lambda pattern: [mk(15, 2), mk(16, 2)])
    with pytest.raises(ValueError):
        W.batch2_runs()                                                     # two seeds: the table would be undefined
    monkeypatch.setattr(W, "find_runs", lambda pattern: [mk(15, 2), mk(16, 2), mk(17, 2)])
    for heading in ("## 2026-11-14 · [CORR] the entry [RESULT] REG-19 named a wrong file\n",
                    "## 2026-11-14 · [RESULT] REG-190: another registration\n",
                    "## 2026-11-13 · [REG] REG-21 (batch 2 waits for [RESULT] REG-19)\n"):
        d.write_text(heading)
        with pytest.raises(RuntimeError):
            W.batch2_runs()                                                 # a heading that only quotes the text


def test_valse_and_jannesaris_rule_read_on_a_trap(ref):
    run = truth(cfg(2.4), MU)
    a, b = W.window(run)
    v = W.vj_rule(run, R(run, ref)["r"], a, b)
    assert v["token_part"] is True and v["slope_part"] is True and v["trapped"] is True
    assert v["backlog_slope"] > v["slope_needed"] > 0
    assert W.vj_rule(run, 1.20, a, b)["token_part"] is False                # outside their 15 percent


def test_decode_residence_in_the_replay_keeps_the_work_and_shifts_the_mix():
    c = cfg(2.0)
    plain, dec = S.simulate(c, MU), S.simulate(c, MU, decode_s=40.0)
    assert S.simulate(c, MU, decode_s=0.0).equals(plain)                    # 0 is model F's trajectory, unchanged
    a, b = W.window(S.as_run(c, plain))
    rp, rd = S.as_run(c, plain), S.as_run(c, dec)
    assert W.work_rate(rd, a, b) == pytest.approx(W.work_rate(rp, a, b), rel=0.02)
    assert np.allclose((dec.t_end - dec.t_first_token).dropna().to_numpy(), 40.0)
    assert K3.kbar_obs(rd, a, b) != pytest.approx(K3.kbar_obs(rp, a, b), abs=0.02)


def test_a_failing_readout_does_not_take_the_judged_values_with_it(ref, monkeypatch):
    monkeypatch.setattr(W, "readouts", lambda run: 1 / 0)
    r = W.row(truth(cfg(2.0), MU), ref)
    assert r["r"] == pytest.approx(1.0, abs=0.02) and "ZeroDivisionError" in r["readouts"]["error"]
    assert r["vj_rule"]["token_part"] is True


def test_readouts_on_a_synthetic_run(ref):
    r = W.row(truth(cfg(2.0), MU, servers=64), ref)
    ro = r["readouts"]
    assert "error" not in ro and ro["residence_s"] > 30
    assert ro["X_all"] == pytest.approx(ro["X_session"], abs=0.2) and 3.5 < ro["kbar"] < 4.6
    assert set(ro["replay_at_floor"]) == {"prop_plain", "prop_residence", "fixed_plain", "fixed_residence"}
    assert ro["replay_at_floor"]["prop_residence"]["U"] == pytest.approx(MU * S.LBAR, rel=0.02)


def test_table_on_fake_runs(monkeypatch, ref):
    runs = {}
    for lam in (2.0, 2.4):
        for sd in (2, 3, 4):
            n = f"20261109-00000{sd}_burst_l1pl350cl_r{lam}_s{sd}"
            runs[n] = truth(cfg(lam, sd), MU, name=n)
    monkeypatch.setitem(W.REG21, "batch1", tuple(runs) + ("20261109-999999_missing",))
    monkeypatch.setattr(W, "find_runs", lambda pattern: [runs[pattern]] if pattern in runs else [])
    monkeypatch.setattr(W, "reference", lambda: ref)
    monkeypatch.setattr(W, "select", lambda rs: (rs[:-1], [{"run": rs[-1]["dir"].name, "cold_backlogged": False}]))
    monkeypatch.setattr(W, "readouts", lambda run: {"stub": True})
    with pytest.raises(ValueError, match="999999_missing"):
        W.reg21_table(1)                                                    # a registered run missing or invalid
    with pytest.raises(ValueError):
        W.reg21_table(3)
    monkeypatch.setitem(W.REG21, "batch1", tuple(runs))
    t = W.reg21_table(1)
    assert len(t["rows"]) == 5 and "fixed_load_contrast" not in t
    assert t["judged"]["at_busy_min_reported"]["J2"] == "undefined"
    assert t["not_cold_backlogged"][0]["cold_backlogged"] is False
    assert t["judged"]["judged_groups"] == ["2.0"] and t["judged"]["J2"] == "undefined"   # 2.4 is left with two runs
    assert t["judged"]["J1"] == "not_pooled" and t["judged"]["groups"]["2.0"]["J1"] == "inside"
    assert all(r["readouts"] == {"stub": True} and r["date"] == "20261109" for r in t["rows"])


def test_batch2_reports_the_fixed_load_contrast(monkeypatch, ref):
    """Batch 2's median minus batch 1's median at the same load: reported, never judged."""
    b1 = {f"20261111-00000{sd}_burst_l1pl350cl_r2.0_s{sd}": truth(cfg(2.0, sd), MU, name=f"20261111-00000{sd}_burst_l1pl350cl_r2.0_s{sd}")
          for sd in (2, 3, 4)}
    b2 = [truth(cfg(2.0, sd), 1.78, name=f"20261112-00000{sd}_burst_l1pl350cl_r2.0_w3000_s1{sd}") for sd in (5, 6, 7)]
    monkeypatch.setitem(W.REG21, "batch1", tuple(b1))
    monkeypatch.setattr(W, "find_runs", lambda pattern: [b1[pattern]] if pattern in b1 else [])
    monkeypatch.setattr(W, "batch2_runs", lambda: b2)
    monkeypatch.setattr(W, "reference", lambda: ref)
    monkeypatch.setattr(W, "select", lambda rs: (rs, []))
    monkeypatch.setattr(W, "readouts", lambda run: {"stub": True})
    t = W.reg21_table(2)
    c = t["fixed_load_contrast"]
    assert t["judged"]["J1"] == "outside" and t["judged"]["J1_side"] == "high" and "J2" not in t["judged"]
    assert c["batch1_median"] == pytest.approx(1.0, abs=0.02) and c["difference"] == pytest.approx(1.78 / MU - 1, abs=0.02)


def test_the_redo_proxy_is_reported_for_both_arms(ref):
    ro = W.row(truth(cfg(2.0), MU), ref)["readouts"]
    assert "redo_share" in ro and "preempt_per_s" in ro and "mean_prompt_all" in ro
    assert all("redo_share" in v or "gauges_error" in v for v in ref["runs"].values())
    assert "slope_needed_at_configured_rate" in W.row(truth(cfg(2.0), MU), ref)["vj_rule"]


# ---------------------------------------------------------------- reported only, outside the judged path

def test_span_values_give_the_window_mean_with_its_spread(ref):
    run = truth(cfg(2.0), MU)
    a, b = W.window(run)
    v = W.span_values(run, a, b)
    assert len(v["spans"]) == 3 and v["spans"][0]["span"] == (a, a + 300.0) and v["spans"][-1]["span"][1] == b
    assert np.mean([x["U"] for x in v["spans"]]) == pytest.approx(W.work_rate(run, a, b))
    assert v["U_min"] <= W.work_rate(run, a, b) <= v["U_max"] and all(x["reuse"] == 0 for x in v["spans"])
    short = W.span_values(run, a, a + 400.0)                                # a last span shorter than 300 s
    assert [x["span"] for x in short["spans"]] == [(a, a + 300.0), (a + 300.0, a + 400.0)]


def test_reported_spans_cover_the_batch_and_the_reference(monkeypatch, ref):
    runs = [truth(cfg(2.0, sd), MU, name=f"20261111-00000{sd}_burst_l1pl350cl_r2.0_s{sd}") for sd in (2, 3)]
    refs = {i: ref_run(3.0, name=i) for i in W.REG21["ref_runs"][:2]}
    monkeypatch.setattr(W, "batch1_runs", lambda: runs)
    monkeypatch.setattr(W, "find_runs", lambda pattern: [refs[pattern]] if pattern in refs else [])
    out = W.reported_spans(1, ref["mean"])
    assert set(out["runs"]) == {r["dir"].name for r in runs}
    assert all(v["r_first"] == pytest.approx(1.0, abs=0.02) for v in out["runs"].values())
    assert "U_min" in out["reference"][W.REG21["ref_runs"][0]] and "error" in out["reference"][W.REG21["ref_runs"][4]]


def test_vj_counts_are_k_of_n_per_load_with_their_bound():
    rows = [{"lam": 2.0, "vj_rule": {"trapped": True}}, {"lam": 2.0, "vj_rule": {"trapped": False}},
            {"lam": 2.4, "vj_rule": {"trapped": True}}, {"lam": 2.4, "vj_rule": {"error": "x"}}]
    c = W.vj_counts(rows)
    assert c["2.0"]["k"] == 1 and c["2.0"]["n"] == 2 and c["2.4"] == {"n": 1, "k": 1, "cp_upper_95": 1.0}
    assert 0.9 < c["2.0"]["cp_upper_95"] < 1.0


def test_the_schedules_of_one_seed_at_two_loads_are_nested():
    """Rule H: the load groups share seeds, and the sharing is exact. Every session start of a seed's schedule at
    lam = 2.0 is also a session start of the same seed's schedule at 2.4 (the count is drawn first, then that many
    uniform times from the same stream), and seed 2's schedule at 2.2 lies between. So J2's two groups are paired by
    seed, and the runs pooled over 2.0 and 2.4 hold six distinct seeds (1 to 6), not eleven."""
    def starts(lam, seed):
        s = S.schedule(cfg(lam, seed))
        s = s[(s.turn == 0) & ~s["burst"].fillna(False).astype(bool)]
        return set(np.round(s.t_planned.to_numpy(float), 6))
    for seed in (2, 3, 4, 5, 6):
        low, high = starts(2.0, seed), starts(2.4, seed)
        assert len(low) > 500 and low < high                              # a proper subset
    assert starts(2.0, 2) < starts(2.2, 2) < starts(2.4, 2)
