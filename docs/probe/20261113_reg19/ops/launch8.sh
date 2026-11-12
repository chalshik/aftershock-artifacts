#!/bin/zsh
# Pre-launch checks and launch of one REG-19 config on the VM; then wait for its checks.json.
# Usage: zsh launch8.sh <config-name-without-.yaml> <probe-file-name>
# launch8 = launch6's checks with: the pin rule of the resume decision (common.sh `mac_checks`); NO power-limit set
# (a limit other than 350.00 W stops the queue, as REG-19 registers; the set is session_probe.sh's, once); the VM's
# boot id compared with the session's; free disk checked; an existing probe never overwritten; the run id awaited for
# up to 120 s; a wait that ends with the run still going reported as such, not as invalid.
# Exit codes: 2 a check failed; 3 the run's tmux session ended without checks.json; 4 no run id; 5 still running.
source ${0:A:h}/common.sh
set -e
mac_checks
CFG=$1; PROBE=$PROBE_DIR/$2; LOG="~/${CFG}_$(date -u +%Y%m%dT%H%M%SZ).log"
[[ -n $CFG && -n $2 ]] || { echo "STOP: usage"; exit 2; }
[[ -f $W/configs/$CFG.yaml ]] || { echo "STOP: no config $CFG at the pin"; exit 2; }
[[ ! -e $PROBE ]] || { echo "STOP: probe $PROBE exists; a launch never overwrites one"; exit 2; }
[[ -f $S/session_boot_id.txt ]] || { echo "STOP: no session probe (run session_probe.sh first)"; exit 2; }
for i in $(seq 1 60); do
  T=$(ssh $K $H "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader")
  (( T <= 45 )) && break
  sleep 30
done
ssh $K $H "echo '# pre-launch read for $CFG (agent, read-only; scripts $SC)'; date -Is; nvidia-smi --query-gpu=power.limit,temperature.gpu,utilization.gpu,memory.used --format=csv; echo '# compute apps:'; nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader; echo '# tree:'; cd ~/aftershock-artifacts && git rev-parse HEAD && git status --short | wc -l; echo '# boot:'; cat /proc/sys/kernel/random/boot_id; echo '# free_kb:'; df -k --output=avail ~ | tail -1; echo '# tmux:'; tmux ls 2>&1 || true" > $PROBE
cat $PROBE
LIM=$(sed -n 4p $PROBE | cut -d, -f1 | tr -d ' W'); TEMP=$(sed -n 4p $PROBE | cut -d, -f2 | tr -d ' ')
APPS=$(sed -n '/# compute apps:/,/# tree:/p' $PROBE | grep -vc '^#' || true)
VMH=$(sed -n '/# tree:/{n;p;}' $PROBE); DIRTY=$(sed -n '/# tree:/{n;n;p;}' $PROBE | tr -d ' ')
BOOT=$(sed -n '/# boot:/{n;p;}' $PROBE); FREE=$(sed -n '/# free_kb:/{n;p;}' $PROBE | tr -d ' ')
[[ $LIM == "350.00" ]] || { echo "STOP: power limit $LIM"; exit 2; }
(( TEMP <= 45 )) || { echo "STOP: GPU at $TEMP C"; exit 2; }
[[ $APPS == 0 ]] || { echo "STOP: GPU compute process present"; exit 2; }
[[ $VMH == $PIN && $DIRTY == 0 ]] || { echo "STOP: VM tree $VMH dirty=$DIRTY, pin $PIN"; exit 2; }
[[ $BOOT == $(cat $S/session_boot_id.txt) ]] || { echo "STOP: the VM rebooted since the session probe (boot id $BOOT)"; exit 2; }
(( FREE >= MIN_FREE_KB )) || { echo "STOP: only $FREE kB free on the VM"; exit 2; }
sed -n '/# tmux:/,$p' $PROBE | grep -q "no server running\|No such file or directory\|error connecting" || { echo "STOP: a tmux session exists"; exit 2; }
ssh $K $H "cd ~/aftershock-artifacts && tmux new-session -d -s run \"~/.local/bin/uv run python -m harness.run configs/$CFG.yaml > $LOG 2>&1\""
RID=""
for i in $(seq 1 24); do
  sleep 5
  RID=$(ssh $K $H "grep -m1 -o \"'run_id': '[^']*'\" $LOG 2>/dev/null | cut -d\"'\" -f4" || true)
  [[ -n $RID ]] && break
done
[[ -n $RID ]] || { echo "STOP: no run id in $LOG after 120 s (the tmux session 'run' may still be alive: look before anything else)"; exit 4; }
echo "LAUNCHED $RID"
done=0
for i in $(seq 1 ${WAIT_MIN:-120}); do
  if ssh $K $H "test -f ~/aftershock-artifacts/runs/$RID/checks.json"; then done=1; echo "DONE $RID"; break; fi
  rc=0; ssh $K $H "tmux has-session -t run 2>/dev/null" || rc=$?
  if (( rc == 1 )); then
    for j in 1 2 3 4 5 6; do sleep 20; ssh $K $H "test -f ~/aftershock-artifacts/runs/$RID/checks.json" && { done=1; break; } || true; done
    (( done )) && { echo "DONE $RID (after tmux ended)"; break; }
    echo "TMUX GONE, no checks.json: $RID"; exit 3
  fi
  sleep 60
done
(( done )) || { echo "STILL RUNNING $RID after ${WAIT_MIN:-120} min"; exit 5; }
for j in 1 2 3; do ssh $K $H "grep 'checks' $LOG | tail -1" && break || sleep 10; done
