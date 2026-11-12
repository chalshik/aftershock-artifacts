"""K1, turn semantics: registration REG-20 (draft, docs/decisions.md 2026-11-12 [REG]; docs/claims.md K1). Never writes
into runs/.

One readout, defined alike for open- and closed-loop turns: no latency (percent fast is measured from the planned time
in one arm and from the release time in the other; docs/definitions.md) and no request mix. A burst run is
*cold-backlogged* when, in the end window of its watch, against its own pre-burst baseline:
  - the prefix reuse of later turns (`reuse`: Σ cached tokens / Σ previous-turn prompt tokens over ok later turns whose
    first token falls in the window) <= baseline - stuck_hit_drop. The server hit rate is not used: closed-loop turns
    shift the served mix towards first turns, which never hit (rule F review of REG-20, T1);
  - mean server waiting > baseline + recovered_q_excess;
  - mean KV >= gate.SURGE["kv_onset"] (0.9, there on a 60 s rolling mean, here on the window's mean).
A run is *recovered* only by the `recovered` rule's hit and queue parts on the same quantities: reuse >= baseline -
recovered_hit_drop and waiting <= baseline + recovered_q_excess. A run that is neither is *partial*.
The numbers are those registered for the verdict and REG-16/17; the reuse statistic is new (REG-20).

Arms: closed = REG-19's burst runs; open A = the same configs with open-loop turns (same seeds, same planned schedule,
λ = 2.0); open B = open-loop turns at λ = 2.5, the same share of the open-loop warm capacity (3.0) as 2.0 is of the
closed-loop one (≈ 2.4).
"""
import math

import numpy as np

from analysis.gate import SURGE, burst_end, overlap_share, shock_size, turn0_share
from analysis.load import _level, find_runs
from analysis.margin import is_burst_request
from analysis.stats import fisher_one_sided

REG20 = {"closed_seeds": (15, 16, 17, 18, 19),
         "a_lam": 2.0, "b_lam": 2.5, "b_seeds": (15, 16, 17),
         "test": "mcnemar",             # the owner's choice between "mcnemar" (paired) and "fisher" (pooled)
         "alpha": 0.05,
         "refute_k": 3,                 # open arm A stuck (control warm) in this many seeds refutes K1
         "min_n": 2,
         "overlap_min": 0.5,            # REG-7's overlap rule (decisions.md 2026-11-05 [REG] REG-7)
         "mech_window": (0.0, 600.0),   # after the burst's end
         "service_grid_s": 10.0,
         "drift_cfg": "burst_l1pl350cl_r2.0_w3000_s15_drift"}

CONTROL_COLD = ("cold_control", "overload_open")


def closed_pattern(seed: int) -> str:
    return f"*_burst_l1pl350cl_r2.0_w3000_s{seed}"


def open_pattern(lam: float, seed: int, control: bool = False) -> str:
    kind = "stage2_control" if control else "burst"
    return f"*_{kind}_l1pl350ol_r{lam:.1f}_w3000_s{seed}"


def windows(burst_cfg: dict) -> dict:
    """Baseline [at - baseline_s, at) and end window [end + watch - end_s, end + watch), from a burst run's config.
    The same absolute windows judge its control, so both runs are read at the same moments of one schedule."""
    t, v = burst_cfg["trigger"], burst_cfg["verdict"]
    at, end = float(t["at_s"]), float(t["at_s"] + t["duration_s"])
    return {"base": (at - v["baseline_s"], at), "end": (end + v["watch_s"] - v["end_s"], end + v["watch_s"])}


def later_turns(run: dict):
    """Ok later session turns with the previous turn's prompt length and end, by session order (no window applied)."""
    q = run["requests"]
    q = q[~is_burst_request(run)].sort_values(["session_id", "turn"]).copy()
    g = q.groupby("session_id")
    q["prev_turn"], q["prev_prompt"], q["prev_end"] = g.turn.shift(), g.prompt_tokens.shift(), g.t_end.shift()
    return q[(q.turn > 0) & (q.prev_turn == q.turn - 1) & (q.status == "ok")]


def reuse(run: dict, a: float, b: float) -> float:
    """Σ cached tokens / Σ previous-turn prompt tokens over ok later turns with first token in [a, b); NaN if none.
    A turn's reusable prefix is its previous prompt (harness/workload.py: the recorded reply is not cached)."""
    q = later_turns(run)
    q = q[(q.t_first_token >= a) & (q.t_first_token < b)]
    den = q.prev_prompt.sum()
    return float(np.minimum(q.cached_tokens, q.prev_prompt).sum() / den) if len(q) and den > 0 else math.nan


