<!-- docs/decisions.md lines 4516-4521 -->
## 2026-11-13 · [DECISION] (owner) E1 goes to review now, so that it can run once REG-19's queue has ended

- **The owner's choice** (this session, about 16:55 UTC), answering whether to send E1 through rule F and the owner-proxy now so that it can run after REG-19: "Yes, prepare E1 (Recommended)".
- **What it allows:** the agent sends `docs/drafts/e1_draft4.md` (about 2.1 GPU h, FILE(docs/drafts/e1_draft4.md:59)) to a rule F review and an owner-proxy pass. If both clear, it registers E1 as delegate, under the delegation's rules.
- **What it does not allow:** E1 is not run before its [REG] entry is committed, and not while REG-19's queue holds the GPU. E1 changes no decision about a shock matrix, as its own draft says first (FILE(docs/drafts/e1_draft4.md:13)).
