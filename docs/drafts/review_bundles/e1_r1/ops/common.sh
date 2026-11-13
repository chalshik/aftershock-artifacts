# Shared, fixed settings and functions of E1's operations scripts. Written 2026-11-13 by a teammate agent from REG-19's
# reviewed docs/probe/20261113_reg19/ops_r3/ (not changed), copied wherever E1 does not differ; DESIGN_NOTES.md lists
# every difference and every place where the registration (docs/drafts/e1_draft4.md, "Stopping rule" and "Pre-launch
# and launch") had to be read. Every parameter of the scripts is set here. Read from the environment: VM_HOST and
# WAIT_MIN only (session_probe.sh also reads SET and RENEW). Nobody types a rate, attempt number or run id: `next_step`
# derives them from the records in state/, the launch logs' run_id lines and the VM's run folders.
R=/Users/chalshik/Projects/aftershock-artifacts
REL=docs/probe/20261113_e1/ops                 # this folder, relative to the repo
S=$R/$REL
ST=$S/state
PROBE_DIR=$R/docs/probe/20261113_e1
COMMIT_FILE=$S/e1_commit.txt                   # the registered commit (the one that holds E1's approval), or UNSET
REG19_LOCK=$R/docs/probe/20261113_reg19/ops_r3/state/queue.lock   # tested for existence only; nothing there is opened
H=chalshik@${VM_HOST:-100.83.53.50}
K=(-i $HOME/.ssh/id_ed25519_vllm -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=4)
VM_GIT=${H}:repos/aftershock-artifacts.git       # the VM's bare repository (agent/RUNBOOK.md section 4); vm_checkout.sh only
SWEEP=sweep_l1pl350cl_pc_off                   # configs/$SWEEP.yaml; every E1 run is named <UTC %Y%m%d-%H%M%S>_${SWEEP}_r<rate>
RATES=(1.5 2 2.5 3 3.5 4)                      # as harness/run.py:36 writes them ({rate:g}), in the sweep's order
ONLY=${SWEEP}_only_r                           # + rate: the single-rate configs (a rate never started; a rerun)
MAX_ATTEMPTS=3                                 # E1: every launch of a rate is one attempt, at most three
HEAT=gpu_steady                                # E1: a heat failure is rerun once ...
MAX_HEAT=2                                     # ... and the second among E1's runs stops the queue
NORERUN=(no_errors power_limit)                # E1: a run failing either check stops the queue, no rerun
LIMIT_W=350.00                                 # read before every launch, never set by a launch
TEMP_MAX_C=45                                  # GPU temperature before every launch
TEMP_TRIES=60; TEMP_SLEEP_S=30                 # wait up to 30 min for it (ops_r3)
RID_TRIES=24; RID_SLEEP_S=5                    # the first run id must be in the launch log within 120 s (ops_r3)
POLL_S=60                                      # one read of the tmux session per minute while an invocation runs
UNREACH_MAX=15                                 # that many unanswered reads in a row: "VM NOT REACHABLE"
SWEEP_WAIT_MIN=240                             # the sweep: 6 x (900 + 300 + about 60 s) = 126 min (registration, Cost), with room
RATE_WAIT_MIN=60                               # one rate: about 21 min
MIN_FREE_KB=2097152                            # 2 GB free on the VM (an E1 run is about 70 MB: ops_r3's 240 MB per 4080 s run, scaled to 1200 s)
DRIVER=595.99.02                               # the pinned driver (PROTOCOL.md, section 4, Software)
MAX_TURNS=100                                  # turns of the queue's loop (E1 needs at most 6 x 3 x 3 + 2)
SCRIPTS=(common.sh vm_state.py session_probe.sh launch.sh queue.sh vm_checkout.sh)
END19_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · (\[RESULT\] REG-19([^0-9]|$)|\[OPS\] REG-19: the queue ended)'   # E1 draft 5: the queue's end, recorded, or REG-19's result
REG_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[REG\] E1([^0-9]|$)'
APPROVE_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[DECISION\] \((owner|delegate)\) E1 approved'
ALLOWED="Allowed reads while diagnosing a stop: 'tmux has-session -t run'; the folder names under runs/; a run's checks.json (valid, failed); in a launch log only the lines holding 'run_id' or '[run] checks'. Nothing else of a log or a run folder (E1: no interim look at any rate's throughput, KV or floor)."

# File-name stamp, left in REPLY (ops_r3): UTC time, process id and a count. Call it as `stamp`, never as $(stamp).
STAMP_N=0
stamp() { STAMP_N=$((STAMP_N + 1)); REPLY="$(date -u +%Y%m%dT%H%M%SZ)_$$_$STAMP_N"; }

