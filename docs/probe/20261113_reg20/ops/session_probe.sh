#!/bin/zsh
# REG-20, once before the queue (copied from ops_r3/session_probe.sh; only the pin, the paths and the wording differ):
# record the VM's session (boot id, uptime, kernel, driver, governor, limit, tree, lock, disk) and the Mac's environment
# against uv.lock, and require 350.00 W, the pinned driver, and the pinned, clean tree and lock. Read-only, except that
# SET=1 first runs the one allowed root command, `sudo -n nvidia-smi -pl 350`, and only when no compute process is on
# the GPU; the limit before and after is written to the probe. Writes state/session_boot_id.txt, which every launch
# compares with the VM's boot id: a reboot between runs stops the queue. A second probe replaces that tripwire, so it
# is refused unless RENEW=1 (after a reboot: a renewal needs a decisions.md entry); the replaced file is kept under
# another name. The kernel and the NVIDIA module of the boot before this one, read from the journal, are recorded
# beside this boot's, so that a change across the reboot is on file before any run.
source ${0:A:h}/common.sh
mac_checks || exit 2
mkdir -p $ST
cur=$ST/session_boot_id.txt
[[ ! -e $cur || -n $RENEW ]] || { echo "STOP: a session probe exists ($cur); RENEW=1 replaces it, and only with a decisions.md entry"; exit 2; }
stamp; ts=$REPLY
out=$PROBE_DIR/session_$ts.txt
[[ ! -e $out ]] || { echo "STOP: $out exists"; exit 2; }
dry=$(cd $R && uv sync --frozen --dry-run --offline 2>&1) || { echo "STOP: the dry-run sync of the Mac's environment failed"; exit 2; }
n_add=$(print -r -- "$dry" | grep -c '^ [+~] '); n_extra=$(print -r -- "$dry" | grep -c '^ - ')
{
  echo "# REG-20 arm A: session probe (agent). scripts commit $SC; Mac HEAD $(git rev-parse HEAD); pin $PIN"
  echo "mac_venv missing_or_other_version $n_add extra $n_extra (uv sync --frozen --dry-run --offline)"
  ssh $K $H 'date -Is; echo "boot_id $(cat /proc/sys/kernel/random/boot_id)"; echo "up_since $(uptime -s)"; echo "kernel $(uname -r)";
    echo "driver $(nvidia-smi --query-gpu=driver_version --format=csv,noheader)";
    echo "governor $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo n/a)";
    echo "limit_before $(nvidia-smi --query-gpu=power.limit --format=csv,noheader)";
    echo "apps $(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)";
    echo "boots $(journalctl --list-boots 2>/dev/null | tail -3 | tr -s " " | tr "\n" ";")";
    echo "prev_boot_kernel $(journalctl -b -1 -k --no-pager 2>/dev/null | grep -m1 -o "Linux version [^ ]*")";
    echo "prev_boot_nvidia $(journalctl -b -1 -k --no-pager 2>/dev/null | grep -m1 -o "NVIDIA UNIX.*Kernel Module  *[0-9.]*")"'
} > $out || { echo "STOP: the VM could not be read"; exit 3; }
if [[ -n $SET ]]; then
  if [[ $(grep '^apps ' $out | awk '{print $2}') == 0 ]]; then
    ssh $K $H 'sudo -n nvidia-smi -pl 350 2>&1; echo "sudo_rc $?"' >> $out
  else
    echo "set_skipped a compute process is on the GPU" >> $out
  fi
fi
ssh $K $H 'echo "limit_after $(nvidia-smi --query-gpu=power.limit --format=csv,noheader)"; cd ~/aftershock-artifacts && echo "tree $(git rev-parse HEAD) dirty $(git status --short | wc -l)"; echo "lock_blob $(git hash-object uv.lock)"; echo "free_kb $(df -k --output=avail ~ | tail -1 | tr -d " ")"' >> $out || { echo "STOP: the VM could not be read (second read)"; exit 3; }
cat $out
[[ $n_add == 0 ]] || { echo "STOP: the Mac's .venv lacks a locked package or holds another version ($n_add)"; exit 2; }
[[ $(grep '^limit_after ' $out | awk '{print $2}') == 350.00 ]] || { echo "STOP: power limit is not 350.00 W"; exit 4; }
[[ $(grep '^tree ' $out | awk '{print $2, $4}') == "$PIN 0" ]] || { echo "STOP: the VM's tree is not the pin $PIN, clean"; exit 2; }
[[ $(grep '^driver ' $out | awk '{print $2}') == $DRIVER ]] || { echo "STOP: the VM's driver is not $DRIVER (PROTOCOL section 4)"; exit 2; }
[[ $(grep '^lock_blob ' $out | awk '{print $2}') == $(git -C $R rev-parse ${PIN}:uv.lock) ]] || { echo "STOP: the VM's uv.lock is not the pin's"; exit 2; }
boot=$(grep '^boot_id ' $out | awk '{print $2}')
[[ $boot =~ '^[0-9a-f-]{36}$' ]] || { echo "STOP: no boot id read"; exit 3; }
if [[ -e $cur ]]; then mv $cur $ST/session_boot_id_replaced_$ts.txt || { echo "STOP: the earlier session file could not be set aside"; exit 2; }; fi
print -r -- $boot > $cur
echo "SESSION OK boot_id $boot"
