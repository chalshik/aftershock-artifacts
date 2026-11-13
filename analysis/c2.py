"""C2, condition 4 (a memory-limited loop, not just a queue) on stuck burst runs: REG-22 (draft until registered).
Never writes into runs/.

PROTOCOL §3, condition 4: "mean KV >= 0.80, mean N >= 2 x baseline, N below the 256 cap, and the traces follow the
plan's order" (decisions.md 2026-11-01: "at `end`"). The plan's order (hit rate drops first, then recomputed prefill
rises, the batch grows, KV fills) was written for a cache wipe. A burst fills the pool itself, so on a burst run the
entry order is the trigger's, not the loop's. What a burst run can show of the loop is that its links hold together
once the burst's own requests have left. So condition 4 is read here as two judged parts:

  levels   in the end window: mean KV >= min_kv, mean N >= n_factor x baseline N, max N < n_cap   (as registered)
  sustain  in every span of the watch that starts after the last burst request has ended, all four links hold:
           reuse of later turns <= baseline - the verdict's stuck_hit_drop   (the cache is lost)
           session uncached prefill tokens/s >= u_factor x baseline            (the prompts are recomputed)
           mean N >= n_factor x baseline N                                     (the batch is large)
           mean KV >= min_kv                                                   (the pool is full)
and one reported part, the onset times of the four signals after the trigger's start (`onsets`), with their order.
"""
from __future__ import annotations

import math

import numpy as np

from analysis.k1 import later_turns
from analysis.load import _covered, find_runs, verdict
from analysis.margin import is_burst_request
from analysis.stats import cp_upper

C2 = {
    "min_kv": 0.80, "n_factor": 2.0, "n_cap": 256,   # PROTOCOL §3 condition 4 (decisions.md 2026-11-01)
    "u_factor": 2.0,        # session uncached prefill rate at least this multiple of its baseline
    "span_s": 300.0,        # the watch is cut into spans of this length from the burst's end
    "min_spans": 2,         # `sustain` needs at least this many spans after the last burst request
    "roll_s": 60.0, "step_s": 10.0, "min_turns": 20,   # onsets: trailing windows on a grid; reuse needs this many turns
    "kv_onset": 0.9,        # as gate.SURGE["kv_onset"]
    "gauge_max_gap_s": 10.0,   # a gauge value over a window needs scrapes covering it with no gap above this
}
KV, N = "vllm:kv_cache_usage_perc", "vllm:num_requests_running"


def windows(run: dict) -> dict:
    t, v = run["cfg"]["trigger"], run["cfg"]["verdict"]
    at, end = float(t["at_s"]), float(t["at_s"] + t["duration_s"])
    return {"at": at, "end": end, "base": (at - v["baseline_s"], at), "watch_end": end + v["watch_s"],
            "end_window": (end + v["watch_s"] - v["end_s"], end + v["watch_s"])}


def gauge(run: dict, col: str, a: float, b: float, how: str = "mean") -> float:
    """Mean (or `how`) of a gauge over [a, b). NaN when the gauge does not cover the window: no scrapes, no such
    column, or a gap between its values above gauge_max_gap_s (`load._covered`). A mean over the few scrapes that
    happen to exist is not a level of the window."""
    m = run["metrics"]
    if not len(m) or col not in m:
        return math.nan
    g = m[["t", col]].dropna()
    if not _covered(g.t.to_numpy(float), a, b, C2["gauge_max_gap_s"]):
        return math.nan
    w = g[(g.t >= a) & (g.t < b)][col]
    return float(getattr(w, how)()) if len(w) else math.nan


def reuse_in(turns, a: float, b: float, min_turns: int = 1) -> float:
    q = turns[(turns.t_first_token >= a) & (turns.t_first_token < b)]
    den = q.prev_prompt.sum()
    return float(np.minimum(q.cached_tokens, q.prev_prompt).sum() / den) if len(q) >= min_turns and den > 0 else math.nan


def session_uncached_rate(run: dict, a: float, b: float) -> float:
    """Uncached prompt tokens per second over ok session requests (no burst rows) whose first token falls in [a, b)."""
    q = run["requests"]
    ok = q[~is_burst_request(run) & (q.status == "ok")]
    if ok.t_first_token.isna().any() or ok.prompt_tokens.isna().any():
        raise ValueError("an ok session request without a first-token time or prompt_tokens: the rate would leave it out")
    w = ok[(ok.t_first_token >= a) & (ok.t_first_token < b)]
    return float((w.prompt_tokens - w.cached_tokens.fillna(0)).clip(lower=0).sum() / (b - a))


