#!/bin/zsh
# Once before the queue: record the VM's session (boot id, uptime, kernel, driver, governor, limit) and require 350 W.
# Read-only, except that SET=1 first runs the one allowed root command, `sudo -n nvidia-smi -pl 350`, and only when no
# compute process is on the GPU; the limit before and after is written to the probe. Writes ops/session_boot_id.txt,
# which every launch compares with the VM's boot id: a reboot between runs stops the queue.
source ${0:A:h}/common.sh
mac_checks || exit 2
out=$PROBE_DIR/session_$(date -u +%Y%m%dT%H%M%SZ).txt
[[ ! -e $out ]] || { echo "STOP: $out exists"; exit 2; }
{
  echo "# REG-19 resume: session probe (agent). scripts commit $SC; Mac HEAD $(git rev-parse HEAD)"
  ssh $K $H 'date -Is; echo "boot_id $(cat /proc/sys/kernel/random/boot_id)"; echo "up_since $(uptime -s)"; echo "kernel $(uname -r)";
    echo "driver $(nvidia-smi --query-gpu=driver_version --format=csv,noheader)";
    echo "governor $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo n/a)";
    echo "limit_before $(nvidia-smi --query-gpu=power.limit --format=csv,noheader)";
    echo "apps $(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)"'
} > $out || { echo "STOP: the VM could not be read"; exit 3; }
if [[ -n $SET ]]; then
  if [[ $(grep '^apps ' $out | awk '{print $2}') == 0 ]]; then
    ssh $K $H 'sudo -n nvidia-smi -pl 350 2>&1; echo "sudo_rc $?"' >> $out
  else
    echo "set_skipped a compute process is on the GPU" >> $out
  fi
fi
ssh $K $H 'echo "limit_after $(nvidia-smi --query-gpu=power.limit --format=csv,noheader)"; cd ~/aftershock-artifacts && echo "tree $(git rev-parse HEAD) dirty $(git status --short | wc -l)"; echo "free_kb $(df -k --output=avail ~ | tail -1 | tr -d " ")"' >> $out
cat $out
[[ $(grep '^limit_after ' $out | awk '{print $2}') == 350.00 ]] || { echo "STOP: power limit is not 350.00 W"; exit 4; }
grep '^boot_id ' $out | awk '{print $2}' > $S/session_boot_id.txt
echo "SESSION OK boot_id $(cat $S/session_boot_id.txt)"
