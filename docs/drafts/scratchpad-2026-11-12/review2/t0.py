import sys; sys.path.insert(0, "/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/fdf13821-770b-43f6-866b-c82b3bbdc140/scratchpad/review2")
from truth import *
# sanity: truth with model F settings == replay
for lam in (2.0, 2.4):
    print("F exact", lam, readback(truth(cfg(lam), 1.681)))