def _state(run: dict, win: dict, v: dict) -> dict:
    base, end = _level(run, *win["base"]), _level(run, *win["end"])
    ru = {"base": reuse(run, *win["base"]), "end": reuse(run, *win["end"])}
    vals = (ru["base"], ru["end"], base["q"], end["q"], end["kv"])
    if any(math.isnan(x) for x in vals):
        cold = rec = parts = None
    else:
        parts = {"reuse_cold": ru["end"] <= ru["base"] - v["stuck_hit_drop"],
                 "backlogged": end["q"] > base["q"] + v["recovered_q_excess"],
                 "kv_full": end["kv"] >= SURGE["kv_onset"]}
        cold = all(parts.values())
        rec = ru["end"] >= ru["base"] - v["recovered_hit_drop"] and end["q"] <= base["q"] + v["recovered_q_excess"]
    return {"cold_backlogged": cold, "recovered": rec, "parts": parts, "reuse": ru,
            "base": {k: base[k] for k in ("hit", "q", "kv", "pf")}, "end": {k: end[k] for k in ("hit", "q", "kv", "n")},
            "windows": win}


def cold_backlogged(run: dict, win: dict | None = None, rules: dict | None = None) -> dict:
    """The K1 readout on one run. `win` defaults to the run's own burst windows; `rules` (the verdict thresholds) to
    its own config. `cold_backlogged` and `recovered` are None when any input is NaN, never rounded."""
    return _state(run, win or windows(run["cfg"]), rules or run["cfg"]["verdict"])


def sessions_in_service(run: dict, a: float, b: float) -> float:
    """Mean number of sessions in service over [a, b) on a grid: from a session's first turn sent to its last reply
    (`docs/definitions.md`, session cap); a session with an unfinished or unsent turn stays in service."""
    q = run["requests"]
    q = q[~is_burst_request(run)]
    g = q.groupby("session_id")
    start = g.t_sent.min()
    done = g.t_end.max().where(g.t_end.apply(lambda s: s.notna().all()), np.inf)
    grid = np.arange(a, b, REG20["service_grid_s"])
    return float(np.mean([((start <= t) & (done > t)).sum() for t in grid])) if len(grid) else math.nan


def mechanism(run: dict) -> dict:
    """The held-prefix contrast after the burst ([end + a, end + b)): the overlap share (`gate.overlap_share`, REG-7)
    and its pre-burst reference; and the prefix reuse of later turns whose first token came before the previous
    turn's end (held) against those after it (idle). The mechanism is shown when the overlap share is above
    overlap_min and held turns reuse more than idle ones."""
    e, (a, b) = burst_end(run), REG20["mech_window"]
    win = windows(run["cfg"])
    q = later_turns(run)
    q = q[(q.t_first_token >= e + a) & (q.t_first_token < e + b)]
    share = lambda d: (float(np.minimum(d.cached_tokens, d.prev_prompt).sum() / d.prev_prompt.sum())
                       if len(d) and d.prev_prompt.sum() > 0 else math.nan)
    held, idle = share(q[q.t_first_token < q.prev_end]), share(q[q.t_first_token >= q.prev_end])
    ov = overlap_share(run, e + a, e + b)
    shown = (not math.isnan(ov) and ov > REG20["overlap_min"] and not math.isnan(held)
             and (math.isnan(idle) or held > idle))
    return {"overlap": ov, "overlap_base": overlap_share(run, *win["base"]), "reuse_held": held, "reuse_idle": idle,
            "shown": shown}


def readouts(run: dict) -> dict:
    """Reported beside the decision, never deciding it: shock size, first-turn share of completions in the end
    window, sessions in service before the burst and in the end window."""
    win, e = windows(run["cfg"]), burst_end(run)
    a, b = win["end"]
    return {"shock": shock_size(run), "turn0_end": turn0_share(run, [(a - e, b - e)])[0],
            "in_service_base": sessions_in_service(run, *win["base"]),
            "in_service_end": sessions_in_service(run, a, b)}


def _runs(pattern: str) -> tuple[dict | None, int]:
    """(the one valid run or None, the number of invalid runs). A second valid run is outside the registration."""
    runs = find_runs(pattern, valid_only=False)
    ok = [r for r in runs if r["checks"] and r["checks"]["valid"]]
    if len(ok) > 1:
        raise ValueError(f"{pattern}: {len(ok)} valid runs, REG-20 needs at most one")
    return (ok[0] if ok else None), len(runs) - len(ok)


