"""Session cap (step D; `docs/definitions.md`, "session cap, sessions in service"; owner 2026-11-12).

The cap's value for a seed is the highest number of sessions in service at once in that seed's no-trigger control,
computed here before the capped run (`max_sessions_in_service`). In service: from a session's first turn sent to its
last reply; a session with an unsent or unfinished turn stays in service; burst requests are not sessions. This is the
definition `k1.sessions_in_service` averages on a grid; here the maximum is taken exactly, over every event.
`cap_wait` reports the time sessions waited at the cap (`t_admitted - t_arrived`, recorded by harness/loadgen.py).
"""
from __future__ import annotations

import math

import numpy as np

from analysis.margin import is_burst_request


def _intervals(run: dict):
    q = run["requests"]
    q = q[~is_burst_request(run)]
    g = q.groupby("session_id")
    start = g.t_sent.min()
    done = g.t_end.max().where(g.t_end.apply(lambda s: s.notna().all()), np.inf)
    keep = start.notna()
    return start[keep].to_numpy(float), done[keep].to_numpy(float)


def max_sessions_in_service(run: dict) -> int:
    """Exact peak of the in-service count over the whole run: +1 at a session's first send, -1 at its last reply
    (half-open [start, done), so a session ending at t is no longer counted at t)."""
    start, done = _intervals(run)
    if not len(start):
        return 0
    t = np.concatenate([start, done])
    step = np.concatenate([np.ones(len(start)), -np.ones(len(done))])
    order = np.lexsort((step, t))          # at equal times, ends (-1) before starts (+1)
    return int(np.max(np.cumsum(step[order])))


def cap_wait(run: dict) -> dict:
    """Waits at the cap over the sessions that reached it (turn 0 with `t_arrived`); a session never admitted counts
    with its wait to the end of the record as NaN and is listed in `n_never_admitted`."""
    q = run["requests"]
    if "t_arrived" not in q:
        return {"n_sessions": 0, "n_waited": 0, "n_never_admitted": 0, "mean_s": math.nan, "max_s": math.nan}
    t0 = q[(q.turn == 0) & q.t_arrived.notna() & ~is_burst_request(run)]
    w = (t0.t_admitted - t0.t_arrived).astype(float)
    adm = w.dropna()
    return {"n_sessions": int(len(t0)), "n_waited": int((adm > 0).sum()), "n_never_admitted": int(w.isna().sum()),
            "mean_s": float(adm.mean()) if len(adm) else math.nan, "max_s": float(adm.max()) if len(adm) else math.nan,
            "p95_s": float(np.percentile(adm, 95)) if len(adm) else math.nan}
