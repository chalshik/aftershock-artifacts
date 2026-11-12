import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/fdf13821-770b-43f6-866b-c82b3bbdc140/scratchpad/sim")
import numpy as np, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import sim
from analysis import k3, modelf
def summ(lab, **kw):
    R=[sim.run(seed=s, **kw) for s in range(40)]
    f=lambda key: np.array([r[key] for r in R])
    print(f"{lab}: Q1dev {np.mean(f('kb')-f('kF')):+.3f} Q2'dev {np.mean(f('d')-f('dmix')):+.3f} Q2dev {np.mean(f('d')-f('dF')):+.3f} mu_hat {np.nanmean(f('muh')):.3f} (sd {np.nanstd(f('muh')):.3f})")
summ("2.0 big burst 6/s", lam=2.0, brate=6.0)
summ("2.0 small burst 1/s", lam=2.0, brate=1.0)
summ("2.0 watch 4500", lam=2.0, watch=4500)
summ("2.4 mu_true 2.0 (not all-miss)", lam=2.4, mu_true=2.0)
summ("2.0 mu_true 1.78", lam=2.0, mu_true=1.78)
summ("2.0 gap 10", lam=2.0, gap=10.0)
