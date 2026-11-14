#!/bin/zsh
# REG-20's table, once, from the repo root on the Mac:   zsh docs/probe/20261113_reg20/ops/final.sh
# (mirrors ops_r3/final.sh; never run mid-matrix; draft 2 of the operations decision). Allowed only after the queue
# has ended: state/queue_done.txt exists, no queue holds the lock, its six slot lines are of the forms the queue
# writes, and the folders of REG-20's eleven configs in the Mac's runs/ are exactly the runs it lists as copied, each
# with a verified copy record and a checks.json, none held or set aside (RB4, RA-O2). Then today's checks are applied
# read-only to those folders by analysis.recheck (RB2), and the result must agree with the queue's own rechecks. The
# command is the registered one, `AFTERSHOCK_UNSEAL=REG-20 .venv/bin/python -m analysis.k1 reg20` (point 13), with the
# seal lifted for REG-20 only and for this one process. Its stdout and stderr go to state/reg20_final_<stamp>.txt and
# state/reg20_final_err_<stamp>.txt, to be committed at once, alone. Refused when either file exists: a second try is an
# operational step with its own [OPS] entry. A stderr that holds a `withheld:` line, or Mac-side checks that fail just
# after the computation, stop it after the files are written (they are kept and committed all the same).
source ${0:A:h}/common.sh
mac_checks || exit 2
gate_in_log || { echo "STOP: $MSG"; exit 2; }
if [[ -d $ST/queue.lock ]]; then
  pid=$(cat $ST/queue.lock/pid 2> /dev/null)
  [[ -n $pid ]] && kill -0 $pid 2> /dev/null && { echo "STOP: a queue is running (pid $pid): no table mid-matrix"; exit 2; }
fi
rec=$ST/queue_done.txt
[[ -f $rec ]] || { echo "STOP: no table. The queue has not ended (no state/queue_done.txt); after an operational stop the owner decides"; exit 2; }
# The six slot lines, in the plan's order, of the forms next_step writes (RB3: not_run and control_not_run included).
RID_RE='[0-9]{8}-[0-9]{6}_[A-Za-z0-9_.]+'
want=(s15 s16 s17 drift s18 s19)
slots=("${(@f)$(head -6 $rec)}")
for i in {1..6}; do
  l=$slots[i]
  [[ ${l%% *} == $want[i] ]] || { echo "STOP: line $i of state/queue_done.txt is not the slot $want[i]"; exit 2; }
  if [[ $want[i] == drift ]]; then
    [[ $l =~ "^drift ($RID_RE|not_run $RID_RE(,$RID_RE)*)\$" ]] || { echo "STOP: the drift slot line is not of a form the queue writes: '$l'"; exit 2; }
  else
    [[ $l =~ "^s1[5-9] ($RID_RE CONTROL_DUE (no|unclear)|$RID_RE CONTROL_DUE yes control $RID_RE gap_s (-|-?[0-9]+) boot (same|changed|-)|$RID_RE CONTROL_DUE yes control_not_run $RID_RE|lost_open $RID_RE( $RID_RE)+|not_run $RID_RE)\$" ]] || { echo "STOP: slot line $i is not of a form the queue writes: '$l'"; exit 2; }
  fi
