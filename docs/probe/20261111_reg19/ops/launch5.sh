#!/bin/zsh
# Pre-launch checks (REG-9/REG-10 Operations) and launch of one config on the VM; then wait for its checks.json.
# Usage: launch.sh <config-name-without-.yaml> <probe-file-name>
# Waits (up to 30 min) for the GPU to be idle at <= 45 C; refuses on any other failed check. Writes the read to the probe.
set -e
cd /Users/chalshik/Projects/aftershock-artifacts
K=(-i $HOME/.ssh/id_ed25519_vllm -o ConnectTimeout=10)
H=chalshik@100.83.53.50
CFG=$1; PROBE=${PROBE_DIR}/$2; mkdir -p ${PROBE_DIR}; LOG="~/${CFG}_$(date -u +%Y%m%dT%H%M%SZ).log"
MAC=$(git rev-parse --short HEAD)
# launch5 = launch4 + recheck checks.json for ~2 min before declaring a run lost (2026-11-12 race over a slow link).
# launch4 (owner 2026-11-12): the VM stays pinned at PIN (no pull); the Mac may be ahead of PIN only in docs/, PROTOCOL.md and (owner, 2026-11-12) CLAUDE.md.
PIN=${PIN:-a7bb77a}
NONDOC=$(git diff --name-only $PIN HEAD | grep -v '^docs/' | grep -v '^PROTOCOL.md$' | grep -v '^CLAUDE.md$' || true)
[[ -z $NONDOC ]] || { echo "STOP: Mac differs from $PIN outside docs: $NONDOC"; exit 2; }
git merge-base --is-ancestor $PIN HEAD || { echo "STOP: $PIN is not an ancestor of the Mac HEAD"; exit 2; }
for i in $(seq 1 60); do
  T=$(ssh $K $H "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader")
  (( T <= 45 )) && break
  sleep 30
done
ssh $K $H "echo '# pre-launch read for $CFG (agent, read-only)'; date -Is; nvidia-smi --query-gpu=power.limit,temperature.gpu,utilization.gpu,memory.used --format=csv; echo '# compute apps:'; nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader; echo '# tree:'; cd ~/aftershock-artifacts && git log -1 --format=%h && git status --short | wc -l; df -h ~ | tail -1; tmux ls 2>&1 || true" > $PROBE
cat $PROBE
LIM=$(sed -n 4p $PROBE | cut -d, -f1 | tr -d ' W'); TEMP=$(sed -n 4p $PROBE | cut -d, -f2 | tr -d ' ')
APPS=$(sed -n '/# compute apps:/,/# tree:/p' $PROBE | grep -vc '^#' || true)
VMH=$(sed -n '/# tree:/{n;p;}' $PROBE); DIRTY=$(sed -n '/# tree:/{n;n;p;}' $PROBE | tr -d ' ')
[[ $LIM == "350.00" ]] || { echo "STOP: power limit $LIM"; exit 2; }
(( TEMP <= 45 )) || { echo "STOP: GPU at $TEMP C"; exit 2; }
[[ $APPS == 0 ]] || { echo "STOP: GPU compute process present"; exit 2; }
[[ $VMH == $PIN && $DIRTY == 0 ]] || { echo "STOP: VM tree $VMH dirty=$DIRTY, pin $PIN (Mac $MAC)"; exit 2; }
grep -q "tmux-1000/default\|no server running" $PROBE || { echo "STOP: a tmux session exists"; exit 2; }
ssh $K $H "cd ~/aftershock-artifacts && tmux new-session -d -s run \"~/.local/bin/uv run python -m harness.run configs/$CFG.yaml > $LOG 2>&1\" && sleep 15 && grep -m1 run_id $LOG"
RID=$(ssh $K $H "grep -m1 -o \"'run_id': '[^']*'\" $LOG | cut -d\"'\" -f4")
echo "LAUNCHED $RID"
for i in $(seq 1 ${WAIT_MIN:-120}); do
  ssh $K $H "test -f ~/aftershock-artifacts/runs/$RID/checks.json" && { echo "DONE $RID"; break; } || true
  rc=0; ssh $K $H "tmux has-session -t run 2>/dev/null" || rc=$?; (( rc == 1 )) && { for j in 1 2 3 4 5 6; do sleep 20; ssh $K $H "test -f ~/aftershock-artifacts/runs/$RID/checks.json" && break; done; ssh $K $H "test -f ~/aftershock-artifacts/runs/$RID/checks.json" && { echo "DONE $RID (after tmux ended)"; break; }; echo "TMUX GONE, no checks.json: $RID"; exit 3; }
  sleep 60
done
ssh $K $H "grep 'checks' $LOG | tail -1"
