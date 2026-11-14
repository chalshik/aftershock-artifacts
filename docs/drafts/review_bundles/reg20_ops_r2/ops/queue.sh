#!/bin/zsh
# REG-20 arm A queue (decisions.md 2026-11-12 [REG] REG-20 and the owner's approval; the operations decision, draft 2;
# README.md). One command, no settings:      zsh docs/probe/20261113_reg20/ops/queue.sh        (in the background)
# It starts only when HEAD's docs/decisions.md holds REG-19's [RESULT] heading, the owner's rulings heading and, on a
# later line than both, the decision that arm A starts (with no stop heading after it), when HEAD holds the one
# committed gate file (docs/probe/reg20/, 3c8e5dc) reading 'may_start': True, and when owner_rulings.txt answers every owner's point; it never computes the
# gate itself. It can be started again after any stop and launches nothing that is already there. Each turn of its
# loop first runs the Mac-side checks, then asks `next_step` (common.sh) what to do, from the records in state/, the
# rulings and the VM:
#   - copy a finished run (valid or invalid) to the holding folder, compare every file's sha256 with the VM's, apply
#     today's checks there (ruling 2a), then move it into the Mac's runs/ and compare again; or hold it in the holding
#     folder when its slot is settled not_run;
#   - after a valid open burst run is copied, rechecked and verified, run control_due.py once on it, with the Mac-side
#     checks just before and just after, and append its one line (CONTROL_DUE yes|no|unclear) to state/control_due.txt;
#     only `yes` puts its control right after it;
#   - launch the next config of the registered order (launch.sh): open burst runs 15, 16, 17, the drift run, 18, 19;
#   - end: write state/queue_done.txt (one line per slot, then the copied, held and lost runs and the runs the recheck
#     changed) and print it. Next: final.sh, once.
# `valid` is read from checks.json, never from a log. After an invalid run, or a run set aside by the recheck, the
# queue stops; starting it again applies REG-20's rerun rule (common.sh `decide`). After an open run whose launch log
# shows an open-file limit below 4096 (or none) it stops as well, and the run is used only with a nofile_ok record.
# Every stop exits non-zero.
source ${0:A:h}/common.sh
mac_checks || exit 2
gate_in_log || { echo "QUEUE STOP $MSG"; exit 2; }
[[ ${WAIT_MIN:-120} == <-> ]] || { echo "QUEUE STOP WAIT_MIN is not a number"; exit 2; }
mkdir -p $ST
LOCK=$ST/queue.lock
if ! mkdir $LOCK 2> /dev/null; then
  pid=$(cat $LOCK/pid 2> /dev/null)
  if [[ -n $pid ]] && kill -0 $pid 2> /dev/null; then echo "QUEUE STOP another queue is running (pid $pid)"; exit 1; fi
  stamp; mv $LOCK $ST/queue.lock.stale_$REPLY && mkdir $LOCK || { echo "QUEUE STOP the lock could not be taken"; exit 1; }
fi
print -r -- $$ > $LOCK/pid
trap 'stamp; mv $LOCK $ST/queue.lock.ended_$REPLY 2> /dev/null' EXIT
stop() { echo "QUEUE STOP $*"; exit 1; }
echo "QUEUE START REG-20 arm A; scripts $SC; pin $PIN; rulings 2a=$(ruling 2a) 6=$(ruling 6) 7=$(ruling 7) 8=$(ruling 8) 9=$(ruling 9) 16=$(ruling 16); $(now)"
cd $R || stop "no repo"

