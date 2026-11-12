import sys; sys.path.insert(0, "/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/fdf13821-770b-43f6-866b-c82b3bbdc140/scratchpad/review2")
from truth import *
import json
res = {}
for lam in (2.0, 2.2, 2.4):
    ek, ex, kx = [], [], []
    for sd in range(1, 16):
        r = readback(truth(cfg(lam, sd), 1.681))
        ek.append(r["prop"][0]-1.681); ex.append(r["prop"][1]-1.681); kx.append(r["prop"][0]-r["prop"][1])
    ek, ex, kx = map(np.array, (ek, ex, kx))
    print(lam, "mu_k err: mean %.3f sd %.3f min %.3f max %.3f | mu_X err mean %.3f sd %.3f | k-X sd %.3f max|.| %.3f" % (
        ek.mean(), ek.std(), ek.min(), ek.max(), ex.mean(), ex.std(), kx.std(), abs(kx).max()))
    res[lam] = ek.tolist()
json.dump(res, open("/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/fdf13821-770b-43f6-866b-c82b3bbdc140/scratchpad/review2/t1.json", "w"))
