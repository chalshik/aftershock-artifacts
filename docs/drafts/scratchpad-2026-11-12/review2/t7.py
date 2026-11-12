import sys; sys.path.insert(0, "/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/fdf13821-770b-43f6-866b-c82b3bbdc140/scratchpad/review2")
from truth import *
for B in (32,):
    for lam in (2.0, 2.4):
        rows=[]
        for sd in (2,3,4,5,6):
            run = truth(cfg(lam, sd), 1.681, servers=B)
            q = run["requests"]; w = q[(q.t_end>=1680)&(q.t_end<2580)]
            rows.append((readback(run), float((w.t_end-w.t_first_token).median())))
        mk=np.array([r[0]["prop"][0] for r in rows]); mx=np.array([r[0]["prop"][1] for r in rows])
        print(B, lam, "mu_k %.3f mu_X %.3f k-X %+.3f residence med %.1fs" % (np.nanmedian(mk), np.nanmedian(mx), np.nanmedian(mk-mx), np.median([r[1] for r in rows])))