# The registered commit, from e1_commit.txt, into E1. Returns 2 with MSG while the file says UNSET or holds anything
# but one full hash of a commit the Mac's repository has.
e1_commit() {
  local c
  E1=""
  [[ -f $COMMIT_FILE ]] || { MSG="no $COMMIT_FILE"; return 2; }
  c=$(<$COMMIT_FILE)
  [[ $c != UNSET ]] || { MSG="e1_commit.txt says UNSET: no E1 commit is registered, so nothing runs (it is set, in a commit of its own, to the commit that holds E1's approval)"; return 2; }
  [[ $c =~ '^[0-9a-f]{40}$' ]] || { MSG="e1_commit.txt holds '$c', not one full commit hash"; return 2; }
  git -C $R cat-file -e "${c}^{commit}" 2> /dev/null || { MSG="e1_commit.txt names $c, which is not a commit in $R"; return 2; }
  E1=$c
}

# At the registered commit, docs/decisions.md holds E1's [REG] heading and, on a later line, its approval.
approval_at_e1() {
  local log rl al
  log=$(git -C $R show ${E1}:docs/decisions.md 2> /dev/null) || { MSG="docs/decisions.md cannot be read at the registered commit $E1"; return 2; }
  rl=$(print -r -- "$log" | grep -n -E "$REG_PAT" | head -1 | cut -d: -f1)
  al=$(print -r -- "$log" | grep -n -E "$APPROVE_PAT" | tail -1 | cut -d: -f1)
  [[ -n $rl ]] || { MSG="no '[REG] E1' heading in docs/decisions.md at the registered commit $E1"; return 2; }
  [[ -n $al ]] || { MSG="no '[DECISION] (owner|delegate) E1 approved' heading in docs/decisions.md at the registered commit $E1 (it must be the commit that holds the approval)"; return 2; }
  (( al > rl )) || { MSG="E1's approval (line $al) is not after its [REG] heading (line $rl) at $E1"; return 2; }
  return 0
}

