#!/bin/zsh
# E1's queue (registration: docs/drafts/e1_draft4.md until it is registered; README.md). One command, no settings:
#   zsh docs/probe/20261113_e1/ops/queue.sh        (in the background)
# It starts only when e1_commit.txt names the commit that holds E1's approval, REG-19's [RESULT] is in the committed log
# and REG-19's queue lock does not exist. It can be started again after any stop and launches nothing that is already
# there. Each turn asks `next_step` (common.sh) what to do, from the records in state/, the settled launch logs and the
# VM's checks.json files (valid, failed):
#   - settle an invocation that has ended: its launch log's run_id lines name its runs; print each run as VALID,
#     INVALID (with its failed checks) or NO CHECKS.JSON, and, for the sweep, each rate it never started;
#   - copy every run with a checks.json (valid or invalid) to the Mac and compare every file's sha256 with the VM's;
#   - launch the sweep (first, once), then, per rate in the sweep's order, the next attempt E1's stopping rule allows;
#   - end: write state/queue_end.txt (one line per rate) and print it.
# After an invalid run the queue stops before the next launch (as REG-19's does); starting it again applies the rerun
# rule from checks.json alone. Every stop exits non-zero and prints the allowed reads. No result is computed here.
source ${0:A:h}/common.sh
mac_checks || { echo "QUEUE STOP $MSG"; echo "$ALLOWED"; exit 2; }
ready_to_run || { echo "QUEUE STOP $MSG"; echo "$ALLOWED"; exit 2; }
[[ ${WAIT_MIN:-0} == <-> ]] || { echo "QUEUE STOP WAIT_MIN is not a number"; echo "$ALLOWED"; exit 2; }
mkdir -p $ST
LOCK=$ST/queue.lock
if ! mkdir $LOCK 2> /dev/null; then
  pid=$(cat $LOCK/pid 2> /dev/null)
  if [[ -n $pid ]] && kill -0 $pid 2> /dev/null; then echo "QUEUE STOP another E1 queue is running (pid $pid)"; echo "$ALLOWED"; exit 1; fi
  stamp; mv $LOCK $ST/queue.lock.stale_$REPLY && mkdir $LOCK || { echo "QUEUE STOP the lock could not be taken"; echo "$ALLOWED"; exit 1; }
fi
print -r -- $$ > $LOCK/pid
trap 'stamp; mv $LOCK $ST/queue.lock.ended_$REPLY 2> /dev/null' EXIT
stop() { echo "QUEUE STOP $1"; echo "$ALLOWED"; exit ${2:-1}; }
echo "QUEUE START E1; scripts $SC; registered commit $E1; $(date -u +%Y-%m-%dT%H:%M:%SZ)"
cd $R || stop "no repo"

# The runs an attempt's launch log names, as the VM's checks.json says them; an invalid one sets PAUSE.
report_settled() {
  local f=$ST/settled_${${1:t}%.txt}.txt line l2 parts id st fl r started=()
  for line in ${(f)"$(grep '^rid ' $f)"}; do
    id=${${=line}[2]}; st=missing; fl=-
    for l2 in $VMS; do parts=(${=l2}); [[ $parts[1] == $id ]] && { st=$parts[2]; fl=$parts[3]; }; done
    started+=($(rate_of $id))
    case $st in
      valid) echo "RUN $id VALID";;
      invalid) echo "RUN $id INVALID failed=$fl"; PAUSE+="${PAUSE:+; }$id failed=$fl";;
      nochecks) echo "RUN $id NO CHECKS.JSON";;
      *) echo "RUN $id $st";;
    esac
  done
  if [[ ${1:t} == attempt_sweep_1.txt ]]; then
    for r in $RATES; do
      [[ ${started[(Ie)$r]} -gt 0 ]] || echo "NOT STARTED rate $r by the sweep: its first attempt is configs/$ONLY$r.yaml"
    done
  fi
}

PAUSE=""
for turn in {1..$MAX_TURNS}; do
  next_step || stop "$MSG"
  case $ACT in
    settle)
      settle $ARG || stop "$MSG"
      echo "SETTLED ${ARG:t}"
      report_settled $ARG;;
    copy)
      copy_verify $ARG || stop "$MSG";;
    launch)
      [[ -z $PAUSE ]] || stop "after an invalid run ($PAUSE). Starting the queue again applies E1's rerun rule from checks.json (valid, failed) alone"
      stamp; outf=$ST/launch_${ARG}_$REPLY.out
      [[ ! -e $outf ]] || stop "$outf exists"
      echo "LAUNCH $ARG attempt $NEXT_ATT"
      out=$(zsh $S/launch.sh $ARG 2>&1); rc=$?
      print -r -- "$out" > $outf
      print -r -- "$out" | grep -E '^(LAUNCHED|ENDED) '
      (( rc == 0 )) || stop "launch of $ARG rc=$rc: $(print -r -- "$out" | grep '^STOP' | tail -1)";;
    done)
      rec=$ST/queue_end.txt
      if [[ -e $rec ]]; then
        [[ "$(head -n ${#SUMMARY} $rec)" == "$(print -r -l -- $SUMMARY)" ]] || stop "state/queue_end.txt differs from what the VM and the records say now: the owner decides"
      else
        print -r -l -- $SUMMARY "time $(date -u +%Y-%m-%dT%H:%M:%SZ)" "scripts $SC" "commit $E1" > $rec.tmp && mv $rec.tmp $rec || stop "state/queue_end.txt could not be written"
      fi
      print -r -l -- $SUMMARY
      if (( ${#SPENT} )); then
        echo "QUEUE END rates without a valid run after $MAX_ATTEMPTS attempts: ${SPENT[*]}. E1's result reports them as holes (registration, 'Holes'); the owner decides. Every other run is copied and checksum-verified"
        echo "$ALLOWED"; exit 3
      fi
      echo "QUEUE DONE (every rate of E1 has a valid run, copied and checksum-verified). Next: E1's [RESULT] by hand, after REG-21's first [RESULT] (registration, 'Result, computed once')"
      exit 0;;
    *) stop "next_step gave no action";;
  esac
done
stop "more than $MAX_TURNS turns without an end"