def open_seed(burst: dict | None, control: dict | None, lost: bool = False) -> dict:
    """An open-arm seed. Labels: `recovered_open`; `partial_open` (neither recovered nor cold-backlogged);
    `stuck_open` (cold-backlogged, its control not cold over the same windows); `overload_open` (both cold);
    `pending_control` (cold, no valid control yet); `cold_control` (cold, control unreadable); `unclear` (a NaN
    readout); `lost_open` (the burst run invalid after its rerun). `lost_open` and `cold_control` count as cold
    (rule F review, T3: a stuck open-loop run is the likeliest to fail its checks)."""
    if burst is None:
        return {"label": "lost_open" if lost else "not_run", "cold_backlogged": None, "mechanism": None,
                "control": None}
    r = cold_backlogged(burst)
    out = {"run": burst["dir"].name, **r, "mechanism": mechanism(burst), "readouts": readouts(burst), "control": None}
    if r["cold_backlogged"] is None:
        out["label"] = "unclear"
    elif not r["cold_backlogged"]:
        out["label"] = "recovered_open" if r["recovered"] else "partial_open"
    elif control is None:
        out["label"] = "pending_control"
    else:
        c = cold_backlogged(control, r["windows"], burst["cfg"]["verdict"])
        out["control"] = {"run": control["dir"].name, **c}
        out["label"] = ("cold_control" if c["cold_backlogged"] is None
                        else "overload_open" if c["cold_backlogged"] else "stuck_open")
    return out


OPEN_COLD = ("stuck_open", "overload_open", "pending_control", "cold_control", "lost_open")


def mcnemar_one_sided(b: int, c: int) -> float:
    """Exact one-sided McNemar: P(X >= b), X ~ Binomial(b + c, 1/2); b = pairs cold only in the closed arm,
    c = pairs cold only in the open arm. 1.0 with no discordant pair."""
    d = b + c
    return sum(math.comb(d, i) for i in range(b, d + 1)) / 2 ** d if d else 1.0


def a_may_start(closed: list[bool | None], test: str | None = None) -> dict:
    """Arm A runs only if `supports` is reachable from REG-19's closed arm: the best case (no open run cold, no
    unclear seed) passes the registered test at alpha (rule F review, recommendation 2)."""
    k = sum(c is True for c in closed)
    n = sum(c is not None for c in closed)
    p = _p(test or REG20["test"], k, n, [(c, False) for c in closed if c is not None])
    return {"k_closed": k, "n": n, "best_p": p, "may_start": n >= REG20["min_n"] and p <= REG20["alpha"]}


def _p(test: str, k_c: int, n: int, pairs: list[tuple[bool, bool]]) -> float:
    if n < 1:
        return math.nan
    if test == "fisher":
        return fisher_one_sided(k_c, n, sum(o for _, o in pairs), n)
    if test == "mcnemar":
        return mcnemar_one_sided(sum(c and not o for c, o in pairs), sum(o and not c for c, o in pairs))
    raise ValueError(f"unknown test {test!r}")


def k1_outcome(closed: list[bool | None], open_rows: list[dict], test: str | None = None) -> dict:
    """The registered decision on seeds with a closed run (True/False) and an open row, paired by seed. A seed with
    an `unclear` reading in either arm, or no open run, leaves n and is listed. Rules, in this order:
      too_few (n < min_n) -> pending_controls -> open_arm_overload -> closed_not_cold (no closed run cold)
      -> refutes (stuck_open + lost_open + cold_control >= refute_k) -> supports (the registered test's p <= alpha,
      every non-cold open run `recovered_open`, mechanism shown in each) -> supports_no_mechanism (the same, mechanism
      not shown in every one) -> inconclusive."""
    test = test or REG20["test"]
    keep, dropped = [], []
    for i, (c, o) in enumerate(zip(closed, open_rows)):
        (dropped if c is None or o["label"] in ("unclear", "not_run") else keep).append((i, c, o))
    pairs = [(c, o["label"] in OPEN_COLD) for _, c, o in keep]
    n, k_c, k_o = len(keep), sum(c for c, _ in pairs), sum(o for _, o in pairs)
    labels = [o["label"] for _, _, o in keep]
    p = _p(test, k_c, n, pairs)
    p_other = _p("fisher" if test == "mcnemar" else "mcnemar", k_c, n, pairs)
    warm = [o for _, _, o in keep if o["label"] not in OPEN_COLD]
    clean = all(o["label"] == "recovered_open" for o in warm)
    mech = bool(warm) and all(o["mechanism"] and o["mechanism"]["shown"] for o in warm)
    k_stuck = sum(lab in ("stuck_open", "lost_open", "cold_control") for lab in labels)
    if n < REG20["min_n"]:
        out = "too_few"
    elif "pending_control" in labels:
        out = "pending_controls"
    elif "overload_open" in labels:
        out = "open_arm_overload"
    elif k_c == 0:
        out = "closed_not_cold"
    elif k_stuck >= REG20["refute_k"]:
        out = "refutes"
    elif p <= REG20["alpha"] and clean:
        out = "supports" if mech else "supports_no_mechanism"
    else:
        out = "inconclusive"
    return {"outcome": out, "test": test, "n": n, "dropped": [i for i, _, _ in dropped], "k_closed": k_c,
            "k_open": k_o, "k_stuck_open": k_stuck, "p": p, "p_other_test": p_other,
            "partial_open": labels.count("partial_open"), "mechanism": mech}


