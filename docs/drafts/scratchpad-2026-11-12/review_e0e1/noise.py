"""SYNTHETIC: label distribution of e1.judge when per-run k-bar noise (sigma) is added to model F's seed-0 curves,
and on a 'flat' truth (closed-loop slope = 0.5 x d_F, i.e. at the threshold) and a no-tilt truth."""
import sys
sys.path.insert(0, "/Users/chalshik/Projects/aftershock-artifacts")
import numpy as np, pandas as pd
from analysis import e1
cl = e1.replay_rows(e1.E1["configs"]["cl"], 1.681, (0.0, 1.0), 0); ol = e1.replay_rows(e1.E1["configs"]["ol"], 1.681, (0.0, 1.0), 0)
thr = {2.0: -0.198, 2.5: -0.186, 3.0: -0.178}
rng = np.random.default_rng(1)
for truth, scale in (("F", 1.0), ("F x0.5", 0.5), ("none", 0.0)):
    base_cl = ol.kbar.mean() + scale * (cl.kbar - cl.kbar.mean()) if scale != 1.0 else cl.kbar
    for lo in (2.0, 3.0):
        for sig in (0.03, 0.08, 0.15):
            labs = []
            for _ in range(4000):
                c = cl.assign(kbar=base_cl + rng.normal(0, sig, len(cl))); o = ol.assign(kbar=ol.kbar + rng.normal(0, sig, len(ol)))
                labs.append(e1.judge(e1.tilt(c, o, "kbar", lo), thr[lo]))
            v = pd.Series(labs).value_counts(normalize=True).round(3).to_dict()
            print(truth, "onset", lo, "sigma", sig, v)
