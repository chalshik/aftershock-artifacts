#!/bin/zsh
# Pre-launch checks and launch of one E1 invocation on the VM, then wait until it ends (copied from ops_r3/launch.sh;
# DESIGN_NOTES.md lists the differences).
# Usage: zsh launch.sh sweep        the one harness invocation of configs/sweep_l1pl350cl_pc_off.yaml (six rates)
#        zsh launch.sh <rate>       one rate from configs/sweep_l1pl350cl_pc_off_only_r<rate>.yaml
# (called by queue.sh). By hand it applies the queue's own rules and no fewer: it launches only what `next_step`
# (common.sh) says is next, with the attempt number it derives, so a launch by hand can pass neither E1's stopping
# rule nor a pending settle or copy. It changes nothing on the VM but starting the run: the power limit is read, never
# set (a limit other than 350.00 W stops), and the tree is checked, never moved. The pre-launch read goes to a
# time-stamped probe file; a stop before the launch spends no attempt. The attempt record (state/attempt_sweep_1.txt or
# state/attempt_r<rate>_<n>.txt) is written immediately before the launch command, so from that line on the attempt
# is spent whatever happens. Exit codes: 2 a check failed, nothing launched (or the launch command itself failed,
# attempt spent); 4 no run id in the log in time; 5 still running after the wait; 7 the VM stopped answering.
# Exit 0 means only that the invocation has ended (the tmux session is gone); the queue then reads, from the launch
# log, the run_id lines and, from each run's checks.json, `valid` and `failed`. Nothing else is read.
source ${0:A:h}/common.sh
die() { echo "STOP: $1"; echo "$ALLOWED"; exit ${2:-2}; }
mac_checks || die "$MSG"
ready_to_run || die "$MSG"
WHAT=$1
[[ $WHAT == sweep || ${RATES[(Ie)$WHAT]} -gt 0 ]] || die "'$WHAT' is neither 'sweep' nor one of E1's rates (${RATES[*]})"
if [[ $WHAT == sweep ]]; then WAIT=${WAIT_MIN:-$SWEEP_WAIT_MIN}; else WAIT=${WAIT_MIN:-$RATE_WAIT_MIN}; fi
[[ $WAIT == <-> ]] || die "WAIT_MIN is not a number"
[[ -s $ST/session_boot_id.txt ]] || die "no session probe (run session_probe.sh first)"
next_step || die "$MSG"
[[ $ACT == launch && $ARG == $WHAT ]] || die "it is not the turn of '$WHAT': the next step is '$ACT $ARG' (the queue settles, copies and launches in E1's order)"
ATT=$NEXT_ATT
if [[ $WHAT == sweep ]]; then CFG=$SWEEP; FRATE=$RATES[1]; MARK=$ST/attempt_sweep_1.txt
else CFG=$ONLY$WHAT; FRATE=$WHAT; MARK=$ST/attempt_r${WHAT}_$ATT.txt; fi
LOCKB=$(git -C $R rev-parse ${E1}:uv.lock) || die "uv.lock cannot be read at the registered commit"
stamp; ts=$REPLY
PROBE=$PROBE_DIR/prelaunch_e1_${CFG}_$ts.txt; LOG="~/e1_${CFG}_$ts.log"
[[ ! -e $PROBE ]] || die "probe $PROBE exists"
for i in $(seq 1 $TEMP_TRIES); do
  T=$(ssh $K $H "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader") || die "the VM could not be read (temperature)"
  [[ $T == <-> ]] || die "the temperature read '$T' is not a number"
  (( T <= TEMP_MAX_C )) && break
  sleep $TEMP_SLEEP_S
