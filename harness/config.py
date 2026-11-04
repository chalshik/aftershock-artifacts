"""Config resolution: `extends:` chains, and `configs/defaults.yaml` beneath them. Shared by run.py and checks.py."""
import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DEFAULTS = REPO / "configs" / "defaults.yaml"  # merged beneath every config; see that file


def _merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_config(path: Path) -> dict:
    raw = yaml.safe_load(path.read_text())
    parent = raw.pop("extends", None)
    return _merge(load_config(path.parent / parent), raw) if parent else raw


def with_defaults(cfg: dict) -> dict:
    """`configs/defaults.yaml` beneath `cfg`: keys the config sets win. Used for new runs and for old run folders."""
    d = yaml.safe_load(DEFAULTS.read_text())
    d.pop("name", None)
    return _merge(d, cfg)
