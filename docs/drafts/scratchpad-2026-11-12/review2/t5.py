import sys; sys.path.insert(0, "/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/fdf13821-770b-43f6-866b-c82b3bbdc140/scratchpad/review2")
from truth import *
cases = {
 "B=128": dict(servers=128),
 "B=64+warm0.7+cv0.3": dict(servers=64, warm_ratio=0.7, noise_cv=0.3),
 "fading hits 0.6->0 by 1680": dict(hit_frac=lambda t: 0.6*max(0.0, 1-(t-900)/780)),
 "speed 1-0.001*queue": dict(speed=lambda t, nq: max(0.5, 1-0.001*nq)),
 "true mu 1.85 (faster CL server)": dict(),
}
for name, kw in cases.items():
    mu = 1.85 if "1.85" in name else 1.681
    for lam in (2.0, 2.4):
        rows = [readback(truth(cfg(lam, sd), mu, **kw)) for sd in (2, 3, 4, 5, 6)]
        mk = np.array([r["prop"][0] for r in rows]); mx = np.array([r["prop"][1] for r in rows])
        fk = np.array([r["fixed"][0] for r in rows]); fx = np.array([r["fixed"][1] for r in rows])
        print(f"{name:32s} lam {lam}: prop mu_k {np.nanmedian(mk):.3f} mu_X {np.nanmedian(mx):.3f} k-X {np.nanmedian(mk-mx):+.3f} | fixed mu_k {np.nanmedian(fk):.3f} mu_X {np.nanmedian(fx):.3f} k-X {np.nanmedian(fk-fx):+.3f} | reuseW {max(r['reuse_W'] for r in rows)} kbar {np.mean([r['kbar'] for r in rows]):.3f} X {np.mean([r['X'] for r in rows]):.3f} st {[r['prop'][2] for r in rows if r['prop'][2]!='ok']}", flush=True)
