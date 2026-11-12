#!/bin/zsh
# Pre-launch checks and launch of one REG-19 config on the VM; then wait for its checks.json.
# Usage: PROBE_DIR=<dir> zsh launch7.sh <config-name-without-.yaml> <probe-file-name>
# launch7 (decisions.md 2026-11-13 [DECISION] (delegate), REG-19 resume) = launch6 with three changes:
#  1. Pin rule. The VM must be clean at PIN, as before. The Mac-side rule of launch6 (what may differ between PIN and
#     the Mac's HEAD) is replaced: every REG-19 computation on the Mac (reg19_step, reg19) runs from a git worktree
#     checked out at PIN, so the Mac's HEAD no longer enters REG-19. Checked here: the worktree is at PIN and clean,
#     PIN is an ancestor of HEAD, and tools/manifest.py (used from HEAD for the checksum manifest) is unchanged since PIN.
#  2. Power limit. The agent sets 350 W itself (sudo -n nvidia-smi -pl 350, the one root command the owner allowed,
#     decisions.md 2026-11-13 [DECISION]) and reads it back. If sudo -n fails, STOP (exit 4).
#  3. The read is written to PROBE_DIR (docs/probe/20261113_reg19/).
set -e
cd /Users/chalshik/Projects/aftershock-artifacts
K=(-i $HOME/.ssh/id_ed25519_vllm -o BatchMode=yes -o ConnectTimeout=10)
H=chalshik@${VM_HOST:-100.83.53.50}
W=${REG19_WORKTREE:-/Users/chalshik/Projects/aftershock-reg19-pin}
CFG=$1; PROBE=${PROBE_DIR}/$2; mkdir -p ${PROBE_DIR}; LOG="~/${CFG}_$(date -u +%Y%m%dT%H%M%SZ).log"
MAC=$(git rev-parse --short HEAD)
PIN=${PIN:-a7bb77a}
[[ $(git -C $W rev-parse --short HEAD) == $PIN ]] || { echo "STOP: worktree $W is not at $PIN"; exit 2; }
[[ -z $(git -C $W status --short) ]] || { echo "STOP: worktree $W is dirty"; exit 2; }
git merge-base --is-ancestor $PIN HEAD || { echo "STOP: $PIN is not an ancestor of the Mac HEAD"; exit 2; }
git diff --quiet $PIN HEAD -- tools/manifest.py || { echo "STOP: tools/manifest.py changed since $PIN"; exit 2; }
[[ -f $W/configs/$CFG.yaml ]] || { echo "STOP: no config $CFG at $PIN"; exit 2; }
ssh $K $H "sudo -n nvidia-smi -pl 350 >/dev/null" || { echo "STOP: sudo -n nvidia-smi -pl 350 failed"; exit 4; }
for i in $(seq 1 60); do
  T=$(ssh $K $H "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader")
  (( T <= 45 )) && break
  sleep 30
done
ssh $K $H "echo '# pre-launch read for $CFG (agent; power limit set by the agent with sudo -n nvidia-smi -pl 350)'; date -Is; nvidia-smi --query-gpu=power.limit,temperature.gpu,utilization.gpu,memory.used --format=csv; echo '# compute apps:'; nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader; echo '# tree:'; cd ~/aftershock-artifacts && git log -1 --format=%h && git status --short | wc -l; df -h ~ | tail -1; tmux ls 2>&1 || true" > $PROBE
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
