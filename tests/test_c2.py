"""C2 condition 4 (analysis/c2.py, draft for REG-22) on hand-made runs: no run folder is read."""
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import analysis.c2 as C

CFG = {"trigger": {"kind": "burst", "at_s": 900.0, "duration_s": 180.0, "prompt_tokens": 2944},
       "verdict": {"baseline_s": 600.0, "watch_s": 1500.0, "end_s": 600.0, "stuck_hit_drop": 0.06}}
END = 2580.0


def fake_run(cold_from=1000.0, rewarm=None, kv_cold=0.95, n_cold=60.0, n_max=None, kv_from=960.0, n_from=940.0,
             burst_last_end=1200.0, burst_unfinished=False):
    """Sessions of 8 turns, one request every 0.5 s. A later turn reuses its whole previous prompt until `cold_from`
    (and again inside `rewarm`, a (start, end) pair); afterwards nothing. Gauges step at kv_from and n_from."""
    rows, sid, t = [], 0, 0.0
    while t < END:
        for k in range(8):
            first = t
            warm = first < cold_from or (rewarm is not None and rewarm[0] <= first < rewarm[1])
            prompt = 2176 + 256 * k
            rows.append({"session_id": sid, "turn": k, "t_planned": first, "t_first_token": first, "t_end": first + 0.3,
                         "prompt_tokens": prompt, "prompt_tokens_planned": prompt,
                         "cached_tokens": (prompt - 256) if (warm and k > 0) else 0, "status": "ok"})
            t += 0.5
        sid += 1
    for j, tb in enumerate(np.linspace(900.0, 1079.0, 40)):          # the burst: one-off 2944-token requests
        last = j == 39
        rows.append({"session_id": 10_000 + j, "turn": 0, "t_planned": tb, "t_first_token": tb + 1.0,
                     "t_end": (math.nan if (last and burst_unfinished) else (burst_last_end if last else tb + 5.0)),
                     "prompt_tokens": 2944, "prompt_tokens_planned": 2944, "cached_tokens": 0,
                     "status": "unfinished" if (last and burst_unfinished) else "ok"})
    ts = np.arange(0.0, END, 1.0)
    n = np.where(ts < n_from, 5.0, n_cold)
    if n_max is not None:
        n[-10] = n_max
    m = pd.DataFrame({"t": ts, C.N: n, C.KV: np.where(ts < kv_from, 0.3, kv_cold)})
    return {"cfg": CFG, "requests": pd.DataFrame(rows), "metrics": m, "dir": Path("fake")}


def test_a_cold_full_backlogged_run_shows_the_loop():
    r = C.condition4(fake_run())
    assert r["label"] == "loop" and r["levels"]["ok"] and r["sustain"]["ok"]
    assert r["baseline"]["reuse"] == pytest.approx(1.0) and r["levels"]["n_over_base"] == pytest.approx(12.0)
    assert r["sustain"]["last_burst_end"] == 1200.0 and r["sustain"]["n_spans"] == 4      # spans from 1380 s on
    assert all(s["reuse"] == 0.0 and s["holds"] for s in r["sustain"]["spans"])


def test_a_backlog_without_a_full_pool_is_not_this_loop():
    assert C.condition4(fake_run(kv_cold=0.5))["label"] == "not_memory_limited"
    assert C.condition4(fake_run(n_cold=8.0))["label"] == "not_memory_limited"            # batch under 2 x baseline
    assert C.condition4(fake_run(n_max=256.0))["label"] == "not_memory_limited"           # at the sequence cap


def test_a_span_in_which_the_cache_comes_back_breaks_sustain():
    r = C.condition4(fake_run(rewarm=(1700.0, 1950.0)))
    assert r["label"] == "not_sustained" and r["levels"]["ok"]
    assert [s["holds"] for s in r["sustain"]["spans"]] == [True, False, True, True]


def test_undefined_when_the_burst_is_still_in_the_system_or_leaves_too_late():
    assert C.condition4(fake_run(burst_unfinished=True))["label"] == "undefined"
    late = C.condition4(fake_run(burst_last_end=2200.0))                                  # one span left: too few
    assert late["sustain"]["n_spans"] == 1 and late["label"] == "undefined"


def test_onsets_report_the_order_found():
    o = C.onsets(fake_run(kv_from=930.0, n_from=920.0, cold_from=1000.0))
    assert o["n"] <= o["kv"] <= o["reuse"] <= o["u"]
    assert o["order"][0] == "n" and set(o["order"]) == {"n", "kv", "reuse", "u"}
    never = C.onsets(fake_run(cold_from=END + 1.0, kv_cold=0.5))                          # the cache is never lost
    assert math.isnan(never["reuse"]) and math.isnan(never["kv"]) and never["order"] == ["n"]


def test_links_are_none_when_a_value_is_missing():
    run = fake_run()
    run["metrics"] = run["metrics"].iloc[:0]
    base = C.baseline(run)
    assert math.isnan(base["n"]) and C.links(run, 1500.0, 1800.0, base)["holds"] is None
    assert C.condition4(run)["label"] == "undefined"


def test_session_uncached_rate_leaves_the_burst_out():
    run = fake_run()
    warm = C.session_uncached_rate(run, 300.0, 900.0)       # 2 req/s; turn 0 prefills 2176, later turns 256
    assert warm == pytest.approx(2 * (2176 + 7 * 256) / 8, rel=0.02)
    assert C.session_uncached_rate(run, 900.0, 1000.0) == pytest.approx(warm, rel=0.05)   # burst rows not counted


def test_table_judges_only_stuck_runs(monkeypatch, tmp_path):
    import analysis.load as L
    names = ("a_stuck", "b_recovered", "c_missing")
    for n in names[:2]:
        (tmp_path / n).mkdir()
        (tmp_path / n / "config.yaml").write_text("x: 1\n")
    monkeypatch.setitem(C.REG22, "runs", names)
    monkeypatch.setattr(L, "RUNS", tmp_path)

    def load_run(p):
        r = fake_run()
        r["dir"] = Path(p)
        r["cfg"] = {**CFG, "workload": {"rate": 2.0}, "seed": 2}
        return r
    monkeypatch.setattr(L, "load_run", load_run)
    monkeypatch.setattr(L, "verdict", lambda run: {"verdict": "stuck" if run["dir"].name == "a_stuck" else "recovered"})
    t = C.reg22_table()
    assert [r["run"] for r in t["rows"]] == ["a_stuck"] and t["counts"]["loop"] == 1 and t["n_stuck"] == 1
    assert t["left_out"] == [{"run": "b_recovered", "why": "verdict recovered"}, {"run": "c_missing", "why": "missing"}]
