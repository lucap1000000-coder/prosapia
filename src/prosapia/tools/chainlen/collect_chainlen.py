from typing import Iterable

import pandas as pd

from prosapia.core import Collected, CollectCtx, CollectEach, DesignCtx


def collect_chainlen(ctx: CollectCtx) -> CollectEach:
    # Runs once: index every <name>.len file that the SLURM tasks wrote.
    len_files = {p.stem: p for p in ctx.out_dir.glob("*.len")}

    def one(d: DesignCtx) -> Iterable[Collected]:
        # Runs once per design that is ready to collect.
        f = len_files.get(d.name)
        if f is None:
            yield Collected(
                status=f"missing: no .len file for {d.name}",
                data={"n_res": pd.NA},
            )
            return
        yield Collected(data={"n_res": int(f.read_text().strip())}, path=f)

    return one