def baseline(run: dict, window: tuple | None = None) -> dict:
    """The four values over the baseline window (the run's own, or `window` for a control, which has no trigger)."""
    a, b = window or windows(run)["base"]
    return {"reuse": reuse_in(later_turns(run), a, b, C2["min_turns"]), "u": session_uncached_rate(run, a, b),
            "n": gauge(run, N, a, b), "kv": gauge(run, KV, a, b)}


def levels(run: dict, base: dict | None = None) -> dict:
    """The registered levels in the end window."""
    base = base or baseline(run)
    a, b = windows(run)["end_window"]
    kv, n, n_max = gauge(run, KV, a, b), gauge(run, N, a, b), gauge(run, N, a, b, "max")
    vals = (kv, n, n_max, base["n"])
    if any(math.isnan(x) for x in vals):
        ok, failed = None, None
    else:
        failed = [k for k, bad in (("kv", kv < C2["min_kv"]), ("n", n < C2["n_factor"] * base["n"]),
                                   ("n_cap", n_max >= C2["n_cap"])) if bad]
        ok = not failed
    return {"kv": kv, "n": n, "n_over_base": n / base["n"] if base["n"] else math.nan, "n_max": n_max, "ok": ok,
            "failed": failed}


def last_burst_end(run: dict) -> float:
    """When the last burst request ended ("the exit"). NaN if a burst request never ended (the burst is then still
    in the system), if one ended with an error status, or if the run has no burst rows."""
    q = run["requests"]
    b = q[is_burst_request(run)]
    if not len(b) or (b.status != "ok").any() or b.t_end.isna().any():
        return math.nan
    return float(b.t_end.max())


def links(run: dict, a: float, b: float, base: dict, turns=None) -> dict:
    """The loop's four links over [a, b); `holds` is None when a value is missing (fewer than min_turns later turns
    give no reuse); `failed` names the links that do not hold."""
    turns = later_turns(run) if turns is None else turns
    drop = float(run["cfg"]["verdict"]["stuck_hit_drop"])
    v = {"reuse": reuse_in(turns, a, b, C2["min_turns"]), "u": session_uncached_rate(run, a, b),
         "n": gauge(run, N, a, b), "kv": gauge(run, KV, a, b)}
    if any(math.isnan(x) for x in (*v.values(), base["reuse"], base["u"], base["n"])):
        return {**v, "span": (a, b), "holds": None, "failed": None}
    failed = [k for k, bad in (("reuse", v["reuse"] > base["reuse"] - drop), ("u", v["u"] < C2["u_factor"] * base["u"]),
                               ("n", v["n"] < C2["n_factor"] * base["n"]), ("kv", v["kv"] < C2["min_kv"])) if bad]
    return {**v, "span": (a, b), "holds": not failed, "failed": failed}


def sustain(run: dict, base: dict | None = None) -> dict:
    """The links in every 300 s span of the watch. A span is judged when it starts at or after the exit (the last
    burst request's end); the earlier spans are reported with `judged` False. With fewer than min_spans judged spans
    (or no exit) the result is None. Otherwise one judged span that fails decides (False), whatever the others are;
    with none failing, a judged span with a missing value gives None; else True."""
    base, w = base or baseline(run), windows(run)
    tb = last_burst_end(run)
    turns = later_turns(run)
    rows = []
    for a in np.arange(w["end"], w["watch_end"] - 1e-9, C2["span_s"]):
        r = links(run, float(a), float(min(a + C2["span_s"], w["watch_end"])), base, turns)
        rows.append({**r, "judged": (not math.isnan(tb)) and a >= tb})
    judged = [r for r in rows if r["judged"]]
    if len(judged) < C2["min_spans"]:
        ok = None
    elif any(r["holds"] is False for r in judged):
        ok = False
    elif any(r["holds"] is None for r in judged):
        ok = None
    else:
        ok = True
    return {"last_burst_end": tb, "n_spans": len(judged), "spans": rows, "ok": ok,
            "links_failed": sorted({k for r in judged for k in (r["failed"] or [])})}


