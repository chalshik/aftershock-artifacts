#!/bin/zsh
# REG-19's table, once, FROM THE WORKTREE at the pin:   zsh docs/probe/20261113_reg19/ops_r3/final.sh
# Allowed only when the step records show that all five seeds were run or that the registered futility stop fired
# ('continue': False after seed 18). After an operational stop (a lost VM, attempts spent, a failed check) there is no
# table: REG-19 says the runs are reported from checks.json and the owner decides. The pinned `reg19` words every short
# matrix as a futility stop, so that wording is only right behind this gate. Refused when a table file exists.
source ${0:A:h}/common.sh
mac_checks || exit 2
links_ok || exit 2
r18=$ST/reg19_step_s18.txt; r19=$ST/reg19_step_s19.txt; why=""
if [[ -f $r19 && -f $r18 ]]; then
  [[ $(sed -n 1p $r19) == "'done': [15, 16, 17, 18, 19]" && $(sed -n 2p $r19) == "'continue': False" && $(sed -n 2p $r18) == "'continue': True" ]] && why="all five seeds run"
elif [[ -f $r18 ]]; then
  [[ $(sed -n 1p $r18) == "'done': [15, 16, 17, 18]" && $(sed -n 2p $r18) == "'continue': False" ]] && why="futility stop after seed 18"
fi
[[ -n $why ]] || { echo "STOP: no table. The step records do not show all five seeds run or a futility stop; after an operational stop the owner decides (REG-19)"; exit 2; }
prev=($ST/reg19_final_*.txt(N))
(( ${#prev} == 0 )) || { echo "STOP: the table was already computed or tried: ${prev[*]:t}"; exit 2; }
ts=$(date -u +%Y%m%dT%H%M%SZ); out=$ST/reg19_final_$ts.txt; err=$ST/reg19_final_err_$ts.txt
(cd $W && $PY -m analysis.gate reg19 > $out 2> $err); rc=$?
echo "FINAL ($why); rc $rc; scripts $SC; pin $PIN; worktree $W; output ${out:t}; stderr_lines $(wc -l < $err | tr -d ' ') ${err:t}"
(( rc == 0 )) || { echo "STOP: reg19 failed (see $err). A second try is an operational step with its own [OPS] entry: the file $out must first be set aside by hand"; exit 1; }
cat $out
