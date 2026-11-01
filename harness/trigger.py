"""The Stage 2 shock: at trigger.at_s, wipe vLLM's prefix cache. One record per attempt -> trigger.jsonl.

Modes (docs/decisions.md):
  preempt: one call with reset_running_requests=true; every running request starts over.
  idle:    calls without it, retrying until one lands while no blocks are held, or max_wait_s runs out.

Usage (started by run.py): python -m harness.trigger <run_dir> <t0_monotonic>
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

DEV_MODE_ENV = "VLLM_SERVER_DEV_MODE"  # vLLM serves /reset_prefix_cache only with this set to 1


def validate(cfg: dict):
    """Stop before the server starts, not an hour into a run."""
    trig, wl = cfg["trigger"], cfg["workload"]
    if trig.get("kind") != "cache_wipe":
        raise SystemExit(f"{cfg['name']}: unknown trigger kind {trig.get('kind')!r}; only cache_wipe is built")
    if trig.get("mode") not in ("preempt", "idle"):
        raise SystemExit(f"{cfg['name']}: trigger.mode must be preempt or idle")
    if (cfg["server"].get("env") or {}).get(DEV_MODE_ENV) != "1":
        raise SystemExit(f"{cfg['name']}: a cache wipe needs server.env.{DEV_MODE_ENV}: '1'")
    last = trig["at_s"] + (trig["max_wait_s"] if trig["mode"] == "idle" else 0)
    if not wl["warmup_s"] <= trig["at_s"] or last >= wl["duration_s"]:
        raise SystemExit(f"{cfg['name']}: the trigger must fall after warm-up and before the end of arrivals")


def _post(url: str, timeout_s: float) -> dict:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=b"", method="POST"), timeout=timeout_s) as r:
            return {"status": r.status, "success": json.loads(r.read())["success"] is True}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "success": False, "error": e.read().decode(errors="replace")[:500]}
    except Exception as e:
        return {"status": None, "success": False, "error": f"{type(e).__name__}: {e}"[:500]}


def fire(trig: dict, base: str, t0: float, write):
    idle = trig["mode"] == "idle"
    url = f"{base}/reset_prefix_cache" + ("" if idle else "?reset_running_requests=true")
    time.sleep(max(0.0, t0 + trig["at_s"] - time.monotonic()))
    give_up = time.monotonic() + (trig["max_wait_s"] if idle else 0)
    while True:
        start = time.monotonic()
        res = _post(url, trig["request_timeout_s"])
        write({"t_start": start - t0, "t_end": time.monotonic() - t0, "mode": trig["mode"], **res})
        if not idle or res["success"] or res["status"] != 200 or time.monotonic() >= give_up:
            return
        time.sleep(trig["retry_interval_s"])


def main(run_dir: Path, t0: float):
    cfg = yaml.safe_load((run_dir / "config.yaml").read_text())
    srv = cfg["server"]
    with open(run_dir / "trigger.jsonl", "a") as f:
        def write(rec):
            f.write(json.dumps(rec) + "\n")
            f.flush()
        fire(cfg["trigger"], f"http://{srv['host']}:{srv['port']}", t0, write)


if __name__ == "__main__":
    main(Path(sys.argv[1]), float(sys.argv[2]))
