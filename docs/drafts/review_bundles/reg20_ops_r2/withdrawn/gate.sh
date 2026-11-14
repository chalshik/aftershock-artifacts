#!/bin/zsh
# REG-20's gate, once, from the repo root on the Mac:   zsh docs/probe/20261113_reg20/ops/gate.sh
# (RB5 (ii); decisions.md 2026-11-12 [REG] REG-20, "Gate before arm A", and the owner's approval: "computed once after
# REG-19's [RESULT]"). It runs `.venv/bin/python -m analysis.k1 reg20_a_may_start` with no AFTERSHOCK_UNSEAL (it reads
# only REG-19's runs, which REG-19's [RESULT] unseals), after the Mac-side checks pass, only when HEAD's
# docs/decisions.md holds REG-19's [RESULT] heading and the working tree's docs/decisions.md equals HEAD's (the seal
# reads the working tree's), and only if no gate file exists yet. Its stdout and stderr go to
# docs/probe/20261113_reg20/reg20_gate_<stamp>.txt and reg20_gate_err_<stamp>.txt, to be committed at once, alone.
# The heading "… REG-20 arm A starts: k1.reg20_a_may_start passed" is written only if that file reads 'may_start': True,
# and the entry quotes it verbatim; the queue, launch.sh and final.sh check this file in HEAD (common.sh `gate_in_log`).
# A stderr with a `withheld:` line, or a computation that fails, is reported and the files are kept and committed.
source ${0:A:h}/common.sh
mac_checks || exit 2
log=$(git -C $R show HEAD:docs/decisions.md 2> /dev/null) || { echo "STOP: the committed docs/decisions.md cannot be read"; exit 2; }
print -r -- "$log" | grep -q -E "$RESULT_PAT" || { echo "STOP: no '[RESULT] REG-19' heading in the committed docs/decisions.md: the gate is computed only after REG-19's [RESULT]"; exit 2; }
git -C $R diff --quiet HEAD -- docs/decisions.md || { echo "STOP: the working tree's docs/decisions.md differs from HEAD's (the seal reads it): commit or set the change aside first"; exit 2; }
prev=($PROBE_DIR/reg20_gate_*(N))
(( ${#prev} == 0 )) || { echo "STOP: the gate was already computed or tried: ${prev[*]:t}"; exit 2; }
stamp; ts=$REPLY; out=$PROBE_DIR/reg20_gate_$ts.txt; err=$PROBE_DIR/reg20_gate_err_$ts.txt
(cd $R && env -u AFTERSHOCK_UNSEAL $PY -m analysis.k1 reg20_a_may_start > $out 2> $err); rc=$?
echo "GATE rc $rc; scripts $SC; Mac HEAD $(git -C $R rev-parse HEAD); output ${out:t}; stderr_lines $(wc -l < $err | tr -d ' ') ${err:t}"
(( rc == 0 )) || { echo "STOP: reg20_a_may_start failed (see ${err:t}). Commit both files; a second try is an operational step with its own [OPS] entry"; exit 1; }
if grep -q '^withheld:' $err; then echo "STOP: the gate's stderr holds a 'withheld:' line: a REG-19 folder was skipped; commit both files; the owner decides"; exit 1; fi
cat $out
grep -q -E "$GATE_LINE_RE" $out && echo "GATE may_start True: the start heading may be written, quoting this file" || echo "GATE may_start not True: arm A does not start (REG-20, decisions.md 2026-11-12 [REG])"
