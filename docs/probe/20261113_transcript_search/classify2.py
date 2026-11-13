"""Classify the hits of a search2.py output, for the [DECISION] (delegate) of REG-21 and REG-22 (rule F round 17 BE-O1,
BE-O3; owner-proxy BH8: "classifies every `ran_unknown` and `names_reg19_run` hit").

    python3 docs/probe/20261113_transcript_search/classify2.py <search2 output> [labels.tsv] > classify2_<stamp>.txt

Which hits. Every record (a call with a hit other than `ran`) whose time is at or after 2026-11-11 17:15:21 UTC, when
REG-19's configs were written (FILE-free: the first record that names `w3000_s15` in a config path), in the classes
ran_unknown, names_reg19_run, ran_on_reg19, reg19_read, runs_glob_loop, cd_run, grep_runs, glob_runs, read_run,
write_runs, or script_reads_runs (`stubbed` included). And every `ran` line, at any time, that runs one of the modules
REG-21/22's append check names (k3w, c2, k3, k1, k5, or `load.rates`).

Labels, by rules first, then by the hand labels in labels.tsv (key `<transcript>:<line>`, a label, a note); a hand label
overrides a rule. A hit no rule or hand label covers is printed as UNLABELLED; the [DECISION] needs none left.
  before_reg19_folders  before 2026-11-12 05:09:20 UTC, when the first REG-19 folder was made (its name,
                        20261112-050920, and the queue's launch command at 05:09:07 UTC; the VM clock is UTC), so no
                        REG-19 folder existed to be read.
  names_in_text         a tool that is not a command (Write, Edit, Agent, SendMessage, ...): names in text, no read.
  reg19_scripts         a run of REG-19's own queue/launch/final/session-probe scripts (reads by design, disclosed).
  own_tools             a run of search.py, search2.py, classify2.py or closure.py (they read transcripts or source; search2
                        flags them because their own text names `runs/`).
  (search2's `stubbed` gets no rule: a script that assigns to `RUNS` or `find_runs` may still read real runs, as
  s57_inv.py did; such records are kept and labelled by hand.)
  code_text             a REG-19 name or pattern only inside python that edits source files or tests (no run read).
  disclosed(<item>)     one of the reads "What was known" lists, by key (the DISCLOSED table below).
  names_in_command      a command whose only class is names_reg19_run: it names a REG-19 run, config or pattern, and
                        search2 found in it no path into a REG-19 folder, no `cd` or loop under runs/, and no run reader.
  names_or_validity     a loop, glob or `cd` under runs/ whose command names no run file other than `checks.json` and
                        no size or count tool (`du`, `stat`, `wc`, `ls -l`), does not `cd` into one run folder, and reads
                        nothing through `xargs`, `rsync` or `scp`: folder names and validity only.
  no_run_read           (`ran` lines) python that, by search2's syntax-tree test, calls no run reader and opens no path
                        under runs/ (the call has no `script_reads_runs` hit, `stubbed` included), and is not a
                        `-m analysis.X` module run.
The rest (validity-only loops, names-only listings, other runs) is labelled by hand, with a note, in labels.tsv.
"""
import re
import sys
from collections import Counter

CUTOFF = "2026-11-11T17:15:21"
FIRST_FOLDER = "2026-11-12T05:09:20"
KEEP = {"ran_unknown", "names_reg19_run", "ran_on_reg19", "reg19_read", "runs_glob_loop", "cd_run", "grep_runs",
        "glob_runs", "read_run", "write_runs"}
