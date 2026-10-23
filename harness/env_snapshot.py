"""Versions, GPU, driver and code commit -> env.json. Called by run.py for every run."""
import importlib.metadata as md
import json
import platform
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _cmd(*args) -> str | None:
    try:
        return subprocess.run(args, capture_output=True, text=True, check=True, cwd=REPO).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _version(pkg: str) -> str | None:
    try:
        return md.version(pkg)
    except md.PackageNotFoundError:
        return None


def snapshot() -> dict:
    torch_cuda = None
    try:
        import torch
        torch_cuda = torch.version.cuda
    except ImportError:
        pass
    gpu = _cmd("nvidia-smi", "--query-gpu=name,driver_version,memory.total,power.limit",
               "--format=csv,noheader")
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "cpu_count": _cmd("nproc") or str(__import__("os").cpu_count()),
        "packages": {p: _version(p) for p in ["vllm", "torch", "transformers", "aiohttp", "numpy", "pandas"]},
        "torch_cuda": torch_cuda,
        "nvidia_smi": gpu,
        "cuda_driver": _cmd("nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"),
        "git_commit": _cmd("git", "rev-parse", "HEAD"),
        "git_dirty": bool(_cmd("git", "status", "--porcelain", "--untracked-files=no")),
        "uv_lock_sha": _cmd("git", "hash-object", "uv.lock"),
    }


def write(path: Path) -> dict:
    env = snapshot()
    path.write_text(json.dumps(env, indent=2))
    return env


if __name__ == "__main__":
    print(json.dumps(snapshot(), indent=2))
