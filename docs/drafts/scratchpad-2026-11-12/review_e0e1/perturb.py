"""SYNTHETIC. Perturbed model-F servers on E1's / REG-8's own schedules. Never reads runs/."""
import sys, heapq, math
sys.path.insert(0, "/Users/chalshik/Projects/aftershock-artifacts")
import numpy as np, pandas as pd
from analysis import e1, modelf_sim
LBAR = 3072.0

def sim(cfg, mu, B=1, D=0.0, cost=(0.0, 1.0), sq=0.0, ps=False, dt=0.02):
    """B slots, FIFO admission; a slot holds a request B*cost(L) (capacity unchanged); D s of extra residence after the
    slot is freed (decode-like latency that uses no capacity). sq: superlinear term, cost ~ a + b(L + sq*L^2/LBAR),
    renormalised so the stationary mean cost is 1/mu (approx, at Lbar). ps: egalitarian processor sharing instead."""
    s = modelf_sim.schedule(cfg).sort_values(["session_id", "turn"]).reset_index(drop=True)
    closed = bool(cfg["workload"]["sessions"].get("closed_loop"))
    a, b = cost
    # normalise by the mean over the planned mix (so the open-loop floor stays ~mu)
    Ls = s.prompt_len.to_numpy(float)
    raw = lambda L: a + b * (L + sq * L * L / LBAR)
    unit = raw(Ls).mean() * mu
    c = lambda L: raw(L) / unit
    sid, turn, tp = s.session_id.to_numpy(), s.turn.to_numpy(), s.t_planned.to_numpy(float)
    nxt = np.full(len(s), -1); same = (sid[1:] == sid[:-1]) & (turn[1:] == turn[:-1] + 1)
    nxt[:-1][same] = np.arange(1, len(s))[same]
    end = np.full(len(s), np.nan)
    ev = []   # release heap
    for i in range(len(s)):
        if turn[i] == 0 or not closed:
            heapq.heappush(ev, (tp[i], i))
    horizon = cfg["workload"]["duration_s"] + 50
    if not ps:
        slots = [0.0] * B   # time each slot frees
        heapq.heapify(slots)
        while ev:
            r, i = heapq.heappop(ev)
            if r > horizon: break
            f = heapq.heappop(slots)
            st = max(f, r); fin = st + B * c(Ls[i])
            heapq.heappush(slots, fin)
            end[i] = fin + D
            j = nxt[i]
            if closed and j >= 0:
                heapq.heappush(ev, (end[i] + tp[j] - tp[i], j))
    else:
        t, active = 0.0, {}   # i -> remaining work (s)
        while t < horizon:
            while ev and ev[0][0] <= t:
                r, i = heapq.heappop(ev); active[i] = c(Ls[i])
            if active:
                share = dt / len(active)
                for i in list(active):
                    active[i] -= share
                    if active[i] <= 0:
                        del active[i]; end[i] = t + dt + D
                        j = nxt[i]
                        if closed and j >= 0:
                            heapq.heappush(ev, (end[i] + tp[j] - tp[i], j))
            t += dt
    return pd.DataFrame({"turn": turn, "t_planned": tp, "t_end": end,
                         "status": np.where(np.isnan(end), "unsent", "ok")})

def rows(path, seed, **kw):
    out = []
    for cfg in e1._cfgs(path, seed):
        wl = cfg["workload"]; q = sim(cfg, 1.681, **kw)
        A, Bw = wl["warmup_s"], wl["duration_s"]; span = Bw - A
        done = q[(q.status == "ok") & (q.t_end >= A) & (q.t_end < Bw)]
        thr = len(done) / span; pl = float(((q.t_planned >= A) & (q.t_planned < Bw)).sum() / span)
        out.append({"rate": float(wl["rate"]), "throughput": thr, "planned_rate": pl,
                    "kv_mean": 1.0 if thr < 0.95 * pl else 0.0, "kbar": float((done.turn + 1).mean())})
    return pd.DataFrame(out)

if __name__ == "__main__":
    variants = {
        "F (B=1)": {}, "B=8": {"B": 8}, "B=25": {"B": 25}, "B=25,D=5s": {"B": 25, "D": 5.0},
        "D=10s": {"D": 10.0}, "superlinear sq=1": {"sq": 1.0}, "PS": {"ps": True}, "PS,D=5s": {"ps": True, "D": 5.0},
    }
    only = sys.argv[1:] or list(variants)
    for name in only:
        kw = variants[name]
        cl, ol = rows(e1.E1["configs"]["cl"], 0, **kw), rows(e1.E1["configs"]["ol"], 0, **kw)
        tk, tx = e1.tilt(cl, ol, "kbar", 2.0), e1.tilt(cl, ol, "throughput", 2.0)
        print(f"{name:18s} d_k={tk['d']:+.3f} (se {tk['se']:.3f}) -> {e1.judge(tk,-0.198):10s} d_X={tx['d']:+.3f} -> {e1.judge(tx,0.021):10s}"
              f" cl kbar {[round(x,2) for x in cl.kbar]} cl thr {[round(x,3) for x in cl.throughput]} ol thr {[round(x,3) for x in ol.throughput]} ol kbar {[round(x,2) for x in ol.kbar]}", flush=True)
