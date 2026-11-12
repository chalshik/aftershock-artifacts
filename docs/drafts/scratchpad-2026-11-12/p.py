# P(outcome | arm A starts), mcnemar, n = 5, all 5 closed cold (the gate). Open per-run beliefs.
p_cold, p_partial = 0.10, 0.08          # per open run; recovered otherwise
p_rec = 1 - p_cold - p_partial
print("all 5 recovered:", round(p_rec**5, 3))
from math import comb
# refutes needs >= 3 stuck
print("P(>=3 cold):", round(sum(comb(5,k)*p_cold**k*(1-p_cold)**(5-k) for k in range(3,6)), 4))
