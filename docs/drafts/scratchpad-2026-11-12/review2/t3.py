import sys; sys.path.insert(0, "/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/fdf13821-770b-43f6-866b-c82b3bbdc140/scratchpad/review2")
from truth import *
g = K3.grid()
for lam, sd in ((2.4, 9), (2.4, 2), (2.0, 2)):
    c = cfg(lam, sd); sch = S.schedule(c)
    ks = np.array([K3.replay(c, float(m), (0.0, 1.0), sch)["kbar"] for m in g])
    xs = np.array([K3.replay(c, float(m), (0.0, 1.0), sch)["X"] for m in g])
    sel = (g >= 1.55) & (g <= 1.85)
    sl = np.polyfit(g[sel], ks[sel], 1)[0]
    print(lam, sd, "kbar slope 1.55-1.85: %.3f per req/s; kbar range on grid %.3f..%.3f; X slope %.3f" % (sl, ks.min(), ks.max(), np.polyfit(g[sel], xs[sel], 1)[0]))
    print("  kbar 1.58..1.80:", np.round(ks[(g>=1.58)&(g<=1.80)], 3).tolist())