done
copied=(${(f)"$(sed -n 's/^copied //p' $rec)"})
(( ${#copied} >= 1 )) || { echo "STOP: state/queue_done.txt lists no copied run"; exit 2; }
for rid in $copied; do
  [[ -f $ST/copied_$rid.txt && -f $ST/recheck_$rid.json && -f $R/runs/$rid/checks.json ]] || { echo "STOP: $rid, listed as copied in state/queue_done.txt, has no verified copy, no recheck record or no checks.json on the Mac"; exit 2; }
done
# The folder set (RB4 (i), RA-O2): every folder of the eleven configs in runs/ is one the queue copied, and the reverse.
here=()
for c in $ALLCFG; do here+=($R/runs/*_${c}(N/:t)); done
for rid in $here; do
  [[ ${copied[(Ie)$rid]} -gt 0 ]] || { echo "STOP: runs/$rid is a folder of a REG-20 config that state/queue_done.txt does not list as copied (a lost, held or set-aside folder, or one copied by hand): k1 would count it; the owner decides"; exit 2; }
  [[ ! -f $ST/held_$rid.txt && ! -f $ST/setaside_$rid.txt ]] || { echo "STOP: runs/$rid is held or set aside"; exit 2; }
done
(( ${#here} == ${#copied} )) || { echo "STOP: runs/ holds ${#here} folders of REG-20's configs and state/queue_done.txt lists ${#copied} copied"; exit 2; }
prev=($ST/reg20_final_*.txt(N) $ST/reg20_recheck_final_*(N))
(( ${#prev} == 0 )) || { echo "STOP: the table was already computed or tried: ${prev[*]:t}"; exit 2; }
# Today's checks over the same folders (RB2 (ii)), read-only, validity fields only; their changes must be the ones the
# queue recorded at each copy (queue_done.txt's recheck_changed lines that say kept).
recheck_guards || { echo "STOP: $MSG"; exit 2; }
stamp; ts=$REPLY
kept=(${(f)"$(sed -n 's/^recheck_changed \([^ ]*\) kept$/\1/p' $rec)"})
n_all=0; changed_all=()
for i in 1 2; do
  rk=$ST/reg20_recheck_final_${ts}_$i.json; rkerr=$ST/reg20_recheck_final_err_${ts}_$i.txt
  raw=$(cd $R && AFTERSHOCK_UNSEAL=REG-20 $PY -m analysis.recheck "$RECHECK_PATS[i]" 2> $rkerr) || { echo "STOP: analysis.recheck failed on '$RECHECK_PATS[i]' (see ${rkerr:t}); no table"; exit 2; }
  if grep -q '^withheld:' $rkerr; then echo "STOP: analysis.recheck skipped sealed folders on '$RECHECK_PATS[i]' (${rkerr:t}); no table"; exit 2; fi
  print -r -- "$raw" | python3 -c 'import json, sys
d = json.load(sys.stdin)
keep = ("run", "stored_valid", "now_valid", "stored_failed", "now_failed", "error")
print(json.dumps({"mac_head": sys.argv[1], "pattern": sys.argv[2], "n_runs": d["n_runs"], "n_changed": d["n_changed"],
                  "changed": [{k: r[k] for k in keep if k in r} for r in d["changed"]]}, indent=1))' "$(git -C $R rev-parse HEAD)" "$RECHECK_PATS[i]" > $rk || { echo "STOP: the recheck's output on '$RECHECK_PATS[i]' cannot be read; no table"; exit 2; }
  n_all=$((n_all + $(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["n_runs"])' $rk)))
  changed_all+=(${(f)"$(python3 -c 'import json, sys; [print(r["run"]) for r in json.load(open(sys.argv[1]))["changed"]]' $rk)"})
done
echo "RECHECK before the table: $n_all runs, ${#changed_all} changed (${ts}; validity fields only)"
(( n_all == ${#copied} )) || { echo "STOP: the recheck before the table saw $n_all runs where ${#copied} are copied; no table"; exit 2; }
[[ "${(j: :)${(o)changed_all}}" == "${(j: :)${(o)kept}}" ]] || { echo "STOP: the recheck before the table changes (${(o)changed_all}) other runs than the queue kept at their copies (${(o)kept}); no table, the owner decides"; exit 2; }
stamp; ts=$REPLY; out=$ST/reg20_final_$ts.txt; err=$ST/reg20_final_err_$ts.txt
(cd $R && AFTERSHOCK_UNSEAL=REG-20 $PY -m analysis.k1 reg20 > $out 2> $err); rc=$?
mc=$(mac_checks); mrc=$?
echo "FINAL rc $rc; scripts $SC; pin $PIN; Mac HEAD $(git -C $R rev-parse HEAD); runs ${#copied}; output ${out:t}; stderr_lines $(wc -l < $err | tr -d ' ') ${err:t}"
(( mrc == 0 )) || { echo "STOP: the Mac-side checks failed just after the table (${mc##*$'\n'}): the table is not used; commit both files and the owner decides"; exit 1; }
(( rc == 0 )) || { echo "STOP: reg20 failed (see $err). A second try is an operational step with its own [OPS] entry: both files must first be set aside by hand"; exit 1; }
if grep -q '^withheld:' $err; then echo "STOP: the table's stderr holds a 'withheld:' line: a folder it needs was skipped; the table is not used; commit both files and the owner decides"; exit 1; fi
cat $out