def onsets(run: dict, base: dict | None = None) -> dict:
    """Reported, never judged: the first grid time after the trigger's start at which each signal, over the trailing
    roll_s, crosses its level (KV >= kv_onset; N >= n_factor x baseline; reuse <= baseline - stuck_hit_drop with at
    least min_turns turns; session uncached rate >= u_factor x baseline), and the order found."""
    base, w = base or baseline(run), windows(run)
    drop, turns = float(run["cfg"]["verdict"]["stuck_hit_drop"]), later_turns(run)
    out = {"kv": math.nan, "n": math.nan, "reuse": math.nan, "u": math.nan}
    for t in np.arange(w["at"] + C2["step_s"], w["watch_end"] + 1e-9, C2["step_s"]):
        a = t - C2["roll_s"]
        tests = {"kv": lambda: gauge(run, KV, a, t) >= C2["kv_onset"],
                 "n": lambda: gauge(run, N, a, t) >= C2["n_factor"] * base["n"],
                 "reuse": lambda: reuse_in(turns, a, t, C2["min_turns"]) <= base["reuse"] - drop,
                 "u": lambda: session_uncached_rate(run, a, t) >= C2["u_factor"] * base["u"]}
        for k, f in tests.items():
            if math.isnan(out[k]) and f():      # a NaN comparison is False
                out[k] = float(t)
        if not any(math.isnan(x) for x in out.values()):
            break
    times = sorted({v for v in out.values() if not math.isnan(v)})
    return {**out, "order": [sorted(k for k, v in out.items() if v == x) for x in times]}   # equal times: one group


def condition4(run: dict, with_readouts: bool = True) -> dict:
    """One run's label: 'loop' (levels and sustain hold), 'not_memory_limited' (levels fail: a backlog, not this
    loop), 'not_sustained' (levels hold but a link is missing in some span after the burst's requests left),
    'undefined' (a value is missing, or fewer than min_spans spans after the last burst request). The reported
    readouts come after the label, and one that raises is kept as its message."""
    base = baseline(run)
    lv, su = levels(run, base), sustain(run, base)
    if lv["ok"] is None or (lv["ok"] and su["ok"] is None):
        label = "undefined"
    elif not lv["ok"]:
        label = "not_memory_limited"
    else:
        label = "loop" if su["ok"] else "not_sustained"
    out = {"run": run["dir"].name, "baseline": base, "levels": lv, "sustain": su, "label": label}
    if with_readouts:
        for key, f in (("onsets", lambda: onsets(run, base)),
                       ("onset_reading", lambda: onset_reading(run, base, out["onsets"])),
                       ("planned", lambda: planned_rates(run, su)), ("evictions", lambda: eviction_readout(run)),
                       ("control", lambda: control_readout(run, su)), ("rows", lambda: row_counts(run))):
            try:
                out[key] = f()
            except Exception as e:   # a reported readout never takes the judged label with it
                out[key] = {"error": f"{type(e).__name__}: {e}"[:200]}
    return out



# ---------------------------------------------------------------- the eviction link, read directly (reported only)

HIST = {"idle": "vllm:kv_block_idle_before_evict_seconds", "lifetime": "vllm:kv_block_lifetime_seconds",
        "reuse_gap": "vllm:kv_block_reuse_gap_seconds"}


def _buckets(values: dict, name: str) -> dict[float, float]:
    """Cumulative bucket counts of one histogram in one scrape, summed over label sets: upper edge -> count."""
    out: dict[float, float] = {}
    pre = name + "_bucket{"
    for k, v in values.items():
        if k.startswith(pre):
            le = k.split('le="', 1)[1].split('"', 1)[0]
            e = math.inf if le == "+Inf" else float(le)
            out[e] = out.get(e, 0.0) + v
    return out