def b_may_start(a: dict) -> bool:
    """Arm B (the headroom check) runs only if arm A supports K1."""
    return a["outcome"] in ("supports", "supports_no_mechanism")


def b_outcome(rows: list[dict]) -> str:
    """Arm B: `headroom_weakened` if every planned seed is `recovered_open`; `headroom_open` if any is cold, lost or
    partial; `incomplete` otherwise (a seed not run, unclear, or waiting for its control)."""
    labels = [r["label"] for r in rows]
    if len(rows) < len(REG20["b_seeds"]) or any(lab in ("unclear", "not_run", "pending_control") for lab in labels):
        return "incomplete"
    return "headroom_weakened" if all(lab == "recovered_open" for lab in labels) else "headroom_open"


def drift(closed_row: dict, rerun: dict | None) -> dict:
    """The drift check: one closed seed rerun under a new config name, interleaved with arm A. `agrees` when both
    give the same cold-backlogged reading; a disagreement is reported with the result, not a verdict changer."""
    if rerun is None:
        return {"run": None, "agrees": None}
    r = cold_backlogged(rerun)
    return {"run": rerun["dir"].name, "cold_backlogged": r["cold_backlogged"],
            "agrees": None if r["cold_backlogged"] is None or closed_row["cold_backlogged"] is None
            else r["cold_backlogged"] == closed_row["cold_backlogged"]}


def reg20_closed() -> list[dict]:
    """REG-19's closed burst runs as REG-20 reads them; seeds with no valid run are listed with None."""
    rows = []
    for sd in REG20["closed_seeds"]:
        cb, _ = _runs(closed_pattern(sd))
        rows.append({"seed": sd, "run": None, "cold_backlogged": None} if cb is None else
                    {"seed": sd, "run": cb["dir"].name, **cold_backlogged(cb), "readouts": readouts(cb)})
    return rows


def reg20_a_may_start() -> dict:
    return a_may_start([r["cold_backlogged"] for r in reg20_closed()])


def _open_row(lam: float, sd: int) -> dict:
    ob, n_bad = _runs(open_pattern(lam, sd))
    oc, _ = _runs(open_pattern(lam, sd, control=True))
    return {"seed": sd, **open_seed(ob, oc, lost=ob is None and n_bad >= 2)}


def reg20_table() -> dict:
    """REG-20 on the runs present."""
    closed = reg20_closed()
    open_a = [_open_row(REG20["a_lam"], r["seed"]) for r in closed]
    a = k1_outcome([r["cold_backlogged"] for r in closed], open_a)
    b_rows = [_open_row(REG20["b_lam"], sd) for sd in REG20["b_seeds"]]
    rerun, _ = _runs(f"*_{REG20['drift_cfg']}")
    first = next(r for r in closed if r["seed"] == int(REG20["drift_cfg"].rsplit("_s", 1)[1].split("_")[0]))
    return {"start": a_may_start([r["cold_backlogged"] for r in closed]), "closed": closed, "open_a": open_a, "a": a,
            "b_may_start": b_may_start(a), "open_b": b_rows,
            "b": "not_run" if all(r["label"] == "not_run" for r in b_rows) else b_outcome(b_rows),
            "drift": drift(first, rerun)}


if __name__ == "__main__":
    import sys
    print({"reg20": reg20_table, "reg20_a_may_start": reg20_a_may_start}[sys.argv[1]]())
