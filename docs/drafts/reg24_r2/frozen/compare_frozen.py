"""REG-24 draft 2, rule F round 1 RE7: compare the frozen seed-rule file with a later analysis/confirm.py, symbol by
symbol, by source text (ast.get_source_segment), so that a reviewer can check which parts of the rule are byte-identical.

    python3 -I docs/drafts/reg24_r2/frozen/compare_frozen.py <frozen confirm.py> <later confirm.py>

Prints one line per top-level function, per top-level assignment and per key of the REG24 dict: `same`, `changed`,
`added` or `removed`, then the sha256 of both files. Reads the two files only; imports neither.
"""
import ast
import hashlib
import sys
from pathlib import Path


def symbols(path: Path) -> dict[str, str]:
    src = path.read_text()
    tree = ast.parse(src)
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            out[f"def {node.name}"] = ast.get_source_segment(src, node)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            out[f"assign {name}"] = ast.get_source_segment(src, node)
            if isinstance(node.value, ast.Dict):
                for k, v in zip(node.value.keys, node.value.values):
                    if isinstance(k, ast.Constant):
                        out[f"{name}[{k.value!r}]"] = ast.get_source_segment(src, v)
    return out


def main(a: str, b: str) -> None:
    pa, pb = Path(a), Path(b)
    sa, sb = symbols(pa), symbols(pb)
    for k in list(sa) + [k for k in sb if k not in sa]:
        if k not in sb:
            state = "removed"
        elif k not in sa:
            state = "added"
        else:
            state = "same" if sa[k] == sb[k] else "changed"
        print(f"{state:8s} {k}")
    for p in (pa, pb):
        print(f"sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
