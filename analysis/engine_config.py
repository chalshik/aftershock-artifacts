"""Scheduler settings each run's server logged at startup (open item A10). Never writes into runs/.

vLLM 0.32.0 logs two lines at startup that matter here:
- `non-default args: {...}`: the flags the harness set (a Python dict literal);
- `Initializing a V1 LLM engine (v0.32.0) with config: ...`: the resolved engine config, which includes
  `enable_chunked_prefill=` and the compile range end points (`'compile_ranges_endpoints': [...]`), but not the
  SchedulerConfig fields (`max_num_batched_tokens`, policy, async scheduling).
The unlogged fields are read from the installed wheel's defaults (docs/probe/20261105_vm_checks/scheduler_source.txt);
this module only checks that no run overrode them and that no run logged the warning that turns async scheduling off.
"""
import ast
import re
from pathlib import Path

import pandas as pd

RUNS = Path(__file__).resolve().parent.parent / "runs"

# Flags that would change a scheduler setting away from its default if they appeared in `non-default args`.
SCHEDULER_ARGS = ("max_num_batched_tokens", "max_num_scheduled_tokens", "max_num_partial_prefills",
                  "long_prefill_token_threshold", "scheduling_policy", "policy", "async_scheduling",
                  "scheduler_reserve_full_isl", "enable_chunked_prefill", "performance_mode", "watermark")

_NONDEFAULT = re.compile(r"non-default args: (\{.*\})\s*$")
_ENGINE = re.compile(r"Initializing a V1 LLM engine \(v([0-9.]+)\) with config: (.*)$")
_CHUNKED = re.compile(r"enable_chunked_prefill=(True|False)")
_ENDPOINTS = re.compile(r"'compile_ranges_endpoints': \[([0-9, ]*)\]")
_MODEL = re.compile(r"model='([^']*)'")
# Every message in vllm 0.32.0 config/vllm.py:1559-1639 that disables async scheduling (or refuses it) starts with one
# of these (docs/probe/20261105_vm_checks/scheduler_source.txt).
_ASYNC_OFF = re.compile(r"Async scheduling (is disabled|will be disabled|not supported|is not compatible)"
                        r"|Disabling asynchronous scheduling", re.I)


def engine_settings(run_dir: Path) -> dict:
    """What one run's server.log records. Fields are None when the line is missing (e.g. the server never started)."""
    out = {"run_id": Path(run_dir).name, "started": False, "vllm": None, "model": None, "chunked_prefill": None,
           "compile_ranges_endpoints": None, "non_default_args": None, "scheduler_overrides": None,
           "async_off_warning": False}
    log = Path(run_dir) / "server.log"
    if not log.exists():
        return out
    for line in log.read_text(errors="replace").splitlines():
        if (m := _NONDEFAULT.search(line)) and out["non_default_args"] is None:
            args = ast.literal_eval(m.group(1))
            out["non_default_args"] = args
            out["scheduler_overrides"] = sorted(k for k in args if k in SCHEDULER_ARGS)
        if (m := _ENGINE.search(line)) and not out["started"]:
            out["started"], out["vllm"] = True, m.group(1)
            cfg = m.group(2)
            if c := _CHUNKED.search(cfg):
                out["chunked_prefill"] = c.group(1) == "True"
            if e := _ENDPOINTS.search(cfg):
                out["compile_ranges_endpoints"] = [int(x) for x in e.group(1).replace(" ", "").split(",") if x]
            if mo := _MODEL.search(cfg):
                out["model"] = mo.group(1)
        if _ASYNC_OFF.search(line):
            out["async_off_warning"] = True
    return out


def scan(runs: Path = RUNS) -> pd.DataFrame:
    """engine_settings for every run folder under runs/, sorted by run id."""
    return pd.DataFrame([engine_settings(d) for d in sorted(p for p in Path(runs).iterdir() if p.is_dir())])


def a10_table(runs: Path = RUNS) -> pd.DataFrame:
    """Counts over all run folders: how many started a server, and among those, the logged values of each setting."""
    s = scan(runs)
    st = s[s.started]
    rows = [("run folders", len(s)), ("started a server (engine config logged)", len(st)),
            ("not started", ", ".join(s[~s.started].run_id) or "none"),
            ("vllm versions", dict(st.vllm.value_counts())),
            ("chunked_prefill", dict(st.chunked_prefill.value_counts(dropna=False))),
            ("compile_ranges_endpoints", dict(st.compile_ranges_endpoints.map(str).value_counts())),
            ("runs with a scheduler flag in non-default args",
             int(st.scheduler_overrides.map(lambda v: bool(v) if isinstance(v, list) else True).sum())),
            ("runs that logged an async-scheduling-off warning", int(st.async_off_warning.sum())),
            ("models", dict(st.model.value_counts()))]
    return pd.DataFrame(rows, columns=["item", "value"])


if __name__ == "__main__":
    pd.set_option("display.width", 250, "display.max_colwidth", 200)
    print(a10_table().to_string(index=False))
