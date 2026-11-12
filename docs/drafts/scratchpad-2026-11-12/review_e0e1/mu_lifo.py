"""SYNTHETIC: d_k sensitivity to mu (model F replay), and a LIFO server (not model F)."""
import sys, heapq
sys.path.insert(0, "/Users/chalshik/Projects/aftershock-artifacts")
import numpy as np, pandas as pd
from analysis import e1, modelf_sim
for mu in (1.5, 1.681, 1.9):
    cl = e1.replay_rows(e1.E1["configs"]["cl"], mu, (0.0, 1.0), 0); ol = e1.replay_rows(e1.E1["configs"]["ol"], mu, (0.0, 1.0), 0)
    t = e1.tilt(cl, ol, "kbar", 2.0); print("mu", mu, "d_k", round(t["d"], 3), "cl kbar", [round(x, 2) for x in cl.kbar])
def lifo(cfg, mu):
    s = modelf_sim.schedule(cfg).sort_values(["session_id", "turn"]).reset_index(drop=True)
    closed = bool(cfg["workload"]["sessions"].get("closed_loop"))
    c = modelf_sim._cost_fn(mu, (0.0, 1.0))
    sid, turn, tp, L = s.session_id.to_numpy(), s.turn.to_numpy(), s.t_planned.to_numpy(float), s.prompt_len.to_numpy(float)
    nxt = np.full(len(s), -1); same = (sid[1:] == sid[:-1]) & (turn[1:] == turn[:-1] + 1); nxt[:-1][same] = np.arange(1, len(s))[same]
    arr = [(tp[i], i) for i in range(len(s)) if turn[i] == 0 or not closed]; heapq.heapify(arr)
    end = np.full(len(s), np.nan); t = 0.0; stack = []
    while arr or stack:
        while arr and arr[0][0] <= t:
            stack.append(heapq.heappop(arr))
        if not stack:
            t = arr[0][0]; continue
        r, i = stack.pop(); t += c(L[i]); end[i] = t
        j = nxt[i]
        if closed and j >= 0: heapq.heappush(arr, (t + tp[j] - tp[i], j))
        if t > 1000: break
    return pd.DataFrame({"turn": turn, "t_planned": tp, "t_end": end, "status": np.where(np.isnan(end), "unsent", "ok")})
def rows(path):
    out = []
    for cfg in e1._cfgs(path, 0):
        wl = cfg["workload"]; q = lifo(cfg, 1.681); d = q[(q.status == "ok") & (q.t_end >= 240) & (q.t_end < 900)]
        out.append({"rate": wl["rate"], "kbar": (d.turn + 1).mean(), "throughput": len(d) / 660})
    return pd.DataFrame(out)
cl, ol = rows(e1.E1["configs"]["cl"]), rows(e1.E1["configs"]["ol"])
t = e1.tilt(cl, ol, "kbar", 2.0); print("LIFO d_k", round(t["d"], 3), e1.judge(t, -0.198), "cl", [round(x, 2) for x in cl.kbar], "ol", [round(x, 2) for x in ol.kbar])
