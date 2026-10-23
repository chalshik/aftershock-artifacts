"""Build the open-loop request schedule before the run (seeded, deterministic).

schedule: one row per request (planned send time, session, turn, prompt_len).
prompts:  one row per session with its full token-ID context. A turn's prompt is
          context[:prompt_len], because each turn extends the previous one.
"""
import numpy as np
import pandas as pd


def build_schedule(wl: dict, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    lo, hi = wl["token_id_range"]
    if wl["kind"] == "random":
        rows, contexts = _random(wl, rng, lo, hi)
    elif wl["kind"] == "sessions":
        rows, contexts = _sessions(wl, rng, lo, hi)
    else:
        raise ValueError(f"unknown workload kind {wl['kind']!r}")
    cols = ["t_planned", "session_id", "turn", "prompt_len"]
    df = pd.DataFrame(rows, columns=cols).sort_values("t_planned", kind="stable").reset_index(drop=True)
    df.insert(0, "request_id", np.arange(len(df)))
    df["output_len"] = wl["output_tokens"]
    prompts = pd.DataFrame({"session_id": np.arange(len(contexts)), "tokens": contexts})
    return df, prompts


def prompt_tokens(prompts: pd.DataFrame, session_id: int, prompt_len: int) -> list[int]:
    return [int(x) for x in prompts.at[session_id, "tokens"][:prompt_len]]


def _poisson_times(rng, rate: float, duration: float) -> np.ndarray:
    n = rng.poisson(rate * duration)
    return np.sort(rng.uniform(0.0, duration, n))


def _random(wl, rng, lo, hi):
    n = wl["random"]["prompt_tokens"]
    times = _poisson_times(rng, wl["rate"], wl["duration_s"])
    rows = [dict(t_planned=float(t), session_id=i, turn=0, prompt_len=n) for i, t in enumerate(times)]
    return rows, [rng.integers(lo, hi, n) for _ in times]


def _gap(rng, spec: dict) -> float:
    if spec["dist"] == "exponential":
        return float(rng.exponential(spec["mean"]))
    if spec["dist"] == "fixed":
        return float(spec["mean"])
    raise ValueError(f"unknown gap dist {spec['dist']!r}")


def _sessions(wl, rng, lo, hi):
    s = wl["sessions"]
    turns = s["turns"]
    rows, contexts = [], []
    # Sessions start at rate lambda/turns, so the steady-state request rate is lambda.
    for sid, t0 in enumerate(_poisson_times(rng, wl["rate"] / turns, wl["duration_s"])):
        parts = [rng.integers(lo, hi, s["system_tokens"])]
        t = float(t0)
        for turn in range(turns):
            if turn > 0:
                # Recorded reply for the previous turn: the cache hit covers the previous prompt only.
                parts.append(rng.integers(lo, hi, s["reply_tokens"]))
                t += _gap(rng, s["turn_gap_s"])
            if t >= wl["duration_s"]:
                break
            parts.append(rng.integers(lo, hi, s["user_tokens"]))
            rows.append(dict(t_planned=t, session_id=sid, turn=turn,
                             prompt_len=sum(len(p) for p in parts)))
        contexts.append(np.concatenate(parts))
    return rows, contexts


def summary(df: pd.DataFrame) -> dict:
    per_session = df.groupby("session_id")
    gaps = per_session["t_planned"].diff().dropna()
    return {
        "requests": int(len(df)),
        "sessions": int(df["session_id"].nunique()),
        "turns_per_session_mean": float(per_session.size().mean()),
        "prompt_len": {q: float(df["prompt_len"].quantile(p)) for q, p in
                       [("p50", .5), ("p90", .9), ("max", 1.0)]},
        "turn_gap_s_mean": float(gaps.mean()) if len(gaps) else None,
        "span_s": float(df["t_planned"].max()) if len(df) else 0.0,
    }