# Mac-side checks before anything: the registered commit set, on the Mac's HEAD, holding E1's registration and
# approval and all seven configs; the files used from the Mac's working tree (manifest tool, lock files) equal to that
# commit's; these scripts and e1_commit.txt tracked and equal to their committed text; the scripts unchanged since the
# registered commit (they are registered with E1). Sets E1 and SC (the last commit of the scripts), or MSG.
mac_checks() {
  local p c scr paths
  MSG=""; SC=""
  cd $R || { MSG="no repo at $R"; return 2; }
  e1_commit || return 2
  git merge-base --is-ancestor $E1 HEAD || { MSG="the registered commit $E1 is not an ancestor of the Mac's HEAD"; return 2; }
  approval_at_e1 || return 2
  for c in $SWEEP ${RATES[@]/#/$ONLY}; do
    git cat-file -e ${E1}:configs/$c.yaml 2> /dev/null || { MSG="no configs/$c.yaml at the registered commit $E1"; return 2; }
  done
  git diff --quiet $E1 -- tools/manifest.py pyproject.toml uv.lock || { MSG="tools/manifest.py, pyproject.toml or uv.lock differ in the Mac's working tree from the registered commit"; return 2; }
  scr=(${SCRIPTS[@]/#/$REL/}); paths=($scr $REL/e1_commit.txt)
  for p in $paths; do
    git ls-files --error-unmatch $p > /dev/null 2>&1 || { MSG="$p is not tracked by git"; return 2; }
  done
  git diff --quiet HEAD -- $paths || { MSG="a script or e1_commit.txt differs from its committed text"; return 2; }
  git diff --quiet $E1 HEAD -- $scr || { MSG="a script differs from its text at the registered commit $E1 (the scripts are registered with E1)"; return 2; }
  SC=$(git log -1 --format=%H -- $paths)
  [[ -n $SC ]] || { MSG="the scripts are not committed"; return 2; }
  return 0
}

# E1 runs after REG-19's queue has ended (registration draft 5, ID line): the committed log holds an [OPS] entry headed
# 'REG-19: the queue ended' (it quotes the queue's QUEUE DONE or QUEUE END line) or REG-19's [RESULT], and REG-19's queue
# lock does not exist. A QUEUE STOP leaves no such entry: REG-19 then waits for the owner, and E1 waits too.
ready_to_run() {
  MSG=""
  git -C $R grep -q -E "$END19_PAT" HEAD -- docs/decisions.md || { MSG="no '[OPS] REG-19: the queue ended' or '[RESULT] REG-19' heading in the committed docs/decisions.md: E1 runs after REG-19's queue has ended"; return 2; }
  [[ ! -e $REG19_LOCK && ! -L $REG19_LOCK ]] || { MSG="REG-19's queue lock exists ($REG19_LOCK; only its existence is tested): REG-19's queue may be running. If it has ended and left its lock, the owner decides"; return 2; }
  return 0
}

# The rate of E1 run id $1, on stdout; returns 1 when $1 is not <UTC %Y%m%d-%H%M%S>_${SWEEP}_r<one of RATES>.
rate_of() {
  local r st=${1%%_*}
  [[ $st == [0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9] ]] || return 1
  for r in $RATES; do [[ ${1#*_} == ${SWEEP}_r$r ]] && { print -r -- $r; return 0; }; done
  return 1
}

# Is the tmux session 'run' alive on the VM? Sets TMUX_ON to 1 or 0; returns 2 with MSG when the VM does not answer.
vm_tmux() {
  local out
  TMUX_ON=""
  out=$(ssh $K $H 'tmux has-session -t run 2> /dev/null; echo "tmux_rc=$?"') || { MSG="the VM could not be read (tmux)"; return 2; }
  case $out in
    tmux_rc=0) TMUX_ON=1;;
    tmux_rc=1) TMUX_ON=0;;
    *) MSG="the VM's tmux read gave '$out'"; return 2;;
  esac
  return 0
}

# What the VM holds for E1's six run names: one line per run folder, "<run id> valid|invalid|nochecks|unreadable
# <failed|->". Read-only: vm_state.py is sent on stdin and reads only `valid` and `failed` of checks.json.
vm_state() {
  local out names=(${RATES[@]/#/${SWEEP}_r})
  VMS=()
  out=$(ssh $K $H "python3 - ${names[*]}" < $S/vm_state.py) || return 1
  [[ ${out##*$'\n'} == "END ${#RATES}" ]] || return 1
  VMS=("${(@f)out}"); VMS=(${VMS[1,-2]})
  return 0
}

# Once the invocation of attempt record $1 has ended: the lines of its launch log that hold run_id (an allowed read)
# are reduced to the run id and the commit the same line names (`[run] start {'run_id': ..., 'git_commit': ...}`,
# harness/run.py:143), and written to state/settled_<attempt>.txt, once. A log that does not exist names no run.
SETTLE_END=END_OF_RUN_ID_LINES
settle() {
  local rec=$1 f log out line id c lines recs=()
  MSG=""
  f=$ST/settled_${${rec:t}%.txt}.txt
  [[ ! -e $f ]] || { MSG="${f:t} exists"; return 2; }
  log=$(sed -n 's/^log //p' $rec)
  [[ $log == '~/e1_'*.log ]] || { MSG="${rec:t} names no launch log"; return 2; }
  out=$(ssh $K $H "if [ -f $log ]; then grep \"'run_id': '\" $log; fi; echo $SETTLE_END") || { MSG="the launch log of ${rec:t} could not be read"; return 2; }
  [[ ${out##*$'\n'} == $SETTLE_END ]] || { MSG="the read of the launch log of ${rec:t} was cut off"; return 2; }
  lines=("${(@f)out}"); lines=(${lines[1,-2]})
  for line in $lines; do
    id=$(print -r -- "$line" | grep -o "'run_id': '[^']*'" | head -1 | cut -d"'" -f4)
    c=$(print -r -- "$line" | grep -o "'git_commit': '[^']*'" | head -1 | cut -d"'" -f4)
    [[ -n $id ]] || { MSG="a run_id line of the launch log of ${rec:t} holds no run id"; return 2; }
    recs+=("rid $id ${c:--}")
  done
  print -r -l -- $recs "time $(date -u +%Y-%m-%dT%H:%M:%SZ)" "scripts $SC" > $f.tmp && mv $f.tmp $f || { MSG="${f:t} could not be written"; return 2; }
  return 0
}

# E1's stopping rule, from the records in state/, the settled launch logs and the VM's checks.json (valid, failed).
# Sets ACT and ARG to the next thing to do, or returns 2 with MSG when the registration, or a check, stops the queue:
#   settle <record>   an attempt whose invocation has ended has not been settled yet;
#   copy <run id>     a run with a checks.json (valid or invalid) is not yet copied and verified on the Mac;
#   launch sweep      the one invocation of the sweep (first, once; nothing of E1 may exist before it);
#   launch <rate>     with NEXT_ATT: that rate's next attempt, from its single-rate config;
#   done              every rate settled; SUMMARY holds one line per rate, SPENT the rates whose attempts are spent.
# The rules, in the order applied:
#   - no decision while the tmux session 'run' is alive (an invocation is running);
#   - every E1 folder on the VM is named by exactly one settled launch log of these scripts, at the registered commit
#     (the commit on its run_id line); every run so named is on the VM; every E1 folder on the Mac is on the VM;
#   - a rate the sweep started has spent attempt 1 on it; a rate it never started has spent none, and its single-rate
#     launch is its first attempt; every single-rate launch is one attempt whatever it left behind;
#   - a run without checks.json, at any rate, stops the queue until state/lost_ok_<run id>.txt records a new
#     decision (the finished runs are copied first);
#   - a rate with a valid run is done; two or more valid runs are all listed, and nothing is launched;
#   - `no_errors` or `power_limit` in any E1 run's `failed` stops the queue; so does a second `gpu_steady` among them;
#   - a rate with MAX_ATTEMPTS attempts spent is not launched again (listed in SPENT); the other rates go on.
next_step() {
  local rec f stem line l2 parts id c r rate name s att n a ids valid inval lost=() stopper="" n_heat=0
  local -A NAMED per
  ACT=""; ARG=""; NEXT_ATT=""; MSG=""; SUMMARY=(); SPENT=()
  vm_tmux || return 2
  (( ! TMUX_ON )) || { MSG="the tmux session 'run' is alive on the VM: an invocation is running (E1's or another). Start the queue again after it ends"; return 2; }
  vm_state || { MSG="the VM's run folders could not be read"; return 2; }
  for rec in $ST/attempt_*.txt(N); do
    [[ -e $ST/settled_${${rec:t}%.txt}.txt ]] || { ACT=settle; ARG=$rec; return 0; }
  done
  for f in $ST/settled_*.txt(N); do
    stem=${${f:t}#settled_}; stem=${stem%.txt}; per=()
    [[ -e $ST/$stem.txt ]] || { MSG="${f:t} has no attempt record"; return 2; }
    for line in ${(f)"$(grep '^rid ' $f)"}; do
      parts=(${=line}); id=$parts[2]; c=$parts[3]
      r=$(rate_of $id) || { MSG="${f:t} names '$id', which is not a run of E1's sweep"; return 2; }
      [[ $stem == attempt_sweep_1 || $stem == attempt_r${r}_<-> ]] || { MSG="${f:t} names $id, a run of another rate"; return 2; }
      [[ -z ${per[$r]} ]] || { MSG="${f:t} names two runs of rate $r"; return 2; }
      [[ -z ${NAMED[$id]} ]] || { MSG="$id is named by two launch logs"; return 2; }
      [[ $c == $E1 ]] || { MSG="$id was made at commit '$c' (its launch log's run_id line), not at the registered commit $E1: the owner decides"; return 2; }
      per[$r]=$id; NAMED[$id]=$stem
    done
  done
  ids=()
  for line in $VMS; do
    parts=(${=line}); id=$parts[1]; ids+=($id)
    [[ -n ${NAMED[$id]} ]] || { MSG="the VM holds $id, which no settled launch log of these scripts names (a launch outside them, or a lost log): the owner decides"; return 2; }
    [[ $parts[2] != unreadable ]] || { MSG="checks.json of $id cannot be read (fields valid and failed)"; return 2; }
  done
  for id in ${(k)NAMED}; do
    [[ ${ids[(Ie)$id]} -gt 0 ]] || { MSG="$id, named by the launch log of ${NAMED[$id]}, is not on the VM: the owner decides"; return 2; }
  done
  for id in $R/runs/*_${SWEEP}_r*(N:t); do
    [[ ${ids[(Ie)$id]} -gt 0 ]] || { MSG="the Mac holds $id, which the VM does not list: the owner decides"; return 2; }
  done
  for line in $VMS; do
    parts=(${=line})
    [[ ( $parts[2] == valid || $parts[2] == invalid ) && ! -e $ST/copied_$parts[1].txt ]] || continue
    ACT=copy; ARG=$parts[1]; return 0
  done
  if [[ ! -e $ST/attempt_sweep_1.txt ]]; then
    a=($ST/attempt_*.txt(N) $ST/settled_*.txt(N))
    (( ${#VMS} == 0 && ${#a} == 0 )) || { MSG="E1 run folders or attempt records exist although the sweep was never launched by these scripts: the owner decides"; return 2; }
    ACT=launch; ARG=sweep; NEXT_ATT=1; return 0
  fi
  for line in $VMS; do
    parts=(${=line})
    for f in ${(s:,:)parts[3]}; do
      [[ $f == $HEAT ]] && n_heat=$((n_heat + 1))
      [[ ${NORERUN[(Ie)$f]} -gt 0 ]] && stopper="$f ($parts[1])"
    done
    [[ $parts[2] == nochecks && ! -f $ST/lost_ok_$parts[1].txt ]] && lost+=($parts[1])
  done
  (( ${#lost} == 0 )) || { MSG="$lost[1] has no checks.json (it ended without one, or is still running): E1 stops until a new decision, recorded as $ST/lost_ok_$lost[1].txt"; return 2; }
  for rate in $RATES; do
    name=${SWEEP}_r$rate; valid=(); inval=(); s=0
    for l2 in $VMS; do
      parts=(${=l2})
      [[ $parts[1] == *_$name ]] || continue
      [[ ${NAMED[$parts[1]]} == attempt_sweep_1 ]] && s=1
      case $parts[2] in
        valid) valid+=($parts[1]);;
        invalid) inval+=($parts[1]);;
      esac
    done
    a=($ST/attempt_r${rate}_<->.txt(N)); att=$((s + ${#a}))
    for (( n = s + 1; n <= att; n++ )); do
      [[ -e $ST/attempt_r${rate}_$n.txt ]] || { MSG="the attempt records of rate $rate are not numbered $((s + 1))..$att (the sweep's run is attempt 1 when the sweep started the rate)"; return 2; }
    done
    if (( ${#valid} == 1 )); then SUMMARY+=("r$rate $valid[1] attempts $att"); continue; fi
    if (( ${#valid} > 1 )); then SUMMARY+=("r$rate $valid[1] attempts $att; also valid, not counted (e1.first_valid counts the earliest): ${valid[2,-1]}"); continue; fi
    if (( att >= MAX_ATTEMPTS )); then SPENT+=($rate); SUMMARY+=("r$rate none: the $MAX_ATTEMPTS attempts are spent (${#inval} invalid)"); continue; fi
    [[ -z $stopper ]] || { MSG="E1 registers no rerun after $stopper: E1 stops; the owner decides"; return 2; }
    (( n_heat < MAX_HEAT )) || { MSG="second heat failure ($HEAT) among E1's runs: E1 stops; the owner decides"; return 2; }
    ACT=launch; ARG=$rate; NEXT_ATT=$((att + 1))
    [[ ! -e $ST/attempt_r${rate}_$NEXT_ATT.txt ]] || { MSG="attempt record $NEXT_ATT of rate $rate exists"; ACT=""; return 2; }
    return 0
  done
  ACT=done
  return 0
}

# Copy one run to the Mac's runs/, compare every file's sha256 with the VM's (ops_r3's queue), update the manifest,
# and only then write state/copied_<run id>.txt (REG-20's form). Returns 2 with MSG on any failure.
copy_verify() {
  local rid=$1 la lb a b
  cd $R || { MSG="no repo"; return 2; }
  rsync -a -e "ssh ${K[*]}" "${H}:aftershock-artifacts/runs/$rid" runs/ || { MSG="copy failed $rid"; return 2; }
  la=$(ssh $K $H "cd ~/aftershock-artifacts/runs/$rid && find . -type f | LC_ALL=C sort | xargs sha256sum") || { MSG="the VM's checksums of $rid could not be read"; return 2; }
  lb=$(cd runs/$rid && find . -type f | LC_ALL=C sort | xargs shasum -a 256) || { MSG="the Mac's checksums of $rid could not be computed"; return 2; }
  [[ -n $la && -n $lb ]] || { MSG="empty checksum list for $rid"; return 2; }
  a=$(print -r -- "$la" | shasum -a 256 | cut -c1-16); b=$(print -r -- "$lb" | shasum -a 256 | cut -c1-16)
  [[ $a == $b ]] || { MSG="checksum mismatch $rid (vm [$a] mac [$b])"; return 2; }
  python3 tools/manifest.py update > /dev/null || { MSG="manifest update failed after copying $rid"; return 2; }
  print -r -l -- "rid $rid" "files ${#${(f)la}}" "sha_of_sums $a" "time $(date -u +%Y-%m-%dT%H:%M:%SZ)" > $ST/copied_$rid.tmp && mv $ST/copied_$rid.tmp $ST/copied_$rid.txt || { MSG="the copy record of $rid could not be written"; return 2; }
  echo "COPIED $rid ${#${(f)la}} files sha-of-sums $a"
  return 0
}
