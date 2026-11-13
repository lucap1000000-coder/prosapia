from typing import Iterable
import json
import pandas as pd
from prosapia.core import Collected, CollectCtx, CollectEach, DesignCtx

KEYS = ("n_res", "fixed_len", "linker_len", "subunit_len")

def collect_chainlen(ctx: CollectCtx) -> CollectEach:
    json_files = {p.stem: p for p in ctx.out_dir.glob("*.json")}
    na = {k: pd.NA for k in KEYS}

    def one(d: DesignCtx) -> Iterable[Collected]:
        f = json_files.get(d.name)
        if f is None:
            yield Collected(status=f"missing: no .json for {d.name}", data=na)
            return
        metrics = json.loads(f.read_text())
        yield Collected(data={k: metrics[k] for k in KEYS}, path=f)

    return one
