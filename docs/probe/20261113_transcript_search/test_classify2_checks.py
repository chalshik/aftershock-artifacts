"""Self-test of classify2.checks_ok (rule F round 18, BI6; owner-proxy on REG-22 draft 16, BL3a): a command that reads
checks.json counts as validity only if it takes `valid` or `failed` by name or tests existence, and names no other
field. Cases 1-3 are rule F round 18's synthetic reads that the earlier rule labelled `names_or_validity`.
run: python3 docs/probe/20261113_transcript_search/test_classify2_checks.py
"""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("classify2", Path(__file__).with_name("classify2.py"))
classify2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classify2)   # main() runs only under __main__
checks_ok = classify2.checks_ok
CASES = [
    ("""for d in runs/*w3000*; do python3 -c "import json;print(json.load(open('$d/checks.json')))"; done""", False),
    ("""for d in runs/*w3000*; do python3 -c "import json;c=json.load(open('$d/checks.json'));print(c['checks'][1]['detail'])"; done""", False),
    ("""jq '.checks[1].detail' runs/20261112-135538_burst_l1pl350cl_r2.0_w3000_s17/checks.json""", False),
    ("""for d in runs/*w3000*; do python3 -c "import json;print('$d', json.load(open('$d/checks.json'))['valid'])"; done""", True),
    ("""for d in runs/*w3000*; do jq -r '.valid' $d/checks.json; done""", True),
    ("""for d in runs/*w3000*; do jq -r '.failed' $d/checks.json; done""", True),
    ("""for d in runs/*w3000*; do jq . $d/checks.json; done""", False),
    ("""for d in runs/*w3000*; do [ -e $d/checks.json ] && echo $d; done""", True),
    ("""for d in runs/*; do echo $d; done""", True),
    ("""for d in runs/*w3000*; do python3 -c "import json;c=json.load(open('$d/checks.json'));print(c['valid'], c['checks'])"; done""", False),
    ("""for d in runs/*w3000*; do python3 -c "import json;c=json.load(open('$d/checks.json'));print(c.get('failed'), c['no_errors']['unfinished'])"; done""", False),
]
bad = 0
for i, (cmd, want) in enumerate(CASES, 1):
    got = checks_ok(cmd)
    print(("ok  " if got == want else "FAIL"), i, want, cmd[:90])
    bad += got != want
print(f"checks_ok self-test: {len(CASES) - bad} of {len(CASES)} pass")
sys.exit(1 if bad else 0)
