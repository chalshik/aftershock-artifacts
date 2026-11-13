#!/bin/zsh
# Pre-launch checks and launch of one REG-19 config on the VM; then wait for its checks.json.
# Usage: zsh launch.sh <config-name-without-.yaml>      (called by queue.sh)
# By hand it applies the queue's own rules and no fewer: `gate` (common.sh) accepts only the four configs of seeds
# 18 and 19, nothing of a seed that has a step record, seed 19 only after seed 18's record says 'continue': True,
# and a burst run only after a valid control; `decide` says which attempt this is and refuses when a valid run
# exists or REG-19 allows no rerun. What it does not do by hand is copy, verify or step: only the queue does.
# No launch before the decision is in the committed log, and none in the hours in which the VM has been powered off.
# It only reads the power limit (a limit other than 350.00 W stops, as REG-19 registers). The pre-launch read goes to
# a time-stamped probe file; a stop before the launch spends no attempt. The attempt record state/attempt_<config>_<n>.txt
# is written immediately before the launch command, so from that line on the attempt is spent whatever happens.
# Exit codes: 2 a check failed, nothing launched (or the launch command itself failed, attempt spent); 3 the run's
# tmux session ended without checks.json; 4 no run id; 5 still running after the wait; 7 the VM stopped answering.
# Exit 0 means only that checks.json exists; the queue reads `valid` from it, never from the log.
source ${0:A:h}/common.sh
mac_checks || exit 2
CFG=$1
decision_in_log || { echo "STOP: $MSG"; exit 2; }
gate "$CFG" || { echo "STOP: $MSG"; exit 2; }
[[ -f $W/configs/$CFG.yaml ]] || { echo "STOP: no config '$CFG' at the pin"; exit 2; }
[[ ${WAIT_MIN:-120} == <-> ]] || { echo "STOP: WAIT_MIN is not a number"; exit 2; }
[[ -s $ST/session_boot_id.txt ]] || { echo "STOP: no session probe (run session_probe.sh first)"; exit 2; }
decide $CFG || { echo "STOP: $MSG"; exit 2; }
[[ -z $RID ]] || { echo "STOP: $RID is a valid run of $CFG: nothing to launch"; exit 2; }
quiet_now $CFG && { echo "STOP: no launch of $CFG between $QUIET_CONTROL_FROM (a control) or $QUIET_BURST_FROM (a burst run) and $QUIET_TO UTC, or between $QUIET2_CONTROL_FROM (a control) or $QUIET2_BURST_FROM (a burst run) and $QUIET2_TO UTC: the run would last into the hours in which the VM has been powered off. Start the queue again after the window ends"; exit 2; }
ATT=$LAUNCH; MARK=$ST/attempt_${CFG}_$ATT.txt
stamp; ts=$REPLY
PROBE=$PROBE_DIR/prelaunch_reg19_${CFG}_$ts.txt; LOG="~/${CFG}_$ts.log"
[[ ! -e $PROBE ]] || { echo "STOP: probe $PROBE exists"; exit 2; }
for i in $(seq 1 60); do
  T=$(ssh $K $H "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader") || { echo "STOP: the VM could not be read (temperature)"; exit 2; }
  [[ $T == <-> ]] || { echo "STOP: the temperature read '$T' is not a number"; exit 2; }
  (( T <= 45 )) && break
  sleep 30
