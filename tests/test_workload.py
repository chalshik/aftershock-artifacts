from pathlib import Path

from harness.run import load_config
from harness.workload import build_schedule, prompt_tokens, summary

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
