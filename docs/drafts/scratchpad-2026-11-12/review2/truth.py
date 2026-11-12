"""Synthetic 'truth' servers that break model F in one way each; read back through k3.fit. Synthetic only."""
import heapq, math, sys, copy
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, "/Users/chalshik/Projects/aftershock-artifacts")
import analysis.k3 as K3
from analysis import modelf_sim as S
from harness.run import load_config
C = Path("/Users/chalshik/Projects/aftershock-artifacts/configs")

def truth(cfg, mu, cost=lambda L: L/3072.0, warm_ratio=None, cold_from=None, servers=1,
          hit_frac=lambda t: 0.0, speed=lambda t, nq: 1.0, prio=None, seed_sched=None, noise_cv=0.0, noise_seed=0):
    """cost(L): seconds at mu=1 relative units (normalised so stationary mean cost = 1/mu).
    warm_ratio: warm turn cost = warm_ratio * cold cost (None: model F's new-token cost).
    hit_frac(t): share of previous prompt cached after cold onset (partial hits).
    speed(t, nq): server speed multiplier. servers: B concurrent FIFO servers each at mu/B.
    prio: None FIFO; 'old' = later turns first."""
    sched = S.schedule(cfg) if seed_sched is None else seed_sched
    closed = True
    trig = cfg["trigger"]; cf = float(trig["at_s"]) if cold_from is None else cold_from
    s = sched.sort_values(["session_id", "turn"]).reset_index(drop=True)
    burst = s["burst"].astype(bool).to_numpy()
    sid, turn = s.session_id.to_numpy(), s.turn.to_numpy()
    tp, L = s.t_planned.to_numpy(float), s.prompt_len.to_numpy(float)
    nxt = np.full(len(s), -1); same = (sid[1:] == sid[:-1]) & (turn[1:] == turn[:-1] + 1)
    nxt[:-1][same] = np.arange(1, len(s))[same]
    prev = np.zeros(len(s)); prev[1:][same] = L[:-1][same]
    # stationary-mix normaliser
    lens = np.array([2176 + 256*k for k in range(8)])
    norm = np.mean([cost(x) for x in lens]) * mu
    c = lambda x: cost(x) / norm
    # event simulation: arrivals into queue; B servers
    arr = [(tp[i], 0, i) for i in range(len(s)) if turn[i] == 0 or burst[i]]
    heapq.heapify(arr)
    queue = []  # (key, rel, i)
    busy = []   # (t_end, i)
    t = 0.0; free = servers
    rel = np.full(len(s), np.nan); st = rel.copy(); en = rel.copy(); cached = np.zeros(len(s))
    cnt = 0
    nrng = np.random.default_rng(noise_seed)
    sg = math.sqrt(math.log(1+noise_cv**2))
    def key(i, r):
        nonlocal cnt; cnt += 1
        if prio == "old": return (-turn[i], r, cnt)
        return (r, cnt)
    while arr or queue or busy:
        # next event
        ta = arr[0][0] if arr else math.inf
        tb = busy[0][0] if busy else math.inf
        if free > 0 and queue:
            _, r, i = heapq.heappop(queue)
            stt = t
            miss = stt >= cf
            if burst[i] or turn[i] == 0: hit = 0.0
            elif not miss:
                hit = prev[i] if warm_ratio is None else None
            else:
                hit = hit_frac(stt) * prev[i]
            if hit is None:
                svc = warm_ratio * c(L[i]); cached[i] = prev[i]
            else:
                svc = c(L[i] - hit); cached[i] = hit
            svc = svc * servers / speed(stt, len(queue))
            if noise_cv: svc *= float(nrng.lognormal(-sg*sg/2, sg))
            st[i] = stt; en[i] = stt + svc; rel[i] = r
            heapq.heappush(busy, (en[i], i)); free -= 1
            continue
        if ta <= tb:
            t, _, i = heapq.heappop(arr); heapq.heappush(queue, (key(i, t), t, i))
        else:
            t, i = heapq.heappop(busy); free += 1
            j = nxt[i]
            if j >= 0 and not burst[i]:
                heapq.heappush(arr, (t + tp[j] - tp[i], 0, j))
    out = pd.DataFrame({"session_id": sid, "turn": turn, "t_planned": tp, "t_sent": rel, "t_first_token": st,
                        "t_end": en, "prompt_tokens": L.astype(int), "prompt_tokens_planned": L.astype(int),
                        "cached_tokens": cached.astype(int), "burst": burst})
    out["status"] = np.where(np.isnan(en), "unsent", "ok")
    return S.as_run(cfg, out)

def readback(run):
    o = K3.observed(run); f = K3.fit(run, o)
    r = {"reuse_W": round(o["reuse_W"], 3), "kbar": round(o["kbar"], 3), "X": round(o["X"], 3)}
    for n in ("prop", "fixed"):
        r[n] = (round(f[n]["mu_k"], 3), round(f[n]["mu_X"], 3), f[n]["mu_k_status"], f[n]["mu_X_status"])
    return r

def cfg(lam=None, seed=None, path="burst_l1pl350cl_r2.0_s2.yaml"):
    c = copy.deepcopy(load_config(C / path))
    if lam: c["workload"]["rate"] = lam
    if seed is not None: c["seed"] = seed
    return c
