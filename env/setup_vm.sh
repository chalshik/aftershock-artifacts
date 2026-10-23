#!/usr/bin/env bash
# One-time setup on the Linux GPU VM. Safe to re-run. Never upgrades pinned versions (--frozen).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== GPU =="
nvidia-smi --query-gpu=name,driver_version,memory.total,power.limit --format=csv
nvidia-smi | head -4 | tail -1   # shows the max CUDA version the driver supports

echo "== uv =="
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

echo "== environment (pinned by uv.lock) =="
uv sync --frozen --extra server
uv run python - <<'PY'
import torch, vllm
print("vllm", vllm.__version__, "| torch", torch.__version__, "| torch CUDA", torch.version.cuda)
assert torch.cuda.is_available(), "torch cannot see the GPU: driver too old for this torch CUDA build?"
print("GPU:", torch.cuda.get_device_name(0))
PY

echo "== models =="
uv run python -c "
from huggingface_hub import snapshot_download
for m in ['Qwen/Qwen3-1.7B', 'Qwen/Qwen3-4B']:
    print(m, '->', snapshot_download(m))"

echo "== CPU cores (for cpus: in configs) =="
nproc; lscpu | grep -E 'Model name|NUMA node' || true
echo "Done. Next: uv run python env/probe.py"
