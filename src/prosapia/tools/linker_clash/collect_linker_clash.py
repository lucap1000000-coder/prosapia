import json
from typing import Iterable

import pandas as pd

from prosapia.core import Collected, CollectCtx, CollectEach, DesignCtx

KEYS = ("min_linker_clash_dist",)


def collect_linker_clash(ctx: CollectCtx) -> CollectEach:
    files = {p.stem: p for p in ctx.out_dir.glob("*.json")}
    na = {k: pd.NA for k in KEYS}

    def one(d: DesignCtx) -> Iterable[Collected]:
        f = files.get(d.name)
        if f is None:
            yield Collected(status=f"missing: no .json for {d.name}", data=na)
            return
        metrics = json.loads(f.read_text())
        yield Collected(data={k: metrics[k] for k in KEYS}, path=f)

    return one
