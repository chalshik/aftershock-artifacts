#!/bin/zsh
# REG-20's table, once, from the repo root on the Mac:   zsh docs/probe/20261113_reg20/ops/final.sh
# (mirrors ops_r3/final.sh; never run mid-matrix). Allowed only after the queue has ended: state/queue_done.txt
# exists, no queue holds the lock, and every run that record names is on the Mac with a verified copy record. The
# command is the registered one, `AFTERSHOCK_UNSEAL=REG-20 uv run python -m analysis.k1 reg20` (agent/RUNBOOK.md §5),
# with the seal lifted for REG-20 only and for this one process. Its stdout and stderr go to
# state/reg20_final_<stamp>.txt and state/reg20_final_err_<stamp>.txt, to be committed at once, alone. Refused when
# either file exists: a second try is an operational step with its own [OPS] entry.
source ${0:A:h}/common.sh
mac_checks || exit 2
gate_in_log || { echo "STOP: $MSG"; exit 2; }
if [[ -d $ST/queue.lock ]]; then
  pid=$(cat $ST/queue.lock/pid 2> /dev/null)
  [[ -n $pid ]] && kill -0 $pid 2> /dev/null && { echo "STOP: a queue is running (pid $pid): no table mid-matrix"; exit 2; }
fi
rec=$ST/queue_done.txt
[[ -f $rec ]] || { echo "STOP: no table. The queue has not ended (no state/queue_done.txt); after an operational stop the owner decides"; exit 2; }
rids=(${(f)"$(grep -oE '[0-9]{8}-[0-9]{6}_[A-Za-z0-9_.]+' $rec)"})
(( ${#rids} >= 6 )) || { echo "STOP: state/queue_done.txt names ${#rids} runs, fewer than the six of arm A and the drift run"; exit 2; }
for rid in $rids; do
  [[ -f $ST/copied_$rid.txt && -d $R/runs/$rid ]] || { echo "STOP: $rid, named in state/queue_done.txt, has no verified copy on the Mac"; exit 2; }
done
prev=($ST/reg20_final_*.txt(N))
(( ${#prev} == 0 )) || { echo "STOP: the table was already computed or tried: ${prev[*]:t}"; exit 2; }
stamp; ts=$REPLY; out=$ST/reg20_final_$ts.txt; err=$ST/reg20_final_err_$ts.txt
(cd $R && AFTERSHOCK_UNSEAL=REG-20 uv run python -m analysis.k1 reg20 > $out 2> $err); rc=$?
echo "FINAL rc $rc; scripts $SC; pin $PIN; Mac HEAD $(git -C $R rev-parse HEAD); runs ${#rids}; output ${out:t}; stderr_lines $(wc -l < $err | tr -d ' ') ${err:t}"
(( rc == 0 )) || { echo "STOP: reg20 failed (see $err). A second try is an operational step with its own [OPS] entry: both files must first be set aside by hand"; exit 1; }
cat $out