def histogram_delta(metrics_jsonl, name: str, a: float, b: float) -> dict:
    """What a sampled residency histogram gained in [a, b): from the first scrape at or after a to the last before b
    (raw metrics.jsonl; `load.metrics_wide` drops the buckets). Returns the count, the upper edge of the bucket that
    holds the median (and its lower edge), and the shares at or below 5 s (the mean turn gap) and 30 s. NaN where
    nothing was sampled. A bucket lower than at the scrape before, at any scrape of the window, is a restart: the
    window is flagged `reset` and not read.
    SOURCE(vLLM 0.32.0 v1/core/kv_cache_metrics.py:KVCacheMetricsCollector.on_block_evicted): for a sampled block
    `idle` is the time from its last access (its allocation, or a later cache hit) to its eviction, so it includes
    the time the block was held by the request that computed it; `reuse_gap` is the time between two cache hits."""
    import json
    first = last = None
    went_down = False
    with open(metrics_jsonl) as f:
        for line in f:
            if not line.strip():
                continue
            s = json.loads(line)
            if "values" not in s or s["t"] < a:
                continue
            if s["t"] >= b:
                break
            cur = _buckets(s["values"], name)
            if first is None:
                first = cur
            elif any(v < last.get(e, 0.0) for e, v in cur.items()):   # any bucket lower than at the scrape before
                went_down = True
            last = cur
    nan = {"count": 0.0, "median_le_s": math.nan, "median_gt_s": math.nan, "share_le_5s": math.nan,
           "share_le_30s": math.nan}
    if not first or not last:
        return nan
    d = {e: last.get(e, 0.0) - first.get(e, 0.0) for e in sorted(last)}
    total = d.get(math.inf, 0.0)
    if went_down or any(v < 0 for v in d.values()):       # a counter went down: a restart inside the window
        return {**nan, "reset": True}
    if total <= 0:                                         # nothing sampled
        return nan
    edges = sorted(d)
    i = next(j for j, e in enumerate(edges) if d[e] >= total / 2)
    return {"count": total, "median_le_s": edges[i], "median_gt_s": edges[i - 1] if i else 0.0,
            "share_le_5s": d.get(5.0, math.nan) / total, "share_le_30s": d.get(30.0, math.nan) / total}


def turn_spacing(run: dict, a: float, b: float) -> float:
    """Median time between the first tokens of consecutive turns of a session, over later turns whose first token
    falls in [a, b): how long a prefix has to survive to be reused."""
    q = run["requests"]
    q = q[~is_burst_request(run) & (q.status == "ok")].sort_values(["session_id", "turn"])
    prev = q.groupby("session_id").t_first_token.shift()
    w = q[(q.turn > 0) & (q.t_first_token >= a) & (q.t_first_token < b)]
    gaps = (w.t_first_token - prev[w.index]).dropna()
    return float(gaps.median()) if len(gaps) else math.nan


def eviction_readout(run: dict) -> dict:
    """Reported, never judged: the three residency histograms and the turn spacing in the baseline and in the stretch
    from the last burst request's end (or the burst's end, if that is NaN) to the end of the watch."""
    w, path = windows(run), run["dir"] / "metrics.jsonl"
    tb = last_burst_end(run)
    after = (w["end"] if math.isnan(tb) else max(tb, w["end"]), w["watch_end"])
    out = {}
    for label, (a, b) in (("baseline", w["base"]), ("after", after)):
        out[label] = {"span": (a, b), "turn_spacing_s": turn_spacing(run, a, b),
                      **{k: histogram_delta(path, name, a, b) for k, name in HIST.items()}} if path.exists() else None
    return out


def row_counts(run: dict) -> dict:
    """Reported only: ok session requests, how many of them carry no cached_tokens (counted as a full miss), and
    requests that got a first token and never finished (not counted in the uncached rate)."""
    q = run["requests"]
    s = q[~is_burst_request(run)]
    ok = s[s.status == "ok"]
    return {"ok_session": int(len(ok)), "ok_without_cached_tokens": int(ok.cached_tokens.isna().sum()),
            "first_token_never_finished": int(((s.status != "ok") & s.t_first_token.notna()).sum())}


def control_readout(run: dict, su: dict) -> dict:
    """Reported only: the same-seed control of a burst run (the same session schedule, no burst), its registered
    verdict, and its links over the burst run's judged spans against its own baseline. A queue that the load alone
    explains would hold the links in the control too; a state the burst left behind would not."""
    name = run["cfg"]["name"]
    cname = REG22["controls"].get(name) or ("stage2_control_" + name[len("burst_"):] if name.startswith("burst_") else None)
    if cname is None:
        return {"why": "this config has no control"}
    got = find_runs(f"*_{cname}")
    if len(got) != 1:
        return {"why": f"{len(got)} valid runs of {cname}"}
    c, w = got[0], windows(run)
    base = baseline(c, w["base"])
    judged = [r["span"] for r in su["spans"] if r["judged"]]
    spans = [links(c, *s, base) for s in judged]
    # Also against the burst run's own baseline: a control already cold or large in [base) cannot double its own
    # baseline, so its own-baseline links would say "no loop" for a state the load alone made (rule F round 2).
    spans_vs_burst = [links(c, *s, baseline(run)) for s in judged]
    return {"run": c["dir"].name, "verdict": verdict(c)["verdict"], "baseline": base,
            "spans": spans, "links_hold_in_every_span": all(s["holds"] is True for s in spans) if spans else None,
            "links_hold_in_no_span": all(s["holds"] is False for s in spans) if spans else None,
            "spans_vs_burst_baseline": spans_vs_burst,
            "links_hold_in_every_span_vs_burst_baseline":
                all(s["holds"] is True for s in spans_vs_burst) if spans_vs_burst else None}


