# Shared, fixed settings of the REG-19 resume scripts (decisions.md 2026-11-13 [DECISION] (delegate), REG-19 resume).
# Nothing here is read from the environment except VM_HOST and WAIT_MIN; a stray PIN or path variable cannot move a check.
R=/Users/chalshik/Projects/aftershock-artifacts
S=$R/docs/probe/20261113_reg19/ops
PROBE_DIR=$R/docs/probe/20261113_reg19
W=/Users/chalshik/Projects/aftershock-reg19-pin
PIN=a7bb77abc863adcaad9d4516815a5ddddf2908e9
PY=$R/.venv/bin/python
H=chalshik@${VM_HOST:-100.83.53.50}
K=(-i $HOME/.ssh/id_ed25519_vllm -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=4)
MIN_FREE_KB=2097152                      # 2 GB free on the VM before a launch (about 240 MB per run)
SCRIPTS=(common.sh session_probe.sh launch8.sh queue_reg19f.sh)
CONTROL_PAT='*_stage2_control_l1pl350cl_r2.0_w3000_s1[5-9]'
BURST_PAT='*_burst_l1pl350cl_r2.0_w3000_s1[5-9]'

# Mac-side checks common to every step: worktree at the pin and clean; the pin an ancestor of HEAD; the files the queue
# uses from the working tree (manifest tool, lock files) equal to the pin's; these scripts equal to their committed text.
mac_checks() {
  cd $R || return 2
  [[ $(git -C $W rev-parse HEAD) == $PIN ]] || { echo "STOP: worktree $W is not at $PIN"; return 2; }
  [[ -z $(git -C $W status --short) ]] || { echo "STOP: worktree $W is dirty"; return 2; }
  git merge-base --is-ancestor $PIN HEAD || { echo "STOP: pin is not an ancestor of the Mac HEAD"; return 2; }
  git diff --quiet $PIN -- tools/manifest.py pyproject.toml uv.lock || { echo "STOP: tools/manifest.py, pyproject.toml or uv.lock differ from the pin in the working tree"; return 2; }
  git diff --quiet HEAD -- ${SCRIPTS[@]/#/docs/probe/20261113_reg19/ops/} || { echo "STOP: a resume script differs from its committed text"; return 2; }
  SC=$(git log -1 --format=%H -- ${SCRIPTS[@]/#/docs/probe/20261113_reg19/ops/})
  [[ -n $SC ]] || { echo "STOP: the resume scripts are not committed"; return 2; }
  if [[ -f $S/scripts_commit.txt ]]; then
    [[ $(cat $S/scripts_commit.txt) == $SC ]] || { echo "STOP: scripts changed since scripts_commit.txt ($SC)"; return 2; }
  fi
  return 0
}

# Every REG-19 run folder on the Mac is linked into the worktree, resolves to the Mac's folder, and nothing else is there.
links_ok() {
  local ids n_w=0 id
  ids=($R/runs/${~CONTROL_PAT}(N/:t) $R/runs/${~BURST_PAT}(N/:t))
  for id in $ids; do
    [[ -L $W/runs/$id ]] || ln -s $R/runs/$id $W/runs/$id || { echo "STOP: could not link $id"; return 2; }
    [[ $W/runs/$id(:A) == $R/runs/$id(:A) ]] || { echo "STOP: $W/runs/$id does not resolve to $R/runs/$id"; return 2; }
  done
  for id in $W/runs/*(N:t); do
    n_w=$((n_w + 1))
    [[ ${ids[(Ie)$id]} -gt 0 ]] || { echo "STOP: $W/runs holds $id, which is not a REG-19 run folder on the Mac"; return 2; }
  done
  [[ $n_w == ${#ids} ]] || { echo "STOP: $n_w entries in $W/runs against ${#ids} REG-19 folders"; return 2; }
  return 0
}
