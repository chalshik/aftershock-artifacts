from pathlib import Path

from harness.run import load_config
from harness.workload import build_schedule, expected_requests, prompt_tokens, segments, summary

CONFIGS = Path(__file__).resolve().parent.parent / "configs"


def wl(name="first_real.yaml", **over):
    w = load_config(CONFIGS / name)["workload"]
    w.update(over)
    return w


def test_deterministic():
    a, pa = build_schedule(wl(), seed=1)
    b, pb = build_schedule(wl(), seed=1)
    assert a.equals(b)
    assert all((x == y).all() for x, y in zip(pa.tokens, pb.tokens))
    c, _ = build_schedule(wl(), seed=2)
    assert not a.equals(c)


def test_each_turn_extends_previous_prompt():
    w = wl()
    s = w["sessions"]
    sched, prompts = build_schedule(w, seed=0)
    for sid, g in sched.groupby("session_id"):
        g = g.sort_values("turn")
        assert list(g.turn) == list(range(len(g)))
        assert g.t_planned.is_monotonic_increasing
        lens = list(g.prompt_len)
        assert lens[0] == s["system_tokens"] + s["user_tokens"]
        assert all(b - a == s["reply_tokens"] + s["user_tokens"] for a, b in zip(lens, lens[1:]))
        p0 = prompt_tokens(prompts, sid, lens[0])
        p_last = prompt_tokens(prompts, sid, lens[-1])
        assert p_last[: len(p0)] == p0


def test_rate_and_bounds():
    w = wl()
    sched, prompts = build_schedule(w, seed=0)
    lo, hi = w["token_id_range"]
    assert sched.t_planned.between(0, w["duration_s"], inclusive="left").all()
    assert all(t.min() >= lo and t.max() < hi for t in prompts.tokens)
    # Steady state (after ramp-up) is close to lambda.
    steady = sched[sched.t_planned >= w["warmup_s"]]
    rate = len(steady) / (w["duration_s"] - w["warmup_s"])
    assert abs(rate - w["rate"]) / w["rate"] < 0.2


def test_random_workload():
    w = wl("smoke.yaml")
    sched, prompts = build_schedule(w, seed=0)
    assert (sched.prompt_len == w["random"]["prompt_tokens"]).all()
    assert sched.session_id.is_unique
    assert summary(sched)["requests"] == len(sched)


def test_load_steps_change_the_rate_at_the_step():
    w = wl(rate=1.0, duration_s=6000, warmup_s=0, steps=[{"at_s": 2000, "rate": 4.0}, {"at_s": 4000, "rate": 1.0}])
    sched, _ = build_schedule(w, seed=0)
    middle = sched[(sched.t_planned >= 2500) & (sched.t_planned < 3500)]  # past the sessions' ramp
    last = sched[(sched.t_planned >= 4500) & (sched.t_planned < 5500)]
    assert 3.6 < len(middle) / 1000 < 4.4
    assert 0.8 < len(last) / 1000 < 1.2
    assert segments(w) == [(0.0, 2000.0, 1.0), (2000.0, 4000.0, 4.0), (4000.0, 6000.0, 1.0)]
    assert expected_requests(w, 1000, 3000) == 1000 + 4000


def test_no_steps_keeps_the_same_schedule_as_before():
    """Same random draws as the code the Stage 1 runs used, so an old config still gives its old schedule."""
    import numpy as np
    w = wl()
    sched, _ = build_schedule(w, seed=0)
    rng = np.random.default_rng(0)
    n = rng.poisson(w["rate"] / w["sessions"]["turns"] * w["duration_s"])
    first = np.sort(rng.uniform(0.0, w["duration_s"], n))[0]
    assert sched.t_planned.iloc[0] == first
