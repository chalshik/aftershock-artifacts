"""Tests of control_due.py on fakes only. analysis.load.RUNS is pointed at a temporary folder and load_run is replaced
by a loader that refuses any path outside it, so no run folder under runs/ is ever opened. The real
analysis.k1.cold_backlogged judges synthetic runs (built like tests/test_k1.py's make_run), and the real seal guard
(analysis.withheld.guard) runs inside the fake loader, against a temporary decisions file.

Run from the repo root:
    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider docs/probe/20261113_reg20/ops/test_control_due.py
"""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from analysis import k1, load, withheld  # noqa: E402

_spec = importlib.util.spec_from_file_location("control_due", HERE / "control_due.py")
CD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CD)

CFG = "burst_l1pl350ol_r2.0_w3000_s15"
NAME = "20261114-060000_" + CFG
VERDICT = {"baseline_s": 600, "watch_s": 3000, "end_s": 600, "stuck_hit_drop": 0.06, "recovered_hit_drop": 0.06,
           "recovered_q_excess": 1.0}


def make_run(reuse_after=0.0, q_after=120.0, kv_after=0.95, gap_at=None, name=CFG):
    """As tests/test_k1.py make_run: sessions every 4 s, 8 turns 5 s apart; before the burst's end (1080 s) every later
    turn reuses its whole previous prompt, after it `reuse_after` of it. Server: empty line and KV 0.5 before; after,
    `q_after` and `kv_after`. `gap_at` removes 30 s of scrapes (an uncovered window gives None)."""
    t = np.arange(0.0, 4081.0)
    after = t >= 1080
    m = pd.DataFrame({"t": t, "vllm:prefix_cache_hits_total": np.cumsum(np.where(after, 100 * reuse_after, 80.0)),
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
    cfg = {"name": name, "trigger": {"kind": "burst", "at_s": 900, "duration_s": 180, "prompt_tokens": 2944},
           "verdict": VERDICT, "slo": {"ttft_s": 1.0}, "checks": {"max_scrape_gap_s": 2.0}}
    return {"cfg": cfg, "metrics": m, "requests": pd.DataFrame(rows), "checks": {"valid": True, "failed": []}}


COLD = {}
WARM = dict(reuse_after=1.0, q_after=0.0, kv_after=0.5)
PARTIAL = dict(reuse_after=0.5, q_after=120.0, kv_after=0.5)      # reuse down, backlogged, KV not full: neither


@pytest.fixture
def fake(monkeypatch, tmp_path):
    """A temporary runs/ with one empty folder per name given; load_run returns the synthetic run registered for it."""
    runs = tmp_path / "runs"
    runs.mkdir()
    decisions = tmp_path / "decisions.md"
    decisions.write_text("## 2026-11-13 · [DECISION] (owner) REG-20 arm A starts: sandbox\n")   # no [RESULT] REG-20
    monkeypatch.setattr(load, "RUNS", runs)
    monkeypatch.setattr(withheld, "DECISIONS", decisions)
    monkeypatch.delenv("AFTERSHOCK_UNSEAL", raising=False)       # restored after each test
    table, calls = {}, []

    def load_run(d):
        d = Path(d)
        assert d.parent == runs, f"control_due asked for {d}, outside the temporary runs/"
        withheld.guard(d.name)                                    # the real seal check
        calls.append(d.name)
        return {**table[d.name], "dir": d}

    monkeypatch.setattr(load, "load_run", load_run)

    def add(name, run):
        (runs / name).mkdir()
        table[name] = run
    return {"add": add, "calls": calls, "runs": runs}


def run_main(argv, capsys):
    rc = CD.main(argv)
    out, err = capsys.readouterr()
    return rc, out, err


@pytest.mark.parametrize("kw, want", [(COLD, "yes"), (WARM, "no"), (PARTIAL, "no"), (dict(gap_at=3700), "unclear")])
def test_one_line_from_the_real_readout(fake, capsys, kw, want):
    fake["add"](NAME, make_run(**kw))
    rc, out, err = run_main(["control_due.py", NAME], capsys)
    assert rc == 0 and out == f"CONTROL_DUE {want}\n"
    assert not any(ch.isdigit() for ch in out)                    # no readout value, reuse, queue or KV number
    assert fake["calls"] == [NAME]


def test_the_key_read_is_kis_cold_backlogged(fake, capsys):
    run = make_run()
    fake["add"](NAME, run)
    r = k1.cold_backlogged({**run, "dir": Path(NAME)})
    assert r["cold_backlogged"] is True and r["recovered"] is False
    assert run_main(["control_due.py", NAME], capsys)[1] == "CONTROL_DUE yes\n"


@pytest.mark.parametrize("value, want", [(None, "unclear"), (float("nan"), "unclear"), (np.True_, "yes"),
                                         (np.False_, "no"), (True, "yes"), (False, "no")])
def test_values_k1_can_give(fake, capsys, monkeypatch, value, want):
    fake["add"](NAME, make_run())
    monkeypatch.setattr(k1, "cold_backlogged", lambda run: {"cold_backlogged": value, "reuse": {"end": 0.123}})
    rc, out, _ = run_main(["control_due.py", NAME], capsys)
    assert rc == 0 and out == f"CONTROL_DUE {want}\n"


@pytest.mark.parametrize("value", ["yes", 1, 0.0, [True]])
def test_a_value_k1_never_gives_prints_nothing(fake, capsys, monkeypatch, value):
    fake["add"](NAME, make_run())
    monkeypatch.setattr(k1, "cold_backlogged", lambda run: {"cold_backlogged": value})
    rc, out, err = run_main(["control_due.py", NAME], capsys)
    assert rc != 0 and out == "" and "unexpected type" in err


@pytest.mark.parametrize("argv", [
    [], [NAME, NAME], ["*"], [CFG], ["../" + NAME], [NAME + " "], [NAME + "/"],
    ["20261114-060000_burst_l1pl350cl_r2.0_w3000_s15"],              # REG-19's closed partner
    ["20261114-060000_stage2_control_l1pl350ol_r2.0_w3000_s15"],     # a control
    ["20261114-060000_burst_l1pl350ol_r2.5_w3000_s15"],              # arm B
    ["20261114-060000_burst_l1pl350cl_r2.0_w3000_s15_drift"],        # the drift run
    ["20261114-060000_burst_l1pl350ol_r2.0_w3000_s20"],              # a seed outside 15-19
    ["2026111-060000_burst_l1pl350ol_r2.0_w3000_s15"]])
def test_only_an_exact_arm_a_burst_name_is_read(fake, capsys, argv):
    rc, out, err = run_main(["control_due.py", *argv], capsys)
    assert rc == 2 and out == "" and fake["calls"] == []


def test_a_missing_folder(fake, capsys):
    rc, out, _ = run_main(["control_due.py", NAME], capsys)
    assert rc == 3 and out == "" and fake["calls"] == []


@pytest.mark.parametrize("checks", [None, {"valid": False, "failed": ["client_lag"]}, {"valid": "true"}])
def test_only_a_valid_run(fake, capsys, checks):
    fake["add"](NAME, {**make_run(), "checks": checks})
    rc, out, err = run_main(["control_due.py", NAME], capsys)
    assert rc == 3 and out == "" and "not a valid run" in err


def test_a_folder_holding_another_config(fake, capsys):
    fake["add"](NAME, make_run(name="burst_l1pl350ol_r2.0_w3000_s16"))
    rc, out, _ = run_main(["control_due.py", NAME], capsys)
    assert rc == 3 and out == ""


def test_the_seal_is_lifted_for_reg20_only_and_in_this_process(fake, capsys, monkeypatch):
    assert withheld.sealed_by(NAME) == "REG-20"                   # sealed while no [RESULT] REG-20 heading exists
    with pytest.raises(withheld.WithheldError):
        load.load_run(load.RUNS / NAME)                           # the fake loader runs the real guard
    monkeypatch.setenv("AFTERSHOCK_UNSEAL", "REG-19")             # an inherited value is replaced, not extended
    fake["add"](NAME, make_run())
    rc, out, _ = run_main(["control_due.py", NAME], capsys)
    assert rc == 0 and out == "CONTROL_DUE yes\n"
    assert os.environ["AFTERSHOCK_UNSEAL"] == "REG-20"


def test_as_a_script_a_bad_name_reads_nothing(tmp_path):
    """The file runs as a script and refuses a bad name before importing or loading anything (a good name is not
    tried here: in a separate process load.RUNS would be the real runs/)."""
    env = {k: v for k, v in os.environ.items() if k != "AFTERSHOCK_UNSEAL"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    p = subprocess.run([sys.executable, str(HERE / "control_due.py"), "not_a_run"], capture_output=True, text=True,
                       cwd=tmp_path, env=env)
    assert p.returncode == 2 and p.stdout == ""
