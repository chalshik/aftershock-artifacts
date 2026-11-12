import sys; sys.path.insert(0, "/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/fdf13821-770b-43f6-866b-c82b3bbdc140/scratchpad/review2")
from truth import *
cases = {
 "noise cv0.3": dict(noise_cv=0.3),
 "B=16 FIFO": dict(servers=16),
 "B=64 FIFO": dict(servers=64),
 "warm ratio 0.7": dict(warm_ratio=0.7),
 "cold at 1080": dict(cold_from=1080.0),
 "cold at 700 (before burst)": dict(cold_from=700.0),
 "prio older turns": dict(prio="old"),
 "superlinear L^2": dict(cost=lambda L: (L/3072.0)**2),
}
which = sys.argv[1:] or list(cases)
for name in which:
    kw = cases[name]
    for lam in (2.0, 2.4):
        rows = []
        for sd in (2, 3, 4, 5, 6):
            r = readback(truth(cfg(lam, sd), 1.681, **kw))
            rows.append(r)
        mk = np.array([r["prop"][0] for r in rows]); mx = np.array([r["prop"][1] for r in rows])
        fk = np.array([r["fixed"][0] for r in rows]); fx = np.array([r["fixed"][1] for r in rows])
        print(f"{name:28s} lam {lam}: prop med mu_k {np.nanmedian(mk):.3f} mu_X {np.nanmedian(mx):.3f} med(k-X) {np.nanmedian(mk-mx):+.3f} | fixed mu_k {np.nanmedian(fk):.3f} mu_X {np.nanmedian(fx):.3f} med(k-X) {np.nanmedian(fk-fx):+.3f} | reuseW {max(r['reuse_W'] for r in rows)} kbar {np.mean([r['kbar'] for r in rows]):.3f} X {np.mean([r['X'] for r in rows]):.3f} st {[r['prop'][2] for r in rows if r['prop'][2]!='ok']}", flush=True)
