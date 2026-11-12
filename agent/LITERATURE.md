# LITERATURE: what I verified myself, with anchors

Rule: a paper is not rule-B evidence. Every line is **SUPPORTED** (I read it in the PDF; anchor given) or **BELIEF** (my reading or inference), never OBSERVED. PDFs: `docs/paper/pdfs/` (local, never committed). Page numbers are PDF pages. Quotes are verbatim from `pdftotext` output, checked against the page image where a figure is involved.

Status of the pass (2026-11-13): KAIROS check done; versions read from the first pages; 26 cited quotes found by my own search. Lu et al., Valse and Jannesari, Huang and Liu, Schroeder et al.: not yet read through by this session; until then the repo's `docs/paper/reading-notes.md` and `quote-check.md` (earlier sessions' reads) stand as BELIEF.

## Versions (from each PDF's own first page)

| Paper | File | First-page stamp |
|---|---|---|
| KAIROS (Yuan, Chowdhury, Talati) | `2604.16682.pdf`, 22 pages | "arXiv:2604.16682v2 [cs.DC] 10 Nov 2026"; header "To appear in the Proceedings of ASPLOS 2027." SUPPORTED (p. 1) |
| Lu et al., "When Cache Pressure Becomes a Trap: Metastability in Agent Serving" | `2611.02543.pdf`, 19 pages | "arXiv:2611.02543v1 [cs.DC] 2 Nov 2026" SUPPORTED (p. 1) |
| Valse and Jannesari, "Inside the Trap: A Renewal Law for Prefix-Cache Collapse in LLM Agent Serving" | `2611.08902.pdf`, 66 pages | "arXiv:2611.08902v1 [cs.DC] 6 Nov 2026" SUPPORTED (p. 1) |
| Huang and Liu, "Bursts That Outlast Themselves: Persistent Degradation in Prefix-Cached Agent Serving" | `2611.13412.pdf`, 12 pages | "arXiv:2611.13412v1 [cs.DC] 10 Nov 2026" SUPPORTED (p. 1) |
| Metronome (Meng, Li) | `2607.02640.pdf`, 21 pages | "arXiv:2607.02640v1 [cs.SD] 2 Jul 2026" SUPPORTED (p. 1) |
| Schroeder, Wierman, Harchol-Balter, "Open Versus Closed: A Cautionary Tale" | `earlier-session/schroeder/p.pdf`, 14 pages | no stamp; title page read. Venue and year not re-checked by me |

## Quote check, my own pass (2026-11-13)

`python3 agent/lit/verify_quotes.py` searches the verbatim quotes of `docs/paper/quote-check.md` rows 1–10, 12, 15, 17–20 (26 strings) in the PDFs, page by page. **All 26 were found** (SUPPORTED), on the pages quote-check.md records, with one difference: row 10's "then from 2400 s arrivals cut to 1.15" is on pp. 9 and 23, where quote-check.md says App. C, p. 24. Not covered by a string search, so still BELIEF from the earlier sessions' reads: the numbers of rows 9, 11, 13, 14 and 16 (tables), and that no paper has an open-loop arm in a figure. None of the three preprints, Metronome or Schroeder et al. has been read through by this session yet.

## KAIROS (arXiv 2604.16682v2): the open check on Fig. 10–11

**Question (start prompt §2.4):** in Fig. 10–11, did the controller restore full frequency during the thrashing in the run without thrashing avoidance? If yes, that is an accidental removed-trigger observation.

**Answer: the paper does not show it, so it cannot be read either way.**

What the paper says and shows (SUPPORTED):
1. The design has a boost that removes the low frequency when agents fall behind: "If Throughput_k^min falls below the SLO target τ, the controller overrides the context-aware policy and sets the frequency to the maximum level" (§6.2.3, Eq. 11–12, p. 7).
2. It asserts persistence: "even a short overload can push the instance into a persistently inefficient operating region" (§6.2.4, p. 7).
3. The experiment: "It compares three configurations: no frequency control, KAIROS without thrashing avoidance, and KAIROS with thrashing avoidance. While the no-control baseline avoids thrashing by running at high frequency, KAIROS without thrashing avoidance reduces frequency to save power, pushing the system into a thrashing regime." (§7, p. 9). Load 0.05 jobs/s, SLO target 20 tokens/s, mini-swe-agent on DABStep.
4. Fig. 10 (p. 10): per-agent P5 throughput 28.6 (no frequency control), 2.3 (KAIROS without thrashing avoidance), 19.9 tokens/s (with); system job throughput 0.051, 0.046, 0.051 jobs/s.
5. Fig. 11 (p. 10), five panels over 180 minutes: (a) context usage without thrashing avoidance, above the capacity line from about minute 60 to the end; (b) job throughput without it, dipping to about 0.03 jobs/s around minutes 55–75 and then moving between about 0.04 and 0.06; (c) pending agent count, titled "Kairos With Thrashing Avoidance"; (d), (e) context usage and job throughput with it. **No panel shows the GPU frequency of either run.** (Fig. 9, p. 10, shows a frequency trace, with boosts to "Max Freq.", but for a different experiment: 0.03 jobs/s, SLO 35 tokens/s.)
6. The text reads Fig. 11 as: "Without thrashing avoidance, context usage (subfigure (a)) exceeds capacity and remains high, pushing the system into a persistent thrashing regime where throughput drops (subfigure (b)) and queued agents accumulate (subfigure (c)), making recovery difficult." (p. 10). The text gives panel (c) to the run without thrashing avoidance; the panel's own title says "With". An inconsistency inside the paper.

What follows (BELIEF, my inference):
- If the boost of §6.2.3 was active in the configuration "KAIROS without thrashing avoidance", then at a P5 throughput of 2.3 tokens/s against a 20 tokens/s target the controller was at maximum frequency for much of the thrashing, i.e. the cause (low frequency) had been removed while the thrashing went on, at a load that the no-control configuration carries at that same frequency (Fig. 10). That would be a removed-trigger observation, not designed as one.
- The paper states neither whether the boost was active in that configuration nor what the frequency was. So it is not an observation the paper reports.

**Consequence for Related Work.** "Untested with the trigger removed" is too strong as a statement about what happened in their run, and right as a statement about what they report. Wording to use: KAIROS asserts persistence (§6.2.4) and shows thrashing that continues in a run without its concurrency control (Fig. 11a–b); the paper reports no frequency trace for that run, so whether its own boost (§6.2.3) had removed the cause cannot be read from it; no test designed to remove the trigger is reported. (To be applied in `docs/paper/related-work-approach-v3.md`; task Z6a/Z10.)

Other KAIROS facts used by the repo, re-read here (SUPPORTED): engine vLLM (p. 2: "that run vLLM"; the implementation paragraph names "v0.14.0", p. 8, to be re-checked when cited); arrivals of agent jobs are Poisson (p. 3: "using a Poisson distribution"); the motivating thrashing example holds "the request arrival rate … fixed at 0.08 agents/s" while service slows (p. 4), i.e. the cause (lower frequency) stays on.