done
ssh $K $H "echo '# pre-launch read for $CFG attempt $ATT (agent, read-only; scripts $SC)'; date -Is; nvidia-smi --query-gpu=power.limit,temperature.gpu,utilization.gpu,memory.used --format=csv; echo '# compute apps:'; nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader; echo '# tree:'; cd ~/aftershock-artifacts && git rev-parse HEAD && git status --short | wc -l; echo '# boot:'; cat /proc/sys/kernel/random/boot_id; echo '# free_kb:'; df -k --output=avail ~ | tail -1; echo '# tmux:'; tmux ls 2>&1 || true" > $PROBE || { echo "STOP: the pre-launch read failed"; exit 2; }
cat $PROBE
LIM=$(sed -n 4p $PROBE | cut -d, -f1 | tr -d ' W'); TEMP=$(sed -n 4p $PROBE | cut -d, -f2 | tr -d ' ')
APPS=$(sed -n '/# compute apps:/,/# tree:/p' $PROBE | grep -vc '^#')
VMH=$(sed -n '/# tree:/{n;p;}' $PROBE); DIRTY=$(sed -n '/# tree:/{n;n;p;}' $PROBE | tr -d ' ')
BOOT=$(sed -n '/# boot:/{n;p;}' $PROBE); FREE=$(sed -n '/# free_kb:/{n;p;}' $PROBE | tr -d ' ')
[[ $LIM == "350.00" ]] || { echo "STOP: power limit '$LIM'"; exit 2; }
[[ $TEMP == <-> ]] && (( TEMP <= 45 )) || { echo "STOP: GPU at '$TEMP' C"; exit 2; }
[[ $APPS == 0 ]] || { echo "STOP: GPU compute process present"; exit 2; }
[[ $VMH == $PIN && $DIRTY == 0 ]] || { echo "STOP: VM tree '$VMH' dirty='$DIRTY', pin $PIN"; exit 2; }
[[ -n $BOOT && $BOOT == $(<$ST/session_boot_id.txt) ]] || { echo "STOP: the VM rebooted since the session probe (boot id '$BOOT')"; exit 2; }
[[ $FREE == <-> ]] && (( FREE >= MIN_FREE_KB )) || { echo "STOP: only '$FREE' kB free on the VM"; exit 2; }
sed -n '/# tmux:/,$p' $PROBE | grep -q "no server running\|No such file or directory\|error connecting" || { echo "STOP: a tmux session exists"; exit 2; }
[[ ! -e $MARK ]] || { echo "STOP: $MARK exists"; exit 2; }
print -r -l -- "attempt $ATT of $CFG" "time $(date -u +%Y-%m-%dT%H:%M:%SZ)" "scripts $SC" "probe ${PROBE:t}" "boot $BOOT" > $MARK || { echo "STOP: the attempt record could not be written; nothing launched"; exit 2; }
ssh $K $H "cd ~/aftershock-artifacts && tmux new-session -d -s run \"~/.local/bin/uv run python -m harness.run configs/$CFG.yaml > $LOG 2>&1\"" || { echo "launch_command_failed" >> $MARK; echo "STOP: the launch command failed; attempt $ATT of $CFG is recorded as spent. $ALLOWED"; exit 2; }
RID=""
for i in $(seq 1 24); do
  sleep 5
  RID=$(ssh $K $H "grep -m1 -o \"'run_id': '[^']*'\" $LOG 2>/dev/null | cut -d\"'\" -f4")
  [[ -n $RID ]] && break
done
[[ $RID =~ '^[0-9]{8}-[0-9]{6}_' && $RID == *_$CFG ]] || { echo "STOP: no run id of $CFG in $LOG after 120 s (read '$RID'); the tmux session 'run' may still be alive. $ALLOWED"; exit 4; }
print -r -- "rid $RID" >> $MARK
echo "LAUNCHED $RID (attempt $ATT)"
fin=0; unreach=0
for i in $(seq 1 ${WAIT_MIN:-120}); do
  ssh $K $H "test -f ~/aftershock-artifacts/runs/$RID/checks.json"; rc=$?
  if (( rc == 0 )); then fin=1; echo "DONE $RID"; break; fi
  if (( rc == 255 )); then unreach=$((unreach + 1)); sleep 60; continue; fi
  unreach=0
  ssh $K $H "tmux has-session -t run 2>/dev/null"; rc=$?
  if (( rc == 1 )); then
    for j in 1 2 3 4 5 6; do sleep 20; if ssh $K $H "test -f ~/aftershock-artifacts/runs/$RID/checks.json"; then fin=1; break; fi; done
    (( fin )) && { echo "DONE $RID (after tmux ended)"; break; }
    echo "TMUX GONE, no checks.json: $RID. $ALLOWED"; exit 3
  fi
  sleep 60
done
if (( ! fin )); then
  (( unreach >= 3 )) && { echo "VM NOT REACHABLE for the last $unreach reads; $RID unknown. $ALLOWED"; exit 7; }
  echo "STILL RUNNING $RID after ${WAIT_MIN:-120} min. $ALLOWED"; exit 5
fi
exit 0