# control_due.py on one copied, rechecked, verified run, once; its line is appended to state/control_due.txt. The
# Mac-side checks run immediately before and immediately after the call; if either fails, the decision is dropped (RA4).
control_due() {
  local rid=$1 ts errf out rc mc
  [[ -f $ST/copied_$rid.txt && -f $ST/recheck_$rid.json ]] || stop "$rid has no verified copy or no recheck record: no control decision"
  mc=$(mac_checks) || stop "Mac-side check failed just before the control decision on $rid: ${mc##*$'\n'}; no control decision is recorded"
  stamp; ts=$REPLY; errf=$ST/control_due_err_${rid}_$ts.txt
  [[ ! -e $errf ]] || stop "$errf exists"
  out=$(cd $R && AFTERSHOCK_UNSEAL=REG-20 $PY $S/control_due.py $rid 2> $errf); rc=$?
  mc=$(mac_checks) || stop "Mac-side check failed just after the control decision on $rid: ${mc##*$'\n'}; the decision is dropped, not recorded or shown"
  (( rc == 0 )) || stop "control_due.py failed on $rid (rc $rc; see ${errf:t}); no control decision is recorded"
  if grep -qE 'Traceback|Error|Exception' $errf; then stop "control_due.py wrote an error line on $rid (see ${errf:t}); no control decision is recorded"; fi
  [[ $out =~ '^CONTROL_DUE (yes|no|unclear)$' ]] || stop "control_due.py printed something other than one CONTROL_DUE line on $rid; no control decision is recorded"
  print -r -- "$rid $out time $(now) scripts $SC stderr_lines $(wc -l < $errf | tr -d ' ') ${errf:t}" >> $ST/control_due.txt || stop "the control decision of $rid could not be recorded"
  echo "CONTROL $rid $out"
}

for turn in {1..80}; do
  mc=$(mac_checks) || stop "Mac-side check failed before turn $turn: ${mc##*$'\n'}"
  next_step || stop "$MSG"
  case $ACT in
    copy)
      copy_verify $ARG; rc=$?
      (( rc == 3 )) && stop "after a run set aside by the recheck (ruling 2a). Starting the queue again applies REG-20's rerun rule to its config"
      (( rc == 0 )) || stop "$MSG";;
    hold)
      copy_verify $ARG hold || stop "$MSG";;
    due)
      control_due $ARG;;
    launch)
      cfg=$ARG
      stamp; ts=$REPLY; outf=$ST/launch_${cfg}_$ts.out
      [[ ! -e $outf ]] || stop "$outf exists"
      out=$(zsh $S/launch.sh $cfg 2>&1); rc=$?
      print -r -- "$out" > $outf
      rid=$(print -r -- "$out" | sed -n 's/^LAUNCHED \([^ ]*\).*/\1/p')
      (( rc == 0 )) || stop "$cfg launch rc=$rc rid=$rid: $(print -r -- "$out" | grep -E 'STOP|TMUX GONE|STILL RUNNING|VM NOT REACHABLE' | tail -1)"
      [[ -n $rid ]] || stop "$cfg: launch.sh ended with rc 0 and no run id"
      warn=$(print -r -- "$out" | grep '^WARN'); [[ -z $warn ]] || print -r -- "$warn"
      vm_state || stop "$cfg: the VM's run folders could not be read after the run; $rid is not judged. Start the queue again"
      state=""; failed=""
      for line in $VMS; do parts=(${=line}); if [[ $parts[1] == $rid ]]; then state=$parts[2]; failed=$parts[3]; fi; done
      case $state in
        valid) echo "RUN $cfg $rid VALID"
               [[ -z $warn ]] || stop "the shell that started $rid did not show an open-file limit of at least $NOFILE_MIN (its attempt record holds the line): REG-20 says stop and ask. The run is used only with a record state/nofile_ok_$rid.txt ('under …', 'by …'), logged in an [OPS] entry (RB15)";;
        invalid) echo "RUN $cfg $rid INVALID failed=$failed"; stop "after an invalid run. Starting the queue again copies it and applies REG-20's rerun rule from checks.json alone";;
        *) stop "$cfg: checks.json of $rid could not be read after the run (state '$state')";;
      esac;;
    done)
      rec=$ST/queue_done.txt
      if [[ -e $rec ]]; then
        [[ "$(head -n ${#SUMMARY} $rec)" == "$(print -r -l -- $SUMMARY)" ]] || stop "state/queue_done.txt differs from what the VM and the records say now: the owner decides"
      else
        print -r -l -- $SUMMARY "time $(now)" "scripts $SC" "pin $PIN" "rulings 2a=$(ruling 2a) 6=$(ruling 6) 7=$(ruling 7) 8=$(ruling 8) 9=$(ruling 9) 16=$(ruling 16)" > $rec.tmp && mv $rec.tmp $rec || stop "state/queue_done.txt could not be written"
      fi
      print -r -l -- $SUMMARY
      echo "QUEUE DONE (arm A: five open burst runs settled, the drift run settled). Next: final.sh, once"
      exit 0;;
    *) stop "next_step gave no action";;
  esac
done
stop "more than 80 steps without an end"