# ------------------------------------------- reported only, added in REG-22 draft 5 (owner-proxy round 1, items 3a-3h)

PLAN_ORDER = ("reuse", "u", "n", "kv")   # docs/experiment-plan.md, "Watch it happen", items 1 to 4


def planned_rates(run: dict, su: dict) -> list[dict]:
    """Reported only: each span's planned session rate (`gate.planned_session_rate`), to stand beside a link that
    failed in a span planned below the cold completion rate."""
    from analysis.gate import planned_session_rate
    return [{"span": r["span"], "lam_p": planned_session_rate(run, *r["span"])} for r in su["spans"]]


def onset_reading(run: dict, base: dict, on: dict) -> dict:
    """Reported, never judged: is the order of the onsets the plan's beyond what the trailing window does by itself?
    For a step at one instant from `before` (the baseline value) to `after` (the end-window value), a trailing roll_s
    mean crosses the onset's level lag = roll_s x (level - before) / (after - before) seconds after the step; onset
    minus lag is the step time the onset implies. For every pair x, y with x before y in the plan's order: `plan` if
    y's implied step is more than step_s (the onsets' grid) after x's, `reversed` if more than step_s before, else
    `together`. The run's reading: `incomplete` if a signal has no onset or no lag (its end value does not pass its
    level); else `differs` if a pair is `reversed`; `plan_order_beyond_lags` if every pair is `plan`; otherwise
    `not_distinguishable_from_simultaneous`. A ramp crosses with another lag; that is not modelled."""
    a, b = windows(run)["end_window"]
    drop = float(run["cfg"]["verdict"]["stuck_hit_drop"])
    after = {"reuse": reuse_in(later_turns(run), a, b, C2["min_turns"]), "u": session_uncached_rate(run, a, b),
             "n": gauge(run, N, a, b), "kv": gauge(run, KV, a, b)}
    level = {"reuse": base["reuse"] - drop, "u": C2["u_factor"] * base["u"], "n": C2["n_factor"] * base["n"],
             "kv": C2["kv_onset"]}
    lag, step = {}, {}
    for k in PLAN_ORDER:
        d = after[k] - base[k]
        f = (level[k] - base[k]) / d if (d and not math.isnan(d)) else math.nan
        lag[k] = C2["roll_s"] * f if 0 < f <= 1 else math.nan            # a NaN comparison is False
        step[k] = float(on[k]) - lag[k]
    pairs = []
    for i, x in enumerate(PLAN_ORDER):
        for y in PLAN_ORDER[i + 1:]:
            dt = step[y] - step[x]
            pairs.append({"pair": (x, y), "dt_s": dt, "reading": None if math.isnan(dt) else
                          ("plan" if dt > C2["step_s"] else "reversed" if dt < -C2["step_s"] else "together")})
    rs = [p["reading"] for p in pairs]
    reading = ("incomplete" if None in rs else "differs" if "reversed" in rs else
               "plan_order_beyond_lags" if all(r == "plan" for r in rs) else "not_distinguishable_from_simultaneous")
    return {"plan_order": list(PLAN_ORDER), "found_order": on.get("order"), "after": after, "level": level,
            "lag_s": lag, "implied_step_s": step, "pairs": pairs, "reading": reading}


def reported_counts(table: dict) -> dict:
    """Reported, never judged, from `reg22_table`'s rows: per load, how many `loop` runs have a same-seed control that
    is `recovered` and holds the four links in none of the burst run's judged spans; over the stuck runs, the tally of
    `onset_reading`'s readings (a readout that raised counts as `error`). A tally, no bound."""
    per: dict[str, dict] = {}
    for r in table["rows"]:
        g = per.setdefault(f"{r['lam']:.1f}", {"loop": 0, "loop_with_recovered_control_holding_no_link_set": 0})
        if r["label"] == "loop":
            g["loop"] += 1
            c = r.get("control") or {}
            if c.get("verdict") == "recovered" and c.get("links_hold_in_no_span") is True:
                g["loop_with_recovered_control_holding_no_link_set"] += 1
    readings = [(r.get("onset_reading") or {}).get("reading", "error") for r in table["rows"]]
    return {"by_load": per, "onset_readings": {k: readings.count(k) for k in sorted(set(readings))}}


