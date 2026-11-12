#!/bin/zsh
# GPU watcher (docs/FABLE_PROMPT.md §7). launchd runs it every 15 minutes; it only reads the VM.
# States: down | up_nogpu | up_busy (a compute process that is not our run) | up_ours (our tmux session "run") | up_idle.
# up_idle writes agent/GPU_AVAILABLE with a timestamp; any other state moves that file to agent/run/GPU_AVAILABLE.last.
# Only state changes are logged (agent/run/gpu_watch.log). On a change to up_idle it calls resume.sh, which starts a
# headless agent session only if no Claude session is alive in this repo.
# Test without the VM: GPU_WATCH_FAKE=<file holding the remote command's output> zsh agent/bin/gpu_watch.sh
export PATH=$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
R=/Users/chalshik/Projects/aftershock-artifacts
A=${GPU_WATCH_DIR:-$R/agent}; RUN=$A/run; mkdir -p $RUN
K=(-i $HOME/.ssh/id_ed25519_vllm -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=5 -o ServerAliveCountMax=2)
REMOTE='nvidia-smi --query-gpu=name,power.limit,temperature.gpu,utilization.gpu,memory.used --format=csv,noheader 2>&1; echo "#apps"; nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader 2>&1; echo "#tmux"; tmux ls 2>&1 | head -5; echo "#tree"; cd ~/aftershock-artifacts 2>/dev/null && git log -1 --format=%h 2>&1; echo "#end"'
state=down; host=""; detail=""
for h in ${=GPU_WATCH_HOSTS:-100.83.53.50 192.168.3.249}; do
  if [[ -n $GPU_WATCH_FAKE ]]; then out=$(cat $GPU_WATCH_FAKE); else out=$(ssh $K chalshik@$h "$REMOTE" 2>/dev/null) || continue; fi
  [[ $out == *"#end"* ]] || continue
  host=$h
  gpu=$(echo "$out" | sed -n 1p)
  apps=$(echo "$out" | sed -n '/^#apps$/,/^#tmux$/p' | grep -v '^#' | grep -c '[0-9]')
  ours=$(echo "$out" | sed -n '/^#tmux$/,/^#tree$/p' | grep -c '^run:')
  tree=$(echo "$out" | sed -n '/^#tree$/,/^#end$/p' | grep -v '^#' | head -1)
  if [[ $gpu != *"RTX 3090"* ]]; then state=up_nogpu
  elif (( ours > 0 )); then state=up_ours
  elif (( apps > 0 )); then state=up_busy
  else state=up_idle; fi
  detail="gpu=[$gpu] apps=$apps tree=$tree"
  break
done
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
prev=$(cat $RUN/gpu_watch.state 2>/dev/null || echo none)
echo $state > $RUN/gpu_watch.state
echo "$now $state host=$host $detail" > $RUN/gpu_watch.last
if [[ $state == up_idle ]]; then
  echo "$now host=$host $detail" > $A/GPU_AVAILABLE
else
  [[ -f $A/GPU_AVAILABLE ]] && mv -f $A/GPU_AVAILABLE $RUN/GPU_AVAILABLE.last
fi
if [[ $state != $prev ]]; then
  echo "$now $prev -> $state host=$host $detail" >> $RUN/gpu_watch.log
  if [[ $state == up_idle && -z $GPU_WATCH_FAKE ]]; then zsh $R/agent/bin/resume.sh gpu & fi
fi
exit 0
