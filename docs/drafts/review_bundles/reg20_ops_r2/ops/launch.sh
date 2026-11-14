#!/bin/zsh
# Pre-launch checks and launch of one REG-20 arm A config on the VM; then wait for its checks.json (copied from
# ops_r3/launch.sh; README.md lists the differences; draft 2 of the operations decision).
# Usage: zsh launch.sh <config-name-without-.yaml>      (called by queue.sh)
# By hand it applies the queue's own rules and no fewer: it launches only the config that `next_step` (common.sh) says
# is next, with the attempt number it derives, so a launch by hand can pass neither the gate, nor the order, nor a
# pending copy or control decision, nor the rerun rule. What it does not do by hand is copy or decide a control: only
# the queue does. No launch before the gate's headings, its committed gate file and the owner's rulings are in place
# (common.sh `gate_in_log`); no time-of-day limit (the owner withdrew the quiet hours, 2026-11-13). It only reads the power limit (a limit other than 350.00 W stops). The pre-launch read goes to a
# time-stamped probe file; a stop before the launch spends no attempt. For an open-loop config the read includes the
# open-file limit of a shell on the VM (hard, and the soft limit after `ulimit -n 65536`); below 4096 it stops (REG-20).
# For the closed drift run the limit is recorded only. The attempt record state/attempt_<config>_<n>.txt is written
# immediately before the launch command, so from that line on the attempt is spent whatever happens. It holds the
# arm and the log's path, and launch.sh appends "end <time> <how>" when its wait ends (done, tmux_gone, unreachable
# with the time of the first unanswered read, still_running, no_run_id, launch_command_failed): the lost runs' elapsed
# time (RA6) and each control's gap after its burst run (RA-O1) come from these lines.
# Exit codes: 2 a check failed, nothing launched (or the launch command itself failed, attempt spent); 3 the run's
# tmux session ended without checks.json; 4 no run id; 5 still running after the wait; 7 the VM stopped answering.
# Exit 0 means only that checks.json exists; the queue reads `valid` from it, never from the log.
source ${0:A:h}/common.sh
mac_checks || exit 2
CFG=$1
gate_in_log || { echo "STOP: $MSG"; exit 2; }
[[ ${ALLCFG[(Ie)$CFG]} -gt 0 ]] || { echo "STOP: '$CFG' is not one of REG-20 arm A's eleven configs"; exit 2; }
[[ ${WAIT_MIN:-120} == <-> ]] || { echo "STOP: WAIT_MIN is not a number"; exit 2; }
[[ -s $ST/session_boot_id.txt ]] || { echo "STOP: no session probe (run session_probe.sh first)"; exit 2; }
next_step || { echo "STOP: $MSG"; exit 2; }
[[ $ACT == launch && $ARG == $CFG ]] || { echo "STOP: it is not $CFG's turn: the next step is '$ACT $ARG' (the queue does copies and control decisions)"; exit 2; }
OPEN=""; [[ $CFG == *_l1pl350ol_* ]] && OPEN=1
ATT=$NEXT_ATT; MARK=$ST/attempt_${CFG}_$ATT.txt
stamp; ts=$REPLY
PROBE=$PROBE_DIR/prelaunch_reg20_${CFG}_$ts.txt; LOG="~/${CFG}_$ts.log"
[[ ! -e $PROBE ]] || { echo "STOP: probe $PROBE exists"; exit 2; }
for i in $(seq 1 60); do
  T=$(ssh $K $H "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader") || { echo "STOP: the VM could not be read (temperature)"; exit 2; }
  [[ $T == <-> ]] || { echo "STOP: the temperature read '$T' is not a number"; exit 2; }
  (( T <= 45 )) && break
  sleep 30
done
ssh $K $H "echo '# pre-launch read for $CFG attempt $ATT (agent, read-only; scripts $SC)'; date -Is; nvidia-smi --query-gpu=power.limit,temperature.gpu,utilization.gpu,memory.used --format=csv; echo '# compute apps:'; nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader; echo '# tree:'; cd ~/aftershock-artifacts && git rev-parse HEAD && git status --short | wc -l; echo '# boot:'; cat /proc/sys/kernel/random/boot_id; echo '# free_kb:'; df -k --output=avail ~ | tail -1; echo '# nofile:'; ulimit -Hn; (ulimit -n $NOFILE_SET && ulimit -n) 2>&1 | tail -1; echo '# tmux:'; tmux ls 2>&1 || true" > $PROBE || { echo "STOP: the pre-launch read failed"; exit 2; }
cat $PROBE
LIM=$(sed -n 4p $PROBE | cut -d, -f1 | tr -d ' W'); TEMP=$(sed -n 4p $PROBE | cut -d, -f2 | tr -d ' ')
APPS=$(sed -n '/# compute apps:/,/# tree:/p' $PROBE | grep -vc '^#')
VMH=$(sed -n '/# tree:/{n;p;}' $PROBE); DIRTY=$(sed -n '/# tree:/{n;n;p;}' $PROBE | tr -d ' ')
BOOT=$(sed -n '/# boot:/{n;p;}' $PROBE); FREE=$(sed -n '/# free_kb:/{n;p;}' $PROBE | tr -d ' ')
NOFH=$(sed -n '/# nofile:/{n;p;}' $PROBE | tr -d ' '); NOFR=$(sed -n '/# nofile:/{n;n;p;}' $PROBE | tr -d ' ')
[[ $LIM == "350.00" ]] || { echo "STOP: power limit '$LIM'"; exit 2; }
[[ $TEMP == <-> ]] && (( TEMP <= 45 )) || { echo "STOP: GPU at '$TEMP' C"; exit 2; }
[[ $APPS == 0 ]] || { echo "STOP: GPU compute process present"; exit 2; }
[[ $VMH == $PIN && $DIRTY == 0 ]] || { echo "STOP: VM tree '$VMH' dirty='$DIRTY', pin $PIN"; exit 2; }
[[ -n $BOOT && $BOOT == $(<$ST/session_boot_id.txt) ]] || { echo "STOP: the VM rebooted since the session probe (boot id '$BOOT')"; exit 2; }
[[ $FREE == <-> ]] && (( FREE >= MIN_FREE_KB )) || { echo "STOP: only '$FREE' kB free on the VM"; exit 2; }
if [[ -n $OPEN ]]; then
  [[ $NOFR == <-> ]] && (( NOFR >= NOFILE_MIN )) || { echo "STOP: the open-file limit after 'ulimit -n $NOFILE_SET' reads '$NOFR' (hard '$NOFH'); REG-20 needs at least $NOFILE_MIN for the open arm: stop and ask"; exit 2; }
