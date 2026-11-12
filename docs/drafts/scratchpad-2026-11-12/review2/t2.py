import sys; sys.path.insert(0, "/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/fdf13821-770b-43f6-866b-c82b3bbdc140/scratchpad/review2")
from truth import *
ek=[]
for sd in range(1, 16):
    r = readback(truth(cfg(2.4, sd), 1.681))
    print(sd, r)
    if not math.isnan(r["prop"][0]): ek.append(r["prop"][0]-1.681)
ek=np.array(ek); print("n", len(ek), "mean %.3f sd %.3f min %.3f max %.3f"%(ek.mean(), ek.std(), ek.min(), ek.max()))