REG22 = {
    # REG-11's control carries no seed in its name; every other burst config maps by its own name.
    "controls": {"burst_l1pl350cl_r2.4_s1": "stage2_control_l1pl350cl_r2.4"},
    # The closed-loop L1 burst runs at 350 W made before REG-19 (REG-11, REG-12, REG-14, REG-15, REG-17, REG-18), as
    # k3.REG21["batch1"]. A run is judged only if its registered verdict (`load.verdict`) is "stuck".
    "runs": ("20261109-042828_burst_l1pl350cl_r2.4_s1", "20261109-080203_burst_l1pl350cl_r2.4_s2",
             "20261109-093609_burst_l1pl350cl_r2.4_s3", "20261109-111316_burst_l1pl350cl_r2.4_s4",
             "20261109-125300_burst_l1pl350cl_r2.4_s5", "20261109-151300_burst_l1pl350cl_r2.4_s6",
             "20261110-063647_burst_l1pl350cl_r2.2_s2", "20261110-085730_confirm_l1pl350cl_r2.2_s12",
             "20261110-182920_burst_l1pl350cl_r2.0_s2", "20261111-101805_burst_l1pl350cl_r2.0_s4",
             "20261111-115409_burst_l1pl350cl_r2.0_s3", "20261111-133019_burst_l1pl350cl_r2.0_s5",
             "20261111-150642_burst_l1pl350cl_r2.0_s6"),
}


def batch_runs(batch: int) -> list[dict]:
    """Batch 1: the 13 registered runs, each valid; raises if one is missing or invalid. Batch 2: REG-19's burst runs
    as `k3w.batch2_runs` gives them (only after REG-19's [RESULT]; one valid run per seed, at least three seeds)."""
    if batch == 1:
        found = {i: find_runs(i) for i in REG22["runs"]}
        missing = [i for i, v in found.items() if len(v) != 1]
        if missing:
            raise ValueError(f"REG-22 needs its {len(REG22['runs'])} registered runs, each valid: not so for {missing}")
        return [found[i][0] for i in REG22["runs"]]
    if batch == 2:
        from analysis.k3w import batch2_runs
        return batch2_runs()
    raise ValueError("REG-22 has batch 1 and batch 2")


def reg22_table(batch: int = 1) -> dict:
    """Condition 4 on every run of the batch whose registered verdict is "stuck"; the others are listed with their
    verdict. The labels are computed before any reported readout. Per load: k of n `loop` with its one-sided 95 %
    Clopper-Pearson upper bound (rule H); loads are never pooled. Each batch is computed once."""
    judged, left = [], []
    for run in batch_runs(batch):
        v = verdict(run)["verdict"]
        (judged if v == "stuck" else left).append(run if v == "stuck" else {"run": run["dir"].name, "why": f"verdict {v}"})
    labels = [condition4(r, with_readouts=False)["label"] for r in judged]
    kinds = ("loop", "not_sustained", "not_memory_limited", "undefined")
    by_load: dict[str, list[str]] = {}
    for r, lab in zip(judged, labels):
        by_load.setdefault(f"{float(r['cfg']['workload']['rate']):.1f}", []).append(lab)
    rows = [{**condition4(r), "lam": float(r["cfg"]["workload"]["rate"]), "seed": r["cfg"].get("seed")} for r in judged]
    return {"batch": batch, "left_out": left, "n_stuck": len(judged), "counts": {k: labels.count(k) for k in kinds},
            "by_load": {g: {"n": len(v), **{k: v.count(k) for k in kinds},
                            "loop_cp_upper_95": cp_upper(v.count("loop"), len(v)),
                            "loop_cp_lower_95": 1.0 - cp_upper(len(v) - v.count("loop"), len(v))}
                        for g, v in sorted(by_load.items())},
            "rows": rows}


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) in (2, 3) and sys.argv[1] == "reg22":
        from analysis.k3w import _dirty
        if _dirty():
            raise SystemExit("analysis/ or tests/ holds modified or untracked files; REG-22 runs from committed code:\n" + _dirty())
        table = reg22_table(int(sys.argv[2]) if len(sys.argv) == 3 else 1)
        print(json.dumps({**table, "reported": reported_counts(table)}, indent=1, default=str))
    else:
        raise SystemExit("usage: python -m analysis.c2 reg22 [1|2]")