fi
sed -n '/# tmux:/,$p' $PROBE | grep -q "no server running\|No such file or directory\|error connecting" || { echo "STOP: a tmux session exists"; exit 2; }
[[ ! -e $MARK ]] || { echo "STOP: $MARK exists"; exit 2; }
print -r -l -- "attempt $ATT of $CFG" "time $(now)" "scripts $SC" "probe ${PROBE:t}" "arm ${${OPEN:+open}:-closed}" "log $LOG" "boot $BOOT" "nofile_hard $NOFH" "nofile_raised $NOFR" > $MARK || { echo "STOP: the attempt record could not be written; nothing launched"; exit 2; }
endrec() { print -r -- "end ${2:-$(now)} $1" >> $MARK; }
if [[ -n $OPEN ]]; then
  # In the shell tmux starts: raise the soft limit, write it as the log's first line, then become the harness.
  RUNCMD="ulimit -n $NOFILE_SET && echo \"nofile \$(ulimit -n)\" > $LOG && exec ~/.local/bin/uv run python -m harness.run configs/$CFG.yaml >> $LOG 2>&1"
else
  RUNCMD="~/.local/bin/uv run python -m harness.run configs/$CFG.yaml > $LOG 2>&1"
fi
ssh $K $H "cd ~/aftershock-artifacts && tmux new-session -d -s run '$RUNCMD'" || { echo "launch_command_failed" >> $MARK; endrec launch_command_failed; echo "STOP: the launch command failed; attempt $ATT of $CFG is recorded as spent. $ALLOWED"; exit 2; }
RID=""
for i in $(seq 1 24); do
  sleep 5
  RID=$(ssh $K $H "grep -m1 -o \"'run_id': '[^']*'\" $LOG 2>/dev/null | cut -d\"'\" -f4")
  [[ -n $RID ]] && break
done
[[ $RID =~ '^[0-9]{8}-[0-9]{6}_' && $RID == *_$CFG ]] || { endrec no_run_id; echo "STOP: no run id of $CFG in $LOG after 120 s (read '$RID'); the tmux session 'run' may still be alive. $ALLOWED"; exit 4; }
print -r -- "rid $RID" >> $MARK
if [[ -n $OPEN ]]; then
  NOFL=$(ssh $K $H "grep -m1 '^nofile ' $LOG 2>/dev/null")
  print -r -- "nofile_log ${${NOFL#nofile }:--}" >> $MARK
  [[ ${NOFL#nofile } == <-> ]] && (( ${NOFL#nofile } >= NOFILE_MIN )) || echo "WARN: the launch log's nofile line reads '$NOFL' (recorded in ${MARK:t}); the run goes on and its checks decide"
fi
echo "LAUNCHED $RID (attempt $ATT)"
fin=0; unreach=0; ufirst=""
for i in $(seq 1 ${WAIT_MIN:-120}); do
  ssh $K $H "test -f ~/aftershock-artifacts/runs/$RID/checks.json"; rc=$?
  if (( rc == 0 )); then fin=1; endrec done; echo "DONE $RID"; break; fi
  if (( rc == 255 )); then (( unreach == 0 )) && ufirst=$(now); unreach=$((unreach + 1)); sleep 60; continue; fi
  unreach=0
  ssh $K $H "tmux has-session -t run 2>/dev/null"; rc=$?
  if (( rc == 1 )); then
    for j in 1 2 3 4 5 6; do sleep 20; if ssh $K $H "test -f ~/aftershock-artifacts/runs/$RID/checks.json"; then fin=1; break; fi; done
    (( fin )) && { endrec done; echo "DONE $RID (after tmux ended)"; break; }
    endrec tmux_gone; echo "TMUX GONE, no checks.json: $RID. $ALLOWED"; exit 3
  fi
  sleep 60
done
if (( ! fin )); then
  (( unreach >= 3 )) && { endrec unreachable $ufirst; echo "VM NOT REACHABLE for the last $unreach reads; $RID unknown. $ALLOWED"; exit 7; }
  endrec still_running; echo "STILL RUNNING $RID after ${WAIT_MIN:-120} min. $ALLOWED"; exit 5
fi
exit 0
