"""Search verbatim quotes in the papers' PDFs and print the page of each hit (agent/LITERATURE.md).

    python3 agent/lit/verify_quotes.py            # all rows
Text: `pdftotext -raw`, per page; whitespace collapsed, line-end hyphens joined, typographic quotes and dashes
normalised, on both sides. A row is FOUND when the normalised quote occurs on a page. PDFs: docs/paper/pdfs/ (local).
"""
import re
import subprocess
import sys
from pathlib import Path

PDFS = Path(__file__).resolve().parents[2] / "docs" / "paper" / "pdfs"
FILES = {"lu": "2611.02543.pdf", "vj": "2611.08902.pdf", "hl": "2611.13412.pdf", "kairos": "2604.16682.pdf",
         "metronome": "2607.02640.pdf"}

# (row of docs/paper/quote-check.md, paper, quote)
ROWS = [
    (1, "lu", "The feedback follows from closed-loop sessions, continuing arrivals and context-dependent miss cost"),
    (2, "hl", "Unlike open-loop chat traffic, the offered load of a session population depends on the server"),
    (3, "hl", "Their analysis assumes exogenous inter-turn times, excluding the latency feedback that sustains the degraded regime here"),
    (4, "vj", "Our synthesis of these rules is that in both engines a session's KV is protected only while one of its requests runs"),
    (5, "vj", "sessions share no cached tokens, each has at most one outstanding request, and evicted KV is discarded, not offloaded to another memory tier"),
    (6, "lu", "each call becomes eligible after its predecessor completes and the recorded tool gap elapses"),
    (6, "lu", "each call is released only after its predecessor completes"),
    (6, "hl", "waits an exponential think time (mean 5 s) between turns"),
    (6, "vj", "during a tool call the client sleeps"),
    (7, "vj", "but have not shown this"),
    (8, "hl", "a 2K-token system prompt shared by all sessions"),
    (8, "hl", "the token-weighted hit ratio is 0.10–0.12, which is just the shared system prompt"),
    (9, "vj", "too narrow for the registration rule to place a test"),
    (10, "vj", "then from 2400 s arrivals cut to 1.15"),
    (12, "lu", "this trapping load remains between 0.46 and 0.70 of the steady-state overload rate"),
    (12, "lu", "+50% on 1P3D and +25% on GPU-only 1P1D"),
    (12, "lu", "every seed recovers at 0.1"),
    (12, "lu", "Plots in this section and §5 report simulation results unless explicitly identified as real measurements"),
    (12, "lu", "starts at half the deployment's profiled critical rate"),
    (12, "lu", "remains trapped in all four"),
    (15, "vj", "empties if and only if"),
    (17, "vj", "not a second stationary state, so we say metastable rather than bistable"),
    (18, "hl", "a single colocated engine on vLLM and SGLang"),
    (18, "vj", "colocated, with one GPU each"),
    (19, "metronome", "The stall never recovers, because audio keeps arriving open-loop"),
    (20, "kairos", "even a short overload can push the instance into a persistently inefficient operating region"),
]


def norm(s: str) -> str:
    s = s.replace("-\n", "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace("−", "-").replace("ﬁ", "fi").replace("ﬂ", "fl")
    return re.sub(r"\s+", " ", s).strip().lower()


def pages(pdf: Path) -> list[str]:
    out = subprocess.run(["pdftotext", "-raw", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    return [norm(p) for p in out.split("\f")]


def main() -> int:
    cache, missing = {}, 0
    for row, paper, quote in ROWS:
        if paper not in cache:
            cache[paper] = pages(PDFS / FILES[paper])
        q = norm(quote)
        hits = [i for i, p in enumerate(cache[paper], 1) if q in p]
        if not hits:   # spaces can vanish in justified lines: retry without any whitespace
            hits = [i for i, p in enumerate(cache[paper], 1) if q.replace(" ", "") in p.replace(" ", "")]
        missing += not hits
        print(f"row {row:>2} {paper:<9} {'FOUND p.' + ','.join(map(str, hits)) if hits else 'NOT FOUND':<14} {quote[:90]}")
    for paper, f in FILES.items():
        first = pages(PDFS / f)[0] if paper not in cache else cache[paper][0]
        m = re.search(r"arxiv:\s?\d{4}\.\d{5}v\d+[^a-z]*\w+ \d{4}", first.replace(" ", " "))
        print(f"stamp {paper:<9} {m.group(0) if m else '(no arXiv stamp found on page 1)'}  pages={len(cache.get(paper) or pages(PDFS / f))}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
