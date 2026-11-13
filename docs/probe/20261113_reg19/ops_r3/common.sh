# Shared, fixed settings and functions of the REG-19 resume scripts, third version (after the round-2 rule F review,
# docs/drafts/reviews-2026-11-13/rulef-reg19-resume-r2.md). Read from the environment: VM_HOST and WAIT_MIN only
# (session_probe.sh also reads SET and RENEW). No seed, attempt number or run id is typed by anyone: the queue derives
# them from the attempt records in state/ and from what the VM's run folders say.
R=/Users/chalshik/Projects/aftershock-artifacts
S=$R/docs/probe/20261113_reg19/ops_r3
ST=$S/state
PROBE_DIR=$R/docs/probe/20261113_reg19
W=/Users/chalshik/Projects/aftershock-reg19-pin
PIN=a7bb77abc863adcaad9d4516815a5ddddf2908e9
PY=$R/.venv/bin/python
H=chalshik@${VM_HOST:-100.83.53.50}
K=(-i $HOME/.ssh/id_ed25519_vllm -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=4)
MIN_FREE_KB=2097152                      # 2 GB free on the VM before a launch (about 240 MB per run)
MAX_ATTEMPTS=3                           # REG-19: a run once, rerun unchanged at most twice
SEEDS=(18 19)                            # the seeds left, in the registered order; not settable
DRIVER=595.99.02                         # the pinned driver (PROTOCOL.md, section 4, Software)
RECHECK_PAT='*_l1pl350cl_r2.0_w3000_s1[5-9]'   # REG-19's runs, both kinds, for analysis.recheck
CHECKS_COMMIT=5ee6e38d3a15994da8bb6597b9b13ea8be08807c    # harness/checks.py as of this commit (the checks in force, A14)
RECHECK_COMMIT=72fafb5991e036eddf1c4ce40b39bc1ca81fa74e   # analysis/recheck.py as of this commit
SCRIPTS=(common.sh vm_state.py session_probe.sh launch.sh queue.sh final.sh)
CONTROL_PAT='*_stage2_control_l1pl350cl_r2.0_w3000_s1[5-9]'
BURST_PAT='*_burst_l1pl350cl_r2.0_w3000_s1[5-9]'
ALLOWED="Allowed reads while diagnosing a stop: 'tmux has-session -t run'; the folder names under runs/; a run's checks.json (valid, failed); in a launch log only the lines holding 'run_id' or '[run] checks'. Nothing else of a log or a run folder (REG-19: no interim look)."

# File-name stamp: UTC time plus the process id, so two starts in one second never share a name.
stamp() { print -r -- "$(date -u +%Y%m%dT%H%M%SZ)_$$"; }

