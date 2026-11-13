#!/bin/zsh
# Read-only probe for the moment the VM answers again after a power-off (written for the one of 2026-11-13, ≈ 04:40 UTC).
# Moved into the repo from the agent's scratchpad on 2026-11-13; run from anywhere: zsh agent/bin/vm_back_probe.zsh
# No run folder and no harness log is opened: folder names, checks.json valid/failed (through vm_state.py),
# the journal's boot list and shutdown lines, the power limit. Writes one probe file into docs/probe/20261113_reg19/.
R=/Users/chalshik/Projects/aftershock-artifacts
O=$R/docs/probe/20261113_reg19/ops_r3
source $O/common.sh
# Tailscale first (common.sh's default); off the tailnet, the LAN address (agent memory: the VM answers on either).
if ! ssh $K $H true 2>/dev/null; then VM_HOST=192.168.3.249; source $O/common.sh; fi
out=$R/docs/probe/20261113_reg19/vm_back_$(date -u +%Y%m%dT%H%M%SZ).txt
{
  echo "# REG-19: read-only read of the VM after it came back (agent). No run folder and no harness log is opened."
  echo "# captured $(date -u +%FT%TZ) via $H"
  ssh $K $H 'date -Is; echo "boot_id $(cat /proc/sys/kernel/random/boot_id)"; echo "up_since $(uptime -s)";
    echo "limit $(nvidia-smi --query-gpu=power.limit --format=csv,noheader)"; echo "temp $(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader)";
    echo "apps $(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)";
    cd ~/aftershock-artifacts && echo "tree $(git rev-parse HEAD) dirty $(git status --short | wc -l)"; echo "free_kb $(df -k --output=avail ~ | tail -1 | tr -d " ")";
    echo "tmux: $(tmux ls 2>&1 | head -1)";
    echo "## journalctl --list-boots (last 6)"; journalctl --list-boots 2>&1 | tail -6;
    echo "## every power-key line in the journal, with its boot (all boots still kept)";
    journalctl -o short-iso --no-pager 2>/dev/null | grep -i -E "Power key pressed|Powering off|System is powering down" | tail -24 | cut -c1-160;
    echo "## the boot that ended on 2026-11-13: its last 6 lines, and its lines naming thermal, overheat, a critical temperature or Xid";
    journalctl -b -1 -o short-iso --no-pager 2>&1 | tail -6 | cut -c1-200;
    journalctl -b -1 -o short-iso --no-pager 2>&1 | grep -i -E "thermal|overheat|critical temperature|Xid" | grep -v "thermal governor\|thermald.service" | tail -10 | cut -c1-200;
    echo "## the last ssh login before that shutdown"; journalctl -b -1 -o short-iso --no-pager 2>&1 | grep "Accepted publickey" | tail -1 | cut -c1-120'
  echo "## what the VM holds for REG-19's configs (vm_state.py), and what decide() and gate() say for the four left"
  vm_state && { for l in $VMS; do echo "   $l"; done; } || echo "   VM STATE NOT READ"
  for c in $LEFT; do
    gate $c; g=$?; gm=$MSG; decide $c
    echo "$c: gate rc $g [$gm]; decide rc $? RID='$RID' LAUNCH='$LAUNCH' [$MSG]"
  done
} > $out 2>&1
echo $out