RAN_MODS = re.compile(r"analysis\.(k3w|c2|k3|k1|k5)\b|load\.rates|\b(k3w|c2|k3|k1|k5)\b")
REG19_SCRIPT = re.compile(r"ops_r3/(queue|launch|final|session_probe)\.sh|queue_reg19\w*\.sh|launch[4-9]\.sh")
# reads that "What was known" lists, by transcript:line (inputs checked by the agent, 2026-11-13)
DISCLOSED = {
    "bc2fcf6d-b7b6-45b7-9398-2cecb62afb9a.jsonl:10177": "(i)+(iii) seed 17 control: log tail, ls -la, tail -3 events",
    "bc2fcf6d-b7b6-45b7-9398-2cecb62afb9a.jsonl:10195": "[CORR] head -c 300 checks.json of seed 17 control (its first ~300 bytes reach the no_errors counts: second [CORR])",
    "fdf13821-770b-43f6-866b-c82b3bbdc140/subagents/agent-ad7b5aba70bdf01d4.jsonl:131": "(ii) env.json fields",
    "fdf13821-770b-43f6-866b-c82b3bbdc140/subagents/agent-ad7b5aba70bdf01d4.jsonl:135": "(ii) server.log start-up grep",
    "fdf13821-770b-43f6-866b-c82b3bbdc140/subagents/agent-ad7b5aba70bdf01d4.jsonl:139": "(ii) server.log line 14",
    "fdf13821-770b-43f6-866b-c82b3bbdc140/subagents/agent-a2058e8f5d4c1fd10.jsonl:67": "(iv) source_config loop",
    "fdf13821-770b-43f6-866b-c82b3bbdc140/subagents/agent-ad7b5aba70bdf01d4.jsonl:154": "(iv) nvidia_smi + KV size loop",
    "fdf13821-770b-43f6-866b-c82b3bbdc140/subagents/agent-ad7b5aba70bdf01d4.jsonl:157": "(iv) nvidia_smi + KV size loop",
    "bc2fcf6d-b7b6-45b7-9398-2cecb62afb9a.jsonl:9988": "(v) size of seed 16's partial metrics file",
    "bc2fcf6d-b7b6-45b7-9398-2cecb62afb9a.jsonl:9968": "(vii) du -sk of seed 16 folders",
    "bc2fcf6d-b7b6-45b7-9398-2cecb62afb9a.jsonl:9977": "(vii) du growth of seed 16 control",
    "bc2fcf6d-b7b6-45b7-9398-2cecb62afb9a.jsonl:9982": "(vii) ls -la of seed 16 control",
    "bc2fcf6d-b7b6-45b7-9398-2cecb62afb9a.jsonl:10006": "(vii) ls -la of seed 16 burst metrics files",
    "fdf13821-770b-43f6-866b-c82b3bbdc140.jsonl:3864": "(viii) ls of the last run folder (seed 17 burst)",
    "fdf13821-770b-43f6-866b-c82b3bbdc140/subagents/agent-a2058e8f5d4c1fd10.jsonl:61": "(viii) ls + config.yaml lines",
    # s134_runs.py: `source_config` and `sweep_parent` of every config.yaml, checks.json valid/failed (found by search2's
    # fix of 2026-11-13: an absolute path ending in /runs)
    "fdf13821-770b-43f6-866b-c82b3bbdc140/subagents/agent-ad7b5aba70bdf01d4.jsonl:83": "(iv)+(ix) s134_runs.py: source_config, validity",
    "fdf13821-770b-43f6-866b-c82b3bbdc140/subagents/agent-ad7b5aba70bdf01d4.jsonl:86": "(iv)+(ix) s134_runs.py: source_config, validity",
    "fdf13821-770b-43f6-866b-c82b3bbdc140/subagents/agent-ad7b5aba70bdf01d4.jsonl:91": "(iv)+(ix) s134_runs.py: source_config, validity",
}


def parse(path):
    text = open(path).read()
    ran = [l.split(" | ") for l in text.split("\n") if re.match(r"^\d{4}-\d\d-\d\dT[^|]+\| [^|]+ \| \d+ \| ran \|", l)]
    recs = []
    for block in text.split("\n### ")[1:]:
        lines = block.split("\n")
        head = lines[0].split(" | ")
        if len(head) < 4:
            continue
        ts, where, tool, classes = head[0], head[1], head[2], head[3].split(", ")
        details = [l[2:] for l in lines[1:] if l.startswith("- ")]
        cmd = "\n".join(l[6:] for l in lines[1:] if l.startswith("    | "))
        recs.append((ts, where, tool, classes, details, cmd))
    return ran, recs


DATAFILE = re.compile(r"events\.jsonl|env\.json|server\.log|config\.yaml|gpu\.jsonl|metrics|requests|schedule|harness|\.log\b|\.parquet")
SIZETOOL = re.compile(r"\bdu\b|\bstat\b|\bwc\b|ls\s+-[a-zA-Z]*l|\bcat\b|\bhead\b|\btail\b|\bsha256sum\b|\bshasum\b")


