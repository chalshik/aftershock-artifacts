"""Every interval: scrape vLLM /metrics and GPU stats, append raw values, print a status line.

Usage (started by run.py): python -m harness.recorder <run_dir> <t0_monotonic>
Runs until SIGTERM/SIGINT.
"""
import json
import signal
import sys
import time
import urllib.request
from pathlib import Path

import yaml
from prometheus_client.parser import text_string_to_metric_families

try:
    import pynvml
except ImportError:  # Mac / tests: no GPU stats
    pynvml = None

_stop = False


def _on_signal(*_):
    global _stop
    _stop = True


def scrape(url: str, timeout_s: float = 0.9) -> dict[str, float]:
    """Raw vllm:* samples as {'name{label="v",...}': value}. Counters stay raw totals. Callers pass the configured
    `recorder.scrape_timeout_s`; the default is that knob's value, for callers without a config."""
    text = urllib.request.urlopen(url, timeout=timeout_s).read().decode()
    out = {}
    for fam in text_string_to_metric_families(text):
        for s in fam.samples:
            if s.name.startswith("vllm:"):
                labels = ",".join(f'{k}="{v}"' for k, v in sorted(s.labels.items()))
                out[f"{s.name}{{{labels}}}"] = s.value
    return out


def total(sample: dict, name: str) -> float | None:
    """Sum of every sample of a metric, across label sets (so a single engine just gives its value)."""
    vals = [v for k, v in sample.items() if k.split("{", 1)[0] == name]
    return sum(vals) if vals else None


class Gpu:
    def __init__(self):
        self.h = None
        if pynvml:
            try:
                pynvml.nvmlInit()
                self.h = pynvml.nvmlDeviceGetHandleByIndex(0)
            except pynvml.NVMLError as e:  # no driver: run without GPU stats; checks flag a real run invalid
                print(f"[recorder] no GPU stats: {e}", flush=True)

    def read(self) -> dict | None:
        if not self.h:
            return None
        n, h = pynvml, self.h
        mem = n.nvmlDeviceGetMemoryInfo(h)
        return dict(
            power_w=n.nvmlDeviceGetPowerUsage(h) / 1000,
            power_limit_w=n.nvmlDeviceGetEnforcedPowerLimit(h) / 1000,
            sm_clock_mhz=n.nvmlDeviceGetClockInfo(h, n.NVML_CLOCK_SM),
            mem_clock_mhz=n.nvmlDeviceGetClockInfo(h, n.NVML_CLOCK_MEM),
            temp_c=n.nvmlDeviceGetTemperature(h, n.NVML_TEMPERATURE_GPU),
            mem_used_mib=mem.used / 2**20,
            util_pct=n.nvmlDeviceGetUtilizationRates(h).gpu,
            throttle_reasons=n.nvmlDeviceGetCurrentClocksThrottleReasons(h),
        )


class LagTail:
    """Reads new lines of requests.jsonl to report recent client lag (actual - planned send).

    The load generator may be partway through writing a line when this reads (open question A14: a half-written line
    is the likely cause of the recorder's exit at t = 213 s in a REG-12 control). So only complete lines, up to the last
    newline, are consumed; a partial tail is left for the next call, and a complete line that does not parse is
    skipped and counted in `bad_lines`."""

    def __init__(self, path: Path):
        self.path, self.pos, self.bad_lines = path, 0, 0

    def recent_max(self) -> float | None:
        if not self.path.exists():
            return None
        with open(self.path, "rb") as f:
            f.seek(self.pos)
            chunk = f.read()
        end = chunk.rfind(b"\n")
        if end < 0:
            return None
        self.pos += end + 1
        lags = []
        for line in chunk[:end].splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except ValueError:
                self.bad_lines += 1
                continue
            if r.get("t_sent") is not None and r.get("t_planned") is not None:
                lags.append(r["t_sent"] - r["t_planned"])
        return max(lags) if lags else None


def main(run_dir: Path, t0: float):
    cfg = yaml.safe_load((run_dir / "config.yaml").read_text())
    srv, interval = cfg["server"], cfg["recorder"]["interval_s"]
    url = f"http://{srv['host']}:{srv['port']}/metrics"
    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT, _on_signal)
    gpu, lag = Gpu(), LagTail(run_dir / "requests.jsonl")
    prev = None
    with open(run_dir / "metrics.jsonl", "a") as fm, open(run_dir / "gpu.jsonl", "a") as fg:
        next_tick = time.monotonic()
        while not _stop:
            t = time.monotonic() - t0
            try:
                sample = scrape(url, cfg["recorder"]["scrape_timeout_s"])  # in every config via configs/defaults.yaml
                fm.write(json.dumps({"t": t, "values": sample}) + "\n")
                fm.flush()
            except Exception as e:
                sample = None
                fm.write(json.dumps({"t": t, "error": f"{type(e).__name__}: {e}"[:200]}) + "\n")
                fm.flush()
            # Nothing below may end the process (A14): a failed GPU read or status line is logged and the loop goes on.
            g = None
            try:
                g = gpu.read()
                if g:
                    fg.write(json.dumps({"t": t, **g}) + "\n")
                    fg.flush()
            except Exception as e:
                print(f"[recorder] t={t:.1f}s gpu read failed: {type(e).__name__}: {e}"[:300], file=sys.stderr, flush=True)
            if sample:
                try:
                    print(status_line(t, prev, sample, g, lag.recent_max()), flush=True)
                except Exception as e:
                    print(f"[recorder] t={t:.1f}s status line failed: {type(e).__name__}: {e}"[:300], file=sys.stderr,
                          flush=True)
                prev = sample
            next_tick += interval  # fixed grid: a slow scrape does not shift later ones
            time.sleep(max(0.0, next_tick - time.monotonic()))


def status_line(t, prev, cur, g, lag) -> str:
    def d(name):
        a, b = total(cur, name), total(prev, name) if prev else None
        return None if a is None or b is None else a - b

    hits, queries = d("vllm:prefix_cache_hits_total"), d("vllm:prefix_cache_queries_total")
    h = f"{hits / queries:.2f}" if hits is not None and queries else "-"
    kv = total(cur, "vllm:kv_cache_usage_perc")
    fmt = lambda v, f: "-" if v is None else format(v, f)
    return (f"t={t:7.1f}s  h={h}  N={fmt(total(cur, 'vllm:num_requests_running'), '.0f')}  "
            f"Q={fmt(total(cur, 'vllm:num_requests_waiting'), '.0f')}  "
            f"KV={fmt(kv * 100 if kv is not None else None, '.0f')}%  lag={fmt(lag, '.3f')}s  "
            f"sm={fmt(g['sm_clock_mhz'] if g else None, '.0f')}MHz")


if __name__ == "__main__":
    main(Path(sys.argv[1]), float(sys.argv[2]))