done
ssh $K $H "echo '# pre-launch read for E1 $WHAT attempt $ATT (agent, read-only; scripts $SC)'; date -Is; nvidia-smi --query-gpu=power.limit,temperature.gpu,utilization.gpu,memory.used --format=csv; echo '# compute apps:'; nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader; echo '# tree:'; cd ~/aftershock-artifacts && git rev-parse HEAD && git status --short | wc -l; echo '# lock:'; git hash-object uv.lock; echo '# boot:'; cat /proc/sys/kernel/random/boot_id; echo '# free_kb:'; df -k --output=avail ~ | tail -1; echo '# tmux:'; tmux ls 2>&1 || true" > $PROBE || die "the pre-launch read failed"
cat $PROBE
LIM=$(sed -n 4p $PROBE | cut -d, -f1 | tr -d ' W'); TEMP=$(sed -n 4p $PROBE | cut -d, -f2 | tr -d ' ')
APPS=$(sed -n '/# compute apps:/,/# tree:/p' $PROBE | grep -vc '^#')
VMH=$(sed -n '/# tree:/{n;p;}' $PROBE); DIRTY=$(sed -n '/# tree:/{n;n;p;}' $PROBE | tr -d ' ')
VML=$(sed -n '/# lock:/{n;p;}' $PROBE)
BOOT=$(sed -n '/# boot:/{n;p;}' $PROBE); FREE=$(sed -n '/# free_kb:/{n;p;}' $PROBE | tr -d ' ')
[[ $LIM == $LIMIT_W ]] || die "power limit '$LIM' (read, never set here: the owner sets $LIMIT_W W)"
[[ $TEMP == <-> ]] && (( TEMP <= TEMP_MAX_C )) || die "GPU at '$TEMP' C"
[[ $APPS == 0 ]] || die "GPU compute process present"
[[ $VMH == $E1 && $DIRTY == 0 ]] || die "VM tree '$VMH' dirty='$DIRTY', registered commit $E1 (only vm_checkout.sh moves it, with the owner's approval)"
[[ $VML == $LOCKB ]] || die "the VM's uv.lock '$VML' is not the registered commit's ($LOCKB)"
[[ -n $BOOT && $BOOT == $(<$ST/session_boot_id.txt) ]] || die "the VM rebooted since the session probe (boot id '$BOOT')"
[[ $FREE == <-> ]] && (( FREE >= MIN_FREE_KB )) || die "only '$FREE' kB free on the VM"
sed -n '/# tmux:/,$p' $PROBE | grep -q "no server running\|No such file or directory\|error connecting" || die "a tmux session exists"
[[ ! -e $MARK ]] || die "$MARK exists"
print -r -l -- "attempt $ATT of $WHAT (configs/$CFG.yaml)" "time $(date -u +%Y-%m-%dT%H:%M:%SZ)" "scripts $SC" "commit $E1" "probe ${PROBE:t}" "boot $BOOT" "log $LOG" > $MARK || die "the attempt record could not be written; nothing launched"
ssh $K $H "cd ~/aftershock-artifacts && tmux new-session -d -s run \"~/.local/bin/uv run python -m harness.run configs/$CFG.yaml > $LOG 2>&1\"" || { echo "launch_command_failed" >> $MARK; die "the launch command failed; attempt $ATT of $WHAT is recorded as spent"; }
RID=""
for i in $(seq 1 $RID_TRIES); do
  sleep $RID_SLEEP_S
  RID=$(ssh $K $H "grep -m1 -o \"'run_id': '[^']*'\" $LOG 2>/dev/null | cut -d\"'\" -f4")
  [[ -n $RID ]] && break
done
[[ -n $RID && $(rate_of $RID) == $FRATE ]] || die "no run id of rate $FRATE in $LOG after $((RID_TRIES * RID_SLEEP_S)) s (read '$RID'); the tmux session 'run' may still be alive" 4
echo "LAUNCHED $RID (attempt $ATT of $WHAT)"
unreach=0
for i in $(seq 1 $WAIT); do
  ssh $K $H "tmux has-session -t run 2>/dev/null"; rc=$?
  case $rc in
    1) echo "ENDED $WHAT attempt $ATT (the tmux session is gone)"; exit 0;;
    0) unreach=0;;
    255) unreach=$((unreach + 1))
         (( unreach < UNREACH_MAX )) || die "VM NOT REACHABLE for the last $unreach reads; the invocation of $WHAT (attempt $ATT) is unknown" 7;;
    *) die "the tmux read gave rc $rc";;
  esac
  sleep $POLL_S
done
die "STILL RUNNING: the invocation of $WHAT (attempt $ATT) after $WAIT min" 5