def rule(ts, where, tool, classes, details, cmd):
    if where in DISCLOSED:
        return f"disclosed{DISCLOSED[where][:DISCLOSED[where].index(' ')]}", DISCLOSED[where]
    if ts < FIRST_FOLDER:
        return "before_reg19_folders", ""
    if not cmd and tool not in ("Read", "Grep", "Glob"):
        return "names_in_text", tool
    if REG19_SCRIPT.search(cmd):
        return "reg19_scripts", REG19_SCRIPT.search(cmd).group(0)
    scripts = [d for d in details if d.startswith("script ")]
    if set(classes) == {"script_reads_runs"} and scripts and all(OWN_TOOL.search(d) for d in scripts):
        return "own_tools", "the search, classification or closure tool: reads transcripts or source, not runs"
    # (no rule for search2's `stubbed`: assigning to RUNS or find_runs is not a guard by itself; s57_inv.py's
    # `RUNS = Path("runs")` read every folder. Every such record is labelled by hand.)
    if set(classes) <= {"names_reg19_run", "ran_on_reg19", "script_reads_runs"} and re.search(r"write_text|\.replace\(|open\([^)]*['\"]w['\"]", cmd) \
            and not re.search(r"\bruns/|find_runs\(|load_run\(", cmd.split("EOF")[0] if "EOF" in cmd else ""):
        return "code_text", ""
    if set(classes) == {"names_reg19_run"} and cmd:
        return "names_in_command", ""
    if set(classes) <= {"runs_glob_loop", "cd_run", "names_reg19_run"} and cmd and not CD_INTO_RUN.search(cmd) \
            and not PIPED_READ.search(cmd):
        runs_part = " ".join(seg for seg in re.split(r"[;&|]+", cmd) if re.search(r"\bruns\b|\$d\b|\$r\b|checks\.json", seg))
        if not DATAFILE.search(runs_part) and not SIZETOOL.search(runs_part):
            return "names_or_validity", "auto"
    return None, ""


# a `cd` into one run folder (its files are then read by bare names), and file contents read through a pipe or xargs:
# both leave names_or_validity to a hand label
CD_INTO_RUN = re.compile(r"\bcd\s+[^;&|]*runs/(\$\{?\w+\}?|[0-9]{8}-[0-9]{6}_\S+)")
OWN_TOOL = re.compile(r"^script \S*docs/probe/20261113_(transcript_search/(search2?|classify2)|freeze/closure)\.py ")
PIPED_READ = re.compile(r"xargs\s+(-\S+\s+)*(sha256sum|shasum|md5|cat|head|tail|wc|grep)\b|\brsync\b|\bscp\b")


def main(argv):
    ran, recs = parse(argv[0])
    hand = {}
    if len(argv) > 1:
        for l in open(argv[1]):
            if l.strip() and not l.startswith("#"):
                k, lab, *note = l.rstrip("\n").split("\t")
                hand[k] = (lab, note[0] if note else "")
    rows = []
    for ts, where, tool, classes, details, cmd in recs:
        if ts < CUTOFF:
            continue
        cls = set(classes)
        if not (cls & KEEP) and "script_reads_runs" not in cls:   # `stubbed` script reads are kept too
            continue
        lab, note = hand.get(where) or rule(ts, where, tool, classes, details, cmd)
        rows.append((ts, where, tool, ",".join(classes), lab or "UNLABELLED", note))
    reads = {w for ts, w, tool, classes, details, cmd in recs
             if "script_reads_runs" in classes and any((", reads" in d or "unparsed" in d or ", stubbed" in d) for d in details)}
    ranrows = []
    for r in ran:
        ts, where_f, ln, _, what, *rest = r
        if RAN_MODS.search(what):
            key = f"{where_f}:{ln}"
            auto = ("no_run_read", "auto") if (key not in reads and not what.startswith("-m analysis.")) else ("UNLABELLED", "")
            lab, note = hand.get(key, auto)
            ranrows.append((ts, key, what[:120], lab, note))
    print(f"# classify2 of {argv[0]}: {len(rows)} records at or after {CUTOFF} UTC; {len(ranrows)} `ran` lines of k3w/c2/k3/k1/k5/load.rates")
    print("# labels: " + "; ".join(f"{k} {v}" for k, v in sorted(Counter(r[4] for r in rows).items())))
    print("# ran labels: " + "; ".join(f"{k} {v}" for k, v in sorted(Counter(r[3] for r in ranrows).items())))
    print("\n## records: time | transcript:line | tool | classes | label | note")
    for r in rows:
        print(" | ".join(r))
    print("\n## ran lines: time | transcript:line | what | label | note")
    for r in ranrows:
        print(" | ".join(r))


if __name__ == "__main__":
    main(sys.argv[1:])