# Mac-side checks before every launch, step and table: worktree at the pin and clean; the pin an ancestor of HEAD; the
# files used from the Mac's working tree (manifest tool, lock files) equal to the pin's; these scripts tracked, equal to
# their committed text, and that commit the one recorded in scripts_commit.txt. Sets SC.
mac_checks() {
  local st p paths
  cd $R || { echo "STOP: no repo at $R"; return 2; }
  [[ $(git -C $W rev-parse HEAD 2>/dev/null) == $PIN ]] || { echo "STOP: worktree $W is not at $PIN"; return 2; }
  st=$(git -C $W status --short) || { echo "STOP: git status failed in $W"; return 2; }
  [[ -z $st ]] || { echo "STOP: worktree $W is dirty"; return 2; }
  git merge-base --is-ancestor $PIN HEAD || { echo "STOP: the pin is not an ancestor of the Mac HEAD"; return 2; }
  git diff --quiet $PIN -- tools/manifest.py pyproject.toml uv.lock || { echo "STOP: tools/manifest.py, pyproject.toml or uv.lock differ from the pin in the working tree"; return 2; }
  paths=(${SCRIPTS[@]/#/docs/probe/20261113_reg19/ops_r3/})
  for p in $paths; do
    git ls-files --error-unmatch $p > /dev/null 2>&1 || { echo "STOP: $p is not tracked by git"; return 2; }
  done
  git diff --quiet HEAD -- $paths || { echo "STOP: a resume script differs from its committed text"; return 2; }
  SC=$(git log -1 --format=%H -- $paths)
  [[ -n $SC ]] || { echo "STOP: the resume scripts are not committed"; return 2; }
  [[ -f $S/scripts_commit.txt ]] || { echo "STOP: no scripts_commit.txt"; return 2; }
  [[ $(<$S/scripts_commit.txt) == $SC ]] || { echo "STOP: the scripts changed since scripts_commit.txt (now $SC)"; return 2; }
  return 0
}

# Every REG-19 run folder on the Mac is linked into the worktree, each link resolves to the Mac's folder, and nothing
# else is in the worktree's runs/. A link is made only where nothing exists at its path; nothing is written elsewhere.
links_ok() {
  local ids n_w=0 id lw lr
  [[ -d $W/runs && ! -L $W/runs ]] || { echo "STOP: $W/runs is not a real directory"; return 2; }
  ids=($R/runs/${~CONTROL_PAT}(N/:t) $R/runs/${~BURST_PAT}(N/:t))
  for id in $ids; do
    lw=$W/runs/$id; lr=$R/runs/$id
    if [[ ! -e $lw && ! -L $lw ]]; then ln -s $lr $lw || { echo "STOP: could not link $id"; return 2; }; fi
    [[ -L $lw ]] || { echo "STOP: $lw exists and is not a link"; return 2; }
    [[ ${lw:A} == ${lr:A} ]] || { echo "STOP: $lw does not resolve to $lr"; return 2; }
  done
  for id in $W/runs/*(N:t); do
    n_w=$((n_w + 1))
    [[ ${ids[(Ie)$id]} -gt 0 ]] || { echo "STOP: $W/runs holds $id, which is not a REG-19 run folder on the Mac"; return 2; }
  done
  [[ $n_w == ${#ids} ]] || { echo "STOP: $n_w entries in $W/runs against ${#ids} REG-19 folders"; return 2; }
  return 0
}

# What the VM holds for one config: one line per run folder, "<run id> valid|invalid|nochecks|unreadable <failed|->".
# Read-only: vm_state.py is sent on stdin and reads folder names and the `valid` and `failed` fields of checks.json.
vm_state() {
  local out
  VMS=()
  out=$(ssh $K $H "python3 - $1" < $S/vm_state.py) || return 1
  [[ ${out##*$'\n'} == "END $1" ]] || return 1
  VMS=("${(@f)out}"); VMS=(${VMS[1,-2]})
  return 0
}

# REG-19's rerun rule for one config, from the attempt records and the VM's checks.json files only. Returns 0 with
# RID set (one valid run exists: use it, launch nothing) or with LAUNCH set (the number of the attempt to launch);
# returns 2 with MSG set when the registration stops the queue.
#   - every launch is one attempt, whatever it left behind; at most MAX_ATTEMPTS attempts of a config;
#   - a run folder on the VM without an attempt record stops the queue (a launch outside these scripts);
#   - no rerun after `no_errors` (a client error), `manipulation` (the burst did not fill the pool) or `power_limit`
#     (a limit other than 350 W); one rerun after `gpu_steady` (heat), a second heat failure stops the queue;
#   - a run folder without checks.json (a lost run) is not rerun unless a decision allows it, recorded as
#     state/lost_ok_<run id>.txt. The record for seed 18's control of 2026-11-12 is committed with these scripts.
decide() {
  local cfg=$1 line parts f n_valid=0 n_heat=0 norerun="" bad="" lost="" atts
  RID=""; LAUNCH=""; MSG=""
  vm_state $cfg || { MSG="the VM's run folders of $cfg could not be read"; return 2; }
  for line in $VMS; do
    parts=(${=line})
    case $parts[2] in
      valid) n_valid=$((n_valid + 1)); RID=$parts[1];;
      invalid)
        for f in ${(s:,:)parts[3]}; do
          case $f in
            no_errors|manipulation|power_limit) norerun="$f ($parts[1])";;
            gpu_steady) n_heat=$((n_heat + 1));;
          esac
        done;;
      nochecks) [[ -f $ST/lost_ok_$parts[1].txt ]] || lost=$parts[1];;
      *) bad=$parts[1];;
    esac
  done
  atts=($ST/attempt_${cfg}_<->.txt(N))
  [[ -z $bad ]] || { RID=""; MSG="checks.json of $bad cannot be read"; return 2; }
  (( n_valid <= 1 )) || { RID=""; MSG="the VM holds $n_valid valid runs of $cfg: the owner decides"; return 2; }
  (( ${#VMS} <= ${#atts} )) || { RID=""; MSG="the VM holds ${#VMS} run folders of $cfg and only ${#atts} attempts are recorded in $ST"; return 2; }
  (( n_valid == 1 )) && return 0
  [[ -z $norerun ]] || { MSG="REG-19 registers no rerun after $norerun: the owner decides"; return 2; }
  [[ -z $lost ]] || { MSG="$lost has no checks.json (lost or still running): a rerun needs its own decision, recorded as $ST/lost_ok_$lost.txt"; return 2; }
  (( n_heat < 2 )) || { MSG="second heat failure (gpu_steady) of $cfg: REG-19 stops the queue"; return 2; }
  (( ${#atts} < MAX_ATTEMPTS )) || { MSG="the $MAX_ATTEMPTS attempts of $cfg are spent: operational stop, no table, the owner decides"; return 2; }
  LAUNCH=$((${#atts} + 1))
  [[ ! -e $ST/attempt_${cfg}_$LAUNCH.txt ]] || { MSG="attempt records of $cfg are not numbered 1..${#atts}"; LAUNCH=""; return 2; }
  return 0
}
